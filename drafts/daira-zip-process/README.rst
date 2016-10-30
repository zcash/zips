<pre>
  ZIP: 0
  Title: ZIP Purpose and Guidelines
  Author: Daira Hopwood
  Status: Active
  Category: Process
  Created: 2011-08-19
</pre>

==Terminology==

The following ... RFC 2119.

==What is a ZIP?==

ZIP stands for Zcash Improvement Proposal. A ZIP is a design document providing 
information to the Zcash community, or describing a new feature for Zcash or its 
processes or environment. The ZIP should provide a concise technical specification 
of the feature and a rationale for the feature.

We intend ZIPs to be the primary mechanisms for proposing new features, for 
collecting community input on an issue, and for documenting the design decisions 
that have gone into Zcash. The ZIP authors are responsible for building consensus 
within the community and documenting dissenting opinions.

ZIPs go through a sequence of versions as described under `ZIP Versioning`_.

ZIP Categories
==============

There are three kinds of ZIP:

* A Standards Track ZIP describes any change that affects most or all Zcash
  implementations, such as a change to the network protocol, a change in block
  or transaction validity rules, or any change or addition that affects the
  interoperability of applications using Zcash. In particular, ZIPs that
  propose changes to consensus MUST be Standards Track.

* An Informational ZIP describes a Zcash design issue, or provides general
  guidelines or information to the Zcash community, but does not propose a
  new feature. Informational ZIPs do not necessarily represent a Zcash
  community consensus or recommendation, so users and implementors are free
  to ignore Informational ZIPs or follow their advice.

* A Process ZIP describes a process surrounding Zcash, or proposes a change
  to (or an event in) a process. Examples include procedures, guidelines,
  changes to the decision-making process, and changes to the tools or
  environment used in Zcash development. All Process ZIPs, and only
  Process ZIPs, have numbers less than 100.


ZIP Work Flow
=============

The ZIP process begins with a new idea for Zcash. ZIPs do not replace the 
`Zcash issue tracker`_; typically, an idea will first have been proposed as an issue on that 
tracker, and will be discussed there. Only when and if an idea has progressed to the point 
where it is useful to propose a more formal specification, will a ZIP be written.

.. _`Zcash issue tracker`: https://github.com/zcash/zcash/issues

Each potential ZIP must have one or more *authors* -- people who write the ZIP using the 
style and format described below, shepherd the discussions in the appropriate forums, and 
attempt to build community consensus around the idea. The authors of a ZIP are authorized
to make ... The `ZIP Editors`_

Vetting an idea publicly before going as far as writing a ZIP is meant to save both the 
potential authors and the wider community time. The Zcash issue tracker contains many ideas 
for changing Zcash that have been rejected for various reasons. Searching this tracker and 
asking the Zcash community first if an idea is original helps prevent too much time being 
spent on something that is guaranteed to be rejected based on prior discussions. It also 
helps to make sure the idea is applicable to the entire community and not just the authors. 
Just because an idea sounds good to the authors does not mean it will work for most people 
in most areas where Zcash is used.

Small enhancements or patches often don't require a ZIP. These should typically be 
injected into the relevant Zcash development work flow with a pull request to the
`Zcash issue tracker`_.

A ZIP should be a clear and complete description of the proposed enhancement.
Technical aesthetics and security auditability are important considerations.

ZIPs need not, and generally SHOULD NOT, propose an implementation. (Note that this differs 
from common practice for Bitcoin Improvement Proposals.) They SHOULD, however, discuss 
non-trivial implementation considerations whenever appropriate.

The original form of a ZIP is written in (any regional variation of) English, but
translations are encouraged and MAY be placed alongside the original by the ZIP Editor.


Versioning
==========

ZIPs are strictly versioned. The versioning scheme starts with "Draft 1", "Draft 2",
etc., for how ever many drafts are needed. When and if the document is considered by
its authors and the `ZIP Editor`_ to be stable, it becomes "Version 1". Any particular
ZIP might not reach this stage. Subsequent revisions, if any, are called "Version 2",
etc. for how ever many revisions are needed.

