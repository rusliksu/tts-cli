from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ASSET_TYPES = ("assetbundle", "audio", "image", "model", "pdf", "unknown")
ASSET_STATUSES = ("cached", "not_found_in_cache", "unverified")


@dataclass(frozen=True, order=True, slots=True)
class Usage:
    pointer: str
    field: str
    inferred_type: str

    def to_dict(self) -> dict[str, str]:
        return {
            "pointer": self.pointer,
            "field": self.field,
            "inferred_type": self.inferred_type,
        }


@dataclass(frozen=True, slots=True)
class ExtractedAsset:
    url: str
    types: tuple[str, ...]
    usages: tuple[Usage, ...]


@dataclass(frozen=True, slots=True)
class CacheMatch:
    method: str
    confidence: str
    relative_path: str | None
    candidate_count: int

    def to_dict(self) -> dict[str, str | int | None]:
        return {
            "method": self.method,
            "confidence": self.confidence,
            "relative_path": self.relative_path,
            "candidate_count": self.candidate_count,
        }


@dataclass(frozen=True, slots=True)
class Asset:
    url: str
    types: tuple[str, ...]
    usages: tuple[Usage, ...]
    status: str
    cache_match: CacheMatch

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "types": list(self.types),
            "usages": [usage.to_dict() for usage in self.usages],
            "status": self.status,
            "cache_match": self.cache_match.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class Summary:
    objects: int
    lua_scripts: int
    assets: int
    by_status: dict[str, int]
    by_type: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "objects": self.objects,
            "lua_scripts": self.lua_scripts,
            "assets": self.assets,
            "by_status": self.by_status,
            "by_type": self.by_type,
        }


@dataclass(frozen=True, slots=True)
class AuditReport:
    save_file: str
    save_name: str
    summary: Summary
    assets: tuple[Asset, ...]
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "save": {"file": self.save_file, "name": self.save_name},
            "summary": self.summary.to_dict(),
            "assets": [asset.to_dict() for asset in self.assets],
        }
