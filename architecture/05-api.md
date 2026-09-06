# API

## Три генерации API

В системе одновременно работают три поколения API с разными схемами аутентификации и разными
принципами построения ответа.

| Генерация | Префикс URL | Аутентификация | Кто использует |
|---|---|---|---|
| **Партнёрские (легаси)** | `/api/*`, `/api2/*` | Токен в query или Bearer | 1С, RetailCRM, Lamoda, Mercaux, WMS |
| **Web (современная)** | `/api/auth/*`, `/api/cart/*`, `/api/v1/*` | JWT ES256 | Сайт, новый чекаут |
| **Mobile** | `/mobile/*`, `/mobile/v2/*` | Ключ приложения + токен сессии | iOS и Android |

Отдельно стоят серверные страницы каталога, отдающие как HTML, так и JSON
(`/product/product/*-json`), и админка (`/cms/*`, 127 контроллеров `*BackendController`).

## Маршрутизация

Правила описаны в `config/url.php` (336 строк). Порядок правил важен — срабатывает первое
совпадение. Помимо обычных правил используются кастомные классы `UrlRule`:

| Класс | Файл | Что обслуживает |
|---|---|---|
| `Application\Auth\Rule\UrlRule` | `src/Auth/Rule/UrlRule.php` | `/api/auth/*` |
| `Application\User\Rule\UrlRule` | `src/User/Rule/UrlRule.php` | `/api/user/me` |
| `Application\User\Notifications\Rule\UrlRule` | `src/User/Notifications/Rule/UrlRule.php` | `/api/v1/notifications/*` |
| `Application\Modules\Mobile\Rules\UrlRule` | `src/Modules/Mobile/Rules/UrlRule.php` | REST-пути mobile v1 с ID в URL |
| `modules\mobilev2\rules\UrlRule` | `modules/mobilev2/rules/UrlRule.php` | REST-пути mobile v2 |
| `modules\product\rules\UrlRule` | `modules/product/rules/UrlRule.php` | SEO-адреса каталога |
| `modules\content\rules\UrlRule` | `modules/content/rules/UrlRule.php` | Статические страницы |

В конце файла стоят общие правила `<module>/<controller>/<action>`, которые перехватывают всё
несовпавшее.

Платёжный вебхук Yandex зарегистрирован отдельно через `controllerMap` в `config/web.php`:
`POST /yandex/notification/v1/webhook`.

### Особенность mobile v2

Префикс `/mobile/v2/` обслуживают **два модуля одновременно**:

- `modules/mobilev2/` — основной трафик, работает через общее правило;
- `src/Modules/MobileV2/` — новые эндпоинты по явным правилам (лукбуки, настройки, YooKassa,
  смена способа оплаты, лендинги, гео пользователя).

Куда попадёт запрос, определяет порядок правил. Подробнее — [09-pitfalls.md](09-pitfalls.md).

## Аутентификация

### Web: JWT

Реализация на `lcobucci/jwt`, алгоритм ES256.

- Ключи читаются из переменных окружения `JWT_PRIVATE_KEY` и `JWT_PUBLIC_KEY` (в base64).
  Каталог `jwt_keys/` в репозитории **не используется кодом**.
- `src/Auth/Service/JwtService.php` выдаёт access- и refresh-токены.
- Refresh-токены хранятся в таблице `jwt_refresh_token`, отозванные access-токены —
  в Redis-denylist с префиксом `jwt:deny:`.
- Фильтр `JwtHttpBearerAuthMethod` подключается к контроллерам; для эндпоинтов входа он
  необязателен.

Публичные эндпоинты: `send-code`, `login`, `login-by-email`, `refresh`.
Защищённые: `logout`, `/api/user/me`, `/api/cart/*`, уведомления, чекаут.

### Mobile: ключ приложения плюс сессия

Все мобильные контроллеры наследуют `ApiBaseController` / `BaseController` и требуют заголовки:

| Заголовок | Назначение |
|---|---|
| `x-access-token` | Ключ приложения, сверяется с `MOBILE_API_KEY` |
| `x-session-token` | Сессия (гостевая или пользовательская), таблица `users_mobile_sessions` |
| `x-platform` | Платформа |
| `x-version` | Версия приложения |

Отдельное свойство `isAuthRequired` в контроллере определяет, нужен ли действию привязанный
к сессии пользователь.

Создание сессии: `PUT /mobile/user/session` (гостевая), `PUT /mobile/user/token` (обмен
учётных данных). Вход: `POST /mobile/user/auth`, `/mobile/user/auth-phone`.

