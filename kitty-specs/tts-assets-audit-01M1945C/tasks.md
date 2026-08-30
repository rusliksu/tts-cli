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

