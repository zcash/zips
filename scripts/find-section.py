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
DEFINING_RE_TEMPLATE = r"\\(?:extralabel|headingandlabel|l(?:sub)*section)\{"


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


def defining_line(texpath, label):
    pat = re.compile(DEFINING_RE_TEMPLATE + r".*\{" + re.escape(label) + r"\}")
    fallback = None
    with open(texpath, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if "{" + label + "}" in line:
                if pat.search(line):
                    return i
                if fallback is None:
                    fallback = i
    return fallback


# A label is the last simple {alphanumeric} group on a heading line; title
# groups contain spaces or macros, so they don't match.
SIMPLE_GROUP_RE = re.compile(r"\{([A-Za-z0-9]+)\}")
# A real section heading: \lsection, \lsubsection, …, possibly wrapped in an
# \extralabel on the same line. The nesting level is 1 + the number of "sub"
# prefixes (lsection = 1, lsubsection = 2, …).
SECTION_CMD_RE = re.compile(r"\\(l(?:sub)*section)\b")


def scan_headings(texpath):
    """Single pass over protocol.tex. Returns (headings, n_lines) where
    headings is [(line number, label, level)] for each real \\l…section
    heading, in source order. The label is the last simple {alphanumeric}
    group on the line (so an \\extralabel-wrapped heading gives the inner
    label); the level is 1 + the number of "sub" prefixes. Change-history
    entries and other \\extralabel/\\headingandlabel lines carrying no
    \\l…section are not headings and are excluded."""
    headings = []
    n_lines = 0
    with open(texpath, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            n_lines = i
            m = SECTION_CMD_RE.search(line)
            if m:
                groups = SIMPLE_GROUP_RE.findall(line)
                if groups:
                    headings.append((i, groups[-1], 1 + m.group(1).count("sub")))
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