Есть список заблокированных устройств — переменная `MOBILE_DEVICE_ID_BAN_LIST`.

### Партнёрские интеграции: токены

Токены хранятся в модели `modules/api/models/Token`. В `api` v1 передаются query-параметром
`?token=`, в `api2` — либо query-параметром, либо Bearer-заголовком
(`modules/api2/auth/HttpBearerAuth.php`).

### Сводка по гостевому доступу

| Поверхность | Гость | Авторизованный |
|---|---|---|
| Каталог сайта (JSON) | доступен | добавляется персонализация |
| `/api/cart/*` | корзина по сессии | JWT добавляет данные пользователя |
| `/api/auth/*` | вход, отправка кода, refresh | logout и защищённые ресурсы |
| Mobile | гостевая сессия | сессия с привязанным пользователем |
| `/api/*`, `/api2/*` | только по валидному токену интеграции | — |

## Эндпоинты

### Аутентификация и пользователь

| Метод и путь | Обработчик | Назначение |
|---|---|---|
| `POST /api/auth/send-code` | `AuthController::actionSendCode` | Отправка SMS-кода (капча + rate limit) |
| `POST /api/auth/login` | `AuthController::actionLogin` | Вход по телефону и коду |
| `POST /api/auth/login-by-email` | `AuthController::actionLoginByEmail` | Вход по email и паролю |
| `POST /api/auth/refresh` | `AuthController::actionRefresh` | Обновление токенов |
| `POST /api/auth/logout` | `AuthController::actionLogout` | Отзыв access-токена |
| `GET /api/user/me` | `UserController::actionMe` | Профиль текущего пользователя |

### Корзина — сайт

Контроллеры в `src/Modules/Cart/Controllers/`.

| Метод и путь | Обработчик |
|---|---|
| `GET /api/cart/info` | `CartApiController::actionGetInfo` |
| `GET /api/cart/items` | `CartApiController::actionGetItems` |
| `PATCH /api/cart/items` | `CartApiController::actionUpdateItem` |
| `DELETE /api/cart/items` | `CartApiController::actionDeleteItem` |
| `GET`/`POST` `/api/cart/user-info` | `CartApiController::actionGetUserInfo` / `actionSaveUserInfo` |
| `POST /api/cart/move-unavailable-to-favourites` | `CartApiController::actionMoveUnavailableToFavourites` |
| `GET`/`POST` `/api/cart/delivery` | `CartDeliveryController::actionDelivery` / `actionSaveDelivery` |
| `GET /api/cart/delivery-list` | `CartDeliveryController::actionDeliveryList` |
| `GET`/`POST` `/api/cart/delivery-city` | `CartDeliveryController::actionCity` / `actionSaveCity` |
| `GET`/`POST` `/api/cart/delivery/pvz` | `CartDeliveryController::actionGetDeliveryPvz` / `actionSavePvz` |
| `GET`/`POST` `/api/cart/delivery/pickup-points` | `CartDeliveryController::actionGetList` / `actionSavePickupPoint` |
| `GET /api/cart/payment` | `CartPaymentController::actionIndex` |
| `GET /carts/main/count` | `CartController::actionCount` |

### Корзина — mobile v1

Контроллеры в `src/Modules/Mobile/Controllers/`.

| Метод и путь | Обработчик |
|---|---|
| `GET`/`PUT` `/mobile/cart` | `CartController::actionIndex` |
| `GET /mobile/cart/info` | `CartDetailsController::actionInfo` |
| `GET`/`PATCH`/`DELETE` `/mobile/cart/items` | `CartDetailsController::actionItems` |
| `PATCH`/`DELETE` `/mobile/cart/<barcode>` | `CartController::actionUpdate` (не `/mobile/cart` — там только `actionIndex` на GET/PUT) |
| `POST /mobile/cart/apply-order-settings` | `CartDetailsController::actionApplyOrderSettings` |
| `GET`/`POST` `/mobile/cart-delivery/*` | `CartDeliveryController` |
| `GET`/`POST` `/mobile/cart-payment/*` | `CartPaymentController` |
| `GET`/`POST`/`DELETE` `/mobile/cart-giftcard/*` | `CartGiftcardController` |
| `POST`/`DELETE` `/mobile/cart-discount/promo-code` | `CartDiscountController::actionPromoCode` (не `PUT`) |
| `GET`/`POST` `/mobile/cart-discount/bonuses` | `CartDiscountController::actionBonuses` (не `PUT`/`DELETE` — DELETE не реализован) |
| `POST /mobile/cart/payment` | `CartController::actionPayment` |

