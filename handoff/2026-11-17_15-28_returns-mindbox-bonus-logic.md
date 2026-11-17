# Handoff: баллы Mindbox (BL-RET-BONUS), модель данных, задачи в requirements/tasks, портал — 2026-11-17 15:28

## Цель
Проект «Возвраты 2.0» (`projects/returns-2.0/`): довести анализ обмена с Mindbox до списка доработок `mindbox-srv-go` для команды BTS (Елена Васильева) и описания нового процесса с вопросами для менеджера Mindbox Ирины Васильевой; разнести остаток сообщения Оли Свистуновой от 16.11; сверить открытые вопросы проекта.

## Сделано
- Описание логики баллов в Mindbox `BL-RET-BONUS` — `projects/returns-2.0/requirements/backend/return-bonus_backend.md`. Стиль — задачи С. Щербатых (`skill/tracker-task/SKILL.md`, §7). Внутри: AS-IS цепочки монолит → `monolith-bfb-ms` → `mindbox-srv-go` → Mindbox, «Текущая реализация не позволяет», сборка строк для Mindbox по данным заявок, предрасчёт, расчёт при создании заявки, фиксация при «Возврат принят», отправка заказа с учётом возвратов, доработки по сервисам (§5 — основа списка для Елены), две sequence-диаграммы, пример запроса.
- `projects/returns-2.0/requirements/questions/refund-bonus_questions.md`: решения 7–14 сокращены до сути (процесс — в BL-RET-BONUS), решения 13 (возвраты в каждой отправке заказа) и 14 (баллы на всю позицию); вопрос 4 — шесть вопросов к Ирине; вопрос 8 переписан под TNT-2687 / ECOMDEV-1185; новые вопросы 12–15; адресаты — «команда BTS (Елена Васильева), сервис `mindbox-srv-go`» и «менеджер Mindbox (Ирина Васильева)».
- Модель данных `ERD-RET` по ECOMDEV-2587 — `projects/returns-2.0/requirements/diagrams/erd/return-request_erd.md` + `return-request_sql.sql` (MariaDB). Предложены поля `refund_amount`, `refund_bonus_amount` в `cms_return_positions` (в ECOMDEV-2587 их нет). Старые ERD (`return-entity_erd_merged.md`, `return-entity-overview_erd.md`, `erd.png`) и черновик `return-entity_data-model_task.md` — в `projects/returns-2.0/archive/`. Ссылки переведены на ERD-RET, в `traceability.md` — `ERD-RET`, `BL-RET-BONUS`.
- Задачи в Трекер отделены от описаний логики: `projects/returns-2.0/requirements/tasks/` (реестр `index.md`, `US-01/`, `stage-0.md`, `stage-0/`). `requirements/backend/` — только описания логики. Обновлены `AGENTS.md`, `skill/tracker-task/SKILL.md` (§5), память.
- Службы возврата — `projects/returns-2.0/requirements/questions/return-carriers_questions.md`: решения 9–11 (досылка вебхука до 200, 500 при сбое геосервиса, ≤50 городов и таймаут 60 с), решения 3, 6, 7 переписаны под справочник `cms_return_city` (ECOMDEV-2681, 2684, 2712), открытый вопрос 6 (города курьера СДЭК: совпадают с ПВЗ или свой список). Реестр задач: ECOMDEV-2681 «Разработка», добавлена ECOMDEV-2712.
- Переписка о городах курьера СДЭК дополнена сообщениями 17.11 (файл в `sources/answers/` заменил пользователь).
- Портал «Возвраты 2.0» на Claude Artifact (идея отложена) — `handoff/returns-portal/README.md`, страница `portal.html`, записи по 1С `seed/`. Память: `returns-portal-idea.md`.
- Коммиты: `2336812`, `eb47ad0`; текущий коммит — с этим handoff.

## Где остановились
Переход к Mindbox. Следующие действия по порядку:
1. **Сверка тела запроса.** Пользователь пришлёт полный запрос расчёта / изменения заказа. Сверить с `BL-RET-BONUS` (раздел «Как сейчас», «Пример») и `mindbox.proto` (`12stz/esb-protobufs/proto/mindbox.proto`, `CalculateRequest`, `CalculateResponsePositions`, `UpdateOrderV2Request`). Найдено по коду: в `CalculateRequest` нет номера заказа (origin/master v0.9.10); монолит уже получает баллы строки из `applied_promotions` с `type = spentBonusPoints`; `line_id` = ID товара.
2. **Текст для Ирины** — описание нового процесса и вопросы: `refund-bonus_questions.md`, вопросы 2, 4, 12–15; дать текстом в ответе, не артефактом.
3. **Список доработок для Елены** — из `BL-RET-BONUS`, раздел 5 «Доработки по сервисам», одним сообщением в канал проекта.
4. **Остаток сообщения Оли 16.11** — карта в `handoff/2026-11-17_14-08_returns-mindbox-analysis-start.md`: галочка реквизитов в 2.0 → `stage-0-bank-details_questions.md`; синхронизация задач ECOMDEV-2681, 2684, 2639, 2348, 2587, 2685, 2279 с Трекером; статусы `401` / `101` → `knowledge/12storeez-master-web/database/order-status-dictionaries.md` (если нужно).
5. **Сверка открытых вопросов** во всех файлах `requirements/questions/`.

