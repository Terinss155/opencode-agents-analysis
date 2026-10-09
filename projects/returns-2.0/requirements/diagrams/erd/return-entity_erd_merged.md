# ERD-RET. Модель данных возврата (TO-BE), сведённая версия

**Основа:** `return-entity_erd.md` (DRAFT от 29.09.2026) + правки после разбора ER-схемы с доски и BRD «Шаг №1» (16.09) с комментариями.
**Дата:** 30.09.2026

> Типы, NULL, значения по умолчанию, индексы и внешние ключи существующих таблиц сняты с БД (`SHOW FULL COLUMNS`, `SHOW INDEX`, `information_schema.KEY_COLUMN_USAGE`); схема локальной БД повторяет прод. У существующих таблиц показаны только поля, участвующие в логике возврата.
> Mermaid не поддерживает запятую в типе, поэтому размер `decimal(10,2)` и значения `enum` указаны в комментарии к полю.

**Обозначения**

| Обозначение | Значение |
|---|---|
| **PK** | Первичный ключ |
| **FK** | Внешний ключ с ограничением в БД (`FOREIGN KEY`). Для новых таблиц - ограничение, которое нужно создать в миграции |
| **FK (лог.)** | Логическая связь: код соединяет таблицы по этому полю, но ограничения в БД нет. Целостность держит только код |
| **UK** | Уникальный индекс |
| **IDX** | Обычный (неуникальный) индекс |
| NULL **Нет** / **Да** | `NOT NULL` / `NULL` в БД |
| На диаграмме `--` / `..` | Связь с ограничением FK / логическая связь |

## 1. Что изменилось относительно версии от 29.09

### 1.1. Модель

| # | Было в ERD от 29.09 | Стало | Почему |
|---|---|---|---|
| 1 | `cms_return_tk`, `cms_returns.return_tk_id` | Таблицы нет. В заявке `return_method_id` → `cms_return_method.id` и `delivery_tk_id` → `cms_delivery_tk.id` | Таблица зачёркнута на схеме с доски; службы уже есть в `cms_delivery_tk` |
| 2 | `cms_return_tk.rcrm_tk_id` | `cms_return_method.rcrm_tk_id` (новое поле) | Коды RetailCRM сейчас зашиты по способу возврата в `ReturnMethodEnum` (13 курьер, 567 СДЭК, 55 5Post) |
| 3 | `cms_return_tk_city` | Таблицы нет. Покрытие по существующей `cms_delivery_city` + новый признак `for_returns` | Так уже работает `DeliveryCityRepository::findReturnVariantTypesByGeoIds` |
| 4 | `cms_return_status_history` | Таблицы нет. Переходы статусов - строки `cms_return_changes` | Таблица зачёркнута на схеме с доски; одна лента изменений вместо двух |
| 5 | `cms_return_changes`: строка = одно поле | Строка = одно событие: `diff` + полный `snapshot` заявки | Решение: хранить в изменениях заявки всё и собирать PDF на лету |
| 6 | Заявление формируется из текущих данных заявки | Заявление формируется из `snapshot` своей версии своим шаблоном (`template_version`) | Версии и «аннулировано» при отмене (BRD 5.3); данные заказа, причины и шаблон со временем меняются |
| 7 | - | `cms_returns.source`, `cms_returns.replaced_return_id` | Заявки «Дружбы» и магазина (BRD 5.2, 5.5); смена канала = отмена + новая заявка |
| 8 | `qr_code` - QR 5Post | `qr_code` - наш QR для магазина | Комментарий к BRD 24.09: QR партнёров в ЛК не показываем |
| 9 | Поля перевозчиков и `receipt_id` в MVP | Остаются, помечены PostMVP | BRD 3.2: интеграции с ТК и чек возврата вне объёма |
| 10 | `user_refund` открытым текстом | Шифрованно; в версии - отдельное шифрованное поле | Реквизиты не должны лежать открыто в JSON |
| 11 | Магазин через `cms_return_tk` | `cms_return_method.alias = store`, типы доставки 7, 13, 16 → `store`, `cms_returns.store_code` + `cms_catalog_stock.for_returns` | Возврат в магазин - свойство магазина, а не покрытие перевозчика |
| 12 | Кто формирует номер заявки - открытый вопрос | `return_num` = `order_num-NN` генерирует сайт; `return_order_num` - отдельное поле под номер документа «Возврат» в 1С, если он отличается | Решение команды: номер нужен сразу (экран «Возврат создан», QR, PDF), а ответ 1С через Outbox асинхронный |

### 1.2. Исправлено по фактической схеме БД

| # | В ERD от 29.09 | В БД | Что это значит для модели |
|---|---|---|---|
| 1 | `cms_catalog_stock.store_code` - `int` | `smallint(6) unsigned` | `cms_returns.store_code` делаем `smallint(6) unsigned`, иначе FK не создать |
| 2 | `cms_delivery_types.internal_id` - UK | Обычный индекс, уникальности нет | `cms_return_method_delivery_type.delivery_type` - только логическая связь |
| 3 | `cms_order_position_statuses.code` - UK | Не уникален, индекса нет | Сопоставление с 1С и RetailCRM по `code` на уровне БД не защищено |
| 4 | `cms_return_reasons.code` - UK | Не уникален, индекса нет | Причину в позиции храним по `id`, не по `code` |
| 5 | `cms_orders.payment_method` - `int` | `tinyint(1)` | `cms_payment_types.internal_id` - `int(11)`; связь логическая, значения пока помещаются |
| 6 | `cms_orders.status`, `delivery_method` - `int` | `int(2)`, `int(3)` | Только ширина отображения, на диапазон не влияет |
| 7 | `cms_order_receipts.receipt` - `text`, `ofd_response` - `varchar`, `operation` - `varchar` | `longtext`, `longtext`, `enum` | Исправлены типы |
| 8 | `cms_catalog_stock.route` - `text` | `varchar(500)` | Исправлен тип |
| 9 | `cms_delivery_city.geo_id` - не описано | `varchar(255)`, индекса нет | Поиск способов возврата идёт по `geo_id` без индекса - добавить индекс |
| 10 | Связи существующих таблиц - как FK | Ограничения FK есть только у `cms_users_refund.user_id`, `cms_delivery_tk.store_code`, `cms_return_reasons.group_id`, `cms_return_reasons_content.parent_id`, `cms_giftcard_use.order_id` | Остальные связи существующих таблиц - логические |
| 11 | `cms_orders.user_id` - обязательно | `NOT NULL DEFAULT 0`, ограничения FK нет | `0` - заказ без пользователя; заявку для такого заказа клиент не оформит |
| 12 | `cms_order_positions.order_id` - обязательно | `NULL`, ограничения FK нет | Проверять наличие заказа в коде |

## 2. Состав таблиц

| Статус | Таблица | Зачем нужна |
|---|---|---|
| Существует, не меняется | `cms_users_user` | Клиент: владелец заказа и заявки; признак F&F для срока возврата |
| Существует, не меняется | `cms_users_refund` | Сохранённые банковские реквизиты клиента - источник для заявки |
| Существует, не меняется | `cms_orders` | Исходный заказ: номер, адрес, способ доставки и оплаты; AS-IS поля возврата на заказе |
| Существует, не меняется | `cms_order_positions` | Товары заказа со слепком данных; из них выбираются штуки к возврату |
| Существует, не меняется | `cms_status_groups` | Группы статусов заказа |
| Существует, не меняется | `cms_order_statuses` | Статусы заказа: можно ли по заказу оформить возврат |
| Существует, не меняется | `cms_order_position_statuses` | Статусы позиции заказа: какие штуки уже отменены или возвращены |
| Существует, не меняется | `cms_delivery_types` | Типы доставки; по типу доставки заказа подставляется способ возврата |
| Существует, не меняется | `cms_delivery_tk` | Службы доставки; служба возврата для курьера, ПВЗ, Почты |
| Существует, добавляется поле | `cms_delivery_city` | Покрытие служб по городам; из него - какие способы возврата доступны в городе |
| Существует, добавляется поле | `cms_catalog_stock` | Магазины; список магазинов, принимающих возвраты |
| Существует, не меняется | `cms_payment_types` | Способы оплаты; по ним определяется способ возврата денег |
| Существует, не меняется | `cms_order_receipts` | Фискальные чеки заказа; чек возврата (PostMVP) |
| Существует, не меняется | `cms_giftcard_use` | Списания сертификатов по заказу; доля сертификата в возврате денег |
| Существует, не меняется | `cms_order_return_statuses_wms` | Справочник статусов возврата на складе |
| Существует, не меняется | `cms_return_reasons_groups` | Группы причин возврата (выпадающий список) |
| Существует, не меняется | `cms_return_reasons` | Уточнения причин внутри группы |
| Существует, не меняется | `cms_return_reasons_content` | Переводы названий причин |
| Существует, добавляются поля | `cms_return_method` | Способы возврата товара: курьер, ПВЗ, магазин, Почта |
| Новая | `cms_returns` | Заявка на возврат: шапка |
| Новая | `cms_return_positions` | Возвращаемые штуки с причиной, статусом и суммами |
| Новая | `cms_return_changes` | Лента событий заявки: изменения, статусы, версии заявления |
| Новая | `cms_return_statuses` | Справочник статусов заявки |
| Новая | `cms_return_status_groups` | Группы статусов заявки |
| Новая | `cms_return_position_statuses` | Справочник статусов штуки |
| Новая | `cms_return_position_status_history` | История статусов штуки со склада |
| Новая | `cms_return_refunds` | Возврат денег по способам: сколько, куда, когда вернули |
| Новая | `cms_refund_methods` | Справочник способов возврата денег |
| Новая | `cms_payment_type_refund_method` | Соответствие способа оплаты способу возврата денег |
| Новая | `cms_return_method_delivery_type` | Соответствие типа доставки заказа способу возврата |
| Убрана | `cms_return_tk`, `cms_return_tk_city`, `cms_return_status_history` | См. 1.1 |

