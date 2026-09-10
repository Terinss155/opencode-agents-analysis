# Матрица трассируемости: возврат товара и возврат денежных средств

Версия бандла: 1 · Дата: 10.09.2026 · Статус: Черновик

Вкладка 03 бандла [product-return_index.md](./product-return_index.md). Прослеживает
требование на всю глубину: `BO → PP → BR → US → UC → бэк-логика → модель данных → API →
sequence → экран → NFR → тест`. Связывает идентификаторы вкладок; содержание артефактов не
пересказывает. Критерии приёмки (AC) живут рядом со своими историями в
[user-story/product-return_user-story.md](./user-story/product-return_user-story.md) и в
матрицу не выносятся.

## Легенда идентификаторов

| Префикс | Расшифровка | Где определяется |
|---|---|---|
| `BO-<n>` | Business Objective — бизнес-цель (соответствует `G<n>` бизнес-кейса) | [product-return_brd.md](./product-return_brd.md), §3 |
| `PP-<n>` | Pain Point — болевая точка AS-IS | [product-return_brd.md](./product-return_brd.md), §5 |
| `BR-<n>` | Business Requirement — бизнес-требование | [product-return_brd.md](./product-return_brd.md), §7 |
| `BR-COM-<n>`, `BR-CUR-<n>` | детальное бизнес-правило (раскрывает `BR-<n>`) | `../drafts/obshie-biznes-pravila-oformleniya-vozvrata.md` и канальные драфты |
| `US-<n>` | User Story — пользовательское требование | [user-story/product-return_user-story.md](./user-story/product-return_user-story.md) |
| `UC-RET-<n>` | Use Case — сценарий / ветка оформления возврата | [use-case/product-return_use-case.md](./use-case/product-return_use-case.md) |
| `BL-RET-<...>` | backend-логика | `./backend/*.md` (skill/backend-logic) — см. таблицу 3 |
| `TASK-RET-DATA` | задача проектирования модели данных сущности «возврат» | `./backend/return-entity_data-model_task.md` (skill/backend-logic, skill/erd-model) |
| `API-<...>` | API-контракт / метод | `../web/`, `../mobile/` (skill/openapi-spec) — см. таблицу 3 |
| `SEQ-RET-<...>` | sequence-диаграмма | `./sequence/*.plantuml` (skill/sequence-diagram) — см. таблицу 3 |
| `SCR-RET-<n>` | спецификация экрана восприятия | [screen-spec/product-return_screen-spec.md](./screen-spec/product-return_screen-spec.md) |
| `ERD-<...>`, `NFR-<...>`, `TC-<...>` | модель данных / НФ-требование / тест-кейс | артефактов пока нет (см. примечание к таблице 3) |
| `COM-OQ-<n>`, `CUR-OQ-<n>`, `CDEK-OQ-<n>`, `5POST-OQ-<n>` | открытый вопрос (блокер уточнения) | [product-return_brd.md](./product-return_brd.md) §9, драфты |

## Таблица 1. Обоснование

| Бизнес-цель | Болевая точка | Бизнес-требование | User Story | Use Case | Статус |
|---|---|---|---|---|---|
| BO-3 | PP-6 | BR-2 | US-101 Просмотр возможности возврата по заказу | — (простая US) | Черновик |
| BO-3 | PP-4 | BR-3, BR-4 | US-102 Выбор изделий и причин | UC-RET-01, UC-RET-02 | Черновик |
| BO-4 | PP-3 | BR-5, BR-6 | US-103 Город и доступные способы | UC-RET-03, UC-RET-04 | Черновик |
| BO-2 | PP-6 | BR-7 | US-104 Банковские реквизиты | UC-RET-04.6 | Черновик |
| BO-2, BO-5 | PP-1, PP-6 | BR-8, BR-10 | US-105 Просмотр информации и создание заявки | UC-RET-05 | Черновик |
| BO-1 | PP-2 | BR-11 | US-106 Просмотр состава и деталей заявки | — (экран восприятия) | Черновик |
| BO-3 | PP-5 | BR-9 | US-106.1 Идентификатор для передачи в пункт приёма | — (экран восприятия) | Черновик |
| BO-1 | PP-2 | BR-11 | US-106.2 Просмотр списка возвратов | — (экран восприятия) | Черновик |
| BO-5 | PP-1 | BR-10 | US-107 Скачивание электронного заявления | — (экран восприятия) | Черновик |
| BO-1 | PP-6 | BR-12 | US-108 Изменение состава заявки | — (`COM-OQ-04`) | Черновик |
| BO-1 | PP-6 | BR-12 | US-109 Отмена заявки клиентом | — | Черновик |
| BO-1 | PP-6 | BR-12 | US-110 Автоотмена по сроку передачи | — (`COM-OQ-23`) | Черновик |
| BO-1, BO-2 | PP-2 | BR-13 | US-111 Возврат денежных средств | — (вне контура оформления) | Черновик |
| BO-1 | PP-2 | BR-14 | US-112 Уведомления о событиях возврата | — (`COM-OQ-12`) | Черновик |
| BO-2, BO-3 | PP-3 | BR-6 | US-201 Курьер — адрес, дата, интервал | UC-RET-04.1 | Черновик |
| BO-2, BO-3 | PP-3 | BR-6 | US-202 Курьер — передача и подтверждение | — (вне контура оформления) | Черновик |
| BO-4 | PP-3, PP-5 | BR-6, BR-9 | US-203 СДЭК ПВЗ — точка, штрихкод, передача | UC-RET-04.3 | Черновик |
| BO-4 | PP-3, PP-5 | BR-6, BR-9 | US-204 5Post — пункт, касса | UC-RET-04.2 | Черновик |
| BO-4 | PP-3, PP-5 | BR-6, BR-9 | US-205 5Post — постамат | UC-RET-04.2 | Черновик |
| BO-4 | PP-3 | BR-6 | US-206 Возврат в розничный магазин | UC-RET-04.4 | Требует уточнения (Retail-процесс отсутствует) |

