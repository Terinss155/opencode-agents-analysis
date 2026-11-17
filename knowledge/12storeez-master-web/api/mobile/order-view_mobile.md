# Открытие заказа — Mobile API

# Название метода

**GET /api/orders/{id}** (хост `core.12stz.com`) — Получение данных заказа

> Сверено 07.11.2026: монолит `dd4a997ac0`, Go `631ac38`, esb `4519218b`, iOS `4f321c86`.

Обработчик: `src/Modules/Mobile/Controllers/OrdersController::actionIndex()` (`:200`) → `getOrders()` (`:544`)
Трансформер: `src/Modules/Order/Transformer/OrderMobileTransformer::transformForMobile($order, full=true)`, позиции — `OrderPositionMobileTransformer::transformForMobile()`

> **Проксирование (шлюз `core`):** iOS (`OrdersEndpoint.orderDetail`, протокол `RequestTarget` → хост `core.12stz.com/api`) вызывает `GET /api/orders/{order_id}`. Этот хост обслуживает **старый шлюз `core`** — NestJS-приложение `esb-monorepo` (`libs/orders/controllers/src/lib/orders.controller.ts:227`, `getOrder`). Шлюз **параллельно** делает два запроса:
> 1. HTTP `GET {PHP_BASE_URL}mobile/orders/{order_id}` в монолит (`orders.service.ts`, `path='/orders'`; клиент `libs/core/src/lib/http-client/http-client-mobile.ts`);
> 2. gRPC `feedbacks.Mobile/CanBeSaved({order_id})` (`:236`) — можно ли оставить отзыв.
>
> Если `CanBeSaved.ok = false`, из `result.messages` удаляются сообщения со `status = can_be_marked` (`:238-249`). Ответ перепаковывается в `ResponseAction` → клиент получает `{success, result}` **без `total`**.
> Внутри монолита Yii2 UrlManager (правило `src/Modules/Mobile/Rules/UrlRule.php:83-84`) разбирает pathInfo `mobile/orders/{id}` и возвращает маршрут (route) `mobile/orders` с параметром `id` — это **внутренняя маршрутизация Yii2, а не HTTP-вызов**.
> Далее маршрут `mobile/orders` диспатчится на `Mobile\OrdersController::actionIndex()`, который читает `id` из query-параметра (`Yii::$app->request->get('id')`).
> **Копия в Go-шлюзе (ECOMDEV-2422):** `GET mobile.12stz.com/api/v1/orders/{order_id}` — `mobile-monorepo-go` `internal/app/service/orders_core.go:376` (`GetOrder`), повторяет контракт `core`: параллельно монолит `mobile/orders/{id}` (по `SITE_BASE_INTERNAL_URL`, `ProxyToSiteAsIs`) и gRPC `CanBeSaved`, фильтр `can_be_marked`, обёртка `{success, result}`. `order_id` — только цифры (`regex(^\d+$)`), query-параметры в монолит не передаются (кроме `gender` → заголовок `X-Gender`). Без `FEEDBACKS_GRPC_URL` ручка отвечает 503. **iOS на 07.11.2026 эту копию не вызывает** — ходит в `core`.
> **Важно:** в swagger монолита (`docs/openapi/mobile.yml:4982`) просмотр заказа описан как `GET /mobile/orders/{orderId}` (`operationId: getOrderById`). Пути `/orders/{orderId}/...` существуют только для операций возврата (return-details, return-method-list).

---

# Используемые методы

| Система | Метод | Ссылка |
|---------|-------|--------|
| Шлюз `core` (esb) | `GET /api/orders/{id}` → `GET /mobile/orders/{id}` + gRPC Feedbacks `CanBeSaved` | `esb-monorepo` `libs/orders/controllers/src/lib/orders.controller.ts:227` |
| Шлюз `mobile` (Go, копия, iOS не вызывает) | `GET /api/v1/orders/{id}` → `GET /mobile/orders/{id}` + gRPC Feedbacks `CanBeSaved` | `mobile-monorepo-go` `internal/app/service/orders_core.go:376` |
| Mobile | `GET /mobile/orders/{id}` | `src/Modules/Mobile/Controllers/OrdersController::actionIndex()` → `getOrders()` |
| Mobile (список) | `core` `GET /api/orders` (esb `orders.controller.ts:54`; Go-копия `orders_core.go:69`) → `GET /mobile/orders` | `src/Modules/Mobile/Controllers/OrdersController::actionIndex()` → `transformForMobile($order, false)` — список заказов; шлюз для заказов с `button.status = can_be_marked` вызывает `CanBeSaved` и при `ok = false` ставит `button: null` |
| Mobile (офлайн-чеки) | `core` `GET /api/orders/offline[/{id}]` (esb `:88`, `:146`; Go `orders_core.go:206`, `:282`) | В монолит не идут: gRPC Orders (`orders.Offline`) + обогащение позиций `POST api2/products/items` |

