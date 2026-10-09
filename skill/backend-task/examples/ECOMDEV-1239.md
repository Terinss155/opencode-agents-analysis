# [B][Web] Форма возврата. Метод для получения способов возврата

> Эталонный пример задачи типа **«новый эндпоинт для сайта»** (`[B][Web]`).
> Источник: Яндекс Трекер, `ECOMDEV-1239` (создано 16.03.2026, разрешено 02.04.2026). Статус: тестирование завершено успешно.
> Парная задача для МП — [ECOMDEV-1240](./ECOMDEV-1240.md), прокси на Gate — [ECOMDEV-1241](./ECOMDEV-1241.md).

**Связи**
- Связана: ECOMDEV-1309 — [QA] Подготовка тестовой документации по форме возврата (web)
- Блокирует: ECOMDEV-1290 — [B][Web][Mobile API] Добавить фильтрацию доступных методов возврата на основе гео-данных

## Цель

Добавить метод `GET /api/orders/{order_id}/return-method-list`, чтобы получать список способов возврата для выбранного заказа.

## Описание реализации

### 1. Характеристики метода

- Архитектура: REST
- Протокол взаимодействия: HTTPS
- Формат выходных данных: JSON

### 2. Входные параметры

Пока не валидируются и не используются, будут добавлены в рамках [ECOMDEV-1290](https://tracker.yandex.ru/ECOMDEV-1290).

| Параметр | Тип данных | Обязательность | Описание |
|---|---|---|---|
| `country_iso` (query) | string | Нет | ISO-код страны |
| `region` (query) | string | Нет | Регион |
| `region_id` (query) | string | Нет | Идентификатор региона в сервисе логистики |
| `city` (query) | string | Нет | Город |
| `city_id` (query) | string | Нет | Идентификатор города в сервисе логистики |
| `city_fias` (query) | string | Нет | Идентификатор города в системе ФИАС |

### 3. Выходные параметры

| Параметр | Тип данных | Описание |
|---|---|---|
| `status` | string | В случае успешного ответа `success`, в случае ошибки `error` |
| `data` | obj | Объект |
| `data.items` | obj[] | Массив объектов |
| `data.items[i]` | obj | Объект с данными способа возврата |
| `data.items[i].method` | string | `courier` / `sdek-pvz` / `5post` |
| `data.items[i].method_type` | string | `courier` / `pvz` |
| `data.items[i].title` | string | Название для вывода текстом |
| `data.items[i].description` | ?string | Описание |
| `data.items[i].active` | bool | Включен ли на сайте |
| `data.items[i].active_mobile` | bool | Включен ли на МП |
| `data.items[i].available_dates_return` | string[] | Массив дат в формате `YYYY-MM-DD` |

Пример успешного ответа (значения `method` / `method_type` приведены к таблице — см. урок 2):

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "method": "courier",
        "method_type": "courier",
        "title": "Курьер",
        "description": "Мы отправим курьера на указанный адрес",
        "active": true,
        "active_mobile": true,
        "available_dates_return": ["2026-10-25", "2026-10-26", "2026-10-27"]
      },
      {
        "method": "sdek-pvz",
        "method_type": "pvz",
        "title": "СДЭК",
        "description": "Вы сами придете",
        "active": true,
        "active_mobile": false,
        "available_dates_return": ["2026-10-25", "2026-10-26", "2026-10-27", "2026-10-28"]
      },
      {
        "method": "5post",
        "method_type": "pvz",
        "title": "5POST",
        "description": "Вы сами придете",
        "active": false,
        "active_mobile": true,
        "available_dates_return": ["2026-10-25", "2026-10-26", "2026-10-27", "2026-10-28"]
      }
    ]
  }
}
```

## Тестирование

**Критерии приёмки**

- Добавлен метод `GET /api/orders/{order_id}/return-method-list`, его ответ соответствует [данным в админке](https://admin.12storeez.com/cms/return/return-details) и учитывает сроки возврата для выбранного заказа.

## Что всплыло на тесте (уроки для постановки)

| # | Что произошло | Чего не хватило в постановке |
|---|---|---|
| 1 | На dev пустой `available_dates_return` для `sdek-pvz` и `5post`. Даты считаются от `cms_orders.end_date`, а оно заполняется только при приёме завершённых статусов из RetailCRM; на dev обмены не настроены → `end_date IS NULL`. На стейджинге всё ок, доработка снята. | Источник расчёта дат (`cms_orders.end_date`) и на каком стенде проверять. |
| 2 | В исходном примере ответа стояли `cdek` / `five_post` / `pickup`, а в таблице — `sdek-pvz` / `5post` / `pvz`. Согласовано по таблице: значения как в чекауте, `pickup` в чекауте = самовывоз из магазина. | Пример ответа обязан совпадать с таблицей выходных параметров; enum сверять с существующими значениями в системе. |
