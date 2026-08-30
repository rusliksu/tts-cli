from __future__ import annotations

import json
from pathlib import Path

import pytest

from tts_cli.cache import NON_ALNUM
from tts_cli.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
CONTRACTS = (
    Path(__file__).parents[1]
    / "kitty-specs"
    / "tts-assets-audit-01M1945C"
    / "contracts"
)


def _mods_for_synthetic(tmp_path: Path) -> Path:
    mods = tmp_path / "Mods"
    (mods / "Images").mkdir(parents=True)
    (mods / "Models").mkdir()
    (mods / "Images" / "cache-123ABCDEF.png").touch()
    shared = NON_ALNUM.sub("", "https://example.invalid/shared-resource")
    (mods / "Images" / shared).touch()
    (mods / "Models" / shared).touch()
    return mods


def test_json_output_matches_golden_bytes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mods = _mods_for_synthetic(tmp_path)

    code = main(
        [
            "assets",
            "audit",
            str(FIXTURES / "synthetic_save.json"),
            "--mods-dir",
            str(mods),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert code == 1
    assert captured.err == ""
    assert captured.out == (CONTRACTS / "audit-report-v1.example.json").read_text()


def test_empty_save_has_exit_zero_and_empty_golden(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mods = tmp_path / "Mods"
    mods.mkdir()

    code = main(
        [
            "assets",
            "audit",
            str(FIXTURES / "empty_save.json"),
            "--mods-dir",
            str(mods),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert (
        captured.out == (CONTRACTS / "audit-report-v1.empty.example.json").read_text()
    )


def test_human_summary_has_same_counts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mods = _mods_for_synthetic(tmp_path)

    code = main(
        [
            "assets",
            "audit",
            str(FIXTURES / "synthetic_save.json"),
            "--mods-dir",
            str(mods),
        ]
    )

    output = capsys.readouterr().out
    assert code == 1
    assert "Objects: 3" in output
    assert "Lua scripts: 0" in output
    assert "Assets: 2" in output
    assert "cached=1" in output
    assert "unverified=1" in output
    assert "image=2" in output
    assert "model=1" in output


def test_mutated_ugc_hash_is_not_found(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mods = _mods_for_synthetic(tmp_path)
    save = json.loads((FIXTURES / "synthetic_save.json").read_text())
    save["ObjectStates"][0]["CustomImage"]["ImageURL"] = (
        "https://example.invalid/ugc/123/ABCDEE/"
    )
    mutated = tmp_path / "mutated.json"
    mutated.write_text(json.dumps(save), encoding="utf-8")

    code = main(["assets", "audit", str(mutated), "--mods-dir", str(mods), "--json"])

    report = json.loads(capsys.readouterr().out)
    assert code == 1
    mutated_asset = next(
        asset for asset in report["assets"] if asset["url"].endswith("/ABCDEE/")
    )
    assert mutated_asset["status"] == "not_found_in_cache"


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["assets", "audit", "missing.json", "--mods-dir", "missing-mods"],
    ],
)
def test_expected_errors_use_exit_two(
    args: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(args) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("error: ")


def test_broken_json_uses_exit_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    save = tmp_path / "broken.json"
    save.write_text("{", encoding="utf-8")
    mods = tmp_path / "Mods"
    mods.mkdir()

    assert main(["assets", "audit", str(save), "--mods-dir", str(mods)]) == 2
    assert capsys.readouterr().out == ""


def test_discovers_sibling_mods_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    saves = tmp_path / "Saves"
    saves.mkdir()
    mods = tmp_path / "Mods"
    mods.mkdir()
    save = saves / "empty.json"
    save.write_text((FIXTURES / "empty_save.json").read_text(), encoding="utf-8")

    assert main(["assets", "audit", str(save), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["summary"]["assets"] == 0


def test_unexpected_error_uses_exit_three(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("private details")

    monkeypatch.setattr("tts_cli.cli.audit_file", fail)

    assert main(["assets", "audit", "save.json", "--mods-dir", "Mods"]) == 3
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: internal error\n"
