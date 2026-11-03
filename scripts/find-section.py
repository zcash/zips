#!/usr/bin/env python3
"""Resolve protocol-spec section numbers to labels, titles, and source lines.

Usage:
  find-section.py [--aux AUXFILE] QUERY [QUERY ...]

Each QUERY is one of:
  - a section number, e.g. "4.20.2";
  - a label, e.g. "decryptivk";
  - a protocol.tex line number prefixed with "line:", e.g. "line:13869"
    (as reported in an Overfull \\hbox warning, say), which reports the
    enclosing section;
  - otherwise, a case-insensitive title substring, e.g. "Key Components".

Section numbering is assigned at build time and differs between build
variants, so this reads the \\newlabel entries from an aux file produced by
a prior `make` in protocol/ (default: the most recently modified
protocol/aux/*.aux). Run a build first if protocol/aux/ is empty. The
source location reported for each match is the range of protocol.tex lines
the section spans: from the line that defines its heading up to the line
before the next heading of the same or higher level (so a section's range
includes its subsections). A change-history entry or other non-section
label, which has no extent, reports just its defining line.
"""

import argparse
import glob
import os
import re
import sys

NEWLABEL_RE = re.compile(r"\\newlabel\{([^}@]+)\}\{\{([^{}]*)\}\{([^{}]*)\}\{(.*)")
DEFINITION_CMD_RE = re.compile(
    r"\\(l(?:sub)*section|extralabel|headingandlabel|historyentry|label)\b"
)
SECTION_CMD_RE = re.compile(r"l(?:sub)*section\Z")


def detex(s: str) -> str:
    """Crudely flatten TeX macros in a title for display."""
    s = re.sub(r"\\([A-Za-z]+)\s*", r"\1 ", s)
    s = s.replace("{", "").replace("}", "")
    # Drop the trailing aux groups after the title text, if any survived.
    s = re.sub(r"\s*(subsubsection|subsection|section|appendix)\..*$", "", s)
    return re.sub(r"\s+", " ", s).strip()


def load_labels(auxpath):
    labels = []
    with open(auxpath, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = NEWLABEL_RE.match(line)
            if m:
                label, number, page, rest = m.groups()
                title = detex(rest.rsplit("{", 2)[0].rstrip("}"))
                labels.append((label, number, page, title))
    return labels


def braced_argument(text, pos):
    """Read a balanced argument, allowing whitespace and nested TeX groups."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos == len(text):
        return None
    if text[pos] != "{":
        return "", pos
    depth = 1
    for match in re.finditer(r"\\.|[{}]", text[pos + 1:]):
        if match[0] == "{":
            depth += 1
        elif match[0] == "}":
            depth -= 1
            if depth == 0:
                end = pos + 1 + match.start()
                return text[pos + 1:end], end + 1
    return None


def definitions(lines):
    """Yield (line, definitions), buffering only incomplete command arguments."""
    pending = ""
    start = 1
    for lineno, line in enumerate(lines, 1):
        if not pending:
            start = lineno
        # Ignore comments, but preserve escaped percent signs and newlines.
        pending += re.sub(r"\\[^\n]|%[^\n]*",
                          lambda m: "" if m[0].startswith("%") else m[0], line)
        found = []
        pos = 0
        while (match := DEFINITION_CMD_RE.search(pending, pos)):
            command = match[1]
            argument = braced_argument(pending, match.end())
            is_section = SECTION_CMD_RE.fullmatch(command) is not None
            if argument is not None and (is_section or command == "headingandlabel"):
                argument = braced_argument(pending, argument[1])
            if argument is None:
                start += pending.count("\n", 0, match.start())
                pending = pending[match.start():]
                break
            label, pos = argument
            label = label.strip()
            if command == "headingandlabel" and label.startswith(r"\#"):
                label = label[2:]
            if re.fullmatch(r"[A-Za-z0-9_.:-]+", label):
                level = 1 + command.count("sub") if is_section else None
                found.append((start + pending.count("\n", 0, match.start()), label, level))
        else:
            pending = ""
        yield lineno, found


def defining_line(texpath, label):
    with open(texpath, encoding="utf-8", errors="replace") as f:
        for _, entries in definitions(f):
            for line, name, _ in entries:
                if name == label:
                    return line
    return None


def scan_headings(texpath):
    """Single pass over protocol.tex. Returns (headings, n_lines) where
    headings is [(line number, label, level)] for each real \\l…section
    heading, in source order. The label is read from the heading's second
    argument, which may span lines (so an \\extralabel-wrapped heading gives
    the inner label); the level is 1 + the number of "sub" prefixes.
    Change-history entries and other \\extralabel/\\headingandlabel lines
    carrying no \\l…section are not headings and are excluded."""
    headings = []
    n_lines = 0
    with open(texpath, encoding="utf-8", errors="replace") as f:
        for n_lines, entries in definitions(f):
            headings.extend(entry for entry in entries if entry[2] is not None)
    return headings, n_lines


def section_range(start, headings, n_lines):
    """(start, end) source-line span of the section whose heading is at
    `start`: up to the line before the next heading of the same or higher
    level (so the span includes subsections). If `start` is not a real
    section heading, the span is just (start, start)."""
    level = next((lvl for defline, _label, lvl in headings if defline == start), None)
    if level is None:
        return (start, start)
    end = n_lines
    for defline, _label, lvl in headings:
        if defline > start and lvl <= level:
            end = defline - 1
            break
    return (start, end)


def enclosing_section(headings, labels, lineno):
    """The nearest section heading at or before lineno whose label is
    numbered in the aux file (labels excluded from this build variant are
    skipped)."""
    by_label = {entry[0]: entry for entry in labels}
    for defline, label, _lvl in reversed(headings):
        if defline <= lineno and label in by_label:
            return by_label[label]
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--aux", help="aux file to read numbering from")
    ap.add_argument("queries", nargs="+")
    args = ap.parse_args()

    protodir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "protocol")
    auxpath = args.aux
    if auxpath is None:
        candidates = glob.glob(os.path.join(protodir, "aux", "*.aux"))
        if not candidates:
            sys.exit("no protocol/aux/*.aux found; run a build "
                     "(e.g. `nix develop -c make -C protocol nu6_3`) first")
        auxpath = max(candidates, key=os.path.getmtime)
    texpath = os.path.join(protodir, "protocol.tex")

    labels = load_labels(auxpath)
    headings, n_lines = scan_headings(texpath)
    print(f"# numbering from {os.path.relpath(auxpath, protodir)}")

    status = 0
    for q in args.queries:
        if q.startswith("line:"):
            try:
                lineno = int(q[len("line:"):])
            except ValueError:
                print(f"{q}: not a line number")
                status = 1
                continue
            entry = enclosing_section(headings, labels, lineno)
            matches = [entry] if entry else []
        elif re.fullmatch(r"[0-9]+(\.[0-9]+)*", q):
            matches = [e for e in labels if e[1] == q]
        else:
            matches = [e for e in labels if e[0] == q]
            if not matches:
                matches = [e for e in labels if q.lower() in e[3].lower()]
        if not matches:
            print(f"{q}: not found")
            status = 1
            continue
        for label, number, page, title in matches:
            line = defining_line(texpath, label)
            if line:
                start, end = section_range(line, headings, n_lines)
                where = (f"protocol.tex:{start}-{end}" if end > start
                         else f"protocol.tex:{start}")
            else:
                where = "(no defining line found)"
            print(f"{number or '-':<10} {label:<40} p.{page:<5} {where:<24} {title}")
    sys.exit(status)


if __name__ == "__main__":
    main()
