# Структура репозитория proto-specifications

**Назначение документа:** карта-справочник по `proto-specifications` — GitLab-хранилищу gRPC-контрактов (`.proto`) новых Go-сервисов бэкенда и сгенерированных из них клиентов (Go, PHP). Помогает понять, какой контракт актуален для сервиса и чем он отличается от старого `esb-protobufs`.

**Дата актуализации:** 25.11.2026
**Сверено с кодом:** `master` `25564f9` (25.11.2026, тег `v0.0.93`), 669 коммитов, первый — 31.05.2024.
**Путь к коду:** `C:\Users\RobotComp.ru\Desktop\12stz\proto-specifications\` (только чтение)
**Хостинг:** GitLab `gitlab.12storeez.com/backend/go/proto-specifications` (origin).

---

## 1. Назначение

- Руками правится только `proto/`. `pkg/go/` и `pkg/php/` генерирует GitLab CI (job `build_proto`) и коммитит обратно в ту же ветку двумя коммитами «remove old proto files» / «add proto files» (`README.md`).
- Каждый мерж в `master` получает тег `vX.Y.Z` (job `tag_release`, `patch` +1). Потребители подключаются по тегу.
- Go-модуль: `gitlab.12storeez.com/backend/go/proto-specifications.git`, пакеты `pkg/go/<домен>` (`go.mod`, `option go_package` в каждом `.proto`).
- Генератор — тот же образ `protobuf-generator`, что и у `esb-protobufs` (`Makefile`: `cr.yandex/.../esb-protobufs/protobuf-generator`).

## 2. Папки

| Папка | Что внутри |
|---|---|
| `proto/*.proto` | Контракты по доменам: `auth`, `feedbacks`, `geo`, `mattermost`, `mercaux`, `mindbox`, `notifications`, `orders`, `passwork`, `rcrm`, `slack`, `store`, `user`, `yandex` |
| `proto/logistics/` | Логистика: 23 файла, proto-пакет `logistics` (зоны, способы и типы доставки, интервалы, ПВЗ, `WinnerService`) |
| `proto/common/` | Общие сообщения `common`, `request`, `response` |
| `proto/google/api/` | Аннотации для grpc-gateway |
| `pkg/go/<домен>/` | Сгенерированный Go: `*.pb.go`, `*_grpc.pb.go`, `*.pb.gw.go` |
| `pkg/php/<Домен>/` | Сгенерированные PHP-классы (больше всего — `Logistics`, `Mindbox`) |

## 3. Сервисы (gRPC `service`)

| Файл | Сервисы | На что обратить внимание |
|---|---|---|
| `mindbox.proto` | `User`, `Mobile`, `Order`, `Gift`, `Cart`, `Product`, `Mailing`, `Offline`, `ModernRetail`, `ReviewsAuth` | `Order.UpdateOrderV2` (`:64`) — через него монолит меняет заказ в Mindbox (через BFB); `User.LoyaltyBalance` (`:36`, TNT-2922); `Offline.Return` (`:104`) |
| `orders.proto` | `Offline`, `Online`, `Purchases` | `Offline.ByClientWithReturns` (`:11`); `Purchases.List` (`:142`, TNT-2684) |
| `rcrm.proto` | `Rcrm` | RetailCRM: `SearchOrders`, `GetDictionary`, `SearchCustomers`, `CancelOrder`, `DismantleOrder` (добавлены 23–25.11.2026, TNT-2922) |
| `logistics/winner.proto` | `WinnerService` | `Intervals`, `PickupList`, `PickupDetail`; для возвратов — см. §5 |
| `logistics/*.proto` | ещё 20 сервисов справочников логистики | — |
| `geo.proto` | `geo` | подсказки и детали стран, городов, адресов |
| `user.proto` | `user`, `Employee` | пользователи, ограничения, стилисты |
| `feedbacks.proto` | `Mobile`, `Store`, `NPS`, `PortalFeedbackService` | — |
| `mercaux.proto` | `StocksService`, `CatalogService`, `StoresService`, `SellersService`, `OrdersService`, `CustomersService` | — |
| `auth`, `notifications`, `store`, `mattermost`, `slack`, `passwork`, `yandex` | по одному сервису | `notifications.SendV2` — отправка уведомлений |

## 4. Кто использует (по коду и диаграммам)

| Потребитель | Как подключён | Источник |
|---|---|---|
| `mindbox-srv-go` | Go-модуль, `v0.0.79`, package `mindbox` | `architecture-docs/mindbox-srv-go/system.puml:27` |
| `orders-srv-go` | Go-модуль, `pkg/go/orders` | `architecture-docs/orders-srv-go/system.puml:25` |
| `monolith-bfb-ms` | **другой репозиторий** `backend/php/proto-specifications` (composer `twelve-storeez/proto-specifications` v1.9.27, Docker-образ `proto-specifications-php:v1.9.27`) | `monolith-bfb-ms/composer.json:43,90`, `.deploy/docker/Dockerfile:1-3` |

Среди локальных репозиториев `12stz` модуль `backend/go/proto-specifications` не подключает никто. `mobile-monorepo-go`, `geo-srv-go` и `logistics-monorepo` работают на `esb-protobufs` (`go.mod:8`, `system.puml`).

## 5. Отличия от `esb-protobufs`

`proto-specifications` выросла из копии `esb-protobufs`: те же имена файлов и сервисов, другой `go_package`. Активность разная: с 01.09.2026 в `proto-specifications` 103 коммита, в `esb-protobufs` — 10 (последний 09.11.2026).

| Контракт | `proto-specifications` | `esb-protobufs` (`origin/master` `c60a6bf`) |
|---|---|---|
| `mindbox.proto` | на ~550 строк больше: офлайн-методы, `LoyaltyBalance`, сервисы `Offline`, `ModernRetail`, `ReviewsAuth` | только базовые `User`, `Mobile`, `Order` (`UpdateOrderV2` есть), `Gift`, `Cart`, `Product`, `Mailing` |
| `orders.proto` | есть `Purchases` | нет `Purchases` |
| `logistics/winner.proto` | `IntervalsRequest.delivery_address` и `sending_address` — объект `ClientAddress` (`country_iso`, `region`, `city`, `street`, `house`), `is_return`, у вариантов доставки `is_return_available` (TNT-2888, 10.11.2026) | адреса — строки, `is_return_available` нет |
| `rcrm.proto` | есть | нет |
| `order.proto`, `receipt.proto`, `nomenclature.proto`, `payments.proto`, `t-bank-ms.proto`, `meta.proto` и др. | **нет** | есть |

Вывод: новые сервисы заказов и чеков (`order.proto`, `receipt.proto`) остаются в `esb-protobufs`; Mindbox, логистика (новые поля возврата), RetailCRM — актуальнее в `proto-specifications`. Какой контракт у конкретного сервиса — по его `go.mod`/`composer.json` или по `system.puml`.

## 6. Подсказки по поиску

1. Методы сервиса — `grep -n "rpc " proto/<домен>.proto`.
2. Поля сообщения — `grep -n "message <Имя>" -A 30 proto/<домен>.proto`.
3. Когда поле появилось — `git -C proto-specifications log --format='%h %cs %s' -- proto/<файл>`.
4. Версия у потребителя — тег `vX.Y.Z` в `go.mod` сервиса; соответствие тега коммиту — `git -C proto-specifications for-each-ref refs/tags`.
5. Граф кода (`graphify-out-12stz/proto-specifications/`) строится только по сгенерированным `pkg/` — сами `.proto` читать напрямую.

## 7. Неопределённости

- Связь с `backend/php/proto-specifications` (её использует `monolith-bfb-ms`, теги `v1.9.x`) не установлена: здесь теги `v0.0.x`, а `pkg/php/` тоже есть. Это может быть отдельный PHP-репозиторий тех же контрактов или его предшественник — уточнить у бэкенда.
- Кто реализует сервер `rcrm.Rcrm` — в коде `12stz` и в найденных диаграммах не указано.
- Переходят ли `mobile-monorepo-go` и логистика с `esb-protobufs` на `proto-specifications` — по коду не видно.
