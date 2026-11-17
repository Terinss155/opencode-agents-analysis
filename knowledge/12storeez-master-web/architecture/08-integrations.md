# Внешние интеграции

> Сверено с `origin/develop` `dd4a997ac0`, 07.11.2026 (шлюзы: `mobile-monorepo-go` и
> `esb-monorepo` — `origin/master`). Значения секретов и прод-адреса из Vault не проверялись.

## Сводная таблица

| Система | Назначение | Протокол | Направление | Где код |
|---|---|---|---|---|
| **Mindbox** | CRM, лояльность, бонусы, рассылки, рекомендации | REST напрямую в `api.mindbox.ru` + REST через BFB MS + gRPC + события через RabbitMQ | Двустороннее | `components/MindboxComponent.php` (прямой REST), `src/Modules/Mindbox/` (клиент BFB, outbox, выключатель), `src/Integration/Mindbox/` (мобильное устройство и SMS-коды приложения через BFB, ECOMDEV-2342), `modules/mindbox/services/` (gRPC-обёртки), `modules/grpc/Mindbox/` (сгенерированные стабы) |
| **RetailCRM** | Заказы, клиенты, скидки, VIC-импорт | REST | Двустороннее | `modules/retailCrm/`, `src/Modules/Rcrm/` |
| **1С** | Номенклатура, остатки, заказы, сертификаты | SOAP + вебхуки | Двустороннее | `src/Modules/OneC/` (каталога `modules/onec/` не существует) |
| **Lamoda** | Маркетплейс-заказы | REST | Двустороннее | `modules/api2/controllers/OrdersController.php` (`actionCreateFromLamoda`), `modules/orders/services/LamodaOrderOutboxService.php`, `src/Modules/Order/Services/LamodaOrderService.php` (каталога `src/Modules/Lamoda/` не существует) |
| **Mercaux** | Офлайн-заказы в магазинах | REST | Входящее | `modules/api2/`, `OrderMethodEnum::MERCAUX` |
| **YooKassa** | Оплата картой | REST | Двустороннее | `modules/yandex/` |
| **Yandex Pay** | Оплата | REST через биллинг-МС | Двустороннее | `src/Integration/Payment/YandexPay/` |
| **Yandex Split** | Рассрочка | REST через биллинг-МС | Двустороннее | `src/Integration/Payment/YandexSplit/` |
| **Yandex SBP** | Оплата по СБП | REST через биллинг-МС | Двустороннее | `src/Integration/Payment/YandexSbp/` |
| **Tinkoff Dolyame** | Оплата долями | REST через биллинг-МС (`AGGREGATE_BILLING_MS_URL`) | Двустороннее | `modules/payment/components/Dolyame.php`, клиент `modules/payment/clients/DolyameClient.php:234-237`, вебхук `modules/payment/controllers/TinkoffController.php` (`/payment/tinkoff/status`, на nginx — allow-список IP Т-Банка) |
| **Alpha Podeli** | Оплата долями | REST через биллинг-МС (`BFB_MS_HOST/aggregate-billing`) | Двустороннее | `src/Modules/Payment/Components/Podeli.php`, клиент `src/Modules/Payment/Clients/AlphaPodeliClient.php:153`, конфигуратор `src/Integration/Payment/AlphaPodeli/Configurator.php`, вебхук `modules/payment/controllers/AlphaPodeliController.php` |
| **ATOL** | Фискализация чеков | REST | Исходящее | `src/Modules/Receipt/`, `modules/atol/` |
| **LifePay** | Фискализация (легаси) | REST | Исходящее | `modules/lifepay/components/Lifepay.php` (компонент), `modules/orders/jobs/LifepayJob.php`, консоль `lifepay` |
| **Boxberry** | ПВЗ и доставка | REST | Двустороннее | `modules/delivery/`, консоль `boxberry` |
| **Accord Post** | ПВЗ и доставка | REST | Двустороннее | `modules/delivery/`, консоль `accord` |
| **DaData** | Подсказки адресов, ФИАС | REST | Исходящее | `components/Dadata.php` |
| **Яндекс.Геокодер** | Геокодирование (несмотря на название класса) | REST | Исходящее | `components/Geocode.php` (`APIURL` — `geocode-maps.yandex.ru`, а не Google) |
| **Google Geocode** | Резервное/альтернативное геокодирование | REST | Исходящее | `components/Google.php` (`maps.googleapis.com/maps/api/geocode/json`) |
| **IpGeoBase** | Гео по IP | Файловый парсинг | Входящее | консоль `ipgeobase-parse` |
| **Diginetica** | Поиск, подсказки, трекинг | REST + JS | Двустороннее | `modules/diginetica/`, `frontend/src/modules/diginetica/` |
| **Elasticsearch** | Поиск по каталогу | HTTP | Двустороннее | `src/Search/Elastic/` |
| **Flomni** | Онлайн-чат | JS-виджет | Клиентское | `themes/basic/views/layouts/parts/marketing/` |
| **Garderobo** | Подбор образов | REST + JS | Двустороннее | `src/Modules/Feed/Service/GarderoboFeedService.php` (сервер), `frontend/src/modules/garderobo/` + `frontend/src/layouts/base/workspace/garderoboService.js` (клиент) |
| **Dresscode** | Стилистические подборки (фид) | REST | Исходящее | `src/Modules/Feed/Service/DresscodeFeedService.php`, `Extractors/Xml/DresscodeFeedExtractor.php` (сервер; отдельного `src/Modules/Dresscode/` не существует), `frontend/src/modules/dresscode/services/DresscodeService.js` (клиент) |
| **AppsFlyer** | Мобильная атрибуция | JS Smart Script | Клиентское | `frontend/src/layouts/base/workspace/smartScriptService.js`, `frontend/src/modules/smart-script/services/SmartScriptService.js` |
| **Admitad, GdeSlon** | Партнёрские программы | REST + фиды | Исходящее | `components/Admitad.php`, `GdeSlon.php` |
| **Criteo, VK, Google, Яндекс** | Реклама и ретаргетинг | Фиды + JS | Исходящее | `modules/feed/extractors/` |
| **PopMechanic** | Сбор контактов | REST | Входящее | `PopmechanicController` |
| **Mattermost** | Оповещения команды | Через Notifications MS (не прямой webhook) | Исходящее | `src/Modules/Notifications/Console/NotificationsController.php` (`notifications-console/send-mattermost`) → `NotificationsClient->sendV2()` |
| **S3** | Хранение изображений | S3 API | Двустороннее | `src/Common/S3/Configurator.php`, загрузка — `src/Modules/Product/Console/ImageS3ExportController.php`, очередь `RabbitMqQueueName::IMAGE_S3_UPLOAD` |
| **Sentry** | Мониторинг ошибок | HTTPS | Исходящее | `src/Monitoring/Sentry/` |
| **Prometheus** | Метрики | Pull `/metrics` | Входящее | `src/Modules/Metrics/` |
| **SMS-коды авторизации** | Отправка через Mindbox, не отдельный SMS-провайдер | gRPC (сайт), REST через BFB MS (приложение) | Исходящее | Сайт: `src/Modules/Auth/Client/MindboxClient.php` → `MindboxGrpcService::sendCode()` → `MobileClient->Code()`. Приложение (с ECOMDEV-2342, перенос входа из esb): `src/Auth/Client/MindboxPhoneCodeClient.php` → `src/Integration/Mindbox/Client/MindboxMobileClient.php` → BFB `/api/v1/mindbox/mobile/send-code`, `check-code` |
| **reCAPTCHA / Яндекс SmartCaptcha** | Защита форм | REST + JS | Двустороннее | `src/Integration/Captcha/`, `frontend/src/modules/captcha/` |
| **Huntflow** | HR, вакансии | REST | Исходящее | `components/Huntflow.php`, `config/common.php` |
| **5Post / ApiShip** | Доставка (провайдер) | REST | Двустороннее | `DELIVERY_PROVIDER=apiship_fivepost` в `.env.example`, `src/Modules/Delivery/Dictionary/ProviderNameDictionary.php::FIVEPOST` |
| **MaxMind** | Гео по IP (наравне с IpGeoBase) | Локальная БД GeoIP | — | `src/Modules/Geo/MaxMind/Service/MaxMindService.php`, используется в `src/Modules/Geo/Common/Service/GeoService.php` |
| **Notifications MS** | Отправка уведомлений (в т.ч. в Mattermost) | REST/HTTP | Исходящее | `src/Modules/Notifications/Client/NotificationsClient.php` |
| **Marshrut, SDT** | Доставка (легаси-провайдеры) | REST | Двустороннее | `modules/delivery/components/`, регистрация в `config/common.php` |
| **Giftcards MS** | Подарочные сертификаты | REST | Двустороннее | `modules/giftcards/`, `BFB_MS_GIFTCARDS_HOST` |
| **Yandex Tracker** | Внутренний трекер задач (используется в мобильном профиле) | REST | Исходящее | `src/Modules/YandexTracker/`, `src/Modules/Mobile/Controllers/ProfileController.php` |
| **PlatformCraft** | Внешний счётчик/сервис | — | — | `components/PlatformCraft.php`, регистрация в `config/web.php` и `config/console.php` |

