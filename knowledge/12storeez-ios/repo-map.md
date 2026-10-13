# Структура репозитория 12storeez-ios

**Назначение документа:** карта-справочник по кодовой базе iOS-приложения 12Storeez: где что лежит, какие запросы приложение шлёт, через какой шлюз и куда они уходят дальше. Для быстрого поиска при анализе требований.

**Дата актуализации:** 10.10.2026
**Сверено с кодом:** ветка `develop`, коммит `a6de858b` (`a6de858beed5c32b8c92fcebf270293681e08894`, 05.10.2026, «Merge tag '1.86.1' into develop»)
**Код:** `C:\Users\RobotComp.ru\Desktop\12stz\12storeez-ios\` (только чтение; remote `gitlab.12storeez.com/mobile/ios/12storeez-ios`)
**Схема цепочки вызовов:** [../architecture/call-chain.html](../architecture/call-chain.html) — iOS → шлюз → монолит → внешние системы, по каждому вызову.
**Примечание:** пути ниже — от корня репозитория. `Business/` = `TwelveStoreez/Classes/Business/`, `Endpoints/` = `Business/Network/Endpoints/`. Где вывод сделан по названию, а не по коду, — помечено.

---

## 1. Общая архитектура

- **Тип:** нативное iOS-приложение на Swift, UIKit + Storyboard. Workspace `TwelveStoreez.xcworkspace`, проект `TwelveStoreez.xcodeproj`, таргеты: приложение, `NotificationService` (rich push), `TwelveStoreezTests`.
- **Паттерн:** MVC со слоем Manager/Service и DI-контейнером **Dip** (`Business/Factories/ManagersAssembly.swift`, `VCAssembly.swift`). ViewModel/Interactor/Coordinator нет, переходы — `UIStoryboardSegue`.
- **Зависимости:** библиотеки — **Swift Package Manager** (`TwelveStoreez.xcworkspace/xcshareddata/swiftpm/Package.resolved`); CocoaPods (`Podfile`) — только тулинг SwiftGen и SwiftLint. Плюс Mint, Brewfile, fastlane. Бинарные `Frameworks/`: Crashlytics, TMX Profiling.
- **Сеть:** Alamofire. Два своих хоста (см. §5): `core.12stz.com/api` — старый шлюз (`12stz/esb-monorepo`) и `mobile.12stz.com/api` — новый шлюз (`12stz/mobile-monorepo-go`). Оба почти всё проксируют в монолит `12stz/12storeez-master-web`. Третий хост — трекинг Diginetica.
- **Локальное хранение:** заказы, корзина, возвраты — только в памяти. CoreData — только история push (`NotificationEntity+*.swift` в корне). Токены — `AuthTokenHolderManager` (Keychain, `keychainaccess`).

---

## 2. Корневые папки

| Папка / файл | Назначение |
|---|---|
| `TwelveStoreez/Classes/` | Весь код приложения (§3) |
| `TwelveStoreez/Resources/` | Storyboard'ы, ассеты, локализация (`L10n`), plist; `Configuration/*.xcconfig` — хосты (§5) |
| `TwelveStoreezTests/` | Юнит-тесты |
| `NotificationService/` | Notification Service Extension: скачивает картинку push (`NotificationService.swift`) |
| `Frameworks/` | Crashlytics, TMX Profiling (антифрод, отпечаток устройства) |
| `Patch/` | Патч тулинга Xcode 16 |
| `ci_scripts/`, `fastlane/`, `hooks/`, `Makefile` | CI и сборка (Bitrise — `fastlane/bitrise.yml`), `make bootstrap` |
| `.swiftlint.yml`, `.swiftformat`, `swiftgen.yml`, `.bartycrouch.toml` | Линтеры, генерация кода, локализация |

---

## 3. `TwelveStoreez/Classes/` по слоям

| Папка | Назначение |
|---|---|
| `Modules/<Фича>/` | ~95 папок, по одной на экран или фичу: `Home`, `Catalog`, `Product`, `Search`, `Cart`, `Checkout`, `MyOrders`, `MyOrderDetail`, `ReturnOrder`, `GiftCard`, `MyGiftCards`, `CreateReservation`, `Bonuses`, `Profile`, `Auth`, `Polls`, `Flomni` и др. Внутри — `XxxVC.swift`, ячейки, extension-файлы |
| `Business/Network/` | Сетевой слой: `RequestTarget.swift` (хост `core`), `RequestTargetNew.swift` (хост `mobile`), `RequestTargetDiginetica.swift`, `RequestDescription.swift` (сборка URL), `RequestProvider.swift` (Alamofire), `AuthRequestAdapter.swift` (JWT и его обновление), `BackendListService.swift` / `BackendListItemsService.swift` (пагинация), `Models/` (конверты ответа), `Errors/` |
| `Business/Network/Endpoints/` | Один файл — эндпоинт или группа. `enum … : RequestTarget` — хост `core`; `struct … : RequestTargetNew` — хост `mobile`. `CheckoutEndpoints/` — новый чекаут |
| `Business/Managers/` | `XxxManager` — состояние фичи и оркестрация вызовов. Папки: `Checkout/`, `Payment/`, `ReturnOrder/`, `Reservation/`, `Polls/`, `Analytics/`, `ABManagers/`, `Dresscode/`, `DebugManagers/` (переключатель хоста) |
| `Business/Services/` | Тонкие обёртки над `RequestProvider`: endpoint → типизированный ответ |
| `Business/Factories/` | DI (Dip): `ManagersAssembly.swift`, `VCAssembly.swift` |
| `Business/Constants/`, `Business/Helpers/` | Константы, хелперы (`DeviceIDGenerator.swift` — `x-device-id`) |
| `Models/` | Codable-модели; `Response/` — ответы, `Payload/` — тела запросов |
| `UIKit/` | Переиспользуемые UI-компоненты |
| `Generated/` | SwiftGen: `Plist.swift` (`baseURL`, `baseURLNew`, `digineticaURL`), сцены, сегвеи, `Strings.swift` |

---

## 4. Возврат товара (клиент, iOS)

### 4.1. Экраны (`Classes/Modules/ReturnOrder/`), в порядке навигации

| Экран | Файл | Назначение |
|---|---|---|
| Карточка заказа (точка входа) | `MyOrderDetail/MyOrderDetailVC.swift` | `didTapReturnedButton` → segue `returnOrder` в `ReturnOrderItemsVC`; передаёт `activeItemsForReturn`/`inactiveItemsForReturn` (фильтр по серверному `OrderItem.canBeReturned`, клиентской арифметики «N дней» нет) |
| Выбор позиций | `ReturnOrderItems/ReturnOrderItemsVC.swift` | `returnOrderManager.orderId`; `needBankData = orderDetail?.return?.isBankDataRequired ?? true` |
| Причина по каждой позиции | `ReturnOrderReasons/ReturnOrderReasonsVC.swift`, `ReturnOrderSelectReasonGroupVC.swift` | Грузит причины, собирает `items: [{barcode, reasonId}]` |
| Способ, город, дата, реквизиты | `ReturnOrderMethod/ReturnOrderMethodVC.swift` (+ extensions) | Секция `.address` — только при `methodType == .courier`; `.requisites` — только при `needBankData`. `confirmReturn()` → `returnOrderDetails` (POST) → `returnOrder` (POST) |
| Предупреждение о дате | `ReturnOrderMethod/ReturnOrderDateWarningVC.swift` | При отказе сервера по дате: код `20110`, `errorTarget == .returnOrderDate` (`date_return`) |
| Банковские реквизиты | `ReturnOrderUserRequisites/ReturnOrderUserRequisitesVC.swift` | ФИО, БИК (9), банк, ИНН банка (10), счёт (20), карта (16, маска) |
| Финал | `ReturnOrderFinishVC.swift` | Модалка подтверждения (`L10n.RetutnOrderFinish.*` — опечатка в коде) |

### 4.2. Manager/Service

| Класс | Файл | Роль |
|---|---|---|
| `ReturnOrderManager` | `Business/Managers/ReturnOrder/ReturnOrderManager.swift` | Синглтон: `returnOrder`, `returnOrderDetails`, `loadReasons`, `loadAvailableMethods`, `update*`, `flush()` |
| `ReturnOrderData`, `ReturnAddressData` | `Business/Managers/ReturnOrder/` | Состояние флоу; валидация адреса (индекс ≥ 6 цифр для стран не из `RU, AE, KZ, BY`) |
| `ReturnOrderService` | `Business/Services/ReturnOrderService.swift` | Проброс в `requestProvider` по 4 эндпоинтам |

### 4.3. Эндпоинты возврата и заказа — полная цепочка

| Назначение | iOS (endpoint) | Хост и путь | Шлюз | Монолит |
|---|---|---|---|---|
| Создать возврат (позиции + реквизиты) | `ReturnOrderEndpoint.returnOrder` | `core` POST `orders/{id}/return` | esb `libs/orders/controllers/src/lib/orders.controller.ts:254` | `mobile/orders/{id}/return` → `Mobile\Rules\UrlRule` → `src/Modules/Mobile/Controllers/OrdersController::actionReturnPositions` |
| Причины возврата | `ReturnOrderEndpoint.loadReasons` | `core` GET `orders/v2/return-reasons` | esb `orders.controller.ts:204` | `mobile/v2/orders/return-reasons` → `modules/mobilev2/controllers/OrdersController::actionReturnReasons` |
| Способы возврата по городу | `ReturnOrderMethodsEndpoint` | `mobile` GET `v1/delivery/{id}/return-method-list` | Go `internal/app/service/delivery.go:166` | `mobile/orders/{id}/return-method-list` → `OrdersController::actionReturnMethodList` (`:1327`) |
| Адрес, дата, способ возврата | `ReturnOrderDetailsEndpoint` | `mobile` POST `v1/delivery/{id}/return-details` | Go `delivery.go:112` | `mobile/orders/{id}/return-details` → `OrdersController::actionReturnDetails` (`:1258`) → `OrderService::updateOrderReturnDetails` → outbox RetailCRM |
| Список заказов | `OrdersEndpoint.orders` | `core` GET `orders` | esb `orders.controller.ts:54` + gRPC feedbacks `canBeSaved` | `mobile/orders` → `OrdersController::actionIndex` |
| Карточка заказа | `OrdersEndpoint.orderDetail` | `core` GET `orders/{id}` | esb `orders.controller.ts:227` + gRPC feedbacks | `mobile/orders/{id}` → `OrdersController::actionIndex` |
| Отмена заказа | `OrdersEndpoint.cancel` | `core` DELETE `orders` (тело `{order_id}`) | esb `orders.controller.ts:272` | `POST mobile/orders/cancel` → `OrdersController::actionCancel` |

Подробнее о шлюзах: [esb-monorepo §8.1](../esb-monorepo/repo-map.md), [mobile-monorepo-go §5](../mobile-monorepo-go/repo-map.md).

### 4.4. Модели данных

- **`ReturnOrderEndpoint.Payload`** (тело `POST orders/{id}/return`): `surname`, `name`, `patronymic`, `bankBic`, `bankName`, `bankInn`, `userAccount`, `userCardNumber`, `items: [{barcode, reasonId: [String]}]`.
- **`ReturnOrderDetailsEndpoint.Payload`**: `methodReturn`, `addressReturn`, `cityReturn`, `dateReturn`, `indexReturn`. Go-шлюз пропускает в монолит только эти 5 полей.
- **`ReturnOrderMethodsEndpoint.Payload`** (query): `countryIso`, `city`, `cityId`, `cityFias`, `region`, `regionId` (из `ConfirmedGeo`).
- **`ReturnOrderMethod`**: `method`, `methodType` (`pvz`/`courier`), `title`, `description`, `activeMobile`, `availableDatesReturn`. Клиент фильтрует `availableDatesReturn.isNotEmpty && activeMobile`.
- **`OrderDetail.Return.isBankDataRequired`**, **`OrderItem.canBeReturned`** — решения сервера, клиент только читает.

### 4.5. Клиентская логика

- Реквизиты обязательны только при `needBankData`; адрес — только для курьера (`ReturnOrderMethodVC.isFulfilledData()`).
- Ошибка `20110` по `date_return` → перезагрузка способов и `ReturnOrderDateWarningVC`.
- Состояние возврата живёт в памяти, `flush()` при `deinit` `ReturnOrderItemsVC`.

---

## 5. Сетевой слой: хосты, заголовки, авторизация

### 5.1. Хосты

| Протокол endpoint | Info.plist / xcconfig | Release | Debug / Internal | Код шлюза |
|---|---|---|---|---|
| `RequestTarget` | `BaseURL` / `BASE_URL` | `core.12stz.com/api` | `core.12stz.dev/api` | `12stz/esb-monorepo` (NestJS) |
| `RequestTargetNew` | `BaseURLNew` / `BASE_URL_NEW` | `mobile.12stz.com/api` | `mobile.12stz.dev/api` | `12stz/mobile-monorepo-go` (Go) |
| `RequestTargetDiginetica` | `DigineticaURL` | `tracking-app.diginetica.net/event` | `tracking-dev.diginetica.net/event` | внешний сервис |

- xcconfig: `TwelveStoreez/Resources/Configuration/{Base,Debug,Internal,Release}.xcconfig`; `https://` добавляется в `Business/Network/RequestDescription.swift:52-56`.
- В не-release сборках хост берётся из `Business/Managers/DebugManagers/DebugServerHostManager.swift:64-80`: пресеты `default`, `mobiledev`, `dev`, `fix`, `sandbox`, `stg` (пары `core-<env>.12stz.dev` / `mobile-<env>.12stz.dev`) и произвольный.
- Версия API — часть пути: у `core` пути в основном без версии (`products/v2/...` — внутри), у `mobile` — `v1/...`, `v2/...`.

### 5.2. Заголовки

| Заголовок | `core` | `mobile` | Где |
|---|---|---|---|
| Платформа | `x-platform: ios` | `X-Platform: ios` | `RequestTarget.swift`, `RequestTargetNew.swift` |
| Версия приложения | `Version` | `X-Version` | то же; Go-шлюз без них отвечает 400 |
| `Authorization: Bearer <JWT>` | да | да | `AuthRequestAdapter.swift`; кроме `PUT authorization/generate-token` и `v1/errors/waf` |
| `x-device-id` | только `generate-token` и `login` | — | `DeviceIDGenerator.swift` (Mindbox UUID → `identifierForVendor` → UUID) |
| `Canary: true` | при debug-флаге | при debug-флаге | `kCanaryAccessKey` |

### 5.3. Авторизация

- **Токен выдаёт только `core`.** iOS не вызывает `/api/v1/auth/*` Go-шлюза. Гостевой JWT — `PUT authorization/generate-token`; при 401 — `PUT authorization/session` с `refresh_token` и повтор запроса; при неудаче — снова гостевой токен (`AuthRequestAdapter.swift:105`, `:135`).
- **Тот же JWT уходит на `mobile`.** esb подписывает HS256 ключом из кода (`esb-monorepo/libs/core/src/lib/constants.ts:7-9`), срок 14 дней, claims `device_id`, `refresh_token`, `session_token`, `user_id`. Go-шлюз проверяет HS256 с `JWT_SECRET` из Vault. Значит, ключи должны совпадать — смена в одном месте ломает все вызовы на `mobile` (вывод по коду, значения не сверялись).
- Оба шлюза передают в монолит `session_token` из JWT заголовком `x-session-token` и свой сервисный `x-access-token`; монолит по нему находит пользователя.
- `503` на `GET authorization/session` → экран техработ (`TechnicalWorkVC`).

### 5.4. Ответы и ошибки

- Конверты (`Network/Models/SuccessDataResult.swift`): `SuccessResult {success, update_flags?}`, `SuccessDataResult<T> {result, success, total?}`, `SuccessCollectionResult<T>`, `ListResponse<T> {result, total}`.
- Ошибкой считается и тело с `success:false` при HTTP 2xx. Валидны только статусы 100–399.
- Ошибка — `ServerError {success:false, result: MessageError}` (`Network/Errors/`). Go-шлюз добавляет `isErrorFromPHP: true` к ответам монолита с кодом ≠ 200.
- WAF: HTML «Forbidden» на `authorization/login/by-phone` сохраняется (`RequestProvider.storeWafBlockIfNeeded`) и отправляется в `POST v1/errors/waf`.

---

## 6. Какие вызовы через какой шлюз идут

Полный список (≈150 вызовов, с файлами шлюза и `Controller::action` монолита) — в [../architecture/call-chain.html](../architecture/call-chain.html). Здесь — раскладка по доменам.

| Домен | Хост `core` (esb-monorepo) | Хост `mobile` (mobile-monorepo-go) |
|---|---|---|
| Авторизация, сессия | `authorization/*` (токен, сессия, логин по паролю и телефону, логаут), `profile/actions/restore-password` | `v1/settings`, `v1/users/device-session-token`, `v1/errors/waf` |
| Профиль | `profile` (GET/PATCH/DELETE), `password`, `phone`, `addresses`, `icons`, `qr`, `wishlist` (добавить, удалить, ids), `subscriptions` | `v1/users/wishlist` (список), `v1/users/addresses/*` (новые адреса), `v1/users/permissions`, `v1/users/geo/confirmation` |
| Лояльность | — | `v1/users/bonuses`, `bonuses/history` (gRPC Mindbox) |
| Каталог, поиск | Карточка `products/v2/{id}`, остатки, образы, недавно просмотренные, подсказки, `catalog/filter`, отзывы о товаре | `v1/pages/home`, `v1/pages/catalog`, `v1/products` (листинг), `advanced-search`, `category`, рекомендации, наличие в магазинах, `for-cart`, `complete-set` |
| Контент | `metadata/*` (FAQ, магазины, сторис, размеры, соцсети, «О компании»), `landings/v2`, `v2/ulink`, `geo/countries/phone-details` | `v1/metadata/splash-screen-image` |
| Гео | — | `v1/geo/countries/*` (gRPC Geo) |
| Корзина и чекаут | **Старый чекаут:** `cart/*`, `cart/delivery2` (+ Boxberry), `cart/delivery`, `PUT orders` | **Новый чекаут:** `v1/cart`, `v2/cart`, `v1/cart/*` (доставка, ПВЗ, интервал, адрес, оплата, получатель, бонусы, промокод, сертификат, позиции), `POST v1/orders`, `v1/delivery/intervals` (gRPC Logistics), `v1/pickup/*` (HTTP Logistics) |
| Заказы | Список, карточка, отмена, офлайн-чеки (gRPC orders), Долями | `v2/payment-types`, `v2/orders/{id}/change-payment-method` |
| Возвраты | `orders/{id}/return`, `orders/v2/return-reasons` | `v1/delivery/{id}/return-method-list`, `return-details` |
| Платежи | — | `v1/payment/yookassa` (+ статус), `v1/payments/{order}/{system}` (+ `/info`) |
| Сертификаты | — | `v1/giftcards/*`, `v1/timezones` |
| Резервирование | — | `v1/reservation/*` |
| Отзывы | `reviews/*` (часть — gRPC feedbacks) | `v1/reviews/offline-product` |
| Уведомления, опросы | `notification/message`, `info`, `user-activities` | `v1/notification/polls` |

Старый и новый чекаут живут одновременно: `CreateOrderManager` и `OrderManager` ходят в `core` (`cart/*`, `PUT orders`), `Managers/Checkout/*` — в `mobile` (`v1/cart/*`, `POST v1/orders`).

---

## 7. Внешние сервисы напрямую из приложения (мимо шлюзов)

| Сервис | Где в коде | Назначение |
|---|---|---|
| Diginetica | `Endpoints/DigineticaEndpoint.swift`, `Managers/Analytics/Diginetica/DigineticaReporterProtocol.swift:70` | События поиска и рекомендаций; без авторизации, ответ не читается |
| Dresscode.ai | `Managers/Dresscode/DresscodeManager.swift:104,129` | Виртуальная примерка: `api.dresscode.ai` + WebView `try-on.dresscode.ai` |
| Mindbox SDK | `AppDelegate+Mindbox.swift` | Push, in-app; UUID устройства → `x-device-id` |
| Платёжные SDK | `Managers/Payment/*` | YooKassa/YooMoney (токенизация), Долями, SberPay, Yandex Pay. Платёж создаётся через шлюз `mobile` |
| Аналитика, крэши | `AppDelegate.swift` | AppsFlyer, AppMetrica + Varioqub (A/B), Firebase, Sentry (`sentry.12stz.dev`), KSCrash, Crashlytics |
| Чат, сторис, карты | `Modules/Flomni/`, `AppDelegate+InAppStory.swift` | Flomni chat, InAppStory, Yandex MapKit |

---

## 8. Быстрые подсказки по поиску

1. **Какой запрос шлёт экран:** `Modules/<Фича>/…VC.swift` → `Business/Managers/…Manager` → `Business/Services/…Service` → `Endpoints/…Endpoint.swift` (`path`, `method`).
2. **Через какой шлюз:** endpoint `: RequestTarget` — `core` (esb-monorepo), `: RequestTargetNew` — `mobile` (mobile-monorepo-go).
3. **Где метод в шлюзе:** `core` — `esb-monorepo/libs/<домен>/controllers/` (`@Controller` + `@Get/@Post`, итог `/api/<префикс>/<метод>`); `mobile` — `mobile-monorepo-go/cmd/mobile_api/mobile_api.go` (`set*Routes`) → `internal/app/service/<домен>.go`.
4. **Во что превращается в монолите:** esb — `path` сервиса (`PHP_BASE_URL + 'mobile/' + path`); Go — `SITE_*_PATH` в `.deploy/helm/values.yaml`; затем `config/url.php` и `src/Modules/Mobile/Rules/UrlRule.php` монолита.
5. **Модель ответа:** `Classes/Models/Response/`; тело запроса — вложенный `Payload` в файле endpoint'а или `Classes/Models/Payload/`.
6. **DI:** `Business/Factories/ManagersAssembly.swift`.
7. **Хост и окружение в тестовой сборке:** `DebugServerHostManager.swift`, экран `Modules/DebugMenu/`.

---

## 9. Неопределённости и вопросы

- [ ] Объявлены, но не вызываются: `CheckAppVersionEndpoint` (`v1/version/check`), `MetadataEndpoint.address`, `MetadataEndpoint.home`.
- [ ] `SplitPaymentManager.swift:43-44` проверяет статус Подели с `paymentId = orderId` — сверить с ожиданием монолита (`M1/PaymentController::actionInfo`).
- [ ] Совпадение JWT-ключей esb и Go подтверждается только тем, что приложение работает; значения в коде и Vault не сверялись.
- [ ] Пути с ведущим `/` (`/profile/wishlist/ids`, `/v1/giftcards`) склеиваются через `appendingPathComponent` — на работу не влияет, но выбивается из стиля.
- [ ] Копия `new/12storeez-ios-develop/` (12.09.2026) устарела: по `AGENTS.md` после появления клона в `12stz` её нужно удалить.

---

# Версии документа

| Версия | Дата изменения | Автор | Описание изменений |
|--------|----------------|-------|--------------------|
| 1.0 | 12.09.2026 | Системный аналитик | Первичное создание на основе копии `12storeez-ios-develop`; расхождение эндпоинта возврата (`POST orders/{id}/return`) с предположением `POST /mobile/orders/return-positions` |
| 1.1 | 12.09.2026 | Системный аналитик | Сверено с `12storeez-master`: `POST orders/{id}/return` → `Mobile\OrdersController::actionReturnPositions()`; `v1/delivery/...` в монолите не найдены |
| 1.2 | 07.10.2026 | Системный аналитик | По сваггеру нового шлюза закрыт вопрос о `v1/delivery/{id}/return-*` |
| 1.3 | 10.10.2026 | Системный аналитик | Код шлюзов найден: `mobile` — `12stz/mobile-monorepo-go`, `core` — `12stz/esb-monorepo` |
| 2.0 | 10.10.2026 | repository-researcher | Карта переписана по клону `12stz/12storeez-ios` (коммит `a6de858b`): структура, сетевой слой и авторизация (§5), раскладка всех вызовов по шлюзам (§6), внешние SDK (§7), подсказки по поиску; §4.3 — сквозная цепочка до контроллера монолита; исправлено: зависимости — SPM, а не CocoaPods. Добавлена схема [../architecture/call-chain.html](../architecture/call-chain.html) (общая для всех репозиториев) |
