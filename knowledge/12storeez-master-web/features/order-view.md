# Справочник: просмотр заказа — где что искать

> **Назначение:** быстрая навигация по кодовой базе для задач «просмотр заказа» (Mobile API и Web API).
> **Правило:** НЕ искать по всем файлам — сначала этот справочник, затем точечно открывать указанные файлы.
> **Сверено с `origin/develop` `dd4a997ac0`, 07.11.2026:** обновлены номера строк (`UrlRule.php`, `docs/openapi/mobile.yml` — файл перестроен, `config/url.php`, `config/web.php`, `config/config.php`, `UserOrderPositionExtractor.php`, `OrderPosition.php`, `DeliveryTk.php`, `Order.php`); добавлен канал «История онлайн-заказов по API» (раздел 2.4). Цепочки вызовов мобильного и веб-просмотра не изменились.

---

# 0. Главное правило взаимодействия (запомнить!)

| Канал | Путь | Через API Gateway? |
|-------|------|--------------------|
| **Mobile App** | `GET /api/orders/{id}` → **через API Gateway** → `GET /mobile/orders/{id}` (монолит) | ✅ **ДА** |
| **Web (сайт)** | `GET /profile/view/{id}` → **напрямую в монолит** | ❌ **НЕТ** |

- **Мобилка** ходит через внешний API Gateway (шлюз вне репозитория). Шлюз проксирует `/api/orders/{id}` на внутренний путь монолита `/mobile/orders/{id}`.
- **Веб-сайт** НЕ использует API Gateway: браузер обращается напрямую к монолиту по маршруту `/profile/view/{id}` (Yii2 UrlManager).

---

# 1. Mobile API — список файлов

## 1.1. Цепочка вызовов (2 сетевых + 1 внутренняя маршрутизация)

```
GET /api/orders/{id}            ← Mobile App → API Gateway (сеть, шлюз вне репозитория)
        ↓ проксирование
GET /mobile/orders/{id}         ← API Gateway → Monolith (сеть)
        ↓ UrlRule::parseRequest()  ← ВНУТРИ монолита (НЕ сеть!)
route: mobile/orders, id={id} (query)
        ↓ dispatch
OrdersController::actionIndex() → getOrders($user, Yii::$app->request->get('id'))
        ↓
OrderMobileTransformer::transformForMobile($order) → JSON
```

## 1.2. Файлы Mobile

| Что | Файл | Где именно |
|-----|------|------------|
| Контроллер (обработчик) | `src/Modules/Mobile/Controllers/OrdersController.php` | `actionIndex()` — строка **200**; чтение `id` из query — строка **209** (`Yii::$app->request->get('id')`); `getOrders()` — строка **544** (сверено 09.10.2026; без изменений на `dd4a997ac0`) |
| Правило маршрутизации | `src/Modules/Mobile/Rules/UrlRule.php` | строка **83-84**: regex `/orders\/\d+/` → route `mobile/orders` + `['id' => ...]` |
| Трансформер ответа | `src/Modules/Order/Transformer/OrderMobileTransformer.php` | `transformForMobile($order, full=true)` |
| Репозиторий | `src/Modules/Order/Repository/OrderRepository.php` | `findOneByIdAndUserId($orderId, $userId)` |
| Базовый контроллер Mobile | `src/Modules/Mobile/Controllers/ApiBaseController.php` | авторизация, ответы |
| **Swagger (источник правды по путям)** | `docs/openapi/mobile.yml` | строка **4982** (сверено 07.11.2026, `dd4a997ac0`): `GET /mobile/orders/{orderId}` (`operationId: getOrderById` — строка 4986) — просмотр заказа; строка **4858**: `GET /mobile/orders` — список; параметр `orderId` — строка **9378** |

## 1.3. Аутентификация Mobile

| Параметр | Где |
|----------|-----|
| `x-access-token` | Header, API-ключ приложения (swagger `securitySchemes.MobileApiKey`, строка 9387) |
| `x-session-token` | Header, токен сессии (swagger `securitySchemes.SessionToken`, строка 9392) |

---

# 2. Web API — список файлов

## 2.1. Цепочка вызовов (прямая, БЕЗ gateway)

```
GET /profile/view/{id}          ← Browser → Monolith (напрямую, НЕ через gateway)
        ↓ Yii2 UrlManager (config/url.php)
route: users/profile/view, id={id}
        ↓ dispatch
ProfileController::actionView($id)
        ↓
OrderProfileService::getOrderStatusData($id)
        ↓
UserOrderExtractor::extract($orderDto) → server-side HTML (render 'base')
```

## 2.2. Файлы Web

