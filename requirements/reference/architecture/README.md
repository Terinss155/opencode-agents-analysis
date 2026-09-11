# Архитектура 12 STOREEZ (AS-IS)

Описание фактического устройства монолита: слои, домены, БД, API, фронтенд, инфраструктура.
Документация описывает состояние ветки `master` и опирается на код, а не на планы.
Все утверждения прошли независимый аудит против исходного кода (сентябрь 2026).

> **Статус: AS-IS.** Этот документ описывает текущее (фактическое) состояние системы
> `12storeez-master`, которое мы анализируем как исходную точку. Для нашего проекта
> (выделение процесса возвратов в отдельную сущность) целевое состояние будет описано
> отдельно как **TO-BE** — в артефактах процессов (`requirements/{process}/`).

Единый PDF со всеми разделами и кликабельным оглавлением: [dist/12storeez-architecture.pdf](dist/12storeez-architecture.pdf).
Пересобрать после правок: `python3 requirements/reference/architecture/build-pdf.py` (нужны `pandoc`, `weasyprint`,
`@mermaid-js/mermaid-cli` — см. комментарий в начале скрипта).

## Состав

| Документ | О чём |
|---|---|
| [01-overview.md](01-overview.md) | Общая картина: два стека, точки входа, конфигурация |
| [02-backend.md](02-backend.md) | `modules/` и `src/`, слои, DI-контейнер, консольные команды |
| [03-business-domains.md](03-business-domains.md) | Каталог, корзина, заказы, платежи, доставка, пользователи, CMS |
| [04-database.md](04-database.md) | Схема, ключевые таблицы и связи, миграции |
| [05-api.md](05-api.md) | Три генерации API, аутентификация, эндпоинты, контракты |
| [06-frontend.md](06-frontend.md) | Сборка, связка PHP↔Vue, модули, ui-kit, редизайн |
| [07-infrastructure.md](07-infrastructure.md) | CI/CD, Kubernetes, очереди, кэш, наблюдаемость |
| [08-integrations.md](08-integrations.md) | Внешние системы и переменные окружения |
| [09-pitfalls.md](09-pitfalls.md) | Неочевидные связи и подводные камни |

## С чего начать

- **Новый разработчик** — [01-overview.md](01-overview.md), затем [02-backend.md](02-backend.md) или [06-frontend.md](06-frontend.md) по своему профилю, и обязательно [09-pitfalls.md](09-pitfalls.md).
- **Правка бизнес-логики** — [03-business-domains.md](03-business-domains.md) + [04-database.md](04-database.md).
- **Новый эндпоинт** — [05-api.md](05-api.md).
- **Новая интеграция или очередь** — [07-infrastructure.md](07-infrastructure.md) + [08-integrations.md](08-integrations.md).

## Наш проект: выделение возвратов (TO-BE)

**Цель проекта:** выделить процесс возвратов из домена «Заказы» в отдельную сущность «Возвраты».

**Исходная точка (AS-IS):** в текущей системе возвраты не являются самостоятельной сущностью —
логика размазана по нескольким местам:

| Аспект | Где сейчас (AS-IS) |
|---|---|
| Модель возврата | `modules/orders/models/OrderReturnPosition.php`, `modules/users/models/UserRefund.php` |
| Сервис возврата | `src/Modules/Order/Services/OrderRefundService.php` |
| Валидаторы | `src/Modules/Order/Validators/OrderRefundValidator.php`, `validators/order/OrderRefundRequestValidator.php` |
| Чеки возврата (АТОЛ) | `src/Modules/Receipt/` (RefundPrepayment, RefundFullpayment) |
| Мобильный возврат | `src/Modules/Mobile/Controllers/OrdersController.php` (actionReturnPositions, actionReturnDetails) |
| Причины возврата | `modules/orders/models/ReturnReason.php`, `ReturnReasonGroup.php` |
| Статусы возврата | `src/Modules/Order/Enum/StatusEnum.php`, `modules/orders/models/Order.php` (STATUS_ORDER_RETURNED_LK=31) |

**Целевое состояние (TO-BE):** отдельный домен «Возвраты» со своей моделью данных, сервисами,
API и статусной моделью. Артефакты TO-BE будут создаваться в `requirements/`
(бандл требований процесса «Возвраты 2.0») на основе этого AS-IS описания.

## Ключевые цифры

| Метрика | Значение |
|---|---|
| Легаси-модули (`modules/`) | 64 |
| Современные модули (`src/Modules/`) | 43 |
| Контроллеры (всего / админских) | 388 / 127 |
| ActiveRecord-модели с `tableName()` | 240 |
| Миграции | 196 (апрель 2025 — август 2026) |
| Модули фронтенда / entry points | 58 / 95 |
| Консольные команды | 94 |
| Строк в DI-контейнере | 1516 |

## Как поддерживать

Документация описывает структуру, а не отдельные фичи. При изменениях обновлять нужно, если:

- появился новый модуль в `modules/` или `src/Modules/`;
- добавлен платёжный провайдер, внешняя интеграция или очередь;
- изменилась схема аутентификации или версионирование API;
- изменился способ сборки фронтенда или связка PHP↔Vue.

Описание отдельных фич живёт рядом по теме — например, [docs/sale/categories-sale.md](../../../12storeez-master/docs/sale/categories-sale.md).
Контракты API — в `docs/frontend/openapi.yml`, `docs/mobileApi/openapi.yml`, `docs/ssr/openapi.yml`.
