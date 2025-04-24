    ZIP: XXX
    Title: Community and Coinholder Funding Model
    Owners: Josh Swihart <josh@electriccoin.co>
    Credits: Daira-Emma Hopwood
             Kris Nuttycombe
             Jack Grigg
             Tatyana Peacemonger
             Alex Bornstein
             Jason McGee
    Status: Draft
    Category: Consensus / Process
    Created: 2025-02-19
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

This proposal outlines a funding model that gives the community and coin holders distinct voices in determining what, if any, grants are provided to support Zcash’s development and community efforts.

In this model:

* 8% of the block rewards will be allocated to the ZCG for grants by and for the Zcash Community.
* 12% of the block rewards will accrue to a fund controlled by decisions of coin holders, seeded by the Deferred Dev Fund Lockbox.

The Coinholder-Controlled Fund may be used to distribute larger grants to ecosystem participants, or left at rest.

This model would be activated through until the 3rd halving, allowing enough time to determine whether it should be changed or codified for longer.


# Motivation

If no action is taken, in November 2025 funds from block subsidies will stop being directed to Zcash Community Grants [^zip-1015-zcg] and to the Deferred Dev Fund Lockbox established by ZIP 2001 [^zip-2001]. If the block subsidies stop, it will risk a gap in funding of Zcash development organisations, either via ZCG grants or via potential future disbursements from the Deferred Dev Fund Lockbox.

This proposal aims to:
* decentralize decision-making,
* hold stakeholders accountable for outcomes,
* be dynamic enough to allow for change, and
* provide clarity on decision-making.

It would immediately increase coinholders’ voice, minimize governance confusion, and simplify decision-making.

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

This proposal empowers both the community (through ZCG) and coin holders to independently determine what, if anything, should be funded through development fund grants.

The funding streams described below will be defined in a new revision of ZIP 214 [^zip-0214].

## Zcash Community Grants

A funding stream will be established for Zcash Community Grants, consisting of 8% of the block subsidy, and subject to all of the same rules currently specified in ZIP 1015 [^zip-1015-zcg].

This funding stream will start on expiry of the existing ``FS_FPF_ZCG`` funding stream [^zip-1015-funding-streams], and last for a further 1,260,000 blocks (approximately 3 years), ending at Zcash's 3rd halving.

## Coinholder-Controlled Fund

A pool of multisig-controlled funds, seeded from the existing contents of the ZIP 1015 Deferred Dev Fund Lockbox [^zip-1015-lockbox] and supplemented with a funding stream consising of 12% of the block subsidy for the same time period as the Zcash Community Grants stream, forms a new Coinholder-Controlled Fund. The mechanisms for the creation and management of this fund are described by the Deferred Dev Fund Lockbox Disbursement proposal [^draft-ecc-lockbox-disbursement]. This proposal sets the $\mathsf{stream\_value}$ parameter of that proposal to 12%, and the $\mathsf{stream\_end\_height}$ parameter to Mainnet block height 4406400, equal to that of the Zcash Community Grants stream so that both streams end at Zcash's 3rd halving.
 
### Requirements on use of the Coinholder-Controlled Fund

The Key-Holder Organizations SHALL be bound by a legal agreement to only use funds held in the Coinholder-Controlled Fund according to the specifications in this ZIP, expressed in suitable legal language. In particular, all requirements on the use of Deferred Dev Fund Lockbox funds in ZIP 1015 [^zip-1015-lockbox] MUST be followed for the Coinholder-Controlled Fund.

The Key-Holder Organizations collectively administer the Coinholder-Controlled Fund based on decisions taken by coinholder voting, following a model decided by the community and specified in another ZIP [TBD].

### Disbursement process

