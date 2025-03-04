    ZIP: XXX
    Title: Community and Coin-holder Funding Model
    Owners: Josh Swihart <josh@electriccoin.co>
    Credits: Daira-Emma Hopwood
             Kris Nuttycombe
             Jack Grigg
             Tatyana Peacemonger
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

Protocol-defined Ecosystem Funding is funding from sources defined by the Zcash Protocol for development of the Zcash ecosystem. At the time of writing, Protocol-defined Ecosystem Funding is allocated from a portion of block rewards via Funding Streams [^zip-0207] and Lockbox Funding Streams [^zip-2001].

“ZEC” refers to the native currency of Zcash on Mainnet.


# Abstract

This proposal outlines a funding model that gives the community and coin holders distinct voices in determining what, if any, grants are provided to support Zcash’s development and community efforts.

In this model:

* 8% of the block rewards will be allocated to the ZCG for grants by and for the Zcash Community.
* 12% of the block rewards will accrue to a fund controlled by decisions of coin holders.
* Once a technical mechanism for doing so is defined, coin holders would also control the distribution for ecosystem funding of funds from the Deferred Dev Fund Lockbox.

The coin-holder-controlled funds may be used to distribute larger grants to ecosystem participants, or left at rest.

This model would be activated for 4 years, allowing enough time to determine whether it should be changed or codified for longer.


# Motivation

If no action is taken, in November 2025 funds from block subsidies will stop being directed to Zcash Community Grants [^zip-1015-zcg] and to the Deferred Dev Fund Lockbox established by ZIP 2001 [^zip-2001]. If the block subsidies stop, it will risk a gap in funding of Zcash development organisations, either via ZCG grants or via potential future disbursements from the Deferred Dev Fund Lockbox.

This proposal aims to:
* decentralize decision-making,
* hold stakeholders accountable for outcomes,
* be dynamic enough to allow for change, and
* provide clarity on decision-making.

It would immediately increase coin-holders’ voice, minimize governance confusion, and simplify decision-making.


# Requirements

* There is a well-defined, publically agreed, process for evaluation and community feedback on grant proposals.
* Funds are held in a multisig resistant to compromise of some of the parties' keys, up to a given threshold.
* No single party's non-cooperation or loss of keys is able to cause any Protocol-defined Ecosystem Funding to be locked up unrecoverably.
* The only additional mechanism required to start disbursing grants according to this proposal, beyond what is already implemented in consensus nodes, is a method of performing coin-holder voting (to be specified separately).
* During the period of this proposal, the block rewards must be distributed as described in the [Abstract] above.
* The funds from the 8% and 12% funding streams will be usable immediately.
* The funds in the Deferred Dev Fund Lockbox will be usable once a mechanism is available for disbursing them.
* Any use of Deferred Dev Fund Lockbox funds is consistent with the purpose specified in [^zip-1015-lockbox] of "funding grants to ecosystem participants".


# Non-requirements

Any changes to the ZCG or its governance, such as its expansion to include more members, may be desired but are specifically outside this proposal’s scope.

The full implementation of this proposal would require the design and implementation of a lockbox distribution mechanism, likely using multisig. This mechanism would be similar to that needed for an alternative proposal, zBloc [^draft-ecc-zbloc]. However, this proposal does not require that a lockbox distribution mechanism be implemented at the same time as a change to the funding stream.

# Specification

This proposal empowers both the community (through ZCG) and coin holders to independently determine what, if anything, should be funded through development fund grants.

The funding streams described below will be defined in a new revision of ZIP 214 [^zip-0214].

## Zcash Community Grants

A funding stream will be established for Zcash Community Grants, consisting of 8% of the block subsidy, and subject to all of the same rules currently specified in ZIP 1015 [^zip-1015-zcg].

This funding stream will start immediately on activation of this ZIP, which is assumed to be after the expiry of the existing ``FS_FPF_ZCG`` funding stream [^zip-1015-funding-streams], and last for 1,680,000 blocks (approximately 4 years).

## Coin-holder-controlled Fund

An additional funding stream will be established for the same period, consisting of 12% of the block subsidy paid to a 2-of-3 P2SH multisig with keys held by the Financial Privacy Foundation, the Zcash Foundation and the Electric Coin Company ("Key-holder Organizations").

This funding stream will start immediately on activation of this ZIP and last for 1,680,000 blocks (approximately 4 years).

The community SHOULD prioritize the development of a mechanism for disbursement of funds from the Deferred Dev Fund Lockbox. It is assumed here that lockbox funds would be controlled via a similar multisig with keys held by the same Key-holder Organizations.

