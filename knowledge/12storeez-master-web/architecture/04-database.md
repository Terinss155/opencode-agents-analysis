# База данных

> Сверено с `origin/develop` `dd4a997ac0`, 07.11.2026.

## Общие сведения

MariaDB 10.3 (не MySQL 8: оконные функции, CTE и JSON-функции ведут себя иначе — см.
`repo-map.md`). 242 файла моделей в `modules/`, `src/`, `components/`, `coreExtends/` объявляют
`tableName()`.

**Префикс таблиц** задаётся переменной `TABLE_PREFIX`, по умолчанию `cms_`. В моделях
используется запись `{{%orders}}`, что в рантайме превращается в `cms_orders`.

Логи пишутся в отдельное подключение `log_db` (переменные `LOG_DSN`, `LOG_USERNAME`,
`LOG_PASSWORD`, свой префикс `LOG_TABLE_PREFIX`), см. `config/common.php:169-175`.

Кэш схемы БД включён (`enableSchemaCache`, TTL 1 час — `config/common.php:165-167`,
действуют для web и консоли), но хранится не в Redis, а в файлах: компонент `cacheSchema`
типа `FileCache` в `@runtime/cache/dbSchema`. Сам компонент `cacheSchema` зарегистрирован
только в `config/web.php:324` — в чистом `config/console.php` (без web-расширения) его нет.

## Соглашения об именовании

- домены в именах таблиц идут после префикса: `catalog_*`, `orders_*`, `order_*`, `users_*`,
  `delivery_*`, `product_*`, `blog_*`;
- в моделях используется `{{%имя}}` для подстановки префикса;
- **исключения:** модели сертификатов задают имена жёстко — `cms_giftcard_sell`,
  `cms_giftcard_use`, `cms_giftcard2user` без `{{%}}`;
- таблица MySQL-очереди `default_queue` префикса не имеет в коде компонента — он подставляется
  из конфигурации.

### Имена, которые отличаются от ожидаемых

Частый источник ошибок при написании запросов:

| Ожидаемое имя | Фактическое |
|---|---|
| `cart` | `shopping_carts` |
| `cart_items` | `shopping_cart_positions` |
| `order_items` | `order_positions` |
| `product_colors` | нет такой таблицы; `products.color_id → dictionary_colors` |
| `order_positions.product_size_id` | `order_positions.item_id` |

## Ключевые таблицы по доменам

### Заказы и чекаут

| Таблица | Модель |
|---|---|
| `orders` | `modules/orders/models/Order.php` **и** `src/Modules/Order/Model/Order.php` |
| `order_positions` | `modules/orders/models/OrderPosition.php` (с 16.09.2026 — колонка `experiment`, вариант A/B-теста ECOMDEV-1821, миграция `m260916_120000_ecomdev_2105_orders_and_mobile_toggle.php`) |
| `orders_history` | `modules/orders/models/OrderHistory.php` |
| `order_positions_history` | `modules/orders/models/OrderPositionHistory.php` |
| `orders_payments` | `modules/payment/models/Payment.php` |
| `order_payment_links` | `src/Modules/Payment/Models/OrderPaymentLink.php` |
| `order_errors` | `modules/orders/models/OrderError.php` |
| `orders_exchange_log` | `modules/orders/models/OrdersExchangeLog.php` |
| `order_reservation_expiration` | `src/Modules/Reservation/Model/OrderReservationExpiration.php` |
| `offline_orders`, `offline_order_positions` | `src/Modules/Order/Model/OfflineOrder*.php` |
| `offline_order_retry_queue` | `src/Modules/Order/Model/OfflineOrderRetryQueue.php` |
| `shopping_carts` | `modules/cart/models/Cart.php` |
| `shopping_cart_positions` | `modules/shopping/models/ShoppingCartPosition.php` (колонка `experiment` — с 10.09.2026) |
| `checkout_user_settings` | `src/Modules/Cart/Model/CheckoutUserSettings.php` |
| `wishlist_items` | `modules/wishlist/models/WishlistItem.php` |

### Товары и каталог

