#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyPDF2 import PdfFileReader
except ImportError:
    print("Please install the PyPDF2 library using `pip3 install PyPDF2`.\n")
    raise

from urllib.request import urlopen, Request
from urllib.error import URLError
from os.path import basename
from collections import deque
import sys

def get_links_and_destinations(f):
    # Based on <https://stackoverflow.com/a/5978161/393146>
    pdf = PdfFileReader(f)

    links = set()
    for pg in range(pdf.getNumPages()):
        obj = pdf.getPage(pg).getObject()

        for annotation in obj.get('/Annots', []):
            uri = annotation.getObject().get('/A', {}).get('/URI', None)
            if uri is not None and uri not in links:
                links.add(uri)

    dests = pdf.getNamedDestinations()

    return (links, dests)


def main(args):
    if len(args) < 2:
        print("Usage: ./links_and_dests.py [--check] [--print-dests] <file.pdf>")
        return 1

    check = '--check' in args[1:]
    print_dests = '--print-dests' in args[1:]
    paths = [arg for arg in args[1:] if not arg.startswith('--')]

    all_links = {}  # url -> pdf_paths
    all_dests = {}  # url -> dests

    for pdf_path in paths:
        with open(pdf_path, 'rb') as f:
            (links, dests) = get_links_and_destinations(f)

        for l in links:
            refs = all_links.get(l, None)
            if refs is None:
                all_links[l] = refs = deque()
            refs.append(pdf_path)

        all_dests["https://zips.z.cash/protocol/" + basename(pdf_path)] = dests

    errors = deque()

    print("Links:")
    for (l, p) in sorted(all_links.items()):
        print(l, end=" ")
        sys.stdout.flush()
        what = "%s (occurs in %s)" % (l, " and ".join(p)) if len(paths) > 1 else l
        status = ""

        if not l.startswith("https:"):
            errors.append("Insecure or unrecognized protocol in link: " + what)
            status = "❌"
        else:
            (url, _, fragment) = l.partition("#")
            if url in all_dests:
                if fragment and fragment not in all_dests[url]:
                    errors.append("Missing link target: " + what)
                    status = "❌"
                else:
                    status = "✓"
            elif check:
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    res = urlopen(Request(url=l, headers=headers))
                    res.read()
                    status = "✓"
                except URLError as e:
                    errors.append("Could not open link: %s due to %r" % (what, e))
                    status = "❌"

        print(status)

    if print_dests:
        for dests in all_dests:
            print("\nDestinations for %s:" % (dests,))
            for d in dests:
                print(d)

    if errors:
        print("\nErrors:")
        for e in errors:
            print(e)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
