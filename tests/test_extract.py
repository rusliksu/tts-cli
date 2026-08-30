from __future__ import annotations

import json
from pathlib import Path

from tts_cli.extract import extract_resources

FIXTURES = Path(__file__).parent / "fixtures"


def test_extracts_and_deduplicates_structured_urls() -> None:
    save = json.loads((FIXTURES / "synthetic_save.json").read_text())

    result = extract_resources(save)

    assert result.objects == 3
    assert result.lua_scripts == 0
    assert len(result.assets) == 2
    shared = result.assets[0]
    assert shared.types == ("image", "model")
    assert [usage.pointer for usage in shared.usages] == [
        "/ObjectStates/1/ImageURL",
        "/ObjectStates/2/MeshURL",
    ]


def test_escapes_json_pointer_and_ignores_arbitrary_text() -> None:
    result = extract_resources(
        {
            "Name": "Root",
            "LuaScript": "https://ignored.invalid/script",
            "Item1": "https://ignored.invalid/item",
            "a/b~cURL": "https://example.invalid/unknown",
        }
    )

    assert result.objects == 1
    assert result.lua_scripts == 1
    assert len(result.assets) == 1
    assert result.assets[0].types == ("unknown",)
    assert result.assets[0].usages[0].pointer == "/a~1b~0cURL"


def test_ignores_local_paths_and_non_http_schemes() -> None:
    result = extract_resources(
        {
            "ImageURL": "file:///tmp/local.png",
            "MeshURL": "C:/local.obj",
            "PDFUrl": "ftp://example.invalid/file.pdf",
        }
    )

    assert result.assets == ()
