# Реестр тегов: Возвраты 2.0

Обновлено: 23.11.2026

Тег → все файлы проекта по теме: требования, вопросы, описания логики, ADR, разборы встреч, транскрибации, переписка, ТЗ. Пути — от `projects/returns-2.0/`. Копии для Яндекс Вики (`*_wiki.md`) и архив не включаются.

## Словарь тегов

### Системы

| Тег | Что объединяет | Заполнен |
|---|---|---|
| `#mindbox` | Mindbox: баллы, статусы строк, события возврата, коммуникации | да |
| `#retailcrm` | RetailCRM (Intaro): обмен заказами и заявками, статусы, свойства позиций | нет |
| `#1c` | 1С: передача заявки, валидация, приёмка, отмена | нет |
| `#wms` | склад, статусы WMS | нет |
| `#сдэк` | СДЭК: курьер, ПВЗ | нет |
| `#5post` | 5Post | нет |
| `#bts` | команда BTS и её сервисы (`mindbox-srv-go`, BFB) | нет |
| `#сайт` | сайт, веб-канал | нет |
| `#мп` | мобильное приложение, гейт | нет |

### Темы процесса

| Тег | Что объединяет | Заполнен |
|---|---|---|
| `#баллы` | возврат и начисление баллов | нет |
| `#реквизиты` | банковские реквизиты, способ возврата денег | нет |
| `#статусы-заявки` | статусная модель заявки на возврат | нет |
| `#статусы-позиции` | статусы позиции исходного заказа и изделий заявки | нет |
| `#деление-позиции` | деление строки позиции, одинаковые изделия | нет |
| `#курьер` | курьерский забор, интервалы | нет |
| `#возврат-в-магазине` | возврат в магазине, в том числе без заявки | нет |
| `#печатная-форма` | заявление на возврат, печатная форма | нет |
| `#этап-0` | этап 0 | да |

### Люди и команды

| Тег | Кто | Заполнен |
|---|---|---|
| `#ирина-васильева` | менеджер Mindbox | да |
| `#елена-васильева` | System Analyst, команда BTS | да |
| `#оля-свистунова` | Backend Developer | да |
| `#леша-осипенко` | System Architect | нет |
| `#катя-тихомирова` | Project Manager | нет |
| `#дружба` | отдел Дружбы (поддержка клиентов) | нет |
| `#intaro` | команда RetailCRM (Intaro) | да |

## #mindbox — обмен с Mindbox

**Вопросы**
- [requirements/questions/mindbox-exchange_questions.md](requirements/questions/mindbox-exchange_questions.md) — все вопросы к Mindbox и команде BTS: операции, статусы строк, расчёт баллов, события заявки, сообщения Ирине Васильевой и Елене Васильевой

**Упоминается в**
- [requirements/questions/refund-bonus_questions.md](requirements/questions/refund-bonus_questions.md) — правила баллов для клиента, вопросы к PM и лояльности
- [requirements/questions/order-position-split_questions.md](requirements/questions/order-position-split_questions.md) — деление строки позиции заказа
- [requirements/questions/retailcrm-exchange_questions.md](requirements/questions/retailcrm-exchange_questions.md) — код `lost`; кто считает баллы по заявкам Дружбы (вопрос к RetailCRM)

**Описание логики**
- [requirements/backend/mindbox-return-bonus_backend.md](requirements/backend/mindbox-return-bonus_backend.md) — `BL-RET-BONUS`: расчёт и фиксация баллов к возврату в Mindbox

**Диаграммы**
- ERD заявки на возврат — [requirements/diagrams/erd/return-request_erd.md](requirements/diagrams/erd/return-request_erd.md): поля баллов по изделию заявки
- Схема статусов v4 — [requirements/diagrams/state/return-status-v4_state.md](requirements/diagrams/state/return-status-v4_state.md): раздел 3, статусы позиции исходного заказа

