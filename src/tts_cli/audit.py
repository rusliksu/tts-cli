from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tts_cli.cache import build_cache_index, match_asset
from tts_cli.extract import extract_resources
from tts_cli.models import ASSET_STATUSES, ASSET_TYPES, Asset, AuditReport, Summary


class AuditInputError(Exception):
    """Expected input or local configuration error."""


def discover_mods_dir(save_path: Path, explicit: Path | None = None) -> Path:
    if explicit is not None:
        if not explicit.is_dir():
            raise AuditInputError(f"Mods directory does not exist: {explicit.name}")
        return explicit

    for ancestor in save_path.parents:
        if ancestor.name.casefold() == "mods" and ancestor.is_dir():
            return ancestor
    for ancestor in save_path.parents:
        candidate = ancestor / "Mods"
        if candidate.is_dir():
            return candidate
    raise AuditInputError("Mods directory was not found; pass --mods-dir")


def _load_save(save_path: Path) -> dict[str, Any]:
    if not save_path.is_file():
        raise AuditInputError(f"save file does not exist: {save_path.name}")
    try:
        with save_path.open("r", encoding="utf-8-sig") as stream:
            value = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AuditInputError(f"cannot read JSON save: {save_path.name}") from error
    if not isinstance(value, dict):
        raise AuditInputError("save root must be a JSON object")
    return value


def audit_file(save_path: Path, mods_dir: Path | None = None) -> AuditReport:
    save_path = save_path.expanduser()
    save = _load_save(save_path)
    resolved_mods = discover_mods_dir(save_path, mods_dir)
    extracted = extract_resources(save)
    cache_index = build_cache_index(resolved_mods)

    assets = []
    for extracted_asset in extracted.assets:
        status, cache_match = match_asset(extracted_asset, cache_index)
        assets.append(
            Asset(
                url=extracted_asset.url,
                types=extracted_asset.types,
                usages=extracted_asset.usages,
                status=status,
                cache_match=cache_match,
            )
        )

    by_status = {status: 0 for status in ASSET_STATUSES}
    by_type = {asset_type: 0 for asset_type in ASSET_TYPES}
    for asset in assets:
        by_status[asset.status] += 1
        for asset_type in asset.types:
            by_type[asset_type] += 1

    save_name = save.get("SaveName")
    if not isinstance(save_name, str) or not save_name.strip():
        save_name = save_path.stem
    summary = Summary(
        objects=extracted.objects,
        lua_scripts=extracted.lua_scripts,
        assets=len(assets),
        by_status=by_status,
        by_type=by_type,
    )
    return AuditReport(save_path.name, save_name, summary, tuple(assets))
