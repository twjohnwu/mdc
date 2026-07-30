#!/usr/bin/env python3
"""Extract assistant/user text from a Claude Code session transcript (JSONL).

Usage: session_to_md.py [SESSION] [--last N] [--all] [--role assistant|user|both]
                         [-o OUT.md] [--copy]
"""
import argparse
import glob
import json
import os
import subprocess
import sys

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")


def resolve_session(session):
    if session and session.endswith(".jsonl") and os.path.isfile(session):
        return session
    if session:
        matches = glob.glob(os.path.join(PROJECTS_DIR, "*", f"*{session}*.jsonl"))
        if not matches:
            print(f"error: no session matching '{session}' found under {PROJECTS_DIR}", file=sys.stderr)
            sys.exit(1)
        if len(matches) > 1:
            print(f"error: ambiguous session id '{session}', matches:", file=sys.stderr)
            for m in matches:
                print(f"  {m}", file=sys.stderr)
            sys.exit(1)
        return matches[0]
    all_files = glob.glob(os.path.join(PROJECTS_DIR, "*", "*.jsonl"))
    if not all_files:
        print(f"error: no transcripts found under {PROJECTS_DIR}", file=sys.stderr)
        sys.exit(1)
    return max(all_files, key=os.path.getmtime)


def extract_text(message):
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return "\n\n".join(t for t in texts if t)
    return ""


def load_messages(path):
    messages = []
    try:
        fh = open(path)
    except OSError as e:
        print(f"error: cannot read '{path}': {e}", file=sys.stderr)
        sys.exit(1)
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") not in ("user", "assistant"):
                continue
            if d.get("isSidechain") is True:
                continue
            text = extract_text(d.get("message", {}))
            if not text:
                continue
            if d["type"] == "user" and (text.startswith("<local-command") or text.startswith("<command-name>")):
                continue
            messages.append({"role": d["type"], "text": text})
    return messages


def select_messages(messages, role, last, show_all):
    if role == "both":
        pool = messages
    else:
        pool = [m for m in messages if m["role"] == role]
    if show_all:
        return pool
    n = last if last else 1
    return pool[-n:]


def render(selected):
    if len(selected) == 1:
        return selected[0]["text"]
    parts = []
    for m in selected:
        header = "## User" if m["role"] == "user" else "## Assistant"
        parts.append(f"{header}\n\n{m['text']}")
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="Extract text from a Claude Code session transcript.")
    ap.add_argument("session", nargs="?", help="path/id/id-prefix; omitted = most recent transcript")
    ap.add_argument("--last", type=int, default=None, help="last N messages of the chosen role(s)")
    ap.add_argument("--all", action="store_true", help="every kept message")
    ap.add_argument("--role", choices=["assistant", "user", "both"], default="assistant")
    ap.add_argument("-o", "--out", help="write rendered text to this path")
    ap.add_argument("--copy", action="store_true", help="copy rendered text to the macOS clipboard")
    args = ap.parse_args()

    path = resolve_session(args.session)
    messages = load_messages(path)
    selected = select_messages(messages, args.role, args.last, args.all)
    if not selected:
        print(f"error: no {args.role} messages with text found in '{path}'", file=sys.stderr)
        sys.exit(1)

    text = render(selected)

    if args.out:
        out_dir = os.path.dirname(args.out)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w") as f:
            f.write(text)
        print(f"wrote {args.out}")
    else:
        print(text)

    if args.copy:
        try:
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
        except FileNotFoundError:
            print("error: pbcopy not found on this machine", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"error: pbcopy failed: {e}", file=sys.stderr)
            sys.exit(1)
        pasted = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout
        if pasted == text or pasted.rstrip("\n") == text.rstrip("\n"):
            print("copied to clipboard (verified via pbpaste)")
        else:
            print("error: clipboard verification failed — pbpaste content differs", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