A ZIP also has a "Change history", separate from the document itself, giving a brief
summary of the changes made in each version. See `Structure of the ZIPs Repository`_
for detail on how the versions are represented.

The source files for a ZIP are maintained under revision control in the `ZIPs 
Repository`_, but the revision history of that repository MAY contain intermediate 
commits that do not correspond to document versions.


ZIP Editors
===========

The ZIP Editors are tasked with managing the process of accepting ZIPs, maintaining 
the ZIPs Repository, assigning ZIP numbers, and performing minor editing tasks on the 
content and metadata of ZIPs. Any major editing SHOULD instead be performed by the 
author(s) of a ZIP.

There is presently a single ZIP Editor, Daira Hopwood (but this document still
uses "ZIP Editors" for generality). If there is more than one ZIP Editor at a
given time, they make decisions by informal consensus.

A Process ZIP describing procedures for selecting new ZIP Editors as and when that
becomes necessary SHOULD be submitted before January 1st, 2017.

The ZIP Editors MAY reject a proposed ZIP or update to an existing ZIP for
any of the following reasons:

 * it violates the `Zcash Code of Conduct`_;
 * it appears too unfocussed or broad;
 * it duplicates effort in other ZIPs without sufficient technical justification
   (however, alternative proposals to address similar or overlapping problems
   are not excluded for this reason);
 * it has manifest security flaws (including being unrealistically dependent
   on user vigilance to avoid security weaknesses);
 * it disregards compatibility with the existing Zcash blockchain or ecosystem;
 * it is manifestly unimplementable;
 * it includes buggy code, pseudocode, or algorithms;
 * it manifestly violates common expectations of a significant portion of the
   Zcash community;
 * it updates a Draft ZIP to Released when there is significant community
   opposition to its content (however, Draft ZIPs explicitly may describe
   proposals to which there is, or could be expected, significant community
   opposition);
 * in the case of a Released ZIP, the update makes a substantive change to
   which there is significant community opposition;
 * it is dependent on a patent that could potentially be an obstacle to
   adoption of the ZIP;
 * it includes commercial advertising;
 * it disregards formatting rules;
 * it makes non-editorial edits to previous entries in a ZIP's Change history;
 * an update to an existing ZIP extends or changes its scope to an extent
   that would be better handled as a separate ZIP;
 * a new ZIP has been proposed for a category that does not reflect its content,
   or an update would change a ZIP to an inappropriate category;
 * it updates a Released ZIP to Draft when the specification is already
   implemented and has been in common use;
 * it violates any specific "MUST" or "MUST NOT" rule in this document;
 * the expressed political views of an author of the document are inimical
   to the `Zcash Code of Conduct`_ (except in the case of an update removing
   that author);
 * it is not authorized by the stated ZIP Authors;
 * it removes an author without their consent (unless the reason for removal
   is directly related to a breach of the Code of Conduct by that author);
 * it is spam.

.. _`Zcash Contributor Code of Conduct`: https://github.com/zcash/zcash/blob/master/code_of_conduct.md

The ZIP Editors MUST NOT unreasonably deny publication of a ZIP proposal or update 
that does not violate any of these criteria. If they refuse a proposal or update, 
they MUST give an explanation of which of the criteria were violated, with the 
exception that spam may be deleted without an explanation.

Note that it is not the primary responsibility of the ZIP Editors to review
proposals for security, correctness, or implementability.

Please send all ZIP-related communications either by email to <zips@z.cash>, or by
opening an issue on the `ZIPs issue tracker`_. However if a communication concerns
a potential security vulnerability that could affect Zcash users, the
`Coordinated Security Disclosure Procedure`_ SHOULD be followed.

.. _`ZIPs issue tracker`: https://github.com/zcash/zips/issues

