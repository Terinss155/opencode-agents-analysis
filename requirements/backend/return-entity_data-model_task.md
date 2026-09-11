# Задача: Возврат как отдельная сущность — модель данных

**Тип:** проектирование модели данных + миграции БД.
**Домен:** E-commerce / Fashion-ритейл, процесс возврата товара.
**Статус:** DRAFT — требует проработки SA + ревью бэкенда и архитектора.
**Дата:** 2026-09-08.
**Связанные артефакты:** `../use-case/use-case-to-be.md` (UC-RET-01…06), `available-return-quantity_backend.md`, `return-eligibility_backend.md`, `../user-story/user-story.md` (US-101…US-206).

---

## 1. Цель и проблема

### Проблема (AS-IS)

Отдельной сущности возврата **не существует**. Возврат хранится «размазанным» по таблице заказа и позиций:

- статус возврата = статус **заказа** (`cms_orders.status = 31 ORDER_RETURNED_LK`);
- параметры возврата — плоские поля `cms_orders.return_*`;
- банковские реквизиты — JSON-снимок в `cms_orders.user_refund`;
- возвращаемая позиция — смена `cms_order_positions.status` на `9 (STATUS_LOST)` / `5 (STATUS_RETURNED)`, **без количества**;
- существующая `cms_order_return_positions` пишется **только из 1С**, не из клиентского оформления.

Из-за этого невозможно: несколько возвратов по одному заказу с независимыми статусами, частичный возврат по количеству, отдельная клиентская статусная модель возврата, история статусов возврата, корректный расчёт `available_return_quantity`.

### Цель (TO-BE)

Спроектировать и создать набор таблиц, где **вся информация по возврату хранится в собственных сущностях**:

1. `cms_returns` — заявка на возврат (шапка).
2. `cms_return_positions` — **новая** таблица, строка на возвращаемую единицу (причина, брак, статус, приёмка — по единице).
3. `cms_return_position_history` — **новая** история статуса единицы (приёмка / экспертиза / вердикт).
4. `cms_return_statuses` + `cms_return_status_groups` — собственная статусная модель возврата.
5. `cms_return_status_history` — история переходов статуса заявки.
6. `cms_return_statuses_map` — маппинг внешних кодов статусов (СДЭК / 5POST / WMS / 1С) на внутренние.
7. Переиспользовать существующие справочники причин.

**Принцип:** `cms_orders.status` и `cms_orders.return_*` больше **не являются источником истины** по возврату. Заказ после оформления возврата остаётся в своём статусе; возврат живёт своим жизненным циклом.

---

## 2. AS-IS: что уже есть (проверено по коду)

### 2.1. Таблицы, которые существуют

| Таблица (физ. имя) | Что хранит | Кто пишет | Вывод для задачи |
|---|---|---|---|
| `cms_order_return_positions` | `id, order_id, position_id, return_quid` (UUID 36), `barcode, quantity` | **Только 1С-инбокс** (`OrderUpdateService::handleReturnPositions()`). Нет статуса, дат, способа | **Не переиспользовать** под клиентскую заявку. Оставить как интеграционный слой 1С либо мигрировать данные (см. §6) |
| `cms_order_position_refunds` | `position_id, return_quid, barcode, quantity, refunded_at` | Модуль Receipt (данные чеков) | Источник «сколько денег фактически вернули». Кандидат для `available_return_quantity` (TBD-10) |
| `cms_order_position_realizations` | `position_id, barcode, quantity` | Модуль Receipt | Источник «сколько фактически выкуплено» (TBD-09) |
| `cms_return_reasons` | `id, group_id, code, title, description, active, _order` | Справочник (админка) | **Переиспользовать.** Совпадает с наброском |
| `cms_return_reasons_groups` | `id, title, order, active, created_at, updated_at` | Справочник | **Переиспользовать.** Совпадает с наброском |
| `cms_return_reasons_content` | `id, lang_id, parent_id, title` | Локализация названий причин/групп | **В наброске упущено.** Названия причин клиенту резолвятся отсюда |
| `cms_return_method` | `id, alias, title, description, is_enabled, is_enabled_mobile` (`courier` / `cdek` / `5post`) | Справочник, миграция `m260318_074226` | Справочник способов возврата. `cms_returns.delivery_method` ссылается на `alias` |
| `cms_return_details_config` | Конфиг доступных дат для курьера | Справочник | Не входит в эту задачу |
| `cms_order_return_statuses_wms` | `id, code, title` (плоский справочник) | Справочник WMS | Частный случай маппинга. Обобщается в `cms_return_statuses_map` |
| `cms_users_refund` (`users_refund`) | `user_id, bank_name, bank_inn, bank_bic, user_account, user_card_number, name, surname, patronymic` | ЛК пользователя, постоянная запись **на пользователя** | Источник банковских реквизитов. В возврат класть **снимок**, а не только FK (реквизиты не должны «плыть» при редактировании профиля) |

