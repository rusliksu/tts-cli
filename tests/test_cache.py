from __future__ import annotations

from pathlib import Path

from tts_cli.cache import NON_ALNUM, build_cache_index, match_asset
from tts_cli.models import ExtractedAsset, Usage


def _asset(url: str, *types: str) -> ExtractedAsset:
    usages = tuple(
        Usage(f"/{index}", f"Field{index}", value) for index, value in enumerate(types)
    )
    return ExtractedAsset(url, tuple(sorted(types)), usages)


def _touch(mods: Path, directory: str, name: str) -> None:
    target = mods / directory / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.touch()


def test_matches_steam_ugc_key_independently_of_hostname(tmp_path: Path) -> None:
    _touch(tmp_path, "Images", "cached-123ABCDEF.png")
    index = build_cache_index(tmp_path)

    status, match = match_asset(
        _asset("https://cdn.example.invalid/ugc/123/abcdef/?x=1", "image"), index
    )

    assert status == "cached"
    assert match.method == "steam_ugc_key"
    assert match.confidence == "high"
    assert match.relative_path == "Images/cached-123ABCDEF.png"


def test_matches_exact_normalized_name(tmp_path: Path) -> None:
    url = "https://example.invalid/image.png?size=2"
    _touch(tmp_path, "Images", NON_ALNUM.sub("", url))

    status, match = match_asset(_asset(url, "image"), build_cache_index(tmp_path))

    assert status == "cached"
    assert match.method == "exact_normalized_name"
    assert match.confidence == "medium"


def test_multiple_candidates_are_unverified(tmp_path: Path) -> None:
    url = "https://example.invalid/shared-resource"
    name = NON_ALNUM.sub("", url)
    _touch(tmp_path, "Images", name)
    _touch(tmp_path, "Models", name)

    status, match = match_asset(
        _asset(url, "image", "model"), build_cache_index(tmp_path)
    )

    assert status == "unverified"
    assert match.method == "ambiguous"
    assert match.relative_path is None
    assert match.candidate_count == 2


def test_unknown_only_asset_is_not_searched(tmp_path: Path) -> None:
    status, match = match_asset(
        _asset("https://example.invalid/mystery", "unknown"),
        build_cache_index(tmp_path),
    )

    assert status == "unverified"
    assert match.method == "none"
    assert match.candidate_count == 0
