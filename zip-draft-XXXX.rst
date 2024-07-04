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
changes are made.

It is crucial to set aside a portion of the block reward for development,
security, legal, and marketing purposes. However, the current direct funding
mechanism has several significant issues:

1. **Regulatory Risks**: The current model involves direct funding of US-based
   organizations, which can potentially attract regulatory scrutiny from
   entities such as the SEC, posing legal risks to the Zcash ecosystem.

2. **Funding Inefficiencies**: The current model directly funds organizations
   rather than specific projects, leading to inefficiencies. Organizations may
   sell the received ZEC for USD to cover expenses, which can potentially drive
   down the price of ZEC. Furthermore, if organizations are guaranteed funds
   regardless of performance, there is little incentive to achieve key
   performance indicators (KPIs) or align with community sentiment. This can
   result in inefficiencies and misallocation of funds. Additionally, US
   corporations tend to prioritize their USD balance sheet, creating a
   disconnect from the Zcash ecosystem's needs and goals.

3. **Centralization Concerns**: The current model centralizes decision-making
   power within a few organizations, contradicting the decentralized ethos of
   blockchain technology. Traditional organizational structures with boards and
   executives introduce a single point of failure and limit community
   involvement in funding decisions.

4. **Community Involvement**: The current system provides minimal formal input
   from the community regarding what projects should be funded, leading to a
   misalignment between funded projects and community priorities.

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

2. **Specific Allocation Percentages**: This ZIP does not prescribe
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

This section describes the consensus rules and protocol changes required to
implement the proposed in-protocol lockbox for deferred development fund
allocation. The specification outlines the creation, management, and
integration of the lockbox within the Zcash protocol.

Deferred Development Fund Chain Value Pool Balance
--------------------------------------------------

A new development fund value pool balance, denominated in zatoshis, will be
created. This balance will be initialized to zero at the NU6 activation block.

Coinbase Transaction Adjustments
--------------------------------

For coinbase transactions, a specified proportion of the block subsidy will be
added to the deferred development fund chain value pool balance and subtracted
from the transparent transaction value pool. The exact
proportions (numerator/denominator) of the block subsidy allocated to the
deferred development fund must be defined to ensure the correct allocation at
every block.

Proportion Specification
------------------------

The proportions of the block subsidy allocated to the deferred development fund
and any existing funding streams must add up to the intended total at every
block. Before NU6 activation, the actual percentage allocated to the deferred
development fund will be zero. After NU6 activation, |percentage| of the block
reward will be allocated to the deferred development fund.

Redefinition of Miner Subsidy
------------------------------

The miner subsidy will be redefined to account for the deferred development
fund.

Reserve Pool Mechanism
----------------------

The reserve pool will be a container for the issued supply, distinct from
existing pools. It will not be subdivided into individually spendable notes or
coins. The lockbox mechanism ensures that funds are accumulated and securely
stored until a future ZIP defines the disbursement mechanism.

Duration
--------

The deferred development fund will be active post-November 2024 halving.
|percentage| of the block reward will be allocated to the lockbox until
modified or disabled by a future ZIP.

References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to
    Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs
    Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#zip-1014] `ZIP 1014: Dev Fund Proposal and Governance <zip-1014.rst>`_