**Требования**
- [requirements/brd.md](requirements/brd.md) — `FR-36`, `OQ-47`, `OQ-52`, `OQ-53`
- [requirements/srs/srs-web-mvp.md](requirements/srs/srs-web-mvp.md), [requirements/srs/srs-mobile-mvp.md](requirements/srs/srs-mobile-mvp.md) — баллы к возврату на экране оформления
- [requirements/traceability.md](requirements/traceability.md)

**ADR**
- `ADR-RET-092` — [расчёт баллов к возврату в Mindbox](<requirements/adr/[2026-10-21 16-30] ADR-RET-092-return-bonus-calculation-mindbox-v1.md>)
- `ADR-RET-064` — [баллы к возврату — отдельная история](<requirements/adr/[2026-10-14 15-00] ADR-RET-064-return-bonus-points-separate-story-v1.md>)
- `ADR-RET-039` — [статус заказа при возврате не меняется](<requirements/adr/[2026-10-02 10-00] ADR-RET-039-return-tag-without-order-status-change-v2.md>)
- `ADR-RET-101` — [коды статусов позиции](<requirements/adr/[2026-11-10 17-00] ADR-RET-101-return-position-status-codes-v2.md>)
- `ADR-RET-073` — [одинаковые изделия, повторная заявка](<requirements/adr/[2026-10-12 13-01] ADR-RET-073-identical-units-repeat-return-v2.md>)

**Разборы встреч**
- [meetings/[2026-11-16 14-00] Баллы из Mindbox_summary.md](<meetings/[2026-11-16 14-00] Баллы из Mindbox_summary.md>)
- [meetings/[2026-11-16 15-06] Weekly 12storeez & Intaro_summary.md](<meetings/[2026-11-16 15-06] Weekly 12storeez & Intaro_summary.md>) — операции Mindbox для возврата, встреча с менеджером Mindbox
- [meetings/[2026-11-12 14-59] PJ Возвраты (регулярная встреча по проекта у рамках OKR Q4)_summary.md](<meetings/[2026-11-12 14-59] PJ Возвраты (регулярная встреча по проекта у рамках OKR Q4)_summary.md>)
- [meetings/[2026-11-10 17-00] 12STOREEZ & Intaro RetailCRM Вопросы по обменам_summary.md](<meetings/[2026-11-10 17-00] 12STOREEZ & Intaro RetailCRM Вопросы по обменам_summary.md>)
- [meetings/[2026-10-21 16-30] Статусная модель. Продолжение_summary.md](<meetings/[2026-10-21 16-30] Статусная модель. Продолжение_summary.md>)

**Транскрибации**
- [[bandicam 2026-11-16 14-00-09-044] Баллы из Mindbox.md](<sources/transcriptions/[bandicam 2026-11-16 14-00-09-044] Баллы из Mindbox.md>) — вся встреча
- [[bandicam 2026-11-16 15-06-10-549] Weekly 12storeez & Intaro.md](<sources/transcriptions/[bandicam 2026-11-16 15-06-10-549] Weekly 12storeez & Intaro.md>)
- [[bandicam 2026-09-25 11-30-41-197] Обсуждение с Леной Васильевой логистики.md](<sources/transcriptions/[bandicam 2026-09-25 11-30-41-197] Обсуждение с Леной Васильевой логистики.md>) — `00:21:17–00:24:45`: кто отправляет возвраты в Mindbox
- [[bandicam 2026-09-25 13-30-52-064] Встреча с RCRM.md](<sources/transcriptions/[bandicam 2026-09-25 13-30-52-064] Встреча с RCRM.md>) — коммуникации Mindbox завязаны на статусы позиций
- [[bandicam 2026-10-07 14-00-18-551]  Возвраты 2.0. Макеты.md](<sources/transcriptions/[bandicam 2026-10-07 14-00-18-551]  Возвраты 2.0. Макеты.md>) — `00:42:18–00:43:23`: коммуникации Mindbox по возврату

