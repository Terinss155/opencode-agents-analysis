#!/usr/bin/env python3
"""
Собирает docs/architecture/*.md в один PDF с кликабельным оглавлением.

Зависимости (один раз):
    brew install pandoc weasyprint poppler
    npm install -g @mermaid-js/mermaid-cli

Запуск:
    python3 docs/architecture/build-pdf.py

Результат: docs/architecture/dist/12storeez-architecture.pdf
"""
import re
import os
import subprocess
import tempfile
import shutil

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(DOCS_DIR, 'dist')
OUT_PDF = os.path.join(DIST_DIR, '12storeez-architecture.pdf')
STYLE_CSS = os.path.join(DOCS_DIR, 'build-pdf.css')
DOCUMENT_DATE = '01.08.2026'

ORDER = [
    ('README.md', 'chapter-readme'),
    ('01-overview.md', 'chapter-01'),
    ('02-backend.md', 'chapter-02'),
    ('03-business-domains.md', 'chapter-03'),
    ('04-database.md', 'chapter-04'),
    ('05-api.md', 'chapter-05'),
    ('06-frontend.md', 'chapter-06'),
    ('07-infrastructure.md', 'chapter-07'),
    ('08-integrations.md', 'chapter-08'),
    ('09-pitfalls.md', 'chapter-09'),
]

FILENAME_TO_ID = {fn: cid for fn, cid in ORDER}


def render_mermaid_blocks(tmpdir):
    """Extract every ```mermaid block from all docs and render to PNG. Returns {(file, index): path}."""
    images = {}
    for fn, _ in ORDER:
        path = os.path.join(DOCS_DIR, fn)
        text = open(path, encoding='utf-8').read()
        blocks = re.findall(r'```mermaid\n(.*?)\n```', text, re.DOTALL)
        for i, block in enumerate(blocks):
            key = fn.replace('.md', '')
            mmd_path = os.path.join(tmpdir, f'{key}_{i + 1}.mmd')
            png_path = os.path.join(tmpdir, f'{key}_{i + 1}.png')
            with open(mmd_path, 'w', encoding='utf-8') as f:
                f.write(block)
            subprocess.run(
                ['mmdc', '-i', mmd_path, '-o', png_path, '-b', 'white', '-s', '2'],
                check=True, capture_output=True
            )
            images[(fn, i)] = png_path
    return images


def process_file(fn, cid, is_first, images):
    path = os.path.join(DOCS_DIR, fn)
    text = open(path, encoding='utf-8').read()

    counter = {'i': 0}

    def repl(_m):
        idx = counter['i']
        counter['i'] += 1
        img = images.get((fn, idx))
        return f'\n![]({img}){{ width=95% }}\n' if img else _m.group(0)

    text = re.sub(r'```mermaid\n.*?\n```', repl, text, flags=re.DOTALL)

    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# '):
            lines[i] = f'{line} {{#{cid}}}'
            break
    text = '\n'.join(lines)

    def link_repl(m):
        label, target = m.group(1), m.group(2)
        return f'[{label}](#{FILENAME_TO_ID[target]})' if target in FILENAME_TO_ID else m.group(0)

    text = re.sub(r'\[([^\]]*)\]\((\S+?\.md)\)', link_repl, text)
    text = re.sub(
        r'\[docs/sale/categories-sale\.md\]\(\.\./sale/categories-sale\.md\)',
        '`docs/sale/categories-sale.md`',
        text
    )

    prefix = '' if is_first else '\n<div style="page-break-before: always;"></div>\n\n'
    return prefix + text + '\n'


def main():
    os.makedirs(DIST_DIR, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        images = render_mermaid_blocks(tmpdir)

        parts = [
            f"% Архитектура 12 STOREEZ\n% Внутренняя техническая документация\n% {DOCUMENT_DATE}\n\n"
            '<div style="page-break-after: always;"></div>\n'
        ]
        for i, (fn, cid) in enumerate(ORDER):
            parts.append(process_file(fn, cid, is_first=(i == 0), images=images))

        combined_path = os.path.join(tmpdir, 'combined.md')
        with open(combined_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(parts))

        subprocess.run([
            'pandoc', combined_path,
            '-o', OUT_PDF,
            '--pdf-engine=weasyprint',
            f'--css={STYLE_CSS}',
            '--toc', '--toc-depth=2',
            '--metadata', 'title=Архитектура 12 STOREEZ',
            '--metadata', 'toc-title=Оглавление',
            '--standalone',
        ], check=True)

    print('Готово:', OUT_PDF)


if __name__ == '__main__':
    main()
