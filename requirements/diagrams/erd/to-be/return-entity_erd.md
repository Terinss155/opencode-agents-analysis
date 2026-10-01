# ERD-RET. Модель данных возврата (TO-BE)

**Тип:** модель данных (ERD).
**Статус:** DRAFT · **Дата:** 29.09.2026
**Связанные артефакты:** [return-entity_data-model_task.md](../../../backend/return-entity_data-model_task.md) (задача на модель данных), [to-be/mobile/01-load-order-card.md](../../../to-be/mobile/01-load-order-card.md), [to-be/mobile/04-prefill-city-method-point.md](../../../to-be/mobile/04-prefill-city-method-point.md), макеты [mockups/](../../../mockups/) (`v2 Создание возврата`, `v2.1 После создания возврата`)

> У существующих таблиц показаны только поля, участвующие в логике возврата, а не полная структура.
> Размер типов (`int(11)`, `varchar(255)`, `decimal(10,2)`) указан в описаниях полей: Mermaid не поддерживает запятую в типе.
> Описание новых таблиц и новых полей — раздел 4. Расхождения с задачей на модель данных — раздел 5.

## 1. Состав таблиц

| Статус | Таблицы |
|---|---|
| Существуют, не меняются | `cms_users_user`, `cms_users_refund`, `cms_orders`, `cms_order_positions`, `cms_status_groups`, `cms_order_statuses`, `cms_order_position_statuses`, `cms_delivery_types`, `cms_delivery_tk`, `cms_order_return_statuses_wms`, `cms_return_reasons_groups`, `cms_return_reasons`, `cms_payment_types`, `cms_order_receipts` |
| Существуют, добавляются поля | `cms_return_method` (+ `_order`, `instruction`), `cms_catalog_stock` (+ `for_returns`) |
| Новые | `cms_returns`, `cms_return_positions`, `cms_return_statuses`, `cms_return_status_groups`, `cms_return_status_history`, `cms_return_position_statuses`, `cms_return_position_status_history`, `cms_return_changes`, `cms_return_refunds`, `cms_refund_methods`, `cms_payment_type_refund_method`, `cms_return_tk`, `cms_return_tk_city`, `cms_return_method_delivery_type` |

Связь с внешним геосервисом — через поле `geo_id` в `cms_return_tk_city` и `cms_catalog_stock` (геосервис не является таблицей БД).

## 2. Ключевые решения модели

| Тема | Решение |
|---|---|
| Данные товара в позиции возврата | Не копируются. Название, артикул, цвет, размер, фото, цены берутся из позиции заказа по `cms_return_positions.order_position_id` (позиция заказа сама хранит слепок товара на момент покупки) |
| Причина | В позиции возврата всегда хранится группа причины (`reason_group_id`); уточнение (`reason_id`) — если у группы оно есть |
| Способ возврата товара и способ возврата денег | Разные справочники: `cms_return_method` — как товар вернётся (курьер, пункт, магазин, почта); `cms_refund_methods` — куда вернутся деньги (на карту оплаты, по реквизитам, на сертификат, баллами, наличными). `cms_refund_methods` заменяет свободную строку AS-IS `cms_orders.return_money` |
| Способ возврата денег по заказу | Определяется по способу оплаты заказа через `cms_payment_type_refund_method`. Сертификат и баллы — дополнительные строки, если в заказе было их списание |
| Признак «нужны банковские реквизиты» | `cms_refund_methods.requires_bank_data` — единое правило для сайта и мобильного приложения вместо разных правил в коде каналов |
| Суммы | Расчётные и фактические суммы хранятся по штукам (`cms_return_positions`) и по способам возврата денег (`cms_return_refunds`). В шапке заявки (`cms_returns`) сумм нет — итоги считаются по `cms_return_refunds`. При создании заявки сумма расчётных сумм по позициям равна сумме расчётных сумм по способам |
| Пункт выдачи и магазин | Хранится идентификатор и слепок (название, адрес, режим работы) на момент создания — чтобы показать заявку, даже если пункт позже закроется. Магазин — по `store_code` из `cms_catalog_stock`; список магазинов для возврата — по признаку `cms_catalog_stock.for_returns` |
| Штрихкод для сдачи в пункт СДЭК | Формируется из номера отправления `cms_returns.waybill_number`; для 5Post — `qr_code` + `pin_code` |
| Заявление на возврат | Не хранится — формируется при каждом запросе из данных заявки |
| Чек возврата | Ссылка на запись чека `cms_order_receipts` (операция `sell_refund`) |
| История изменений | `cms_return_changes` — изменения полей заявки из любых источников (сайт, 1С, RetailCRM) в виде «поле: было → стало» |

## 3. Диаграмма

