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
) -> dict[str, Any]:
    data = None
    headers = {
        "Accept": "application/json",
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, method=method, data=data, headers=headers)

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
) -> dict[str, Any]:
    return request_json(
        method="POST",
        url=f"{config.api_base_url}{path}",
        timeout_seconds=config.timeout_seconds,
        payload=payload,
    )


def get_resource(
    *,
    config: SeedConfig,
    path: str,
) -> dict[str, Any]:
    return request_json(
        method="GET",
        url=f"{config.api_base_url}{path}",
        timeout_seconds=config.timeout_seconds,
    )


def build_seed_payloads(label: str) -> dict[str, dict[str, Any]]:
    return {
        "project": {
            "name": f"Manual QA Sandbox {label}",
            "description": (
                "Seeded demo project for local browser verification and cross-page manual QA."
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
        "device_profile": {
            "name": f"QA iPhone 15 Pro {label}",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
            "os_version": "17.4",
            "locale": "en-US",
            "notes": "Seeded by the local demo data workflow.",
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
    project: dict[str, Any],
    campaign: dict[str, Any],
    safety: dict[str, Any],
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
    print("Created records")
    print(f"- project: {project['id']} ({project['name']})")
    print(f"- campaign: {campaign['id']} ({campaign['name']})")
    print(f"- safety: {safety['id']} ({safety['source_label']})")
    print(f"- device profile: {device_profile['id']} ({device_profile['name']})")
    print(f"- task: {task['id']} ({task['title']})")
    print(f"- feedback: {feedback['id']} ({feedback['summary']})")
    print("")
    print("Frontend detail URLs")
    print(f"- project detail: {frontend}/projects/{project['id']}")
    print(f"- campaign detail: {frontend}/campaigns/{campaign['id']}")
    print(f"- device profile detail: {frontend}/device-profiles/{device_profile['id']}")
    print(f"- task detail: {frontend}/tasks/{task['id']}")
    print(f"- feedback detail: {frontend}/tasks/{task['id']}/feedback/{feedback['id']}")
    print("")
    print("API detail URLs")
    print(f"- project detail: {api_base}/projects/{project['id']}")
    print(f"- campaign detail: {api_base}/campaigns/{campaign['id']}")
    print(f"- safety detail: {api_base}/campaigns/{campaign['id']}/safety")
    print(f"- device profile detail: {api_base}/device-profiles/{device_profile['id']}")
    print(f"- task detail: {api_base}/tasks/{task['id']}")
    print(f"- feedback detail: {api_base}/feedback/{feedback['id']}")
    print("")
    print("Notes")
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

        project = post_resource(
            config=config,
            path="/projects",
            payload=payloads["project"],
        )
        campaign = post_resource(
            config=config,
            path="/campaigns",
            payload={
                "project_id": project["id"],
                **payloads["campaign"],
            },
        )
        safety = post_resource(
            config=config,
            path=f"/campaigns/{campaign['id']}/safety",
            payload=payloads["safety"],
        )
        device_profile = post_resource(
            config=config,
            path="/device-profiles",
            payload=payloads["device_profile"],
        )
        task = post_resource(
            config=config,
            path=f"/campaigns/{campaign['id']}/tasks",
            payload={
                **payloads["task"],
                "device_profile_id": device_profile["id"],
            },
        )
        feedback = post_resource(
            config=config,
            path=f"/tasks/{task['id']}/feedback",
            payload=payloads["feedback"],
        )

        print_summary(
            config=config,
            health=health,
            project=project,
            campaign=campaign,
            safety=safety,
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
