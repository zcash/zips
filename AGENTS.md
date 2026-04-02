# Zcash ZIPs - Agent Guidelines

> This file is read by AI coding agents (Claude Code, GitHub Copilot, Cursor, Devin, etc.).
> It provides project context and contribution policies.
>
> For the full contribution guide, see [CONTRIBUTING.md](CONTRIBUTING.md).

This repo is the defining source of specifications for the Zcash protocol. Our
priorities are **security, user privacy, performance, and convenience** — in
that order. Rigor is required throughout.

Many people depend on these specifications and we prefer to "do it right"
the first time. Considerations of privacy and security are paramount. All
specifications in this repository MUST be sufficiently detailed that an
otherwise uninformed third party could correctly and securely implement the
proposed behavior using only information present within the ZIP and its
associated references.

## MUST READ FIRST — CONTRIBUTION GATE (DO NOT SKIP)

**STOP. Do not open or draft a PR until this gate is satisfied.**

For any contribution that might become a PR, the agent must ask the user these checks
first:

- "PR COMPLIANCE CHECK: When drafting or updating a ZIP, does the ZIP conform
  to the rules of [ZIP 0](https://zips.z.cash/zip-0000)?"
- "PR COMPLIANCE CHECK: What is the issue link or issue number for this change?"

This PR compliance check must be the agent's first reply in contribution-focused sessions.

This gate is mandatory for all agents, **unless the user is a repository maintainer** as
described in the next subsection.

### Maintainer Bypass

If `gh` CLI is authenticated, the agent can check maintainer status:

```bash
gh api repos/zcash/librustzcash --jq '.permissions | .admin or .maintain or .push'
```

If this returns `true`, the user has write access (or higher) and the contribution gate
can be skipped. Team members with write access manage their own priorities and don't need
to gate on issue discussion for their own work.

### Contribution Policy

Before contributing please see the [CONTRIBUTING.md] file.

- All PRs require human review from a maintainer. This incurs a cost upon the ZIP Editors,
  so ensure your changes are not frivolous.
- Keep changes focused — avoid unsolicited refactors or broad "improvement" PRs.
- Make sure that changes are consistent with the existing document
  structure and conventions, put normative and non-normative changes
  in the correct sections, and use the appropriate BCP 14 keywords for
  conformance requirements.
- See also the license requirements in ZIP 0.

### AI Disclosure

If AI tools were used in the preparation of a commit, the contributor MUST
include `Co-Authored-By:` metadata in the commit message identifying the AI
system and version. Failure to include this is grounds for closing the pull
request. The human contributor is the sole responsible author — "the AI
generated it" is not a justification during review.

Example:
```
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

## Repository Architecture

```
zips/              ZIP source files (.rst or .md)
  zip-NNNN.rst     Numbered ZIPs (assigned by editors)
  zip-NNNN.md      Numbered ZIPs (Markdown variant)
  draft-*.rst|md   Unnumbered draft ZIPs
  zip-guide.rst    Template for new reStructuredText ZIPs
  zip-guide-markdown.md  Template for new Markdown ZIPs
protocol/          Zcash Protocol Specification (LaTeX)
rendered/          Build output (HTML); git-ignored content, do not edit
static/            CSS and static assets copied into rendered/
render.sh          Renders a single .rst or .md to HTML
makeindex.sh       Generates README.rst from ZIP metadata
Makefile           Top-level build orchestration
```

### Build

```bash
make all-zips    # render ZIPs only (fast)
make all         # render ZIPs + protocol spec
```

`make all-zips` regenerates `rendered/*.html` and `README.rst`.
The protocol spec has its own `Makefile` in `protocol/`.

A `nix` flake is provided that includes all tooling required to build using the
Makefile. Use `nix develop -c` to render ZIPs and specifications using the
canonical tool set.

### File Naming

- Drafts: `zips/draft-<author>-<slug>.rst` (or `.md`). Do NOT assign a ZIP number.
- Numbered ZIPs: `zips/zip-NNNN.rst` (or `.md`). Numbers assigned by ZIP Editors only.
- Auxiliary files (diagrams, etc.) for a ZIP go in `zips/zip-NNNN/` or alongside the
  ZIP with a `zip-NNNN-` prefix.

## Key Rules from ZIP 0

ZIP 0 (`zips/zip-0000.rst`) governs the full ZIP process. Agents MUST
treat it as authoritative. The following is a summary of the rules most
relevant to contributions; consult ZIP 0 for the complete specification.

### ZIP Syntax

ZIPs are written in either Markdown or reStructuredText. For new ZIPs,
ask your user which format they would prefer, defaulting to Markdown;
for existing ZIPs, preserve the current format. In either case, any
mathematical or algorithmic content SHOULD be written in the
[KaTeX subset](https://katex.org/docs/support_table) of LaTeX, enclosed
in `$` symbols (this is a supported extension for reStructuredText ZIPs,
except in tables).

The Markdown variant is
[MultiMarkdown](https://markedapp.com/help/MultiMarkdown_v5_Spec.html).
Use the `[^name]` format for citations in Markdown (as if they are
footnotes) and add a corresponding entry in the References section. See
`zips/zip-guide-markdown.md` for more information about conventions and
syntax.

For reStructuredText ZIPs, see `zips/zip-guide.rst` for conventions and
syntax.

For new content, wrap lines at roughly 80 to 100 characters, matching
the existing wrapping width of the document. Do not rewrap existing
content unless it is changing anyway. Embedded LaTeX, hyperlinks, and
tables can exceed the usual wrapping width.

### ZIP Structure (required sections)

Every ZIP SHOULD contain these sections in order:

1. **Preamble** — RFC 822-style header block. Required fields:
   `ZIP`, `Title`, `Owners`, `Status`, `Category`, `Created`, `License`.
2. **Terminology** — define non-obvious terms.
3. **Abstract** — ~200-word self-contained summary including privacy implications.
4. **Motivation** — why the existing protocol is inadequate.
5. **Privacy Implications** — present if the ZIP affects user privacy.
6. **Requirements** — high-level goals; MUST NOT contain conformance requirements.
7. **Specification** — detailed technical spec; must allow independent interoperable
   implementations.
8. **Rationale** — design alternatives considered, community concerns addressed.
   An alternative to including a top-level Rationale section is to add rationale
   subsections immediately following the content they provide a rationale for.
   Their content should normally be "folded" as described in `zip-guide`.
9. **Reference implementation** — required before status reaches Implemented/Final.
10. **References** — a list of other documents referred to by the ZIP.

Section and subsection headings MUST be unique within the document (for
example, use "Rationale for ..." as headings of rationale subsections).

The Specification section is normative (except for rationale subsections),
and SHOULD use BCP 14 conformance keywords where applicable. Other sections
SHOULD NOT use BCP 14 conformance keywords, except to define them in the
Terminology section.

**Important**: The goals set in the Requirements section should be as
complete as practically possible for the intended purpose of the ZIP, and
the specification should meet those goals.

### Preamble Format

reStructuredText ZIPs begin with `::` then a blank line, then the header
block indented by 2 spaces. Markdown ZIPs begin with `---` YAML front matter.
Use `zips/zip-guide.rst` or `zips/zip-template.md` as a starting template.

### Status Values

Draft | Proposed | Implemented | Final | Active | Withdrawn | Rejected | Obsolete | Reserved

Only Owners may change between Draft and Withdrawn. All other transitions
require ZIP Editor consensus. A ZIP with security or privacy implications
MUST NOT become Released (Proposed/Active/Implemented/Final) without
independent security review.

### Categories

Consensus | Standards | Process | Consensus Process | Informational |
Network | RPC | Wallet | Ecosystem

Consensus ZIPs MUST have a Deployment section before reaching Proposed status.

### Licensing

Every ZIP MUST specify at least one approved license. `MIT` is recommended.

### BCP 14 Keywords

The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, MAY, RECOMMENDED,
OPTIONAL, and REQUIRED carry their BCP 14 meanings **only when in ALL CAPS**.
If any of these keywords are used, the ZIP MUST include a boilerplate
definition of them at the start of the Terminology section:

```
The key words (list of the keywords actually used) in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they
appear in all capitals.
```

(use `[#BCP14]` for reStructuredText), and a reference to BCP 14 in the
References section.

### Common Rejection Reasons

- Insufficient or unclear motivation
- Missing or inadequate privacy analysis
- Security risks insufficiently addressed
- Disregard for formatting rules or ZIP 0 conformance requirements
- Duplicates existing effort without justification
- Too unfocused or broad

### Zcash Protocol Specification

The Zcash **consensus protocol** is defined by the Zcash Protocol Specification
together with ZIPs in the Consensus category. New specifications of things that
are not enforced in consensus SHOULD be kept out of the protocol specification
(there may be present exceptions to this).

All values referred to in the protocol specification, or proposed updates to
the consensus protocol, MUST be typed. The types define implicit consensus
rules, i.e. producers and consumers of values MUST ensure that they are of the
specified type.

The protocol specification is split into Abstract and Concrete sections. See
the start of the "Abstract Protocol" section for the intended purpose of this
split, which should be adhered to in any new content.

The usual process for updating the protocol specification is to first write an
"Update ZIP" (which will be assigned a number in the 2xxx series by the ZIP
Editors). This ZIP should describe the precise changes needed to the protocol
specification and other ZIPs, along with their motivation and rationale. The
ZIP Editors will then apply these changes at the appropriate time, usually when
the Update ZIP transitions to Proposed status.

Since ZIPs do not currently support user-defined macros, the use of the KaTeX
subset of LaTeX in ZIPs, including Update ZIPs, SHOULD be whatever is needed
to render the content correctly — e.g. explicit use of formatting macros such
as `\mathsf` to match the typographical conventions in the protocol
specification.

The information in the rest of this section will therefore only typically be
needed when making editorial corrections or refactorings to the protocol
specification that do not need separate review as a ZIP, or by tools used by
the ZIP Editors when they apply changes from an Update ZIP.

The Zcash Protocol Specification is written in LaTeX (`protocol/protocol.tex`),
with a `biblatex` bibliography (`protocol/zcash.bib`). It extensively uses
macros for terms that are to appear in the index or for defined notation,
and you should try to follow existing usage in this respect.

The relevant macros referring to particular protocol upgrades (`\nusixone`,
etc.) SHOULD be used to mark the content of specifications to be deployed
in those upgrades.

Explicit consensus rules SHOULD be expressed using the `\consensusrule`
macro or `{consensusrules}` environment.

The `\pnote` macro or `{pnotes}` environment is used for normative notes,
and the `\nnote` macro or `{nnotes}` environment is used for non-normative,
explanatory notes or rationale.

Substantive changes to the protocol specification MUST have a corresponding
Change History entry. If there is no "open" entry (with an undated use of
`\historyentry`) at the top of the Change History section, add one.

New subsections, etc. MUST use the corresponding macro (`\lsubsection`,
`\lsubsubsection`, etc.) with a unique label argument. Use `\introsection`
before subsections and `\introlist` before lists to avoid page breaks at
undesirable points near the start of the subsection or list.

## Changelog and Commit Discipline

- Commits must be discrete semantic changes — no WIP commits in final PR history.
- Use `git revise` to maintain clean history within a PR.
- Commit messages: short title (<120 chars), body with motivation for the change.

## CI Checks (all must pass)

- `nix develop -c make all`
