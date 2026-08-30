# tts-cli

`tts-cli` — read-only CLI для проверки сейвов и локального кэша Tabletop
Simulator. Стабильный JSON-отчёт предназначен для человека, AI-агента или CI,
которым нужны доказательства без запуска игры и изменения сейва.

[English](README.md)

## Установка

Требуются Python 3.12+ и [uv](https://docs.astral.sh/uv/). Установка
опубликованной версии из PyPI:

```console
uv tool install tabletop-simulator-cli==0.1.1
tts --help
```

Однократный запуск без постоянной установки:

```console
uvx --from tabletop-simulator-cli==0.1.1 tts --help
```

Для разработки из исходников:

```console
git clone https://github.com/rusliksu/tts-cli.git
cd tts-cli
uv sync --locked
```

## Аудит сейва

```console
uv run tts assets audit <save.json> [--mods-dir <path>] [--json]
```

Без `--mods-dir` CLI ищет ближайший `Mods` в пути сейва, затем соседний `Mods`
рядом с `Saves`.

- `0`: аудит выполнен без findings;
- `1`: полный отчёт содержит `not_found_in_cache` или `unverified`;
- `2`: ошибка входа или локальной конфигурации;
- `3`: неожиданная внутренняя ошибка.

`not_found_in_cache` не означает, что внешний URL недоступен: сеть в ходе
аудита вообще не используется.

## Границы безопасности

- Никаких сетевых запросов, скачивания, удаления кэша и изменения сейва.
- Lua и произвольный текст не сканируются на URL.
- Реальные Workshop-сейвы и игровые ассеты отсутствуют в репозитории.

Контракт JSON: [`audit-report-v1.schema.json`](kitty-specs/tts-assets-audit-01M1945C/contracts/audit-report-v1.schema.json).
Исследование аналогов: [docs/research/existing-tools.md](docs/research/existing-tools.md).
