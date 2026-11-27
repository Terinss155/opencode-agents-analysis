# SEQ-RET-BONUS: Баллы к возврату в Mindbox — от оформления до возврата баллов

Возвраты 2.0 · 26.11.2026 · Статус: предварительная схема

Схемы показывают, через какие системы проходят расчёт и фиксация возврата баллов. Логика — [BL-RET-BONUS-SUM](../../backend/mindbox-return-bonus-summary_backend.md); подробный анализ, правила сборки строк и обработка ошибок — [BL-RET-BONUS](../../backend/mindbox-return-bonus_backend.md); решение — `ADR-RET-114`. Новые методы сайта и мобильного приложения помечены TBD. Нужен ли после изменения заказа отдельный метод возврата баллов, не подтверждено — [mindbox-exchange_questions.md](../../questions/mindbox-exchange_questions.md), вопрос 19.

Участники:

| Участник | Система |
|---|---|
| App | Мобильное приложение |
| mobile-api-gate | Шлюз мобильного приложения |
| Сайт | Фронтенд сайта |
| Monolith | Монолит `12storeez-master-web` |
| Outbox и очередь | Таблица `mindbox_update_transaction_outbox` и очередь `mindbox.order.update.v1.command` монолита |
| monolith-bfb-ms | Сервис-прослойка монолита |
| mindbox-srv-go | Сервис связи с Mindbox (команда BTS) |
| Mindbox | Программа лояльности |
| 1C | Передаёт на сайт статус «Возврат принят» после приёмки на складе или в магазине |
| RetailCRM | Передаёт на сайт статус «Возврат принят», если Дружба перевела заявку вручную |

## 1. Предрасчёт и создание заявки — мобильное приложение

```mermaid
sequenceDiagram
    autonumber
    actor U as Пользователь
    participant APP as App
    participant API as mobile-api-gate
    participant MON as Monolith
    participant BFB as monolith-bfb-ms
    participant MSG as mindbox-srv-go
    participant MB as Mindbox

    U->>APP: Выбрать изделия для возврата
    APP->>API: POST /api/v1/orders/{order_id}/return/calculate (TBD)
    API->>MON: TBD — рассчитать сумму и баллы к возврату
    MON->>MON: Рассчитать сумму к возврату, собрать строки заказа
    MON->>BFB: PUT /api/v1/mindbox/orders/calculate-authorized
    BFB->>MSG: gRPC Order.CalculateAuthorized
    MSG->>MB: Website.CalculateAuthorizedCart
    MB-->>MSG: Баллы к возврату, баллы по строкам
    MSG-->>BFB: Баллы к возврату, баллы по строкам
    BFB-->>MON: Баллы к возврату, баллы по строкам
    MON-->>API: Сумма к возврату, баллы к возврату
    API-->>APP: Сумма к возврату, баллы к возврату
    APP-->>U: Блоки «Итого к возврату» и «Баллы к возврату»
    U->>APP: Нажать «Подтвердить возврат»
    APP->>API: POST /создать заявку на возврат (TBD)
    API->>MON: TBD — создать заявку на возврат
    MON->>MON: Проверить заявку, собрать строки заказа
    MON->>BFB: PUT /api/v1/mindbox/orders/calculate-authorized
    BFB->>MSG: gRPC Order.CalculateAuthorized
    MSG->>MB: Website.CalculateAuthorizedCart
    MB-->>MSG: Баллы по строкам
    MSG-->>BFB: Баллы по строкам
    BFB-->>MON: Баллы по строкам
    MON->>MON: Сохранить сумму и баллы по каждому изделию заявки
    MON-->>API: Заявка создана
    API-->>APP: Заявка создана
    APP-->>U: Шторка «Заявка уже у нас»
```

Предрасчёт и расчёт при создании заявки ничего не меняют в заказе Mindbox.

## 2. Предрасчёт и создание заявки — сайт

