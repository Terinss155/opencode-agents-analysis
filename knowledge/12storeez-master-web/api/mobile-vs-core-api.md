# Исследование: Mobile API и Core API — архитектура и кодовая база

**Дата:** 2026-09-09 (актуализировано 2026-11-07)
**Цель:** Определить, где живут Mobile API и Core API, какие спеки присутствуют в проекте, и как они связаны.

> Сверено 07.11.2026: монолит `dd4a997ac0`, Go `631ac38`, esb `4519218b`, iOS `4f321c86`.
>
> **Главная поправка относительно версии 09.2026:** `core` — это **не микросервис, который вызывает монолит**, а **старый мобильный шлюз (BFF)** `esb-monorepo` (NestJS, хост `core.12stz.com/api`), который стоит **перед** монолитом: МП ходит в `core`, `core` проксирует в монолит (`mobile/...`, `mobilev2/...`, `api2/...`) и в gRPC-сервисы. Рядом работает **новый шлюз** `mobile-monorepo-go` (Go, `mobile.12stz.com/api`). С ноября 2026 в Go есть копии почти всех ручек `core`, но iOS их ещё не вызывает (см. §4.1).

---

## 1. OpenAPI-спеки в репозитории

В репозитории `12storeez-master/` присутствуют **3 OpenAPI-спеки** (hand-written YAML, без автогенерации из PHP-кода):

| # | Спека | Файл | Потребитель | Base URL | Эндпоинтов |
|---|---|---|---|---|---|
| 1 | **Mobile API** | `docs/openapi/mobile.yml` (до 16.09.2026 — `docs/mobileApi/openapi.yml`) | Шлюзы `core`/`mobile`, через них — iOS/Android | `/mobile` | **159 путей / 187 операций** на `dd4a997ac0` (09.2026 — 113) |
| 2 | **Frontend (Web)** | `docs/openapi/frontend.yml` (до 16.09.2026 — `docs/frontend/openapi.yml`) | Браузерный сайт | `/` | **409 путей / 352 `operationId`** на `dd4a997ac0` (09.2026 — 144) |
| 3 | **SSR** | ~~`docs/ssr/openapi.yml`~~ — удалён 16.09.2026 (коммит `79806a5167`) | SSR-фронтенд | `/ssr/api/` | **21** |

**Все три спеки обслуживаются одним монолитом** (Yii2-приложение), различаются только URL-префиксами.

### Spецификация Mobile API — серверы

```yaml
servers:
  - url: https://12storeez.com/mobile        # prod
  - url: https://staging.12stz.tech/mobile    # staging
  - url: https://{devname}.12stz.tech/mobile  # dev (devname = dev/env/fix/mobiledev/sandbox/var)
```

### Spецификация Frontend — серверы

```yaml
servers:
  - url: https://12storeez.com/               # prod
  - url: https://staging.12stz.tech/           # staging
  - url: https://{devname}.12stz.tech/         # dev
```

### Spецификация SSR — серверы

```yaml
servers:
  - url: https://12storeez.com/ssr/api/        # prod
  - url: https://staging.12stz.tech/ssr/api/   # staging
  - url: https://{devname}.12stz.tech/ssr/api/ # dev
```

---

## 2. Core API — старый мобильный шлюз (`esb-monorepo`)

**Спека `core.12stz.dev` В ЭТОМ РЕПОЗИТОРИИ ОТСУТСТВУЕТ.** Core API — это шлюз-прокси (BFF) из репозитория `12stz/esb-monorepo` (NestJS 8 / Nx, приложение `apps/mobile-api`, глобальный префикс `api`, Swagger — `/swagger`). Prod — `core.12stz.com/api`, dev — `core.12stz.dev/api`. Собственной БД и бизнес-логики нет: контроллеры проксируют запросы МП в монолит (`PHP_BASE_URL` + `mobile/...`, `mobilev2/...`, `api2/...`) или вызывают gRPC (orders, feedbacks, mindbox, geo, meta). Шлюз **сворачивается**: в октябре 2026 удалена часть ручек (ECOMDEV-2180, 2189, 2230), функционал переносится в Go-шлюз (§4.1).

### Доказательства

В коде монолита есть только **ссылки** на core:

