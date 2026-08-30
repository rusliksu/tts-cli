from __future__ import annotations

import json

from tts_cli.models import ASSET_STATUSES, ASSET_TYPES, AuditReport


def render_json(report: AuditReport) -> str:
    return (
        json.dumps(report.to_dict(), sort_keys=True, ensure_ascii=False, indent=2)
        + "\n"
    )


def render_human(report: AuditReport) -> str:
    summary = report.summary
    statuses = ", ".join(
        f"{status}={summary.by_status[status]}" for status in ASSET_STATUSES
    )
    types = ", ".join(
        f"{asset_type}={summary.by_type[asset_type]}" for asset_type in ASSET_TYPES
    )
    return "\n".join(
        [
            f"Save: {report.save_name} ({report.save_file})",
            f"Objects: {summary.objects}",
            f"Lua scripts: {summary.lua_scripts}",
            f"Assets: {summary.assets}",
            f"Status: {statuses}",
            f"Types: {types}",
            "",
        ]
    )