## Внутренние микросервисы

Монолит обращается к ним как клиент. Не все связи — gRPC: часть клиентов ходит по REST через
общий хост `BFB_MS_HOST`, а не по отдельным gRPC-каналам, как можно было бы предположить по
аналогии с Mindbox/Feedbacks/Orders.

| Микросервис | Реальный клиент в DI | Протокол | Назначение |
|---|---|---|---|
| Биллинг (aggregate-billing) | `Application\Integration\Payment\Yandex*\Client\BillingMsClient` (три конфигуратора, не единый `BillingMsClient::class`-синглтон) и `AlphaPodeliClient` — все на `BFB_MS_HOST . '/aggregate-billing'` (`di/ContainerRegister.php:1258-1304`); `DolyameClient` — на отдельный `AGGREGATE_BILLING_MS_URL` (с `todo` перевести на конфигуратор и BFB) | REST | Платежи Yandex Pay / Split / SBP, Подели, Долями |
| Чеки | `Application\Modules\Receipt\Client\ReceiptClient` (хост `BFB_MS_HOST`, не отдельный `ReceiptMsClient`) | REST | Фискальные чеки |
| BFB MS | `MonolithBfbMsClient` (интервалы доставки), `modules/orders/services/OrderService.php:442-517` (`/marketplace/order*`), `NotificationsClient`, `OfflineOrderClientConfigurator` — все на `BFB_MS_HOST` | REST | Интервалы доставки, маркетплейсы, уведомления, офлайн-заказы |
| Mindbox через BFB | `src/Modules/Mindbox/Client/MindboxClient.php` (`/api/v1/mindbox/orders`, `calculate-*`, рекомендации, подписка, подарочные коды), `src/Integration/Mindbox/Client/MindboxMobileClient.php` (`/api/v1/mindbox/mobile/send-code`, `check-code`, `init-client`); хост — `BFB_MS_HOST`, таймаут — `MINDBOX_TIMEOUT` (`MindboxConfigurator`, `di/ContainerRegister.php:1137`) | REST | Заказы и расчёт лояльности, SMS-коды и привязка устройства приложения |
| Отзывы | `Feedbacks\MobileClient` (зарегистрирован, но по коду не вызывается — используется только в DI); портал отзывов ходит через отдельный HTTP `FeedbackClient` (`FEEDBACK_BASE_URL`), а не через `PortalFeedbackServiceClient` (тот — неиспользуемый gRPC-стаб) | gRPC / HTTP | Отзывы |
| Orders MS | `Orders\OfflineClient` | gRPC | Офлайн-заказы |
| Mindbox MS | `Mindbox\MobileClient`, `UserClient` | gRPC | Авторизация на сайте (`Code`, `CheckCode`), лояльность |