## 3. Диаграмма

```mermaid
erDiagram
    %% ================= СУЩЕСТВУЮЩИЕ: пользователь =================

    %% Зачем: клиент - владелец заказа и заявки; is_vic даёт увеличенный срок возврата F&F
    cms_users_user {
        int(11) id PK "ID пользователя"
        tinyint(1) is_vic "NOT NULL 0: VIC / Friends & Family из RetailCRM"
    }

    %% Зачем: сохранённые реквизиты клиента, из них заполняется cms_returns.user_refund
    cms_users_refund {
        int(11) id PK "ID записи"
        int(11) user_id FK,UK "NULL: пользователь"
        varchar(255) bank_name "NULL: банк"
        varchar(255) bank_inn "NULL: ИНН банка"
        varchar(255) bank_bic "NULL: БИК"
        varchar(255) user_account "NULL: расчётный счёт"
        varchar(255) user_card_number "NULL: номер карты"
        varchar(255) name "NULL: имя владельца"
        varchar(255) surname "NULL: фамилия владельца"
        varchar(255) patronymic "NULL: отчество владельца"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: заказ =================

    %% Зачем: исходный заказ - номер (база номера заявки), адрес, доставка, оплата, AS-IS поля возврата
    cms_orders {
        int(11) id PK "ID заказа"
        int(11) user_id "NOT NULL 0, IDX: пользователь (лог.)"
        varchar(255) order_num "NULL, IDX: номер заказа"
        varchar(31) type "NOT NULL order: тип корзины"
        int(2) status "NOT NULL 0, IDX: статус (лог.)"
        int(3) delivery_method "NULL, IDX: служба доставки (лог.)"
        varchar(255) delivery_slug "NULL: копия cms_delivery_tk.slug"
        tinyint(1) payment_method "NULL: способ оплаты (лог.)"
        smallint(6) store_code "unsigned NULL: магазин сборки заказа C&C / экспресс (лог.)"
        varchar(255) country "NULL: страна"
        varchar(255) state "NULL: регион"
        varchar(255) city "NULL: город"
        varchar(255) city_fias "NULL: ID города в геосервисе"
        varchar(255) street "NULL"
        varchar(255) house "NULL"
        varchar(255) housing "NULL"
        varchar(255) flat "NULL"
        varchar(255) porch "NULL"
        varchar(255) floor "NULL"
        varchar(255) postal "NULL"
        varchar(255) full_address "NULL"
        varchar(32) pvz_id "NULL: пункт выдачи"
        datetime end_date "NULL: дата выполнения"
        varchar(32) lamoda_id "NULL, UK: заказ Lamoda"
        varchar(255) return_status_wms "NULL: AS-IS статус возврата WMS (лог.)"
        varchar(255) return_order_num "NULL: AS-IS номер возврата 1С, один на заказ"
        varchar(255) return_money "NULL: AS-IS способ возврата денег строкой"
        int(11) return_store "NULL: AS-IS магазин офлайн-возврата из RetailCRM"
        timestamp created_at "NOT NULL now, IDX"
    }

    %% Зачем: товары заказа со слепком на момент покупки; источник штук для возврата
    cms_order_positions {
        int(11) id PK "ID позиции"
        int(11) order_id "NULL, IDX: заказ (лог.)"
        int(2) status "NULL: статус позиции (лог.)"
        int(11) item_id "NULL, IDX: товар"
        bigint(20) barcode "NULL, IDX barcode+order_id"
        varchar(255) model_title_ru "NULL: название (слепок)"
        varchar(255) article "NULL: артикул (слепок)"
        varchar(255) color_title_ru "NULL: цвет (слепок)"
        varchar(255) size_title_ru "NULL: размер (слепок)"
        varchar(255) image_mobile_url "NULL: фото (слепок)"
        int(3) quantity "NULL: купленное количество"
        decimal price "(10,2) NOT NULL 0.00: цена со скидкой за штуку"
        decimal price_before_discount "(10,2) NULL: цена до скидки"
        decimal sum "(10,2) NOT NULL 0.00: сумма по позиции"
        decimal discount_promo "(10,2) NOT NULL 0.00: скидка промокода"
        decimal discount_bonus "(10,2) NOT NULL 0.00: оплачено баллами"
        tinyint(1) is_present "NOT NULL 0: подарок"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: статусы заказа и позиций =================

    %% Зачем: группы статусов заказа (complete, cancel ...)
    cms_status_groups {
        int(11) id PK "ID группы"
        varchar(191) code UK "NULL: код группы"
        varchar(255) title "NULL: название"
    }

    %% Зачем: статусы заказа; по ним решается, можно ли оформить возврат
    cms_order_statuses {
        int(11) id PK "ID записи"
        int(11) internal_id UK "NULL: бизнес-код статуса"
        varchar(100) code UK "NULL: символьный код"
        varchar(255) title "NULL"
        varchar(255) client_title "NULL: для клиента"
        varchar(191) group "NULL, IDX: группа (лог.)"
        tinyint(1) is_returned "NULL, IDX: возвратный статус"
    }

    %% Зачем: статусы позиции заказа; какие штуки уже отменены или возвращены
    cms_order_position_statuses {
        int(11) id PK "ID записи"
        int(11) internal_id UK "NULL: бизнес-код статуса"
        varchar(255) code "NULL, не уникален: код для 1С и RetailCRM"
        varchar(255) title "NULL"
        tinyint(1) cancel_status "NULL, IDX: отмена / возврат"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: доставка, покрытие, магазины =================

    %% Зачем: типы доставки; по типу доставки заказа подставляется способ возврата
    cms_delivery_types {
        int(11) id PK "ID записи"
        int(11) internal_id "NULL, IDX, не уникален: тип (1 курьер, 7 самовывоз, 11 5Post, 15 СДЭК ПВЗ)"
        varchar(255) internal_title "NOT NULL пусто"
        varchar(255) title_ru "NULL"
    }

    %% Зачем: службы доставки; служба возврата для курьера, ПВЗ, Почты; самовывоз - строка на магазин
    cms_delivery_tk {
        int(11) id PK "ID службы"
        varchar(255) title "NULL"
        varchar(255) slug "NULL, IDX: код службы"
        int(1) type "NULL: тип доставки (лог.)"
        tinyint(3) state "unsigned NOT NULL 0: активность"
        smallint(6) store_code FK "unsigned NULL, IDX: магазин самовывоза"
    }

    %% Зачем: покрытие служб по городам; из него - доступные способы возврата в городе
    cms_delivery_city {
        int(11) id PK "ID записи"
        int(11) tk_id "NULL, IDX: служба (лог.)"
        varchar(2) country "NULL, IDX"
        varchar(255) region "NULL, IDX"
        varchar(255) city "NULL, IDX"
        varchar(255) geo_id "NULL, без индекса: ФИАС / Google Place ID"
        tinyint(3) _state "NOT NULL 0: активность"
        tinyint(1) for_returns "НОВОЕ, NOT NULL 0: служба принимает возвраты"
    }

    %% Зачем: магазины; список магазинов, принимающих возвраты, и слепок адреса в заявке
    cms_catalog_stock {
        int(11) id PK "ID магазина / склада"
        smallint(6) store_code UK "unsigned NOT NULL: код магазина"
        varchar(255) title_ru "NULL"
        varchar(255) address "NULL"
        varchar(255) working_time "NULL"
        varchar(36) geo_id "NULL: город в геосервисе"
        varchar(50) latitude "NULL"
        varchar(50) longitude "NULL"
        varchar(500) route "NULL: как добраться"
        enum stock_type "main, shop, additional; NOT NULL shop"
        tinyint(3) _state "NOT NULL 0: активность"
        tinyint(1) for_cnc "NOT NULL 0"
        tinyint(1) for_reservation "NOT NULL 0"
        tinyint(1) for_returns "НОВОЕ, NOT NULL 0: принимает возвраты"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: оплата, сертификаты, чеки =================

    %% Зачем: способы оплаты; по ним определяется способ возврата денег
    cms_payment_types {
        int(11) id PK "ID записи"
        int(11) internal_id UK "NULL: код способа оплаты"
        varchar(255) code "NULL"
        varchar(255) crm_title "NULL"
        tinyint(1) is_bnpl "NULL 0: BNPL (Долями, Подели)"
    }

    %% Зачем: списания сертификатов по заказу; доля к возврату на сертификат
    cms_giftcard_use {
        int(11) id PK "ID записи"
        int(11) order_id FK "NULL, IDX: заказ"
        varchar(40) guid "NULL, IDX: GUID сертификата"
        varchar(20) cert_number "NULL: маскированный номер"
        decimal amount "(10,2) NOT NULL: сумма списания"
        tinyint(1) is_purchased "NOT NULL 0: списано"
    }

    %% Зачем: фискальные чеки заказа; чек возврата (PostMVP)
    cms_order_receipts {
        int(11) id PK "ID чека"
        int(11) order_id "NULL, IDX: заказ (лог.)"
        enum operation "sell, sell_refund, ...; NULL"
        enum payment_system "yookassa, dolyame, podeli; NULL"
        decimal sum "(10,2) NULL"
        varchar(130) receipt_id UK "NULL: ID чека"
        longtext receipt "NULL: данные чека"
        longtext ofd_response "NULL: ответ ОФД"
        timestamp created_at "NOT NULL now"
    }

    %% ================= СУЩЕСТВУЮЩИЕ: справочники возврата =================

    %% Зачем: статусы возврата на складе (1С / WMS)
    cms_order_return_statuses_wms {
        int(11) id PK "ID записи"
        varchar(255) code UK "NOT NULL: код статуса"
        varchar(255) title "NOT NULL"
    }

    %% Зачем: группы причин возврата - выпадающий список при оформлении
    cms_return_reasons_groups {
        int(11) id PK "ID группы"
        varchar(255) title "NOT NULL"
        int(11) order "NULL: сортировка"
        tinyint(3) active "NULL 1"
        timestamp created_at "NOT NULL now"
        timestamp updated_at "NOT NULL now"
    }

    %% Зачем: уточнения причины внутри группы
    cms_return_reasons {
        int(11) id PK "ID причины"
        int(11) group_id FK "NULL, IDX: группа"
        varchar(255) code "NULL, не уникален"
        varchar(255) title "NULL"
        text description "NULL: подсказка"
        tinyint(1) active "NULL, IDX"
        int(11) _order "NULL, IDX"
    }

    %% Зачем: переводы названий причин
    cms_return_reasons_content {
        int(11) id PK "ID записи"
        int(11) parent_id FK "NULL, IDX: причина"
        int(11) lang_id "NULL: язык"
        varchar(255) title "NULL: перевод"
    }

    %% Зачем: способы возврата товара - курьер, ПВЗ, магазин, Почта
    cms_return_method {
        int(11) id PK "ID способа"
        varchar(255) alias UK "NOT NULL: courier, sdek-pvz, 5post, store, russian-post"
        varchar(255) title "NOT NULL"
        text description "NULL: подсказка при оформлении"
        tinyint(1) is_enabled "NOT NULL 1: сайт"
        tinyint(1) is_enabled_mobile "NOT NULL 1: МП"
        text instruction "НОВОЕ, NULL: «Что дальше»"
        int(11) _order "НОВОЕ, NOT NULL 0: приоритет"
        varchar(32) rcrm_tk_id "НОВОЕ, NULL: служба в RetailCRM"
    }

    %% Зачем: тип доставки заказа -> способ возврата «как в заказе»
    cms_return_method_delivery_type {
        int(11) id PK "ID записи"
        int(11) delivery_type UK "NOT NULL: тип доставки (лог.)"
        int(11) return_method_id FK "NOT NULL: способ возврата"
    }

    %% ================= НОВЫЕ: заявка =================

    %% Зачем: шапка заявки на возврат - одна строка на заявку
    cms_returns {
        int(11) id PK "ID заявки"
        char(36) return_guid UK "NOT NULL: UUID для обмена"
        varchar(32) return_num UK "NOT NULL: order_num-NN, генерирует сайт"
        int(11) return_seq "NOT NULL, UK с order_id"
        int(11) user_id FK "NOT NULL"
        int(11) order_id FK "NOT NULL"
        int(11) status_id FK "NOT NULL"
        varchar(16) source "NOT NULL: site, mobile, rcrm, onec"
        int(11) replaced_return_id FK "NULL: заменённая заявка"
        int(11) return_method_id FK "NOT NULL"
        int(11) delivery_tk_id FK "NULL: курьер, ПВЗ, Почта"
        varchar(255) return_order_num "NULL: номер документа «Возврат» в 1С, если отличается от return_num"
        varchar(255) return_status_wms FK "NULL"
        varchar(2) country "NOT NULL"
        varchar(255) region "NULL"
        varchar(255) city "NOT NULL"
        varchar(255) city_fias "NOT NULL"
        varchar(255) return_street "NULL: курьер"
        varchar(255) return_house "NULL: курьер"
        varchar(255) return_flat "NULL: курьер"
        varchar(20) return_postal "NULL: курьер"
        varchar(512) return_address "NULL: курьер"
        varchar(32) pvz_id "NULL: ПВЗ"
        smallint(6) store_code FK "unsigned NULL: магазин"
        varchar(255) pvz_title "NULL: слепок"
        varchar(512) pvz_address "NULL: слепок"
        varchar(255) pvz_work_time "NULL: слепок"
        date return_date "NULL: курьер"
        varchar(32) return_time "NULL: курьер"
        time return_time_from "NULL: курьер"
        time return_time_to "NULL: курьер"
        datetime handover_deadline "NULL"
        datetime handed_over_at "NULL"
        varchar(255) qr_code "NULL: наш QR для магазина"
        varchar(255) external_return_id "NULL: PostMVP"
        varchar(255) track_number "NULL: PostMVP"
        varchar(255) waybill_number "NULL: PostMVP"
        varchar(32) pin_code "NULL: PostMVP"
        text user_refund "NULL: реквизиты, шифрованно"
        int(11) receipt_id FK "NULL: PostMVP"
        varchar(255) cancel_reason "NULL"
        timestamp created_at "NOT NULL now"
        timestamp updated_at "NOT NULL now, on update"
    }

    %% Зачем: возвращаемые штуки - одна строка на штуку со своей причиной, статусом и суммой
    cms_return_positions {
        int(11) id PK "ID строки"
        int(11) return_id FK "NOT NULL"
        int(11) order_position_id FK "NOT NULL"
        bigint(20) barcode "NOT NULL: копия"
        int(11) reason_group_id FK "NOT NULL"
        int(11) reason_id FK "NULL"
        int(11) status_id FK "NOT NULL"
        int(3) quantity "NOT NULL 1"
        decimal refund_amount "(10,2) NOT NULL"
        decimal refunded_amount "(10,2) NULL"
        decimal refund_bonus_amount "(10,2) NOT NULL 0.00"
        decimal refunded_bonus_amount "(10,2) NULL"
    }

    %% Зачем: лента событий заявки - изменения, смена статусов, версии заявления для PDF
    cms_return_changes {
        int(11) id PK "ID записи"
        int(11) return_id FK "NOT NULL"
        varchar(16) event "NOT NULL: created, changed, status, cancelled"
        varchar(32) source "NOT NULL: SITE, MOBILE, 1C, RCRM, WMS"
        varchar(255) author "NULL"
        int(11) status_id FK "NOT NULL: статус после события"
        longtext diff "JSON, NULL"
        int(11) application_version "NULL, UK с return_id"
        smallint(6) template_version "NULL"
        longtext snapshot "JSON, NULL"
        text bank_data_encrypted "NULL"
        datetime external_event_at "NULL"
        datetime changed_at "NOT NULL"
    }

    %% ================= НОВЫЕ: статусы =================

    %% Зачем: группы статусов заявки для фильтров и вкладок
    cms_return_status_groups {
        int(11) id PK "ID группы"
        varchar(64) code UK "NOT NULL"
        varchar(255) title "NOT NULL"
        tinyint(1) active "NOT NULL 1"
        int(11) _order "NOT NULL 0"
    }

    %% Зачем: справочник статусов заявки (Создан, Завершён, Отменён)
    cms_return_statuses {
        int(11) id PK "ID записи"
        int(11) internal_id UK "NOT NULL: бизнес-код"
        varchar(64) code UK "NOT NULL"
        varchar(255) title "NOT NULL"
        varchar(255) client_title "NOT NULL"
        varchar(64) group FK "NOT NULL"
        tinyint(1) active "NOT NULL 1"
        int(11) _order "NOT NULL 0"
        tinyint(1) can_be_cancelled "NOT NULL 0"
    }

    %% Зачем: справочник статусов штуки (ожидается, получена, принята, отклонена)
    cms_return_position_statuses {
        int(11) id PK "ID записи"
        int(11) internal_id UK "NOT NULL"
        varchar(64) code UK "NOT NULL"
        varchar(255) title "NOT NULL"
        varchar(255) client_title "NOT NULL"
        tinyint(1) active "NOT NULL 1"
        int(11) _order "NOT NULL 0"
    }

    %% Зачем: история статусов штуки - по событиям склада
    cms_return_position_status_history {
        int(11) id PK "ID записи"
        int(11) return_position_id FK "NOT NULL"
        int(11) status_id FK "NOT NULL"
        datetime status_at "NOT NULL"
        varchar(32) source "NOT NULL"
        datetime external_event_at "NULL"
        timestamp created_at "NOT NULL now"
    }

    %% ================= НОВЫЕ: возврат денег =================

    %% Зачем: справочник, куда возвращаются деньги; заменяет строку cms_orders.return_money
    cms_refund_methods {
        int(11) id PK "ID способа"
        varchar(64) code UK "NOT NULL: card_payment, bank_details, certificate, bonus, cash"
        varchar(255) title "NOT NULL"
        tinyint(1) requires_bank_data "NOT NULL 0"
        int(11) _order "NOT NULL 0"
        tinyint(1) active "NOT NULL 1"
    }

    %% Зачем: способ оплаты заказа -> способ возврата денег; одно правило для сайта и МП
    cms_payment_type_refund_method {
        int(11) id PK "ID записи"
        int(11) payment_type FK,UK "NOT NULL"
        int(11) refund_method_id FK "NOT NULL"
    }

    %% Зачем: возврат денег по заявке в разрезе способов - расчёт и факт
    cms_return_refunds {
        int(11) id PK "ID строки"
        int(11) return_id FK "NOT NULL, UK с refund_method_id"
        int(11) refund_method_id FK "NOT NULL"
        decimal refund_amount "(10,2) NOT NULL"
        decimal refunded_amount "(10,2) NULL"
        datetime refunded_at "NULL: деньги возвращены"
    }

    %% ================= СВЯЗИ: -- с ограничением FK, .. логическая =================
    %% Пользователь
    cms_users_user ||--o| cms_users_refund : "id = user_id"
    cms_users_user ||..o{ cms_orders : "id = user_id"
    cms_users_user ||--o{ cms_returns : "id = user_id"

    %% Заказ
    cms_orders ||..o{ cms_order_positions : "id = order_id"
    cms_orders ||..o{ cms_order_receipts : "id = order_id"
    cms_orders ||--o{ cms_giftcard_use : "id = order_id"
    cms_orders ||--o{ cms_returns : "id = order_id"
    cms_status_groups ||..o{ cms_order_statuses : "code = group"
    cms_order_statuses ||..o{ cms_orders : "internal_id = status"
    cms_order_position_statuses ||..o{ cms_order_positions : "internal_id = status"
    cms_payment_types ||..o{ cms_orders : "internal_id = payment_method"
    cms_delivery_tk ||..o{ cms_orders : "id = delivery_method"
    cms_catalog_stock |o..o{ cms_orders : "store_code = store_code"

    %% Доставка и покрытие
    cms_delivery_types ||..o{ cms_delivery_tk : "internal_id = type"
    cms_delivery_tk ||..o{ cms_delivery_city : "id = tk_id"
    cms_catalog_stock |o--o{ cms_delivery_tk : "store_code = store_code"

    %% Способы возврата
    cms_delivery_types ||..o| cms_return_method_delivery_type : "internal_id = delivery_type"
    cms_return_method ||--o{ cms_return_method_delivery_type : "id = return_method_id"

    %% Заявка
    cms_return_method ||--o{ cms_returns : "id = return_method_id"
    cms_delivery_tk |o--o{ cms_returns : "id = delivery_tk_id"
    cms_catalog_stock |o--o{ cms_returns : "store_code = store_code"
    cms_returns |o--o| cms_returns : "id = replaced_return_id"
    cms_return_statuses ||--o{ cms_returns : "internal_id = status_id"
    cms_return_status_groups ||--o{ cms_return_statuses : "code = group"
    cms_order_return_statuses_wms |o--o{ cms_returns : "code = return_status_wms"
    cms_order_receipts |o--o| cms_returns : "id = receipt_id"

    %% Изменения заявки
    cms_returns ||--|{ cms_return_changes : "id = return_id"
    cms_return_statuses ||--o{ cms_return_changes : "internal_id = status_id"

    %% Позиции
    cms_returns ||--|{ cms_return_positions : "id = return_id"
    cms_order_positions ||--o{ cms_return_positions : "id = order_position_id"
    cms_return_reasons_groups ||--o{ cms_return_positions : "id = reason_group_id"
    cms_return_reasons |o--o{ cms_return_positions : "id = reason_id"
    cms_return_position_statuses ||--o{ cms_return_positions : "internal_id = status_id"
    cms_return_positions ||--|{ cms_return_position_status_history : "id = return_position_id"
    cms_return_position_statuses ||--o{ cms_return_position_status_history : "internal_id = status_id"

    %% Причины
    cms_return_reasons_groups ||--o{ cms_return_reasons : "id = group_id"
    cms_return_reasons ||--o{ cms_return_reasons_content : "id = parent_id"

    %% Деньги
    cms_returns ||--|{ cms_return_refunds : "id = return_id"
    cms_refund_methods ||--o{ cms_return_refunds : "id = refund_method_id"
    cms_refund_methods ||--o{ cms_payment_type_refund_method : "id = refund_method_id"
    cms_payment_types ||--o| cms_payment_type_refund_method : "internal_id = payment_type"
```

