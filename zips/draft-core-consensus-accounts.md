    ZIP: TBD
    Title: Zcash Consensus Accounts
    Owners: Kris Nuttycombe <kris@nutty.land>
            Jack Grigg <thestr4d@gmail.com>
            Daira-Emma Hopwood <daira@jacaranda.org>
    Status: Draft
    Category: Consensus
    Created: 2026-01-11
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in § 3.12 ‘Mainnet and Testnet’. [^protocol-networks]

The term "full validator" in this document is to be interpreted as defined in § 3.3 ‘The Block Chain’. [^protocol-blockchain].

The terms below are to be interpreted as follows:

output

: A sink of funds within the transaction that is controlled by a payment address. This excludes e.g. miner fees, or the ZIP 233 field.


# Abstract

This ZIP replaces both transparent and shielded coinbase outputs with a system of transparent accounts, with spending from each account being controlled by a ZIP 270 [^zip-0270] signing key. These accounts can be funded either by new ZEC issuance, or (in the future) by ZSA issuance transactions for other assets. In the process, it eliminates the coinbase maturity rule while retaining the property that all ZEC and ZSA value must enter the shielded pool(s) before it can be otherwise transferred (or, in the case of ZEC, deshielded.)


# Motivation

The Zcash development fund lockbox currently has the characteristics of a transparent, account-based system. Spending from the lockbox requires the introduction of a new transaction bundle that treats the lockbox as a source of transaction inputs, controlled by a key that may be rotated using the mechanism specified in ZIP 270 [^zip-0270]. Instead of creating a mechanism that is specific to the development fund lockbox, creating a general mechanism provides several benefits to consistency and usability.

Part of the rationale for the creation of the dev fund lockbox was that the process of shielding tens of thousands of development fund outputs (over a thousand outputs per day) has created excessive operational friction for key-holder entities; in addition, transactions that spend these outputs have significant fee costs under ZIP 317 [^zip-0317]. These disadvantages do not uniquely effect the key holders of the development fund, however; they are felt just as acutely by miners and Zcash Community Grants. By introducing an account-based system, all recipients of new issuance can gain the same benefits that are available to the keyholders of the coinholder-controlled fund introduced in ZIP 1016 [^zip-1016].

In addition to eliminating hassles related to UTXO management, introducing a transparent account mechanism makes it possible for individuals to make direct donations to the development fund lockbox.

In addition to the benefits to recipients of new ZEC issuance, we can generalize the mechanism to serve the issuers of Zcash Shielded Assets (ZSAs) [^zip-0227]. In this case, it becomes possible for a ZSA issuer to finalize ZSA issuance into a consensus account without immediately sending the entirety of the issuance to shielded recipients; this allows the creation of fixed-supply ZSA assets with publicly-visible undistributed balance, without requiring the issuer to expose their full viewing key that would reveal the recipients of subsequent transfers from that finalized issuance pool.


# Privacy Implications

At present, all ZEC issuance is transparent, in that mining outputs are either sent to the lockbox, sent to a transparent address, or sent to a shielded address but with the output verified to be decryptable with the all-zeroes OVK, to ensure that the value of each issuance output can be verified. The suggested change preserves this transparency by specifying that all issuance outputs be sent to a transparent account.

All spends from a consensus account are required to be shielding transactions, preserving the existing property that all issued funds are initially shielded.


# Requirements

- All new ZEC (and in the future, ZSA) issuance is credited to a transparent account.
    - TODO: Should this be a requirement for ZSAs? str4d thinks no.
- Newly-issued ZEC is credited either to a hardcoded funding stream key (until block height 4476000 as specified in [^zip-0214], this will be either the coinholder-controlled-fund key or a to-be-defined Zcash Community Grants fund key) or to a miner-controlled key.
- When a miner produces a coinbase transaction, they will include a coinbase outputs bundle in the coinbase transaction instead of transparent, Sapling, or Orchard bundles.
- Preserve the existing requirement that newly-issued ZEC is always shielded at least once.


# Non-requirements

- This does not need to define a general-purpose transparent accounts mechanism.


# High-level summary

This section and the tables below are non-normative.

Prior to this ZIP, coinbase and non-coinbase transactions supported several different kinds of inputs and outputs. Some of these were explicitly encoded in the transaction (namely, spending or receiving UTXOs), while some were implicitly defined by the consensus rules (e.g. fees). The full set of possible actions were as follows:

<table>
    <tr>
        <th>Transaction type</th>
        <td colspan=2>Coinbase</td>
        <td colspan=2>Non-coinbase</td>
    </tr>
    <tr>
        <th>Encoding</th>
        <td>Implicit rule</td>
        <td>Explicit UTXO</td>
        <td>Explicit rule</td>
        <td>Explicit UTXO</td>
    </tr>
    <tr>
        <th>Direction: Input</th>
        <td>
            <ul>
                <li>Block subsidy</li>
                <li>Fees</li>
                <li>CCF disbursement</li>
            </ul>
        </td>
        <td>N/A</td>
        <td>N/A</td>
        <td>
            <ul>
                <li>Spending funds</li>
                <li>Miner shielding</li>
            </ul>
        </td>
    </tr>
    <tr>
        <th>Direction: Output</th>
        <td>
            <ul>
                <li>CCF funding</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>Transparent coinbase</li>
                <li>Shielded coinbase</li>
                <li>Funding streams</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>NSM (ZIP 233)</li>
                <li>Fees (ZIP 2002)</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>Receiving funds</li>
            </ul>
        </td>
    </tr>