From activation of this ZIP, the Coin-holder-controlled Fund is considered to include funds both from this 12% funding stream and from the Deferred Dev Fund Lockbox, which will become available for use on the same basis. That is, disbursement transactions MAY, at the discretion of the Key-holder Organizations, come either from the 12% funding stream, or from the Deferred Dev Fund Lockbox via a mechanism to be defined.

The Key-Holder Organizations would be bound by a legal agreement to only use funds held in the Coin-holder-controlled Fund according to the specifications in this ZIP, expressed in suitable legal language.

The Financial Privacy Foundation (FPF) would administer the Coin-holder-controlled Fund based on decisions taken by coin-holder voting, following a model decided by the community and specified in another ZIP [TBD].

### Disbursement process

1. Anyone can submit a grant application via a process agreed between the FPF, the Zcash Foundation, and the Electric Coin Company.
2. Grant applications with total below USD 500,000 (or equivalent in another currency) would be directed to ZCG.
3. For grant applications above this threshold, a 30-day community review and feedback period would start.
4. If the grant applications should proceed to a coin-holder vote according to the agreed process, then coin-holders would be asked to vote on it.
5. If the vote passes, then as payments are scheduled for the grant, then the FPF, the Zcash Foundation, and the Electric Coin Company SHOULD sign the corresponding transactions for disbursement from the Coin-holder-controlled Fund.

For coin holder votes, a minimum of 420,000 ZEC (2% of the total eventual supply) MUST be voted, with a simple majority cast in favor, for a grant proposal to be approved. Upon approval, the grants would be paid to the recipient per the terms of the grant proposal.

Coin holders would not be obligated to fund grants and MAY leave the funds at rest.

No organizations or individuals would be restricted from voting their coins.

## Administrative obligations and constraints

All provisions of ZIP 1015 imposing obligations and constraints on Bootstrap Project, Electric Coin Company, Zcash Foundation, Financial Privacy Foundation, the ZCG Committee, and grant recipients relating to the previous ``FS_FPF_ZCG`` funding stream, SHALL continue in effect for *both* Zcash Community Grants and the Coin-holder-controlled Fund. In particular, the provisions after the first paragraph of the section "Zcash Community Grants (ZCG)" also apply to FPF's administration of the Coin-holder-controlled Fund, with coin-holder voting replacing the role of the ZCG Committee.

For the avoidance of doubt, this includes the following:

* Decisions on use of the Coin-holder-controlled Fund taken by coin-holder vote require no approval from the FPF Board, but are subject to veto if FPF judges them to violate Cayman law or the FPF's reporting requirements and other (current or future) obligations under the Cayman Islands' Companies Act (2023 Revision) and Foundation Companies Law, 2017.
* FPF SHALL be contractually required to recognize the Coin-holder-controlled Fund as a Restricted Fund donation under the above constraints, and keep separate accounting of its balance and usage under its Transparency and Accountability obligations defined in ZIP 1015 [^zip-1015-transparency-and-accountability].

Coin-holders SHOULD take account of the same factors considered by the ZCG Committee (described in points 2, 3, and 4 of [^zip-1015-zcg]) in deciding whether to fund a grant. If any contentious issue arises in connection with a grant (such as milestones not being met), or periodically for grants of indefinite duration, FPF SHOULD hold additional coin-holder votes to determine whether funding should continue.

## Security precautions

The Key-holder Organizations and the ZCG Committee MUST take appropriate precautions to safeguard funds from theft or accidental loss. Any theft or loss of funds, or any loss or compromise of key material MUST be reported to the Zcash community as promptly as possible after applying necessary mitigations.

## Testnet-specific considerations

In order to allow the mechanism and process for coin-holder voting to be tested, this process SHOULD be rehearsed on Testnet. The threshold of 420,000 ZEC applied to Mainnet coin-holder votes does not apply to these rehearsals.

# Open questions

* Should there be another Key-holder Organisation, or are FPF, ZF, and ECC sufficient? Is a 2-of-3 threshold appropriate? Do we need to specify more about key rotation (beyond "take appropriate precautions")?
* Is 420,000 ZEC the right threshold for coin-holder votes?
* Is USD 500,000 the right threshold for grants to be controlled by coin-holder vote rather than ZCG?


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

[^zip-1015-transparency-and-accountability]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Transparency and Accountability](zip-1015#transparency-and-accountability)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](zip-2001.rst)

[^draft-ecc-zbloc]: [draft-ecc-zbloc: Zcash Governance Bloc](draft-ecc-zbloc.md)
