---
name: mdc
description: Format any content — summaries, branch/commit descriptions, review notes, reports, explanations, snippets from the conversation — as clean GitHub-flavored Markdown and copy it to the macOS clipboard with pbcopy so the user can paste it anywhere (Slack, GitLab MR descriptions, Notion, Asana, docs). Use this whenever the user says "copy to my clipboard", "pbcopy", "copy it so I can paste", "give me markdown I can paste", or asks for a summary/description "in md format" together with copying — even if they don't say the word clipboard but clearly want paste-ready output.
---

# mdc

Turn requested content into paste-ready GitHub-flavored Markdown and put it
on the macOS clipboard. macOS-only: if `pbcopy` is missing, say so and
deliver the file instead.

## Steps

1. **Compose** clean GFM: one `#` title, `##` sections, bullets over prose
   walls; inline code for identifiers, fenced blocks with a language tag.
   Plain pasteable text — no ANSI colors, no `cat -n` line-number prefixes,
   no HTML unless asked. Match the source material's language; scale length
   to the ask (a "summary" is a screenful, not a spec).
2. **Write** it to `{scratchpad}/clipboard.md` (create the directory if
   needed) — a file, not echo/heredoc: backticks, `$`, and quotes break
   shell quoting in subtle ways and the clipboard silently ends up mangled.
   Don't leave copies in the user's project tree.
3. **Copy**: `pbcopy < {scratchpad}/clipboard.md`
4. **Verify**: `pbpaste | cmp -s - {scratchpad}/clipboard.md` — exit 0 means
   the clipboard matches the file. If it fails, retry steps 3–4 once; if it
   still fails, report the failure honestly (likely cause: another process
   wrote the clipboard between copy and verify) — never claim it was copied.
5. **Report** in 1–2 lines: what was copied (title + line count) plus the
   file path as fallback. Do NOT paste the full content back into chat. If
   the content is sensitive (credentials, personal data), offer to delete
   the scratchpad file once the user confirms the paste succeeded.

## Iterating

If the user says "too long", "add X", "change the tone": edit the same
scratchpad file and re-run steps 3–5. Same file, same path — no v2 copies.