## 4. Описание существующих таблиц

Только поля, участвующие в логике возврата. Все типы, NULL и значения по умолчанию - из БД.

### 4.1. `cms_users_user` - пользователь

**Зачем нужна:** клиент - владелец заказа и заявки. Признак `is_vic` определяет увеличенный срок возврата для F&F.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор пользователя |
| 2 | `is_vic` | `tinyint(1)` | | Нет | `0` | Признак VIC / Friends & Family. Приходит из RetailCRM, назначается один раз и навсегда |

### 4.2. `cms_users_refund` - реквизиты пользователя

**Зачем нужна:** сохранённые банковские реквизиты клиента. При оформлении заявки с `requires_bank_data = 1` из них заполняется `cms_returns.user_refund`; клиент может перезаписать их в любой момент, поэтому заявка хранит свою копию.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `user_id` | `int(11)` | FK, UK | Да | `NULL` | Пользователь, одна запись на пользователя.<br>Связь: `cms_users_refund.user_id = cms_users_user.id` |
| 3 | `bank_name` | `varchar(255)` | | Да | `NULL` | Название банка |
| 4 | `bank_inn` | `varchar(255)` | | Да | `NULL` | ИНН банка |
| 5 | `bank_bic` | `varchar(255)` | | Да | `NULL` | БИК банка |
| 6 | `user_account` | `varchar(255)` | | Да | `NULL` | Расчётный счёт |
| 7 | `user_card_number` | `varchar(255)` | | Да | `NULL` | Номер карты |
| 8 | `name` | `varchar(255)` | | Да | `NULL` | Имя владельца счёта |
| 9 | `surname` | `varchar(255)` | | Да | `NULL` | Фамилия владельца счёта |
| 10 | `patronymic` | `varchar(255)` | | Да | `NULL` | Отчество владельца счёта. По BRD для возврата обязательно - проверять в коде, в БД допускается `NULL` |