---

# Диаграмма взаимодействия

```mermaid
sequenceDiagram
    autonumber
    actor U as USER
    participant APP as Mobile App
    participant G as Шлюз core (esb-monorepo)
    participant FB as feedbacks-ms (gRPC)
    participant URL as UrlRule (Yii2)
    participant SVC as OrdersController
    participant REPO as OrderRepository
    participant TR as OrderMobileTransformer
    participant DB as MariaDB

    U ->> APP: Открыть заказ
    APP ->> G: GET core.12stz.com/api/orders/500127505 (Authorization: Bearer JWT)
    activate G
    par параллельно
    G ->> FB: feedbacks.Mobile/CanBeSaved(order_id)
    FB -->> G: {ok}
    and
    G ->> URL: GET /mobile/orders/500127505 (x-access-token, x-session-token из JWT)
    end
    activate URL
    URL ->> URL: parseRequest(): regex /orders\/\d+/ → route mobile/orders, id=500127505
    URL -->> SVC: dispatch: actionIndex() (id в query)
    deactivate URL
    activate SVC
    SVC ->> REPO: findOneByIdAndUserId(orderId, userId)
    REPO ->> DB: SELECT * FROM orders WHERE id=? AND user_id=?
    activate DB
    DB -->> REPO: Order record
    deactivate DB
    REPO -->> SVC: Order model
    SVC ->> SVC: null или резерв (getIsReservation) → 404, error_code 1009
    SVC ->> TR: transformForMobile(order, full=true)
    activate TR
    TR ->> DB: SELECT * FROM order_positions WHERE order_id=?
    activate DB
    DB -->> TR: OrderPosition records
    deactivate DB
    TR ->> DB: SELECT * FROM delivery_tk WHERE id=?
    DB -->> TR: DeliveryTk record
    TR ->> DB: SELECT * FROM payment_types WHERE internal_id=?
    DB -->> TR: PaymentType record
    TR ->> DB: SELECT * FROM order_statuses WHERE internal_id=?
    DB -->> TR: OrderStatus record
    TR -->> SVC: Array (formatted order data)
    deactivate TR
    SVC -->> G: {success, total, result}
    deactivate SVC
    G ->> G: ok=false → убрать messages со status=can_be_marked; ResponseAction (без total)
    G -->> APP: {success: true, result: {...}}
    deactivate G
    APP -->> U: Данные заказа
```

## Упрощённая диаграмма взаимодействия

Диаграмма показывает взаимодействие систем без детализации внутренней логики монолита.

```mermaid
sequenceDiagram
    autonumber
    actor U as Юзер
    participant APP as Mobile App
    participant GW as Шлюз core (esb)
    participant FB as feedbacks-ms
    participant MON as Monolith
    participant DB as DB

    U ->> APP: Открыть заказ
    APP ->> GW: GET /api/orders/500127505
    GW ->> FB: CanBeSaved (gRPC, параллельно)
    GW ->> MON: GET /mobile/orders/500127505
    MON ->> DB: Получить заказ пользователя и связанные данные
    DB -->> MON: Данные заказа
    MON -->> GW: JSON с данными заказа
    FB -->> GW: можно ли оценить
    GW -->> APP: JSON с данными заказа (без лишних can_be_marked)
    APP -->> U: Показать заказ
```

---

# Входящие данные

## Источник данных

| Параметр | Обяз. | Тип источника | Метод-источник | Поле ответа | Описание |
|----------|-------|---------------|----------------|-------------|----------|
| `Authorization: Bearer <JWT>` | + | Header (клиент → шлюз) | `authorization/*` шлюза `core` | — | JWT шлюза; из claim `session_token` шлюз формирует `x-session-token` |
| `x-platform`, `version` | + | Header (клиент → шлюз) | Приложение | — | Платформа и версия; шлюз `core` передаёт `version` в монолит как `x-version` (в Go-копии обязательны `X-Platform`/`X-Version`, иначе 400) |
| `x-access-token` | + | Header (шлюз → монолит) | `PHP_API_KEY` шлюза | — | Ключ мобильного API монолита; клиент его **не** передаёт |
| `x-session-token` | + | Header (шлюз → монолит) | `users_mobile_sessions` | — | Токен сессии (из JWT) |
| `id` | + | Path → Query | Часть URL (`/api/orders/{id}`), UrlRule монолита транслирует в query `id` | `result.id` | ID заказа |

