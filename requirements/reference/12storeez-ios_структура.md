# Структура репозитория 12storeez-ios-develop

**Назначение документа:** карта-справочник по кодовой базе iOS-приложения 12Storeez (`12storeez-ios-develop`) для быстрого поиска информации при анализе требований и разработке.

**Дата актуализации:** 2026-09-12
**Примечание:** папка с исходным кодом (`12storeez-ios-develop/`) — сторонний/внешний код, добавлена в `.gitignore` и не должна попадать в этот git-репозиторий (по аналогии с `12storeez-master/`). Структура описана по фактическому содержимому папок.

---

## 1. Общая архитектура

- **Тип:** нативное iOS-приложение (Swift), единый Xcode-проект/workspace `TwelveStoreez.xcodeproj` / `TwelveStoreez.xcworkspace`. Локальных SPM-модулей нет (`Package.swift` в репозитории отсутствует), `Frameworks/` содержит только сторонние бинарные фреймворки (Crashlytics, TMX Profiling).
- **Управление зависимостями:** CocoaPods (`Podfile`, `Podfile.lock`), + Mint/Brewfile/fastlane для тулинга.
- **Паттерн:** Storyboard-driven **MVC** со слоем Manager/Service и лёгким DI-контейнером (**Dip**). Это **не** MVVM/VIPER/Clean Swift/TCA — классов `ViewModel`/`Interactor`/`Presenter` (в бизнес-смысле) в кодовой базе нет; навигационного Coordinator-паттерна тоже нет (переходы — через `UIStoryboardSegue`).
- **Всего файлов `.swift`:** 1071 (включая сгенерированный код, тесты и таргет `NotificationService`).
- **Два поколения бэкенд-API:** легаси `baseURL` (протокол `RequestTarget`) и новый `baseURLNew` (протокол `RequestTargetNew`) — читаются из `Info.plist` (SwiftGen), с переключателем хоста через `UserDefaults` в non-release сборках. Есть также отдельный `digineticaURL` (аналитика/рекомендации, `RequestTargetDiginetica`).

---

## 2. Корневые папки

| Папка | Назначение |
|---|---|
| `TwelveStoreez/Classes/` | Весь исходный код приложения (см. §3) |
| `TwelveStoreez/Resources/` | Storyboard'ы, ассеты, локализация (`L10n`), plist-файлы |
| `TwelveStoreezTests/` | Юнит-тесты |
| `NotificationService/` | Отдельный таргет — Notification Service Extension (rich push), к заказам/возвратам не относится |
| `Patch/` | `xcode_16_patch.diff` — патч тулинга сборки, не бизнес-логика |
| `Frameworks/` | Crashlytics + TMX Profiling (антифрод/фингерпринтинг устройства) — бинарные фреймворки |
| `NotificationEntity+CoreDataClass.swift`, `+CoreDataProperties.swift` (корень) | CoreData-модель истории push-уведомлений (`UserNotificationsManager`, `Modules/NotificationsHistory/`). **К заказам/возвратам не относится** — единственная CoreData-модель в проекте, заказы и возвраты хранятся только в памяти (см. §4.5) |
| `ci_scripts/`, `fastlane/`, `hooks/` | CI/сборка |
| `.bartycrouch.toml`, `.swiftformat`, `.swiftlint.yml` | Конфигурация линтеров/локализации |

---

## 3. `TwelveStoreez/Classes/` — по слоям

