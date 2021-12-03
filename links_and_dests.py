#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import build_opener, HTTPCookieProcessor, HTTPSHandler, Request
from urllib.error import URLError, HTTPError
from os.path import relpath
from collections import deque
import sys
from time import sleep
import ssl
from io import BytesIO

try:
    from bs4 import BeautifulSoup
    import html5lib
    import certifi
except ImportError:
    print("Please install the BeautifulSoup, html5lib, and certifi libraries using `pip install bs4 html5lib certifi`.\n")
    raise

if [int(v) for v in certifi.__version__.split('.')] < [2021, 5, 30]:
    print("Please upgrade certifi using `pip install --upgrade certifi`.\n")
    sys.exit(1)

def get_links_and_destinations_from_pdf(f):
    try:
        from PyPDF2 import PdfFileReader
    except ImportError:
        print("Please install the PyPDF2 library using `pip install PyPDF2`.\n")
        raise

    # Based on <https://stackoverflow.com/a/5978161/393146>
    pdf = PdfFileReader(f)

    links = set()
    for pg in range(pdf.getNumPages()):
        obj = pdf.getPage(pg).getObject()

        for annotation in obj.get('/Annots', []):
            uri = annotation.getObject().get('/A', {}).get('/URI', None)
            if uri is not None and uri not in links:
                links.add(uri)

    dests = pdf.getNamedDestinations().keys()

    return (links, dests)


def get_links_and_destinations_from_html(f):
    links = set()
    internal = set()
    dests = set()

    soup = BeautifulSoup(f.read(), "html5lib")
    for link in soup.find_all('a'):
        if link.has_attr('href'):
           url = link['href']
           (internal if url.startswith('#') else links).add(url)

        if link.has_attr('name'):
           dests.add(link['name'])

    for link in soup.find_all(id=True):
        dests.add(link['id'])
        # GitHub's rendering of .mediawiki files puts 'id="user-content-<ANCHOR>"' in the source
        # and dynamically creates a corresponding link #<ANCHOR>.
        if link['id'].startswith("user-content-"):
            dests.add(link['id'][13:])

    internal.difference_update(['#' + d for d in dests])  # ignore internal links satisfied by a dest
    links.update(internal)
    return (links, dests)


def main(args):
    if len(args) < 2:
        print("Usage: ./links_and_dests.py [--check] [--print-dests] <file.pdf|html|xhtml>")
        return 1

    check = '--check' in args[1:]
    print_dests = '--print-dests' in args[1:]
    paths = [arg for arg in args[1:] if not arg.startswith('--')]

    all_links = {}  # url -> pdf_paths
    all_dests = {}  # url -> dests

    errors = deque()

    print("Reading files...")
    for path in paths:
        print(path, end=" ")
        sys.stdout.flush()

        with open(path, 'rb') as f:
            if path.endswith(".html") or path.endswith(".xhtml"):
                (links, dests) = get_links_and_destinations_from_html(f)
            elif path.endswith(".pdf"):
                (links, dests) = get_links_and_destinations_from_pdf(f)
            else:
                errors.append("Unrecognized file type: " + path)
                continue

        path = relpath(path)
        for l in links:
            refs = all_links.get(l, None)
            if refs is None:
                all_links[l] = refs = deque()
            refs.append(path)

        all_dests["https://zips.z.cash/" + path] = dests
        if path.endswith(".html"):
            all_dests["https://zips.z.cash/" + path[:-5]] = dests

    print("\n")
    print("Links:")

    last_url = None
    content = None
    content_type = None
    dests = None

    for (l, p) in sorted(all_links.items()):
        print(l, end=" ")
        sys.stdout.flush()
        what = "%s (occurs in %s)" % (l, " and ".join(p)) if len(paths) > 1 else l
        status = ""

        if ":" not in l:
            l = "https://zips.z.cash/" + l

        if l.startswith("mailto:"):
            status = "(not checked)"
        elif l.startswith("https:") or l.startswith("HTTP:"):  # use uppercase HTTP: for links with no https: equivalent
            (url, _, fragment) = l.partition("#")

            if url in all_dests:
                if fragment and fragment not in all_dests[url]:
                    errors.append("Missing link target: " + what)
                    status = "❌"
                else:
                    status = "✓"
            elif check:
                # If url == last_url, there is no need to refetch content. This is an optimization when
                # checking URLs with the same site but different fragments (which will be sorted together).
                if url != last_url:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    https_handler = HTTPSHandler(context=ssl.create_default_context(cafile=certifi.where()))

                    # Some DOI links (i.e. to https://doi.org/) redirect to link.springer.com
                    # in a way that requires cookies (booo!). We allow this for DOI links,
                    # but for all other links we simulate a client that never sets cookies.
                    if l.startswith("https://doi.org/"):
                        opener = build_opener(HTTPCookieProcessor(), https_handler)
                    else:
                        opener = build_opener(https_handler)

                    for retry in range(2):
                        try:
                            response = opener.open(Request(url=l, headers=headers))
                            content_type = response.info().get_content_type()
                            content = response.read()
                            last_url = url
                        except URLError as e:
                            if retry == 0 and isinstance(e, HTTPError) and e.code == 429:
                                try:
                                    delay = int(e.headers['Retry-After'], 10) + 1
                                except Exception:
                                    delay = 60

                                print("(waiting %ds due to rate limiting)" % (delay,), end=" ")
                                sys.stdout.flush()
                                sleep(delay)
                                continue

                            errors.append("Could not open link: %s due to %r" % (what, e))
                            status = "❌"
                            content_type = None
                            content = None
                            last_url = None

                        dests = None
                        break

                if content is not None:
                    if fragment:
                        if dests is None:
                            if content_type in ('text/html', 'application/xhtml+xml'):
                                (_, dests) = get_links_and_destinations_from_html(BytesIO(content))
                            elif content_type == 'application/pdf':
                                (_, dests) = get_links_and_destinations_from_pdf(BytesIO(content))

                        if dests is None:
                            print("(link target not checked)", end=" ")
                            status = "✓"
                        elif fragment not in dests:
                            errors.append("Missing link target: " + what)
                            status = "❌"
                        else:
                            status = "✓"
                    else:
                        status = "✓"
        else:
            errors.append("Insecure or unrecognized protocol in link: " + what)
            status = "❌"

        print(status)

    if print_dests:
        for (path, dests) in all_dests.items():
            if path + ".html" not in all_dests:  # avoid duplication
                print("\nDestinations for %s:" % (path,))
                for d in dests:
                    print(d)

    if errors:
        print("\nErrors:")
        for e in errors:
            print(e)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