### 2.2. Поля `cms_orders`, относящиеся к возврату (AS-IS)

`status` (→ 31), `return_status_wms`, `return_order_num`, `return_delivery_method`, `return_delivery_tk`, `return_city`, `return_address`, `return_postal`, `return_date`, `return_interval` (строкой; фактически **не заполняется**), `return_reason` (= `cms_return_reasons.code`, на уровне заказа), `return_store` (int), `return_money` (varchar: «Не возвращать» / «Наличные» / «На карту»), `user_refund` (JSON реквизитов), `cancel_reason` / `client_cancel_reason_id` / `client_cancel_reason_text` / `is_cancel_site`.

> Все эти поля в TO-BE переезжают в `cms_returns` / `cms_return_positions`. В `cms_orders` они остаются только для обратной совместимости на переходный период (см. §6).

### 2.3. Как создаётся возврат сейчас

- **Оформление из ЛК** (`OrderRefundService::refundPositions()`): меняет статус позиций → `STATUS_LOST` + `reason`; пишет `user_refund` в заказ (если оплата не онлайн); меняет статус **заказа** → `ORDER_RETURNED_LK`; шлёт в RCRM / Mindbox / Lamoda outbox. **Записи о «заявке» не создаётся.**
- **Детали возврата** (`POST /api/orders/{id}/return-details` → `OrderService::updateOrderReturnDetails()`): пишет `return_city`, `return_date`, `return_delivery_tk`, `return_postal`, `return_address` — снова в `cms_orders`.
- **Из 1С** (`OrderUpdateService`): пишет `cms_order_return_positions` + `return_status_wms`.

### 2.4. Статусная модель возврата AS-IS

Отдельной **нет**. Есть только флаг `cms_order_statuses.is_returned` у статусов заказа + плоский `cms_order_return_statuses_wms`. Клиентской модели («Заявка принята» → «Товар в пути» → «Возврат принят» → «Деньги возвращены») в БД нет.

---

## 3. Разбор набросков — комментарии

Легенда: 🟢 верно / оставить · 🟡 уточнить · 🔴 проблема / переделать · ➕ упущено, добавить.

### 3.1. `cms_returns` (новая, шапка возврата)

