# Структура репозитория monolith-bfb-ms

**Назначение документа:** карта-справочник по кодовой базе `monolith-bfb-ms` (Backend-for-Backend монолита) для быстрого поиска при анализе требований.

**Дата актуализации:** 25.11.2026
**Сверено с кодом:** `origin/develop` `5828b91f0b` (17.11.2026, «Merge branch 'feature/ECOMDEV-2558' into 'develop'»); `origin/master` `3a12dc5daf` (17.11.2026), в `develop` нет коммитов сверх `master`.
**Путь к коду:** `C:\Users\RobotComp.ru\Desktop\12stz\monolith-bfb-ms\` (только чтение)
**Примечание:** структура описана по фактическому содержимому папок; номера строк `file:line` — по `5828b91`. C4-диаграмма сервиса — `12stz/architecture-docs/monolith-bfb-ms/system.puml` (см. [../architecture-docs/repo-map.md](../architecture-docs/repo-map.md)).

---

## 1. Назначение и общая архитектура

- **Что это:** HTTP-прокси между монолитом `12storeez-master-web` и внутренними микросервисами (`composer.json`: «Backend for backend for monolith on oms project»). Монолит шлёт сюда REST/JSON, сервис превращает запрос в gRPC-вызов нужного микросервиса и отдаёт ответ как JSON.
- **Собственной бизнес-логики и БД нет.** Нет БД, Redis, RabbitMQ, консьюмеров и cron-задач; `bin/console` — только стандартные команды Symfony. Логика — сборка gRPC-запроса из JSON (`mergeFromJsonString` или трансформеры `src/Transformer/`) и обработка ошибок.
- **Кто вызывает:** только монолит, по двум хостам из `config/config.php:149-150` монолита:
  - `BFB_MS_HOST` — всё, кроме подарочных сертификатов;
  - `BFB_MS_GIFTCARDS_HOST` — `/giftcards/{method}` (отдельный релиз `giftcard-prod`).
  МП и шлюзы (`mobile-monorepo-go`, `esb-monorepo`) этот сервис не вызывают.
- **Прод-хост:** `monolith-bfb.12stz.com`, k8s, 3 реплики (`.deploy/helm/prod.values.yaml:30`); вход ограничен белым списком IP (по `system.puml`).
- **Стек:** PHP 8.2, Symfony 6.2 (php-fpm + nginx), gRPC (`grpc/grpc`, `google/protobuf`), Guzzle для HTTP-сервисов, Sentry, общий пакет `twelve-storeez/api-helper` 1.1.2 (ответы, ошибки, Sentry).
- **Контракты gRPC** — пакет `twelve-storeez/proto-specifications` **v1.9.27** (`composer.json`), а **не** `esb-protobufs`. В `system.puml` указана v1.9.22 — диаграмма отстаёт.

---

## 2. Корневые папки и файлы

| Путь | Назначение |
|---|---|
| `public/index.php`, `src/Kernel.php` | Точка входа Symfony |
| `src/Controller/` | **Все HTTP-маршруты** — атрибуты `#[Route]`, по контроллеру на домен (см. §3) |
| `src/Client/` | Клиенты микросервисов: gRPC-обёртки (`*Client.php`, доставка — `DeliveryGrpcClient`) и HTTP-клиент `FeedbackClient`; HTTP `DeliveryClient` не используется (§8) |
| `src/Transformer/` | JSON ↔ gRPC: `AggregateBilling/`, `Delivery/`, `Geo/`, `Mindbox/`, `Receipt/`, `Tinkoff/`, `Notifications/`, `Input/` (PATCH маркетплейса) |
| `src/Dto/` | DTO входящих запросов (Mindbox, чеки, Т-Банк, уведомления, интервалы доставки) |
| `src/Helper/` | `GrpcHelper` (вызов и JSON-ответ), `GrpcStatusHelper` (gRPC-код → HTTP), `SentryHelper` (проброс `sentry-trace`/`baggage` в gRPC-метаданные), `SerializeHelper`, `TransformHelper` |
| `src/EventSubscriber/` | `RequestSubscriber` (Sentry-трейсинг входящего запроса), `ExceptionSubscriber` (ошибки → JSON), `ResponceSubscriber` |
| `src/Common/` | `EnvEnum` (на `stg` gRPC без TLS), `PlatformEnum` |
| `src/Grpc/` | **Сгенерированные gRPC-классы — в репозитории их нет.** Создаются при старте контейнера скриптом `generate.sh` из `vendor/twelve-storeez/proto-specifications/*.proto` (`Dockerfile`: `generate.sh; php-fpm`). Пространства имён `App\Grpc\`, `GPBMetadata\`, `Orders\` (`composer.json` → `autoload`) |
| `config/services.yaml` | DI: адреса микросервисов из env `CONTAINER_*_MS`, привязка клиентов к ним |
| `config/packages/` | Настройки Symfony, monolog, Sentry, validator |
| `.env.example` | Все env-переменные с комментариями (адреса dev-стендов) |
| `.deploy/helm/` | `prod`, `stg`, `dev`, `giftcard-prod` values; адреса прод-сервисов — `prod.values.yaml:10-21` |
| `docs/swagger.yaml`, `docs/swagger.html` | Swagger сервиса; отдаётся по `/swagger` (`SwaggerController`) |
| `tests/` | PHPUnit-тесты (в граф не входят) |

---

## 3. Маршруты → микросервисы

Маршруты заданы атрибутами в `src/Controller/*.php`; отдельного `routes.yaml` нет (`config/routes.yaml` пустой).

| Маршрут | Метод | Контроллер | Куда уходит |
|---|---|---|---|
| `/aggregate-billing` | POST | `AggregateBillingController` | aggregate-billing-ms, gRPC `PaymentService.CreateOrder` |
| `/aggregate-billing/{commit,refund,cancel,info,schedule,alpha-podeli-info,yandex-pay-info,rollback}` | POST | `AggregateBillingController` | `CommitOrder`, `RefundOrder`, `CancelOrder`, `InfoOrder`, `CalculateOrder`, `AlphaPodeliInfoOrder`, `YandexPayInfoOrder`, `RollbackOrder` |
| `/receipt/sell/{prepayment,fullpayment}`, `/receipt/refund/{fullpayment,prepayment}` | POST | `ReceiptController` | receipt-ms, gRPC `ReceiptService` — чеки продажи и **возврата** |
| `/api/v1/mindbox/orders` | PUT | `MindboxOrderController:40` | mindbox-srv-go, gRPC `Order.CreateOrder` |
| `/api/v1/mindbox/orders/{orderId}` | PATCH | `MindboxOrderController:49` | `Order.UpdateOrderV2` — изменение заказа в Mindbox, в т.ч. статусов позиций |
| `/api/v1/mindbox/orders/{orderId}` | GET | `MindboxOrderController:58` | `Order.GetOrderInfo` |
| `/api/v1/mindbox/orders/calculate-{authorized,unauthorized}` | PUT | `MindboxOrderController:22,31` | `Order.CalculateAuthorized` / `CalculateUnauthorized` (заголовок `Device-uuid` → метаданные) |
| `/api/v1/mindbox/cart/recommendations`, `/api/v1/mindbox/product/recommendations` | POST | `MindboxCartController`, `MindboxProductController` | `Cart.Recommendations`, `Product.Recommendations` |
| `/api/v1/mindbox/gift/{send-code-by-email,send-code-by-sms,verify-email-code,verify-sms-code}` | POST | `MindboxGiftController` | `Gift.SendCodeByEmail`, `SendCodeBySMS`, `VerifyCode` |
| `/api/v1/mindbox/email-subscription[/status]` | POST | `MindboxUserController` | `User.OrderSubscription`, `CheckEmailSubscription` |
| `/api/v1/mindbox/mobile/{send-code,check-code,init-client,edit-user}` | POST | `MindboxMobileController` | Mindbox Mobile: `Code`, `CheckCode`, `InitClient`, `EditUser` (SMS-коды и устройство МП, вызывает монолит) |
| `/delivery/intervals` | POST | `DeliveryController:30` | logistics-monorepo-go, gRPC `WinnerService.Intervals` (Bearer `AUTHORIZATION_BEARER`) |
| `/delivery/providers/{providerId}/points[/{pointId}]` | GET | `DeliveryController:52,74` | `WinnerService.PickupList`, `PickupDetail` |
| `/offline-order/{by-guid,by-client,by-id}` | GET | `OfflineOrderController` | orders-srv-go, gRPC `Offline.GetByGuid`, `ByClient`, `GetById` |
| `/marketplace/order`, `/marketplace/order/item`, `/marketplace/order/number` | PATCH | `MarketplaceController` | marketplace-ms, gRPC `OrderService.UpdateOrderStatus`, `UpdateOrderItemStatus`, `UpdateOrderNumber` |
| `/api/v1/geo/countries…`, `/api/v1/geo/cities` | GET | `GeoController` | geo-srv-go: подсказки и детали стран, городов, адресов; страна по телефону |
| `/api/v1/notifications/send-v2` | POST | `NotificationsController` | notifications-go-ms, gRPC `SendV2` |
| `/api/v1/auth/t-bank/{login,settings,user}` | POST/GET | `TinkoffController` | auth-go-ms (`LoginTBankCode`, `GetAuthSettings`), user-go-ms (`GetByToken`) |
| `/feedback/form/{slug}` | GET/POST | `FeedbackController` | feedbacks по HTTPS (`FEEDBACK_API_URL`) |
| `/giftcards/{method}` | любой | `GiftcardsController:31` | gift-cards-ms, gRPC `GiftcardService.{method}`: `Sell`, `InfoBy*`, `TrxBy*`, `Lock`, `Unlock`, `Purchase`, конфиг; неизвестный метод — ошибка валидации |
| `/swagger` | GET | `SwaggerController` | служебный |

**Как запрос превращается в gRPC.** Mindbox-заказы и подарочные сертификаты: тело запроса монолита целиком разбирается в protobuf-сообщение (`mergeFromJsonString`, `src/Client/MindboxClient.php:62-118`, `GiftcardsController.php:78-84`) — **формат JSON задаёт proto-контракт**, BFB поля не меняет. Остальные домены — через трансформеры `src/Transformer/`.

---

## 4. Интеграции и конфигурация

| Микросервис | env-переменная | Прод-адрес (`prod.values.yaml`) | Транспорт |
|---|---|---|---|
| aggregate-billing-ms | `CONTAINER_AGGREGATE_BILLING_MS` | `aggregate-billing-ms.core-prod.svc.cluster.local:5000` | gRPC без TLS |
| gift-cards-ms | `CONTAINER_GIFTCARDS_MS` | `gift-cards-ms.core-prod.svc.cluster.local:5000` | gRPC без TLS |
| receipt-ms | `CONTAINER_RECEIPT_MS` | `receipt-ms.receipt-ms-prod.svc.cluster.local:5000` | gRPC без TLS |
| marketplace-ms | `CONTAINER_MARKETPLACE_MS` | `marketplace-ms.core-prod.svc.cluster.local:5000` | gRPC без TLS |
| logistics (winner) | `CONTAINER_LOGISTICS_MS`, `CONNECT_LOGISTICS_MS_SECURE` | `winner.logistics-monorepo-go-prod.svc.cluster.local:50051` | gRPC |
| orders-srv-go (офлайн-заказы) | `CONTAINER_ORDERS_MS`, `CONNECT_ORDERS_MS_SECURE` | `orders-srv-go-prod.orders-srv-go.svc.cluster.local:50051` | gRPC |
| mindbox-srv-go | `CONTAINER_MINDBOX_MS` | `grpc-prod.12storeez.com` | gRPC, TLS (кроме `APP_ENV=stg`) |
| notifications-go-ms | `CONTAINER_NOTIFICATIONS_MS` | `notifications-go-ms.12stz.com` | gRPC, TLS |
| auth-go-ms, user-go-ms | `CONTAINER_AUTH_MS`, `CONTAINER_USER_MS` | `auth-go-ms.12stz.com`, `user-go-ms.12stz.com` | gRPC, TLS |
| geo-srv-go | `GEO_SERVICE_HOSTNAME`, `GEO_SERVICE_API_KEY` | из Vault | gRPC, `api_key` в метаданных |
| logistics (HTTP) | `DELIVERY_API_URL` | `https://logistics.12stz.com` | HTTP (`DeliveryClient`) — в коде не вызывается, маршруты `/delivery/*` идут через gRPC `DeliveryGrpcClient` |
| feedbacks | `FEEDBACK_API_URL` | `https://feedbacks.12stz.com` | HTTP |

Секреты (`APP_SECRET`, `SENTRY_DSN`, `AUTHORIZATION_BEARER`, гео) — Vault `backend/php/oms/services/monolith-bfb-ms/prod/envs` (по `system.puml`).

---

## 5. Где монолит вызывает BFB

| Что | Код монолита (`12storeez-master-web`) |
|---|---|
| Хосты | `config/config.php:149-150` (`BFB_MS_HOST`, `BFB_MS_GIFTCARDS_HOST`) |
| Mindbox: заказы, расчёт, изменение | `src/Modules/Mindbox/Client/MindboxClient.php` (`ORDER_URL = '/api/v1/mindbox/orders'`, `:34`), `src/Modules/Mindbox/Service/MindboxService.php:197,266`, конфигуратор `di/ContainerRegister.php:1103` |
| Mindbox МП: SMS-коды, устройство | `src/Integration/Mindbox/Client/MindboxMobileClient.php` |
| Чеки | `ReceiptClient`, `di/ContainerRegister.php:878` |
| Платежи (Yandex Pay, Split, SBP, Подели) | `di/ContainerRegister.php:1216-1252` (`BFB_MS_HOST . '/aggregate-billing'`) |
| Интервалы доставки | `modules/common/client/MonolithBfbMsClient.php:35`, `DeliveryConfigurator` (`di/ContainerRegister.php:1354`) |
| Уведомления, офлайн-заказы | `di/ContainerRegister.php:1111`, `:1142` |
| Маркетплейсы | `modules/orders/services/OrderService.php:442,480,517` |
| Подарочные сертификаты | `GiftcardServiceConfigurator`, `di/ContainerRegister.php:1168` |

Подробно об интеграциях монолита — [../12storeez-master-web/architecture/08-integrations.md](../12storeez-master-web/architecture/08-integrations.md).

---

## 6. Ключевые точки для «Возвратов 2.0»

- **Статусы позиций и баллы в Mindbox.** Монолит меняет заказ в Mindbox через `PATCH /api/v1/mindbox/orders/{orderId}` → `Order.UpdateOrderV2`. BFB передаёт тело как есть, поэтому новые поля или статусы позиций — изменение контракта `proto-specifications` (`mindbox.proto`) и mindbox-srv-go, а в BFB достаточно обновить версию пакета. Маппинг статусов сайта на Mindbox (`cms_mb_statuses_map`) — в монолите, не здесь.
- **Предрасчёт баллов** — `PUT /api/v1/mindbox/orders/calculate-*` (`CalculateAuthorized`/`CalculateUnauthorized`).
- **Чеки возврата** — `/receipt/refund/{fullpayment,prepayment}` → receipt-ms.
- **Возврат денег по онлайн-оплате** — `/aggregate-billing/refund` → aggregate-billing-ms `RefundOrder`.
- **Офлайн-заказы** (возврат покупки из магазина) — `/offline-order/*` → orders-srv-go.

---

## 7. Быстрые подсказки по поиску

- Какой маршрут куда ведёт — `src/Controller/<Домен>Controller.php`, затем `src/Client/<Домен>Client.php`.
- Какие поля уходят в gRPC — сообщения в `vendor/twelve-storeez/proto-specifications/*.proto` (локально `vendor` может не быть; сгенерированного `src/Grpc/` в репозитории нет).
- Адрес сервиса на проде — `.deploy/helm/prod.values.yaml`, на dev — `.env.example`.
- Граф кода: `graphify query "<вопрос>" --graph graphify-out-12stz/monolith-bfb-ms/graph.json`. В графе нет сгенерированных gRPC-классов и тестов.

---

## 8. Неопределённости и вопросы

- Версия `proto-specifications`: в `composer.json` v1.9.27, в `system.puml` — v1.9.22. Какая выкачена на прод, по коду не определить (`composer.lock` не сверялся).
- BFB подключает `backend/php/proto-specifications`, а в `12stz` склонирован `backend/go/proto-specifications` (теги `v0.0.x`) — копия `esb-protobufs`, ушедшая вперёд (см. [../proto-specifications/repo-map.md](../proto-specifications/repo-map.md) §5). Связь PHP- и Go-репозиториев по коду не установлена.
- `DeliveryClient` (HTTP), `DeliveryDummyClient` и `DeliveryClientInterface` в `src/` никем не используются — похоже на остаток до перехода на gRPC `DeliveryGrpcClient`; `DELIVERY_API_URL` при этом остаётся в конфиге.

---

## История изменений

| Дата | Изменение |
|---|---|
| 25.11.2026 | Карта создана по `origin/develop` `5828b91` |
