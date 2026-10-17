# Структура репозитория esb-protobufs

**Назначение документа:** карта-справочник по `esb-protobufs` — общему хранилищу gRPC-контрактов (`.proto`) 12Storeez и сгенерированных из них клиентов (Go, TypeScript, Angular) и Swagger. Помогает быстро найти, какой сервис что умеет, кто им пользуется и где в контрактах поля возврата.

**Дата актуализации:** 14.10.2026
**Сверено с кодом:** ветка `master`, коммит `f889483e` (`f889483e7ccc3858cb0c9a91d64fa84254616b5d`, 29.06.2026, тег `v0.9.5`, «TNT-2265 (#448)»)
**Код:** `C:\Users\RobotComp.ru\Desktop\12stz\esb-protobufs\` (только чтение)
**Примечание:** в репозитории только контракты — **реализаций сервисов здесь нет**. Где живёт сервер каждого контракта, по этому репозиторию не установить; потребители найдены поиском по соседним репозиториям в `12stz/`. Где вывод сделан по названию — помечено.

---

## 1. Общая архитектура

- **Что это:** библиотека контрактов. Исходники — `proto/**/*.proto` (proto3). Из них генерируются:
  - `go/` — Go-пакеты (`protoc-gen-go`, `protoc-gen-go-grpc`, для части — `grpc-gateway` `*.pb.gw.go` и `go-micro` `*.pb.micro.go`). Импорт: `github.com/12storeez/esb-protobufs/go/<пакет>`;
  - `typescript/index.d.ts` + `index.js` — TS-описания всех namespace (скрипт `app.ts` на `proto-parser`);
  - `angular/` — клиенты `@ngx-grpc` (только 9 старых контрактов, см. §2);
  - `swagger/` — OpenAPI v2 для контрактов с HTTP-аннотациями (`google.api.http`).
- **Как распространяется:**
  - **npm-пакет `esb-protobufs`** (`package.json:2-3`, версия `0.9.5`); в пакет попадают `typescript/`, `proto/`, `angular/` (`package.json:7-11`). Публикация — GitHub Actions при создании релиза (`.github/workflows/npm-publish.yml`). Node-потребители читают `.proto` прямо из `node_modules/esb-protobufs/proto/`.
  - **Go-модуль** `github.com/12storeez/esb-protobufs` по git-тегам `vX.Y.Z`. Файла `go.mod` в репозитории нет (есть только `go.sum`) — Go собирает модуль без него.
- **Хостинг кода:** GitHub `12storeez/esb-protobufs` (`package.json:15-17`) — в отличие от шлюзов, которые собираются в GitLab.
- **История:** первый коммит — 04.02.2020; активная разработка до 06.2026 (последние задачи `TNT-*`). Ветки задач: `ITSOL-*`, `LGS-*` (логистика), `TNT-*`, `NOVADEV-*`, `MOBILE-*`.

---

## 2. Корневые папки и файлы

| Папка / файл | Назначение |
|---|---|
| `proto/` | **Исходные контракты** (см. §3). Подпапки: `logistics/` (25 файлов), `platform/`, `notifications/`, `internal/`, `common/`, `google/` |
| `go/` | Сгенерированный Go-код, по папке на `go_package` (`go/logistics`, `go/order`, `go/orders`, …) |
| `typescript/` | `index.d.ts` (~3 000 строк) и `index.js` — namespace-типы по всем `.proto`; точка входа npm-пакета (`package.json:4-5`) |
| `angular/` | `*.pb.ts`, `*.pbconf.ts`, `*.pbsc.ts` для `feedbacks`, `logistics`, `mercaux`, `meta`, `mindbox`, `orders`, `slack`, `transports` (последнего `.proto` уже нет — артефакт старой версии) |
| `swagger/` | `feedbacks/`, `logistics/` (объединённый `logistics.swagger.json`), `notifications/`, `platform/` |
| `google.golang.org/protobuf/.../emptypb/` | Сгенерированный `google.protobuf.Empty` (из `proto/google/empty.proto`) |
| `protoc-gen.sh` | Скрипт генерации Go внутри Docker-образа: для каждого файла/папки в `proto/` выбирает вариант `protoc` по наличию `annotations.proto` и `google.api.http` |
| `Dockerfile` | Образ `protobuf-generator` (golang 1.18 + `protoc` + плагины + клон `googleapis`), `ENTRYPOINT protoc-gen.sh` |
| `Makefile` | `push` — собрать и залить образ генератора в Yandex Container Registry; `go-unix`/`go-win` — запустить генератор над локальной копией; нужен `login.json` (ключ сервисного аккаунта, в `.gitignore`) |
| `build-go.sh` | Ручная генерация Go для `proto/logistics/` (старый способ; остальные строки закомментированы) |
| `build-ts.sh`, `app.ts` | Генерация `typescript/index.d.ts` |
| `build-angular.sh` | Генерация `angular/` (`@ngx-grpc/protoc-gen-ng`) |
| `login.json.example` | Шаблон ключа сервисного аккаунта Yandex Cloud (пустые значения) |
| `.npmrc` | Токен npm берётся из переменной окружения, значения в файле нет |
| `README.md` | Команды `protoc` для каждого вида генерации, порядок выпуска версии |

---

## 3. Контракты (`proto/`)

Колонка «Потребители в `12stz`» — где контракт реально подключён в коде соседних репозиториев (сверено 14.10.2026). «—» — потребителей в `12stz` нет, сервис используется кем-то вне этих репозиториев.

### 3.1. Заказы, оплата, чеки

| Файл | Пакет / go | Сервисы и методы | Потребители в `12stz` |
|---|---|---|---|
| `orders.proto` | `orders` / `go/orders` | `Offline`: `ByClient`, `GetById`, `GetByGuid` (`:7-13`) — офлайн-чеки магазинов; `Online`: `ByClient` (`:73-75`) | `esb-monorepo` (`libs/orders/grpc`, офлайн-заказы); монолит — PHP-копия `modules/grpc/Orders/` (`OfflineClient`, `OnlineClient`) |
| `order.proto` | `orders` / `go/order` | **Новый сервис заказов** (по названию — Order MS): `OrderService` (списки, по ID, по пользователю, для админки, статистика), `OrderHistoryService`, `PositionHistoryService`, `OutboxService` (просмотр/правка/удаление outbox-сообщений), `OrderPaymentService.UpdatePaymentStatus` (`:751-779`) | — |
| `payments.proto` | `payments` / `go/payments` | `Payments.GetPaymentsByOrderIDForAdmin` | — |
| `receipt.proto` | `app.grpc.receipt` / `go/receipt` | `ReceiptService`: `SellPrepaymentReceipt`, `SellFullpaymentReceipt`, `RefundPrepaymentReceipt`, `RefundFullpaymentReceipt` (`:7-12`) — фискальные чеки продажи и возврата | — по gRPC. Монолит ходит в чековый сервис по **HTTP** (`src/Modules/Receipt/Client/ReceiptClient.php` — `yii\httpclient`) |
| `t-bank-ms.proto` | `app.grpc.tBankMs` | `tBankMs.LoginByCode` | — |
| `common/marketplace-sku.proto` | `app.grpc.marketplace` / `go/common` | `DeliveryService` (`GetSKU`, `UpdateStocks`), `OrderService` (`UpdateOrderStatus`, `UpdateOrderItemStatus`, `UpdateOrderNumber`) — обмен с маркетплейсами | — |
| `gate-shopify.proto` | `gate` / `go/gate/shopify` | `Shopify.Emit` | — |
| `mercaux.proto` | `mercaux` / `go/mercaux` | `StocksService`, `CatalogService`, `StoresService`, `SellersService` (`List`), `OrdersService.New`; HTTP `/api/v1/{stocks,catalog,stores,sellers,order}` | — |

### 3.2. Клиенты, авторизация, лояльность

| Файл | Пакет / go | Сервисы и методы | Потребители в `12stz` |
|---|---|---|---|
| `auth.proto` | `auth` / `go/auth` | `auth`: `LoginPassword`, `LoginSMS`, `Logout`, `Refresh`, `Validate`, `LoginTBankCode`, `GetAuthSettings` | `mobile-monorepo-go` (`pkg/grpc_client/grpc_client.go:140`, `internal/app/usecase/auth.go`) |
| `user.proto` | `user` / `go/user` | `user`: CRUD, `GetBySiteID`, `GetByToken`, `Merge`, `GetUserAddresses`, ограничения (`Restrict`, …); `Employee`: стилисты | — |
| `mindbox.proto` | `mindbox` / `go/mindbox` | `User` (профиль, заказы, OSMI-карта, история бонусов), `Mobile` (устройство, код подтверждения, push-клик), `Order` (создание/обновление заказа, расчёт), `Gift`, `Cart`/`Product` (рекомендации), `Mailing` | `esb-monorepo` (`libs/profile/{bonus,auth}-grpc`, `libs/notification/grpc`); `mobile-monorepo-go` (`grpc_client.go:108,124`); монолит — PHP-копия `modules/grpc/Mindbox/` (`UserClient`, `MobileClient`) |
| `platform/oauth.proto`, `platform/client.proto` | `platform` / `go/platform` | `Oauth` (`Token`, `Authorize`), `Clients` (CRUD); HTTP `/api/oauth/*`, `/api/client*` | — |
| `passwork.proto` | `passwork` / `go/passwork` | `Passwork` CRUD (по названию — интеграция с менеджером паролей) | — |

### 3.3. Логистика (`proto/logistics/`, пакет `logistics`, go `go/logistics`)

Все сервисы, кроме общих типов (`common.proto`), опубликованы ещё и как REST через grpc-gateway с префиксом `/api/v1/...`. Общий Swagger — `swagger/logistics/logistics.swagger.json`.

| Файл | Сервис | Методы / HTTP |
|---|---|---|
| `winner.proto` | `WinnerService` | **Расчёт доступной доставки** («победитель»): `Calculate` (`POST /api/v1/winner/calculate`), `Intervals`, `PickupList`, `PickupDetail`, `AddressDetails` (`:11-43`) |
| `delivery_type.proto`, `delivery_mode.proto`, `delivery_method.proto` | `DeliveryTypeService`, `DeliveryModeService`, `DeliveryMethodService` | Справочники способов доставки: CRUD + `Suggest` |
| `transport_company.proto`, `transport_company_mode.proto` | `TransportCompanyService`, `TransportCompanyModeService` | ТК и режимы ТК; интервалы режима (`/transport-company-mode/{id}/interval`) |
| `zone.proto`, `zone_group.proto`, `zone_to_geo.proto` | `ZoneService`, `ZoneGroupService`, `ZoneToGeoService` | Зоны доставки и привязка к geo_id |
| `zone_group_restriction.proto`, `category_zone_group_restriction.proto`, `category_delivery_type_restrictions.proto`, `global_restrictions.proto` | `*RestrictionService` | Ограничения доставки по зонам, категориям, типам доставки, глобальные |
| `delivery_calendar.proto`, `interval.proto` | `DeliveryCalendarService`, `IntervalService` | Календарь и интервалы доставки |
| `pickup_points.proto` | `PickupPointsLogisticsService` | ПВЗ провайдера: `PickupList`, `PickupUpdate` |
| `store.proto`, `store_delivery_type.proto` | `StoreService`, `StoreDeliveryTypeService` | Магазины и доступные в них типы доставки |
| `payment_method.proto` | `PaymentMethodService` | Способы оплаты в привязке к логистике |
| `message.proto`, `popup.proto` | `MessageService`, `PopupService` | Тексты и попапы для чекаута |
| `country.proto`, `category.proto`, `address_file.proto` | `CountryService`, `CategoryService`, `AddressFileService` | Страны, категории, файлы адресов |
| `common.proto` | — (пакет `common`) | `UnifiedResponse` и общие типы |

Потребители: `mobile-monorepo-go` использует только `WinnerService` (`pkg/grpc_client/grpc_client.go:60`) и типы `logistics` в `internal/app/helpers/logistics_proxy.go`, `internal/app/models/dto/logistics/`.

### 3.4. Каталог, справочники, магазины

| Файл | Пакет / go | Сервисы и методы | Потребители в `12stz` |
|---|---|---|---|
| `nomenclature.proto` | `nomenclature` / `go/nomenclature` | `NomenclatureService`, `PhotoModelService`, `DictionarySizeService`, `MaintenanceService` (уход за изделием), `ProductOrderService`, `ModelTypeService`, `ProductFilterService`, `CategoryService`, `ProductForAdminService` (`:1022-1079`) | — |
| `internal/products.proto` | `products` / `go/products` | `Catalog`: `Get`, `GetByArticle` | — |
| `internal/stocks.proto` | `stocks` / `go/stocks` | `Stocks`: `Upsert`, `Get`, `GetPagination` | — |
| `internal/release_plan.proto` | `release` / `go/release` | `ArticlesRelease` CRUD (план выпуска артикулов) | — |
| `store.proto` | `store` / `go/store` | `StoreService`: `GetList`, `GetByStoreCode` | — |
| `meta.proto` | `meta` / `go/meta` | `Mobile` (`Contacts`, `About`, `Faq`, `Countries`, `SocialNetworks`), `Stores` (`All`, `ByID`, `Cities`) | `esb-monorepo` (`libs/metadata/grpc`, `libs/stores/grpc`); `mobile-monorepo-go` (`grpc_client.go:92`) |
| `geo.proto` | `geo` / `go/geo` | `geo`: подсказки и детали стран, городов, адресов; город по IP; страна по телефону | `esb-monorepo` (`libs/geo/grpc`); `mobile-monorepo-go` (`grpc_client.go:76`) |

### 3.5. Отзывы, поддержка, уведомления, служебное

| Файл | Пакет / go | Сервисы и методы | Потребители в `12stz` |
|---|---|---|---|
| `feedbacks.proto` | `feedbacks` / `go/feedbacks` | `Mobile` (оценки приложения, магазина, заказа, причины, `CanBeSaved`), `Store`, `NPS`, `PortalFeedbackService` (HTTP `/api/v1/portal/feedback*`) | `esb-monorepo` (`libs/reviews/grpc`); монолит — PHP-копия `modules/grpc/Feedbacks/` |
| `usedesk.proto` | `usedesk` / `go/usedesk` | `CSI.Save` (HTTP `POST /`) | `esb-monorepo` (`apps/usedesk-gate`, `libs/usedesk-gate/grpc`) |
| `slack.proto` | `slack` / `go/slack` | `Slack`: сообщения, файлы (stream), ссылки | `esb-monorepo` (`libs/slack/grpc`) |
| `notifications.proto`, `notifications/slack.proto` | `notifications` | `notifications.Send`; `Slack.Send`, `SendFile` (HTTP `/v1/slack/*`) | — |
| `tracker_slack.proto` | `tracker` / `go/tracker` | `TrackerSlack.SendTicket` | — |
| `yandex.proto` | `yandex` / `go/yandex` | `Yandex`: события и комментарии, `CreateTicket` (по названию — Яндекс Трекер, не Яндекс Pay) | — |
| `internal/errors.proto` | `products` (sic) / `go/errors` | `Errors.Create` | `esb-monorepo` (`libs/errors/grpc`, где вызывается — не проверено) |
| `common/{common,request,response}.proto` | `app.grpc.*` / `go/common` | Общие типы запросов/ответов | — |
| `google/empty.proto` | `google.protobuf` | `Empty` | все |

---

## 4. Кто использует контракты и какой версии

| Потребитель | Как подключён | Версия | Какие контракты |
|---|---|---|---|
| `esb-monorepo` (старый шлюз `core`) | npm `esb-protobufs` (`package.json:46`), путь к `.proto` — `GRPC.nameToPath()` (`libs/constants/src/lib/grpc-transport.ts`) | **`0.6.77`** (тег от 27.09.2023) | `orders`, `feedbacks`, `mindbox`, `geo`, `meta`, `slack`, `usedesk`, `internal/errors` |
| `mobile-monorepo-go` (новый шлюз `mobile`) | Go-модуль (`go.mod:8`) | **`v0.8.99`** (16.03.2026) | `auth`, `geo`, `logistics` (`WinnerService`), `meta`, `mindbox` |
| `12storeez-master-web` (монолит) | **Не подключён** как зависимость. Лежит ручная PHP-генерация трёх контрактов: `modules/grpc/{Feedbacks,Mindbox,Orders}/` + `GPBMetadata/` | неизвестна (копия) | `feedbacks`, `mindbox`, `orders` |
| `12storeez-ios` | Не использует (ходит в шлюзы по HTTP) | — | — |

Остальные контракты (`order`, `receipt`, `user`, `nomenclature`, `logistics` кроме `WinnerService`, `mercaux`, `platform`, …) в репозиториях `12stz` не подключены — их серверы и клиенты находятся вне доступного кода.

---

## 5. Как выпускается новая версия контракта

1. Правка `.proto` в `proto/`.
2. Генерация Go: `make go-unix` / `make go-win` — запускает образ `protobuf-generator` из `cr.yandex` над репозиторием (`Makefile`, `protoc-gen.sh`). Правила выбора команды:
   - есть `annotations.proto` → генерация с googleapis;
   - есть `google.api.http` → дополнительно `*.pb.gw.go` (REST-прокси) и, для папок, объединённый Swagger `swagger/<папка>/<папка>.json`.
3. Генерация TS: `sh ./build-ts.sh` (`typescript/index.d.ts`). Angular — `build-angular.sh` (в последних версиях не обновлялся, см. §2).
4. Поднять версию в `package.json` (`README.md`, «Обновление версии»), создать GitHub-релиз → npm-публикация. Go-потребители берут git-тег.

---

## 6. Ключевые точки для поиска по процессам

### 6.1. Возврат товара (Возвраты 2.0)

Отдельного сервиса возвратов в контрактах **нет**: поиск `refund`, `return`, `возврат` по `proto/` даёт совпадения только в двух файлах.

| Что | Где | Комментарий |
|---|---|---|
| Поля возврата в заказе нового сервиса заказов | `order.proto:240-250` (`Order`): `return_delivery_type_id/code/name/mode`, `return_delivery_transport_company_mode_id/code/name`, `return_money`, `return_store_code`, `return_reason`, `return_datetime` | Способ возврата хранится теми же сущностями логистики, что и доставка (тип доставки + режим ТК). Причина — строкой |
| Причина возврата позиции | `order.proto:86` (`Position.return_reason`) | Строка, без справочника |
| Признаки статуса | `order.proto:141-142` (`OrderStatus.is_returned`, `can_be_returned`) | Можно ли вернуть заказ — флаг статуса |
| Возврат ТК в админке | `order.proto:443-447` (`ReturnTK`: `datetime`, `mode_id`, `mode_name`), `:476` | Только для списка заказов админки |
| Чек возврата | `receipt.proto:10-11` (`RefundPrepaymentReceipt`, `RefundFullpaymentReceipt`), `RefundRequest` (`:28-33`), `RefundPayment.returnQuid` (`:79-83`) | Монолит вызывает чековый сервис по HTTP, не через этот контракт |
| Методы `v1/delivery/{orderId}/return-method-list` и `return-details` | **нет в контрактах** | Реализованы в `mobile-monorepo-go` поверх монолита, см. [../mobile-monorepo-go/repo-map.md](../mobile-monorepo-go/repo-map.md) §5 |

### 6.2. Прочее

| Что искать | Где |
|---|---|
| Расчёт доступной доставки для чекаута | `proto/logistics/winner.proto` |
| Справочники доставки и ограничения | `proto/logistics/*` (§3.3), REST — `swagger/logistics/logistics.swagger.json` |
| Статусы заказа и позиций в новом сервисе заказов | `order.proto:53-62` (`PositionStatus`), `:123-157` (`StatusGroup`, `OrderStatus`) |
| Outbox заказов (что и куда отправлено) | `order.proto:308-324` (`Outbox`), `:751-756` (`OutboxService`) |
| История изменений заказа и позиций | `order.proto:108-121`, `:281-294`, `:758-766` |
| Офлайн-чеки клиента | `orders.proto` (`Offline`) |
| Авторизация МП (новый шлюз) | `auth.proto` |
| Бонусы, коды подтверждения, Mindbox | `mindbox.proto` |

---

## 7. Быстрые подсказки по поиску

1. **Какие методы у сервиса:** `rpc ` в нужном `proto/**/*.proto`; блок `service` обычно в начале файла (у `order.proto` и `nomenclature.proto` — в конце).
2. **Есть ли REST-адрес:** `option (google.api.http)` рядом с `rpc`; итоговые пути — в `swagger/<папка>/`.
3. **Какой Go-пакет импортировать:** `option go_package` в `.proto` → `github.com/12storeez/esb-protobufs/<go_package>`.
4. **Кто использует контракт:** в `esb-monorepo` — `GRPC.nameToPath('<файл>.proto')`; в `mobile-monorepo-go` — `esb-protobufs/go/<пакет>`; в монолите — только `modules/grpc/`.
5. **Совпадает ли поле у потребителя:** сравнивай с версией, которую он подключил (§4) — `git show v0.6.77:proto/<файл>` или `v0.8.99`; HEAD может быть новее.

---

## 8. Неопределённости и вопросы

- [ ] Где развёрнуты серверы контрактов (`order`, `receipt`, `user`, `logistics`, `nomenclature`, …) и в каких репозиториях их код — в `12stz` его нет.
- [ ] Используется ли `order.proto` (новый сервис заказов, поля `return_*`) в процессе возврата сейчас и кем — потребителей в `12stz` не найдено.
- [ ] Совпадает ли PHP-копия `modules/grpc/` в монолите с текущими `feedbacks.proto`, `mindbox.proto`, `orders.proto` — не сверялось.
- [ ] `esb-monorepo` сидит на версии `0.6.77` (2023 г.): расхождения с HEAD для его 8 контрактов не проверялись.
- [ ] Каталог `angular/` и `transports` — используется ли где-то, из кода не видно.

---

## История изменений

| Версия | Дата | Автор | Изменения |
|---|---|---|---|
| 1.0 | 14.10.2026 | repository-researcher | Первая версия карты по коммиту `f889483e` (`v0.9.5`): контракты, потребители в `12stz`, поля возврата |
