#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib import error, request


@dataclass(frozen=True)
class SeedConfig:
    api_base_url: str
    frontend_base_url: str
    timeout_seconds: float
    label: str


class SeedWorkflowError(Exception):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seed a local demo graph through the public beta-feedback-platform APIs."
    )
    parser.add_argument(
        "--api-base-url",
        default="http://127.0.0.1:8000/api/v1",
        help="Backend API base URL. Default: %(default)s",
    )
    parser.add_argument(
        "--frontend-base-url",
        default="http://127.0.0.1:3000",
        help="Frontend base URL used for printed detail links. Default: %(default)s",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds. Default: %(default)s",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="Optional label suffix for created records. Defaults to an ISO-like timestamp.",
    )
    return parser


def normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def build_label(value: str | None) -> str:
    if value:
        return value.strip()

    return datetime.now().strftime("%Y%m%d-%H%M%S")


def request_json(
    *,
    method: str,
    url: str,
    timeout_seconds: float,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    data = None
    request_headers = {
        "Accept": "application/json",
    }
    if headers is not None:
        request_headers.update(headers)

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    req = request.Request(url, method=method, data=data, headers=request_headers)

    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            raw_body = response.read().decode("utf-8")
            if not raw_body:
                return {}
            return json.loads(raw_body)
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = body

        try:
            parsed_json = json.loads(body)
            parsed = json.dumps(parsed_json, ensure_ascii=True)
        except json.JSONDecodeError:
            pass

        raise SeedWorkflowError(
            f"{method} {url} failed with HTTP {exc.code}: {parsed}"
        ) from exc
    except error.URLError as exc:
        raise SeedWorkflowError(
            f"{method} {url} failed: {exc.reason}"
        ) from exc


def post_resource(
    *,
    config: SeedConfig,
    path: str,
    payload: dict[str, Any],
    actor_id: str | None = None,
) -> dict[str, Any]:
    return request_json(
        method="POST",
        url=f"{config.api_base_url}{path}",
        timeout_seconds=config.timeout_seconds,
        payload=payload,
        headers=build_actor_headers(actor_id),
    )


def get_resource(
    *,
    config: SeedConfig,
    path: str,
    actor_id: str | None = None,
) -> dict[str, Any]:
    return request_json(
        method="GET",
        url=f"{config.api_base_url}{path}",
        timeout_seconds=config.timeout_seconds,
        headers=build_actor_headers(actor_id),
    )


def build_actor_headers(actor_id: str | None) -> dict[str, str] | None:
    if actor_id is None:
        return None

    return {
        "X-Actor-Id": actor_id,
    }


def build_seed_payloads(label: str) -> dict[str, dict[str, Any]]:
    return {
        "developer_account": {
            "display_name": f"Role-Aware Developer {label}",
            "role": "developer",
            "bio": "Seeded developer account for owned workspace verification.",
            "locale": "zh-TW",
        },
        "tester_account": {
            "display_name": f"Role-Aware Tester {label}",
            "role": "tester",
            "bio": "Seeded tester account for inbox and feedback verification.",
            "locale": "zh-TW",
        },
        "project": {
            "name": f"Owned Project Sandbox {label}",
            "description": (
                "Seeded owned project for role-aware browser verification and manual QA."
            ),
        },
        "campaign": {
            "name": f"Closed Beta Round 1 {label}",
            "description": (
                "Seeded campaign covering Mobile Web and iOS verification paths."
            ),
            "target_platforms": ["h5", "ios"],
            "version_label": "0.9.1-demo",
        },
        "safety": {
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "source_url": "https://testflight.apple.com/join/demo-example",
            "risk_level": "low",
            "review_status": "approved",
            "official_channel_only": True,
            "risk_note": "Install only from the official invite link.",
        },
        "eligibility_rule": {
            "platform": "ios",
            "os_name": "iOS",
            "os_version_min": "17.0",
            "os_version_max": "18.0",
            "install_channel": "testflight",
            "is_active": True,
        },
        "device_profile": {
            "name": f"Owned QA iPhone 15 Pro {label}",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
            "os_version": "17.4",
            "locale": "zh-TW",
            "notes": "Seeded by the role-aware local demo data workflow.",
        },
        "task": {
            "title": "Validate onboarding and pricing flow",
            "instruction_summary": (
                "Install from TestFlight, complete onboarding, review the pricing copy, "
                "and submit structured feedback."
            ),
            "status": "assigned",
        },
        "feedback": {
            "summary": "Pricing copy is unclear on first launch",
            "rating": 3,
            "severity": "medium",
            "category": "usability",
            "reproduction_steps": (
                "Open the app from a fresh install and continue to the first pricing screen."
            ),
            "expected_result": "The pricing copy should clearly explain the trial boundary.",
            "actual_result": "The copy feels ambiguous for a first-time tester.",
            "note": (
                "This seed intentionally leaves review_status as submitted so T027 can be "
                "manually exercised from the UI."
            ),
        },
    }


def print_summary(
    *,
    config: SeedConfig,
    health: dict[str, Any],
    developer_account: dict[str, Any],
    tester_account: dict[str, Any],
    project: dict[str, Any],
    campaign: dict[str, Any],
    safety: dict[str, Any],
    eligibility_rule: dict[str, Any],
    device_profile: dict[str, Any],
    task: dict[str, Any],
    feedback: dict[str, Any],
) -> None:
    frontend = config.frontend_base_url
    api_base = config.api_base_url

    print("")
    print("Local demo data seed completed.")
    print("")
    print("Backend health")
    print(f"- service: {health.get('service')}")
    print(f"- status: {health.get('status')}")
    print("")
    print("Current actors")
    print(
        f"- developer: {developer_account['id']} ({developer_account['display_name']})"
    )
    print(f"- tester: {tester_account['id']} ({tester_account['display_name']})")
    print("")
    print("Created owned records")
    print(f"- project: {project['id']} ({project['name']})")
    print(f"- campaign: {campaign['id']} ({campaign['name']})")
    print(f"- safety: {safety['id']} ({safety['source_label']})")
    print(
        f"- eligibility rule: {eligibility_rule['id']} ({eligibility_rule['platform']})"
    )
    print(f"- device profile: {device_profile['id']} ({device_profile['name']})")
    print(f"- task: {task['id']} ({task['title']})")
    print(f"- feedback: {feedback['id']} ({feedback['summary']})")
    print("")
    print("Frontend detail URLs")
    print(f"- developer account detail: {frontend}/accounts/{developer_account['id']}")
    print(f"- tester account detail: {frontend}/accounts/{tester_account['id']}")
    print(f"- project detail: {frontend}/projects/{project['id']}")
    print(f"- campaign detail: {frontend}/campaigns/{campaign['id']}")
    print(
        "- eligibility rule detail: "
        f"{frontend}/campaigns/{campaign['id']}/eligibility-rules/{eligibility_rule['id']}"
    )
    print(f"- device profile detail: {frontend}/device-profiles/{device_profile['id']}")
    print(f"- task detail: {frontend}/tasks/{task['id']}")
    print(f"- feedback detail: {frontend}/tasks/{task['id']}/feedback/{feedback['id']}")
    print("")
    print("Role-aware workspace URLs")
    print(f"- developer workspace projects: {frontend}/my/projects")
    print(f"- developer workspace campaigns: {frontend}/my/campaigns")
    print(f"- developer review queue: {frontend}/review/feedback")
    print(f"- tester inbox: {frontend}/my/tasks")
    print("")
    print("API detail URLs")
    print(f"- developer account detail: {api_base}/accounts/{developer_account['id']}")
    print(f"- tester account detail: {api_base}/accounts/{tester_account['id']}")
    print(f"- project detail: {api_base}/projects/{project['id']}")
    print(f"- campaign detail: {api_base}/campaigns/{campaign['id']}")
    print(f"- safety detail: {api_base}/campaigns/{campaign['id']}/safety")
    print(f"- eligibility rule detail: {api_base}/eligibility-rules/{eligibility_rule['id']}")
    print(f"- device profile detail: {api_base}/device-profiles/{device_profile['id']}")
    print(f"- task detail: {api_base}/tasks/{task['id']}")
    print(f"- feedback detail: {api_base}/feedback/{feedback['id']}")
    print("")
    print("Notes")
    print("- Use the homepage Current Actor selector to switch between the seeded developer and tester.")
    print("- The seeded project and campaign are owned by the developer actor.")
    print("- The seeded device profile and inbox task belong to the tester actor.")
    print("- Backend data is in-memory. Restarting the backend clears everything.")
    print("- The seeded feedback remains in review_status=submitted for manual T027 checks.")
    print("- Re-running this script creates a fresh demo graph with a new label.")


def main() -> int:
    args = build_parser().parse_args()
    config = SeedConfig(
        api_base_url=normalize_base_url(args.api_base_url),
        frontend_base_url=normalize_base_url(args.frontend_base_url),
        timeout_seconds=args.timeout_seconds,
        label=build_label(args.label),
    )

    try:
        health = get_resource(config=config, path="/health")
        payloads = build_seed_payloads(config.label)

        developer_account = post_resource(
            config=config,
            path="/accounts",
            payload=payloads["developer_account"],
        )
        tester_account = post_resource(
            config=config,
            path="/accounts",
            payload=payloads["tester_account"],
        )
        project = post_resource(
            config=config,
            path="/projects",
            payload=payloads["project"],
            actor_id=developer_account["id"],
        )
        campaign = post_resource(
            config=config,
            path="/campaigns",
            payload={
                "project_id": project["id"],
                **payloads["campaign"],
            },
            actor_id=developer_account["id"],
        )
        safety = post_resource(
            config=config,
            path=f"/campaigns/{campaign['id']}/safety",
            payload=payloads["safety"],
            actor_id=developer_account["id"],
        )
        eligibility_rule = post_resource(
            config=config,
            path=f"/campaigns/{campaign['id']}/eligibility-rules",
            payload=payloads["eligibility_rule"],
            actor_id=developer_account["id"],
        )
        device_profile = post_resource(
            config=config,
            path="/device-profiles",
            payload=payloads["device_profile"],
            actor_id=tester_account["id"],
        )
        task = post_resource(
            config=config,
            path=f"/campaigns/{campaign['id']}/tasks",
            payload={
                **payloads["task"],
                "device_profile_id": device_profile["id"],
            },
            actor_id=developer_account["id"],
        )
        feedback = post_resource(
            config=config,
            path=f"/tasks/{task['id']}/feedback",
            payload=payloads["feedback"],
            actor_id=tester_account["id"],
        )

        print_summary(
            config=config,
            health=health,
            developer_account=developer_account,
            tester_account=tester_account,
            project=project,
            campaign=campaign,
            safety=safety,
            eligibility_rule=eligibility_rule,
            device_profile=device_profile,
            task=task,
            feedback=feedback,
        )
        return 0
    except SeedWorkflowError as exc:
        print(f"Seed workflow failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