```mermaid
erDiagram
    %% ================= СУЩЕСТВУЮЩИЕ: пользователь =================
    cms_users_user {
        int id PK "ID пользователя"
        tinyint is_vic "Признак VIC / Friends & Family"
    }

    cms_users_refund {
        int id PK "ID записи"
        int user_id FK "Пользователь (одна запись на пользователя)"
        varchar bank_name "Название банка"
        varchar bank_inn "ИНН банка"
        varchar bank_bic "БИК банка"
        varchar user_account "Расчётный счёт"
        varchar user_card_number "Номер карты"
        varchar name "Имя владельца"
        varchar surname "Фамилия владельца"
        varchar patronymic "Отчество владельца"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: заказ =================
    cms_orders {
        int id PK "ID заказа"
        int user_id FK "Пользователь"
        varchar order_num "Номер заказа (база номера заявки)"
        varchar type "Тип заказа (reservation = бронь)"
        int status FK "Статус заказа -> cms_order_statuses.internal_id"
        int delivery_method FK "Служба доставки -> cms_delivery_tk.id"
        varchar delivery_slug "Копия cms_delivery_tk.slug"
        int payment_method FK "Способ оплаты -> cms_payment_types.internal_id"
        varchar country "ISO страны доставки"
        varchar state "Регион доставки"
        varchar city "Город доставки"
        varchar city_fias "ID города в геосервисе"
        varchar street "Улица"
        varchar house "Дом"
        varchar housing "Корпус"
        varchar flat "Квартира"
        varchar porch "Подъезд"
        varchar floor "Этаж"
        varchar postal "Индекс"
        varchar full_address "Полный адрес"
        varchar pvz_id "ID пункта выдачи"
        datetime end_date "Дата выполнения заказа"
        varchar lamoda_id "ID заказа Lamoda"
        timestamp created_at "Дата создания"
    }

    cms_order_positions {
        int id PK "ID позиции заказа"
        int order_id FK "Заказ"
        int status FK "Статус позиции -> cms_order_position_statuses.internal_id"
        int item_id "ID товара"
        bigint barcode "Штрихкод"
        varchar model_title_ru "Название товара (слепок)"
        varchar article "Артикул (слепок)"
        varchar color_title_ru "Цвет (слепок)"
        varchar size_title_ru "Размер (слепок)"
        varchar image_mobile_url "Фото (слепок)"
        int quantity "Купленное количество"
        decimal price "Цена со скидкой за единицу (10,2)"
        decimal price_before_discount "Цена до скидки (10,2)"
        decimal sum "Сумма по позиции (10,2)"
        decimal discount_promo "Скидка по промокоду (10,2)"
        decimal discount_bonus "Оплачено баллами (10,2)"
        tinyint is_present "Признак подарка"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: статусы заказа и позиций =================
    cms_status_groups {
        int id PK "ID группы"
        varchar code UK "Код группы (complete, cancel ...)"
        varchar title "Название"
    }

    cms_order_statuses {
        int id PK "ID записи"
        int internal_id UK "Бизнес-код статуса"
        varchar code "Символьный код"
        varchar title "Название"
        varchar client_title "Название для клиента"
        varchar group FK "Группа -> cms_status_groups.code"
        tinyint is_returned "Возвратный статус"
    }

    cms_order_position_statuses {
        int id PK "ID записи"
        int internal_id UK "Бизнес-код статуса"
        varchar code UK "Символьный код (сопоставление с 1С и RetailCRM)"
        varchar title "Название"
        tinyint cancel_status "Признак отмены / возврата"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: доставка и магазины =================
    cms_delivery_types {
        int id PK "ID записи"
        int internal_id UK "Тип службы (1 курьер, 11 5Post, 15 СДЭК ПВЗ ...)"
        varchar title_ru "Название типа"
    }

    cms_delivery_tk {
        int id PK "ID службы доставки"
        varchar slug "Код службы (sdek-pvz, 5post, dalli-msk-nofit)"
        int type FK "Тип -> cms_delivery_types.internal_id"
    }

    cms_catalog_stock {
        int id PK "ID магазина / склада"
        int store_code UK "Код магазина"
        varchar title_ru "Название"
        varchar address "Адрес"
        varchar working_time "Режим работы"
        varchar geo_id "ID города в геосервисе"
        varchar latitude "Широта"
        varchar longitude "Долгота"
        text route "Как добраться"
        tinyint for_returns "НОВОЕ ПОЛЕ: магазин принимает возвраты"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: оплата и чеки =================
    cms_payment_types {
        int id PK "ID записи"
        int internal_id UK "Способ оплаты (1 карта онлайн, 3 наличные курьеру ...)"
        varchar code "Код"
        varchar crm_title "Название"
    }

    cms_order_receipts {
        int id PK "ID чека"
        int order_id FK "Заказ"
        varchar operation "Операция (sell, sell_refund ...)"
        decimal sum "Сумма чека (10,2)"
        text receipt "Данные чека"
        varchar ofd_response "Ответ ОФД"
    }

    %% ================= НОВАЯ: заявка на возврат =================
    cms_returns {
        int id PK "ID заявки"
        char return_guid UK "UUID для межсистемной связи"
        varchar return_num UK "Номер заявки: order_num-return_seq (500128139-01)"
        int return_seq "Порядковый номер заявки в заказе (уникален вместе с order_id)"
        int user_id FK "Пользователь"
        int order_id FK "Исходный заказ"
        int status_id FK "Статус -> cms_return_statuses.internal_id"
        int return_tk_id FK "Служба возврата -> cms_return_tk.id"
        varchar return_order_num "Номер документа возврата в 1С / WMS (если отличается от return_num)"
        varchar return_status_wms FK "Статус WMS -> cms_order_return_statuses_wms.code"
        varchar country "ISO страны возврата"
        varchar region "Регион возврата"
        varchar city "Город возврата"
        varchar city_fias "ID города в геосервисе"
        varchar return_street "Улица (курьер)"
        varchar return_house "Дом, корпус (курьер)"
        varchar return_flat "Квартира / офис (курьер)"
        varchar return_postal "Индекс (курьер)"
        varchar return_address "Полный адрес для показа (курьер)"
        varchar pvz_id "ID пункта сдачи (СДЭК, 5Post)"
        int store_code FK "Магазин -> cms_catalog_stock.store_code"
        varchar pvz_title "Слепок: название пункта / магазина"
        varchar pvz_address "Слепок: адрес пункта / магазина"
        varchar pvz_work_time "Слепок: режим работы пункта / магазина"
        date return_date "Плановая дата передачи"
        varchar return_time "Интервал текстом для клиента"
        varchar return_time_from "Начало интервала"
        varchar return_time_to "Конец интервала"
        datetime handover_deadline "Крайний срок передачи"
        datetime handed_over_at "Фактическая передача"
        varchar external_return_id "ID заявки во внешней системе"
        varchar track_number "Трек-номер"
        varchar waybill_number "Номер отправления СДЭК (из него формируется штрихкод)"
        varchar qr_code "QR-код для сдачи (5Post)"
        varchar pin_code "PIN-код для сдачи (5Post)"
        text user_refund "Слепок реквизитов на момент создания (JSON)"
        int receipt_id FK "Чек возврата -> cms_order_receipts.id"
        varchar cancel_reason "Причина отмены заявки"
        timestamp created_at "Дата оформления"
        timestamp updated_at "Дата изменения"
    }

    cms_return_positions {
        int id PK "ID строки возврата (одна штука)"
        int return_id FK "Заявка"
        int order_position_id FK "Позиция заказа (данные товара берутся из неё)"
        bigint barcode "Копия штрихкода позиции заказа"
        int reason_group_id FK "Группа причины -> cms_return_reasons_groups.id (обязательно)"
        int reason_id FK "Уточнение причины -> cms_return_reasons.id (если есть)"
        int status_id FK "Статус позиции -> cms_return_position_statuses.internal_id"
        int quantity "Количество (1)"
        decimal refund_amount "Расчётная сумма за штуку при оформлении, слепок (10,2)"
        decimal refunded_amount "Фактически возвращено за штуку (10,2), null - ещё не возвращали"
        decimal refund_bonus_amount "Расчётные баллы за штуку, слепок (10,2)"
        decimal refunded_bonus_amount "Фактически возвращено баллами за штуку (10,2)"
    }

    %% ================= НОВЫЕ: возврат денег =================
    cms_refund_methods {
        int id PK "ID способа возврата денег"
        varchar code UK "Код (card_payment, bank_details, certificate, bonus, cash)"
        varchar title "Название для клиента"
        tinyint requires_bank_data "Нужны банковские реквизиты"
        int _order "Сортировка"
        tinyint active "Активен"
    }

    cms_payment_type_refund_method {
        int id PK "ID записи"
        int payment_type UK "Способ оплаты -> cms_payment_types.internal_id"
        int refund_method_id FK "Способ возврата денег -> cms_refund_methods.id"
    }

    cms_return_refunds {
        int id PK "ID строки возврата денег"
        int return_id FK "Заявка"
        int refund_method_id FK "Куда возвращаем -> cms_refund_methods.id"
        decimal refund_amount "Расчётная сумма при оформлении, слепок (10,2)"
        decimal refunded_amount "Фактически возвращено (10,2), null - ещё не возвращали"
        datetime refunded_at "Дата фактического возврата"
    }

    %% ================= НОВАЯ: история изменений заявки =================
    cms_return_changes {
        int id PK "ID записи"
        int return_id FK "Заявка"
        varchar field "Изменённое поле"
        text old_value "Было"
        text new_value "Стало"
        varchar source "Источник (сайт, МП, 1С, RetailCRM, WMS)"
        datetime changed_at "Время изменения"
    }

    %% ================= НОВЫЕ: статусы заявки =================
    cms_return_status_groups {
        int id PK "ID группы"
        varchar code UK "Код группы"
        varchar title "Название"
        tinyint active "Активна"
        int _order "Сортировка"
    }

    cms_return_statuses {
        int id PK "ID записи"
        int internal_id UK "Бизнес-код статуса"
        varchar code UK "Символьный код"
        varchar title "Внутреннее название"
        varchar client_title "Название для клиента"
        varchar group FK "Группа -> cms_return_status_groups.code"
        tinyint active "Активен"
        int _order "Сортировка"
        tinyint can_be_cancelled "Клиент может отменить"
    }

    cms_return_status_history {
        int id PK "ID записи"
        int return_id FK "Заявка"
        int status_id FK "Статус -> cms_return_statuses.internal_id"
        datetime status_at "Время перехода"
        varchar source "Источник (система, WMS, пользователь)"
        datetime external_event_at "Время события во внешней системе"
        timestamp created_at "Время записи в БД"
    }

    %% ================= НОВЫЕ: статусы позиции возврата =================
    cms_return_position_statuses {
        int id PK "ID записи"
        int internal_id UK "Бизнес-код статуса"
        varchar code UK "Символьный код"
        varchar title "Внутреннее название"
        varchar client_title "Название для клиента"
        tinyint active "Активен"
        int _order "Сортировка"
    }

    cms_return_position_status_history {
        int id PK "ID записи"
        int return_position_id FK "Строка возврата"
        int status_id FK "Статус -> cms_return_position_statuses.internal_id"
        datetime status_at "Время перехода"
        varchar source "Источник (система, WMS, пользователь)"
        datetime external_event_at "Время события во внешней системе"
        timestamp created_at "Время записи в БД"
    }

    %% ================= СУЩЕСТВУЮЩИЙ: статусы возврата WMS =================
    cms_order_return_statuses_wms {
        int id PK "ID записи"
        varchar code UK "Код статуса возврата WMS"
        varchar title "Название"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: причины возврата =================
    cms_return_reasons_groups {
        int id PK "ID группы"
        varchar title "Название"
        int order "Сортировка"
        tinyint active "Активна"
        timestamp created_at "Дата создания"
        timestamp updated_at "Дата изменения"
    }

    cms_return_reasons {
        int id PK "ID причины"
        int group_id FK "Группа -> cms_return_reasons_groups.id"
        varchar code UK "Технический код"
        varchar title "Название для клиента"
        text description "Подсказка под уточнением"
        tinyint active "Активна"
        int _order "Сортировка"
    }

    %% ================= Способы и службы возврата товара =================
    cms_return_method {
        int id PK "ID способа (существует)"
        varchar alias UK "Код способа (courier, sdek-pvz, 5post, store, russian-post)"
        varchar title "Название"
        text description "Короткая подсказка под карточкой способа при оформлении"
        text instruction "НОВОЕ ПОЛЕ: инструкция «Что дальше» в созданном возврате"
        int _order "НОВОЕ ПОЛЕ: приоритет вывода"
        tinyint is_enabled "Активен на сайте"
        tinyint is_enabled_mobile "Активен в МП"
    }

    cms_return_tk {
        int id PK "ID службы возврата (НОВАЯ)"
        int return_method_id FK "Способ -> cms_return_method.id"
        varchar slug "Провайдер для логистики"
        varchar title "Название службы"
        varchar rcrm_tk_id "Служба в RetailCRM"
        tinyint is_enabled "Активна"
    }

    cms_return_tk_city {
        int id PK "ID записи (НОВАЯ)"
        int return_tk_id FK "Служба возврата -> cms_return_tk.id"
        varchar geo_id "ID города или региона в геосервисе"
        varchar country "ISO страны"
        varchar region "Регион"
        varchar city "Город"
        tinyint active "Активна в городе"
    }

    cms_return_method_delivery_type {
        int id PK "ID записи (НОВАЯ)"
        int delivery_type UK "Тип доставки -> cms_delivery_types.internal_id"
        int return_method_id FK "Способ -> cms_return_method.id"
    }

    %% ================= СВЯЗИ =================
    %% Пользователь
    cms_users_user ||--o| cms_users_refund : "id -> user_id"
    cms_users_user ||--o{ cms_orders : "id -> user_id"
    cms_users_user ||--o{ cms_returns : "id -> user_id"

    %% Заказ и позиции
    cms_orders ||--|{ cms_order_positions : "id -> order_id"
    cms_orders ||--o{ cms_returns : "id -> order_id"
    cms_orders ||--o{ cms_order_receipts : "id -> order_id"

    %% Статусы заказа и позиций
    cms_status_groups ||--o{ cms_order_statuses : "code -> group"
    cms_order_statuses ||--o{ cms_orders : "internal_id -> status"
    cms_order_position_statuses ||--o{ cms_order_positions : "internal_id -> status"

    %% Доставка заказа
    cms_delivery_types ||--o{ cms_delivery_tk : "internal_id -> type"
    cms_delivery_tk ||--o{ cms_orders : "id -> delivery_method"

    %% Оплата заказа
    cms_payment_types ||--o{ cms_orders : "internal_id -> payment_method"

    %% Заявка и её позиции
    cms_returns ||--|{ cms_return_positions : "id -> return_id"
    cms_order_positions ||--o{ cms_return_positions : "id -> order_position_id"

    %% Статусы заявки
    cms_return_status_groups ||--o{ cms_return_statuses : "code -> group"
    cms_return_statuses ||--o{ cms_returns : "internal_id -> status_id"
    cms_returns ||--|{ cms_return_status_history : "id -> return_id"
    cms_return_statuses ||--o{ cms_return_status_history : "internal_id -> status_id"

    %% Статусы позиции возврата
    cms_return_position_statuses ||--o{ cms_return_positions : "internal_id -> status_id"
    cms_return_positions ||--|{ cms_return_position_status_history : "id -> return_position_id"
    cms_return_position_statuses ||--o{ cms_return_position_status_history : "internal_id -> status_id"

    %% История изменений заявки
    cms_returns ||--o{ cms_return_changes : "id -> return_id"

    %% Статус WMS
    cms_order_return_statuses_wms ||--o{ cms_returns : "code -> return_status_wms"

    %% Причины
    cms_return_reasons_groups ||--o{ cms_return_reasons : "id -> group_id"
    cms_return_reasons_groups ||--o{ cms_return_positions : "id -> reason_group_id"
    cms_return_reasons |o--o{ cms_return_positions : "id -> reason_id"

    %% Возврат денег
    cms_returns ||--|{ cms_return_refunds : "id -> return_id"
    cms_refund_methods ||--o{ cms_return_refunds : "id -> refund_method_id"
    cms_refund_methods ||--o{ cms_payment_type_refund_method : "id -> refund_method_id"
    cms_payment_types ||--o| cms_payment_type_refund_method : "internal_id -> payment_type"

    %% Чек возврата
    cms_order_receipts |o--o| cms_returns : "id -> receipt_id"

    %% Магазин сдачи
    cms_catalog_stock |o--o{ cms_returns : "store_code -> store_code"

    %% Способы и службы возврата товара
    cms_return_method ||--|{ cms_return_tk : "id -> return_method_id"
    cms_return_tk ||--o{ cms_return_tk_city : "id -> return_tk_id"
    cms_return_tk ||--o{ cms_returns : "id -> return_tk_id"

    %% Соответствие «тип доставки -> способ возврата»
    cms_delivery_types ||--o| cms_return_method_delivery_type : "internal_id -> delivery_type"
    cms_return_method ||--o{ cms_return_method_delivery_type : "id -> return_method_id"
```

