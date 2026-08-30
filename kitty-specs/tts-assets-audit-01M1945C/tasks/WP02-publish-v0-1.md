---
work_package_id: "WP02"
title: "Подготовить и опубликовать v0.1"
dependencies:
  - "WP01"
planning_base_branch: "codex/tts-assets-audit"
merge_target_branch: "main"
branch_strategy: "Публичные metadata добавляются в task-owned ветке и интегрируются в main только через GitHub PR."
subtasks:
  - "T006"
  - "T007"
  - "T008"
  - "T009"
phase: "Публикация v0.1"
assignee: ""
agent: "codex"
shell_pid: ""
history:
  - timestamp: "2026-08-30T00:00:00Z"
    agent: "codex"
    action: "Публикация явно разрешена после подтверждённого локального v0.1."
---

# Рабочий пакет WP02: подготовить и опубликовать v0.1

## Реализация

1. Добавить MIT license, `SECURITY.md`, package URLs и public README metadata.
2. Добавить CI для Python 3.12/3.13 на Linux/Windows с минимальными permissions
   и actions, закреплёнными полными commit SHA.
3. Выполнить tests, lint, build, schema validation и privacy scan tracked tree.
4. Создать public repo, push `main` и task-ветку, открыть PR, дождаться зелёного
   CI и merge без административного обхода.
5. Проверить visibility, license, default branch и совпадение итогового tree.

## Границы

- Не публиковать пакет в PyPI и не создавать GitHub Release.
- Не добавлять реальные сейвы, cache-файлы, URL или абсолютные локальные пути.
- Не ослаблять branch protection и не использовать `--admin` для merge.