| Поле из наброска | Комментарий |
|---|---|
| `id` | 🟢 PK. |
| `return_guid` (UUID) | 🟡 Согласовать с существующим `cms_order_return_positions.return_quid` (UUID, ровно 36 символов, с дефисами). Либо переиспользовать его как значение, либо явно завести новый и описать связь `1С return_quid ↔ cms_returns.return_guid`. Индекс **unique**. |
| `user_id` | 🟡 Не обязателен (выводится из `order_id → cms_orders.user_id`). Допустимо как **денормализация** для выборки «все возвраты пользователя» — пометить как денорм, заполнять при создании. |
| `order_id` | 🟢 FK → `cms_orders.id`, **не** unique (один заказ → N возвратов). Индекс. |
| `status` (без номера) **и** `status_id` (стр. 5) | 🔴 **Дубль.** Это одно поле. Оставить одно — `status_id` (или `status`, по аналогии с `cms_orders.status`) → FK на `cms_return_statuses.internal_id`. Вторую строку удалить. |
| `return_order_num` | 🟡 AS-IS `cms_orders.return_order_num`. Источник подтвердить (1С? генерируем сами?). Nullable до подтверждения. |
| `return_status_wms` | 🟡 Оставить nullable. Лучше — `wms_status_id` → FK на справочник, а сам справочник `cms_order_return_statuses_wms` поглотить маппингом `cms_return_statuses_map` (source = `WMS`). |
| `delivery_method` | 🟢 AS-IS `cms_orders.return_delivery_method`. FK → `cms_return_method.alias`. |
| `delivery_tk` | 🟢 AS-IS `cms_orders.return_delivery_tk`. Nullable (магазин). |
| `city` / `city_fias` | 🟢 `city` — AS-IS `cms_orders.return_city`. `city_fias` — 🟢 добавить (нужен гео/логистике). |
| `address` / `postal` | 🟢 AS-IS `cms_orders.return_address` / `return_postal`. |
| `point_id` / `point_provider` | 🟡 Новое. Нужно, когда канал требует фиксации точки (СДЭК/5POST/магазин). Обязательность зависит от финального процесса (UC-RET-04.2/04.3 — «точка не сохраняется» в AS-IS). Nullable. |
| `date` | 🔴 Плохое имя (зарезервированное слово в ряде СУБД, неинформативно). Переименовать → `handover_planned_date` или `planned_date`. AS-IS `cms_orders.return_date`. |
| `interval_from` / `interval_to` | 🟢 Разбивка вместо строки — правильно. ⚠️ В AS-IS `return_interval` **не заполняется вообще** — это поля под будущий функционал выбора интервала (UC-RET-04.1). Пометить «TO-BE, пока не используется». |
| `handover_deadline` | 🟢 ➕ важно (US-109/110 — доступность отмены и автоотмена по сроку передачи). Правило расчёта — открытый вопрос (см. §5). |
| `handed_over_at` | 🟢 Факт передачи. Триггер зависит от канала. |
| `external_return_id` | 🟢 Интеграционный ID (1С / логистика). |
| `tracking_number` | 🟢 Отдельно от `cms_orders.track_number` — верно. Nullable. |
| `waybill_number` / `waybill_url` | 🟡 Канало-специфично (СДЭК). Много NULL. Допустимо в шапке для MVP; при росте канальных полей — вынести в `cms_return_delivery`. |
| `qr_code` / `pin_code` | 🟡 То же. Для розницы QR генерируем мы, для 5POST — от логиста. Nullable. |
| `refund_amount` / `refund_bonus_amount` | 🟢 Нужны для карточки. Источник и алгоритм частичного расчёта со скидками — открытый вопрос (см. §5). |
| `refund_method` | 🔴 Дубль с нижней заметкой `return_money` («Не возвращать / Наличные / На карту»). Свести в одно поле. AS-IS `cms_orders.return_money`. |
| `cancel_reason` | 🔴 Тип `varchar`, а **пример — дата** (`2026-09-06 00:05:11`) — ошибка. Разбить: `cancel_reason_id` (FK на справочник причин отмены возврата — **новый**, не переиспользовать `cms_order_cancel_reasons`) + `cancelled_at` (datetime) + опц. `cancel_comment`. |
| `created_at` / `updated_at` | 🟢 |

**➕ Упущено в `cms_returns`:**

- ➕ `return_type` / `is_partial` — полный / частичный возврат. (В наброске статусов `title = "Полный возврат"` — это **тип**, а не статус; не смешивать.)
- ➕ `created_channel` — где оформлен (`site` / `mobile`).
- ➕ `bank_details_snapshot` (JSON) или `bank_details_id` (FK → `cms_users_refund`) + снимок. AS-IS кладёт JSON в `cms_orders.user_refund`. **Реквизиты фиксировать на момент создания возврата** (снимок), иначе поедут при редактировании профиля. Снимок заполняется **только при оплате курьеру при получении** (`payment_method ∈ {CASH_COURIER=3, CASHLESS_COURIER=5}` — доставка «курьер с примеркой»); обычный курьер = только онлайн-оплата → поле пустое, деньги идут исходным способом (см. UC-RET-04.6). В снимке `patronymic` (отчество) — обязательное поле.
- ➕ `refund_deadline` + `refunded_at` — плановый срок и факт возврата денег (US-111: до 10 дней).
- ➕ `return_store` (int) — магазин/склад приёмки (в наброске только в нижней заметке).
- ➕ `is_bank_data_required` (bool) — снимок признака на момент оформления. **TO-BE:** истинен только при `OrderHelper::isCourierPayment()` (`payment_method` 3 или 5), а не при любой не-онлайн оплате. Веб-логику `!ALL_ONLINE_PAYMENT_METHODS` сузить до этого.
- ➕ `refund_target` — куда возвращаются деньги: `original_payment` (исходный способ, все случаи кроме оплаты курьеру) / `bank_details` (по снимку реквизитов, оплата курьеру). Заменяет AS-IS `cms_orders.return_money`.
- ➕ `version` (int) — оптимистичная блокировка для конкурентных переходов статуса и отмены заявки (в `cms_orders` паттерн уже есть).
- ➕ Индексы: `order_id`, `status_id`, `return_guid` (unique), `created_at`, `handover_deadline` (для джобы автоотмены).
- 🟡 Причины возврата на уровне заявки **быть не должно** — `BR-COM-03`: причина отдельно для каждого изделия → только в `cms_return_positions`. Явно зафиксировать.

