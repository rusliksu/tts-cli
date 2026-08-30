# Рабочие пакеты: аудит ресурсов TTS-сейва

## WP01: Реализовать и проверить пилот

Реализовать команду `tts assets audit`, её стабильный JSON-контракт, human
summary, синтетические тесты и локальную acceptance-проверку. Пакет атомарен:
extractor и cache matcher вместе определяют наблюдаемый статус ресурса, поэтому
их разнесение не дало бы независимо поставляемого результата.

**Готово, когда:**

- `tts assets audit <save.json> [--mods-dir <path>] [--json]` работает offline и
  не изменяет входные файлы;
- один URL объединяет все отсортированные usages и inferred types;
- оба метода cache matching, ambiguity и unknown URL покрыты тестами;
- проверены exit codes `0/1/2/3` и паритет human/JSON summary;
- mutation check превращает подтверждённый UGC asset в `not_found_in_cache`;
- golden JSON соответствует schema version `1`;
- весь tracked tree проходит privacy scan;
- три локальных сейва проходят read-only smoke менее чем за 10 секунд каждый;
- GitHub remote и публикация отсутствуют.

## WP02: Подготовить и опубликовать v0.1

Добавить минимальные публичные metadata, MIT license и безопасный CI, повторить
локальные проверки и privacy scan, создать public repo `rusliksu/tts-cli`,
провести task-ветку через PR в `main` и проверить результат через GitHub API.

**Готово, когда:** public `main` содержит проверенный tree, CI зелёный,
visibility равна `PUBLIC`, license определяется как MIT, а PyPI/GitHub Release
не создавались.

## WP03: Опубликовать `tts-cli==0.1.0` в PyPI

Добавить минимальный one-shot Trusted Publishing workflow, инструкции установки и
проверки дистрибутивов. Провести изменения через task-owned PR, привязать
production PyPI publisher без токена, вручную запустить workflow для
существующего тега `v0.1.0` и проверить установку из PyPI.

**Готово, когда:** production PyPI возвращает `tts-cli==0.1.0`, workflow
успешен, а чистая установка предоставляет рабочую команду `tts`. Workflow
собирает только `v0.1.0` на точном SHA `54af70b` и не создаёт автоматический
publish surface для следующих релизов.