### 4.3. `cms_orders` - заказ

**Зачем нужна:** исходный заказ заявки. Даёт номер (база номера заявки), город и адрес для подстановки, службу доставки (для автовыбора способа возврата), способ оплаты (для способа возврата денег). Поля `return_*` - AS-IS: возврат, привязанный к заказу, как он приходит сейчас из 1С и RetailCRM.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор заказа |
| 2 | `user_id` | `int(11)` | FK (лог.), IDX | Нет | `0` | Пользователь. `0` - заказ без пользователя.<br>Связь: `cms_orders.user_id = cms_users_user.id` |
| 3 | `order_num` | `varchar(255)` | IDX | Да | `NULL` | Номер заказа. База номера заявки `order_num-NN` |
| 4 | `type` | `varchar(31)` | | Нет | `order` | Тип корзины (`order`, `reservation`, `express_delivery` ...) |
| 5 | `status` | `int(2)` | FK (лог.), IDX | Нет | `0` | Статус заказа.<br>Связь: `cms_orders.status = cms_order_statuses.internal_id` |
| 6 | `delivery_method` | `int(3)` | FK (лог.), IDX | Да | `NULL` | Служба доставки заказа.<br>Связь: `cms_orders.delivery_method = cms_delivery_tk.id` |
| 7 | `delivery_slug` | `varchar(255)` | | Да | `NULL` | Копия `cms_delivery_tk.slug` на момент заказа |
| 8 | `payment_method` | `tinyint(1)` | FK (лог.) | Да | `NULL` | Способ оплаты.<br>Связь: `cms_orders.payment_method = cms_payment_types.internal_id` |
| 9 | `store_code` | `smallint(6) unsigned` | FK (лог.) | Да | `NULL` | Магазин, из которого собирается заказ: магазин с наибольшим остатком для Click&Collect, магазин экспресс-самовывоза. У заказов со склада сайта пусто или `100` (`Stock::SITE_STORE_CODE`, может проставить 1С). **Не магазин самовывоза:** магазин самовывоза определяется по службе доставки — `cms_orders.delivery_method` → `cms_delivery_tk.store_code` → `cms_catalog_stock.store_code`.<br>Связь: `cms_orders.store_code = cms_catalog_stock.store_code` |
| 10 | `country` | `varchar(255)` | | Да | `NULL` | Страна доставки |
| 11 | `state` | `varchar(255)` | | Да | `NULL` | Регион доставки |
| 12 | `city` | `varchar(255)` | | Да | `NULL` | Город доставки |
| 13 | `city_fias` | `varchar(255)` | | Да | `NULL` | ID города в геосервисе (ФИАС для РФ). Совпадает по значению с `cms_delivery_city.geo_id` и `cms_catalog_stock.geo_id` |
| 14 | `street` | `varchar(255)` | | Да | `NULL` | Улица |
| 15 | `house` | `varchar(255)` | | Да | `NULL` | Дом |
| 16 | `housing` | `varchar(255)` | | Да | `NULL` | Корпус |
| 17 | `flat` | `varchar(255)` | | Да | `NULL` | Квартира |
| 18 | `porch` | `varchar(255)` | | Да | `NULL` | Подъезд |
| 19 | `floor` | `varchar(255)` | | Да | `NULL` | Этаж |
| 20 | `postal` | `varchar(255)` | | Да | `NULL` | Индекс |
| 21 | `full_address` | `varchar(255)` | | Да | `NULL` | Полный адрес одной строкой |
| 22 | `pvz_id` | `varchar(32)` | | Да | `NULL` | Пункт выдачи заказа. Для автовыбора ПВЗ возврата |
| 23 | `end_date` | `datetime` | | Да | `NULL` | Дата выполнения заказа. От неё считается срок возврата |
| 24 | `lamoda_id` | `varchar(32)` | UK | Да | `NULL` | ID заказа Lamoda. Заказы Lamoda возвращаются не через нас |
| 25 | `return_status_wms` | `varchar(255)` | FK (лог.) | Да | `NULL` | AS-IS: статус возврата на складе по заказу.<br>Связь: `cms_orders.return_status_wms = cms_order_return_statuses_wms.code` |
| 26 | `return_order_num` | `varchar(255)` | | Да | `NULL` | AS-IS: номер возврата, который присылает 1С в `POST /api2/orders/order-update`. Сохраняется только вместе с непустым `return_status_wms`, одно значение на заказ (следующий возврат перезаписывает), в коде нигде не читается |
| 27 | `return_money` | `varchar(255)` | | Да | `NULL` | AS-IS: способ возврата денег свободной строкой. В новой модели заменяется `cms_refund_methods` |
| 28 | `return_store` | `int(11)` | | Да | `NULL` | AS-IS: магазин офлайн-возврата из кастомного поля RetailCRM. Что именно передаётся (`store_code` или ID RetailCRM) - уточнить |
| 29 | `created_at` | `timestamp` | IDX | Нет | `current_timestamp()` | Дата создания заказа |

