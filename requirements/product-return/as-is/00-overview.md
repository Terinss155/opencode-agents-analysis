# AS-IS процесс оформления возврата — обзор

**Статус:** DRAFT
**Дата:** 07.09.2026
**Владелец состава:** этот файл (индекс пошагового AS-IS)

## Назначение

Пошаговое описание того, **как процесс оформления возврата работает сейчас** — от входа в форму до момента, когда в системе фиксируется возврат (позиции переходят в статус «возврат», заказ — в статус `31`). Описание собрано по фактам кодовой базы `12storeez-master` (контроллеры, сервисы, модели, миграции, frontend-компоненты) и сверено с существующими материалами проекта (`api/`, `analysis/`, `sources/`).

Целевой сценарий (`../use-case/product-return_use-case.md`, макеты, TO-BE-драфты) используется только для того, чтобы задать **последовательность логических шагов**. Сам AS-IS основан на реализации, а не на желаемом поведении.

## Границы

| В границах | Вне границ |
|---|---|
| Вход в форму возврата из карточки заказа | Физическая передача возврата, приёмка, экспертиза |
| Выбор позиций, причин, города, способа, данных способа, банковских реквизитов | Изменение / отмена / автоотмена созданной заявки |
| Сохранение реквизитов возврата в заказ (`return-details`) | Возврат денег и баллов, финансовый статус |
| Создание возврата: перевод позиций и заказа в статусы возврата, исходящие интеграции | Формирование ТТН/трек-номеров, статусы транспортных компаний, идентификаторы СДЭК/5Post |

Терминальная точка описания — успешный ответ метода создания возврата и показ экрана «заявка создана».

## Каналы

AS-IS сайта и мобильного приложения — **две разные реализации** с разными эндпоинтами, разным составом экранов и разным способом фиксации возврата. Поэтому пошаговое описание разнесено по подпапкам:

| Канал | Подпапка | Точка входа | Метод создания возврата |
|---|---|---|---|
| Сайт (Frontend Vue + SSR, backend Yii) | [`web/`](web/) | карточка заказа в ЛК → попап `OrderRefundPopup` | `POST /orders/refund/save-reason` |
| Мобильное приложение (core `core.12stz.dev` + gateway `mobile.12stz.dev`) | [`mobile/`](mobile/) | карточка заказа → экран возврата | `POST /mobile/orders/return-positions` (устар. `POST /api/orders/{id}/return`) |

Общая серверная логика у обоих каналов: расчёт доступных способов и дат, сохранение реквизитов возврата в заказ, перевод позиций и заказа в статусы возврата, справочники причин (`cms_return_reasons`, `cms_return_reasons_groups`) и способов (`cms_return_method`).

## Карта процесса (сводно)

| Логический шаг | Сайт (`web/`) | Мобильное приложение (`mobile/`) |
|---|---|---|
| Вход, загрузка формы | `GET /orders/refund/get-positions` (позиции + причины + `need_bank_details` — всё сразу) | `GET /api/orders/{order_id}` (карточка заказа с позициями) |
| Выбор изделий | экран «Выберите изделия», чекбоксы, **без выбора количества** | выбор позиций по `barcode` |
| Выбор причины | экран «Причина возврата» по каждой позиции; причины уже пришли на входе | `GET /mobile/v2/orders/return-reasons` (единый кэшируемый справочник, не зависит от выбора товаров) + выбор по каждой позиции. Два уровня «группа причин → причина» (в TO-BE те же два уровня — «причина → подпричина») |
| Выбор города | экран «Оформление возврата» → блок города (geo API) | экран возврата → блок города (geo API) |
| Выбор способа | `GET /api/orders/{id}/return-method-list` | `GET /mobile/orders/{id}/return-method-list` |
| Данные способа | курьер → адрес + индекс + дата; ПВЗ (`sdek-pvz` / `5post`) → только дата | аналогично; `method_return` по умолчанию `courier` |
| Банковские реквизиты | если `need_bank_details`: `POST /user/cabinet/return-item/ajax/check-bank-details` (сохранение в `cms_users_refund`) | если оплата курьеру: поля реквизитов прямо в теле `return-positions` |
| Подтверждение и сохранение реквизитов возврата | `POST /api/orders/{id}/return-details` | `POST /mobile/orders/{id}/return-details` |
| Создание возврата | `POST /orders/refund/save-reason` | `POST /mobile/orders/return-positions` |
| Результат | окно успеха, перезагрузка карточки | `success: true`, обновление карточки |