## 4. Описание таблиц

Обозначения колонки «Ключ»: **PK** — первичный ключ, **FK** — внешний ключ, **UK** — уникальное значение. Колонка «NULL»: **Нет** — поле обязательное (в БД `NOT NULL`), **Да** — может быть пустым (в БД `NULL`); условие обязательности указано в описании.

### 4.1. Заявка на возврат (`cms_returns`)

Шапка заявки: одна строка — одна заявка. Одна заявка относится к одному заказу; по одному заказу может быть несколько заявок.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор заявки (автоинкремент) | `1245` |
| 2 | `return_guid` | `char(36)` | UK | Нет | UUID заявки для обмена с внешними системами (1С, RetailCRM, WMS, логистика) | `3f2b9c1e-7a4d-4e8b-9f10-2c6d5a8e1b74` |
| 3 | `return_num` | `varchar(32)` | UK | Нет | Номер заявки для клиента: `cms_orders.order_num` + «-» + `return_seq` (две цифры с ведущим нулём) | `500128139-01` |
| 4 | `return_seq` | `int` | UK (вместе с `order_id`) | Нет | Порядковый номер заявки внутри заказа. Считается по всем заявкам заказа, включая отменённые, чтобы номера не повторялись | `1` |
| 5 | `user_id` | `int` | FK | Нет | Пользователь, оформивший возврат.<br>Связь: `cms_returns.user_id = cms_users_user.id` | `2115660` |
| 6 | `order_id` | `int` | FK | Нет | Исходный заказ.<br>Связь: `cms_returns.order_id = cms_orders.id` | `500128139` |
| 7 | `status_id` | `int` | FK | Нет | Текущий статус заявки.<br>Связь: `cms_returns.status_id = cms_return_statuses.internal_id` | `10` |
| 8 | `return_tk_id` | `int` | FK | Нет | Служба, которая выполняет возврат. Способ возврата определяется через службу.<br>Связь: `cms_returns.return_tk_id = cms_return_tk.id` | `3` |
| 9 | `return_order_num` | `varchar(255)` | | Да | Номер документа возврата в 1С / WMS, если он отличается от `return_num`. Заполняется после ответа 1С | `ВЗ-000123` |
| 10 | `return_status_wms` | `varchar(255)` | FK | Да | Текущий статус возврата на складе. Заполняется по данным 1С / WMS.<br>Связь: `cms_returns.return_status_wms = cms_order_return_statuses_wms.code` | `accepted` |
| 11 | `country` | `varchar(2)` | | Нет | ISO-код страны возврата | `RU` |
| 12 | `region` | `varchar(255)` | | Да | Регион возврата | `Москва` |
| 13 | `city` | `varchar(255)` | | Нет | Город возврата | `Москва` |
| 14 | `city_fias` | `varchar(36)` | | Нет | Идентификатор города в геосервисе (совпадает с `cms_delivery_city.geo_id`, `cms_orders.city_fias`) | `0c5b2444-70a0-4932-980c-b4dc0d3f02b5` |
| 15 | `return_street` | `varchar(255)` | | Да | Улица забора. Обязательно для курьера | `Кастанаевская` |
| 16 | `return_house` | `varchar(255)` | | Да | Дом, корпус. Обязательно для курьера | `96` |
| 17 | `return_flat` | `varchar(255)` | | Да | Квартира / офис. Для курьера необязательно | `12` |
| 18 | `return_postal` | `varchar(20)` | | Да | Индекс. Обязательно для курьера, если геосервис не определил индекс по адресу | `121108` |
| 19 | `return_address` | `varchar(512)` | | Да | Полный адрес забора одной строкой — для показа клиенту и передачи в службу. Заполняется для курьера | `121108, Москва, ул. Кастанаевская, д. 96, кв. 12` |
| 20 | `pvz_id` | `varchar(64)` | | Да | Идентификатор пункта сдачи в сервисе логистики. Обязательно для пунктов СДЭК и 5Post | `1631548` |
| 21 | `store_code` | `int` | FK | Да | Магазин сдачи. Обязательно для способа «Магазин 12 STOREEZ».<br>Связь: `cms_returns.store_code = cms_catalog_stock.store_code` | `27` |
| 22 | `pvz_title` | `varchar(255)` | | Да | Слепок названия пункта / магазина на момент создания. Заполняется для пунктов и магазинов | `ПВЗ «Москва Трубная»` |
| 23 | `pvz_address` | `varchar(512)` | | Да | Слепок адреса пункта / магазина | `Москва, Трубная ул., д. 32, стр. 4` |
| 24 | `pvz_work_time` | `varchar(255)` | | Да | Слепок режима работы пункта / магазина | `Пн-вс: 10:00–22:00` |
| 25 | `return_date` | `date` | | Да | Плановая дата передачи курьеру. Обязательно для курьера | `2026-10-02` |
| 26 | `return_time` | `varchar(32)` | | Да | Интервал текстом для клиента. Обязательно для курьера | `10:00 — 12:00` |
| 27 | `return_time_from` | `varchar(6)` | | Да | Начало интервала. Обязательно для курьера | `10:00` |
| 28 | `return_time_to` | `varchar(6)` | | Да | Конец интервала. Обязательно для курьера | `12:00` |
| 29 | `handover_deadline` | `datetime` | | Да | Крайний срок передачи («Вернуть до»). Заполняется для пунктов, магазина, Почты России | `2026-10-09 23:59:59` |
| 30 | `handed_over_at` | `datetime` | | Да | Фактическое время передачи товара в службу. Заполняется по событию от службы / 1С | `2026-10-03 14:12:00` |
| 31 | `external_return_id` | `varchar(255)` | | Да | Идентификатор заявки во внешней системе (служба доставки) | `CDEK-7788123` |
| 32 | `track_number` | `varchar(255)` | | Да | Трек-номер отправления | `10234567890` |
| 33 | `waybill_number` | `varchar(255)` | | Да | Номер отправления СДЭК. Из него формируется штрихкод для сдачи в пункт | `273672394` |
| 34 | `qr_code` | `varchar(255)` | | Да | Значение QR-кода для сдачи в пункт 5Post | `5P-8f3a1c` |
| 35 | `pin_code` | `varchar(32)` | | Да | PIN-код для сдачи в пункт 5Post | `947486458` |
| 36 | `user_refund` | `text` | | Да | Слепок банковских реквизитов на момент создания (JSON). Обязательно, если способ возврата денег требует реквизиты (`cms_refund_methods.requires_bank_data = 1`). Источник — `cms_users_refund` | `{"surname":"Гагарин","name":"Виктор","bank_bic":"044525974",...}` |
| 37 | `receipt_id` | `int` | FK | Да | Чек возврата. Заполняется после формирования чека.<br>Связь: `cms_returns.receipt_id = cms_order_receipts.id` (операция `sell_refund`) | `88412` |
| 38 | `cancel_reason` | `varchar(255)` | | Да | Причина отмены заявки. Заполняется при отмене | `Отменено клиентом` |
| 39 | `created_at` | `timestamp` | | Нет | Дата и время оформления заявки | `2026-09-30 12:04:11` |
| 40 | `updated_at` | `timestamp` | | Нет | Дата и время последнего изменения заявки | `2026-10-03 14:12:05` |

