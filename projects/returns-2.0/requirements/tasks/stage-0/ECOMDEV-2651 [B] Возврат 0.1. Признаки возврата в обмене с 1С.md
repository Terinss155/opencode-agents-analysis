# ECOMDEV-2651: [B] Возврат 0.1. Признаки возврата в обмене с 1С

## Цель

Передавать в 1С в выгрузке заказа два признака возврата: клиент подтвердил банковские реквизиты; деньги возвращаются на исходный способ оплаты.

## Описание реализации

**Endpoint:** выгрузка заказа в 1С — SOAP `loadOrder`.

Добавить в блок `customer` два поля. Поля передаются в каждой выгрузке заказа; пустое значение — JSON `null`.

| Поле | Тип | Значение |
|---|---|---|
| `is_bank_details_confirmed` | `boolean`, nullable | `cms_orders.user_refund` → ключ `is_bank_details_confirmed`; ключа нет → `null` |
| `is_refund_to_original_payment_method` | `boolean`, nullable | заказ с возвратом (в выгрузке есть позиция с `return = true`) → `cms_orders.is_refund_to_original_payment_method`; заказ без возврата → `null` |

- Те же поля — в копии тела запроса в журнале обмена `cms_orders_exchange_log`.
- Остальные поля блоков `customer` и `return` не меняются.

Выкатывать после ECOMDEV-2649: в ней появляются оба значения в заказе.

## Тестирование

{% cut "Критерии приёмки" %}

1. Заказ без возврата → оба поля `null`.
2. Возврат с реквизитами, подтверждёнными на сайте или в новой версии МП → `is_bank_details_confirmed = true`, `is_refund_to_original_payment_method = false`.
3. Возврат заказа, оплаченного онлайн без сертификата → `is_refund_to_original_payment_method = true`, `is_bank_details_confirmed = null`.
4. Возврат из старой версии МП или оформленный до выкатки → `is_bank_details_confirmed = null`.
5. Тело запроса в журнале обмена совпадает с отправленным.
6. Остальные поля блоков `customer` и `return` не изменились.

{% endcut %}