**Важная деталь:** у gRPC-клиентов (`MobileClient`, `Feedbacks\MobileClient`, `OfflineClient`,
`UserClient`) в DI нет отдельных переменных на каждый сервис — все они настроены через один
общий `$params['GRPC_GEO_HOSTNAME']` (см. `di/ContainerRegister.php`), то есть в `.env.example`
это выглядит как единая секция `#> Microservices → Geo` (`GRPC_GEO_*`), а не набор
`MINDBOX_MS_*` / `ORDERS_MS_*` / `FEEDBACKS_MS_*`, как можно было бы ожидать
(`di/ContainerRegister.php:777-817`).

Контракты gRPC лежат в `esb-protobufs`. На 07.11.2026 там вышла v0.9.9 (поля возврата в
логистике), а Go-шлюз `mobile-monorepo-go` подключает v0.8.99 (`go.mod:8`). Из `esb-monorepo`
удалён `libs/gateway-1c`.

Подробнее о методах — [05-api.md](05-api.md), раздел «gRPC».

## Особенности отдельных интеграций

### Mindbox

Самая глубоко встроенная система. Используется одновременно как:

- источник истины по бонусам — локальные таблицы только отображают состояние;
- поставщик рекомендаций (`MindboxRecommendationsService`);
- канал авторизации сайта через gRPC — фактически используются только `Code` и `CheckCode`
  (`modules/mindbox/services/MindboxGrpcService.php:53-110`); `InitDevice` вызывается лишь внутри
  сгенерированного клиента `modules/grpc/Mindbox/MobileClient.php`, из прикладного кода — не
  напрямую;