### 4.2. Позиция возврата (`cms_return_positions`)

Одна строка — одна возвращаемая штука со своей причиной и своим статусом. Данные товара (название, артикул, цвет, размер, фото, цены) не копируются — берутся из позиции заказа.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор строки возврата | `5001` |
| 2 | `return_id` | `int` | FK | Нет | Заявка, к которой относится строка.<br>Связь: `cms_return_positions.return_id = cms_returns.id` | `1245` |
| 3 | `order_position_id` | `int` | FK | Нет | Позиция заказа, из которой возвращается штука.<br>Связь: `cms_return_positions.order_position_id = cms_order_positions.id` | `5512001` |
| 4 | `barcode` | `bigint` | | Нет | Копия штрихкода позиции заказа — для поиска и сверки с 1С. Источник: `cms_order_positions.barcode` | `2000012345678` |
| 5 | `reason_group_id` | `int` | FK | Нет | Группа причины возврата (то, что клиент выбрал в выпадающем списке).<br>Связь: `cms_return_positions.reason_group_id = cms_return_reasons_groups.id` | `6` |
| 6 | `reason_id` | `int` | FK | Да | Уточнение причины (вариант под группой). Заполняется, если у группы есть уточнения.<br>Связь: `cms_return_positions.reason_id = cms_return_reasons.id` | `41` |
| 7 | `status_id` | `int` | FK | Нет | Текущий статус штуки.<br>Связь: `cms_return_positions.status_id = cms_return_position_statuses.internal_id` | `1` |
| 8 | `quantity` | `int` | | Нет | Количество в строке. Всегда `1` | `1` |
| 9 | `refund_amount` | `decimal(10,2)` | | Нет | Расчётная сумма к возврату деньгами за штуку на момент оформления. После создания не меняется | `12980.00` |
| 10 | `refunded_amount` | `decimal(10,2)` | | Да | Фактически возвращено деньгами за штуку. `NULL` — ещё не возвращали; `0` — отказано | `12980.00` |
| 11 | `refund_bonus_amount` | `decimal(10,2)` | | Нет | Расчётное количество баллов к возврату за штуку на момент оформления. По умолчанию `0` | `130.00` |
| 12 | `refunded_bonus_amount` | `decimal(10,2)` | | Да | Фактически возвращено баллами за штуку. `NULL` — ещё не возвращали | `130.00` |

