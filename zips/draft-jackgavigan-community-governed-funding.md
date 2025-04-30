    ZIP: XXX
    Title: Community-Governed Funding Model
    Owners: Jack Gavigan <jackgaviganzip@gmail.com>
    Status: Draft
    Category: Consensus / Process
    Created: 2025-03-31
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "SHOULD", and "MAY" in this document are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as defined in the Zcash protocol specification [^protocol-networks].

The terms "Electric Coin Company" (or "ECC"), "Bootstrap Project" (or "BP") and "Zcash Foundation" (or "ZF") in this document are to be interpreted as described in ZIP 1014 [^zip-1014].

The terms "Zcash Community Grants" (or "ZCG"), "ZCG Committee", "Financial Privacy Foundation" (or "FPF"), and "Deferred Dev Fund Lockbox" in this document are to be interpreted as defined in ZIP 1015 [^zip-1015].

"Shielded Labs" refers to the Assocation of that name registered in the Swiss canton of Zug under the Unique Identifier CHE-243.302.798.

Protocol-defined Ecosystem Funding is funding from sources defined by the Zcash Protocol for development of the Zcash ecosystem. At the time of writing, Protocol-defined Ecosystem Funding is allocated from a portion of block rewards via Funding Streams [^zip-0207] and Lockbox Funding Streams [^zip-2001].

“ZEC” refers to the native currency of Zcash on Mainnet.


# Abstract

This proposal outlines a funding model that ensures that Zcash ecosystem funding and grant-making and funding decisions reflect the clear consensus of the Zcash community. 

In this model:

* 8% of the block rewards will be allocated to the ZCG for grants by and for the Zcash Community.
* 12% of the block rewards will accrue to a fund controlled by decisions of ZCAP members, seeded by the Deferred Dev Fund Lockbox.

The ZCAP-Controlled Fund may be used to distribute larger grants to ecosystem participants, or left at rest.

This model would be activated  until the 3rd halving, allowing enough time to determine whether it should be changed or codified for longer.


# Motivation

If no action is taken, in November 2025 funds from block subsidies will stop being directed to Zcash Community Grants [^zip-1015-zcg] and to the Deferred Dev Fund Lockbox established by ZIP 2001 [^zip-2001]. If the block subsidies stop, it will risk a gap in funding of Zcash development organisations, either via ZCG grants or via potential future disbursements from the Deferred Dev Fund Lockbox.

This proposal aims to:
* enshrine the primacy of the clear consensus of the Zcash community in funding decisions, 
* decentralize decision-making,
* hold stakeholders accountable for outcomes,
* be dynamic enough to allow for change, and
* provide clarity on decision-making.

It would immediately amplify Zcash community members' voices, minimize governance confusion, and simplify decision-making.

# Requirements

* There is a well-defined, publically agreed, process for evaluation and community feedback on grant proposals.
* Funds are held in a multisig resistant to compromise of some of the parties' keys, up to a given threshold.
* No single party's non-cooperation or loss of keys is able to cause any Protocol-defined Ecosystem Funding to be locked up unrecoverably.
* During the period of this proposal, the block rewards are distributed as described in the [Abstract] above.
* The funds from the 8% funding stream will be usable immediately on activation of this ZIP.
* The funds in the Deferred Dev Fund Lockbox will be usable immediately on activation of this ZIP.
* Any use of Deferred Dev Fund Lockbox funds is consistent with the purpose specified in [^zip-1015-lockbox] of "funding grants to ecosystem participants".

# Non-requirements

* Any changes to the ZCG or its governance, such as its expansion to include more members, may be desired but are specifically outside this proposal’s scope.
* Any changes to Zcash protocol governance, specifically what changes are made to consensus node software, are outside this proposal’s scope.

# Specification

This proposal empowers both the community (as represented by the Zcash Community Advisory Panel, and ZCG) to independently determine what, if anything, should be funded through development fund grants.

The funding streams described below will be defined in a new revision of ZIP 214 [^zip-0214].

## Zcash Community Grants

A funding stream will be established for Zcash Community Grants, consisting of 8% of the block subsidy, and subject to all of the same rules currently specified in ZIP 1015 [^zip-1015-zcg].

This funding stream will start on expiry of the existing ``FS_FPF_ZCG`` funding stream [^zip-1015-funding-streams], and last for a further 1,260,000 blocks (approximately 3 years), ending at Zcash's 3rd halving.

