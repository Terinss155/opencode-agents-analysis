# Архив скиллов про эндпоинты — 17.11.2026

**Не действующие правила.** Содержимое перенесено при реструктуризации скиллов по варианту А+ (`Анализ_скиллов_эндпоинты.md` в этой папке, часть 2). Архив — для сверки и истории; при расхождении верны действующие скиллы.

| Что в архиве | Было | Куда перенесено |
|---|---|---|
| `tracker-task-references/request-response_web.md` | `skill/tracker-task/references/` (ранее `backend-task/references/`) | `skill/openapi-spec/references/web.md` |
| `tracker-task-references/request-response_mobile-api.md` | то же | `skill/openapi-spec/references/mobile.md` |
| `tracker-task-references/api-errors_memo.md` | то же | `skill/openapi-spec/references/errors.md` |
| `tracker-task-references/field-glossary.md` | то же | `skill/openapi-spec/references/field-glossary.md` (без изменений по смыслу) |
| `web-endpoint/SKILL.md` | `skill/web-endpoint/` | §1–2.5 → `openapi-spec/references/web.md`; §2.6 → `errors.md`; §2.7 → `web.md` §8а; §3 → `swagger.md`; §4 → чек-лист `openapi-spec/SKILL.md` §5 |
| `mobile-endpoint/SKILL.md` | `skill/mobile-endpoint/` | §1–2 → `openapi-spec/references/mobile.md`; §2.7 → `errors.md`; §3 → `swagger.md`; §4 → чек-лист `openapi-spec/SKILL.md` §5 |

Перенесены отдельно, в архиве их нет:
- шаблоны `web-endpoint/template.md` и `mobile-endpoint/template.md` (шаблон А) → `skill/tracker-task/templates/new-web.md` и `new-mobile.md`, переработаны; шаблон Б (гейт) заменён на `templates/gate-proxy.md`;
- примеры swagger → `skill/openapi-spec/examples/`.

Изменения смысла при переносе — намеренные, с основанием:
- решения по противоречиям — `Анализ_скиллов_эндпоинты.md`, часть 2, §6.1 «Проверка по коду»;
- уточнения по коду — там же, таблица «Уточнения по коду, внесённые при переносе»;
- независимая сверка переноса — там же.