**Переписка**
- [[2026-10-15] Переписка Лемешева — Васильева Mindbox (баллы при частичном возврате).md](<sources/answers/[2026-10-15] Переписка Лемешева — Васильева Mindbox (баллы при частичном возврате).md>)
- [[2026-11-16 16-30] Переписка Лемешева — Господинова, Свистунова (тип в вебхуке, токен, номер С, итоги 16.11).md](<sources/answers/[2026-11-16 16-30] Переписка Лемешева — Господинова, Свистунова (тип в вебхуке, токен, номер С, итоги 16.11).md>) — баллы позиции, учёт возвратов при изменении заказа
- [[2026-11-11] Переписка Лемешева — Осипенко, Свистунова (деление строки позиции заказа при возврате).md](<sources/answers/[2026-11-11] Переписка Лемешева — Осипенко, Свистунова (деление строки позиции заказа при возврате).md>) — начисленные баллы распределяет Mindbox

**ТЗ и документация**
- [sources/mindbox/Website.CalculateAuthorizedCart — расчёт корзины авторизованного пользователя.md](<sources/mindbox/Website.CalculateAuthorizedCart — расчёт корзины авторизованного пользователя.md>) — расчёт баллов к возврату
- [sources/mindbox/Website.UpdateOrderv2 — обновление заказа.md](<sources/mindbox/Website.UpdateOrderv2 — обновление заказа.md>) — фиксация возврата: поля изменения заказа
- [sources/ТЗ Программа лояльности 12storeez.md](<sources/ТЗ Программа лояльности 12storeez.md>)

**AS-IS и знания о системах**
- [as-is/00-overview.md](as-is/00-overview.md), [as-is/web/08-confirm-and-create-return.md](as-is/web/08-confirm-and-create-return.md), [as-is/mobile/07-create-return.md](as-is/mobile/07-create-return.md)
- [order-status-dictionaries.md](../../knowledge/12storeez-master-web/database/order-status-dictionaries.md) — раздел 5, маппинг `cms_mb_statuses_map`
- [order-integration-exchange.md](../../knowledge/12storeez-master-web/features/order-integration-exchange.md) — обмен заказами с Mindbox через outbox
- [08-integrations.md](../../knowledge/12storeez-master-web/architecture/08-integrations.md) — раздел Mindbox

**Задачи в Трекер**
- [requirements/tasks/index.md](requirements/tasks/index.md) — TNT-2687, ECOMDEV-1185

## #этап-0 — этап 0, банковские реквизиты

Заполнено по комплекту задач этапа 0 (банковские реквизиты).

**Вопросы**
- [stage-0-bank-details_questions.md](requirements/questions/stage-0-bank-details_questions.md) — решения и вопросы этапа 0: Р-1 (отменённое списание сертификата), 1С-12, Р-7, BNPL без сертификата (раздел 2.2)

**ADR**
- [[2026-11-19 15-00] ADR-RET-108-refund-details-without-inn-v1.md](<requirements/adr/[2026-11-19 15-00] ADR-RET-108-refund-details-without-inn-v1.md>) — поле ИНН убирается из форм на этапе 0
- [[2026-11-19 15-00] ADR-RET-109-phone-bank-details-confirmation-v1.md](<requirements/adr/[2026-11-19 15-00] ADR-RET-109-phone-bank-details-confirmation-v1.md>) — подтверждение реквизитов по телефону, возврат через RetailCRM
- [[2026-11-18 15-48] ADR-RET-111-card-number-credit-account-only-v2.md](<requirements/adr/[2026-11-18 15-48] ADR-RET-111-card-number-credit-account-only-v2.md>) — номер карты только для кредитного счёта