### 4.4. `cms_order_positions` - позиция заказа

**Зачем нужна:** товары заказа со слепком данных на момент покупки. Из них клиент выбирает штуки к возврату; название, артикул, цвет, размер, фото и цены в позицию возврата не копируются.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор позиции |
| 2 | `order_id` | `int(11)` | FK (лог.), IDX | Да | `NULL` | Заказ.<br>Связь: `cms_order_positions.order_id = cms_orders.id` |
| 3 | `status` | `int(2)` | FK (лог.) | Да | `NULL` | Статус позиции.<br>Связь: `cms_order_positions.status = cms_order_position_statuses.internal_id` |
| 4 | `item_id` | `int(11)` | IDX | Да | `NULL` | Товар каталога |
| 5 | `barcode` | `bigint(20)` | IDX (`barcode`, `order_id`) | Да | `NULL` | Штрихкод. По нему 1С и RetailCRM сопоставляют позиции |
| 6 | `model_title_ru` | `varchar(255)` | | Да | `NULL` | Название товара (слепок) |
| 7 | `article` | `varchar(255)` | | Да | `NULL` | Артикул (слепок) |
| 8 | `color_title_ru` | `varchar(255)` | | Да | `NULL` | Цвет (слепок) |
| 9 | `size_title_ru` | `varchar(255)` | | Да | `NULL` | Размер (слепок) |
| 10 | `image_mobile_url` | `varchar(255)` | | Да | `NULL` | Фото (слепок) |
| 11 | `quantity` | `int(3)` | | Да | `NULL` | Купленное количество. Верхняя граница штук к возврату |
| 12 | `price` | `decimal(10,2)` | | Нет | `0.00` | Цена со скидкой за штуку |
| 13 | `price_before_discount` | `decimal(10,2)` | | Да | `NULL` | Цена до скидки |
| 14 | `sum` | `decimal(10,2)` | | Нет | `0.00` | Сумма по позиции |
| 15 | `discount_promo` | `decimal(10,2)` | | Нет | `0.00` | Скидка по промокоду |
| 16 | `discount_bonus` | `decimal(10,2)` | | Нет | `0.00` | Оплачено баллами. Для расчёта баллов к возврату |
| 17 | `is_present` | `tinyint(1)` | | Нет | `0` | Подарок. Подарок к возврату не предлагается |

### 4.5. `cms_status_groups` - группы статусов заказа

**Зачем нужна:** группирует статусы заказа (`complete`, `cancel` ...). Используется, чтобы понять, выполнен ли заказ и можно ли по нему оформить возврат.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор группы |
| 2 | `code` | `varchar(191)` | UK | Да | `NULL` | Код группы. На него ссылается `cms_order_statuses.group` |
| 3 | `title` | `varchar(255)` | | Да | `NULL` | Название |

### 4.6. `cms_order_statuses` - статусы заказа

**Зачем нужна:** справочник статусов заказа. По статусу и группе решается, доступен ли возврат по заказу.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `internal_id` | `int(11)` | UK | Да | `NULL` | Бизнес-код статуса. На него ссылается `cms_orders.status` |
| 3 | `code` | `varchar(100)` | UK | Да | `NULL` | Символьный код |
| 4 | `title` | `varchar(255)` | | Да | `NULL` | Название |
| 5 | `client_title` | `varchar(255)` | | Да | `NULL` | Название для клиента |
| 6 | `group` | `varchar(191)` | FK (лог.), IDX | Да | `NULL` | Группа статуса.<br>Связь: `cms_order_statuses.group = cms_status_groups.code` |
| 7 | `is_returned` | `tinyint(1)` | IDX | Да | `NULL` | Возвратный статус заказа (AS-IS) |

### 4.7. `cms_order_position_statuses` - статусы позиции заказа

**Зачем нужна:** справочник статусов позиции. По признаку `cancel_status` видно, какие штуки уже отменены или возвращены и не могут попасть в новую заявку.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `internal_id` | `int(11)` | UK | Да | `NULL` | Бизнес-код статуса. На него ссылается `cms_order_positions.status` |
| 3 | `code` | `varchar(255)` | | Да | `NULL` | Символьный код для сопоставления с 1С и RetailCRM. **Не уникален и без индекса** |
| 4 | `title` | `varchar(255)` | | Да | `NULL` | Название |
| 5 | `cancel_status` | `tinyint(1)` | IDX | Да | `NULL` | Признак отмены / возврата позиции |

### 4.8. `cms_delivery_types` - типы доставки

**Зачем нужна:** типы доставки. По типу службы доставки заказа через `cms_return_method_delivery_type` подставляется способ возврата «как в заказе».

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `internal_id` | `int(11)` | IDX | Да | `NULL` | Код типа: `1` курьер, `7` самовывоз, `11` 5Post, `13` экспресс-самовывоз, `15` СДЭК ПВЗ, `16` бронирование. На него ссылаются `cms_delivery_tk.type` и `cms_return_method_delivery_type.delivery_type`. **Уникальности в БД нет** |
| 3 | `internal_title` | `varchar(255)` | | Нет | `''` | Внутреннее название |
| 4 | `title_ru` | `varchar(255)` | | Да | `NULL` | Название |

### 4.9. `cms_delivery_tk` - службы доставки

**Зачем нужна:** службы доставки (тарифы). Для курьера, ПВЗ и Почты - служба возврата в заявке. У самовывоза своя строка на магазин.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор службы |
| 2 | `title` | `varchar(255)` | | Да | `NULL` | Название |
| 3 | `slug` | `varchar(255)` | IDX | Да | `NULL` | Код службы (`sdek-pvz`, `5post`, `dalli-msk-nofit`). Провайдер для запроса пунктов в сервисе логистики |
| 4 | `type` | `int(1)` | FK (лог.) | Да | `NULL` | Тип доставки.<br>Связь: `cms_delivery_tk.type = cms_delivery_types.internal_id` |
| 5 | `state` | `tinyint(3) unsigned` | | Нет | `0` | Активность службы |
| 6 | `store_code` | `smallint(6) unsigned` | FK, IDX | Да | `NULL` | Магазин для самовывоза.<br>Связь: `cms_delivery_tk.store_code = cms_catalog_stock.store_code` |

### 4.10. `cms_delivery_city` - покрытие служб доставки

**Зачем нужна:** в каких городах работает служба. По `geo_id` города возврата определяется набор доступных способов возврата (`findReturnVariantTypesByGeoIds`).

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `tk_id` | `int(11)` | FK (лог.), IDX | Да | `NULL` | Служба доставки.<br>Связь: `cms_delivery_city.tk_id = cms_delivery_tk.id` |
| 3 | `country` | `varchar(2)` | IDX | Да | `NULL` | ISO страны |
| 4 | `region` | `varchar(255)` | IDX | Да | `NULL` | Регион |
| 5 | `city` | `varchar(255)` | IDX | Да | `NULL` | Город |
| 6 | `geo_id` | `varchar(255)` | | Да | `NULL` | ФИАС GUID для РФ, Google Place ID для других стран. Сравнивается с `cms_orders.city_fias` / `cms_returns.city_fias`. **Индекса нет** - добавить |
| 7 | `_state` | `tinyint(3)` | | Нет | `0` | Активность записи |
| 8 | `for_returns` | `tinyint(1)` | | Нет | `0` | **Новое поле.** Служба принимает возвраты в этом городе. По умолчанию `0`: возвраты включаются явно |

### 4.11. `cms_catalog_stock` - магазины и склады

**Зачем нужна:** магазины. Даёт список магазинов, принимающих возвраты в городе, и данные для слепка адреса в заявке.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор магазина / склада |
| 2 | `store_code` | `smallint(6) unsigned` | UK | Нет | - | Код магазина. По нему связываются `cms_delivery_tk`, `cms_orders`, `cms_returns`; так магазин знают 1С и RetailCRM |
| 3 | `title_ru` | `varchar(255)` | | Да | `NULL` | Название. Источник `cms_returns.pvz_title` |
| 4 | `address` | `varchar(255)` | | Да | `NULL` | Адрес. Источник `cms_returns.pvz_address` |
| 5 | `working_time` | `varchar(255)` | | Да | `NULL` | Режим работы. Источник `cms_returns.pvz_work_time` |
| 6 | `geo_id` | `varchar(36)` | | Да | `NULL` | Город в геосервисе. Список магазинов: `geo_id` = город возврата |
| 7 | `latitude` | `varchar(50)` | | Да | `NULL` | Широта |
| 8 | `longitude` | `varchar(50)` | | Да | `NULL` | Долгота |
| 9 | `route` | `varchar(500)` | | Да | `NULL` | Как добраться |
| 10 | `stock_type` | `enum('main','shop','additional')` | | Нет | `shop` | Тип склада. Для возврата - только `shop` |
| 11 | `_state` | `tinyint(3)` | | Нет | `0` | Активность |
| 12 | `for_cnc` | `tinyint(1)` | | Нет | `0` | Click and collect |
| 13 | `for_reservation` | `tinyint(1)` | | Нет | `0` | Бронирование |
| 14 | `for_returns` | `tinyint(1)` | | Нет | `0` | **Новое поле.** Магазин принимает возвраты |

