# Логистика: запрос дат и интервалов курьера (`WinnerService.Intervals`) и адрес в запросе

**Дата:** 22.10.2026
**Сверено с кодом:** `esb-protobufs` — `f889483`; `12storeez-master-web` — `be3cd759d2`; `mobile-monorepo-go` — `bc39bdb`; `12storeez-ios` — текущая ветка `develop` на 22.10.2026
**БД:** `12stz_staging`, таблица `cms_orders`, заказы с 01.09.2026

Справочник общий для доставки заказа и курьерского возврата: метод один, поток различается кодом типа доставки и параметром адреса (для возврата — адрес отправки, см. §1).

## 1. Контракт

`proto/logistics/winner.proto`, сервис `WinnerService`, метод `rpc Intervals(IntervalsRequest) returns (common.UnifiedResponse)`, HTTP — `POST /api/v1/winner/intervals`.

### Запрос `IntervalsRequest`

| Поле | Тип | Назначение |
|---|---|---|
| `delivery_type_code` | string | Код типа доставки (слаг ТК в 1С), например `cdek-rf-790` |
| `date` | string | Дата и время, от которых считать; пусто — текущие |
| `timezone` | string | Часовой пояс, например `UTC+07:00` |
| `order_type` | enum `OrderType` | `ORDER` = 0, `CNC` = 1, `PREORDER` = 2 |
| `delivery_address` | string | Адрес доставки (для возврата — адрес забора) одной строкой |

Формат строки `delivery_address` в контракте не описан. Структурных полей адреса (город, улица, дом по отдельности) и признака «возврат» в запросе нет.

Для курьерского возврата адрес клиента планируется передавать отдельным параметром — адресом отправки, а не `delivery_address` (`projects/returns-2.0`, `ADR-RET-060`). На коммите `f889483` такого поля в `IntervalsRequest` нет.

Пример:

```json
{
  "delivery_type_code": "cdek-rf-790",
  "timezone": "UTC+07:00",
  "order_type": "ORDER",
  "delivery_address": "Россия, Кемеровская обл, г Новокузнецк, ул Кутузова, д. 5, кв. 100"
}
```

### Ответ

Данные дат — `Intervals.delivery_dates[]` (`WinnerDeliveryDates`: `date`, `title`, `intervals[]`); интервал — `WinnerInterval`: `title`, `time_from`, `time_to`, `code`, `internal_time_from`, `internal_time_to`. Монолит читает даты из `data.delivery_type.delivery_dates` (`modules/common/client/MonolithBfbMsClient.php`, `getDeliveryIntervals`).

## 2. Кто что передаёт сейчас

| Потребитель | Путь | Передаёт | `delivery_address` |
|---|---|---|---|
| Сайт, чекаут | `GET /delivery/delivery/intervals` → монолит → BFB `POST {BFB_MS_HOST}/delivery/intervals` | `delivery_type_code`, `timezone`, `order_type` | нет (`modules/delivery/dto/DeliveryIntervalRequestDto.php`) |
| МП (iOS) | `POST v1/delivery/intervals` → Mobile API Gateway → gRPC логистики | `delivery_type_code`, `date`, `timezone`, `order_type` | нет (`mobile-monorepo-go/internal/app/models/dto/logistics/intervals.go`, `ConvertToPb`; iOS `TimeIntervalsEndpoint.swift`) |
| Админка сайта, «Проверка доставки» | `GET /cms/delivery/check/get-intervals` → монолит → BFB | `delivery_type_code`, `order_type`; `timezone` пустой | нет (`modules/delivery/controllers/CheckBackendController.php`, `actionGetIntervals`) |

Когда запрашиваются интервалы:
- сайт — при выборе способа доставки, если у способа `showIntervals` и есть код типа (`frontend/src/modules/cart/components/Form.vue`, `updateDeliveryIntervals`);
- iOS — так же (`CheckoutManager.swift`, `loadDeliveryIntervals`).

Ручной ввод адреса на запрос не влияет: адрес в запросе не передаётся.

### Доработка для заказов: полный адрес в запросе (ECOMDEV-588)

По переписке System Analyst BTS с командами WEB и MOBILE от 12.03.2026; последнее сообщение о доработках сайта и МП — за 3 дня до 22.10.2026 ([projects/returns-2.0/sources/answers/[2026-03-12] Переписка Васильевой с WEB и MOBILE — интервалы СДЭК для заказов (ECOMDEV-588).md](<../../../projects/returns-2.0/sources/answers/[2026-03-12] Переписка Васильевой с WEB и MOBILE — интервалы СДЭК для заказов (ECOMDEV-588).md>)):

- Цель — даты и интервалы СДЭК для курьерской доставки заказа («Курьер», «Курьер с примеркой») по адресам РФ. Если СДЭК недоступен или интервалы не пришли, клиент оформляет заказ без даты и времени.
- Сайт и МП передают в `delivery_address` полный адрес заказа. Источник — ответ геосервиса после ввода дома: детализация адреса, поле `data.house.fullTitle` (предпочтительно), или подсказка адреса, поле `data.suggest`. С обоими вариантами СДЭК отвечает одинаково; адреса от геосервиса проверены.
- Город (`geo_id`) не подходит: интервалы СДЭК различаются внутри города, а по некоторым городам без улицы и дома СДЭК возвращает ошибку.
- `house_geo_id` вместо строки не выбран: логистике пришлось бы самой ходить в геосервис.
- `delivery_address` обязателен только для типов доставки с интервалами СДЭК. Без адреса логистика для СДЭК возвращает ошибку; остальным типам отдаёт интервалы и без адреса. Адрес можно передавать для любого типа доставки — логистика сама определит источник интервалов.
- Для ПВЗ и самовывоза интервалы не запрашиваются.
- Предложение MOBILE: для курьерских типов с `show_intervals: true` запрашивать интервалы после того, как есть детали адреса доставки.
- Открыто в переписке: адрес, который сайт и МП отправят не из геосервиса (сохранённый адрес и другие сценарии), — System Analyst BTS просила примеры для проверки со СДЭК. Админка «Проверка доставки» тоже должна передавать улицу и дом.
- Задача на доработку сайта и МП — ECOMDEV-588.

