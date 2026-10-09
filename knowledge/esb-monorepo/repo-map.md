# Структура репозитория esb-monorepo

**Назначение документа:** карта-справочник по кодовой базе `esb-monorepo` (NestJS/Nx, TypeScript) — старого мобильного шлюза (BFF) 12Storeez, через который МП ходит в монолит и в gRPC-сервисы. Для быстрого поиска при анализе требований.

**Дата актуализации:** 10.10.2026
**Сверено с кодом:** ветка `master`, коммит `beba6e61` (`beba6e61b305c682849a286b8da616989677e642`, 06.10.2026, «Merge branch 'develop' into 'master'»)
**Код:** `C:\Users\RobotComp.ru\Desktop\12stz\esb-monorepo\` (только чтение)
**Примечание:** структура и назначение описаны по фактическому коду; где вывод сделан по названию — помечено. Значения секретов в документ не переносятся — только факт и путь.

---

## 1. Общая архитектура

- **Стек:** Node.js 16 (образ CI), NestJS 8, Nx 9 (workspace в формате Angular CLI: `angular.json`, `nx.json`), TypeScript 3.7, RxJS, axios 0.20, gRPC (`@grpc/grpc-js`, `@nestjs/microservices`), `esb-protobufs` 0.6.77 (npm-пакет с `.proto`), Swagger (`@nestjs/swagger`), Sentry, Jest (`package.json`).
- **Роль:** шлюз-прокси (BFF) для мобильного приложения. Почти каждый контроллер либо **проксирует HTTP-запрос в PHP-монолит** `12storeez-master-web` (в его маршруты `mobile/...`, `mobilev2/...`, `api2/...`), либо **вызывает gRPC-сервис** (orders, feedbacks, mindbox, geo, meta, slack, usedesk). Собственной БД и бизнес-логики заказов/возвратов нет — только склейка ответов и маппинг.
- **Внешний адрес:** prod — `core.12stz.com`, путь `/api` (`.deploy/helm/prod.values.yaml:4`, ingress `/api` и `/swagger` — `.deploy/helm/values.yaml:63-80`). Это **старый шлюз `core`**, который iOS-клиент называет `BASE_URL` (см. `knowledge/12storeez-ios/repo-map.md`, §4.3). Новый шлюз `mobile.12stz.com` (`BASE_URL_NEW`) — **не этот репозиторий**, а `12stz/mobile-monorepo-go` (см. [../mobile-monorepo-go/repo-map.md](../mobile-monorepo-go/repo-map.md)).
- **Приложения:** 2 (`apps/mobile-api`, `apps/usedesk-gate`); в CI собирается и деплоится только `mobile-api` (`.gitlab-ci.yml`: `yarn nx build mobile-api --prod`, matrix `APP_NAME: mobile-api`).

---

## 2. Корневые папки и файлы

| Папка / файл | Назначение |
|---|---|
| `apps/` | Запускаемые приложения Nest: `mobile-api`, `usedesk-gate` |
| `libs/` | Библиотеки Nx (`@12stz/<lib>/<sub>`): контроллеры, gRPC-клиенты, swagger-модели, сущности |
| `tools/` | Nx-schematics (`e2e-app`, `k8s`, `k8s-angular`) и `swagger-migration-tool.js` |
| `.deploy/docker/Dockerfile` | Сборка образа приложения (`ARG_APP_NAME`) |
| `.deploy/helm/` | Helm-чарт: `values.yaml` (база) + `dev/fix/sandbox/mobiledev/stg/prod.values.yaml` |
| `.gitlab-ci.yml` | CI: lint → unit → build → kaniko image → helm deploy (ручной), Sentry release |
| `docker-compose.yaml` | Локальная сборка образов `mobile-api` (порт 8080→80) и `usedesk-gate` |
| `.env` | Содержит только `IMAGE_VERSION` |
| `README.md` | Таблица env-переменных, инструкция локального запуска (minikube/k8s), заметка о `Mercaux-Gate` (приложения в репо уже нет) |
| `angular.json`, `nx.json`, `tsconfig.json`, `jest.config.js`, `tslint.json` | Конфигурация workspace и путей `@12stz/*` |

---

## 3. `apps/` — приложения

| Приложение | Назначение | Ключевые файлы |
|---|---|---|
| `mobile-api` | **Шлюз мобильного API** (`core.12stz.com/api`). Глобальный префикс `api` (`apps/mobile-api/src/main.ts:18`), Swagger на `/swagger` (`main.ts:65`), Bearer-auth, Sentry, `LoggingInterceptor`. Собирает все `*ControllersModule` из `libs/` | `src/main.ts`, `src/app/app.module.ts` (список подключённых модулей: authorization, cart, catalog, gateway-1c, geo, locations, metadata, notification, orders, products, profile, reviews, landings, ulink, health-check), `src/common/interceptors/logging.interceptor.ts`, `test/*.e2e.spec.ts` (e2e по каждому домену) |
| `usedesk-gate` | Приём CSI-оценок из Usedesk: `POST /api` → gRPC `usedesk.proto` (`apps/usedesk-gate/src/app/app.controller.ts:28-41`). В CI не деплоится (см. §1) | `src/app/app.controller.ts`, `src/app/app.module.ts`, `src/main.ts` |

---

## 4. `libs/` — библиотеки

Типовая раскладка домена: `<домен>/controllers` (Nest-контроллеры + сервисы-прокси), `<домен>/grpc` (gRPC-клиент), `<домен>/swagger` (DTO/модели для Swagger), `<домен>/entity|entities` (интерфейсы). Префикс маршрута — в `@Controller('...')`, итоговый URL = `/api/<префикс>/...`.

### 4.1. Доменные библиотеки

| Библиотека | Маршруты (`/api/...`) | Куда ходит | Ключевые файлы |
|---|---|---|---|
| `orders` | `orders`, `orders/offline`, `orders/v2/return-reasons`, `orders/:order_id`, `orders/:order_id/return`, `orders/dolyame-id/:orderId`, `orders/payment/yandex`, `orders/messages` | Монолит `mobile/orders...`, `mobile/v2/orders/...`, `mobile/payment`; gRPC `orders.proto` (офлайн-чеки), gRPC `feedbacks.proto` (можно ли оценить заказ); монолит `api2/products/items` (обогащение офлайн-позиций) | `controllers/src/lib/orders.controller.ts`, `orders.service.ts` (`path='/orders'`), `mobile-v2.service.ts` (`path='/v2/orders'`), `http-products.service.ts`, `payment/*`, `message-buttons/*`; `grpc/src/lib/orders-grpc.service.ts`; `swagger/src/lib/orders.swagger.ts` (`ReturnItemsDTO`, `OrderReturnReasons`) |
| `cart` | `cart`, `cart/delivery` (deprecated GET, POST выбор доставки, `intervals`), `cart/delivery2` (+ `boxberry`) | Монолит `mobile/cart`, `mobile/delivery`, `mobile/v2/delivery` | `controllers/src/lib/cart.controller.ts`, `delivery/delivery.controller.ts`, `delivery2/delivery2.controller.ts` |
| `geo` | `geo/countries`, `geo/cities`, `geo/addresses` | gRPC `geo.proto` (`GEO_GRPC_SRV`, API-ключ `GEO_GRPC_API_KEY`) | `controllers/src/lib/{countries,cities,addresses}/*`, `grpc/src/lib/*` |
| `locations` | `locations`, `locations/countries`, `locations/cities` | Монолит `mobile/...` (`geo/countries`, `cities`) | `controllers/src/lib/*` |
| `gateway-1c` | `gateway1c` (инфо), `gateway-1c/site/{products,stocks}`, `gateway-1c/hs/{products,stocks}`, `gateway-1c/hs/offline-orders/{ru,kz}`, `gateway-1c/slack/send` | **1С** по HTTP (`http://3d-1c-app02.12stz.local`, базы `/Prod_Marking` и `/Prod_MarkingKaz`, ресурсы `/hs/catalog/all/`, `/hs/stocks/all/`); сайт `SITE_BASE_URL/api/{products,stocks}`; gRPC `slack.proto` | `controllers/src/lib/enterprise1c/abstract-http-1c.service.ts`, `enterprise1c/*`, `site/*`, `slack/slack.controller.ts`, `validator-1c/` |
| `stores` | — (только gRPC-клиент) | gRPC `meta.proto` (`META_GRPC_SRV`) | `grpc/src/lib/*`; используется в `metadata/controllers/.../stores/stores.controller.ts` |
| `metadata` | `metadata/*`: stores, stores2, about, contacts, faq, colors, sizes, sizes-table, social, categories, collections, tags, home, promotion, video, stories(/v2), banners | Монолит `mobile/...` и gRPC `meta.proto` (about, contacts, stores) | `controllers/src/lib/*`, `grpc/src/lib/*` |
| `profile` | `profile`, `profile/{addresses,bonus,credit-card,phone,push,subscriptions,wishlist}` | Монолит `mobile/user...`, `mobile/wishlist`, `mobilev2/...`; gRPC `mindbox.proto` (бонусы — `bonus-grpc`, телефон/авторизация — `auth-grpc`) | `controllers/src/lib/*`, `bonus-grpc/`, `auth-grpc/` |
| `authorization` | `authorization`, `authorization/session` | Монолит `mobile/user/auth`, `mobile/user/token`, `mobile/user/session`; gRPC `mindbox.proto`; выпуск/проверка JWT | `controllers/src/lib/authorization.controller.ts`, `session/*`, `token/*` |
| `notification` | `notification` | gRPC `mindbox.proto` + монолит `mobile/...` | `controllers/src/lib/notification.controller.ts`, `grpc/` |
| `reviews` | `reviews`, `reviews/product`, `reviews/company` | Монолит `mobile/user`, `mobile/feedback/items`, `mobile/feedback/shop`; gRPC `feedbacks.proto` | `controllers/src/lib/*`, `grpc/` |
| `products` | `products`, `products/v2` | Монолит `mobile/products`, `mobile/v2/products` (v2 — через публичный адрес `PHP_BASE_URL_PUBLIC`) | `controllers/src/lib/*` |
| `catalog` | `catalog` | Монолит `mobile/catalog` | `controllers/src/lib/*` |
| `landings` | `landings/v2` | Монолит `mobile/v2/landings` | `controllers/src/lib/*` |
| `ulink` | `v2/ulink` | Монолит `mobile/v2/ulink` | `controllers/src/lib/*` |
| `usedesk-gate` | — | gRPC `usedesk.proto` (`USEDESK_GRPC_SRV`) | `grpc/`, `swagger/` |
| `slack` | — | gRPC `slack.proto` (`SLACK_GRPC_SRV`) | `grpc/slack-grpc/` |
| `errors` | — | gRPC `internal/errors.proto` (`INTERNAL_MONOREPO_SRV`); где используется — не проверено | `grpc/` |
| `appearance`, `category`, `stories`, `tags`, `entities` | — | — | Только сущности/swagger-модели |

### 4.2. Инфраструктурные библиотеки

| Библиотека | Назначение | Ключевые файлы |
|---|---|---|
| `core` | **HTTP-клиенты к монолиту**, guard, JWT, константы | `src/lib/http-client/http-client.ts` (базовый axios-клиент, `baseURL = PHP_BASE_URL`), `http-client/http-client-mobile.ts` (`baseURL = PHP_BASE_URL + 'mobile/'`, проброс заголовков, см. §5), `auth-request.guard.ts` (пропускает запрос только с заголовком `authorization`, кроме `ping`), `jwt-strategy/jwt-strategy.service.ts`, `constants.ts`, `axios-error.interceptor.ts` (ретрай при `ECONNRESET`, флаг `ALLOW_RETRY_ON_ECONNRESET`) |
| `constants` | `GRPC.nameToPath()` — путь к `.proto` в `node_modules/esb-protobufs/proto/` | `src/lib/grpc-transport.ts` |
| `controllers-entities` | Обёртки ответов `ResponseList`, `ResponseAction` | `src/` |
| `swagger` | Общие swagger-модели, загрузка swagger-документа из `SWAGGER_HOST`/`SWAGGER_PATH` | `models/`, `document-resolver/` |
| `shared` | `health-check` (`/api/ping`, `RedirectToPingInterceptor`), `logger` (ELK/JSON-лог) | `health-check/`, `logger/` |
| `sentry` | Nest-модуль и интерсептор Sentry | `src/` |
| `utils` | `rabbitmq` (паблишер AMQP), `test-helpers` | `rabbitmq/` — **не подключён ни в одном приложении/модуле** (импорты только в собственных spec-файлах) |

---

## 5. Как устроены маршруты и проксирование

1. URL `/api/<префикс контроллера>/<путь метода>` (`main.ts:18` — префикс `api`).
2. Почти все сервисы наследуют `HttpClientMobile` (`libs/core/src/lib/http-client/http-client-mobile.ts:31`) и задают `path` (например `OrdersService.path = '/orders'`). Итоговый адрес в монолите: `PHP_BASE_URL + 'mobile/' + path + /id`. Пример: `GET /api/orders/123` → `GET {PHP_BASE_URL}mobile/orders/123`.
3. В монолит пробрасываются заголовки: `x-access-token` (API-ключ шлюза, `PHP_API_KEY`), `x-session-token` (из JWT-пейлоада `session_token`), `user-agent`, `x-platform`, `X-Request-Id`, `x-version` (из `version`), `Referer`, `DeviceID`, `X-Real-IP` (из `x-original-forwarded-for`/`x-qrator-ip-source`/…), `X-Gender` (из query `gender`) — `http-client-mobile.ts:17-87`.
4. Аутентификация клиента: Bearer JWT; `AuthRequestGuard` проверяет только наличие заголовка, сама проверка подписи — `JwtStrategyService.verifySync` при создании клиента (`http-client-mobile.ts:63-67`). JWT подписан симметричным ключом из кода (`libs/core/src/lib/constants.ts:7-9`), `ignoreExpiration: true` (`jwt-strategy.service.ts:13`).
5. Описание «куда проксируется» обычно есть прямо в `@ApiOperation({ description: 'proxied to: ...' })` над методом.
6. Тайм-аут запросов в монолит — `REQUEST_TIMEOUT_TO_PHP_SITE` (по умолчанию 55000 мс, `constants.ts:10-11`).

---

## 6. Интеграции

| Система | Протокол | Направление | Где в коде | Назначение |
|---|---|---|---|---|
| Монолит `12storeez-master-web` | HTTP (axios) | шлюз → монолит | `libs/core/src/lib/http-client/*`, все `*.service.ts` с `extends HttpClientMobile` | Основной бэкенд МП: заказы, возвраты, корзина, доставка, профиль, каталог |
| gRPC orders | gRPC (`orders.proto`) | шлюз → сервис | `libs/orders/grpc/` (`ORDERS_GRPC_SRV`) | Офлайн-заказы (чеки магазинов) |
| gRPC feedbacks | gRPC (`feedbacks.proto`) | шлюз → сервис | `libs/reviews/grpc/` (`FEEDBACKS_GRPC_SRV`) | Отзывы; `canBeSaved` для кнопки «Оценить» в заказе |
| Mindbox-сервис | gRPC (`mindbox.proto`) | шлюз → сервис | `libs/profile/bonus-grpc/`, `libs/profile/auth-grpc/`, `libs/notification/grpc/` (`MINDBOX_GRPC_SRV`, префикс `MINDBOX_USER_ID_PREFIX`) | Бонусы, авторизация по телефону, уведомления |
| Geo-сервис | gRPC (`geo.proto`) | шлюз → сервис | `libs/geo/grpc/` (`GEO_GRPC_SRV`, `GEO_GRPC_API_KEY`) | Страны, города, адреса |
| Meta-сервис | gRPC (`meta.proto`) | шлюз → сервис | `libs/metadata/grpc/`, `libs/stores/grpc/` (`META_GRPC_SRV`) | Магазины, «о нас», контакты |
| Slack-сервис | gRPC (`slack.proto`) | шлюз → сервис | `libs/slack/grpc/` (`SLACK_GRPC_SRV`) | Отправка сообщений из 1С в Slack |
| Usedesk-сервис | gRPC (`usedesk.proto`) | Usedesk → `usedesk-gate` → сервис | `apps/usedesk-gate/`, `libs/usedesk-gate/grpc/` | CSI-оценки поддержки |
| 1С (Enterprise) | HTTP | шлюз → 1С | `libs/gateway-1c/controllers/src/lib/enterprise1c/` (адрес захардкожен) | Товары, остатки (RU/KZ), офлайн-заказы |
| Сайт (монолит, публичный) | HTTP | 1С → шлюз → сайт | `libs/gateway-1c/controllers/src/lib/site/` (`SITE_BASE_URL`) | Загрузка товаров и остатков на сайт |
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
| Создать возврат (позиции + реквизиты) | `POST /api/orders/:order_id/return` | `POST mobile/orders/{order_id}/return` (тело — как есть; в Swagger описано только `items`) | `orders.controller.ts:254-270`, DTO `libs/orders/swagger/src/lib/orders.swagger.ts:94-99` |
| Карточка заказа | `GET /api/orders/:order_id` | `GET mobile/orders/{order_id}` + gRPC feedbacks `canBeSaved` (фильтр сообщения `can_be_marked`) | `orders.controller.ts:227-252` |
| Список заказов / отмена | `GET /api/orders`, `DELETE /api/orders` | `GET mobile/orders`, `POST mobile/orders/cancel` | `orders.controller.ts:54-86`, `272-282` |
| Способы возврата / детали возврата | **нет в этом репозитории** | — | см. §8.2 |

### 8.2. `v1/delivery/{orderId}/return-method-list` и `return-details`

**Не найдено** (на коммите `beba6e61`, а также во всей локальной истории всех веток — `git log --all -S`):
- поиск по `apps/`, `libs/` и корню: `return-method`, `returnMethod`, `ReturnMethod`, `return_method`, `return-details`, `returnDetails`, `delivery/:`, `@Controller('delivery…')`, `v1/delivery` — совпадений нет;
- контроллера с префиксом `delivery` нет — есть только `cart/delivery` и `cart/delivery2` (доставка корзины);
- шлюз публикует только `/api/...` без сегмента `v1` (`main.ts:18`, ingress `values.yaml:73-80`);
- хост этого шлюза — `core.12stz.com`, а iOS шлёт эти два запроса на `BASE_URL_NEW` = `mobile.12stz.com/api` (`knowledge/12storeez-ios/repo-map.md`, §4.3). По сваггеру нового шлюза (`knowledge/12storeez-master-web/api/mobile/mobile-gateway_swagger.yaml`) их проксирует **Mobile API Gateway** в `mobile/orders/{id}/return-method-list` / `return-details` монолита. Это подтверждено кодом нового шлюза — `12stz/mobile-monorepo-go`, см. [../mobile-monorepo-go/repo-map.md](../mobile-monorepo-go/repo-map.md) §5.

### 8.3. Прочее

| Что искать | Где |
|---|---|
| Доставка корзины, ПВЗ Boxberry | `libs/cart/controllers/src/lib/delivery*/` |
| Офлайн-заказы (чеки магазинов) | `orders.controller.ts:88-202` (gRPC orders), `libs/gateway-1c/.../offline-orders/` (1С) |
| Бонусы | `libs/profile/controllers/src/lib/bonus/`, `libs/profile/bonus-grpc/` |
| Авторизация, JWT | `libs/authorization/`, `libs/core/src/lib/jwt-strategy/` |
| Обмен с 1С | `libs/gateway-1c/` |
| Swagger шлюза | `/swagger` на хосте окружения (генерируется из декораторов, `main.ts:55-65`) |

---

## 9. Быстрые подсказки по поиску

1. **Есть ли метод в старом шлюзе:** ищи `@Controller('` (префикс) и `@Get(`/`@Post(` в `libs/*/controllers/`; итоговый путь = `/api/<префикс>/<метод>`.
2. **Куда проксируется:** `description: 'proxied to: ...'` в `@ApiOperation` и поле `path` в сервисе (`extends HttpClientMobile` → `mobile/` монолита).
3. **gRPC-зависимости:** `libs/*/grpc/src/lib/constants.ts` (env-переменная адреса) и `*.module.ts` (`protoPath`).
4. **Окружения и хосты:** `.deploy/helm/*.values.yaml`.
5. **Тесты:** `apps/mobile-api/test/*.e2e.spec.ts`, `libs/**/*.spec.ts`.

---

## 10. Неопределённости и вопросы

- [x] Где лежит код нового шлюза `mobile.12stz.com` (Mobile API Gateway), который обслуживает `v1/delivery/...`. Ответ: `12stz/mobile-monorepo-go` (10.10.2026).
- [ ] `apps/usedesk-gate` в CI не собирается — развёрнут ли он где-то ещё, из кода не видно.
- [ ] `libs/errors/grpc` (`internal/errors.proto`) — где используется, не проверялось.
- [ ] Реальные значения `PHP_BASE_URL` и gRPC-адресов на prod — в Vault (`mobile-api-vault-envs`), в репозитории их нет.

---

## История изменений

| Версия | Дата | Автор | Изменения |
|---|---|---|---|
| 1.0 | 10.10.2026 | repository-researcher | Первая версия карты по коммиту `beba6e61`; поиск `v1/delivery/{orderId}/return-method-list` и `return-details` — не найдено |
| 1.1 | 10.10.2026 | Системный аналитик | Новый шлюз `mobile.12stz.com` найден в `12stz/mobile-monorepo-go`: §1, §8.2, §10 — ссылки на его карту |
