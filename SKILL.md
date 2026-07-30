---
name: mdc
description: Copy paste-ready GitHub-flavored Markdown to the macOS clipboard with pbcopy. Use when the user wants any content — composed (summary, MR description, review note), an existing file, or a passage from this conversation — on their clipboard to paste elsewhere (Slack, GitLab, Notion, Asana), whether they say "copy", "pbcopy", or just ask for paste-ready markdown.
---

# mdc

Put paste-ready GitHub-flavored Markdown on the macOS clipboard. If `pbcopy`
is missing, say so and deliver a file instead.

## Routing — pick the cheapest writer by where the content lives

| Content lives… | Route | Content tokens in main context |
|---|---|---|
| Already a file, no reformatting | `SOURCE` = that path; go to step 2 | 0 |
| On disk but needs composing (a diff, files, a plan to trim) | Dispatch ONE cheap agent (`tlor:dwarf-smith` `model: haiku`; `tlor:gondor-builder` if summarizing needs judgment) with pointers only — paths, line ranges, git refs, NEVER the content; it runs steps 1–4 itself | ~0 |
| Said verbatim in the conversation | Run `python3 ${CLAUDE_SKILL_DIR}/scripts/session_to_md.py <session-id> --copy` (add `-o` for a file; `--last N`/`--all` to widen) | ~0 |
| New or reworked text | Compose and write inline (step 1) | 1× — the minimum; dispatching doubles it (prompt + write) |

No dispatch when already inside a subagent or in plan mode (plan-mode state
propagates; the agent can't write files or the clipboard).

## Steps

1. **Compose** clean GFM: one `#` title, `##` sections, bullets over prose
   walls, inline code for identifiers, fenced blocks with a language tag; no
   ANSI colors, line-number prefixes, or HTML unless asked; match the source
   language; scale length to the ask. Write it to `{scratchpad}/clipboard.md`
   = `SOURCE` — always via a file write, never echo/heredoc (backticks, `$`,
   and quotes break shell quoting and silently mangle the clipboard). Don't
   leave copies in the user's project tree.
2. **Copy**: `pbcopy < $SOURCE`
3. **Verify**: `pbpaste | cmp -s - $SOURCE` — exit 0 is a pass; a
   trailing-newline-only diff also passes. On failure retry steps 2–3 once,
   then report the failure honestly — never claim it was copied.
4. **Report** in 1–2 lines: title + line count + `SOURCE` path as fallback;
   don't paste the content back into chat. If the content is sensitive and
   `SOURCE` is a scratchpad file the skill created, offer to delete it once
   the paste is confirmed.

Iterating ("too long", "add X"): edit the same `SOURCE` file (a pre-existing
file gets edited in place) and re-run steps 2–4 — no v2 copies.