### 3.2. `cms_return_positions` — **в наброске отсутствует, обязательна**

Существующая `cms_order_return_positions` (из 1С) под клиентскую заявку не подходит. Нужна новая таблица.

**Гранулярность: строка на одну возвращаемую единицу**, а не на SKU-линию с `quantity`. Причина — у единиц одного штрихкода в одном возврате бывает **две независимые оси расхождения**:

1. **Разная причина.** Клиент вернул 3 одинаковых платья: 2 — «не подошёл размер», 1 — «брак» (`BR-COM-03` — причина отдельно для каждого изделия; мобильный AS-IS уже шлёт `reason_id[]` массивом, хоть и берёт первый).
2. **Разная судьба на приёмке.** Одну приняли сразу, вторую отправили на экспертизу → приняли, третью → отклонили. Разные даты приёмки → разные сроки возврата денег.

Агрегированная строка с `quantity` + корзины количеств покрывает только ось 2. Ось 1 она не тянет. Поэтому — строка на единицу; `quantity` в запросе клиента (степпер из `UC-RET-01`) разворачивается в N строк.

| # | Поле | Тип | Описание |
|---|---|---|---|
| 1 | `id` | int | PK |
| 2 | `return_id` | int | FK → `cms_returns.id`. Индекс |
| 3 | `order_position_id` | int | FK → `cms_order_positions.id` (агрегированная строка заказа с `quantity = N`). Индекс |
| 4 | `barcode` | int | Денормализация для интеграций и дедупа расчёта количества |
| 5 | `reason_code` | varchar | → `cms_return_reasons.code`. Скаляр на единицу. Группа выводится джойном `group_id → cms_return_reasons_groups.id` (см. §3.7) |
| 6 | `is_defective` | tinyint(1) | Признак «Брак» по этой единице (`BR-COM-14`) |
| 7 | `status_id` | int | Статус единицы: `awaiting` (создана, не поступила) / `received` / `in_expertise` / `accepted` / `rejected` / `returned_to_client`. Скаляр — корзины и дельты не нужны |
| 8 | `condition_code` | varchar | Состояние при приёмке. Nullable |
| 9 | `rejection_reason` | varchar | Вердикт при `rejected`. Nullable |
| 10 | `accepted_at` | datetime | Дата приёмки как годной — точка отсчёта 10 дней на возврат денег по этой единице. Nullable |
| 11 | `refund_amount` | decimal(10,2) | Сумма к возврату за единицу (частичный расчёт со скидками — открытый вопрос §5) |
| 12 | `refund_bonus_amount` | decimal(10,2) | Баллы к возврату за единицу |
| 13 | `refunded_at` | datetime | Факт возврата денег за единицу. Nullable |
| 14 | `expertise_doc_url` | varchar | Акт экспертизы по единице. Nullable |
| 15 | `created_at` / `updated_at` | timestamp | |

**Что это упрощает** (по сравнению с корзинами количеств):
- `reason_code`, `is_defective`, `status_id` — скаляры, а не наборы;
- `cms_return_position_history` — простые переходы статуса единицы, без дельт количества;
- `refund_amount` / `accepted_at` / `refunded_at` — по единице, транши возврата денег выражаются естественно;
- `available_return_quantity` = выкуплено − `COUNT`(строк `cms_return_positions` по `order_position_id` в блокирующих и завершённых статусах). Ещё проще, чем сумма количеств.

**Инвариант:** `COUNT(cms_return_positions)` по одному `order_position_id` во всех незавершённых и завершённых возвратах ≤ выкупленное количество этой позиции. Это делает `cms_returns` + `cms_return_positions` **авторитетным источником** для `available_return_quantity` (закрывает TBD-03 / TBD-10).

