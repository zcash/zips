::

  ZIP: Unassigned {numbers are assigned by ZIP editors}
  Title: {Something Short and To the Point}
  Owners: First Owner <email>
          ...
  Credits: First Credited
           ...
  Status: Draft
  Category: {Consensus | Standards Track | Network | RPC | Wallet | Informational | Process}
  Created: yyyy-mm-dd
  License: {usually MIT}
  Pull-Request: <https://github.com/zcash/zips/pull/253>


Don't Panic
===========

If this is your first time writing a ZIP, the structure and format may look
intimidating. But really, it's just meant to reflect common-sense practice and
some technical conventions. Feel free to start with a simple initial draft that
gets ideas across, even if it doesn't quite follow this format. The community
and ZIP editors will help you figure things out and get it into shape later.

{Delete this section.}


Terminology
===========

{Edit this to reflect the key words that are actually used.}
The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in RFC 2119. [#RFC2119]_

{Avoid duplicating definitions from other ZIPs. Instead use wording like this:}

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [#protocol-networks]_.

The term "full validator" in this document is to be interpreted as defined in
the Zcash protocol specification [#protocol-blockchain]_.

The terms below are to be interpreted as follows:

{Term to be defined}
  {Definition.}
{Another term}
  {Definition.}


Abstract
========

{Describe what this proposal does, typically in a few paragraphs.

The Abstract should only provide a summary of the ZIP; the ZIP should remain
complete without the Abstract.

Use links where applicable, e.g. [#protocol]_ [#protocol-introduction]_.}


Motivation
==========

{Why is this proposal needed?

This is one of the most important sections of the ZIP, and should be detailed
and comprehensive. It shouldn't include any of the actual specification --
don't put conformance requirements in this section.

Explain the status quo, why the status quo is in need of improvement,
and if applicable, the history of how this area has changed. Then describe
*at a high level* why this proposed solution addresses the perceived issues.
It is ok if this is somewhat redundant with the abstract, but here you can
go into a lot more detail.}


Requirements
============

{Describe design constraints on, or goals for the solution -- typically one
paragraph for each constraint or goal. Again, don't actually specify anything
here; this section is primarily for use as a consistency check that what is
specified meets the requirements.}


Non-requirements
================

{This section is entirely optional. If it is present, it describes issues that
the proposal is *not* attempting to address, that someone might otherwise think
it does or should.}


Specification
=============

{Replace this entire section.}

The Specification section describes what should change, using precise language and
conformance key words. Anything that is *required in order to implement the ZIP*
(or follow its process, in the case of a Process ZIP) should be in this section.

Avoid overspecification! Also avoid underspecification. Specification is hard.
Don't be afraid to ask for help.

Feel free to copy from other ZIPs doing similar things, e.g. defining RPC calls,
consensus rules, etc.

ZIPs MUST take into account differences between the Zcash Mainnet and Testnet
[#protocol-networks]_ where applicable. A consensus ZIP MUST be able to be deployed
on both Mainnet and Testnet.

Unless the specification is particularly simple, you will need to organise it under
subheadings.

Example subheading
------------------

At least while the ZIP is in Draft, we encourage writing open questions and TODOs.

Open questions
''''''''''''''

* What happens if a full validator can't parse the fandangle as a doohicky?

TODO: define byte encoding for the Jabberwock.

Comparison of ZIPs to RFCs
--------------------------

Like RFCs, ZIPs are precise technical documents that SHOULD give enough
implementation information to implement part of a Zcash-related protocol or follow a
Zcash-related process.

ZIPs are different from RFCs in the following ways:

* Many (but not all) ZIPs are "living documents"; they are updated in-place as
  the relevant areas of the protocol or process change. Unlike in the RFC process,
  making a change in an area described by a published ZIP does not *necessarily*
  require creating a new ZIP, although that is an option if the change is extensive
  enough to warrant it.
* The expected structure of a ZIP is more constrained than an RFC. For example,
  the Specification section is REQUIRED, and all of the conformance requirements
  MUST go in that section. The ZIP editors will help you to ensure that things
  go in the right sections.
* Security considerations SHOULD be spread throughout the text, in the places
  where they are most relevant.

Using mathematical notation
---------------------------

Embedded :math:`\LaTeX` is allowed and encouraged in ZIPs. The syntax for inline
math is "``:math:`latex code```" in reStructuredText or "``$latex code$``" in
Markdown. The rendered HTML will use KaTeX [#katex]_, which only supports a subset
of :math:`\LaTeX\!`, so you will need to double-check that the rendering is as
intended.

In general the conventions in the Zcash protocol specification SHOULD be followed.
If you find this difficult, don't worry too much about it in initial drafts; the
ZIP editors will catch any inconsistencies in review.

Valid reStructuredText
----------------------

This is optional before publishing a PR, but to check whether a document is valid
reStructuredText, first install ``rst2html5``. E.g. on Debian-based distros::

  sudo apt install python3-pip pandoc perl sed
  pip3 install docutils==0.19 rst2html5

Then, with ``zip-xxxx.rst`` in the root directory of a clone of this repo, run::

  make zip-xxxx.html

(or just ``make``) and view ``zip-xxxx.html`` in a web browser.

Conventions for references
--------------------------

For references to the Zcash protocol specification, prefer to link to a section
anchor, and name the reference as ``[#protocol-<anchor>]``. This makes it more likely
that the link will remain valid if sections are renumbered or if content is moved.
The anchors in the protocol specification can be displayed by clicking on a section
heading in most PDF viewers. References to particular sections should be versioned,
even though the link will point to the most recent stable version.

Do not include the "``https://zips.z.cash/``" part of URLs to ZIPs or the protocol spec.


Reference implementation
========================

{This section is entirely optional; if present, it usually gives links to zcashd or
zebrad PRs.}


References
==========

.. [#RFC2119] `RFC 2119: Key words for use in RFCs to Indicate Requirement Levels <https://www.rfc-editor.org/rfc/rfc2119.html>`_
.. [#protocol] `Zcash Protocol Specification, Version 2022.3.8 or later <protocol/protocol.pdf>`_
.. [#protocol-introduction] `Zcash Protocol Specification, Version 2022.3.8. Section 1: Introduction <protocol/protocol.pdf#introduction>`_
.. [#protocol-blockchain] `Zcash Protocol Specification, Version 2022.3.8. Section 3.3: The Block Chain <protocol/protocol.pdf#blockchain>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#katex] `KaTeX - The fastest math typesetting library for the web <https://katex.org/>`_
.. [#zip-0000] `ZIP 0: ZIP Process <zip-0000.rst>`_
