# Структура репозитория 12storeez-master-web

**Назначение документа:** карта-справочник по кодовой базе `12storeez-master-web` (до переименования — `12storeez-master`; Yii2 PHP-монолит интернет-магазина 12Storeez) для быстрого поиска информации при анализе требований и разработке.

**Дата актуализации:** 07.11.2026 (первая версия — 06.09.2026; раздел 5.1 дополнен 12.09.2026 по итогам сверки с реальным iOS-клиентом)
**Сверено с кодом:** ветка develop, коммит `dd4a997ac0` (03.11.2026); предыдущая база соседних документов — `be3cd759d2` (07.10.2026), между ними 191 коммит без merge. Для справки: `origin/master` = `9197ef5286`.
**Примечание:** структура описана по фактическому содержимому папок; назначение модулей — по названиям и ключевым классам.

---

## 1. Общая архитектура

- **Стек:** PHP 8.2+ (Yii2), MariaDB 10.3 (не MySQL 8 — оконные функции/CTE/JSON работают иначе), Redis, RabbitMQ, Elasticsearch, Sphinx, Docker/Kubernetes (Helm в `.deploy/helm/`); фронтенд — Vue 2.7 + Webpack 5 (по `CLAUDE.md`).
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
| `migrations/` | Миграции БД (220 миграций на `dd4a997ac0`, плюс `.gitignore` и папка `ImportData`; на `be3cd759d2` — 208) |
| `components/` | Компоненты: `goqr/`, `mindbox/` (легаси-клиент Mindbox), `rabbitmq/`, `MindboxComponent.php`, `SqlQueue.php`, Dadata, Geocode, Huntflow и др. |
| `coreExtends/` | Расширения ядра (исключения, логирование) |
| `di/` | DI-контейнер (определения сервисов) |
| `eventHandlers/` | Обработчики событий (`MenuCacheReloaderHandler.php`) |
| `helpers/` | Хелперы: Color, Db, Image, MobileVersionChecker, MoneyFormat, String, Transliterate |
| `validators/` | Валидаторы: `auth/`, `base/`, `order/` (в т.ч. `OrderRefundRequestValidator`) |
| `widgets/` | Виджеты |
| `themes/` | Темы оформления (basic) |
| `translations/` | Переводы (i18n) |
| `frontend/` | Фронтенд (Vue 2.7 + Webpack 5, Storybook: `.storybook/`, `src/`, `docs/`, `eslint/`, `frontend.Dockerfile`; в старой версии карты ошибочно — React) |
| `www/` | Web-корень: assets, documents, external, favicons, giftcards, jwk, offline, seo, temporary-feeds, service worker'ы (`sw.js`, `mindbox-services-worker.js`) |
| `docs/` | Документация: `openapi/` (`mobile.yml`/`.html`, `frontend.yml`/`.html`, `readme.md`), `diagrams/` (mermaid), `frontend/`, `sale/`, `setup/`, `errors.yaml`. Папок `mobileApi/` и `ssr/` больше нет (перенесены/удалены 16.09.2026) |
| `ai-tasks/` | Служебная папка AI-процессов: правила (`ai-rules.md`, `ai-traps.md`, `working-agreement.md`, `commit-messages.md`, `setup.md`, `task-template.md`, `dod-ai-template.md`), агенты `agents/` (phpstan-rule-writer, retro, software-analyst, test-plan-reviewer, unit-test-writer), разобранные задачи `jwt-auth/`, `ECOMDEV-1952/` |
| `openspec/` | **Новое (после `be3cd759d2`).** OpenSpec: `config.yaml`, действующие спецификации `specs/<capability>/spec.md` (15 шт.: web-reservation-order, reservation-expiration/instructions, mobile-metadata-api, admin-mobile-content, early-access, product-size-*, catalog-jeans-size-filters, special-promo-code, gender-context-persistence, order-review-prompt, product-color-naming, mobile-app-settings, dev-harness), архив изменений `changes/archive/<дата>-ecomdev-NNNN-*/` (proposal, design, tasks, test-plan) — полезный источник «зачем и что» по задачам ECOMDEV с 28.09.2026 |
| `.claude/` | **Новое.** Настройки Claude Code для разработчиков: `agents/` (code-reviewer, qa, security, software-analyst, test-plan-reviewer, unit-test-writer), `commands/opsx/*` (OpenSpec), `rules/*.md` (тематические правила: backend, catalog, delivery, deploy-config, feeds, frontend, mindbox, mobile-api), `skills/openspec-*`, `settings.json` |
| `CLAUDE.md` | **Новое.** Инструкции AI-ассистенту: команды, гейты CI, три области кода (`modules/`, `src/`, корневые слои), таблица параллельных реализаций (легаси/новая), правила веток и Трекера |
| `Makefile` | **Новое.** Обёртки проверок в docker-контейнере `monolith-backend`: `lint`, `stan_src`/`stan_legacy`, `cs`, `test`, `check_files`, `check_branch`, `db_snapshot`/`db_restore`, `migrate`, `es_index_*`, TestIT |
| `.cocoindex_code/`, `.gitlab/` | **Новое.** Настройки индекса семантического поиска cocoindex; шаблон MR GitLab |
| `.deploy/` | Helm-чарты и values по окружениям (dev, fix, mobiledev, sandbox, stg, prod) |
| `tests/` | Тесты (phpunit) |
| `mail/` | Шаблоны писем |
| `jwt_keys/` | Ключи JWT |
| `runtime/` | Runtime-файлы |
| `stubs/` | Стабы |
| `utils/` | Утилиты (раньше было «пусто» — устарело): `check-branch.sh`, `db-snapshot.sh`, `ai-preview.sh`, кастомные правила PHPStan `phpstan/src/Rules/*`, экспорт тест-планов `testit/` |
| `dump.rdb` | Дамп Redis |
| `composer.json`, `package-lock.json` | Зависимости PHP/JS |
| `docker-compose.yaml`, `backend.Dockerfile`, `nginx.conf`, `bootstrap.sh`, `check-migrate-trigger.sh` | Инфраструктура (`check-migrate-trigger.sh` — гейт CI «миграции по orders/order_positions/products должны трогать *_history») |
| `phpstan.neon`, `phpstan_6lvl_src.neon`, `phpcs.xml`, `phpunit.xml` | Качество кода (PHPStan уровня 2 для легаси, уровня 6 для `src/`) |
| `openapi-coverage.php` | Проверка покрытия OpenAPI |
| `yii`, `yii.bat`, `Yii.php`, `init`, `migrateup`, `php-cli` | CLI-точки входа |