### 4.12. `cms_payment_types` - способы оплаты

**Зачем нужна:** способы оплаты. Через `cms_payment_type_refund_method` определяют способ возврата денег и нужны ли реквизиты.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `internal_id` | `int(11)` | UK | Да | `NULL` | Код способа оплаты (`1` карта онлайн, `3` наличные курьеру ...). На него ссылаются `cms_orders.payment_method` и `cms_payment_type_refund_method.payment_type` |
| 3 | `code` | `varchar(255)` | | Да | `NULL` | Код |
| 4 | `crm_title` | `varchar(255)` | | Да | `NULL` | Название в RetailCRM |
| 5 | `is_bnpl` | `tinyint(1)` | | Да | `0` | BNPL-сервис (Долями, Подели): деньги возвращаются через провайдера |

### 4.13. `cms_giftcard_use` - списания сертификатов

**Зачем нужна:** сколько по заказу списано с подарочных сертификатов. Нужна для расчёта строки `certificate` в `cms_return_refunds` (в MVP деньги на сертификат не возвращаются: оплаченная сертификатом сумма возвращается по реквизитам — `RULE-37`, `ADR-RET-046`; возврат на сертификат — Post-MVP).

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `order_id` | `int(11)` | FK, IDX | Да | `NULL` | Заказ.<br>Связь: `cms_giftcard_use.order_id = cms_orders.id` |
| 3 | `guid` | `varchar(40)` | IDX | Да | `NULL` | GUID сертификата |
| 4 | `cert_number` | `varchar(20)` | | Да | `NULL` | Маскированный номер сертификата |
| 5 | `amount` | `decimal(10,2)` | | Нет | - | Сумма списания. Хранится на весь заказ, по штукам не распределена |
| 6 | `is_purchased` | `tinyint(1)` | | Нет | `0` | Сумма фактически списана |

### 4.14. `cms_order_receipts` - фискальные чеки

**Зачем нужна:** чеки заказа. Чек возврата (`operation = sell_refund`) связывается с заявкой через `cms_returns.receipt_id`. PostMVP.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор чека |
| 2 | `order_id` | `int(11)` | FK (лог.), IDX | Да | `NULL` | Заказ.<br>Связь: `cms_order_receipts.order_id = cms_orders.id` |
| 3 | `operation` | `enum('sell','sell_refund','buy','buy_refund','sell_correction','buy_correction','sell_refund_correction','buy_refund_correction')` | | Да | `NULL` | Операция |
| 4 | `payment_system` | `enum('yookassa','dolyame','podeli')` | IDX | Да | `NULL` | Платёжная система |
| 5 | `sum` | `decimal(10,2)` | | Да | `NULL` | Сумма чека |
| 6 | `receipt_id` | `varchar(130)` | UK | Да | `NULL` | Уникальный ID чека |
| 7 | `receipt` | `longtext` | | Да | `NULL` | Данные чека |
| 8 | `ofd_response` | `longtext` | | Да | `NULL` | Ответ ОФД |
| 9 | `created_at` | `timestamp` | | Нет | `current_timestamp()` | Дата создания |

### 4.15. `cms_order_return_statuses_wms` - статусы возврата WMS

**Зачем нужна:** справочник статусов возврата на складе, которые присылает 1С / WMS (коды 1-9, 11).

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `code` | `varchar(255)` | UK | Нет | - | Код статуса. На него ссылаются `cms_orders.return_status_wms` и `cms_returns.return_status_wms` |
| 3 | `title` | `varchar(255)` | | Нет | - | Название |

### 4.16. `cms_return_reasons_groups` - группы причин

**Зачем нужна:** группы причин возврата - то, что клиент выбирает в выпадающем списке. Управляются из админки сайта (комментарий к BRD: причины берутся оттуда).

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор группы |
| 2 | `title` | `varchar(255)` | | Нет | - | Название |
| 3 | `order` | `int(11)` | | Да | `NULL` | Сортировка (в отличие от других таблиц - без подчёркивания) |
| 4 | `active` | `tinyint(3)` | | Да | `1` | Активность |
| 5 | `created_at` | `timestamp` | | Нет | `current_timestamp()` | Дата создания |
| 6 | `updated_at` | `timestamp` | | Нет | `current_timestamp()` | Дата изменения, on update |

### 4.17. `cms_return_reasons` - уточнения причин

**Зачем нужна:** уточнения внутри группы причины.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор причины |
| 2 | `group_id` | `int(11)` | FK, IDX | Да | `NULL` | Группа.<br>Связь: `cms_return_reasons.group_id = cms_return_reasons_groups.id` |
| 3 | `code` | `varchar(255)` | | Да | `NULL` | Технический код. **Не уникален и без индекса** |
| 4 | `title` | `varchar(255)` | | Да | `NULL` | Название для клиента |
| 5 | `description` | `text` | | Да | `NULL` | Подсказка под уточнением |
| 6 | `active` | `tinyint(1)` | IDX | Да | `NULL` | Активность |
| 7 | `_order` | `int(11)` | IDX | Да | `NULL` | Сортировка |

### 4.18. `cms_return_reasons_content` - переводы причин

**Зачем нужна:** названия причин на других языках.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `parent_id` | `int(11)` | FK, IDX | Да | `NULL` | Причина.<br>Связь: `cms_return_reasons_content.parent_id = cms_return_reasons.id` |
| 3 | `lang_id` | `int(11)` | | Да | `NULL` | Язык |
| 4 | `title` | `varchar(255)` | | Да | `NULL` | Перевод названия |

### 4.19. `cms_return_method` - способы возврата товара

**Зачем нужна:** справочник способов возврата: курьер, ПВЗ СДЭК, 5Post, магазин, Почта России. Показывается клиенту при оформлении, задаёт порядок и инструкцию «Что дальше».

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор способа |
| 2 | `alias` | `varchar(255)` | UK | Нет | - | Код: `courier`, `sdek-pvz`, `5post`; новые строки `store`, `russian-post` |
| 3 | `title` | `varchar(255)` | | Нет | - | Название |
| 4 | `description` | `text` | | Да | `NULL` | Короткая подсказка под карточкой способа при оформлении |
| 5 | `is_enabled` | `tinyint(1)` | | Нет | `1` | Активен на сайте |
| 6 | `is_enabled_mobile` | `tinyint(1)` | | Нет | `1` | Активен в МП |
| 7 | `instruction` | `text` | | Да | `NULL` | **Новое поле.** Инструкция «Что дальше» в созданном возврате (для Почты России - с адресом склада) |
| 8 | `_order` | `int(11)` | | Нет | `0` | **Новое поле.** Порядок вывода и автовыбор «первого по приоритету» |
| 9 | `rcrm_tk_id` | `varchar(32)` | | Да | `NULL` | **Новое поле.** Код службы в RetailCRM для передачи заявки. Заменяет константы `ReturnMethodEnum` (`13`, `567`, `55`) |

## 5. Описание новых таблиц

### 5.1. `cms_returns` - заявка на возврат