### 4.3. Возврат денег по способам (`cms_return_refunds`)

Одна строка — один способ, которым клиенту возвращаются деньги по заявке (например, часть на карту, часть на сертификат, часть баллами). Итоги заявки считаются по этой таблице.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор строки | `301` |
| 2 | `return_id` | `int` | FK, UK (вместе с `refund_method_id`) | Нет | Заявка.<br>Связь: `cms_return_refunds.return_id = cms_returns.id` | `1245` |
| 3 | `refund_method_id` | `int` | FK, UK (вместе с `return_id`) | Нет | Куда возвращаются деньги.<br>Связь: `cms_return_refunds.refund_method_id = cms_refund_methods.id` | `1` |
| 4 | `refund_amount` | `decimal(10,2)` | | Нет | Расчётная сумма к возврату этим способом на момент оформления. После создания не меняется | `23750.00` |
| 5 | `refunded_amount` | `decimal(10,2)` | | Да | Фактически возвращено этим способом. `NULL` — ещё не возвращали | `23750.00` |
| 6 | `refunded_at` | `datetime` | | Да | Дата и время фактического возврата | `2026-10-06 11:20:00` |

### 4.4. Способы возврата денег (`cms_refund_methods`) — справочник

Куда клиенту возвращаются деньги. Заменяет свободную строку AS-IS `cms_orders.return_money`.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор способа | `1` |
| 2 | `code` | `varchar(64)` | UK | Нет | Технический код способа | `card_payment`, `bank_details`, `certificate`, `bonus`, `cash` |
| 3 | `title` | `varchar(255)` | | Нет | Название для клиента (блок «Возврат средств») | `На банковскую карту, с которой была произведена оплата` |
| 4 | `requires_bank_data` | `tinyint(1)` | | Нет | Нужны ли банковские реквизиты клиента. По умолчанию `0`. Определяет признак `return.is_bank_data_required` в карточке заказа | `1` для `bank_details` |
| 5 | `_order` | `int` | | Нет | Порядок сортировки. По умолчанию `0` | `10` |
| 6 | `active` | `tinyint(1)` | | Нет | Признак активности. По умолчанию `1` | `1` |