### Заказы

| Метод и путь | Обработчик |
|---|---|
| `POST /order/proceed-new` | `modules/orders/.../OrdersController::actionProceedNew` |
| `GET /order/payment/<hash>` | `OrdersController::actionPayment` |
| `GET`/`POST` `/mobile/orders` | `Mobile\OrdersController::actionIndex` |
| `GET /mobile/orders/{id}` | `Mobile\OrdersController` (через `UrlRule`) |
| `POST /mobile/orders/cancel` | `Mobile\OrdersController::actionCancel` |
| `POST /mobile/orders/return-positions` | `Mobile\OrdersController::actionReturnPositions` (id — query-параметром, метод POST, не GET) |
| `POST /mobile/orders/{id}/return-details` | `Mobile\OrdersController::actionReturnDetails` |
| `GET /api/orders/{id}/return-method-list` | `Application\Modules\Api2\Controller\OrdersController::actionReturnMethodList` (модуль `api2_new`, не легаси `api2`) |
| `PATCH /api/orders/{id}/change-payment-method` | `Payment\Controller\ChangePaymentController` (только `PATCH`; GET списка типов оплаты — отдельный эндпоинт `GET /api/payment-types`) |
| `PATCH /mobile/v2/orders/{id}/change-payment-method` | `MobileV2\Controllers\ChangePaymentController` (только `PATCH`; GET — `GET /mobile/v2/payment-types`) |

### Каталог и товары

| Метод и путь | Обработчик |
|---|---|
| `GET /catalog/{слаги}` | `ProductController::actionIndex` (через `UrlRule`) |
| `GET /product/product/index-json` | `ProductController::actionIndexJson` |
| `GET /product/product/count` | `ProductController::actionCountJson` (URL без `-json`, метод — с) |
| `GET /catalog/{slug1}/{slug2}/{slug3}` | `ProductController::actionView` (карточка товара по SEO-адресу, не `/product/product/view`) |
| `GET /catalog/search` | `ProductController::actionSearchProduct` |
| `GET /catalog/suggest` | `ProductController::actionSuggestJson` |
| `GET /catalog/all-fashion-json` | `ProductController::actionAllFashionJson` (URL резолвится в action-id `all-fashion`, который формально не совпадает с именем метода — см. [09-pitfalls.md](09-pitfalls.md)) |
| `GET /product/product/recommendations` | `ProductV2\ProductController::actionRecommendations` |
| `GET /api/v1/get-url-by-article/{article}` | `ProductV2\ProductController::actionGetUrlByArticle` |
| `GET /mobile/products/{id}/last-search`, `/fashion/{id}`, `/stocks/{id}`, `/accompaniments/{id}`, `/last-view/{id}` | `Mobile\ProductsController` — методы `actionLastSearch`, `actionRecommendations`, `actionStoreAvailability`, `actionProductRecommendations`, `actionCompleteSet` (у контроллера **нет** `actionIndex`, поэтому голого `GET /mobile/products/{id}` не существует) |
| `GET /mobile/v1/products/{id}/recommendations` | `Mobile\ProductsController::actionProductRecommendations` |
| `GET /mobile/v2/products/{id}` | `mobilev2\ProductsController::actionIndex` |
| `GET /mobile/category/list` | `Mobile\CategoryController::actionList` |
| `GET /mobile/catalog/filter` | `Mobile\CatalogController::actionFilter` |
| `GET /mobile/v2/lookbooks` | `MobileV2\LookbookController::actionList` |

### Доставка и гео

| Метод и путь | Обработчик |
|---|---|
| `GET /api/v1/delivery/geo/cities` | `DeliveryV2\GeoController::actionCities` |
| `GET /api/v1/delivery/geo/countries/{iso}/addresses` | `GeoController::actionSuggestAddress` |
| `GET /api/v1/delivery/pickup/provider/{id}/points` | `PickupController::actionPointListJson` |
| `GET /mobile/delivery` | `Mobile\DeliveryController::actionIndex` |
| `GET /mobile/delivery/intervals` | `Mobile\DeliveryController::actionIntervals` |
| `POST /mobile/v2/geo/confirmation` | `MobileV2\UserGeoController::actionConfirmation` |

### Партнёрские API

