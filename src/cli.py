from __future__ import annotations

import argparse
import json

from sqlmodel import Session

from src.config import get_settings
from src.database import engine, init_db
from src.integrations.youtube.oauth import get_authorization_url
from src.integrations.youtube.status import get_connection_status


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))


def youtube_status_cmd(args: argparse.Namespace) -> None:
    settings = get_settings()
    init_db()

    with Session(engine) as session:
        _print(get_connection_status(session, settings, account_key=args.account_key))


def youtube_auth_url_cmd(args: argparse.Namespace) -> None:
    settings = get_settings()
    _print(get_authorization_url(settings, account_key=args.account_key))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="backend")
    subparsers = parser.add_subparsers(dest="command", required=True)

    youtube = subparsers.add_parser("youtube")
    youtube_sub = youtube.add_subparsers(dest="youtube_command", required=True)

    status = youtube_sub.add_parser("status", help="Verify YouTube OAuth connection")
    status.add_argument("--account-key", default="default")
    status.set_defaults(func=youtube_status_cmd)

    auth_url = youtube_sub.add_parser(
        "auth-url",
        help="Generate OAuth authorization URL",
    )
    auth_url.add_argument("--account-key", default="default")
    auth_url.set_defaults(func=youtube_auth_url_cmd)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