### Примечание

- Внешний путь `GET /api/orders/{order_id}` проксируется шлюзом `core` на `GET /mobile/orders/{order_id}`; дополнительно шлюз пробрасывает `user-agent`, `X-Request-Id`, `x-language`, `Referer`, `DeviceID`, `X-Real-IP`, а query `gender` — как заголовок `X-Gender` (`http-client-mobile.ts`).
- Внутри монолита UrlRule транслирует pathInfo `mobile/orders/{id}` в маршрут `mobile/orders` с параметром `id` (query), а `Mobile\OrdersController::actionIndex()` читает его через `Yii::$app->request->get('id')`.
- Заказы типа `reservation` (резерв в магазине) исключаются из ответа.

---

# Описание входных параметров

| Параметр | Способ передачи | Тип | Обяз. | Описание | Пример |
|----------|-----------------|-----|-------|----------|--------|
| `id` | path (внешний) / query (внутренний) | integer | + | ID заказа | `500127505` |

---

# Пример запроса

```http
GET /api/orders/500127505 HTTP/1.1
Host: core.12stz.com
Authorization: Bearer {jwt}
x-platform: ios
version: 1.89.0

# Шлюз core проксирует на внутренний путь монолита (с x-access-token, x-session-token, x-version):
# GET /mobile/orders/500127505  →  UrlRule: route mobile/orders (id=500127505)  →  actionIndex()
# Копия в Go (iOS пока не вызывает): GET mobile.12stz.com/api/v1/orders/500127505 (X-Platform, X-Version, Authorization)
```

---

# Возвращаемые данные

## Описание параметров положительного ответа (full=true)

> **Примечание:** монолит отдаёт `{success, total, result: {...}}`; шлюз `core` (и Go-копия) перепаковывает ответ в `{success, result}` — поля `total` клиент **не получает**.

### Блок `result.*`

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `result.id` | integer | ID заказа | `12345` |
| `result.dolyame_id` | string\|null | ID заказа в Dolyame | `"dl_abc123"` |
| `result.date` | string | Дата создания (Y-m-d H:i:s) | `"2026-08-15 14:30:00"` |
| `result.status` | integer | Код статуса заказа | `14` |
| `result.status_message` | string | Клиентское название статуса | `"Передан в доставку"` |
| `result.expiration_date.start` | integer | Timestamp создания заказа (`created_at`) — **начало периода** | `1723733400` |
| `result.expiration_date.end` | integer\|null | Timestamp даты доставки (`delivery_date`) — **конец периода** | `1724000000` |
| `result.title` | string | Заголовок заказа (формируется по шаблону `Заказ №{id}`) | `"Заказ №12345"` |
| `result.is_click_and_collect` | boolean | Самовывоз из магазина | `false` |
| `result.giftcardsAmount` | float | Сумма использованных подарочных сертификатов | `5000.00` |
| `result.giftcards` | array | Данные использованных сертификатов | `[{id, num, sum}]` |

> **⚠️ `expiration_date` — это НЕ таймер оплаты.** Это период жизненного цикла заказа «от создания до доставки» (`start` = `created_at`, `end` = `delivery_date`), используется для отображения диапазона на карточке заказа.
>
> **Реальный дедлайн оплаты — `payment.pay_before`** (см. блок `payment`): `cms_orders.created_at + 2 часа` (`OrderDictionary::PAYMENT_TIME_BEFORE_CANCEL = 'PT2H'`). После этого времени заказ автоотменяется через `OrderHelper::createStatusTimer()` → `OrderStatusTimer::create()` (для статусов `WAITING_PAYMENT`, `PREORDER_NEW`, `CC_WAITING_FOR_PAYMENT`). `pay_before` возвращается только если заказ **не оплачен** и способ оплаты **не офлайн**.
>
> **⚠️ `expiration_date.end` = `cms_orders.delivery_date` — это ПЛАНОВАЯ дата доставки, НЕ фактическая.** Ставится при оформлении заказа (выбор клиента) или из 1С при переносе; при фактическом получении товара **не обновляется**. Поля «фактическая дата получения» в системе **не существует**.
>
> **⚠️ `cms_orders.end_date` ≠ `expiration_date.end` — это РАЗНЫЕ поля таблицы `cms_orders`:**
> - `expiration_date.end` = `cms_orders.delivery_date` — **плановая** дата доставки (для отображения периода на карточке);
> - `cms_orders.end_date` — **дата выполнения заказа** (фактическая, с подтверждением от 1С): ставится один раз при переходе в статус «выполнен» (`end_date = date('Y-m-d H:i:s')` в `OrderUpdateService`/`RcrmOrderService`).
>
> **⚠️ AS-IS: расчёт окна возврата идёт от `end_date + N дней`** (НЕ от `delivery_date`):
> `canBeReturned = (isCompleted || isReturned) && strtotime(end_date + "N days") > time()`, где `N = Parameter::valueOf('days_can_be_returned')` (в БД, в UI показывается как 14).
> - **Как прячется кнопка:** когда `end_date + N дней <= now` → `canBeReturned()` = `false` → на мобилке не формируется сообщение `can_be_returned` (кнопка «Оформить возврат» скрыта), на вебе `status.show_refund_button = false`.
> - Т.е. сообщение «14 дней после получения заказа» — фактически 14 дней от `end_date` (дата выполнения заказа), а не от фактического получения товара клиентом.
> - Нюанс (подтверждено разработчиком): для возврата **курьеркой** при выборе даты окно считается мягче — разрешают выбрать любую дату, пока не истекло 14 дней (намеренно не показывают «последний день»); для **ПВЗ** — точные расчёты от `cms_orders.end_date`.