> **Цена решения:** N строк вместо одной при `quantity = N`. Для fashion-возвратов N мало (1–3), приемлемо. Если у всех единиц причина и судьба совпали — строки почти идентичны (отличаются только `id`), это нормально.
>
> ⚠️ Если продукт решит, что **разные причины у одинаковых единиц не поддерживаются** (одна причина на весь выбор SKU) и приёмка всегда «всё или ничего» — тогда можно вернуться к агрегированной строке с `quantity`. Это развилка для PO (открытый вопрос §5).

### 3.3. `cms_return_status_history` (новая) — история статусов **заявки**

Клиентский таймлайн возврата в целом (для раздела «Возвраты» в ЛК: «Заявка принята» → «Товар в пути» → …).

| Поле | Комментарий |
|---|---|
| `id`, `return_id`, `status_at`, `created_at` | 🟢 |
| `status` | 🟡 Для единообразия назвать `status_id` (как в `cms_returns` и `cms_return_positions`). Связь → `cms_return_statuses.internal_id`. |
| `source` | 🟢 enum-строка (`CDEK` / `5POST` / `DALLI` / `WMS` / `1C` / `SITE` / `MOBILE`). Зафиксировать список или справочник. |
| `external_event_at` | 🟢 **Да, нужно** (nullable). Внешние системы присылают событие задним числом — время наступления ≠ время получения. |
| ➕ `actor` | Кто инициировал: `client` / `operator` / `system` / `external`. |
| ➕ `payload` (JSON) | Сырое событие от источника — для разбора инцидентов интеграций. |
| ➕ `is_client_visible` | Не все переходы показываем клиенту (внутренние WMS-детали). Либо берётся из `cms_return_statuses`. |
| ➕ `comment` | Комментарий оператора при ручном переводе. |

### 3.3-bis. `cms_return_position_history` (новая) — история по **единице возврата**

**Нужна.** Заявка-уровневой истории недостаточно: единицы одного штрихкода расходятся по срокам и вердиктам приёмки/экспертизы. Так как `cms_return_positions` — строка на единицу, история — это простые переходы статуса единицы (без дельт количества).

| Поле | Тип | Описание |
|---|---|---|
| `id` | int | PK |
| `return_position_id` | int | FK → `cms_return_positions.id`. Индекс |
| `status_id` | int | Новый статус единицы (`received` / `in_expertise` / `accepted` / `rejected` / `returned_to_client`) |
| `reason` | varchar | Вердикт/причина перехода (для `rejected` — почему). Nullable |
| `expertise_doc_url` | varchar | Акт экспертизы. Nullable |
| `at` | datetime | Когда событие произошло |
| `external_event_at` | datetime | Время события во внешней системе (WMS/1С), если отличается. Nullable |
| `source` | varchar | `WMS` / `1C` / `STORE` / `OPERATOR` |
| `actor` | varchar | `warehouse` / `operator` / `system` |
| `comment` | varchar | Nullable |
| `created_at` | timestamp | Фиксация в нашей системе |

> Скалярные поля `cms_return_positions` (`status_id`, `accepted_at`, `rejection_reason`) — это «последнее состояние»; полный таймлайн единицы — здесь.

### 3.4. `cms_return_statuses` (новая, справочник)

| Поле | Комментарий |
|---|---|
| `id` + `internal_id` | 🟡 Два ключа — как в `cms_order_statuses` (там та же схема). Оставить для консистентности, но задокументировать: `internal_id` хранится в `cms_returns.status_id` / `cms_return_status_history.status_id`, стабилен; `id` — суррогатный PK справочника. |
| `title` / `client_title` | 🟢 `client_title` по смыслу верный («Заявка на возврат принята»). |
| `code` (`full-return`), `title` (`Полный возврат`) | 🔴 «Полный возврат» — это **тип возврата**, не статус. Примеры статусов: `created` / `accepted` / `in_transit` / `received` / `refunded` / `rejected` / `cancelled`. Пересмотреть примеры и наполнение. |
| `active`, `_order` | 🟢 `_order` с шагом (10, 20, 30…) — верно, вставка между без перенумерации. |
| `group` → `cms_return_status_groups.code` | 🟢 (varchar-code — как в `cms_order_statuses`). |
| `can_be_cancelled` | 🟢 ➕ важно — управляет кнопкой «Отменить заявку» в ЛК (US-109). |
| ➕ `is_final` | Терминальный статус (возврат завершён / отменён) — для джоб и аналитики. |
| ➕ `is_client_visible` | Показывать ли статус клиенту. |
| ➕ `notification_template` / `sends_notification` | US-112 — уведомления о событиях возврата. Либо отдельная таблица «статус → шаблон уведомления». |

