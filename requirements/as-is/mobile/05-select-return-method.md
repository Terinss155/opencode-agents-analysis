# Шаг 05 (mobile). Выбор способа возврата

**Канал:** Мобильное приложение · **Эндпоинт:** `GET /mobile/orders/{order_id}/return-method-list`
**Статус:** DRAFT · **Дата:** 07.09.2026
**Результат шага:** в приложении выбран способ возврата и связанный с ним список доступных дат. В базе ничего не меняется.

> **⚠️ Обновлено 12.09.2026, сверено с бэкендом `12storeez-master`.** Реальный путь, который вызывает приложение: **`GET v1/delivery/{orderId}/return-method-list`** на **новом** хосте (`BASE_URL_NEW` = `mobile.12stz.com/api`, `struct ReturnOrderMethodsEndpoint: RequestTargetNew`, `Classes/Business/Network/Endpoints/ReturnOrderMethodsEndpoint.swift`). Проверка кода монолита показала: **такого маршрута там не существует.** Модуль `deliveryV2` (`config/modules.php`, `Application\Modules\Delivery\Module`), на который заведены все `api/v1/delivery/...`-пути (`config/url.php:206-219`), разрешает только контроллеры `geo`, `pickup`, `webhooks` — контроллера заказов/возврата в нём нет. Официальная спека Mobile API (`docs/mobileApi/openapi.yml:1818`) тоже описывает этот метод **по-старому** — `/orders/{orderId}/return-method-list` (со словом «orders»), что как раз и совпадает с маршрутом ниже (`GET /mobile/orders/{order_id}/return-method-list` → `Mobile\OrdersController::actionReturnMethodList()`, подтверждён кастомным правилом `src/Modules/Mobile/Rules/UrlRule.php:77-80`). **Вывод: путь, который реально вызывает iOS-приложение, не обслуживается монолитом `12storeez-master` и не совпадает с официальной спекой** — либо это отдельный сервис (см. `mobile-core-api-research.md` в корне репозитория — там задокументирован факт существования внешнего Core-микросервиса, код которого не входит ни в этот, ни в мобильный репозиторий), либо спека и маршруты монолита устарели относительно реальной версии бэкенда, к которой ходит приложение. Требует подтверждения у бэкенд-команды / по трафику — из исходного кода однозначно не разрешить. См. также [12storeez-ios_структура.md, §4.3](../../reference/12storeez-ios_структура.md).
>
> **Дополнительно подтверждено кодом клиента:**
> - Query-параметры запроса — `countryIso, city, cityId, cityFias, region, regionId` (снейк-кейс на проводе через `URLEncodedFormEncoder(keyEncoding: .convertToSnakeCase)`) — в клиентской модели есть параметр **`cityFias`**, не упомянутый в разделе 2.3 ниже.
> - Decodable-модель ответа `ReturnOrderMethod` (`Classes/Models/Response/ReturnOrderMethod.swift`) содержит поля `method, methodType, title, description, activeMobile, availableDatesReturn` — **поля `active` в модели нет вообще**, клиент его не читает и не может на него ориентироваться. Это снимает открытый вопрос из раздела 2.7 «приложение должно ориентироваться на `active_mobile` — но это поведение клиента, не проверяемое из репозитория»: **подтверждено** — приложение физически не в состоянии учитывать `active`.
> - Клиентский фильтр перед показом способов (`ReturnOrderManager.loadAvailableMethods`): `methods.filter { $0.availableDatesReturn.isNotEmpty && $0.activeMobile }` — способ с пустым списком дат или выключенный для мобилки не показывается, даже если сервер его вернул.

---

## 1. Пользовательский сценарий

### 1.1 Откуда пользователь приходит

С экрана оформления возврата после выбора города (шаг [04](04-select-city.md)).

### 1.2 Что система отображает

Список способов из ответа: `courier` (Курьер), `sdek-pvz` (СДЭК ПВЗ), `5post` (5Post) — подмножество, доступное для города. По каждому: название, описание, список доступных дат.

### 1.3 Действия пользователя

Выбрать способ. Для способа с непустым списком дат — выбрать дату (шаг [06](06-confirm-return-details.md)).

### 1.4 Ограничения

- Состав списка определяет сервер по городу (по связке таблиц `cms_delivery_city` и `cms_delivery_tk`, типы транспортных компаний `1`, `11`, `15`). Если ничего не найдено — один способ `courier`.
- В ответе поле `active` означает «включён на сайте», поле `active_mobile` — «включён в мобильном приложении». Список доступных дат для способа считается, только если у способа включён **мобильный** флаг; иначе список пустой.

### 1.5 Что происходит после действия

Приложение хранит выбранный способ и его список дат; они уйдут в запрос сохранения реквизитов возврата (шаг 06).

### 1.6 Ошибочные сценарии

- Ошибка разбора параметров → ответ с кодом ошибки «неверный запрос».
- Заказ не найден у пользователя → ответ с кодом ошибки «неверный заказ».

---

## 2. Системная реализация

### 2.0 Диаграмма последовательности

