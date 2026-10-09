# Request/Response — Mobile API

> Основа: регламент wiki `teams/web-development/arxitektura/standarty/request-response/requestresponse-mobile-api`,
> приведённый к фактической практике (код `12storeez-master`, задачи ECOMDEV-1126 / 1240 / 1241, сверено 02.10.2026). Где регламент и практика расходятся — действует практика.
> Колонка «Web» в таблицах — единственное место, где зафиксировано соответствие полей сайта и МП.
> Коды ошибок — [api-errors_memo.md](./api-errors_memo.md). Правила сайта — [request-response_web.md](./request-response_web.md).

## Контракт запроса

1. Правила применимы к общению МП ↔ Mobile API: Gate `/api/v1/...` (новый гейт `mobile.12stz.*`) и монолит `/mobile/...`.
2. Дополняют правила сайта, не противореча им: snake_case, CRUD по возможности.
3. Gate проксирует запрос в монолит без изменения параметров, тела и конверта ответа.

## Структура

### Заголовок запроса

Регламентом для Mobile API не определены. Ниже — заголовки из фактических запросов МП (ECOMDEV-1240 / 1241);
в задаче описываются только заголовки, специфичные для метода.

| Ключ | Описание |
|:---|:---|
| `Authorization` | `Bearer <JWT>` — запрос к Gate |
| `x-session-token`, `x-access-token` | Токены сессии — прямой запрос в монолит `/mobile/...` |
| `x-platform` | Платформа: `ios` / `android` |
| `x-version` | Версия приложения |
| `accept-language` | Язык |

#### Пример заголовка запроса

```json
{
  "Authorization": "Bearer <token>",
  "x-platform": "ios",
  "x-version": "1.73.0",
  "accept-language": "ru-RU;q=1.0",
  "content-type": "application/json"
}
```

### Параметры запроса

#### Общие соглашения

- snake_case, только плоская запись — как на сайте.
- Регламент описывает `limit` / `offset` / `*` как `pagination.limit` / `pagination.offset` / `filters.*` — это смысловое соответствие, в коде они читаются как отдельные параметры.

| Ключ | Web | Описание | Ограничения (`Mobile\Controllers\BaseController`) |
|---|---|---|---|
| `limit` | `limit` | Размер страницы | По умолчанию `50`, максимум `1000` |
| `offset` | `offset` | Смещение | Максимум `100000` |
| `*` | `*` | Фильтры | — |

### Тело запроса

#### Общие соглашения

- JSON, snake_case; поля совпадают с полями того же метода сайта.

#### Пример запроса

```
GET /api/v1/delivery/{order_id}/return-method-list?country_iso=RU&city=Москва&limit=20&offset=0
```

```json
POST /api/v1/delivery/{order_id}/return-details

{
  "method_return": "sdek-pvz",
  "city_return": "Москва",
  "date_return": "2026-10-05"
}
```

### Заголовок ответа

Специфичные заголовки ответа для Mobile API регламентом не определены; в задаче описываются, только если метод их возвращает.

#### Пример заголовка ответа

```json
{
  "content-type": "application/json"
}
```

### Параметры ответа

#### Общие соглашения

- snake_case.
- `success` — `true` или `false`.

| Ключ | Web | Описание |
|:---|:---|:---|
| `success` | `status == "success"` | Статус ответа (`true`/`false`) |
| `result` | `data` | Объект ответа, `null` или — на практике (1240) — массив элементов списка |
| `result.message` | `message` | Сообщение ответа, если `result` — объект |
| `result.items` | `data.items` | Пагинируемый список, если `result` — объект |
| `total` | `pagination.total` | Количество элементов; на практике (1240) приходит и без пагинации |

### Тело ответа

#### Общие соглашения

- JSON, поля — по таблице «Параметры ответа».
- Конверт одинаков для Gate и монолита — Gate его не меняет.

#### Пример успешного ответа

```json
{
  "result": [
    {
      "available_dates_return": [
        "2026-10-05",
        "2026-10-06"
      ],
      "method": "courier",
      "method_type": "courier",
      "title": "Курьер"
    }
  ],
  "success": true,
  "total": 1
}
```
```json
{
  "result": {
    "items": [
      {
        "subtitle": "subtitle",
        "title": "title"
      }
    ],
    "message": "Успех"
  },
  "success": true,
  "total": 100
}
```

### Ответ с ошибкой

| Ключ | Web | Описание |
|:---|:---|:---|
| `success` | `status == "success"` | Статус ответа (`true`/`false`) |
| `result` | — | Объект ошибки |
| `result.error_code` | `code` | Код верхнего уровня — int из `Mobile\Controllers\BaseController` (`1015`, `1002`, …) |
| `result.error_text` | `message` | Сообщение ошибки; МП может строить текст для пользователя из него — согласовать в задаче |
| `result.error_data` | `errors` | Массив ошибок, с согласованной структурой `Error[]` — только для детальной структуры (формы ввода) |
| `result.data` | — | Ассоциативный массив «String → String» с доп. данными |

#### Error

| Ключ | Web | Описание |
|:---|:---|:---|
| `target` | `target` | Имя поля, к которому относится ошибка; общая ошибка — `""` |
| `code` | `code` | Предметный код из `ResponseErrorCode` — строка (`"20110"`) |
| `message` | `message` | Сообщение ошибки |

#### Пример ответа с ошибкой

Детальная структура — форма ввода (`POST /api/v1/delivery/{order_id}/return-details`):

```json
{
  "success": false,
  "result": {
    "error_code": 1015,
    "error_text": "Некорректный запрос",
    "error_data": [
      {
        "target": "date_return",
        "code": "20110",
        "message": "Некорректная дата возврата"
      }
    ]
  }
}
```

Плоская структура — ввода нет, клиенту нужен только факт ошибки (условный пример: запрос без валидной сессии; `error_data` не передаётся):

```json
{
  "success": false,
  "result": {
    "error_code": 1002,
    "error_text": "<сообщение ошибки>"
  }
}
```
