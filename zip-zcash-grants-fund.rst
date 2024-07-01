::

  ZIP: 
  Title: Zcash Grants Fund
  Owners: Matthew Green (@gguy)
  Original-Authors: Matthew Green (@gguy)
  Status: Draft
  Category: Consensus Process
  Created: 2024-03-04
  License: MIT
  Discussions-To: ...
  Pull-Request: ...


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

The terms "Testnet" and "Mainnet" are to be interpreted as described in
section 3.12 of the Zcash Protocol Specification [#protocol-networks]_.


Abstract
========

This proposal describes a structure for the Zcash Grants Fund, to be
enacted in Network Upgrade 6 and lasting for {length} years. This Grants Fund would consist
of 20% of the block subsidies, split into 2 slices:
* {percent(0-20%)} to ZecHub for funding bounties focused on education and onboarding new users to the Zcash ecosystem;
* {percent(80-100%)} to "Zcash Community Grants" for funding grants that support projects and initiatives aligned with Zcash's mission (denoted ZCG slice).

Governance and accountability are based on existing entities and legal mechanisms,
and increasingly decentralized governance is encouraged.


Motivation
==========

## Motivation

Starting at Zcash's second halving in November 2024, the development fund will end, directing 100% of the block
subsidies to miners, resulting in no automatic funding for other entities. This change risks depriving
existing and new teams of essential funding. Establishing ongoing funding through grants ensures that
resources can continue to be allocated to initiatives deemed important by the community.

There is a critical need to balance incentivizing the security of the
consensus protocol (i.e., mining) with supporting charitable, educational, and
scientific endeavors, such as research, development, outreach, and future
funding needs of the network.

Additionally, there is a need to sustain the ongoing work of current teams
dedicated to Zcash while promoting decentralization and the growth of
independent development teams.

For these reasons, the Zcash Community proposes transitioning the Zcash
Development Fund to a Zcash Grants Fund. This fund will allocate a portion of
the block subsidies, which would otherwise go to miners, as grants to support
charitable, educational, and scientific activities within the meaning of
Section 501(c)(3). This approach will ensure continuous funding through a
structured grant application process, fostering the ongoing development and
decentralization of the Zcash ecosystem.

Requirements
============

The Grants Fund should encourage decentralization of the work and funding, by
supporting new teams dedicated to Zcash. The Grants Fund should maintain the
existing teams and capabilities in the Zcash ecosystem, unless and until
concrete opportunities arise to create even greater value for the Zcash ecosystem.

Grant funding decisions should be based, to the extent feasible, on inputs from
domain experts and pertinent stakeholders.

The Grants Fund mechanism should not modify the monetary emission curve (and in
particular, should not irrevocably burn coins).

In case the value of ZEC jumps, the Grant Fund recipients should not wastefully
use excessive amounts of funds. Conversely, given market volatility and eventual
halvings, it is desirable to create rainy-day reserves.

The Grants Fund mechanism should not reduce users' financial privacy or security.
In particular, it should not cause them to expose their coin holdings, nor
cause them to maintain access to secret keys for much longer than they would
otherwise. (This rules out some forms of voting, and of disbursing coins to
past/future miners.)

The new Grants Fund system should be simple to understand and realistic to
implement. In particular, it should not assume the creation of new mechanisms
(e.g., election systems) or entities (for governance or development) for its
execution; but it should strive to support and use these once they are built.

Comply with legal, regulatory, and taxation constraints in pertinent
jurisdictions.


Non-requirements
================

General on-chain governance is outside the scope of this proposal.

Rigorous voting mechanisms (whether coin-weighted, holding-time-weighted or
one-person-one-vote) are outside the scope of this proposal, though there is
prescribed room for integrating them once available.


Specification
=============

Consensus changes implied by this specification are applicable to the
Zcash Mainnet. Similar (but not necessarily identical) consensus changes
SHOULD be applied to the Zcash Testnet for testing purposes.


Dev Fund allocation
-------------------

Starting at the second Zcash halving in 2024, until {length},
20% of the block subsidy of each block SHALL be allocated to a "Grants Fund" that
consists of the following two slices:

* {percent(0-20%)} to ZecHub for funding bounties focused on education and onboarding new users to the Zcash ecosystem;
* {percent(80-100%)} to "Zcash Community Grants" for funding grants that support projects and initiatives aligned with Zcash's mission (denoted ZCG slice).

The slices are described in more detail below. The fund flow will be implemented
at the consensus-rule layer, by sending the corresponding ZEC to the designated
address(es) for each block. This Dev Fund will end at the second halving (unless
extended/modified by a future ZIP).


ZecHub
~~~~~~

This slice of the Zcash Grants Fund is dedicated to ZecHub, which is designed to play
a pivotal role in education and user onboarding within the Zcash ecosystem. ZecHub
aims to expand decentralized governance models and increase the utility of ZEC across
various chains. As a collaborative platform, ZecHub will engage the community in
creating, validating, and promoting open-source educational content that supports the
Zcash ecosystem. Upholding its core values, ZecHub asserts that privacy is a
fundamental human right, education should be open-source and accessible globally,
and community members have the right to earn ZEC privately. This allocation to ZecHub
will fund bounties that focus on these educational and developmental efforts, thereby
fostering a robust and inclusive community within the Zcash network.

The funds SHALL be received and administered by FPF. FPF MUST disburse them for
bounties and expenses reasonably related to the administration of bounties, but
subject to the following additional constraints:

1. These funds MUST primarily be used to issue bounties to external parties
   that are independent of FPF. They can also be used to fund other initiatives such
   as community support personnel and public goods projects that benefit Zcash, and
   to pay for expenses reasonably related to the administration of ZecHub. They MUST NOT
   be used by FPF for its internal operations and direct expenses not related to the
   administration of ZecHub.

2. ZecHub bounties SHOULD support work at reasonable market-rate costs.
   They can be of any duration or ongoing without a duration limit. Bounties of
   indefinite duration SHOULD have semiannual review points for continuation of funding.

3. Bounties SHOULD be restricted to furthering the Zcash cryptocurrency and
   its ecosystem (which is more specific than furthering financial privacy in
   general).

4. Bounty awards are subject to approval by ZecHub DAO.

5. The ZecHub DAO's funding decisions will be final, requiring
   no further approval, but are subject to veto if FPF
   judges them to violate laws or if FPF reporting requirements and other
   (current or future) obligations.

FPF SHALL recognize the ZCG slice of the Grants Fund as a Restricted Fund
donation under the above constraints (suitably formalized), and keep separate
accounting of its balance and usage under its `Transparency and Accountability`_
obligations defined below.

Zcash Community Grants (ZCG)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This slice of the Zcash Grants Fund is intended to fund independent teams entering the
Zcash ecosystem, to perform major ongoing development (or other work) that
benefits the public good within the Zcash ecosystem, to the extent that such
teams are available and effective. The Zcash Community Grants (ZCG) Committee is
given the discretion to allocate funds to a diverse range of projects that
advance the usability, security, privacy, and adoption of Zcash, including
community programs, dedicated resources, and other projects of varying sizes.

The funds SHALL be received and administered by {ZCG Administration}. {ZCG Administration} MUST disburse them for
grants and expenses reasonably related to the administration of grants, but subject to the following additional constraints:

1. These funds MUST primarily be used to issue grants to external parties
   that are independent of {ZCG Administration}. They can also be used to fund other initiatives such
   as community support personnel and public goods projects that benefit Zcash, and
   to pay for expenses reasonably related to the administration of Zcash Community
   Grants. They MUST NOT be used by {ZCG Administration} for its internal operations and direct
   expenses not related to administration of Zcash Community Grants.

2. Zcash Community Grants SHOULD support well-specified work proposed by the grantee,
   at reasonable market-rate costs. They can be of any duration or ongoing
   without a duration limit. Grants of indefinite duration SHOULD have
   semiannual review points for continuation of funding.

3. Priority SHOULD be given to grants that bolster teams with
   substantial (current or prospective) continual existence, and set them up
   for long-term success, subject to the usual grant award considerations
   (impact, ability, risks, team, cost-effectiveness, etc.). Priority SHOULD be
   given to grants that support ecosystem growth, for example through
   mentorship, coaching, technical resources, creating entrepreneurial
   opportunities, etc. If one proposal substantially duplicates another's
   plans, priority SHOULD be given to the originator of the plans.

4. Grants SHOULD be restricted to furthering the Zcash cryptocurrency and
   its ecosystem (which is more specific than furthering financial privacy in
   general) as permitted under Section 501(c)(3).

5. Grant awards are subject to approval by a five-seat Zcash Community
   Grants Committee. The Zcash Community Grants Committee SHALL be selected by the
   ZF's Community Advisory Panel or successor process. Elections SHALL be staggered to
   ensure continuity within the Committee.

6. The Zcash Community Grants Committee's funding decisions will be final, requiring
   no further approval, but are subject to veto if {ZCG Administration}
   judges them to violate laws or if {ZCG Administraion} reporting requirements and other
   (current or future) obligations under U.S. IRS 501(c)(3).

7. Zcash Community Grants Committee members SHALL have a one-year term and MAY sit
   for reelection. The Zcash Community Grants Committee is subject to the same
   conflict of interest policy that governs the ZF Board of Directors (i.e. they
   MUST recuse themselves when voting on proposals where they have a financial
   interest). At most one person with association with the BP/ECC, and at most
   one person with association with the ZF, are allowed to sit on the Major
   Grant Review Committee. "Association" here means: having a financial
   interest, full-time employment, being an officer, being a director, or having
   an immediate family relationship with any of the above. The ZF SHALL continue
   to operate the Community Advisory Panel and SHOULD work toward making it more
   representative and independent (more on that below).
   
   Zcash Community Grants Committee members are expected to work approximately 35
   hours per month and will be compensated accordingly from the Zcash Community Grants Committee
   budget. The total compensation for the committee is paid from the Zcash Community Grants Committee budget. 
   This works out to be a total of 175hours of compensation per month which is roughly the equivalent of a 
   signle full time position.
   
8. a portion of the ZCG Slice shall be allocated to a
   Discretionary Budget, which may be disbursed for expenses reasonably related
   to the administration of Zcash Community Grants. The amount of funds allocated to the
   Discretionary Budget SHALL be decided by the ZF's Community Advisory Panel or
   successor process. Any disbursement of funds from the Discretionary Budget
   MUST be approved by the Zcash Community Grants Committee. Expenses related to the
   administration of Zcash Community Grants include, without limitation the following:
   
   * Paying third party vendors for services related to domain name registration, or
     the design, website hosting and administration of websites for the Zcash Community Grants
     Committee.
   * Paying independent consultants to develop requests for proposals that align
     with the Zcash Community Grants program.
   * Paying independent consultants for expert review of grant applications.
   * Paying for sales and marketing services to promote the Zcash Community Grants
     program.
   * Paying third party consultants to undertake activities that support the
     purpose of the Zcash Community Grants program. 
   * Reimbursement to members of the Zcash Community Grants Committee for reasonable
     travel expenses, including transportation, hotel and meals allowance.

9. A portion of the Discretionary Budget MAY be allocated to provide reasonable
   compensation to members of the ZCG Committee. Committee member compensation
   SHALL be limited to the hours needed to successfully perform their positions
   and MUST align with the scope and responsibilities of their roles. The
   allocation and distribution of compensation to committee members SHALL be
   administered by the {ZCG Adminisration}. The compensation rate and hours for committee members SHALL be determined by
   the ZF’s Community Advisory Panel or successor process.

{ZCG Administration} SHALL recognize the ZCG slice of the Grants Fund as a Restricted Fund
donation under the above constraints (suitably formalized), and keep separate
accounting of its balance and usage under its `Transparency and Accountability`_
obligations defined below.


Transparency and Accountability
-------------------------------

Obligations
~~~~~~~~~~~

ZCG and ZecHub (during and leading to their award
period) SHALL all accept the obligations in this section.

Ongoing public reporting requirements:

* Quarterly reports, detailing future plans, execution on previous plans, and
  finances (balances, and spending broken down by major categories).
* Monthly developer calls, or a brief report, on recent and forthcoming tasks.
  (Developer calls may be shared.)
* Annual detailed review of the organization performance and future plans.
* Annual financial report (IRS Form 990, or substantially similar information).

These reports may be either organization-wide, or restricted to the income,
expenses, and work associated with the receipt of Zcash Grants Fund.

It is expected that Zcash Community Grants recipients will be focused
primarily (in their attention and resources) on Zcash. Thus, they MUST
promptly disclose:

* Any major activity they perform (even if not supported by the Grants Fund) that
  is not in the interest of the general Zcash ecosystem.
* Any conflict of interest with the general success of the Zcash ecosystem.

Zcash Community Grants and ZecHub MUST promptly disclose any security or privacy
risks that may affect users of Zcash (by responsible disclosure under
confidence to the pertinent developers, where applicable).

All substantial software whose development was funded by the Dev Fund SHOULD
be released under an Open Source license (as defined by the Open Source
Initiative [#osd]_), preferably the MIT license.


Enforcement
~~~~~~~~~~~

For Zcash Community Grants recipients, these conditions SHOULD be included in their contract
with {ZCG Administration}, such that substantial violation, not promptly remedied, will cause
forfeiture of their grant funds and their return to {ZCG Administration}.

{ZCG Adminisration} and FPF MUST contractually commit to each other to fulfill these
conditions, and the prescribed use of funds, such that substantial violation,
not promptly remedied, will permit the other parties to issue a modified version
of Zcash node software that removes the violating party's Grants Fund slice, and
use the Zcash trademark for this modified version. The slice's funds will be
unallocated until ZF’s Community Advisory Panel or successor process is able to decide on a new allocation.


Acknowledgements
================

This proposal is a modification of Zooko Wilcox and Andrew Miller's ZIP 1014
[#zip-1012]_ with feedback from the community.

The authors are grateful to all of the above for their excellent ideas and
any insightful discussions.

.. _Zcash Community Forum: https://forum.zcashcommunity.com/


References
==========

.. [#RFC2119] `RFC 2119: Key words for use in RFCs to Indicate Requirement Levels <https://www.rfc-editor.org/rfc/rfc2119.html>`_
.. [#protocol] `Zcash Protocol Specification, Version 2021.2.16 or later <protocol/protocol.pdf>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2021.2.16. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#trademark] `Zcash Trademark Donation and License Agreement <https://electriccoin.co/wp-content/uploads/2019/11/Final-Consolidated-Version-ECC-Zcash-Trademark-Transfer-Documents-1.pdf>`_
.. [#osd] `The Open Source Definition <https://opensource.org/osd>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <zip-0200.rst>`_
.. [#zip-1014] `ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants <zip-1014.rst>`_
.. [#zf-community] `ZF Community Advisory Panel <https://www.zfnd.org/governance/community-advisory-panel/>`_
.. [#section501c3] `U.S. Code, Title 26, Section 501(c)(3) <https://www.law.cornell.edu/uscode/text/26/501>`_
