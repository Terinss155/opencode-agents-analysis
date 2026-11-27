# Рабочие вопросы «Возвратов 2.0»

В этой папке собраны вопросы к бизнесу и смежным командам: что уже решено по теме и что осталось выяснить. Одна тема — один файл. Решения по существу фиксируются в ADR и требованиях, а здесь — их краткий итог и открытые вопросы с адресатом.

## Этап 0

| Файл | О чём |
|---|---|
| [stage-0-bank-details_questions.md](./stage-0-bank-details_questions.md) | Срочная доработка действующего возврата: проверка банковских реквизитов, подтверждение клиентом, признаки для 1С |

## Запуск и переходный период

| Файл | О чём |
|---|---|
| [transition-period_questions.md](./transition-period_questions.md) | Переход со старых возвратов на новые: выключение старой схемы, обмены через Дружбу после переключения |

## Заявка на возврат

| Файл | О чём |
|---|---|
| [return-status-model_questions.md](./return-status-model_questions.md) | Статусы заявки в MVP, расхождения со схемой RetailCRM |
| [return-number_questions.md](./return-number_questions.md) | Номер заявки от 1С и QR-код для магазина |

## Позиции и карточка заказа

| Файл | О чём |
|---|---|
| [order-position-split_questions.md](./order-position-split_questions.md) | Деление строки позиции при возврате части одинаковых изделий: хранение, объединение, цены и баллы |
| [order-card_questions.md](./order-card_questions.md) | Как карточка заказа показывает изделия с оформленным возвратом |

## Способы возврата и логистика

| Файл | О чём |
|---|---|
| [return-carriers_questions.md](./return-carriers_questions.md) | Службы возврата: коды типов доставки, города, где служба принимает возвраты |
| [courier-intervals_questions.md](./courier-intervals_questions.md) | Даты и интервалы курьера: возврат без дат, проверка интервалов Дружбой |
| [return-methods-admin_questions.md](./return-methods-admin_questions.md) | Инструкция «Что дальше» для каждого способа возврата в админке |
| [store-return-courier-request_questions.md](./store-return-courier-request_questions.md) | Клиент сдал изделия в магазин при действующей курьерской заявке |
| [return-without-request_questions.md](./return-without-request_questions.md) | Посылка через ТК без предварительной заявки на возврат |
| [retailcrm-export_questions.md](./retailcrm-export_questions.md) | Выгрузка заявок из RetailCRM в ТК и письма клиенту |

## Деньги и баллы

| Файл | О чём |
|---|---|
| [refund-payment_questions.md](./refund-payment_questions.md) | Куда и сколько денег возвращается в зависимости от способа оплаты |
| [refund-bonus_questions.md](./refund-bonus_questions.md) | Какие баллы возвращаются и отменяются при возврате |

## Обмен с другими системами

| Файл | О чём |
|---|---|
| [1c-exchange_questions.md](./1c-exchange_questions.md) | Обмен заявками с 1С: проверка, номер, приёмка |
| [retailcrm-exchange_questions.md](./retailcrm-exchange_questions.md) | Обмен заявками с RetailCRM: приём заявок Дружбы, коды статусов, вебхуки |
| [mindbox-exchange_questions.md](./mindbox-exchange_questions.md) | Обмен с Mindbox: баллы к возврату, статусы позиций, события возврата |

## Где ещё искать

- Файлы по тегам (системы, темы, люди) — [tags.md](../../tags.md).
- Схема статусов заявки и позиций — [return-status-v4_state.md](../diagrams/state/return-status-v4_state.md).
- Решения — [adr/](../adr/).
