::

  ZIP: Unassigned
  Title: Lockbox for Decentralized Grants Allocation
  Owners: Skylar Saveland <skylar@free2z.com>
          Jason McGee <>
  Credits: @daira
           @str4d
           @nuttycom
  Status: Draft
  Category: Consensus
  Created: 2024-06-26
  License: MIT
  Pull-Request: <https://github.com/zcash/zips/pull/858>


Terminology
===========

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [#BCP14]_ when, and
only when, they appear in all capitals.

.. {Avoid duplicating definitions from other ZIPs. Instead use wording like this:}

.. The terms "Mainnet" and "Testnet" in this document are to be interpreted as
.. defined in the Zcash protocol specification [#protocol-networks]_.

.. The term "full validator" in this document is to be interpreted as defined in
.. the Zcash protocol specification [#protocol-blockchain]_.

.. The terms below are to be interpreted as follows:

.. {Term to be defined}
..   {Definition.}
.. {Another term}
..   {Definition.}


.. |percentage| replace:: 50%


Abstract
========

This ZIP proposes the allocation of |percentage| of the Zcash block reward,
post-November 2024 halving, to a decentralized "lockbox." Currently, 80% of the
block reward goes to miners, while 20% is distributed among the Major Grants
Fund (ZCG), Electric Coin Company (ECC), and the Zcash Foundation (ZF). If no
changes are made, this 20% dev fund will expire, resulting in the entire block
reward going to miners, leaving no block-reward funds for essential protocol
development, security, marketing, or legal expenses.

The proposed lockbox addresses significant issues observed with [#zip-1014]_,
such as regulatory risks, inefficiencies in funding organizations instead of
projects, tax compliance inefficiencies, and centralization. While the exact
disbursement mechanism for the lockbox funds is yet to be determined, the goal
is to employ a decentralized mechanism resembling a DAO, ensuring community
involvement and efficient, project-specific funding. This approach is intended
to improve regulatory compliance, reduce inefficiencies, simplify tax compliance,
and enhance the decentralization of Zcash's funding structure.

Motivation
==========

As of now, the Zcash block reward is allocated with 80% going to miners, and
the remaining 20% distributed among the Major Grants Fund (8%), Electric Coin
Company (ECC) (7%), and the Zcash Foundation (ZF) (5%). This funding structure
supports various essential activities such as protocol development, security,
marketing, and legal expenses. However, this model will expire in November
2024, leading to the entire block reward being allocated to miners if no
changes are made. This expiration poses several significant issues:

1. **Regulatory Risks**: The current model, as observed with ZIP-1014, involves
   direct funding of US-based organizations. This can potentially attract
   regulatory scrutiny from entities such as the SEC, posing legal risks to the
   Zcash ecosystem.

2. **Funding Inefficiencies**: Directly funding organizations rather than
   specific projects leads to inefficiencies. Organizations may accumulate
   excess funds while specific projects may not receive adequate resources. A
   more granular approach, funding projects directly, would be more efficient.

3. **Centralization Concerns**: The existing funding model centralizes
   decision-making power within a few organizations, which contradicts the
   decentralized ethos of blockchain technology. Traditional organizational
   structures with boards and executives introduce a single point of failure
   and limit community involvement in funding decisions.

4. **Community Involvement**: The current system provides minimal formal input
   from the community regarding what projects should be funded. This lack of
   community involvement can lead to misalignment between funded projects and
   community priorities.

5. **Tax Inefficiency**: While 501(c)(3) organizations do not
   immediately pay taxes on received block rewards, the need to convert rewards
   to USD for operational expenses triggers tax liabilities for. This often
   requires immediate liquidation of some block rewards, which is financially
   inefficient. The proposed lockbox mechanism has the potential to defer
   taxable events until the liquidation of funds by recipients, allowing for
   greater flexibility and efficiency in handling tax liabilities. This
   deferred approach could reduce the need for immediate liquidation and
   improve overall use of the block reward resources.

Given these issues, this ZIP proposes the creation of a decentralized "lockbox"
to which |percentage| of the Zcash block reward will be allocated post-November
2024 halving. The funds in this lockbox will only be disbursed through a
decentralized mechanism resembling a DAO. This new approach aims to:

- Reduce regulatory risks by avoiding direct funding of specific organizations.
- Improve funding efficiency by allocating resources directly to projects
  rather than organizations.
- Simplify tax compliance by allowing recipients to handle tax liabilities
  according to their circumstances.
- Enhance decentralization by distributing decision-making power and ensuring
  community involvement in funding decisions.

By addressing these issues, this proposal aims to ensure sustainable,
efficient, and decentralized funding for essential activities within the Zcash
ecosystem.

Requirements
============

1. **Decentralized Funding Mechanism**: The new funding model must implement a
   decentralized mechanism for disbursing funds. This mechanism should resemble
   a DAO, ensuring that the community has a direct say in funding decisions.
   This is crucial to avoid centralization and ensure transparency and fairness
   in the allocation of resources.

2. **Regulatory Compliance**: The proposed funding model must be designed to
   minimize regulatory risks. This involves avoiding direct funding of US-based
   organizations to prevent potential scrutiny from regulatory bodies such as
   the SEC. The mechanism should comply with applicable laws and regulations to
   ensure the long-term sustainability of the funding model.

3. **Efficiency in Funding Allocation**: The new model should focus on funding
   specific projects rather than organizations. This approach aims to ensure
   that resources are utilized efficiently and that projects receive the
   necessary support without accumulating excess funds in organizations.

4. **Simplified Tax Compliance**: The funding mechanism must simplify tax
   compliance for recipients. This can be achieved by deferring tax liabilities
   to the recipients, allowing them to handle taxes according to their
   circumstances, thus avoiding the need for organizations to sell block
   rewards to cover taxes.

5. **Community Involvement**: The funding model must enhance community
   involvement in decision-making processes. This includes mechanisms for the
   community to propose, discuss, and vote on projects that should receive
   funding. Ensuring broad community participation is key to aligning funded
   projects with the community's priorities.

6. **Security of Funds**: The mechanism for storing and disbursing funds must
   be secure. This includes protecting against key compromise, ensuring the
   integrity of the decentralized voting/signature mechanism, and implementing
   robust security measures to prevent unauthorized access or misuse of funds.

7. **Flexibility and Adaptability**: The new funding model should be flexible
   and adaptable to changing circumstances. This involves creating a system
   that can evolve based on feedback and new developments in the Zcash
   ecosystem, ensuring it remains relevant and effective over time.


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

Notes and warnings
------------------

.. note::
    "``.. note::``" in reStructuredText, or "``:::info``" (terminated by
    "``:::``") in Markdown, can be used for an aside from the main text.

    The rendering of notes is colourful and may be distracting, so they should
    only be used for important points.

.. warning::
    "``.. warning::``" in reStructuredText, or "``:::warning``" (terminated by
    "``:::``") in Markdown, can be used for warnings.

    Warnings should be used very sparingly — for example to signal that a
    entire specification, or part of it, may be inapplicable or could cause
    significant interoperability or security problems. In most cases, a "MUST"
    or "SHOULD" conformance requirement is more appropriate.

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

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to
    Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs
    Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#zip-1014] `ZIP 1014: Dev Fund Proposal and Governance <zip-1014.rst>`_
.. [#protocol] `Zcash Protocol Specification, Version 2022.3.8 or later <protocol/protocol.pdf>`_
.. [#protocol-introduction] `Zcash Protocol Specification, Version 2022.3.8. Section 1: Introduction <protocol/protocol.pdf#introduction>`_
.. [#protocol-blockchain] `Zcash Protocol Specification, Version 2022.3.8. Section 3.3: The Block Chain <protocol/protocol.pdf#blockchain>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#katex] `KaTeX - The fastest math typesetting library for the web <https://katex.org/>`_
.. [#zip-0000] `ZIP 0: ZIP Process <zip-0000.rst>`_