| Метод и путь | Обработчик | Назначение |
|---|---|---|
| `GET`/`POST` `/api/clients` | `api\ClientsController` | Пользователи для RCRM |
| `GET`/`POST`/`PATCH`/`DELETE` `/api/products/{id}` | `api\ProductsController` | Синхронизация товаров |
| `GET`/`POST` `/api/orders` | `api\OrdersController` | Синхронизация заказов |
| `GET /api/orders/a-payments/{begin}/{end}` | `api\OrdersController::actionPayments` | Выгрузка платежей |
| `GET /api2/healthcheck/ping` | `HealthcheckController::actionPing` | Проверка живости |
| `GET /api2/products/items` | `api2\ProductsController::actionItems` | Товары для партнёров |
| `POST /api2/orders/create` | `api2\OrdersController::actionCreate` | Создание заказа (Lamoda) |
| `POST /api2/orders/order-update` | `api2\OrdersController::actionOrderUpdate` | Обновление от WMS |
| `POST /api2/orders/status` | `api2\OrdersController::actionStatus` | Смена статуса |
| `GET /api2/stocks` | `api2\StocksController::actionIndex` | Снимок остатков |
| `POST /api2/stocks/esb` | `Application\Modules\Api2\Controller\StocksController::actionEsb` (роутится на `api2_new`, а не легаси `modules/api2`) | Приём остатков из ESB |
| `POST /api2/popmechanic/contact` | `PopmechanicController::actionContact` | Контакт в CRM |

В `api` v1 действуют два стиля маршрутов: `api/<controller>/a-<action>` и REST-варианты.

## Формирование ответа

Единого сериализатора для публичного API нет. Ответ собирают **экстракторы** и **трансформеры**.

Экстракторы реализуют `ExtractorInterface` и превращают модели в массивы. Под каждый канал —
свой экстрактор:

| Экстрактор | Назначение |
|---|---|
| `ProductItemFullDtoExtractor` | Полная карточка товара |
| `ProductFullMobileV2Extractor` | Карточка для mobile v2 |
| `ProductListMobileV2Extractor` | Список товаров для mobile v2 |
| `ProductListMobileV1Extractor` | Список для mobile v1 |
| `ProductListApi2Extractor` | Список для партнёров |
| `AddressMobileV2Extractor` | Адреса пользователя |

Трансформеры используются в новых модулях: `src/Modules/Cart/Transformer/`,
`src/Auth/Transformer/`, `src/Modules/MobileV2/Transformer/`.

### Форматы обёртки

Mobile v1 — через `ApiBaseController::answer()`:

```json
{ "success": true, "total": 10, "result": [] }
```

При ошибке:

```json
{ "result": { "error_code": 1001, "error_text": "..." } }
```

Web JWT — через `FrontendApiResponseService` (успех и ошибка — разные наборы полей, ключ
называется `status`, а не `success`):

```json
{ "status": "success", "message": "", "data": {} }
```

При ошибке:

```json
{ "status": "error", "message": "", "code": "SERVER_ERROR", "errors": [] }
```

Дополнительно сервис добавляет заголовки `X-Response-Id`, `X-Response-Version`, `X-Language`
к каждому ответу.

**Следствие:** один и тот же товар отдаётся в разных формах для сайта, mobile v1, mobile v2
и партнёров. Добавляя поле, нужно решить, в каких экстракторах оно должно появиться.

## Валидация

| Инструмент | Где применяется |
|---|---|
| Symfony Validator | DTO в модулях Cart, Feedback, вебхуки 1С и доставки — через `DtoValidator` |
| Opis JsonSchema | Схемы параметров CMS (`ParameterSchemaValidator`), обмен товарами (`ExchangeSchemaValidator`) |
| Валидаторы Yii и кастомные | Авторизация (`RequestLoginValidator`), правила полей в `ApiBaseController` |
| MobileV2 | `AppVersionValidator` и исключения корзины |

Symfony Serializer используется ограниченно — для разбора входящих вебхуков и в консольных
обработчиках платежей, но не для формирования публичных ответов.

## Контракты и документация

Спецификации OpenAPI:

| Файл | База | Путей | Операций | `operationId` | Область |
|---|---|---|---|---|---|
| `docs/mobileApi/openapi.yml` | `https://12storeez.com/mobile` | 113 | 138 | 138 | Mobile v1 и v2 |
| `docs/frontend/openapi.yml` | `https://12storeez.com/` | 144 | 152 | 114 | Web: авторизация, корзина, каталог |
| `docs/ssr/openapi.yml` | `https://12storeez.com/ssr/api/` | 21 | 21 | 5 | Авторизация, вишлист, меню |