**Зачем нужна:** шапка заявки. Одна строка - одна заявка; по одному заказу может быть несколько заявок. Хранит способ и точку возврата, текущий статус, номера для обмена с 1С и RetailCRM, реквизиты.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор заявки |
| 2 | `return_guid` | `char(36)` | UK | Нет | - | UUID для обмена с 1С, RetailCRM, WMS |
| 3 | `return_num` | `varchar(32)` | UK | Нет | - | Номер заявки. **Генерирует сайт** при создании: `cms_orders.order_num` + «-» + `return_seq` с ведущим нулём (`500128139-01`). Передаётся в RetailCRM и 1С, по нему системы находят заявку. Для заявок, созданных в RetailCRM и 1С, номер присваивается при импорте (см. открытые вопросы) |
| 4 | `return_seq` | `int(11)` | UK (`order_id`, `return_seq`) | Нет | - | Порядковый номер заявки в заказе, включая отменённые. Считается на сайте: `MAX(return_seq) + 1` по заказу; уникальный ключ защищает от двух одинаковых номеров при одновременном создании |
| 5 | `user_id` | `int(11)` | FK, IDX | Нет | - | Пользователь.<br>Связь: `cms_returns.user_id = cms_users_user.id` |
| 6 | `order_id` | `int(11)` | FK, IDX | Нет | - | Исходный заказ.<br>Связь: `cms_returns.order_id = cms_orders.id` |
| 7 | `status_id` | `int(11)` | FK, IDX | Нет | - | Текущий статус.<br>Связь: `cms_returns.status_id = cms_return_statuses.internal_id` |
| 8 | `source` | `varchar(16)` | | Нет | - | Где оформлена: `site`, `mobile`, `rcrm` («Дружба»), `onec` (магазин) |
| 9 | `replaced_return_id` | `int(11)` | FK | Да | `NULL` | Отменённая заявка, которую заменила эта (смена канала).<br>Связь: `cms_returns.replaced_return_id = cms_returns.id` |
| 10 | `return_method_id` | `int(11)` | FK, IDX | Нет | - | Способ возврата.<br>Связь: `cms_returns.return_method_id = cms_return_method.id` |
| 11 | `delivery_tk_id` | `int(11)` | FK | Да | `NULL` | Служба для курьера, ПВЗ, Почты. Пусто для магазина.<br>Связь: `cms_returns.delivery_tk_id = cms_delivery_tk.id` |
| 12 | `return_order_num` | `varchar(255)` | | Да | `NULL` | Номер документа «Возврат» в 1С, если он отличается от `return_num`. Заполняется по ответу 1С; `NULL` - 1С ещё не ответила или использует наш `return_num`. Нужен для сверки и поддержки: по нему «Дружба» и склад ищут документ в 1С |
| 13 | `return_status_wms` | `varchar(255)` | FK | Да | `NULL` | Статус возврата на складе.<br>Связь: `cms_returns.return_status_wms = cms_order_return_statuses_wms.code` |
| 14 | `country` | `varchar(2)` | | Нет | - | ISO страны возврата |
| 15 | `region` | `varchar(255)` | | Да | `NULL` | Регион |
| 16 | `city` | `varchar(255)` | | Нет | - | Город |
| 17 | `city_fias` | `varchar(255)` | | Нет | - | ID города в геосервисе. Тот же формат, что `cms_orders.city_fias` и `cms_delivery_city.geo_id` (для других стран Place ID длиннее 36 символов) |
| 18 | `return_street` | `varchar(255)` | | Да | `NULL` | Улица. Обязательно для курьера |
| 19 | `return_house` | `varchar(255)` | | Да | `NULL` | Дом, корпус. Обязательно для курьера |
| 20 | `return_flat` | `varchar(255)` | | Да | `NULL` | Квартира / офис |
| 21 | `return_postal` | `varchar(20)` | | Да | `NULL` | Индекс. Обязательно для курьера, если геосервис его не определил |
| 22 | `return_address` | `varchar(512)` | | Да | `NULL` | Полный адрес забора одной строкой. Для курьера |
| 23 | `pvz_id` | `varchar(32)` | | Да | `NULL` | Пункт сдачи в сервисе логистики. Обязательно для ПВЗ. Тип как у `cms_orders.pvz_id` |
| 24 | `store_code` | `smallint(6) unsigned` | FK, IDX | Да | `NULL` | Магазин сдачи. Обязательно для `store`.<br>Связь: `cms_returns.store_code = cms_catalog_stock.store_code` |
| 25 | `pvz_title` | `varchar(255)` | | Да | `NULL` | Слепок названия пункта / магазина на момент создания |
| 26 | `pvz_address` | `varchar(512)` | | Да | `NULL` | Слепок адреса |
| 27 | `pvz_work_time` | `varchar(255)` | | Да | `NULL` | Слепок режима работы |
| 28 | `return_date` | `date` | | Да | `NULL` | Плановая дата забора. Обязательно для курьера |
| 29 | `return_time` | `varchar(32)` | | Да | `NULL` | Интервал текстом для клиента. Обязательно для курьера |
| 30 | `return_time_from` | `time` | | Да | `NULL` | Начало интервала. `time`, а не строка: интервалы сравниваются и сортируются |
| 31 | `return_time_to` | `time` | | Да | `NULL` | Конец интервала |
| 32 | `handover_deadline` | `datetime` | | Да | `NULL` | Крайний срок передачи («Вернуть до») для ПВЗ, магазина, Почты |
| 33 | `handed_over_at` | `datetime` | | Да | `NULL` | Фактическая передача товара |
| 34 | `qr_code` | `varchar(255)` | | Да | `NULL` | Наш QR для сдачи в магазин. Обязательно для `store` |
| 35 | `external_return_id` | `varchar(255)` | | Да | `NULL` | PostMVP. ID заявки у перевозчика |
| 36 | `track_number` | `varchar(255)` | | Да | `NULL` | PostMVP. Трек-номер |
| 37 | `waybill_number` | `varchar(255)` | | Да | `NULL` | PostMVP. Номер отправления СДЭК |
| 38 | `pin_code` | `varchar(32)` | | Да | `NULL` | PostMVP. PIN-код 5Post |
| 39 | `user_refund` | `text` | | Да | `NULL` | Текущие реквизиты (JSON), шифрованно. Обязательно, если `cms_refund_methods.requires_bank_data = 1`. Источник - `cms_users_refund` |
| 40 | `receipt_id` | `int(11)` | FK | Да | `NULL` | PostMVP. Чек возврата.<br>Связь: `cms_returns.receipt_id = cms_order_receipts.id` |
| 41 | `cancel_reason` | `varchar(255)` | | Да | `NULL` | Причина отмены. Заполняется при отмене |
| 42 | `created_at` | `timestamp` | | Нет | `current_timestamp()` | Дата оформления |
| 43 | `updated_at` | `timestamp` | | Нет | `current_timestamp()` | Дата изменения, on update |

Ограничение по способу: для `store` заполнены `store_code` и `qr_code`, `delivery_tk_id` пусто; для курьера - `delivery_tk_id` и адрес; для ПВЗ - `delivery_tk_id` и `pvz_id`; `store_code` у них пусто.

### 5.2. `cms_return_positions` - позиция возврата

**Зачем нужна:** возвращаемые штуки. Одна строка - одна штука со своей причиной, статусом и суммой к возврату. Данные товара не копируются, берутся из позиции заказа.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор строки |
| 2 | `return_id` | `int(11)` | FK, IDX | Нет | - | Заявка.<br>Связь: `cms_return_positions.return_id = cms_returns.id` |
| 3 | `order_position_id` | `int(11)` | FK, IDX | Нет | - | Позиция заказа.<br>Связь: `cms_return_positions.order_position_id = cms_order_positions.id` |
| 4 | `barcode` | `bigint(20)` | IDX | Нет | - | Копия `cms_order_positions.barcode` для сверки с 1С |
| 5 | `reason_group_id` | `int(11)` | FK | Нет | - | Группа причины.<br>Связь: `cms_return_positions.reason_group_id = cms_return_reasons_groups.id` |
| 6 | `reason_id` | `int(11)` | FK | Да | `NULL` | Уточнение причины, если у группы оно есть.<br>Связь: `cms_return_positions.reason_id = cms_return_reasons.id` |
| 7 | `status_id` | `int(11)` | FK | Нет | - | Статус штуки.<br>Связь: `cms_return_positions.status_id = cms_return_position_statuses.internal_id` |
| 8 | `quantity` | `int(3)` | | Нет | `1` | Количество, всегда `1` |
| 9 | `refund_amount` | `decimal(10,2)` | | Нет | - | Расчётная сумма за штуку при оформлении. Не меняется |
| 10 | `refunded_amount` | `decimal(10,2)` | | Да | `NULL` | Фактически возвращено. `NULL` - ещё не возвращали, `0` - отказано |
| 11 | `refund_bonus_amount` | `decimal(10,2)` | | Нет | `0.00` | Расчётные баллы за штуку |
| 12 | `refunded_bonus_amount` | `decimal(10,2)` | | Да | `NULL` | Фактически возвращено баллами |

### 5.3. `cms_return_changes` - изменения заявки

**Зачем нужна:** лента событий заявки. Одна строка - одно событие: создание, изменение содержания, смена статуса, отмена. Из неё строятся история статусов для сайта и МП, журнал изменений для «Дружбы» и все версии заявления - PDF собирается на лету из `snapshot`.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `return_id` | `int(11)` | FK, IDX (`return_id`, `changed_at`) | Нет | - | Заявка.<br>Связь: `cms_return_changes.return_id = cms_returns.id` |
| 3 | `event` | `varchar(16)` | | Нет | - | `created`, `changed` (изменено содержание), `status` (только статус), `cancelled` |
| 4 | `source` | `varchar(32)` | | Нет | - | Источник: `SITE`, `MOBILE`, `1C`, `RCRM`, `WMS` |
| 5 | `author` | `varchar(255)` | | Да | `NULL` | Клиент или сотрудник «Дружбы» / магазина, если источник передаёт |
| 6 | `status_id` | `int(11)` | FK | Нет | - | Статус заявки после события.<br>Связь: `cms_return_changes.status_id = cms_return_statuses.internal_id` |
| 7 | `diff` | `longtext` (JSON) | | Да | `NULL` | Изменённые поля: `{"return_date": ["2026-10-02", "2026-10-03"]}`. Реквизиты не пишутся, только признак изменения |
| 8 | `application_version` | `int(11)` | UK (`return_id`, `application_version`) | Да | `NULL` | Версия заявления. Для `created`, `changed`, `cancelled`; для `status` - `NULL` |
| 9 | `template_version` | `smallint(6)` | | Да | `NULL` | Версия шаблона PDF. Заполняется вместе с `application_version` |
| 10 | `snapshot` | `longtext` (JSON) | | Да | `NULL` | Полный снимок заявки для PDF: клиент, заказ, номер заявки, позиции (название, артикул, цвет, размер, штрихкод, цена, количество), причины текстом, способ и точка, способ возврата денег, суммы. Для `cancelled` повторяет последнюю версию |
| 11 | `bank_data_encrypted` | `text` | | Да | `NULL` | Реквизиты на момент версии, шифрованно |
| 12 | `external_event_at` | `datetime` | | Да | `NULL` | Время события во внешней системе |
| 13 | `changed_at` | `datetime` | | Нет | - | Время фиксации события у нас |

