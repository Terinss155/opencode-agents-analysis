# API

> Сверено с `origin/develop` `dd4a997ac0`, 07.11.2026.

## Три генерации API

В системе одновременно работают три поколения API с разными схемами аутентификации и разными
принципами построения ответа. Современное веб-поколение ниже разбито на две строки: почти всё
оно работает на cookie и сессии Yii, JWT — только у `/api/auth/*` и `/api/user/me`.

| Генерация | Префикс URL | Аутентификация | Кто использует |
|---|---|---|---|
| **Партнёрские (легаси)** | `/api/*`, `/api2/*` | Токен в query или Bearer | 1С, RetailCRM, Lamoda, Mercaux, WMS |
| **Web (современная)** | `/api/cart/*`, `/api/v1/*`, `/reservation/*`, `/profile/permissions` | Cookie `_identity` + сессия Yii (как у всего сайта) | Сайт, новый чекаут |
| **Web JWT** | `/api/auth/*`, `/api/user/me` | JWT ES256 (Bearer) | Фронт сайта не вызывает; в шлюзах `mobile-monorepo-go` и `esb-monorepo` вызовов тоже нет — клиент не найден (был SSR, спецификация `docs/ssr/` удалена 16.09.2026) |
| **Mobile** | `/mobile/*`, `/mobile/v2/*` | Ключ приложения + токен сессии | iOS и Android через шлюзы `core` (esb) и `mobile` (Go) |

Отдельно стоят серверные страницы каталога, отдающие как HTML, так и JSON
(`/product/product/*-json`), и админка (`/cms/*`, 126 контроллеров `*BackendController`).

Ещё одна поверхность — API пользователей для внешних систем (`src/User/Controller/UserApiController.php`,
модуль `userApi`): `GET /user/search`, `GET /user/{id}/orders`, `POST /user/create`,
`PATCH /user/{id}` (`config/url.php:142-145`), авторизация — `modules\api2\auth\HttpBearerAuth`
(токен интеграции, не JWT). Клиент API в коде не виден (ECOMDEV-1966, 1994, 2007).

## Маршрутизация

Правила описаны в `config/url.php` (351 строка). Порядок правил важен — срабатывает первое
совпадение. Помимо обычных правил используются кастомные классы `UrlRule`
(подключены в `config/url.php:253-262`):

| Класс | Файл | Что обслуживает |
|---|---|---|
| `Application\Auth\Rule\UrlRule` | `src/Auth/Rule/UrlRule.php` | `/api/auth/*` |
| `Application\User\Rule\UrlRule` | `src/User/Rule/UrlRule.php` | `/api/user/me` |
| `Application\User\Notifications\Rule\UrlRule` | `src/User/Notifications/Rule/UrlRule.php` | `/api/v1/notifications/*` |
| `Application\Modules\Mobile\Rules\UrlRule` | `src/Modules/Mobile/Rules/UrlRule.php` | REST-пути mobile v1 с ID в URL |
| `modules\mobilev2\rules\UrlRule` | `modules/mobilev2/rules/UrlRule.php` | REST-пути mobile v2 |
| `modules\product\rules\UrlRule` | `modules/product/rules/UrlRule.php` | SEO-адреса каталога |
| `modules\content\rules\UrlRule` | `modules/content/rules/UrlRule.php` | Статические страницы |

В конце файла стоят общие правила `<module>/<controller>/<action>` (`config/url.php:344-346`),
которые перехватывают всё несовпавшее.

Платёжный вебхук Yandex — контроллер из `controllerMap` в `config/web.php` (`yandex-notification`),
маршруты `yandex/notification/v1/webhook` и устаревший `yandex-split/notification/v1/webhook`
(`config/url.php:348-349`, стоят после общих правил).

Для AJAX-запросов сайта действует ещё одно поколение маршрутов — «+json»: при AJAX
`modules/common/controllers/AbstractRestController.php` вызывает `action…Json` вместо
`action…` на том же URL. Сводка по всем AJAX-вызовам фронта —
`knowledge/architecture/web-call-chain.html`.

### Особенность mobile v2

Префикс `/mobile/v2/` обслуживают **два модуля одновременно**:

- `modules/mobilev2/` — основной трафик, работает через общее правило;
- `src/Modules/MobileV2/` (id модуля `mobile-v2`) — новые эндпоинты по явным правилам
  (`config/url.php:248-249`, `:268-277`: лукбуки, настройки, YooKassa, смена способа оплаты,
  лендинги, гео пользователя, `mobile/v2/products/category`, `PUT mobile/v2/cart`).

В `modules/mobilev2/` после ECOMDEV-2228 удалены `CategoryController` и `StoresController`.

Куда попадёт запрос, определяет порядок правил. Подробнее — [09-pitfalls.md](09-pitfalls.md).

## Аутентификация

### Сайт: cookie и сессия Yii

Ранее здесь было написано, что сайт защищён JWT, — это неверно. Пользователя сайта монолит
узнаёт по cookie `_identity` (`enableAutoLogin`, `httpOnly => false`, `config/web.php:105-111`)
и стандартной PHP-сессии Yii (компонент `session` не переопределён). Гостевая корзина — cookie
`sessionId`. Проверка CSRF и подпись cookie выключены глобально
(`enableCookieValidation`/`enableCsrfValidation => false`, `config/web.php:97-98`).

Так работают и страничные контроллеры, и REST `/api/cart/*` (`src/Modules/Cart/Controllers/*`
проверяют `Yii::$app->user->isGuest`), и `/api/v1/notifications/*`, `/checkout`,
`/profile/permissions`, `POST /reservation` — вход требуют через `AuthRequiredBehavior`
(`src/Modules/Common/Behavior/AuthRequiredBehavior.php`) или проверку `isGuest`.

### JWT: `/api/auth/*` и `/api/user/me`

Реализация на `lcobucci/jwt`, алгоритм ES256.

- Ключи читаются из переменных окружения `JWT_PRIVATE_KEY` и `JWT_PUBLIC_KEY` (в base64).
  Каталог `jwt_keys/` в репозитории **не используется кодом** (при этом `jwt_keys/jwtRS256.key`
  отслеживается git — ключ стоит считать скомпрометированным).
- `src/Auth/Service/JwtService.php` выдаёт access- и refresh-токены.
- Refresh-токены хранятся в таблице `jwt_refresh_token`, отозванные access-токены —
  в Redis-denylist с префиксом `jwt:deny:` (`JwtService.php:282-284`).
- Фильтр `JwtHttpBearerAuthMethod` подключён **только** к двум контроллерам:
  `src/Auth/Controller/AuthController.php:75` (для `login`, `login-by-email`, `refresh`,
  `send-code` он необязателен) и `src/User/Controller/UserController.php:48` (`/api/user/me`).
  `login-by-email` дополнительно логинит пользователя в сессию Yii через `LoginForm`.

Публичные эндпоинты: `send-code`, `login`, `login-by-email`, `refresh`.
Защищённые JWT: `logout`, `/api/user/me`. Корзина, уведомления и чекаут JWT **не** используют.

Мобильные шлюзы (`core`, `mobile`) выдают приложению свои JWT, но в монолит передают
`x-session-token` (см. ниже) — JWT монолита они не используют.

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
учётных данных). Вход: `POST /mobile/user/auth`, `/mobile/user/auth-phone`, а также
`/mobile/user/auth-phone-code` (`UserController::actionAuthPhoneCode`,
`src/Modules/Mobile/Controllers/UserController.php:349`) — копия входа по коду для Go-шлюза
`mobile` (ECOMDEV-2342); коды отправляются через `src/Auth/Client/MindboxPhoneCodeClient.php`
(HTTP-клиент Mindbox, не gRPC). iOS пока ходит через старый шлюз `core`, где вход по SMS
идёт в Mindbox напрямую, мимо монолита.

Ключ приложения сверяется с `MOBILE_API_KEY` в `ApiBaseController.php:376` и
`BaseController.php:431`. Есть список заблокированных устройств — переменная
`MOBILE_DEVICE_ID_BAN_LIST` (`config/config.php:180`).

### Партнёрские интеграции: токены

Токены хранятся в модели `modules/api/models/Token`. В `api` v1 передаются query-параметром
`?token=`, в `api2` — либо query-параметром, либо Bearer-заголовком
(`modules/api2/auth/HttpBearerAuth.php`).

### Сводка по гостевому доступу