- канал авторизации приложения — с ECOMDEV-2342 вход по телефону перенесён из esb (Core Gateway)
  в монолит: SMS-код и проверка идут REST-ом через BFB MS (`MindboxMobileClient`), а привязка
  устройства (`init-client`) — асинхронно, см. ниже;
- получатель фида товаров (`modules/feed/extractors/xml/MindboxFeedExtractor.php`);
- трекер поведения на клиенте (JS-обёртка `frontend/src/layouts/base/workspace/mindbox.js`).

Заказы уходят в Mindbox через outbox: таблицы `mindbox_create_transaction_outbox` и
`mindbox_update_transaction_outbox`, консьюмеры `mindbox-outbox-rabbit-create/update`. Сам
outbox заказа пишется после `commit()` — см. [09-pitfalls.md](09-pitfalls.md).

**Изменения ECOMDEV-2342 (октябрь 2026).**

- Интеграция разнесена на два слоя: `src/Integration/Mindbox/` (клиент приложения
  `MindboxMobileClient`, `MindboxMobileDeviceService`, `MindboxConfigurator` с `BFB_MS_HOST` и
  `MINDBOX_TIMEOUT`) и доменный `src/Modules/Mindbox/` (клиент BFB `MindboxClient`, outbox,
  консоль `mindbox-console`).
- Привязка устройства приложения после входа — асинхронная: `MindboxMobileDeviceService::initClientAsync()`
  публикует сообщение через `RabbitMqPublisherService` в очередь
  `mindbox.mobile-device.v1.command`, консьюмер `mindbox-console/mobile-device` вызывает
  `init-client`. Ошибки только логируются и вход не прерывают. Консьюмер должен работать в одном
  экземпляре (порядок сообщений).
- `removeDevice` для приложения убран вместе с очередью (коммит 188b0177a8).
- Глобальный выключатель прямых запросов в API Mindbox: `MindboxIntegrationToggleService`
  (`src/Modules/Mindbox/Service/`) читает CMS-параметр `mindbox_integration_enabled`
  (`Parameters::MINDBOX_INTEGRATION_ENABLED`) из БД в обход кеша параметров и держит значение в
  процессе 30 секунд. Проверка стоит в `components/MindboxComponent.php:350-362`: при
  выключенном параметре запрос в `api.mindbox.ru` не отправляется, пишется warning. Запросы
  через BFB MS и gRPC этот выключатель не останавливает (по коду не найдено).

**Следствие:** недоступность Mindbox затрагивает и авторизацию в приложении, и отображение
бонусов, и блок рекомендаций — то есть далеко не только рассылки.

### 1С

Обмен по SOAP, WSDL загружается кроном `cron-onec-settings/download-wsdl`
(`CronOneCSettingsController::actionDownloadWsdl()`; отдельной команды `load-wsdl-cron` нет)
и кэшируется. Входящие вебхуки —
`/api/onec/webhooks/*` (баланс сертификата, статусы, офлайн-покупка, смена владельца).
Исходящее направление — outbox-таблицы `onec_create_transaction_outbox` и
`onec_update_transaction_outbox` плюс консьюмеры.

Настройки обмена хранятся в БД и обновляются командой `cron-onec-settings`.

### Платёжные провайдеры

Все построены по одному шаблону: outbox-таблица, таблица уведомлений, обработчик транзакций,
outbox-сервис, консольный обработчик уведомлений, cron и consumer в Helm. Детали — в
[03-business-domains.md](03-business-domains.md), раздел «Платежи».

Ни один из BNPL- и Yandex-провайдеров монолит не вызывает напрямую — все идут через биллинговый
микросервис aggregate-billing. Yandex Pay, Split, SBP и Подели — через `BFB_MS_HOST . '/aggregate-billing'`
(`di/ContainerRegister.php:1258-1304`). Долями — через отдельную переменную
`AGGREGATE_BILLING_MS_URL` (`modules/payment/clients/DolyameClient.php:236`; в `.env.example` она
указывает на `.../aggregate-billing` другого BFF-хоста). Прежнее утверждение «Dolyame и Podeli —
напрямую в API провайдера» было неверным.

