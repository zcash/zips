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

The key words "MUST", "MUST NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in § 3.12 ‘Mainnet and Testnet’. [^protocol-networks]

The term "full validator" in this document is to be interpreted as defined in § 3.3 ‘The Block Chain’. [^protocol-blockchain].

The terms below are to be interpreted as follows:

output

: A sink of funds within the transaction that is controlled by a payment address. This excludes e.g. miner fees, or the ZIP 233 field.


# Abstract

This ZIP introduces a system of transparent consensus accounts for receiving newly-issued ZEC, with spending from each account being controlled by a ZIP 270 [^zip-0270] signing key. Consensus accounts supplement (but do not replace) shielded coinbase outputs. These accounts can be funded either by new ZEC issuance, or (in the future) by ZSA issuance transactions for other assets. This ZIP eliminates the coinbase maturity rule while retaining the property that all ZEC and ZSA value must enter the shielded pool(s) before it can be otherwise transferred (or, in the case of ZEC, deshielded.)


# Motivation

The Zcash development fund lockbox currently has the characteristics of a transparent, account-based system. Spending from the lockbox requires the introduction of a new transaction bundle that treats the lockbox as a source of transaction inputs, controlled by a key that may be rotated using the mechanism specified in ZIP 270 [^zip-0270]. Instead of creating a mechanism that is specific to the development fund lockbox, creating a general mechanism provides several benefits to consistency and usability.

Part of the rationale for the creation of the dev fund lockbox was that the process of shielding tens of thousands of development fund outputs (over a thousand outputs per day) has created excessive operational friction for key-holder entities; in addition, transactions that spend these outputs have significant fee costs under ZIP 317 [^zip-0317]. These disadvantages do not uniquely effect the key holders of the development fund, however; they are felt just as acutely by miners and Zcash Community Grants. By introducing an account-based system, all recipients of new issuance can gain the same benefits that are available to the keyholders of the coinholder-controlled fund introduced in ZIP 1016 [^zip-1016].

In addition to eliminating hassles related to UTXO management, introducing a transparent account mechanism makes it possible for individuals to make direct donations to the development fund lockbox.

While this ZIP focuses on ZEC issuance, the transaction format reserves space for asset identifiers to allow future network upgrades to extend consensus accounts to hold Zcash Shielded Assets (ZSAs) [^zip-0227]. Such an extension could allow a ZSA issuer to finalize ZSA issuance into a consensus account without immediately sending the entirety of the issuance to shielded recipients; this would enable the creation of fixed-supply ZSA assets with publicly-visible undistributed balance, without requiring the issuer to expose their full viewing key that would reveal the recipients of subsequent transfers from that finalized issuance pool.


# Privacy Implications

At present, all ZEC issuance is transparent, in that mining outputs are either sent to the lockbox, sent to a transparent address, or sent to a shielded address but with the output verified to be decryptable with the all-zeroes OVK, to ensure that the value of each issuance output can be verified. This ZIP preserves this transparency: consensus account balances are publicly visible, and shielded coinbase outputs remain subject to the all-zeroes OVK requirement.

All spends from a consensus account are required to be shielding transactions, preserving the existing property that all issued funds are initially shielded.


# Requirements

- All new ZEC issuance is credited to a transparent consensus account.
- Newly-issued ZEC is credited either to a hardcoded funding stream key (until block height 4476000 as specified in [^zip-0214], this will be either the coinholder-controlled-fund key or a to-be-defined Zcash Community Grants fund key) or to a miner-controlled key.
- When a miner produces a coinbase transaction, they MAY include an account registration bundle and consensus account output bundle to credit their rewards to a consensus account. Alternatively, they MAY continue to use shielded coinbase outputs.
- Preserve the existing requirement that newly-issued ZEC is always shielded at least once.
- All funding streams defined after the activation of this ZIP must use consensus accounts as recipients.


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

Shielded coinbase outputs remain supported, as shown in the "Explicit UTXO" column above. While the address receiving a shielded coinbase output is publicly visible, the subsequent spend of that output is not distinguishable from other shielded spends on-chain. This provides better privacy properties than the transparent account model, and avoids requiring privacy-conscious miners to create a new account key for each block they mine (which would rapidly bloat the consensus account set).


# Specification

## Consensus accounts

A consensus account is uniquely identified by a `consensus_account_id`, which is a 32-byte value derived from the account's initial public key:

```
consensus_account_id = BLAKE2b-256("Zcash_ConAcctId_", protocol_type || initial_public_key)
```

where:
- `protocol_type` is the single-byte protocol type identifier as defined in ZIP 270 [^zip-0270] (0 for RedPallas, 1 for BIP340, etc.)
- `initial_public_key` is the public key provided when the account was first registered

