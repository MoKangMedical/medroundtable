#!/usr/bin/env python3
"""Small helper for SecondMe Develop control-plane operations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

API_BASE = "https://app.mindos.com/gate/lab/api"
AUTH_URL_BASE = "https://develop.second.me/auth/cli"


def normalize_token(token: str) -> str:
    return token.split("|", 1)[0].strip()


def read_json_file(path: str | None) -> Any:
    if not path:
        return None
    return json.loads(Path(path).read_text())


def build_headers(token: str | None) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
    }
    if token:
        normalized = normalize_token(token)
        # Different Develop routes may accept either or both forms.
        headers["Authorization"] = f"Bearer {normalized}"
        headers["token"] = normalized
    return headers


def api_request(method: str, path: str, token: str | None = None, body: Any = None, params: list[str] | None = None) -> requests.Response:
    url = f"{API_BASE}{path if path.startswith('/') else '/' + path}"
    query: dict[str, str] = {}
    for item in params or []:
        if "=" not in item:
            raise SystemExit(f"Invalid --query value: {item}")
        key, value = item.split("=", 1)
        query[key] = value
    return requests.request(
        method=method.upper(),
        url=url,
        headers=build_headers(token),
        json=body,
        params=query or None,
        timeout=30,
    )


def handle_auth_create(_: argparse.Namespace) -> int:
    response = requests.post(f"{API_BASE}/auth/cli/session", timeout=30)
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data", {})
    result = {
        "sessionId": data.get("sessionId"),
        "userCode": data.get("userCode"),
        "expiresAt": data.get("expiresAt"),
        "authUrl": f"{AUTH_URL_BASE}?session={data.get('sessionId', '')}",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def handle_auth_poll(args: argparse.Namespace) -> int:
    response = requests.get(f"{API_BASE}/auth/cli/session/{args.session_id}/poll", timeout=30)
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data", {})
    if "token" in data and isinstance(data["token"], str):
        data["token"] = normalize_token(data["token"])
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def handle_request(args: argparse.Namespace) -> int:
    body = read_json_file(args.body_file) if args.body_file else (json.loads(args.body) if args.body else None)
    response = api_request(args.method, args.path, token=args.token, body=body, params=args.query)
    print(f"HTTP {response.status_code}", file=sys.stderr)
    try:
        parsed = response.json()
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except ValueError:
        print(response.text)
    return 0 if response.ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SecondMe Develop helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser("auth", help="CLI auth helpers")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command", required=True)

    auth_create = auth_subparsers.add_parser("create", help="Create CLI auth session")
    auth_create.set_defaults(func=handle_auth_create)

    auth_poll = auth_subparsers.add_parser("poll", help="Poll CLI auth session")
    auth_poll.add_argument("--session-id", required=True)
    auth_poll.set_defaults(func=handle_auth_poll)

    request_parser = subparsers.add_parser("request", help="Generic Develop API request")
    request_parser.add_argument("method", choices=["get", "post"])
    request_parser.add_argument("path", help="API path such as /integrations/list")
    request_parser.add_argument("--token")
    request_parser.add_argument("--body")
    request_parser.add_argument("--body-file")
    request_parser.add_argument("--query", action="append", default=[])
    request_parser.set_defaults(func=handle_request)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