## Сквозная диаграмма — Сайт

```mermaid
sequenceDiagram
    actor U as Пользователь
    participant W as Сайт (попап)
    participant B as Backend
    participant DB as БД
    participant GEO as Гео-сервис
    participant EXT as RetailCRM / Mindbox / Lamoda

    U->>W: «Оформить возврат»
    W->>B: GET /orders/refund/get-positions
    B->>DB: cms_order_positions (status=1, price>1) + cms_return_reasons(_groups)
    B-->>W: позиции + причины + need_bank_details

    Note over U,W: выбор изделий и причин — только на клиенте

    U->>W: выбрать город
    W->>GEO: GET .../geo/.../cities (+ details)
    GEO-->>W: город (geo_id, ФИАС, регион, страна)
    W->>B: GET /api/orders/{order_id}/return-method-list
    B->>DB: cms_delivery_city ⋈ cms_delivery_tk + cms_return_method
    B-->>W: способы + доступные даты

    Note over U,W: выбор способа, адреса/даты — на клиенте

    opt оплата не онлайн
        U->>W: сохранить банковские реквизиты
        W->>B: POST /user/cabinet/return-item/ajax/check-bank-details
        B->>DB: INSERT/UPDATE cms_users_refund
        B-->>W: success
    end

    U->>W: «Подтвердить возврат»
    W->>B: POST /api/orders/{order_id}/return-details
    B->>DB: UPDATE cms_orders (return_city, return_date, return_delivery_tk, return_postal, return_address)
    B->>EXT: RetailCRM — обновить заказ
    B-->>W: success
    W->>B: POST /orders/refund/save-reason
    B->>DB: UPDATE cms_order_positions (status=9, reason); UPDATE cms_orders (status=31, user_refund)
    B->>EXT: RetailCRM + Mindbox (+ Lamoda) — обновить заказ
    B-->>W: success
    W-->>U: «Заявка уже у нас» → перезагрузка карточки
```

## Сквозная диаграмма — Мобильное приложение

```mermaid
sequenceDiagram
    actor U as Пользователь
    participant M as Мобильное приложение
    participant B as Backend
    participant DB as БД
    participant GW as Мобильный шлюз (гео)
    participant Q as Очереди (RabbitMQ)
    participant EXT as RetailCRM / Mindbox / 1С

    U->>M: открыл карточку заказа
    M->>B: GET /mobile/orders/{order_id}
    B->>DB: cms_orders + cms_order_positions
    B-->>M: карточка (messages[can_be_returned], positions[], return.is_bank_data_required)

    U->>M: «Оформить возврат» → выбор изделий (barcode)

    M->>B: GET /mobile/v2/orders/return-reasons
    B->>DB: cms_return_reasons(_groups) (кэш Redis)
    B-->>M: справочник «группа → причина» (+ current_datetime, available_dates_return)

    Note over U,M: выбор причин по каждой позиции — на клиенте

    U->>M: выбрать город
    M->>GW: GET /api/v1/geo/.../cities (+ details)
    GW-->>M: параметры города
    M->>B: GET /mobile/orders/{order_id}/return-method-list
    B->>DB: cms_delivery_city ⋈ cms_delivery_tk + cms_return_method
    B-->>M: способы + доступные даты

    Note over U,M: выбор способа, адреса/даты, реквизитов — на клиенте

    U->>M: подтвердить данные способа
    M->>B: POST /mobile/orders/{order_id}/return-details
    B->>DB: UPDATE cms_orders (return_city, return_date, return_delivery_tk, return_postal, return_address)
    B->>EXT: RetailCRM — обновить заказ
    B-->>M: success

    U->>M: подтвердить создание возврата
    M->>B: POST /mobile/orders/return-positions { items:[{barcode, reason_id}], реквизиты при оплате курьеру }
    B->>DB: UPDATE cms_order_positions (status=9, reason); UPDATE cms_orders (status=31, user_refund)
    B->>Q: задачи UPDATE заказа
    Q->>EXT: RetailCRM, Mindbox, 1С
    B-->>M: success → обновление карточки заказа
```