| Что | Файл | Где именно |
|-----|------|------------|
| Маршрут | `config/url.php` | строка **25**: `/profile/<action>/<id:\d+>` → `users/profile/<action>` |
| Контроллер (обработчик) | `modules/users/controllers/ProfileController.php` | `actionView($id)` — строка **496**; проверка `$order->user_id != Yii::$app->user->id` — строка **504**; `render('base', ...)` — строка **537**; behaviors (auth/access) — строка **203** |
| Сервис | `modules/orders/services/OrderProfileService.php` | `getOrderStatusData($id)` — строка **28**; `getOrderStatusDataByHash($hash)` — строка **35** |
| Экстрактор заказа | `modules/users/extractors/UserOrderExtractor.php` | `extract()` — строка **42**; поля: status/positions/recipient/delivery/payment/cost |
| Экстрактор позиций | `modules/users/extractors/UserOrderPositionExtractor.php` | `extract($object, bool $appendExperimentQueryParam = true)` — строка **28**; поля positions[]; к ссылке на товар добавляется `?experiment=<вариант>` из `cms_order_positions.experiment` (АБ-тест ECOMDEV-1821, строки 80-82) |
| DTO платежа | `modules/orders/dto/OrderPaymentDataDto.php` | поля totalCost, deliveryCost, discount, totalPayable, returnCost |
| Поведение авторизации | `src/Modules/Common/Behavior/AuthRequiredBehavior.php` | `checkAuth()` — строка **70**: `Yii::$app->user->isGuest` → редирект на login (MODE_REDIRECT) |
| Конфиг аутентификации | `config/web.php` | строка **105-111**: `enableAutoLogin => true`, `identityCookie.name = _identity`, `loginUrl = users/users/login` |

## 2.3. Аутентификация Web (ВАЖНО!)

| Параметр | Где |
|----------|-----|
| Cookie `_identity` | Yii2 auto-login (`config/web.php:105-111`), **НЕ JWT Bearer** |
| Поведение при отсутствии сессии | редирект на `users/users/login` (`AuthRequiredBehavior`, MODE_REDIRECT) |

## 2.4. История онлайн-заказов по API (новое на `dd4a997ac0`)

| Что | Файл | Где именно |
|-----|------|------------|
| Маршрут | `GET /user/<user_id>/orders` | `src/User/Controller/UserApiController.php`, `actionOrders()`; аутентификация `HttpBearerAuth` (`modules/api2/auth`), не cookie |
| Операция | `src/User/Operation/UserOrdersOp.php` | вызывает `OnlineOrderHistoryService` |
| Сервис | `src/Modules/Order/Services/OnlineOrderHistoryService.php` | `getHistory($userId, $cursor, $limit)` — курсорная пагинация по `created_at`; клиентские названия статусов — `OrderStatusRepository::getClientTitlesByInternalIds()` |
| Репозиторий | `src/Modules/Order/Repository/OrderRepository.php` | `getOnlineHistoryByUserId()` |
| DTO | `src/Modules/Order/Dto/OnlineOrderDto.php`, `OnlineOrderPositionDto.php`, `OnlineOrderHistoryPageDto.php` | формат ответа |

Это серверный API для внешних систем (рядом — `user/search`, `user/create` «из Modern Retail»), а не канал просмотра заказа клиентом. Данные ecommerce для веба вынесены из `modules/orders/controllers/OrdersController.php` в `src/Modules/Order/Services/OrderEcommerceDataService.php` (также используется в `ReservationOrderWebResponseTransformer`).

> ⚠️ **Не путать:** JWT-настройки в `config/config.php` (строки 200-208) относятся к API/mobile-контексту, НЕ к Web-сайту.

---

# 3. Таблицы БД (префикс `cms_` из `.env.example:191`)

| Таблица | Модель | tableName() |
|---------|--------|-------------|
| `cms_orders` | `modules/orders/models/Order.php` | `{{%orders}}` (строка 466) |
| `cms_order_positions` | `modules/orders/models/OrderPosition.php` | `{{%order_positions}}` (строка 256) |
| `cms_orders_history` | `modules/orders/models/OrderHistory.php` | `{{%orders_history}}` (строка 125) |
| `cms_order_statuses` | `modules/statuses/models/OrderStatus.php` | `{{%order_statuses}}` (строка 39) |
| `cms_payment_statuses` | `modules/statuses/models/PaymentStatus.php` | `{{%payment_statuses}}` (строка 26) |
| `cms_delivery_tk` | `modules/delivery/models/DeliveryTk.php` | `{{%delivery_tk}}` (строка 248) |

---

# 4. Ключевые факты и исправления (чтобы не искать заново)