### 3.5. `cms_return_status_groups` (новая, справочник)

🟢 Минимально достаточно (`id`, `title`, `code` unique, `active`, `_order`). Копия `cms_status_groups`. Ничего критичного не упущено. ➕ опц. `client_title` (если группы показываются клиенту как этапы).

### 3.6. `cms_return_statuses_map` («??? нужна ли»)

🟢 **Нужна.** Внешние источники (СДЭК, 5POST, DALLI, WMS, 1С) присылают свои коды — без маппинга он окажется захардкожен в коде интеграций.

Предлагаемая структура: `id`, `source` (varchar), `external_code` (varchar), `external_title` (varchar, справочно), `internal_status_id` (int FK → `cms_return_statuses.internal_id`), `active`, `direction` (`inbound` / `outbound` — если наши статусы тоже отдаём наружу). Unique `(source, external_code, direction)`.

Существующий `cms_order_return_statuses_wms` — это частный случай (только WMS, только `code → title`); его логику поглощает эта таблица (`source = 'WMS'`).

### 3.7. `cms_return_reasons` / `cms_return_reasons_groups` — существуют

🟢 Таблицы есть. Фактическая структура (проверено по коду):

| Таблица | Поля (факт) |
|---|---|
| `cms_return_reasons_groups` | `id`, `title`, `order`, `active` — **поля `code` НЕТ** (в наброске указано `code` — ошибка; связь с причинами только по `id`) |
| `cms_return_reasons` | `id`, `group_id` (FK → groups.id), `code`, `title`, `description`, `active`, `_order` |
| `cms_return_reasons_content` | `id`, `lang_id`, `parent_id` (→ reason.id), `title` — **в наброске упущена**; клиентские названия причин берутся отсюда (`ReturnReason::$content->title`) |

**Иерархия AS-IS — ровно 2 уровня: `группа → причина`.** Понятия «подпричина» / `subreason` / `parent_id` внутри `cms_return_reasons` в коде **нет вообще**. Целевая модель «причина → подпричина» — открытый вопрос (UC-RET-02), не реализована.

**Как причина хранится на позиции AS-IS:**
- `cms_order_positions.reason` = **`cms_return_reasons.code`** (строка leaf-уровня, одно значение). Группа **не хранится** — выводится через `group_id`.
- Веб `POST /orders/refund/save-reason`: тело `positions[].reasonCode` → `cms_order_positions.reason`.
- Мобилка `POST /mobile/orders/return-positions`: `items[].reason_id[]` — несмотря на имя, это тоже `code` (`ReturnReason::find()->where(['code' => ...])`), берётся `reset()` — фактически **один код**.
- API отдаёт 2 уровня: веб `reason_groups[].items[].code`, мобилка v2 `items[].items[].code` (у группы даже `id` не отдаётся).

**Вывод для `cms_return_positions`:** одно поле `reason_code` (→ `cms_return_reasons.code`) **на единицу** (строка = единица, см. §3.2 — это и решает кейс «разные причины у одинаковых товаров»). Второе поле (`reason_subcode`) — только под будущую 3-уровневую модель, сейчас не заводить. `group_id` на позиции не хранить.

🟡 AS-IS: `cms_orders.return_reason = cms_return_reasons.code` (на заказе). TO-BE: причина уходит на позицию возврата, поле `cms_orders.return_reason` депрекейтится.

---

## 4. Целевой набор таблиц (итог)