| Папка | Назначение |
|---|---|
| `Modules/<Feature>/` | ~80 папок — по одной на экран/фичу (`ReturnOrder/`, `MyOrders/`, `MyOrderDetail/`, `Checkout/`, `Cart/`, ...). Внутри — `XxxVC.swift` (UIViewController), ячейки, вспомогательные extension-файлы |
| `Business/Network/` | Ядро сетевого слоя: `RequestDescription.swift`, `RequestTarget.swift`/`RequestTargetNew.swift`, `RequestProvider.swift` (на базе **Alamofire**), `RequestProviderProtocol.swift`, `Models/SuccessDataResult.swift` (конверты ответа), `Errors/` (`ServerError`, `MessageError`, `RequestProviderError`) |
| `Business/Network/Endpoints/` | Один файл — один эндпоинт/группа эндпоинтов: `enum ... : RequestTarget` (легаси API) или `struct ... : RequestTargetNew` (новое API). Профильные для заказов/возврата: `OrdersEndpoint.swift`, `ReturnOrderEndpoint.swift`, `ReturnOrderDetailsEndpoint.swift`, `ReturnOrderMethodsEndpoint.swift`, `CreateOrderEndpoint.swift`, `ChangePaymentTypeEndpoint.swift`, `PaymentTypesEndpoint.swift` |
| `Business/Managers/` | По-фиче классы `XxxManager` (держат состояние, оркестрируют вызовы Service) — ближайший аналог ViewModel. Для возврата: `Managers/ReturnOrder/ReturnOrderManager.swift`, `ReturnOrderData.swift`, `ReturnAddressData.swift` |
| `Business/Services/` | Тонкие обёртки над `RequestProvider`, маппят `RequestTarget` → типизированный ответ (аналог Repository/DataSource). Для возврата: `Services/ReturnOrderService.swift` |
| `Business/Factories/` | DI-контейнер (библиотека **Dip**): `ManagersAssembly.swift`, `VCAssembly.swift` — регистрация Manager/Service/VC |
| `Business/Constants/`, `Business/Helpers/` | Константы, хелперы |
| `Models/` | Общие Codable-модели |
| `Models/Response/` | Модели ответов сервера: `Order.swift` (`OrderItem`), `OrderDetail.swift` (в т.ч. `Return.isBankDataRequired`), `ReturnOrderMethod.swift`, `ReturnOrderReasons.swift`, `CreateOrderResponse.swift`, `ConfirmedGeo.swift` и др. |
| `UIKit/` | Переиспользуемые UI-компоненты (кнопки, ячейки, текстовые поля) |
| `Generated/` | Код SwiftGen: `Plist.swift` (типизированный доступ к `Info.plist`, в т.ч. `baseURL`/`baseURLNew`), `StoryboardScenes.swift`, `StoryboardSegue.swift`, `Strings.swift` (L10n) |

---

## 4. Ключевые точки для поиска: процесс возврата товара (клиент, iOS)

### 4.1. Экраны (`Classes/Modules/ReturnOrder/`), в порядке навигации

| Экран | Файл | Назначение |
|---|---|---|
| Карточка заказа (точка входа) | `MyOrderDetail/MyOrderDetailVC.swift` | `didTapReturnedButton` → segue `returnOrder` в `ReturnOrderItemsVC`; передаёт `activeItemsForReturn`/`inactiveItemsForReturn` (фильтр по серверному `OrderItem.canBeReturned` — **никакой клиентской арифметики «N дней» нет**) |
| Выбор позиций | `ReturnOrderItems/ReturnOrderItemsVC.swift` | Устанавливает `returnOrderManager.orderId` и **`returnOrderManager.needBankData = orderDetail?.return?.isBankDataRequired ?? true`** — клиентское зеркало серверного `is_bank_data_required` |
| Выбор причины (по каждой позиции) | `ReturnOrderReasons/ReturnOrderReasonsVC.swift`, `ReturnOrderSelectReasonGroupVC.swift` | Грузит причины (GET), собирает payload `items: [{barcode, reasonId}]` |
| Способ/город/дата/реквизиты | `ReturnOrderMethod/ReturnOrderMethodVC.swift` (+ extensions `+Section/+Delegates/+Layouts/+UICollectionViewDataSource/+UICollectionViewDelegate`) | Секция `.address` — только если `methodType == .courier`; `.requisites` — только если `needBankData`. `confirmReturn()` → `isFulfilledData()` → `returnOrderDetails` (POST) → `returnOrder` (POST) |
| Предупреждение о дате | `ReturnOrderMethod/ReturnOrderDateWarningVC.swift` | Показывается при отклонении сервером выбранной даты (код ошибки `20110`, `errorTarget == .returnOrderDate` / `date_return`) |
| Банковские реквизиты | `ReturnOrderUserRequisites/ReturnOrderUserRequisitesVC.swift` | Поля: фамилия/имя/отчество, БИК (9 цифр), название банка, ИНН банка (10 цифр), счёт (20 цифр), номер карты (16 цифр, маска `#### #### #### ####`) |
| Финал | `ReturnOrderFinishVC.swift` | Модалка подтверждения (`L10n.RetutnOrderFinish.*` — опечатка `Retutn` так в коде/локализации) |

### 4.2. Manager/Service (аналог ViewModel/Repository)