---

## 3. `modules/` — старый слой (63 модуля на `dd4a997ac0`; было 64 — удалён `userActivities`, переехал в `src/Modules/User`)

### 3.1. Ключевые бизнес-модули

| Модуль | Назначение | Ключевые классы |
|---|---|---|
| `orders/` | **Заказы** (ядро): модели Order/OrderPosition, возвраты, статусы, outbox Lamoda | `models/Order.php`, `models/OrderPosition.php`, `models/OrderReturnPosition.php`, `models/ReturnReason.php`, `models/ReturnReasonGroup.php`, `controllers/RefundController.php`, `repositories/OrderReturnReasonRepository.php`, `repositories/OrderReturnReasonGroupRepository.php`, `repositories/OrderPositionRepository.php`, `repositories/OrderReturnPositionRepository.php`, `services/OrderService.php`, `services/LamodaOrderOutboxService.php` |
| `users/` | **Пользователи, ЛК, возвраты**: профиль, адреса, реквизиты возврата, wishlist, RBAC | `models/UserRefund.php`, `controllers/UserRefundController.php`, `services/UserRefundService.php`, `repositories/UserRefundRepository.php`, `forms/SaveReasonForm.php`, `forms/RefundBankDataForm.php`, `extractors/UserReturnReasonExtractor.php`, `extractors/UserReturnReasonGroupExtractor.php`, `validators/UserRefundMobileValidator.php` |
| `catalog/` | Каталог товаров, категории, коллекции | `dictionaries/ItemStockDictionary.php`, `dictionaries/LastSearchTermDictionary.php`. ~~`GroupCategoryDictionary`, `BlockCategoryDictionary`~~ и вся админка «Блок категорий» (`BlockCategoryBackendController`, модель/форма/репозиторий/сервис `BlockCategory*`) удалены в ECOMDEV-2228 вместе с Redis-группой `BlockCategories`; `extractors/StockSiteExtractor.php` тоже удалён (ECOMDEV-2228/1508) |
| `product/` | Товары, размеры, цены, изображения | `models/Product/Product.php`, `models/ProductSize.php`, `service/ProductService.php`, `service/ProductEnrichService.php`, `service/ProductReservationAvailabilityService.php` (новый). Экшен городов товара (`product-cities`) перенесён в `src/Modules/Product/Controller/ProductController::actionProductCitiesJson` |
| `cart/` | Корзина | — |
| `payment/` | Платежи | — |
| `delivery/` | Доставка, ПВЗ, возвраты ТК | ~~`repository/TaxRepository.php`~~ и веб-экшен `/delivery/delivery/tax` удалены (ECOMDEV-2180) |
| `bonuses/` | Бонусная программа | — |
| `giftcards/` | Подарочные сертификаты | — |
| `discounts/` | Скидки, промокоды | — |
| `processing/` | Обработка заказов, скидки на позиции | `interfaces/DiscountablePosition.php`, `models/ManualDiscount.php` |
| `statuses/` | Справочник статусов | `models/OrderPositionStatus.php` |
| `retailCrm/` | Интеграция RetailCRM | — |
| `mindbox/` | Интеграция Mindbox (легаси; новый код — `src/Modules/Mindbox/` и `src/Integration/Mindbox/`, см. 4.1) | — |
| `atol/` | Интеграция АТОЛ (чеки) | — |
| `yandex/` | Yandex Pay/Касса | `controllers/PayController.php`, `services/PaymentService.php`, `models/PaymentLog.php` |
| `lifepay/` | LifePay | — |
| `bonuses/` | Бонусы | — |
| `feedback/` | Отзывы | `models/Feedback.php`, `models/FeedbackProduct.php`, `models/CardPoll.php`, `models/Tag.php` (файла `FeedbackPosition.php`, указанного в старой версии карты, в репозитории нет) |
| `support/` | Поддержка | — |
| `notification/` | Уведомления | — |
| `wishlist/` | Избранное | `services/WishlistService.php`, `controllers/WishlistController.php` |
| `vacancy/` | Вакансии | `service/JobVacancyService.php`, `models/JobVacancy.php` |
| `blog/` | Блог | — |
| `content/` | Контент | — |
| `cms/` | CMS-ядро (модели, контроллеры, виджеты) | `controllers/FrontendController.php`, `models/Model.php` |
| `common/` | Общее: виджеты, валидаторы | `widgets/gridview/CommonGridView.php`, `validator/NoUrlTagValidator.php` |
| `api/`, `api2/` | API (старые версии) | `controllers/OrdersController.php` (api2), `service/ExchangeStockService.php`, `repository/ExchangeStockRepository.php` |
| `mobile/` | Остатки старого мобильного модуля: **контроллеров нет**; модели `MobileInfo`, `MobileMessage`, `UserAuthToken`, `UserMobileSession`, репозиторий `MobileMessageRepository`, вьюхи админок `mobile-info-backend`/`mobile-message-backend` | ~~`models/MobileBanner*`, `views/banner-backend/*`~~ — админка «MOBILE Баннер» удалена (ECOMDEV-2228) |
| `mobilev2/` | Мобильное API v2 (легаси, id модуля `mobilev2`; каталог, поиск и карточка товара — только здесь) | `controllers/`: Android, Apple, Delivery, Feedback, Giftcards, Home, Notification, Orders, Products, Profile, Subscribtions, Ulink, Wishlist. ~~`CategoryController`, `StoresController`~~, `CategoryDictionary`, `CategoryListForm`, `MobileBanner`, `CityRepository`, `WarehouseRepository` удалены (ECOMDEV-2228: v2 category/list, home/banners, stores, stores/cities) |
| `abTest/` | A/B-тесты | `services/AbTestService.php` |
| `geo/`, `location/` | Гео, города | — |
| `google/` | Google Analytics | `models/Operation.php` |
| `diginetica/` | Рекомендации Diginetica | — |
| `feed/` | Фиды | — |
| `marketing/` | Маркетинг | — |
| `poll/`, `contest/`, `popmechanic/`, `onelink/`, `redirect/`, `redirecturl/`, `social/`, `subscription/`, `smsRateLimiter/`, `rates/`, `banks/`, `blocks/`, `care/`, `completeMessages/`, `home/`, `layout/`, `lookbook/`, `mainpage/`, `navigation/`, `news/`, `present/`, `shopping/`, `automatic/`, `gii/`, `grpc/` (сгенерированный gRPC-код 1С), `widget/` | Вспомогательные/прочие | ~~`userActivities/`~~ — модуль удалён (ECOMDEV-2310): модель `UserActivityModel` переименована в `src/Modules/User/Models/`, репозиторий и сервис — `src/Modules/User/Repository/UserActivitiesRepository.php`, `src/Modules/User/Service/UserActivitiesService.php` |

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
| `Modules/` | Бизнес-модули (44 шт.) |
| `Integration/` | Интеграции: Captcha (ReCaptcha, SmartCaptcha), Common, Communication (Flomni), Microservice (Bfb), Notification, Payment (Yandex Pay/SBP/Split, AlphaPodeli, TbankDolyame), **Mindbox** (новое, ECOMDEV-2342: `MindboxConfigurator`, `Client/MindboxMobileClient`, `Service/MindboxMobileDeviceService`, `Builder/MindboxExternalIdBuilder`, `Enum/MindboxMobileDeviceActionEnum` — мобильные устройства/авторизация МП в Mindbox; события отправляются асинхронно через RabbitMQ, removeDevice для МП убран) |
| `Queue/` | Очереди: `SqlQueueName.php`, `RabbitMqQueueName.php`, `SqlQueueHelper.php`, `DiHelper.php`, `Service/RabbitMqPublisherService.php` (новый, ECOMDEV-2342) |
| `Search/` | Поиск: `Elastic/` (клиент, сервисы, индексация каталога) |
| `Monitoring/` | Мониторинг: `Sentry/` |
| `Auth/` | Аутентификация (JWT); новое — отправка/проверка SMS-кода: `Client/PhoneCodeClientInterface`, `MindboxPhoneCodeClient`, `LocalPhoneCodeClient`, `Dto/PhoneCode*`, `Enum/PhoneCodeErrorEnum` |
| `Cache/` | Кэш |
| `Cart/` | Корзина |
| `Common/` | Общее: хелперы (LogHelper, YiiDbHelper, YiiTranslateHelper), enum, utils |
| `Framework/` | Фреймворк-обвязка |
| `Http/` | HTTP (в т.ч. новый `Request/EmptyRequest.php` для экшенов без параметров) |
| `User/` | Пользователи — два Yii-модуля: **`userApi`** (`User/Module.php`, новое) — `Controller/UserApiController.php` (под `HttpBearerAuth` из `modules/api2/auth`: `user/search`, `user/{id}/orders`, `user/create`, `PATCH user/{id}`; операции `Operation/UserSearchOp`, `UserOrdersOp`, `CreateUserOp`, `UpdateUserOp`; сервисы `UserSearchService`, `UserFavoritesService`), `Controller/ProfileController.php` (`actionPermissions` → `/profile/permissions`), `Controller/UserController.php` (`api/user/me` под JWT), `Rule/UrlRule.php`; **`userNotifications`** — `Notifications/*` (уведомления пользователя) |

