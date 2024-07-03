::

  ZIP: Unassigned
  Title: Allocation of Block Rewards for Decentralized Development Funding
  Owners: Kris Nuttycombe <kris@nutty.land>
          Jason McGee <aquietinvestor@gmail.com>
  Original-Authors: Skylar Saveland <skylar@free2z.com>
  Credits: Daira-Emma Hopwood
           Jack Grigg
  Status: Draft
  Category: Consensus
  Created: 2024-07-03
  License: MIT
  Pull-Request: <https://github.com/zcash/zips/pull/866>

Terminology
===========

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [#BCP14]_ when, and only
when, they appear in all capitals.

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


Abstract
========

This ZIP proposes several options for the allocation of a percentage of the
Zcash block subsidy, post-November 2024 halving, to an in-protocol "lockbox."
Currently, 80% of the block subsidy goes to miners, while 20% is distributed
among the Major Grants Fund (ZCG), Electric Coin Company (ECC), and the Zcash
Foundation (ZF). If no changes are made, this 20% dev fund will expire,
resulting in the entire block subsidy going to miners, leaving no block-subsidy
funds for essential protocol development, security, marketing, or legal
expenses.

The proposed lockbox addresses significant issues observed with [#zip-1014]_,
such as regulatory risks, inefficiencies in funding organizations instead of
projects, and centralization. While the exact disbursement mechanism for the
lockbox funds is yet to be determined and will be addressed in a future ZIP,
the goal is to employ a decentralized mechanism that ensures community
involvement and efficient, project-specific funding. This approach is intended
to potentially improve regulatory compliance, reduce inefficiencies, and
enhance the decentralization of Zcash's funding structure.

Motivation
==========

Starting at Zcash's second halving in November 2024, by default 100% of the
block subsidies will be allocated to miners, and no further funds will be
automatically allocated to any other entities. Consequently, no substantial new
funding may be available to existing teams dedicated to furthering charitable,
educational, or scientific purposes, such as research, development, and
outreach.

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
   executives introduce a single point of failure and limit community
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
   the Lockbox Funding Streams proposal [#zip-lockbox-funding-streams]_.

2. **Regulatory Considerations**: The allocation of funds should minimize
   regulatory risks by avoiding direct funding of specific organizations. The
   design should ensure compliance with applicable laws and regulations to
   support the long-term sustainability of the funding model.

Non-requirements
================

The following consideratiosn are explicitly deferred to future ZIPs and are not
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
[#zip-lockbox-funding-streams]_ for storage of funds into a deferred value
pool.

Some of the alternatives described below do not specify a termination height
for the funding streams they propose. In these cases, the termination height
is set to `u32::MAX_VALUE`. A future network upgrade is required in order for
these streams to be terminated.

Alternatives
============

Alternative 1
-------------

Proposed by Skylar Saveland

* 50% of the block subsidy is to be distributed to the lockbox.

As of block height 2726400, and continuing until modified by a future ZIP, the
complete set of funding streams will be::

  ================= =========== ============= ============== ============
        Stream       Numerator   Denominator   Start height   End height
  ================= =========== ============= ============== ============
  ``FS_DEFERRED``       50           100          2726400     u32::MAX
  ================= =========== ============= ============== ============

Motivations for Alternative 1
'''''''''''''''''''''''''''''

This alternative proposes a substantially larger slice of the block subsidy
than is currently allocated for development funding, in order to provide 
a long-term source of funding for protocol improvements. It is intended that
a future mechanism put in place for the disbursement of these funds to only
release funds from the pool in relatively small increments and with a bounded
upper value, to ensure that funding remains available for years to come.

Alternative 2
-------------

Proposed by Jason McGee

* 12% of the block subsidy is to be distributed to the lockbox.
* 8% of the block subsidy is to be distributed to the Financial Privacy
  Foundation (FPF), for the express use of the Zcash Community Grants Committee
  (ZCG) to fund independent teams in the Zcash ecosystem.

As of block height 2726400, and continuing for one year, the complete set of
funding streams will be::

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

* **Mitigating Regulatory Risks**: By minimizing direct funding of US-based
  organizations, the lockbox helps to reduce potential regulatory scrutiny and
  legal risks.

Alternative 3
-------------

Proposed by Kris Nuttycombe

* 20% of the block subsidy is to be distributed to the lockbox.

As of block height 2726400, and continuing for two years, the complete set of
funding streams will be::

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

Alternative 4
-------------

Proposed by NoamChom (Zcash forum)

* 17% of the block subsidy is to be distributed to the lockbox.
* 8% of the block subsidy is to be distributed to the Financial Privacy
  Foundation (FPF), for the express use of the Zcash Community Grants Committee
  (ZCG) to fund independent teams in the Zcash ecosystem.

As of block height 2726400, and continuing for four years, the complete set of
funding streams will be::

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

References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to
    Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs
    Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#zip-1014] `ZIP 1014: Dev Fund Proposal and Governance <zip-1014.rst>`_