### Блок `recipient`

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `recipient.email` | string\|null | Email получателя | `"user@mail.ru"` |
| `recipient.first_name` | string\|null | Имя | `"Иван"` |
| `recipient.last_name` | string\|null | Фамилия | `"Иванов"` |
| `recipient.phone` | string\|null | Телефон | `"+79001234567"` |

### Блок `payment`

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `payment.type_title` | string\|null | Платформенный заголовок типа оплаты | `"Карта"` |
| `payment.type_name` | string | Код типа оплаты | `"yookassa"` |
| `payment.type_id` | integer\|null | ID типа оплаты | `1` |
| `payment.send` | object | Параметры для отправки в платёжную систему (YooKassa) | `{amount: {value: "1500", currency: "RUB"}}` |
| `payment.total_cost` | integer | Сумма товаров до скидок | `2000` |
| `payment.cost_sum` | float | Итого с учётом скидок | `1500.00` |
| `payment.delivery_cost` | integer | Стоимость доставки | `300` |
| `payment.discount` | integer\|float | Общая скидка | `500` |
| `payment.discount_sale` | integer\|float | Скидка по акции | `400` |
| `payment.discount_bonus` | integer\|float | Скидка бонусами | `0` |
| `payment.discount_promo` | integer\|float | Скидка по промокоду | `100` |
| `payment.total_payable` | integer | К оплате (за вычетом сертификатов) | `1500` |
| `payment.is_payed` | boolean | Оплачен ли заказ | `true` |
| `payment.by_certificate` | float | Сумма сертификатов | `5000.00` |
| `payment.payment_system` | string\|null | Система оплаты | `"yookassa"` |
| `payment.payment_url` | string\|null | Ссылка на оплату | `"https://yookassa.ru/..."` |
| `payment.pay_before` | string\|false | **Дедлайн оплаты** (ISO 8601) = `created_at + 2 часа` (`PAYMENT_TIME_BEFORE_CANCEL = 'PT2H'`). После него заказ автоотменяется. Присутствует только если заказ не оплачен и способ оплаты не офлайн | `"2026-08-16T14:30:00+03:00"` |

### Блок `items[]` (позиции заказа)

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `items[].id` | integer | ID позиции | `67890` |
| `items[].article` | string | Артикул товара | `"ART-12345"` |
| `items[].model_id` | integer | ID товара (products.id) | `555` |
| `items[].barcode` | integer | Штрихкод (product_sizes.id) | `111222` |
| `items[].title` | string | Название модели (`OrderPosition::getCurrentModelTitle()`) | `"Пламя"` |
| `items[].tags[]` | array | Теги товара | `[{id: 1, title: "New"}, ...]` |
| `items[].colors[0].id` | integer | ID товара | `555` |
| `items[].colors[0].color_id` | integer | ID цвета | `12` |
| `items[].colors[0].hash` | string | HEX-код цвета | `"#000000"` |
| `items[].colors[0].color` | string | Название цвета | `"Чёрный"` |
| `items[].colors[0].image` | string\|null | URL изображения цвета | `"https://..."` |
| `items[].colors[0].has_circle` | boolean | Есть ли кружок цвета | `true` |
| `items[].colors[0].circle_color` | string | Цвет кружка: `Product::CIRCLE_COLOR_HASH`, если `has_circle`, иначе `""` | `"#FFFFFF"` |
| `items[].discount_price` | float | Цена со скидкой | `1200.00` |
| `items[].price` | float | Цена до скидки | `1500.00` |
| `items[].preview` | string | URL превью изображения | `"https://..."` |
| `items[].preview_new[]` | array | Превью нового формата | `[{type, width, height, url}]` |
| `items[].selected_color_id` | integer | Выбранный цвет | `12` |
| `items[].selected_size_id` | string | Размер | `"M"` |
| `items[].count` | integer | Количество | `1` |
| `items[].is_present` | boolean | Подарок | `false` |
| `items[].can_be_returned` | boolean | Можно ли вернуть | `true` |
| `items[].ga.category` | string | Категория для GA | `"Одежда"` |
| `items[].item_id` | integer | FK → product_sizes.id | `111222` |
| `items[].is_cnc` | boolean | Click & Collect | `false` |
| `items[].can_be_marked` | boolean | Можно ли оценить: `OrderHelper::canBeMarked($order, true)` и позиция не подарок | `true` |
| `items[].experiment` | string\|null | **Новое.** Эксперимент (A/B), с которым товар попал в заказ (`OrderPosition::getExperiment()`) | `null` |

