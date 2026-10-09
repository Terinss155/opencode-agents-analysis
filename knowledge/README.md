# Навигатор по базе знаний

## Назначение

Общая база знаний о системах 12Storeez, код которых лежит в `C:\Users\RobotComp.ru\Desktop\12stz\`: карты репозиториев, архитектура, API, БД и разборы отдельных фич.

**Правило:** перед поиском по коду в `12stz` сначала открыть этот навигатор и карту нужного репозитория (`repo-map.md`), найти в таблице ниже свой вопрос, и только потом точечно идти в указанные файлы кода. Не искать по всему репозиторию вслепую.

## Репозитории

| Папка знаний | Код в `12stz` | С каким коммитом сверено |
|---|---|---|
| [12storeez-master-web/](12storeez-master-web/repo-map.md) | `12stz/12storeez-master-web` (Yii2 PHP-монолит, ветка `develop`) | `be3cd759d2`, 2026-10-09. Тексты написаны по копии `12storeez-master` (сентябрь 2026); пути сверены с живым репозиторием, расхождения — в `knowledge_staleness.md` |
| [12storeez-ios/](12storeez-ios/repo-map.md) | — | Репозиторий ещё не в `12stz`; карта по копии `12storeez-ios-develop` от 12.09.2026 |

Точки входа по монолиту: [repo-map.md](12storeez-master-web/repo-map.md) (карта папок и модулей) и [architecture/README.md](12storeez-master-web/architecture/README.md) (оглавление архитектурных документов 01–09).

## Вопрос → файл знаний → код

Пути к коду указаны внутри `12stz/12storeez-master-web`. Все они проверены на коммите `be3cd759d2`.

| Вопрос | Файл знаний | Где смотреть в коде |
|---|---|---|
| Как устроен монолит в целом, какие точки входа | [architecture/01-overview.md](12storeez-master-web/architecture/01-overview.md) | `www/index.php`, `yii`, `config/web.php`, `config/console.php` |
| Где какой модуль: старый `modules/` или новый `src/`; DI-контейнер | [repo-map.md](12storeez-master-web/repo-map.md) §3–4, [architecture/02-backend.md](12storeez-master-web/architecture/02-backend.md) | `modules/`, `src/Modules/`, `di/ContainerRegister.php` |
| Почему Yii ID модуля не совпадает с папкой (`productV2`, `mobile-v2`, `user`) | [architecture/02-backend.md](12storeez-master-web/architecture/02-backend.md) «Два стека» | `config/modules.php` |
| Какие бывают статусы заказа (коды, названия) | [database/order-status-dictionaries.md](12storeez-master-web/database/order-status-dictionaries.md) §3 | `modules/statuses/models/OrderStatus.php`, `src/Modules/Order/Enum/StatusEnum.php` |
| Какие бывают статусы позиций заказа | [database/order-status-dictionaries.md](12storeez-master-web/database/order-status-dictionaries.md) §4 | `modules/statuses/models/OrderPositionStatus.php`, `modules/orders/models/OrderPosition.php` |
| Как статусы заказа и позиций мапятся на Mindbox | [database/order-status-dictionaries.md](12storeez-master-web/database/order-status-dictionaries.md) §5 | `modules/statuses/models/MbStatusesMap.php`, `src/Modules/Mindbox/Service/MindboxStatusesMapService.php` |
| Какие бывают WMS-статусы заказа и возврата, откуда они приходят | [database/order-status-dictionaries.md](12storeez-master-web/database/order-status-dictionaries.md) §6–7 | `modules/statuses/models/OrderStatusWms.php`, `modules/statuses/models/OrderReturnStatusWms.php`, `modules/orders/models/Order.php` (`getWmsStatuses()`), `modules/api2/controllers/OrdersController.php` (`actionOrderUpdate`) |
| Какие таблицы хранят заказ и как они связаны | [database/orders-er.md](12storeez-master-web/database/orders-er.md), [architecture/04-database.md](12storeez-master-web/architecture/04-database.md) | `modules/orders/models/Order.php`, `src/Modules/Order/Model/Order.php` |
| Ключевые таблицы других доменов, Redis, поиск | [architecture/04-database.md](12storeez-master-web/architecture/04-database.md) | `src/Search/Elastic/`, `config/common.php` |
| Где миграции и как их называют | [architecture/04-database.md](12storeez-master-web/architecture/04-database.md) «Миграции» | `migrations/`, `check-migrate-trigger.sh` |
| Как создаётся заказ на сайте и в приложении | [architecture/03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md) «Заказы», [repo-map.md](12storeez-master-web/repo-map.md) §5.2 | `src/Modules/Order/Services/CreateOrder/`, `src/Modules/Order/Services/OrderService.php` |
| Что происходит после сохранения заказа (побочные эффекты) | [architecture/03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md) «Заказы» | `src/Modules/Order/AfterSaveEvent/` |
| Как мобильное приложение открывает карточку заказа | [features/order-view.md](12storeez-master-web/features/order-view.md) §1 | `src/Modules/Mobile/Controllers/OrdersController.php`, `src/Modules/Mobile/Rules/UrlRule.php` |
| Какие поля возвращает мобильная карточка заказа | [api/mobile/order-view_mobile.md](12storeez-master-web/api/mobile/order-view_mobile.md) | `src/Modules/Order/Transformer/OrderMobileTransformer.php`, `src/Modules/Order/Repository/OrderRepository.php` |
| Как сайт открывает карточку заказа в ЛК | [features/order-view.md](12storeez-master-web/features/order-view.md) §2, [api/web/order-view_web.md](12storeez-master-web/api/web/order-view_web.md) | `modules/users/controllers/ProfileController.php`, `modules/orders/services/OrderProfileService.php`, `modules/users/extractors/UserOrderExtractor.php` |
| Как устроена авторизация на сайте и в приложении | [features/order-view.md](12storeez-master-web/features/order-view.md) §1.3, §2.3, [architecture/05-api.md](12storeez-master-web/architecture/05-api.md) «Аутентификация» | `src/Modules/Common/Behavior/AuthRequiredBehavior.php`, `src/Auth/Service/JwtService.php`, `modules/api2/auth/HttpBearerAuth.php` |
| Что можно менять в заказе после оформления | [features/order-edit.md](12storeez-master-web/features/order-edit.md) §3 | `modules/orders/controllers/OrdersBackendController.php`, `modules/orders/views/orders-backend/_form.php` |
| Обязателен ли email и влияет ли статус клиента на срок возврата | [features/order-edit.md](12storeez-master-web/features/order-edit.md) §1–2 | `modules/users/models/User.php`, `src/Modules/Order/Helpers/OrderHelper.php`, `modules/cms/models/Parameter.php` |
| Где логика возвратов сейчас (AS-IS) | [repo-map.md](12storeez-master-web/repo-map.md) §5.1, [architecture/README.md](12storeez-master-web/architecture/README.md) «Наш проект» | `src/Modules/Order/Services/OrderRefundService.php`, `modules/orders/controllers/RefundController.php`, `modules/users/controllers/UserRefundController.php` |
| Как пробиваются чеки (АТОЛ, продажа и возврат) | [repo-map.md](12storeez-master-web/repo-map.md) §4.2, [architecture/03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md) «Платежи» | `src/Modules/Receipt/`, `modules/atol/` |
| Какие есть способы оплаты и провайдеры | [architecture/03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md) «Платежи» | `src/Modules/Order/Enum/PaymentMethodEnum.php`, `src/Integration/Payment/`, `modules/yandex/`, `modules/payment/` |
| Где принимаются уведомления от платёжных систем | [architecture/03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md) «Приём уведомлений», [architecture/05-api.md](12storeez-master-web/architecture/05-api.md) «Вебхуки» | `modules/yandex/controllers/PayController.php`, `modules/payment/controllers/TinkoffController.php`, `src/Integration/Payment/Yandex/Controller/NotificationController.php` |
| Как работает outbox платежей и BNPL (Долями, Подели, Сплит) | [architecture/03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md) «Паттерн outbox для платежей» | `src/Modules/Payment/Service/Outbox/OutboxTransactionService.php`, `docs/diagrams/bnpl/` |
| Доставка, ТК, ПВЗ, экспресс-доставка | [architecture/03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md) «Доставка» | `modules/delivery/models/`, `src/Modules/Delivery/Service/DeliveryVariantsService.php`, `src/Modules/Cart/Enum/ExpressDeliveryEnum.php` |
| Интеграция с Mindbox | [architecture/08-integrations.md](12storeez-master-web/architecture/08-integrations.md) | `src/Modules/Mindbox/`, `modules/mindbox/`, `modules/grpc/Mindbox/` |
| Интеграция с 1С (заказы, остатки, возвраты из 1С) | [architecture/08-integrations.md](12storeez-master-web/architecture/08-integrations.md), [repo-map.md](12storeez-master-web/repo-map.md) §5.4 | `src/Modules/OneC/`, `src/Modules/Order/Services/Inbox/` |
| Интеграция с RetailCRM | [architecture/08-integrations.md](12storeez-master-web/architecture/08-integrations.md) | `src/Modules/Rcrm/`, `modules/retailCrm/` |
| Заказы из Lamoda и Mercaux | [architecture/08-integrations.md](12storeez-master-web/architecture/08-integrations.md) | `modules/api2/controllers/OrdersController.php`, `src/Modules/Order/Services/LamodaOrderService.php` |
| Какие есть внешние системы и переменные окружения | [architecture/08-integrations.md](12storeez-master-web/architecture/08-integrations.md) | `.env.example`, `config/config.php` |
| Очереди: MySQL-очередь, RabbitMQ, outbox/inbox | [architecture/07-infrastructure.md](12storeez-master-web/architecture/07-infrastructure.md) «Асинхронная обработка» | `components/SqlQueue.php`, `components/rabbitmq/RabbitMQ.php`, `src/Queue/RabbitMqQueueName.php`, `src/Modules/Order/Services/Outbox/` |
| Консольные команды и cron | [architecture/02-backend.md](12storeez-master-web/architecture/02-backend.md) «Консольные команды», [architecture/07-infrastructure.md](12storeez-master-web/architecture/07-infrastructure.md) | `config/console.php` (`controllerMap`). Файл `config/cron-web` в Kubernetes не используется, расписания задаются в Helm |
| Какой контроллер обрабатывает URL | [architecture/05-api.md](12storeez-master-web/architecture/05-api.md) «Маршрутизация», [repo-map.md](12storeez-master-web/repo-map.md) §6 | `config/url.php`, `src/Modules/Mobile/Rules/UrlRule.php`, `modules/mobilev2/rules/UrlRule.php` |
| Какие есть API сайта и мобилки, версии, эндпоинты, OpenAPI-спецификации | [architecture/05-api.md](12storeez-master-web/architecture/05-api.md), [api/mobile-vs-core-api.md](12storeez-master-web/api/mobile-vs-core-api.md) §1 | `src/Modules/Mobile/Controllers/`, `modules/mobilev2/`, `src/Modules/MobileV2/`, `modules/api2/`; спеки — `docs/openapi/mobile.yml`, `docs/openapi/frontend.yml` (в знаниях ещё старые пути `docs/mobileApi/`, `docs/frontend/`, `docs/ssr/`) |
| Чем отличаются Mobile API, API Gateway и Core API | [api/mobile-vs-core-api.md](12storeez-master-web/api/mobile-vs-core-api.md), [api/mobile/mobile-gateway_swagger.yaml](12storeez-master-web/api/mobile/mobile-gateway_swagger.yaml) | `docs/openapi/mobile.yml`. Gateway и Core API живут в других репозиториях |
| Как устроен фронтенд (Vue, сборка, entry points, `window._site`) | [architecture/06-frontend.md](12storeez-master-web/architecture/06-frontend.md) | `frontend/webpack.config.js`, `frontend/webpack.helpers.js`, `frontend/src/modules/` |
| Админка: где формы и контроллеры | [architecture/02-backend.md](12storeez-master-web/architecture/02-backend.md), [features/order-edit.md](12storeez-master-web/features/order-edit.md) | `modules/cms/`, контроллеры `*BackendController.php` (например `modules/orders/controllers/OrdersBackendController.php`) |
| Фича-флаги и параметры CMS | [architecture/03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md) «Параметры и фича-флаги» | `src/Modules/Common/Enum/Parameters.php`, `modules/cms/models/Parameter.php` |
| CI/CD, Kubernetes, кэш, Sentry | [architecture/07-infrastructure.md](12storeez-master-web/architecture/07-infrastructure.md) | `.gitlab-ci.yml`, `backend.Dockerfile`, `nginx.conf` |
| Неочевидные связи и подводные камни | [architecture/09-pitfalls.md](12storeez-master-web/architecture/09-pitfalls.md) | См. чек-лист в конце документа |
| Как возврат устроен в iOS-приложении | [12storeez-ios/repo-map.md](12storeez-ios/repo-map.md) §4 | Кода iOS в `12stz` пока нет |

## Чего здесь нет

- Каталог, корзина, чекаут, пользователи и CMS описаны только обзорно в [03-business-domains.md](12storeez-master-web/architecture/03-business-domains.md). Отдельных разборов фич по ним нет.
- Нет схемы таблиц за пределами заказов: ER-диаграмма есть только для `cms_orders` и связанных с ней таблиц. Типы полей в ней предварительные.
- Нет описания Core API и API Gateway изнутри: их код в других репозиториях. Есть только swagger шлюза.
- Нет Android-клиента и кода iOS-приложения в `12stz`.
- Нет описания Helm-чартов и расписаний cron: они вне этого репозитория.
