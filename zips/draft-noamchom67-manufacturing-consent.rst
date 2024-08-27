::

  ZIP: ####
  Title: Manufacturing Consent; Re-Establishing a Dev Fund for ECC, ZF, ZCG, Qedit, FPF, and ZecHub
  Owner: Noam Chom <noamchom1967@gmail.com>
  Credits: The ZIP-1014 Authors
  Status: Withdrawn
  Category: Consensus Process
  Created: 2024-06-25
  License: MIT
  Discussions-To: <https://forum.zcashcommunity.com/t/manufacturing-consent-noamchoms-nu6-block-reward-proposal/47155>
  Pull-Request: TBD


Terminology
===========

The key words "MUST", "MUST NOT", "SHALL", "SHALL NOT", "SHOULD", and "MAY"
in this document are to be interpreted as described in BCP 14 [#BCP14]_ when,
and only when, they appear in all capitals.

The term "network upgrade" in this document is to be interpreted as
described in ZIP 200 [#zip-0200]_ and the Zcash Trademark Donation and License
Agreement ([#trademark]_ or successor agreement).

The terms "block subsidy" and "halving" in this document are to be interpreted
as described in sections 3.10 and 7.8 of the Zcash Protocol Specification.
[#protocol]_

"Electric Coin Company", also called "ECC", refers to the Zerocoin Electric
Coin Company, LLC.

"Bootstrap Project", also called "BP", refers to the 501(c)(3) nonprofit
corporation of that name.

"Zcash Foundation", also called "ZF", refers to the 501(c)(3) nonprofit
corporation of that name.

"Section 501(c)(3)" refers to that section of the U.S. Internal Revenue
Code (Title 26 of the U.S. Code). [#section501c3]_

"Community Advisory Panel" refers to the panel of community members assembled
by the Zcash Foundation and described at [#zf-community]_.

"Zcash Community Grants", also called "ZCG", refers to grants program
(formerly known as ZOMG) that funds independent teams entering the Zcash ecosystem, 
to perform major ongoing development (or other work) 
for the public good of the Zcash ecosystem.
<https://zcashcommunitygrants.org/>

"Financial Privacy Foundation", also called "FPF" refers to the start-up non-profit
organization incorporated and based in the Cayman Islands.
<https://www.financialprivacyfoundation.org/>

"Qedit" refers to the company founded in 2016 by a world-class team of 
accomplished tech entrepreneurs, researchers, and developers; 
QEDIT has emerged as a global leader in the field of Zero-Knowledge Proofs.
<https://qed-it.com/about-us/>

"ZecHub" refers to the team of content creators who have supported Zcash
through a series of ZCG approved grants.
<https://forum.zcashcommunity.com/t/zechub-an-education-hub-for-zcash-2024-continued/47947>

The terms "Testnet" and "Mainnet" are to be interpreted as described in
section 3.12 of the Zcash Protocol Specification [#protocol-networks]_.

The term "ZSA" is to be interpreted as "Zcash Shielded Assets" the protocol
feature enhancement (and subsequent application layer, legal, maintenance 
efforts, et al) on-going by Qedit, et al.
<https://forum.zcashcommunity.com/t/grant-update-zcash-shielded-assets-monthly-updates/41153>

✳️ is used to denote elements of the process part of the ZIP that are still
to-be-determined.


Abstract
========

This proposal describes a structure for the Zcash Development Fund, to be
enacted in Network Upgrade 6 and last for 4 years. This Dev Fund would consist
of 15% of the block subsidies, as the following allocations:

* 5% for the Zcash Foundation (for internal work and grants);
* 4% for the Bootstrap Project (the parent of the Electric Coin Company) for the 1st year only;
* 4% for Zcash Community Grants for continuation of their current activities as-is;
* 2% for Qedit in support of their ZSA activities, and other Zcash protocol support;

Following the first year, when ECC will no longer receive their 4% allocation, 
those block subsidies will be distributed as 1% to ZCG, 1% to ZecHub, 1% to FPF,
and 1% to ZF.

Governance and accountability are based on existing entities and legal mechanisms,
and increasingly decentralized governance is encouraged.  This proposal mandates 
the ecosystem to design and deploy a "non-direct funding model" as generally
recommended in Josh Swihart's proposal. [#draft-swihart]_

Upon creation/ activation of a "non-direct funding model" this ZIP should be 
reconsidered (potentially terminated) by the Zcash ecosystem, to determine 
if its ongoing direct block subsidies are preferred for continuation.
Discussions/ solications/ sentiment gathering from the Zcash
ecosystem should be initiated ~6 months in advance of the presumed
activation of a "non-direct funding model", such that the Zcash ecosystem
preference can be expediently realized.

Block subsidies will be administered through two organizations:

1. Zcash Foundation  (✳️ for ECC, ZCG)
2. Financial Privacy Foundation (✳️ for Qedit, ZecHub)

✳️ **ZF and FPF adminstration of block subsidy details, costs, et al are currently under debate**
[#zf-fpf-admin-details]_


Motivation
==========

As of Zcash's second halving in November 2024, by default 100% of the block
subsidies will be allocated to miners, and no further funds will be automatically
allocated to any other entities. Consequently, no new funding
may be available to existing teams dedicated to furthering charitable,
educational, or scientific purposes, such as research, development, and outreach:
the Electric Coin Company (ECC), the Zcash Foundation (ZF), the ZCG, and the many
entities funded by the ZF and ZCG grant programs.

There is a need to strike a balance between incentivizing the security of the
consensus protocol (i.e., mining) versus crucial charitable, educational, and/or
scientific aspects, such as research, development and outreach.

Furthermore, there is a need to balance the sustenance of ongoing work by the
current teams dedicated to Zcash, with encouraging decentralization and growth
of independent development teams.

For these reasons, the Zcash Community desires to allocate and
contribute a portion of the block subsidies otherwise allocated to
miners as a donation to support charitable, educational, and
scientific activities within the meaning of Section 501(c)(3).

This proposal also introduces the benefit of a non-USA based entity (FPF) as 
the administrator for block subsidies to two organizations that are also 
non-USA based (Qedit and ZecHub). USA based regulatory risk continues to
(negatively) impact the Zcash project, which has been predominantly based in the USA.


Requirements
============

The Dev Fund should encourage decentralization of the work and funding, by
supporting new teams dedicated to Zcash.

The Dev Fund should maintain the existing teams and capabilities in the Zcash
ecosystem, unless and until concrete opportunities arise to create even greater
value for the Zcash ecosystem.

There should not be any single entity which is a single point of failure, i.e.,
whose capture or failure will effectively prevent effective use of the funds.

Major funding decisions should be based, to the extent feasible, on inputs from
domain experts and pertinent stakeholders.

The Dev Fund mechanism should not modify the monetary emission curve (and in
particular, should not irrevocably burn coins).

In case the value of ZEC jumps, the Dev Fund recipients should not wastefully
use excessive amounts of funds. Conversely, given market volatility and eventual
halvings, it is desirable to create rainy-day reserves.

The Dev Fund mechanism should not reduce users' financial privacy or security.
In particular, it should not cause them to expose their coin holdings, nor
cause them to maintain access to secret keys for much longer than they would
otherwise. (This rules out some forms of voting, and of disbursing coins to
past/future miners.)

The Dev Fund system should be simple to understand and realistic to
implement. In particular, it should not assume the creation of new mechanisms
(e.g., election systems) or entities (for governance or development) for its
execution; but it should strive to support and use these once they are built.

Dev Fund recipients should comply with legal, regulatory, and taxation
constraints in their pertinent jurisdiction(s).


Non-requirements
================

General on-chain governance is outside the scope of this proposal.

Rigorous voting mechanisms (whether coin-weighted, holding-time-weighted or
one-person-one-vote) are outside the scope of this proposal, however this 
proposal does mandate the undertaking of the project to build a "non-direct
funding model" as generally described in [#draft-swihart]_.

Specification
=============

Consensus changes implied by this specification are applicable to the
Zcash Mainnet. Similar (but not necessarily identical) consensus changes
SHOULD be applied to the Zcash Testnet for testing purposes.


Dev Fund allocation
-------------------

Starting at the second Zcash halving in 2024, until the third halving in 2028,
15% of the block subsidy of each block SHALL be allocated to a "Dev Fund" that
consists of the following allocations:

* 5% for the Zcash Foundation (for internal work and grants);
* 4% for the Bootstrap Project (the parent of the Electric Coin Company) for the 1st year only; 
* 4% for Zcash Community Grants for continuation of their current activities as-is;
* 2% for Qedit in support of their ZSA activities, and other Zcash protocol support;

Following the first year, when ECC will no longer receive their 4% allocation, 
those block subsidies will be distributed as 1% to ZCG, 1% to ZecHub, 1% to FPF,
and 1% to ZF.

This proposal mandates the ecosystem to design and deploy a "non-direct funding model"
as generally recommended in Josh Swihart's proposal [#draft-swihart]_.

"Dev Fund" block subsidies will be administered through two organizations:

1. Zcash Foundation  (✳️ for ECC, ZCG)
2. Financial Privacy Foundation (✳️ for Qedit, ZecHub)

✳️ **ZF and FPF adminstration of block subsidy details, costs, et al are currently under debate**
[#zf-fpf-admin-details]_

The allocations are described in more detail below. The fund flow will be implemented
at the consensus-rule layer, by sending the corresponding ZEC to the designated
address(es) for each block. This Dev Fund will end at the third halving (unless
extended/modified by a future ZIP).


BP allocation (Bootstrap Project)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

✳️ These funds SHALL be received and administered by ZF.

This allocation of the Dev Fund will flow as charitable contributions from
the Zcash Community to the Bootstrap Project, the newly formed parent
organization to the Electric Coin Company. The Bootstrap Project is organized
for exempt educational, charitable, and scientific purposes in
compliance with Section 501(c)(3), including but not
limited to furthering education, information, resources, advocacy,
support, community, and research relating to cryptocurrency and
privacy, including Zcash. This allocation will be used at the discretion of
the Bootstrap Project for any purpose within its mandate to support financial
privacy and the Zcash platform as permitted under Section 501(c)(3). The
BP allocation will be treated as a charitable contribution from the
Community to support these educational, charitable, and scientific
purposes.


ZF allocation (Zcash Foundation's general use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This allocation of the Dev Fund will flow as charitable contributions from
the Zcash Community to ZF, to be used at its discretion for any
purpose within its mandate to support financial privacy and the Zcash
platform, including: development, education, supporting community
communication online and via events, gathering community sentiment,
and awarding external grants for all of the above, subject to the
requirements of Section 501(c)(3). The ZF allocation will be
treated as a charitable contribution from the Community to support
these educational, charitable, and scientific purposes.


Zcash Community Grants (ZCG)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This allocation of the Dev Fund is intended to fund independent teams entering the
Zcash ecosystem, to perform major and minor ongoing development (or other work) for the
public good of the Zcash ecosystem, to the extent that such teams are available
and effective.

✳️ These funds SHALL be received and administered by ZF (or FPF, pending TBD outcomes
of FPF proposal: [#zf-fpf-admin-details]_).
ZF MUST disburse them for "Major Grants" and expenses reasonably related to
the administration of Major Grants, but subject to the following additional constraints:

1. These funds MUST only be used to issue Major Grants to external parties
   that are independent of ZF, and to pay for expenses reasonably related to 
   the administration of Major Grants. They MUST NOT be used by ZF for its 
   internal operations and direct expenses not related to administration of 
   Major Grants. Additionally, BP, ECC, and ZF are ineligible to receive 
   Major Grants.

2. Major Grants SHOULD support well-specified work proposed by the grantee,
   at reasonable market-rate costs. They can be of any duration or ongoing
   without a duration limit. Grants of indefinite duration SHOULD have
   semiannual review points for continuation of funding.

3. Priority SHOULD be given to Major Grants that bolster teams with
   substantial (current or prospective) continual existence, and set them up
   for long-term success, subject to the usual grant award considerations
   (impact, ability, risks, team, cost-effectiveness, etc.). Priority SHOULD be
   given to Major Grants that support ecosystem growth, for example through
   mentorship, coaching, technical resources, creating entrepreneurial
   opportunities, etc. If one proposal substantially duplicates another's
   plans, priority SHOULD be given to the originator of the plans.

4. Major Grants SHOULD be restricted to furthering the Zcash cryptocurrency and
   its ecosystem (which is more specific than furthering financial privacy in
   general) as permitted under Section 501(c)(3).

5. Major Grants awards are subject to approval by a five-seat Major Grant
   Review Committee. The Major Grant Review Committee SHALL be selected by the
   ZF's Community Advisory Panel or successor process.

6. The Major Grant Review Committee's funding decisions will be final, requiring
   no approval from the ZF Board, but are subject to veto if the Foundation
   judges them to violate U.S. law or the ZF's reporting requirements and other
   (current or future) obligations under U.S. IRS 501(c)(3).

7. Major Grant Review Committee members SHALL have a one-year term and MAY sit
   for reelection. The Major Grant Review Committee is subject to the same
   conflict of interest policy that governs the ZF Board of Directors (i.e. they
   MUST recuse themselves when voting on proposals where they have a financial
   interest). At most one person with association with the BP/ECC, and at most
   one person with association with the ZF, are allowed to sit on the Major
   Grant Review Committee. "Association" here means: having a financial
   interest, full-time employment, being an officer, being a director, or having
   an immediate family relationship with any of the above. The ZF SHALL continue
   to operate the Community Advisory Panel and SHOULD work toward making it more
   representative and independent (more on that below).
   
8. From 1st January 2022, a portion of the MG allocation shall be allocated to a 
   Discretionary Budget, which may be disbursed for expenses reasonably related 
   to the administration of Major Grants. The amount of funds allocated to the 
   Discretionary Budget SHALL be decided by the ZF's Community Advisory Panel or 
   successor process. Any disbursement of funds from the Discretionary Budget 
   MUST be approved by the Major Grant Review Committee. Expenses related to the 
   administration of Major Grants include, without limitation the following:
   
   * Paying third party vendors for services related to domain name registration, or
     the design, website hosting and administration of websites for the Major Grant 
     Review Committee.
   * Paying independent consultants to develop requests for proposals that align 
     with the Major Grants program.
   * Paying independent consultants for expert review of grant applications.
   * Paying for sales and marketing services to promote the Major Grants 
     program.
   * Paying third party consultants to undertake activities that support the 
     purpose of the Major Grants program. 
   * Reimbursement to members of the Major Grant Review Committee for reasonable 
     travel expenses, including transportation, hotel and meals allowance.
     
   The Major Grant Review Committee's decisions relating to the allocation and 
   disbursement of funds from the Discretionary Budget will be final, requiring 
   no approval from the ZF Board, but are subject to veto if the Foundation 
   judges them to violate U.S. law or the ZF's reporting requirements and other 
   (current or future) obligations under U.S. IRS 501(c)(3).

ZF SHALL recognize the MG allocation of the Dev Fund as a Restricted Fund
donation under the above constraints (suitably formalized), and keep separate
accounting of its balance and usage under its `Transparency and Accountability`_
obligations defined below.

ZF SHALL strive to define target metrics and key performance indicators,
and the Major Grant Review Committee SHOULD utilize these in its funding
decisions.


Qedit
~~~~~

✳️ These funds SHALL be received and administered by FPF.

This allocation of the Dev Fund will flow as charitable contributions from
the Zcash Community to Qedit, for the purposes of supporting their ongoing
activities related to Zcash Shielded Assets, and related protocol/ application/ 
legal/ and other efforts.

ZecHub
~~~~~~

✳️ These funds SHALL be received and administered by FPF.

This allocation of the Dev Fund will flow as charitable contributions from
the Zcash Community to ZecHub, for the purposes of continuing their 
ongoing content contributions, community organizing, et al within the
Zcash ecosystem.


Transparency and Accountability
-------------------------------

Obligations
~~~~~~~~~~~

BP, ECC, ZF, ZCG, Qedit, FPF and ZecHub are recommended to accept the obligations in this section.

Ongoing public reporting requirements:

* Quarterly reports, detailing future plans, execution on previous plans, and
  finances (balances, and spending broken down by major categories).
* Monthly developer calls, or a brief report, on recent and forthcoming tasks.
  (Developer calls may be shared.)
* Annual detailed review of the organization performance and future plans.
* Annual financial report (IRS Form 990, or substantially similar information).

These reports may be either organization-wide, or restricted to the income,
expenses, and work associated with the receipt of Dev Fund.
As BP is the parent organization of ECC it is expected they may publish
joint reports.

It is expected that ECC, ZF, and ZCG will be focused
primarily (in their attention and resources) on Zcash. Thus, they MUST
promptly disclose:

* Any major activity they perform (even if not supported by the Dev Fund) that
  is not in the interest of the general Zcash ecosystem.
* Any conflict of interest with the general success of the Zcash ecosystem.

BP, ECC, ZF, and grant recipients MUST promptly disclose any security or privacy
risks that may affect users of Zcash (by responsible disclosure under
confidence to the pertinent developers, where applicable).

BP's reports, ECC's reports, and ZF's annual report on its non-grant operations,
SHOULD be at least as detailed as grant proposals/reports submitted by other
funded parties, and satisfy similar levels of public scrutiny.

All substantial software whose development was funded by the Dev Fund SHOULD
be released under an Open Source license (as defined by the Open Source
Initiative [#osd]_), preferably the MIT license.


Enforcement
~~~~~~~~~~~

For grant recipients, these conditions SHOULD be included in their contract
with ZF, such that substantial violation, not promptly remedied, will cause
forfeiture of their grant funds and their return to ZF.

BP, ECC, and ZF MUST contractually commit to each other to fulfill these
conditions, and the prescribed use of funds, such that substantial violation,
not promptly remedied, will permit the other party to issue a modified version
of Zcash node software that removes the violating party's Dev Fund allocation, and
use the Zcash trademark for this modified version. The allocation's funds will be
reassigned to MG (whose integrity is legally protected by the Restricted
Fund treatment).


Future Community Governance
---------------------------

It is highly desirable to develop robust means of decentralized community
voting and governance –either by expanding the Zcash Community Advisory Panel or a
successor mechanism– and to integrate them into this process by the end of
2025. BP, ECC, ZCG, and ZF SHOULD place high priority on such development and its
deployment, in their activities and grant selection.


ZF Board Composition
--------------------

Members of ZF's Board of Directors MUST NOT hold equity in ECC or have current
business or employment relationships with ECC, except as provided for by the
grace period described below.

Grace period: members of the ZF board who hold ECC equity (but do not have other
current relationships to ECC) may dispose of their equity, or quit the Board,
by 21 November 2024. (The grace period is to allow for orderly replacement, and
also to allow time for ECC corporate reorganization related to Dev Fund
receipt, which may affect how disposition of equity would be executed.)

The Zcash Foundation SHOULD endeavor to use the Community Advisory Panel (or
successor mechanism) as advisory input for future board elections.


Acknowledgements
================

This proposal is a modification of ZIP 1014 [#zip-1014]_
and a modification from the original "Manufacturing Consent" proposal 
as described in the Zcash Forum, in response to observable Zcash
community sentiment.

The author is grateful to everyone in the Zcash ecosystem.


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#protocol] `Zcash Protocol Specification, Version 2021.2.16 or later <protocol/protocol.pdf>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2021.2.16. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#trademark] `Zcash Trademark Donation and License Agreement <https://electriccoin.co/wp-content/uploads/2019/11/Final-Consolidated-Version-ECC-Zcash-Trademark-Transfer-Documents-1.pdf>`_
.. [#osd] `The Open Source Definition <https://opensource.org/osd>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <zip-0200.rst>`_
.. [#zip-1003] `ZIP 1003: 20% Split Evenly Between the ECC and the Zcash Foundation, and a Voting System Mandate <zip-1003.rst>`_
.. [#zip-1010] `ZIP 1010: Compromise Dev Fund Proposal With Diverse Funding Streams <zip-1010.rst>`_
.. [#zip-1011] `ZIP 1011: Decentralize the Dev Fee <zip-1011.rst>`_
.. [#zip-1014] `ZIP 1012: Dev Fund to ECC + ZF + Major Grants <zip-1014.rst>`_
.. [#zf-community] `ZF Community Advisory Panel <https://www.zfnd.org/governance/community-advisory-panel/>`_
.. [#section501c3] `U.S. Code, Title 26, Section 501(c)(3) <https://www.law.cornell.edu/uscode/text/26/501>`_
.. [#draft-swihart] `Zcash Funding Bloc : A Dev Fund Proposal from Josh at ECC <https://forum.zcashcommunity.com/t/zcash-funding-bloc-a-dev-fund-proposal-from-josh-at-ecc/47187>`_
.. [#zf-fpf-admin-details] `Proposal: ZCG under FPF <https://forum.zcashcommunity.com/t/proposal-zcg-under-fpf/48113/11>`_
