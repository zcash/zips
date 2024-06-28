~~~
ZIP: XXXX
Title: One year extension to existing ZIP 1014 ; Dev Fund for ECC, ZF, and Major Grants
Owner: Josh Swihart <josh@electriccoin.co>
Original - ZIP 1014 Authors: Eran Tromer
Credits: Matt Luongo
         @aristarchus
         @dontbeevil
         Daira-Emma Hopwood
         George Tankersley
         Josh Cincinnati
         Andrew Miller
         Zooko Wilcox
Status:
Category: Consensus Process
Created: 2024-5-24
License: MIT
Discussions-To:
~~~

# Terminology
The key words "MUST", "MUST NOT", "SHALL", "SHALL NOT", "SHOULD", and "MAY" in
this document are to be interpreted as described in BCP 14 [1] when, and only
when, they appear in all capitals.

The term "network upgrade" in this document is to be interpreted as described
in ZIP 200 [6] and the Zcash Trademark Donation and License Agreement ([4] or
successor agreement).

The term “non-direct funding model” in this document is to be interpreted as a
funding model where no wallet address is built into the protocol that is
controlled by a single organization or person. 

The term “one-year extension” is to be interpreted as a period of blocks
corresponding to one year starting from the second Zcash halving in 2024,
through exactly one quarter of the third halving period ending in 2028. This
corresponds to a period of approximately one year. This ZIP is assumed to
activate at or before the start of this period on Zcash mainnet.

The terms "block subsidy" and "halving" in this document are to be interpreted
as described in sections 3.10 and 7.8 of the Zcash Protocol Specification. [2]

"Electric Coin Company", also called "ECC", refers to the Zerocoin Electric
Coin Company, LLC.

"Bootstrap Project", also called "BP", refers to the 501(c)(3) nonprofit
corporation of that name.

"Zcash Foundation", also called "ZF", refers to the 501(c)(3) nonprofit
corporation of that name.

"Section 501(c)(3)" refers to that section of the U.S. Internal Revenue Code
(Title 26 of the U.S. Code). [12]

"Zcash Community Grants" refers to the panel of community members assembled by
the Zcash Foundation and described at [11].

The terms "Testnet" and "Mainnet" are to be interpreted as described in section
3.12 of the Zcash Protocol Specification [3].

# Abstract 
This proposal describes a modification of the existing Zcash Development Fund
(ZIP 1014) which is set to expire in November of 2024. The goal is to provide a
one-year extension for the creation of a non-direct funding model for Zcash
development. If a non-direct funding model can be established and approved by
the community at any point within this one-year extension period, that model
will supersede and terminate the one-year extension.  This Dev Fund Extension
would consist of the continuance of 20% of the block subsidies, split into 3
slices:

- 35% for the Bootstrap Project (the parent of the Electric Coin Company);
- 25% for Zcash Foundation (for internal work and grants);
- 40% for additional "Major Grants" for large-scale long-term projects
  (administered by the Zcash Foundation, with extra community input and
  scrutiny).

Governance and accountability are based on existing entities and legal
mechanisms, and increasingly decentralized governance is encouraged.

# Motivation 
Starting in November 2024 the current Zcash Development Fund will expire
leaving 100% of the block subsidy allocated to miners, and no further funds
will be automatically allocated to any other entities. Due to the short timing
before the halving occurs this one-year extension will serve to give the Zcash
community time to develop and deploy a non-direct funding model to support
future Zcash development work. Consequently, if the current fund expires in
November 2024 then no substantial new funding may be available to existing
teams dedicated to furthering charitable, educational, or scientific purposes,
such as research, development, and outreach: the Electric Coin Company (ECC),
the Zcash Foundation (ZF), and the many entities funded by the ZF grant
program.

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
of Section 501(c)(3).

# Requirements 
The extension period should be used to design, gain community consensus on, and
implement a non-direct funding model. 

The Dev Fund should encourage decentralization of the work and funding, by
supporting new teams dedicated to Zcash.

