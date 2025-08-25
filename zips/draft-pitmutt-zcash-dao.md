    ZIP: XXX
    Title: Zcash DAO Mechanism
    Owners: Rene Vergara <pitmutt@vergara.tech>
    Status: Draft
    Credits:
    Category: Consensus / Process
    Created: 2025-03-31
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>

# Terminology

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this document are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as defined in the Zcash protocol specification [^protocol-networks].

# Abstract

This proposal specifies a mechanism to manage a Decentralized Autonomous Organization (DAO) using Zcash shielded addresses.

# Motivation

The Zcash community needs a mechanism to:

- Represent different groups of stakeholders
- Present proposals to these stakeholders
- Hold verifiable votes on the proposals

The need to address this problem is pressing, which means that handling this through a protocol change or a network upgrade could not be done in a timely manner.

This proposal specifies a Decentralized Autonomous Organization (DAO) with the aim of minimizing any additional development needed to meet the following objectives:

1. DAO information is decentralized:
1.1. Record membership of the DAO on-chain
1.2. Record proposals on-chain
1.3. Record votes on-chain
1. Use the existing Zcash protocol (does not require ZSAs, programmability or a different transaction format)
1. Remain flexible so it's applicable to different stakeholders and governance models
1. Existing wallets can interact with the DAO in their current state (Payment URI[^ZIP-321] support is highly recommended)

# Specification

## Member

A member of the DAO is identified by their Zcash unified address and a [minisign](https://jedisct1.github.io/minisign/) public key (UA/PK pair) that is used to validate their interactions with the DAO. This approach minimizes the amount of information that needs to be stored about each member while allowing the DAO to validate that proposals and votes were provided by the member. This approach also allows for recursive structures, where a UA/PK pair may be controlled by a sub-DAO that may define its own separate charter and still participate in the main DAO.

## DAO Creation

Founding members create 3 Zcash unified addresses with at least an Orchard receiver (optionally, using FROST threshold signatures):

- Membership address `MA`: used to record approved voting members of the DAO
- Proposals address `PA`: used to record proposals presented to the DAO for voting
- Votes address `VA`: used to record votes for proposals

Founders create the DAO Charter, a.k.a. "Proposal 0" where they determine:

- Any requirements for membership
- The `MA`, `PA` and `VA`
- A process to spend any funds accumulated in these DAO addresses
- Voting threshold for proposal approval
- Quorum threshold for valid votes
- Tie-breaking process
- A list of Zcash addresses, one per founding member of the DAO
- A minimum amount ZEC may be defined for submissions to `MA`, `PA` and `VA` as a spam-reducing measure
- Any other definitions, requirements or processes that the DAO will follow

Founders record the charter on the Zcash blockchain by sending a transaction to the `PA` with a memo as defined in **Proposals**.

Founders record their signing of the DAO Charter by creating their membership records in `MA` as defined in **Membership**.

The founders may now distribute Incoming Viewing Keys of the `MA`, `PA` and `VA` addresses as needed for proposal validation and voting verification.

## Membership

To request membership, a Zcasher would create a proposal providing their Zcash address, their minisign public key and meet any other requirements established by the DAO Charter. The prospective member would need to request an existing DAO member to submit the proposal to the DAO on their behalf and act as their sponsor. More than one sponsor may be required if Sybil-resistance is a concern.

Membership to the DAO is recorded by sending a transaction to `MA` with a memo that contains:

- A Zcash unified address
- The string `:`
- A minisign public key string
- The string `:prop:`
- The unique identifier of the proposal that established membership
- The string `:`
- A stable URL to the signature file produced by [minisign](https://jedisct1.github.io/minisign/) as defined in **Signatures** for the file containing the proposal that established membership. For founding members, this is the DAO Charter and each member submits their signature of the charter.

A membership record is valid when:
- The Zcash unified address matches the one listed in the referred proposal.
- The minisign public key string matches the one listed in the referred proposal.
- The referred proposal is approved per the charter.

## Proposals

A proposal is submitted to the DAO by sending a transaction to the `PA` with a memo that contains:

- The string `minisig:`
- A stable URL to the signature file produced by [minisign](https://jedisct1.github.io/minisign/) as defined in **Signatures** for the file containing the proposal
- The string `:`
- A stable URL to the contents of the file

The proposal file must include:
- a unique identifier
- a blockheight in the future specifying the deadline for voting
- an indexed list of options for voting, for example:

```
Options:
1. Yes
2. No
```

Or

```
Options:
1. Red
2. Green
3. Blue
```

## Voting
A vote is submitted to the DAO by sending a transaction to the `VA` with a memo that contains:

- The string `vote:`
- The integer representing the option defined in the proposal
- The string `:prop:`
- The unique identifier of the proposal being voted on
- The string `:minisig:`
- A stable URL to the signature file produced by `minisign` as defined in **Signatures** for the file containing the proposal corresponding to the identifier

Votes are valid when:
- The Zcash transaction containing the memo was mined on a block less than or equal to the deadline blockheight specified in the proposal
- The option included in the memo is one of the valid options specified in the proposal
- The submitted signature file can be validated by using the public key listed in `MA` for the DAO member.
- Any further requirements established in the DAO charter are met

If multiple valid votes are found on chain for the same member, the vote with the highest blockheight that is less than the deadline blockheight is considered the final vote and supersedes all previous votes.

## Signatures

Cryptographic signatures are used to ensure:
- Only proposals that are submitted by DAO members are considered valid, all other submissions to `PA` are ignored.
- Only votes that are submitted by DAO members are considered valid, all other submissions to `VA` are ignored.
- Only membership entries that are submitted by an authorized DAO member (per the Charter) are considered valid, all other submissions to `MA` are ignored.

We propose using the [minisign](https://jedisct1.github.io/minisign/) tool to create these signatures, as it uses modern cryptography, is readily available in multiple platforms, there are implementations in [multiple programming languages](https://wasmer.io/jedisct1/minisign) and it produces a small file that is easy to distribute.

For our proposed DAO mechanism, the `minisign` feature of "trusted comment" (a line of text that is cryptographically signed) must be used to include the Zcash address of the member originating the signature. If the trusted comment in the signature file does not include a Zcash address or if the Zcash address is not registered in `MA`, the signature is not valid.

# Acknowledgements

This proposed DAO mechanism was inspired by the proposed ECC on-chain accountable voting[^draft-ecc-accountable-voting].

# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2024.5.1 or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2024.5.1. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^ZIP-321]: [ZIP-321: Payment Request URIs](zip-0321.rst)

[^draft-ecc-accountable-voting]: [On-chain Accountable Voting](draft-ecc-onchain-accountable-voting.md)