Authors of proposed ZIPs MUST NOT self-assign ZIP numbers. Proposals and updates
SHOULD be made as pull requests to the ZIPs Repository. A proposal for a new ZIP
MUST indicate whether it is intended to be Standards Track, Informational, or
Process. It is also possible to update an Informational ZIP to be Standards Track
or vice-versa, with the approval of the ZIP Editors. It is not possible to change
a Process ZIP to another category of ZIP, or vice versa. Each ZIP MUST be initially
proposed as a Draft.

A ZIP author may at any time withdraw their authorship on any or all versions
of a ZIP (even if this results in there being no authors for a given version).
Withdrawal of authorship is recorded in the ZIP metadata. An author who has
changed their name, formally or informally, can also ask for their name to be
updated on the ZIP metadata; the result will not include their previous name
unless they ask for it to. (As a technical caveat, the previous name may still
be visible in previous git revisions of the `ZIPs Repository`_ that remain
publically accessible, although it may be possible to fix that by a force-push.)


Relation to the Zcash Protocol Specification
============================================

The `Zcash Protocol Specification`_ describes aspects of the

The canonical description of Zcash consensus and security requirements is the 
protocol specification. It is the responsibility of the ZIP Editors and the 
authors of the protocol specification to maintain consistency between the 
specification and ZIPs that overlap its scope.

The protocol specification SHOULD explicitly reference ZIPs that describe 
proposals that are incorporated into it. Duplication between the protocol 
specification and such ZIPs is inevitable and acceptable.

To minimize the risk of unintended discrepancies, a ZIP that proposes to change 
consensus behaviour SHOULD express its proposal in terms of specific text to be 
added or changed in the specification (in addition to motivation, history, 
alternative approaches that were not adopted, etc., which may not be appropriate 
for the specification).



It is highly recommended that a single ZIP contain a single key proposal or new 
idea. The more focussed the ZIP, the more successful it is likely to be. If in 
doubt, split your ZIP into several well-focussed ones.

Both initial proposals and updates to ZIPs SHOULD be submitted by an author of
the document as a pull request to the `ZIPs repository`_.

A ZIP can also be assigned status "Deferred". The ZIP author or editor can assign 
the ZIP this status when no progress is being made on the ZIP. Once a ZIP is 
deferred, the ZIP editor can re-assign it to draft status.

A ZIP can also be "Rejected". Perhaps after all is said and done it was not a good 
idea. It is still important to have a record of this fact.

The possible paths of the status of ZIPs are as follows:

<img src=ZIP-0001/process.png></img>

Some Informational and Process ZIPs may also have a status of "Active" if they are 
never meant to be completed. E.g. ZIP 1 (this ZIP).

==What belongs in a successful ZIP?==

Each ZIP should have the following parts:

* Preamble -- RFC 822 style headers containing meta-data about the ZIP, including 
the ZIP number, a short descriptive title (limited to a maximum of 44 characters), 
the names, and optionally the contact info for each author, etc.

* Abstract -- a short description of the issue being addressed.

* Copyright -- Each ZIP MUST be licensed under the MIT License, unless the
ZIP Editor makes an explicit exception to resolve a license incompatibility
with a work from which the ZIP is derived. In the latter case the license
MUST be explicitly stated in the ZIP metadata and MUST satisfy the
`Open Source Definition`_ (interpreted to apply to documentation).

.. _`Open Source Definition`: https://opensource.org/osd-annotated


* Specification -- The technical specification should describe the syntax and 
semantics of any new feature. The specification should be detailed enough to allow 
competing, interoperable implementations in principle (whether or not multiple
implementations exist).

* Motivation -- The motivation is critical for ZIPs that want to change the Zcash 
protocol. It should clearly explain why the existing protocol specification is 
inadequate to address the problem that the ZIP solves. ZIP submissions without 
sufficient motivation may be rejected outright.

* Rationale -- The rationale fleshes out the specification by describing what 
motivated the design and why particular design decisions were made. It should 
describe alternate designs that were considered and related work.