The `consensus_account_id` remains stable across key rotations performed via ZIP 270.

Each consensus account has a ZIP 270 tracked signing key associated with it, that authorizes the spending of funds from the account. The tracked signing key MAY be any protocol type supported by ZIP 270.

## Global account state

Consensus accounts require the following additions to the global state:

- A map, `consensus_accounts`, from `consensus_account_id` to a tuple of:
    - `balance`: the current ZEC balance
    - `current_key`: the current signing key (protocol_type, public_key)
    - `rotation_key`: the current rotation key (protocol_type, public_key)

For newly registered accounts, `current_key` and `rotation_key` are both set to the initial key provided at registration.

As of the activation of this ZIP, consensus accounts hold only ZEC. The transaction format reserves space for asset identifiers to allow future network upgrades to extend consensus accounts to hold other assets.

## Initializing an account

There are two ways to initialize a consensus account:

- Define it in the consensus rules.
    - The `consensus_account_id`s of these accounts are "visible" to the consensus rules, and can be used in implicit rules.
- Create a miner account by mining a block that includes an account registration bundle with a previously-unknown key.
    - The `consensus_account_id`s of these accounts are "opaque" to the consensus rules, and their balance can only be modified by being explicitly referenced in a transaction.

## Account registration bundle

This ZIP defines a new bundle type for the extensible transaction format specified in ZIP NNN [^zip-extfmt]. The account registration bundle registers new consensus accounts.

### Account Registration Effecting Data

| Bytes   | Name              | Data Type                              | Description |
|---------|-------------------|----------------------------------------|-------------|
| varies  | `nRegistrations`  | `compactSize`                          | The number of account registrations. |
| varies  | `vRegistrations`  | `AccountRegistration[nRegistrations]`  | New account registrations. |

### AccountRegistration

| Bytes   | Name           | Data Type       | Description |
|---------|----------------|-----------------|-------------|
| 1       | `protocolType` | `uint8`         | Signing protocol type as defined in ZIP 270 (0=RedPallas, 1=BIP340, etc.). |
| varies  | `publicKey`    | `byte[keylen]`  | Public key. Length is determined by `protocolType`. |

Upon processing an `AccountRegistration`, full validators:
1. Compute the `consensus_account_id` from `protocolType` and `publicKey` as specified above.
2. MUST reject the transaction if an account with that `consensus_account_id` already exists.
3. Create a new account entry in `consensus_accounts` with the computed ID, the provided key as both `current_key` and `rotation_key`, and `balance` set to zero.

### Account Registration Authorizing Data

| Bytes   | Name                  | Data Type                            | Description |
|---------|-----------------------|--------------------------------------|-------------|
| varies  | `vRegistrationAuths`  | `RegistrationAuth[nRegistrations]`   | Authorization signatures for account registrations. |

### RegistrationAuth

| Bytes   | Name        | Data Type      | Description |
|---------|-------------|----------------|-------------|
| varies  | `signature` | `byte[siglen]` | Signature over the transaction id, proving control of the corresponding private key. Length is determined by the `protocolType` of the corresponding `AccountRegistration`. |

The `vRegistrationAuths` entries correspond positionally to `vRegistrations` entries. Each signature MUST verify against the `publicKey` in the corresponding `AccountRegistration`.

### Value Balance

The account registration bundle does not transfer value; it has no entry in the value balance map.

### Consensus Rules

In a coinbase transaction, if an account registration bundle is present, a consensus account output bundle MUST also be present, and for each registered account there MUST be at least one `AccountOutput` crediting value to that account's `consensus_account_id`.

## Consensus account output bundle

This ZIP defines a second bundle type for the extensible transaction format. The consensus account output bundle credits value to consensus accounts.

### Consensus Account Output Effecting Data

| Bytes   | Name        | Data Type                    | Description |
|---------|-------------|------------------------------|-------------|
| varies  | `nOutputs`  | `compactSize`                | The number of account outputs. |
| varies  | `vOutputs`  | `AccountOutput[nOutputs]`    | The account output records. |

### AccountOutput

| Bytes   | Name         | Data Type                | Description |
|---------|--------------|--------------------------|-------------|
| 32      | `accountId`  | `byte[32]`               | The `consensus_account_id` of the account to credit. |
| 1       | `assetClass` | `uint8`                  | Asset class identifier. 0x00 for ZEC, 0x01 for other assets. |
| 0 or 64 | `assetId`    | `byte[0]` or `byte[64]`  | If `assetClass == 0`, the zero-length byte array; otherwise a 64-byte asset identifier. |
| 8       | `value`      | `uint64`                 | The value to credit to the account. |