| Таблица | Модель |
|---|---|
| `products` | `modules/product/models/Product/Product.php` |
| `product_sizes` | `modules/product/models/ProductSize.php` |
| `product_category` | `modules/product/models/ProductCategory.php` (составной ключ) |
| `dictionary_colors` | `modules/product/models/Colors/DictionaryColor.php` |
| `dictionary_sizes` | `modules/product/models/DictionarySize.php` |
| `catalog_category` | `modules/catalog/models/Category.php` |
| `catalog_category_tree_items` | `src/Modules/Product/Models/CategoryTreeItem.php` (Nested Sets) |
| `catalog_stock` | `modules/catalog/models/Stock.php` — склады и магазины |
| `catalog_item_stock` | `modules/catalog/models/ItemStock.php` — остаток по штрихкоду и магазину |
| `product_stocks` | `src/Modules/Product/Models/ProductStock.php` |
| `product_attributes` | `src/Modules/Product/Models/ProductAttribute.php` |
| `product_stocks_by_cities` | `src/Modules/Stock/Model/ProductStockByCity.php` |
| `product_size_mapping` | `src/Modules/Product/Models/ProductSizeMapping.php` — маппинг размеров по типу размерной таблицы (сентябрь 2026; у `products` и `product_history` появилась колонка типа таблицы, `m261014_120000_add_size_table_type_to_products_table.php`) |
| `product_order_weighted_demand`, `category_size_weight` | `src/Modules/Product/Models/ProductOrderWeightedDemand.php`, `CategorySizeWeight.php` — сортировка «взвешенный спрос» (август 2026), админка `ProductOrderWeightedDemandBackendController` |
| `product_order_kate`, `product_order_sonya` | веса мерчандайзинговой сортировки |

### Пользователи

| Таблица | Модель |
|---|---|
| `users_user` | `modules/users/models/User.php` (колонка `last_context` — последний выбранный раздел `female`/`male`/`home`, с 25.09.2026, пишется `LastContextService` с сайта и из приложения) |
| `users_address` | `modules/users/models/Address.php` |
| `users_auth` | `modules/users/models/Auth.php` |
| `users_geo` | `src/Modules/Delivery/Model/UserGeo.php` |
| `users_mobile_sessions` | `modules/mobile/models/UserMobileSession.php` |
| `jwt_refresh_token` | `src/Auth/Model/JwtRefreshToken.php` |
| `user_import_files` | `src/Modules/User/Models/UserImportFile.php` |

### Платежи и чеки

| Таблица | Назначение |
|---|---|
| `orders_payments` | Платежи по заказу |
| `payment_types`, `payment_statuses` | Справочники |
| `receipts`, `order_receipts` | Фискальные чеки |
| `order_receipts_to_send`, `*_outbox` | Асинхронная отправка чеков |
| `dolyame_payment_transaction_outbox` | Outbox Dolyame |
| `podeli_payment_transaction_outbox` | Outbox Podeli |
| `split_payment_transaction_outbox` | Outbox Yandex Split |
| `yandex_pay_payment_transaction_outbox` | Outbox Yandex Pay |
| `yandex_sbp_payment_transaction_outbox` | Outbox Yandex SBP |
| `notification_podeli`, `notification_yandex_split`, `notification_yandex_pay`, `notification_yandex_sbp` | Входящие уведомления провайдеров |

### Доставка и гео

| Таблица | Назначение |
|---|---|
| `delivery_tk` | Транспортные компании |
| `delivery_types`, `delivery_city`, `delivery_ipgeo` | Справочники доставки |
| `geo_city` | Города (`src/Modules/Delivery/Model/GeoCity.php`) |
| `pickup_points`, `boxberry_point`, `accord_point` | Пункты выдачи |
| `return_method`, `return_details_config` | Конфигурация возвратов |

### CMS и флаги

| Таблица | Назначение |
|---|---|
| `parameters`, `parameters_content`, `parameter_categories` | Фича-флаги и настройки |
| `mainpages`, `mainpage_blocks`, `mainpage_block_elements` | Главная страница |
| `ab_test`, `ab_test_variant` | A/B-тесты |
| `events_toggle` | Переключатели аналитических событий |
| `notifications` | In-app уведомления пользователей (`src/User/Notifications/Model/Notification.php`) |

