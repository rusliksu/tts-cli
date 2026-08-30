# tts-cli

[![CI](https://github.com/rusliksu/tts-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/rusliksu/tts-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Deterministic, read-only audits for Tabletop Simulator save files and the local
asset cache. The JSON output is designed for AI agents, CI jobs, and scripts
that need evidence without launching the game or rewriting a save.

[Русская версия](README.ru.md)

## Install

Python 3.12+ and [uv](https://docs.astral.sh/uv/) are required:

```console
git clone https://github.com/rusliksu/tts-cli.git
cd tts-cli
uv sync --locked
```

## Audit a save

```console
uv run tts assets audit <save.json> [--mods-dir <path>] [--json]
```

Without `--mods-dir`, the CLI looks for the nearest `Mods` directory or a
`Mods` directory next to `Saves`.

Exit codes:

- `0`: audit completed with no findings;
- `1`: full report produced with `not_found_in_cache` or `unverified` assets;
- `2`: invalid input or local configuration;
- `3`: unexpected internal error.

`not_found_in_cache` only means that the deterministic local rules did not find
a matching file. It does not mean that the remote URL is unavailable.

## Safety boundaries

- No network requests during an audit.
- No downloads, cache deletion, URL replacement, or save-file mutation.
- Lua source and arbitrary text are not scanned for URLs.
- Real Workshop saves and game assets are not included in this repository.

The machine-readable contract is documented in
[`audit-report-v1.schema.json`](kitty-specs/tts-assets-audit-01M1945C/contracts/audit-report-v1.schema.json).

## Development

```console
uv sync --locked
uv run pytest
uv run --with ruff==0.16.5 ruff check src tests
uv run --with ruff==0.16.5 ruff format --check src tests
uv build
```

See the [pilot contract](docs/pilot-baseline.md) and
[comparison with existing tools](docs/research/existing-tools.md).
