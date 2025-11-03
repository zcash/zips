#!/usr/bin/env python3

import sys
import re
from io import StringIO
from pathlib import Path
from collections import namedtuple, deque


def main(args):
    if args[1:] == ["--test"]:
        return self_test()

    if len(args) != 3:
        print("Usage: ./expand_macros.py <macrofile> <targetfile>\n"
              "\n"
              "Expand <targetfile> using the macros defined in <macrofile>, writing the\n"
              "output on stdout. If <targetfile> is \"-\", read from stdin.\n"
              "\n"
              "The contents of <macrofile> should be a list of file inclusions and\n"
              "macro definitions, one per line. Comments (from the rightmost '%' to the\n"
              "end of the line), whitespace, and blank lines will be ignored.\n"
              "\n"
              "A file inclusion has the form\n"
              "\n"
              "\\includeonly{filename}\n"
              "\n"
              "and causes another macro file 'filename.tex' in the same directory as\n"
              "<macrofile> to be included.\n"
              "\n"
              "A macro definition has the form\n"
              "\n"
              "\\newcommand{\\macroname}[n]{replacement}\n"
              "\n"
              "where n is the number of arguments. If n is zero then the '[0]' can be\n"
              "omitted. The replacement text may include '#i' to substitute the i'th\n"
              "argument, counting from 1.\n"
              "\n"
              "For example, given a macro\n"
              "\n"
              "\\newcommand{\\journey}[3]{from {#1} to {#3} via {#2}}\n"
              "\n"
              "the invocation '\\journey{Manchester}{Crewe}{London}' will expand to\n"
              "'from {Manchester} to {London} via {Crewe}'. (It is usual, but not\n"
              "required, to use '{}' around subsitutions to compensate for lack of\n"
              "syntactic hygiene in LaTeX.)\n"
              "\n"
              "Note that this intentionally covers only the most commonly used subset\n"
              "of LaTeX macro definition syntax.\n"
              "\n"
              "A very simple approximation of LaTeX's tokenization is used in order to\n"
              "ensure that substitutions are not applied incorrectly in the case of\n"
              "no-argument macros. Specifically, a macro named '\\foo' will match only\n"
              "instances of the string '\\foo' followed by a non-letter or the end of\n"
              "a line, i.e. it will match on '\\foo0' (giving the replacement text\n"
              "followed by '0'), but not on '\\foonly'. As in LaTeX, a space after a\n"
              "no-argument macro is consumed, i.e. '\\foo ' behaves like '\\foo'.\n"
              "\n"
              "Unlike LaTeX, macros with arguments will only match if each argument is\n"
              "surrounded by '{}'. Nesting of '{}' within macro arguments works, i.e.\n"
              "in the example above, '\\journey{{a}}{b}{c}' will expand to\n"
              "'from {{a}} to {c} via {b}'. The '{' and '}' characters can be escaped\n"
              "as '\\{' and '\\}'.\n"
              "\n"
              "A token effort (pun intended) is made to ensure that macro expansion\n"
              "does not lead to tokenization inconsistent with LaTeX: if a replacement\n"
              "starts with a letter that would continue a control word, then a space\n"
              "is inserted before the replacement so that the tokenization of the\n"
              "preceding control word is preserved. (In combination with the stricter\n"
              "syntax for macro arguments, this means that certain patterns in which a\n"
              "macro expansion provides arguments to another macro are not supported.)\n"
              "Similarly, if a replacement ends with a control word that would be\n"
              "extended by the following text, then a space is inserted after the\n"
              "replacement to prevent that.\n"
              "\n"
              "Doubling a '\\' character can be used to escape it, i.e. an even number\n"
              "of '\\' characters will be left as-is and will not be considered as the\n"
              "start of a potential macro invocation. To write a literal '%' character\n"
              "in a macro definition, include a comment after the definition.\n"
              "\n"
              "Unlike LaTeX, macro arguments cannot span lines; the expansion of each\n"
              "line is independent.\n"
              "\n"
              "Exit code: 0 on success, 1 on failure.\n"
              "\n"
              "To run a self-test, use './expand_macros.py --test'. This follows the\n"
              "same exit code convention.\n")
        return 1

    macroset = parse_macros_from_file(Path(args[1]))

    targetfile = args[2]
    if targetfile == "-":
        expand_stream(macroset, sys.stdin, "<stdin>")
    else:
        with open(targetfile, "r", encoding="utf-8") as targetstream:
            expand_stream(macroset, targetstream, targetfile)



class MacroDefinitionError(Exception):
    pass

class MacroSubsitutionError(Exception):
    pass

Macro = namedtuple("Macro", "argcount replacement")
MacroSet = namedtuple("MacroSet", "mapping regex")