**Задачи в Трекер**
- [requirements/tasks/stage-0.md](requirements/tasks/stage-0.md) — список задач, состояние, порядок выкатки, блокирующие вопросы
- [ECOMDEV-2526 [B] Возврат 0.1. Единые правила запроса и проверки банковских реквизитов для сайта и МП.md](<requirements/tasks/stage-0/ECOMDEV-2526 [B] Возврат 0.1. Единые правила запроса и проверки банковских реквизитов для сайта и МП.md>) — правило «нужны реквизиты», формат реквизитов, признаки сайта и МП
- [ECOMDEV-2649 [B] Возврат 0.1. Реквизиты и подтверждение клиента в запросе создания возврата.md](<requirements/tasks/stage-0/ECOMDEV-2649 [B] Возврат 0.1. Реквизиты и подтверждение клиента в запросе создания возврата.md>) — реквизиты и подтверждение в запросе, сохранение в заказ, признак возврата на исходный способ оплаты, обязательность подтверждения по версии МП (предложение)
- [ECOMDEV-2651 [B] Возврат 0.1. Признаки возврата в обмене с 1С.md](<requirements/tasks/stage-0/ECOMDEV-2651 [B] Возврат 0.1. Признаки возврата в обмене с 1С.md>) — два признака в `loadOrder`
- [ECOMDEV-2532 [F] Возврат 0.1. Банковские реквизиты — чекбокс подтверждения и проверка по общим правилам.md](<requirements/tasks/stage-0/ECOMDEV-2532 [F] Возврат 0.1. Банковские реквизиты — чекбокс подтверждения и проверка по общим правилам.md>) — форма сайта
- [DEVIOS-2709 [iOS] Возврат 0.1. Банковские реквизиты — чекбокс подтверждения и проверка по общим правилам.md](<requirements/tasks/stage-0/DEVIOS-2709 [iOS] Возврат 0.1. Банковские реквизиты — чекбокс подтверждения и проверка по общим правилам.md>), [DEVANDROID-1800 [Android] Возврат 0.1. Банковские реквизиты — чекбокс подтверждения и проверка по общим правилам.md](<requirements/tasks/stage-0/DEVANDROID-1800 [Android] Возврат 0.1. Банковские реквизиты — чекбокс подтверждения и проверка по общим правилам.md>) — экраны МП, версия с чекбоксом, тексты ошибок под полями
- [ECOMDEV-2530 [B] Некорректное сохранение номера банковской карты.md](<requirements/tasks/stage-0/ECOMDEV-2530 [B] Некорректное сохранение номера банковской карты.md>) — закрытый баг номера карты в МП

## #ирина-васильева — менеджер Mindbox

- Вопросы и сообщение — [mindbox-exchange_questions.md](requirements/questions/mindbox-exchange_questions.md), «Сообщения для Mindbox и команды BTS»
- Переписка — [[2026-10-15] Переписка Лемешева — Васильева Mindbox (баллы при частичном возврате).md](<sources/answers/[2026-10-15] Переписка Лемешева — Васильева Mindbox (баллы при частичном возврате).md>)

## #елена-васильева — команда BTS

- Вопросы и сообщение — [mindbox-exchange_questions.md](requirements/questions/mindbox-exchange_questions.md), вопрос 15 и «Сообщения для Mindbox и команды BTS»
- Разборы встреч — [meetings/[2026-11-16 14-00] Баллы из Mindbox_summary.md](<meetings/[2026-11-16 14-00] Баллы из Mindbox_summary.md>), [meetings/[2026-11-19 15-00] PJ Возвраты (регулярная встреча по проекта у рамках OKR Q4 )_summary.md](<meetings/[2026-11-19 15-00] PJ Возвраты (регулярная встреча по проекта у рамках OKR Q4 )_summary.md>) — отчёты Qlik в плане, сервис логистики, задачи на статусы во всех системах
- Переписка — [[2026-11-20 13-00] ...согласование статусной модели MVP).md](<sources/answers/[2026-11-20 13-00] Переписка Тихомирова — Крицин, Мезинова, Колосов, Филатова, Соколова, Васильева (согласование статусной модели MVP).md>)
- Транскрибации — [[bandicam 2026-11-19 15-00-44-622] PJ Возвраты (регулярная встреча по проекта у рамках OKR Q4 ).md](<sources/transcriptions/[bandicam 2026-11-19 15-00-44-622] PJ Возвраты (регулярная встреча по проекта у рамках OKR Q4 ).md>), [[bandicam 2026-11-16 14-00-09-044] Баллы из Mindbox.md](<sources/transcriptions/[bandicam 2026-11-16 14-00-09-044] Баллы из Mindbox.md>), [[bandicam 2026-09-25 11-30-41-197] Обсуждение с Леной Васильевой логистики.md](<sources/transcriptions/[bandicam 2026-09-25 11-30-41-197] Обсуждение с Леной Васильевой логистики.md>)