### 4.5. Соответствие способа оплаты способу возврата денег (`cms_payment_type_refund_method`)

По способу оплаты заказа определяет основной способ возврата денег. Одна строка — один способ оплаты.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор записи | `1` |
| 2 | `payment_type` | `int` | FK, UK | Нет | Способ оплаты заказа.<br>Связь: `cms_payment_type_refund_method.payment_type = cms_payment_types.internal_id`; для заказа — `cms_orders.payment_method` | `3` (наличные курьеру) |
| 3 | `refund_method_id` | `int` | FK | Нет | Способ возврата денег для этого способа оплаты.<br>Связь: `cms_payment_type_refund_method.refund_method_id = cms_refund_methods.id` | `2` (`bank_details`) |

### 4.6. История изменений заявки (`cms_return_changes`)

Журнал изменений полей заявки из любых источников. Одна строка — одно изменённое поле.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор записи | `9001` |
| 2 | `return_id` | `int` | FK | Нет | Заявка.<br>Связь: `cms_return_changes.return_id = cms_returns.id` | `1245` |
| 3 | `field` | `varchar(64)` | | Нет | Имя изменённого поля `cms_returns` | `return_date` |
| 4 | `old_value` | `text` | | Да | Значение до изменения. `NULL` — поле было пустым | `2026-10-02` |
| 5 | `new_value` | `text` | | Да | Значение после изменения. `NULL` — поле очищено | `2026-10-03` |
| 6 | `source` | `varchar(32)` | | Нет | Источник изменения | `SITE`, `MOBILE`, `1C`, `RCRM`, `WMS`, `CDEK`, `5POST` |
| 7 | `changed_at` | `datetime` | | Нет | Дата и время изменения | `2026-10-01 09:15:42` |