| Класс | Файл | Роль |
|---|---|---|
| `ReturnOrderManagerProtocol` / `ReturnOrderManager` | `Business/Managers/ReturnOrder/ReturnOrderManager.swift` | Синглтон (регистрация в `ManagersAssembly.swift`). Методы: `returnOrder`, `returnOrderDetails`, `loadReasons`, `loadAvailableMethods`, `updateSelectedItems`, `updateItemsData`, `updateReturnOrderPayload`, `updateReturnItemsPayload`, `updateReturnAddressData`, `updateSelectedMethod`, `getSelectedReason(index:)`, `flush()` |
| `ReturnOrderData` | `Business/Managers/ReturnOrder/ReturnOrderData.swift` | Состояние: `reasons`, `availableDates`, `selectedDate`, `selectedItems`, `itemsData`, `payload`, `returnAddressData`, `methods`, `selectedMethod` |
| `ReturnAddressData` | `Business/Managers/ReturnOrder/ReturnAddressData.swift` | Валидация адреса: `isFulfilledCity`, `isFulfilledHouse`, `isFulfilledIndex` (индекс ≥ 6 цифр для стран НЕ из `["RU","AE","KZ","BY"]`, иначе просто непусто) |
| `ReturnOrderServiceProtocol` / `ReturnOrderService` | `Business/Services/ReturnOrderService.swift` | Тонкий проброс в `requestProvider.make(...)` по каждому из 4 эндпоинтов |

### 4.3. Эндпоинты возврата, подтверждённые из кода (реальные строки путей)

| Назначение | Класс | Метод | Путь (буквально из кода) | API-поколение |
|---|---|---|---|---|
| Отправить возврат | `ReturnOrderEndpoint.returnOrder(orderId:payload:)` | POST | `orders/\(orderId)/return` | легаси (`baseURL`) |
| Причины возврата | `ReturnOrderEndpoint.loadReasons` | GET | `orders/v2/return-reasons` | легаси (`baseURL`) |
| Адрес/дата/способ возврата | `ReturnOrderDetailsEndpoint` | POST | `v1/delivery/\(orderId)/return-details` | новое (`baseURLNew`) |
| Доступные способы возврата по городу | `ReturnOrderMethodsEndpoint` | GET | `v1/delivery/\(orderId)/return-method-list` (query: `country_iso, city, city_id, city_fias, region, region_id`) | новое (`baseURLNew`) |
| Список заказов | `OrdersEndpoint.orders(page:)` | GET | `orders` | легаси |
| Карточка заказа | `OrdersEndpoint.orderDetail(id:)` | GET | `orders/\(id)` | легаси |
| Отмена заказа | `OrdersEndpoint.cancel(id:)` | DELETE | `orders` (тело: `{order_id}`) | легаси |

