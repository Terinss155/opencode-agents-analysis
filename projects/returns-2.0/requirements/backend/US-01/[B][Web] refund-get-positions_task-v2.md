# [B][Web] Форма возврата. Доработать получение позиций для возврата: срок, остаток изделий и данные доставки заказа

## Цель

Доработать ответ, который сайт получает при нажатии «Оформить возврат», чтобы система заново проверяла доступность возврата по тем же правилам, что в мобильном приложении (ECOMDEV-2343), отдавала только позиции с изделиями, доступными для возврата, остаток изделий по каждой позиции и данные доставки заказа для автоподстановки на следующих шагах.

**Web**
- `GET /orders/refund/get-positions?id={id}` — AJAX-запрос попапа возврата

## Описание реализации

Что требуется изменить:

1. Доработать `GET /orders/refund/get-positions?id={id}`.
2. Добавить новые поля в ответ:
   * `data.positions[].available_return_quantity`

   * `data.order_delivery`

   * `data.refund`
3. Изменить отбор позиций `data.positions[]` — подключить общий расчёт доступности возврата из ECOMDEV-2343.
4. Изменить расчёт `data.need_bank_details` — общее с мобильным приложением правило (ECOMDEV-2343, шаг 9).

Вне этой задачи:
* общий расчёт доступности возврата и параметр `days_can_be_returned_ff` создаются в ECOMDEV-2343;
* ограничение выбора количества изделий в попапе — задача фронта сайта;
* дата «Вернуть до …» (срок передачи изделий по способу возврата) — в методе списка способов возврата `return-method-list`, отдельная задача;
* сумма и баллы к возврату по позиции («Итого к возврату», «Баллы к возврату») — отдельная задача после согласования правила расчёта;
* постоянные тексты формы возврата (подсказка про «Отдел дружбы с клиентами», полная комплектация, смена города и др.) — на фронте сайта, задача фронта;
* таблицы `cms_returns`, `cms_return_positions`, `cms_return_statuses` создаются задачей на модель данных.

---

#### 1\. Выходные параметры

Входные параметры не меняются.

{% cut "**Изменённые поля**" %}

| Параметр | Было | Стало |
|---|---|---|
| `data.positions[]` | Позиции заказа в статусе «Добавлен» и не подарок (`price_before_discount > 1`). Статус заказа и срок возврата не проверяются | Позиции заказа в статусе «Добавлен» и не подарок — по признаку `is_present = 0`, как на странице заказа и в мобилке. Дополнительно: статус заказа допускает возврат, срок возврата по категории клиента (14 / 30 дней) не истёк, у позиции остались изделия, не занятые заявками на возврат. Позиции без доступных изделий в список не попадают |
| `data.need_bank_details` | `true` для всех способов оплаты, кроме онлайн-оплаты | `true`, если `cms_orders.payment_method` IN (3, 5, 15) — оплата курьеру наличными или картой, подарочный сертификат — или заказ оплачен подарочным сертификатом частично (сумма `cms_giftcard_use.amount` по заказу больше 0); иначе `false`. Правило общее с мобильным приложением (ECOMDEV-2343, шаг 9) |

{% endcut %}

{% cut "**Новые поля ответа**" %}

| Поле | Тип данных | Описание |
|---|---|---|
| `data.positions[].available_return_quantity` | `int` | Количество изделий позиции, доступных для возврата. Всегда больше 0 |
| `data.order_delivery` | `object` | Данные исходной доставки заказа |
| `data.refund` | `object` \| `null` | Куда вернутся деньги — блок «Возврат средств». `null`, если `data.need_bank_details = true`: тогда клиент указывает банковские реквизиты |
| `data.refund.message` | `string` | Текст для клиента |

Объект `data.order_delivery`:

| Поле | Тип данных | Описание |
|---|---|---|
| `data.order_delivery.country_iso` | string \| null | ISO-код страны доставки |
| `data.order_delivery.region` | string \| null | Регион доставки |
| `data.order_delivery.city` | string \| null | Город доставки |
| `data.order_delivery.city_fias` | string \| null | ID города в геосервисе (ФИАС для РФ) |
| `data.order_delivery.address` | object \| null | Адрес курьерской доставки — для проверки в геосервисе |
| `data.order_delivery.address.postal` | string \| null | Индекс |
| `data.order_delivery.address.street` | string \| null | Улица |
| `data.order_delivery.address.house` | string \| null | Дом |
| `data.order_delivery.address.housing` | string \| null | Корпус |
| `data.order_delivery.address.flat` | string \| null | Квартира |
| `data.order_delivery.pvz` | object \| null | Пункт выдачи, куда доставлялся заказ — для проверки в сервисе логистики |
| `data.order_delivery.pvz.provider` | string | Код службы пункта выдачи |
| `data.order_delivery.pvz.id` | string | ID пункта выдачи |
| `data.order_delivery.store` | object \| null | Магазин самовывоза — для проверки по списку магазинов, принимающих возвраты |
| `data.order_delivery.store.store_code` | int | Код магазина |

