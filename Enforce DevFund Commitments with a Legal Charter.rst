::

  ZIP: unassigned.
  Title: Enforce DevFund Commitments with a Legal Charter
  Owner: unassigned
  Author: @lex-node (zcash forums)
  Advocates: @lex-node (zcash forums) /  @mistfpga  (zcash forums) <steve@mistfpga.net>
  Category: ?
  Created: 2019-08-24
  License: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0) [1]
  

Originally posted and discussed `on the Zcash Community Forum <https://forum.zcashcommunity.com/t/dev-fund-supplemental-proposal-enforce-devfund-commitments-with-legal-charter/34709>`__.


Terminology
===========

`RFC2119 <https://tools.ietf.org/html/rfc2119>` refrences will be in CAPS.

**The key words include "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL"**

For clarity in this ZIP defines these terms:

-  Covenant is defined as a legally binding agreement upon which a specific aspect of development of the zcash protocol and/or adoption is scheduled and agreed upon.

Abstract
========

Supplemental proposal to ensure feature selection and work is community driven.

Hopefully it will be compatible with a number of other zips and can be worked into them.

Out of Scope for this proposal
==============================

-  This proposal does not address the merits, motivations or terms of any particular development funding proposal.
-  Requirements & Implementation
-  The current trademark and sign off issues that just popped up.


Motivation
==========

This proposal is supplemental to any Development Fund Proposal which places or purports to place conditions on how the Electric Coin Company (ECC) and the Zcash Foundation use development funds or take other related off-chain actions (such requirements, Covenants).

For example, the proposal 20% to a 2-of-3 multisig with community-involved governance provides that “[f]unds accruing to the Zcash Development Fund MUST be used only for … technical work directly connected to the various software implementations of the Zcash protocol.” However, once development funding is approved and implemented via a hardfork, there will be no enforcement mechanism to ensure that the ZF and ECC abide by this requirement.

This proposal aims to provide such an enforcement mechanism. If this proposal is adopted, then the ECC and/or ZF, as applicable MUST enter into a legal agreement which would entitle ZCash (ZEC) holders to enforce ECC’s/ZF’s performance of any Covenants. For purposes of this proposal we will refer to the legal agreement as the “DevFund Charter” or “Charter” for short, but it MAY also be styled in other ways–e.g,. as a Constitution, Bylaws, Fund Governance Agreement, etc.

The DevFund Charter should be used to the benefit of all ZEC users, but the DevFund Charter MAY provide that an enforcement action requires the support of the holders of a plurality, majority or supermajority of ZEC. ZEC held by the ZF, ECC and their officers, directors, employees and/or affiliates SHOULD be excluded from the denominator in calculating the requisite plurality, majority or supermajority of ZEC.

A quorum of yet to be decided number of representatives from a number specified groups from which the DevFund Charter MAY provide that an enforcement action requires the support of the assigned representatives of each.  One such mechanism SHOULD be ZEC balance, however this would require a 66% majority or a 85% super majority. (These numbers are not binding and are up for discussion)

It is assumed that the ECC, Foundation or party with a direct conflict of interest WILL identify their vote/signal - which MAY be rejected from the vote.

Legal enforcement MAY occur in a court of law, non-binding mediation or binding arbitration. The DevFund Charter MAY also provide rights to other ZCash community constituencies, such as specified miners or the “Third Entity” contemplated by the 20% to a 2-of-3 multisig with community-involved governance proposal referenced above.

Rationale
=========

Because ZEC holders do not have specific legal rights against the ECC or ZF, but MAY wish to condition renewed on-chain development funding on the ECC’s or ZF’s agreement to use the development funds in certain ways, ZEC holders SHOULD have the legal right to enforce ECC’s/ZF’s compliance with those agreements.

Requirements
============

-  If a development funding proposal receives sufficient community support and requires certain Covenants on the part of ECC or ZF, then one or more attorneys MUST be engaged to draft a Charter that reflects those Covenants, and the Charter MUST become legally effective & binding at the same time as the other aspects of the development funding proposal are implemented on-chain (e.g., at the same time as a hardfork, if a hardfork is required to implement the development funding proposal).

-  Each pending development funding proposal SHOULD be amended to specifically describe any Covenants that the ECC, ZF or any other relevant person or entity would be required to agree to as part of such development funding proposal.

Specification
=============

Please see "Issues for the Specification"


Issues
======

Because lex-node is currently unavailable but will be, I have put yet to be addressed concerns here. and addressed them as best I can.

Here is a precompiled list:

-  “Code is Law; This is Just Law!”
Objection: Relying on off-chain legal mechanisms is contrary to the cypherpunk ethos and/or the mission/ethos of ZCash.

Answer: This is a values judgment that some people may reasonably hold. However, one should also consider that “don’t trust, verify” is also a cypherpunk principle and that the off-chain nature of some requirements means that a code-based solution is currently not possible; therefore, a legal enforcement mechanism, while imperfect, may be preferable to no enforcement mechanism.

- “Social Coordination Impracticality/Risk”
Objection: ZEC holders prize anonymity, but legal enforcement of breached Covenants will require social coordination (people must agree to enforce the action, and someone must actually get a lawyer and go to court). Therefore, this mechanism will not be valuable to ZEC holders and could lead them to compromise their anonymity and thus be worse than useless.

Answer: The community should further discuss how, in practice, ZEC holders might securely coordinate to bring an enforcement action against ECC and the ZF if it were needed. Additionally, it should be considered that the mere possibility of legal enforcement due to the clear terms of a Charter may dissuade ECC and ZF from violating covenants and thus, paradoxically, having a Charter may also mean that no legal action ever becomes necessary. Additionally, the “class action” legal structure in some jurisdictions may mean that the ZEC holders community could find a ‘champion’ in the form of a class-action attorney, without ZEC holders being required to personally become involved or 'out themselves’ as ZEC holders (other than one willing ZEC holder as class representative).

- 3 “This Will Just Waste Funding On Lawyers”
Objection: This Charter will be novel and bespoke, and lawyers may charge high fees to draft it and give assurances that it is enforceable. This wastes money that otherwise could be spent on ZCash development.

Answer: This is a valid concern. The ZCash community may be able to crowdsource an initial rough draft of the Charter from lawyers in the community or even non-lawyers who may be willing to do research and make an attempt at an initial draft. Lawyers could be involved primarily to issue-spot and formalize the initial draft. ECC and ZF may have law firms on retainer that could perform the work at favorable rates. Lawyers may be willing to work at discounted rates due to the unique opportunity and prestige of developing this innovative blockchain governance mechanism. Additionally, any legal fees may be small as a percentage of the overall value at stake, which may be considerable if a 5-20% development funding block reward is authorized.
 
Issues for the specification
============================

-  Whether a plurality, majority or supermajority of ZEC are required to approve an enforcement action against ECC or ZF;
-  Logistics and technical implementation regarding the Charter, such as on-chain signalling/voting for enforcement;
-  Remedies under the Charter, such as “specific performance” (getting a court to order ZF or ECC to comply with a covenant),
-  Discontinuation or reduction of development funding (which MAY occur by having Covenants that the ZF or ECC will prepare a hard-fork that discontinues or reduces development funding if so requested by holders of the requisite plurality, majority or supermajority of ZEC), etc.

References
==========

[1] https://creativecommons.org/licenses/by-sa/4.0/