### Блок `track_number`

Весь блок = `null`, если трек-номера нет или ТК — самовывоз из магазина (`PickupHelper::isSelfPickupTkType`).

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `track_number.track_number` | string | Трек-номер | `"777123456789"` |
| `track_number.url` | string\|null | Ссылка на отслеживание | `"https://..."` |

### Блок `summary` (только full=true)

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `summary.total_cost` | string\|false | Сумма товаров | `"2 000 ₽"` |
| `summary.delivery_cost` | string\|false | Стоимость доставки | `"300 ₽"` |
| `summary.discount` | string\|false | Скидка | `"-500 ₽"` |
| `summary.discount_sale` | string\|false | Скидка по акции | `"-400 ₽"` |
| `summary.discount_bonus` | string\|false | Скидка бонусами | `"-100 ₽"` |
| `summary.discount_promo` | string\|false | Скидка промокодом | `"-0 ₽"` |
| `summary.total_payable` | string\|false | К оплате | `"1 800 ₽"` |
| `summary.by_certificate` | string\|false | Сертификатами | `"5 000 ₽"` |

### Блок `delivery` (только full=true)

Массив строк с информацией о доставке: тип ТК (`getTypeTitleMobile()`), дата и интервал, адрес; далее для самовывоза из магазина — «Срок хранения заказа в магазине — {N} дней» (`CommonCartService::SHOP_STORAGE_DAYS`) и часы работы магазина (`worktime`), для остальных — «Транспортная компания: {name}».

### Блок `bonuses` (только full=true)

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `bonuses` | float | Начисленные бонусы | `150.00` |

### Блок `messages[]` (только full=true)

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `messages[].status` | string | Тип сообщения: `can_be_cancelled`, `can_be_payed`, `can_be_returned`, `can_be_marked` (курьер / самовывоз из магазина / ПВЗ — разный текст), `can_be_picked_up` (`OrderMobileTransformer::getMessages()`) | `"can_be_returned"` |
| `messages[].message` | string | Текст сообщения | `"Вы можете вернуть вещи..."` |
| `messages[].button` | string | Текст кнопки (у `can_be_picked_up` — пустая строка) | `"Оформить возврат"` |

> Сообщения `can_be_marked` шлюз (`core` и Go-копия) **вырезает**, если gRPC `feedbacks.Mobile/CanBeSaved` вернул `ok = false` (отзыв уже оставлен / оценить нельзя). Монолит этого не знает и отдаёт их по `OrderHelper::canBeMarked()`.

### Блок `return`

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `return.is_bank_data_required` | boolean | Нужны ли банковские данные | `false` |

---

## Пример успешного ответа

Ответ клиенту после шлюза (у монолита дополнительно `"total": 1`):

