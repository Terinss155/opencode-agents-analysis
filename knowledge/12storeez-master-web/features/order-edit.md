# Анализ: обязательность email, срок возврата по статусу клиента, редактирование заказа

> **Назначение:** сводный анализ кодовой базы `12storeez-master/` по трём вопросам:
> 1. Обязателен ли email при оформлении заказа
> 2. Проверяется ли статус клиента (Friends & Family) для увеличения срока возврата
> 3. Что можно менять в заказе после его оформления
>
> **Дата:** 2026-09-08
> **Источник:** анализ кода монолита (Yii2)

---

## 1. Обязателен ли email при оформлении заказа

### Вывод: **ДА, email обязателен при оформлении заказа**

### Подтверждение в коде

**Файл:** `modules/users/models/User.php`, строка 242

```php
[['email', 'number', 'name'], 'required', 'on' => 'order'],
```

При сценарии `order` (оформление заказа через корзину) обязательными полями являются:
- **email** — почта
- **number** — телефон
- **name** — имя

Сценарий `order` активируется в `src/Modules/Cart/Service/AbstractCartService.php`, строка 607:

```php
$cart->scenario = 'order';
```

### Исключение: покупка в один клик

**Файл:** `modules/users/models/User.php`, строка 243

```php
[['number'], 'required', 'on' => 'order_one_click'],
```

При сценарии `order_one_click` (покупка в один клик) обязательным является **только телефон** (`number`), email — **не обязателен**.

---

## 2. Проверяется ли статус клиента (Friends & Family) для увеличения срока возврата

### Вывод: **НЕТ, в текущем коде статус клиента НЕ проверяется**

Срок возврата **одинаков для всех клиентов** и определяется глобальным параметром `days_can_be_returned` из таблицы `parameters`.

### Как работает логика возврата сейчас

**Файл:** `src/Modules/Order/Helpers/OrderHelper.php`, строки 587-610

```php
public function canBeReturned(Order $order): bool
{
    $days = Parameter::valueOf('days_can_be_returned');  // Глобальный параметр из БД
    $isCompleted = $this->isCompleted($order);
    $isReturned = $this->isReturned($order);
    $orderCan = ($isCompleted || $isReturned) && strtotime(
            $order->end_date . "+ $days day"
        ) > time();
    // ...
}
```

Аналогичная логика (deprecated, но используется):
- `modules/orders/models/Order.php`, строки 1367-1380 — `Order::canBeReturned()`
- `modules/orders/models/OrderPosition.php`, строки 647-657 — `OrderPosition::canBeReturned()`

### Что есть в коде о статусах клиентов

| Поле/модель | Что хранит | Используется ли в возврате? |
|-------------|------------|----------------------------|
| `User.vip` (строка 1340) | Флаг VIP из CRM | ❌ Нет |
| `UserSegment` | Только блокировка наложенного платежа (`cash_pay_block_user_id`) | ❌ Нет |
| `Parameters.days_can_be_returned` | Глобальное значение (14 дней) | ✅ Да, но для всех одинаково |

### Подтверждение от разработчика (2026-09-08)

Переписка в чате подтверждает отсутствие разделения сроков возврата:

> **Екатерина Лемешева:** «Оля, мы сейчас как-нибудь разделяем сроки возврата для обычных клиентов и F&F. Для F&F должно даваться 30 дней, но мне пишет, что такого нет»
>
> **Ольга Свистунова (разработчик):** «Привет, я про отдельные правила для ff первый раз слышу :) так что нет, точно нету»

**Вывод:** разработчик подтверждает — отдельных правил срока возврата для Friends & Family **не существует**.

### Вывод для бизнеса

Если бизнес-требование — клиенты Friends & Family имеют увеличенный срок возврата (30 дней вместо 14), то **это требование НЕ реализовано в коде** (подтверждено разработчиком). Для реализации необходимо:

1. Добавить логику определения статуса клиента (Friends & Family)
2. Изменить метод `canBeReturned()` для учёта этого статуса
3. Либо создать отдельный параметр `days_can_be_returned_ff`, либо передавать срок в зависимости от статуса клиента

---

## 3. Что можно менять в заказе после его оформления

### Вывод: **В CMS-админке заказ можно менять практически без ограничений по статусу; клиент после оформления заказ изменить не может**

### 3.1. Кто и где может менять заказ

**CMS-админка (backend)** — `modules/orders/controllers/OrdersBackendController.php`, `actionUpdate()` (строка 159):
- Может редактировать заказ **в любом статусе** (нет проверки `isCompleted`/`isReturned` перед сохранением)
- Единственное ветвление: если статус меняется на `STATUS_ORDER_CANCELLED` → вызывается `cancelOrder()` (строки 219-224)

**Клиент (сайт/мобилка)** — после оформления заказ **не редактируется** клиентом. Клиент может только:
- Отменить заказ (если `canBeCancelled()`)
- Оформить возврат (если `canBeReturned()`)

### 3.2. Что именно можно менять в CMS

**Поля самого заказа** (форма `modules/orders/views/orders-backend/_form.php`):

