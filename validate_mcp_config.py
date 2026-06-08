#!/usr/bin/env python3
"""
Validate the GitHub Copilot MCP configuration for this repository.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

CONFIG_FILE = Path(__file__).parent / ".vscode" / "mcp.json"


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"MCP config file not found at {path}")

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_config(config: dict) -> str:
    if not isinstance(config, dict):
        raise ValueError("MCP config must be a JSON object")

    servers = config.get("servers")
    if not isinstance(servers, dict):
        raise ValueError("Missing or invalid 'servers' object in MCP config")

    github = servers.get("github")
    if not isinstance(github, dict):
        raise ValueError("Missing 'github' server configuration in MCP config")

    server_type = github.get("type")
    if server_type != "http":
        raise ValueError("Expected github.type to be 'http'")

    url = github.get("url")
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Missing or invalid github.url")

    if not url.startswith("http://") and not url.startswith("https://"):
        raise ValueError("github.url must begin with http:// or https://")

    return url


def check_connectivity(url: str, timeout: int = 10) -> None:
    print(f"Checking MCP server connectivity to {url} ...")
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            print(f"✅ Connected successfully: HTTP {response.status}")
            return
    except HTTPError as exc:
        raise RuntimeError(f"HTTP error when connecting to {url}: {exc.code} {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to connect to {url}: {exc.reason}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the GitHub Copilot MCP server configuration."
    )
    parser.add_argument(
        "--connect",
        action="store_true",
        help="Attempt a network connection to the configured MCP server.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        config = load_config(CONFIG_FILE)
        url = validate_config(config)
        print(f"✅ MCP config is valid: {CONFIG_FILE}")

        if args.connect:
            check_connectivity(url)
            print("✅ MCP server connectivity check passed.")

        return 0
    except Exception as exc:
        print(f"❌ MCP validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