### 4.2. `src/Modules/` — бизнес-модули (44 шт.; новый — `Discount/`)
| Модуль | Назначение | Ключевые классы |
|---|---|---|
| `Order/` | **Заказы (новый слой)**: сервисы, outbox/inbox, возвраты | `Services/OrderService.php`, `Services/OrderRefundService.php`, `Services/OrderCancelService.php`, `Services/Inbox/OrderUpdateService.php`, `Services/Outbox/*`, `Validators/OrderRefundValidator.php`, `Dto/OrderUpdateDto.php`, `Dto/OrderRefundItemDto.php`, `Dto/Inbox/OrderOneCInboxDto.php`, `Dto/Inbox/OrderReturnPositionDto.php`, `Model/Order.php`, `Repository/OrderRepository.php`, `Enum/StatusEnum.php`, `Enum/PaymentMethodEnum.php`, `Enum/LastSourceEnum.php`, `Helpers/OrderHelper.php`, `AfterSaveEvent/*`; новые — `Services/CreateOrder/AbstractCreateReservationService.php`, `CreateReservationServiceSite.php` (веб-бронирование), `Services/OnlineOrderHistoryService.php`, `Services/OfflineOrderService.php`, `Services/OrderEcommerceDataService.php`, `Dto/OnlineOrder*Dto.php` |
| `Receipt/` | **Чеки/ОФД (АТОЛ)**: продажа, возврат, коррекция | `Service/OrderReceiptService.php`, `Service/ReceiptService.php`, `Service/ReceiptBuilder.php`, `Service/ReceiptSender/*` (SellPrepayment, SellFullpayment, RefundPrepayment, RefundFullpayment), `Repository/OrderPositionRefundRepository.php`, `Repository/OrderPositionRequireRefundReceiptRepository.php`, `Model/OrderPositionRefund.php`, `Model/OrderPositionRequireRefundReceipt.php`, `Enum/OperationEnum.php`, `Enum/EndpointEnum.php`, `Job/SendJob.php`, `Job/OfdJob.php`, `Console/ReceiptController.php`, `Console/ReceiptOutboxController.php` |
| `Mobile/` | **Мобильное API (новый слой)** | `Controllers/OrdersController.php` (actionReturnPositions, actionReturnDetails, actionReturnMethodList), `Controllers/UserController.php` (в т.ч. новые `actionAuthPhoneCode` → `/mobile/user/auth-phone-code`, ECOMDEV-2342; `actionLastContext` → `GET/PUT mobile/user/last-context`), `Controllers/ReservationController.php`, `Controllers/CartBaseController.php`, `Controllers/ApiBaseController.php`, `Validator/UserRequestFieldValidator.php` (новый), `Rules/UrlRule.php`. Остальные контроллеры: Cart*, Catalog, Category, Cities, Delivery, Feedback, Lookbooks, Metadata, Payment, Products, Profile, Static, Stores, Subscribtions, Support, UserActivities, UserAddress, Version, Wishlist, MobileInfoBackend, MobileMessageBackend. **Удалены:** ~~`GeoController`, `HomeController`, `VirtualCardController`, `BannerBackendController`, `Extractors/TaxExtractor.php`, `Services/MobileMindboxAuthService.php`~~ (ECOMDEV-2228, ECOMDEV-2180, ECOMDEV-2342); из оставшихся контроллеров убраны экшены v1 category/collections, metadata/colors, metadata/tags, delivery/intervals, delivery/taxes, locations/geo, payment/yandex |
| `OneC/` | Интеграция 1С | — |
| `Rcrm/` | Интеграция RetailCRM (outbox) | `Service/RcrmOutboxService.php` |
| `Mindbox/` | Интеграция Mindbox (outbox, процессинг заказов, бонусы) | `Service/MindboxOutboxService.php`, `Service/MindboxService.php`, `Service/MindboxIntegrationToggleService.php` (новый: CMS-параметр `mindbox_integration_enabled`), `Client/MindboxClient.php`, `Client/MindboxCachedClient.php`, `Enum/MindboxStatusEnum.php`; ~~`Configurator/MindboxClientConfigurator.php`~~ удалён — конфигурация мобильного клиента в `src/Integration/Mindbox/MindboxConfigurator.php` |
| `Discount/` | **Новое.** Скидки (новый слой) | `Repository/DiscountRepository.php`, `Service/DiscountService.php` |
| `Delivery/` | Доставка, способы возврата | `Enum/ReturnMethodEnum.php`, `Helper/PickupHelper.php` |
| `Payment/` | Платежи | — |
| `Giftcard/` | Подарочные сертификаты | `Service/GiftcardCreateOrderService.php`, `Service/GiftcardAntiFraudService.php`, `Service/GiftCardCartService.php` |
| `Stock/` | Остатки | — |
| `Reservation/` | Резервы; **веб-бронирование** (Yii-модуль `reservation`, новое) | `Controller/ReservationController.php` (`POST reservation/cart` → actionCreateCart, `POST reservation` → actionCreateOrder, `GET reservation/expiration`, `GET reservation/instructions`), `Operation/CreateCartOp`, `CreateOrderOp`, `StoreExpirationOp`, `ReservationInstructionsOp`, `Service/ReservationCartExpirationService.php`, `ReservationOrderUrlService.php`, `StockReservationEnricher.php`, `Exception/Reservation*Exception.php` |
| `Checkout/` | Оформление заказа | — |
| `Cart/` | Корзина | новые `Service/SpecialPromoCodeChecker.php`, `Exception/PromoCodeLoyalityProgramException.php` (ECOMDEV-2377) |
| `Product/` | Товары (Yii-модуль `productV2`) | `Controller/ProductController.php` — `actionStoreAvailability` (`/product/product/{id}/store-availability`), `actionProductCitiesJson` (`product/product/product-cities/{id}`, перенесён из `modules/product`), `actionRecommendations`, `actionGetUrlByArticle`; `Service/StoreAvailabilityService.php`, `EarlyAccessEligibilityService.php`, `JeansSizeFilterService.php`, `ProductSizeInfoService.php`, `SizeTableTypeResolver.php`, `ProductColorTitleService.php`; `Operation/ProductCitiesOp`, `ProductStoreAvailabilityOp` |
| `User/` | Пользователи | `Services/UserService.php`, `Services/UserRegistrationService.php`, `Services/UserAddressService.php`, `Services/UserProfileUpdateService.php`, `UserIdentityCacheService.php`, `UserInfoCacheService.php` (новые), `Repository/UserWishlistRepository.php`; **перенесено из `modules/userActivities`**: `Models/UserActivityModel.php`, `Repository/UserActivitiesRepository.php`, `Service/UserActivitiesService.php`; `Dto/Permission/*` (для `/profile/permissions`) |
| `Auth/` | Аутентификация | — |
| `Api/`, `Api2/` | API (`Api2` — Yii-модуль `api2_new`) | `Api2/Controller/OrdersController.php` (в т.ч. `actionReturnMethodList`, `actionReturnDetails` — `api/orders/{id}/return-method-list`, `return-details`) |
| `Cms/` | CMS | `Model/Parameter.php` |
| `Common/` | Общее | `Helpers/LogHelper.php`, `Helpers/YiiDbHelper.php`, `Helpers/YiiTranslateHelper.php`, `Enum/LogMessageEnum.php`, `Utils/UuidUtils.php`; новые `Component/CacheKeyPrefix.php` (префикс ключей кэша, вызывается в `config/web.php:300-304`), `Operation/OperationInterface.php` (паттерн Operation/Request для новых экшенов), `Dictionary/Duration.php` |
| `Mainpage/` | Главная страница | `Controllers/MainpageController.php` (`actionLastContext` → `POST /home/last-context`), `Service/LastContextService.php` (новый: последний контекст пользователя, сохраняется в профиль; используется и в МП `mobile/user/last-context`), `Service/MainpageService.php` |
| `Analytics/` | Аналитика | — |
| `Metrics/` | Метрики | — |
| `Notifications/` | Уведомления | — |
| `Images/` | Изображения, S3 | `Service/ImageResizeService.php`, `Client/S3Client.php`, `Console/RabbitImageResizeConsolePopController.php` |
| `Vacancy/` | Вакансии (Huntflow) | `Service/HuntflowService.php` |
| `Wishlist/` | Избранное | `Service/WishlistService.php` |
| `YandexTracker/` | Yandex Tracker | `Service/YandexTrackerService.php`, `Client/YandexTrackerClient.php` |
| `ActionPresent/`, `Blog/`, `Feed/`, `Feedback/`, `Geo/`, `Landing/`, `Lookbook/`, `Marketing/`, `Menu/`, `Metadata/`, `MobileInfo/`, `MobileV2/`, `Navigation/`, `Poll/`, `Subscription/` | Прочие | — |

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
| Мобильный возврат | `src/Modules/Mobile/Controllers/OrdersController.php` (actionReturnPositions, actionReturnDetails, actionReturnMethodList) — маршрутизируются кастомным `src/Modules/Mobile/Rules/UrlRule.php` (regex по `orders/{id}/return[-details\|-method-list]`) |
| Мобильный возврат — способ/детали (путь `v1/delivery/...`) | iOS запрашивает `v1/delivery/{orderId}/return-method-list` и `v1/delivery/{orderId}/return-details` на хосте `mobile` — это маршруты **Go-шлюза** `mobile-monorepo-go` (`internal/app/service/delivery.go:166`, `:112`), а не монолита. Шлюз проксирует их в старые мобильные пути монолита `mobile/orders/{id}/return-method-list` и `mobile/orders/{id}/return-details` → `src/Modules/Mobile/Rules/UrlRule.php` → `Mobile/Controllers/OrdersController::actionReturnMethodList` (`:1327`) / `actionReturnDetails` (`:1258`). Подтверждено по коду шлюза (см. [../mobile-monorepo-go/repo-map.md](../mobile-monorepo-go/repo-map.md), [../12storeez-ios/repo-map.md](../12storeez-ios/repo-map.md) §4.3). Отдельные `GET api/orders/{order_id}/return-method-list` и `POST api/orders/{order_id}/return-details` (`config/url.php:234-235` → `src/Modules/Api2/Controller/OrdersController.php`, модуль `api2_new`, ECOMDEV-1239) — **веб-версия** для ЛК сайта (`frontend/src/modules/orders/services/OrderService.js:408`, `:315`), к мобильному пути отношения не имеет |
| Чеки возврата (АТОЛ) | `src/Modules/Receipt/` (OrderReceiptService, RefundPrepayment, RefundFullpayment, OrderPositionRefund) |
| Обновление заказа (updateOrder) | `src/Modules/Order/Services/OrderService.php` |
| Проверка возможности возврата | `src/Modules/Order/Helpers/OrderHelper.php` (canBeReturned, canPositionBeReturned, isReturned) |
| Статусы возврата | `src/Modules/Order/Enum/StatusEnum.php`, `modules/orders/models/Order.php` (STATUS_ORDER_RETURNED_LK=31, STATUS_REFUND_REQUEST_*) |

