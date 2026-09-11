# Бэкенд

## Два стека: `modules/` и `src/`

### `modules/` — Yii2 MVC

64 каталога, namespace `modules\<имя>\`. Ориентировочная структура модуля (реально
присутствует не везде — см. ниже):

```
modules/<имя>/
├── controllers/     # web + *BackendController (админка)
├── models/          # ActiveRecord, часто с бизнес-логикой
├── service/ | services/
├── repository/ | repositories/
├── views/
├── console/         # консольные контроллеры
├── components/
└── Module.php
```

Это не универсальный шаблон: одновременно `controllers/` + `models/` + `views/` + `Module.php`
есть только у 40 из 64 каталогов. У 10 каталогов `Module.php` нет вовсе (`common`, `feed`, `grpc`,
`gii`, `mainpage`, `mindbox`, `mobile`, `shopping`, `smsRateLimiter`, `userActivities`) — это
общие библиотеки или каталоги, подключаемые без регистрации как Yii-модуль. `console/` встречается
в 17/64, `components/` — в 10/64. Там, где `Module.php` есть, он обычно наследует `modules\cms\Module`;
явные исключения, наследующие `\yii\base\Module` напрямую: `modules/cms/Module.php` (сам базовый
класс), `modules/onelink/Module.php`, `modules/rates/Module.php`, `modules/diginetica/Module.php`.

Здесь живут модели данных и вся CMS-админка. Админские контроллеры называются `*BackendController`
и доступны по маршруту `cms/<модуль>/<контроллер>-backend/<действие>` — их 127 из 388 контроллеров.

Крупнейшие классы проекта — именно здесь, и они содержат бизнес-логику:

| Класс | Файл | ≈ строк |
|---|---|---|
| `Cart` | `modules/cart/models/Cart.php` | 3329 |
| `Product` | `modules/product/models/Product/Product.php` | 3028 |
| `Order` | `modules/orders/models/Order.php` | 2976 |
| `Category` | `modules/catalog/models/Category.php` | 2177 |
| `ProductService` | `modules/product/service/ProductService.php` | 1951 |
| `ProductAggregate` | `modules/product/models/Product/ProductAggregate.php` | 1665 |
| `OrderPosition` | `modules/orders/models/OrderPosition.php` | 1483 |
| `User` | `modules/users/models/User.php` | 1445 |
| `OrderService` | `modules/orders/services/OrderService.php` | 1396 |

Список не исчерпывающий — среди крупных каталогов `modules/`, не разобранных подробно в этом
документе: `cms/` (138 файлов, базовый Yii-фреймворк админки), `product/` (289 файлов),
`catalog/` (95), `common/` (66, легаси-слой без своего `Module.php`), `grpc/` (72,
сгенерированный protobuf-код).

### `src/` — слоистая структура

Namespace `Application\`, 43 домен-модуля в `src/Modules/` плюс 11 инфраструктурных каталогов
рядом (всего 12 каталогов верхнего уровня в `src/`, включая сам `Modules/`).

Инфраструктурные каталоги `src/`:

| Каталог | Назначение |
|---|---|
| `Auth/` | JWT-аутентификация как Yii-модуль |
| `Cache/` | Redis: подключения, контракты, конфигураторы кластеров |
| `Cart/` | Тонкий мост — единственный файл `Service/CartService.php`, не путать с полноценным доменом `src/Modules/Cart/` (188 файлов) |
| `Common/` | Bootstrap событий, базовое подключение к БД, RabbitMQ, S3, rate limiter |
| `Framework/` | `LogJsonTarget` |
| `Http/` | Контроллеры API, валидация запросов, сервис формирования ответа |
| `Integration/` | Внешние системы: платежи Yandex, капча, email-уведомления, микросервисы |
| `Monitoring/` | Sentry |
| `Queue/` | Имена очередей (`SqlQueueName`, `RabbitMqQueueName`), хелперы DI |
| `Search/` | Elasticsearch: клиент, индексатор, построитель запросов |
| `User/` | REST API пользователя + подмодуль уведомлений |

Крупнейшие домен-модули `src/Modules/` по числу файлов:

| Модуль | Файлов | Ключевые слои |
|---|---|---|
| `Order` | 197 | 32 сервиса, 24 репозитория, 26 обработчиков `AfterSaveEvent`, 26 DTO |
| `Cart` | 188 | 75 сервисов (фабрики под режимы корзины), 25 фильтров (12 платёжных + 13 доставки/прочих), 29 DTO |
| `Mobile` | 105 | 38 контроллеров mobile API v1, 16 валидаторов |
| `Payment` | 80 | outbox-сервисы, клиенты провайдеров, консольные обработчики |
| `Receipt` | 70 | фискальные чеки, ATOL, receipt MS |
| `Delivery` | 69 | построение вариантов доставки, гео |
| `Common` | 69 | параметры-флаги, middleware, локализация |
| `Product` | 59 | пара к легаси `modules/product/`: рекомендации, ранний доступ, остатки |
| `Mindbox` | 44 | REST- и gRPC-обёртки над CRM |
| `MobileV2` | 40 | контроллеры второй версии mobile API (Yii ID `mobile-v2`) |
| `Stock` | 21 | буферы и консольные команды синхронизации остатков (ESB) |

Список неполный — в `src/Modules/` также есть `Rcrm`, `Images`, `Notifications`, `Reservation`,
`Geo`, `Giftcard`, `Api2`, `Cms`, `YandexTracker`, `MobileInfo`, `Landing`, `Poll`, `Vacancy`,
`Blog`, `Navigation`, `ActionPresent`, `Analytics` и другие домены меньшего размера.

### Соглашения по именованию в `src/`

Единообразия нет — в разных модулях встречаются оба варианта:

- `Service/` и `Services/`
- `Controller/` и `Controllers/`
- `Helper/` и `Helpers/`
- `Exception/` и `Exceptions/`
- `Model/` и `Models/`

Суффиксы устойчивы: `*Dto`, `*Enum`, `*Dictionary`, `*Service`, `*Repository`, `*Extractor`,
`*Transformer`, интерфейсы — в `Interfaces/`.

### Дублирование модулей

**Важно:** таблица ниже — это про **Yii ID модулей** в `config/modules.php`, а не про пары
одноимённых каталогов. У большинства «современных» ID нет каталога `modules/<id>/` вообще —
их класс модуля зарегистрирован напрямую на `Application\Modules\...\Module` из `src/`.
Каталог `modules/<имя>/` существует **только у легаси-стороны** каждой пары.

| Легаси: Yii ID → каталог | Современный: Yii ID → класс | Как разделены |
|---|---|---|
| `product` → `modules/product/` | `productV2` → `Application\Modules\Product\Module` (только `src/`) | CRUD каталога легаси; рекомендации и API — в `src/` |
| `cart` → `modules/cart/` | `carts` → `Application\Modules\Cart\Module` (только `src/`) | Оба ID зарегистрированы с одним и тем же `'controllers' => ['cart']`; UI старой корзины — легаси, новый чекаут-API — в `src/` |
| `orders` → `modules/orders/` | *(своего Yii ID нет)* `src/Modules/Order/` подключается напрямую, без записи в `config/modules.php` | Админка и страницы оплаты — легаси; создание заказа, outbox — в `src/` |
| `payment` → `modules/payment/` | `paymentV2` → `Application\Modules\Payment\Module` (только `src/`) | Админка чеков — легаси |
| `mobilev2` → `modules/mobilev2/` | `mobile-v2` → `Application\Modules\MobileV2\Module` (только `src/`, каталога `modules/mobile-v2/` нет) | **Общий префикс URL `/mobile/v2/`** — см. [09-pitfalls.md](09-pitfalls.md) |
| `retailCrm` → `modules/retailCrm/` | `rcrm` → `Application\Modules\Rcrm\Module` (только `src/`) | Синхронизация через outbox — в `src/` |
| `users` → `modules/users/` | `user`, `userApi`, `userNotifications` — три отдельных ID, все на классы из `src/` (`Application\Modules\User\Module`, `Application\User\Module`, `Application\User\Notifications\Module`); каталогов `modules/user/`, `modules/userApi/` нет | Профиль и админка — легаси; импорт, REST-профиль и уведомления — в `src/` |
| `delivery` → `modules/delivery/` | `deliveryV2` и `return` — **оба указывают на один и тот же класс** `Application\Modules\Delivery\Module`, различаются только набором `controllers` | Модель данных — легаси; расчёт вариантов и обработка возвратов — в `src/` |
| `lookbook` → `modules/lookbook/` | `lookbookv2` → `Application\Modules\Lookbook\Module` (только `src/`) | |
| `marketing` → `modules/marketing/` | `marketingV2` → `Application\Modules\Marketing\Module` (только `src/`) | |
| `subscription` → `modules/subscription/` | `subscriptions` → `Application\Modules\Subscription\Module` (только `src/`) | |
| `wishlist` → `modules/wishlist/` | `wishlists` → `Application\Modules\Wishlist\Module` (только `src/`) | |
| `feedback` → `modules/feedback/` | `feedbackV2` → `Application\Modules\Feedback\Module` (только `src/`) | |
| `api2` → `modules/api2/` | `api2_new` → `Application\Modules\Api2\Module` (только `src/`) | Старые и новые вебхуки |

Особые случаи, не укладывающиеся в схему «легаси-каталог + современный ID»:

- **`feed`** — Yii ID **один**, `Application\Modules\Feed\Module` из `src/`; отдельного
  legacy-модуля нет. При этом каталог `modules/feed/` существует (35 файлов: старые
  extractors/services/console для экспорта) и используется напрямую консольными командами,
  без прохождения через систему Yii-модулей.
- **`mainpage`** — аналогично, Yii ID один и указывает на `Application\Modules\Mainpage\Module`.
  Каталог `modules/mainpage/` при этом существует (6 файлов) — там остались legacy-views,
  которые современный модуль по-прежнему использует для рендера.

Только в `src/`, без каких-либо legacy-остатков в `modules/`: `auth`, `checkout`, `metadata`,
`menu`, `metrics`, `onec`, `analytics`.

Ещё один пример не столь очевидного дублирования: позиции корзины лежат в отдельном модуле
`modules/shopping/` (`ShoppingCartPosition`), а не в `modules/cart/`, хотя сама корзина
(`Cart`) — в `cart`. Механизмы outbox/inbox и gRPC-клиенты в `modules/grpc/` здесь не
расписаны подробно — см. [07-infrastructure.md](07-infrastructure.md) и
[05-api.md](05-api.md), раздел «gRPC».

## DI-контейнер

`di/ContainerRegister.php` — 1516 строк, реализует `BootstrapInterface`, подключается в
`config/common.php`. Содержит **341** вызов `setSingleton()` и импортирует **381** класс
из обоих стеков.

Что делает:

- регистрирует конкретные классы как синглтоны;
- связывает интерфейсы с реализациями;
- создаёт фабрики для Redis, gRPC, JWT, капчи, обработчиков Yandex-платежей;
- конфигурирует клиентов по `Yii::$app->params`.

Основные связи интерфейс → реализация:

| Интерфейс | Реализация |
|---|---|
| `RedisInterface` | `ClusterConnection` или `StandaloneConnection` |
| `NewRedisInterface` | `NewClusterConnection` или `NewStandaloneConnection` |
| `UserMobileSessionRepositoryInterface` | `CacheUserMobileSessionRepository` |
| `CaptchaInterface` | `ReCaptchaService` |
| `LoggerInterface` | `Application\Modules\Common\Service\Logger` |
| `FieldMapperInterface` | `ElasticCatalogFieldMapperService` |
| `DeliveryTkEntityRepositoryInterface` | `CacheDeliveryTkPvzRepository` |

Выбор реализации Redis зависит от окружения: если заполнены переменные с узлами кластера —
кластерное подключение, иначе одиночное.

Отдельная группа регистраций — мосты к легаси: `OldCartService`, `OldOrderService`,
`OldUserService`, `OldPaymentTypeService`, `OldImageService`, `OldDeliveryTkRepository`,
`OldOrderPositionRepository`, `OldOrderRepository`. Они регистрируются рядом с новыми
сервисами, из-за чего граница между стеками намеренно проницаема.

Дополнительные синглтоны есть и в `config/common.php` в секции `container.singletons` —
например, `AuthClientInterface` подменяется на `LocalClient` вне прода.

**Практическое следствие:** менять `ContainerRegister.php` рискованно — от него зависят оба
стека, и файл не разделён на провайдеры по доменам.

## События

Два независимых механизма.

**1. События приложения** — `src/Common/Bootstrap/EventBootstrap.php` регистрирует:
`UserAfterLoginEvent`, `UserAfterEditEvent`, события смены пароля, `OrderAfterCreateEvent`,
`OrderAfterUpdateEvent`. Каждый наследует `BaseEvent`.

**2. Побочные эффекты заказа** — 26 классов в `src/Modules/Order/AfterSaveEvent/`, запускаются
через `src/Modules/Order/Services/EventRunner.php` после коммита транзакции: отправка в Mindbox,
переиндексация товаров, блокировка сертификатов, отмена BNPL-платежей, аналитика.

Отдельно в `config/events.php` — единственный обработчик: обновление кэша меню навигации
(`eventHandlers/MenuCacheReloaderHandler.php`).

## Общие каталоги вне модулей

| Каталог | Файлов | Содержимое |
|---|---|---|
| `components/` | 33 | Yii-компоненты: `SqlQueue`, `RabbitMQ`, `MindboxComponent`, `Mailer`, `LangRequest`, гео (`Dadata`, `Google`, `Geocode`), партнёрские (`Admitad`, `GdeSlon`) |
| `helpers/` | 7 | `StringHelper`, `TransliterateHelper`, `MobileVersionChecker`, `ColorHelper`, `DbHelper`, `ImageHelper`, `MoneyFormatHelper` |
| `coreExtends/` | 10 | `ExtendedErrorHandler`, HTTP-исключения (`Redirect301Exception`), расширенное логирование |
| `widgets/` | 6 | Легаси-UI: пагинация, нотификации, подписка |
| `validators/` | 7 | Валидаторы авторизации по SMS, телефона, заявки на возврат |
| `eventHandlers/` | 1 | Обработчик обновления кэша меню |
| `translations/` | — | YAML-переводы для Symfony Translator (домены `cart/`, `order/` и др.) |
| `themes/basic/` | — | PHP-views сайта, точка связки с фронтендом |

## Консольные команды

94 команды регистрируются в `config/console.php` через `controllerMap`. Namespace
`app\commands`, указанный как `controllerNamespace`, физически не существует (нет ни каталога,
ни PSR-4 записи в `composer.json`) — команды приходят только из `controllerMap`. Группы:

| Группа | Примеры команд |
|---|---|
| Очереди | `queue`, `slave-queue`, `rabbit-inbox-transactions`, `rabbit-outbox-transactions`, `cron-outbox-transactions`, `rabbit-bnpl-outbox-transactions`, `receipt-outbox` |
| Платёжные уведомления | `notification-podeli`, `notification-yandex-split`, `notification-yandex-pay`, `notification-yandex-sbp`, `change-status-podeli`, `change-status-dolyame` |
| Заказы и интеграции | `order`, `lamoda-order`, `offline-order`, `send-order-1c`, `bug-orders`, `mindbox-console`, `rcrm`, `cron-onec-settings` |
| Каталог | `export`, `feed-export`, `exchange`, `product-reindex`, `product-import`, `product-attributes`, `early-access`, `elastic`, `stocks` |
| Доставка и гео | `delivery`, `boxberry`, `accord`, `geo`, `ipgeobase-parse` |
| Пользователи | `user-import`, `jwt-auth`, `check-user-address`, `DuplicateMerge`, `sms-log` |
| Чеки | `receipt`, `atol`, `lifepay` |
| Обслуживание | `migrate`, `sitemap`, `clear-log`, `clear-db`, `clear-outbox`, `cache`, `message` |

Файл `config/cron-web` описывает расписания времён bare-metal и **в Kubernetes не используется** —
актуальные расписания в Helm.

## Статический анализ

| Конфиг | Уровень | Область |
|---|---|---|
| `phpstan.neon` | 2 | `components`, `config`, `modules`, `www` и др. — **`src/` не входит**, 181 строка `excludedPaths` (не `ignoreErrors` — этой секции в файле нет) |
| `phpstan_6lvl_src.neon` | 6 | только `src/`, подключается отдельной job при изменениях в `src/**` |

Дополнительно: `phpcs.xml` (code style), `phpunit.xml` (тесты в `tests/`).

Обратите внимание на асимметрию: строгая проверка применяется к `src/`, который зависит от
слабо проверяемого `modules/`. Последствия описаны в [09-pitfalls.md](09-pitfalls.md).