| Таблица | Действие | Назначение |
|---|---|---|
| `cms_returns` | **создать** | Шапка заявки на возврат: канал, адрес/точка, даты, суммы, реквизиты-снимок, текущий статус |
| `cms_return_positions` | **создать** | **Строка на возвращаемую единицу**: `order_position_id`, `reason_code`, `is_defective`, `status_id`, `accepted_at`, суммы. Строка-на-единицу — из-за разных причин и/или разной судьбы у одинаковых единиц |
| `cms_return_position_history` | **создать** | Таймлайн статуса единицы (приёмка / экспертиза / вердикт), с датой, источником, актом экспертизы |
| `cms_return_statuses` | **создать** | Справочник внутренних статусов возврата (клиентская модель) |
| `cms_return_status_groups` | **создать** | Группировка статусов для админки/этапов |
| `cms_return_status_history` | **создать** | Журнал переходов статуса **заявки** (клиентский таймлайн) |
| `cms_return_statuses_map` | **создать** | Маппинг внешних кодов (СДЭК/5POST/WMS/1С) ↔ внутренние статусы; поглощает `cms_order_return_statuses_wms` |
| `cms_return_reasons`, `cms_return_reasons_groups`, `cms_return_reasons_content` | **переиспользовать** | Справочник причин (существует; content — не забыть) |
| `cms_return_method` | **переиспользовать** | Справочник способов возврата (существует) |
| `cms_order_return_positions` | **оставить / решить** | Интеграционный слой 1С. Либо не трогать, либо мигрировать в `cms_return_positions` (§6) |
| `cms_users_refund` | **переиспользовать** | Источник банковских реквизитов; в возврат — снимок |
| `cms_orders.return_*`, `cms_orders.status` | **депрекейт** | Больше не источник истины по возврату; поддерживать на переходный период |

---

## 5. Открытые вопросы (для PO / архитектора / бэкенда)

1. **Гранулярность `cms_return_positions` — подтвердить «строку на единицу».** Предложено: строка на возвращаемую единицу (решает и разные причины у одинаковых товаров, и разную судьбу на приёмке). Развилка: если продукт зафиксирует, что причина — одна на весь выбор SKU **и** приёмка всегда «всё или ничего», можно вернуться к агрегированной строке с `quantity`. По коду AS-IS: причина одна на SKU-линию, но мобилка шлёт `reason_id[]` массивом (задел под пер-юнит).
2. **Статус единицы возврата.** Набор значений `status_id` (`awaiting` / `received` / `in_expertise` / `accepted` / `rejected` / `returned_to_client`) — подтвердить. Статус заявки (`cms_returns.status_id`) вычисляется как роллап по единицам (`partially_accepted` и т. п.) — подтвердить правило.
3. **Правило расчёта `handover_deadline`** по каналам (курьер — выбранная дата; ПВЗ/5POST — норматив ТК; магазин/почта — 14 дней от создания). Не финализировано в UC-RET-04.
4. **Источник и алгоритм `refund_amount`** при частичном возврате со скидками, промокодами, баллами и сертификатами. На единицу; сумма заявки = Σ по принятым единицам. Подтвердить правило распределения скидки на единицу. Также решить, **какую величину показывать клиенту** по каждой единице на экранах возврата (`SCR-RET-01` / `SCR-RET-02`): уплаченную цену (`cms_order_positions.price`) или `refund_amount`.
5. **`return_order_num`** — кто генерирует (мы / 1С) и когда.
6. **`return_guid` vs `cms_order_return_positions.return_quid`** — переиспользовать или новый идентификатор + связь.
7. **Миграция исторических возвратов** из `cms_orders.return_*` — переносить или оставить в заказе (см. §6).
8. **Банковские реквизиты в возврате** — снимок JSON или FK на `cms_users_refund` + версия. Заполняется только при оплате курьеру при получении (`payment_method` 3/5, доставка «курьер с примеркой»); `patronymic` в снимке обязателен; при онлайн-оплате (в т.ч. обычный курьер) реквизиты не собираются (клиенту показывается подсказка про обращение в «Дружбу»).
9. **Куда переезжает `cms_orders.return_status_wms`** — в `cms_returns.wms_status_id` через маппинг или остаётся строкой.
10. **Множественные возвраты по заказу** — подтвердить, что `cms_orders.status` перестаёт меняться на «возвращён» (или меняется только когда возвращён весь заказ).
11. **Нужна ли `cms_return_delivery`** — отдельная таблица канальных полей (waybill/qr/pin/point), если их станет много.
12. **Модель причин: 2 или 3 уровня.** AS-IS — `группа → причина` (одно поле `code` на позицию). Нужна ли целевая `причина → подпричина` (UC-RET-02)? От ответа зависит, добавлять ли `reason_subcode` в `cms_return_positions` и расширять ли справочник причин.
13. **Уведомляет ли WMS/1С о приёмке по-единично** (статус каждой единицы отдельным событием) или общим итогом по SKU? От этого зависит, как раскладывать входящее событие на строки `cms_return_positions`.