`longtext` (JSON): в MariaDB тип `json` - синоним `longtext` с проверкой `JSON_VALID`.
Записи с заявлением не удаляются минимум 5 лет (комментарий к BRD); старые версии шаблонов PDF остаются в коде.

### 5.4. `cms_return_status_groups` - группы статусов заявки

**Зачем нужна:** группирует статусы заявки для вкладок и фильтров (в работе, завершённые, отменённые).

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор группы |
| 2 | `code` | `varchar(64)` | UK | Нет | - | Код группы. На него ссылается `cms_return_statuses.group` |
| 3 | `title` | `varchar(255)` | | Нет | - | Название |
| 4 | `active` | `tinyint(1)` | | Нет | `1` | Активность |
| 5 | `_order` | `int(11)` | | Нет | `0` | Сортировка |

### 5.5. `cms_return_statuses` - статусы заявки

**Зачем нужна:** справочник статусов заявки. В Шаге 1: Создан, Завершён, Отменён.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `internal_id` | `int(11)` | UK | Нет | - | Бизнес-код. На него ссылаются `cms_returns.status_id` и `cms_return_changes.status_id` |
| 3 | `code` | `varchar(64)` | UK | Нет | - | Символьный код (`created`, `completed`, `cancelled`) |
| 4 | `title` | `varchar(255)` | | Нет | - | Внутреннее название |
| 5 | `client_title` | `varchar(255)` | | Нет | - | Название для клиента |
| 6 | `group` | `varchar(64)` | FK | Нет | - | Группа.<br>Связь: `cms_return_statuses.group = cms_return_status_groups.code` |
| 7 | `active` | `tinyint(1)` | | Нет | `1` | Активность |
| 8 | `_order` | `int(11)` | | Нет | `0` | Сортировка |
| 9 | `can_be_cancelled` | `tinyint(1)` | | Нет | `0` | Клиент может отменить заявку в этом статусе |

### 5.6. `cms_return_position_statuses` - статусы штуки

**Зачем нужна:** справочник статусов возвращаемой штуки (ожидается, получена, принята, отклонена) - склад принимает или отклоняет каждую штуку отдельно.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `internal_id` | `int(11)` | UK | Нет | - | Бизнес-код. На него ссылаются `cms_return_positions.status_id` и `cms_return_position_status_history.status_id` |
| 3 | `code` | `varchar(64)` | UK | Нет | - | Символьный код (`awaiting`, `received`, `accepted`, `rejected`) |
| 4 | `title` | `varchar(255)` | | Нет | - | Внутреннее название |
| 5 | `client_title` | `varchar(255)` | | Нет | - | Название для клиента |
| 6 | `active` | `tinyint(1)` | | Нет | `1` | Активность |
| 7 | `_order` | `int(11)` | | Нет | `0` | Сортировка |

### 5.7. `cms_return_position_status_history` - история статусов штуки

**Зачем нужна:** когда и по какому событию склада штука сменила статус. Отдельно от `cms_return_changes`, потому что события идут по штукам, а не по заявке.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `return_position_id` | `int(11)` | FK, IDX | Нет | - | Строка возврата.<br>Связь: `cms_return_position_status_history.return_position_id = cms_return_positions.id` |
| 3 | `status_id` | `int(11)` | FK | Нет | - | Статус штуки.<br>Связь: `cms_return_position_status_history.status_id = cms_return_position_statuses.internal_id` |
| 4 | `status_at` | `datetime` | | Нет | - | Время перехода |
| 5 | `source` | `varchar(32)` | | Нет | - | Источник: `WMS`, `1C`, `SITE` |
| 6 | `external_event_at` | `datetime` | | Да | `NULL` | Время события во внешней системе |
| 7 | `created_at` | `timestamp` | | Нет | `current_timestamp()` | Время записи у нас |

### 5.8. `cms_refund_methods` - способы возврата денег

**Зачем нужна:** справочник, куда клиенту возвращаются деньги. Заменяет свободную строку `cms_orders.return_money`; признак `requires_bank_data` - единое правило «нужны ли реквизиты» для сайта и МП.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор способа |
| 2 | `code` | `varchar(64)` | UK | Нет | - | `card_payment`, `bank_details`, `certificate`, `bonus`, `cash` |
| 3 | `title` | `varchar(255)` | | Нет | - | Название для клиента |
| 4 | `requires_bank_data` | `tinyint(1)` | | Нет | `0` | Нужны банковские реквизиты |
| 5 | `_order` | `int(11)` | | Нет | `0` | Сортировка |
| 6 | `active` | `tinyint(1)` | | Нет | `1` | Активность |

### 5.9. `cms_payment_type_refund_method` - способ оплаты → способ возврата денег

**Зачем нужна:** по способу оплаты заказа определяет основной способ возврата денег. Одна строка - один способ оплаты. Сертификат и баллы добавляются отдельными строками `cms_return_refunds`, если были списания.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `payment_type` | `int(11)` | FK, UK | Нет | - | Способ оплаты.<br>Связь: `cms_payment_type_refund_method.payment_type = cms_payment_types.internal_id` |
| 3 | `refund_method_id` | `int(11)` | FK | Нет | - | Способ возврата денег.<br>Связь: `cms_payment_type_refund_method.refund_method_id = cms_refund_methods.id` |

### 5.10. `cms_return_refunds` - возврат денег по способам

**Зачем нужна:** сколько, куда и когда вернули деньги по заявке. Одна строка - один способ (часть на карту, часть на сертификат, часть баллами). Итоги заявки считаются по этой таблице. `refunded_at` - статус «деньги возвращены», который по комментарию к BRD должен к нам приходить.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор строки |
| 2 | `return_id` | `int(11)` | FK, UK (`return_id`, `refund_method_id`) | Нет | - | Заявка.<br>Связь: `cms_return_refunds.return_id = cms_returns.id` |
| 3 | `refund_method_id` | `int(11)` | FK | Нет | - | Куда возвращаем.<br>Связь: `cms_return_refunds.refund_method_id = cms_refund_methods.id` |
| 4 | `refund_amount` | `decimal(10,2)` | | Нет | - | Расчётная сумма при оформлении. Не меняется |
| 5 | `refunded_amount` | `decimal(10,2)` | | Да | `NULL` | Фактически возвращено. `NULL` - ещё не возвращали |
| 6 | `refunded_at` | `datetime` | | Да | `NULL` | Дата фактического возврата |

### 5.11. `cms_return_method_delivery_type` - тип доставки → способ возврата

**Зачем нужна:** по типу службы доставки заказа подставляет способ возврата «как в заказе». Заменяет константу `ReturnMethodEnum::ORDER_DELIVERY_TYPES_MAP`. Одна строка - один тип доставки.

| # | Атрибут | Тип | Ключ | NULL | По умолчанию | Описание |
|---|---|---|---|---|---|---|
| 1 | `id` | `int(11)` | PK | Нет | auto_increment | Идентификатор записи |
| 2 | `delivery_type` | `int(11)` | FK (лог.), UK | Нет | - | Тип доставки. Ограничение FK не создать: `cms_delivery_types.internal_id` не уникален.<br>Связь: `cms_return_method_delivery_type.delivery_type = cms_delivery_types.internal_id`; для заказа - `cms_orders.delivery_method = cms_delivery_tk.id`, затем `cms_delivery_tk.type` |
| 3 | `return_method_id` | `int(11)` | FK | Нет | - | Способ возврата.<br>Связь: `cms_return_method_delivery_type.return_method_id = cms_return_method.id` |

Начальные строки: `1 → courier`, `11 → 5post`, `15 → sdek-pvz` (как в `ReturnMethodEnum`), `7, 13, 16 → store`.

## 6. Открытые вопросы

Вопрос 2 из ERD от 29.09 («кто формирует номер заявки») **решён: номер `order_num-NN` генерирует сайт** и передаёт в RetailCRM и 1С. Вопросы 1, 3-8 остаются. Добавляются:

9. Статус «деньги возвращены» (`cms_return_refunds.refunded_at`): откуда приходит (1С или RetailCRM) и ставится ли «Возврат завершён» только после него.
10. Мастер-система для заявки: RetailCRM или 1С. От этого зависит, чьё изменение побеждает при конфликте в `cms_return_changes`.
11. Где хранится ключ шифрования реквизитов и кто в админке видит их расшифрованными.
12. Нужен ли `for_returns` в `cms_delivery_city` в MVP или хватит текущего покрытия доставки.
13. Срок для F&F: 30 дней (доска) или 31 (комментарий к BRD).
14. Что приходит в `cms_orders.return_store` из RetailCRM: `store_code` магазина или его ID в RetailCRM.
15. Сделать ли `cms_delivery_types.internal_id` уникальным (сейчас только индекс), чтобы у `cms_return_method_delivery_type` появился настоящий FK.
16. Заводит ли 1С свой номер документа «Возврат» и в каком поле ответа его присылает (для `cms_returns.return_order_num`).
17. Нумерация заявок, созданных «Дружбой» в RetailCRM и магазином в 1С: получают следующий `return_seq` при импорте к нам (тогда номер сайта нужно вернуть в RetailCRM и 1С) или RetailCRM / 1С запрашивают номер у сайта перед созданием.
18. Какой формат `return_order_num` сейчас на проде (`SELECT order_num, return_order_num FROM cms_orders WHERE return_order_num <> '' ORDER BY id DESC LIMIT 20`).