def make_macroset(macros):
    regexes = deque()
    for name, macro in macros.items():
        assert re.escape(name) == name
        if macro.argcount == 0:
            regexes.append(r"(?:(?:^|[^\\])(\\\\)*\\" + name + r" ?)")
        else:
            regexes.append(r"(?:(?:^|[^\\])(\\\\)*\\" + name + r"\{)")

    return MacroSet(macros, re.compile("|".join(regexes)))

def parse_macros_from_file(filepath):
    filepath = filepath.resolve()
    basepath = filepath.parent
    macros = {}
    inclusions = set()

    def opener(includename, location):
        if includename in inclusions:
            raise MacroDefinitionError(f"Re-inclusion of '{includename}' at {location}")
        inclusions.add(includename)

        with open(basepath / includename, "r", encoding="utf-8") as macrostream:
            parse_macros_into(macros, opener, macrostream, includename)

    opener(filepath.name, "<top-level>")
    return make_macroset(macros)

def parse_macros_from_string(s, name):
    macros = {}
    def opener(includename, location):
        raise MacroDefinitionError("Cannot include {includename} from a string at {location}")

    parse_macros_into(macros, opener, StringIO(s), name)
    return make_macroset(macros)


# The filename pattern cannot access other directories.
INCLUDEONLY = re.compile(r"\\includeonly\{([a-zA-Z][-.a-zA-Z]*)\}")

NEWCOMMAND_START = re.compile(r"\\newcommand\{\\([a-zA-Z]+)\}(?:\[([0-9])\])?")

def parse_macros_into(macros, opener, macrostream, filename):
    for n, line in enumerate(macrostream):
        line = line.partition('%')[0].strip(' \t\n')
        if line == "": continue

        include = INCLUDEONLY.match(line)
        if include:
            opener(include.group(1) + ".tex", f"{filename} line {n+1}")
            continue

        start = NEWCOMMAND_START.match(line)
        if not start:
            raise MacroDefinitionError(f"Non-macro found\n  At {filename} line {n+1}: <{line}>")

        name = start.group(1)
        argcount = int(start.group(2) or 0)
        (replacement, rest) = munch(line[start.end():])
        if replacement is None or rest != "":
            raise MacroDefinitionError(f"Incomplete macro definition\n  At {filename} line {n+1}: <{line}>\n  Still to parse: <{rest}>")

        macros[name] = Macro(argcount, replacement)

def munch(s):
    """Parse a balanced {} group. Return (group, rest) if found, or (None, s) otherwise."""
    if s[0] != '{':
        return (None, s)

    depth = 0
    unescaped = 1
    for i in range(len(s)):
        c = s[i]
        match c:
          case '{' : depth += unescaped
          case '}' : depth -= unescaped

        unescaped = (1 - unescaped) if c == '\\' else 1

        if depth == 0:
            return (s[1:i], s[i+1:])

    return (None, s)

def expand_stream(macroset, targetstream, filename):
    for n, line in enumerate(targetstream):
        print(expand_line(macroset, line.rstrip("\n"), f"{filename} line {n+1}"))

# 0-based
SUBST = [re.compile(r"(?:^|[^\\])(\\\\)*#" + str(i)) for i in range(1, 10)]

ENDS_IN_CONTROL_WORD = re.compile(r"(?:^|[^\\])(\\\\)*\\[a-zA-Z]+$")
ASCII_LETTER = re.compile(r"[a-zA-Z]")

def would_extend_control_word(before, after):
    return (ASCII_LETTER.match(after) is not None) and (ENDS_IN_CONTROL_WORD.search(before) is not None)

def expand_line(macroset, line, location):
    result = ""
    rest = line
    runaway = 0
    while found := macroset.regex.search(rest):
        name = found.group().rstrip('{')
        end = found.start() + len(name)
        name = name.rpartition('\\')[2]
        assert name is not None, f"name: {name}, rest: <{rest}>, found: {found}"
        start = end - len(name)
        assert start > 0, f"name: {name}, rest: <{rest}>, found: {found}"
        name = name.rstrip(' ')
        macro = macroset.mapping.get(name)
        assert macro is not None, f"name: {name}, rest: <{rest}>, found: {found}, macroset: {macroset}"
        replacement = macro.replacement

        # Append the target string up to the macro invocation including any escaped '\'s.
        result += rest[:start-1]
        rest = rest[end:]

        for subst in SUBST[:macro.argcount]:
            (arg, rest) = munch(rest)
            if arg is None:
                raise MacroSubsitutionError(f"Too few arguments to macro '\\{name}'\n  At {location}: <{line}>\n  Still to parse: <{rest}>")
            replacement = subst.sub(lambda m: m.group()[:-2] + arg, replacement)

        # If a replacement starts with a letter that would continue a control word, then a
        # space is inserted before the replacement so that the tokenization of the preceding
        # control word is preserved.
        if would_extend_control_word(result, replacement + rest):
            result += ' '

        # If a replacement ends with a control word that would be extended by the following
        # text, then a space is inserted after the replacement to prevent that.
        if would_extend_control_word(result + replacement, rest):
            replacement += ' '

        rest = replacement + rest
        runaway += 1
        if runaway == 100:
            raise MacroSubsitutionError(f"Runaway macro expansion\n  At {location}: <{line}>\n  Result: <{result}>\n  Still to parse: <{rest}>")

    return result + rest