| Файл | Ссылка | Тип |
|---|---|---|
| `modules/mobilev2/controllers/DeliveryController.php:83` | `@swagger-mobile https://core.12stz.dev/swagger/#/Cart/Delivery2Controller_getDelivery2` | PHPDoc аннотация |
| `src/Modules/Mobile/Controllers/CartController.php:402` | `@swagger-mobile https://core.12stz.dev/swagger/#/Cart/DeliveryController_selectDelivery` | PHPDoc аннотация |
| `src/Modules/MobileV2/Controllers/LookbookController.php:71` | `@swagger-mobile https://core.12stz.dev/swagger/#/Metadata/StoriesV2Controller_getAll` | PHPDoc аннотация |
| `src/Modules/MobileV2/Controllers/LookbookController.php:127` | `@swagger-mobile https://core.12stz.dev/swagger/#/Metadata/StoriesV2Controller_getById` | PHPDoc аннотация |
| `src/Modules/Mobile/Controllers/LookbooksController.php:43` | `@swagger-mobile https://core.12stz.dev/swagger/#/Metadata/StoriesController_getAll` | PHPDoc аннотация |
| `modules/cms/console/EnrichWarehouses.php:14` | `@link https://core.12stz.com/swagger/#/Metadata%23stores/StoresController_getCitiesListWithStores` | PHPDoc @link |
| `modules/feedback/controllers/ReviewShopController.php:19` | `ESB_HOST_PROD = 'https://internal.core.12stz.com'` (dev — `ESB_HOST_DEV = 'https://rest-srv-go.12stz.dev'`, `:20`) | PHP-константа |

> **Как читать `@swagger-mobile`:** это ссылка на метод шлюза `core`, который **проксирует в данный метод монолита** (МП → `core` → монолит), а не вызов `core` из монолита. Единственный найденный вызов монолит → ESB — `ReviewShopController` (`internal.core.12stz.com`). Ручки `cart/delivery`, `cart/delivery2` и `metadata/stories/v2` в esb на `4519218b` на месте и имеют Go-копии; `GET metadata/stories` (список, `StoriesController_getAll`) из esb удалён (ECOMDEV-2189).

---

## 3. Сравнение: что есть, чего нет

### Mobile API

| Домен | В коде | В спеке | Статус |
|---|---|---|---|
| `mobile.12storeez.com` | Нет (0 совпадений) | ❌ Нет | Не используется. **Исправлено:** в `servers` спеки — `12storeez.com/mobile`, `staging.12stz.tech/mobile`, `{devname}.12stz.tech/mobile` (`mobile.yml:3-7`) |
| `mobile.12stz.com` | Нет (0 совпадений) | ❌ Нет | Prod-хост **нового Go-шлюза** `mobile-monorepo-go` (`.deploy/helm/prod.values.yaml:4`), в iOS — `BASE_URL_NEW` |
| `mobile.12stz.dev` | Нет (0 совпадений) | ❌ Нет | Dev-хост Go-шлюза (iOS Debug/Internal), не nginx-алиас монолита |
| `mobile.12stz.tech` | Нет (0 совпадений) | ❌ Нет | В спеке не найден (там `staging.12stz.tech/mobile`) |

### Core API

| Домен | В коде | В спеке | Статус |
|---|---|---|---|
| `core.12stz.dev` | 5 совпадений (аннотации) | ❌ Нет | Только PHPDoc-ссылки; dev-хост шлюза esb (iOS Debug/Internal `BASE_URL`) |
| `core.12stz.com` | 1 совпадение (аннотация) | ❌ Нет | Только PHPDoc-ссылка; prod-хост шлюза esb (iOS Release `BASE_URL`) |
| `internal.core.12stz.com` | 1 совпадение (константа) + упоминание в `frontend.yml:2982` | ❌ Нет | URL для ESB-вызовов из монолита (`ReviewShopController`) |
| `core.12storeez.com` | 0 совпадений | ❌ Нет | Не используется |

---

## 4. Архитектура: как всё связано

> Схема версии 09.2026 («МП → Istio/Nginx `mobile.12stz.dev` → монолит → core-микросервис») **неверна** и заменена.

