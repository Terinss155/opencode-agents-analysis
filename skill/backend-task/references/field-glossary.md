# Словарь полей API

> Единый словарь имён полей запросов и ответов. Задача: один смысл — одно имя во всех новых и дорабатываемых методах,
> на сайте, в Mobile API и на Gate. Собран по примерам задач (`../examples/`), AS-IS процесса возврата
> (`projects/returns-2.0/as-is/`) и AS-IS-контрактам (`knowledge/12storeez-master-web/api/`, `projects/returns-2.0/as-is/api/`), 03.10.2026.

## Правила

1. Перед тем как назвать параметр, найти его смысл в словаре. Есть — использовать **каноническое имя** и тип из словаря.
2. **Имена в действующих эндпоинтах не меняются** — даже если они попали в колонку «Не использовать» (обратная совместимость с сайтом и МП). При доработке существующего метода его поля сохраняют текущие имена; по словарю называются только **новые** поля и поля **новых** методов. Синонимы в новые методы не копируются.
3. Нового смысла в словаре нет — имя по конвенции ниже, и строка добавляется в словарь в той же задаче.
4. Одно поле в Web и Mobile API называется одинаково; различаются только конверты ответа (`data` / `result`).
5. Смысл, для которого канон не выбран (⚠), в новой задаче не вводится без решения аналитика — открытый вопрос.

**Конвенция имён:** snake_case; идентификатор — `<сущность>_id`; флаг — `is_<состояние>` / `has_<что>`; дата — `<что>_date` или
`date_<что>` по образцу соседних полей; массив — множественное число (`items`, `positions`); суффикс `_return` — только у полей формы деталей возврата.

## Гео

| Смысл | Каноническое имя | Тип | Где встречается | Не использовать |
|---|---|---|---|---|
| ISO-код страны | `country_iso` | string | ECOMDEV-1239 / 1240 | — |
| Регион (название) | `region` | string | ECOMDEV-1239 / 1240 | — |
| ID региона в сервисе логистики | `region_id` | string | ECOMDEV-1239 / 1240 | — |
| Город (название) | `city` | string | ECOMDEV-1239 / 1240 | — |
| ID города в сервисе логистики | `city_id` | string | ECOMDEV-1239 / 1240 | — |
| ID города в ФИАС (геосервис) | `city_fias` | string | ECOMDEV-1239 / 1240; карточка заказа МП `order_delivery` | `city_geo_id` (TO-BE шаг 04, рабочее имя) |

## Заказ и позиции

| Смысл | Каноническое имя | Тип | Где встречается | Не использовать |
|---|---|---|---|---|
| ID заказа (в пути) | `order_id` | int | все методы возврата | `orderId` |
| Штрихкод позиции | `barcode` | int | Mobile: создание возврата | — |
| ID цвета | `color_id` | int | `order-view`, `order-refund-get-positions` | `colorId` (Web, рядом с `color_id` в том же ответе) |
| Количество единиц в позиции | `quantity` | int | Web: `order-view`, `order-refund-get-positions` | `count` (Mobile: `positions[]` карточки заказа) |

## Доставка заказа

Блок `order_delivery` описывает, куда и как был доставлен заказ; к возврату не относится.
Передаются только данные, нужные для проверки и подстановки на следующих шагах. Из объектов `address`, `pvz`, `store` заполнен один — по типу доставки.