{% cut "Пример успешного ответа (поля AS-IS без изменений сокращены):" %}

```json
{
  "data": {
    "positions": [
      {
        "id": 67890,
        "title": "Пламя",
        "quantity": 3,
        "price_before_discount": 1500,
        "is_present": false,
        "available_return_quantity": 2
      }
    ],
    "reason_groups": [],
    "need_bank_details": false,
    "refund": {
      "message": "На банковскую карту с которой была произведена оплата"
    },
    "order_delivery": {
      "country_iso": "RU",
      "region": "Москва",
      "city": "Москва",
      "city_fias": "0c5b2444-70a0-4932-980c-b4dc0d3f02b5",
      "address": null,
      "pvz": {
        "provider": "sdek-pvz",
        "id": "1631548"
      },
      "store": null
    }
  },
  "errorCode": null,
  "errors": [],
  "message": "success",
  "success": true
}
```

**Нужны банковские реквизиты:**

```json
"need_bank_details": true,
"refund": null
```

Примеры `order_delivery` для курьерской доставки, самовывоза и случая без данных — как в ECOMDEV-2343.

{% endcut %}

{% endcut %}

`data.order_delivery` формируется всегда, независимо от доступности возврата. Из объектов `address`, `pvz`, `store` заполняется один, два других равны `null`.

Способ доставки определяется по типу службы доставки заказа (`cms_orders.delivery_method = cms_delivery_tk.id` → `cms_delivery_tk.type`) — так же, как в существующей логике формирования адреса заказа (`getFullAddressCompiled()`). Проверки выполняются по порядку:

1. самовывоз из магазина — `cms_delivery_tk.type` IN (7, 13) → заполняется `store`;
2. пункт выдачи — `cms_delivery_tk.type` IN (3, 11, 14, 15) и заполнен `cms_orders.pvz_id` → заполняется `pvz`;
3. иначе курьерская доставка → заполняется `address`; если пустые `cms_orders.street` и `cms_orders.house` → `address = null`.

#### 2\. Изменить логику отбора позиций для возврата

**Эндпоинт:** `GET /orders/refund/get-positions?id={id}`

Метод проходит **общий расчёт доступности возврата из ECOMDEV-2343 целиком** — те же шаги, в том же порядке, без исключений. Расчёт реализуется один раз и используется обоими каналами; для сайта не дублируется. Расчёт выполняется заново при каждом запросе: попап может быть открыт из списка заказов или спустя время после открытия страницы заказа.

{% cut "Какие шаги ECOMDEV-2343 выполняются" %}

| Шаг ECOMDEV-2343 | В этом методе |
|---|---|
| 1. Проверка статуса заказа | Да, без изменений. **Для этого метода проверка новая** — в AS-IS не выполнялась |
| 2. Категория клиента и срок возврата | Да, без изменений. **Для этого метода новая** |
| 3. Проверка срока возврата | Да, без изменений. **Для этого метода новая** |
| 4. Первичная проверка позиций | Да, без изменений: `status = 1`, `is_present = 0` — как на странице заказа и в мобилке. **Для этого метода условие «не подарок» меняется:** прежнее `price_before_discount > 1` заменяется на `is_present = 0` |
| 5. Количество изделий в заявках | Да, без изменений |
| 6. Доступное количество | Да, без изменений → `data.positions[].available_return_quantity` |
| 7. Признак по позиции | Да, но признак в ответ не отдаётся: позиция без доступных изделий не попадает в `data.positions[]` |
| 8. Сообщение `can_be_returned` в `messages[]` | Нет |
| 9. Банковские реквизиты | Да, без изменений → `data.need_bank_details`. **Для этого метода правило меняется:** прежнее «все способы оплаты, кроме онлайн-оплаты» заменяется общим правилом |

{% endcut %}

{% cut "Изменить логику отбора позиций" %}

**Проверки выполняются последовательно — от первого пункта к последнему.**

1. **Поиск заказа** — логика не меняется. Заказ не найден → ответ AS-IS: `success = false`, «Заказ не найден».

2. Система выполняет общий расчёт доступности возврата по заказу (ECOMDEV-2343, шаги 1–7).

   Прежний отбор позиций `OrderPositionRepository::findAllForRefundByOrderId()` (`status = 1` и `price_before_discount > 1`) заменяется первичной проверкой общего расчёта (`status = 1` и `is_present = 0`), чтобы страница заказа и попап отбирали позиции одинаково.

3. **Формирование `data.positions[]`**
   1. В список попадают позиции, у которых по результату расчёта возврат доступен (`<available_return_quantity> > 0`).
   2. Для позиции из списка `data.positions[].available_return_quantity = <available_return_quantity>`.
   3. Если статус заказа не допускает возврат, срок истёк или ни у одной позиции нет доступных изделий: `data.positions = []`, {red}(ответ сайту при недоступности возврата — `success = true` с пустым списком или `success = false` с текстом — требует согласования.)

4. **Причины возврата — логика не меняется.** `data.reason_groups` формируется по AS-IS-логике, независимо от результата расчёта.

