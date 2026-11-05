# ECOMDEV-2559: [B][Mobile-Api] Добавить delivery_address в метод получения интервалов доставки (mobile-api-gate)

Ссылка: https://tracker.yandex.ru/ECOMDEV-2559

## **Цель** {#cel}

Для интервалов доставки СДЭК ( ECOMDEV-588 ) приложение должно передавать полный адрес доставки. Гейт МП проксирует запрос в Логистику по gRPC, но в `IntervalRequest` поля адреса нет. Необходимо принять `delivery_address` и передать его в Логистику.

## Описание реализации

#### Доработать метод получения интервалов

Endpoint `POST /api/v1/delivery/intervals` (mobile-api-gate → gRPC `Logistics.WinnerService.Intervals`)

{% cut "Параметры запроса" %}

#|
||

**Параметр**

|

**Тип**

|

**Обязательность**

|

**Описание**

||
||

`delivery_type_code`

|

string

|

Да

|

Код типа доставки, например `dali-msk-590` (без изменений)

||
||

`timezone`

|

string

|

Нет

|

Таймзона (без изменений)

||
||

`order_type`

|

string

|

Нет

|

`ORDER`, `CNC`, `PREORDER` (без изменений)

||
||

`delivery_address`

|

object

|

Нет

|

**Новый.** Полный адрес доставки клиента: код страны,  регион, город, улица, дом и корпус/строение.

Пример:

```json
"delivery_address": {
  "country_iso": "iso код страны", // по умолчанию сделаем RU
  "region": "название региона", // например "Нижегородская область" или "Нижегородская обл" 
  "city": "название города", // например, "Нижний Новгород"
  "street": "название улицы", // например, "ул Лебяжья"
  "house": "номер дома и если есть корпус/строение" // например, "д. 1" или "д. 1, к 2"
}
```

||
|#

{% endcut %}

{% cut "Пример запроса" %}

```json
{
  "delivery_type_code": "dali-msk-590",
  "timezone": "UTC+07:00",
  "order_type": "ORDER",
  "delivery_address": {
    "country_iso": "RU",
    "region": "республика Татарстан",
    "city": "Казань",
    "street": "ул Переселенческая",
    "house": "д. 5А"
  }
}
```

{% endcut %}

#### Алгоритм

1. В `go.mod` поднять `github.com/12storeez/esb-protobufs` с `v0.8.99` до `v0.9.3` или новее (первый тег, содержащий поле `delivery_address`); проверить сборку и остальные вызовы gRPC на несовместимости
2. В `internal/app/models/dto/logistics/intervals.go` добавить в `IntervalRequest` поле `DeliveryAddress` (`json:"delivery_address"`) и передавать его в `ConvertToPb()`
3. Обновить аннотации `@Param` и `@Router` в `internal/app/service/delivery.go`, перегенерировать swagger (`make build`)
4. Проверить, что адрес клиента не попадает в логи

{% note info "Важно!" %}

Параметр необязательный: для СДЭК без адреса ошибку возвращает Логистика, для остальных типов доставки интервалы отдаются как раньше. Задача не зависит от `monolith-bfb-ms`: гейт ходит в Логистику напрямую.

{% endnote %}

### Полезные материалы

#|
||

**Описание**

|

**Ссылка**

||
||

Родительская задача

|

https://tracker.yandex.ru/ECOMDEV-588

||
||

Анализ интеграции с КС СДЭК

|

https://tracker.yandex.ru/TNT-1888

||
||

Протобаф Логистики (`IntervalsRequest`)

|

https://github.com/12storeez/esb-protobufs/blob/master/proto/logistics/winner.proto

||
|#

## Тестирование

{% cut "Критерии приёмки" %}

1. `POST /api/v1/delivery/intervals` с `delivery_address` передаёт значение в gRPC-запрос `Logistics.Intervals`
2. Запрос без `delivery_address` работает как раньше
3. Swagger гейта описывает новый параметр
4. Сервис собирается на новой версии `esb-protobufs`

{% endcut %}
