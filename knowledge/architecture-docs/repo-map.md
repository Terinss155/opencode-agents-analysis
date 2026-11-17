# Структура репозитория architecture-docs

**Назначение документа:** карта-справочник по `architecture-docs` — C4-диаграммам (PlantUML) бэкенда 12Storeez. Это единственный источник в `12stz`, где описаны **сервисы, кода которых здесь нет** (gRPC-серверы `esb-protobufs`, BFF/BFB, воркеры, интеграции с 1С и внешними системами), а также полная схема БД монолита с типами колонок. Используется при постановке задач: кто владелец данных, через какой сервис идёт вызов, какие очереди и cron затронуты.

**Дата актуализации:** 06.11.2026
**Сверено с репозиторием:** ветка `main`, коммит `874cecd` (`874cecd3be9e5b1bfe9941bf6ad3803663151b69`, 12.10.2026, «Merge branch 'feature/architecture_2026_10'»)
**Код:** `C:\Users\RobotComp.ru\Desktop\12stz\architecture-docs\` (только чтение). Remote: `gitlab.12storeez.com/backend/architecture-docs`
**Примечание:** это **документация, а не код**. Диаграммы написаны командой бэкенда по коду и Helm на начало октября 2026; часть связей помечена в самих диаграммах «не проверено по коду». Для AS-IS-логики в задаче диаграмма — подсказка, где искать; факт подтверждается кодом (`12storeez-master-web`, `mobile-monorepo-go`, `esb-monorepo`) или вопросом команде.

---

## 1. Как пользоваться при написании задач

| Шаг постановки | Что брать из `architecture-docs` |
|---|---|
| Выбрать, где делать доработку (монолит, BFB, сервис) | §3 — кто владелец данных и какой сервис уже обслуживает похожий вызов. Ориентир TO-BE — §5 (новое не тащим в Yii2 без нужды, учёт — в 1С) |
| Описать цепочку вызова и «Связи» задачи | `system.puml` нужного сервиса: `Rel(...)` — кто кого вызывает, протокол, метод; `AddProperty` — маршруты, gRPC-методы, env-переменные адресов |
| Сверить имена и типы колонок MariaDB | `monolith/database.puml` — 279 таблиц с типами и комментариями (§4). Дополняет ERD проекта и `knowledge/12storeez-master-web/database/` |
| Указать очереди, cron, outbox/inbox | `monolith/queue.puml`, `<сервис>/queue.puml`, блоки Workers / CronJob в `system.puml` (расписание prod и команда запуска) |
| Внешние системы и их документация | `System_Ext(..., $link=...)` — ссылки на API-доки (Долями, Подели, Yandex Pay, CDEK, Mindbox и др.) |
| Отметить устаревшее / мёртвое | `monolith/readme.md` — статусы интеграций 🟢 / 🟡 / 🔴 |
| «Открытые вопросы» | §7 — что в диаграммах заглушка или не проверено |

Не указывать в задаче пароли и prod-секреты (регламент README репозитория): только имя env-переменной или путь Vault.

---

## 2. Корневые папки и файлы

Регламент репозитория (`README.md`): на сервис — папка; `system.puml` (C2/C3: контейнеры сервиса + интеграции), `database.puml` (автогенерация из IDEA), `queue.puml` (vhost, exchanges, queues). Внутренние системы ссылаются на `../<сервис>/system.puml`, внешние — на документацию интеграции. Рендер — плагин PlantUML для VS Code + Java + Graphviz.

| Папка | Что внутри | Полнота |
|---|---|---|
| `acrhitecture_10_2026/` (sic) | `summary.md`, `compare.md`, `people.md` — TO-BE архитектура 08.10.2026 (§5) | текст |
| `monolith/` | `readme.md` (входящие/исходящие интеграции со статусами), `system.puml`, `database.puml` (3 836 строк), `queue.puml` | **подробно** |
| `monolith-bfb-ms/` | `system.puml` — маршруты HTTP → gRPC | **подробно** |
| `mobile-monorepo-go/` | `system.puml` — группы маршрутов `/api/v1/*` и их источники | **подробно** |
| `feedbacks/` | `system.puml`, `database.puml` (101 таблица), `queue.puml` | **подробно** |
| `stocks-monorepo-go/` | `system.puml`, `database.puml` (20), `queue.puml` | **подробно** |
| `logistics-monorepo/` | `system.puml`, `database.plantuml` (43) | **подробно** |
| `mindbox-srv-go/` | `system.puml`, `database.puml` (2) | **подробно** |
| `geo-srv-go/` | `system.puml`, `database.puml` (7) | **подробно** |
| `orders-srv-go/` | `system.puml`, `database.puml` (4) | **подробно** |
| `aggregate-billing-ms/` | `system.puml` | **подробно** |
| `auth-go-ms/`, `user-go-ms/`, `file-go-ms/`, `assets-srv-go/`, `passwork-go-ms/`, `meta-srv-go/` | `system.puml` (+ `database.puml` у user, assets, meta) | кратко, старый формат |
| `gift-cards-ms/`, `receipt-ms/`, `marketplace-ms/`, `notifications-go-ms/`, `mattermost-go-ms/`, `oms-bff-ms/`, `rest-srv-go/`, `mobile-api/`, `workers-go-v3/` | `system.puml` | **заглушка** («...») — смотреть описание у вызывающих (`monolith-bfb-ms`, `monolith`) |
| `reviews/` | `system.puml` | шаблон («Description goes here») |

---

## 3. Сервисы: роль, адрес, кто вызывает

Адреса — как в диаграммах (prod). Протокол «gRPC (TLS)» через общий ingress `grpc-prod.12storeez.com:443` с IP whitelist; «insecure» — внутри кластера `*.svc.cluster.local`.

### 3.1. Монолит и прослойки

| Сервис | Что это | Адрес | Кто вызывает → что |
|---|---|---|---|
| **monolith** (`12storeez-master-web`) | Yii2, PHP 8.2, Vue 2.7-острова, MariaDB 10.3, Redis, RabbitMQ, Elastic, S3. Контейнеры: `web-monolith` (3 реплики), `web-monolith-admin` (`admin.12storeez.com/cms`), `web-monolith-mobile` (только кластер, для `mobile/*`), `web-monolith-images`, воркеры (~45 RabbitMQ-консьюмеров, ~25 SQL-очередей, ~120 cron) | `12storeez.com`, `admin.12storeez.com` | Входящие — `monolith/readme.md` «Входящие точки»: Vue, шлюзы МП, stocks, marketplace, 1С, RetailCRM, Mindbox, платёжки, ATOL, logistics. Авторизация service-to-service на `/api2/*`, `/api/*` — `?token=` |
| **monolith-bfb-ms** | Backend-for-Backend монолита: HTTP → gRPC прокси, Symfony 6.2, 3 реплики | `monolith-bfb.12stz.com` (`BFB_MS_HOST`) | Монолит (web + воркеры). Маршруты: `/giftcards/*` → gift-cards-ms; `/aggregate-billing*` → aggregate-billing-ms; `/receipt/sell/*`, `/receipt/refund/*` → receipt-ms; `/marketplace/order*` → marketplace-ms; `/delivery/intervals`, `/delivery/providers/{id}/points` → logistics `WinnerService`; `/offline-order/*` → orders-srv-go; `/api/v1/geo/*` → geo-srv-go; `/api/v1/mindbox/*` → mindbox-srv-go; `/api/v1/notifications/send-v2` → notifications-go-ms; `/api/v1/auth/t-bank/*` → auth-go-ms, user-go-ms; `/feedback/form/{slug}` → feedbacks |
| **oms-bff-ms** | PHP-прокси (диаграмма-заглушка) | `oms.bff.12stz.com` | Монолит: `/aggregate-billing` (только Долями, TODO перевести на BFB), формы отзывов `/form/{name}` |
| **mobile-monorepo-go** | Новый шлюз МП (Go, Fiber), выпускает JWT | `mobile.12stz.com` | Приложение. `/api/v1/auth` → монолит + auth-go-ms; `/geo` → geo-srv-go; `/metadata` → meta-srv-go + монолит; `/delivery` → logistics (intervals) + **монолит (types, return)**; `/pickup` → logistics HTTP; `/users` → mindbox-srv-go (бонусы) + монолит; корзина, каталог, заказы, оплаты, подарочные карты, профиль, отзывы → монолит. В монолит: `SITE_BASE_URL` (`mobile/*`, `mobile/v2/*`, `mobilev2/*`, `api/metadata/*`) и `SITE_BASE_INTERNAL_URL`; заголовки `X-Access-Token`, `X-Session-Token` |
| **esb-monorepo** (`mobile-api`) | Старый шлюз МП `core.12stz.com` (Node), помечен deprecated | `core.12stz.com` | Диаграмма-заглушка; связи — в диаграммах feedbacks, meta, orders, mindbox. Подробно — `knowledge/esb-monorepo/repo-map.md` |
| **rest-srv-go** | Старый Go-прокси ESB (deprecated) | `internal.core.12stz.com` | Монолит: `/api/v1/store/feedback/*` (отзывы о магазинах) |

### 3.2. Заказы, оплата, чеки

| Сервис | Что это | Адрес | Методы и вызывающие |
|---|---|---|---|
| **aggregate-billing-ms** | Платёжный шлюз BNPL / Yandex: RoadRunner gRPC + PHP 8.2 Symfony, без БД и очередей | `aggregate-billing-ms.core-prod.svc.cluster.local:5000`, proto `app.grpc.billing.PaymentService` (репозиторий `backend/php/proto-specifications`) | `CreateOrder`, `CommitOrder`, `CancelOrder`, **`RefundOrder`**, `RollbackOrder`, `InfoOrder`, `AlphaPodeliInfoOrder`, `YandexPayInfoOrder`, `CalculateOrder`. Платёжки: Долями (T-Bank, mTLS), Подели (Альфа, mTLS), Yandex Split / Pay / СБП. Вызывают monolith-bfb-ms (Подели, Yandex) и oms-bff-ms (Долями). Колбэки платёжек идут прямо в монолит |
| **receipt-ms** | Фискальные чеки (заглушка) | `receipt-ms.receipt-ms-prod.svc.cluster.local:5000` | `SellPrepaymentReceipt`, `SellFullpaymentReceipt`, **`RefundPrepaymentReceipt`, `RefundFullpaymentReceipt`** — через BFB `/receipt/*`. Включается в монолите флагом `USE_RECEIPT_MS=true` (консьюмер `receipt-outbox/handle`, очередь `send-receipts`); иначе монолит пробивает чеки напрямую в ATOL Online v5 |
| **orders-srv-go** | Офлайн-чеки магазинов (сервер `orders.proto`), только чтение PG | `orders-srv-go-prod.orders-srv-go.svc.cluster.local:50051`; ingress `grpc-prod.12storeez.com` | `Offline/ByClient`, **`ByClientWithReturns`** (чеки + возвраты), `GetById`, `GetByGuid`, `GetPurchaseAmountByClient` (продажи минус возвраты); `Online/ByClient` — заглушка. Вызывают: монолит (ЛК), BFB `/offline-order/*`, stocks (Mercaux), esb-monorepo. Таблицы `public.orders_offline`, `public.offline_orders` заполняют cron 1С КА / Цветной (по старой документации — workers-go-v3) |
| **gift-cards-ms** | Подарочные сертификаты (заглушка) | `gift-cards-ms.core-prod.svc.cluster.local:5000` | Через BFB `/giftcards/{method}` (`BFB_MS_GIFTCARDS_HOST`): `Sell`, `InfoBy*`, `TrxBy*`, `Lock`, `Unlock`, `Purchase`, конфиги |
| **marketplace-ms** | Маркетплейсы (Lamoda), заглушка | `marketplace-ms.core-prod.svc.cluster.local:5000` | Монолит → BFB `/marketplace/order*` → `OrderService.UpdateOrderStatus / UpdateOrderItemStatus / UpdateOrderNumber`; marketplace-ms → монолит `/api2/orders/create-from-lamoda`, `notification-from-lamoda`; stocks → `GetSKU`, `UpdateStocks` |

### 3.3. Клиенты, авторизация, лояльность

| Сервис | Что это | Методы и вызывающие |
|---|---|---|
| **mindbox-srv-go** | Прокси gRPC → Mindbox API v3 / Maestra (ОАЭ, Кувейт), лимиты отправки кодов (PG `mindbox.send_limit`) | `User.*`, `Mobile.*` (коды, устройства, push), `Order.*` (расчёт, создание, офлайн), `Gift.*`, `Cart/Product.Recommendations`, `Offline.*` (в т.ч. **`Offline.Return`**), `ModernRetail.*`, `ReviewsAuth.*`. Вызывают: монолит (`Mobile.Code/CheckCode` — SMS), BFB `/api/v1/mindbox/*`, mobile-monorepo-go (бонусы), esb-monorepo, кассы 1С Розница / Modern Retail, Mercaux, feedbacks-tg-bot, CRM. Читает MariaDB `cms_users_user` |
| **auth-go-ms** | Авторизация (Keycloak), T-Bank ID | `GetAuthSettings`, `LoginTBankCode` — mobile-monorepo-go, BFB; CRM через crm-bff-ms |
| **user-go-ms** | Пользователи в PG ESB, cron `users_sync` из MariaDB | `user.GetByToken` — BFB; CRM. Диаграмма старого формата |
| **Keycloak** | `keycloak-beige.12stz.com` | Авторизация админок: логистика, отзывы, CRM |

### 3.4. Логистика, гео, остатки

| Сервис | Что это | Ключевое |
|---|---|---|
| **logistics-monorepo** (`logistics-monorepo-go`) | Админка логистов (Angular + `logistics`, gRPC/HTTP `logistics.12stz.com/api/v1`, Keycloak), **`winner`** (МРП: расчёт доставки, 8 реплик, кэш 5 мин), `logistics-bff-ms`, cron-воркеры ПВЗ | `WinnerService.Calculate / Intervals / PickupList / PickupDetail / AddressDetails`. Вызывают: BFB (`Intervals`, `PickupList`, `PickupDetail`), mobile-monorepo-go (`Intervals` по gRPC, ПВЗ по HTTP). Воркеры: ПВЗ Boxberry, 5Post, ApiShip, Yandex, CDEK; сроки ТК (SDT, CSE); нормализация адресов через geo; → монолит `POST /api/v1/delivery/webhooks/city-carriers-coverage`, `GET /api/stores/get-busy-points`. Ошибки — в Mattermost через notifications-go-ms |
| **geo-srv-go** | Страны, города, адреса: RU → Dadata, остальные → Google; город по IP — MaxMind | `geo.Geo` (`Suggest*`, `*Details*`, `CityDetailsByIP`, `CountryDetailsByPhone`, `DefaultCityList`), auth metadata `api_key`. Вызывают: mobile-monorepo-go, BFB `/api/v1/geo/*`, logistics. Монолит сам geo не вызывает — только через BFB |
| **stocks-monorepo-go** | Остатки и номенклатура из 1С (HTTP `Prod_Marking/hs/...`) → PG `catalog.*` → RabbitMQ → сайт; Mercaux (планшет продавца); Shopify KZ / Global; маркетплейсы | cron `catalog_stocks` (каждые 2 мин), `catalog_nomenclature` (раз в час), `site_stocks_sync`, `site_catalog_sync`, `mercaux_*`, `marketplace_stocks_push`, `shopify_*`. Остатки в монолит: consumer `delta.esb` → `POST /api2/stocks/esb`. Номенклатура: exchange `nomenclature` → очередь монолита `product` (`php yii exchange/import`). Mercaux создаёт заказ через `POST /api2/orders/create` |
| **meta-srv-go** | Контакты, «о компании», магазины для МП (probably deprecated) | `Mobile.Contacts / About`, `Stores.*` — esb-monorepo, mobile-monorepo-go |

### 3.5. Отзывы, уведомления, файлы

| Сервис | Ключевое |
|---|---|
| **feedbacks** (`feedbacks-monorepo-go`) | Портал отзывов `feedbacks.12stz.com` (API, WS, loader, BFB для форм), gRPC `feedbacks-ms` (`feedbacks.Mobile`, `feedbacks.Store`), Telegram-бот, 5 консьюмеров, 13 cron (отзывы сайта из `cms_feedbacks`, карты, AppFollow, Lamoda, Instagram, Mango, Sherlock). Пишет в Mattermost, Yandex Tracker (через yandex-go-ms), читает 1С (продуктовые команды) |
| **notifications-go-ms** | gRPC `notifications.SendV2` → Mattermost; вызывают BFB, logistics, stocks, feedbacks, mindbox. Монолит шлёт через очередь `notifications-ms.send.mattermost.v1.command` → BFB. Диаграмма-заглушка |
| **mattermost-go-ms** | Посты и файлы Mattermost (заглушка) |
| **file-go-ms** | Файлы в SberCloud S3 (`file-go-ms.12stz.com`) для feedbacks, notifications, assets, onec-bfb-ms |
| **assets-srv-go** | Кропы изображений `assets.12stz.com` за CDN `assets.12storeez.com` |
| **passwork-go-ms** | Интеграция 1С ↔ Passwork через onec-bfb-ms |

Упоминаются, но папок нет: `crm-bff-ms`, `onec-bfb-ms`, `order-go-ms`, `yandex-go-ms`, `logistics-bff-ms` (отдельные репозитории).

---

## 4. Схемы БД

| Файл | БД | Что полезно для задач |
|---|---|---|
| `monolith/database.puml` | MariaDB `12stz_production` | **279 таблиц с типами и комментариями колонок** + связи (`-[...]-^ ... : "fk:id"`). Возвраты: `cms_order_return_positions` (`return_quid varchar(36)`, FK на `cms_orders`, `cms_order_positions`), `cms_order_position_refunds` (`refunded_at`, `return_quid` — из 1С), `cms_order_position_require_refund_receipts` (`processing_type enum('refund-dolyame','refund-fullpayment','refund-podeli')`), `cms_order_return_statuses_wms`, `cms_return_method`, `cms_return_reasons*`, `cms_return_details_config` (`return_delay`, `return_dates_count`, `return_time_limit`), `cms_users_refund`; поля `return_*` в `cms_orders` (`return_status_wms`, `return_order_num`, `return_delivery_tk`, `return_delivery_method`, `return_money`, `return_store`, `return_reason`, `return_city/address/postal/date/interval`). Поиск: `class <таблица> {` |
| `feedbacks/database.puml` | PG ESB, схемы `feedbacks`, `csi`, `sherlock`, `portal`, … | 101 таблица |
| `logistics-monorepo/database.plantuml` | PG ESB, схема `logistics` | 43 таблицы: ТК, режимы, зоны, ограничения, ПВЗ провайдеров, `winners_cache` |
| `stocks-monorepo-go/database.puml` | PG ESB, `catalog`, `mercaux`, `site` | 20 таблиц: товары, размеры, цены, остатки, магазины (`catalog.stores` — общий справочник магазинов) |
| `orders-srv-go/`, `geo-srv-go/`, `user-go-ms/`, `mindbox-srv-go/`, `meta-srv-go/`, `assets-srv-go/` | PG ESB | 1–7 таблиц |

Схема монолита — автогенерация из IDEA, дата генерации в файле не указана; типы сверять с миграциями монолита, если от них зависит логика.

---

## 5. TO-BE архитектура (`acrhitecture_10_2026/`, 08.10.2026, на утверждении)

Авторы — М. Пестов, А. Осипенко. Статус — **предложение для утверждения**, не принятое решение.

- **Принцип:** «учёт — 1С, канал — свой стек, граница — контракт». Каждая учётная система получает адаптер с OpenAPI; КД3 — только между базами 1С.
- **Мастер-данные:** заказ — OMS в 1С:УТ; остатки и резерв — `stocks-ms` (SLA 99,9%); номенклатура — МДМ; клиент — `user-ms` + региональное хранилище ПДн. Ecom учётными данными не владеет.
- **Ecom:** Yii2 → Laravel по доменам (Strangler Fig), Nuxt SSR, Android на Capacitor + Vue 3, iOS остаётся на Swift, mobile-bff на Go.
- **Регионы:** новый регион стартует на Shopify.
- **Вехи:** Q1 2027 — фаза 0, user-ms и API stocks-ms; октябрь 2027 — корзина, чекаут и заказы на новой платформе; июнь 2028 — запуск 1С:УТ; декабрь 2028 — Yii2 и MariaDB выключены.
- `compare.md` — сравнение четырёх вариантов TO-BE по 8 критериям; `people.md` — найм под миграцию.

**Для задач:** если доработка затрагивает корзину, чекаут, заказы, остатки или клиента — учитывать, что эти домены в 2027 уходят из Yii2. Крупную новую логику в монолите стоит отметить в «Открытых вопросах» (делать в Yii2 или сразу в целевом сервисе) — решение за командой, не за аналитиком.

---

## 6. Ключевые точки по процессам

### 6.1. Возврат товара (Возвраты 2.0)

| Что | Где в `architecture-docs` |
|---|---|
| Методы возврата МП на новом шлюзе | `mobile-monorepo-go/system.puml`: `/api/v1/delivery` — «monolith (types, return)»; интервалы — logistics `WinnerService.Intervals` |
| Интервалы и ПВЗ для курьера / ПВЗ на возврат | Сайт: монолит → BFB `/delivery/intervals`, `/delivery/providers/{id}/points` → `WinnerService`. МП: напрямую в `winner` |
| Возврат денег по BNPL / Yandex | `aggregate-billing-ms` `RefundOrder`; очереди монолита `to.{dolyame,podeli,split,yandex-pay,yandex-sbp}.payment.v1.command` (`monolith/queue.puml`) |
| Чек возврата | BFB `/receipt/refund/*` → receipt-ms `RefundPrepaymentReceipt / RefundFullpaymentReceipt` при `USE_RECEIPT_MS=true`, иначе ATOL v5; таблица `cms_order_position_require_refund_receipts` |
| Возврат по YooKassa (карта) | Монолит ↔ api.yookassa.ru напрямую (`monolith/readme.md`) |
| Возвраты из 1С и статусы WMS | 1С → монолит `POST /api2/orders/{status,track,update-status,order-update}` → inbox `from.onec.order.update.v1.command`; таблицы `cms_order_position_refunds`, `cms_order_return_statuses_wms` |
| Передача заказа / возврата в 1С, RetailCRM, Mindbox | Outbox: `to.onec.order.*`, `to.rcrm.order.*`, `mindbox.order.*` (`monolith/queue.puml`); 1С — SOAP `loadOrder` |
| Офлайн-возвраты (магазины) | orders-srv-go `ByClientWithReturns`, mindbox-srv-go `Offline.Return` |
| Магазины для возврата | `catalog.stores` (stocks-monorepo-go, PG ESB) и логистика `StoreService`; на сайте — данные монолита |

### 6.2. Прочее

| Что искать | Где |
|---|---|
| Через какой сервис монолит ходит во внутренние системы | `monolith/system.puml` блок «Внутренние системы» (пути `BFB_MS_HOST`) |
| Все внешние интеграции монолита и живы ли они | `monolith/readme.md` (🟢/🟡/🔴) |
| Очереди монолита: RabbitMQ и SQL queue, консьюмеры | `monolith/queue.puml` |
| Остатки на сайте: откуда и как часто | `stocks-monorepo-go/system.puml`, `queue.puml` |
| Способы доставки, зоны, ограничения | `logistics-monorepo/system.puml`, `database.plantuml` |
| Платёжки BNPL, эндпоинты, колбэки | `aggregate-billing-ms/system.puml` |
| SMS-коды, бонусы, Mindbox-операции | `mindbox-srv-go/system.puml` (список операций `/operations/sync`) |
| Отзывы о заказе / магазине из МП | `feedbacks/system.puml` (`feedbacks.Mobile`) |

---

## 7. Неопределённости и вопросы

- [ ] Заглушки без содержания: `receipt-ms`, `gift-cards-ms`, `marketplace-ms`, `notifications-go-ms`, `mattermost-go-ms`, `oms-bff-ms`, `rest-srv-go`, `mobile-api`, `workers-go-v3`, `reviews`. Методы известны только со стороны вызывающих (BFB, монолит).
- [ ] Значение флага `USE_RECEIPT_MS` в prod (receipt-ms или ATOL напрямую) по диаграммам не установить — в Vault.
- [ ] `esb-monorepo` в `monolith/system.puml` — «актуальность уточнить», в `mindbox-srv-go` — deprecated; в iOS он ещё используется (`knowledge/12storeez-ios/repo-map.md` §5.1).
- [ ] Кто заполняет `orders_offline` (workers-go-v3) — «кодом не подтверждено».
- [ ] `user-go-ms`, `auth-go-ms`, `file-go-ms`, `assets-srv-go`, `passwork-go-ms` — диаграммы старого формата, без методов и даты сверки.
- [ ] Дата генерации `monolith/database.puml` неизвестна; новые таблицы после неё могут отсутствовать.

---

## История изменений

| Версия | Дата | Автор | Изменения |
|---|---|---|---|
| 1.0 | 06.11.2026 | Claude | Первая версия карты по коммиту `874cecd`: сервисы, BFB-маршруты, БД, очереди, TO-BE, точки по возвратам, порядок использования в задачах |
