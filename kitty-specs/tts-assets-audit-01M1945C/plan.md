# План реализации: аудит ресурсов TTS-сейва

## Контекст

Новый Python CLI без существующего продуктового кода. Пилот читает один JSON-сейв
Tabletop Simulator и локальный каталог `Mods`, не выполняет сеть и не изменяет
входные данные. Реальные Workshop-сейвы используются только для локальной
acceptance-проверки и не копируются в репозиторий.

## Технический контекст

- Python 3.12+.
- Runtime-зависимости отсутствуют.
- CLI: `argparse`, console script `tts`.
- Тесты: `pytest` как dev dependency.
- Формат входа: UTF-8 JSON, загруженный стандартным `json`.
- Формат машинного выхода: JSON schema version `1`.
- Целевые платформы пилота: Windows; структура ядра не должна блокировать Linux/macOS.

## Архитектура

```text
CLI arguments
    -> load save JSON
    -> recursive structured-reference extractor
    -> cache index + deterministic matcher
    -> AuditReport
    -> JSON renderer | human summary renderer
```

### Модули

```text
src/tts_cli/
  __init__.py       package version
  __main__.py       python -m tts_cli
  cli.py            argparse, stderr и exit codes
  audit.py          orchestration и сводные счётчики
  extract.py        рекурсивный обход и JSON Pointer provenance
  cache.py          каталогизация кэша и правила сопоставления
  models.py         frozen dataclasses и сериализация отчёта
  render.py         deterministic JSON и human summary
tests/
  fixtures/         только синтетические JSON
  test_extract.py
  test_cache.py
  test_cli.py
docs/codemap/
  codemap.json
  codemap.html
  codemap.lock
```

Разделение сохраняет чистое ядро без I/O в extractor/models и позволяет
проверять cache matching независимо от CLI. Дополнительные service/repository
слои для однокомандного инструмента не вводятся.

## Контракты

### Извлечение ссылок

1. Рекурсивно обходятся все словари и массивы.
2. Объектом считается словарь с непустым строковым `Name`.
3. Lua-скриптом считается непустое строковое поле `LuaScript`; его содержимое
   не сканируется.
4. Известные поля классифицируются таблицей без учёта регистра:
   - `FaceURL`, `BackURL`, `ImageURL`, `ImageSecondaryURL`, `DiffuseURL`,
     `NormalURL`, `TableURL`, `SkyURL` -> `image`;
   - `MeshURL`, `ColliderURL` -> `model`;
   - `PDFUrl` -> `pdf`;
   - `CurrentAudioURL` -> `audio`;
   - `AssetbundleURL` -> `assetbundle`.
5. Незнакомое поле с суффиксом `url` учитывается как `unknown`; другие строки,
   включая Lua и `Item1`, не сканируются.
6. Provenance хранится как RFC 6901 JSON Pointer с экранированием `~` и `/`.
7. Один URL хранит отсортированные usages `{pointer, field, inferred_type}` и
   отсортированный уникальный набор inferred types.

### Сопоставление кэша

1. Пилот индексирует канонические cooked-каталоги `Images`, `Models`, `PDF`,
   `Audio`, `Assetbundles`; парные каталоги `* Raw` не участвуют, чтобы две
   формы одного локального ресурса не создавали ложную ambiguity.
2. Для всех известных типов usages строится объединение их TTS-каталогов;
   `unknown` не добавляет каталогов.
3. Сначала применяется `steam_ugc_key`: из raw URL без percent-decoding
   извлекается case-insensitive `/ugc/<decimal-id>/<hex-hash>`. Ключ
   `<id><uppercase-hash>` сравнивается как case-insensitive substring полного
   имени cache-файла. Query и fragment не участвуют. Ровно один кандидат даёт
   `cached/high`.
4. Если URL не Steam UGC, применяется `exact_normalized_name`: из полного raw
   URL и полного имени cache-файла удаляются символы вне `[A-Za-z0-9]`, затем
   строки сравниваются case-insensitive. Percent-encoding, query и fragment не
   преобразуются. Ровно один кандидат даёт `cached/medium`.