Входящие уведомления: Долями — `TinkoffController::actionStatus` (`/payment/tinkoff/status`,
nginx пропускает только подсети Т-Банка), Подели — `AlphaPodeliController`, Yandex —
`src/Integration/Payment/Yandex/Controller/NotificationController.php`. В браузере SDK Долями,
Сплита и SberPay нет — только редирект на `payment_url`.

### Diginetica

Работает на двух уровнях: серверном (`DigineticaService` — поиск и подсказки) и клиентском
(три JS-сервиса: поиск, трекинг, произвольные запросы). Отключение серверной части не
отключает клиентский трекинг.

## Переменные окружения

Полный список — в `.env.example` (корневой, для бэкенда) и `frontend/.env.example` (для
фронтенда). Ниже — группировка по назначению **с реальными именами**; предыдущая версия
документа во многих местах указывала предполагаемые по аналогии, а не фактические имена —
таких переменных в `.env.example` нет.

### Приложение и БД

```
APP_ENV, DEBUG_TOOLS, HOST, HOST_ADMIN, TABLE_PREFIX, BUILD_VERSION*
DSN, USERNAME, PASSWORD
LOG_DSN, LOG_USERNAME, LOG_PASSWORD
LOG_CONTAINER_CALLS
```
`*` — `BUILD_VERSION` читается в `config/config.php`, но в `.env.example` отсутствует
(подставляется отдельно при деплое через Helm/ConfigMap). Переменных `APP_DEBUG`, `APP_URL`
не существует.

### Redis

```
REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DATABASE
REDIS_CLUSTER_NODES
REDIS_NEW_CLUSTER_NODES*
NEW_CHECKOUT_CACHE_ENABLED
```
`*` — используется в `config/config.php`, но тоже отсутствует в `.env.example`.

### Очереди и поиск

```
ELASTIC_HOST, ELASTIC_PORT, ELASTIC_USER, ELASTIC_PASSWORD, ELASTIC_ENABLED, ELASTIC_FORCE_USE_INDEX
```
Единой переменной `ELASTIC_HOSTS` нет. Имя индекса каталога (`elastic_catalog_index`) —
это не переменная окружения, а параметр CMS (`ElasticConfigurator::PARAMETER_INDEX_ALIAS`),
задаётся миграцией и хранится в БД.

### Аутентификация

```
JWT_PRIVATE_KEY, JWT_PUBLIC_KEY
MOBILE_API_KEY, MOBILE_DEVICE_ID_BAN_LIST
```

### Платежи

```
ALPHA_PODELI_API_KEY           # Alpha Podeli (не PODELI_*)
YANDEX_SPLIT_MERCHANT_ID       # Yandex Split (нет отдельной группы YANDEX_SPLIT_*)
YANDEX_PAY_SBP_ONLY_MERCHANT_ID
ATOLV3_*, ATOLV4_*             # фискализация (не ATOL_*; в проде используется ATOLV4_*)
AGGREGATE_BILLING_MS_URL       # биллинговый микросервис для Долями (не BILLING_MS_*); остальные провайдеры — BFB_MS_HOST/aggregate-billing
USE_RECEIPT_MS                 # флаг микросервиса чеков; сам клиент ходит на BFB_MS_HOST
```
Переменных `DOLYAME_*` в `.env.example` нет вовсе. Групп `YANDEX_PAY_*` / `YANDEX_SBP_*` как
таковых тоже нет — только точечные ключи мерчантов.

### CRM и интеграции

```
RCRM_API_ADDRESS, RCRM_API_KEY   # RetailCRM (не RETAIL_CRM_*)
API1C_URL, API1C_LOGIN, API1C_PASSWORD   # 1С (не ONEC_*)
FLOMNI_CLIENT_KEY
HUNTFLOW_*
MINDBOX_SITE_ENDPOINT, MINDBOX_SITE_SECRET          # прямой REST в api.mindbox.ru
MINDBOX_ANDROID_ENDPOINT, MINDBOX_ANDROID_SECRET
MINDBOX_IOS_ENDPOINT, MINDBOX_IOS_SECRET
MINDBOX_TIMEOUT                                      # запросы к Mindbox через BFB MS, по умолчанию 2 с
```
Групп `LAMODA_*` (есть только `IT_ORDERS_LAMODA_WARNING_CHANNEL_ID` — канал Mattermost),
`GARDEROBO_*`, `DRESSCODE_*` (в корневом `.env.example` нет; для Dresscode есть
`FRONTEND_DRESSCODE_API_KEY`/`FRONTEND_DRESSCODE_COMPANY_ID`, но во `frontend/.env.example`)
не существует. `MINDBOX_*` есть только для REST (список выше); для gRPC-стабов отдельных
переменных нет — gRPC-клиенты настроены через `GRPC_GEO_*`.