| Поле | Редактируемо? |
|------|--------------|
| `status` | ✅ Да (выпадающий список) |
| `user_id` (клиент) | ✅ Да |
| `delivery_method`, `delivery_slug` | ✅ Да |
| `name`, `surname`, `email`, `number` | ✅ Да |
| Адрес (postal, country, city, street, house, flat и т.д.) | ✅ Да |
| `delivery_time_from/to`, `delivery_interval_code` | ✅ Да |
| `comment` | ✅ Да |
| `payment_method`, `payment_status` | ✅ Да |
| `discount_sum`, `discount_percent` | ✅ Да |
| `surcharge_sum` (доплата) | ✅ Да |
| `org`, `for_blogger`, `created_at`, `storage_expired_at` | ✅ Да |
| `is_dismantle`, `is_unf` | ✅ Да |
| `lamoda_id`, `dolyame_id`, `receipt_guid` | ❌ **readonly/disabled** |
| `retail_id` | ❌ disabled (если уже задан) |
| `email` (в блоке доплаты, строка 884) | ❌ disabled (но в блоке заказчика, строка 739 — редактируемо) |

**Позиции заказа** (`modules/orders/views/orders-backend/_order_position.php`):

| Поле | Редактируемо? |
|------|--------------|
| `item_id` (товар) | ✅ Да |
| Размер | ✅ Да |
| `stock_confirmed` | ✅ Да |
| `stock_cancel_status` | ✅ Да |
| `status` позиции | ✅ Да |
| `stock_id` | ❌ disabled (автоматически) |
| `price` | ✅ Да |
| `discount_sum`, `discount_percent` | ✅ Да |
| `quantity` | ✅ Да |
| `sum` | ✅ Да |
| Добавление/удаление позиций | ✅ Да (dynamicform) |

### 3.3. Важные нюансы при сохранении

1. **`Order::beforeSave()`** (строка 939) — при каждом сохранении:
   - Обновляется `updated_at`
   - Инкрементируется `version` (если изменились атрибуты)
   - Если статус → `CANCELLED` — удаляются позиции из буфера

2. **`updateCustomer()`** (строка 243) — синхронизация данных клиента

3. **`fromSite()`** (строка 244) — обработка данных

4. **`Order::afterSave()`** (строка 1453) — отправка в CRM/1С и т.д.

5. **История изменений** — ведётся через `adminHistoryService` (строки 165, 209, 248, 269, 282)

### 3.4. Safe-атрибуты модели Order

**Файл:** `modules/orders/models/Order.php`, `rules()` (строки 723-892)

Массовое присваивание разрешено для полей из блока `'safe'` (строки 831-879):
`created_at`, `end_date`, `name`, `surname`, `email`, `number`, `comment`, `flat`, `floor`, `porch`, `housing`, `house`, `street`, `city`, `state`, `country`, `postal`, `city_fias`, `full_address`, `delivery_time`, `delivery_time_from`, `delivery_time_to`, `delivery_interval_code`, `delivery_internal_time_from`, `delivery_internal_time_to`, `delivery_date`, `surcharge_sum`, `payment_id`, `order_method`, `pvz_id`, `track_number`, `status_comment`, `return_store`, `source`, `spend_bonus`, `seller_id`, `store_code`, `pvz_provider`, `pvz_provider_id`, `updated_at`, `processing_reason`, `storage_expired_at`, `shipment_date`

---

## 4. Сводная таблица выводов

| Вопрос | Ответ | Где в коде |
|--------|-------|------------|
| Email обязателен при заказе? | ✅ Да (сценарий `order`); ❌ Нет (сценарий `order_one_click`) | `User.php:242-243` |
| Статус Friends & Family влияет на срок возврата? | ❌ Нет, срок одинаков для всех (подтверждено разработчиком) | `OrderHelper.php:587-610` |
| Можно ли менять заказ после оформления? | ✅ Да, в CMS-админке (любой статус); ❌ Нет, для клиента | `OrdersBackendController.php:159` |

---

## 5. Связанные файлы

| Файл | Назначение |
|------|------------|
| `modules/users/models/User.php` | Валидация пользователя (email required) |
| `src/Modules/Cart/Service/AbstractCartService.php` | Установка сценария `order` |
| `src/Modules/Order/Helpers/OrderHelper.php` | Логика `canBeReturned()` |
| `modules/orders/models/Order.php` | Модель заказа, `rules()`, `beforeSave()`, `canBeReturned()` |
| `modules/orders/models/OrderPosition.php` | Модель позиции, `canBeReturned()` |
| `modules/orders/controllers/OrdersBackendController.php` | Редактирование заказа в CMS |
| `modules/orders/views/orders-backend/_form.php` | Форма редактирования заказа |
| `modules/orders/views/orders-backend/_order_position.php` | Форма редактирования позиций |
| `modules/cms/models/Parameter.php` | Параметр `days_can_be_returned` |
| `modules/users/models/UserSegment.php` | Сегменты пользователей (только блокировка наложенного платежа) |