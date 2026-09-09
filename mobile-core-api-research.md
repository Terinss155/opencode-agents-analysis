# Исследование: Mobile API и Core API — архитектура и кодовая база

**Дата:** 2026-09-09
**Цель:** Определить, где живут Mobile API и Core API, какие спеки присутствуют в проекте, и как они связаны.

---

## 1. OpenAPI-спеки в репозитории

В репозитории `12storeez-master/` присутствуют **3 OpenAPI-спеки** (hand-written YAML, без автогенерации из PHP-кода):

| # | Спека | Файл | Потребитель | Base URL | Эндпоинтов |
|---|---|---|---|---|---|
| 1 | **Mobile API** | `docs/mobileApi/openapi.yml` | iOS/Android приложения | `/mobile` | **113** |
| 2 | **Frontend (Web)** | `docs/frontend/openapi.yml` | Браузерный сайт | `/` | **144** |
| 3 | **SSR** | `docs/ssr/openapi.yml` | SSR-фронтенд | `/ssr/api/` | **21** |

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

## 2. Core API — внешний микросервис

**Спека `core.12stz.dev` В ЭТОМ РЕПОЗИТОРИИ ОТСУТСТВУЕТ.** Core API — это отдельный микросервис, живущий в другом репозитории.

### Доказательства

В коде монолита есть только **ссылки** на core:

| Файл | Ссылка | Тип |
|---|---|---|
| `modules/mobilev2/controllers/DeliveryController.php:83` | `@swagger-mobile https://core.12stz.dev/swagger/#/Cart/Delivery2Controller_getDelivery2` | PHPDoc аннотация |
| `src/Modules/Mobile/Controllers/CartController.php:370` | `@swagger-mobile https://core.12stz.dev/swagger/#/Cart/DeliveryController_selectDelivery` | PHPDoc аннотация |
| `src/Modules/MobileV2/Controllers/LookbookController.php:71` | `@swagger-mobile https://core.12stz.dev/swagger/#/Metadata/StoriesV2Controller_getAll` | PHPDoc аннотация |
| `src/Modules/MobileV2/Controllers/LookbookController.php:127` | `@swagger-mobile https://core.12stz.dev/swagger/#/Metadata/StoriesV2Controller_getById` | PHPDoc аннотация |
| `src/Modules/Mobile/Controllers/LookbooksController.php:43` | `@swagger-mobile https://core.12stz.dev/swagger/#/Metadata/StoriesController_getAll` | PHPDoc аннотация |
| `modules/cms/console/EnrichWarehouses.php:14` | `@link https://core.12stz.com/swagger/#/Metadata%23stores/StoresController_getCitiesListWithStores` | PHPDoc @link |
| `modules/feedback/controllers/ReviewShopController.php:19` | `ESB_HOST_PROD = 'https://internal.core.12stz.com'` | PHP-константа |

---

## 3. Сравнение: что есть, чего нет

### Mobile API

| Домен | В коде | В спеке | Статус |
|---|---|---|---|
| `mobile.12storeez.com` | Нет (0 совпадений) | ✅ Да (prod server URL) | Прод-домен прописан только в openapi.yml |
| `mobile.12stz.dev` | Нет (0 совпадений) | Нет | Dev-домен, вероятно DNS/nginx alias |
| `mobile.12stz.tech` | Нет (0 совпадений) | ✅ Да (staging server URL) | Staging-домен прописан только в openapi.yml |

### Core API

| Домен | В коде | В спеке | Статус |
|---|---|---|---|
| `core.12stz.dev` | 5 совпадений (аннотации) | ❌ Нет | Только PHPDoc-ссылки |
| `core.12stz.com` | 1 совпадение (аннотация) | ❌ Нет | Только PHPDoc-ссылка |
| `internal.core.12stz.com` | 1 совпадение (константа) | ❌ Нет | URL для ESB-вызовов |
| `core.12storeez.com` | 0 совпадений | ❌ Нет | Не используется |