## ZCAP-Controlled Fund

A pool of multisig-controlled funds, seeded from the existing contents of the ZIP 1015 Deferred Dev Fund Lockbox [^zip-1015-lockbox] and supplemented with a funding stream consising of 12% of the block subsidy for the same time period as the Zcash Community Grants stream, forms a new ZCAP-Controlled Fund. The mechanisms for the creation and management of this fund are described by the Deferred Dev Fund Lockbox Disbursement proposal [^draft-ecc-lockbox-disbursement] (subject to the amendment described below). This proposal sets the $\mathsf{stream\_value}$ parameter of that proposal to 12%, and the $\mathsf{stream\_end\_height}$ parameter to mainnet block height 4406400, equal to that of the Zcash Community Grants stream so that both streams end at Zcash's 3rd halving.
 
## Amendment to the Deferred Dev Fund Lockbox Disbursement ZIP [^draft-ecc-lockbox-disbursement]

In the section **One-time lockbox disbursement**, replace

> The coinbase transaction of the activation block of this ZIP MUST include an additional output to a 3-of-5 P2SH multisig with keys held by the following "Key-Holder Organizations": Zcash Foundation, the Electric Coin Company, Shielded Labs, and two other organizations yet to be decided.

with

> The coinbase transaction of the activation block of this ZIP MUST include an additional output to a 3-of-5 P2SH multisig with keys held by the following "Key-Holder Organizations": Zcash Foundation, the Electric Coin Company, Shielded Labs, the Financial Privacy Foundation, and one other organization to be decided by a ZCAP vote.

### Requirements on use of the ZCAP-Controlled Fund

The Key-Holder Organizations SHALL be bound by a legal agreement to only use
funds held in the ZCAP-Controlled Fund according to the specifications in
this ZIP, expressed in suitable legal language. In particular, all requirements
on the use of Deferred Dev Fund Lockbox funds in ZIP 1015 [^zip-1015-lockbox]
MUST be followed for ZCAP-Controlled Fund.

The legal agreement referenced above MUST be in place before the one-time 
lockbox disbursement (as specified in [^draft-ecc-lockbox-disbursement]) is 
carried out, and before any funds are disbursed from the ZCAP-Controlled Fund.

Once three Key-Holder Organizations have entered into a legal agreement as 
referenced above, the remaining Key-Holder Organizations shall have 30 calendar 
days to join the agreement. If any or the proposed Key-Holder Organizations
have not entered into the legal agreement after the expiry of the 30 calendar day
period, those Key-Holder Organizations who have entered into the agreement MAY 
propose to ZCAP that the dissenting Key-Holder Organization(s) be replaced with 
appropriate alternatives (or the number of Key-Holder Organizations be reduced). 
If ZCAP approves the proposal, the list of Key-Holder Organizations shall be 
amended accordingly. 

The Key-Holder Organizations collectively administer the ZCAP-Controlled
Fund based on decisions taken by ZCAP voting, following a model decided
by the community and specified in another ZIP [TBD].

### Disbursement process

