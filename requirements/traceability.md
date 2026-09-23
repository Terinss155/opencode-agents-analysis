# Матрица трассируемости: возврат товара и возврат денежных средств

Версия бандла: 15 · Дата: 24.09.2026 · Статус: Черновик

Вкладка 03 бандла [index.md](./index.md). Прослеживает
требование на всю глубину: `BO → PP → Requirement → US → UC → бэк-логика → модель данных → API →
sequence → экран → NFR → тест`. Связывает идентификаторы вкладок; содержание артефактов не
пересказывает. Критерии приёмки (AC) живут рядом со своими историями во вкладке 01
([user-story/](./user-story/)) и в матрицу не выносятся.

## Легенда идентификаторов

| Префикс | Расшифровка | Где определяется |
|---|---|---|
| `BO-<n>` | Business Objective — бизнес-цель | [brd.md](./brd.md), §3 |
| `PP-<n>` | Pain Point — болевая точка AS-IS | [brd.md](./brd.md), §5 |
| `BR-NN` | Business Requirement — бизнес-требование | [brd.md](./brd.md), §7.1 |
| `RULE-NN` | Business Rule — бизнес-правило | [brd.md](./brd.md), §7.2 |
| `FR-NN` | Functional Requirement — функциональное требование | [brd.md](./brd.md), §7.3 |
| `NFR-NN` | Non-functional Requirement — нефункциональное требование раздела BRD | [brd.md](./brd.md), §7.4 |
| `INT-NN` | Integration / Technical Requirement — интеграционное требование | [brd.md](./brd.md), §7.5 |
| `C-<n>`, `A-<n>` | ограничение / допущение | [brd.md](./brd.md), §9 |
| `BR-COM-<n>`, `BR-CUR-<n>` | детальное бизнес-правило исходных процессных документов | `drafts/obshie-biznes-pravila-oformleniya-vozvrata.md` и канальные драфты |
| `US-CR-NN`, `US-VW-NN`, `US-LC-NN`, `US-CH-NN` | User Story: оформление / просмотр / жизненный цикл / каналы | [user-story/](./user-story/) (вкладка 01) |
| `UC-RET-<n>` | Use Case — сценарий / ветка оформления возврата | [use-case/use-case.md](./use-case/use-case.md) |
| `BL-RET-<...>` | backend-логика | `./backend/*.md` (skill/backend-logic) — см. таблицу 3 |
| `TASK-RET-DATA` | задача проектирования модели данных сущности «возврат» | `./backend/return-entity_data-model_task.md` (skill/backend-logic, skill/erd-model) |
| `API-<...>` | API-контракт / метод | `reference/api/web/`, `reference/api/mobile/` (skill/openapi-spec) — см. таблицу 3 |
| `SEQ-RET-<...>` | sequence-диаграмма | `./as-is/sequence/*.plantuml` (skill/sequence-diagram) — см. таблицу 3 |
| `SCR-RET-<n>` | спецификация экрана восприятия | [screen-spec/screen-spec.md](./screen-spec/screen-spec.md) |
| `ERD-<...>`, `NFR-<КАТ>-<n>`, `TC-<...>` | модель данных / NFR отдельного `nfr/nfr.md` / тест-кейс | артефактов пока нет (см. примечание к таблице 3) |
| `OQ-<n>` | открытый вопрос согласования (блокер уточнения) | [brd.md](./brd.md), §9 |
| `ADR-RET-<n>` | запись об обосновании значимого решения; не является уровнем трассировки | [adr/](./adr/) (skill/adr) |

## Таблица 1. Обоснование

Проектная адаптация: столбец «Требования BRD» содержит требования раздела 7 BRD
(`BR` / `RULE` / `FR`), которые раскрывает история; `BO` и `PP` строки — объединение поля
«Источник» этих требований в BRD. Требования без User Story — в таблице 1а с явным статусом.