---

## 4. Архитектура: как всё связано

```
┌──────────────────┐
│ Мобильное        │
│ приложение       │
└────────┬─────────┘
         │ HTTPS
         ▼
┌────────────────────────────┐
│ API Gateway (инфраструктура)│
│ mobile.12stz.dev            │
│ = Istio Ingress / Nginx    │
│ • TLS termination           │
│ • Rate limiting             │
│ • X-Forwarded-For           │
└────────────┬───────────────┘
             │ HTTP (внутренний)
             ▼
┌────────────────────────────┐
│ Yii2 Монолит               │
│ (web-monolith-http)        │
│                            │
│  Модули:                   │
│  • Mobile (v1) — 38 ctrl   │
│  • MobileV2 (v2) — 27 ctrl │
│  • Api / Api2 — core ctrl  │
│  • Cart, Payment, Delivery │
│                            │
│  ┌──────────────────────┐  │
│  │ /mobile/* → Mobile   │  │
│  │ /api/*    → Core API │  │
│  │ /ssr/api/* → SSR     │  │
│  └──────────────────────┘  │
│          │                 │
│          │ вызовы для      │
│          │ доставки/лукбуков│
│          ▼                 │
│  ┌──────────────────────┐  │
│  │ Core Microservice    │  │
│  │ core.12stz.dev       │  │
│  │ (отдельный репозиторий│  │
│  │  + отдельная спека)  │  │
│  └──────────────────────┘  │
└────────────────────────────┘
```

### Поток запросов

1. **Мобильное приложение** → `mobile.12stz.dev` → **nginx/Istio** → **монолит**
2. **Монолит** обрабатывает большинство эндпоинтов самостоятельно
3. **Для доставки и лукбуков** монолит вызывает **core.12stz.dev** (отдельный микросервис)
4. **Core-сервис** имеет свою Swagger UI (`core.12stz.dev/swagger/`), спека живёт в другом репозитории

### Что core-сервис делает для mobile

| Mobile эндпоинт | Обработчик в монолите | Вызов в core |
|---|---|---|
| `/mobile/v2/delivery` | `DeliveryController` (mobilev2) | `Delivery2Controller.getDelivery2` |
| `/mobile/cart/delivery` | `CartController` (mobile) | `DeliveryController.selectDelivery` |
| `/mobile/lookbook` | `LookbooksController` (mobile) | `StoriesController.getAll` |
| `/mobile/v2/lookbook/{id}` | `LookbookController` (mobilev2) | `StoriesV2Controller.getAll / getById` |

---

## 5. Модули Mobile API в коде

### OpenAPI-спека содержит 23 модуля (tag)

| # | Модуль | Контроллер v1 | Контроллер v2 |
|---|---|---|---|
| 1 | User | `UserController` + `UserAddressController` + `UserActivitiesController` | `ProfileController` (geo) |
| 2 | Cart | `CartController` + 6 подконтроллеров | — |
| 3 | Order | `OrdersController` | `OrdersController` |
| 4 | Profile | `ProfileController` | — |
| 5 | Product | `ProductsController` | `ProductsController` |
| 6 | Giftcards | — | `GiftcardsController` (только v2) |
| 7 | Delivery | `DeliveryController` | `DeliveryController` |
| 8 | Wishlist | `WishlistController` | `WishlistController` |
| 9 | Lookbook | `LookbooksController` | — |
| 10 | Catalog | `CatalogController` + `CategoryController` | `CategoryController` |
| 11 | Feedback | `FeedbackController` | `FeedbackController` |
| 12 | Metadata | `MetadataController` | — |
| 13 | Stores | `StoresController` | `StoresController` |
| 14 | Geo | `GeoController` + `CitiesController` | — |
| 15 | Payment | `PaymentController` | через роуты v2 |
| 16 | Support | `SupportController` | — |
| 17 | Subscriptions | `SubscribtionsController` | `SubscribtionsController` |
| 18 | Version | `VersionController` | — |
| 19 | VirtualCard | `VirtualCardController` | — |
| 20 | Home | `HomeController` | `HomeController` |
| 21 | Static | `StaticController` | — |
| 22 | Settings | — | через модуль mobile-v2 |
| 23 | Landing | — | через модуль mobile-v2 |