> **✅ Обновлено 07.10.2026 — сваггер нового шлюза.** Команда МП прислала сваггер Mobile API Gateway (`mobile.12stz.com/api`): [`api/mobile/mobile-gateway_swagger.yaml`](./api/mobile/mobile-gateway_swagger.yaml) (Swagger 2.0, «Mobile API Gateway», v1.0). Он закрывает открытый вопрос ниже о маршрутах `v1/delivery/...`:
> - `GET /api/v1/delivery/{order_id}/return-method-list` — «Proxy to http mobile/orders/{order_id}/return-method-list» → монолит, `Mobile\OrdersController::actionReturnMethodList()`;
> - `POST /api/v1/delivery/{order_id}/return-details` — «Proxy to http mobile/orders/{order_id}/return-details» → монолит, `Mobile\OrdersController::actionReturnDetails()`.
>
> Отдельного сервиса для возврата нет. Новый шлюз только меняет внешнюю форму пути и проксирует запрос в те же обработчики монолита, что описаны в `docs/mobileApi/openapi.yml`. Остальных методов возврата и заказа из таблицы (`orders/{id}/return`, `orders/v2/return-reasons`, `GET orders/{id}`, `GET orders`, `DELETE orders`) в сваггере нового шлюза нет: из заказов там только `POST /api/v1/orders` (создание) и `POST /api/v2/orders/{order_id}/change-payment-method`. Значит, эти методы обслуживает старый шлюз `core.12stz.com/api`. Его сваггер доступен только на сайте и в репозиторий не выгружен, поэтому проксирование старого шлюза по-прежнему подтверждено только по коду монолита.
>
> Дефект сваггера: у `return-method-list` параметры `country_iso` и `region` объявлены как `in: path`, хотя в шаблоне пути их нет. iOS-клиент передаёт их в query.
>
> **✅ Сверено с бэкендом (`12storeez-master`), 12.09.2026.** Реальные хосты подтверждены конфигом сборки iOS (`TwelveStoreez/Resources/Configuration/*.xcconfig`): легаси `BASE_URL` = **`core.12stz.com/api`** (прод) / `core.12stz.dev/api` (dev); новый `BASE_URL_NEW` = **`mobile.12stz.com/api`** (прод) / `mobile.12stz.dev/api` (dev). Ни одна из этих двух строк нигде не встречается в коде монолита `12storeez-master` (маршрутизация доменов — на уровне инфраструктуры/шлюза, вне обоих репозиториев) — поэтому окончательно, к какому бэкенду ведёт каждый домен, можно подтвердить только логами трафика или конфигурацией шлюза, не исходным кодом.
>
> **По путям — подтверждено на уровне кода:**
> - `POST orders/{orderId}/return` (легаси, `core.12stz.com`) — в монолите есть кастомное правило `src/Modules/Mobile/Rules/UrlRule.php:82-85`: regex `/orders\/\d+\/return/` (без `-details`/`-method-list`) → маршрут `mobile/orders/return-positions` (id — из пути) → `src/Modules/Mobile/Controllers/OrdersController.php::actionReturnPositions()`. По аналогии с уже подтверждённым проксированием `GET /api/orders/{id}` → `GET /mobile/orders/{id}` (см. `reference/api/mobile/order-view_mobile.md`) это, по всей видимости, **тот же самый эндпоинт**, что и `POST /mobile/orders/return-positions?id=`, ранее описанный в `as-is/mobile/07-create-return.md` — просто другая внешняя форма пути. Путь `/mobile/orders/return-positions` в коде iOS-клиента буквально не встречается, но это ожидаемо: клиент обращается по внешнему REST-пути, а не по внутреннему маршруту Yii2.
> - **`v1/delivery/{orderId}/return-method-list` и `v1/delivery/{orderId}/return-details`** (новое API, `mobile.12stz.com`) — **в монолите `12storeez-master` нет ни одного маршрута с такой формой пути.** Модуль `deliveryV2` (`config/modules.php`, класс `Application\Modules\Delivery\Module`), на который заведены все `api/v1/delivery/...`-маршруты (`config/url.php:206-219`, гео/ПВЗ), разрешает только контроллеры `geo`, `pickup`, `webhooks` — **контроллера заказов/возврата там нет**. Второй модуль с тем же классом, id `return` (`config/modules.php:262-267`), содержит только `ReturnDetailsBackendController` — это **админка** конфигурации способов возврата (`return_details_config`, `return_method`), без единого публичного API-действия для мобильного клиента. Официальная спека Mobile API (`docs/mobileApi/openapi.yml`) тоже описывает эти два метода **по старому пути** — `/orders/{orderId}/return-method-list` и `/orders/{orderId}/return-details` (со словом «orders», как в легаси-модуле), а не `/v1/delivery/...`.
>   **Вывод:** запросы `return-method-list`/`return-details`, которые реально отправляет iOS-приложение, не совпадают ни с одним маршрутом в этом репозитории и не описаны в официальной openapi-спеке Mobile API. Либо это отдельный сервис (см. `mobile-core-api-research.md` в корне — там задокументирован факт существования внешнего Core-микросервиса `core.12stz.dev`, код которого не входит ни в один из имеющихся репозиториев), либо openapi-спека устарела относительно реальной версии бэкенда. Требует подтверждения через трафик/логи или у бэкенд-команды — из исходного кода это не разрешить.

### 4.4. Модели данных (Codable), ключевые поля

