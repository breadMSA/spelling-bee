# Handoff: 世新 spelling bee practice app

Read this first if you are an AI (or a person) picking this project up.

Live site: https://breadMSA.github.io/spelling-bee/ (GitHub Pages, branch `main`, root folder).
Owner: breadMSA, a 世新大學 student. Talk to them in Traditional Chinese. They dislike generic "AI-looking" design and
want requests followed exactly as worded (placement, names), not reinterpreted.

## The one job you will probably be asked to do: load the new official word list

Each year the school publishes a list of 250 words (a photo of a printed table: word, part of speech, definition,
example sentence, a picture for many nouns). The user will send you those photos. Put the words in
`words/official-2027.txt` (rename the file and the entry in `words/decks.json` if the year differs). That deck is
already wired up: it is listed first, it appears automatically in the list/quiz/practice pickers as soon as the file
has words, and it needs **no login** (the whole page is static; progress is stored on the device).

Steps:

1. Transcribe every row, in order, one per line: `word|pos|definition|example sentence`
   - `pos` is `n`, `v`, `adj`, `adv` (as printed). Copy definitions and sentences as printed. Skip the pictures.
   - The first lines of the file start with `#`; they are comments. Keep them, delete only the "Nothing below" line.
   - Do not use `|` inside any field.
2. Proofread against the photos (ask the user to spot check some rows). Note: `words/base-2026.txt` was transcribed from
   photos last year and only its count (250) and format were verified, not every letter. If the user reports a wrong
   word or definition there, fix the line.
3. Run `python3 build.py` from the repo root. It rewrites `index.html` and prints:
   - `WARN` lines: unusable line (needs word|pos|definition) or a word already in another deck (the first deck in
     `decks.json` wins, so the official list wins over older decks).
   - `NOTE` lines: the sentence lacks the exact word (that word then only gets definition questions, no fill-in-the-blank)
     or the definition contains the word.
4. Read the near-synonym cases. Two words with interchangeable definitions (last year: weird / bizarre / unnatural /
   abnormal) make a definition question unfair. Add such groups to `CLUSTERS` in `src/app.html`; those words show a
   first-letter + length hint. The user may toggle that hint in 練習 > 題目選項 > 字母提示.
5. Accepted alternate spellings (British variants) live in the `ALT` map in `src/app.html`. Add any the list needs.
   Words that contain capitals (Armageddon, February) are graded case-sensitively; everything else ignores case,
   spaces and stray symbols.
6. Bump `VERSION` in `src/app.html` (a date string), rebuild, test (below), then commit `index.html`, `src/`, `words/`
   and push to `main`. Pages redeploys in about a minute. The service worker is network-first, so people get the new
   version after reopening the app once or twice.

## Contest format (so you can describe it correctly)

初賽 (written): 25 words drawn from the 250, 4 points each. 決賽 (oral): words from outside the list, out after two
mistakes. The quiz draws 25 words uniformly at random (`crypto.getRandomValues`, rejection sampling, partial
Fisher-Yates in `rnd` / `sample`). Do not replace that with `Math.random`.

## Layout

```
index.html          BUILT file served by Pages. Never edit by hand; run build.py.
src/app.html        the whole app (HTML + CSS + JS in one file) with a __DECKS__ placeholder
words/decks.json    deck list: id, display name, short name, file. Order = priority and display order
words/*.txt         one file per deck, format above
build.py            checks the word files and embeds them into index.html
sw.js, manifest.webmanifest, icon-*.png, apple-touch-icon.png    PWA (install on phone, works offline)
```

Question types: `def` (definition with the word masked, spell it on a four-line staff input) and `cloze` (example
sentence with a blank). No dictation, no fill-in-the-middle (the user ruled both out). A speaker button plays the
word only (Web Speech API) and is available on every question, before and after answering, because the real contest
reads the word, the example sentence and the definition aloud and the user spells best by ear.

Progress, keyed by the word string: `weak` (wrong-word list, removed after 2 first-try-correct in a row), `prog`
(per-word ok/miss counts; "known" = 2+ correct and not weak), `hist` (last 200 sessions), `rm` (deletion tombstones for
sync). Everything is in `localStorage`.

## Weekly extra decks

The user also wants about 250 new words a week for real vocabulary learning (not exam cramming): from intermediate
to hard, a mix, not only rare words. Add `words/weekly-NN.txt` plus an entry at the end of `words/decks.json`.
English definitions and example sentences only (no Chinese; they said so). Write original definitions and concrete,
easy-to-picture sentences (the user remembers by images). Check duplicates against every other deck: `build.py` warns.

## Weekly routine (home screen card)

The user picks a start date (day 1 of week 1); everything else is computed from today's date (`todayPlan()` in
`src/app.html`). Week N uses the N-th weekly deck: decks whose id matches `w` + digits (`w01`, `w02`, ...), in the
order they appear in `words/decks.json`. A week with no deck yet shows "new words not added yet"; add the next
`words/weekly-NN.txt` and a `decks.json` entry (id `wNN`) when asked ("出下一週").
Day 1 learn the new batch (and first sweep last week's), day 2 retest the batch (most important: forgetting is steepest
in the first 24 h), day 4 wrong-word quick test, day 5 mixed review of older decks from week 3 on, other days free.
Only the start date is stored (`prefs.start`, device-local, not synced); "done" ticks are in localStorage key `rt`.

## Login and sync (optional, for the user's own devices)

Not needed to use the app. Accounts are username + password, but a static site cannot write to a repo, so:
- The user creates a fine-grained GitHub token limited to this repo (Contents: read and write).
- On sign-up the app encrypts that token with the password (PBKDF2 200k + AES-GCM) and stores the result in
  `vault/<user>.json` on the branch **`data`**; progress goes to `data/<user>.json` on the same branch. Other devices
  log in with username + password only: they fetch the vault, decrypt the token, then sync.
- Merge rules are in `merge()` in `src/app.html` (newest wrong-word entry wins, tombstones for removals, max for counters,
  union for history).
- The `data` branch must keep existing. Never commit a token. Everything on `data` is public (the repo is public; the user
  accepted that).
- Only tested against a mocked GitHub API, plus real GitHub's documented behavior. If sync misbehaves in real use, check the
  browser console and the `data` branch first.

## Testing

`python3 build.py && python3 -m http.server 8765`, open `http://localhost:8765/#play`. Check: a quiz of 25 draws, grading
accepts case and stray symbols, practice re-queues wrong words, the deck pickers list every non-empty deck, the home
map counts add up to the total number of words. Test at phone width (390 px) too: the action bar must stay above the
on-screen keyboard.
