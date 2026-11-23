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
- Остальные поля блоков `customer` и `return` не меняются. Реквизиты в `customer` (`bank_bic`, `bank_inn`, `bank_name`, `user_account`, `user_card_number`) передаются как сейчас из одноимённых ключей JSON `cms_orders.user_refund`; ключа нет — пустая строка. По возвратам с сайта `bank_inn` в `cms_orders.user_refund` записан пустой строкой (ECOMDEV-2649), поэтому в 1С уходит `bank_inn = ""`, как сейчас.

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

{% cut "Критерии приёмки" %}

1. Заказ без возврата → `is_bank_details_confirmed = null`, `is_refund_to_original_payment_method = null`.
2. Возврат на сайте или в новой версии МП заказа, оплаченного курьеру; клиент подтвердил реквизиты → `is_bank_details_confirmed = true`, `is_refund_to_original_payment_method = false`.
3. Возврат на сайте или в новой версии МП заказа с полной или частичной оплатой подарочным сертификатом; клиент подтвердил реквизиты → `is_bank_details_confirmed = true`, `is_refund_to_original_payment_method = false`.
4. Возврат на сайте заказа, оплаченного онлайн без подарочного сертификата → `is_bank_details_confirmed = null`, `is_refund_to_original_payment_method = true`.
5. Возврат из старой версии МП заказа, оплаченного курьеру, без передачи подтверждения реквизитов → `is_bank_details_confirmed = null`, `is_refund_to_original_payment_method = false`.
6. Тело запроса в журнале обмена соответствует отправленному.
7. При выгрузке `loadOrder` все остальные поля блоков `customer` и `return` остаются без изменений, кроме добавления двух новых признаков в `customer`.
8. Возврат на сайте с реквизитами → в `customer` реквизиты из `cms_orders.user_refund`, `bank_inn = ""`.

{% endcut %}

## Открытые вопросы

| Вопрос | Кому |
|---|---|
| 1С-12. Какое значение `is_refund_to_original_payment_method` передавать в 1С при повторной выгрузке заказов с возвратом, оформленным до внедрения признака? Согласовать до выкатки | {red}(не определён) |
