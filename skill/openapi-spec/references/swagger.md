# Swagger: правила по проектам

> **Источники** (перенесено 17.11.2026):
> - правила swagger сайта (бывший `web-endpoint/SKILL.md` §3 и таблица «Состояние swagger» из §1; разделы 3.2 и 3.3 — **дословно**);
> - правила swagger МП (бывший `mobile-endpoint/SKILL.md` §3);
> - минимальная структура файла и обязательные разделы (бывший `openapi-spec/SKILL.md` §4.6.2, 4.6.5 — без обязательной версии 3.0.3);
> - решение по swag-тегам гейта (`knowledge/_archive/skills_2026-11-17/Анализ_скиллов_эндпоинты.md`, часть 2, §6.1 п. 9, 17.11.2026).
>
> Примеры — [../examples/](../examples/). Контракт, который описывает swagger, — [web.md](./web.md), [mobile.md](./mobile.md), [errors.md](./errors.md).

**Цель:** swagger самодостаточен — по открытому методу понятно, что передаётся, зачем, в каком формате и обязательно ли это, без чтения кода и задачи. На всех уровнях.

## 0. Где какой swagger

| Проект | Файл | Версия | Как правится | Раздел |
|---|---|---|---|---|
| Сайт (монолит) | `12storeez-master-web/docs/openapi/frontend.yml` | OpenAPI 3.1.0 | вручную | 1 |
| Mobile API в монолите | `12storeez-master-web/docs/openapi/mobile.yml` | OpenAPI 3.1.0 | вручную | 3 |
| Гейт МП | `mobile-monorepo-go`: аннотации `swag` + теги DTO → `docs/mobile_api/*` | Swagger 2.0 | генерируется, YAML руками не правится | 4 |
| Новый сервис / свой файл спецификации | — | по проекту | вручную | 6 |
| ESB (NestJS) | декораторы | — | — | **не описано** — открытый вопрос (часть 1 анализа, §9 п. 5) |

Покрытие swagger сайта проверяется в CI (`openapi-coverage.php` — `knowledge/12storeez-master-web/architecture/05-api.md`).

Swagger обновляется в задаче на тот уровень, где появился метод: `frontend.yml` — в задаче `[B][Web]`, `mobile.yml` — в задаче `[B][Mobile API]`, гейт — в задаче `[B][Mobile API][Gate]`. Аналитик прикладывает фрагмент к задаче только по запросу разработки (решение части 3, §4 п. 14); разработчик добавляет его в файл в той же задаче.

---

## 1. Сайт — `docs/openapi/frontend.yml`

Образец — [web-new-endpoint.yml](../examples/web-new-endpoint.yml) (условный ресурс, такого эндпоинта в системе нет).

### 1.1. Общие правила

1. **Версия.** Файл объявлен как `openapi: 3.1.0`: nullable — `type: [string, "null"]`, а не `nullable: true`; `required` — списком у объекта, не у свойства.
2. **Место.** Путь — в блоке `paths` рядом с путями того же тега; схемы — в `components/schemas`, ответы — в `components/responses`, общий path-параметр — в `components/parameters`.
3. **Тег** — из существующего списка `tags` (`Order`, `Cart`, `User`, `Notification`…). Новый тег — только с `description`.
4. **Операция:** `tags`, `summary` (одна фраза по-русски), `description` (поведение, значения по умолчанию, предобработка — если есть что сказать), `operationId` (camelCase, глагол + ресурс, уникален в файле: `getUserAddresses`, `createUserAddress`), `security`.
5. **`security`:** закрытый метод — `- Bearer: []`; открытый — `[]`.
6. **Параметры:** имя совпадает с маршрутом (`order_id`), `in` — только `path` / `query` / `header`; заполнение — по разделу 2.
7. **`requestBody`:** `required: true`, схема в `components/schemas` с именем `<Операция>Request`, список `required`; поля — по разделу 2.
8. **Ответы:** коды в кавычках (`"200"`). Успех — `$ref` на `components/responses/<Операция>Response` с заголовками `X-Response-Id`, `X-Response-Version`, `X-Language` и схемой через `allOf` от `BaseSuccessResponse`. Список — массив в `data` + `total` / `pagination` на верхнем уровне ([web.md](./web.md), раздел 7).
9. **Ошибки:** каждая — `description` с условием и `$ref` на `ValidationErrorResponse` (422) или `BaseErrorResponse` (остальные) + `example` с реальными `code` и `target`. 500 не описывается.
10. **Без кода и секретов:** без имён классов в `description`, без реальных токенов и персональных данных в `example`.
11. **Проверка:** фрагмент проходит `docker run --rm -v $PWD:/spec redocly/cli lint frontend.yml` без новых ошибок; HTML пересобирается командой из `docs/openapi/readme.md`.

