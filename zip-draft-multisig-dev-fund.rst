::

  ZIP: Unassigned
  Title: 2-of-3 Multisig Development Fund
  Owners: Mario Laul <mario@placeholder.vc>
          Chris Burniske <chris@placeholder.vc>
  Status: Draft
  Discussion: Zcash Forum [#FORUM1]_
  Category: Consensus
  Created: 2019-08-30
  License: MIT


Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be interpreted
as described in RFC 2119 [#RFC2119]_, both in terms of the technical specification and
governance rules of the Zcash Development Fund.

The terms below are to be interpreted as follows:

Mining
  The action of processing transactions, regardless of whether it is done in a Proof-of-Work,
  Proof-of-Stake, or Proof-of-Work/Proof-of-Stake hybrid system.
Mining software
  Mining pool software, local mining software, or staking software.
Mining rewards / Block rewards
  Transaction fees and coinbase rewards, i.e. fees paid for processing transactions and
  the newly issued ZEC associated with block generation.
Network upgrade
  Any planned change or set of changes to the Zcash software, introduced as part of the
  standard Network Upgrade Pipeline [#NUPIPELINE]_ or otherwise.
Zcash Development Fund
  A set of transparent addresses controlled jointly by the Electric Coin Company, the Zcash
  Foundation, and a Third Entity to be determined. It is used to hold funds intended for
  research, development, maintenance, and other types of technical work directly connected
  to the various software implementations of the Zcash protocol, as well as non-technical
  initiatives (including design, marketing, events, regulatory outreach, education,
  governance, and any other form of business or community development) that contribute
  to the long-term success of the Zcash network. In the context of this proposal, 20% of
  Zcash coinbase rewards between 2020 and 2024 halvings are automatically directed to
  the Zcash Development Fund, but this does not exclude other funding mechanisms, both
  during and after the aforementioned period.
Applicant
  Any individual, group, or entity that seeks funding from the Zcash Development Fund.
Recipient
  Any individual, group, or entity that receives funding from the Zcash Development Fund.

Abstract
========

This proposal puts forward the creation of the Zcash Development Fund and describes its
financing mechanism and fundamental rules of governance.


Specification
============

Funding mechanism of the Zcash Development Fund:

- This feature MUST be hard-coded so that 20% of newly issued ZEC in the mining rewards
associated with block generation are automatically directed to a set of transparent
addresses of the Zcash Development Fund, each controlled jointly by the ECC, the ZF,
and a Third Entity described below (2-of-3 multisig);

- The previous requirement MUST be met between the first (year 2020, at block height
840,000) and second (year 2024, at block height 1,680,000) halving. With the second
halving, the Zcash protocol MUST automatically shift to a system whereby all subsequent
mining rewards are earned by miners. The Zcash community MAY decide to change this in
the future, but prescribing or suggesting such change is not part of the current proposal;

- The two previous requirements MUST hold regardless of the Network Upgrades or changes
to mining or mining software introduced prior to second halving;

- The Zcash Development Fund MAY outlive the duration of its initial funding mechanism,
either through a substantial appreciation in the price of ZEC, or by switching to
alternative funding sources after the second halving in 2024.

Governance rules of the Zcash Development Fund:

- Funds accruing to the Zcash Development Fund MUST be used only for their intended purpose
as defined in the Motivation section of this proposal;

- The set of transparent addresses of the Zcash Development Fund MUST be jointly controlled
by the ECC, the ZF, and a third independent entity (“Third Entity”) still to be determined,
and all transfers from the Zcash Development Fund MUST be officially and publicly confirmed
by a majority decision among the ECC, the ZF, and the Third Entity (2-of-3 multisig). As such,
each funding decision MUST be put on an officially documented vote which MUST NOT pass
unless at least 2 of the 3 entities involved vote approvingly;

- Prior to any movement of funds from the Zcash Development Fund, the ZF and the ECC MUST
coordinate to establish the Third Entity that will be involved in the governance of the
Zcash Development Fund. The process of determining the exact initial composition and rules
of governance of the Third Entity MUST involve the Zcash community at large, similar to the
process around the issue described in the Motivation section of this proposal;

- The governance rules of the Third Entity MUST include the following:

  - All decision-making and other governing processes of the Third Entity MUST be independent
  of the ECC and the ZF, and MUST include measures that are necessary to avoid conflicts of
  interest in relation to the ECC and the ZF;
  
  - At creation, the Third Entity MUST include at least 5 individuals with independent previous
  affiliations, each having a single vote in decisions relating to the Zcash Development Fund.
  All such decisions MUST have majority support within the Third Entity to be approved;
  
  - Once the Third Entity is established, it MAY decide to change its rules of governance,
  but any such change MUST be preceded by the involvement of the Zcash community at large,
  similar to the process around the issue described in the Motivation section of this proposal;
  
  - Once the Third Entity is established as a self-governing body, it SHOULD evolve toward
  a system whereby ZEC holders have a direct role in determining the votes of the Third Entity
  in Zcash Development Fund funding decisions, as well as decisions relating to the governance
  of the Third Entity itself;
  
  - Just as the ECC and the ZF, the Third Entity MAY apply for funding from the Zcash
  Development Fund, should its governing body deem doing so appropriate.

- Prior to any movement of funds from the Zcash Development Fund, the ECC, the ZF, and the
Third Entity MUST specify, approve, and make public the final rules on applying for and
receiving funding from the Zcash Development Fund, including the details of the decision-making
process for approving or rejecting funding requests. These rules MUST apply equally to all
Applicants, including the ECC, the ZF, and the Third Entity, and MUST include the following:

  - Funding from the Zcash Development Fund MUST be available not only to the ECC, the ZF,
  and the Third Entity but also to other individuals, groups, or entities that have made
  or have a proven ability to make useful technical and/or non-technical contributions to
  Zcash as described in the Motivation section of this proposal;
  
  - To receive funding from the Zcash Development Fund, all Applicants MUST follow the rules
  described in this proposal and in final detail by the ECC, the ZF, and the Third Entity;
  
  - As part of their application, all Applicants MUST make public an overview of the
  activities and associated costs for which they are seeking funds for;
  
  - Each funding decision MUST be preceded by a community review period of reasonable length
  during which all Zcash stakeholders - should they wish to do so - can familiarize themselves
  with the Applicant’s request and ask for clarifying questions, make suggestions, or raise
  objections;
  
  - In case of substantial opposition among the broader Zcash community to approving a
  particular Applicant’s request, the ECC, the ZF, and the Third Entity SHOULD NOT approve
  it before considering ways to address the concerns raised by the community and change the
  funding request accordingly;
  
  - Each funding decision MUST be accompanied by a joint public statement by the ECC, the ZF,
  and the Third Entity (appropriately numbered and/or titled for easy referencing) which MUST
  include the final outcome of the relevant vote, as well as the votes of the three entities
  involved. As part of this statement, each of the three entities MUST provide an explicit
  justification for why the Applicant’s funding request was approved or rejected by the
  respective organization;
  
  - Zcash Development Fund votes and the accompanying justifications described in the previous
  point MUST be archived and kept publicly available by the ZF so that all current and future
  Zcash stakeholders can review the history of voting and resource allocation of the Zcash
  Development Fund;
  
  - The ECC, the ZF, and the Third Entity MAY approve funding requests on a rolling basis,
  but at a minimum a vote MUST take place every 6 months that includes all funding requests
  that have been submitted since the previous vote and meet the requirements set by this
  proposal and in final detail by the ECC, the ZF, and the Third Entity;
  
  - Recipients MUST publicize regular (at least every quarter) progress updates on their
  activities funded from the Zcash Development Fund. In the case of short-term work (up to
  3-5 months), a single progress report upon the completion of the project is sufficient.
  Default reporting requirements MUST be specified by the ECC, the ZF, and the Third Entity
  prior to any movement of funds from the Zcash Development Fund and additional requirements
  MAY be introduced on an ad hoc basis;
  
  - Depending on the nature of the request, and especially the length of the funding period,
  funds MAY be disbursed in increments, based on concrete deliverables or various adoption
  and/or performance metrics.

- Any decision to change the governance of the Zcash Development Fund as described in this
proposal and in final detail by the ECC, the ZF, and the Third Entity, MUST involve the
Zcash community at large, similar to the process around the issue described in the Motivation
section of this proposal;

- In situations involving security threats, the ECC, the ZF, and/or the Third Entity MUST
take all possible steps necessary to avoid any loss of funds and ensure that the Zcash
Development Fund remains intact and available for its intended purpose as described above.
However, these steps SHOULD NOT result in a situation whereby the requirements described
in this proposal can no longer be met;

- All transfers from the Zcash Development Fund MUST be in full accordance with the
requirements described in this proposal, and the official mission and values of
the ZF. [#ABOUTZF]_

Rationale
============
To be completed.

Motivation
========

In October 2020, the Zcash network is scheduled to undergo its first block reward halving
and fourth Network Upgrade (NU4). According to the current protocol specification, this
is also when the 20% of newly issued ZEC included in the block reward known as the Founders’
Reward (FR) expires so that all subsequent rewards can be claimed exclusively by miners.

Currently, the two organizations leading the development and maintenance of Zcash - the
Electric Coin Company (ECC) and the Zcash Foundation (ZF) - are either directly or indirectly
financially dependent on the FR. Once the FR funds run out and respective balance sheets are
depleted, both organizations would have to secure alternative sources of funding to continue
supporting Zcash. The same holds for any other group or entity that contributes or plans to
contribute work beneficial for Zcash.

To address this issue, the current proposal - originally described and discussed on the Zcash
Forum [#FORUM2]_ - puts forward the creation of the Zcash Development Fund and describes its
initial financing mechanism and fundamental rules of governance. The purpose of the latter
is to effectively direct the Zcash Development Fund toward its intended purpose as described
below, and to establish proper norms of accountability and transparency for its Recipients.

The implementation of this proposal would automatically direct 20% of newly issued ZEC in
coinbase rewards between the first (year 2020, at block height 840,000) and second (year 2024,
at block height 1,680,000) halving to the Zcash Development Fund. This allocation amounts to
1.05 million, or 5%, of fully diluted ZEC. Combined with the FR of 2.1 million, or 10%, of
fully diluted ZEC, this amounts to 3.15 million, or 15%, of fully diluted ZEC.

There are two crucial differences between the FR and the Zcash Development Fund. First, the
Zcash Development Fund would be directed exclusively toward technical and non-technical
initiatives that contribute to the success of Zcash. And second, to ensure proper accountability
and transparency, the handling of the funds in the Zcash Development Fund would be subject to
much more explicit and inclusive rules of governance, as laid out in the Specification section
of this proposal.

This proposal aspires to achieve the following:

- To guarantee sufficient financial resources for research, development, maintenance, and
other types of technical work directly connected to the various software implementations of
the Zcash protocol by world-class cryptographers and engineers, as well as non-technical
initiatives (including design, marketing, events, regulatory outreach, education, governance,
and any other form of business or community development) that contribute to the long-term
success of the Zcash network. Funding such activities constitutes the intended purpose of
the Zcash Development Fund;

- To ensure that funding for both technical and non-technical work on Zcash stays
sufficiently independent from external entities (investors, donors, private companies, etc.)
who could end up acquiring a disproportionately large influence over the network and its
development, or jeopardize the sustainability of funding necessary for the success and
stability of Zcash;

- To establish the fundamental rules of governance and accountability regarding the use of
funds in the Zcash Development Fund;

- To increase the level of decentralization and community involvement in Zcash governance
and resource allocation;

- To encourage transparency and cooperation among different Zcash stakeholders and
strengthen the community’s governance capabilities moving forward.

Out of Scope
============

This proposal does not address the following closely related issues:

- Details of the decision-making process for supporting or rejecting this or other
relevant proposals by the ECC, the ZF, or other Zcash stakeholders. That said, the
authors of this proposal maintain that any decision by the ECC and the ZF on the
issue described in the Motivation section above MUST be preceded by at least the
following procedures for measuring community sentiment, listed in the August 6,
2019 statement by the ZF [#ZFSTATEMENT1]_:

  - Reviving the Community Advisory Panel with an opportunity for new members of
  the Zcash community to join. The Panel is expected to vote on all proposals that
  meet the basic ZIP draft requirements [#ZIPGUIDE]_;
  
  - Miner signalling whereby mining pools can signal their support of specific
  proposals using their ability to embed arbitrary messages in the mined blocks;
  
  - Methods for measuring community sentiment MAY also include Zcash Forum user
  signalling limited to accounts created before a certain date. Ideally, all  ZEC
  holders would also be able to signal their support of specific proposals but, given
  current technical limitations, this may not be feasible. The outcome of the two
  procedures listed above, as well as any other that end up getting implemented for
  the same purpose, SHOULD play a central role in determining the official position
  of both the ECC and the  ZF on the issue described in the Motivation section of
  this proposal.

- Question of whether the ECC should reorganize itself into a non-profit, as suggested
by the ZF in their August 6, 2019 statement. [#ZFSTATEMENT2]_ The current proposal
neither prescribes nor excludes the option of the ECC becoming a non-profit. The
authors consider the basic governance rules of the Zcash Development Fund outlined
above sufficient to ensure transparency and accountability, regardless of whether
the Applicant is a for-profit or a non-profit entity. According to the current proposal,
funding from the Zcash Development Fund would be available to both for- and non-profit
entities, thereby allowing for maximal flexibility in terms of the types of activities
that can be funded.

Security Considerations
============

To be completed.

Trade-offs between 2-of-2, 2-of-3, and 3-of-3.

Internal security and key management practices within each of the governing entities.

Discussion
============

Recognized objections to this proposal include:

- It is not in accordance with the current protocol specification and the initial
promise of the creators of Zcash, according to which 100% of coinbase rewards will go
to miners after the first halving. The main counter-argument that motivates the current
proposal concerns the need to guarantee stable and sufficient funding for world-class
cryptographers, engineers, and other professionals to continue contributing their time
and effort to Zcash;

- Objections concerning the various parameters of the Zcash Development Fund funding
mechanism described above;

- Objections concerning the governance rules of the Zcash Development Fund described
above.

References
==========

.. [#FORUM1] `Placeholder Considerations: Resources, Governance, and Legitimacy in NU4 <https://forum.zcashcommunity.com/t/placeholder-considerations-resources-governance-and-legitimacy-in-nu4/34045>`_
.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#NUPIPELINE] `The Zcash Network Upgrade Pipeline <https://electriccoin.co/blog/the-zcash-network-upgrade-pipeline/>`_
.. [#ABOUTZF] `About the Zcash Foundation <https://www.zfnd.org/about/>`_
.. [#FORUM2] `Placeholder Considerations: Resources, Governance, and Legitimacy in NU4 <https://forum.zcashcommunity.com/t/placeholder-considerations-resources-governance-and-legitimacy-in-nu4/34045>`_
.. [#ZFSTATEMENT1] `Zcash Foundation Guidance on Dev Fund Proposals <https://www.zfnd.org/blog/dev-fund-guidance-and-timeline/>`_
.. [#ZIPGUIDE] `ZIP Guide <https://github.com/zcash/zips/blob/master/zip-0000.rst>`_
.. [#ZFSTATEMENT2] `Zcash Foundation Guidance on Dev Fund Proposals <https://www.zfnd.org/blog/dev-fund-guidance-and-timeline/>`_