| Поверхность | Гость | Авторизованный |
|---|---|---|
| Каталог сайта (JSON) | доступен | добавляется персонализация |
| `/api/cart/*` | корзина по cookie `sessionId` | сессия Yii (`_identity`) добавляет данные пользователя; часть методов (`delivery-city`) требует входа |
| `/reservation/*` | `cart`, `expiration`, `instructions` | `POST /reservation` — только с входом |
| `/api/auth/*` | вход, отправка кода, refresh | logout и `/api/user/me` по JWT |
| Mobile | гостевая сессия | сессия с привязанным пользователем |
| `/api/*`, `/api2/*`, `/user/search` и др. API пользователей | только по валидному токену интеграции | — |

## Эндпоинты

### Аутентификация и пользователь

| Метод и путь | Обработчик | Назначение |
|---|---|---|
| `POST /api/auth/send-code` | `AuthController::actionSendCode` | Отправка SMS-кода (капча + rate limit) |
| `POST /api/auth/login` | `AuthController::actionLogin` | Вход по телефону и коду |
| `POST /api/auth/login-by-email` | `AuthController::actionLoginByEmail` | Вход по email и паролю |
| `POST /api/auth/refresh` | `AuthController::actionRefresh` | Обновление токенов |
| `POST /api/auth/logout` | `AuthController::actionLogout` | Отзыв access-токена |
| `GET /api/user/me` | `UserController::actionMe` | Профиль текущего пользователя (JWT) |
| `GET /profile/permissions` | `src/User/Controller/ProfileController.php:79` (`userApi/profile/permissions`, `config/url.php:23`) | Права текущего пользователя сайта, нужен вход (ECOMDEV-2182) |
| `GET /user/search`, `GET /user/{id}/orders`, `POST /user/create`, `PATCH /user/{id}` | `src/User/Controller/UserApiController.php:80`, `:110`, `:137`, `:167` | API пользователей для внешних систем, Bearer-токен интеграции |
| `GET`/`PUT` `/mobile/user/last-context` | `Mobile\UserController::actionLastContext` (`UserController.php:929`, методы — `:123-124`, нужен вход) | Последний раздел каталога из приложения (ECOMDEV-2248), общий `LastContextService`; также отдаётся полем `last_context` в профиле `/mobile/user` |
| `POST /mobile/user/auth-phone-code` | `Mobile\UserController::actionAuthPhoneCode` (`UserController.php:349`) | Вход по SMS-коду для Go-шлюза (ECOMDEV-2342) |
| `POST /home/last-context` | `src/Modules/Mainpage/Controllers/MainpageController.php:168` (`config/url.php:15`) | Последний раздел каталога с сайта: `female`/`male`/`home` → `LastContextService`, профиль и cookie `lastContext` |

### Корзина — сайт

Контроллеры в `src/Modules/Cart/Controllers/`, маршруты — `config/url.php:292-310`. Сейчас
эти методы вызывает только редизайн корзины (`/cart?redesign=12stz`, только админам); основная
корзина сайта работает через MCA-маршруты `/cart/cart/*` (`modules/cart/controllers/CartController.php`).

| Метод и путь | Обработчик |
|---|---|
| `GET /api/cart/info` | `CartApiController::actionGetInfo` |
| `GET /api/cart/items` | `CartApiController::actionGetItems` |
| `PATCH /api/cart/items` | `CartApiController::actionUpdateItem` |
| `DELETE /api/cart/items` | `CartApiController::actionDeleteItem` |
| `GET`/`POST` `/api/cart/user-info` | `CartApiController::actionGetUserInfo` / `actionSaveUserInfo` |
| `POST /api/cart/move-unavailable-to-favourites` | `CartApiController::actionMoveUnavailableToFavourites` (через общее правило `api/cart/<action>`, `config/url.php:310`) |
| `GET`/`POST` `/api/cart/delivery` | `CartDeliveryController::actionDelivery` / `actionSaveDelivery` |
| `GET /api/cart/delivery-list` | `CartDeliveryController::actionDeliveryList` |
| `GET`/`POST` `/api/cart/delivery-city` | `CartDeliveryController::actionCity` / `actionSaveCity` |
| `GET /api/cart/delivery-address` | `CartDeliveryController::actionAddress` |
| `GET`/`POST` `/api/cart/delivery/pvz` | `CartDeliveryController::actionGetDeliveryPvz` / `actionSavePvz` |
| `GET /api/cart/delivery/pickup-points` | `CartDeliveryController::actionGetList` |
| `POST /api/cart/delivery/pickup-point` | `CartDeliveryController::actionSavePickupPoint` (путь в единственном числе, `config/url.php:309`) |
| `GET /api/cart/payment` | `CartPaymentController::actionIndex` |
| `GET /carts/main/count`, `GET /cart/ids` | `Cart\CartController::actionCount` / `actionIds` |
| `POST /cart/subscription/check` | `CartSubscriptionController::actionCheck` (`config/url.php:176`) |

