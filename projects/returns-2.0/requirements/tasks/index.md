# Возвраты 2.0 — реестр задач в Трекере

Сверено с Трекером: 12.11.2026 · корень — [ECOMDEV-2246](https://tracker.yandex.ru/ECOMDEV-2246) [MVP] Возвраты (родитель — [ECOMDEV-1375](https://tracker.yandex.ru/ECOMDEV-1375)).

Описание и актуальный статус задачи — в Трекере. «Наш файл» — копия задачи в `requirements/tasks/` или анализ в `requirements/`, если есть.

## US1. Создание возврата — [ECOMDEV-2281](https://tracker.yandex.ru/ECOMDEV-2281)

Статус истории: Открыт.

### Подзадачи

| Задача | Автор | Исполнитель | Статус | Наш файл / примечание |
|---|---|---|---|---|
| [ECOMDEV-2343](https://tracker.yandex.ru/ECOMDEV-2343) [B][Mobile API] Карточка заказа. Доработать расчёт доступности и количества товара для возврата | Лемешева | — | Беклог | `US-01/ECOMDEV-2343 … v2.md` |
| [ECOMDEV-2354](https://tracker.yandex.ru/ECOMDEV-2354) [B][Web] Карточка заказа. Доработать расчёт доступности возврата и срок оформления возврата | Лемешева | — | Беклог | `US-01/ECOMDEV-2354 … v2.md` — в Трекере предыдущая версия, без `remaining_quantity` и `return_items` |
| [ECOMDEV-2355](https://tracker.yandex.ru/ECOMDEV-2355) [B][Web] Форма возврата. Доработать получение позиций для возврата | Лемешева | — | Беклог | `US-01/ECOMDEV-2355 … v2.md` — в Трекере предыдущая версия: без правила `need_bank_details` из ECOMDEV-2343, расчёта `data.refund` и `address.flat` |
| [ECOMDEV-2359](https://tracker.yandex.ru/ECOMDEV-2359) [B] Добавить признак приёма возвратов cms_catalog_stock | Лемешева | — | Беклог | `US-01/stores/ECOMDEV-2359 …md` |
| [ECOMDEV-2360](https://tracker.yandex.ru/ECOMDEV-2360) [B][Mobile API] Возвраты. Метод для получения списка магазинов, принимающих возвраты | Лемешева | — | Беклог | Сайт, МП и гейт одной задачей; отдельного метода деталей магазина нет |
| [ECOMDEV-2587](https://tracker.yandex.ru/ECOMDEV-2587) [B] Возвраты. Модель данных заявки на возврат | Свистунова | Ватанин | Пауза | `US-01/ECOMDEV-2587 …md` |
| [ECOMDEV-2588](https://tracker.yandex.ru/ECOMDEV-2588) [B] Возвраты. Шифрование банковских реквизитов заявки | Свистунова | Свистунова | Пауза | — |
| [ECOMDEV-2589](https://tracker.yandex.ru/ECOMDEV-2589) [B][Mobile API] Возвраты. Флаг показа возвратов в настройках | Свистунова | Ватанин | Можно тестировать | — |
| [ECOMDEV-2590](https://tracker.yandex.ru/ECOMDEV-2590) [B][Mobile API] Возвраты. Интервалы забора курьером и ПВЗ, принимающие возвраты, в гейтвее | Свистунова | — | Беклог | [return-carriers_questions.md](../questions/return-carriers_questions.md) |
| [ECOMDEV-2639](https://tracker.yandex.ru/ECOMDEV-2639) [B][WEB] Возвраты. Интервалы забора курьером и ПВЗ, принимающие возвраты, на сайте | Свистунова | — | Беклог | [return-carriers_questions.md](../questions/return-carriers_questions.md) |
| [ECOMDEV-2640](https://tracker.yandex.ru/ECOMDEV-2640) [B] Возвраты. Админка статусов заявки на возврат | Свистунова | — | Беклог | — |
| [ECOMDEV-2641](https://tracker.yandex.ru/ECOMDEV-2641) [B] Возвраты. Админка способов возврата | Свистунова | Осипенко | Разработка | [return-methods-admin_questions.md](../questions/return-methods-admin_questions.md) |
| [ECOMDEV-2642](https://tracker.yandex.ru/ECOMDEV-2642) [B] Возвраты. Обновить справочник причин возврата | Лемешева | Осипенко | Пауза (20.11) | `US-01/ECOMDEV-2642 …md` |
| [ECOMDEV-2665](https://tracker.yandex.ru/ECOMDEV-2665) [QA] Подготовка тестовой документации. Возвраты US1. Создание возврата | Ватанин | Ватанин | Беклог | — |
| [ECOMDEV-2677](https://tracker.yandex.ru/ECOMDEV-2677) [B] Возвраты. Не создавать заказ на сайте из возврата RetailCRM | Свистунова | Свистунова | Беклог | — |
| [ECOMDEV-2681](https://tracker.yandex.ru/ECOMDEV-2681) [B] Возвраты. Города приёма возвратов СДЭК и 5Post: вебхук логистики, первичная загрузка | Свистунова | Свистунова | Разработка (17.11) | [return-carriers_questions.md](../questions/return-carriers_questions.md) |
| [ECOMDEV-2712](https://tracker.yandex.ru/ECOMDEV-2712) [B] Возвраты. Админка городов приёма возвратов | Свистунова | — | Разработка (17.11) | [return-carriers_questions.md](../questions/return-carriers_questions.md) |
| [ECOMDEV-2683](https://tracker.yandex.ru/ECOMDEV-2683) [B] Возвраты. Статусы позиции заказа для возвратов | Свистунова | Свистунова | Беклог | — |
| [ECOMDEV-2684](https://tracker.yandex.ru/ECOMDEV-2684) [B] Возвраты. Способы возврата для города | Свистунова | Свистунова | Беклог | [return-carriers_questions.md](../questions/return-carriers_questions.md) |
| [ECOMDEV-2685](https://tracker.yandex.ru/ECOMDEV-2685) [B] Возвраты. Создание заявки на возврат | Свистунова | Свистунова | Беклог | — |
| [DEVIOS-2675](https://tracker.yandex.ru/DEVIOS-2675) [iOS] Оформление возврата | Осипов | — | Открыт | — |

### Связанные

| Задача | Статус | Примечание |
|---|---|---|
| [ECOMDEV-2348](https://tracker.yandex.ru/ECOMDEV-2348) [B] [Админка] Проверка доступных служб и интервалов для возврата | Беклог | Подзадача эпика ECOMDEV-2246 |
| [DEVIOS-2683](https://tracker.yandex.ru/DEVIOS-2683) [iOS] Возвраты MVP — API / модели / сервис | Открыт | — |
| [ECOMDEV-2582](https://tracker.yandex.ru/ECOMDEV-2582) [B][CI] Проверка истории миграций: не требовать историю, если миграция только ссылается на заказ, позицию или товар | Можно тестировать | Исполнитель — Ватанин |
| [TNT-2845](https://tracker.yandex.ru/TNT-2845) [Logistics. Backend] Winner Service. МРП. Возвратный поток | Беклог | Логистика |
| [TNT-2862](https://tracker.yandex.ru/TNT-2862) [Logistics. Backend] Админка. Возвраты в магазин | В работе | Логистика, исполнитель — Крамаровский |
| [ECOMDEV-1968](https://tracker.yandex.ru/ECOMDEV-1968) [D] Возвраты 2.0 | Беклог | Дизайн, исполнитель — Жуков |
| [ITGENERAL-33](https://tracker.yandex.ru/ITGENERAL-33) Возвраты 2.0 | Открыт | — |
| [SUP-110983](https://tracker.yandex.ru/SUP-110983) Создать новый тип доставки «Курьер СДЭК (возврат)» | Выполнена (18.11) | Техподдержка, автор — Лемешева, исполнитель — Попкова. Тип доставки `sdek-courier-vzt` в 1С, RetailCRM, на сайте и в логистике, доставка на возврат бесплатная; заведена отдельная ТК, код 568; всё выключено до запуска; [return-carriers_questions.md](../questions/return-carriers_questions.md) |

## US2. Просмотр списка возвратов — [ECOMDEV-2275](https://tracker.yandex.ru/ECOMDEV-2275)

Статус истории: Беклог.

| Задача | Связь | Статус |
|---|---|---|
| [ECOMDEV-2643](https://tracker.yandex.ru/ECOMDEV-2643) [B][Mobile API] Возвраты. Список заявок клиента | Подзадача | Беклог |
| [DEVIOS-2670](https://tracker.yandex.ru/DEVIOS-2670) [iOS] Возвраты. Список возвратов | Подзадача | Открыт |
| [DEVIOS-2671](https://tracker.yandex.ru/DEVIOS-2671) [iOS] Возвраты. Список — API / модели / сервис | Связана | Открыт |

## US3. Просмотр детальной информации по заявке на возврат — [ECOMDEV-2276](https://tracker.yandex.ru/ECOMDEV-2276)

Статус истории: Беклог.

| Задача | Связь | Статус |
|---|---|---|
| [ECOMDEV-2644](https://tracker.yandex.ru/ECOMDEV-2644) [B][Mobile API] Возвраты. Детальная информация по заявке | Подзадача | Беклог |
| [DEVIOS-2687](https://tracker.yandex.ru/DEVIOS-2687) [iOS] Детали возврата | Подзадача | Открыт |

## US3.1. Получить документы и QR-код возврата — [ECOMDEV-2278](https://tracker.yandex.ru/ECOMDEV-2278)

Статус истории: Открыт.

| Задача | Связь | Статус |
|---|---|---|
| [DEVIOS-2687](https://tracker.yandex.ru/DEVIOS-2687) [iOS] Детали возврата | Связана | Открыт |

## US4. Отмена заявки на возврат — [ECOMDEV-2277](https://tracker.yandex.ru/ECOMDEV-2277)

Статус истории: Открыт.

| Задача | Связь | Статус |
|---|---|---|
| [ECOMDEV-2645](https://tracker.yandex.ru/ECOMDEV-2645) [B][Mobile API] Возвраты. Отмена заявки клиентом | Подзадача | Беклог |
| [DEVIOS-2687](https://tracker.yandex.ru/DEVIOS-2687) [iOS] Детали возврата | Связана | Открыт |

## US6. Исполнение возврата денежных средств и восстановление бонусов — [ECOMDEV-2279](https://tracker.yandex.ru/ECOMDEV-2279)

Статус истории: Открыт.

| Задача | Связь | Статус |
|---|---|---|
| [ECOMDEV-2683](https://tracker.yandex.ru/ECOMDEV-2683) [B] Возвраты. Статусы позиции заказа для возвратов | Связана (подзадача US1) | Беклог |
| [ECOMDEV-2827](https://tracker.yandex.ru/ECOMDEV-2827) Возвраты. Обмен с Mindbox — баллы к возврату и письма о возврате | Связана (история обмена с Mindbox) | Открыт |

## Обмен с Mindbox — [ECOMDEV-2827](https://tracker.yandex.ru/ECOMDEV-2827)

История — подзадача эпика ECOMDEV-2246, заведена 26.11.2026; связана с US1 (ECOMDEV-2281) и US6 (ECOMDEV-2279). Файлы — в [mindbox/](./mindbox/). Описание логики — [BL-RET-BONUS-SUM](../backend/mindbox-return-bonus-summary_backend.md), вопросы — [mindbox-exchange_questions.md](../questions/mindbox-exchange_questions.md).

Статус истории: Открыт.

| Задача | Автор | Исполнитель | Статус | Наш файл / примечание |
|---|---|---|---|---|
| [ECOMDEV-2829](https://tracker.yandex.ru/ECOMDEV-2829) [B] Возвраты. Расчёт баллов к возврату в Mindbox | Лемешева | — | Беклог | `mindbox/ECOMDEV-2829 …md`. Зависит от ECOMDEV-1185, ECOMDEV-2828 |
| [ECOMDEV-2828](https://tracker.yandex.ru/ECOMDEV-2828) [B] Возвраты. Коды статусов строки Mindbox для заявки на возврат и принятого возврата | Лемешева | — | Беклог | `mindbox/ECOMDEV-2828 …md`. Зависит от ECOMDEV-2683 |
| [ECOMDEV-2831](https://tracker.yandex.ru/ECOMDEV-2831) [B] Возвраты. Фиксация возврата баллов в Mindbox при «Возврат принят» | Лемешева | — | Беклог | `mindbox/ECOMDEV-2831 …md`. Связана с US6 (ECOMDEV-2279); зависит от ECOMDEV-2829, ECOMDEV-2828 |

## Журнал действий по заявке на возврат — [ECOMDEV-2647](https://tracker.yandex.ru/ECOMDEV-2647)

Статус: Открыт. Зависит от [ECOMDEV-2587](https://tracker.yandex.ru/ECOMDEV-2587) (модель данных заявки). Связана с ECOMDEV-2648.

## Просмотр заявок на возврат в админке — [ECOMDEV-2648](https://tracker.yandex.ru/ECOMDEV-2648)

Статус: Открыт. Зависит от [ECOMDEV-2587](https://tracker.yandex.ru/ECOMDEV-2587) (модель данных заявки).

## Прочие подзадачи эпика ECOMDEV-2246

| Задача | Автор / исполнитель | Статус |
|---|---|---|
| [ECOMDEV-2400](https://tracker.yandex.ru/ECOMDEV-2400) Возвраты. Открытка с условиями возврата | Филатова | Беклог |
| [DEVIOS-2708](https://tracker.yandex.ru/DEVIOS-2708) [QA] Подготовка тестовой документации по возвратам для аппов | Шабловская | Тестируется |
| [DEVIOS-2710](https://tracker.yandex.ru/DEVIOS-2710) [QA] Анализ и уточнение требований по возвратам для аппов | Шабловская | Открыт |

## Этап 0 — [ECOMDEV-2796](https://tracker.yandex.ru/ECOMDEV-2796) Возврат 0.1. Банковские реквизиты: единые правила, подтверждение клиентом и передача в 1С

Подробно — [stage-0.md](./stage-0.md). История — подзадача эпика ECOMDEV-2246; ECOMDEV-2530 — подзадача эпика, в историю не входит.

Статус истории: Открыт.

| Задача | Статус |
|---|---|
| [ECOMDEV-2526](https://tracker.yandex.ru/ECOMDEV-2526) [B] Возврат 0.1: единые правила запроса и проверки банковских реквизитов для сайта и МП | Можно тестировать (MR монолита 6430, гейтов — Go 388, ESB 774), разработчик Свистунова, тестировщик Ватанин |
| [ECOMDEV-2530](https://tracker.yandex.ru/ECOMDEV-2530) [B] Некорректное сохранение номера банковской карты | Закрыт (Решен) |
| [ECOMDEV-2532](https://tracker.yandex.ru/ECOMDEV-2532) [F] Возврат 0.1. Проверка банковских реквизитов по общим правилам | Беклог |
| [ECOMDEV-2649](https://tracker.yandex.ru/ECOMDEV-2649) [B] Возврат 0.1. Реквизиты и подтверждение клиента в запросе создания возврата | Разработка, исполнитель Свистунова |
| [ECOMDEV-2651](https://tracker.yandex.ru/ECOMDEV-2651) [B] Возврат 0.1. Признаки возврата в обмене с 1С | Беклог |
| [DEVIOS-2709](https://tracker.yandex.ru/DEVIOS-2709) [iOS] Возврат 0.1. Банковские реквизиты: чекбокс подтверждения и проверка по общим правилам | Открыт |
| [DEVANDROID-1800](https://tracker.yandex.ru/DEVANDROID-1800) [Android] Возврат 0.1. Банковские реквизиты: чекбокс подтверждения и проверка по общим правилам | Открыт, исполнитель Лопухов |

## Post-MVP — [ECOMDEV-2256](https://tracker.yandex.ru/ECOMDEV-2256)

| Задача | Статус |
|---|---|
| [ECOMDEV-2280](https://tracker.yandex.ru/ECOMDEV-2280) [Post MVP] Возвраты US7. Уведомление об истекающем сроке передачи возврата | Открыт; связана с ECOMDEV-2246 |
| [ECOMDEV-2282](https://tracker.yandex.ru/ECOMDEV-2282) [Post MVP] Возвраты US8. Просмотр идентификаторов для передачи изделий в ТК (QR / Штрихкоды) | Открыт |
| [ECOMDEV-2283](https://tracker.yandex.ru/ECOMDEV-2283) [Post MVP] Возвраты US9. Категории Friends & Family | Беклог |

## Задачи BTS

Сверено с Трекером: 17.11.2026 · очередь TNT · корень аналитики логистики — [TNT-2516](https://tracker.yandex.ru/TNT-2516) [Logistics] [SA] Аналитика. Возвраты 2.0 (Васильева, «Анализ»). С эпиком ECOMDEV-2246 напрямую не связаны.

### Аналитика

| Задача | Исполнитель | Статус | Что даёт / связь |
|---|---|---|---|
| [TNT-2516](https://tracker.yandex.ru/TNT-2516) [Logistics] [SA] Аналитика. Возвраты 2.0 | Васильева | Анализ | Связывает задачи логистики по возвратам |
| [TNT-2717](https://tracker.yandex.ru/TNT-2717) [Logistics] [SA] Аналитика. Подготовить ADR для проекта Возвраты 2.0 | Васильева | Закрыт | — |
| [TNT-2718](https://tracker.yandex.ru/TNT-2718) [Logistics] [SA] Аналитика. Подготовить описание настроек в Логистике | Васильева | Закрыт | — |
| [TNT-2866](https://tracker.yandex.ru/TNT-2866) [Logistics] [SA] Аналитика. Кросскомандные договорённости для возвратов | Васильева | В работе | — |

### Даты и интервалы курьера — метод `Logistics.WinnerService.Intervals`

| Задача | Исполнитель | Статус | Что даёт / связь |
|---|---|---|---|
| [TNT-2837](https://tracker.yandex.ru/TNT-2837) [Logistics. Backend] Winner Service. Метод получения интервалов. Возвратный поток: признак возврата и адрес отправки. Получение дат забора посылки от ТК CDEK | Крамаровский | Закрыт (16.11) | `is_return`, `sending_address`; `is_return` сверяется с признаком возвратного типа доставки, иначе 400; даты от СДЭК с ближайшей даты по отсечке 16:00 МСК; один интервал 09:00–18:00; число дат — настройка `delivery_interval_days`; ошибка СДЭК — 400. ECOMDEV-2590, 2639; [courier-intervals_questions.md](../questions/courier-intervals_questions.md) |
| [TNT-2876](https://tracker.yandex.ru/TNT-2876) [Logistics. Backend] Winner Service. Доработка метода получения интервалов | Крамаровский | Закрыт (13.11) | `delivery_address` и `sending_address` — объект `ClientAddress` (`full_address`, `country_iso`, `region`, `city`, `street`, `house`); без адреса — ручные интервалы. ECOMDEV-2590, 2639 |
| [TNT-2937](https://tracker.yandex.ru/TNT-2937) [Logistics. Backend] Winner Service. Доработка метода получения интервалов | Крамаровский | Беклог, спринт 113 | Меняет TNT-2876: при включённой интеграции без адреса — ошибка `empty sending address`, без `region`, `city` или `house` — `incomplete sending address`; при выключенной — ручные интервалы. ECOMDEV-2590, 2639 |
| [TNT-2844](https://tracker.yandex.ru/TNT-2844) [Logistics. Frontend] Админка. Демонстрация. Метод расчёта интервалов для возвратного потока | Ляхов | Закрыт | Админка логистики |
| [TNT-1905](https://tracker.yandex.ru/TNT-1905) [Logistics. Backend] Winner Service. Метод получения интервалов. Новый параметр для адреса заказа. Получение интервалов от ТК CDEK | Крамаровский | Закрыт | Прямой поток, образец для возвратного |
| [TNT-1750](https://tracker.yandex.ru/TNT-1750) [Logistics. Backend] Интервалы доставки с учетом таймзон. Метод расчёта интервалов | Крамаровский | Закрыт | Без `timezone` расчёт по Москве; `ADR-RET-062` |

### Возвратный тип доставки

| Задача | Исполнитель | Статус | Что даёт / связь |
|---|---|---|---|
| [TNT-2840](https://tracker.yandex.ru/TNT-2840) [Logistics. Backend] Доработка БД. Признак возвратного типа доставки | Крамаровский | Закрыт | `delivery_type.is_return` |
| [TNT-2839](https://tracker.yandex.ru/TNT-2839) [Logistics. Backend] Админка. Признак возвратного типа доставки | Крамаровский | Закрыт | Тип доставки `sdek-courier-vzt`; [return-carriers_questions.md](../questions/return-carriers_questions.md) |
| [TNT-2843](https://tracker.yandex.ru/TNT-2843) [Logistics. Frontend] Админка. Признак возвратного типа доставки | Ляхов | Закрыт | — |

### Пункты выдачи, принимающие возвраты

| Задача | Исполнитель | Статус | Что даёт / связь |
|---|---|---|---|
| [TNT-2710](https://tracker.yandex.ru/TNT-2710) [Logistics. Backend] Доработка БД и Workers. Хранение признака приёма возвратов | Крамаровский | В работе | — |
| [TNT-2712](https://tracker.yandex.ru/TNT-2712) [Logistics. Backend] Доработать методы получения списка ПВЗ и деталей ПВЗ. Признак приёма возвратов | Крамаровский | Готово к релизу | Фильтр и признак `is_return_available`. ECOMDEV-2590, 2639, 2359 |
| [TNT-2713](https://tracker.yandex.ru/TNT-2713) [Logistics. Backend] Админка. Доработать метод для справочников ПВЗ. Признак приёма возврата | Крамаровский | Закрыт | — |
| [TNT-2714](https://tracker.yandex.ru/TNT-2714) [Logistics. Frontend] Админка. Доработать справочники для ПВЗ. Признак приёма возвратов | Ляхов | Закрыт | — |
| [TNT-1889](https://tracker.yandex.ru/TNT-1889) Получать инфо от логистики изменения по списку пвз в городе (Яндекс ПВЗ, 5Post, СДЭК ПВЗ) | Васильева | Закрыт | Вебхук покрытия городов, прямой поток (вместе с [ECOMDEV-1170](https://tracker.yandex.ru/ECOMDEV-1170)). ECOMDEV-2681 |

### Возвраты в магазин

| Задача | Исполнитель | Статус | Что даёт / связь |
|---|---|---|---|
| [TNT-2862](https://tracker.yandex.ru/TNT-2862) [Logistics. Backend] Админка. Возвраты в магазин | Крамаровский | Ревью | — |
| [TNT-2863](https://tracker.yandex.ru/TNT-2863) [Logistics. Frontend] Админка. Возвраты в магазин | Ляхов | Беклог | — |

### Метод расчёта победителя (МРП)

| Задача | Исполнитель | Статус | Что даёт / связь |
|---|---|---|---|
| [TNT-2845](https://tracker.yandex.ru/TNT-2845) [Logistics. Backend] Winner Service. МРП. Возвратный поток | — | Беклог | — |
| [TNT-2846](https://tracker.yandex.ru/TNT-2846) [Logistics. Frontend] Админка. Демонстрация. Метод расчёта победителя (МРП) для возвратного потока | — | Беклог | — |

### Mindbox — `mindbox-srv-go`

| Задача | Исполнитель | Статус | Что даёт / связь |
|---|---|---|---|
| [TNT-2687](https://tracker.yandex.ru/TNT-2687) Необходимо добавить передачу номера заказа в методе calculate | Крамаровский | Закрыт (14.10) | ID заказа в расчёте; в `mindbox.proto` на `origin/master` поля нет. ECOMDEV-1185; [mindbox-return-bonus_backend.md](../backend/mindbox-return-bonus_backend.md), [mindbox-exchange_questions.md](../questions/mindbox-exchange_questions.md), вопрос 15 |

