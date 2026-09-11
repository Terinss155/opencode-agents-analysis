# Структура репозитория 12storeez-master

**Назначение документа:** карта-справочник по кодовой базе `12storeez-master` (Yii2 PHP-монолит интернет-магазина 12Storeez) для быстрого поиска информации при анализе требований и разработке.

**Дата актуализации:** 2026-09-06
**Примечание:** структура описана по фактическому содержимому папок; назначение модулей — по названиям и ключевым классам.

---

## 1. Общая архитектура

- **Стек:** PHP (Yii2), MySQL, Redis, RabbitMQ, Elasticsearch, Sphinx, Docker.
- **Два слоя кода:**
  - `modules/` — «старый» слой (модули Yii2, ActiveRecord-модели, контроллеры, репозитории).
  - `src/` — «новый» слой (PSR-4, namespace `Application\...`, сервисы, DTO, репозитории, фасады).
- **Интеграции:** 1С, RetailCRM, Mindbox, Lamoda, Mercaux, Yandex (Pay/Split/SBP), Dolyame (Т-Банк), Podeli (Альфа), Atol (чеки/ОФД), Elasticsearch, S3, Sentry, Yandex Tracker, Huntflow (вакансии).
- **Очереди:** RabbitMQ (outbox/inbox транзакции), Redis (буфер остатков).

---

## 2. Корневые папки