### Корзина — сайт, старый стек (MCA)

`modules/cart/controllers/CartController.php`, вызывается из `frontend/src/modules/cart/ancient/api/cart.js`.
Промокод: `POST /cart/cart/add-promo` принимает `code` и `delete_bonuses`
(`CartController.php:479`); если промокод несовместим с программой лояльности, отвечает ошибкой
`20171` (`ResponseErrorCode::CART_PROMO_CODE_LOYALITY_PROGRAM_ERROR`,
`PromoCodeLoyalityProgramException`), и фронт предлагает применить его со снятием бонусов.
Признак спецпромокода — `isSpecialPromo`/`bonusBlocked` в данных корзины
(`AbstractCartService.php:1251-1252`, ECOMDEV-2377/2379); в мобильном API —
`is_special_promo`, там же `delete_bonuses` принимает `POST /mobile/cart-discount/promo-code`. Остальные
методы (`add-item`, `remove-item`, `update-items`, `add-bonus`, `delete-bonus`, `send-cart-list`
и др.) перечислены в `web-call-chain.html`.

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
| `POST /mobile/cart/subscription/check` | `CartController::actionSubscriptionCheck` (`config/url.php:338`) |
| `POST /mobile/cart-delivery/update-delivery-from-list` | `CartDeliveryController::actionUpdateDeliveryFromList` (`config/url.php:320`) |

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
| `GET /mobile/products/last-search` | `Mobile\ProductsController::actionLastSearch` (без id) |
| `GET /mobile/products/recommendations` | `Mobile\ProductsController::actionRecommendations` (корзина и «спасибо за заказ», `?is_thank_you_page=1`) |
| `GET /mobile/products/{id}/store-availability` | `Mobile\ProductsController::actionStoreAvailability` (через `Mobile\Rules\UrlRule`; вход не обязателен) |
| `GET /mobile/v1/products/{id}/recommendations` | `Mobile\ProductsController::actionProductRecommendations` (`config/url.php:247`) |
| `GET /mobile/v1/products/{id}/complete-set` | `Mobile\ProductsController::actionCompleteSet` (`config/url.php:251`) |
| `GET /product/product/{id}/store-availability` | `ProductV2\ProductController::actionStoreAvailability` (`src/Modules/Product/Controller/ProductController.php:271`, `config/url.php:213`) — веб-аналог, ECOMDEV-1497; фронт пока не вызывает |
| `GET /product/product/product-cities/{id}` | `ProductV2\ProductController::actionProductCitiesJson` (`ProductController.php:256`, `config/url.php:214`) — перенесён из `modules/product` в `productV2` (`ProductCitiesOp`) |

`Mobile\Rules\UrlRule` до сих пор разбирает пути `/mobile/products/{id}`, `/products/stocks/{id}`,
`/fashion/{id}`, `/accompaniments/{id}`, `/last-view/{id}` в маршруты `mobile/products`,
`mobile/products/stocks` и т.д., но в `src/Modules/Mobile/Controllers/ProductsController.php`
таких действий нет — эти URL дают 404 (аналоги живут в `mobilev2\ProductsController`:
`actionStocks`, `actionFashion`, `actionAccompaniments`, `actionLastView`).
| `GET /mobile/v2/products/{id}` | `mobilev2\ProductsController::actionIndex` |
| `GET /mobile/category/list` | `Mobile\CategoryController::actionList` |
| `GET /mobile/catalog/filter` | `Mobile\CatalogController::actionFilter` |
| `GET /mobile/v2/lookbooks` | `MobileV2\LookbookController::actionList` |
| ~~`GET /mobile/v2/category/list`, `/mobile/category/collections/{id}`~~ | удалены в ECOMDEV-2228 |

