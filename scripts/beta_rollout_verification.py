#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import public_beta_smoke as smoke


DEFAULT_PAGE_PATHS = [
    "/login",
    "/register",
    "/",
    "/dashboard",
    "/projects",
    "/campaigns",
    "/tasks",
    "/review/feedback",
]

DEFAULT_KNOWN_LIMITATIONS = [
    "deploy 前仍需先執行 Alembic upgrade head",
    "X-Actor-Id 只保留作為 local QA / seed fallback，不是正式 beta identity model",
    "active workspace role 只影響 frontend 視角，backend authorization 仍以 account roles 判斷",
    "目前 beta 僅支援 Web、Mobile Web、PWA、iOS、Android",
    "notification、search overhaul、auto matching、team/org model 尚未納入本輪 beta",
]


@dataclass(frozen=True)
class VerificationConfig:
    api_base_url: str
    frontend_base_url: str
    environment_label: str
    timeout_seconds: float
    output_dir: Path
    manual_qa_status: str
    manual_qa_note: str
    rollout_note: str
    require_database_configured: bool
    require_session_only: bool
    page_paths: list[str]
    known_limitations: list[str]


@dataclass(frozen=True)
class PageCheckResult:
    path: str
    status_code: int | None
    ok: bool
    note: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a beta rollout rehearsal and write an evidence pack with health, "
            "smoke, key page checks, and a go/no-go conclusion."
        ),
    )
    parser.add_argument(
        "--api-base-url",
        default="http://127.0.0.1:8000/api/v1",
        help="Backend API base URL. Default: %(default)s",
    )
    parser.add_argument(
        "--frontend-base-url",
        default="http://127.0.0.1:3000",
        help="Frontend app base URL. Default: %(default)s",
    )
    parser.add_argument(
        "--environment-label",
        default="local-rehearsal",
        help="Short label used in the evidence output. Default: %(default)s",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds. Default: %(default)s",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Directory for evidence output. Default: "
            "runtime_artifacts/rollout-verification/<label>-<timestamp>"
        ),
    )
    parser.add_argument(
        "--manual-qa-status",
        choices=("pending", "pass", "fail"),
        default="pending",
        help="Manual QA completion status for the rehearsal. Default: %(default)s",
    )
    parser.add_argument(
        "--manual-qa-note",
        default="",
        help="Optional manual QA note to embed in the evidence pack.",
    )
    parser.add_argument(
        "--rollout-note",
        default="",
        help="Optional rollout note or environment-specific observation.",
    )
    parser.add_argument(
        "--require-database-configured",
        action="store_true",
        help="Fail the automated gate if health reports database_configured=false.",
    )
    parser.add_argument(
        "--require-session-only",
        action="store_true",
        help="Fail the automated gate if health reports auth_mode other than session_only.",
    )
    parser.add_argument(
        "--page-path",
        action="append",
        dest="page_paths",
        default=[],
        help="Additional frontend page path to verify. Can be provided multiple times.",
    )
    parser.add_argument(
        "--known-limitation",
        action="append",
        dest="known_limitations",
        default=[],
        help="Additional known limitation line to embed in the evidence pack.",
    )
    return parser


def normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def build_output_dir(environment_label: str) -> Path:
    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    return (
        Path("/Users/lowhaijer/projects/beta-feedback-platform")
        / "runtime_artifacts"
        / "rollout-verification"
        / f"{environment_label}-{timestamp}"
    )


def build_config(args: argparse.Namespace) -> VerificationConfig:
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else build_output_dir(args.environment_label)
    )

    page_paths = list(DEFAULT_PAGE_PATHS)
    for page_path in args.page_paths:
        normalized = page_path if page_path.startswith("/") else f"/{page_path}"
        if normalized not in page_paths:
            page_paths.append(normalized)

    known_limitations = list(DEFAULT_KNOWN_LIMITATIONS)
    known_limitations.extend(item for item in args.known_limitations if item.strip())

    return VerificationConfig(
        api_base_url=normalize_base_url(args.api_base_url),
        frontend_base_url=normalize_base_url(args.frontend_base_url),
        environment_label=args.environment_label.strip() or "local-rehearsal",
        timeout_seconds=args.timeout_seconds,
        output_dir=output_dir,
        manual_qa_status=args.manual_qa_status,
        manual_qa_note=args.manual_qa_note.strip(),
        rollout_note=args.rollout_note.strip(),
        require_database_configured=args.require_database_configured,
        require_session_only=args.require_session_only,
        page_paths=page_paths,
        known_limitations=known_limitations,
    )


