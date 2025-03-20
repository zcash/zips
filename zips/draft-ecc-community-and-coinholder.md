    ZIP: XXX
    Title: Community and Coinholder Funding Model
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

### One-time lockbox disbursement

The coinbase transaction of the activation block of this ZIP MUST include an additional output to a 3-of-5 P2SH multisig with keys held by the following "Key-Holder Organizations": Zcash Foundation, the Electric Coin Company, Shielded Labs, and two other organizations yet to be decided.

Let $v$ be the zatoshi amount in the Deferred Dev Fund Lockbox at the activation height. ($v$ can be predicted in advance given that height.)

The additional coinbase output MUST follow the same consensus rules as apply to funding stream outputs [^zip-0207-consensus-rules]. That is, the coinbase transaction MUST contain at least one output that pays $v$ zatoshi, in the prescribed way defined in ZIP 207, to the above P2SH multisig address. $v$ zatoshi are added to the transparent transaction value pool to fund this output, and subtracted from the balance of the Deferred Dev Fund Lockbox (i.e. the latter balance is reset to zero).

Exactly one of the following options will also be taken.

### Option 1: Extend the lockbox funding stream

The ``FS_DEFERRED`` lockbox funding stream is extended by a further 1,260,000 blocks (approximately 3 years), ending at the 3rd halving.

#### Rationale for Option 1

Performing a one-time disbursement to a P2SH multisig address will provide a source of grant funding for a limited period, allowing time for a lockbox disbursement mechanism to be specified and deployed.

In particular, this provides an opportunity for transaction format changes that may be required for such a mechanism to be included in the v6 transaction format [^zip-0230]. It is desirable to limit the frequency of transaction format changes because such changes are disruptive to the ecosystem. It is not necessary that protocol rules for disbursement actually be implemented until after the transaction format changes are live on the network.

By implementing a one-time disbursement along with a continuation of the ``FS_DEFERRED`` stream, we prioritize both the availability of grant funding and the implementation of a more flexible and secure mechanism for disbursement from the lockbox — making it possible to address the need to rotate keys and/or alter the set of key holders in a way that reverting to hard-coded output addresses for repeated disbursements would not.

### Option 2: Revert to hard-coded output address

The 12% of the block subsidy that currently is distributed to the lockbox via the existing ``FS_DEFERRED`` funding stream, is instead regularly distributed to a 3-of-5 P2SH multisig with keys held by the same Key-Holder Organizations as above. The Coinholder-Controlled Fund is considered to include both this stream of funds, and funds from the one-time lockbox disbursement described above.

Option 2 can be realized by either of the following mechanisms:

#### Mechanism 2a: Classic funding stream

A new funding stream is defined that replaces the existing ``FS_DEFERRED`` lockbox funding stream [^zip-1015-funding-streams]. That is, the end height of ``FS_DEFERRED`` will be changed to the activation height of this ZIP. The new ``FS_COINHOLDER`` stream will start at the same height and last until the 3rd halving.

#### Mechanism 2b: Periodic lockbox disbursement

Constant parameter $N = 35000$ blocks $= \mathsf{PostBlossomHalvingInterval}/48$ (i.e. approximately one month of blocks).

The ``FS_DEFERRED`` lockbox funding stream is extended by a further 1,260,000 blocks (approximately 3 years), ending at the 3rd halving. A consensus rule is added to disburse from the Deferred Dev Fund Lockbox to a 3-of-5 P2SH multisig with keys held by the same Key-Holder Organizations as above, starting at block height $\mathsf{activation\_height} + N$ and continuing at periodic intervals of $N$ blocks ending with the 3rd halving height. Each disbursement empties the lockbox. This is equivalent to specifying $\frac{\mathstrut\mathsf{third\_halving\_height} \,-\, \mathsf{activation\_height}}{N}$ [One-time lockbox disbursement]s, that all output to the same address.

#### Rationale for periodic disbursement