```
┌──────────────────────────────┐
│ Мобильное приложение (iOS)   │
│ RequestTarget    → BASE_URL  │
│ RequestTargetNew → BASE_URL_NEW
└───────┬──────────────┬───────┘
        │ HTTPS, Bearer JWT
        ▼              ▼
┌────────────────┐  ┌─────────────────────────┐
│ core.12stz.com │  │ mobile.12stz.com        │
│ /api/...       │  │ /api/v1/..., /api/v2/...│
│ esb-monorepo   │  │ mobile-monorepo-go      │
│ (NestJS, BFF,  │  │ (Go/Fiber, BFF;         │
│  сворачивается)│  │  копии ручек core)      │
└──┬──────────┬──┘  └──┬───────────────┬──────┘
   │ HTTP     │ gRPC   │ HTTP          │ gRPC
   │          ▼        │               ▼
   │   orders, feedbacks, mindbox, geo, meta,
   │   logistics, auth (ESB-микросервисы)
   ▼                   ▼
┌───────────────────────────────────────────┐
│ Yii2 Монолит 12storeez-master-web         │
│  /mobile/*, /mobilev2/*, /mobile-v2/* → Mobile (v1/v2)
│  /api2/* (напр. api2/products/items)      │
│  /api/*  → Api2 (api2_new) — сайт/интеграции
│  Модули: Mobile (v1) — 34 файла,          │
│          MobileV2 (v2) — 14 + 11 файлов   │
│  Заголовки от шлюза: x-access-token,      │
│  x-session-token (из JWT), x-version      │
└───────────────────────────────────────────┘
```

### Поток запросов

1. **Мобильное приложение** → `core.12stz.com/api/...` (старый шлюз `esb-monorepo`) **или** `mobile.12stz.com/api/v1|v2/...` (новый шлюз `mobile-monorepo-go`) — какой хост, решает протокол endpoint в iOS (`RequestTarget` / `RequestTargetNew`).
2. **Шлюз** проверяет JWT, подставляет `x-access-token` (ключ API монолита) и `x-session-token` (из JWT) и **проксирует** в монолит (`mobile/...`, `mobilev2/...`, `api2/...`) либо вызывает gRPC-сервис.
3. **Монолит** обрабатывает запрос в модулях Mobile / MobileV2 и отвечает `{success, total?, result}`; шлюз может склеить ответ с gRPC (например, `orders/{id}` + Feedbacks `CanBeSaved`) и перепаковать обёртку.
4. **Swagger шлюзов** живёт в их репозиториях: `core.12stz.dev/swagger/` (esb), `/swagger/*` Go-шлюза (`docs/mobile_api/swagger.yaml`).

### Примеры: что шлюз `core` проксирует в монолит (по аннотациям `@swagger-mobile`)

| Ручка `core` (esb) | Куда в монолите | Обработчик в монолите | Статус на `4519218b` / копия в Go |
|---|---|---|---|
| `GET cart/delivery2` (`Delivery2Controller.getDelivery2`) | `POST mobile/v2/delivery` | `DeliveryController` (mobilev2, `:83`) | есть / `GET /api/v1/old-cart/delivery2` (`old_cart.go:304`) |
| `POST cart/delivery` (`DeliveryController.selectDelivery`) | `mobile/cart/delivery` | `CartController` (mobile, `:402`) | есть / `/api/v1/old-cart/delivery` (`old_cart.go:260`) |
| `GET metadata/stories` (`StoriesController.getAll`) | `mobile/lookbooks` | `LookbooksController` (mobile, `:43`) | **удалён** (ECOMDEV-2189) |
| `GET metadata/stories/v2[/:id]` (`StoriesV2Controller.getAll / getById`) | `mobile/v2/lookbooks[/{id}]` | `LookbookController` (MobileV2, `:71`, `:127`) | есть / `/api/v1/metadata/stories/v2[/:id]` (`metadata_core.go:381`, `:422`) |

### 4.1. Два шлюза: перенос ручек `core` в Go (ноябрь 2026)