| # | Факт | Подробности |
|---|------|-------------|
| 1 | **Mobile: путь в swagger — `/mobile/orders/{orderId}`, а НЕ `/orders/{orderId}`** | `docs/openapi/mobile.yml:4982` (`getOrderById`). Пути `/orders/{orderId}/...` в swagger есть только для return-details (строка 5042) и return-method-list (строка 5069) |
| 2 | **`mobile/orders (id в query)` — это НЕ третий сетевой вызов** | Это внутренняя маршрутизация Yii2: `UrlRule::parseRequest()` извлекает `id` из pathInfo и кладёт в query-параметры, затем диспатчит на `actionIndex()` |
| 3 | **Web НЕ ходит через API Gateway** | `GET /profile/view/{id}` → напрямую в монолит (`config/url.php:25`). Gateway участвует только в Mobile-канале |
| 4 | **Web-аутентификация — cookie `_identity`, НЕ JWT Bearer** | `config/web.php:105-111` (enableAutoLogin, identityCookie). `AuthRequiredBehavior` проверяет `isGuest` |
| 5 | **Web `payment.type` — string (название метода оплаты), НЕ integer** | `OrderGetterTrait::getPaymentMethod()` (строка 1205) возвращает `?string` из маппинга `paymentMethods`; при `NOT_DEFINED` блок `payment` удаляется из ответа |
| 6 | **`modules/api/controllers/OrdersController::view()` — легаси** | Контроллер для интеграций RCRM/1С, выбрасывает `ForbiddenHttpException`, **НЕ** обслуживает мобильный просмотр заказа |
| 7 | **Web `payment_method` (прочее поле) — integer FK** | `Order::getPaymentTypeId()` (`modules/orders/models/Order.php:2724`; в новой модели — `OrderGetterTrait.php:657`) → `?int` (поле `payment_method`) |
| 8 | **Web `delivery.type` — string** | `DeliveryTk::getDeliveryType()` (строка 447) → `$this->deliveryTypes[$this->type] ?? ''` |
| 9 | **Web `status.steps[]` — из `cms_orders_history`** | `OrderHistory::getByOrderId()` + `Order::getStatusTitle()` + формат `j M` |
| 10 | **Web `positions[].is_returned`** | `(bool) $object->positionStatusRelation?->cancel_status` (UserOrderPositionExtractor:59) |
| 11 | **Банковские реквизиты: разная логика Web vs Mobile** | Web `need_bank_details` = `!in_array(payment_method, ALL_ONLINE_PAYMENT_METHODS)` (все не-онлайн, считается в `RefundController::actionGetPositionsJson` при открытии попапа возврата); Mobile `return.is_bank_data_required` = `isCourierPayment()` (только типы 3/5, приходит сразу в ответе заказа). Подробно: `reference/api/web/order-view_web.md` (раздел «Банковские реквизиты») + `reference/api/web/order-refund-get-positions_web.md` |
| 12 | **`expiration_date` — НЕ таймер оплаты** | Это период «создание → доставка» (`start` = `created_at`, `end` = `delivery_date`). Реальный дедлайн оплаты — `payment.pay_before` = `created_at + PT2H` (автоотмена через `OrderStatusTimer`) |
| 13 | **`delivery_date` — ПЛАНОВАЯ дата, НЕ фактическая** | Ставится при оформлении (выбор клиента) или из 1С; при получении товара не обновляется. Поля «фактическая дата получения» в системе нет |
| 14 | **Окно возврата считается от `end_date`, НЕ от `delivery_date`** | `canBeReturned = (isCompleted \|\| isReturned) && strtotime(end_date + "N days") > time()`, `N = Parameter::valueOf('days_can_be_returned')` (в БД, в UI = 14). Когда `end_date + N <= now` → кнопка возврата скрыта (mobile: нет сообщения `can_be_returned`; web: `show_refund_button = false`). Нюанс: для курьерки выбор даты мягче (в пределах 14 дней), для ПВЗ — точный расчёт от `end_date` |
| 15 | **`end_date` ≠ `expiration_date.end`** | `expiration_date.end` = `delivery_date` (плановая дата доставки, для отображения периода); `end_date` = дата выполнения заказа (фактическая, с подтверждением 1С, ставится один раз при статусе «выполнен»). Это разные поля таблицы `orders` |

---

# 5. Артефакты аналитики (документы)

| Документ | Содержимое |
|----------|------------|
| `requirements/reference/api/mobile/order-view_mobile.md` | Полный маппинг Mobile API: `GET /api/orders/{id}` → `GET /mobile/orders/{id}` → route `mobile/orders` |
| `requirements/reference/api/web/order-view_web.md` | Полный маппинг Web API: `GET /profile/view/{id}` → `ProfileController::actionView()` (без gateway) |
| `requirements/reference/api/web/order-refund-get-positions_web.md` | Полный маппинг Web API: `GET /orders/refund/get-positions?id={id}` → `RefundController::actionGetPositionsJson()` (позиции для возврата, причины, `need_bank_details`) |

---

# 6. Быстрый чек-лист при новой задаче «просмотр заказа»

1. Определи канал: **Mobile** (через gateway) или **Web** (напрямую)?
2. Mobile → открой `docs/openapi/mobile.yml` (путь), `OrdersController.php` (логика), `OrderMobileTransformer.php` (формат ответа).
3. Web → открой `config/url.php` (маршрут), `ProfileController.php` (логика), `UserOrderExtractor.php` + `UserOrderPositionExtractor.php` (формат ответа).
4. Таблицы БД → раздел 3 этого справочника.
5. Сверься с ключевыми фактами (раздел 4) — там собраны все ранее найденные «грабли».