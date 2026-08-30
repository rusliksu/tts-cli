from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from tts_cli.models import ExtractedAsset, Usage

KNOWN_FIELDS = {
    "faceurl": "image",
    "backurl": "image",
    "imageurl": "image",
    "imagesecondaryurl": "image",
    "diffuseurl": "image",
    "normalurl": "image",
    "tableurl": "image",
    "skyurl": "image",
    "meshurl": "model",
    "colliderurl": "model",
    "pdfurl": "pdf",
    "currentaudiourl": "audio",
    "assetbundleurl": "assetbundle",
}


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    assets: tuple[ExtractedAsset, ...]
    objects: int
    lua_scripts: int


def _pointer_token(value: object) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _is_http_url(value: str) -> bool:
    parsed = urlsplit(value)
    return parsed.scheme.casefold() in {"http", "https"} and bool(parsed.netloc)


def extract_resources(root: Any) -> ExtractionResult:
    usages_by_url: dict[str, list[Usage]] = {}
    objects = 0
    lua_scripts = 0

    def visit(value: Any, pointer: str) -> None:
        nonlocal objects, lua_scripts

        if isinstance(value, dict):
            if isinstance(value.get("Name"), str) and value["Name"].strip():
                objects += 1
            if isinstance(value.get("LuaScript"), str) and value["LuaScript"].strip():
                lua_scripts += 1

            for field, child in value.items():
                child_pointer = f"{pointer}/{_pointer_token(field)}"
                field_key = str(field).casefold()
                inferred_type = KNOWN_FIELDS.get(field_key)
                if inferred_type is None and field_key.endswith("url"):
                    inferred_type = "unknown"
                if inferred_type and isinstance(child, str) and _is_http_url(child):
                    usages_by_url.setdefault(child, []).append(
                        Usage(child_pointer, str(field), inferred_type)
                    )
                visit(child, child_pointer)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{pointer}/{index}")

    visit(root, "")

    assets = []
    for url in sorted(usages_by_url):
        usages = tuple(sorted(set(usages_by_url[url])))
        types = tuple(sorted({usage.inferred_type for usage in usages}))
        assets.append(ExtractedAsset(url, types, usages))
    return ExtractionResult(tuple(assets), objects, lua_scripts)