- **`ReturnOrderEndpoint.Payload`** (тело `POST orders/{id}/return`): `surname`, `name`, `patronymic`, `bankBic`, `bankName`, `bankInn`, `userAccount`, `userCardNumber`, `items: [{barcode, reasonId: [String]}]`. Вычисляемое `isFulledBankData`: БИК=9 цифр, ИНН=10 цифр, карта=16 цифр, ФИО/банк/счёт непусты.
- **`ReturnOrderDetailsEndpoint.Payload`** (тело `POST v1/delivery/{id}/return-details`): `methodReturn`, `addressReturn`, `cityReturn`, `dateReturn`, `indexReturn`.
- **`ReturnOrderMethodsEndpoint.Payload`** (query `GET v1/delivery/{id}/return-method-list`): `countryIso`, `city`, `cityId`, `cityFias`, `region`, `regionId` (строится из `ConfirmedGeo`).
- **`ReturnOrderMethod`** (ответ): `method`, `methodType` (`"pvz"`/`"courier"`), `title`, `description`, `activeMobile`, `availableDatesReturn`. Клиент **сам фильтрует**: `methods.filter { $0.availableDatesReturn.isNotEmpty && $0.activeMobile }`.
- **`ReturnOrderReasons`**: `items: [{title, items: [{title, code, description}]}]` (группы причин).
- **`OrderDetail.Return`**: `isBankDataRequired: Bool` — решение принимается **сервером**, клиент только читает.
- **`OrderItem.canBeReturned: Bool?`** — тоже серверный флаг, без клиентской даты-арифметики.

### 4.5. Клиентская валидация / бизнес-логика

- Реквизиты обязательны только если `needBankData == true` (= `OrderDetail.return.isBankDataRequired`); адрес обязателен только если `selectedMethod.methodType == .courier` (`ReturnOrderMethodVC.isFulfilledData()`).
- Никакой клиентской логики «вернуть можно в течение N дней» нет — `canBeReturned` и `isBankDataRequired` берутся из ответа сервера как есть. Единственная дата-арифметика в этой области экрана (`MyOrderDetailVC.calculateRemainingMinutes(from:)`) — обратный отсчёт до отмены **неоплаченного** заказа, к возврату отношения не имеет.
- Обработка отказа сервера по дате возврата: код ошибки `20110` (`errorTarget == .returnOrderDate`, бэкенд-поле `date_return`) → клиент перезагружает доступные способы/даты и показывает `ReturnOrderDateWarningVC` вместо обычной ошибки.
- Состояние возврата (`ReturnOrderManager`/`ReturnOrderData`) хранится **только в памяти** на время прохождения флоу и сбрасывается (`flush()`) при `deinit` `ReturnOrderItemsVC` — постоянного локального хранилища (CoreData/UserDefaults) для заказов/возврата нет.

---

## 5. Быстрые подсказки по поиску

1. **Экраны возврата:** `Classes/Modules/ReturnOrder/`.
2. **Состояние возврата:** `Classes/Business/Managers/ReturnOrder/`.
3. **Эндпоинты возврата:** `Classes/Business/Network/Endpoints/ReturnOrderEndpoint.swift`, `ReturnOrderDetailsEndpoint.swift`, `ReturnOrderMethodsEndpoint.swift`.
4. **Модели заказа/возврата:** `Classes/Models/Response/Order.swift`, `OrderDetail.swift`, `ReturnOrderMethod.swift`, `ReturnOrderReasons.swift`.
5. **DI-регистрация:** `Classes/Business/Factories/ManagersAssembly.swift` (искать `ReturnOrder`).
6. **Коды ошибок возврата:** `Classes/Business/Network/Errors/MessageError.swift` (`ErrorTarget.returnOrderDate` → `date_return`).

---

# Версии документа

| Версия | Дата изменения | Автор | Описание изменений |
|--------|----------------|-------|--------------------|
| 1.0 | 12.09.2026 | Системный аналитик | Первичное создание документа на основе анализа реального iOS-клиента (`12storeez-ios-develop`); зафиксировано расхождение реального эндпоинта возврата (`POST orders/{id}/return`) с ранее задокументированным предположением (`POST /mobile/orders/return-positions`) |
| 1.1 | 12.09.2026 | Системный аналитик | Сверено с кодом бэкенда (`12storeez-master`): подтверждено, что `POST orders/{id}/return` маршрутизируется в `Mobile\OrdersController::actionReturnPositions()` (через `Mobile\Rules\UrlRule.php`); подтверждено, что `v1/delivery/{id}/return-method-list` и `v1/delivery/{id}/return-details` — пути, которых **нет** ни в одном маршруте монолита (модуль `deliveryV2` не имеет контроллера заказов/возврата) и нет в официальной openapi-спеке Mobile API |
| 1.2 | 07.10.2026 | Системный аналитик | §4.3: по сваггеру нового шлюза (`api/mobile/mobile-gateway_swagger.yaml`) закрыт вопрос о маршрутах `v1/delivery/{id}/return-method-list` и `return-details` — шлюз проксирует их в `mobile/orders/{id}/...` монолита; зафиксировано, что остальные методы возврата и заказа идут через старый шлюз `core` |
