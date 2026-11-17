# Структура репозитория esb-monorepo

**Назначение документа:** карта-справочник по кодовой базе `esb-monorepo` (NestJS/Nx, TypeScript) — старого мобильного шлюза (BFF) 12Storeez, через который МП ходит в монолит и в gRPC-сервисы. Для быстрого поиска при анализе требований.

**Дата актуализации:** 07.11.2026
**Сверено с кодом:** ref `origin/master`, коммит `4519218b` (`4519218b3da0796433b048183eee8893242f77d5`, 03.11.2026, «Merge branch 'develop' into 'master'»); `origin/develop` не впереди master. Предыдущая сверка — `beba6e61` (06.10.2026); между ними 10 коммитов без мержей, 288 файлов, −7413 строк (в основном удаление ручек: ECOMDEV-2180, 2189, 2230).
**Код:** `C:\Users\RobotComp.ru\Desktop\12stz\esb-monorepo\` (только чтение)
**Примечание:** структура и назначение описаны по фактическому коду; где вывод сделан по названию — помечено. Значения секретов в документ не переносятся — только факт и путь.

---

## 1. Общая архитектура

- **Стек:** Node.js 16 (образ CI), NestJS 8, Nx 9 (workspace в формате Angular CLI: `angular.json`, `nx.json`), TypeScript 3.7, RxJS, axios 0.20, gRPC (`@grpc/grpc-js`, `@nestjs/microservices`), `esb-protobufs` 0.6.77 (npm-пакет с `.proto`), Swagger (`@nestjs/swagger`), Sentry, Jest (`package.json`).
- **Роль:** шлюз-прокси (BFF) для мобильного приложения. Почти каждый контроллер либо **проксирует HTTP-запрос в PHP-монолит** `12storeez-master-web` (в его маршруты `mobile/...`, `mobilev2/...`, `api2/...`), либо **вызывает gRPC-сервис** (orders, feedbacks, mindbox, geo, meta, slack, usedesk). Собственной БД и бизнес-логики заказов/возвратов нет — только склейка ответов и маппинг.
- **Внешний адрес:** prod — `core.12stz.com`, путь `/api` (`.deploy/helm/prod.values.yaml:4`, ingress `/api` и `/swagger` — `.deploy/helm/values.yaml:63-80`). Это **старый шлюз `core`**, который iOS-клиент называет `BASE_URL` (см. `knowledge/12storeez-ios/repo-map.md`, §4.3). Новый шлюз `mobile.12stz.com` (`BASE_URL_NEW`) — **не этот репозиторий**, а `12stz/mobile-monorepo-go` (см. [../mobile-monorepo-go/repo-map.md](../mobile-monorepo-go/repo-map.md)).
- **Приложения:** 2 (`apps/mobile-api`, `apps/usedesk-gate`); в CI собирается и деплоится только `mobile-api` (`.gitlab-ci.yml:110`: `yarn nx build mobile-api --prod`, matrix `APP_NAME: mobile-api` — `:201`).
- **Статус шлюза (на 07.11.2026):** шлюз **сворачивается**. В октябре 2026 удалены неиспользуемые ручки: ECOMDEV-2180 (locations, `orders/payment/yandex`, часть cart), ECOMDEV-2189 (`libs/gateway-1c` целиком, большая часть `metadata/*`, часть `notification/*`; `c76e7c11` вернул ещё используемые `metadata/categories` и `notification/polls`), ECOMDEV-2230 (лишние ручки Orders, Products, Profile, Feedback, message-buttons). Параллельно функционал **переносится в Go** (`mobile-monorepo-go`, ECOMDEV-2342…2480): по сводке `knowledge/architecture/call-chain.html` копии в Go-шлюзе (`v1/auth/*`, `v1/catalog/*`, `v1/products/*`, `v1/metadata/*`, `v1/landings`, `v1/ulink`, `v1/old-cart/*`, `v1/orders/*`, `v1/reviews/*`, `v1/notification/*`) уже есть у большинства оставшихся ручек, но **iOS пока ходит сюда**. Без Go-копии по той же сводке: `profile/*` (профиль, телефон, адреса, иконки, QR, подписки, вишлист), `profile/actions/restore-password`, `PUT orders` (создание заказа старым чекаутом), `geo/countries/phone-details`. Наличие копий в Go в рамках этой сверки по коду Go не перепроверялось.

---

## 2. Корневые папки и файлы

| Папка / файл | Назначение |
|---|---|
| `apps/` | Запускаемые приложения Nest: `mobile-api`, `usedesk-gate` |
| `libs/` | Библиотеки Nx (`@12stz/<lib>/<sub>`): контроллеры, gRPC-клиенты, swagger-модели, сущности |
| `tools/` | Nx-schematics (`e2e-app`, `k8s`, `k8s-angular`) и `swagger-migration-tool.js` |
| `.deploy/docker/Dockerfile` | Сборка образа приложения. С `7c07c6d6` аргумент называется `APP_NAME` (по умолчанию `mobile-api`, `Dockerfile:10`), а CI и `docker-compose.yaml` по-прежнему передают `ARG_APP_NAME` (`.gitlab-ci.yml:205`, `docker-compose.yaml:8,17`) — см. §10 |
| `.deploy/helm/` | Helm-чарт: `values.yaml` (база) + `dev/fix/sandbox/mobiledev/stg/prod.values.yaml`; зависимость `nxs-universal-chart ~3.2.2` берётся из `http://chartmuseum.stage.12stz.local` (`Chart.yaml`, hotfix `5fdead26`) |
| `.gitlab-ci.yml` | CI: lint → unit → build → kaniko image → helm deploy (ручной), Sentry release |
| `docker-compose.yaml` | Локальная сборка образов `mobile-api` (порт 8080→80) и `usedesk-gate` |
| `.env` | Содержит только `IMAGE_VERSION` |
| `README.md` | Таблица env-переменных, инструкция локального запуска (minikube/k8s), заметка о `Mercaux-Gate` (приложения в репо уже нет) |
| `angular.json`, `nx.json`, `tsconfig.json`, `jest.config.js`, `tslint.json` | Конфигурация workspace и путей `@12stz/*` |

---

## 3. `apps/` — приложения

| Приложение | Назначение | Ключевые файлы |
|---|---|---|
| `mobile-api` | **Шлюз мобильного API** (`core.12stz.com/api`). Глобальный префикс `api` (`apps/mobile-api/src/main.ts:18`), Swagger на `/swagger` (`main.ts:65`), Bearer-auth, Sentry, `LoggingInterceptor`. Собирает все `*ControllersModule` из `libs/` | `src/main.ts`, `src/app/app.module.ts` (список подключённых модулей: authorization, cart, catalog, geo, metadata, notification, orders, products, profile, reviews, landings, ulink, health-check; `gateway-1c` и `locations` отключены и удалены в ECOMDEV-2189/2180), `src/common/interceptors/logging.interceptor.ts`, `test/*.e2e.spec.ts` (e2e: app, authorization, cart, catalog, geo, metadata, notification, orders, products, profile, reviews; `gateway-1c` и `locations` удалены) |
| `usedesk-gate` | Приём CSI-оценок из Usedesk: `POST /api` → gRPC `usedesk.proto` (`apps/usedesk-gate/src/app/app.controller.ts:26-39`). В CI не деплоится (см. §1) | `src/app/app.controller.ts`, `src/app/app.module.ts`, `src/main.ts` |

---

## 4. `libs/` — библиотеки

Типовая раскладка домена: `<домен>/controllers` (Nest-контроллеры + сервисы-прокси), `<домен>/grpc` (gRPC-клиент), `<домен>/swagger` (DTO/модели для Swagger), `<домен>/entity|entities` (интерфейсы). Префикс маршрута — в `@Controller('...')`, итоговый URL = `/api/<префикс>/...`.

### 4.1. Доменные библиотеки

| Библиотека | Маршруты (`/api/...`) | Куда ходит | Ключевые файлы |
|---|---|---|---|
| `orders` | `orders` (`GET` список, `PUT` создание заказа, `DELETE` отмена), `orders/offline`, `orders/offline/:id`, `orders/v2/return-reasons`, `orders/:order_id`, `orders/:order_id/return`, `orders/dolyame-id/:orderId`. **Удалены:** `orders/payment/yandex` (ECOMDEV-2180, `8c5946a1`), `orders/messages` (message-buttons, ECOMDEV-2230) | Монолит `mobile/orders...`, `mobile/v2/orders/...`; gRPC `orders.proto` (офлайн-чеки), gRPC `feedbacks.proto` (можно ли оценить заказ); монолит `api2/products/items` (обогащение офлайн-позиций) | `controllers/src/lib/orders.controller.ts`, `orders.service.ts` (`path='/orders'`), `mobile-v2.service.ts` (`path='/v2/orders'`), `http-products.service.ts`; `grpc/src/lib/orders-grpc.service.ts`; `swagger/src/lib/orders.swagger.ts` (`ReturnItemsDTO`, `OrderReturnReasons`, `OrderCreatDto`) |
| `cart` | `cart`: `GET check-items`, `POST :barcode` (→ `PATCH mobile/cart/{barcode}`), `DELETE :barcode`, `POST payment`, `GET clean`; `cart/delivery`: `GET` (deprecated, → `POST mobile/delivery`), `POST` (выбор доставки → `mobile/cart/delivery`); `cart/delivery2`: `GET` (→ `POST mobile/v2/delivery`), `boxberry`, `boxberry/:boxberry_id`. **Удалены** (ECOMDEV-2180, `35759378`): `GET cart`, `PUT cart`, `cart/delivery/intervals`. Контроллеры `cart/delivery*` без `AuthRequestGuard` | Монолит `mobile/cart`, `mobile/delivery`, `mobile/v2/delivery` | `controllers/src/lib/cart.controller.ts`, `delivery/delivery.controller.ts`, `delivery2/delivery2.controller.ts` |
| `geo` | `geo/countries` (+ `phone-details`), `geo/cities/{suggest,geocode}`, `geo/addresses/{suggest,geocode}` — всё, кроме `phone-details`, помечено `deprecated` в Swagger | gRPC `geo.proto` (`GEO_GRPC_SRV`, API-ключ `GEO_GRPC_API_KEY`) | `controllers/src/lib/{countries,cities,addresses}/*`, `grpc/src/lib/*` |
| ~~`locations`~~ | **Удалено целиком** в ECOMDEV-2180 (`ff8275e3`): были `locations/countries/taxes`, `locations/geo/{suggest,geocode}`, `locations/countries`, `locations/cities` (+ `suggest`, `geocode`) | — | — |
| ~~`gateway-1c`~~ | **Удалено целиком** в ECOMDEV-2189 (`7c07c6d6`): были `gateway1c`, `gateway-1c/site/{products,stocks}`, `gateway-1c/hs/{products,stocks}`, `gateway-1c/hs/offline-orders/{ru,kz}`, `gateway-1c/slack/send` (обмен с 1С `http://3d-1c-app02.12stz.local` и загрузка товаров/остатков на сайт) | — | — |
| `stores` | — (только gRPC-клиент) | gRPC `meta.proto` (`META_GRPC_SRV`) | `grpc/src/lib/*`; используется в `metadata/controllers/.../stores/stores.controller.ts` |
| `metadata` | `metadata/stores` (+ `cities`, `:store_id`), `metadata/faq` (+ `category/:id`, `theme/:id`), `metadata/sizes`, `metadata/sizes-table`, `metadata/social`, `metadata/categories` (только `GET`), `metadata/stories/:stories_id`, `metadata/stories/v2` (+ `/:stories_id`). **Удалены** в ECOMDEV-2189 (`b3074985`): `metadata` (корень), `about`, `banners`, `collections`, `colors`, `contacts`, `home`, `promotion`, `stores2` (stores-v2), `tags`, `video`, `categories/v2`, `categories/v2/suggest`, `GET metadata/stories` (список); `c76e7c11` вернул `GET metadata/categories` | Монолит `mobile/...` (`support`, `metadata/*`, `category/list`, `lookbooks`, `v2/lookbooks`); gRPC `meta.proto` — только магазины (через `libs/stores/grpc`) | `controllers/src/lib/{stores,faq,sizes,size-table,social,categories,stories,stories-v2}/*`, `grpc/src/lib/*` (`MetadataGrpcModule` импортируется в `metadata-controllers.module.ts:23`, но ни одним контроллером не вызывается — about/contacts удалены) |
| `profile` | `profile` (`GET`, `PATCH`, `DELETE`, `POST actions/restore-password`, `POST password`, `GET icons`, `GET qr`), `profile/addresses` (`GET`, `DELETE :address_id`), `profile/bonus` (`GET`, `GET history`), `profile/phone` (`POST`, `PATCH`), `profile/subscriptions` (`GET`, `PUT`, `DELETE :barcode`, `GET v2`), `profile/wishlist` (`GET ids`, `PUT`, `DELETE :model_id`). **Удалены** в ECOMDEV-2230 (`b28b1f36`): `profile/credit-card/*`, `profile/push`, `profile/wishlist/v2`, `GET profile/wishlist`, `profile/get-phone`, `PATCH profile/email`, `PUT profile/addresses`, `POST profile/bonus/osmi-card` | Монолит `mobile/user...`, `mobile/wishlist`, `mobile/v2/profile`, `mobilev2/subscribtions/...`; gRPC `mindbox.proto` (бонусы — `bonus-grpc`, телефон — `auth-grpc`) | `controllers/src/lib/*`, `bonus-grpc/`, `auth-grpc/` |
| `authorization` | `authorization` (`PUT generate-token`, `POST login`, `POST login/by-phone/request-code`, `POST login/by-phone`, `POST logout`), `authorization/session` (`GET`, `PUT`) | Монолит `mobile/user/auth`, `mobile/user/auth-phone`, `mobile/user/token`, `mobile/user/session`; gRPC `mindbox.proto` (`profile/auth-grpc`, а также `notification/grpc` — `unsubscribe` устройства при logout, `authorization.service.ts:44`); выпуск/проверка JWT | `controllers/src/lib/authorization.controller.ts`, `authorization.service.ts`, `session/*`, `token/*` |
| `notification` | `notification/message`, `notification/info`, `notification/user-activities`, `notification/polls` (`GET`, `POST`). **Удалены** в ECOMDEV-2189: `POST`/`DELETE notification/subscribe`, `POST notification/push-click`; `c76e7c11` вернул `polls` | Только монолит (`mobile/v2/notification/*`, `mobile/user-activities`). `NotificationGrpcModule` из модуля контроллеров убран; сама библиотека `notification/grpc` (Mindbox) теперь используется только в `authorization` | `controllers/src/lib/notification.controller.ts`, `grpc/` |
| `reviews` | `reviews` (`PUT order`, `PUT store`, `PUT app`, `GET order/reasons/:order_id`), `reviews/product` (`GET :model_id`, `PUT :order_id`), `reviews/company` (`GET`, `PUT`). **Удалён** в ECOMDEV-2230: `GET reviews/store/reasons` | Монолит `mobile/feedback/items`, `mobile/feedback/shop`; gRPC `feedbacks.proto` | `controllers/src/lib/*`, `grpc/` |
| `products` | `products/last-view`; `products/v2`: `last-view`, `suggest`, `last-search-term`, `:model_id`, `:model_id/{stocks,last-view,fashion,fashion-stylist}`. **Удалены** в ECOMDEV-2230: `products/ping`, `products/last-search`, `products/suggest`, `products/suggest-diginetica`, `GET products/v2` (индекс), `products/v2/last-search`, `products/v2/for-cart`, `products/v2/:model_id/accompaniments`, `products/v2/:model_id/sizes` | Монолит `mobile/products`, `mobile/v2/products`. Обращение через публичный адрес `PHP_BASE_URL_PUBLIC` было только у удалённого `GET products/v2`; теперь все v2-ручки идут на `PHP_BASE_URL` (константа осталась в `constants.ts:3-4` и в спеке) | `controllers/src/lib/products.controller.ts`, `v2/v2.controller.ts`, `v2/v2.service.ts` (`path='/v2/products'`), `dto/product-query.dto.ts` |
| `catalog` | `catalog/filter` | Монолит `mobile/catalog` (ECOMDEV-2263 — фильтры по талии и длине, `e8b45a6e`) | `controllers/src/lib/*`, `swagger/src/lib/filter-response.ts` |
| `landings` | `landings/v2/:id` | Монолит `mobile/v2/landings` | `controllers/src/lib/*` |
| `ulink` | `v2/ulink` (`POST`) | Монолит `mobile/v2/ulink` | `controllers/src/lib/*` |
| `usedesk-gate` | — | gRPC `usedesk.proto` (`USEDESK_GRPC_SRV`) | `grpc/`, `swagger/` |
| `slack` | — | gRPC `slack.proto` (`SLACK_GRPC_SRV`). **Не используется:** единственный потребитель (`gateway-1c/slack`) удалён в ECOMDEV-2189; библиотека осталась в `angular.json`/`nx.json`/`tsconfig.json` | `grpc/slack-grpc/`, `swagger/` |
| `errors` | — | gRPC `internal/errors.proto` (`INTERNAL_MONOREPO_SRV`). **Не используется:** на `origin/master` импортируется только в собственном spec-файле | `grpc/` |
| `appearance`, `category`, `stories`, `tags`, `entities` | — | — | Только сущности/swagger-модели |

### 4.2. Инфраструктурные библиотеки

| Библиотека | Назначение | Ключевые файлы |
|---|---|---|
| `core` | **HTTP-клиенты к монолиту**, guard, JWT, константы | `src/lib/http-client/http-client.ts` (базовый axios-клиент, `baseURL = PHP_BASE_URL`), `http-client/http-client-mobile.ts` (`baseURL = PHP_BASE_URL + 'mobile/'`, проброс заголовков, см. §5), `auth-request.guard.ts` (пропускает запрос только с заголовком `authorization`, кроме URL с `ping` — `:28-35`), `jwt-strategy/jwt-strategy.service.ts`, `core.module.ts` (регистрация `JwtModule`, срок жизни токена), `constants.ts`, `axios-error.interceptor.ts` (ретрай при `ECONNRESET`, флаг `ALLOW_RETRY_ON_ECONNRESET`) |
| `constants` | `GRPC.nameToPath()` — путь к `.proto` в `node_modules/esb-protobufs/proto/` | `src/lib/grpc-transport.ts` |
| `controllers-entities` | Обёртки ответов `ResponseList`, `ResponseAction` | `src/` |
| `swagger` | Общие swagger-модели, загрузка swagger-документа из `SWAGGER_HOST`/`SWAGGER_PATH` | `models/`, `document-resolver/` |
| `shared` | `health-check` (`/api/ping`, `RedirectToPingInterceptor`), `logger` (ELK/JSON-лог) | `health-check/`, `logger/` |
| `sentry` | Nest-модуль и интерсептор Sentry | `src/` |
| `utils` | `rabbitmq` (паблишер AMQP), `test-helpers` | `rabbitmq/` — **не подключён ни в одном приложении/модуле** (импорты только в собственных spec-файлах) |

---

## 5. Как устроены маршруты и проксирование

1. URL `/api/<префикс контроллера>/<путь метода>` (`main.ts:18` — префикс `api`).
2. Почти все сервисы наследуют `HttpClientMobile` (`libs/core/src/lib/http-client/http-client-mobile.ts:31-32`) и задают `path` (например `OrdersService.path = '/orders'`). Итоговый адрес в монолите: `PHP_BASE_URL + 'mobile/' + path + /id`. Пример: `GET /api/orders/123` → `GET {PHP_BASE_URL}mobile/orders/123`.
3. В монолит пробрасываются заголовки: `x-access-token` (API-ключ шлюза, `PHP_API_KEY`), `x-session-token` (из JWT-пейлоада `session_token`), `user-agent`, `x-platform`, `X-Request-Id`, `x-version` (из `version`), `Referer`, `DeviceID`, `X-Real-IP` (из `x-original-forwarded-for`/`x-qrator-ip-source`/…), `X-Gender` (из query `gender`), `x-language` (как есть, добавлен в ECOMDEV-2239, `46656731`) — `http-client-mobile.ts:16-85`.
4. Аутентификация клиента: Bearer JWT; `AuthRequestGuard` проверяет только наличие заголовка, сама проверка подписи — `JwtStrategyService.verifySync` при создании клиента (`http-client-mobile.ts:60-64`, `jwt-strategy.service.ts:35-42`); тот же `verifySync` вызывает Sentry-интерсептор (`libs/sentry/src/sentry.interceptor.ts:76`). JWT подписан симметричным ключом, **захардкоженным в коде без env-переменной** (`libs/core/src/lib/constants.ts:7-9`, `JWT_CONSTANTS.secret`). **Срок действия проверяется** (исправлено 07.11.2026, ранее в карте было обратное): токены выпускаются с `expiresIn: 3600 * 24 * 14` — 14 дней (`libs/core/src/lib/core.module.ts:15-20`), а `verifySync` вызывает `JwtService.verify` без `ignoreExpiration`, т.е. просроченный токен даёт `UnauthorizedException`. Флаг `ignoreExpiration: true` (`jwt-strategy.service.ts:13`) относится только к passport-стратегии, которая как guard не используется (`AuthGuard(...)` в `libs/`/`apps/` не найден).
5. Описание «куда проксируется» обычно есть прямо в `@ApiOperation({ description: 'proxied to: ...' })` над методом.
6. Тайм-аут запросов в монолит — `REQUEST_TIMEOUT_TO_PHP_SITE` (по умолчанию 55000 мс, `constants.ts:10-11`).

---

## 6. Интеграции

| Система | Протокол | Направление | Где в коде | Назначение |
|---|---|---|---|---|
| Монолит `12storeez-master-web` | HTTP (axios) | шлюз → монолит | `libs/core/src/lib/http-client/*`, все `*.service.ts` с `extends HttpClientMobile` | Основной бэкенд МП: заказы, возвраты, корзина, доставка, профиль, каталог |
| gRPC orders | gRPC (`orders.proto`) | шлюз → сервис | `libs/orders/grpc/` (`ORDERS_GRPC_SRV`) | Офлайн-заказы (чеки магазинов) |
| gRPC feedbacks | gRPC (`feedbacks.proto`) | шлюз → сервис | `libs/reviews/grpc/` (`FEEDBACKS_GRPC_SRV`) | Отзывы; `canBeSaved` для кнопки «Оценить» в заказе |
| Mindbox-сервис | gRPC (`mindbox.proto`) | шлюз → сервис | `libs/profile/bonus-grpc/`, `libs/profile/auth-grpc/`, `libs/notification/grpc/` (`MINDBOX_GRPC_SRV`, префикс `MINDBOX_USER_ID_PREFIX`) | Бонусы, SMS-коды входа и смены телефона; `notification/grpc` — только отписка устройства при logout (ручки `notification/subscribe`, `push-click` удалены в ECOMDEV-2189) |
| Geo-сервис | gRPC (`geo.proto`) | шлюз → сервис | `libs/geo/grpc/` (`GEO_GRPC_SRV`, `GEO_GRPC_API_KEY`) | Страны, коды телефонов, города, адреса |
| Meta-сервис | gRPC (`meta.proto`) | шлюз → сервис | `libs/stores/grpc/` (`META_GRPC_SRV`); `libs/metadata/grpc/` подключён, но не вызывается | Только магазины (`Stores.all`, `cities`, `byID`). «О нас» и контакты удалены в ECOMDEV-2189 |
| Slack-сервис | gRPC (`slack.proto`) | — | `libs/slack/grpc/` (`SLACK_GRPC_SRV`) | **Не используется** с ECOMDEV-2189 (была отправка сообщений из 1С в Slack через `gateway-1c/slack/send`) |
| Usedesk-сервис | gRPC (`usedesk.proto`) | Usedesk → `usedesk-gate` → сервис | `apps/usedesk-gate/`, `libs/usedesk-gate/grpc/` | CSI-оценки поддержки |
| ~~1С (Enterprise)~~ | HTTP | — | ~~`libs/gateway-1c/`~~ | **Удалено** в ECOMDEV-2189 (`7c07c6d6`): были товары, остатки (RU/KZ), офлайн-заказы из 1С |
| ~~Сайт (монолит, публичный)~~ | HTTP | — | ~~`libs/gateway-1c/controllers/src/lib/site/`~~ | **Удалено** в ECOMDEV-2189: была загрузка товаров и остатков из 1С на сайт (`SITE_BASE_URL`) |
| Sentry | SDK | — | `apps/mobile-api/src/main.ts:22-41`, `libs/sentry/` | Ошибки и трейсинг |
| RabbitMQ | AMQP | — | `libs/utils/rabbitmq/` | Библиотека есть, **не используется** |
| БД | — | — | — | **Своей БД нет.** `mongoose`/`@nestjs/mongoose` только в devDependencies; `MONGO_URL` упомянут в README, в коде `apps/`/`libs/` не найден |
| Kafka | — | — | — | **Не найдено** |

---

## 7. Конфигурация и окружения

| Что | Где |
|---|---|
| Env-переменные (адреса монолита и gRPC, тайм-ауты, логи) | `README.md` (таблица), `libs/core/src/lib/constants.ts`, `libs/*/grpc/src/lib/constants.ts` |
| ConfigMap и секреты k8s | `.deploy/helm/values.yaml` (`mobile-api-envs`; секреты из Vault — `mobile-api-vault-envs`, путь `esb/esb-monorepo/<env>/envs`) |
| Хосты окружений | `core-dev.12stz.dev`, `core-fix.12stz.dev`, `core-sandbox.12stz.dev`, `core-mobiledev.12stz.dev`, `core-stg.12stz.dev`, `core.12stz.com` (prod) — `.deploy/helm/*.values.yaml:4` |
| Ingress / Istio | `.deploy/helm/values.yaml:63-135` — только префиксы `/api` и `/swagger`, IP-whitelist |
| Прод-ресурсы | `prod.values.yaml`: 3 реплики |
| **Секреты в коде (значения не приводятся)** | Значения по умолчанию для `PHP_API_KEY` и JWT-ключ — `libs/core/src/lib/constants.ts:5-9`; `GEO_GRPC_API_KEY` — `libs/geo/grpc/src/lib/constants.ts:7`; токен в URL — `libs/orders/controllers/src/lib/http-products.service.ts:6`; `PHP_API_KEY` в `README.md` |

---

## 8. Ключевые точки для поиска по процессам

### 8.1. Возврат товара (МП, старый шлюз `core`)

| Что | Маршрут шлюза | Проксирует в монолит | Где |
|---|---|---|---|
| Причины возврата | `GET /api/orders/v2/return-reasons` | `GET mobile/v2/orders/return-reasons` | `libs/orders/controllers/src/lib/orders.controller.ts:204-212` |
| Создать возврат (позиции + реквизиты) | `POST /api/orders/:order_id/return` | `POST mobile/orders/{order_id}/return` (тело — как есть; в Swagger описано только `items`) | `orders.controller.ts:254-270`, DTO `libs/orders/swagger/src/lib/orders.swagger.ts:86-91` |
| Карточка заказа | `GET /api/orders/:order_id` | `GET mobile/orders/{order_id}` + gRPC feedbacks `canBeSaved` (фильтр сообщения `can_be_marked`) | `orders.controller.ts:227-252` |
| Список заказов / отмена | `GET /api/orders`, `DELETE /api/orders` | `GET mobile/orders`, `POST mobile/orders/cancel` | `orders.controller.ts:54-86`, `272-282` |
| Способы возврата / детали возврата | **нет в этом репозитории** | — | см. §8.2 |

### 8.2. `v1/delivery/{orderId}/return-method-list` и `return-details`

**Не найдено** (на коммите `beba6e61`, а также во всей локальной истории всех веток — `git log --all -S`; повторно 07.11.2026 на `origin/master` `4519218b` — `git grep` по `return-method`, `returnMethod`, `return_method`, `return-details`, `returnDetails`, `v1/delivery` пуст):
- поиск по `apps/`, `libs/` и корню: `return-method`, `returnMethod`, `ReturnMethod`, `return_method`, `return-details`, `returnDetails`, `delivery/:`, `@Controller('delivery…')`, `v1/delivery` — совпадений нет;
- контроллера с префиксом `delivery` нет — есть только `cart/delivery` и `cart/delivery2` (доставка корзины);
- шлюз публикует только `/api/...` без сегмента `v1` (`main.ts:18`, ingress `values.yaml:73-80`);
- хост этого шлюза — `core.12stz.com`, а iOS шлёт эти два запроса на `BASE_URL_NEW` = `mobile.12stz.com/api` (`knowledge/12storeez-ios/repo-map.md`, §4.3). По сваггеру нового шлюза (`knowledge/12storeez-master-web/api/mobile/mobile-gateway_swagger.yaml`) их проксирует **Mobile API Gateway** в `mobile/orders/{id}/return-method-list` / `return-details` монолита. Это подтверждено кодом нового шлюза — `12stz/mobile-monorepo-go`, см. [../mobile-monorepo-go/repo-map.md](../mobile-monorepo-go/repo-map.md) §5.

### 8.3. Прочее

| Что искать | Где |
|---|---|
| Доставка корзины, ПВЗ Boxberry | `libs/cart/controllers/src/lib/delivery*/` |
| Офлайн-заказы (чеки магазинов) | `orders.controller.ts:88-202` (gRPC orders); выгрузка из 1С (`libs/gateway-1c/.../offline-orders/`) удалена в ECOMDEV-2189 |
| Бонусы | `libs/profile/controllers/src/lib/bonus/`, `libs/profile/bonus-grpc/` |
| Авторизация, JWT | `libs/authorization/`, `libs/core/src/lib/jwt-strategy/`, `libs/core/src/lib/core.module.ts` (срок жизни токена) |
| Обмен с 1С | **Удалён** (`libs/gateway-1c/`, ECOMDEV-2189, `7c07c6d6`); смотреть историю до `beba6e61` |
| Удалённые ручки и их задачи | `git log --oneline beba6e61..4519218b` (ECOMDEV-2180, 2189, 2230), сводка — §4.1 |
| Копии ручек в Go-шлюзе | `knowledge/architecture/call-chain.html` (пометка «копия в Go»), [../mobile-monorepo-go/repo-map.md](../mobile-monorepo-go/repo-map.md) |
| Swagger шлюза | `/swagger` на хосте окружения (генерируется из декораторов, `main.ts:55-65`) |

---

## 9. Быстрые подсказки по поиску

1. **Есть ли метод в старом шлюзе:** ищи `@Controller('` (префикс) и `@Get(`/`@Post(` в `libs/*/controllers/`; итоговый путь = `/api/<префикс>/<метод>`.
2. **Куда проксируется:** `description: 'proxied to: ...'` в `@ApiOperation` и поле `path` в сервисе (`extends HttpClientMobile` → `mobile/` монолита).
3. **gRPC-зависимости:** `libs/*/grpc/src/lib/constants.ts` (env-переменная адреса) и `*.module.ts` (`protoPath`).
4. **Окружения и хосты:** `.deploy/helm/*.values.yaml`.
5. **Тесты:** `apps/mobile-api/test/*.e2e.spec.ts`, `libs/**/*.spec.ts`.

---

## 10. Находки и риски (на `origin/master` `4519218b`)

| # | Находка | Где | Последствие |
|---|---|---|---|
| 1 | **`GET /api/metadata/about` удалён (ECOMDEV-2189, `b3074985`), а iOS его ещё вызывает** (`AboutCompanyVC` → `MetadataEndpoint.about`, см. `knowledge/architecture/call-chain.html`) | был `libs/metadata/controllers/src/lib/about/about.controller.ts` | После выкладки master на prod экран «О компании» в iOS получит **404**. Варианты: вернуть ручку (как `c76e7c11` вернул categories/polls) или перевести iOS на Go-копию `v1/metadata/about` (`mobile-monorepo-go`, по сводке `metadata.go:47`) |
| 2 | Шлюз сворачивается и переносится в Go (ECOMDEV-2342…2480); у большинства ручек есть Go-копии, но iOS ходит сюда | §1 | Любое новое удаление в esb надо сверять с вызовами iOS (`call-chain.html`), пока клиент не переключён на `mobile.12stz.com`. Ручки без Go-копии (профиль, `PUT orders`, `restore-password`, `geo/countries/phone-details`) — блокеры для отключения шлюза |
| 3 | Исправлено: `GET products/v2/last-search-term` раньше перехватывался маршрутом `/:model_id`; теперь объявлен до него (`libs/products/controllers/src/lib/v2/v2.controller.ts:61` против `:73`) и покрыт тестом (`v2.controller.spec.ts:158-163`) | `v2.controller.ts` | Риск снят |
| 4 | Аргумент Dockerfile переименован `ARG_APP_NAME` → `APP_NAME` (`7c07c6d6`), но CI (`.gitlab-ci.yml:205`) и `docker-compose.yaml:8,17` передают `ARG_APP_NAME` | `.deploy/docker/Dockerfile:10-12` | `mobile-api` собирается за счёт значения по умолчанию; образ `usedesk-gate` через `docker-compose` соберётся как `mobile-api`. Для prod-деплоя сейчас не критично |
| 5 | Мёртвый код после чисток: `libs/slack/*` (потребитель удалён), `libs/errors/grpc` (импорт только в своём spec), `libs/metadata/grpc` (модуль подключён, сервис не вызывается), `libs/utils/rabbitmq`; константа `PHP_BASE_URL_PUBLIC` больше не используется в коде | §4.1, §4.2 | Не влияет на работу; кандидаты на следующую чистку |
| 6 | JWT: ключ подписи захардкожен (`'secretKey'`, `libs/core/src/lib/constants.ts:7-9`), без переопределения через env; тот же JWT проверяет Go-шлюз | `constants.ts`, `core.module.ts:15-20` | Знание ключа позволяет выпустить валидный токен для обоих шлюзов. Срок жизни (14 дней) проверяется — см. §5 п. 4 |
| 7 | `cart/delivery` и `cart/delivery2` без `AuthRequestGuard` | `libs/cart/controllers/src/lib/delivery*/` | Ручки доступны без заголовка `authorization`; если заголовок есть — JWT всё равно проверяется в `HttpClientMobile` |

---

## 11. Неопределённости и вопросы

- [x] Где лежит код нового шлюза `mobile.12stz.com` (Mobile API Gateway), который обслуживает `v1/delivery/...`. Ответ: `12stz/mobile-monorepo-go` (10.10.2026).
- [ ] `apps/usedesk-gate` в CI не собирается — развёрнут ли он где-то ещё, из кода не видно.
- [ ] Реальные значения `PHP_BASE_URL` и gRPC-адресов на prod — в Vault (`mobile-api-vault-envs`), в репозитории их нет.
- [ ] Выложен ли `4519218b` на prod (`core.12stz.com`) и когда — из репозитория не видно (деплой ручной, `.gitlab-ci.yml`); от этого зависит, когда сработает риск №1 из §10.
- [ ] Кто ещё (Android, веб) вызывает оставленные «по просьбе» `metadata/categories` и `notification/polls` — iOS их не вызывает (по `call-chain.html`).

---

## История изменений

| Версия | Дата | Автор | Изменения |
|---|---|---|---|
| 1.0 | 10.10.2026 | repository-researcher | Первая версия карты по коммиту `beba6e61`; поиск `v1/delivery/{orderId}/return-method-list` и `return-details` — не найдено |
| 1.1 | 10.10.2026 | Системный аналитик | Новый шлюз `mobile.12stz.com` найден в `12stz/mobile-monorepo-go`: §1, §8.2, §10 — ссылки на его карту |
| 1.2 | 07.11.2026 | repository-researcher | Сверка с `origin/master` `4519218b` (03.11.2026; было `beba6e61`). §1 — статус шлюза: чистка ECOMDEV-2180/2189/2230 и перенос в Go (ECOMDEV-2342…2480). §3–§4 — убраны `gateway-1c` и `locations` (помечены удалёнными), обновлены маршруты orders/cart/metadata/notification/profile/reviews/products, отмечены неиспользуемые `slack`, `errors`, `metadata/grpc`. §5 — заголовок `x-language`, номера строк; **исправлено утверждение про JWT**: срок действия (14 дней) проверяется, `ignoreExpiration` действует только в неиспользуемой passport-стратегии. §6 — 1С/сайт/Slack удалены, Meta — только магазины. §7 — Dockerfile/Chart. §8 — номера строк, повторная проверка `return-method-list`. Новый §10 «Находки и риски» (удалённый `metadata/about` при живом вызове из iOS и др.); вопросы — §11, вопрос про `libs/errors/grpc` закрыт (не используется) |