### Интеграционные outbox и inbox

| Направление | Таблицы |
|---|---|
| RetailCRM | `rcrm_create_transaction_outbox/inbox`, `rcrm_update_transaction_outbox/inbox` |
| 1С | `onec_create_transaction_outbox`, `onec_update_transaction_outbox/inbox` |
| Mindbox | `mindbox_create_transaction_outbox`, `mindbox_update_transaction_outbox` |
| Lamoda | `lamoda_orders_outbox` |
| Фиды | `feed_counters` |

## Связи ключевых сущностей

### Корзина

```
shopping_carts
  ├─ user_id → users_user.id
  └─ hasMany shopping_cart_positions (cart_id)
       ├─ product_id → products.id
       └─ product_size_id → product_sizes.id
```

Позиции корзины загружаются через `getPositionsRelation()` с `joinWith('productRelation')` —
без N+1.

### Заказ

```
orders
  ├─ user_id         → users_user.id (relation getUser())
  ├─ cart_id         → shopping_carts.id (поле есть, но relation getCart() в моделях Order нет —
  │                     связь только через прямой запрос по cart_id)
  ├─ address_id      → users_address.id (relation getAddress())
  ├─ delivery_method → delivery_tk.id (relation getDeliveryMethod())
  ├─ hasMany order_positions (order_id)
  │    ├─ item_id  → product_sizes.id      ← не product_size_id!
  │    ├─ товар получается через размер
  │    ├─ stock_id → catalog_stock.id
  │    └─ status   → order_position_statuses
  ├─ hasMany orders_payments (order_id)
  └─ hasOne  order_statuses (по internal_id)
```

### Товар

```
products
  ├─ color_id          → dictionary_colors.id
  ├─ main_category_id  → catalog_category.id
  ├─ категории          → JSON-поле + связь M2M через product_category
  ├─ hasMany product_sizes (product_id)
  │    ├─ size_id → dictionary_sizes.id
  │    ├─ hasMany catalog_item_stock (по barcode)
  │    └─ hasOne  product_stocks (по barcode)
  └─ цветовые варианты — отдельные строки products с общим group_guid / super_model_guid
```

### ER-диаграмма коммерческого ядра

```mermaid
erDiagram
    users_user ||--o{ shopping_carts : "user_id"
    users_user ||--o{ orders : "user_id"
    shopping_carts ||--|{ shopping_cart_positions : "cart_id"
    shopping_cart_positions }o--|| products : "product_id"
    shopping_cart_positions }o--|| product_sizes : "product_size_id"
    orders ||--|{ order_positions : "order_id"
    orders }o--o| shopping_carts : "cart_id"
    orders ||--o{ orders_payments : "order_id"
    order_positions }o--|| product_sizes : "item_id"
    product_sizes }o--|| products : "product_id"
    product_sizes }o--|| dictionary_sizes : "size_id"
    products }o--|| dictionary_colors : "color_id"
    products }o--o{ product_category : "M2M"
    product_category }o--|| catalog_category : "category_id"
    product_sizes ||--o{ catalog_item_stock : "barcode"
    catalog_item_stock }o--|| catalog_stock : "store_code"
    orders }o--|| delivery_tk : "delivery_method"
```

## Служебные и легаси-таблицы

| Таблица | Назначение | Примечание |
|---|---|---|
| `default_queue` | MySQL-очередь заданий | Колонки `queue`, `run_at`, `payload`, `ukey`. Имя **жёстко захардкожено** в `components/SqlQueue.php` (`SqlQueueName::DEFAULT . '_queue'`) — `TABLE_PREFIX` к нему не применяется, в отличие от моделей ActiveRecord |
| `slave_queue` | Стейджинг синхронизации заказов | `modules/cms/models/SlaveQueue.php` |
| `log`, `frontend_logs` | Логи приложения и фронтенда | Отдельное подключение `log_db` |
| `product_order_kate`, `product_order_sonya` | Веса сортировки каталога | Пересобираются через временные таблицы |
| `product_size_stocks_temp` | Стейджинг импорта остатков | TRUNCATE + массовая загрузка |
| `catalog_item_quantity_buffer` | Буфер остатков под заказы | |
| `catalog_item_stocks_quantity_buffer` | Буфер синхронизации остатков | `src/Modules/Stock/Model/ItemStockQuantityBuffer.php` |
| `low_stock_alert_state` | Однократные алерты о низком остатке | |
| `complete_messages`, `popmechanic_contacts` | Маркетинговые артефакты | |