* The rationale should provide evidence of consensus within the community and 
discuss important objections or concerns raised during discussion.

* Backwards Compatibility -- All ZIPs that introduce backwards incompatibilities 
MUST include a section describing these incompatibilities and their severity. The 
ZIP MUST explain how the author proposes to deal with these incompatibilities.


Formatting Rules
================

The metadata of a ZIP MUST be represented as a reStructuredText file.
This file includes:

* a Change history ...
* the current authors.

Each Change history entry includes:

* a description of what was changed (this can be just "initial draft" or
  similar in the case of the first draft).
* a link to the main reStructuredText or LaTeX source file for that
  version.
* a link to a rendered PDF file for that version.
* the new authors, if this is the first draft or the authors have changed.


ZIPs can be represented in either `reStructuredText`_ or `LaTeX`_ format.

Images and diagrams can be included ..., provided that a rendering to
a PNG image is included. SVG is a preferred source format.
The ZIP Editor MAY accept other formats. Formats that depend on proprietary
software are strongly discouraged.


Rules specific to reStructuredText
----------------------------------

The source for the `rst` file MUST be readable in an editor window set to
90 columns, except possibly where prevented by reStructuredText technical
limitations (such as avoiding wrapping of URLs).

The document MAY include images in .png format.


Rules specific to LaTeX
-----------------------

The ZIP directory MUST contain a ``Makefile``, the default target of
which produces a PDF file.

The README.rst file MUST include instructions to build the PDF (including
build dependencies for at least Debian-like systems).

The typographical conventions used by a LaTeX-formatted ZIP SHOULD be
consistent, as far as possible, with those used in the `Zcash protocol specification`_.
It is desirable, but not strictly necessary, that the macros used in
the protocol specification also be used in LaTeX-formatted ZIPs. This
facilitates editing accepted proposals into the main specification.


===ZIP Header Preamble===

Each ZIP must begin with an RFC 822 style header preamble. The headers must appear in the following order. Headers marked with "*" are optional and are described below. All other headers are required.

<pre>
  ZIP: <ZIP number>
  Title: <ZIP title>
  Author: <list of authors' real names and optionally, email addrs>
* Discussions-To: <email address>
  Status: <Draft | Active | Accepted | Deferred | Rejected |
           Withdrawn | Final | Superseded>
  Type: <Standards Track | Informational | Process>
  Created: <date created on, in ISO 8601 (yyyy-mm-dd) format>
* Post-History: <dates of postings to Zcash mailing list>
* Replaces: <ZIP number>
* Superseded-By: <ZIP number>
* Resolution: <url>
</pre>

The Author header lists the names, and optionally the email addresses of all the authors/owners of the ZIP. The format of the Author header value must be

  Random J. User <address@dom.ain>

if the email address is included, and just

  Random J. User

if the address is not given.

If there are multiple authors, each should be on a separate line following RFC 2822 continuation line conventions.

Note: The Resolution header is required for Standards Track ZIPs only. It contains a URL that should point to an email message or other web resource where the pronouncement about the ZIP is made.

While a ZIP is in private discussions (usually during the initial Draft phase), a Discussions-To header will indicate the mailing list or URL where the ZIP is being discussed. No Discussions-To header is necessary if the ZIP is being discussed privately with the author, or on the bitcoin email mailing lists.

The Type header specifies the type of ZIP: Standards Track, Informational, or Process.

The Created header records the date that the ZIP was assigned a number, while Post-History is used to record the dates of when new versions of the ZIP are posted to Zcash mailing lists. Both headers should be in yyyy-mm-dd format, e.g. 2001-08-14.

ZIPs may have a Requires header, indicating the ZIP numbers that this ZIP depends on.

ZIPs may also have a Superseded-By header indicating that a ZIP has been rendered obsolete by a later document; the value is the number of the ZIP that replaces the current document. The newer ZIP must have a Replaces header containing the number of the ZIP that it rendered obsolete.