## Что такое «возврат» в AS-IS

Отдельной сущности возврата (`return`, `return_request`) в базе **нет**. «Создание возврата» = набор изменений заказа и позиций:

| Что меняется | Где | Значение |
|---|---|---|
| Статус возвращаемых позиций | `cms_order_positions.status` | `9` — «Возврат (если был отгружен)» |
| Причина по позиции | `cms_order_positions.reason` | код причины из `cms_return_reasons` |
| Статус заказа | `cms_orders.status` | `31` — внутреннее название «Возврат из ЛК», клиентское «Заявка на возврат принята», код `vozv-lk`, группа `approval` (по справочнику `cms_order_statuses`) |
| Реквизиты возврата | `cms_orders`: `return_city`, `return_address`, `return_postal`, `return_date`, `return_delivery_tk` | заполняются на запросе сохранения реквизитов возврата (`return-details`) |
| Банковские реквизиты (если оплата не онлайн) | `cms_orders.user_refund` (в виде JSON) | из таблицы `cms_users_refund` |
| Исходящие интеграции | очереди на отправку в RetailCRM, Mindbox, Lamoda (web) / RetailCRM, Mindbox, 1С (mobile) | обновление заказа |

`cms_orders.return_money`, `return_store`, `return_interval`, `return_reason` (верхнего уровня), `return_status_wms`, `return_order_num` на этом этапе **не заполняются**.

### Когда данные уходят на бэкенд

Серверного «черновика оформления» в AS-IS нет (и в BRD такого требования нет). Пока пользователь выбирает товары, причины, город и способ, на бэкенд идут только **чтения** (`get-positions`, `return-method-list`, гео) — записей нет.

| Канал | Что пишется до кнопки «Подтвердить возврат» | Что пишется по кнопке |
|---|---|---|
| Сайт | только `cms_users_refund` — когда пользователь сохраняет форму банковских реквизитов (шаг 07), отдельным запросом | `POST return-details` (реквизиты возврата в `cms_orders` + пуш в RetailCRM), затем `POST save-reason` (статусы `9`/`31`, `cms_orders.user_refund`, интеграции) |
| Мобильное приложение | ничего | `POST return-details` (реквизиты возврата в `cms_orders` + пуш в RetailCRM), затем `POST return-positions` (статусы `9`/`31`, `cms_orders.user_refund` из тела запроса, интеграции) |

## Ключевые отличия AS-IS от TO-BE (сводно)

Подробности — в разделе «Соответствие TO-BE» / «Отличия от TO-BE» каждого шага. Там же различия разделены на подтверждённые расхождения и пункты «под вопросом» (когда в целевом сценарии на этом месте открытый вопрос, а не утверждённое требование).

| Тема | AS-IS | TO-BE |
|---|---|---|
| Выбор количества позиции | На сайте отсутствует (возврат позиции целиком); в МП возврат по `barcode` | Управление возвращаемым количеством |
| Способы возврата | Только `courier`, `sdek-pvz`, `5post` (таблица `cms_return_method` + маппинг типов доставки `1/11/15`) | + Магазин, Аутлет, «Цветной», Почта России, офис СДЭК |
| Выбор конкретного ПВЗ / постамата | Для `sdek-pvz` и `5post` адрес и индекс **обнуляются сервером** при сохранении; конкретная точка не выбирается и не сохраняется | Выбор точки на карте/в списке, сохранение её идентификатора и адреса |
| Интервал курьера | Сохраняется только дата (`return_date`); поле `return_interval` не заполняется | Дата + интервал |
| Предвыбор способа по способу получения заказа | Не реализован | Предвыбор по способу доставки заказа |
| Правило «Почта России только для Калининграда» | Неприменимо (канала нет) | Есть |
| Отдельная сущность и номер возврата | Нет; изменения в `cms_orders` / `cms_order_positions` | Заявка с номером и статусной моделью |
| Клиентские идентификаторы (штрихкод/накладная СДЭК, QR/PIN 5Post) | В коде оформления не формируются | Формируются, показываются после обновления карточки |

## Условные обозначения

