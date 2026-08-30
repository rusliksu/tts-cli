from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tts_cli.audit import AuditInputError, audit_file
from tts_cli.render import render_human, render_json


class ArgumentError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ArgumentError(message)


def _parser() -> Parser:
    parser = Parser(prog="tts")
    commands = parser.add_subparsers(dest="command", required=True)
    assets = commands.add_parser("assets")
    asset_commands = assets.add_subparsers(dest="assets_command", required=True)
    audit = asset_commands.add_parser("audit")
    audit.add_argument("save", type=Path)
    audit.add_argument("--mods-dir", type=Path)
    audit.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        report = audit_file(args.save, args.mods_dir)
        output = render_json(report) if args.json_output else render_human(report)
        sys.stdout.write(output)
        return 0 if all(asset.status == "cached" for asset in report.assets) else 1
    except (ArgumentError, AuditInputError) as error:
        sys.stderr.write(f"error: {error}\n")
        return 2
    except Exception:  # noqa: BLE001 - CLI boundary maps unexpected failures to exit 3.
        sys.stderr.write("error: internal error\n")
        return 3


def entrypoint() -> None:
    raise SystemExit(main())