The Dev Fund should maintain the existing teams and capabilities in the Zcash
ecosystem, unless and until concrete opportunities arise to create even greater
value for the Zcash ecosystem.

There should not be any single entity which is a single point of failure, i.e.,
whose capture or failure will effectively prevent effective use of the funds.

Major funding decisions should be based, to the extent feasible, on inputs from
domain experts and pertinent stakeholders.

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
implement. In particular, during the extension period, it should not assume the
creation of new mechanisms (e.g., election systems) or entities (for governance
or development) for its execution; but it should strive to support and use
these once they are built.

Comply with legal, regulatory, and taxation constraints in pertinent
jurisdictions.

# Non-requirements 
General on-chain governance is outside the scope of this proposal.

Rigorous voting mechanisms (whether coin-weighted, holding-time-weighted or
one-person-one-vote) are outside the scope of this proposal, though there is
prescribed room for integrating them once available.

# Specification 
Consensus changes implied by this specification are applicable to the Zcash
Mainnet. Similar (but not necessarily identical) consensus changes SHOULD be
applied to the Zcash Testnet for testing purposes.

# Dev Fund allocation 
Starting at the second Zcash halving in 2024, through exactly one quarter of
the third halving period ending in 2028, 20% of the block subsidy of each block
SHALL be allocated to a "Dev Fund" that consists of the following three slices:

- 35% for the Bootstrap Project (denoted BP slice);
- 25% for the Zcash Foundation, for general use (denoted ZF slice);
- 40% for additional "Major Grants" for large-scale long-term projects (denoted MG slice).

The slices are described in more detail below. The fund flow will be
implemented at the consensus-rule layer, by sending the corresponding ZEC to
the designated address(es) for each block. This Dev Fund will end after the
one-year extension.

## BP slice (Bootstrap Project) 
This slice of the Dev Fund will flow as charitable contributions from the Zcash
Community to the Bootstrap Project, the parent organization to the Electric
Coin Company. The Bootstrap Project is organized for exempt educational,
charitable, and scientific purposes in compliance with Section 501(c)(3),
including but not limited to furthering education, information, resources,
advocacy, support, community, and research relating to cryptocurrency and
privacy, including Zcash. This slice will be used at the discretion of the
Bootstrap Project for any purpose within its mandate to support financial
privacy and the Zcash platform as permitted under Section 501(c)(3). The BP
slice will be treated as a charitable contribution from the Community to
support these educational, charitable, and scientific purposes.

## ZF slice (Zcash Foundation's general use) 
This slice of the Dev Fund will flow as charitable contributions from the Zcash
Community to ZF, to be used at its discretion for any purpose within its
mandate to support financial privacy and the Zcash platform, including:
development, education, supporting community communication online and via
events, gathering community sentiment, and awarding external grants for all of
the above, subject to the requirements of Section 501(c)(3). The ZF slice will
be treated as a charitable contribution from the Community to support these
educational, charitable, and scientific purposes.

## MG slice (Major Grants) 
This slice of the Dev Fund is intended to fund independent teams entering the
Zcash ecosystem, to perform major ongoing development (or other work) for the
public good of the Zcash ecosystem, to the extent that such teams are available
and effective.

The funds SHALL be received and administered by ZF. ZF MUST disburse them for
"Major Grants" and expenses reasonably related to the administration of Major
Grants, but subject to the following additional constraints:

1. These funds MUST only be used to issue Major Grants to external parties that
   are independent of ZF, and to pay for expenses reasonably related to the
   administration of Major Grants. They MUST NOT be used by ZF for its internal
   operations and direct expenses not related to administration of Major
   Grants. Additionally, BP, ECC, and ZF are ineligible to receive Major
   Grants.
2. Major Grants SHOULD support well-specified work proposed by the grantee, at
   reasonable market-rate costs. They can be of any duration or ongoing without
   a duration limit. Grants of indefinite duration SHOULD have semiannual
   review points for continuation of funding.