### 4.7. Статусы заявки (`cms_return_statuses`) — справочник

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор записи справочника | `1` |
| 2 | `internal_id` | `int` | UK | Нет | Бизнес-код статуса. На него ссылаются `cms_returns.status_id` и `cms_return_status_history.status_id` | `10` |
| 3 | `code` | `varchar(64)` | UK | Нет | Символьный код статуса | `created` |
| 4 | `title` | `varchar(255)` | | Нет | Внутреннее название (админка) | `Заявление на возврат создано` |
| 5 | `client_title` | `varchar(255)` | | Нет | Название для клиента (сайт, МП) | `Создан` |
| 6 | `group` | `varchar(64)` | FK | Нет | Группа статуса.<br>Связь: `cms_return_statuses.group = cms_return_status_groups.code` | `in_progress` |
| 7 | `active` | `tinyint(1)` | | Нет | Признак активности. По умолчанию `1` | `1` |
| 8 | `_order` | `int` | | Нет | Порядок сортировки. По умолчанию `0` | `10` |
| 9 | `can_be_cancelled` | `tinyint(1)` | | Нет | Может ли клиент отменить заявку в этом статусе. По умолчанию `0` | `1` |

### 4.8. Группы статусов заявки (`cms_return_status_groups`) — справочник

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор группы | `1` |
| 2 | `code` | `varchar(64)` | UK | Нет | Технический код группы. На него ссылается `cms_return_statuses.group` | `in_progress` |
| 3 | `title` | `varchar(255)` | | Нет | Название группы | `В работе` |
| 4 | `active` | `tinyint(1)` | | Нет | Признак активности. По умолчанию `1` | `1` |
| 5 | `_order` | `int` | | Нет | Порядок сортировки. По умолчанию `0` | `10` |

### 4.9. История статусов заявки (`cms_return_status_history`)

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор записи истории изменения статуса заявки | `1` |
| 2 | `return_id` | `int` | FK | Нет | Заявка, к которой относится запись.<br>Связь: `cms_return_status_history.return_id = cms_returns.id` | `1245` |
| 3 | `status_id` | `int` | FK | Нет | Статус заявки на момент события.<br>Связь: `cms_return_status_history.status_id = cms_return_statuses.internal_id` | `30` |
| 4 | `status_at` | `datetime` | | Нет | Дата и время перехода заявки в статус. Показывается в истории статусов на сайте и в МП | `2026-09-02 18:30:15` |
| 5 | `source` | `varchar(32)` | | Нет | Источник события, на основании которого установлен статус | `CDEK`, `5POST`, `DALLI`, `WMS`, `1C`, `SITE` |
| 6 | `external_event_at` | `datetime` | | Да | Дата и время события во внешней системе, если источник его передаёт. Может отличаться от времени получения события сайтом | `2026-09-02 18:30:15` |
| 7 | `created_at` | `timestamp` | | Нет | Дата и время фиксации изменения статуса в нашей системе | `2026-09-02 18:31:47` |

### 4.10. Статусы позиции возврата (`cms_return_position_statuses`) — справочник

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор записи справочника | `1` |
| 2 | `internal_id` | `int` | UK | Нет | Бизнес-код статуса. На него ссылаются `cms_return_positions.status_id` и `cms_return_position_status_history.status_id` | `1` |
| 3 | `code` | `varchar(64)` | UK | Нет | Символьный код статуса | `awaiting`, `received`, `accepted`, `rejected` |
| 4 | `title` | `varchar(255)` | | Нет | Внутреннее название (админка) | `Принята складом` |
| 5 | `client_title` | `varchar(255)` | | Нет | Название для клиента | `Принят` |
| 6 | `active` | `tinyint(1)` | | Нет | Признак активности. По умолчанию `1` | `1` |
| 7 | `_order` | `int` | | Нет | Порядок сортировки. По умолчанию `0` | `10` |

### 4.11. История статусов позиции возврата (`cms_return_position_status_history`)

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор записи | `1` |
| 2 | `return_position_id` | `int` | FK | Нет | Строка возврата.<br>Связь: `cms_return_position_status_history.return_position_id = cms_return_positions.id` | `5001` |
| 3 | `status_id` | `int` | FK | Нет | Статус штуки на момент события.<br>Связь: `cms_return_position_status_history.status_id = cms_return_position_statuses.internal_id` | `3` |
| 4 | `status_at` | `datetime` | | Нет | Дата и время перехода штуки в статус | `2026-10-04 16:02:10` |
| 5 | `source` | `varchar(32)` | | Нет | Источник события | `WMS`, `1C`, `SITE` |
| 6 | `external_event_at` | `datetime` | | Да | Дата и время события во внешней системе, если источник его передаёт | `2026-10-04 16:00:00` |
| 7 | `created_at` | `timestamp` | | Нет | Дата и время фиксации в нашей системе | `2026-10-04 16:02:31` |

### 4.12. Служба возврата (`cms_return_tk`) — справочник

Кто выполняет возврат товара (аналог `cms_delivery_tk` для доставки). У одного способа возврата может быть несколько служб.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор службы | `3` |
| 2 | `return_method_id` | `int` | FK | Нет | Способ возврата, к которому относится служба.<br>Связь: `cms_return_tk.return_method_id = cms_return_method.id` | `2` |
| 3 | `slug` | `varchar(64)` | UK | Нет | Код провайдера в сервисе логистики. Подставляется в запрос списка пунктов при ручном выборе | `sdek-pvz` |
| 4 | `title` | `varchar(255)` | | Нет | Название службы (админка) | `СДЭК ПВЗ` |
| 5 | `rcrm_tk_id` | `varchar(32)` | | Да | Код службы в RetailCRM для передачи заявки. Заменяет значения, зашитые сейчас в коде (`13`, `567`, `55`) | `567` |
| 6 | `is_enabled` | `tinyint(1)` | | Нет | Признак активности службы. По умолчанию `1` | `1` |

### 4.13. Город работы службы возврата (`cms_return_tk_city`)