def check_backend_health(
    config: VerificationConfig,
) -> tuple[bool, dict[str, Any], str]:
    try:
        response = smoke.perform_request(
            method="GET",
            url=f"{config.api_base_url}/health",
            timeout_seconds=config.timeout_seconds,
        )
    except smoke.SmokeCheckError as exc:
        return False, {}, str(exc)

    note = ""
    if response.status_code != 200:
        return False, {"status_code": response.status_code, "body": response.text}, "health endpoint did not return 200"

    try:
        payload = response.json()
    except json.JSONDecodeError:
        return False, {"status_code": response.status_code, "body": response.text}, "health endpoint did not return valid JSON"

    ok = payload.get("status") == "ok"
    if not ok:
        note = "health payload status is not ok"

    if config.require_database_configured and not payload.get("database_configured"):
        ok = False
        note = "database_configured=false"

    if config.require_session_only and payload.get("auth_mode") != "session_only":
        ok = False
        note = "auth_mode is not session_only"

    return ok, payload, note


def check_frontend_pages(config: VerificationConfig) -> list[PageCheckResult]:
    results: list[PageCheckResult] = []
    for page_path in config.page_paths:
        try:
            response = smoke.perform_request(
                method="GET",
                url=f"{config.frontend_base_url}{page_path}",
                timeout_seconds=config.timeout_seconds,
                headers={"Accept": "text/html"},
            )
        except smoke.SmokeCheckError as exc:
            results.append(
                PageCheckResult(
                    path=page_path,
                    status_code=None,
                    ok=False,
                    note=str(exc),
                )
            )
            continue

        ok = response.status_code == 200
        note = "ok" if ok else f"HTTP {response.status_code}"
        if ok:
            lowered = response.text.lower()
            if "<html" not in lowered and "__nuxt" not in lowered:
                ok = False
                note = "page did not return expected HTML shell"

        results.append(
            PageCheckResult(
                path=page_path,
                status_code=response.status_code,
                ok=ok,
                note=note,
            )
        )
    return results


def run_public_beta_smoke(
    config: VerificationConfig,
) -> tuple[int, str, str, list[str]]:
    script_path = Path("/Users/lowhaijer/projects/beta-feedback-platform/scripts/public_beta_smoke.py")
    command = [
        sys.executable,
        str(script_path),
        "--api-base-url",
        config.api_base_url,
        "--frontend-base-url",
        config.frontend_base_url,
        "--timeout-seconds",
        str(config.timeout_seconds),
    ]
    if config.require_database_configured:
        command.append("--require-database-configured")
    if config.require_session_only:
        command.append("--require-session-only")

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd="/Users/lowhaijer/projects/beta-feedback-platform",
    )
    return completed.returncode, completed.stdout, completed.stderr, command