def self_test():
    successes = 0
    failures = 0
    for testname, (macrostr, expect_mapping, cases) in TESTS.items():
        try:
            macroset = parse_macros_from_string(macrostr, f"test {testname}")
            assert macroset.mapping == expect_mapping, f"{testname} definitions\n    actual: {macroset.mapping}\n  expected: {expect_mapping}"
            for i, (target, expect_replacement) in enumerate(cases):
                location = f"test {testname} case {i+1}"
                try:
                    replacement = expand_line(macroset, target, location)
                except MacroSubsitutionError as e:
                    replacement = None
                    if expect_replacement is not None: raise
                assert replacement == expect_replacement, f"{location}\n    actual: {replacement}\n  expected: {expect_replacement}"

            successes += 1
        except (MacroDefinitionError, AssertionError) as e:
            print(f"Failed testcase: {testname}\n  {e.__class__.__name__}: {e}")
            failures += 1

    if failures > 0:
        print(f"\nTests failed: {failures} failures, {successes} successes.\n")
        return 1
    else:
        print(f"Tests passed: no failures, {successes} successes.\n")
        return 0


TESTS = {
    "journey": ("\\newcommand{\\journey}[3]{from {#1} to {#3} via {#2}}",
        {'journey': Macro(3, 'from {#1} to {#3} via {#2}')}, [
            ("\\journey{Manchester}{Crewe}{London}", "from {Manchester} to {London} via {Crewe}"),
            ("\\journey{{a}}{b}{c}", "from {{a}} to {c} via {b}"),
            ("\\journey{{a}}{\\b}{\\\\c}", "from {{a}} to {\\\\c} via {\\b}"),
            ("\\journey{{a}}{\\}\\{b}{c}", "from {{a}} to {c} via {\\}\\{b}"),
            ("\\journey{{a}}{\\}\\\\\\{b}{\\\\c}", "from {{a}} to {\\\\c} via {\\}\\\\\\{b}"),
            ("\\journey{{a}{b}{c}", None),
        ]),
    "noarg": (" \\newcommand{\\foo}{bar}",
        {'foo': Macro(0, 'bar')}, [
            ("rhu\\foo b", "rhubarb"),
            ("rhu\\foo{}b", "rhubar{}b"),
        ]),
    "unclosedarg": ("\t\\newcommand{\\foo}[1]{bar}",
        {'foo': Macro(1, 'bar')}, [
            ("rhu\\foo{", None),
        ]),
    "unusedarg": ("\\newcommand{\\foo}[1]{bar} ",
        {'foo': Macro(1, 'bar')}, [
            ("rhu\\foo{}b", "rhubarb"),
        ]),
    "recursive": ("\\newcommand{\\journey}[3]{from {#1} to {#3} via {#2}}\t\n\\newcommand{\\foo}{bar}",
        {'journey': Macro(3, 'from {#1} to {#3} via {#2}'), 'foo': Macro(0, 'bar')}, [
            ("\\journey{cabbage}{rhu\\foo b}{cauliflower}", "from {cabbage} to {cauliflower} via {rhubarb}"),
        ]),
    "comment": ("% abc\n\n \t\\newcommand{\\foo}{bar}\t % def",
        {'foo': Macro(0, 'bar')}, [
            ("rhu\\foo b", "rhubarb"),
        ]),
    "noextbefore": ("\\newcommand{\\foo}{o}",
        {'foo': Macro(0, 'o')}, [
            ("\\fo\\foo", "\\fo o"),
        ]),
    "noextafter": ("\\newcommand{\\foo}{\\bar}",
        {'foo': Macro(0, '\\bar')}, [
            ("rhu\\foo b", "rhu\\bar b"),
            ("rhu\\\\foo b", "rhu\\\\foo b"),
            ("rhu\\\\\\foo b", "rhu\\\\\\bar b"),
        ]),
    "escape": ("\\newcommand{\\foo}{bar}",
        {'foo': Macro(0, 'bar')}, [
            ("rhu\\\\\\foo b", "rhu\\\\barb"),
        ]),
    "runaway": ("\\newcommand{\\foo}{\\foo}",
        {'foo': Macro(0, '\\foo')}, [
            ("\\foo", None),
        ]),
}

if __name__ == '__main__':
    sys.exit(main(sys.argv))