| Смысл | Каноническое имя | Тип | Где встречается | Не использовать |
|---|---|---|---|---|
| Данные доставки заказа | `order_delivery` | object | карточка заказа МП | — |
| Адрес курьерской доставки | `address` | object: `postal`, `street`, `house`, `housing` | `order_delivery.address` | адрес строкой в поле `address` (адрес в форме возврата — `address_return`) |
| Индекс | `postal` | string | `order_delivery.address` | `zip_code` (сервис логистики); индекс в форме возврата — `index_return` |
| Улица / дом / корпус | `street` / `house` / `housing` | string | `order_delivery.address` | корпус внутри `house` |
| Пункт выдачи заказа | `pvz` | object: `provider`, `id` | `order_delivery.pvz` | — |
| Код службы пункта выдачи | `provider` | string | `order_delivery.pvz` | — |
| Магазин самовывоза | `store` | object: `store_code` | `order_delivery.store` | `store_code` на верхнем уровне блока; `cms_orders.store_code` как источник |
| Код магазина | `store_code` | int | `order_delivery.store` | — |
| Признак «способ, которым доставлен заказ» | `is_order_method` | bool | элемент `return-method-list` (задача в работе) | `delivery_type` в карточке заказа для сопоставления на клиенте |

## Возврат

| Смысл | Каноническое имя | Тип | Где встречается | Не использовать |
|---|---|---|---|---|
| Способ возврата — код элемента в списке / справочнике способов | `method` | string: `courier` / `sdek-pvz` / `5post` | `return-method-list` (1239 / 1240) | — |
| Способ возврата, выбранный клиентом в форме деталей возврата | `method_return` | string: `courier` / `sdek-pvz` / `5post` | `return-details` (1126) | `return_method` (TO-BE шаг 04, рабочее имя) |
| Тип способа возврата | `method_type` | string: `courier` / `pvz` | 1239 / 1240 | `pickup` (в чекауте = самовывоз из магазина) |
| Город возврата | `city_return` | string | форма деталей (1126) | — |
| Адрес возврата | `address_return` | ?string | форма деталей (1126) | — |
| Индекс возврата | `index_return` | ?string | форма деталей (1126) | — |
| Дата возврата | `date_return` | string `YYYY-MM-DD` | форма деталей (1126) | — |
| Доступные даты возврата | `available_dates_return` | string[] `YYYY-MM-DD` | 1239 / 1240, ошибка формы (1126) | — |
| Остаток изделий позиции, доступных к возврату | `available_return_quantity` | int | карточка заказа МП `items[]` | `return_available_count` (TO-BE шаг 01, рабочее имя) |
| Последний день оформления заявки на возврат | `until_date` (в блоке `return`) | string `YYYY-MM-DD` | карточка заказа МП `return.until_date` | `return_until_date` (TO-BE шаг 01), `return_deadline` (`BL-RET-ELIG-01`) |
| Код причины возврата | `reason_id` | string | Mobile: создание возврата | `reasonCode` (Web: `save-reason`) |
| Нужны ли банковские реквизиты | `is_bank_data_required` | bool | Mobile: карточка заказа (`return.is_bank_data_required`) | `need_bank_details` (Web: `order-refund-get-positions`, остаётся там как есть) |
| БИК банка | `bank_bic` | string | Web и Mobile | — |
| ИНН банка | `bank_inn` | string | Mobile | — |
| Название банка | `bank_name` | string | Mobile | — |
| Расчётный счёт | `user_account` | string | Mobile | — |
| Номер карты | `user_card_number` | string | Mobile | — |

## Справочные поля элемента списка

| Смысл | Каноническое имя | Тип | Где встречается | Не использовать |
|---|---|---|---|---|
| Название для вывода | `title` | string | 1239 / 1240, позиции заказа | — |
| Описание | `description` | ?string | 1239 / 1240 | `message` для описания элемента (просили МП в 1240) |
| Включено на сайте | `active` | bool | 1239 / 1240 | — |
| Включено в МП | `active_mobile` | bool | 1239 / 1240 | — |

## Пагинация и ошибки

| Смысл | Каноническое имя | Тип | Где встречается | Не использовать |
|---|---|---|---|---|
| Размер страницы | `limit` | int | Web и Mobile | `pagination[limit]` |
| Смещение | `offset` | int | Web и Mobile | `pagination[offset]` |
| Код ошибки | `code` (Web) / `error_code` (Mobile) | см. конверты | `request-response_*.md` | `errorCode` (Web: `order-refund-get-positions`, `save-reason`) |
| Поле с ошибкой | `target` | string | Web и Mobile | — |