```mermaid
sequenceDiagram
    autonumber
    actor U as Пользователь
    participant WEB as Сайт
    participant MON as Monolith
    participant BFB as monolith-bfb-ms
    participant MSG as mindbox-srv-go
    participant MB as Mindbox

    U->>WEB: Выбрать изделия для возврата
    WEB->>MON: POST /рассчитать сумму и баллы к возврату (TBD)
    MON->>MON: Рассчитать сумму к возврату, собрать строки заказа
    MON->>BFB: PUT /api/v1/mindbox/orders/calculate-authorized
    BFB->>MSG: gRPC Order.CalculateAuthorized
    MSG->>MB: Website.CalculateAuthorizedCart
    MB-->>MSG: Баллы к возврату, баллы по строкам
    MSG-->>BFB: Баллы к возврату, баллы по строкам
    BFB-->>MON: Баллы к возврату, баллы по строкам
    MON-->>WEB: Сумма к возврату, баллы к возврату
    WEB-->>U: Блоки «Итого к возврату» и «Баллы к возврату»
    U->>WEB: Нажать «Подтвердить возврат»
    WEB->>MON: POST /создать заявку на возврат (TBD)
    MON->>MON: Проверить заявку, собрать строки заказа
    MON->>BFB: PUT /api/v1/mindbox/orders/calculate-authorized
    BFB->>MSG: gRPC Order.CalculateAuthorized
    MSG->>MB: Website.CalculateAuthorizedCart
    MB-->>MSG: Баллы по строкам
    MSG-->>BFB: Баллы по строкам
    BFB-->>MON: Баллы по строкам
    MON->>MON: Сохранить сумму и баллы по каждому изделию заявки
    MON-->>WEB: Заявка создана
    WEB-->>U: Модальное окно «Заявка уже у нас»
```

## 3. Фиксация возврата при «Возврат принят»

```mermaid
sequenceDiagram
    autonumber
    participant ONEC as 1C
    participant RCRM as RetailCRM
    participant MON as Monolith
    participant Q as Outbox и очередь
    participant BFB as monolith-bfb-ms
    participant MSG as mindbox-srv-go
    participant MB as Mindbox

    alt Склад или магазин принял изделия
        ONEC->>MON: TBD — статус заявки «Возврат принят»
    else Дружба вручную перевела заявку в «Возврат принят»
        RCRM->>MON: PUT /api/orders-new/{id}, заявка в «Возврат принят»
    end
    MON-)Q: Запись outbox с номером заказа
    Q->>MON: Сообщение с номером заказа
    MON->>MON: Перечитать заказ и заявки, собрать строки по принятым изделиям
    MON->>BFB: PUT /api/v1/mindbox/orders/calculate-authorized
    BFB->>MSG: gRPC Order.CalculateAuthorized
    MSG->>MB: Website.CalculateAuthorizedCart
    MB-->>MSG: Баллы по строкам
    MSG-->>BFB: Баллы по строкам
    BFB-->>MON: Баллы по строкам
    MON->>MON: Рассчитать остаток списанных баллов
    MON->>BFB: PATCH /api/v1/mindbox/orders/{ID заказа в Mindbox}
    BFB->>MSG: gRPC Order.UpdateOrderV2
    MSG->>MB: Website.UpdateOrderv2, принятые строки в статусе 505
    MB->>MB: Вернуть списанные баллы, снять начисленные за строки
    alt Заказ обновлён
        MB-->>MSG: Заказ обновлён
        MSG-->>BFB: Заказ обновлён
        BFB-->>MON: Заказ обновлён
        MON->>MON: Сохранить остаток баллов и номера строк
        MON->>Q: Удалить запись outbox
    else Ошибка или таймаут
        MSG-->>BFB: Ошибка
        BFB-->>MON: Ошибка
        MON->>MON: Оставить запись outbox для повторной отправки
    end
    opt Mindbox требует отдельный метод возврата баллов
        MON->>BFB: TBD — вернуть баллы
        BFB->>MSG: TBD — вернуть баллы
        MSG->>MB: TBD — метод возврата баллов Mindbox
    end
```

При приёмке на складе или в магазине 1С передаёт статус «Возврат принят» на сайт напрямую, метод — TBD. Ручной перевод Дружбой приходит вебхуком RetailCRM — [retailcrm-exchange_backend.md](../../backend/retailcrm-exchange_backend.md). Возврат денег клиенту — отдельный процесс, Mindbox в нём не участвует.