У `frontend` и `ssr` спецификаций часть операций не имеет `operationId` — на подсчёт покрытия
это не влияет, так как проверка ниже вообще не использует `operationId`.

Покрытие проверяется в CI скриптом `openapi-coverage.php` по более грубой логике:
он суммирует количество методов `action*(` во всех файлах `*Controller.php` внутри
`controllers/`-подобных каталогов `modules/**` и `src/**` (исключая только `*BackendController.php`,
абстрактные классы не считаются отдельно) и делит на суммарное число HTTP-операций
(`get`/`post`/`put`/`patch`/`delete`) во **всех** файлах `docs/**/openapi.yml` — сопоставления
конкретного action с конкретной операцией нет, сравниваются только общие числа.
**Минимальный порог — 50%** (`OPENAPI_COVERAGE_MIN_PERSENTAGE`).

## Вебхуки и входящие интеграции

### HTTP-вебхуки

| Метод и путь | Обработчик | Источник |
|---|---|---|
| `POST /yandex/notification/v1/webhook` | `Integration\Payment\Yandex\Controller\NotificationController` | Yandex Pay / Split |
| `POST /payment/alpha-podeli/notification` | `modules/payment/controllers/AlphaPodeliController::actionNotification` | Alpha Podeli |
| `POST /api/onec/webhooks/change-balance` | `OneC\WebhooksController::actionChangeBalance` | 1С, баланс сертификата |
| `POST /api/onec/webhooks/change-status` | `OneC\WebhooksController::actionChangeStatus` | 1С, статусы |
| `POST /api/onec/webhooks/not-web-purchase` | `OneC\WebhooksController::actionNotWebPurchase` | 1С, офлайн-покупка |
| `POST /api/onec/webhooks/change-owner` | `OneC\WebhooksController::actionChangeOwner` | 1С, смена владельца сертификата |
| `POST /api/v1/delivery/webhooks/city-carriers-coverage` | `DeliveryV2\WebhooksController` | Логистика |
| `POST /api2/orders/status` | `api2\OrdersController::actionStatus` | WMS / RCRM |
| `POST /api2/orders/notification-from-lamoda` | `api2\OrdersController::actionNotificationFromLamoda` | Lamoda |

### Консольные консьюмеры

| Обработчик | Назначение |
|---|---|
| `src/Integration/Payment/Yandex*/Console/NotificationController.php` | Уведомления Yandex Pay / Split / SBP |
| `src/Modules/Payment/Console/NotificationController.php` | Обработка платёжного outbox |
| `src/Modules/Order/Controller/RabbitInboxTransactionController.php` | Входящие изменения заказов |
| `src/Modules/Notifications/Console/NotificationsController.php` | Отправка уведомлений |

## gRPC

`modules/grpc/` содержит сгенерированные PHP-клиенты (файлы `.proto` в репозитории не хранятся).
Клиенты регистрируются в DI, адреса и ключи берутся из параметров.

| Сервис | Клиент | Методы | Где используется |
|---|---|---|---|
| Mindbox | `Mindbox\MobileClient` | InitDevice, InitClient, RemoveDevice, Code, CheckCode, EditUser, IsUserExist, PushClick | `MindboxGrpcService` — мобильная авторизация и push |
| Mindbox | `Mindbox\UserClient` | Info, Orders, SendOSMICard | `MindboxUserService` — программа лояльности |
| Feedbacks | `Feedbacks\MobileClient` | App, Store, Order, Categories, ReasonsByOrder, ReasonsByStore, CanBeSaved | `FeedbackGRPCService` |
| Feedbacks | `Feedbacks\PortalFeedbackServiceClient` | Delete, List, Validate | Админка отзывов |
| Orders | `Orders\OfflineClient` | ByClient, GetById | `OrderGRPCService` — офлайн-заказы |

**Направление только исходящее** — монолит выступает клиентом микросервисов, gRPC-сервер
он не поднимает.

Особенность автозагрузки: в `composer.json` каталог `modules/grpc/` подключён как PSR-4
с пустым префиксом (`"": "modules/grpc/"`), из-за чего сгенерированные классы попадают
в корень пространства имён.

## Экспорт фидов

Фиды формируются только из консоли и сохраняются файлами. Полный список получателей —
в [03-business-domains.md](03-business-domains.md), раздел «Фиды».
