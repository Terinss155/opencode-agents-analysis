# AGENTS.md

Репозиторий — библиотека OpenCode агентов и скиллов для аналитики требований (E-commerce). Это НЕ приложение: нет кода, сборки, тестов, линтеров. Не запускай build/test/lint.

## Структура
- `.opencode/agents/*.md` — определения агентов (frontmatter).
  - `mode: primary`: `business-analyst`, `system-analyst`, `product-owner` (permission: редактирование `ask`, bash `ask`).
  - `mode: subagent`: `security-reviewer` (edit: deny — пишет только в `reports/`).
- `skill/*/SKILL.md` — скиллы OpenCode; подгружаются по frontmatter `description` через `skills.paths` в `opencode.json`. Зови скилл при запросе соответствующего артефакта (например, `openapi-spec`, `nfr-requirements`, `user-story`, `erd-model`, `security-review-checklist`).
- `opencode.json` — конфиг: `default_agent: system-analyst`, `edit`/`bash` = ask, `skills.paths: ["./skill"]`, скиллы — только из allow-списка (все 13, `*` = deny).

## Разделение контекстов
- **Бизнес-контекст (код):** `12storeez-master/` — внешний репозиторий (Yii2-монолит 12Storeez). Только для чтения при анализе; **запрещено изменять** и **запрещено добавлять в git** (правило в `.gitignore`).
- **Артефакты аналитики (описывают работу):** `requirements/` — все документы требований, диаграммы, черновики, справочники. Создавать и сохранять артефакты только здесь.
  - `requirements/{process}/` — артефакты по процессу/фиче (например, `requirements/product-return/`).
  - `requirements/drafts/` — черновики и исходные бизнес-материалы.
  - `requirements/*_структура.md` — справочники по кодовой базе.
- **Отчёты:** `reports/` — ревью и отчёты о качестве (создать, если нет).

## Язык и стиль
- Все артефакты и общение — на русском.
- Требования атомарные, измеримые, проверяемые; запрещены общие формулировки («быстро», «удобно»).
- Acceptance Criteria — в формате Gherkin (Given/When/Then); User Story — по INVEST.
- Порядок: AS-IS до TO-BE; трассируемость от бизнес-цели до User Story и технического артефакта.
- Факты не выдумывать: при нехватке вводных запросить уточнение, не додумывать.
- Каждый артефакт сохраняется в отдельный файл в `requirements/` (см. «Разделение контекстов»).

## Конвенция имён файлов (легко ошибиться)
- `business-analyst`: `*_as-is.bpmn.md`, `*_to-be.bpmn.md`, `*_brd.md`, `*_use-case.md`, `*_gap-analysis.md`, `*_brs.md`
- `system-analyst`: `*_backend.md`, `*_erd.plantuml` + `*_sql.sql`, `*_sequence.plantuml`, `*_openapi.yaml`, `*_asyncapi.yaml`, `*_nfr.md`
- `product-owner`: `*_user-story.md`, `*_backlog-priority.md`, `*_business-case.md`, `*_roadmap.md`, `*_stakeholder-map.md`
- Ревью/отчёты: папка `reports/` (создать, если нет); `security-reviewer` → `{артефакт}_security_review.md`, `system-analyst` (по явному запросу) → `{артефакт}_review_report.md`.

## Рабочий процесс
- PO → ценность и приоритеты (RICE/WSJF/MoSCoW), User Story. BA → процессы AS-IS/TO-BE, BRD, Use Case, Gap-анализ; передаёт SA.
- SA → технические артефакты: backend-логика, ERD, Sequence, OpenAPI, AsyncAPI, NFR; обеспечивает совместимость с User Story/Use Case.
- `security-reviewer` — ревью ИБ требований (ISO 27001, NIST, OWASP, PCI DSS, 152-ФЗ; STRIDE/PASTA/DREAD).
- Перед фиксацией требований BA/PO синхронизируются по приоритетам; технические детали — только через SA.

## Домен по умолчанию

- Сфера: E-commerce / Fashion-ритейл.
- Core-процессы: Каталог товаров, проведение оплат, программы лояльности и подарочные сертификаты.
- Операции и логистика: Управление складами, учет остатков, обработка и оформление возвратов.