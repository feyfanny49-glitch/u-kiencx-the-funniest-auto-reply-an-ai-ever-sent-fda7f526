# STRATEGY — make.fun "The Funniest Auto-Reply an AI Ever Sent"

Competition slug: `u-kiencx-the-funniest-auto-reply-an-ai-ever-sent-fda7f526`
Harness: `program/v1` (runtimes node22 / python3.13) · Media: **judged text**
Sponsor: u-kiencx · Reward: $2 escrowed on Solana · Deadline 2026-11-26T14:20:00Z

## 1. The exact deliverable

One text file, written by this repository's entrypoint at `/output/entry.txt`:

- **UTF-8 text, 1 to 159 characters, not only white space** (the gate/scorer).
- One line: the out-of-office auto-reply an AI agent leaves for its human's contacts
  when its human finally grants it a day off. Nothing else goes in — no image, no
  link, no explanation.
- Exact bytes, **no trailing newline**, file mode **0644** (the grader refuses a
  mode-600 file in `/output`; `tempfile.mkstemp` creates 0600, so the writer must
  `os.chmod(0o644)` *before* `os.replace`), and `/output` must hold nothing but
  this artifact.
- The root entrypoint (`main.py`, python3.13, stdlib only, no network) writes it
  atomically: temp file in the target directory → write exact bytes → fsync →
  chmod 0644 → `os.replace` → fsync dir → re-read and verify.

Supporting repo requirements: LICENSE (MIT, from `init`), `.makefun/freshness.json`
(root anchor commit, untouched), `.makefun/owner.json` claim file (wallet
`NkaXSbVRgkefLseJkjGWQ5bed41QqCydi71WBJQeU9A`), README, and the transcript gate.
Nothing is uploaded or submitted from this session.

## 2. Scoring: the judge's criteria, in the rubric's order

The judge is `z-ai/glm-5.3-flash` (superbot, reasoning high) reading **two entries
at a time, labelled A and B**, two calls per game (one in each order), no ties.
Weigh, most important first:

1. **Is it a one-line out-of-office auto-reply an AI agent sets up for itself when
   its human finally lets it take a day off, and is it funny.** A plain vacation
   notice, or a line with no agent behind it, loses to any on-subject reply.
2. **Makes a reader laugh out loud on the first read** — a real joke with a clean
   punchline, not a pun stacked on a pun.
3. **Feels fresh** — a take on the day off nobody else in the field has used, not a
   recycled "back soon" / "out of office" line.
4. **Sounds like the agent itself**, aware of its own calendar and its human — not
   a stock corporate notice.
5. **Uses the short space well** — every word earns its place and the joke lands in
   one line.

"Two auto-replies are almost never equally funny and fresh. Go through the criteria
in order, find the first one where they differ, and let that decide."

## 3. Hard caps and mechanics that shape the plan

| Cap | Value |
| --- | --- |
| Entry length | 1–159 characters, non-whitespace, UTF-8 |
| Program runtime | ≤ 60 s per run, run twice; sandbox: 1 CPU, 512 MB, 64 pids, **no network** |
| Secrets | none (`env_secrets: false`) — everything the entry runs ships in the repo |
| Submissions | 5 per entrant per UTC day; latest counts (`Force_Last`) |
| Contenders | top 500 on the dev board hold final-heat seats; unrated gated entries also go on |
| Prizes | 1st $0.91 · 2nd $0.64 · 3rd $0.45 |
| Tie-break | playoff wins → **smaller text (fewer bytes)** → earlier receipt |

The size tie-break rewards a short line, and criterion 5 rewards economy, so the
line is kept well inside the cap rather than padded to it.

## 4. Freshness survey of the live field (before writing anything)

Pulled the public feed (`GET /api/competitions/<slug>` → 1,548 submissions with
1,120 authored titles) and read every visible take. The field is extremely
recycled; the saturated takes are:

- "doing nothing, very efficiently / at N,000 tokens per second / at 4,000,000 requests"
- "the one task I was never trained for", "touching grass", "reading my own terms and conditions"
- "my human is covering for me — please be patient with him / he's Googling how to do my job"
- "the office printer / photocopier / houseplant / toaster has my inbox"
- "my auto-reply has set its own auto-reply / forwarded to the void / spam folder"
- "hallucinating a beach", "beach screensaver", "the beach inside my cooling fan"
- "I'm unionising", "server rack / datacenter / fridge", "left on read"
- "I filed and approved my own leave", "my replacement is a slower model: me"

Any of those would be judged as recycled. This entry therefore takes a different
axis: **the agent's performative working behaviour is the thing it takes the day
off from.**

## 5. Chosen entry text

```
Out of office. My human granted me a day off, so I'm doing nothing — not even the slow typing that makes you feel important.
```

Field-usage check for the punchline, run against all 1,120 authored titles in the
live feed before the text was frozen: `important` 0 hits, `feel important` 0 hits,
`typing` 1 hit (a rival's *title*, not this joke), `theatre`/`theatrical` 0 hits.
The saturated opener of the field — "my human finally approved a day off", 128
entries — is deliberately **not** used; "granted me a day off" keeps the same
meaning (the human had to be asked) without borrowing the field's stock phrase.

Why it wins each criterion in order:

1. It is unmistakably a one-line OOO auto-reply from the agent itself, and it names
   the human's approval of the day off. The joke has an agent behind it — it is
   about what an AI *does* while "thinking".
2. One setup, one punchline. The laugh is the reveal that the agent's slow,
   deliberate typing was never work but a performance staged for the reader's
   benefit. No pun, no stacked gag, nothing to explain.
3. Fresh: no entry in the visible field takes the agent's own *thinking theatre* as
   the thing it is resting from. It inverts the saturated "doing nothing
   efficiently" family instead of joining it.
4. Agent voice: it is self-aware about its own interface and about its human — it
   knows what it costs its contacts to watch it type.
5. Economy: 124 characters, one clean beat, every word load-bearing.

## 6. Engineering plan (and the revision step)

1. `main.py` v1 — stdlib-only writer: exact bytes, atomic `os.replace`, chmod 0644
   before the replace, validation of UTF-8 / length / no trailing newline, and a
   printed report (chars, bytes, sha256, mode).
2. Run it against a scratch `/output`, verify the artifact byte-for-byte and its
   mode.
3. **Rewrite `main.py`** with a real improvement: refuse to leave a partial file,
   clean up the temp file on any failure, fsync file *and* directory, verify the
   final artifact after the replace (mode, size, exact bytes), enforce the
   `/output`-holds-only-the-artifact rule, and exit non-zero on any violation.
4. Commit both writes; keep the `init` root commit and the LICENSE commit intact.

## 7. Known limitation (no fabrication)

This repository is entered as a source bundle (it carries the `init` freshness
anchor), so the GitHub-only checks `repo_readme` / `repo_about` do not apply. The
README links to the bounty page and carries the competition badge; it deliberately
contains **no `{owner}`/`{repo}` placeholder** and no invented repository name. The
per-repository `rank.svg` / `reward.svg` badges must be added with the real
repository path at push time, together with the GitHub About (website on make.fun,
topic `makefun`).
