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
The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119. [#RFC2119]_

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

{This section describes what should change, using precise language and conformance
key words. Anything that is *required in order to implement the ZIP* (or follow its
process, in the case of a Process ZIP) should be in this section.

Avoid overspecification! Also avoid underspecification. Specification is hard.
Don't be afraid to ask for help.

Unless the specification is particularly simple, you will need to organise it under
subheadings.}

Example subheading
------------------

{At least while the ZIP is in Draft, we encourage writing open questions and TODOs.}

Open questions
''''''''''''''

* What happens if a full node can't parse the fandangle as a doohicky?

TODO: define byte encoding for the Jabberwock.

{Feel free to copy from other ZIPs doing similar things, e.g. defining RPC calls,
consensus rules, etc.}

Valid reStructuredText
----------------------

This is optional before publishing a PR, but to check whether a document is valid
reStructuredText, first install ``rst2html5``. E.g. on Debian-based distros::

  sudo apt install python3-pip pandoc perl sed
  pip3 install docutils==0.19 rst2html5

Then, with ``zip-xxxx.rst`` in the root directory of a clone of this repo, run::

  make zip-xxxx.html

(or just ``make``) and view ``zip-xxxx.html`` in a web browser.


Reference implementation
========================

{This section is entirely optional; if present, it usually gives links to zcashd or
zebrad PRs.}


References
==========

.. [#RFC2119] `RFC 2119: Key words for use in RFCs to Indicate Requirement Levels <https://www.rfc-editor.org/rfc/rfc2119.html>`_
.. [#protocol] `Zcash Protocol Specification, Version 2020.1.24 or later <protocol/protocol.pdf>`_
.. [#protocol-introduction] `Zcash Protocol Specification, Version 2020.1.24. Section 1: Introduction <protocol/protocol.pdf#introduction>`_
.. [#zip-0000] `ZIP 0: ZIP Process <zip-0000.rst>`_