### 1.2. Состояние swagger новых методов сайта (AS-IS, 28.10.2026)

| Что | Где | Почему плохо |
|---|---|---|
| У параметров нет `description` или оно повторяет имя (`description: locale`, `description: limit`) | `/api/v1/delivery/geo/*`, `/api/cart/*` (`mode`) | Непонятно, что передавать и зачем |
| `required: true` у параметров, которые в коде необязательны и имеют значение по умолчанию (`locale` = `ru`, `limit` = `0`, `ip` = `''`) | `/api/v1/delivery/geo/countries/{countryIso}/cities` | Swagger противоречит коду — несоответствие, выносится на согласование |
| `in: form` у параметров тела | `POST /api/cart/user-info` | В OpenAPI 3 такого места нет; тело описывается через `requestBody` |
| `required: true` внутри `properties`, нет `requestBody.required` | `PATCH /api/cart/items`, `SaveOrderReturnDetailsRequest` | Обязательность не читается инструментами |
| Ответ 200 без схемы | `GET /api/user/me` | Непонятно, что возвращается |
| `Authorization` — параметром заголовка при `security: [ ]` | `GET /api/user/me`, `/api/auth/refresh`, `/api/auth/logout` | Авторизация описывается через `security` |
| Служебные пометки в `summary` (`НОВЫЙ ЧЕКАУТ …`), имя класса в `description` | `/api/cart/*`, `change-payment-method` | `summary` — что делает метод; код в swagger не пишется |
| Хорошо: `required` списком, `description` с правилами и кодами ошибок, пример ошибки | `POST /cart/subscription/check` | Образец |

---

## 2. Заполнение параметров запроса и полей ответа

### 2.1. Сайт (`frontend.yml`) — дословно из `web-endpoint` §3.2

Для **каждого** параметра запроса (`path`, `query`, `header`, поле тела) и **каждого** поля ответа, включая вложенные объекты и элементы массивов:

| Атрибут | Когда | Как заполнять |
|---|---|---|
| `description` | всегда | На русском: что означает поле и для чего используется. Не повторяет имя (`description: locale` — нельзя). Для необязательного параметра — что происходит без него (значение по умолчанию). Для nullable — когда приходит `null`. Единицы измерения (секунды, рубли, копейки). Связь с другим методом, если значение берётся оттуда (`ID адреса — data[].id из списка адресов`) |
| `type` | всегда | `string` / `integer` / `number` / `boolean` / `array` / `object`; nullable — `[<тип>, "null"]`; у `array` — `items` с типом элемента |
| `format` | только если применимо | `date` (`YYYY-MM-DD`), `date-time` (ISO 8601 со смещением), `uuid`, `email`, `uri`, `int64`, `float`. Для строк без стандартного формата — `pattern` или правило в `description`, не выдуманный `format` |
| `required` | всегда | Параметр — `required: true / false`. Поле тела и ответа — список `required` у объекта. Для ответа `required` = поле приходит всегда (в том числе со значением `null`) |
| `example` | всегда | Реалистичное значение в формате поля; без реальных персональных данных и токенов. У параметра — на уровне параметра, у поля — в свойстве |
| `enum` | если значения ограничены списком | Все значения в `enum`; расшифровка каждого — в `description` в виде `<значение> — <смысл>; …`. Отдельные атрибуты (`x-enum-descriptions`) не вводятся — в файле их нет |

Ограничения (`minimum`, `maximum`, `maxLength`, `pattern`, `default`) указываются, если они есть в коде или в постановке задачи.

Изменение 17.11.2026: пример связи с другим методом `data.items[].id` заменён на `data[].id` — список отдаётся массивом в `data` ([web.md](./web.md), раздел 7).

### 2.2. Mobile API (`mobile.yml`) и гейт (`swag`) — из `mobile-endpoint` §3.3

Для **каждого** параметра запроса и **каждого** поля ответа, включая вложенные, на обоих уровнях:

