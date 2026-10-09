# Handoff: настройка рабочего пространства — 09.10.2026

## Цель
Рабочее пространство аналитика: `12stz` — только актуальные рабочие репозитории (только чтение),
`new` — личный репозиторий с проектами, знаниями о системах, агентами и скиллами для OpenCode и
Claude Code с одинаковыми инструкциями и ограничениями.

## Сделано
- `12stz/12storeez-master-web` — рабочий репозиторий (develop, `be3cd759d2`), перенесён без изменений.
- БД `12stz_staging` через MCP PhpStorm: read-only в PhpStorm, SQL-фильтр
  `~/.claude/hooks/sql_readonly_guard.py`; 21 опасный инструмент PhpStorm выключен, 22 запрещены в Claude.
- `new` перестроен (коммит `2332422`, запушен): `knowledge/` + `projects/returns-2.0/`
  (sources, as-is, requirements, reviews, archive).
- Применено, НЕ закоммичено (23 изменённых + новые файлы):
  - `AGENTS.md` — новая версия (доступы и запреты, структура проекта, knowledge, security-reviewer);
  - `CLAUDE.md`, `.claude/settings.json`, `.claude/agents/*` (тексты = `.opencode/agents/*`, сверено diff),
    `.claude/skills` — junction на `skill/` (в `.gitignore`);
  - пути в агентах и 8 скиллах (43 замены), `gap-analysis` и `handoff` включены в `opencode.json`;
  - `skill/handoff/SKILL.md`, `knowledge/README.md` (навигатор, 95 путей проверены);
  - 20 правок устаревших путей/цифр в `knowledge/` (OpenAPI → `docs/openapi/*.yml`, 208 миграций,
    64 модуля, строки в order-view).
- Пользовательские настройки `~/.claude/settings.json`: строка статуса (процент контекста),
  `workspace_guard.py` (12stz и sources только чтение, commit/push — подтверждение),
  `context_warn.py` (предупреждение при ≥ 90%). Проверено вживую: rm в 12stz и запись в sources заблокированы.

## Где остановились
Нужен коммит в `new` (и push — только по просьбе пользователя). Перед коммитом:
- добавить в `.gitignore`: `/.claude/settings.local.json` и `/.claude/scheduled_tasks.lock`;
- показать пользователю `git status` и краткий diff.

## Принятые решения
- Вариант структуры C (под несколько проектов), имена папок английские — пользователь, 09.10.2026.
- `gap-analysis` включён в обоих инструментах — пользователь, 09.10.2026.
- Настройки организации (синхронизированные плагины claude.ai) не трогать — пользователь, 09.10.2026.

## Открытые вопросы к пользователю
- 17 битых ссылок в `projects/returns-2.0/as-is/*` на ненаписанные карточки API
  (`reference/api/core/...`): писать их в `knowledge/12storeez-master-web/api/` или удалить ссылки?
- iOS: заменить копию `new/12storeez-ios-develop` клоном в `12stz` (после проверки пользователем).
- Права на запись в `12stz_sandbox`/`12stz_fix` у пользователя БД — оставить или попросить снять.

## Что прочитать новой сессии
- `AGENTS.md` — правила и структура; `CLAUDE.md`.
- `knowledge/README.md` — навигатор по коду.
- Проверить: строка статуса показывает «new · контекст: N%»; `/agents` — 5 агентов.

## Ограничения, о которых нельзя забыть
- `12stz` и БД — только чтение; `projects/*/sources/` — только чтение.
- commit и push в `new` — только по явной просьбе пользователя.