### 5.2. Процесс создания заказа
| Что искать | Где |
|---|---|
| Создание заказа (сайт) | `src/Modules/Order/Services/CreateOrder/CreateOrderServiceSite.php` |
| Создание заказа (МП) | `src/Modules/Order/Services/CreateOrder/CreateOrderServiceMobile.php` |
| Создание заказа (корзина) | `src/Modules/Order/Services/CreateOrder/AbstractCreateOrderService.php`, `src/Modules/Order/Services/CartOrderCreateDtoPrepareService.php` (лежит в `Services/`, не в `CreateOrder/`) |
| Создание брони (сайт) | `src/Modules/Order/Services/CreateOrder/CreateReservationServiceSite.php` (наследник `AbstractCreateReservationService`), вызывается из `src/Modules/Reservation/Operation/CreateOrderOp.php` |
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
| Mindbox | `src/Modules/Mindbox/`, `src/Integration/Mindbox/` (мобильные устройства/авторизация МП, ECOMDEV-2342), `src/Auth/Client/MindboxPhoneCodeClient.php`, `components/MindboxComponent.php`, `components/mindbox/`, `src/Modules/Order/Repository/MindboxOrder*`; три пути запросов описаны в `.claude/rules/mindbox.md` репозитория |
| Lamoda | `modules/orders/services/LamodaOrderOutboxService.php`, `src/Modules/Order/Services/LamodaOrderService.php` |
| Mercaux | `modules/api2/service/UserMercauxService.php`, `src/Modules/Order/Services/MercauxOrderCreateDtoPrepareService.php` |
| АТОЛ (чеки) | `src/Modules/Receipt/` |
| Elasticsearch | `src/Search/Elastic/` |
| RabbitMQ | `src/Queue/` (в т.ч. `Service/RabbitMqPublisherService.php`), `components/rabbitmq/` |