Classic funding streams [^zip-0207] produce many small output values, due to only being able to direct funds from a single block's subsidy at a time. This creates operational burdens to utilizing the funds — in particular due to block and transaction sizes limiting how many outputs can be combined at once, which increases the number of required transactions and correspondingly the overall fee.

The periodic lockbox disbursement mechanism can produce the same effective funding stream, but with aggregation performed for free: the output to the funding stream recipient is aggregated into larger outputs every $N$ blocks. In the specific case of Mechanism 2b, the recipient multisig address would receive around 40 outputs, instead of around 1,300,000.

### Requirements on use of the Coinholder-Controlled Fund

The Key-Holder Organizations SHALL be bound by a legal agreement to only use funds held in the Coinholder-Controlled Fund according to the specifications in this ZIP, expressed in suitable legal language. In particular, all requirements on the use of Deferred Dev Fund Lockbox funds in ZIP 1015 [^zip-1015-lockbox] MUST be followed for the funds obtained from the [One-time lockbox disbursement].

The Key-Holder Organizations collectively administer the Coinholder-Controlled Fund based on decisions taken by coinholder voting, following a model decided by the community and specified in another ZIP [TBD].

### Disbursement process

1. Anyone can submit a grant application via a process agreed upon by the Key-Holder Organizations.
2. Grant applications with total below USD 500,000 (or equivalent in another currency) are directed to ZCG.
3. For grant applications above this threshold, a 30-day community review and feedback period will start.
4. If a grant application is not [vetoed](#veto-process) and proceeds to a coinholder vote according to the agreed process, then coinholders will be asked to vote on it.
5. If the vote passes, then as payments are scheduled for the grant, then (subject to the [Veto process]) the Key-Holder Organizations SHOULD sign the corresponding transactions for disbursement from the Coinholder-Controlled Fund.

For coinholder votes, a minimum of 420,000 ZEC (2% of the total eventual supply) MUST be voted, with a simple majority cast in favor, for a grant proposal to be approved. Upon approval, the grants are paid to the recipient per the terms of the grant proposal.

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

## Security precautions

The Key-Holder Organizations and the ZCG Committee MUST take appropriate precautions to safeguard funds from theft or accidental loss. Any theft or loss of funds, or any loss or compromise of key material MUST be reported to the Zcash community as promptly as possible after applying necessary mitigations.

## Testnet-specific considerations

In order to allow the mechanism and process for coinholder voting to be tested, this process SHOULD be rehearsed on Testnet. The threshold of 420,000 ZEC applied to Mainnet coinholder votes does not apply to these rehearsals.


# Rationale

TODO: Write a rationale for not having manually authorized disbursements (they require a transaction format change, to add a section similar to the ZSA issuance bundle).


# Open questions

* Is a 3-of-5 threshold appropriate? What should the other two Key-Holder Organizations be?
* Do we need to specify more about key rotation (beyond "take appropriate precautions")?
* Is 420,000 ZEC the right threshold for coinholder votes?
* Is USD 500,000 the right threshold for grants to be controlled by coinholder vote rather than ZCG?
* Should Option 1 or Option 2 be taken?


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2024.5.1 or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2024.5.1. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0207-consensus-rules]: [ZIP 207: Funding Streams — Consensus Rules](zip-0207#consensus-rules)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-0230]: [ZIP 230: Version 6 Transaction Format](zip-0230.rst)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-lockbox]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Lockbox](zip-1015#lockbox)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Zcash Community Grants](zip-1015#zcash-community-grants-zcg)

[^zip-1015-funding-streams]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Funding Streams](zip-1015#funding-streams)

[^zip-1015-transparency-and-accountability]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Transparency and Accountability](zip-1015#transparency-and-accountability)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](zip-2001.rst)

[^draft-ecc-zbloc]: [draft-ecc-zbloc: Zcash Governance Bloc](draft-ecc-zbloc.md)