Upon processing an `AccountOutput`, full validators:
1. MUST reject the transaction if no account with the given `accountId` exists (note: registrations in the same transaction are processed first).
2. Add `value` to the account's `balance`.

### Consensus Account Output Authorizing Data

The consensus account output bundle has no authorizing data. Any party may credit value to an existing account (analogous to sending funds to an address).

### Value Balance

The value balance map entry for the consensus account output bundle equals the sum of all output values:

```
valueBalance = Σ(output.value for each output in vOutputs)
```

### Consensus Rules

As of the activation of this ZIP, full validators MUST reject transactions where any `AccountOutput` has `assetClass` other than 0x00. Support for crediting other assets to consensus accounts may be added in a future network upgrade.

## Consensus account spend bundle

This ZIP defines a third bundle type for the extensible transaction format: the consensus account spend bundle. This bundle allows spending value from consensus accounts into shielded pools.

### Consensus Account Spend Effecting Data

| Bytes   | Name           | Data Type                        | Description |
|---------|----------------|----------------------------------|-------------|
| varies  | `nSpends`      | `compactSize`                    | The number of account spends. |
| varies  | `vSpends`      | `AccountSpend[nSpends]`          | The account spend descriptions. |

### AccountSpend

| Bytes   | Name         | Data Type                | Description |
|---------|--------------|--------------------------|-------------|
| 32      | `accountId`  | `byte[32]`               | The `consensus_account_id` of the account to spend from. |
| 1       | `assetClass` | `uint8`                  | Asset class identifier. 0x00 for ZEC, 0x01 for other assets. |
| 0 or 64 | `assetId`    | `byte[0]` or `byte[64]`  | If `assetClass == 0`, the zero-length byte array; otherwise a 64-byte asset identifier. |
| 8       | `value`      | `uint64`                 | The value to spend from the account. |

### Consensus Account Spend Authorizing Data

| Bytes   | Name           | Data Type                    | Description |
|---------|----------------|------------------------------|-------------|
| varies  | `vSpendAuths`  | `SpendAuth[nSpends]`         | Authorization signatures for each spend. |

### SpendAuth

| Bytes   | Name        | Data Type      | Description |
|---------|-------------|----------------|-------------|
| varies  | `signature` | `byte[siglen]` | Signature over the transaction id authorizing the spend. Length is determined by the protocol type of the account's current signing key. |

The `vSpendAuths` entries correspond positionally to `vSpends` entries. Each signature MUST verify against the `current_key` of the account identified by the corresponding `accountId`.

### Value Balance

The value balance map entry for the consensus account spend bundle equals the negation of the sum of all spend values (since spends remove value from accounts and add it to the transparent transaction value pool):

```
valueBalance = -Σ(spend.value for each spend in vSpends)
```

### Consensus Rules

- Full validators MUST reject a transaction containing a consensus account spend bundle if any `AccountSpend` references an `accountId` that does not exist.
- Full validators MUST reject a transaction if the total value spent from any single account (summing all `AccountSpend` entries for that account) exceeds that account's current balance.
- Full validators MUST reject a transaction containing a consensus account spend bundle if any output within the transaction is not shielded. This preserves the requirement that all newly-issued ZEC must be shielded at least once before being transferred or deshielded.
- As of the activation of this ZIP, full validators MUST reject transactions where any `AccountSpend` has `assetClass` other than 0x00.

## Changes to ZIP 270

The following row is added to the table of key usages for tracked signing keys:

| Usage typecode | Description |
| -------------- | ----------- |
| 1              | ZIP NNN: Consensus account spending |

The `key_id` for this usage is the `consensus_account_id` as defined in this ZIP.

This usage typecode authorizes spending from consensus accounts. The tracked signing key associated with a consensus account may be rotated using the key rotation mechanism defined in ZIP 270. Upon rotation, the account's `current_key` is updated to the new key, while the `consensus_account_id` remains unchanged.

## Changes to ZIP 207

The following paragraphs are added to the section Funding Streams, after the definition of Revision 1 recipient identifiers:

> As of Revision 3, a recipient identifier MAY be a consensus account identifier as defined in ZIP NNN.
>
> Any funding stream defined after the activation of ZIP NNN MUST use a consensus account identifier as its recipient.

## Changes to ZIP 214

The following bullet point is added to the section Revisions:

> - Revision 3: The Zcash Community Grants funding stream is redirected to a consensus account at the activation height of this ZIP. The coinholder-controlled fund (dev fund lockbox) continues unchanged.