```mermaid
sequenceDiagram
    actor U as Пользователь
    participant M as Мобильное приложение
    participant B as Backend
    participant DB as БД
    participant CFG as cms_return_details_config + Redis

    M->>B: GET /mobile/orders/{order_id}/return-method-list?city&cityId&countryIso&region&regionId
    B->>DB: SELECT cms_orders (order_id, user_id)
    B->>DB: cms_delivery_city ⋈ cms_delivery_tk (type IN 1,11,15)
    Note over B: type 1→courier, 11→5post, 15→sdek-pvz; пусто → [courier]
    B->>DB: SELECT cms_return_method (по alias)
    B->>CFG: параметры дат курьера; B->>DB: cms_orders.end_date (даты ПВЗ)
    Note over B: даты считаются с учётом is_enabled_mobile
    B-->>M: { result: [ {method, method_type, title, description, active, active_mobile, available_dates_return} ] }
    M-->>U: список способов + доступные даты
```

### 2.1 Источники данных

| Что нужно | Где хранится |
|---|---|
| Доступные типы транспортных компаний по городу | связка `cms_delivery_city` и `cms_delivery_tk` (по идентификатору города/региона или по названиям) |
| Справочник способов | `cms_return_method` (`alias`, `title`, `description`, `is_enabled`, `is_enabled_mobile`) |
| Конфигурация дат курьера | `cms_return_details_config` |
| Дата завершения заказа | `cms_orders.end_date` |

### 2.2 Как система собирает данные

Логика **та же, что на сайте** (см. [`web/05`, раздел 2.2](../web/05-select-return-method.md)):

1. Находит заказ по `order_id` и `user_id`.
2. Определяет доступные типы транспортных компаний по городу (типы `1`, `11`, `15` в связке `cms_delivery_city` ⋈ `cms_delivery_tk`).
3. Переводит типы в способы: `1` → `courier`, `11` → `5post`, `15` → `sdek-pvz`. Если ни одного — берётся один `courier`.
4. Достаёт строки этих способов из справочника `cms_return_method`.
5. Считает доступные даты: курьер — по конфигурации возврата; ПВЗ — по окну «`cms_orders.end_date` + 14 дней». Оба расчёта учитывают **мобильный** флаг способа (`is_enabled_mobile`): если он выключен, список дат пустой.
6. Собирает по каждому способу: внутреннее имя, тип (`pvz` / `courier`), название, описание, признак «активен на сайте», признак «активен в МП», список дат.

Карточка: [`api/mobile/delivery/get-return-method-list.md`](../../reference/api/mobile/delivery/get-return-method-list.md).

### 2.3 Обмен по API

**Запрос**

```http
GET /mobile/orders/{order_id}/return-method-list?city=Москва&cityId={cityId}&countryIso=RU&region=...&regionId=...
Authorization: <мобильная сессия>
```

**Ответ**

```json
{
  "success": true,
  "total": 2,
  "result": [
    { "method": "courier", "method_type": "courier", "title": "Курьер", "description": "...",
      "active": true, "active_mobile": true, "available_dates_return": ["2026-09-09", "2026-09-10"] },
    { "method": "5post", "method_type": "pvz", "title": "5Post", "description": "...",
      "active": true, "active_mobile": true, "available_dates_return": ["2026-09-08"] }
  ]
}
```

### 2.4 Что использует приложение

| Поле | Использование |
|---|---|
| `method` | `method_return` в запросе реквизитов возврата |
| `method_type` | `courier` → форма адреса; `pvz` → без адреса |
| `available_dates_return` | список дат для шага 06 |
| `active` / `active_mobile` | фильтрация способов на клиенте — **подтверждено кодом:** по `activeMobile` (+ непустой список дат); поле `active` клиентом не декодируется |

### 2.5 Что передаётся на следующий шаг

Внутреннее имя способа, выбранная дата и город → тело запроса `POST /mobile/orders/{order_id}/return-details`.

### 2.6 Что сохраняется или меняется

Ничего. Способ запишется в `cms_orders.return_delivery_tk` (`13` / `567` / `55`) на шаге 06.

### 2.7 Неуточнённые места

- ~~В ответе поле `active` всегда означает «включён на сайте», не мобильный флаг. Приложение должно ориентироваться на `active_mobile` — но это поведение клиента, не проверяемое из репозитория.~~ **Подтверждено 12.09.2026 кодом iOS-клиента** (см. предупреждение в начале документа): модель ответа на клиенте вообще не содержит поля `active`; используется только `activeMobile`.
- Наполнение `cms_delivery_city` / `cms_delivery_tk` определяет фактический состав способов.
- **Даты курьера и ПВЗ — разная логика (подтверждено разработкой).** Курьер: список из `cms_return_details_config`, 14-дневный срок / `cms_orders.end_date` в списке не проверяются. ПВЗ: окно `cms_orders.end_date + 14 дней`. `available_dates_return` — фактический источник «когда можно вернуть» (отдельного поля «Вернуть до» нет). Объект `expiration_date` из карточки заказа (`created_at` → `delivery_date`) к сроку возврата **не относится**.
- Совместимость: старые версии приложения могут не передавать имя способа — см. [шаг 06](06-confirm-return-details.md).

---

## 3. Отличия от TO-BE

| TO-BE (`UC-RET-04`) | AS-IS (mobile) |
|---|---|
| Каналы по месту покупки, Магазин, Почта России, офис СДЭК | Только `courier`, `sdek-pvz`, `5post`; «место покупки» не учитывается |
| Предвыбор способа по способу доставки заказа | Не реализован на сервере |
| Для ПВЗ — выбор конкретной точки | Точка не выбирается (см. шаг 06) |
| Почта России — Калининград | Канала нет |