</table>

After the reworking of transactions in this ZIP, the following actions are supported:

<table>
    <tr>
        <th>Transaction type</th>
        <td colspan=4>Coinbase</td>
        <td colspan=3>Non-coinbase</td>
    </tr>
    <tr>
        <th>Encoding</th>
        <td>Implicit rule</td>
        <td>Explicit rule</td>
        <td>Explicit account</td>
        <td>Explicit UTXO</td>
        <td>Explicit rule</td>
        <td>Explicit account</td>
        <td>Explicit UTXO</td>
    </tr>
    <tr>
        <th>Direction: Input</th>
        <td>
            <ul>
                <li>Block subsidy</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>Fees (ZIP NNN)</li>
            </ul>
        </td>
        <td>N/A</td>
        <td>N/A</td>
        <td>N/A</td>
        <td>
            <ul>
                <li>CCF or ZCG disbursement</li>
                <li>Miner shielding</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>Spending funds</li>
            </ul>
        </td>
    </tr>
    <tr>
        <th>Direction: Output</th>
        <td>
            <ul>
                <li>CCF funding (account increment)</li>
                <li>Funding streams (account increment)</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>NSM (ZIP 235)</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>Transparent coinbase</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>Shielded coinbase</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>NSM (ZIP 233)</li>
                <li>Fees (ZIP 2002)</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>CCF or ZCG donations</li>
            </ul>
        </td>
        <td>
            <ul>
                <li>Receiving funds</li>
            </ul>
        </td>
    </tr>
</table>

TODO: Decide whether to still allow shielded coinbase (i.e. whether to allow any explicit UTXOs in coinbase transactions).


# Specification

## Consensus accounts

A consensus account is uniquely identified by a `consensus_account_id`.

TODO: decide on and specify format of `consensus_account_id`.

Each consensus account has a ZIP 270 tracked signing key associated with it, that authorizes the spending of funds from the account. As of the current revision of this ZIP, the tracked signing key MUST be a RedPallas key.

## Global account state

Consensus accounts require the following additions to the global state:

- A map, `consensus_accounts`, from `consensus_account_id` to a current balance.
    - TODO: Each consensus account has a single denomination? Or allow the complexity of multi-asset accounts?

## Initializing an account

There are two ways to initialize a consensus account:

- Define it in the consensus rules.
    - The `consensus_account_id`s of these accounts are "visible" to the consensus rules, and can be used in implicit rules.
- Create a miner account by mining a block with coinbase outputs to a previously-unknown key.
    - The `consensus_account_id`s of these accounts are "opaque" to the consensus rules, and their balance can only be modified by being explicitly referenced in a transaction.

## Coinbase outputs bundle

The coinbase outputs bundle consists of a set of (public_key, value) tuples where the public key corresponds to a tracked signing key.

A `consensus_account_id` is created on first appearance of a `public_key`, initialized as ... (TODO).

TODO: Maybe include `asset_uuid` if this bundle is reused for storing issued ZSAs.

## Consensus account spend bundle

This consists of a `consensus_account_id`, an amount being spent from the account, and an authorizing signature.

### Consensus rules

- When spending from a transparent account, all outputs MUST be shielded.

## Changes to ZIP 270

TODO describe key usage typecode 1, which this ZIP is "adding" despite being written at the same time.

## Changes to ZIP 207

The following paragraph is added to the section Funding Streams, after the definition of Revision 1 recipient identifers:

> As of Revision 2, each recipient identifier MUST be a ZIP NNN consensus account identifier.

## Changes to ZIP 214

The following bullet point is added to the section Revisions:

> - Revision 3: Modifications to the Revision 2 funding streams to direct their outputs to ZIP NNN consensus accounts.

TODO: Decide whether to split the Revision 2 funding streams into "region using addresses" and "region using consensus accounts", in the same way we chose to not merge Revision 1 and Revision 2 streams on mainnet (because we couldn't on testnet).

The following new sections are added:

> ## Mainnet Recipients for Revision 3
>
> ```
> FS_FPF_ZCG_H3 = TODO
> FS_CCF_H3 = TODO
> ```
>
> ## Testnet Recipients for Revision 3
>
> ```
> FS_FPF_ZCG_H3 = TODO
> FS_CCF_H3 = TODO
> ```

## Changes to the Zcash Protocol Specification

The following changes are made to section 7.1.1 Transaction Consensus Rules:

- If a consensus account spend bundle is present in a transaction, all outputs within the transaction must be shielded.


# Rationale

Implicit rules are kept in the post-rework to reduce churn for miners; they only need to know the fraction of block subsidy available for miner rewards, instead of needing to ensure they craft the correct outputs for the current consensus rules in their block templates.


# Deployment

TBD


# Reference implementation

TBD


# Open issues

TBD


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0270]: [ZIP 270: Key Rotation for Tracked Signing Keys](https://github.com/zcash/zips/pull/1117)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317.md)