Верхнеуровневая история [US-100](./user-story/product-return_user-story.md#us-100-оформление-возврата-товара)
декомпозирована на US-101…US-105 и канальные US-201…US-206; её сквозной сценарий раскрыт
Use Case UC-RET-01 … UC-RET-05 (с ветками UC-RET-04.1 … UC-RET-04.6).

## Таблица 2. Реализация (трассировка вниз)

Строки по `US → UC`. Ячейки — короткие ID из таблицы 3, либо `—`.

| User Story | Use Case | Бэк-логика | Модель данных | API-контракт | Sequence | Экран / фронт | NFR | Тест-кейс |
|---|---|---|---|---|---|---|---|---|
| US-101 | — | BL-RET-ELIG-01, BL-RET-QTY-01 | — | API-ORD-VIEW-WEB, API-ORD-VIEW-MOB | — | — | — | — |
| US-102 | UC-RET-01, UC-RET-02 | BL-RET-QTY-01 | — | API-RET-GETPOS | — | — | — | — |
| US-103 | UC-RET-03, UC-RET-04 | — | — | — | — | — | — | — |
| US-104 | UC-RET-04.6 | — | — | API-RET-GETPOS | — | — | — | — |
| US-105 | UC-RET-05 | TASK-RET-DATA | TASK-RET-DATA | — | SEQ-RET-WEB, SEQ-RET-MOB, SEQ-RET-1C, SEQ-RET-RCRM, SEQ-RET-OTHER | — | — | — |
| US-106 | — | TASK-RET-DATA | TASK-RET-DATA | — | — | SCR-RET-01 | — | — |
| US-106.1 | — | — | — | — | — | SCR-RET-01 | — | — |
| US-106.2 | — | — | — | — | — | SCR-RET-02 | — | — |
| US-107 | — | — | — | — | — | SCR-RET-01 | — | — |
| US-108 | — | TASK-RET-DATA | TASK-RET-DATA | — | — | — | — | — |
| US-109 | — | TASK-RET-DATA | TASK-RET-DATA | — | — | — | — | — |
| US-110 | — | TASK-RET-DATA | TASK-RET-DATA | — | — | — | — | — |
| US-111 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-112 | — | — | TASK-RET-DATA | — | — | — | — | — |
| US-201, US-202 | UC-RET-04.1 | — | TASK-RET-DATA | — | — | — | — | — |
| US-203 | UC-RET-04.3 | — | TASK-RET-DATA | — | — | — | — | — |
| US-204, US-205 | UC-RET-04.2 | — | TASK-RET-DATA | — | — | — | — | — |
| US-206 | UC-RET-04.4 | — | TASK-RET-DATA | — | — | — | — | — |

Отдельные ветки `UC-RET-04.1 … UC-RET-04.5` (выбор конкретной точки по каналам) технических
артефактов пока не имеют — во всех столбцах `—`.

## Таблица 3. Реестр технических артефактов

Каждый артефакт — одна строка, даже если он покрывает несколько US/UC.

| ID | Тип | Файл | Скилл | Статус |
|---|---|---|---|---|
| BL-RET-ELIG-01 | Бэк-логика | `./backend/product-return-eligibility_backend.md` | backend-logic | DRAFT |
| BL-RET-QTY-01 | Бэк-логика | `./backend/available-return-quantity_backend.md` | backend-logic | DRAFT |
| TASK-RET-DATA | Модель данных / задача БД | `./backend/return-entity_data-model_task.md` | backend-logic, erd-model | DRAFT |
| SCR-RET-01 | Экран | `./screen-spec/product-return_screen-spec.md` (SCR-RET-01) | screen-spec | DRAFT |
| SCR-RET-02 | Экран | `./screen-spec/product-return_screen-spec.md` (SCR-RET-02) | screen-spec | DRAFT |
| API-RET-GETPOS | API-контракт | `../web/order-refund-get-positions_web.md` | openapi-spec | AS-IS описан |
| API-ORD-VIEW-WEB | API-контракт | `../web/order-view_web.md` | openapi-spec | AS-IS описан |
| API-ORD-VIEW-MOB | API-контракт | `../mobile/order-view_mobile.md` | openapi-spec | AS-IS описан |
| SEQ-RET-WEB | Sequence | `./sequence/product-return_web_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-MOB | Sequence | `./sequence/product-return_mobile_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-1C | Sequence | `./sequence/product-return_1c_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-RCRM | Sequence | `./sequence/product-return_rcrm_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-OTHER | Sequence | `./sequence/product-return_other_sequence.plantuml` | sequence-diagram | — |
| SEQ-RET-ASIS | Sequence (AS-IS, базовая линия) | `./sequence/product-return_sequence.plantuml` | sequence-diagram | — |

**Отсутствуют в бандле** (в таблице 2 — везде `—`): ERD (`*_erd.plantuml` + `*_sql.sql`),
OpenAPI/AsyncAPI-контракты (`*_openapi.yaml`), NFR (`nfr/product-return_nfr.md`), тест-кейсы
QA. Пошаговый AS-IS — `./as-is/` (не входит в реестр реализации TO-BE).

## Полнота

**Сверху вниз:**
- BO-1 → BR-11, BR-12, BR-13, BR-14; BO-2 → BR-7, BR-8, BR-13; BO-3 → BR-1, BR-2, BR-3, BR-4; BO-4 → BR-5, BR-6, BR-9; BO-5 → BR-10. Целей без требований нет.
- BR-1 — сквозное требование, раскрывается всей цепочкой US-101…US-105; отдельной строкой не дублируется.
- Каждый Use Case и каждая простая US имеют строку в таблице 2.

**Снизу вверх:** все US трассируются до BR и BO; каждый UC — до своей US. Use Case без родительской US нет.

**Реализация (таблица 2 / 3):**
- `TASK-RET-DATA` (модель данных сущности «возврат») покрывает весь жизненный цикл заявки — US-105…US-112, канальные US-201…US-206; описана один раз в таблице 3, в таблице 2 повторяется только ID.
- Бэк-логика проверки права и количества (`BL-RET-ELIG-01`, `BL-RET-QTY-01`) — только вход в оформление (US-101, US-102, UC-RET-01).
- Sequence-диаграммы покрывают шаг создания заявки и исходящие интеграции (US-105 / UC-RET-05).
- Экраны восприятия (`SCR-RET-01/02`) покрывают просмотр карточки, идентификаторов, списка и скачивание заявления (US-106, US-106.1, US-106.2, US-107).

**Открытые места (не пустые ячейки молча):**
- Use Case для US-106…US-112 не создаётся: это экраны восприятия (`SCR-RET-*`) либо процессы вне контура оформления (US-111, US-202) либо заблокированы открытым вопросом (US-108 → `COM-OQ-04`, US-110 → `COM-OQ-23`, US-112 → `COM-OQ-12`).
- US-206 (розничный магазин): бизнес-процесс канала не описан — критерии приёмки и Use Case требуют уточнения PO/BA.
- Единая статусная модель (`COM-OQ-05`) затрагивает US-106, US-110 и все канальные US — до ответа статусы держатся как «Черновик».
- ERD, OpenAPI-контракты, NFR и тест-кейсы для процесса не создавались — в таблице 2 соответствующие столбцы `—`; это осознанный пробел, не упущение матрицы.

## Чек-лист качества

- [x] Заполнена легенда идентификаторов (включая технические префиксы)
- [x] Нет бизнес-цели без бизнес-требования; нет BR без US
- [x] Каждый Use Case и каждая простая US имеют строку в таблице 2
- [x] В таблице 2 техника указана только короткими ID
- [x] Ни один артефакт не описан в таблице 3 дважды
- [ ] Все ID из таблицы 2 сверены с таблицей 3 и с вкладками (US-100…US-206, UC-RET-01…07, SCR-RET-01/02 — да; сверить после консолидации use-case)
- [x] Отсутствующие типы артефактов (ERD / OpenAPI / NFR / тест) помечены примечанием, а не выдуманы
- [x] Acceptance Criteria в матрицу не скопированы
- [ ] Статусы актуализируются после закрытия блокеров `COM-OQ-04/05/12/23`
- [x] Матрица соответствует версии бандла 1
