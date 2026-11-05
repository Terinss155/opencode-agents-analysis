# Заказы

Процессы оформления и доставки заказа (прямой поток). Сейчас — даты и интервалы курьера СДЭК для
заказа: сайт и МП передают в логистику полный адрес доставки по частям.

## Задачи

| Файл | Что это |
|---|---|
| [DEVIOS-2694 [iOS] Изменить логику отображения интервалов доставки.md](<./tasks/DEVIOS-2694 [iOS] Изменить логику отображения интервалов доставки.md>) | Задача iOS: загрузка интервалов только при выбранном адресе, маппинг частей адреса для старого и нового чекаута, обратная совместимость |
| [ECOMDEV-2559 [B][Mobile-Api] Добавить delivery_address в метод получения интервалов доставки (mobile-api-gate).md](<./tasks/ECOMDEV-2559 [B][Mobile-Api] Добавить delivery_address в метод получения интервалов доставки (mobile-api-gate).md>) | Задача шлюза МП: параметр `delivery_address` в `POST /api/v1/delivery/intervals` и передача в логистику |

Родительская задача — ECOMDEV-588. Переписка по ней хранится в проекте возвратов:
[[2026-03-12] Переписка Васильевой с WEB и MOBILE — интервалы СДЭК для заказов (ECOMDEV-588).md](<../returns-2.0/sources/answers/[2026-03-12] Переписка Васильевой с WEB и MOBILE — интервалы СДЭК для заказов (ECOMDEV-588).md>).

## Связь с другими проектами

- Контракт метода логистики `Intervals`, общий для доставки и возврата, — [knowledge/esb-protobufs/api/logistics-intervals.md](../../knowledge/esb-protobufs/api/logistics-intervals.md).
- Возвраты 2.0 — тот же метод для курьерского возврата: адрес отправки `sending_address` и признак `is_return` ([ADR-RET-093](<../returns-2.0/requirements/adr/[2026-10-22 15-00] ADR-RET-093-courier-intervals-full-address-v2.md>), [вопросы по интервалам](../returns-2.0/requirements/questions/courier-intervals_questions.md)).
