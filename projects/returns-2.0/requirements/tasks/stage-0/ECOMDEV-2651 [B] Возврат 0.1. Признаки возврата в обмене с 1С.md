# ECOMDEV-2651: [B] Возврат 0.1. Признаки возврата в обмене с 1С

## Цель

Передавать в 1С в выгрузке заказа два признака возврата: клиент подтвердил банковские реквизиты; деньги возвращаются на исходный способ оплаты.

## Описание реализации

**Endpoint:** выгрузка заказа в 1С — SOAP `loadOrder`.

Добавить в блок `customer` два поля. Поля передаются в каждой выгрузке заказа; пустое значение — JSON `null`, не пустая строка.

| Поле | Тип | Значение |
|---|---|---|
| `is_bank_details_confirmed` | `boolean`, nullable | заказ с возвратом (в выгрузке есть позиция с `return = true`) → значение параметра `is_bank_details_confirmed` из JSON в поле `cms_orders.user_refund` (`cms_orders.user_refund.is_bank_details_confirmed`), параметр отсутствует → `null`; заказ без возврата → `null`. По согласованным сценариям ECOMDEV-2649 в источнике формируются `true` или `null`; значение передаётся в 1С без преобразования |
| `is_refund_to_original_payment_method` | `boolean`, nullable | заказ с возвратом (в выгрузке есть позиция с `return = true`) → `cms_orders.is_refund_to_original_payment_method`; заказ без возврата → `null` |

{red}(Заказы с возвратом, оформленным до внедрения признака, при повторной выгрузке получат `is_refund_to_original_payment_method = false` — значение поля по умолчанию. Какое значение передавать в 1С — вопрос 1С-12, согласовать до выкатки.)

- Те же поля — в копии тела запроса в журнале обмена `cms_orders_exchange_log`.
- Остальные поля блоков `customer` и `return` не меняются.

Пример фрагмента выгрузки, остальные поля AS-IS сокращены. Заказ с возвратом:

```json
{
  "customer": [
    {
      "bank_inn": "",
      "is_bank_details_confirmed": true, //новый параметр
      "is_refund_to_original_payment_method": false //новый параметр
    }
  ]
}
```

Заказ без возврата:

```json
{
  "customer": [
    {
      "bank_inn": "",
      "is_bank_details_confirmed": null, //новый параметр
      "is_refund_to_original_payment_method": null //новый параметр
    }
  ]
}
```

Выкатывать после ECOMDEV-2649: в ней появляются оба значения в заказе.

## Тестирование

**Предусловия:** доступно исходящее тело `loadOrder` для проверки: журнал обмена `cms_orders_exchange_log` — для проверки сформированных данных; интеграционный стенд с обменом с 1С — если проверяется приём в 1С. Заказы (условия можно совмещать в одном заказе):
- без возврата;
- с возвратом, `cms_orders.user_refund` содержит `is_bank_details_confirmed = true`, `cms_orders.is_refund_to_original_payment_method = false`;
- с возвратом, параметра `is_bank_details_confirmed` в `cms_orders.user_refund` нет, `cms_orders.is_refund_to_original_payment_method = true`.

{% cut "Критерии приёмки" %}

1. Заказ без возврата → оба поля передаются со значением `null`.
2. Заказ с возвратом → `is_bank_details_confirmed` передаётся из `cms_orders.user_refund` без изменения значения.
3. Заказ с возвратом, параметр `is_bank_details_confirmed` отсутствует в `cms_orders.user_refund` → передаётся `null`.
4. Заказ с возвратом → `is_refund_to_original_payment_method` передаётся из `cms_orders.is_refund_to_original_payment_method` без изменения значения (`true` или `false`).
5. Тело запроса в журнале обмена соответствует отправленному.
6. При выгрузке `loadOrder` все остальные поля блоков `customer` и `return` остаются без изменений, кроме добавления двух новых признаков в `customer`.

{% endcut %}

## Открытые вопросы

| Вопрос | Кому |
|---|---|
| 1С-12. Какое значение `is_refund_to_original_payment_method` передавать в 1С при повторной выгрузке заказов с возвратом, оформленным до внедрения признака? Согласовать до выкатки | Мария Мезинова (1С), бизнес-владелец процесса возвратов, Оля Свистунова |