### Доставка и гео

Boxberry, Accord Post, DaData и геокодеры настроены **захардкоженными ключами** в
`config/common.php`, а не через переменные окружения — групп `BOXBERRY_*`, `ACCORD_*`,
`DADATA_*`, `GOOGLE_GEOCODE_*` в `.env.example` нет.

```
BFB_MS_HOST, BFB_MS_GIFTCARDS_HOST
DELIVERY_PROVIDER   # например, apiship_fivepost — для 5Post
CDN_HOST            # хост картинок (EnvironmentConfigurator)
```

### Мониторинг

```
SENTRY_ENABLED, SENTRY_DSN, SENTRY_SAMPLE_RATE
SENTRY_TRACES_SAMPLE_RATE, SENTRY_ENABLE_TRACING
SENTRY_PROFILES_SAMPLE_RATE, SENTRY_ENABLE_PROFILER, SENTRY_DEBUG
SENTRY_ENABLE_REDIS_TRACING
```

### S3 и почта

```
S3_KEY, S3_SECRET, S3_REGION, S3_ENDPOINT, S3_ENV_DIRECTORY
```
Переменной `S3_BUCKET` нет — имя бакета собирается иначе (через `S3_ENV_DIRECTORY` и
конфигурацию клиента). Отдельных `SMTP_*`/`DKIM_*` тоже нет: почта настроена
захардкоженным `Swift_SmtpTransport` (`host: 127.0.0.1`, `port: 25`) в `config/common.php`,
из переменных — только `FROM_EMAIL`, `USE_FILE_TRANSPORT`; DKIM монтируется в под отдельным
Vault-секретом (см. [07-infrastructure.md](07-infrastructure.md)).

### Фронтенд

Только переменные с префиксом `FRONTEND_*` попадают в бандл (`frontend/.env.example`):

```
FRONTEND_APP_ENV
FRONTEND_SENTRY_DSN
FRONTEND_YANDEX_SMART_CAPTCHA_*
FRONTEND_GOOGLE_RECAPTCHA_API_KEY, FRONTEND_GOOGLE_RECAPTCHA_SCRIPT_URL   # не FRONTEND_GOOGLE_CAPTCHA_*
FRONTEND_DRESSCODE_API_KEY, FRONTEND_DRESSCODE_COMPANY_ID
```

## Схема потоков данных

```mermaid
flowchart TB
    subgraph mono [Монолит]
        Web[Веб-слой]
        Outbox[(Outbox-таблицы)]
        Inbox[(Inbox-таблицы)]
        Cron[CronJobs и воркеры]
    end

    subgraph ms [Микросервисы]
        Billing[aggregate-billing: Yandex Pay/Split/SBP, Подели, Долями]
        Receipt[Receipt Client → BFB]
        BFB[BFB MS, в т.ч. Mindbox REST]
        Feedbacks[Feedbacks gRPC]
        Mindboxms[Mindbox gRPC]
        Orders[Orders gRPC]
    end

    subgraph ext [Внешние системы]
        Mindbox[Mindbox REST]
        RCRM[RetailCRM]
        OneC[1С]
        Pay[Платёжные провайдеры]
        Delivery[Boxberry / Accord / 5Post]
        Search[Diginetica]
        Atol[ATOL]
    end

    Web -->|после commit| Outbox
    Web -->|прямой REST, выключатель| Mindbox
    Outbox --> Cron
    Cron -->|RabbitMQ| Mindbox & RCRM & OneC & Pay
    Mindbox & RCRM & OneC & Pay -->|вебхуки| Inbox
    Inbox --> Cron
    Web -->|REST| Billing & Receipt & BFB
    Web -->|gRPC| Feedbacks & Mindboxms & Orders
    Web -->|REST| Delivery & Search
    Billing --> Pay
    Receipt -->|REST| Atol
```