5. Ноль кандидатов для известного типа даёт `not_found_in_cache` с
   `method=none`, `confidence=none` и `relative_path=null`.
6. Больше одного кандидата при любом методе даёт `unverified` с
   `method=ambiguous`, `confidence=none`, `relative_path=null` и фактическим
   `candidate_count`; произвольный первый файл не выбирается.
7. Ресурс только с типом `unknown` всегда получает `unverified` без обхода всего
   кэша.

### Детерминированность

- Ресурсы сортируются по URL, usages — по `(pointer, field, inferred_type)`.
- Словари счётчиков сериализуются с отсортированными ключами.
- `json.dumps(..., sort_keys=True, ensure_ascii=False, indent=2)` и один `LF` в конце.
- В stdout нет timestamps, duration и абсолютного пути до сейва или `Mods`.
- Cache paths используют `/` и всегда относительны к `Mods`.
- Нормативная форма зафиксирована в `contracts/audit-report-v1.schema.json` и
  двух golden examples.

## Определение каталога `Mods`

1. Явный `--mods-dir` имеет приоритет.
2. Иначе используется ближайший предок входного файла с именем `Mods`.
3. Иначе вверх по предкам ищется первый существующий дочерний каталог `Mods`;
   это покрывает обычный путь `Tabletop Simulator/Saves/...`.
4. Если каталог не найден или не существует, команда завершается с кодом `2`.

## Ошибки и exit codes

- `0`: аудит выполнен, findings нет.
- `1`: аудит выполнен, есть `not_found_in_cache` или `unverified`.
- `2`: ожидаемая пользовательская ошибка чтения, JSON или конфигурации.
- `3`: неожиданная ошибка; короткое сообщение без traceback по умолчанию.

## Тестовая стратегия

1. Red-first unit tests для JSON Pointer, рекурсии, дедупликации и счётчиков.
2. Cache tests создают временные каталоги и пустые файлы с TTS-подобными
   именами; бинарные ассеты не нужны.
3. CLI tests вызывают `main(args)` и проверяют все exit codes: полный JSON при
   `1`, пустой stdout и короткий stderr при `2/3`, invalid `Mods` и broken JSON.
4. Mutation check: изменить Steam UGC hash в fixture и потребовать переход
   `cached -> not_found_in_cache`.
5. Privacy gate: поиск реальных Workshop IDs, Steam asset URL и `C:\Users` во
   всём наборе tracked-файлов, а не только в текущем diff.
6. Локальная acceptance-проверка на трёх существующих сейвах выполняется
   отдельной командой; сохраняются только агрегаты и время, не полный отчёт.

## Карта кода

До первого изменения продуктового модуля создаются `docs/codemap/codemap.json`,
`codemap.html` и `codemap.lock`. Карта должна отвечать:

- `cli.py` вызывает `audit.py` и renderer;
- `audit.py` затрагивает extractor, cache matcher и models;
- покрытие обеспечивают `test_extract.py`, `test_cache.py`, `test_cli.py`.

## Риски

- TTS меняет hostname Steam Cloud: снижено использованием UGC key.
- Cache naming не документирован полностью: каждый match содержит метод и
  confidence; отсутствие совпадения не объявляется сетевой поломкой.
- Большие сейвы создают память-пропорциональную структуру JSON: для v0.1
  допустимо при критерии менее 10 МБ и 10 секунд.
- Публичный repo может случайно утечь реальные данные: публикация отделена от
  v0.1 и требует privacy scan.

## Поставка

Один work package реализует код, тесты, codemap и локальную acceptance-проверку.
После подтверждённого v0.1 и явного разрешения второй work package добавляет
MIT license, `SECURITY.md`, public metadata и GitHub Actions. Actions получают
только `contents: read`, используют полные commit SHA и запускают tests/lint на
Python 3.12 и 3.13 под Linux и Windows. Затем создаётся public repo, task-ветка
проходит через PR в `main`, а visibility, license, CI и итоговый tree
проверяются через GitHub API. PyPI и GitHub Release остаются вне scope.