**Все 23 модуля имеют бэкенд-реализацию** — «сиротских» тегов нет.

### Контроллеры без тега в спеке (инфраструктурные / доп.)

| Контроллер | Назначение |
|---|---|
| `ReservationController` | Бронирование |
| `CartTestController` | Тестирование |
| `UlinkController` | Deep links |
| `AppleController` | Apple App Links |
| `AndroidController` | Android Asset Links |
| `NotificationController` | Push-уведомления |
| `BannerBackendController` | Админ-бэкенд баннеров |
| `MobileMessageBackendController` | Админ-бэкенд сообщений |
| `MobileInfoBackendController` | Админ-бэкенд информации |

---

## 6. Mobile API: старый (v1) и новый (v2)

| | Старый (v1) | Новый (v2) |
|---|---|---|
| **Модуль** | `src/Modules/Mobile/` | `modules/mobilev2/` + `src/Modules/MobileV2/` |
| **URL-префиксы** | `/mobile/...`, `/mobile/v1/...` | `/mobile/v2/...`, `/mobilev2/...`, `/mobile-v2/...` |
| **Контроллеров** | 38 | 16 + 11 = 27 |
| **Базовый контроллер** | `ApiBaseController` (auth по `MOBILE_API_KEY`, сессия `x-session-token`) | Наследует v1, меняет формат ответа (`items` вместо `answerList`) |

### Core API: старый и новый

| | Старый | Новый |
|---|---|---|
| **Модули** | `modules/api/` + `modules/api2/` | `src/Modules/Api2/` + отдельные модули в `src/Modules/` |
| **URL-префиксы** | `/api/...`, `/api2/...` | `/api/v1/...`, `/api/v2/...`, `/api/...` |
| **Авторизация** | Токен в query `?token=` (retailCRM/Bitrix) | `QueryParamAuth` + современные |

---

## 7. Аннотации `@route` + `@proxy-route`

В коде контроллеров используются PHPDoc-аннотации, фиксирующие связку URL-путей:

```php
// Один метод PHP — два URL на него ведут
/**
 * @route /mobile/cart-payment/list       ← mobile приложение
 * @proxy-route /api/v1/cart/payment-list ← core/frontend клиент
 */
public function actionList() { ... }
```

- **`@route`** — основной URL метода (Yii2 парсит и маршрутизирует)
- **`@proxy-route`** — альтернативный URL (только документация;Yii2 стандартный UrlManager не обрабатывает)

Это **не два метода с одним смыслом** — это **один метод, обслуживающий двух клиентов** по разным адресам.

---

## 8. Итог

| Вопрос | Ответ |
|---|---|
| Есть ли в проекте спека Mobile API? | ✅ Да — `docs/mobileApi/openapi.yml` (113 эндпоинтов) |
| Есть ли в проекте спека Core API? | ❌ Нет — `core.12stz.dev` живёт в другом репозитории |
| Mobile и Core — разные сервисы? | Да. Монолит (mobile + frontend + SSR) и отдельный микросервис (core) |
| Есть ли отдельный API Gateway-сервис? | Нет. Gateway = инфраструктура (Istio/Nginx), не PHP-компонент |
| Сколько модулей Mobile API? | 23 модуля в спеке, все реализованы в коде |
| Старый и новый mobile API? | Да — v1 (`/mobile/`) и v2 (`/mobile/v2/`) |
| Старый и новый core API? | Да — `modules/api/` + `modules/api2/` (старый) и `src/Modules/Api2/` (новый) |
