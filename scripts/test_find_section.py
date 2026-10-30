"""Regression tests for find-section.py (run with unittest discover)."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("find-section.py")
spec = importlib.util.spec_from_file_location("find_section", SCRIPT)
find_section = importlib.util.module_from_spec(spec)
spec.loader.exec_module(find_section)


class FindSectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "protocol.tex"

    def write(self, text):
        self.source.write_text(text, encoding="utf-8")

    def test_multiline_heading_and_range(self):
        self.write(
            "\\crossref{subsidies}\n"
            "\\lsection{Parent}{parent}\n"
            "\\lsubsection{Calculating Block Subsidy\\notbeforecanopy{, Funding Streams,}\n"
            "and Founders' Reward}\n"
            " {subsidies}\n"
            "body\n"
            "\\lsubsubsection{Child}{child}\n"
            "child body\n"
            "\\lsubsection{Next}{next}\n"
        )
        headings, n_lines = find_section.scan_headings(self.source)
        self.assertEqual(headings, [(2, "parent", 1), (3, "subsidies", 2),
                                    (7, "child", 3), (9, "next", 2)])
        self.assertEqual(n_lines, 9)
        self.assertEqual(find_section.defining_line(self.source, "subsidies"), 3)
        self.assertEqual(find_section.section_range(3, headings, n_lines), (3, 8))
        labels = [("subsidies", "7.8", "1", "Subsidies")]
        self.assertEqual(find_section.enclosing_section(headings, labels, 6), labels[0])

    def test_definitions_not_references_or_title_groups(self):
        self.write(
            "\\crossref{missing} \\crossref{alias}\n"
            "% \\lsection{Commented}{missing}\n"
            "\\extralabel{alias}{\\lsection{Title {nested} \\{literal\\}}\n"
            "{inner}} \\crossref{not-the-label}\n"
            "\\historyentry{2026.1.0}{}\n"
            "\\headingandlabel{Other heading}\n"
            "{\\#other}\n"
            "\\label{explicit}\n"
        )
        headings, n_lines = find_section.scan_headings(self.source)
        self.assertEqual(headings, [(3, "inner", 1)])
        for label, line in [("alias", 3), ("inner", 3), ("2026.1.0", 5),
                            ("other", 6), ("explicit", 8)]:
            with self.subTest(label=label):
                self.assertEqual(find_section.defining_line(self.source, label), line)
        for label in ["missing", "nested", "not-the-label"]:
            with self.subTest(label=label):
                self.assertIsNone(find_section.defining_line(self.source, label))
        self.assertEqual(find_section.section_range(5, headings, n_lines), (5, 5))

    def test_comments_and_escaped_percent_in_multiline_title(self):
        self.write(
            "\\lsection{A \\% sign % }{wrong}\n"
            "and title} % comment between arguments\n"
            "{actual}\n"
        )
        self.assertEqual(find_section.scan_headings(self.source),
                         ([(1, "actual", 1)], 3))

    def test_incremental_reading(self):
        def lines():
            yield "Unrelated text\n"
            yield "\\lsection{Multiline\n"
            yield "title}{target}\n"
            raise AssertionError("Read past the completed definition")

        entries = find_section.definitions(lines())
        self.assertEqual(next(entries), (1, []))
        self.assertEqual(next(entries), (2, []))
        self.assertEqual(next(entries), (3, [(2, "target", 1)]))

    def test_actual_subsidies_heading(self):
        source = SCRIPT.parent.parent / "protocol" / "protocol.tex"
        lines = source.read_text(encoding="utf-8").splitlines()
        start = next(i for i, line in enumerate(lines, 1)
                     if line.startswith(r"\lsubsection{Calculating Block Subsidy"))
        self.assertNotIn("{subsidies}", lines[start - 1])
        headings, n_lines = find_section.scan_headings(source)
        self.assertIn((start, "subsidies", 2), headings)
        self.assertEqual(find_section.defining_line(source, "subsidies"), start)
        labels = [("subsidies", "7.8", "1", "Subsidies")]
        self.assertEqual(find_section.enclosing_section(headings, labels, start + 2),
                         labels[0])
        end = find_section.section_range(start, headings, n_lines)[1]
        self.assertGreater(end, start + 1)


if __name__ == "__main__":
    unittest.main()