Остаток товара получается из трёх источников (`catalog_item_stock`, `product_stocks`, буферы)
и согласован не мгновенно, а по мере обработки очередей.

## Миграции

На `dd4a997ac0` — **220 миграций** (плюс `.gitignore` и каталог `ImportData/`, поэтому
`ls-tree` показывает 222 записи), диапазон: `m250403_150841_5479_add_is_express_to_cart.php`
(апрель 2025) — `m261023_120000_rename_dictionary_colors_ecomdev_2426.php` (23.10.2026).
**116 миграций (53%) написаны в 2026 году.** Классификация ниже сделана на срезе 196 миграций
(последняя — 17.08.2026) и не пересчитывалась; новые миграции перечислены в п. 8–11 списка
«Что разрабатывалось в 2026 году».

`m261023_120000_rename_dictionary_colors_ecomdev_2426.php`, несмотря на имя, таблицу не
переименовывает — она обновляет `dictionary_colors.title_ru` по `guid`.

### Соглашение об именовании

```
m{ГГММДД}_{ЧЧММСС}[_{номер задачи}]_{описание_через_подчёркивания}.php
```

Примеры:

- `m260602_100002_add_idx_orders_cart_id.php` — суффикс времени используется для упорядочивания
  связанных миграций одного дня;
- `m250403_150841_5479_add_is_express_to_cart.php` — с номером задачи;
- `m260210_091507_ab_test_ecomdev_887.php` — со ссылкой на задачу в описании.

Флаги-параметры добавляются через трейт `ParameterManager` (`addBooleanParameter` и аналоги).

### Распределение по доменам

Классификация приблизительная — часть миграций затрагивает несколько доменов сразу
(например, добавление параметра, влияющего и на корзину, и на доставку) и отнесена к
основному контексту по смыслу имени файла. Строка «Прочее» — разница между суммой явно
классифицированных строк и общим числом миграций (196 / 92), а не отдельная категория.

| Домен | Всего | Из них 2026 |
|---|---|---|
| Заказы, корзина, чекаут | 47 | 27 |
| Доставка, гео, ФИАС | 34 | 8 |
| Параметры CMS, мобильные, A/B | 33 | 19 |
| Товары, каталог, остатки | 30 | 18 |
| Платежи, сертификаты, BNPL | 29 | 15 |
| Пользователи, адреса | 8 | 3 |
| Прочее / на стыке доменов | 15 | 2 |
| **Итого** | **196** | **92** |

### Что разрабатывалось в 2026 году

По кластерам миграций видно направление работ:

1. **Резерв в магазине** (март–апрель) — `m260323_181900_1106_add_reservation_delivery_type.php`,
   `m260407_090042_create_reservation_parameters.php`,
   `m260417_150054_1339_add_order_reservation_expiration_table.php`.
2. **Новый чекаут и предвыбор оплаты** (март–июнь) —
   `m260330_143915_add_payment_method_preselection_parameter.php`,
   `m260331_083825_add_new_checkout_abc_enum_parameter.php`,
   `m260617_113742_add_preselected_payment_feature_parameter.php`.
3. **Yandex Pay и Yandex SBP** (май–июль) — `m260512_121100_add_new_yandex_pay_payment_type.php`,
   `m260520_121200_add_yandex_pay_fields_to_orders.php`,
   `m260625_170000_add_yandex_sbp_payment_method.php`,
   `m260701_130000_add_yandex_sbp_outbox_notification_and_parameters.php`.