## #оля-свистунова — Backend Developer

Заполнено по теме Mindbox и вопросу Р-7 этапа 0.

- Вопросы — [mindbox-exchange_questions.md](requirements/questions/mindbox-exchange_questions.md), вопросы 6, 12; [stage-0-bank-details_questions.md](requirements/questions/stage-0-bank-details_questions.md), Р-7 — признак подтверждения для возврата через RetailCRM
- Задачи — [ECOMDEV-2651 [B] Возврат 0.1. Признаки возврата в обмене с 1С.md](<requirements/tasks/stage-0/ECOMDEV-2651 [B] Возврат 0.1. Признаки возврата в обмене с 1С.md>) — передача признаков в 1С; [ECOMDEV-2649 [B] Возврат 0.1. Реквизиты и подтверждение клиента в запросе создания возврата.md](<requirements/tasks/stage-0/ECOMDEV-2649 [B] Возврат 0.1. Реквизиты и подтверждение клиента в запросе создания возврата.md>) — номер карты, срок хранения карты, повторный возврат без реквизитов (вопрос 4)
- ADR — [[2026-11-19 15-00] ADR-RET-109-phone-bank-details-confirmation-v1.md](<requirements/adr/[2026-11-19 15-00] ADR-RET-109-phone-bank-details-confirmation-v1.md>) — реквизиты из RetailCRM, согласие с решением, возврат из RetailCRM по `channel = support`; [[2026-11-18 15-48] ADR-RET-111-card-number-credit-account-only-v2.md](<requirements/adr/[2026-11-18 15-48] ADR-RET-111-card-number-credit-account-only-v2.md>) — номер карты только для кредитного счёта распространён на этап 0
- Переписка — [[2026-11-20 13-00] ...реквизиты из RetailCRM, is_bank_details_confirmed).md](<sources/answers/[2026-11-20 13-00] Переписка Лемешева — Осипенко, Свистунова (реквизиты из RetailCRM, is_bank_details_confirmed).md>), [[2026-11-16 16-30] ...итоги 16.11).md](<sources/answers/[2026-11-16 16-30] Переписка Лемешева — Господинова, Свистунова (тип в вебхуке, токен, номер С, итоги 16.11).md>), [[2026-11-11] ...деление строки позиции заказа при возврате).md](<sources/answers/[2026-11-11] Переписка Лемешева — Осипенко, Свистунова (деление строки позиции заказа при возврате).md>)

## #intaro — команда RetailCRM

Заполнено по теме Mindbox и справочнику причин возврата.

- Задачи — [ECOMDEV-2642 [B] Возвраты. Обновить справочник причин возврата.md](<requirements/tasks/US-01/ECOMDEV-2642 [B] Возвраты. Обновить справочник причин возврата.md>) — новые коды причин в справочнике RetailCRM
- Переписка — [[2026-11-20 13-00] ...причины возврата, RetailCRM и 1С перед выкаткой).md](<sources/answers/[2026-11-20 13-00] Переписка Осипенко — Лемешева, Крицин, Колосов (причины возврата, RetailCRM и 1С перед выкаткой).md>), [[2026-11-18 16-10] ...причины возврата, токен, статусная модель).md](<sources/answers/[2026-11-18 16-10] Переписка Лемешева — Господинова (причины возврата, токен, статусная модель).md>) — коды свободны, причины на тесте, причины RetailCRM вне списка, новый триггер для возвратов
- Разборы встреч — [meetings/[2026-11-16 15-06] Weekly 12storeez & Intaro_summary.md](<meetings/[2026-11-16 15-06] Weekly 12storeez & Intaro_summary.md>), [meetings/[2026-11-10 17-00] 12STOREEZ & Intaro RetailCRM Вопросы по обменам_summary.md](<meetings/[2026-11-10 17-00] 12STOREEZ & Intaro RetailCRM Вопросы по обменам_summary.md>)