### 5.5. Новые точки входа (после `be3cd759d2`)
| Что искать | Где |
|---|---|
| Веб-бронирование в магазине | `src/Modules/Reservation/Controller/ReservationController.php`; маршруты `config/url.php:285-288` (`POST reservation/cart`, `GET reservation/expiration`, `GET reservation/instructions`, `POST reservation`); МП — `src/Modules/Mobile/Controllers/ReservationController.php` (`config/url.php:280-284`) |
| Наличие товара в магазинах / города товара (сайт) | `src/Modules/Product/Controller/ProductController.php` — `actionStoreAvailability` (`config/url.php:213`), `actionProductCitiesJson` (`config/url.php:214`) |
| Последний контекст пользователя | `src/Modules/Mainpage/Service/LastContextService.php`; сайт — `POST /home/last-context` (`config/url.php:15`, `MainpageController::actionLastContext`); МП — `GET/PUT mobile/user/last-context` (`src/Modules/Mobile/Controllers/UserController::actionLastContext`) |
| API пользователей для внешних систем (поиск, заказы, создание, изменение) | `src/User/Controller/UserApiController.php` (модуль `userApi`, `config/modules.php:102`; маршруты `config/url.php:142-145`: `GET user/search`, `GET user/{id}/orders`, `POST user/create`, `PATCH user/{id}`), авторизация `modules/api2/auth/HttpBearerAuth` |
| Права пользователя (заказ/бронирование) | `src/User/Controller/ProfileController::actionPermissions` → `/profile/permissions` (`config/url.php:23`), DTO `src/Modules/User/Dto/Permission/*` |
| Авторизация МП по коду из SMS | `src/Modules/Mobile/Controllers/UserController::actionAuthPhoneCode` → `/mobile/user/auth-phone-code`; клиенты `src/Auth/Client/*PhoneCodeClient.php` |
| Активности пользователя | `src/Modules/User/Service/UserActivitiesService.php` (бывш. `modules/userActivities`), МП — `src/Modules/Mobile/Controllers/UserActivitiesController.php` |