5. **Формирование `data.need_bank_details`** — рассчитывается независимо от результата расчёта доступности возврата, по общему правилу (ECOMDEV-2343, шаг 9).
   1. Если `cms_orders.payment_method` IN (3, 5, 15) или заказ оплачен подарочным сертификатом частично — сумма `cms_giftcard_use.amount` по `cms_giftcard_use.order_id` = `cms_orders.id` больше 0 (как в ECOMDEV-2343, шаг 9) → `data.need_bank_details = true`.
   2. Иначе `data.need_bank_details = false`.

   > **AS-IS:** прежнее правило сайта — `true` для всех способов оплаты, кроме онлайн-оплаты, — больше не применяется и заменяется общим правилом. Сайт и мобильное приложение запрашивают банковские реквизиты в одних и тех же случаях.

6. **Формирование `data.refund`** — рассчитывается независимо от результата расчёта доступности возврата. Тексты — те же, что в мобилке (ECOMDEV-2343, шаг 10).

   1. Если `data.need_bank_details = true` → `data.refund = null`.
   2. Иначе `data.refund.message` определяется по способу оплаты заказа `cms_orders.payment_method`:

      | `cms_orders.payment_method` | `data.refund.message` |
      |---|---|
      | 1 — карта онлайн | На банковскую карту, с которой была произведена оплата |
      | 16, 20 — СБП | На банковскую карту, с которой была произведена оплата |
      | 13, 14, 17 — оплата частями | На банковскую карту, с которой была произведена оплата |
      | 15 — сертификат; заказ частично оплачен сертификатом | — (`data.need_bank_details = true`, блок реквизитов, `data.refund = null`) |
      | остальные | {red}(к согласованию) |

      Правило по `RULE-37`, `RULE-39`, `FR-45`, `ADR-RET-046` (07.10.2026): все онлайн-оплаты — один текст; при полной или частичной оплате подарочным сертификатом — блок реквизитов, на сертификат деньги не возвращаются.

{% endcut %}

{% cut "Маппинг API → БД" %}

| API | Тип данных | БД | Тип данных |
|---|---|---|---|
| `data.positions[].available_return_quantity` | int | Динамический расчёт (ECOMDEV-2343, шаги 5–6) из `cms_order_positions.quantity` и `cms_return_positions` | — |
| `data.order_delivery.country_iso` | string \| null | `cms_orders.country` | `varchar(255)` |
| `data.order_delivery.region` | string \| null | `cms_orders.state` | `varchar(255)` |
| `data.order_delivery.city` | string \| null | `cms_orders.city` | `varchar(255)` |
| `data.order_delivery.city_fias` | string \| null | `cms_orders.city_fias` | `varchar(255)` |
| `data.order_delivery.address.postal` | string \| null | `cms_orders.postal` | `varchar(255)` |
| `data.order_delivery.address.street` | string \| null | `cms_orders.street` | `varchar(255)` |
| `data.order_delivery.address.house` | string \| null | `cms_orders.house` | `varchar(255)` |
| `data.order_delivery.address.housing` | string \| null | `cms_orders.housing` | `varchar(255)` |
| `data.order_delivery.address.flat` | string \| null | `cms_orders.flat` | `varchar` {red}(длина — как в ECOMDEV-2343, сверить с БД) |
| `data.order_delivery.pvz.provider` | string | `cms_delivery_tk.slug` (по `cms_orders.delivery_method` = `cms_delivery_tk.id`) | `varchar(255)` |
| `data.order_delivery.pvz.id` | string | `cms_orders.pvz_id` | `varchar(32)` |
| `data.order_delivery.store.store_code` | int | `cms_delivery_tk.store_code` (по `cms_orders.delivery_method` = `cms_delivery_tk.id`) | `smallint(6)` |
| `data.need_bank_details` | boolean | Динамический расчёт по `cms_orders.payment_method` и сумме `cms_giftcard_use.amount` по заказу (шаг 5) | — |
| `data.refund.message` | string | Динамический расчёт по `cms_orders.payment_method` (шаг 6) | — |

{% endcut %}

### Ошибки

Состав ошибок не меняется. Недоступность возврата ошибкой не является — см. шаг 3.3.

## Открытые вопросы

Общие вопросы расчёта (пустой `end_date`, срок до конца дня или до времени, статусы заявок) — в ECOMDEV-2343; ответы применяются и к сайту.

| Вопрос | Кому |
|---|---|
| 1. Ответ, если на момент нажатия возврат уже недоступен (истёк срок, все изделия в заявках): пустой список или `success = false` с текстом? Какой текст? | Product Manager, фронт сайта |
| 2. Нужен ли в `data.positions[]` штрихкод позиции (`barcode`) для метода создания заявки? Сейчас позиция передаётся только `id` | Бэкенд-команда |
| 3. Тексты «Возврат средств» для остальных способов оплаты (строка «остальные» в шаге 6) — общие с мобилкой (ECOMDEV-2343). СБП, оплата частями и смешанная оплата (карта + сертификат) решены 07.10.2026 (`ADR-RET-046`) | Product Manager |