def determine_go_no_go(
    *,
    health_ok: bool,
    page_results: list[PageCheckResult],
    smoke_exit_code: int,
    manual_qa_status: str,
) -> tuple[str, list[str]]:
    blockers: list[str] = []

    if not health_ok:
        blockers.append("health gate 未通過")
    if any(not result.ok for result in page_results):
        blockers.append("關鍵頁面 shell 驗證未通過")
    if smoke_exit_code != 0:
        blockers.append("public_beta_smoke.py 未通過")
    if manual_qa_status != "pass":
        blockers.append("manual QA 尚未完成或未通過")

    if blockers:
        return "no_go", blockers

    return "go", []


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_markdown(
    *,
    config: VerificationConfig,
    started_at: datetime,
    finished_at: datetime,
    health_ok: bool,
    health_payload: dict[str, Any],
    health_note: str,
    page_results: list[PageCheckResult],
    smoke_exit_code: int,
    smoke_command: list[str],
    go_no_go: str,
    blockers: list[str],
) -> str:
    page_lines = []
    for result in page_results:
        status = "PASS" if result.ok else "FAIL"
        code = result.status_code if result.status_code is not None else "-"
        page_lines.append(f"| `{result.path}` | {status} | {code} | {result.note} |")

    limitation_lines = "\n".join(f"- {item}" for item in config.known_limitations)
    blocker_lines = "\n".join(f"- {item}" for item in blockers) if blockers else "- 無"
    manual_note = config.manual_qa_note or "未附加 manual QA 備註。"
    rollout_note = config.rollout_note or "未附加 rollout 備註。"
    health_note_text = health_note or "ok"

    return f"""# Beta Rollout Evidence Pack

## 1. Run Summary

- Environment label: `{config.environment_label}`
- Started at: `{started_at.astimezone().isoformat()}`
- Finished at: `{finished_at.astimezone().isoformat()}`
- API base URL: `{config.api_base_url}`
- Frontend base URL: `{config.frontend_base_url}`
- Manual QA status: `{config.manual_qa_status}`
- Go / No-Go: `{go_no_go}`

## 2. Health Gate

- Health gate result: `{"pass" if health_ok else "fail"}`
- Health note: `{health_note_text}`

```json
{json.dumps(health_payload, ensure_ascii=False, indent=2)}
```

## 3. Smoke Gate

- Smoke exit code: `{smoke_exit_code}`
- Smoke command:

```bash
{" ".join(smoke_command)}
```

- Raw smoke logs:
  - `smoke_stdout.txt`
  - `smoke_stderr.txt`

## 4. Key Page Checks

| Path | Result | HTTP | Note |
| --- | --- | --- | --- |
{chr(10).join(page_lines)}

## 5. Manual QA Note

{manual_note}

## 6. Known Limitations

{limitation_lines}

## 7. Rollout Note

{rollout_note}

## 8. Go / No-Go Rationale

{blocker_lines}

## 9. Related Repo Docs

- [README.md](/Users/lowhaijer/projects/beta-feedback-platform/README.md)
- [OPS_RUNBOOK.md](/Users/lowhaijer/projects/beta-feedback-platform/OPS_RUNBOOK.md)
- [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)
- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)
"""


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = build_config(args)
    config.output_dir.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now().astimezone()
    health_ok, health_payload, health_note = check_backend_health(config)
    page_results = check_frontend_pages(config)
    smoke_exit_code, smoke_stdout, smoke_stderr, smoke_command = run_public_beta_smoke(config)
    go_no_go, blockers = determine_go_no_go(
        health_ok=health_ok,
        page_results=page_results,
        smoke_exit_code=smoke_exit_code,
        manual_qa_status=config.manual_qa_status,
    )
    finished_at = datetime.now().astimezone()

    summary_payload = {
        "environment_label": config.environment_label,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "api_base_url": config.api_base_url,
        "frontend_base_url": config.frontend_base_url,
        "manual_qa_status": config.manual_qa_status,
        "go_no_go": go_no_go,
        "blockers": blockers,
        "health_ok": health_ok,
        "smoke_exit_code": smoke_exit_code,
        "page_failures": [asdict(result) for result in page_results if not result.ok],
    }

    write_json(config.output_dir / "summary.json", summary_payload)
    write_json(config.output_dir / "health.json", health_payload)
    write_json(
        config.output_dir / "page_checks.json",
        [asdict(result) for result in page_results],
    )
    (config.output_dir / "smoke_stdout.txt").write_text(smoke_stdout, encoding="utf-8")
    (config.output_dir / "smoke_stderr.txt").write_text(smoke_stderr, encoding="utf-8")
    (config.output_dir / "evidence_pack.md").write_text(
        render_markdown(
            config=config,
            started_at=started_at,
            finished_at=finished_at,
            health_ok=health_ok,
            health_payload=health_payload,
            health_note=health_note,
            page_results=page_results,
            smoke_exit_code=smoke_exit_code,
            smoke_command=smoke_command,
            go_no_go=go_no_go,
            blockers=blockers,
        ),
        encoding="utf-8",
    )

    print(f"Rollout verification finished with {go_no_go}.")
    print(f"Evidence output: {config.output_dir}")

    return 0 if go_no_go == "go" else 1


if __name__ == "__main__":
    raise SystemExit(main())