### Доставка и гео

| Метод и путь | Обработчик |
|---|---|
| `GET /api/v1/delivery/geo/cities` | `DeliveryV2\GeoController::actionCities` |
| `GET /api/v1/delivery/geo/countries/{iso}/addresses` | `GeoController::actionSuggestAddress` |
| `GET /api/v1/delivery/pickup/provider/{id}/points` | `PickupController::actionPointListJson` |
| `GET /mobile/delivery` | `Mobile\DeliveryController::actionIndex` |
| ~~`GET /mobile/delivery/intervals`~~ | удалён в ECOMDEV-2180 |
| `POST /mobile/v2/geo/confirmation` | `MobileV2\UserGeoController::actionConfirmation` |

### Бронирование в магазине

| Метод и путь | Обработчик |
|---|---|
| `POST /reservation/cart` | `src/Modules/Reservation/Controller/ReservationController.php:106` (ECOMDEV-2195) |
| `GET /reservation/expiration` | `ReservationController.php:158` (ECOMDEV-2197) |
| `GET /reservation/instructions` | `ReservationController.php:193` (ECOMDEV-2207) |
| `POST /reservation` | `ReservationController.php:204` — создание брони, нужен вход (ECOMDEV-2222, 2533) |
| `POST /mobile/reservation/cart`, `POST /mobile/reservation`, `GET /mobile/reservation[/{id}]` | `Mobile\ReservationController::actionCreateCart` / `actionOrder` / `actionList` / `actionItem` (`config/url.php:280-284`); `expiration`, `instructions` — через общее правило |

Веб-маршруты брони (`config/url.php:285-288`, модуль `reservation`) фронт сайта пока не вызывает.

### Удалённые эндпоинты (октябрь 2026)

Удалены из кода и из `docs/openapi/mobile.yml`:

| Задача | Эндпоинты |
|---|---|
| ECOMDEV-2228 | v1: `/mobile/category/collections/{id}`, `/mobile/metadata/colors`, `/mobile/metadata/tags`, `/mobile/home/banners`, `/mobile/virtual-card`; v2: `/mobile/v2/category/list`, `/mobile/v2/home/banners` (и старый `/api/metadata/banners2`), `/mobile/v2/stores`, `/mobile/v2/stores/cities` |
| ECOMDEV-2180 | `/mobile/delivery/intervals`, `/mobile/delivery/taxes`, `/mobile/cities`, `/mobile/cities/suggest`, `/mobile/cities/geocode`, `/mobile/geo/suggest`, `/mobile/geo/geocode`, `/mobile/payment/yandex`; на сайте — `/delivery/delivery/tax` |