В `mobile-monorepo-go` (`631ac38`) появились копии почти всех оставшихся ручек `core`. Путь копии = путь `core` под префиксом `/api/v1` (сегмент `v2` в пути убран), числовые параметры — `regex(^\d+$)`; в монолит копии ходят через `helpers.ProxyToSiteAsIs` по `SITE_BASE_INTERNAL_URL`, обёртки ответов повторяют NestJS (`helpers/core_gateway_compat.go`). Хендлеры — `internal/app/service/*_core.go`, `old_cart.go`, `cart_boxberry.go`, `catalog.go`.

| Домен (задача) | `core` → Go | Хендлер Go |
|---|---|---|
| Авторизация (ECOMDEV-2342) | `authorization/*` → `/api/v1/auth/*` | `auth.go` |
| Старая корзина (2361) | `cart/{barcode}`, `cart/clean`, `cart/check-items`, `cart/payment`, `cart/delivery`, `cart/delivery2` → `/api/v1/old-cart/*`; `cart/delivery2/boxberry[/{id}]` → `/api/v1/cart/delivery/boxberry[/{id}]`; `PUT orders` (создание заказа старым чекаутом) → `PUT /api/v1/old-cart/order` | `old_cart.go`, `cart_boxberry.go`, `orders_core.go:169` |
| Каталог, гео, метаданные (2409) | `catalog/filter`, `metadata/{stores*, sizes-table, faq*, sizes, social, stories/v2*}` | `catalog.go:45`, `metadata_core.go` |
| Уведомления, заказы (2422) | `notification/{message,info,user-activities}`; `orders` GET/DELETE, `orders/{id}`, `orders/offline[/{id}]`, `orders/dolyame-id/{id}`, `orders/{id}/return`, `orders/v2/return-reasons` → `/api/v1/orders/return-reasons` | `notification_core.go`, `orders_core.go` (`{id}` — `:376`, список — `:69`) |
| Товары (2438) | `products/v2/*` → `/api/v1/products/*` | `product_core.go` |
| Отзывы, лендинги, веблинки (2480) | `reviews/*`, `landings/v2/{id}` → `/api/v1/landings/{id}`, `v2/ulink` → `/api/v1/ulink` | `reviews_core.go`, `landings_core.go:43`, `ulink_core.go:57` |

- **iOS (`4f321c86`) эти копии пока не вызывает** — по-прежнему ходит в `core.12stz.com`. Копии заказов и отзывов требуют `ORDERS_GRPC_URL` / `FEEDBACKS_GRPC_URL` / `SITE_API2_PRODUCTS_TOKEN` (только Vault; без них — 503).
- **Параллельно esb удалил ручки** (ECOMDEV-2180 — `locations/*`, `orders/payment/yandex`, `GET/PUT cart`, `cart/delivery/intervals`; ECOMDEV-2189 — `gateway-1c`, большая часть `metadata/*`, `notification/subscribe`, `push-click`; ECOMDEV-2230 — лишние ручки orders/products/profile/feedback, `orders/messages`). **Риск:** iOS всё ещё вызывает `core` `GET metadata/about` (`AboutCompanyVC` → `MetadataEndpoint.about`), а в esb этот маршрут удалён → 404 на экране «О компании»; в Go есть `/api/v1/metadata/about` (gRPC Meta Mobile).
- Без Go-копии остаются: `profile/*` (профиль, телефон, адреса, иконки, QR, подписки, вишлист), `profile/actions/restore-password` (по сводке `knowledge/architecture/call-chain.html`; в Go по коду не перепроверялось).
- Полная раскладка «путь core → копия в Go → файл:строка» — `knowledge/architecture/call-chain.html` и §3.2 `knowledge/mobile-monorepo-go/repo-map.md`.

---

## 5. Модули Mobile API в коде

### OpenAPI-спека содержит 25 модулей (tag) — `mobile.yml:38-102` на `dd4a997ac0`

Контроллеры v1 — `src/Modules/Mobile/Controllers/`; v2 — `modules/mobilev2/controllers/` и `src/Modules/MobileV2/Controllers/`.

