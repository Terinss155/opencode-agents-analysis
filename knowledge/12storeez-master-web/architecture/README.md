# Архитектура 12 STOREEZ (AS-IS)

Описание фактического устройства монолита: слои, домены, БД, API, фронтенд, инфраструктура.
Документация опирается на код, а не на планы. Все утверждения прошли независимый аудит против
исходного кода (сентябрь 2026, ветка `master`).

**Актуализация:** все разделы (README, 01–09) сверены с `origin/develop` `dd4a997ac0`, 07.11.2026
(база предыдущей сверки — `be3cd759d2`, 07.10.2026). Опорная карта репозитория — [../repo-map.md](../repo-map.md).

> **Статус: AS-IS.** Этот документ описывает текущее (фактическое) состояние системы
> `12storeez-master`, которое мы анализируем как исходную точку. Для нашего проекта
> (выделение процесса возвратов в отдельную сущность) целевое состояние будет описано
> отдельно как **TO-BE** — в артефактах процессов (`requirements/{process}/`).

Единый PDF собирается из этих же файлов (README + 01–09). Прежняя сборка от 06.09.2026 устарела и перенесена в архив:
[../../_archive/12storeez-architecture.pdf](../../_archive/12storeez-architecture.pdf) (сборка 06.09.2026). Актуальный источник — md-файлы.
Собрать новый PDF (в `dist/`): `python3 requirements/reference/architecture/build-pdf.py` (нужны `pandoc`, `weasyprint`,
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
| Мобильный возврат | `src/Modules/Mobile/Controllers/OrdersController.php` (actionReturnPositions `:426`, actionReturnDetails `:1258`, actionReturnMethodList `:1327`); маршруты — `src/Modules/Mobile/Rules/UrlRule.php` |
| Веб-возврат (ЛК сайта) | `modules/orders/controllers/RefundController.php`, `modules/users/controllers/UserRefundController.php`, `src/Modules/Api2/Controller/OrdersController.php` (actionReturnMethodList `:96`, actionReturnDetails `:145`; `config/url.php:234-235`) |
| Причины возврата | `modules/orders/models/ReturnReason.php`, `ReturnReasonGroup.php` |
| Статусы возврата | `src/Modules/Order/Enum/StatusEnum.php`, `modules/orders/models/Order.php` (STATUS_ORDER_RETURNED_LK=31, `:275`) |

**Целевое состояние (TO-BE):** отдельный домен «Возвраты» со своей моделью данных, сервисами,
API и статусной моделью. Артефакты TO-BE будут создаваться в `requirements/`
(бандл требований процесса «Возвраты 2.0») на основе этого AS-IS описания.

## Ключевые цифры

На `origin/develop` `dd4a997ac0` (сверено 07.11.2026):

| Метрика | Значение |
|---|---|
| Легаси-модули (`modules/`) | 63 (удалён `userActivities`, ECOMDEV-2310) |
| Современные модули (`src/Modules/`) | 44 (новый — `Discount`) |
| Контроллеры (всего / админских) | 386 / 126 (файлы `*Controller.php` / `*BackendController.php`) |
| ActiveRecord-модели с `tableName()` | 242 |
| Миграции | 220 (апрель 2025 — октябрь 2026; на `be3cd759d2` — 208) |
| Модули фронтенда / entry points | 59 / 96 (`frontend/src/modules`, файлы `_entry.js`) |
| Консольные команды | 93 |
| Строк в DI-контейнере | 1589 |

## Как поддерживать

Документация описывает структуру, а не отдельные фичи. При изменениях обновлять нужно, если:

- появился новый модуль в `modules/` или `src/Modules/`;
- добавлен платёжный провайдер, внешняя интеграция или очередь;
- изменилась схема аутентификации или версионирование API;
- изменился способ сборки фронтенда или связка PHP↔Vue.

Описание отдельных фич живёт рядом по теме — например, [docs/sale/categories-sale.md](../../../../12stz/12storeez-master-web/docs/sale/categories-sale.md).
Контракты API — в `docs/openapi/frontend.yml` и `docs/openapi/mobile.yml` (с 16.09.2026; SSR-спека удалена).
Причины изменений по задачам ECOMDEV (с 28.09.2026) — в `openspec/changes/archive/` репозитория.

## История изменений

| Дата | Что обновлено | Коммит |
|---|---|---|
| 09.10.2026 | Пересчёт миграций (208) | `be3cd759d2` |
| 07.11.2026 | Сверка README, 01, 02, 03 с `origin/develop`: пересчитаны метрики, исправлен флоу создания заказа сайта (без `CreateOrderServiceSite`), учтены ECOMDEV-2228/2180/2342/2310, веб-бронирование, `src/User` (userApi), MariaDB 10.3, мобильные шлюзы | `dd4a997ac0` |