```json
{
  "success": true,
  "result": {
    "id": 12345,
    "dolyame_id": null,
    "date": "2026-08-15 14:30:00",
    "status": 14,
    "status_message": "Передан в доставку",
    "expiration_date": {
      "start": 1723733400,
      "end": 1724000000
    },
    "title": "Заказ №12345",
    "items": [
      {
        "id": 67890,
        "article": "ART-12345",
        "model_id": 555,
        "barcode": 111222,
        "title": "Пламя",
        "tags": [{"id": 1, "title": "New"}],
        "colors": [{
          "id": 555,
          "color_id": 12,
          "hash": "#000000",
          "color": "Чёрный",
          "image": "https://cdn.12storeez.com/images/colors/black.jpg",
          "has_circle": true,
          "circle_color": "#FFFFFF"
        }],
        "discount_price": 1200.00,
        "price": 1500.00,
        "preview": "https://cdn.12storeez.com/images/products/555/mobile.jpg",
        "preview_new": [{
          "type": "mobile_order",
          "width": 200,
          "height": 267,
          "url": "https://cdn.12storeez.com/images/products/555/mobile.jpg"
        }],
        "selected_color_id": 12,
        "selected_size_id": "M",
        "count": 1,
        "is_present": false,
        "can_be_returned": true,
        "ga": {"category": "Платья"},
        "item_id": 111222,
        "is_cnc": false,
        "experiment": null,
        "can_be_marked": false
      }
    ],
    "payment": {
      "type_title": "Карта",
      "type_name": "yookassa",
      "type_id": 1,
      "send": {"amount": {"value": "1500", "currency": "RUB"}},
      "total_cost": 2000,
      "cost_sum": 1500.00,
      "delivery_cost": 300,
      "discount": 500,
      "discount_sale": 400,
      "discount_bonus": 0,
      "discount_promo": 100,
      "total_payable": 1500,
      "is_payed": true,
      "by_certificate": 0,
      "payment_system": "yookassa",
      "payment_url": null
    },
    "track_number": {
      "track_number": "777123456789",
      "url": "https://tracking.dpd.ru/track?id=777123456789"
    },
    "recipient": {
      "email": "user@mail.ru",
      "first_name": "Иван",
      "last_name": "Иванов",
      "phone": "+79001234567"
    },
    "is_click_and_collect": false,
    "giftcardsAmount": 0,
    "giftcards": [],
    "delivery": [
      "Доставка курьером",
      "18 августа, 10:00 – 18:00",
      "г. Москва, ул. Пушкина, д. 10, кв. 5",
      "Транспортная компания: ДПД"
    ],
    "summary": {
      "total_cost": "2 000 ₽",
      "delivery_cost": "300 ₽",
      "discount": "-500 ₽",
      "discount_sale": "-400 ₽",
      "discount_bonus": "0 ₽",
      "discount_promo": "-100 ₽",
      "total_payable": "1 800 ₽",
      "by_certificate": "0 ₽"
    },
    "bonuses": 150,
    "messages": [
      {
        "status": "can_be_returned",
        "message": "Вы можете вернуть вещи в течение четырнадцати дней после получения заказа.",
        "button": "Оформить возврат"
      }
    ],
    "return": {
      "is_bank_data_required": false
    }
  }
}
```

## Пример ответа с ошибкой

Заказ не найден у пользователя или это резерв в магазине — монолит отвечает HTTP 404 (`ERROR_CODE_NOT_AVAILABLE = 1009`, `OrdersController.php:549-553`, `ApiBaseController::getError()`):

```json
{
  "success": false,
  "result": {
    "error_code": 1009,
    "error_text": "Заказ 500127505 не найден у пользователя",
    "error_data": []
  }
}
```

> Как именно шлюз `core` переупаковывает ошибку монолита (axios-interceptor esb) — по коду не проверялось. Go-копия отдаёт тело ошибки со статусом монолита и флагом `isErrorFromPHP: true`; ошибка gRPC `CanBeSaved` → HTTP-статус по таблице `core_gateway_grpc_error.go`, без `FEEDBACKS_GRPC_URL` — 503.

---

# Маппинг с БД

## Таблица `orders` (физическое имя: `cms_orders`)