---

## 6. Конфигурация и маршрутизация

| Файл | Назначение |
|---|---|
| `config/common.php` | Общая конфигурация |
| `config/web.php` | Web-конфигурация (префикс ключей кэша — `CacheKeyPrefix::build(...)` в строках 300-304: хост, наличие cookie `_identity`, мобильное ли устройство; класс — `src/Modules/Common/Component/CacheKeyPrefix.php`) |
| `config/console.php` | Консольная конфигурация |
| `config/url.php` | **Маршруты URL** (в т.ч. `user/cabinet/return-item/*` → `users/user-refund/*`; новые — `reservation*`, `home/last-context`, `profile/permissions`, `user/*` userApi, `product/product/{id}/store-availability`) |
| `config/modules.php` | Подключение модулей (новые id: `userApi`, `reservation`; `productV2` — `src/Modules/Product`, `api2_new` — `src/Modules/Api2`, `deliveryV2`/`return` — `src/Modules/Delivery`) |
| `config/config.php`, `config/sphinx.php`, `config/phpstan-config.php`, `config/cron-web` | Прочая конфигурация (Sphinx, конфиг для PHPStan, cron) |
| `.deploy/helm/*.values.yaml` | Переменные окружения по стендам (dev, fix, mobiledev, sandbox, stg, prod) |
| `config/events.php` | События |
| `config/log.php` | Логирование |
| `config/i18n.php` | Переводы |
| `config/params_example.php` | Параметры (пример) |
| `di/` | DI-контейнер |

