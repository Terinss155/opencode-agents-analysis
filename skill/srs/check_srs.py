#!/usr/bin/env python3
"""check_srs.py — read-only проверка SRS (Markdown и Яндекс Вики) при точечной правке User Story.

Только читает файлы и печатает отчёт. Ничего не записывает, не исправляет, не вызывает сеть и git.

Проверки:
  US-01    границы US найдены однозначно (иначе файл не проверяется, код 2)
  EOL-01   смешанные переводы строк LF/CRLF в файле
  EOL-02   перевод строк или BOM изменились относительно исходного состояния
  KEEP-01  часть файла до или после US изменилась относительно исходного состояния
  KEEP-00  исходное состояние не передано — сохранность частей вне US не проверялась
  STEP-01  повтор номера шага внутри одной последовательности
  REF-01   однозначная ссылка на несуществующий шаг (ERROR) или неоднозначная (NEEDS_REVIEW)
  TBD-01   новый метод (заголовок «— новый метод» в «Логике бэкенда») без TBD:
           в заголовке, в записи метода в тексте, на стрелке sequence. TBD полей не проверяется
  MMD-03   ссылка «(шаг N)» внутри Mermaid
  PARSE-01 фрагмент не удалось надёжно разобрать — по нему проверка не выполнена

Исходное состояние: каждый запуск с --us печатает строку SRSSNAP1 … Её передают в следующий
запуск через --baseline (или --baseline - для чтения из stdin). Файлы состояния не создаются.

Пример:
  python -B skill/srs/check_srs.py --us 1.3 srs-mobile-mvp.md srs-web-mvp.md
  python -B skill/srs/check_srs.py --us 1.3 --baseline SRSSNAP1:… srs-mobile-mvp.md srs-web-mvp.md
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys

# Согласованные исключения. Формат: (имя файла, ID проверки, фрагмент текста, причина).
# В первой версии исключений для реализованных проверок нет.
EXCEPTIONS = []

LEVELS = ("ERROR", "WARNING", "NEEDS_REVIEW", "NOT_CHECKED", "INFO")
VERBS = r"(?:GET|POST|PUT|PATCH|DELETE)"

RE_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
RE_US_HEADING = re.compile(r"^.*\sUS\s+(\d+(?:\.\d+)*)$")
RE_SEQ = re.compile(r"^(Основная|Альтернативная)\s+последовательность\s+[\"«“](.+?)[\"»”]\s*$")
RE_FENCE = re.compile(r"^\s*```(\S*)")
RE_STEP_NUM = re.compile(r"^\d+(?:\.\d+)*$")
RE_WIKI_INLINE_ROW = re.compile(r"^\|\|\s*([0-9][0-9\\.]*)\s*\|")
RE_WIKI_BLOCK_NUM = re.compile(r"^[0-9]+(?:\\?\.[0-9]+)*$")
RE_REF = re.compile(
    r"(?<![\w])(шаг(?:а|у|е|ом|и|ов|ам|ами|ах)?)\s+(\d+(?:\.\d+)*)(?:\s*[–-]\s*(\d+(?:\.\d+)*))?",
    re.IGNORECASE,
)
RE_Q_MAIN = re.compile(r"^\s*основной\s+последовательности", re.IGNORECASE)
RE_Q_ALT = re.compile(r"^\s*альтернативной\s+последовательности\s+[\"«“]([^\"»”]+)[\"»”]", re.IGNORECASE)
RE_Q_US = re.compile(r"^\s*(?:основной\s+последовательности\s+)?\(?US\s+(\d+(?:\.\d+)*)")
RE_NEW_METHOD = re.compile(r"\*\*`" + VERBS + r"\s+[^`]*`\s*\((.*?)\)\s*—\s*новый метод\*\*")
RE_PATH_IN_PARENS = re.compile(r"`(" + VERBS + r")\s+(/[^`\s]*)`")
RE_MMD_STEP = re.compile(r"\(\s*шаг(?:и)?\s+\d", re.IGNORECASE)
TOKEN_PREFIX = "SRSSNAP1:"


class Finding:
    def __init__(self, level, code, path, line, us, place, msg):
        self.level, self.code, self.path, self.line = level, code, path, line
        self.us, self.place, self.msg = us, place, msg

    def as_dict(self):
        return {"level": self.level, "code": self.code, "file": self.path, "line": self.line,
                "us": self.us, "place": self.place, "message": self.msg}

    def as_text(self):
        loc = "%s:%s" % (os.path.basename(self.path), self.line) if self.line else os.path.basename(self.path)
        where = " · ".join(x for x in (("US " + self.us) if self.us else "", self.place) if x)
        return "%-12s %-8s %-28s %-40s %s" % (self.level, self.code, loc, where, self.msg)


class Doc:
    """Разбор одного файла: строки, ограждения кода, US, последовательности и шаги."""

    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            raw = f.read()
        self.bom = raw.startswith(b"\xef\xbb\xbf")
        self.text = raw.decode("utf-8-sig" if self.bom else "utf-8")  # UnicodeDecodeError → наверх
        crlf = raw.count(b"\r\n")
        lf_only = raw.count(b"\n") - crlf
        self.eol = "CRLF" if crlf and not lf_only else "LF" if lf_only and not crlf else "MIXED" if crlf else "NONE"
        self.eol_counts = (crlf, lf_only)
        self.lines_raw = self.text.split("\n")            # с '\r' на конце для CRLF
        self.lines = [l[:-1] if l.endswith("\r") else l for l in self.lines_raw]
        self.is_wiki = any(l.startswith("#|") for l in self.lines)
        self._mark_fences()
        self._find_us()

    def _mark_fences(self):
        # kind[i]: None — обычная строка, 'mermaid' — внутри mermaid, 'code' — внутри иного блока кода
        self.kind = [None] * len(self.lines)
        inside = None
        for i, l in enumerate(self.lines):
            m = RE_FENCE.match(l)
            if m:
                if inside is None:
                    inside = "mermaid" if m.group(1).lower() == "mermaid" else "code"
                    self.kind[i] = "fence"
                    continue
                self.kind[i] = "fence"
                inside = None
                continue
            self.kind[i] = inside

    def heading(self, i):
        if self.kind[i] is not None:
            return None
        m = RE_HEADING.match(self.lines[i])
        if not m:
            return None
        text = m.group(2)
        # Пользовательские пометки вики вида «# TODO …», «# ИЗМЕНЕНО …» заголовками не считаются
        if re.match(r"^(TODO|ИЗМЕНЕНО)\b", text):
            return None
        return len(m.group(1)), text

    def _find_us(self):
        self.us = []  # [(номер, start, end)] — строки [start, end)
        heads = []
        for i in range(len(self.lines)):
            h = self.heading(i)
            if h:
                heads.append((i, h[0], h[1]))
        starts = []
        for idx, (i, lvl, text) in enumerate(heads):
            m = RE_US_HEADING.match(text)
            if lvl == 3 and m:
                starts.append((idx, i, m.group(1)))
        for k, (idx, i, num) in enumerate(starts):
            end = len(self.lines)
            for j, lvl, text in heads[idx + 1:]:
                if lvl <= 2 or (lvl == 3 and RE_US_HEADING.match(text)):
                    end = j
                    break
            self.us.append((num, i, end))

    def us_ranges(self, num):
        return [(s, e) for n, s, e in self.us if n == num]

    def us_of_line(self, i):
        for n, s, e in self.us:
            if s <= i < e:
                return n
        return None

    def sequences(self, start, end):
        """Последовательности US: [{name, main, start, end, steps:{num:[line]}, table:(a,b) | None, parsed}]."""
        seqs = []
        cur = None
        for i in range(start, end):
            h = self.heading(i)
            if not h:
                continue
            lvl, text = h
            if cur is not None and lvl <= 4:
                cur["end"] = i
                seqs.append(cur)
                cur = None
            m = RE_SEQ.match(text) if lvl == 4 else None
            if m:
                cur = {"name": m.group(2), "main": m.group(1) == "Основная", "start": i, "end": end}
        if cur is not None:
            seqs.append(cur)
        for s in seqs:
            self._parse_steps(s)
        return seqs

    def _parse_steps(self, s):
        s["steps"], s["table"], s["parsed"] = {}, None, False
        rng = range(s["start"] + 1, s["end"])
        if self.is_wiki:
            a = next((i for i in rng if self.kind[i] is None and self.lines[i].startswith("#|")), None)
            if a is None:
                return
            b = next((i for i in range(a + 1, s["end"]) if self.lines[i].startswith("|#")), None)
            if b is None:
                return
            s["table"] = (a, b)
            body = range(a + 1, b)
            header_ok = any("**Шаг**" in self.lines[i] for i in body)
            prev = None
            for i in body:
                l = self.lines[i].strip()
                m = RE_WIKI_INLINE_ROW.match(l)
                if m:
                    s["steps"].setdefault(m.group(1).replace("\\", ""), []).append(i)
                elif RE_WIKI_BLOCK_NUM.match(l) and prev == "||":
                    s["steps"].setdefault(l.replace("\\", ""), []).append(i)
                if l:
                    prev = l
            s["parsed"] = header_ok and bool(s["steps"])
        else:
            a = next((i for i in rng if self.kind[i] is None and self.lines[i].lstrip().startswith("|")
                      and "Шаг" in self.lines[i]), None)
            if a is None:
                return
            b = a + 1
            while b < s["end"] and self.lines[b].lstrip().startswith("|"):
                b += 1
            s["table"] = (a, b)
            ok = True
            for i in range(a + 2, b):
                cells = self.lines[i].strip().strip("|").split("|")
                num = cells[0].strip() if cells else ""
                if RE_STEP_NUM.match(num):
                    s["steps"].setdefault(num, []).append(i)
                else:
                    ok = False
            s["parsed"] = ok and bool(s["steps"])


def snapshot_entry(doc, num):
    rng = doc.us_ranges(num)
    if len(rng) != 1:
        return None
    s, e = rng[0]
    pre = "\n".join(doc.lines_raw[:s])
    post = "\n".join(doc.lines_raw[e:])
    h = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()[:20]
    return {"eol": doc.eol, "bom": doc.bom, "pre": h(pre), "post": h(post),
            "pre_lines": s, "post_lines": len(doc.lines) - e}


def file_key(path):
    return os.path.normcase(os.path.abspath(path)).replace("\\", "/")


def check_doc(doc, num, out):
    """Проверки шагов, ссылок, TBD и Mermaid. num=None — весь документ."""
    P = doc.path
    in_scope = (lambda i: True) if num is None else (lambda i: doc.us_of_line(i) == num)
    us_seqs = {n: doc.sequences(s, e) for n, s, e in doc.us}

    # STEP-01 и PARSE-01
    for n, seqs in us_seqs.items():
        if num is not None and n != num:
            continue
        for s in seqs:
            if not s["parsed"]:
                out.append(Finding("NOT_CHECKED", "PARSE-01", P, s["start"] + 1, n, s["name"],
                                   "таблица шагов не распознана — шаги и ссылки последовательности не проверены"))
                continue
            for step, lines in s["steps"].items():
                if len(lines) > 1:
                    out.append(Finding("ERROR", "STEP-01", P, lines[1] + 1, n, s["name"],
                                       "номер шага %s повторяется (строки %s)" % (step, ", ".join(str(x + 1) for x in lines))))

    # REF-01: все US документа; выводятся ссылки в выбранной US и ссылки на неё из других US
    for n, us_s, us_e in doc.us:
        seqs = us_seqs[n]
        for i in range(us_s, us_e):
            if doc.kind[i] is not None:
                continue
            cur = next((s for s in seqs if s["table"] and s["table"][0] <= i < s["table"][1]), None)
            line = doc.lines[i].replace("\\.", ".")  # экранирование номеров в вики: 3\.1
            for m in RE_REF.finditer(line):
                a, b = m.group(2), m.group(3)
                tail = line[m.end():m.end() + 140]
                target_us, target_seq, qual = n, None, None
                mq = RE_Q_US.match(tail)
                if RE_Q_ALT.match(tail):
                    qual, target_seq = "alt", RE_Q_ALT.match(tail).group(1)
                elif mq:
                    qual, target_us = "us", mq.group(1)
                elif RE_Q_MAIN.match(tail):
                    qual = "main"
                if num is not None and n != num and target_us != num:
                    continue
                place = (cur["name"] if cur else "текст US")
                ref_txt = m.group(0).strip()
                res = resolve_ref(us_seqs, target_us, target_seq, qual, cur, [a] + ([b] if b else []))
                if res is None:
                    continue
                lvl, why = res
                out.append(Finding(lvl, "REF-01", P, i + 1, n, place, "«%s»: %s" % (ref_txt, why)))

    # TBD-01: реестр новых методов по всему документу
    new_paths = {}
    for i, l in enumerate(doc.lines):
        if doc.kind[i] is not None:
            continue
        for m in RE_NEW_METHOD.finditer(l):
            inner = m.group(1)
            pm = RE_PATH_IN_PARENS.search(inner)
            has_tbd = re.search(r"\bTBD\b", inner) is not None
            if pm:
                new_paths[(pm.group(1), pm.group(2))] = i
            if not has_tbd and in_scope(i):
                out.append(Finding("ERROR", "TBD-01", P, i + 1, doc.us_of_line(i), "Логика бэкенда",
                                   "новый метод без TBD в заголовке: %s" % (pm.group(0) if pm else inner)))
    for i, l in enumerate(doc.lines):
        if not in_scope(i):
            continue
        if doc.kind[i] == "mermaid":
            if "->>" in l or "-)" in l:
                label = l.split(":", 1)[1] if ":" in l else ""
                for (verb, path) in new_paths:
                    mm = re.search(r"(?<![\w/])" + verb + r"\s+" + re.escape(path) + r"(?=$|[\s(])", label)
                    if mm and "(TBD)" not in label[mm.end():]:
                        out.append(Finding("ERROR", "TBD-01", P, i + 1, doc.us_of_line(i), "Mermaid",
                                           "новый метод на стрелке без (TBD): %s %s" % (verb, path)))
            continue
        if doc.kind[i] is not None or RE_NEW_METHOD.search(l):
            continue
        for pm in RE_PATH_IN_PARENS.finditer(l):
            key = (pm.group(1), pm.group(2))
            if key not in new_paths:
                continue
            after = l[pm.end():]
            if re.match(r"^\s*,\s*TBD\s*\)", after):
                continue
            if re.match(r"^\s*\)", after):
                out.append(Finding("ERROR", "TBD-01", P, i + 1, doc.us_of_line(i), "текст US",
                                   "новый метод без TBD: %s %s" % key))

    # MMD-03
    for i, l in enumerate(doc.lines):
        if doc.kind[i] == "mermaid" and in_scope(i) and RE_MMD_STEP.search(l):
            out.append(Finding("ERROR", "MMD-03", P, i + 1, doc.us_of_line(i), "Mermaid",
                               "ссылка на номер шага: «%s…»" % RE_MMD_STEP.search(l).group(0).strip()))


def resolve_ref(us_seqs, target_us, target_seq, qual, cur, nums):
    """Возвращает (уровень, причина) или None, если ссылка корректна или не оценивается."""
    seqs = us_seqs.get(target_us)
    if seqs is None:
        return ("NEEDS_REVIEW", "US %s нет в этом файле" % target_us)
    if qual == "alt":
        cand = [s for s in seqs if not s["main"] and s["name"] == target_seq]
        if not cand:
            return ("NEEDS_REVIEW", "последовательность «%s» не найдена по точному названию" % target_seq)
        seq = cand[0]
    elif qual in ("main", "us"):
        cand = [s for s in seqs if s["main"]]
        if not cand:
            return ("NEEDS_REVIEW", "основная последовательность US %s не найдена" % target_us)
        seq = cand[0]
    else:
        seq = cur
    if seq is not None:
        if not seq["parsed"]:
            return None  # уже отмечено PARSE-01
        missing = [x for x in nums if x not in seq["steps"]]
        if not missing:
            return None
        if qual is None:
            others = [s["name"] for s in seqs if s is not seq and s["parsed"] and all(x in s["steps"] for x in missing)]
            if others:
                return ("NEEDS_REVIEW", "шага %s нет в текущей последовательности, есть в «%s»" % (", ".join(missing), others[0]))
            if any(not s["parsed"] for s in seqs):
                return ("NEEDS_REVIEW", "шага %s нет; часть последовательностей US не разобрана" % ", ".join(missing))
        return ("ERROR", "шага %s нет в последовательности «%s»" % (", ".join(missing), seq["name"]))
    # Ссылка без уточнения вне таблицы шагов
    if any(not s["parsed"] for s in seqs):
        return None
    exists = any(all(x in s["steps"] for x in nums) for s in seqs)
    if exists:
        return None
    return ("NEEDS_REVIEW", "последовательность не указана, такого шага нет ни в одной последовательности US")


def apply_exceptions(doc, findings):
    kept = []
    for f in findings:
        exc = next((e for e in EXCEPTIONS if e[0] == os.path.basename(f.path) and e[1] == f.code
                    and f.line and e[2] in doc.lines[f.line - 1]), None)
        if exc:
            kept.append(Finding("INFO", f.code, f.path, f.line, f.us, f.place, "исключение: " + exc[3]))
        else:
            kept.append(f)
    return kept


def decode_token(token):
    if token == "-":
        token = sys.stdin.read().strip()
    token = token.strip()
    if not token.startswith(TOKEN_PREFIX):
        raise ValueError("строка исходного состояния должна начинаться с " + TOKEN_PREFIX)
    return json.loads(base64.b64decode(token[len(TOKEN_PREFIX):]).decode("utf-8"))


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # консоль Windows: вывод в UTF-8, иначе русский текст искажается
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Read-only проверка SRS при точечной правке US. Ничего не изменяет.")
    ap.add_argument("files", nargs="+", help="SRS и вики-копии (Markdown или разметка Яндекс Вики)")
    ap.add_argument("--us", help="номер US, например 1.3. Без него — проверка всего документа без контроля сохранности")
    ap.add_argument("--baseline", help="строка SRSSNAP1:… из предыдущего запуска или '-' для чтения из stdin")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--max-per-code", type=int, default=20, help="сколько сообщений одного кода показывать в тексте")
    args = ap.parse_args(argv)

    findings, snap, summary, fatal = [], {"us": args.us, "files": {}}, [], False
    baseline = None
    if args.baseline:
        if not args.us:
            print("--baseline требует --us", file=sys.stderr)
            return 2
        try:
            baseline = decode_token(args.baseline)
        except Exception as e:  # noqa: BLE001
            print("Не удалось прочитать исходное состояние: %s" % e, file=sys.stderr)
            return 2
        if baseline.get("us") != args.us:
            print("Исходное состояние снято для US %s, а проверяется US %s" % (baseline.get("us"), args.us), file=sys.stderr)
            return 2

    for path in args.files:
        try:
            doc = Doc(path)
        except (OSError, UnicodeDecodeError) as e:
            findings.append(Finding("NOT_CHECKED", "PARSE-02", path, 0, None, "", "файл не прочитан: %s" % e))
            fatal = True
            continue
        out = []
        crlf, lf = doc.eol_counts
        if doc.eol == "MIXED":
            out.append(Finding("WARNING", "EOL-01", path, 0, None, "", "смешанные переводы строк: CRLF %d, LF %d" % (crlf, lf)))
        scope_txt = "весь документ"
        if args.us:
            rng = doc.us_ranges(args.us)
            if len(rng) != 1:
                out.append(Finding("NOT_CHECKED", "US-01", path, 0, args.us, "",
                                   "US %s %s — файл не проверен" % (args.us, "не найдена" if not rng else "найдена %d раз" % len(rng))))
                fatal = True
                findings.extend(out)
                summary.append("%s: %s, US %s не определена" % (os.path.basename(path), doc.eol, args.us))
                continue
            s, e = rng[0]
            scope_txt = "US %s (строки %d–%d) и ссылки на неё из других US" % (args.us, s + 1, e)
            entry = snapshot_entry(doc, args.us)
            snap["files"][file_key(path)] = entry
            if baseline is not None:
                old = baseline.get("files", {}).get(file_key(path))
                if old is None:
                    out.append(Finding("NOT_CHECKED", "KEEP-01", path, 0, args.us, "",
                                       "файла нет в исходном состоянии — сохранность частей вне US не проверена"))
                else:
                    if old["eol"] != entry["eol"] or old["bom"] != entry["bom"]:
                        out.append(Finding("ERROR", "EOL-02", path, 0, None, "",
                                           "переводы строк/BOM изменились: было %s%s, стало %s%s" % (
                                               old["eol"], " BOM" if old["bom"] else "", entry["eol"], " BOM" if entry["bom"] else "")))
                    if old["pre"] != entry["pre"]:
                        out.append(Finding("ERROR", "KEEP-01", path, s + 1, args.us, "до US",
                                           "часть файла до US изменилась (было строк %d, стало %d)" % (old["pre_lines"], entry["pre_lines"])))
                    if old["post"] != entry["post"]:
                        out.append(Finding("ERROR", "KEEP-01", path, e + 1, args.us, "после US",
                                           "часть файла после US изменилась (было строк %d, стало %d)" % (old["post_lines"], entry["post_lines"])))
            else:
                out.append(Finding("INFO", "KEEP-00", path, 0, args.us, "",
                                   "исходное состояние не передано — сохранность частей вне US не проверялась"))
        check_doc(doc, args.us, out)
        out = apply_exceptions(doc, out)
        findings.extend(out)
        not_checked = sum(1 for f in out if f.level == "NOT_CHECKED")
        summary.append("%s: %s%s, %s, %s; не проверено фрагментов: %d" % (
            os.path.basename(path), doc.eol, " BOM" if doc.bom else "",
            "вики" if doc.is_wiki else "Markdown", scope_txt, not_checked))

    counts = {lv: sum(1 for f in findings if f.level == lv) for lv in LEVELS}
    token = TOKEN_PREFIX + base64.b64encode(json.dumps(snap, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).decode("ascii") if args.us and snap["files"] else None
    full = not args.us

    if args.format == "json":
        print(json.dumps({"scope": {"us": args.us,
                                    "full_document_checked": full and not fatal and counts["NOT_CHECKED"] == 0,
                                    "baseline_used": baseline is not None},
                          "files": summary, "counts": counts,
                          "findings": [f.as_dict() for f in findings], "snapshot": token},
                         ensure_ascii=False, indent=1))
    else:
        print("Область: " + ("весь документ" if full else "US %s — это НЕ полная проверка SRS" % args.us))
        for s in summary:
            print("  " + s)
        shown = {}
        for f in findings:
            shown[f.code] = shown.get(f.code, 0) + 1
            if shown[f.code] <= args.max_per_code:
                print(f.as_text())
        hidden = {c: n - args.max_per_code for c, n in shown.items() if n > args.max_per_code}
        for c, n in hidden.items():
            print("… %s: ещё %d сообщений (увеличьте --max-per-code)" % (c, n))
        print("Итог: " + " · ".join("%s %d" % (lv, counts[lv]) for lv in LEVELS))
        if token:
            print("Исходное состояние для следующего запуска (--baseline):")
            print(token)
    if fatal:
        return 2
    return 1 if counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