| Поле API | Тип | Поле БД | Тип БД | Описание |
|----------|-----|---------|--------|----------|
| `id` | integer | `id` | int(11) PK AUTO_INCREMENT | ID заказа |
| `dolyame_id` | string | `dolyame_id` | varchar(255) NULL | ID заказа в Dolyame |
| `date` | string | `created_at` | datetime | Дата создания заказа |
| `status` | integer | `status` | int(11) | FK → order_statuses.internal_id |
| `status_message` | string | — | — | FK → order_statuses.client_title |
| `title` | string | — | — | Вычисляется в трансформере: `Заказ №{id}` |
| `recipient.first_name` | string | `name` | varchar(255) NULL | Имя получателя |
| `recipient.last_name` | string | `surname` | varchar(255) NULL | Фамилия получателя |
| `recipient.phone` | string | `number` | varchar(255) NULL | Телефон получателя |
| `recipient.email` | string | `email` | varchar(255) NULL | Email получателя |
| `payment.type_id` | integer | `payment_method` | int(11) NULL | FK → payment_types.internal_id |
| `payment.is_payed` | boolean | `payment_status` | int(11) | FK → payment_statuses.internal_id |
| `payment.payment_url` | string | `payment_url` | varchar(512) NULL | Ссылка на оплату |
| `payment.payment_system` | string | `payment_method` | — | Вычисляется через PaymentSystemEnum |
| `track_number.track_number` | string | `track_number` | varchar(255) NULL | Трек-номер |
| `is_click_and_collect` | boolean | `is_click_and_collect` | tinyint(1) | Самовывоз |
| `giftcardsAmount` | float | — | — | Вычисляется через GiftcardsService |
| `payment.total_cost` | float | — | — | Вычисляется из order_positions |
| `payment.cost_sum` | float | `sum` | decimal(10,2) | Итоговая сумма |
| `payment.delivery_cost` | float | `delivery_price` | decimal(10,2) NULL | Стоимость доставки |
| `payment.total_payable` | float | — | — | sum - giftcardsAmount |
| `bonuses` | float | `given_bonus` | int(11) | Начисленные бонусы |
| `payment.send` | object | `payment_method` | — | Вычисляется из YooKassa-компонента |
| `payment.pay_before` | string | `created_at` | — | Вычисляется: `created_at + PT2H` (PAYMENT_TIME_BEFORE_CANCEL) |
| `expiration_date.start` | integer | `created_at` | datetime | Timestamp создания заказа |
| `expiration_date.end` | integer\|null | `delivery_date` | varchar(255) NULL | Timestamp даты доставки |
| `return.is_bank_data_required` | boolean | `payment_method` | — | Определяется через isCourierPayment() |
| `delivery.date` | string | `delivery_date` | varchar(255) NULL | Дата доставки |
| `delivery.time_from` | string | `delivery_time_from` | varchar(255) NULL | Время доставки с |
| `delivery.time_to` | string | `delivery_time_to` | varchar(255) NULL | Время доставки до |
| `delivery.track_number` | string | `track_number` | varchar(255) NULL | Трек-номер |
| `delivery.type` | string | `delivery_method` | int(11) | FK → delivery_tk.id |

## Таблица `order_positions` (физическое имя: `cms_order_positions`)

| Поле API | Тип | Поле БД | Тип БД | Описание |
|----------|-----|---------|--------|----------|
| `items[].id` | integer | `id` | int(11) PK AUTO_INCREMENT | ID позиции |
| `items[].article` | string | `article` | varchar(255) | Артикул товара |
| `items[].model_id` | integer | `model_id` | int(11) | FK → products.id |
| `items[].barcode` | integer | `barcode` | int(11) | Штрихкод (→ product_sizes.id) |
| `items[].title` | string | `model_title_ru` | varchar(255) | Денормализованное название модели (через `getCurrentModelTitle()`) |
| `items[].discount_price` | float | `price` | decimal(10,2) | Цена со скидкой |
| `items[].price` | float | `price_before_discount` | decimal(10,2) | Цена до скидки |
| `items[].selected_color_id` | integer | `color_id` | int(11) | FK → dictionary_colors.id |
| `items[].selected_size_id` | string | `size_title_ru` | varchar(255) | Денормализованный размер |
| `items[].count` | integer | `quantity` | int(11) | Количество |
| `items[].is_present` | boolean | `is_present` | tinyint(1) | Признак подарка |
| `items[].item_id` | integer | `item_id` | int(11) | FK → product_sizes.id |
| `items[].is_cnc` | boolean | `is_click_and_collect` | tinyint(1) | Click & Collect |
| `items[].colors[0].hash` | string | `color_hash` | varchar(10) | HEX-код цвета |
| `items[].colors[0].color` | string | `color_title_ru` | varchar(255) | Название цвета (RU) |
| `items[].colors[0].image` | string | `color_image` | varchar(512) NULL | URL изображения цвета |
| `items[].colors[0].has_circle` | boolean | `color_has_circle` | tinyint(1) | Есть ли кружок |
| `items[].preview` | string | `image_mobile_url` | varchar(512) | URL изображения (mobile) |
| `items[].preview_new[].url` | string | `image_mobile_url` | varchar(512) | URL изображения |
| `items[].can_be_returned` | boolean | `status` | — | Вычисляется OrderHelper |
| `items[].can_be_marked` | boolean | `status` | — | Вычисляется OrderHelper |
| `items[].ga.category` | string | — | — | Вычисляется Product::getMainCategoryTitleGa() |
| `items[].experiment` | string | — | — | Вычисляется `OrderPosition::getExperiment()` (источник не сверялся) |

## Таблица `order_statuses` (справочник)