---

## 7. Документация и схемы

| Файл | Назначение |
|---|---|
| `docs/openapi/mobile.yml` (+ собранный `mobile.html`) | OpenAPI мобильного API (до 16.09.2026 — `docs/mobileApi/openapi.yml`); описания удалённых в ECOMDEV-2228 эндпоинтов убраны |
| `docs/openapi/frontend.yml` (+ `frontend.html`), `docs/openapi/readme.md`, `docs/frontend/entry-architecture.md` | OpenAPI и архитектура фронтенда; гейт CI `openapi-coverage.php` требует путь в `docs/openapi/*.yml` для каждого публичного `action*` веб-контроллера |
| ~~`docs/ssr/openapi.yml`~~ | OpenAPI SSR — удалён 16.09.2026 |
| `docs/diagrams/bnpl/abstractPayement.mmd` | Mermaid-диаграмма BNPL |
| `docs/diagrams/elastic/*.mmd` | Mermaid-диаграммы Elasticsearch |
| `docs/diagrams/yandex-split/*.mmd` | Mermaid-диаграммы Yandex Split |
| `docs/setup/setup-guide.md`, `docs/setup/README.md` | Руководство по установке |
| `docs/sale/categories-sale.md` | Распродажи по категориям |
| `docs/errors.yaml` | Коды ошибок |
| `ai-tasks/jwt-auth/api-contract.md` | API-контракт JWT-авторизации |
| `ai-tasks/jwt-auth/step-*.task.md` | Пошаговые задачи JWT |
| `CLAUDE.md`, `.claude/rules/*.md` | Инструкции разработчиков для AI: архитектура, параллельные реализации, тематические правила (mobile-api, delivery, catalog, mindbox, deploy-config, feeds) — хороший источник «как устроено» |
| `openspec/specs/*/spec.md`, `openspec/changes/archive/*/` | Спецификации возможностей и архив изменений по задачам ECOMDEV (proposal/design/tasks/test-plan) |