| Папка | Назначение |
|---|---|
| `modules/` | Модули Yii2 (старый слой): контроллеры, модели, репозитории, сервисы, views |
| `src/` | Новый слой кода (namespace `Application\`): сервисы, DTO, репозитории, фасады |
| `config/` | Конфигурация приложения (common, web, console, url, modules, events, log, i18n) |
| `migrations/` | Миграции БД (~197 файлов) |
| `components/` | Компоненты: `goqr/`, `mindbox/`, `rabbitmq/` |
| `coreExtends/` | Расширения ядра (исключения, логирование) |
| `di/` | DI-контейнер (определения сервисов) |
| `eventHandlers/` | Обработчики событий (`MenuCacheReloaderHandler.php`) |
| `helpers/` | Хелперы: Color, Db, Image, MobileVersionChecker, MoneyFormat, String, Transliterate |
| `validators/` | Валидаторы: `auth/`, `base/`, `order/` (в т.ч. `OrderRefundRequestValidator`) |
| `widgets/` | Виджеты |
| `themes/` | Темы оформления (basic) |
| `translations/` | Переводы (i18n) |
| `frontend/` | Фронтенд (React/Storybook: `.storybook/`, `src/`, `docs/`) |
| `www/` | Web-корень: assets, documents, external, favicons, giftcards, jwk, offline, seo, temporary-feeds |
| `docs/` | Документация: `diagrams/` (mermaid), `frontend/`, `mobileApi/` (openapi.yml), `sale/`, `setup/`, `ssr/` |
| `ai-tasks/` | Задачи для ИИ-агентов: `jwt-auth/` (api-contract, step-*.task.md, postman), dod-ai-template, working-agreement |
| `tests/` | Тесты (phpunit) |
| `mail/` | Шаблоны писем |
| `jwt_keys/` | Ключи JWT |
| `runtime/` | Runtime-файлы |
| `stubs/` | Стабы |
| `utils/` | Утилиты (пусто) |
| `dump.rdb` | Дамп Redis |
| `composer.json`, `package-lock.json` | Зависимости PHP/JS |
| `docker-compose.yaml`, `*.Dockerfile`, `nginx.conf`, `bootstrap.sh` | Инфраструктура |
| `phpstan.neon`, `phpcs.xml`, `phpunit.xml` | Качество кода |
| `openapi-coverage.php` | Проверка покрытия OpenAPI |
| `yii`, `yii.bat`, `Yii.php`, `init`, `migrateup`, `php-cli` | CLI-точки входа |

---

## 3. `modules/` — старый слой (65 модулей)

### 3.1. Ключевые бизнес-модули

| Модуль | Назначение | Ключевые классы |
|---|---|---|
| `orders/` | **Заказы** (ядро): модели Order/OrderPosition, возвраты, статусы, outbox Lamoda | `models/Order.php`, `models/OrderPosition.php`, `models/OrderReturnPosition.php`, `models/ReturnReason.php`, `models/ReturnReasonGroup.php`, `controllers/RefundController.php`, `repositories/OrderReturnReasonRepository.php`, `repositories/OrderReturnReasonGroupRepository.php`, `repositories/OrderPositionRepository.php`, `repositories/OrderReturnPositionRepository.php`, `services/OrderService.php`, `services/LamodaOrderOutboxService.php` |
| `users/` | **Пользователи, ЛК, возвраты**: профиль, адреса, реквизиты возврата, wishlist, RBAC | `models/UserRefund.php`, `controllers/UserRefundController.php`, `services/UserRefundService.php`, `repositories/UserRefundRepository.php`, `forms/SaveReasonForm.php`, `forms/RefundBankDataForm.php`, `extractors/UserReturnReasonExtractor.php`, `extractors/UserReturnReasonGroupExtractor.php`, `validators/UserRefundMobileValidator.php` |
| `catalog/` | Каталог товаров, категории, коллекции | `dictionaries/GroupCategoryDictionary.php`, `dictionaries/BlockCategoryDictionary.php` |
| `product/` | Товары, размеры, цены, изображения | `models/Product/Product.php`, `models/ProductSize.php`, `service/ProductService.php`, `service/ProductEnrichService.php` |
| `cart/` | Корзина | — |
| `payment/` | Платежи | — |
| `delivery/` | Доставка, ПВЗ, возвраты ТК | — |
| `bonuses/` | Бонусная программа | — |
| `giftcards/` | Подарочные сертификаты | — |
| `discounts/` | Скидки, промокоды | — |
| `processing/` | Обработка заказов, скидки на позиции | `interfaces/DiscountablePosition.php`, `models/ManualDiscount.php` |
| `statuses/` | Справочник статусов | `models/OrderPositionStatus.php` |
| `retailCrm/` | Интеграция RetailCRM | — |
| `mindbox/` | Интеграция Mindbox | — |
| `atol/` | Интеграция АТОЛ (чеки) | — |
| `yandex/` | Yandex Pay/Касса | `controllers/PayController.php`, `services/PaymentService.php`, `models/PaymentLog.php` |
| `lifepay/` | LifePay | — |
| `bonuses/` | Бонусы | — |
| `feedback/` | Отзывы | `models/Feedback.php`, `models/FeedbackPosition.php` |
| `support/` | Поддержка | — |
| `notification/` | Уведомления | — |
| `wishlist/` | Избранное | `services/WishlistService.php`, `controllers/WishlistController.php` |
| `vacancy/` | Вакансии | `service/JobVacancyService.php`, `models/JobVacancy.php` |
| `blog/` | Блог | — |
| `content/` | Контент | — |
| `cms/` | CMS-ядро (модели, контроллеры, виджеты) | `controllers/FrontendController.php`, `models/Model.php` |
| `common/` | Общее: виджеты, валидаторы | `widgets/gridview/CommonGridView.php`, `validator/NoUrlTagValidator.php` |
| `api/`, `api2/` | API (старые версии) | `controllers/OrdersController.php` (api2), `service/ExchangeStockService.php`, `repository/ExchangeStockRepository.php` |
| `mobile/`, `mobilev2/` | Мобильное API (старые версии) | — |
| `abTest/` | A/B-тесты | `services/AbTestService.php` |
| `geo/`, `location/` | Гео, города | — |
| `google/` | Google Analytics | `models/Operation.php` |
| `diginetica/` | Рекомендации Diginetica | — |
| `feed/` | Фиды | — |
| `marketing/` | Маркетинг | — |
| `poll/`, `contest/`, `popmechanic/`, `onelink/`, `redirect/`, `redirecturl/`, `social/`, `subscription/`, `smsRateLimiter/`, `userActivities/`, `rates/`, `banks/`, `blocks/`, `care/`, `completeMessages/`, `home/`, `layout/`, `lookbook/`, `mainpage/`, `navigation/`, `news/`, `present/`, `shopping/`, `automatic/`, `gii/`, `grpc/` | Вспомогательные/прочие | — |

### 3.2. Типовая структура модуля (на примере `orders/`)
```
controllers/   — контроллеры (RefundController, ...)
console/       — консольные команды (StatusController, OrderController, LamodaOrderController)
dictionaries/  — справочники
dto/           — DTO (OrderDataDto, CartDataDto, ...)
exceptions/    — исключения
extractors/    — экстракторы (преобразование моделей в массивы/JSON)
interfaces/    — интерфейсы (OrderInterface)
jobs/          — очереди (CreatePaymentCrmJob, RetailCrmCustomerJob, ...)
models/        — ActiveRecord-модели (Order, OrderPosition, ReturnReason, ...)
repositories/  — репозитории (OrderPositionRepository, OrderReturnReasonRepository, ...)
services/      — сервисы (OrderService, LamodaOrderOutboxService, ...)
views/         — шаблоны
```

---

## 4. `src/` — новый слой (namespace `Application\`)

### 4.1. Верхний уровень `src/`
| Папка | Назначение |
|---|---|
| `Modules/` | Бизнес-модули (43 шт.) |
| `Integration/` | Интеграции: Captcha, Common, Communication, Microservice, Notification, Payment |
| `Queue/` | Очереди: `SqlQueueName.php`, `RabbitMqQueueName.php`, `SqlQueueHelper.php`, `DiHelper.php` |
| `Search/` | Поиск: `Elastic/` (клиент, сервисы, индексация каталога) |
| `Monitoring/` | Мониторинг: `Sentry/` |
| `Auth/` | Аутентификация (JWT) |
| `Cache/` | Кэш |
| `Cart/` | Корзина |
| `Common/` | Общее: хелперы (LogHelper, YiiDbHelper, YiiTranslateHelper), enum, utils |
| `Framework/` | Фреймворк-обвязка |
| `Http/` | HTTP |
| `User/` | Пользователи: Notifications, Controller, Rule |

### 4.2. `src/Modules/` — бизнес-модули (43 шт.)
| Модуль | Назначение | Ключевые классы |
|---|---|---|
| `Order/` | **Заказы (новый слой)**: сервисы, outbox/inbox, возвраты | `Services/OrderService.php`, `Services/OrderRefundService.php`, `Services/OrderCancelService.php`, `Services/Inbox/OrderUpdateService.php`, `Services/Outbox/*`, `Validators/OrderRefundValidator.php`, `Dto/OrderUpdateDto.php`, `Dto/OrderRefundItemDto.php`, `Dto/Inbox/OrderOneCInboxDto.php`, `Dto/Inbox/OrderReturnPositionDto.php`, `Model/Order.php`, `Repository/OrderRepository.php`, `Enum/StatusEnum.php`, `Enum/PaymentMethodEnum.php`, `Enum/LastSourceEnum.php`, `Helpers/OrderHelper.php`, `AfterSaveEvent/*` |
| `Receipt/` | **Чеки/ОФД (АТОЛ)**: продажа, возврат, коррекция | `Service/OrderReceiptService.php`, `Service/ReceiptService.php`, `Service/ReceiptBuilder.php`, `Service/ReceiptSender/*` (SellPrepayment, SellFullpayment, RefundPrepayment, RefundFullpayment), `Repository/OrderPositionRefundRepository.php`, `Repository/OrderPositionRequireRefundReceiptRepository.php`, `Model/OrderPositionRefund.php`, `Model/OrderPositionRequireRefundReceipt.php`, `Enum/OperationEnum.php`, `Enum/EndpointEnum.php`, `Job/SendJob.php`, `Job/OfdJob.php`, `Console/ReceiptController.php`, `Console/ReceiptOutboxController.php` |
| `Mobile/` | **Мобильное API (новый слой)** | `Controllers/OrdersController.php` (actionReturnPositions, actionReturnDetails, actionReturnMethodList), `Controllers/CartBaseController.php`, `Controllers/ApiBaseController.php` |
| `OneC/` | Интеграция 1С | — |
| `Rcrm/` | Интеграция RetailCRM (outbox) | `Service/RcrmOutboxService.php` |
| `Mindbox/` | Интеграция Mindbox (outbox) | `Service/MindboxOutboxService.php` |
| `Delivery/` | Доставка, способы возврата | `Enum/ReturnMethodEnum.php`, `Helper/PickupHelper.php` |
| `Payment/` | Платежи | — |
| `Giftcard/` | Подарочные сертификаты | `Service/GiftcardCreateOrderService.php`, `Service/GiftcardAntiFraudService.php`, `Service/GiftCardCartService.php` |
| `Stock/` | Остатки | — |
| `Reservation/` | Резервы | — |
| `Checkout/` | Оформление заказа | — |
| `Cart/` | Корзина | — |
| `Product/` | Товары | — |
| `User/` | Пользователи | `Services/UserService.php`, `Services/UserRegistrationService.php`, `Services/UserAddressService.php`, `Repository/UserWishlistRepository.php` |
| `Auth/` | Аутентификация | — |
| `Api/`, `Api2/` | API | — |
| `Cms/` | CMS | `Model/Parameter.php` |
| `Common/` | Общее | `Helpers/LogHelper.php`, `Helpers/YiiDbHelper.php`, `Helpers/YiiTranslateHelper.php`, `Enum/LogMessageEnum.php`, `Utils/UuidUtils.php` |
| `Analytics/` | Аналитика | — |
| `Metrics/` | Метрики | — |
| `Notifications/` | Уведомления | — |
| `Images/` | Изображения, S3 | `Service/ImageResizeService.php`, `Client/S3Client.php`, `Console/RabbitImageResizeConsolePopController.php` |
| `Vacancy/` | Вакансии (Huntflow) | `Service/HuntflowService.php` |
| `Wishlist/` | Избранное | `Service/WishlistService.php` |
| `YandexTracker/` | Yandex Tracker | `Service/YandexTrackerService.php`, `Client/YandexTrackerClient.php` |
| `ActionPresent/`, `Blog/`, `Feed/`, `Feedback/`, `Geo/`, `Landing/`, `Lookbook/`, `Mainpage/`, `Marketing/`, `Menu/`, `Metadata/`, `MobileInfo/`, `MobileV2/`, `Navigation/`, `Poll/`, `Subscription/` | Прочие | — |

### 4.3. Типовая структура модуля `src/Modules/Order/`
```
AfterSaveEvent/  — события после сохранения (UpdateOrdersCounterEvent, UpdateQuantityBufferEvent, SendCancelTo*Event, UnlockGiftcardsByOrderEvent)
Builder/         — билдеры
Client/          — клиенты
Common/          — общее
Configurator/    — конфигураторы
Console/         — консольные команды
Controller/      — контроллеры
Dictionary/      — словари
Dto/             — DTO (в т.ч. Inbox/Outbox)
Enum/            — перечисления (StatusEnum, PaymentMethodEnum, LastSourceEnum, ExternalServiceActionEnum, OrderMethodEnum)
Event/           — события
Exception/       — исключения
Extractors/      — экстракторы
Helpers/         — хелперы (OrderHelper, OrderDiscountHelper, LamodaOrderHelper, GAHelper, ExternalServiceSendHelper, DbConnectionHelper)
Interfaces/      — интерфейсы
Model/           — модели (Order, OrderOutboxBaseModel, OrderInboxBaseModel, RcrmOrder*, OnecOrder*, MindboxOrder*, OfflineOrder*)
Repository/      — репозитории (OrderRepository, OrderPositionStatusRepository, OrdersHistoryRepository, Outbox/Inbox фабрики)
Services/        — сервисы (OrderService, OrderRefundService, OrderCancelService, Inbox/*, Outbox/*, CreateOrder/*, LamodaOrderService, GAExchangeService, EventRunner)
Traits/          — трейты (OrderGetterTrait, OrderSetterTrait, ProcessedOrderTrait)
Transformer/     — трансформеры (OrderMobileTransformer, BillingMsOrderTransformer, ...)
Validators/      — валидаторы (OrderRefundValidator, CreateOrderCartSiteValidator, ...)
```

---

## 5. Ключевые точки для поиска по процессам

### 5.1. Процесс возврата товара (клиент)
| Что искать | Где |
|---|---|
| Web REST-контроллер возврата | `modules/orders/controllers/RefundController.php` |
| AJAX-контроллер возврата (ЛК) | `modules/users/controllers/UserRefundController.php` |
| Сервис возврата (ядро) | `src/Modules/Order/Services/OrderRefundService.php` |
| Валидатор возврата | `src/Modules/Order/Validators/OrderRefundValidator.php`, `validators/order/OrderRefundRequestValidator.php` |
| Формы возврата | `modules/users/forms/SaveReasonForm.php`, `modules/users/forms/RefundBankDataForm.php` |
| Модель реквизитов возврата | `modules/users/models/UserRefund.php` (таблица `users_refund`) |
| Модель позиции заказа (returnPosition, canBeReturned) | `modules/orders/models/OrderPosition.php` |
| Модель заказа (updateReturnStatus, статусы) | `modules/orders/models/Order.php` |
| Причины возврата | `modules/orders/models/ReturnReason.php`, `ReturnReasonGroup.php`, `repositories/OrderReturnReasonRepository.php`, `OrderReturnReasonGroupRepository.php` |
| Возврат из 1С (inbox) | `src/Modules/Order/Services/Inbox/OrderUpdateService.php` (handleReturnPositions), `modules/orders/models/OrderReturnPosition.php` |
| Мобильный возврат | `src/Modules/Mobile/Controllers/OrdersController.php` (actionReturnPositions, actionReturnDetails, actionReturnMethodList) |
| Чеки возврата (АТОЛ) | `src/Modules/Receipt/` (OrderReceiptService, RefundPrepayment, RefundFullpayment, OrderPositionRefund) |
| Обновление заказа (updateOrder) | `src/Modules/Order/Services/OrderService.php` |
| Проверка возможности возврата | `src/Modules/Order/Helpers/OrderHelper.php` (canBeReturned, canPositionBeReturned, isReturned) |
| Статусы возврата | `src/Modules/Order/Enum/StatusEnum.php`, `modules/orders/models/Order.php` (STATUS_ORDER_RETURNED_LK=31, STATUS_REFUND_REQUEST_*) |

### 5.2. Процесс создания заказа
| Что искать | Где |
|---|---|
| Создание заказа (сайт) | `src/Modules/Order/Services/CreateOrder/CreateOrderServiceSite.php` |
| Создание заказа (МП) | `src/Modules/Order/Services/CreateOrder/CreateOrderServiceMobile.php` |
| Создание заказа (корзина) | `src/Modules/Order/Services/CreateOrder/AbstractCreateOrderService.php`, `CartOrderCreateDtoPrepareService.php` |
| Валидаторы создания | `src/Modules/Order/Validators/CreateOrderCartSiteValidator.php`, `CreateOrderCartMobileValidator.php` |

### 5.3. Платежи и оплата
| Что искать | Где |
|---|---|
| Yandex Pay/Касса | `modules/yandex/` (PayController, PaymentService, PaymentLog) |
| BNPL (Dolyame/Podeli/Split) | `src/Modules/Order/AfterSaveEvent/SendCancelTo*Event.php`, `src/Modules/Order/Dto/BnplStatusDto.php`, `docs/diagrams/bnpl/` |
| Платежи (модель) | `modules/payment/` |

### 5.4. Интеграции (outbox/inbox)
| Что искать | Где |
|---|---|
| RetailCRM | `src/Modules/Rcrm/`, `modules/retailCrm/`, `src/Modules/Order/Repository/RcrmOrder*` |
| 1С | `src/Modules/OneC/`, `src/Modules/Order/Repository/OnecOrder*`, `src/Modules/Order/Services/Inbox/` |
| Mindbox | `src/Modules/Mindbox/`, `src/Modules/Order/Repository/MindboxOrder*` |
| Lamoda | `modules/orders/services/LamodaOrderOutboxService.php`, `src/Modules/Order/Services/LamodaOrderService.php` |
| Mercaux | `modules/api2/service/UserMercauxService.php`, `src/Modules/Order/Services/MercauxOrderCreateDtoPrepareService.php` |
| АТОЛ (чеки) | `src/Modules/Receipt/` |
| Elasticsearch | `src/Search/Elastic/` |
| RabbitMQ | `src/Queue/`, `components/rabbitmq/` |

---

## 6. Конфигурация и маршрутизация

| Файл | Назначение |
|---|---|
| `config/common.php` | Общая конфигурация |
| `config/web.php` | Web-конфигурация |
| `config/console.php` | Консольная конфигурация |
| `config/url.php` | **Маршруты URL** (в т.ч. `user/cabinet/return-item/*` → `users/user-refund/*`) |
| `config/modules.php` | Подключение модулей |
| `config/events.php` | События |
| `config/log.php` | Логирование |
| `config/i18n.php` | Переводы |
| `config/params_example.php` | Параметры (пример) |
| `di/` | DI-контейнер |

---

## 7. Документация и схемы

| Файл | Назначение |
|---|---|
| `docs/mobileApi/openapi.yml` | OpenAPI мобильного API |
| `docs/frontend/openapi.yml`, `docs/frontend/entry-architecture.md` | OpenAPI и архитектура фронтенда |
| `docs/ssr/openapi.yml` | OpenAPI SSR |
| `docs/diagrams/bnpl/abstractPayement.mmd` | Mermaid-диаграмма BNPL |
| `docs/diagrams/elastic/*.mmd` | Mermaid-диаграммы Elasticsearch |
| `docs/diagrams/yandex-split/*.mmd` | Mermaid-диаграммы Yandex Split |
| `docs/setup/setup-guide.md`, `docs/setup/README.md` | Руководство по установке |
| `docs/sale/categories-sale.md` | Распродажи по категориям |
| `docs/errors.yaml` | Коды ошибок |
| `ai-tasks/jwt-auth/api-contract.md` | API-контракт JWT-авторизации |
| `ai-tasks/jwt-auth/step-*.task.md` | Пошаговые задачи JWT |

---

## 8. Быстрые подсказки по поиску

1. **Возвраты (клиентские):** ищи `Refund`, `Return`, `refund`, `return` в `modules/orders/`, `modules/users/`, `src/Modules/Order/`, `src/Modules/Mobile/`.
2. **Чеки возврата:** ищи `Refund` в `src/Modules/Receipt/`.
3. **Статусы:** `StatusEnum` в `src/Modules/Order/Enum/`, константы `STATUS_*` в `modules/orders/models/Order.php` и `OrderPosition.php`.
4. **Таблицы БД:** ищи `tableName()` в моделях (`{{%...}}`), миграции в `migrations/`.
5. **Маршруты:** `config/url.php` — маппинг URL → контроллер/action.
6. **Outbox-интеграции:** `src/Modules/Order/Services/Outbox/`, `src/Modules/Order/Repository/*Outbox*`.
7. **Мобильное API:** `src/Modules/Mobile/Controllers/` (новый слой), `modules/mobile/`, `modules/mobilev2/` (старый слой).
8. **Тесты возврата:** `tests/Modules/Order/Services/OrderRefundServiceTest.php`, `tests/Modules/Order/Validators/OrderRefundValidatorTest.php`.