---
work_package_id: "WP01"
title: "Реализовать и проверить пилот"
dependencies: []
planning_base_branch: "codex/tts-assets-audit"
merge_target_branch: "codex/tts-assets-audit"
branch_strategy: "Артефакты планирования и реализация остаются в task-owned ветке codex/tts-assets-audit."
subtasks:
  - "T001"
  - "T002"
  - "T003"
  - "T004"
  - "T005"
phase: "Пилот v0.1"
assignee: ""
agent: "codex"
shell_pid: ""
history:
  - timestamp: "2026-08-30T00:00:00Z"
    agent: "codex"
    action: "Рабочий пакет сформирован после одобрения baseline."
---

# Рабочий пакет WP01: реализовать и проверить пилот

## Цель

Дать AI-ассистенту и человеку одну детерминированную read-only команду для
инвентаризации внешних ресурсов TTS-сейва и проверки их присутствия в локальном
кэше.

## Реализация

1. Зафиксировать начальную карту модулей и тестового покрытия в
   `docs/codemap/`.
2. Создать Python package и console script `tts` без runtime-зависимостей.
3. Реализовать structured extractor с RFC 6901 provenance и дедупликацией URL.
4. Реализовать индекс канонических cache-каталогов и два нормативных метода
   сопоставления без выбора первого кандидата при ambiguity.
5. Собрать versioned report и два renderer с одинаковой сводкой.
6. Добавить synthetic fixtures, golden tests, mutation check и все error paths.
7. Обновить README фактическими командами установки и использования.
8. Выполнить тесты, privacy scan и read-only smoke на трёх локальных сейвах.

## Проверка

```powershell
uv run pytest
uv run tts assets audit tests/fixtures/empty_save.json --mods-dir <temp-mods> --json
git diff --check
```

Отдельный privacy scan всего списка `git ls-files` с локально сформированным
denylist должен завершиться без совпадений. Реальные пути и Workshop ID
используются только локально и не записываются в tracked-файлы или саму команду.

## Границы

- Никакой сети, скачивания, ремонта, переписывания сейва или кэша.
- Никакого GitHub remote, release или публикации.
- Полный отчёт реального сейва не сохраняется в репозитории.