---

## 8. Быстрые подсказки по поиску

1. **Возвраты (клиентские):** ищи `Refund`, `Return`, `refund`, `return` в `modules/orders/`, `modules/users/`, `src/Modules/Order/`, `src/Modules/Mobile/`.
2. **Чеки возврата:** ищи `Refund` в `src/Modules/Receipt/`.
3. **Статусы:** `StatusEnum` в `src/Modules/Order/Enum/`, константы `STATUS_*` в `modules/orders/models/Order.php` и `OrderPosition.php`.
4. **Таблицы БД:** ищи `tableName()` в моделях (`{{%...}}`), миграции в `migrations/`.
5. **Маршруты:** `config/url.php` — маппинг URL → контроллер/action.
6. **Outbox-интеграции:** `src/Modules/Order/Services/Outbox/`, `src/Modules/Order/Repository/*Outbox*`.
7. **Мобильное API:** `src/Modules/Mobile/Controllers/` (v1, новый слой), `src/Modules/MobileV2/` и `modules/mobilev2/` (v2; каталог/поиск/карточка — в легаси `modules/mobilev2`). В `modules/mobile/` контроллеров больше нет. Удалённые эндпоинты — `openspec/changes/archive/2026-10-21-ecomdev-2228-remove-unused-mobile-endpoints/`.
8. **Тесты возврата:** `tests/Modules/Order/Services/OrderRefundServiceTest.php`, `tests/Modules/Order/Validators/OrderRefundValidatorTest.php`.
9. **Поиск по всему коду:** кроме `src/` и `modules/` проверяй корневые слои `coreExtends/`, `components/`, `di/` (namespace `app\`). Одна сущность часто есть в двух реализациях (заказ, репозиторий товаров, мобильный API v2, Redis, параметры CMS, варианты доставки) — таблица в `CLAUDE.md`, раздел «Параллельные реализации».
10. **Зачем сделано изменение:** ищи по ключу задачи в `openspec/changes/archive/` и в `git log --grep=ECOMDEV-NNNN`.

---

## 9. История изменений

| Дата | Автор | Что обновлено | Коммит |
|---|---|---|---|
| 06.09.2026 | — | Первая версия карты (репозиторий под именем `12storeez-master`) | не указан |
| 07.11.2026 | repository-researcher | Сверка с develop: новые корневые папки (`openspec/`, `.claude/`, `CLAUDE.md`, `Makefile`, `.cocoindex_code/`, `.gitlab/`), `utils/` больше не пустая, пересчёт миграций (222) и модулей (`modules/` 63, `src/Modules/` 44); удалённое в ECOMDEV-2228/2180 (BlockCategory, MobileBanner, мобильные Geo/Home/VirtualCard, mobilev2 Category/Stores, TaxRepository); перенос `userActivities` в `src/Modules/User`; новые `src/User` (userApi, `/profile/permissions`), `src/Integration/Mindbox` (ECOMDEV-2342), `src/Modules/Discount`, веб-бронирование, `ProductController` (store-availability, product-cities), `LastContextService`, `CacheKeyPrefix`; раздел 5.5; исправлены ошибки старой версии (React → Vue, MySQL → MariaDB, `FeedbackPosition`, путь `CartOrderCreateDtoPrepareService`, `docs/mobileApi`) | `dd4a997ac0` |