| Атрибут | `mobile.yml` | Гейт (`swag`) | Как заполнять |
|---|---|---|---|
| `description` | `description` | текст в `@Param` / комментарий к полю DTO | На русском: смысл и назначение, не имя поля; для необязательного — поведение без него; для nullable — когда `null`; единицы измерения |
| `type` | `type` | тип в `@Param` / тип поля Go | `string` / `integer` / `number` / `boolean` / `array` / `object` |
| `format` | `format` | `format(...)` / тег `format:"..."` | Только если применимо: `date`, `date-time`, `uuid`, `email`, `int64` |
| `required` | `required` у параметра / список у объекта | `true` / `false` в `@Param`; у поля DTO — см. раздел 4, п. 5 | Для ответа — поле приходит всегда |
| `example` | `example` | `example(...)` / тег `example:"..."` | Реалистичное значение, без ПДн и токенов |
| `enum` | `enum` + расшифровка в `description` | `Enums(...)` + расшифровка в описании | Все значения: `<значение> — <смысл>; …` |

Ограничения (`minimum`, `maximum`, `maxLength`, `pattern`, `default`) — если они есть в коде (`fieldRules`) или в задаче.

---

## 3. Mobile API в монолите — `docs/openapi/mobile.yml` (OpenAPI 3.1.0)

Образец — [mobile-new-endpoint.yml](../examples/mobile-new-endpoint.yml) (условный ресурс, такого эндпоинта нет).

1. **Пути — без `/mobile`:** `servers` уже заканчиваются на `/mobile`. Новый метод `/mobile/favourite-stores` описывается как `/favourite-stores`. **AS-IS:** в файле встречаются оба варианта — существующие пути не трогать, расхождение — в список на согласование (раздел 5).
2. **Версия 3.1:** nullable — `type: [string, "null"]`; `required` — списком у объекта; коды ответов в кавычках.
3. **Общие элементы:**
   - параметры `$ref: "#/components/parameters/x-version"`, `$ref: "#/components/parameters/x-platform"` — в каждом методе;
   - `security: - MobileApiKey: [ ]` + `SessionToken: [ ]` (не `Bearer` — он у гейта);
   - ошибки — `MobileErrorBadRequestVersionOneResponse` (400), `MobileErrorNotAuthVersionOneResponse` (401).
4. **AS-IS-ошибка общей схемы:** `MobileErrorVersionOneResponseSchema` описывает `error_code` / `error_text` / `error_data` на верхнем уровне, а в ответе они внутри `result` рядом с `success: false`. Для нового метода пример ошибки показывает фактическую структуру; исправление общей схемы — открытый вопрос (не менять без согласования).
5. **Тег** — из списка `tags` файла; `operationId` — camelCase, уникален в файле (в `mobile.yml` и `frontend.yml` бывают одинаковые — это допустимо, файлы разные).
6. **Без имён классов** в `description` (AS-IS: `"...ReservationOrderTransformer"`) — поля описываются схемой.
7. **Список** — массив в `result` + `total` на верхнем уровне; `result.items` — только при соседних полях ([mobile.md](./mobile.md), раздел 6).

---

## 4. Гейт — аннотации `swag` (Swagger 2.0)

Образец — [gate-new-endpoint.go](../examples/gate-new-endpoint.go). Swagger гейта генерируется из комментариев к функции сервиса и тегов DTO; файлы `docs/mobile_api/*` руками не правятся.

1. **Операция:** `@Summary`, `@Description` — первой строкой `Proxy to <МЕТОД> /mobile/...` (для прокси), второй — что делает метод **на русском**; `@Tags` — ресурс; `@Security Bearer` (кроме открытых методов); `@Router <путь> [<метод>]`.
2. **Заголовки** — в каждом методе: `X-Platform` (`Enums(android, ios)`), `X-Version` (`example(1.16.1)`); `Cookie` — только если монолит его использует, без выдуманного примера.
3. **Параметры** `@Param <имя> <path|query|header|body> <тип> <обязательность> "<описание>"` + `example(...)`, `Enums(...)`, `default(...)`, `minimum(...)` / `maximum(...)`.
4. **Ответы:** `@Success 200` и `@Failure` на **каждый** HTTP-статус, который может вернуть монолит или гейт (400, 401, 404, 500), а не только 500. Схема ошибки — **фактическая**: проксируемая ошибка монолита — `{success: false, result: {error_code, error_text, error_data}}` (+ `isErrorFromPHP`); своя ошибка гейта — `{"error": {"message", "details"}}` (`dto.ErrorResponse`, [mobile.md](./mobile.md), раздел 8). AS-IS: у части методов в `@Failure` указан `FailureResponse`, а код отдаёт `{"error": …}` — в новом методе так не делать.
5. **DTO** (§6.1 п. 9, практика 17.11.2026):
   - **Согласовано (практика):** у каждого поля — тег `json` и `example:"..."` (866 вхождений в 113 файлах DTO); описание — комментарием к полю (попадает в `description`).
   - **Предложение (практики нет):** обязательность — `binding:"required"` / `validate:"required"`; enum — `enums:"a,b"`; nullable — указатель (`*string`) + `extensions:"x-nullable"`. В гейте эти теги встречаются 3 раза в 2 файлах; в задаче не требовать, обязательность и enum — в описании поля.