`GET /mobile/category/list` (`Mobile\CategoryController::actionList`) и `GET /mobile/cities/ip`
остались.

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
| `GET /user/search`, `GET /user/{id}/orders`, `POST /user/create`, `PATCH /user/{id}` | `src/User/Controller/UserApiController.php` (Bearer `HttpBearerAuth`, `:69`) | Поиск, заказы, создание и изменение пользователя для внешних систем; любимые категории и размеры кэшируются в Redis-группе `UserSearch` (`UserFavoritesCacheService`); коды ошибок `20600`–`20604` |

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
{ "success": false, "result": { "error_code": 1001, "error_text": "...", "error_data": [] } }
```

(Исправлено 17.11.2026 по `ApiBaseController::getError()`: ответ с ошибкой содержит `success: false` и `error_data`; HTTP — по `error_code`, см. `skill/openapi-spec/references/errors.md`, раздел 1.1.)

Новые веб-контроллеры (наследники `FrontendApiBaseController`: `/api/auth/*`, `/api/user/me`,
`/reservation/*`, `/profile/permissions` и др.) — через `FrontendApiResponseService`
(успех и ошибка — разные наборы полей, ключ называется `status`, а не `success`):

```json
{ "status": "success", "message": "", "data": {} }
```

При ошибке:

```json
{ "status": "error", "message": "", "code": "50000", "errors": [] }
```

Дополнительно сервис добавляет заголовки `X-Response-Id`, `X-Response-Version`, `X-Language`
к каждому ответу (`src/Http/Response/Service/FrontendApiResponseService.php:196-198`).
Старые AJAX-методы «+json» отвечают через `AbstractRestController` и любое исключение
превращают в `success: true` с HTTP 200 (`modules/common/controllers/AbstractRestController.php:76-85`). Часть веб-методов (`Api2/OrdersController`, в т.ч. методы возврата) собирает ответ
массивом в контроллере, без этого сервиса и с HTTP 200 при ошибке. Правила оформления контрактов и реестры
кодов ошибок — `skill/openapi-spec/references/` (`web.md`, `mobile.md`, `errors.md`, `swagger.md`).

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
| `docs/openapi/mobile.yml` | `https://12storeez.com/mobile` | 159 | 187 | 187 | Mobile v1 и v2 (удалённые в ECOMDEV-2228/2180 эндпоинты убраны) |
| `docs/openapi/frontend.yml` | `https://12storeez.com/` | 409 | 423 | 352 | Web: авторизация, корзина, каталог, ЛК, бронирование |
| ~~`docs/ssr/openapi.yml`~~ (удалён 16.09.2026) | `https://12storeez.com/ssr/api/` | 21 | 21 | 5 | Авторизация, вишлист, меню |

Числа на `dd4a997ac0` посчитаны по строкам YAML (пути — ключи второго уровня в `paths`,
операции — ключи `get`/`post`/`put`/`patch`/`delete`). У `frontend.yml` часть операций не
имеет `operationId` — на подсчёт покрытия это не влияет. Рядом лежат собранные `mobile.html` и
`frontend.html`, их пересобирают вместе с YAML.

Покрытие проверяется в CI скриптом `openapi-coverage.php` (job `openapi_coverage` в
`.gitlab-ci.yml`, только в MR) по грубой логике:

- числитель — количество **путей** (ключей `paths`, не операций) во всех файлах `docs/**/*.yml`;
- знаменатель — количество методов `public function action…(` во всех `*Controller.php` внутри
  каталогов `controllers/`/`Controller/` в `modules/` и `src/`; пропускаются
  `*BackendController.php`, абстрактные классы и консольные контроллеры (`yii\console\Controller`);
- сопоставления конкретного action с конкретным путём нет, сравниваются только общие числа.

**Порог — 100%** (`OPENAPI_COVERAGE_MIN_PERSENTAGE: 100`, `.gitlab-ci.yml:36`; по умолчанию в
самом скрипте — 80). `allow_failure` у job нет, поэтому новый action без нового пути в
спецификации может уронить MR-пайплайн.

## Вебхуки и входящие интеграции

### HTTP-вебхуки

| Метод и путь | Обработчик | Источник |
|---|---|---|
| `POST /yandex/notification/v1/webhook` (и устаревший `/yandex-split/notification/v1/webhook`) | `Integration\Payment\Yandex\Controller\NotificationController` | Yandex Pay / Split |
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

Сгенерированы, но в коде не используются: `Orders\OnlineClient` (`ByClient`),
`Feedbacks\NPSClient`, `Feedbacks\StoreClient`.

**Направление только исходящее** — монолит выступает клиентом микросервисов, gRPC-сервер
он не поднимает.

С ECOMDEV-2342 часть мобильной работы с Mindbox (коды входа для Go-шлюза, устройства) идёт не
через gRPC, а через HTTP-клиент `src/Integration/Mindbox/Client/MindboxMobileClient.php`
(Guzzle) и `src/Auth/Client/MindboxPhoneCodeClient.php`. Общий выключатель интеграции —
параметр `Parameters::MINDBOX_INTEGRATION_ENABLED` (миграция
`m261011_120000_add_mindbox_integration_enabled_parameter.php`), читается
`src/Modules/Mindbox/Service/MindboxIntegrationToggleService.php:32`.

Особенность автозагрузки: в `composer.json` каталог `modules/grpc/` подключён как PSR-4
с пустым префиксом (`"": "modules/grpc/"`), из-за чего сгенерированные классы попадают
в корень пространства имён.

## Экспорт фидов

Фиды формируются только из консоли и сохраняются файлами. Полный список получателей —
в [03-business-domains.md](03-business-domains.md), раздел «Фиды».