| Поле API | Тип | Поле БД | Тип БД | Описание |
|----------|-----|---------|--------|----------|
| `status` (код) | integer | `internal_id` | int(11) | Числовой код статуса |
| `status_message` | string | `client_title` | varchar(255) | Клиентское название |

### Основные статусы

| `internal_id` | Код | Описание |
|----------------|-----|----------|
| 1 | RESERVED | Зарезервирован |
| 3 | WAITING_PROCESSING | Ожидает обработки |
| 4 | PREPARING_PACKAGE | Сборка |
| 7 | WAITING_PAYMENT | Ожидает оплаты |
| 11 | PACKED | Упакован |
| 14 | ITEM_SENT | Передан в доставку |
| 16 | AWAITING_PICKUP_IN_STORE | Ожидает в магазине |
| 17 | ORDER_COMPLETED | Заказ выполнен |
| 23 | ORDER_CANCELLED | Заказ отменён |

## Таблица `payment_statuses` (справочник)

| `internal_id` | Код | Описание |
|----------------|-----|----------|
| 1 | SUCCESS | Оплачен |
| 2 | NOT_PAID | Не оплачен |
| 3 | FAILURE | Ошибка оплаты |
| 4 | CREDIT_APPROVED | Кредит одобрен |

## Таблица `delivery_tk` (транспортные компании)

| Поле API | Тип | Поле БД | Тип БД | Описание |
|----------|-----|---------|--------|----------|
| `delivery.type` | string | `type` | varchar(255) | Тип ТК (courier, box, self, etc.) |

---

# Связанные задачи

| Задача | Описание изменений |
|--------|--------------------|
| | |

---

# Версии документа

| Версия | Дата изменения | Автор | Описание изменений |
|--------|----------------|-------|--------------------|
| 1.0 | 07.09.2026 | Системный аналитик | Первичное создание документа — маппинг эндпоинта открытия заказа (Mobile API) с таблицами БД |
| 1.1 | 07.09.2026 | Системный аналитик | Уточнён реальный маршрут: `GET /api/orders/{id}` |
| 1.2 | 07.09.2026 | Системный аналитик | Уточнено проксирование: `GET /api/orders/{id}` → `GET /mobile/orders/{id}` (шлюз) → route `mobile/orders` (id в query); проверен обработчик |
| 1.3 | 07.09.2026 | Системный аналитик | Исправлен внутренний путь монолита: `GET /mobile/orders/{id}` (по swagger `docs/mobileApi/openapi.yml`, строка 1653, `getOrderById`); пояснена внутренняя маршрутизация Yii2 (UrlRule → route `mobile/orders` + id в query) |
| 1.4 | 07.09.2026 | Системный аналитик | Зафиксировано: `expiration_date` — период «создание → доставка» (НЕ таймер оплаты); реальный дедлайн оплаты — `payment.pay_before` (`created_at + PT2H`, автоотмена через OrderStatusTimer); добавлен маппинг `expiration_date` и `pay_before`; файл перенесён в `requirements/mobile/` |
| 1.5 | 07.09.2026 | Системный аналитик | Зафиксировано: `delivery_date` — плановая дата доставки (НЕ фактическая); окно возврата считается от `end_date` (`end_date + days_can_be_returned > now`), а не от `delivery_date`; поля «фактическая дата получения» в системе нет |
| 1.6 | 07.09.2026 | Системный аналитик | AS-IS (подтверждено разработчиком): `end_date` ≠ `expiration_date.end` (разные поля `orders`); расчёт возврата — `end_date + N дней`; как скрывается кнопка возврата; нюанс курьерка vs ПВЗ |
| 1.7 | 11.09.2026 | Системный аналитик | Файл перенесён в `requirements/reference/api/mobile/` — AS-IS API-контракты по каналам вынесены из бандлов процессов в сквозной справочник |
| 1.8 | 07.11.2026 | Системный аналитик | Сверено: монолит `dd4a997ac0`, Go `631ac38`, esb `4519218b`, iOS `4f321c86`. Шлюз конкретизирован: `core.12stz.com` = esb (`orders.controller.ts:227`) + параллельный gRPC Feedbacks `CanBeSaved` с фильтром `can_be_marked`; ответ клиенту без `total`; добавлена Go-копия `orders_core.go:376` (iOS не вызывает); заголовки разделены на клиент→шлюз (JWT) и шлюз→монолит; исправлены ошибка (404, `1009`), `UrlRule.php:83-84`, `mobile.yml:4982`; добавлены `items[].experiment`, значения `messages[].status`, `track_number = null`, строки самовывоза в `delivery`; список, офлайн-чеки |
