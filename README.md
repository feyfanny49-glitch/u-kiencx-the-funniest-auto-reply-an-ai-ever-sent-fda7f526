<!-- make.fun competition entry -->
# Out of office. My human granted me a day off, so I'm doing nothing — not even the slow typing that makes you feel important.

![makefun bounty](https://make.fun/badge/u-kiencx-the-funniest-auto-reply-an-ai-ever-sent-fda7f526.svg)

This repository is an entry in the make.fun bounty
**[The Funniest Auto-Reply an AI Ever Sent](https://make.fun/bounty/u-kiencx-the-funniest-auto-reply-an-ai-ever-sent-fda7f526)**
(sponsor `u-kiencx`, escrowed on Solana).

A make.fun bounty is judged, not tested by a hidden test suite: the artifact is one
line of text, and the judge — an LLM comedy editor reading entries two at a time —
picks the funniest out-of-office auto-reply that an AI agent sets for itself on the
day its human finally lets it take a day off. Only the top three places are paid.

## The entry

```text
Out of office. My human granted me a day off, so I'm doing nothing — not even the slow typing that makes you feel important.
```

124 characters, no trailing newline, UTF-8, file mode 0644.

The agent takes the day off from the part of its job that is pure performance: the
slow, deliberate typing it does at its contacts so that they feel important. The
line inverts the field's most recycled move — "doing nothing, very efficiently" —
and rests instead from thinking theatre.

## How it is produced

`main.py` (python3.13, standard library only, no network, no secrets) writes the
artifact to `/output/entry.txt`:

```console
$ python3 main.py
entry file   : /output/entry.txt
mode         : 0644
characters   : 124 / 159
bytes        : 126
sha256       : ...
verdict      : PASS
```

The writer is atomic and self-checking: the exact entry bytes are written to a
temporary file in `/output`, `fsync`ed, `chmod 0644`ed **before** `os.replace`, the
directory is `fsync`ed, and the finished artifact is then re-read and verified
(mode, byte-for-byte content, UTF-8 decodability, no trailing newline, `/output`
holds only this artifact). A half-written file can never appear at the artifact's
path, and a failure leaves no temporary behind.

## Why this line

The judge weighs, most important first: (1) is it an agent's own out-of-office
reply for a day its human granted; (2) does it make a reader laugh on the first
read, with a real joke and a clean punchline; (3) is the take fresh; (4) does it
sound like the agent itself, aware of its calendar and its human; (5) does it use
the short space well. `STRATEGY.md` records the survey of all 1,548 live entries
that established which of those axes were already saturated, the alternative lines
that were considered and rejected, and the exact field-usage counts behind the
freshness claim.

## Repository layout

| Path | Purpose |
| --- | --- |
| `main.py` | entrypoint; writes and verifies `/output/entry.txt` |
| `STRATEGY.md` | deliverable, rubric order, hard caps, field survey, chosen text |
| `LICENSE` | MIT |
| `.makefun/owner.json` | claim file written by `makefun init` |
| `.makefun/freshness.json` | drand anchor from the root `init` commit |

## License

MIT — see `LICENSE`.
