#!/usr/bin/env python3

try:
    from PyPDF2 import PdfFileReader
except ImportError:
    print("Please install the PyPDF2 library using `pip3 install PyPDF2`.\n")
    raise

from collections import deque
import sys

def get_links_and_destinations(f):
    # Based on <https://stackoverflow.com/a/5978161/393146>
    pdf = PdfFileReader(f)

    links = deque()
    dests = deque()
    errors = deque()

    for pg in range(pdf.getNumPages()):
        obj = pdf.getPage(pg).getObject()

        for annotation in obj.get('/Annots', []):
            uri = annotation.getObject().get('/A', {}).get('/URI', None)
            if uri is not None and uri not in links:
                links.append(uri)

    dests = pdf.getNamedDestinations()

    for l in links:
        if not l.startswith("https:"):
            errors.append("Insecure or unrecognized protocol in link: " + l)

        if l.startswith("https://zips.z.cash/protocol/"):
            fragment = l.partition("#")[2]
            if fragment and fragment not in dests:
                errors.append("Missing link target: " + l)

    return (links, dests, errors)


def main(args):
    if len(args) < 2:
        print("Usage: ./links_and_dests.py <file.pdf>")
        return 1

    with open(args[1], 'rb') as f:
        (links, dests, errors) = get_links_and_destinations(f)

    print("Links:")
    for l in links:
        print(l)

    print("\nDestinations:")
    for d in dests:
        print(d)

    if errors:
        print("\nErrors:")
        for e in errors:
            print(e)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