| # | Модуль | Контроллер v1 | Контроллер v2 |
|---|---|---|---|
| 1 | User | `UserController` + `UserAddressController` + `UserActivitiesController` | `UserGeoController` (MobileV2) |
| 2 | Cart | `CartController` + 7 подконтроллеров (`CartDelivery`, `CartDetails`, `CartDiscount`, `CartGiftcard`, `CartPayment`, `CartRecipient`, `CartTest`) | `CartController` (MobileV2) |
| 3 | Order | `OrdersController` | `OrdersController` (mobilev2) |
| 4 | Profile | `ProfileController` | `ProfileController` (mobilev2) |
| 5 | Product | `ProductsController` | `ProductsController` (mobilev2) |
| 6 | Giftcards | — | `GiftcardsController` (mobilev2, только v2) |
| 7 | Delivery | `DeliveryController` | `DeliveryController` (mobilev2) |
| 8 | Wishlist | `WishlistController` | `WishlistController` (mobilev2) |
| 9 | Lookbook | `LookbooksController` | `LookbookController` (MobileV2) |
| 10 | Catalog | `CatalogController` + `CategoryController` | `CategoryController` (MobileV2) |
| 11 | Feedback | `FeedbackController` | `FeedbackController` (mobilev2) |
| 12 | Metadata | `MetadataController` | — |
| 13 | Stores | `StoresController` | — (v2-контроллера нет; в версии 09.2026 ошибочно указан) |
| 14 | Geo | `CitiesController` (**`GeoController` удалён** — в рамках ECOMDEV-2228/2180/2342, по `repo-map.md` §4.2) | `UserGeoController` (MobileV2) |
| 15 | Payment | `PaymentController` | `PaymentController`, `ChangePaymentController` (MobileV2) |
| 16 | Support | `SupportController` | — |
| 17 | Subscriptions | `SubscribtionsController` | `SubscribtionsController` (mobilev2) |
| 18 | Version | `VersionController` | — |
| 19 | Home | — (**v1 `HomeController` удалён**) | `HomeController` (mobilev2) |
| 20 | Static | `StaticController` | — |
| 21 | Settings | — | `SettingsController` (MobileV2) |
| 22 | Landing | — | `MobileLandingController` (MobileV2) |
| 23 | Notification | — | `NotificationController` (mobilev2) — **новый тег** |
| 24 | Reservation | `ReservationController` — **новый тег** | — |
| 25 | System | `ApiBaseController` / `BaseController` (`/mobile/api-base/error`, `/mobile/base/error`, `/mobilev2/base/error`) — **новый тег** | — |

~~VirtualCard (`VirtualCardController`)~~ — тег и контроллер удалены.

### Контроллеры без тега в спеке (инфраструктурные / доп.)

| Контроллер | Назначение |
|---|---|
| `CartTestController` | Тестирование |
| `UlinkController` (mobilev2) | Deep links |
| `AppleController` (mobilev2) | Apple App Links |
| `AndroidController` (mobilev2) | Android Asset Links |
| `MobileMessageBackendController` | Админ-бэкенд сообщений |
| `MobileInfoBackendController` | Админ-бэкенд информации |
| `AppVersionsConfigBackendController`, `ContactsSettingsBackendController`, `MobileLandingBackendController` (MobileV2) | Админ-бэкенды версий приложения, контактов, лендингов |
| ~~`BannerBackendController`~~ | Удалён (вместе с v1 `GeoController`, `HomeController`, `VirtualCardController`; ECOMDEV-2228/2180/2342) |
| ~~`ReservationController`~~, ~~`NotificationController`~~ | Перенесены в таблицу выше — теперь у них есть теги `Reservation`, `Notification` |

> Привязка тегов к контроллерам сверена по именам файлов и путям; покрытие спекой каждого экшена не проверялось.

---

## 6. Mobile API: старый (v1) и новый (v2)

| | Старый (v1) | Новый (v2) |
|---|---|---|
| **Модуль** | `src/Modules/Mobile/` | `modules/mobilev2/` + `src/Modules/MobileV2/` |
| **URL-префиксы** | `/mobile/...`, `/mobile/v1/...` | `/mobile/v2/...`, `/mobilev2/...`, `/mobile-v2/...` |
| **Контроллеров** (файлов на `dd4a997ac0`) | 34 (в т.ч. 3 базовых: `ApiBaseController`, `BaseController`, `CartBaseController`); в 09.2026 — 38 | 14 (`modules/mobilev2`, в т.ч. `BaseController`) + 11 (`src/Modules/MobileV2`) = 25; в 09.2026 — 27 |
| **Базовый контроллер** | `ApiBaseController` (auth по `MOBILE_API_KEY`, сессия `x-session-token`) | Наследует v1, меняет формат ответа (`items` вместо `answerList`) |

