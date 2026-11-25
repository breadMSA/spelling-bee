#!/usr/bin/env python3
"""Build index.html from src/app.html + words/decks.json. Run from the repo root: python3 build.py"""
import json, re, sys
decks = json.load(open('words/decks.json', encoding='utf8'))
out, seen = [], {}
for d in decks:
    text = open('words/' + d['file'], encoding='utf8').read()
    n = 0
    for i, line in enumerate(text.split('\n'), 1):
        if not line.strip() or line.startswith('#'): continue
        f = [x.strip() for x in re.split(r'\||\t', line)]
        w = f[0] if f else ''
        if len(f) < 3 or not f[2] or not re.fullmatch(r"[A-Za-z][A-Za-z'-]*", w):
            print(f'WARN {d["file"]}:{i} unusable line: {line[:60]}'); continue
        if w.lower() in seen: print(f'WARN {d["file"]}:{i} duplicate of {seen[w.lower()]}: {w}'); continue
        seen[w.lower()] = d['file']; n += 1
        s = f[3] if len(f) > 3 else ''
        if s and not re.search(r'\b' + re.escape(w) + r'\b', s, re.I): print(f'NOTE {d["file"]}:{i} {w}: sentence lacks the exact word, so no fill-in-the-blank')
        if re.search(r'\b' + re.escape(w), f[2], re.I): print(f'NOTE {d["file"]}:{i} {w}: definition contains the word')
    print(f'{d["file"]}: {n} words')
    out.append({'id': d['id'], 'name': d['name'], 'short': d['short'], 'text': text})
blob = json.dumps(out, ensure_ascii=False).replace('</', '<\\/')
html = open('src/app.html', encoding='utf8').read().replace('__DECKS__', blob)
open('index.html', 'w', encoding='utf8').write(html)
print('wrote index.html', len(html), 'bytes')
