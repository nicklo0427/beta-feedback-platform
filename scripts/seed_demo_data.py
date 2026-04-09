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


def patch_resource(
    *,
    config: SeedConfig,
    path: str,
    payload: dict[str, Any],
    actor_id: str | None = None,
) -> dict[str, Any]:
    return request_json(
        method="PATCH",
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
        "qualified_campaign": {
            "name": f"Qualified Campaign Round {label}",
            "description": (
                "Seeded campaign used for qualification pass/fail verification."
            ),
            "target_platforms": ["ios", "android"],
            "version_label": "0.9.2-qualified",
        },
        "drift_campaign": {
            "name": f"Qualification Drift Round {label}",
            "description": (
                "Seeded campaign used to demonstrate qualification drift after eligibility updates."
            ),
            "target_platforms": ["ios", "android"],
            "version_label": "0.9.2-drift",
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
            "install_channel": None,
            "is_active": True,
        },
        "qualified_device_profile": {
            "name": f"Qualified QA iPhone 15 Pro {label}",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
            "os_version": "17.4",
            "locale": "zh-TW",
            "notes": "Seeded qualified device profile for qualification pass and assignment success.",
        },
        "ineligible_device_profile": {
            "name": f"Ineligible QA Pixel 9 {label}",
            "platform": "android",
            "device_model": "Pixel 9",
            "os_name": "Android",
            "os_version": "14.0",
            "locale": "zh-TW",
            "notes": "Seeded failing device profile for qualification and assignment guard verification.",
        },
        "qualified_task": {
            "title": "Validate onboarding and pricing flow",
            "instruction_summary": (
                "Install from TestFlight, complete onboarding, review the pricing copy, "
                "and submit structured feedback."
            ),
            "status": "assigned",
        },
        "drift_task": {
            "title": "Validate qualification drift handling",
            "instruction_summary": (
                "This task is intentionally seeded to become ineligible after the campaign "
                "eligibility rule changes, so task detail and tester inbox drift warnings "
                "can be verified."
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
    qualified_campaign: dict[str, Any],
    drift_campaign: dict[str, Any],
    safety: dict[str, Any],
    qualified_eligibility_rule: dict[str, Any],
    drift_eligibility_rule: dict[str, Any],
    qualified_device_profile: dict[str, Any],
    ineligible_device_profile: dict[str, Any],
    qualified_task: dict[str, Any],
    drift_task: dict[str, Any],
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
    print(
        f"- qualified campaign: {qualified_campaign['id']} ({qualified_campaign['name']})"
    )
    print(f"- drift campaign: {drift_campaign['id']} ({drift_campaign['name']})")
    print(f"- safety: {safety['id']} ({safety['source_label']})")
    print(
        "- qualified eligibility rule: "
        f"{qualified_eligibility_rule['id']} ({qualified_eligibility_rule['platform']})"
    )
    print(
        "- drift eligibility rule: "
        f"{drift_eligibility_rule['id']} ({drift_eligibility_rule['platform']})"
    )
    print(
        "- qualified device profile: "
        f"{qualified_device_profile['id']} ({qualified_device_profile['name']})"
    )
    print(
        "- ineligible device profile: "
        f"{ineligible_device_profile['id']} ({ineligible_device_profile['name']})"
    )
    print(f"- qualified task: {qualified_task['id']} ({qualified_task['title']})")
    print(f"- drift task: {drift_task['id']} ({drift_task['title']})")
    print(f"- feedback: {feedback['id']} ({feedback['summary']})")
    print("")
    print("Frontend detail URLs")
    print(f"- developer account detail: {frontend}/accounts/{developer_account['id']}")
    print(f"- tester account detail: {frontend}/accounts/{tester_account['id']}")
    print(f"- project detail: {frontend}/projects/{project['id']}")
    print(f"- qualified campaign detail: {frontend}/campaigns/{qualified_campaign['id']}")
    print(f"- drift campaign detail: {frontend}/campaigns/{drift_campaign['id']}")
    print(
        "- qualified eligibility rule detail: "
        f"{frontend}/campaigns/{qualified_campaign['id']}/eligibility-rules/{qualified_eligibility_rule['id']}"
    )
    print(
        "- drift eligibility rule detail: "
        f"{frontend}/campaigns/{drift_campaign['id']}/eligibility-rules/{drift_eligibility_rule['id']}"
    )
    print(
        "- qualified device profile detail: "
        f"{frontend}/device-profiles/{qualified_device_profile['id']}"
    )
    print(
        "- ineligible device profile detail: "
        f"{frontend}/device-profiles/{ineligible_device_profile['id']}"
    )
    print(f"- qualified task detail: {frontend}/tasks/{qualified_task['id']}")
    print(f"- drift task detail: {frontend}/tasks/{drift_task['id']}")
    print(
        "- feedback detail: "
        f"{frontend}/tasks/{qualified_task['id']}/feedback/{feedback['id']}"
    )
    print("")
    print("Qualification verification URLs")
    print(f"- tester eligible campaigns workspace: {frontend}/my/eligible-campaigns")
    print(f"- developer task create form: {frontend}/campaigns/{qualified_campaign['id']}/tasks/new")
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
    print(f"- qualified campaign detail: {api_base}/campaigns/{qualified_campaign['id']}")
    print(f"- drift campaign detail: {api_base}/campaigns/{drift_campaign['id']}")
    print(f"- safety detail: {api_base}/campaigns/{qualified_campaign['id']}/safety")
    print(
        f"- qualified eligibility rule detail: {api_base}/eligibility-rules/{qualified_eligibility_rule['id']}"
    )
    print(
        f"- drift eligibility rule detail: {api_base}/eligibility-rules/{drift_eligibility_rule['id']}"
    )
    print(
        f"- qualified device profile detail: {api_base}/device-profiles/{qualified_device_profile['id']}"
    )
    print(
        f"- ineligible device profile detail: {api_base}/device-profiles/{ineligible_device_profile['id']}"
    )
    print(f"- qualified task detail: {api_base}/tasks/{qualified_task['id']}")
    print(f"- drift task detail: {api_base}/tasks/{drift_task['id']}")
    print(f"- feedback detail: {api_base}/feedback/{feedback['id']}")
    print("")
    print("Notes")
    print("- Use the homepage Current Actor selector to switch between the seeded developer and tester.")
    print("- The seeded qualified campaign gives you one passing and one failing device profile for qualification checks.")
    print("- Use the qualified campaign task form to verify assignment preview and ineligible assignment blocking.")
    print("- The drift campaign already contains an assigned task whose qualification now drifts after rule changes.")
    print("- The seeded project and both campaigns are owned by the developer actor.")
    print("- Both seeded device profiles belong to the tester actor.")
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
        qualified_campaign = post_resource(
            config=config,
            path="/campaigns",
            payload={
                "project_id": project["id"],
                **payloads["qualified_campaign"],
            },
            actor_id=developer_account["id"],
        )
        drift_campaign = post_resource(
            config=config,
            path="/campaigns",
            payload={
                "project_id": project["id"],
                **payloads["drift_campaign"],
            },
            actor_id=developer_account["id"],
        )
        safety = post_resource(
            config=config,
            path=f"/campaigns/{qualified_campaign['id']}/safety",
            payload=payloads["safety"],
            actor_id=developer_account["id"],
        )
        qualified_eligibility_rule = post_resource(
            config=config,
            path=f"/campaigns/{qualified_campaign['id']}/eligibility-rules",
            payload=payloads["eligibility_rule"],
            actor_id=developer_account["id"],
        )
        drift_eligibility_rule = post_resource(
            config=config,
            path=f"/campaigns/{drift_campaign['id']}/eligibility-rules",
            payload=payloads["eligibility_rule"],
            actor_id=developer_account["id"],
        )
        qualified_device_profile = post_resource(
            config=config,
            path="/device-profiles",
            payload=payloads["qualified_device_profile"],
            actor_id=tester_account["id"],
        )
        ineligible_device_profile = post_resource(
            config=config,
            path="/device-profiles",
            payload=payloads["ineligible_device_profile"],
            actor_id=tester_account["id"],
        )
        qualified_task = post_resource(
            config=config,
            path=f"/campaigns/{qualified_campaign['id']}/tasks",
            payload={
                **payloads["qualified_task"],
                "device_profile_id": qualified_device_profile["id"],
            },
            actor_id=developer_account["id"],
        )
        drift_task = post_resource(
            config=config,
            path=f"/campaigns/{drift_campaign['id']}/tasks",
            payload={
                **payloads["drift_task"],
                "device_profile_id": qualified_device_profile["id"],
            },
            actor_id=developer_account["id"],
        )
        feedback = post_resource(
            config=config,
            path=f"/tasks/{qualified_task['id']}/feedback",
            payload=payloads["feedback"],
            actor_id=tester_account["id"],
        )
        patch_resource(
            config=config,
            path=f"/eligibility-rules/{drift_eligibility_rule['id']}",
            payload={
                "platform": "android",
                "os_name": "Android",
            },
            actor_id=developer_account["id"],
        )

        print_summary(
            config=config,
            health=health,
            developer_account=developer_account,
            tester_account=tester_account,
            project=project,
            qualified_campaign=qualified_campaign,
            drift_campaign=drift_campaign,
            safety=safety,
            qualified_eligibility_rule=qualified_eligibility_rule,
            drift_eligibility_rule=drift_eligibility_rule,
            qualified_device_profile=qualified_device_profile,
            ineligible_device_profile=ineligible_device_profile,
            qualified_task=qualified_task,
            drift_task=drift_task,
            feedback=feedback,
        )
        return 0
    except SeedWorkflowError as exc:
        print(f"Seed workflow failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