The Revision 2 ZCG funding stream (`FS_FPF_ZCG_H2`) ends at the activation height of this ZIP. A new Revision 3 ZCG funding stream begins at that height, directing outputs to a ZCG consensus account.

The following new sections are added:

> ## Mainnet Recipients for Revision 3
>
> ```
> FS_FPF_ZCG_H3 = TODO (consensus account identifier)
> ```
>
> ## Testnet Recipients for Revision 3
>
> ```
> FS_FPF_ZCG_H3 = TODO (consensus account identifier)
> ```

## Changes to the Zcash Protocol Specification

### Section 3.4 (Transactions and Treestates)

The global chain state is extended to include a map `consensus_accounts` from `consensus_account_id` to account state, as defined in this ZIP.

### Section 7.1.1 (Transaction Consensus Rules)

The following consensus rules are added:

**Account registration bundle:**
- A transaction MAY contain an account registration bundle.
- Each `AccountRegistration` MUST have a valid signature in the corresponding `RegistrationAuth` entry, verifiable against the provided `publicKey`.
- Each `AccountRegistration` MUST NOT reference a `consensus_account_id` that already exists.
- In a coinbase transaction, if an account registration bundle is present, a consensus account output bundle MUST also be present, and for each registered account there MUST be at least one `AccountOutput` crediting value to that account.

**Consensus account output bundle:**
- A transaction MAY contain a consensus account output bundle.
- Each `AccountOutput` MUST reference a `consensus_account_id` that exists (either pre-defined in consensus rules, or registered in an account registration bundle processed earlier in the same transaction, or previously registered).
- As of the activation of this ZIP, `assetClass` MUST be 0x00 for all `AccountOutput` entries.

**Consensus account spend bundle:**
- A non-coinbase transaction MAY contain a consensus account spend bundle.
- If a consensus account spend bundle is present, all outputs within the transaction MUST be shielded (Sapling or Orchard outputs only; no transparent outputs).
- Each `AccountSpend` MUST reference a `consensus_account_id` that exists.
- Each `AccountSpend` MUST have a valid signature in the corresponding `SpendAuth` entry, verifiable against the account's current signing key.
- The total value spent from any single account within a transaction MUST NOT exceed that account's balance.
- As of the activation of this ZIP, `assetClass` MUST be 0x00 for all `AccountSpend` entries.

### Section 7.8 (Block Subsidy and Founders' Reward)

Funding stream outputs to consensus accounts are credited via implicit additions to the `consensus_accounts` map, rather than via explicit transaction outputs. The value balance of a coinbase transaction is computed to include these implicit credits.


# Rationale

Implicit rules are kept in the post-rework to reduce churn for miners; they only need to know the fraction of block subsidy available for miner rewards, instead of needing to ensure they craft the correct outputs for the current consensus rules in their block templates.

Shielded coinbase outputs are retained alongside consensus accounts because they offer superior privacy properties for miners who desire them. Although the receiving address of a shielded coinbase output is publicly visible, its subsequent spend is indistinguishable from other shielded spends. In contrast, spending from a consensus account is always a publicly visible operation. Retaining shielded coinbase also avoids forcing privacy-conscious miners to generate a new consensus account key for each block, which would cause unbounded growth of the consensus account set.

Account registration and account outputs are specified as separate bundles because these operations have fundamentally different characteristics. Account registrations require a signature proving control of the registered public key; this prevents the creation of accounts with keys that no one controls, which would permanently burn any funds credited to them. Account outputs, in contrast, require no authorization—any party may credit value to an existing account, analogous to sending funds to a known address. Separating these into distinct bundles provides a cleaner abstraction: the registration bundle handles identity establishment (with authorization), while the output bundle handles value transfer (without authorization). The requirement that a coinbase transaction with registrations must include outputs to those accounts ensures that newly registered accounts receive their initial funding in a single atomic operation.


# Alternatives

An alternative design considered was a single combined bundle containing both registrations and credits, with registrations including a value field. This would result in a single entry in the value balance map. However, this approach conflates two distinct operations (identity establishment and value transfer) and requires either including asset class fields in registrations (adding complexity) or limiting registrations to ZEC only (reducing future flexibility). The two-bundle design provides cleaner separation of concerns and allows the registration bundle to remain simple and focused on key management.


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

[^protocol-networks]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-extfmt]: [ZIP NNN: Extensible Transaction Format](https://github.com/zcash/zips/pull/1156)

[^zip-0270]: [ZIP 270: Key Rotation for Tracked Signing Keys](https://github.com/zcash/zips/pull/1117)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-0227]: [ZIP 227: Zcash Shielded Assets (ZSA)](zip-0227.md)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317.md)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)