| Бизнес-цель | Болевая точка | Требования BRD (BR / RULE / FR) | User Story | Use Case | Статус |
|---|---|---|---|---|---|
| — | PP-15 | BR-01 | Эпик «Оформление возврата товара» (контейнер историй, не US) | UC-RET-01…05 | Черновик |
| BO-1 | — | RULE-10, FR-03 | [US-CR-01](./user-story/user-story-creation.md#us-cr-01) Просмотр условий и возможности возврата по заказу | — | Черновик |
| BO-1 | PP-15, PP-20 | BR-03, FR-02, FR-32, FR-33, FR-34, FR-35 | [US-CR-02](./user-story/user-story-creation.md#us-cr-02) Выбор изделий и причин возврата | UC-RET-01, UC-RET-02 | Черновик |
| BO-1 | PP-7, PP-15 | RULE-15, RULE-16, RULE-22, RULE-23, RULE-24, RULE-25, RULE-26, FR-18, FR-19, FR-20, FR-21, FR-22, FR-24 | [US-CR-03](./user-story/user-story-creation.md#us-cr-03) Определение города и списка доступных способов возврата | UC-RET-03, UC-RET-04 | Черновик |
| BO-6 | PP-11 | RULE-33, RULE-34, RULE-35, RULE-36, RULE-37, RULE-38, RULE-39, RULE-40, RULE-41, RULE-42, FR-37 | [US-CR-04](./user-story/user-story-creation.md#us-cr-04) Определение способа возврата денежных средств | UC-RET-04.6 | Черновик (`OQ-46` — карта или договор) |
| BO-3 | PP-1 | RULE-02, FR-04, FR-05 | [US-CR-05](./user-story/user-story-creation.md#us-cr-05) Просмотр информации и создание заявки на возврат | UC-RET-05 | Черновик |
| BO-3 | — | FR-06 | [US-CR-06](./user-story/user-story-creation.md#us-cr-06) Скачивание пустого бланка заявления без авторизации | — | Черновик (приоритет требует подтверждения) |
| BO-1, BO-5, BO-6 | PP-11, PP-15, PP-16 | BR-04, RULE-05, RULE-29, RULE-33, RULE-34, RULE-35, RULE-36, RULE-37, RULE-38, FR-17, FR-26 | [US-VW-01](./user-story/user-story-view.md#us-vw-01) Просмотр деталей созданной заявки на возврат | — (экран восприятия) | Черновик (`OQ-40`, `OQ-41`) |
| BO-5 | PP-16 | RULE-28, FR-27 | [US-VW-02](./user-story/user-story-view.md#us-vw-02) Отслеживание состояния созданного возврата | — (экран восприятия) | Черновик (`OQ-1`) |
| BO-5 | PP-16 | RULE-17, FR-07, FR-08 | [US-VW-03](./user-story/user-story-view.md#us-vw-03) Просмотр идентификаторов для передачи изделий | — (экран восприятия) | Черновик |
| BO-5 | PP-16 | BR-04, RULE-29, FR-25 | [US-VW-04](./user-story/user-story-view.md#us-vw-04) Просмотр списка оформленных возвратов | — (экран восприятия) | Черновик |
| BO-3 | PP-1, PP-13 | RULE-02, RULE-13 | [US-VW-05](./user-story/user-story-view.md#us-vw-05) Доступ к документам созданного возврата | — (экран восприятия) | Черновик (`OQ-34`) |
| BO-1 | PP-15 | RULE-05, RULE-06, RULE-09, RULE-14, FR-15 | [US-LC-01](./user-story/user-story-lifecycle.md#us-lc-01) Отмена и переоформление созданного возврата | — | Черновик (`OQ-39`) |
| BO-1 | — | RULE-11, FR-11 | [US-LC-02](./user-story/user-story-lifecycle.md#us-lc-02) Автоотмена заявки на возврат по истечении срока передачи | — | Черновик (`OQ-36` — Почта России) |
| BO-6 | PP-10, PP-11, PP-12 | RULE-30, RULE-33, RULE-34, RULE-35, RULE-36, RULE-37, RULE-38, FR-36 | [US-LC-03](./user-story/user-story-lifecycle.md#us-lc-03) Исполнение возврата денежных средств и бонусов | — (вне контура оформления) | Черновик |
| BO-5 | PP-16 | RULE-27, FR-12 | [US-LC-04](./user-story/user-story-lifecycle.md#us-lc-04) Уведомления о событиях возврата | — | Черновик (`OQ-45`) |
| BO-1 | PP-7 | RULE-11, RULE-12, FR-13, FR-14 | [US-CH-01](./user-story/user-story-channels.md#us-ch-01) Курьер — выбор адреса, даты и интервала приезда | UC-RET-04.1 | Черновик |
| BO-1 | PP-15 | RULE-08 | [US-CH-02](./user-story/user-story-channels.md#us-ch-02) Курьер — изменение даты или интервала через «Дружбу» | — | Черновик |
| BO-1, BO-5 | PP-15, PP-16 | RULE-08, FR-27 | [US-CH-03](./user-story/user-story-channels.md#us-ch-03) Курьер — изменение по согласованию с транспортной компанией | — | Черновик |
| BO-1 | PP-15 | RULE-09 | [US-CH-04](./user-story/user-story-channels.md#us-ch-04) Курьер — передача изделий и фиксация факта передачи | — (вне контура оформления) | Требует уточнения (`OQ-39`) |
| BO-5 | PP-16 | RULE-18, FR-16, FR-17 | [US-CH-05](./user-story/user-story-channels.md#us-ch-05) СДЭК ПВЗ — выбор точки передачи | UC-RET-04.3 | Черновик |
| BO-5 | PP-16 | RULE-17 | [US-CH-06](./user-story/user-story-channels.md#us-ch-06) СДЭК ПВЗ — идентификация и передача изделий | — | Черновик (`OQ-40` не блокирует основной сценарий) |
| BO-5 | PP-16 | RULE-18, FR-16, FR-17 | [US-CH-07](./user-story/user-story-channels.md#us-ch-07) 5Post — выбор пункта передачи | UC-RET-04.2 | Черновик |
| BO-5 | PP-16 | RULE-17, RULE-27 | [US-CH-08](./user-story/user-story-channels.md#us-ch-08) 5Post — идентификация и передача изделий на кассе | — | Черновик (`OQ-41` не блокирует основной сценарий) |
| BO-5 | PP-16 | RULE-17 | [US-CH-09](./user-story/user-story-channels.md#us-ch-09) 5Post — передача изделий через постамат | — | Черновик (`OQ-41`) |
| BO-1, BO-5 | PP-7, PP-16 | RULE-15, RULE-16, RULE-18, FR-16, FR-17 | [US-CH-10](./user-story/user-story-channels.md#us-ch-10) Розничный магазин — выбор точки передачи | UC-RET-04.4 | Требует уточнения (Retail-процесс, `OQ-27`, `OQ-33`, `OQ-42`) |
| BO-5 | PP-16 | RULE-17 | [US-CH-11](./user-story/user-story-channels.md#us-ch-11) Розничный магазин — идентификация и передача изделий | — | Требует уточнения (Retail-процесс, `OQ-27`) |
| BO-1, BO-5 | PP-7, PP-16 | RULE-11, RULE-15, RULE-17 | [US-CH-12](./user-story/user-story-channels.md#us-ch-12) Почта России — самостоятельная отправка возврата | UC-RET-04.5 | Требует уточнения (`OQ-12`, `OQ-36`) |

### Таблица 1а. Требования без User Story

Каждое из 108 требований BRD учтено ровно один раз: в таблице 1 либо здесь.

| Статус | Требования | Пояснение |
|---|---|---|
| gap — пользовательский сценарий без US | BR-02, FR-01 | Оформление возврата сотрудником Дружбы в админке сайта (`ADR-RET-007`); отсутствие US отмечено в `user-story/user-story.md`, п. 7 |
| gap — пользовательский сценарий без US | BR-06 | Подтверждение приёма/передачи изделия для клиента; форма подтверждения не решена (`OQ-8`) |
| gap — пользовательский сценарий без US | FR-09 | Предъявление QR-кода офлайн без печати |
| gap — пользовательский сценарий без US | FR-28, FR-29 | Признак возврата в списке и карточке заказа, индикатор на позиции заказа |
| gap — пользовательский сценарий без US | FR-31 | Информирование клиента о причине отклонения по итогам экспертизы |
| gap — пользовательский сценарий без US | FR-40 | Клиентская часть CSI-опроса (`gap-analysis.md`, раздел 4) |
| `—` в US — правило процесса | RULE-01, RULE-03, RULE-04, RULE-07, RULE-19, RULE-32 | Правила процесса и операций (обработка возвратов Дружбы, упаковка заказа, отдельная заявка на другое изделие, обратная доставка, маркировка); отдельной клиентской US не требуют |
| `—` в US — обмен | RULE-43, RULE-44 | Процесс обмена в проекте не изменяется (BRD §4, Out of Scope) |
| `—` в US — внецифровые обращения | BR-08, RULE-20, RULE-21 | Операционный процесс Дружбы / розницы; владелец не назначен (`gap-analysis.md`, раздел 5) |
| `—` в US — административный интерфейс | FR-10, FR-23 | Настройка интервала автоотмены и доступности способов по городу; для `FR-23` владелец не назначен (`gap-analysis.md`, раздел 5) |
| `—` в US — сторона компании | BR-05, FR-30 | Приёмка и экспертиза по идентификатору, фиксация результата экспертизы |
| `—` в US — отчётность для бухгалтерии | BR-07, FR-38, FR-39, NFR-03 | Отчёт в Qlik/1С; владелец не назначен (`gap-analysis.md`, раздел 5) |
| `—` в US — интеграция | INT-01, INT-02, INT-03, INT-04, INT-05, INT-06, INT-07, INT-08, INT-09 | Обмен данными между системами; для `INT-04`, `INT-05`, `INT-06`, `INT-09` владелец не назначен (`gap-analysis.md`, раздел 5) |
| `—` в US — нефункциональное | NFR-01, NFR-02, NFR-04, NFR-05, NFR-06, NFR-07 | Сквозные NFR раздела 7.4 BRD; отдельного `nfr/nfr.md` в бандле нет |
| Post-MVP | RULE-31 | Организационное ограничение по категориям (приоритет в BRD — Should (Post-MVP)); в MVP действует `FR-35` (покрыт `US-CR-02`) |

## Таблица 2. Реализация (трассировка вниз)

Строки по `US → UC`. Ячейки — короткие ID из таблицы 3, либо `—`.

| User Story | Use Case | Бэк-логика | Модель данных | API-контракт | Sequence | Экран / фронт | NFR | Тест-кейс |
|---|---|---|---|---|---|---|---|---|
| US-CR-01 | — | BL-RET-ELIG-01, BL-RET-QTY-01 | — | API-ORD-VIEW-WEB, API-ORD-VIEW-MOB | — | — | — | — |
| US-CR-02 | UC-RET-01, UC-RET-02 | BL-RET-QTY-01 | — | API-RET-GETPOS | — | — | — | — |
| US-CR-03 | UC-RET-03, UC-RET-04 | — | — | — | — | — | — | — |
| US-CR-04 | UC-RET-04.6 | — | — | API-RET-GETPOS | — | — | — | — |
| US-CR-05 | UC-RET-05 | TASK-RET-DATA | TASK-RET-DATA | — | SEQ-RET-MOB, SEQ-RET-1C, SEQ-RET-RCRM, SEQ-RET-OTHER | — | — | — |
| US-CR-06 | — | — | — | — | — | — | — | — |
| US-VW-01 | — | TASK-RET-DATA | TASK-RET-DATA | — | — | SCR-RET-01 | — | — |
| US-VW-02 | — | — | — | — | — | — | — | — |
| US-VW-03 | — | — | — | — | — | SCR-RET-01 | — | — |
| US-VW-04 | — | — | — | — | — | SCR-RET-02 | — | — |
| US-VW-05 | — | — | — | — | — | SCR-RET-01 | — | — |
| US-LC-01 | — | TASK-RET-DATA | TASK-RET-DATA | — | — | — | — | — |
| US-LC-02 | — | TASK-RET-DATA | TASK-RET-DATA | — | — | — | — | — |
| US-LC-03 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-LC-04 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-01 | UC-RET-04.1 | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-02 | — | — | — | — | — | — | — | — |
| US-CH-03 | — | — | — | — | — | — | — | — |
| US-CH-04 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-05 | UC-RET-04.3 | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-06 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-07 | UC-RET-04.2 | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-08 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-09 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-10 | UC-RET-04.4 | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-11 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-CH-12 | UC-RET-04.5 | — | TASK-RET-DATA | — | — | — | — | — |

Столбец NFR: сквозные `NFR-01`…`NFR-07` раздела 7.4 BRD отдельным историям не назначаются
(таблица 1а); артефакта `nfr/nfr.md` в бандле нет.

## Таблица 3. Реестр технических артефактов

Каждый артефакт — одна строка, даже если он покрывает несколько US/UC.

| ID | Тип | Файл | Скилл | Статус |
|---|---|---|---|---|
| BL-RET-ELIG-01 | Бэк-логика | `./backend/return-eligibility_backend.md` | backend-logic | DRAFT |
| BL-RET-QTY-01 | Бэк-логика | `./backend/available-return-quantity_backend.md` | backend-logic | DRAFT |
| TASK-RET-DATA | Модель данных / задача БД | `./backend/return-entity_data-model_task.md` | backend-logic, erd-model | DRAFT |
| SCR-RET-01 | Экран | `./screen-spec/screen-spec.md` (SCR-RET-01) | screen-spec | DRAFT |
| SCR-RET-02 | Экран | `./screen-spec/screen-spec.md` (SCR-RET-02) | screen-spec | DRAFT |
| API-RET-GETPOS | API-контракт | `reference/api/web/order-refund-get-positions_web.md` | openapi-spec | AS-IS описан |
| API-ORD-VIEW-WEB | API-контракт | `reference/api/web/order-view_web.md` | openapi-spec | AS-IS описан |
| API-ORD-VIEW-MOB | API-контракт | `reference/api/mobile/order-view_mobile.md` | openapi-spec | AS-IS описан |
| SEQ-RET-MOB | Sequence | `./as-is/sequence/mobile_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-1C | Sequence | `./as-is/sequence/1c_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-RCRM | Sequence | `./as-is/sequence/rcrm_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-OTHER | Sequence | `./as-is/sequence/other_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-ASIS | Sequence (AS-IS, базовая линия) | `./as-is/sequence/sequence.plantuml` | sequence-diagram | — |

**Отсутствуют в бандле** (в таблице 2 — везде `—`): ERD (`*_erd.plantuml` + `*_sql.sql`),
OpenAPI/AsyncAPI-контракты (`*_openapi.yaml`), NFR (`nfr/nfr.md`), тест-кейсы
QA. Пошаговый AS-IS — `./as-is/` (не входит в реестр реализации TO-BE).

## Полнота

**Сверху вниз:**
- BO-1 … BO-6 → требования BRD по полю «Источник» (таблица 1, столбцы BO/PP). BO-2 прямых требований не имеет: снижение затрат — эффект отказа от бумаги и ручного труда; помечено явно.
- Все 108 требований BRD (BR 8 · RULE 44 · FR 40 · NFR 7 · INT 9) учтены: в таблице 1 либо в таблице 1а со статусом.
- Каждый Use Case и каждая простая US имеют строку в таблице 2.

**Снизу вверх:** все 27 US трассируются до требований BRD; каждый UC — до своей US. Use Case без родительской US нет.

**Реализация (таблица 2 / 3):**
- `TASK-RET-DATA` (модель данных сущности «возврат») покрывает создание, просмотр и жизненный цикл заявки; описана один раз в таблице 3, в таблице 2 повторяется только ID.
- Бэк-логика проверки права и количества (`BL-RET-ELIG-01`, `BL-RET-QTY-01`) — только вход в оформление (US-CR-01, US-CR-02, UC-RET-01).
- Sequence-диаграммы покрывают шаг создания заявки и исходящие интеграции (US-CR-05 / UC-RET-05).
- Экраны восприятия (`SCR-RET-01/02`) покрывают карточку, идентификаторы, список и документы (US-VW-01, US-VW-03, US-VW-04, US-VW-05).

**Открытые места (не пустые ячейки молча):**
- Gap-строки таблицы 1а — пользовательские сценарии без US; истории заводятся решением PO/BA.
- Единая статусная модель (`OQ-1`) затрагивает US-VW-01, US-VW-02, US-LC-02, US-LC-04 и все канальные US.
- `OQ-39` блокирует приёмку `US-CH-04`; `OQ-40` и `OQ-41` описывают сдачу в другой точке и не блокируют основной сценарий.
- Почта России: клиентский срок отправки (`RULE-11`) и технический интервал автоотмены — `OQ-36`, `OQ-12`.
- ERD, OpenAPI-контракты, `nfr/nfr.md` и тест-кейсы для процесса не создавались — в таблице 2 соответствующие столбцы `—`; это осознанный пробел, не упущение матрицы.

## Чек-лист качества

- [x] Заполнена легенда идентификаторов (включая технические префиксы)
- [ ] Нет бизнес-цели без требования: `BO-2` осознанно без прямых требований
- [x] Каждый Use Case и каждая простая US имеют строку в таблице 2
- [x] В таблице 2 техника указана только короткими ID
- [x] Ни один артефакт не описан в таблице 3 дважды
- [x] Все ID из таблицы 2 сверены с таблицей 3 и с вкладками (27 US, UC-RET-01…05 + ветки `.1–.6`, SCR-RET-01/02)
- [x] Отсутствующие типы артефактов (ERD / OpenAPI / NFR / тест) помечены примечанием, а не выдуманы
- [x] Acceptance Criteria в матрицу не скопированы
- [x] Все 108 требований BRD учтены в таблице 1 или 1а
- [ ] Статусы актуализируются после закрытия блокеров `OQ-1`, `OQ-27`, `OQ-36`, `OQ-39`