4. **Ранний доступ** (июль) — `m260728_120000_add_early_access_parameter.php`,
   `m260728_130000_add_early_access_dates_to_products_table.php`,
   `m260729_140000_add_qty_site_early_access_to_product_stocks_table.php`.
5. **In-app уведомления** (июль) — `m260713_111620_create_notifications_table.php`,
   `m260804_140914_add_parameter_web_notifications_enabled.php`.
6. **Индексы производительности** (июнь) — серия `m260602_100001`…`m260602_100004` на
   `orders.order_num`, `orders.cart_id`, `wishlist_items._created` (поле называется с
   ведущим подчёркиванием), `shopping_carts.updated_at`.
7. **Повторные попытки офлайн-заказов и флаги RCRM** (апрель–июль) —
   `m260420_122824_add_offline_order_retry_queue_table.php`,
   `m260730_065013_add_is_rcrm_modified_column_order.php`.
8. **Сортировка «взвешенный спрос»** (август) — `m260828_120000_add_weighted_demand_sorting.php`:
   таблицы `product_order_weighted_demand`, `category_size_weight`, колонки в `products` и
   `product_history`.
9. **A/B-тест фона фото ECOMDEV-1821** (сентябрь) — `m260908_120000_ab_test_dark_vs_light_bg.php`,
   `m260910_160933_add_experiment_to_shopping_cart_positions.php`,
   `m260916_120000_ecomdev_2105_orders_and_mobile_toggle.php` (колонка `order_positions.experiment`
   добавлена без пары для `order_positions_history`).
10. **Размерные таблицы** (сентябрь–октябрь) — `m260921_083149_create_size_mapping_table.php`,
    `m261012_100000_add_size_info_fields_to_catalog_category_table.php`,
    `m261014_120000_add_size_table_type_to_products_table.php`.
11. **Последний раздел каталога и Mindbox** (сентябрь–октябрь) —
    `m260925_120000_add_last_context_to_users_user_table.php`,
    `m261011_120000_add_mindbox_integration_enabled_parameter.php`,
    `m261011_150000_remove_mindbox_sms_enabled_parameter.php`,
    `m261020_120000_add_early_access_vic_only_parameter.php`.

### Проверка парных миграций истории в CI

Скрипт `check-migrate-trigger.sh` запускается в CI и требует, чтобы миграция, меняющая
`{%orders}`, `{%order_positions}` или `{%products}`, шла в паре с миграцией соответствующей
таблицы истории (`{%orders_history}`, `{%order_positions_history}`, `{%product_history}`).

**У скрипта есть дефект** — он корректно работает только при одной изменённой миграции.
Подробности в [09-pitfalls.md](09-pitfalls.md). Правило при этом реальное: **изменяя основные
таблицы, добавляйте миграцию для таблицы истории.**

## Способы доступа к данным

| Слой | Где | Когда используется |
|---|---|---|
| ActiveRecord (легаси) | `modules/*/models/` | Корзина, заказ, товар — с бизнес-логикой в модели |
| ActiveRecord (современный) | `src/Modules/*/Model/` | Outbox, уведомления, резерв |
| Репозитории (~230 файлов в каталогах `Repository/`, `repository/`, `repositories/`) | `src/Modules/*/Repository/`, `modules/*/repository/` | Предпочтительно для нового кода |
| Сырой SQL | Репозитории, миграции, консольные команды | Массовый обмен остатками, пересборка сортировок, очистка outbox |

Примеры тяжёлых запросов:

| Файл | Что делает |
|---|---|
| `modules/api2/repository/ExchangeStockRepository.php` | Многотабличные JOIN, TRUNCATE временной таблицы, массовый INSERT |
| `modules/product/repository/ProductOrderSonyaRepository.php` | `CREATE TEMPORARY TABLE` и UPSERT в таблицу сортировки |
| `src/Modules/Order/Repository/MindboxOrderUpdateOutboxRepository.php` | Дедупликация через DELETE с self-JOIN |
| `modules/payment/repository/ReceiptRepository.php` | `INSERT … ON DUPLICATE KEY UPDATE` |
| `modules/catalog/repository/CatalogDataSource.php` | Загрузка дерева категорий с последующим кэшированием в Redis |