## Не доделано из предыдущего handoff (`handoff/2026-11-17_14-08_returns-mindbox-analysis-start.md`)
- Шаг 1, AS-IS обмена с Mindbox → сделан (BL-RET-BONUS, раздел «Как сейчас»).
- Шаг 2, сверка тела запроса → не начат: тела нет; п. 1 нового плана.
- Шаг 3, описание процесса и вопросы для Ирины → вопросы внесены в `refund-bonus_questions.md`, текст для Ирины не собран; п. 2.
- Шаг 4, разнести сообщение Оли → частично: вопросы к Ирине, решения 13–14, вопрос 8, службы возврата; остальное — п. 4.
- Шаг 5, сверка открытых вопросов → не начат; п. 5.
- Ссылка на сообщение Оли в переписке `[2026-11-16 16-30] …` (строка 43) → пользователь вставляет вручную: https://mattermost.12stz.com/12storeez/pl/est3ptb1ypn6zkk54dn1dfq1uh. Проверить, вставлена ли.
- Открытые вопросы прошлого handoff (ТК для `sdek-courier-vzt` — Софья Попкова; итог статусной модели; ссылка ECOMDEV-2359 на ADR-RET-061; ответ Оли по правилам API; деление строки позиции, вопрос 6 в `order-position-split_questions.md`) → без ответа, перенесены ниже.
- Этап 2 реструктуризации скиллов (`handoff/2026-11-17_11-10_tracker-task-migration-start.md`) → не трогался.

## Принятые решения
- Описание процесса в системах — `requirements/backend/*_backend.md` (BL), диаграммы внутри файла; вопросы и решения — только в `requirements/questions/`, без пересечений — пользователь, 17.11.
- Задачи в Трекер — `requirements/tasks/`, отдельно от описаний логики — пользователь, 17.11 (папку перенёс сам из `projects/returns-2.0/tasks/`).
- Стиль описаний логики — по задачам С. Щербатых — пользователь, 17.11.
- Сервис Mindbox называть `mindbox-srv-go`, владелец — команда BTS (Елена Васильева) — пользователь, 17.11.
- Вебхук городов: досылка до ответа 200, при сбое геосервиса — 500, ≤50 городов, таймаут 60 с — переписка 17.11 (Васильева — Свистунова).
- Портал: продолжать по варианту 2 (владелец — учётная запись пользователя) — пользователь, 17.11; отложено.

## Открытые вопросы к пользователю
- Тело запроса для сверки с Mindbox.
- Напомнить Оле в ECOMDEV-2681 комментарием, что при сбое геосервиса нужен ответ 500 (в задаче пока 200 «по ответу логистики»)?
- Поля `refund_amount`, `refund_bonus_amount` (ERD-RET) — передать Оле для ECOMDEV-2587?
- ТК для `sdek-courier-vzt` — ждём Софью Попкову; вопрос 5 в `return-carriers_questions.md`, `ADR-RET-100`.
- Города курьера СДЭК — совпадают с ПВЗ или свой список (вопрос 6 в `return-carriers_questions.md`).
- Итог статусной модели после досогласования и встречи с RetailCRM.
- ECOMDEV-2359 ссылается на `ADR-RET-061` — менять ли вместе с Трекером.
- Ответ Оли по пяти вопросам о правилах API.
- Делить ли сайту строку позиции заказа (вопрос 6 в `order-position-split_questions.md`).
- Портал: переключить Claude Code на `e.lemesheva@12storeez.com` и переопубликовать — когда вернёмся к идее.

## Что прочитать новой сессии
- `projects/returns-2.0/requirements/backend/return-bonus_backend.md` — процесс баллов и доработки по сервисам.
- `projects/returns-2.0/requirements/questions/refund-bonus_questions.md` — решения и вопросы по баллам.
- `projects/returns-2.0/meetings/[2026-11-16 14-00] Баллы из Mindbox_summary.md` — контекст встречи с BTS.
- `projects/returns-2.0/sources/answers/[2026-10-15] Переписка Лемешева — Васильева Mindbox (баллы при частичном возврате).md` — что рекомендовала Ирина.
- `handoff/2026-11-17_14-08_returns-mindbox-analysis-start.md` — карта сообщения Оли.

## Ограничения, о которых нельзя забыть
- `projects/*/sources/` — только чтение; переписку готовить в scratchpad, переносит пользователь.
- `12stz/` — только чтение; Bash с несколькими командами или `for` в `12stz` хук отклоняет — по одной команде, Grep/Read.
- Перед поиском по коду — `graphify query`.
- Задачи на бэк: локальный файл = Трекер; в Трекере менять только по просьбе.
- Публикация во внешние сервисы (портал) — только по явной просьбе; данные прода и код не публиковать.
- Commit и push — только по просьбе пользователя.
- Старые `handoff/` не править.
