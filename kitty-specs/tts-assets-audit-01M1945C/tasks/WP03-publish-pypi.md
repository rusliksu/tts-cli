---
work_package_id: "WP03"
title: "Опубликовать tts-cli 0.1.0 в PyPI"
dependencies:
  - "WP02"
requirement_refs:
  - "FR-011"
  - "FR-012"
  - "FR-013"
planning_base_branch: "main"
merge_target_branch: "main"
branch_strategy: "Изменения готовятся в codex/tts-cli-pypi-publish и попадают в main только через PR."
subtasks:
  - "T010"
  - "T011"
  - "T012"
  - "T013"
phase: "PyPI Trusted Publishing"
assignee: ""
agent: "codex"
shell_pid: ""
history:
  - timestamp: "2026-08-30T12:30:00Z"
    agent: "codex"
    action: "Руслан явно разрешил начать самостоятельный этап публикации в PyPI."
  - timestamp: "2026-08-30T12:50:00Z"
    agent: "codex"
    action: "Baseline one-shot Trusted Publishing одобрен Русланом."
---

# Рабочий пакет WP03: опубликовать `tts-cli==0.1.0` в PyPI

## Реализация

1. Добавить pinned one-shot `.github/workflows/publish-pypi.yml` для сборки из
   `v0.1.0` на SHA `54af70be429ea0aa49922b9984af3e099e66cd54`,
   строгой проверки wheel/sdist, smoke-установки и OIDC-публикации.
2. Обновить английский и русский README установкой через PyPI.
3. Локально проверить tests, lint, build, metadata, состав архивов и console
   script; затем провести ветку через PR в `main`.
4. Создать GitHub Environment `pypi` и PyPI pending Trusted Publisher с точной
   привязкой к `rusliksu/tts-cli` и publish workflow.
5. Перед dispatch повторить проверку свободного имени, запустить workflow,
   проверить PyPI API и чистую установку.

## Границы

- Не создавать API token или GitHub secret для PyPI.
- Не пересобирать пакет из плавающего `main`; источник только тег `v0.1.0`.
- Не публиковать в TestPyPI и не менять продуктовый код аудита.
- Не повторять dispatch после успешной публикации `0.1.0`.
- Не добавлять `release.published`, произвольный tag input или `skip-existing`;
  будущая release automation требует отдельного изменения.

## Проверки

- `uv run --frozen --group dev pytest`
- `uv run --with ruff==0.16.5 ruff check src tests`
- `uv run --with ruff==0.16.5 ruff format --check src tests`
- `uv build --no-sources`
- `uvx --from twine twine check --strict dist/*`
- install smoke wheel в новом временном окружении
- remote tag `v0.1.0`, checkout и ожидаемый SHA совпадают
- concurrency не отменяет активный publish run; повтор блокируется preflight
- GitHub Actions run conclusion `success`
- `https://pypi.org/pypi/tts-cli/json` содержит версию `0.1.0`

## Gate

Материальное расширение scope подтверждено. Фактическая публикация разрешена,
но выполняется только после успешных локальных, PR и Trusted Publisher проверок.