В каких городах / регионах работает служба возврата (аналог `cms_delivery_city` для доставки). С `cms_delivery_city` внешним ключом не связана — общее только значение `geo_id`.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор записи | `801` |
| 2 | `return_tk_id` | `int` | FK, UK (вместе с `geo_id`) | Нет | Служба возврата.<br>Связь: `cms_return_tk_city.return_tk_id = cms_return_tk.id` | `3` |
| 3 | `geo_id` | `varchar(36)` | UK (вместе с `return_tk_id`) | Нет | Идентификатор города или региона в геосервисе. Сравнивается с `cityId` / `regionId` запроса способов возврата | `0c5b2444-70a0-4932-980c-b4dc0d3f02b5` |
| 4 | `country` | `varchar(2)` | | Нет | ISO-код страны | `RU` |
| 5 | `region` | `varchar(255)` | | Да | Название региона — для админки и поиска по названию | `Москва` |
| 6 | `city` | `varchar(255)` | | Да | Название города. `NULL`, если запись заведена на весь регион | `Москва` |
| 7 | `active` | `tinyint(1)` | | Нет | Работает ли служба в этом городе / регионе. По умолчанию `1` | `1` |

### 4.14. Соответствие типа доставки способу возврата (`cms_return_method_delivery_type`)

По типу службы доставки заказа определяет способ возврата «как в заказе». Одна строка — один тип доставки.

| # | Атрибут | Тип | Ключ | NULL | Описание | Пример |
|---|---|---|---|---|---|---|
| 1 | `id` | `int` | PK | Нет | Уникальный идентификатор записи | `1` |
| 2 | `delivery_type` | `int` | FK, UK | Нет | Тип службы доставки.<br>Связь: `cms_return_method_delivery_type.delivery_type = cms_delivery_types.internal_id`; для заказа — `cms_orders.delivery_method → cms_delivery_tk.id → cms_delivery_tk.type` | `15` |
| 3 | `return_method_id` | `int` | FK | Нет | Способ возврата для этого типа доставки.<br>Связь: `cms_return_method_delivery_type.return_method_id = cms_return_method.id` | `2` (`sdek-pvz`) |

### 4.15. Новые поля в существующих таблицах

| Таблица | Атрибут | Тип | NULL | Описание | Пример |
|---|---|---|---|---|---|
| `cms_return_method` | `_order` | `int` | Нет | Приоритет способа возврата: порядок вывода и автовыбор «первого по приоритету». По умолчанию `0` | `10` |
| `cms_return_method` | `instruction` | `text` | Да | Инструкция «Что дальше» на экране созданного возврата (для Почты России — с адресом склада). Поле `description` остаётся короткой подсказкой при оформлении | `1. Упакуйте изделия… 2. Принесите посылку в пункт СДЭК…` |
| `cms_catalog_stock` | `for_returns` | `tinyint(1)` | Нет | Магазин принимает возвраты. По умолчанию `0`. Список магазинов для возврата: `geo_id` = город возврата и `for_returns = 1` | `1` |

## 5. Расхождения с задачей на модель данных

Сверка с [return-entity_data-model_task.md](../../../backend/return-entity_data-model_task.md). Решение по каждой строке — за SA; после решения одна из сторон приводится к другой.

| № | Тема | В задаче на модель данных | В этой ERD |
|---|---|---|---|
| 1 | Статусы WMS и внешних систем | Новая таблица `cms_return_statuses_map` (источник, внешний код → внутренний статус); поглощает `cms_order_return_statuses_wms` | `cms_returns.return_status_wms` ссылается на существующий `cms_order_return_statuses_wms.code` |
| 2 | Причина на строке возврата | `reason_code` → `cms_return_reasons.code` (как в AS-IS API); `group_id` на позиции не хранить | `reason_group_id` (обязательно) + `reason_id` (если есть уточнение) |
| 3 | Имя истории строки возврата | `cms_return_position_history` | `cms_return_position_status_history` |
| 4 | Способ / служба возврата в заявке | `cms_returns.delivery_method` → `cms_return_method.alias` | `cms_returns.return_tk_id` → `cms_return_tk.id` (способ — через службу) |
| 5 | Службы и города возврата | Не описаны | `cms_return_tk`, `cms_return_tk_city`, `cms_return_method_delivery_type` |
| 6 | Локализация причин | `cms_return_reasons_content` переиспользуется | Не показана |
| 7 | Поля строки возврата | `is_defective`, `accepted_at` | Нет; есть расчётные и фактические суммы и баллы по штуке |
| 8 | Факт возврата денег | Источник — `cms_order_position_refunds` (данные чеков) | `cms_return_refunds` по способам возврата денег; чек — ссылка на `cms_order_receipts` |
| 9 | Суммы в шапке заявки | `refund_amount` в `cms_returns` | В шапке сумм нет, итоги — по `cms_return_refunds` |
| 10 | Способ возврата денег | `cms_orders.return_money` (свободная строка) переносится в заявку | Справочник `cms_refund_methods` + соответствие по способу оплаты `cms_payment_type_refund_method` |

## 6. Открытые вопросы

1. Правило расчёта суммы к возврату за штуку: распределение скидок на заказ, промокодов, баллов; распределение сертификата (хранится на весь заказ в `cms_giftcard_use`); возвращается ли доставка.
2. Кто формирует номер заявки `order_num-NN`: сайт (и передаёт в 1С) или 1С.
3. Какой идентификатор заявки 1С передаёт вместе со статусом возврата WMS (`return_num` или `return_guid`). Сейчас метод `/api2/orders/order-update` относит статус к заказу.
4. Набор значений `cms_refund_methods` и соответствие каждому способу оплаты (`cms_payment_type_refund_method`), включая оплату «Долями», «Подели», «Сплит» (возврат через провайдера).
5. Набор статусов строки возврата и правило, по которому из них складывается статус заявки.
6. Соответствие типов доставки 6, 10, 12, 14, 7, 13 способам возврата (`cms_return_method_delivery_type`).
7. Как показывать клиенту чек возврата («Скачать чек»): ссылка ОФД или печатная форма по данным `cms_order_receipts`. Готового механизма показа чеков клиенту в коде нет.
8. Какие магазины принимают возвраты (заполнение `cms_catalog_stock.for_returns`).