1. Anyone can submit a grant application via a process agreed upon by the Key-Holder Organizations.
2. Grant applications with total below USD 500,000 (or equivalent in another currency) are directed to ZCG.
3. For grant applications above this threshold, a 30-day community review and feedback period will start.
4. If a grant application is not [vetoed](#veto-process) and proceeds to a ZCAP vote according to the agreed process, then ZCAP members will be asked to vote on it.
5. If the vote passes, then as payments are scheduled for the grant, then (subject to the [Veto process]) the Key-Holder Organizations SHOULD sign the corresponding transactions for disbursement from the ZCAP-Controlled Fund.

For ZCAP votes, a minimum of 50% of ZCAP members must participate in the vote, 
with a simple majority (i.e. 50% of the number of vote participants, plus one) 
cast in favour for a grant proposal to be approved. Upon approval, the grants 
are paid to the recipient per the terms of the grant proposal. In the case that 
multiple grant proposals are submitted that are in competition with one another, 
the proposal that attracts the highest approval from ZCAP members will be the 
winner. It is the responsibility of the Key-Holder Organizations to
determine whether proposals are in competition with one another when organizing
ZCAP votes.

ZCAP members SHOULD take account of the same factors considered by the ZCG
Committee (described in points 2, 3, and 4 of [^zip-1015-zcg]) in deciding
whether to fund a grant. If any contentious issue arises in connection with a
grant (such as milestones not being met), or periodically for grants of
indefinite duration, the Key-Holder Organizations SHOULD hold additional
ZCAP votes to determine whether funding should continue.

ZCAP members are not obligated to fund any grants and MAY leave the funds at rest.

No organizations or individuals are restricted from participating in ZCAP votes.


### Veto process

A grant is vetoed if:

* any Key-Holder Organization declares that funding the grant would violate any of its legal or reporting obligations; or
* two or more Key-Holder Organizations declare that they have a principled objection to it on the basis of potential harm to Zcash users, or because it is antithetical to the values of the Zcash community.

If a grant is vetoed after passing a ZCAP vote, then payments for it MUST be stopped. This is expected to be an unusual situation that would only occur if new adverse information came to light, or in the case of a change in the law or unanticipated legal proceedings.

The Key-holder Organizations cannot veto ZCAP rejection of a proposal.

Vetos are intended for exceptional cases and SHOULD be accompanied by a thorough rationale.

## Administrative obligations and constraints

All provisions of ZIP 1015 imposing obligations and constraints on Bootstrap Project, Electric Coin Company, Zcash Foundation, Financial Privacy Foundation, the ZCG Committee, and grant recipients relating to the previous ``FS_FPF_ZCG`` funding stream, SHALL continue in effect for Zcash Community Grants.

These obligations and constraints will be extended to all Key-Holder Organizations in respect of the ZCAP-Controlled Fund.

The provisions after the first paragraph of the section "Zcash Community Grants (ZCG)" also apply to the Key-Holder Organizations' administration of the ZCAP-Controlled Fund, with ZCAP voting replacing the role of the ZCG Committee.

The ZF SHALL continue to operate ZCAP and SHOULD work toward making it more 
representative and independent, including through collaboration with the other
Key-holder Organizations. 

Key-holder Organizations that collaborate with ZF to determine the make-up of 
ZCAP SHOULD endeavor to use ZCAP as advisory input for future board elections.

Note: Nothing forces developers of Zcash consensus node software to implement any particular proposal. The aim of a process specification like this one is only to social consensus. It fundamentally cannot affect the autonomy of developers of Zcash consensus node software to publish (or not) the software they want to publish, or the autonomy of node operators to run (or not) the software they want to run.

## Security precautions

The Key-Holder Organizations and the ZCG Committee MUST take appropriate precautions to safeguard funds from theft or accidental loss. Any theft or loss of funds, or any loss or compromise of key material MUST be reported to the Zcash community as promptly as possible after applying necessary mitigations.

## Testnet-specific considerations

In order to allow the mechanism and process for ZCAP voting to be tested,
this process SHOULD be rehearsed on Testnet. The threshold of 50% approval
applied to Mainnet ZCAP votes does not apply to these rehearsals.

# Open questions

* Is a 3-of-5 threshold appropriate? What should the other Key-Holder Organization be?
* Is 50% participation the right threshold for ZCAP votes?
* Is USD 500,000 the right threshold for grants to be controlled by ZCAP vote rather than ZCG?

# Acknowledgements

This proposal is a limited modification of Tatyana Peacemonger and Josh Swihart's Community and Coinholder Funding Model proposal [^zip-ccfm-draft].

# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2024.5.1 or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2024.5.1. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-lockbox]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Lockbox](zip-1015#lockbox)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Zcash Community Grants](zip-1015#zcash-community-grants-zcg)

[^zip-1015-funding-streams]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Funding Streams](zip-1015#funding-streams)

[^draft-ecc-lockbox-disbursement]: [draft-ecc-lockbox-disbursement: Deferred Dev Fund Lockbox Disbursement](draft-ecc-zbloc.md)

[^zip-1015-transparency-and-accountability]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Transparency and Accountability](zip-1015#transparency-and-accountability)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](zip-2001.rst)

[^draft-ecc-zbloc]: [draft-ecc-zbloc: Zcash Governance Bloc](draft-ecc-zbloc.md)

[^zip-ccfm-draft]: [Draft ZIP: Community and Coinholder Funding Model](draft-ecc-community-and-coinholder.md)