---

## 6. Совместимость и миграция

1. **Обратная совместимость интеграций.** `cms_orders.return_*` сейчас читают/пишут: 1С-инбокс (`OrderUpdateService`), RCRM outbox, Lamoda outbox, Mindbox outbox, WMS (`api2/OrdersController`), витрины ЛК (сайт + МП). На переходный период — **дублировать запись** в `cms_orders.return_*` и в новые таблицы, либо ввести адаптер, отдающий старым потребителям данные из `cms_returns`.
2. **`OrderHelper::canBeReturned()` / `isReturned()` / `OrderStatus.is_returned`** — сейчас определяют возможность возврата через статус **заказа**. После разделения сущностей — ревизия: заказ остаётся «Выполнен», право на новый возврат определяется по `cms_returns` + `cms_return_positions` (см. `return-eligibility_backend.md`).
3. **`OrderRefundService::refundPositions()`** — переписать: вместо смены статуса заказа создавать `cms_returns` + `cms_return_positions` в транзакции.
4. **Расчёт `available_return_quantity`** — переключить шаг «занято действующими заявками» на `cms_return_positions` (закрывает TBD-03).
5. **Историческая миграция:** для каждого заказа со статусом `is_returned` или с заполненными `return_*` — создать одну запись `cms_returns` (+ позиции из `cms_order_positions` в статусе `STATUS_LOST/RETURNED` и/или из `cms_order_return_positions`). Маппинг старого `cms_orders.status` → `cms_return_statuses.internal_id` задать в `cms_return_statuses_map` (`source = LEGACY`).
6. **`cms_order_return_positions`** — решить: оставить приёмником 1С и синхронизировать в `cms_return_positions`, либо перенаправить 1С-инбокс сразу на новую таблицу.

---

## 7. Объём задачи (Definition of Done)

- [ ] Финальная ER-модель 7 новых таблиц (`cms_returns`, `cms_return_positions`, `cms_return_position_history`, `cms_return_statuses`, `cms_return_status_groups`, `cms_return_status_history`, `cms_return_statuses_map`) + связи (обновить `erd-model`).
- [ ] Миграции создания таблиц с индексами и FK.
- [ ] Наполнение справочников `cms_return_statuses`, `cms_return_status_groups`, `cms_return_statuses_map` (по клиентской статусной модели из макетов и US-106/US-110).
- [ ] Скрипт исторической миграции `cms_orders.return_*` → `cms_returns` (+ откат).
- [ ] Слой совместимости для 1С / RCRM / Lamoda / Mindbox / WMS на переходный период.
- [ ] Новый эндпоинт карточки возврата `GET /returns/{return_id}` (сайт и МП) — read-модель для `SCR-RET-01` (`../screen-spec/screen-spec.md`, таблица «Параметры экрана»).
- [ ] Обновлённые `available-return-quantity_backend.md` (источник = `cms_return_positions`) и `return-eligibility_backend.md`.
- [ ] Ответы на открытые вопросы §5 зафиксированы или явно отложены с владельцем.

---

## 8. История изменений

| Версия | Дата | Автор | Описание |
|---|---|---|---|
| 1.0 | 08.09.2026 | Системный аналитик | Первичная постановка: AS-IS-инвентаризация по коду, разбор набросков (`cms_returns`, история/справочники статусов, маппинг), добавлена обязательная `cms_return_positions`, миграционная стратегия |
| 1.1 | 08.09.2026 | Системный аналитик | Проверена AS-IS модель причин (2 уровня `группа → причина`, одно поле `code`, подпричин в коде нет) → одно поле `reason_code`. Добавлена таблица `cms_return_position_history` отдельно от истории статуса заявки |
| 1.2 | 08.09.2026 | Системный аналитик | Гранулярность `cms_return_positions` изменена на **строку на возвращаемую единицу** (а не SKU-линию с `quantity`): у одинаковых единиц бывают разные причины (`BR-COM-03`) и/или разная судьба на приёмке/экспертизе. Скалярные `reason_code` / `is_defective` / `status_id` / `accepted_at` вместо корзин количеств; `cms_return_position_history` упрощена до переходов статуса единицы; `available_return_quantity` = выкуплено − COUNT(строк) |