### «Core API» внутри монолита: старый и новый

> Это **API монолита** под префиксами `/api/...`, `/api2/...` (сайт, интеграции, `api2/products/items` для шлюзов) — **не путать** с шлюзом `core` (`core.12stz.com`, `esb-monorepo`, §2).

| | Старый | Новый |
|---|---|---|
| **Модули** | `modules/api/` + `modules/api2/` | `src/Modules/Api2/` + отдельные модули в `src/Modules/` |
| **URL-префиксы** | `/api/...`, `/api2/...` | `/api/v1/...`, `/api/v2/...`, `/api/...` |
| **Авторизация** | Токен в query `?token=` (retailCRM/Bitrix) | `QueryParamAuth` + современные |

---

## 7. Аннотации `@route` + `@proxy-route`

В коде контроллеров используются PHPDoc-аннотации, фиксирующие связку URL-путей:

```php
// Один метод PHP — внешний путь шлюза и внутренний путь монолита
/**
 * @route /mobile/cart-payment/list       ← путь в монолите (куда приходит шлюз)
 * @proxy-route /api/v1/cart/payment-list ← внешний путь шлюза, который проксирует сюда
 */
public function actionList() { ... }
```

- **`@route`** — URL метода в монолите (Yii2 парсит и маршрутизирует)
- **`@proxy-route`** — внешний URL **шлюза**, который проксирует запрос МП в этот метод (только документация; Yii2 его не обрабатывает). `/api/v1/...` — Go-шлюз `mobile.12stz.com`, `/api/...` без версии — шлюз `core` (`core.12stz.com`).

На `dd4a997ac0` аннотация есть в 4 местах: `src/Modules/Mobile/Controllers/CartPaymentController.php:107` (`/api/v1/cart/payment-list`), `PaymentController.php:41` (`/api/v1/payments/{order_id}/{payment_system}/{payment_id}/info`), `modules/mobilev2/controllers/ProductsController.php:137` (`/api/v1/products`), `:1005` (`/api/products/v2/{id}` — путь `core`).

Это **не два метода с одним смыслом** и не два клиента монолита — это **один метод монолита и внешний адрес шлюза перед ним**.

---

## 8. Итог

| Вопрос | Ответ |
|---|---|
| Есть ли в проекте спека Mobile API? | ✅ Да — `docs/openapi/mobile.yml` (159 путей / 187 операций на `dd4a997ac0`; 113 на 09.2026) |
| Есть ли в проекте спека Core API? | ❌ Нет — `core` = шлюз `esb-monorepo`, Swagger в его репозитории (`core.12stz.dev/swagger/`) |
| Mobile и Core — разные сервисы? | Да. Монолит (mobile + frontend API) и **шлюз** `core` (esb) **перед** ним; монолит core не вызывает (кроме ESB-вызова отзывов о магазине `internal.core.12stz.com`) |
| Есть ли отдельный API Gateway-сервис? | **Да, два** (исправлено): старый `core.12stz.com` — `esb-monorepo` (NestJS), новый `mobile.12stz.com` — `mobile-monorepo-go` (Go). Оба — BFF без своей БД |
| Сколько модулей Mobile API? | 25 тегов в спеке (+ Notification, Reservation, System; − VirtualCard) |
| Старый и новый mobile API? | Да — v1 (`/mobile/`) и v2 (`/mobile/v2/`, `/mobilev2/`, `/mobile-v2/`) |
| Старый и новый «core API» монолита? | Да — `modules/api/` + `modules/api2/` (старый) и `src/Modules/Api2/` (новый); к шлюзу `core` отношения не имеют |
| Куда ходит iOS на 07.11.2026? | В оба шлюза: большинство ручек — `core`; `v1/...`, `v2/...` — Go. Go-копии ручек `core` (ECOMDEV-2342…2480) iOS пока не вызывает; `core` `metadata/about` удалён в esb — риск 404 |
