#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from http.cookiejar import CookieJar
from typing import Any
from urllib import error, request


class SmokeCheckError(Exception):
    pass


@dataclass(frozen=True)
class SmokeConfig:
    api_base_url: str
    frontend_base_url: str
    timeout_seconds: float
    require_database_configured: bool
    require_session_only: bool


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: dict[str, str]
    text: str

    def json(self) -> dict[str, Any]:
        return json.loads(self.text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a minimal public beta smoke check against frontend and backend.",
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
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds. Default: %(default)s",
    )
    parser.add_argument(
        "--require-database-configured",
        action="store_true",
        help="Fail if backend health reports database_configured=false.",
    )
    parser.add_argument(
        "--require-session-only",
        action="store_true",
        help="Fail if backend health reports auth_mode other than session_only.",
    )
    return parser


def normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def build_config(args: argparse.Namespace) -> SmokeConfig:
    return SmokeConfig(
        api_base_url=normalize_base_url(args.api_base_url),
        frontend_base_url=normalize_base_url(args.frontend_base_url),
        timeout_seconds=args.timeout_seconds,
        require_database_configured=args.require_database_configured,
        require_session_only=args.require_session_only,
    )


def make_opener() -> request.OpenerDirector:
    return request.build_opener(request.HTTPCookieProcessor(CookieJar()))


def perform_request(
    *,
    method: str,
    url: str,
    timeout_seconds: float,
    opener: request.OpenerDirector | None = None,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> HttpResponse:
    body = None
    request_headers = {"Accept": "application/json"}
    if headers is not None:
        request_headers.update(headers)

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    req = request.Request(url, method=method, data=body, headers=request_headers)
    opener_to_use = opener or request.build_opener()

    try:
        with opener_to_use.open(req, timeout=timeout_seconds) as response:
            text = response.read().decode("utf-8")
            return HttpResponse(
                status_code=response.getcode(),
                headers=dict(response.headers.items()),
                text=text,
            )
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8")
        return HttpResponse(
            status_code=exc.code,
            headers=dict(exc.headers.items()),
            text=text,
        )
    except error.URLError as exc:
        raise SmokeCheckError(f"{method} {url} failed: {exc.reason}") from exc


def assert_backend_health(config: SmokeConfig) -> dict[str, Any]:
    response = perform_request(
        method="GET",
        url=f"{config.api_base_url}/health",
        timeout_seconds=config.timeout_seconds,
    )
    if response.status_code != 200:
        raise SmokeCheckError(
            f"Backend health check failed with HTTP {response.status_code}: {response.text}"
        )

    payload = response.json()
    if payload.get("status") != "ok":
        raise SmokeCheckError(f"Backend health status is not ok: {payload}")

    if config.require_database_configured and not payload.get("database_configured"):
        raise SmokeCheckError(
            "Backend health reports database_configured=false, but --require-database-configured was set."
        )

    if config.require_session_only and payload.get("auth_mode") != "session_only":
        raise SmokeCheckError(
            "Backend health reports auth_mode other than session_only."
        )

    return payload


def assert_frontend_shell(config: SmokeConfig) -> None:
    response = perform_request(
        method="GET",
        url=f"{config.frontend_base_url}/",
        timeout_seconds=config.timeout_seconds,
        headers={"Accept": "text/html"},
    )
    if response.status_code != 200:
        raise SmokeCheckError(
            f"Frontend shell check failed with HTTP {response.status_code}: {response.text[:200]}"
        )

    lowered = response.text.lower()
    if "<html" not in lowered and "__nuxt" not in lowered:
        raise SmokeCheckError("Frontend root did not return expected HTML content.")


def assert_auth_and_write_smoke(config: SmokeConfig) -> dict[str, str]:
    opener = make_opener()
    unique_suffix = str(int(time.time() * 1000))
    email = f"ops-smoke-{unique_suffix}@example.com"
    password = "supersecret"

    register_response = perform_request(
        method="POST",
        url=f"{config.api_base_url}/auth/register",
        timeout_seconds=config.timeout_seconds,
        opener=opener,
        payload={
            "display_name": f"Ops Smoke Dual Role {unique_suffix}",
            "role": "developer",
            "roles": ["developer", "tester"],
            "email": email,
            "password": password,
            "locale": "zh-TW",
        },
    )
    if register_response.status_code != 201:
        raise SmokeCheckError(
            f"Register smoke failed with HTTP {register_response.status_code}: {register_response.text}"
        )

    register_payload = register_response.json()
    account_id = register_payload["account"]["id"]
    if register_payload["account"].get("roles") != ["developer", "tester"]:
        raise SmokeCheckError(
            "Register smoke did not return the expected dual-role account payload."
        )

    me_response = perform_request(
        method="GET",
        url=f"{config.api_base_url}/auth/me",
        timeout_seconds=config.timeout_seconds,
        opener=opener,
    )
    if me_response.status_code != 200:
        raise SmokeCheckError(
            f"Auth me smoke failed with HTTP {me_response.status_code}: {me_response.text}"
        )
    if me_response.json()["account"].get("roles") != ["developer", "tester"]:
        raise SmokeCheckError(
            "Auth me smoke did not preserve the expected dual-role account payload."
        )

    project_response = perform_request(
        method="POST",
        url=f"{config.api_base_url}/projects",
        timeout_seconds=config.timeout_seconds,
        opener=opener,
        payload={
            "name": f"Ops Smoke Project {unique_suffix}",
            "description": "Project created by the public beta smoke script.",
        },
    )
    if project_response.status_code != 201:
        raise SmokeCheckError(
            f"Project create smoke failed with HTTP {project_response.status_code}: {project_response.text}"
        )

    project_payload = project_response.json()
    if project_payload.get("owner_account_id") != account_id:
        raise SmokeCheckError(
            "Session-backed project create did not assign the expected owner_account_id."
        )

    logout_response = perform_request(
        method="POST",
        url=f"{config.api_base_url}/auth/logout",
        timeout_seconds=config.timeout_seconds,
        opener=opener,
    )
    if logout_response.status_code != 204:
        raise SmokeCheckError(
            f"Logout smoke failed with HTTP {logout_response.status_code}: {logout_response.text}"
        )

    me_after_logout_response = perform_request(
        method="GET",
        url=f"{config.api_base_url}/auth/me",
        timeout_seconds=config.timeout_seconds,
        opener=opener,
    )
    if me_after_logout_response.status_code != 401:
        raise SmokeCheckError(
            "Auth me after logout should return 401 unauthenticated."
        )

    return {
        "account_id": account_id,
        "project_id": project_payload["id"],
        "email": email,
        "roles": "developer,tester",
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = build_config(args)

    try:
        health = assert_backend_health(config)
        assert_frontend_shell(config)
        smoke_result = assert_auth_and_write_smoke(config)
    except SmokeCheckError as exc:
        print(f"Public beta smoke failed: {exc}", file=sys.stderr)
        return 1

    print("Public beta smoke succeeded.")
    print(f"Backend health: {json.dumps(health, ensure_ascii=True)}")
    print(
        "Auth/write smoke result: "
        f"{json.dumps(smoke_result, ensure_ascii=True, sort_keys=True)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
