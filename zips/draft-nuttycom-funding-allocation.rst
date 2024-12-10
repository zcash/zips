::

  ZIP: Unassigned
  Title: Block Reward Allocation for Non-Direct Development Funding
  Owners: Kris Nuttycombe <kris@nutty.land>
          Jason McGee <aquietinvestor@gmail.com>
  Original-Authors: Skylar Saveland <skylar@free2z.com>
  Credits: Daira-Emma Hopwood
           Jack Grigg
           @Peacemonger (Zcash Forum)
  Status: Withdrawn
  Category: Consensus
  Created: 2024-07-03
  License: MIT
  Pull-Request: <https://github.com/zcash/zips/pull/866>

Terminology
===========

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [#BCP14]_ when, and only
when, they appear in all capitals.

Abstract
========

This ZIP proposes several options for the allocation of a percentage of the
Zcash block subsidy, post-November 2024 halving, to an in-protocol "lockbox."
The "lockbox" will be a separate pool of issued funds tracked by the protocol,
as described in ZIP 2001: Lockbox Funding Streams
[#zip-2001]_. No disbursement mechanism is currently defined
for this "lockbox"; the Zcash community will need to decide upon and specify a
suitable decentralized mechanism for permitting withdrawals from this lockbox
in a future ZIP in order to make these funds available for funding grants to
ecosystem participants.

The proposed lockbox addresses significant issues observed with ZIP 1014
[#zip-1014]_, such as regulatory risks, inefficiencies due to funding of organizations
instead of projects, and centralization. While the exact disbursement mechanism
for the lockbox funds is yet to be determined and will be addressed in a future
ZIP, the goal is to employ a decentralized mechanism that ensures community
involvement and efficient, project-specific funding. This approach is intended
to potentially improve regulatory compliance, reduce inefficiencies, and
enhance the decentralization of Zcash's funding structure.

Motivation
==========

Starting at Zcash's second halving in November 2024, by default 100% of the
block subsidies will be allocated to miners, and no further funds will be
automatically allocated to any other entities. Consequently, unless the
community takes action to approve new block-reward based funding, existing
teams dedicated to development or outreach or furthering charitable,
educational, or scientific purposes will likely need to seek other sources of
funding; failure to obtain such funding would likely impair their ability to
continue serving the Zcash ecosystem. Setting aside a portion of the block
subsidy to fund development will help ensure that both existing teams and
new contributors can obtain funding in the future.

It is important to balance the incentives for securing the consensus protocol
through mining with funding crucial charitable, educational, and scientific
activities like research, development, and outreach. Additionally, there is a
need to continue to promote decentralization and the growth of independent
development teams.

For these reasons, the Zcash Community wishes to establish a new Zcash
Development Fund after the second halving in November 2024, with the intent to
put in place a more decentralized mechanism for allocation of development
funds. The alternatives presented here are intended to address the following:

1. **Regulatory Risks**: The current model involves direct funding of US-based
   organizations, which can potentially attract regulatory scrutiny from
   entities such as the SEC, posing legal risks to the Zcash ecosystem.

2. **Funding Inefficiencies**: The current model directly funds organizations
   rather than specific projects, leading to a potential mismatch between those
   organizations' development priorities and the priorities of the community.
   Furthermore, if organizations are guaranteed funds regardless of
   performance, there is little incentive to achieve key performance indicators
   (KPIs) or align with community sentiment. A future system that allocates
   resources directly to projects rather than organizations may help reduce
   inefficiencies and better align development efforts with community
   priorities.

3. **Centralization Concerns**: The current model centralizes decision-making
   power within a few organizations, contradicting the decentralized ethos of
   blockchain technology. Traditional organizational structures with boards and
   executives introduce single points of failure and limit community
   involvement in funding decisions.

4. **Community Involvement**: The current system provides minimal formal input
   from the community regarding what projects should be funded, leading to a
   misalignment between funded projects and community priorities.

5. **Moving Towards a Non-Direct Funding Model**: There is strong community
   support for a non-direct Dev Fund funding model. Allocating funds to a
   Deferred Dev Fund Lockbox incentivizes the development of a decentralized
   mechanism for the disbursement of the locked funds.

By addressing these issues, this proposal aims to ensure sustainable,
efficient, and decentralized funding for essential activities within the Zcash
ecosystem.

Requirements
============

1. **In-Protocol Lockbox**: The alternatives presented in this ZIP depend upon
   the Lockbox Funding Streams proposal [#zip-2001]_.

2. **Regulatory Considerations**: The allocation of funds should minimize
   regulatory risks by avoiding direct funding of specific organizations. The
   design should enable and encourage compliance with applicable laws and regulations to
   support the long-term sustainability of the funding model.

Non-requirements
================

The following considerations are explicitly deferred to future ZIPs and are not
covered by this proposal:

1. **Disbursement Mechanism**: The exact method for disbursing the accumulated
   funds from the lockbox is not defined in this ZIP. The design,
   implementation, and governance of the disbursement mechanism will be
   addressed in a future ZIP. This includes specifics on how funds will be
   allocated, the voting or decision-making process, and the structure of the
   decentralized mechanism (such as a DAO).

2. **Regulatory Compliance Details**: The proposal outlines the potential to
   reduce regulatory risks by avoiding direct funding of US-based
   organizations, but it does not detail specific regulatory compliance
   strategies. Future ZIPs will need to address how the disbursement mechanism
   complies with applicable laws and regulations.

3. **Impact Assessment**: The long-term impact of reallocating a portion of the
   block subsidy to the lockbox on the Zcash ecosystem, including its effect on
   miners, developers, and the broader community, is not analyzed in this ZIP.
   Subsequent proposals will need to evaluate the outcomes and make necessary
   adjustments based on real-world feedback and data.

Specification
=============

The following alternatives all depend upon the Lockbox Funding Streams proposal
[#zip-2001]_ for storage of funds into a deferred value
pool.

Some of the alternatives described below do not specify a termination height
for the funding streams they propose. In these cases, the termination height
is set to `u32::MAX_VALUE`. A future network upgrade that alters the
maximum possible block height MUST also alter these termination heights.

Alternatives
============

Alternative 1: Lockbox For Decentralized Grants Allocation (perpetual 50% option)
---------------------------------------------------------------------------------

Proposed by Skylar Saveland

* 50% of the block subsidy is to be distributed to the lockbox.

As of block height 2726400, and continuing until modified by a future ZIP, the
complete set of funding streams will be:

================= =========== ============= ============== ============
      Stream       Numerator   Denominator   Start height   End height
================= =========== ============= ============== ============
``FS_DEFERRED``       50           100          2726400      u32::MAX
================= =========== ============= ============== ============

Motivations for Alternative 1
'''''''''''''''''''''''''''''

This alternative proposes allocating a significantly larger portion of the block
subsidy to development funding than is currently allocated, aiming to establish
a long-term source of funding for protocol improvements. The disbursement of
these funds will be governed by a mechanism to be determined by the community
in the future, ensuring that the funds are released under agreed-upon constraints
to maintain availability for years to come.

The proposed lockbox funding model for Zcash's post-NU6 halving period allocates
50% of the block reward to a deferred reserve, or "lockbox," designated for
future decentralized grants funding. This approach is designed to address several
critical motivations:

.. Note: some of these are similar to the general motivations.

1. **Regulatory Compliance**:

   - **Reduction of Regulatory Risks**: Direct funding to legal entities poses
     significant regulatory risks. Allocating funds to a decentralized lockbox
     mitigates these risks by avoiding direct funding of any specific
     organizations. This alternative represents the strongest regulatory
     posture, as it reduces the likelihood of legal challenges associated with
     funding centralized entities directly.

   - **Potential Minimization of KYC Requirements**: The current funding
     mechanism involves 100% KYC for recipients, which can be detrimental to
     security, privacy, resilience, and participation. A sufficiently
     decentralized disbursement mechanism could reduce the need for recipients
     to undergo KYC with a controlling entity. This would preserve privacy and
     encourage broader participation from developers and contributors who value
     anonymity and privacy. By shifting from direct funding of specific legal
     entities to a decentralized funding model, we create a more secure,
     private, and resilient ecosystem. This potential future difference
     enhances the robustness of the Zcash network by fostering a diverse and
     engaged community without the constraints of centralized direct funding.

2. **Ensuring Sustainable Development Funding**:

   - **Need for Continuous Funding**: Zcash has numerous ongoing and future
     projects essential for its ecosystem's growth and security. Without a
     change, the expiration of the devfund will result in 100% of the block
     reward going to miners, jeopardizing funding for development. The proposed
     50% lockbox allocation ensures that funds are directed towards sustaining
     and improving the Zcash ecosystem through a wide array of initiatives.
     These include protocol development, new features, security audits, legal
     support, marketing, ZSAs (Zcash Shielded Assets), stablecoins,
     programmability, transitioning to a modern Rust codebase, wallets,
     integrations with third-party services, improved node software, block
     explorers, supporting ambassadors, and educational initiatives like
     ZecHub.

   - **Balanced Incentives for Network and Protocol Security**: While miners
     have been essential in providing network security through hashpower,
     allocating 100% of the block reward to mining alone overlooks the crucial
     need for development, innovation, and protocol security. By investing in
     these priorities, we enhance the long-term health and value of the
     protocol, which ultimately benefits miners. A well-maintained and
     innovative protocol increases the overall value of the network, making
     miners' rewards more valuable. This balanced approach aligns the interests
     of miners with the broader community, ensuring sustainable growth and
     security for Zcash.

3. **Efficiency, Accountability, and Decentralization**:

   - **Reduction of Inefficiencies**: Traditional funding models often involve
     significant corporate overhead and centralized decision-making, leading to
     inefficiencies. The prior model provided two 501(c)(3) organizations with
     constant funding for four years, which reduced accountability and allowed
     for potential misalignment with the community's evolving priorities. By
     funding projects directly rather than organizations, we can allocate
     resources more efficiently, ensuring that funds are used for tangible
     development rather than administrative costs. This approach minimizes the
     influence of corporate executives, whose decisions have sometimes failed
     to address critical issues promptly.

   - **Increased Accountability**: A presumed grants-only mechanism, to be
     defined in a future ZIP, would necessitate continuous accountability and
     progress for continuous funding. Unlike the prior model, where
     organizations received guaranteed funding regardless of performance, a
     grants-based approach would require projects to demonstrate ongoing
     success and alignment with community goals to secure funding. This
     continuous evaluation fosters a more responsive and responsible allocation
     of resources, ensuring that funds are directed towards initiatives that
     provide the most value to the Zcash ecosystem. By increasing
     accountability, this model promotes a culture of excellence and
     innovation, driving sustained improvements and advancements in the
     protocol.

   - **Promotion of Decentralization**: The proposed non-direct funding model
     stores deferred funds for future use, with the specifics of the
     disbursement mechanism to be determined by a future ZIP. This could allow
     the community to have a greater influence over funding decisions, aligning
     more closely with the ethos of the Zcash project. By decentralizing the
     allocation process, this approach has the potential to foster innovation
     and community involvement, ensuring that development priorities are more
     reflective of the community's needs and desires, promoting a more open,
     transparent, and resilient ecosystem.

4. **Incentives for Development and Collaboration**:

   - **Creating a Strong Incentive to Implement the Disbursement Mechanism**:
     Allocating 50% of the block reward to the lockbox indefinitely creates
     a powerful incentive for the community to work together to implement the
     disbursement mechanism without delay. Knowing that there is a substantial
     amount of funds available, stakeholders will be motivated to develop and
     agree on an effective, decentralized method for distributing these funds.

   - **Incentivizing Continuous Improvements**: The accumulation of a large
     stored fortune within the lockbox incentivizes continuous improvements
     to the Zcash protocol and ecosystem. Developers, contributors, and
     community members will be driven to propose and execute projects that
     enhance the network, knowing that successful initiatives have the
     potential to receive funding. This model fosters a culture of ongoing
     innovation and development, ensuring that Zcash remains at the forefront
     of blockchain technology.

   - **Aligning Long-Term Interests**: By tying a significant portion of the
     block reward to future decentralized grants funding, the model aligns
     the long-term interests of all stakeholders. Miners, developers, and
     community members alike have a vested interest in maintaining and
     improving the Zcash network, as the value and success of their efforts
     are directly linked to the availability and effective use of the lockbox
     funds. This alignment of incentives ensures that the collective efforts
     of the community are focused on the sustainable growth and advancement
     of the Zcash ecosystem.

Guidance on Future Requirements for Alternative 1
'''''''''''''''''''''''''''''''''''''''''''''''''

To support the motivations outlined, the following guidance is proposed for
Alternative 1. Future ZIP(s) will define the disbursement mechanism. These are
suggestions to achieve the outlined motivations and should be considered in
those future ZIP(s). It is important to note that these are ideas and guidance,
not hard, enforceable requirements:

1. **Cap on Grants**: Grants should be capped to promote more granular
   accountability and incremental goal-setting. This approach ensures that
   projects are required to define their work, goals, milestones, KPIs, and
   achievements in smaller, more manageable increments. Even if a single
   project is utilizing significant funds quickly, the cap ensures that
   progress is continuously evaluated and approved based on tangible results
   and alignment with community priorities.

2. **Decentralized Disbursement Mechanism**: The disbursement mechanism should
   be sufficiently decentralized to ensure the regulatory motivations are
   fulfilled. A decentralized mechanism could reduce the need for recipients to
   undergo KYC with a controlling party, preserving privacy and aligning with
   the ethos of the Zcash project.

3. **Governance and Accountability**: The governance structure for the
   disbursement mechanism should be open and accountable, with decisions made
   through community consensus or decentralized voting processes to maintain
   trust and accountability. This approach will help ensure that the allocation
   of funds is fair and aligned with the community's evolving priorities.

4. **Periodic Review and Adjustment**: There should be provisions for periodic
   review and adjustment of the funding mechanism to address any emerging
   issues or inefficiencies and to adapt to the evolving needs of the Zcash
   ecosystem. This could include the ability to add or remove participants as
   necessary. Regular assessments will help keep the funding model responsive
   and effective, ensuring it continues to meet the community's goals.

By addressing these motivations and providing this guidance, Alternative 1 aims
to provide a robust, sustainable, and decentralized funding model that aligns
with the principles and long-term goals of the Zcash community.

Alternative 2: Hybrid Deferred Dev Fund: Transitioning to a Non-Direct Funding Model
------------------------------------------------------------------------------------

Proposed by Jason McGee, Peacemonger, GGuy

* 12% of the block subsidy is to be distributed to the lockbox.
* 8% of the block subsidy is to be distributed to the Financial Privacy
  Foundation (FPF), for the express use of the Zcash Community Grants Committee
  (ZCG) to fund independent teams in the Zcash ecosystem.

As of block height 2726400, and continuing for one year, the complete set of
funding streams will be:

================= =========== ============= ============== ============
      Stream       Numerator   Denominator   Start height   End height
================= =========== ============= ============== ============
``FS_DEFERRED``       12           100          2726400      3146400
``FS_FPF_ZCG``         8           100          2726400      3146400
================= =========== ============= ============== ============

Motivations for Alternative 2
'''''''''''''''''''''''''''''

* **Limited Runway**: ZCG does not have the financial runway that ECC/BP and ZF
  have. As such, allocating ongoing funding to ZCG will help ensure the Zcash
  ecosystem has an active grants program.

* **Promoting Decentralization**: Allocating a portion of the Dev Fund to Zcash
  Community Grants ensures small teams continue to receive funding to
  contribute to Zcash. Allowing the Dev Fund to expire, or putting 100% into a
  lockbox, would disproportionally impact grant recipients. This hybrid
  approach promotes decentralization and the growth of independent development
  teams.

* **Mitigating Regulatory Risks**: The Financial Privacy Foundation (FPF) is a
  non-profit organization incorporated and based in the Cayman Islands. By
  minimizing direct funding of US-based organizations, this proposal helps to
  reduce potential regulatory scrutiny and legal risks.

Alternative 3: Lockbox For Decentralized Grants Allocation (20% option)
-----------------------------------------------------------------------

Proposed by Kris Nuttycombe

* 20% of the block subsidy is to be distributed to the lockbox.

As of block height 2726400, and continuing for two years, the complete set of
funding streams will be:

================= =========== ============= ============== ============
      Stream       Numerator   Denominator   Start height   End height
================= =========== ============= ============== ============
``FS_DEFERRED``       20           100          2726400      3566400
================= =========== ============= ============== ============

Motivations for Alternative 3
'''''''''''''''''''''''''''''

This alternative is presented as the simplest allocation of block rewards
to a lockbox for future disbursement that is consistent with results of
community polling.

Alternative 4: Masters Of The Universe?
---------------------------------------

Proposed by NoamChom (Zcash forum)

* 17% of the block subsidy is to be distributed to the lockbox.
* 8% of the block subsidy is to be distributed to the Financial Privacy
  Foundation (FPF), for the express use of the Zcash Community Grants Committee
  (ZCG) to fund independent teams in the Zcash ecosystem.

As of block height 2726400, and continuing for four years, the complete set of
funding streams will be:

================= =========== ============= ============== ============
      Stream       Numerator   Denominator   Start height   End height
================= =========== ============= ============== ============
``FS_DEFERRED``       17           100          2726400      4406400
``FS_FPF_ZCG``         8           100          2726400      4406400
================= =========== ============= ============== ============

Motivations for Alternative 4
'''''''''''''''''''''''''''''

This alternative proposes a slightly larger slice of the block subsidy than is
currently allocated for development funding, in order to better provide for the
needs of the Zcash community.


Revisitation Requirement for Alternative 4
''''''''''''''''''''''''''''''''''''''''''

The terms for this Alternative should be revisited by the Zcash ecosystem upon
creation/ activation of a "non-direct funding model" (NDFM). At that completion
of an NDFM which accessess the lockbox funds, this ZIP should be reconsidered
(potentially terminated) by the Zcash ecosystem, to determine if its ongoing
direct block subsidies are preferred for continuation. Discussions / solications
/ sentiment gathering from the Zcash ecosystem should be initiated ~6 months in
advance of the presumed activation of a "non-direct funding model", such that
the Zcash ecosystem preference can be expediently realized.


Requirements related to direct streams for the Financial Privacy Foundation
===========================================================================

The following requirements apply to Alternative 2 and Alternative 4:

The stream allocated to Zcash Community Grants (ZCG) is intended to fund
independent teams entering the Zcash ecosystem, to perform major ongoing
development (or other work) for the public good of the Zcash ecosystem, to the
extent that such teams are available and effective. The ZCG Committee is given
the discretion to allocate funds not only to major grants, but also to a
diverse range of projects that advance the usability, security, privacy, and
adoption of Zcash, including community programs, dedicated resources, and other
projects of varying sizes.

The funds SHALL be received and administered by the
Financial Privacy Foundation (FPF). FPF MUST disburse them for grants and
expenses reasonably related to the administration of the ZCG program, but
subject to the following additional constraints:

1. These funds MUST only be used to issue grants to external parties that are
   independent of FPF, and to pay for expenses reasonably related to the
   administration of the ZCG program. They MUST NOT be used by FPF for
   its internal operations and direct expenses not related to the
   administration of grants or the grants program.

2. ZCG SHOULD support well-specified work proposed by the grantee, at
   reasonable market-rate costs. They can be of any duration or ongoing without
   a duration limit. Grants of indefinite duration SHOULD have semiannual
   review points for continuation of funding.

3. Priority SHOULD be given to major grants that bolster teams with substantial
   (current or prospective) continual existence, and set them up for long-term
   success, subject to the usual grant award considerations (impact, ability,
   risks, team, cost-effectiveness, etc.). Priority SHOULD be given to major
   grants that support ecosystem growth, for example through mentorship,
   coaching, technical resources, creating entrepreneurial opportunities, etc.
   If one proposal substantially duplicates another’s plans, priority SHOULD be
   given to the originator of the plans.

4. The ZCG committee SHOULD be restricted to funding projects that further the
   Zcash cryptocurrency and its ecosystem (which is more specific than
   furthering financial privacy in general) as permitted by FPF
   and any relevant jurisdictional requirements.

5. ZCG awards are subject to approval by a five-seat ZCG Committee. The ZCG
   Committee SHALL be selected by the ZF’s Community Advisory Panel or a
   successor process (e.g. as established by FPF). Elections SHALL be staggered
   to ensure continuity within the Committee.

6. The ZCG Committee’s funding decisions will be final, requiring no approval
   from the FPF Board, but are subject to veto if the FPF judges them to
   violate any relevant laws or other (current or future) obligations.

7. ZCG Committee members SHALL have a one-year term and MAY sit for reelection.
   The ZCG Committee is subject to the same conflict of interest policy that
   governs the FPF Board of Directors (i.e. they MUST recuse themselves when
   voting on proposals where they have a financial interest). At most one
   person with association with the BP/ECC, at most one person with
   association with the ZF, and at most one person with association with FPF
   are allowed to sit on the ZCG Committee.
   “Association” here means: having a financial interest, full-time employment,
   being an officer, being a director, or having an immediate family
   relationship with any of the above. The ZF SHALL continue to operate the
   Community Advisory Panel and SHOULD work toward making it more
   representative and independent (more on that below). Similarly, FPF should
   also endeavor to establish its own means of collecting community sentiment
   for the purpose of administering ZCG elections.

8. A portion of the ZCG Slice shall be allocated to a Discretionary Budget,
   which may be disbursed for expenses reasonably related to the administration
   of the ZCG program. The amount of funds allocated to the Discretionary
   Budget SHALL be decided by the ZF’s Community Advisory Panel or successor
   process. Any disbursement of funds from the Discretionary Budget MUST be
   approved by the ZCG Committee. Expenses related to the administration of the
   ZCG program include, without limitation the following:

    * Paying third party vendors for services related to domain name
      registration, or the design, website hosting and administration of
      websites for the ZCG Committee.
    * Paying independent consultants to develop requests for proposals that
      align with the ZCG program.
    * Paying independent consultants for expert review of grant applications.
    * Paying for sales and marketing services to promote the ZCG program.
    * Paying third party consultants to undertake activities that support the
      purpose of the ZCG program.
    * Reimbursement to members of the ZCG Committee for reasonable travel
      expenses, including transportation, hotel and meals allowance.

9. A portion of the Discretionary Budget MAY be allocated to provide reasonable
   compensation to members of the ZCG Committee. Committee member compensation
   SHALL be limited to the hours needed to successfully perform their positions
   and MUST align with the scope and responsibilities of their roles. The
   allocation and distribution of compensation to committee members SHALL be
   administered by the FPF. The compensation rate and hours for committee
   members SHALL be determined by the ZF’s Community Advisory Panel or
   successor process.

10. The ZCG Committee’s decisions relating to the allocation and disbursement
    of funds from the Discretionary Budget will be final, requiring no approval
    from the FPF Board, but are subject to veto if the FPF judges
    them to violate laws or FPF reporting requirements and other
    (current or future) obligations.

FPF SHALL recognize the ZCG slice of the Dev Fund as a Restricted Fund
donation under the above constraints (suitably formalized), and keep separate
accounting of its balance and usage under its Transparency and Accountability
obligations defined below.

FPF SHALL strive to define target metrics and key performance indicators,
and the ZCG Committee SHOULD utilize these in its funding decisions.

Furthering Decentralization
---------------------------

FPF SHALL conduct periodic reviews of the
organizational structure, performance, and effectiveness of the ZCG program and
committee, taking into consideration the input and recommendations of the ZCG
Committee. As part of these periodic reviews, FPF MUST commit to
exploring the possibility of transitioning ZCG into an independent organization
if it is economically viable and it aligns with the interests of the Zcash
ecosystem and prevailing community sentiment.

In any transition toward independence, priority SHALL be given to maintaining
or enhancing the decentralization of the Zcash ecosystem. The newly formed
independent organization MUST ensure that decision-making processes remain
community-driven, transparent, and responsive to the evolving needs of the
Zcash community and ecosystem. In order to promote geographic decentralization,
the new organization SHOULD establish its domicile outside of the United
States.

Transparency and Accountability
-------------------------------

FPF MUST accept the following obligations in this section on behalf of ZCG:

* Publication of the ZCG Dashboard, providing a snapshot of ZCG’s current
  financials and any disbursements made to grantees.
* Bi-weekly meeting minutes documenting the decisions made by the ZCG committee
  on grants.
* Quarterly reports, detailing future plans, execution on previous plans, and
  finances (balances, and spending broken down by major categories).
* Annual detailed review of the organization performance and future plans.
* Annual financial report (IRS Form 990, or substantially similar information).

BP, ECC, ZF, FPF, ZCG and grant recipients MUST promptly disclose any security
or privacy risks that may affect users of Zcash (by responsible disclosure
under confidence to the pertinent developers, where applicable).

All substantial software whose development was funded by the Dev Fund SHOULD be
released under an Open Source license (as defined by the Open Source Initiative
[#osd]_), preferably the MIT license.

Enforcement
-----------

FPF MUST contractually commit to fulfill these obligations on behalf of
ZCG, and the prescribed use of funds, such that substantial violation, not
promptly remedied, will result in a modified version of Zcash node software
that removes ZCG’s Dev Fund slice and allocates it to the Deferred Dev Fund
lockbox.

References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to
    Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs
    Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#osd] `The Open Source Definition <https://opensource.org/osd>`_
.. [#zip-1014] `ZIP 1014: Dev Fund Proposal and Governance <zip-1014.rst>`_
.. [#zip-2001] `ZIP 2001: Lockbox Funding Streams <zip-2001.rst>`_