1. Anyone can submit a grant application via a process agreed upon by the Key-Holder Organizations.
2. Coinholders will vote on grant applications every three months. Grant applications must be submitted for community review 30 days prior to coinholder voting.
3. If a grant application is not [vetoed](#veto-process) and proceeds to a coinholder vote according to the agreed process, then coinholders will be asked to vote on it.
4. If the vote passes, then as payments are scheduled for the grant, then (subject to the [Veto process]) the Key-Holder Organizations SHOULD sign the corresponding transactions for disbursement from the Coinholder-Controlled Fund.

For coinholder votes, a minimum of 420,000 ZEC (2% of the total eventual supply) MUST be voted, with a simple majority cast in favor, for a grant proposal to be approved. Upon approval, the grants are paid to the recipient per the terms of the grant proposal. In the case that multiple grant proposals are submitted that are in competition with one another, a single winner will be selected by holding a separate coinholder vote for each proposal, with the approved proposal having the highest total ZEC value committed in support being the winner. It is the responsibility of the Key-Holder Organizations to determine whether proposals are in competition with one another when organizing coinholder votes.

Each coinholder vote (including in cases where multiple grants are in competition) is independent, and coins used in one vote are also allowed to be used in another; this approach is necessary to avoid vote-splitting scenarios that can result in an option being selected that achieves only a plurality (not a majority) of coinholder support.

Coinholders SHOULD take account of the same factors considered by the ZCG Committee (described in points 2, 3, and 4 of [^zip-1015-zcg]) in deciding whether to fund a grant. If any contentious issue arises in connection with a grant (such as milestones not being met), or periodically for grants of indefinite duration, the Key-Holder Organizations SHOULD hold additional coinholder votes to determine whether funding should continue.

Coinholders are not obligated to fund any grants and MAY leave the funds at rest.

No organizations or individuals are restricted from voting their coins.

### Veto process

A grant is vetoed if:

* any Key-Holder Organization declares that funding the grant would violate any of its legal or reporting obligations; or
* two or more Key-Holder Organizations declare that they have a principled objection to it on the basis of potential harm to Zcash users, or because it is antithetical to the values of the Zcash community.

If a grant is vetoed after passing a coinholder vote, then payments for it MUST be stopped. This is expected to be an unusual situation that would only occur if new adverse information came to light, or in the case of a change in the law or unanticipated legal proceedings.

The Key-holder Organizations cannot veto coinholder rejection of a proposal.

Vetos are intended for exceptional cases and SHOULD be accompanied by a thorough rationale.

## Administrative obligations and constraints

All provisions of ZIP 1015 imposing obligations and constraints on Bootstrap Project, Electric Coin Company, Zcash Foundation, Financial Privacy Foundation, the ZCG Committee, and grant recipients relating to the previous ``FS_FPF_ZCG`` funding stream, SHALL continue in effect for Zcash Community Grants.

These obligations and constraints will be extended to all Key-Holder Organizations in respect of the Coinholder-Controlled Fund.

The provisions after the first paragraph of the section "Zcash Community Grants (ZCG)" also apply to the Key-Holder Organizations' administration of the Coinholder-Controlled Fund, with coinholder voting replacing the role of the ZCG Committee.

Note: Nothing forces developers of Zcash consensus node software to implement any particular proposal. The aim of a process specification like this one is only to indicate social consensus. It fundamentally cannot affect the autonomy of developers of Zcash consensus node software to publish (or not) the software they want to publish, or the autonomy of node operators to run (or not) the software they want to run.

## Security precautions

The Key-Holder Organizations and the ZCG Committee MUST take appropriate precautions to safeguard funds from theft or accidental loss. Any theft or loss of funds, or any loss or compromise of key material MUST be reported to the Zcash community as promptly as possible after applying necessary mitigations.

## Testnet-specific considerations

In order to allow the mechanism and process for coinholder voting to be tested, this process SHOULD be rehearsed on Testnet. The threshold of 420,000 ZEC applied to Mainnet coinholder votes does not apply to these rehearsals.

# Open questions

* Is 420,000 ZEC the right threshold for coinholder votes?

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

[^draft-ecc-lockbox-disbursement]: [draft-ecc-lockbox-disbursement: Deferred Dev Fund Lockbox Disbursement](draft-ecc-lockbox-disbursement.md)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](zip-2001.rst)