### Известные места с риском N+1

- `ProductSize::getSize()` (`modules/product/models/ProductSize.php:362`) вызывает
  `hasOne(...)->one()` внутри метода, а не через свойство-связь.
- `OrderPosition::beforeSave()` (`modules/orders/models/OrderPosition.php:445`) подгружает товар
  и размер на каждое сохранение.
- Фиды: в `src/Modules/Feed/Service/YandexFeedService.php:171` и `GarderoboFeedService.php:96`
  оставлен комментарий о необходимости заранее загружать товары с `with('sizes')`.

## Поиск

Поиск работает на **Elasticsearch**: `src/Search/Elastic/`, индексатор
`ElasticCatalogIndexerService`, алиас индекса задаётся параметром `elastic_catalog_index`.

Переиндексация идёт через MySQL-очереди (`reindexproduct`, `reindexproductstocks`,
`reindexproductsizes`) и RabbitMQ.

Пакет `yiisoft/yii2-sphinx` и файл `config/sphinx.php` присутствуют, но **в рантайме не
используются** — компонент не зарегистрирован, импортов в коде нет.

## Redis

Доступ через `Application\Cache\Redis\Contract\RedisInterface` с обязательным указанием группы:
`$redis->byGroup(RedisGroupDictionary::GROUP_*)`. Словарь —
`src/Cache/Redis/Dictionary/RedisGroupDictionary.php`: 42 константы, в `getValidGroups()`
43 группы (плюс `RateLimiterConfigurator::REDIS_GROUP`).

Основные группы:

| Область | Группы |
|---|---|
| Каталог | `CatalogCategories`, `FastProduct`, `FastProductLists`, `ProductsMobileListv2`, `CategoryDefaultProductsList`, `ProductSizeMappingByType` (новая) |
| Остатки | `stocks`, `ProductStocksMobile` |
| Корзина и чекаут | `NewCheckout`, `OrderCreateAction`, `PaymentType` |
| Мобильные | `UserMobileSession`, `MobileCategories`, `MobileInfo`, `AppVersionsConfig` |
| Интеграции | `Integration`, `Mindbox`, `WebhookOnec`, `Elastic` |
| Прочее | `AbTests`, `ProductImageBgExperiment` (новая, A/B фона фото), `UserSearch` (новая, кэш любимых категорий и размеров для API поиска пользователей), `Diginetica`, `SessionLocation`, `Auth`, `ActionPresent` |

Группа `BlockCategories` удалена в ECOMDEV-2228 вместе с админкой «Блок категорий».

Группы, исключённые из массового сброса (`getFlushExcludedGroups()`, `RedisGroupDictionary.php:110`):
`Logs`, `ExchangeErrors`, `Auth`, `Integration`, `OrderCreateAction`, `WebhookOnec`,
`ProductImageBgExperiment`, а также `RateLimiter` (`RateLimiterConfigurator::REDIS_GROUP`).

Помимо этого Redis используется как бэкенд Yii-компонентов кэша (`cache`, `cacheMain`,
`cacheYiiT`). Формирование ключа имеет неочевидную особенность — см.
[07-infrastructure.md](07-infrastructure.md) и [09-pitfalls.md](09-pitfalls.md).

Хранение сессий:

- **вход на сайте** — cookie `_identity` (`enableAutoLogin`, не HttpOnly, `config/web.php:110`)
  и стандартная PHP-сессия Yii: компонент `session` в конфигурации не переопределён, в Redis и
  БД сессии не хранятся;
- **корзина на сайте** — `shopping_carts.session_id` (не Redis);
- **мобильная авторизация** — таблица `users_mobile_sessions` с кэширующей обёрткой;
- **JWT** (только `/api/auth/*` и `/api/user/me`, фронт сайта их не вызывает) — таблица
  `jwt_refresh_token` плюс denylist в Redis с префиксом `jwt:deny:`
  (`src/Cache/Redis/Enum/RedisKeyPrefixEnum.php:8`).
