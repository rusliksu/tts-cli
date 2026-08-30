from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from tts_cli.models import CacheMatch, ExtractedAsset

CACHE_DIRECTORIES = {
    "assetbundle": "Assetbundles",
    "audio": "Audio",
    "image": "Images",
    "model": "Models",
    "pdf": "PDF",
}
UGC_PATTERN = re.compile(r"/ugc/(\d+)/([a-f0-9]+)(?:/|$)", re.IGNORECASE)
NON_ALNUM = re.compile(r"[^A-Za-z0-9]")


@dataclass(frozen=True, slots=True)
class CacheFile:
    name: str
    relative_path: str


def build_cache_index(mods_dir: Path) -> dict[str, tuple[CacheFile, ...]]:
    index: dict[str, tuple[CacheFile, ...]] = {}
    for asset_type, directory_name in CACHE_DIRECTORIES.items():
        directory = mods_dir / directory_name
        files = []
        if directory.is_dir():
            for path in directory.rglob("*"):
                if path.is_file():
                    files.append(
                        CacheFile(path.name, path.relative_to(mods_dir).as_posix())
                    )
        index[asset_type] = tuple(sorted(files, key=lambda item: item.relative_path))
    return index


def _known_candidates(
    asset: ExtractedAsset, index: dict[str, tuple[CacheFile, ...]]
) -> tuple[CacheFile, ...]:
    candidates = {
        item.relative_path: item
        for asset_type in asset.types
        if asset_type != "unknown"
        for item in index.get(asset_type, ())
    }
    return tuple(candidates[path] for path in sorted(candidates))


def _result(method: str, candidates: tuple[CacheFile, ...]) -> tuple[str, CacheMatch]:
    if len(candidates) == 1:
        confidence = "high" if method == "steam_ugc_key" else "medium"
        return "cached", CacheMatch(method, confidence, candidates[0].relative_path, 1)
    if len(candidates) > 1:
        return "unverified", CacheMatch("ambiguous", "none", None, len(candidates))
    return "not_found_in_cache", CacheMatch("none", "none", None, 0)


def match_asset(
    asset: ExtractedAsset, index: dict[str, tuple[CacheFile, ...]]
) -> tuple[str, CacheMatch]:
    known_types = set(asset.types) - {"unknown"}
    if not known_types:
        return "unverified", CacheMatch("none", "none", None, 0)

    files = _known_candidates(asset, index)
    path = urlsplit(asset.url).path
    ugc_match = UGC_PATTERN.search(path)
    if ugc_match:
        key = f"{ugc_match.group(1)}{ugc_match.group(2)}".casefold()
        matches = tuple(item for item in files if key in item.name.casefold())
        return _result("steam_ugc_key", matches)

    normalized_url = NON_ALNUM.sub("", asset.url).casefold()
    matches = tuple(
        item
        for item in files
        if NON_ALNUM.sub("", item.name).casefold() == normalized_url
    )
    return _result("exact_normalized_name", matches)