3. Priority SHOULD be given to Major Grants that bolster teams with substantial
   (current or prospective) continual existence, and set them up for long-term
   success, subject to the usual grant award considerations (impact, ability,
   risks, team, cost-effectiveness, etc.). Priority SHOULD be given to Major
   Grants that support ecosystem growth, for example through mentorship,
   coaching, technical resources, creating entrepreneurial opportunities, etc.
   If one proposal substantially duplicates another's plans, priority SHOULD be
   given to the originator of the plans.
4. Major Grants SHOULD be restricted to furthering the Zcash cryptocurrency and
   its ecosystem (which is more specific than furthering financial privacy in
   general) as permitted under Section 501(c)(3).
5. Major Grants awards are subject to approval by a five-seat Major Grant
   Review Committee. The Major Grant Review Committee SHALL be selected by the
   ZF's Community Advisory Panel or successor process.
6. The Major Grant Review Committee's funding decisions will be final,
   requiring no approval from the ZF Board, but are subject to veto if the
   Foundation judges them to violate U.S. law or the ZF's reporting
   requirements and other (current or future) obligations under U.S. IRS
   501(c)(3).
7. Major Grant Review Committee members SHALL have a one-year term and MAY sit
   for reelection. The Major Grant Review Committee is subject to the same
   conflict of interest policy that governs the ZF Board of Directors (i.e.
   they MUST recuse themselves when voting on proposals where they have a
   financial interest). At most one person with association with the BP/ECC,
   and at most one person with association with the ZF, are allowed to sit on
   the Major Grant Review Committee. "Association" here means: having a
   financial interest, full-time employment, being an officer, being a
   director, or having an immediate family relationship with any of the above.
   The ZF SHALL continue to operate the Community Advisory Panel and SHOULD
   work toward making it more representative and independent (more on that
   below).
8. A portion of the MG Slice shall be allocated to a Discretionary Budget,
   which may be disbursed for expenses reasonably related to the administration
   of Major Grants. The amount of funds allocated to the Discretionary Budget
   SHALL be decided by the ZF's Community Advisory Panel or successor process.
   Any disbursement of funds from the Discretionary Budget MUST be approved by
   the Major Grant Review Committee. Expenses related to the administration of
   Major Grants include, without limitation the following:
    - Paying third party vendors for services related to domain name registration,
    - or the design, website hosting and administration of websites for the Major
    - Grant Review Committee.
    - Paying independent consultants to develop requests for proposals that
      align with the Major Grants program.
    - Paying independent consultants for expert review of grant applications.
    - Paying for sales and marketing services to promote the Major Grants program.
    - Paying third party consultants to undertake activities that support the
      purpose of the Major Grants program.
    - Reimbursement to members of the Major Grant Review Committee for
      reasonable travel expenses, including transportation, hotel and meals
      allowance.

The Major Grant Review Committee's decisions relating to the allocation and
disbursement of funds from the Discretionary Budget will be final, requiring no
approval from the ZF Board, but are subject to veto if the Foundation judges
them to violate U.S. law or the ZF's reporting requirements and other (current
or future) obligations under U.S. IRS 501(c)(3).

ZF SHALL recognize the MG slice of the Dev Fund as a Restricted Fund donation
under the above constraints (suitably formalized), and keep separate accounting
of its balance and usage under its Transparency and Accountability obligations
defined below.

ZF SHALL strive to define target metrics and key performance indicators, and
the Major Grant Review Committee SHOULD utilize these in its funding decisions.

# Transparency and Accountability 
## Obligations
BP, ECC, ZF, and Major Grant recipients (during and leading to their award
period) SHALL all accept the obligations in this section.

For the duration of this extension the ECC, ZF, BP, SHALL coordinate and
cooperate together to establish a non-direct funding model that will supersede
this ZIP no later than the expiration of the one-year extension period.

Ongoing public reporting requirements:

* Quarterly reports, detailing future plans, execution on previous plans, and
  finances (balances, and spending broken down by major categories). Monthly
  developer calls, or a brief report, on recent and forthcoming tasks.
  (Developer calls may be shared.)
