@AGENTS.md

# Дополнения только для Claude Code

Методология, структура и все запреты — в `AGENTS.md` (подключён выше, общий с OpenCode). Здесь —
только то, чего нет в OpenCode.

## Агенты
- Основной агент по умолчанию — `system-analyst` (как `default_agent` в `opencode.json`).
  Другой основной агент: `claude --agent business-analyst` (`product-owner`, `repository-researcher`).
- `security-reviewer` — субагент: вызывается из основного агента только по явной просьбе
  пользователя (`AGENTS.md` → «Рабочий процесс»); пишет только в `projects/<проект>/reviews/security/`.
- `ui-reviewer` — субагент: вызывается из основного агента по просьбе пользователя; пишет только в
  `projects/<проект>/reviews/ui/`.
- В Claude нет белого списка скиллов на агента: каждый агент вызывает **только скиллы из своей
  строки** таблицы «Роли и скиллы» в `AGENTS.md`. Это обязательное правило, а не рекомендация.

## Код и БД
- Код: `C:\Users\RobotComp.ru\Desktop\12stz\` подключён на чтение. Перед поиском —
  `knowledge/README.md` и карта репозитория.
- Графы. `graphify-out/` — граф документов этого репозитория (требования, ADR, встречи,
  `knowledge/`). `graphify-out-12stz/<репозиторий>/graph.json` — граф кода каждого репозитория 12stz:
  `12storeez-master-web` (PHP, Vue и JS из `frontend/src`), `mobile-monorepo-go` (гейт МП),
  `esb-monorepo`, `esb-protobufs` (GitHub, обновляется редко), `12storeez-ios`, `monolith-bfb-ms`
  (BFB монолита, PHP), `proto-specifications` (GitLab, контракты новых Go-сервисов);
  `graphify-out-12stz/merged/graph.json` — все
  репозитории вместе, только для поиска «где вообще есть X» (пути в нём без имени репозитория, связей
  между системами нет).
- Порядок поиска по коду (по замеру 25.11.2026):
  1. `knowledge/README.md` → `repo-map.md` нужного репозитория → точечный grep/чтение найденных
     файлов. Это основной путь: он самый короткий, а карта даёт то, чего нет в коде.
  2. Граф — вторым шагом, когда нужно найти, «кто ещё это вызывает» или связи, которых не видно
     по названиям: `graphify explain "<точное имя класса>" --graph graphify-out-12stz/<репозиторий>/graph.json`
     (так же `path`). Широкий `query` не начинать: выдача обрезается и уводит в тупики.
  3. `merged` — только для «где вообще есть X», не для вопросов о логике.
  Тестов, миграций, `.proto` и сжатого JS в графах нет — их читать напрямую.
- Графы кода пересобираются скриптом `graphify-out-12stz/build_all.py [репозиторий ...]` (по
  структуре кода, без токенов; весь код — около 5 минут) после обновления локальных копий; запуск —
  на E-ядрах с низким приоритетом (см. «Тяжёлые операции»). Результат пишется только в
  `graphify-out-12stz/`, в `12stz` ничего не пишется. Запускать Python-ом окружения graphify (uv):
  `C:\Users\RobotComp.ru\AppData\Roaming\uv\tools\graphifyy\Scripts\python.exe` — у системного
  `python` модуля `graphify` нет. Из сессии `12stz` хук не даёт запустить скрипт — его запускает
  пользователь через `!`.
- БД: инструменты `mcp__phpstorm__*` (проект PhpStorm `12stz` — оба репозитория,
  `projectPath`: `C:\Users\RobotComp.ru\Desktop\12stz`), подключения `12stz_staging` и `12stz_prod`
  (схема `12stz_production`, только чтение — см. `AGENTS.md` → «Доступ и запреты»). Каждый запрос проходит SQL-фильтр; отказ фильтра не обходить.
- Защитные проверки (12stz, sources, SQL, commit/push) работают как hooks; их отказ — окончательный,
  не пытайся достичь того же другим инструментом.

## Ресурсы компьютера и уборка
Каждая открытая сессия держит свои MCP-серверы (PhpStorm, браузер и др.) и всё, что в ней запущено
в фоне. Поэтому:
- **Фоновые процессы.** Перед завершением ответа останови всё, что запустил сам: фоновые команды
  (`run_in_background`), `Monitor`, dev-серверы `preview_start`, открытые вкладки встроенного браузера.
  Оставлять работающим — только если пользователь прямо попросил.
- **Субагенты.** Не запускай без явной просьбы. Исключение — независимая проверка из `skill/meeting-summary-adr`: запускается всегда, после разбора встречи и после ADR по ней, без отдельного вопроса пользователю. Одновременно:
  - агенты, которые только читают и проверяют, — не больше четырёх;
  - агент, который пишет в файлы, — не больше одного, и параллельные агенты не работают с теми же файлами.
- **Тяжёлые операции.** Сборки, тесты, линтеры в этом репозитории не запускаются (см. `AGENTS.md`).
  Поиск по `12stz` — только в конкретном репозитории/папке (например `12stz\12storeez-master-web\modules\...`),
  не по всему `12stz`. Долгие скрипты (дольше ~1 мин) и массовую обработку файлов запускай на
  энергоэффективных ядрах с низким приоритетом (i7-12700F: E-ядра — логические процессоры 16–19):
  ```powershell
  $p = Start-Process <exe> -ArgumentList '<args>' -NoNewWindow -PassThru
  $p.PriorityClass = 'Idle'; $p.ProcessorAffinity = 0xF0000; $p.WaitForExit()
  ```
- **Архивация сессий.** Когда задача сессии выполнена (результат сохранён, закоммичен или
  отклонён пользователем), предложи заархивировать сессию одной строкой. Архивируй только после
  явного «да». Перед архивацией убедись, что фоновых процессов не осталось.

## Контекст и передача дел
- Предлагай пользователю `/handoff` и новый терминал, когда строка статуса показывает ≥ 75% контекста
  или пришло предупреждение. Лучший момент — после завершённого блока работы, до начала следующего
  крупного: ответь на текущий запрос, предложи `/handoff`, новую работу в старой сессии не начинай.
- Крупный блок (правки нескольких SRS, разбор длинной транскрибации, сверка многих файлов) не
  начинай, если контекст уже заполнен на 60–70% и больше: сначала предложи `/handoff`.
- Если предыдущий блок занял много контекста (например, разбор встречи и ADR по нему), следующий
  блок по его итогам (правки SRS) — в новой сессии. Если контекст заполнен мало (около 30%),
  продолжай в текущей.
- В начале новой сессии прочитай последний файл из `handoff/` (по дате в имени) и продолжи с него. Это рабочий контекст: в артефакты из него ничего не переносится.

## graphify

Правила ниже — для графа документов `graphify-out/`; порядок поиска по коду 12stz — в разделе «Код и БД».

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
