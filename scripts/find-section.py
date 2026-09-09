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
defining line reported for each match is the first line of protocol.tex
that uses the label in a sectioning or \\extralabel command.
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


SECTIONING_RE = re.compile(DEFINING_RE_TEMPLATE)
# A label is the last simple {alphanumeric} group on a sectioning line; title
# groups contain spaces or macros, so they don't match.
SIMPLE_GROUP_RE = re.compile(r"\{([A-Za-z0-9]+)\}")


def sectioning_lines(texpath):
    """One pass over protocol.tex: [(line number, label)] per sectioning line."""
    out = []
    with open(texpath, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if SECTIONING_RE.search(line):
                groups = SIMPLE_GROUP_RE.findall(line)
                if groups:
                    out.append((i, groups[-1]))
    return out


def enclosing_section(texpath, labels, lineno):
    """The nearest sectioning command at or before lineno whose label is
    numbered in the aux file (labels excluded from this build variant are
    skipped)."""
    by_label = {label: entry for entry in labels for label in [entry[0]]}
    for defline, label in reversed(sectioning_lines(texpath)):
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
            entry = enclosing_section(texpath, labels, lineno)
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
            where = f"protocol.tex:{line}" if line else "(no defining line found)"
            print(f"{number or '-':<10} {label:<40} p.{page:<5} {where:<20} {title}")
    sys.exit(status)


if __name__ == "__main__":
    main()