===Auxiliary Files===

ZIPs may include auxiliary files such as diagrams. Image files should be included in a subdirectory for that ZIP. Auxiliary files must be named ZIP-XXXX-Y.ext, where "XXXX" is the ZIP number, "Y" is a serial number (starting at 1), and "ext" is replaced by the actual file extension (e.g. "png").

==Transferring ZIP Ownership==

It occasionally becomes necessary to transfer ownership of ZIPs to a new champion. In general, we'd like to retain the original author as a co-author of the transferred ZIP, but that's really up to the original author. A good reason to transfer ownership is because the original author no longer has the time or interest in updating it or following through with the ZIP process, or has fallen off the face of the 'net (i.e. is unreachable or not responding to email). A bad reason to transfer ownership is because you don't agree with the direction of the ZIP. We try to build consensus around a ZIP, but if that's not possible, you can always submit a competing ZIP.

If you are interested in assuming ownership of a ZIP, send a message asking to take over, addressed to both the original author and the ZIP editor. If the original author doesn't respond to email in a timely manner, the ZIP editor will make a unilateral decision (it's not like such decisions can't be reversed :).

==ZIP Editors==

The current ZIP editor is Luke Dashjr who can be contacted at [[mailto:luke_ZIPeditor@dashjr.org|luke_ZIPeditor@dashjr.org]].

==ZIP Editor Responsibilities & Workflow==

The ZIP editor subscribes to the Zcash development mailing list. All ZIP-related 
correspondence should be sent (or CC'd) to luke_ZIPeditor@dashjr.org.

For each new ZIP that comes in an editor does the following:

* Read the ZIP to check if it is ready: sound and complete. The ideas must make technical 
sense, even if they don't seem likely to be accepted.
* The title should accurately describe the content.
* Edit the ZIP for language (spelling, grammar, sentence structure, etc.), 
markup, code style (examples should match ZIP 8 & 7).

If the ZIP isn't ready, the editor will send it back to the author for revision, with specific instructions.

Once the ZIP is ready for the repository it should be submitted as a "pull request" to the [https://github.com/Zcash/ZIPs Zcash/ZIPs] repository on GitHub where it may get further feedback.

The ZIP Editors will:

* Assign a ZIP number (almost always just the next available number, but sometimes it's a special/joke number, like 666 or 3141) in the pull request comments.

* Merge the pull request when the author is ready (allowing some time for further peer review).

* List the ZIP in [[README.mediawiki]]

* Send email back to the ZIP author with next steps (post to Zcash-dev mailing list).

The ZIP editors are intended to fulfill administrative and editorial responsibilities. The ZIP editors monitor ZIP changes, and correct any structure, grammar, spelling, or markup mistakes we see.

==History==

This document is derived heavily from Bitcoin's BIP 1, authored by Amir Taaki, 
which in turn was derived from Python's PEP-0001. In many places text was simply 
copied and modified. The authors of PEP-0001 (Barry Warsaw, Jeremy Hylton, and 
David Goodger) and BIP 1 (Amir Taaki) are not responsible for any use of their 
text or ideas in the Zcash Improvement Process. The `I2P Proposal Process`_
and the RFC Process also influenced this document.

Please direct all comments to the ZIP Editors by email to <zips@z.cash> or by
filing an issue in the `ZIPs issue tracker`_.



Change history (move this to metadata)
==============

Draft 1
-------

Initial version based mainly on BIP 1. Changes include:

* Obvious renamings.
* Changes of forum, e.g. Zcash development uses GitHub repositories
  and issue tracking to a greater extent than Bitcoin, and does not
  rely on mailing lists.
* We use "ZIP Editors" even though that is currently only one person.
  Similarly a given ZIP may have more than one author, and authors
  have equal status.
* The list of potential reasons for rejection of a ZIP is expanded
  from the corresponding reasons for a BIP, and more precisely defined.