## 3. Детализация города и адреса в геосервисе

`proto/geo.proto`, сервис `geo`.

| Метод | Ответ | Что есть для строки адреса |
|---|---|---|
| `CityDetails`, `CityDetailsByGeoID` | `City` | `full_title` (по тестам монолита — вида «Россия, г Москва»), `region` (`fias`, `title`, `title_with_type`), `city` (`fias`, `title`, `type`), `postal_code`, `timezone`, `location` |
| `AddressDetails`, `AddressDetailsByGeoID` | `Address` | `full_title` (по тестам монолита — вида «Россия, г Москва, пр-кт Маршала Жукова, д. 1»), `region`, `city`, `settlement`, `street`, `house`, `postal_code`, `location` |

Имя поля в JSON зависит от канала: сайт вызывает `GET /api/v1/delivery/geo/countries/{countryIso}/addresses/details?geo_id={geo_id}` (`frontend/src/modules/geo/services/GeoService.js`) и получает ответ в camelCase — `data.house.fullTitle` (фронт читает `postalCode`, `street.titleWithType`: `frontend/src/modules/cart/components/Form.vue`); МП вызывает Mobile API Gateway `GET /api/v1/geo/countries/{country_iso_code}/addresses/{geo_id}/details` (`mobile-monorepo-go/cmd/mobile_api/mobile_api.go`, маршрут `GetAddressDetails`) и получает snake_case — `house.full_title` (`mobile-monorepo-go/internal/app/models/dto/geo/address.go`). Это одно и то же поле `HouseDetails.full_title` из proto.

Примеры `full_title` взяты из тестов монолита: `tests/Modules/User/Validator/GeoAddressValidatorTest.php`, `tests/Modules/Mobile/Validator/GeoManualAddressValidatorTest.php`.

## 4. Адрес из заказа без обращения в геосервис

### Поля заказа (`cms_orders`)

| Поле | Содержимое | Заполнено у заказов с улицей (staging, с 01.09.2026, 772 заказа) |
|---|---|---|
| `country` | ISO-код страны (`RU`) | — |
| `state` | Регион | 772 |
| `city` | Населённый пункт, иногда с типом («п. Ленинское») | — |
| `city_fias` | ФИАС населённого пункта | 745 из 799 заказов |
| `street` | Улица с типом («ул Советская», «Ленинградский пр-кт») | 772 |
| `house` | Дом; бывает с префиксом («д 9») или с квартирой внутри («210 кв 85») | 771 |
| `flat` | Квартира | — |
| `postal` | Индекс | 768 |
| `full_address` | Полная строка адреса | 123; почти всегда у заказов в ПВЗ (у курьерских — 1) |

`full_address` записывают: адрес ПВЗ (`src/Modules/Delivery/Helper/PickupHelper.php`) и заказы Lamoda (`LamodaOrderCreateDtoPrepareService.php`). Для курьерского заказа строки обычно нет.

### Готовая сборка в монолите

`Order::getFullAddressCompiled()` (`src/Modules/Order/Traits/OrderGetterTrait.php`) для курьерской доставки собирает строку «индекс, город, улица, д. N, кв. M» из полей `postal`, `city`, `street`, `house`, `flat`. Регион и страну метод не добавляет. Используется в ответе МП о заказе (`OrderMobileTransformer.php`).

### Вывод

- Строку адреса для `delivery_address` можно собрать из полей заказа без вызова геосервиса: страна, регион, населённый пункт, улица, дом, квартира, индекс заполнены почти у всех курьерских заказов.
- Формат будет отличаться от `full_title` геосервиса: тип населённого пункта (`г`) в `city` обычно нет, в `house` встречаются префикс «д» и квартира. Регион из `state` компенсирует отсутствие типа города.
- Вариант с детализацией города: `City.full_title` («Россия, г Москва») плюс улица, дом и квартира из заказа. Детализацию города сайт и МП уже вызывают ради `timezone`.
- Распознает ли СДЭК такую строку, по коду не проверить. Это тот же случай «адрес не из геосервиса», что сохранённый адрес в доработке ECOMDEV-588. Проверка System Analyst BTS для прямого потока по адресам заказов с прода: по 3 адресам РФ из 5 даты пришли ([projects/returns-2.0/sources/answers/[2026-10-20] Переписка Лемешева — Васильева (ручной адрес, адрес для возврата СДЭК).md](<../../../projects/returns-2.0/sources/answers/[2026-10-20] Переписка Лемешева — Васильева (ручной адрес, адрес для возврата СДЭК).md>)).

## 5. Открытые вопросы

1. Как сайт и МП собирают `delivery_address` для адреса не из геосервиса (сохранённый адрес, адрес из заказа, ручной ввод) и проходит ли такая строка у СДЭК стабильно?
2. Для возврата СДЭК принимает код города или адрес. Будет ли в `IntervalsRequest` поле для `city_fias` или код города логистика определит сама?