* Annual detailed review of the organization performance and future plans.
* Annual financial report (IRS Form 990, or substantially similar information).
* These reports may be either organization-wide, or restricted to the income,
  expenses, and work associated with the receipt of Dev Fund. As BP is the
  parent organization of ECC it is expected they may publish joint reports.

It is expected that ECC, ZF, and Major Grant recipients will be focused
primarily (in their attention and resources) on Zcash. Thus, they MUST promptly
disclose:

* Any major activity they perform (even if not supported by the Dev Fund) that
  is not in the interest of the general Zcash ecosystem.
* Any conflict of interest with the general success of the Zcash ecosystem.
* BP, ECC, ZF, and grant recipients MUST promptly disclose any security or
  privacy risks that may affect users of Zcash (by responsible disclosure under
  confidence to the pertinent developers, where applicable).

BP's reports, ECC's reports, and ZF's annual report on its non-grant
operations, SHOULD be at least as detailed as grant proposals/reports submitted
by other funded parties, and satisfy similar levels of public scrutiny.

All substantial software whose development was funded by the Dev Fund SHOULD be
released under an Open Source license (as defined by the Open Source Initiative
[5]), preferably the MIT license.

## Enforcement 
For grant recipients, these conditions SHOULD be included in their contract
with ZF, such that substantial violation, not promptly remedied, will cause
forfeiture of their grant funds and their return to ZF.

BP, ECC, and ZF MUST contractually commit to each other to fulfill these
conditions, and the prescribed use of funds, such that substantial violation,
not promptly remedied, will permit the other party to issue a modified version
of Zcash node software that removes the violating party's Dev Fund slice. The
slice's funds will be reassigned to MG (whose integrity is legally protected by
the Restricted Fund treatment).

# Future Community Governance 
Decentralized community governance is used in this proposal via the Community
Panel as input into the Major Grant Review Committee which governs the MG slice
(Major Grants).

# ZF Board Composition 
Members of ZF's Board of Directors MUST NOT hold equity in ECC or have current
business or employment relationships with ECC.

The Zcash Foundation SHOULD endeavor to use the Community Advisory Panel (or
successor mechanism) as advisory input for future board elections.

# Acknowledgments 
This proposal is a modification of ZIP 1014, which itself was a limited
modification of Eran Tromer's ZIP 1012 [10] by the Zcash Foundation and the
ECC, further modified by feedback from the community and the results of a
Helios poll.

Eran's proposal was most closely based on the Matt Luongo 'Decentralize the Dev
Fee' proposal (ZIP 1011) [9]. Relative to ZIP 1011 there were substantial
changes and mixing in of elements from @aristarchus's '20% Split Evenly Between
the ECC and the Zcash Foundation' (ZIP 1003) [7], Josh Cincinnati's 'Compromise
Dev Fund Proposal With Diverse Funding Streams' (ZIP 1010) [8], and extensive
discussions in the Zcash Community Forum.

The authors are grateful to all of the above for their excellent ideas and any
insightful discussions, and to forum users @aristarchus and @dontbeevil for
valuable initial comments on ZIP 1012.

# References 
1.	Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"
2.	Zcash Protocol Specification, Version 2021.2.16 or later
3.	Zcash Protocol Specification, Version 2021.2.16. Section 3.12: Mainnet and Testnet
4.	Zcash Trademark Donation and License Agreement
5.	The Open Source Definition
6.	ZIP 200: Network Upgrade Mechanism
7.	ZIP 1003: 20% Split Evenly Between the ECC and the Zcash Foundation, and a Voting System Mandate
8.	ZIP 1010: Compromise Dev Fund Proposal With Diverse Funding Streams
9.	ZIP 1011: Decentralize the Dev Fee
10.	ZIP 1012: Dev Fund to ECC + ZF + Major Grants
11.	ZF Community Advisory Panel
12.	U.S. Code, Title 26, Section 501(c)(3)
