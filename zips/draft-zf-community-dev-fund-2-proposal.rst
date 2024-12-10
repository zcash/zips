::

  ZIP: Unassigned
  Title: Establishing a Hybrid Dev Fund for ZF, ZCG and a Dev Fund Reserve
  Owners: Jack Gavigan <jack@zfnd.org>
  Credits: The ZIP 1014 Authors
  Status: Withdrawn
  Category: Consensus Process
  Created: 2024-07-01
  License: MIT
  Discussions-To: 
  Pull-Request: 


Terminology
===========

The key words "MUST", "MUST NOT", "SHALL", "SHALL NOT", "SHOULD", and "MAY" 
in this document are to be interpreted as described in BCP 14 [#BCP14]_ when,
and only when, they appear in all capitals.

The term "network upgrade" in this document is to be interpreted as described 
in ZIP 200 [#zip-0200]_ and the Zcash Trademark Donation and License Agreement
([#trademark]_ or successor agreement).

The terms "block subsidy" and "halving" in this document are to be interpreted 
as described in sections 3.10 and 7.8 of the Zcash Protocol Specification.
[#protocol]_

"Electric Coin Company", also called "ECC", refers to the US-incorporated 
Zerocoin Electric Coin Company, LLC.

"Bootstrap Project", also called "BP", refers to the US-incorporated 501(c)(3) 
nonprofit corporation of that name.

"Zcash Foundation", also called "ZF", refers to the US-incorporated 501(c)(3) 
nonprofit corporation of that name.

"Financial Privacy Foundation", also called "FPF", refers to the Cayman 
Islands-incorporated non-profit foundation company limited by guarantee of 
that name.

"Autonomous Entities" refers to committees, DAOs, teams or other groups to 
which FPF provides operations, administrative, and financial management 
support. 

"Section 501(c)(3)" refers to that section of the U.S. Internal Revenue Code 
(Title 26 of the U.S. Code). [#section501c3]_

"Zcash Community Advisory Panel", also called "ZCAP", refers to the panel of 
community members assembled by the Zcash Foundation and described at [#zcap]_.

The terms "Testnet" and "Mainnet" are to be interpreted as described in 
section 3.12 of the Zcash Protocol Specification [#protocol-networks]_.

“Lockbox” refers to a deferred funding pool of issued Zcash value as described 
in ZIP 2001 [#zip-2001]_.

“Dev Fund Reserve”, also called “DFR”, refers to the funds that are to be 
stored in the Lockbox as a result of the changes described in this ZIP. 


Abstract
========

This proposal describes a structure for a new Zcash Development Fund (“Dev 
Fund”), to be enacted in Network Upgrade 6 and last for 2 years. This Dev 
Fund shall consist of 20% of the block subsidies. 

The Dev Fund shall be split into 3 slices:

* 32% for Zcash Foundation;
* 40% for "Zcash Community Grants", intended to fund large-scale long-term 
  Projects (administered by the Financial Privacy Foundation, with extra
  community input and scrutiny).
* 28% for a Dev Fund Reserve, to be stored in a Lockbox. 

The Lockbox will securely store funds until a disbursement mechanism is 
established in a future ZIP.

Governance and accountability are based on existing entities and legal 
mechanisms, and increasingly decentralized governance is encouraged.


Motivation
==========

Starting at Zcash's second halving in November 2024, the first Dev Fund will 
expire, meaning that by default 100% of the block subsidies will be allocated 
to miners, and no further funds will be automatically allocated to any other 
entities. Consequently, no substantial new funding may be available to 
existing teams dedicated to furthering charitable, educational, or scientific 
purposes, such as research, development, and outreach: the Electric Coin 
Company (ECC), the Zcash Foundation (ZF), and the many entities funded by the 
ZF grants and Zcash Community Grants programs.

There is a need to continue to strike a balance between incentivizing the 
security of the consensus protocol (i.e., mining) versus crucial charitable, 
educational, and/or scientific aspects, such as research, development and 
outreach.

Furthermore, there is a need to balance the sustenance of ongoing work by the 
current teams dedicated to Zcash, with encouraging decentralization and growth 
of independent development teams.

For these reasons, the Zcash Community desires to allocate and contribute a 
slice of the block subsidies otherwise allocated to miners as a donation to 
support charitable, educational, and scientific activities within the meaning 
of Section 501(c)(3) of Title 26 of the United States Code, and the Cayman 
Islands’ Foundation Companies Law, 2017.

The Zcash Community also supports the concept of a non-direct funding model, 
and desires to allocate a slice of the block subsidies otherwise allocated 
to miners to a Lockbox, with the expectation that those funds will be 
distributed under a non-direct funding model, which may be implemented in a 
future network upgrade. 

For these reasons, the Zcash Community wishes to establish a Hybrid 
Development Fund after the second halving in November 2024, and apportion it 
among ZF, ZCG, and a Dev Fund Reserve to be held in a Lockbox.


Requirements
============

The Dev Fund should encourage decentralization of the Zcash ecosystem, by 
supporting new teams dedicated to Zcash.

The Dev Fund should maintain the existing teams and capabilities in the Zcash 
ecosystem, unless and until concrete opportunities arise to create even 
greater value for the Zcash ecosystem.

There should not be any single entity which is a single point of failure, 
i.e., whose capture or failure will effectively prevent effective use of the 
funds.

Major funding decisions should be based, to the extent feasible, on inputs 
from domain experts and pertinent stakeholders.

The Dev Fund mechanism itself should not modify the monetary emission curve 
(and in particular, should not irrevocably burn coins).

In case the value of ZEC jumps, the Dev Fund recipients should not wastefully 
use excessive amounts of funds. Conversely, given market volatility and 
eventual halvings, it is desirable to create rainy-day reserves.

The Dev Fund mechanism should not reduce users' financial privacy or security. 
In particular, it should not cause them to expose their coin holdings, nor 
cause them to maintain access to secret keys for much longer than they would 
otherwise. (This rules out some forms of voting, and of disbursing coins to 
past/future miners.)

The new Dev Fund system should be simple to understand and realistic to 
implement. In particular, it should not assume the creation of new mechanisms 
(e.g., election systems) or entities (for governance or development) for its 
execution; but it should strive to support and use these once they are built.

The Dev Fund should comply with legal, regulatory, and taxation constraints in 
pertinent jurisdictions.

The Lockbox must be prepared to allocate resources efficiently once the 
disbursement mechanism is defined. This includes ensuring that funds are 
readily available for future projects and not tied up in organizational 
overhead. 

The Lockbox must implement robust security measures to protect against 
unauthorized access or misuse of funds. It must not be possible to disburse 
funds from the Lockbox until the Zcash Community reaches consensus on the 
design of a disbursement mechanism that is defined in a ZIP and implemented as 
part of a future Network Upgrade. 


Non-requirements
================

General on-chain governance is outside the scope of this proposal.

Rigorous voting mechanisms (whether coin-weighted, holding-time-weighted or 
one-person-one-vote) are outside the scope of this proposal, though there is 
prescribed room for integrating them once available.

The mechanism by which funds held in the Dev Fund Reserve Lockbox are to be 
distributed is outside the scope of this proposal. 


Specification
=============

Consensus changes implied by this specification are applicable to the Zcash 
Mainnet. Similar (but not necessarily identical) consensus changes SHOULD be 
applied to the Zcash Testnet for testing purposes.


Dev Fund allocation
-------------------

Starting at the second Zcash halving in 2024, until block height 3566400 
(which is expected to occur approximately two years after the second Zcash 
halving), 20% of the block subsidy of each block SHALL be allocated to a Dev 
Fund that consists of the following three slices:

* 32% for the Zcash Foundation (denoted **ZF slice**);
* 40% for the Financial Privacy Foundation, for "Zcash Community Grants" for
  large-scale long-term projects (denoted **ZCG slice**);
* 28% for the Dev Fund Reserve (denoted **DFR slice**).

The slices are described in more detail below. The fund flow will be 
implemented at the consensus-rule layer, by sending the corresponding ZEC to 
the designated address(es) for each block. This Dev Fund will end at block 
height 3566400 (unless extended/modified by a future ZIP).


ZF slice (Zcash Foundation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This slice of the Dev Fund will flow as charitable contributions from the 
Zcash Community to ZF, to be used at its discretion for any purpose within its 
mandate to support financial privacy and the Zcash platform, including: 
development, education, supporting community communication online and via 
events, gathering community sentiment, and awarding external grants for all of 
the above, subject to the requirements of Section 501(c)(3). The ZF slice will 
be treated as a charitable contribution from the Community to support these 
educational, charitable, and scientific purposes.


ZCG slice (Zcash Community Grants)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This slice of the Dev Fund is intended to fund independent teams entering the
Zcash ecosystem, to perform major ongoing development (or other work) for the
public good of the Zcash ecosystem, to the extent that such teams are 
available and effective.

The funds SHALL be received and administered by FPF. FPF MUST disburse them 
for "Zcash Community Grants" and expenses reasonably related to the 
administration of Zcash Community Grants, but subject to the following 
additional constraints:

1. These funds MUST only be used to issue Zcash Community Grants to external 
   parties that are independent of FPF or to Autonomous Entities that operate 
   under the FPF umbrella, and to pay for expenses reasonably related to 
   the administration of Zcash Community Grants. They MUST NOT be used by FPF 
   for its internal operations and direct expenses not related to 
   administration of Zcash Community Grants. Additionally, ZF is ineligible to 
   receive Zcash Community Grants while ZF is receiving a slice of the Dev 
   Fund. 

2. Zcash Community Grants SHOULD support well-specified work proposed by the 
   grantee, at reasonable market-rate costs. They can be of any duration or 
   ongoing without a duration limit. Grants of indefinite duration SHOULD be 
   reviewed periodically (on a schedule that the Zcash Community Grants
   Committee considers appropriate for the value and complexity of the grant) 
   for continuation of funding.

3. Priority SHOULD be given to Zcash Community Grants that bolster teams with 
   substantial (current or prospective) continual existence, and set them up 
   for long-term success, subject to the usual grant award considerations 
   (impact, ability, risks, team, cost-effectiveness, etc.). Priority SHOULD 
   Be given to grants that support ecosystem growth, for example through 
   mentorship, coaching, technical resources, creating entrepreneurial 
   opportunities, etc. If one proposal substantially duplicates another's 
   plans, priority SHOULD be given to the originator of the plans.

4. Zcash Community Grants SHOULD be restricted to furthering the Zcash 
   cryptocurrency and its ecosystem (which is more specific than furthering
   financial privacy in general).

5. Zcash Community Grants awards are subject to approval by a five-seat Zcash 
   Community Grants Committee. The Zcash Community Grants Committee SHALL be 
   selected by the ZF's Zcash Community Advisory Panel (ZCAP) or successor 
   process.

6. The Zcash Community Grants Committee's funding decisions will be final, 
   requiring no approval from the FPF Board, but are subject to veto if FPF
   judges them to violate Cayman law or the FPF's reporting requirements and 
   other (current or future) obligations under the Cayman Islands’ Companies 
   Act (2023 Revision) and Foundation Companies Law, 2017.

7. Zcash Community Grants Committee members SHALL have a one-year term and MAY 
   sit for reelection. The Zcash Community Grants Committee is subject to the 
   same conflict of interest policy that governs the FPF Board of Directors 
   (i.e. they MUST recuse themselves when voting on proposals where they have 
   a financial interest). At most one person with association with the BP/ECC, 
   at most one person with association with the ZF and at most one person with 
   association with the FPF, are allowed to sit on the Zcash Community Grants 
   Committee.  "Association" here means: having a financial interest, 
   full-time employment, being an officer, being a director, or having an 
   immediate family relationship with any of the above. 
   
8. A portion of the ZCG Slice shall be allocated to a Discretionary Budget, 
   which may be disbursed for expenses reasonably related to the 
   administration of Zcash Community Grants. The amount of funds allocated to  
   the Discretionary Budget SHALL be decided by the ZF's Zcash Community 
   Advisory Panel or successor process. Any disbursement of funds from the 
   Discretionary Budget MUST be approved by the Zcash Community Grants 
   Committee. Expenses related to the administration of Zcash Community Grants 
   include, without limitation the following:
  
   * Paying for operational management and administration services that 
     support the purpose of the Zcash Community Grants program, including
     administration services provided by FPF.
   * Paying third party vendors for services related to domain name
     registration, or the design, website hosting and administration of
     websites for the Zcash Community Grants Committee.
   * Paying independent consultants to develop requests for proposals that
     align with the Zcash Community Grants program.
   * Paying independent consultants for expert review of grant applications.
   * Paying for sales and marketing services to promote the Zcash Community 
     Grants program.
   * Paying third party consultants to undertake activities that support the 
     purpose of the Zcash Community Grants program. 
   * Reimbursement to members of the Zcash Community Grants Committee for 
     reasonable travel expenses, including transportation, hotel and meals 
     allowance.
     
   The Zcash Community Grants Committee's decisions relating to the allocation 
   and disbursement of funds from the Discretionary Budget will be final, 
   requiring no approval from the FPF Board, but are subject to veto if FPF 
   judges them to violate Cayman law or the FPF's reporting requirements and 
   other (current or future) obligations under Cayman Islands law.


9. A portion of the Discretionary Budget MAY be allocated to provide 
   reasonable compensation to members of the Zcash Community Grants Committee.
   The time for which each Committee member is compensated SHALL be limited to 
   the hours needed to successfully perform their positions, up to a maximum 
   of 15 hours in each month, and MUST align with the scope and 
   responsibilities of that member's role. The compensation rate for each 
   Committee member SHALL be $115 per hour (and therefore the maximum 
   compensation for a Committee member is $1725 per month). The allocation and 
   distribution of compensation to committee members SHALL be administered by
   FPF. Changes to the hours or rate SHALL be determined by the ZF’s Zcash 
   Community Advisory Panel or successor process.

As part of the contractual commitment specified under the `Enforcement`_ section 
below, FPF SHALL be contractually required to recognize the ZCG slice of the Dev 
Fund as a Restricted Fund donation under the above constraints (suitably 
formalized), and keep separate accounting of its balance and usage under its 
`Transparency and Accountability`_ obligations defined below.


DFR slice (Dev Fund Reserve)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This slice of the Dev Fund is to be stored in a Lockbox until such time as the  
Zcash Community reaches consensus on the design of a disbursement mechanism 
that is defined in a ZIP and implemented as part of a future Network Upgrade. 


Transparency and Accountability
-------------------------------

Obligations
~~~~~~~~~~~

ZF, FPF and Zcash Community Grant recipients (during and leading to their award 
period) SHALL all accept the obligations in this section.

Ongoing public reporting requirements:

* Quarterly reports, detailing future plans, execution on previous plans, and 
  finances (balances, and spending broken down by major categories).
* Monthly developer calls, or a brief report, on recent and forthcoming tasks. 
  (Developer calls may be shared.)
* Annual detailed review of the organization performance and future plans.
* Annual financial report (IRS Form 990, or substantially similar 
  information).

These reports may be either organization-wide, or restricted to the income, 
expenses, and work associated with the receipt of Dev Fund. 

It is expected that ZF, FPF and Zcash Community Grant recipients will be 
focused primarily (in their attention and resources) on Zcash. Thus, they MUST
promptly disclose:

* Any major activity they perform (even if not supported by the Dev Fund) that 
  is not in the interest of the general Zcash ecosystem.
* Any conflict of interest with the general success of the Zcash ecosystem.

BP, ECC, ZF, FPF and grant recipients MUST promptly disclose any security or 
privacy risks that may affect users of Zcash (by responsible disclosure under 
confidence to the pertinent developers, where applicable).

ZF's and FPF's annual reports on its non-grant operations, SHOULD be at least 
as detailed as grant proposals/reports submitted by other funded parties, and 
satisfy similar levels of public scrutiny.

All substantial software whose development was funded by the Dev Fund SHOULD 
be released under an Open Source license (as defined by the Open Source 
Initiative [#osd]_), preferably the MIT license.

The ZF SHALL continue to operate the Zcash Community Advisory Panel and SHOULD 
work toward making it more representative and independent (more on that below).

Enforcement
~~~~~~~~~~~

For grant recipients, these conditions SHOULD be included in their contract 
with FPF, such that substantial violation, not promptly remedied, will cause 
forfeiture of their grant funds and their return to FPF.

ZF and FPF MUST contractually commit to each other to fulfill these conditions, 
and the prescribed use of funds, such that substantial violation, not promptly 
remedied, will permit the other parties to issue a modified version of Zcash 
node software that removes the violating party's Dev Fund slice, and use the 
Zcash trademark for this modified version. The slice's funds will be reassigned 
to ZCG (whose integrity is legally protected by the Restricted Fund treatment).


Amendments and Replacement of the Dev Fund
------------------------------------------

Nothing in this ZIP is intended to preclude any amendments to the Dev Fund 
(including but not limited to, changes to the Dev Fund allocation and/or the 
addition of new Dev Fund recipients), if such amendments enjoy the consensus 
support of the Zcash community. 

Nothing in this ZIP is intended to preclude replacement of the Dev Fund with a 
different mechanism for ecosystem development funding. 

ZF and FPF SHOULD facilitate the amendment or replacement of the Dev Fund if 
there is sufficient community support for doing so. 

This ZIP recognizes there is strong community support for a non-direct funding 
model. As such, ZF MUST collaborate with the Zcash community to research and 
explore the establishment of a non-direct funding model. The research should 
consider potential designs as well as possible legal and regulatory risks.


Future Community Governance
---------------------------

Decentralized community governance is used in this proposal via the Zcash 
Community Advisory Panel as input into the Zcash Community Grants Committee 
which governs the `ZCG slice (Zcash Community Grants)`_.

It is highly desirable to develop robust means of decentralized community
voting and governance, either by expanding the Zcash Community Advisory Panel 
or a successor mechanism. ZF, FPF and ZCG SHOULD place high priority on such 
development and its deployment, in their activities and grant selection.


ZF Board Composition
--------------------

Members of ZF's Board of Directors MUST NOT hold equity in ECC or have current 
business or employment relationships with ECC or BP.

The Zcash Foundation SHOULD endeavor to use the Zcash Community Advisory Panel 
(or successor mechanism) as advisory input for future board elections.


FPF Board Composition
---------------------

Members of FPF's Board of Directors MUST NOT hold equity in ECC or have current 
business or employment relationships with ECC or BP. 


Acknowledgements
================

This proposal is a modification of ZIP 1014 [#zip-1014]_ by the Zcash Foundation based on 
feedback and suggestions from the community, and incorporating elements of draft ZIPs by 
community members Jason McGee and Skylar. 

ZIP 1014 is a limited modification of Eran Tromer's ZIP 1012 [#zip-1012]_
by the Zcash 
Foundation and ECC, further modified by feedback from the community.

Eran's proposal is most closely based on the Matt Luongo 'Decentralize the
Dev Fee' proposal (ZIP 1011) [#zip-1011]_. Relative to ZIP 1011 there are substantial 
changes and mixing in of elements from *@aristarchus*'s '20% Split Evenly 
Between the ECC and the Zcash Foundation' (ZIP 1003) [#zip-1003]_, Josh Cincinnati's 
'Compromise Dev Fund Proposal With Diverse Funding Streams' (ZIP 1010) [#zip-1010]_, and 
extensive discussions in the `Zcash Community Forum`_, including valuable comments 
from forum users *@aristarchus* and *@dontbeevil*. 

.. _Zcash Community Forum: https://forum.zcashcommunity.com/


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
.. [#zip-1012] `ZIP 1012: Dev Fund to ECC + ZF + Major Grants <zip-1012.rst>`_
.. [#zip-1014] `ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants <zip-1014.rst>`_
.. [#zip-2001] `ZIP 2001: Lockbox Funding Streams <zip-2001.rst>`_
.. [#zcap] `Zcash Community Advisory Panel <https://zfnd.org/zcap/>`_
.. [#section501c3] `U.S. Code, Title 26, Section 501(c)(3) <https://www.law.cornell.edu/uscode/text/26/501>`_