- **AS-IS** — подтверждено кодом / API / БД / миграцией / материалами проекта.
- **TO-BE** — описано в целевых сценариях/макетах как желаемое поведение.
- **Допущение** — логически следует из кода, но не подтверждено напрямую (нет лога/теста/явной ветки).
- **Не уточнено** — данных нет ни в коде, ни в материалах.

## Справочник сущностей и таблиц

Имена таблиц даны с префиксом `cms_` (конфигурация `TABLE_PREFIX='cms_'`; в коде модели объявлены как `{{%имя}}`, физическая таблица — `cms_имя`). Префикс `cms_return_reasons*` подтверждён проектной ER-моделью `sources/technical/database/as-is-cms-orders-full-er-v8.md`; для остальных таблиц он выведен из той же конфигурации.

| Таблица | Роль в процессе | Ключевые поля |
|---|---|---|
| `cms_orders` | Заказ; носитель статуса возврата и реквизитов возврата | `status`, `end_date`, `return_city`, `return_address`, `return_postal`, `return_date`, `return_delivery_tk`, `user_refund` |
| `cms_order_positions` | Позиция заказа; при возврате переходит в статус `9`, в поле `reason` пишется код причины | `status`, `reason`, `barcode`, `price_before_discount` |
| `cms_return_reasons_groups` | Группа причин возврата | `id`, `title`, `active`, `order` |
| `cms_return_reasons` | Причина возврата | `code`, `title`, `group_id`, `active`, `_order` |
| `cms_return_method` | Справочник способов возврата | `alias`, `title`, `description`, `is_enabled` (сайт), `is_enabled_mobile` (МП) |
| `cms_users_refund` | Банковские реквизиты пользователя для возврата денег (одна запись на пользователя) | `user_id`, `surname`, `name`, `patronymic`, `bank_name`, `bank_inn`, `bank_bic`, `user_account`, `user_card_number` |
| `cms_order_statuses`, `cms_order_position_statuses` | Справочники статусов заказа и позиции | `internal_id`, `code`, `cancel_status` |
| `cms_parameters` | Настроечные параметры; используется `days_can_be_returned` — срок возврата в днях | — |
| `cms_delivery_city`, `cms_delivery_tk` | Города и транспортные компании; по их связке определяются доступные способы возврата (типы `1`, `11`, `15`) | `delivery_city.geo_id`, `delivery_city.tk_id`, `delivery_tk.type` |
| `cms_return_details_config` | Конфигурация расчёта дат курьерского возврата | задержка, число дат, время-отсечка, «доступен ли выбор даты» |

## Индекс файлов

### Сайт — [`web/`](web/)

1. `01-entry-and-load-return-form.md` — вход из карточки заказа, доступность кнопки, `GET /orders/refund/get-positions`
2. `02-select-return-items.md` — экран «Выберите изделия»
3. `03-select-return-reason.md` — экран «Причина возврата»
4. `04-select-city.md` — блок города на экране «Оформление возврата»
5. `05-select-return-method.md` — `GET /api/orders/{id}/return-method-list`
6. `06-fill-return-method-details.md` — адрес/индекс/дата (курьер) или дата (ПВЗ)
7. `07-fill-bank-details.md` — банковские реквизиты
8. `08-confirm-and-create-return.md` — `POST return-details` + `POST save-reason`

### Мобильное приложение — [`mobile/`](mobile/)

1. `01-load-order-card.md` — `GET /mobile/orders/{order_id}`, доступность возврата, `return.is_bank_data_required`
2. `02-select-return-items.md` — выбор позиций по `barcode`
3. `03-select-return-reasons.md` — `GET /mobile/v2/orders/return-reasons` (единый кэш-справочник, не зависит от выбора товаров; несёт также `current_datetime`, `available_dates_return`) + выбор причины по каждой позиции
4. `04-select-city.md` — гео gateway, параметры города
5. `05-select-return-method.md` — `GET /mobile/orders/{order_id}/return-method-list`
6. `06-confirm-return-details.md` — `POST /mobile/orders/{order_id}/return-details`
7. `07-create-return.md` — `POST /mobile/orders/return-positions` (создание возврата, реквизиты в теле)

> Исходный код мобильного клиента в `12storeez-master` отсутствует — есть только backend и web-фронтенд. Экранное поведение МП в файлах `mobile/02`–`mobile/04` восстановлено по контракту API и серверным валидаторам; такие места помечены.
