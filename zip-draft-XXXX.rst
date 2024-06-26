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
post-November 2024 halving, to an in-protocol "lockbox." Currently, 80% of the
block reward goes to miners, while 20% is distributed among the Major Grants
Fund (ZCG), Electric Coin Company (ECC), and the Zcash Foundation (ZF). If no
changes are made, this 20% dev fund will expire, resulting in the entire block
reward going to miners, leaving no block-reward funds for essential protocol
development, security, marketing, or legal expenses.

The proposed lockbox addresses significant issues observed with [#zip-1014]_,
such as regulatory risks, inefficiencies in funding organizations instead of
projects, and centralization. While the exact disbursement mechanism for the
lockbox funds is yet to be determined and will be addressed in a future ZIP,
the goal is to employ a decentralized mechanism resembling a DAO, ensuring
community involvement and efficient, project-specific funding. This approach is
intended to potentially improve regulatory compliance, reduce inefficiencies,
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

5. **Potential Tax Efficiency**: By potentially deferring taxable events until
   the liquidation of funds by recipients, the proposed lockbox mechanism could
   allow for more flexibility in handling tax liabilities. This approach could
   reduce the need for immediate liquidation and improve the overall use of
   block reward resources compared to directly funding US-based organizations
   with a USD bottom line.

Given these issues, this ZIP proposes the creation of a decentralized "lockbox"
to which |percentage| of the Zcash block reward will be allocated post-November
2024 halving. The exact disbursement mechanism for the lockbox funds will be
determined in a future ZIP, but the goal is to ensure:

- Reduced regulatory risks by avoiding direct funding of specific organizations.
- Improved funding efficiency by allocating resources directly to projects
  rather than organizations.
- Enhanced decentralization by distributing decision-making power and ensuring
  community involvement in funding decisions.

By addressing these issues, this proposal aims to ensure sustainable,
efficient, and decentralized funding for essential activities within the Zcash
ecosystem.

Requirements
============

1. **In-Protocol Lockbox Creation**: The ZIP must define the creation of an
   in-protocol lockbox where |percentage| of the Zcash block reward will be
   allocated post-November 2024 halving. This lockbox will securely store funds
   until a disbursement mechanism is established in a future ZIP.

2. **Decentralization Goal**: The lockbox must be designed with the goal of
   future decentralization in mind. While the disbursement mechanism will be
   defined later, the lockbox should support the principles of decentralization
   to ensure future community involvement and project-specific funding.

3. **Regulatory Considerations**: The creation of the lockbox should minimize
   regulatory risks by avoiding direct funding of specific organizations. The
   design should ensure compliance with applicable laws and regulations to
   support the long-term sustainability of the funding model.

4. **Efficient Allocation Preparation**: The lockbox must be prepared to
   allocate resources efficiently once the disbursement mechanism is defined.
   This includes ensuring that funds are readily available for future projects
   and not tied up in organizational overhead.

5. **Potential Tax Efficiency**: The lockbox should be designed with the
   potential to defer taxable events until the liquidation of funds by
   recipients, allowing for more flexibility in handling tax liabilities
   compared to direct funding of US-based organizations.

6. **Security of Funds**: The lockbox must implement robust security measures
   to protect against unauthorized access or misuse of funds. This includes
   ensuring the integrity of the future decentralized voting/signature
   mechanism.

7. **Future Adaptability**: The lockbox design should be flexible and adaptable
   to accommodate the disbursement mechanism defined in a future ZIP. This
   ensures that the system can evolve based on feedback and new developments in
   the Zcash ecosystem.


Non-requirements
================

This ZIP specifically addresses the creation of an in-protocol "lockbox" for
accumulating a portion of the Zcash block reward post-November 2024 halving.
The following aspects are explicitly deferred to future ZIPs and are not
covered by this proposal:

1. **Disbursement Mechanism**: The exact method for disbursing the accumulated
   funds from the lockbox is not defined in this ZIP. The design,
   implementation, and governance of the disbursement mechanism will be
   addressed in a future ZIP. This includes specifics on how funds will be
   allocated, the voting or decision-making process, and the structure of the
   decentralized mechanism (such as a DAO).

2. **Specific Allocation Percentages**: While this ZIP proposes the allocation
   of |percentage| of the block reward to the lockbox, it does not prescribe
   the detailed percentages for various funding categories or the specific
   amounts that will be distributed to different projects or entities.

3. **Regulatory Compliance Details**: The proposal outlines the potential to
   reduce regulatory risks by avoiding direct funding of US-based
   organizations, but it does not detail specific regulatory compliance
   strategies. Future ZIPs will need to address how the disbursement mechanism
   complies with applicable laws and regulations.

4. **Technical Implementation**: The technical specifics of how the lockbox
   will be integrated into the Zcash protocol, including any necessary changes
   to the codebase and the precise methods for ensuring security and
   transparency, are not covered in this ZIP. These details will be provided in
   subsequent proposals and technical documentation.

5. **Taxation Strategy**: Although the potential for improved tax efficiency is
   mentioned, this ZIP does not provide a detailed strategy for managing tax
   liabilities. Future ZIPs will explore the implications of tax compliance and
   the best methods for handling taxable events related to the disbursement of
   funds.

6. **Impact Assessment**: The long-term impact of reallocating a portion of the
   block reward to the lockbox on the Zcash ecosystem, including its effect on
   miners, developers, and the broader community, is not analyzed in this ZIP.
   Subsequent proposals will need to evaluate the outcomes and make necessary
   adjustments based on real-world feedback and data.

By focusing on the establishment of the lockbox, this ZIP aims to lay the
groundwork for a more decentralized and efficient funding mechanism. The
deferred issues will be crucial in shaping the final implementation and
ensuring the proposed system's success and sustainability.

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