6. Имя DTO — `<Ресурс><Действие>Request` / `...Response` (как `CartSubscriptionCheckRequest`).

---

## 5. Доописание существующих методов

Дословно из `web-endpoint` §3.3; для МП и гейта — дополнения в конце.

Применяется, когда задача — дополнить swagger уже работающих методов (а не описать новый).

1. **Сначала изучить** текущие описания метода и соседних методов того же тега, общие схемы в `components` и соглашения файла.
2. **Сохранить структуру и стиль** файла: тот же порядок ключей, те же общие схемы и `$ref`, тот же язык описаний.
3. **Не дублировать** уже описанное и **не трогать корректные** определения: добавляются только недостающие атрибуты из раздела 2.
4. **Не менять контракт:** имена полей, типы, обязательность, пути, коды ответов и бизнес-логика остаются как в коде, даже если они нарушают правила [web.md](./web.md) / [mobile.md](./mobile.md).
5. **Не придумывать:** `format`, обязательность, значения `enum`, ограничения и смысл поля берутся только из кода, переводов, данных БД или задачи.
6. **Несоответствия и неизвестное — на согласование.** Если swagger противоречит коду (`required: true` у параметра с значением по умолчанию) или смысл / формат / список значений не удалось установить, swagger в этом месте не меняется, а пункт выносится в отдельный список:

   | Метод | Параметр / поле | Что в swagger | Что в коде / что неизвестно | Предложение | Кому |
   |---|---|---|---|---|---|
   | `GET /api/v1/delivery/geo/countries/{countryIso}/cities` | `limit` | `required: true` | необязательный, по умолчанию `0` | `required: false`, описать поведение при `0` | бэк |

7. **SRS не дополняется** отдельными таблицами параметров и лишними атрибутами: контракт живёт в swagger, SRS ссылается на метод.
8. **МП (`mobile.yml`).** Тот же порядок; расхождение путей с `/mobile` и без (раздел 3, п. 1) — в список на согласование.
9. **Гейт.** Доописание — правка аннотаций и DTO, а не сгенерированного YAML.

---

## 6. Новый файл спецификации (другой сервис)

Из бывшего `openapi-spec` §4.6.2, 4.6.5. Применяется, только если у сервиса нет своего файла и проект не задаёт иное; для монолита и гейта действуют разделы 1–4.

Минимальная структура:

```yaml
openapi: 3.1.0            # версию берём по проекту; 3.0.3 — если инструменты сервиса не поддерживают 3.1
info:
  title: Название API
  description: Описание назначения и особенностей API
  version: '1.0.0'
servers:
  - url: https://api.example.com/v1
    description: Production server
tags:
  - name: users
    description: Операции с пользователями
paths: {}
components:
  schemas: {}
```

Обязательные разделы:

- **`info`** — `title`, `description` (назначение API, что поддерживает), `version`; `contact` / `license` — если приняты в проекте:

  ```yaml
  info:
    title: User Management API
    description: |
      REST API для управления пользователями системы.
      Поддерживает полный CRUD для пользователей и ролей.
    version: '1.0.0'
  ```

- **`servers`** — URL и `description` каждого окружения:

  ```yaml
  servers:
    - url: https://api.example.com/v1
      description: Production server
    - url: https://staging-api.example.com/v1
      description: Staging server
  ```

- **`tags`** — группировка операций, у каждого тега `description`:

  ```yaml
  tags:
    - name: users
      description: Управление пользователями
    - name: auth
      description: Аутентификация и авторизация
  ```
