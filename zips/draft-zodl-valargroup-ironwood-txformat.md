    ZIP: XXX
    Title: Version 6 Transaction Format
    Owners: Daira-Emma Hopwood <daira@jacaranda.org>
            ‹other ZODL / Valar Group authors›
    Status: Draft
    Category: Consensus
    Created: 2026-06-13
    License: MIT
    Discussions-To: ‹https://github.com/zcash/zips/issues/XXXX›


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be
interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in all
capitals.

The term "network upgrade" in this document is to be interpreted as described in
ZIP 200. [^zip-0200]

The terms "Mainnet" and "Testnet" are to be interpreted as described in § 3.12
‘Mainnet and Testnet’. [^protocol-networks]

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms below are to be interpreted as follows:

Orchard protocol
:   The shared cryptographic design used by both the Orchard pool and the Ironwood
    pool: the Pallas/Vesta curves, the Sinsemilla hash, the Action circuit and its
    verifying key, and the note, commitment, nullifier, and key constructions and note
    encryption defined for Orchard. There is a single Orchard protocol.

Orchard pool
:   The value pool, with its own note commitment tree, anchor, and chain value pool
    balance, that was introduced by ZIP 224 [^zip-0224]. Also called the *legacy* or
    *original* Orchard pool where disambiguation is needed.

Ironwood pool
:   A new value pool of the Orchard protocol, introduced by this ZIP, with its own note
    commitment tree, anchor, and chain value pool balance, distinct from the Orchard
    pool.


# Abstract

This ZIP defines version 6 of the Zcash transaction format, activated at NU6.3. A
version 6 transaction is a version 5 transaction extended with an **Ironwood bundle**:
a second Orchard-protocol shielded bundle that commits to, and spends from, the
Ironwood pool rather than the Orchard pool.

The Ironwood bundle reuses the Orchard Action encoding, authorization structure, and
proof system unchanged; it differs from the Orchard bundle only in that its actions are
committed to the Ironwood note commitment tree and spent against the Ironwood nullifier
set, and in the transaction-hashing personalizations used for it.


# Motivation

NU6.3 introduces the Ironwood pool as an Orchard-protocol successor to the legacy
Orchard pool, in order to bound the circulating supply of ZEC transacting through the
shielded protocol while allowing existing Orchard funds to be migrated across the
turnstile. Carrying the Ironwood pool requires a new transaction version that can hold
an Ironwood bundle alongside the existing transparent, Sapling, and Orchard components,
together with the corresponding transaction-identifier, signature-hash, and block-commitment
changes.

This ZIP specifies only the transaction format and its associated hashing. The circuit
change that the Ironwood pool relies on (the `enableCrossAddress` flag) is specified in
the Ironwood circuit ZIP [^ironwood-circuit]; activation parameters are specified in the
Ironwood deployment ZIP [^ironwood-deploy].


# Requirements

The version 6 transaction format MUST be able to carry an Ironwood bundle in addition
to the transparent, Sapling, and Orchard components of a version 5 transaction.

The Ironwood bundle MUST reuse the Orchard Action and bundle encoding, so that the
Orchard proving system, authorization, and note encryption apply unchanged.

The transaction identifier, signature hash, and authorizing-data commitment MUST commit
to the Ironwood bundle when it is present, using personalizations distinct from those
used for the Orchard bundle.


# Non-requirements

This ZIP does not define the Ironwood circuit or the `enableCrossAddressOrchard`
constraint (see [^ironwood-circuit]), the activation height or consensus branch ID
(see [^ironwood-deploy]), or wallet behaviour for migrating funds across the turnstile.

This ZIP does not reintroduce the OrchardZSA, issuance, or asset-burn fields, the
`zip233Amount` field, or per-transparent-input sighash information that appeared in the
withdrawn ZIP 230. [^zip-0230]


# Specification

## Transaction Format

A version 6 transaction is encoded as follows. Fields up to and including the Orchard
bundle are as in the version 5 format [^zip-0225], except as noted; the Ironwood bundle
is new.

Bytes                    | Name                     | Data Type                              | Description
------------------------ | ------------------------ | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Common Transaction Fields** ||||
`4`                      | `header`                 | `uint32`                               | Contains the `fOverwintered` flag (bit 31, always set) and `version` (bits 30 .. 0), which MUST be `6`.
`4`                      | `nVersionGroupId`        | `uint32`                               | Version group ID (nonzero); the version 6 value fixed in [^ironwood-deploy].
`4`                      | `nConsensusBranchId`     | `uint32`                               | Consensus branch ID; MUST be the NU6.3 branch ID [^ironwood-deploy].
`4`                      | `lock_time`              | `uint32`                               | Unix-epoch UTC time or block height, encoded as in Bitcoin.
`4`                      | `nExpiryHeight`          | `uint32`                               | A block height in {1 .. 499999999} after which the transaction will expire, or 0 to disable expiry. [^zip-0203]
**Transparent Transaction Fields** ||||
`varies`                 | `tx_in_count`            | `compactSize`                          | Number of transparent inputs in `tx_in`.
`varies`                 | `tx_in`                  | `tx_in`                                | Transparent inputs, encoded as in Bitcoin.
`varies`                 | `tx_out_count`           | `compactSize`                          | Number of transparent outputs in `tx_out`.
`varies`                 | `tx_out`                 | `tx_out`                               | Transparent outputs, encoded as in Bitcoin.
**Sapling Transaction Fields (unchanged from v5)** ||||
`varies`                 | `nSpendsSapling`         | `compactSize`                          | Number of Sapling Spend descriptions in `vSpendsSapling`.
`96 * nSpendsSapling`    | `vSpendsSapling`         | `SpendDescriptionV5[nSpendsSapling]`   | Sapling Spend descriptions, encoded per § 7.3 ‘Spend Description Encoding and Consensus’.
`varies`                 | `nOutputsSapling`        | `compactSize`                          | Number of Sapling Output descriptions in `vOutputsSapling`.
`756 * nOutputsSapling`  | `vOutputsSapling`        | `OutputDescriptionV5[nOutputsSapling]` | Sapling Output descriptions, encoded per § 7.4 ‘Output Description Encoding and Consensus’.
`8`                      | `valueBalanceSapling`    | `int64`                                | The net value of Sapling Spends minus Outputs.
`32`                     | `anchorSapling`          | `byte[32]`                             | A root of the Sapling note commitment tree at some block height in the past.
`192 * nSpendsSapling`   | `vSpendProofsSapling`    | `byte[192 * nSpendsSapling]`           | Encodings of the zk-SNARK proofs for each Sapling Spend.
`64 * nSpendsSapling`    | `vSpendAuthSigsSapling`  | `byte[64 * nSpendsSapling]`            | Authorizing signatures for each Sapling Spend.
`192 * nOutputsSapling`  | `vOutputProofsSapling`   | `byte[192 * nOutputsSapling]`          | Encodings of the zk-SNARK proofs for each Sapling Output.
`64`                     | `bindingSigSapling`      | `byte[64]`                             | A Sapling binding signature on the SIGHASH transaction hash.
**Orchard Transaction Fields** ||||
`varies`                 | `nActionsOrchard`        | `compactSize`                          | The number of Orchard Action descriptions in `vActionsOrchard`.
`820 * nActionsOrchard`  | `vActionsOrchard`        | `OrchardAction[nActionsOrchard]`       | A sequence of Orchard Action descriptions, encoded per § 7.5 ‘Action Description Encoding and Consensus’.
`1`                      | `flagsOrchard`           | `byte`                                 | An 8-bit value representing a set of flags. From LSB to MSB: `enableSpendsOrchard`, `enableOutputsOrchard`, `enableCrossAddressOrchard` (new at NU6.3); the remaining bits MUST be `0`.
`8`                      | `valueBalanceOrchard`    | `int64`                                | The net value of Orchard spends minus outputs.
`32`                     | `anchorOrchard`          | `byte[32]`                             | A root of the Orchard note commitment tree at some block height in the past.
`varies`                 | `sizeProofsOrchard`      | `compactSize`                          | Length in bytes of `proofsOrchard`. Value is `2720 + 2272 * nActionsOrchard`.
`sizeProofsOrchard`      | `proofsOrchard`          | `byte[sizeProofsOrchard]`              | Encoding of aggregated zk-SNARK proofs for Orchard Actions.
`64 * nActionsOrchard`   | `vSpendAuthSigsOrchard`  | `byte[64 * nActionsOrchard]`           | Authorizing signatures for each Orchard Action.
`64`                     | `bindingSigOrchard`      | `byte[64]`                             | An Orchard binding signature on the SIGHASH transaction hash.
**Ironwood Transaction Fields (new)** ||||
`varies`                 | `nActionsIronwood`       | `compactSize`                          | The number of Ironwood Action descriptions in `vActionsIronwood`.
`820 * nActionsIronwood` | `vActionsIronwood`       | `OrchardAction[nActionsIronwood]`      | A sequence of Ironwood Action descriptions, using the same encoding as Orchard Actions (§ 7.5).
`1`                      | `flagsIronwood`          | `byte`                                 | The same layout as `flagsOrchard`, including `enableCrossAddressOrchard` at bit 2; the remaining bits MUST be `0`.
`8`                      | `valueBalanceIronwood`   | `int64`                                | The net value of Ironwood spends minus outputs.
`32`                     | `anchorIronwood`         | `byte[32]`                             | A root of the **Ironwood** note commitment tree at some block height in the past.
`varies`                 | `sizeProofsIronwood`     | `compactSize`                          | Length in bytes of `proofsIronwood`. Value is `2720 + 2272 * nActionsIronwood`.
`sizeProofsIronwood`     | `proofsIronwood`         | `byte[sizeProofsIronwood]`             | Encoding of aggregated zk-SNARK proofs for Ironwood Actions.
`64 * nActionsIronwood`  | `vSpendAuthSigsIronwood` | `byte[64 * nActionsIronwood]`          | Authorizing signatures for each Ironwood Action.
`64`                     | `bindingSigIronwood`     | `byte[64]`                             | An Ironwood binding signature on the SIGHASH transaction hash.

The encoding of the transparent and Sapling fields is unchanged from version 5
[^zip-0225]. Ironwood Action descriptions use the same `OrchardAction` encoding as
Orchard Action descriptions. Every Ironwood output note uses the quantum-recoverable
note plaintext format (lead byte `0x03`) defined in ZIP 2005 [^zip-2005]; no Orchard
output note uses that format. This is the note-level distinction between the two pools.

## Consensus Rules

* `nVersionGroupId` MUST equal the version 6 version group ID, and `nConsensusBranchId`
  MUST equal the NU6.3 consensus branch ID, both defined in [^ironwood-deploy].

* As in version 5 [^zip-0225]:
    * The Orchard fields `flagsOrchard`, `valueBalanceOrchard`, `anchorOrchard`,
      `sizeProofsOrchard`, `proofsOrchard`, and `bindingSigOrchard` are present if and
      only if `nActionsOrchard > 0`. If `valueBalanceOrchard` is not present, it is taken
      to be `0`.
    * The proofs in `proofsOrchard` and the signatures in `vSpendAuthSigsOrchard` each
      correspond 1:1 to the elements of `vActionsOrchard`, in the same order.

* The same rules apply to the Ironwood bundle:
    * The Ironwood fields `flagsIronwood`, `valueBalanceIronwood`, `anchorIronwood`,
      `sizeProofsIronwood`, `proofsIronwood`, and `bindingSigIronwood` are present if and
      only if `nActionsIronwood > 0`. If `valueBalanceIronwood` is not present, it is
      taken to be `0`.
    * The proofs in `proofsIronwood` and the signatures in `vSpendAuthSigsIronwood` each
      correspond 1:1 to the elements of `vActionsIronwood`, in the same order.

* In `flagsOrchard` and `flagsIronwood`, bits 3 .. 7 MUST be `0`. The semantics of
  `enableSpendsOrchard` and `enableOutputsOrchard` are as in ZIP 224 [^zip-0224]. The
  `enableCrossAddressOrchard` flag is specified in [^ironwood-circuit]; before NU6.3 this
  bit was reserved as `0`.

* For coinbase transactions, `enableSpendsOrchard` MUST be `0` in both `flagsOrchard` and
  `flagsIronwood`. (From NU6.3, coinbase transactions are additionally constrained to have an
  empty Orchard bundle — forcing newly created shielded value into Ironwood — specified
  separately.)

* The `anchorOrchard` field refers to the Orchard note commitment tree, and the
  `anchorIronwood` field to the Ironwood note commitment tree. The Orchard and Ironwood pools
  have separate, independent note commitment trees and nullifier sets.

* The following rules apply from NU6.3 activation. *(Their placement — this ZIP or the
  deployment ZIP — is under discussion; see [Open Issues](#openissues).)*
    * A version 6 transaction MUST have `enableCrossAddressOrchard = 0` in `flagsOrchard`,
      restricting the legacy Orchard pool to same-receiver actions (see [^ironwood-circuit]).
    * No new value may enter the Orchard pool: `valueBalanceOrchard` MUST be greater than
      or equal to `0`.

## Transaction Identifiers, Signature Hashing, and Block Commitments

Version 6 transaction identifiers (txids), authorizing-data commitments ("auth digests"), and
signature hashes are computed as in ZIP 244 [^zip-0244], with two changes: an **Ironwood bundle
digest** is added, and for version 6 the Orchard and Ironwood **anchors move from effecting data to
authorizing data**. The version 5 algorithm is unchanged.

### Ironwood bundle digest

Relative to the txid digest for v5 transactions [^zip-0244-txiddigest], the version 6 txid digest
adds an Ironwood bundle digest as the last child, after the Orchard bundle digest:

    txid_digest_v6 = BLAKE2b-256("ZcashTxHash_" || consensusBranchId,
                                 header_digest || transparent_digest || sapling_digest ||
                                 orchard_digest_v6 || ironwood_digest_v6)

Relative to the auth digest for v5 transactions [^zip-0244-authorizingdatacommitment], the
version 6 auth digest adds an Ironwood auth digest as the last child, after the Orchard one:

    auth_digest_v6 = BLAKE2b-256("ZTxAuthHash_" || consensusBranchId,
                                 transparent_auth_digest || sapling_auth_digest ||
                                 orchard_auth_digest_v6 || ironwood_auth_digest_v6)

### Anchor commitment (version 6)

In version 5, the Sapling anchor (encoded redundantly as `anchor` in each
`sapling_spends_noncompact_digest`) and the Orchard anchor (`anchorOrchard` in `orchard_digest`)
are part of the **effecting data**: they are committed to in `txid_digest`, while the Sapling and
Orchard auth digests commit only to proofs and signatures [^zip-0244-authorizingdatacommitment].

In version 6, for Sapling, Orchard, and Ironwood bundles, the anchor is instead part of the
**authorizing data**. Relative to ZIP 244, for version 6 transactions:

- `sapling_spends_noncompact_digest`, `orchard_digest`, and `ironwood_digest` omit the anchor.
- `sapling_auth_digest`, `orchard_auth_digest`, and `ironwood_auth_digest` additionally commit
  to `anchorSapling`, `anchorOrchard`, or `anchorIronwood` respectively, after the existing fields.

This lets the anchor be updated (re-anchored to a more recent note commitment tree root) without
changing the transaction ID, while signatures still bind to the specific anchor used.

`ironwood_digest` and `ironwood_auth_digest` are computed with *the same structure* as the Orchard
`orchard_digest` and `orchard_auth_digest` (ZIP 244), but with Ironwood-specific 16-byte BLAKE2b
personalizations at each node. Also, distinct personalizations are used for Sapling and Orchard nodes
where the encoding has changed as a result of moving the anchor commitments to auth data, as follows:

node                                  | v5 personalization | v6 personalization | Comment for v6
------------------------------------- | ------------------ | ------------------ | -------------------------
sapling_digest[_v6]                   | `ZTxIdSaplingHash` | `ZTxIdSaplingHash` | not changed directly
sapling_spends_digest                 | `ZTxIdSSpendsHash` | `ZTxIdSSpendsHash` | unchanged
sapling_spends_compact_digest         | `ZTxIdSSpendCHash` | `ZTxIdSSpendCHash` | unchanged
sapling_spends_noncompact_digest[_v6] | `ZTxIdSSpendNHash` | `ZTxIdSSpendNH_v6` | omits `anchor`
sapling_auth_digest[_v6]              | `ZTxAuthSapliHash` | `ZTxAuthSapliH_v6` | includes `anchorSapling`
------------------------------------- | ------------------ | ------------------ | -------------------------
orchard_digest[_v6]                   | `ZTxIdOrchardHash` | `ZTxIdOrchardH_v6` | omits `anchorOrchard`
orchard_actions_compact_digest        | `ZTxIdOrcActCHash` | `ZTxIdOrcActCHash` | unchanged
orchard_actions_memos_digest          | `ZTxIdOrcActMHash` | `ZTxIdOrcActMHash` | unchanged
orchard_actions_noncompact_digest     | `ZTxIdOrcActNHash` | `ZTxIdOrcActNHash` | unchanged
orchard_auth_digest_v6                | `ZTxAuthOrchaHash` | `ZTxAuthOrchaH_v6` | includes `anchorOrchard`
------------------------------------- | ------------------ | ------------------ | -------------------------
ironwood_digest                       | n/a                | `ZTxIdIronwd_H_v6` | omits `anchorIronwood`
ironwood_actions_compact_digest       | n/a                | `ZTxIdIrnActCH_v6` |
ironwood_actions_memos_digest         | n/a                | `ZTxIdIrnActMH_v6` |
ironwood_actions_noncompact_digest    | n/a                | `ZTxIdIrnActNH_v6` |
ironwood_auth_digest                  | n/a                | `ZTxAuthIrnwdH_v6` | includes `anchorIronwood`

As in the case of Sapling and Orchard, when a version 6 transaction has no Ironwood actions,
`ironwood_digest` and `ironwood_auth_digest` are the hashes of empty input under the bundle and
auth personalizations respectively, i.e. `BLAKE2b-256("ZTxIdIronwd_H_v6", [])` and
`BLAKE2b-256("ZTxAuthIrnwdH_v6", [])`, which are distinct from the Orchard empty-bundle digests.

### Summary of the resulting digest structure and personalizations

Below, `(*)` indicates a node that is directly changed relative to v5, and `(+)` indicates a node
that is added relative to v5.

The txid digest structure becomes:

    txid_digest_v6
    ├── header_digest
    ├── transparent_digest
    │   ├── prevouts_digest
    │   ├── sequence_digest
    │   └── outputs_digest
    ├── sapling_digest_v6
    │   ├── sapling_spends_digest_v6
    │   │   ├── sapling_spends_compact_digest
    │   │   └── sapling_spends_noncompact_digest_v6 (*)
    │   │       ├── cv
    │   │       └── rk
    │   ├── sapling_outputs_digest
    │   │   ├── sapling_outputs_compact_digest
    │   │   ├── sapling_outputs_memos_digest
    │   │   └── sapling_outputs_noncompact_digest
    │   └── valueBalance
    ├── orchard_digest_v6 (*)
    │   ├── orchard_actions_compact_digest
    │   ├── orchard_actions_memos_digest
    │   ├── orchard_actions_noncompact_digest
    │   ├── flagsOrchard
    │   └── valueBalanceOrchard
    └── ironwood_digest_v6 (+)
        ├── ironwood_actions_compact_digest
        ├── ironwood_actions_memos_digest
        ├── ironwood_actions_noncompact_digest
        ├── flagsIronwood
        └── valueBalanceIronwood

The auth digest structure becomes:

    auth_digest_v6
    ├── transparent_scripts_digest
    ├── sapling_auth_digest_v6 (*)
    │   ├── vSpendProofsSapling
    │   ├── vSpendAuthSigsSapling
    │   ├── vOutputProofsSapling
    │   ├── bindingSigSapling
    │   └── anchorSapling (+)
    ├── orchard_auth_digest_v6 (*)
    │   ├── proofsOrchard
    │   ├── vSpendAuthSigsOrchard
    │   ├── bindingSigOrchard
    │   └── anchorOrchard (+)
    └── ironwood_auth_digest_v6 (+)
        ├── proofsIronwood
        ├── vSpendAuthSigsIronwood
        ├── bindingSigIronwood
        └── anchorIronwood

Note that the nodes under each of `sapling_digest_v6`, `orchard_digest_v6`, `ironwood_digest_v6`,
and their `auth_digest`s are present only if the corresponding bundle is non-empty.

### Block commitments

The `hashBlockCommitments` authorizing-data commitment [^zip-0244] incorporates the version 6 auth
digest — which now includes the Ironwood auth digest, and (per the change above) the anchors — with
no further structural change.

## Changes to ZIP 209

ZIP 209 [^zip-0209] is extended to track an Ironwood chain value pool balance and to require
it, like the other shielded pool balances, not to become negative.

[TODO take account of changes that should be (but are not currently) made in ZIP 256.
The check for each pool is now that the chain value pool balance stays within [0, MAX_MONEY].]

In the Terminology section, after the paragraph

> The "Orchard chain value pool balance" for a given block chain is the negation of the sum
> of all `valueBalanceOrchard` fields for transactions in the block chain. (Before NU5 has
> activated, the Orchard chain value pool balance is zero.)

add

> The "Ironwood chain value pool balance" for a given block chain is the negation of the sum
> of all `valueBalanceIronwood` fields for transactions in the block chain. (Before NU6.3
> has activated, the Ironwood chain value pool balance is zero.)

In the Specification section, replace

> If any of the "Sprout chain value pool balance", "Sapling chain value pool balance", or
> "Orchard chain value pool balance" would become negative in the block chain created as a
> result of accepting a block, then all nodes MUST reject the block as invalid.

with

> If any of the "Sprout chain value pool balance", "Sapling chain value pool balance",
> "Orchard chain value pool balance", or "Ironwood chain value pool balance" would become
> negative in the block chain created as a result of accepting a block, then all nodes MUST
> reject the block as invalid.

## Changes to the Protocol Specification

Changes corresponding to the [ZIP 209 changes above](#changestozip209) are required in
§ 4.17 ‘Chain Value Pool Balances’ [^protocol-chainvalue] to define an Ironwood chain value
pool balance alongside those for the existing Sprout, Sapling, and Orchard pools. These
mirror the changes above and are not spelled out here.

## Changes to ZIP 221

The history tree that commits to chain history [^zip-0221] gains Ironwood metadata, exactly
as it gained Orchard metadata at NU5. The new fields are computed and aggregated identically
to the corresponding `...Orchard...` fields.

In the "Tree Node specification" section, after field 14 `nOrchardTxCount`, add:

> 15. [NU6.3 onward] `hashEarliestIronwoodRoot`
>
>     Leaf node
>       Calculated as the note commitment root of the final Ironwood treestate
>       (similar to `hashEarliestOrchardRoot`).
>
>     Internal or root node
>       Inherited from the left child.
>
>     Serialized as `char[32]`.
>
> 16. [NU6.3 onward] `hashLatestIronwoodRoot`
>
>     Leaf node
>       Calculated as the note commitment root of the final Ironwood treestate
>       (similar to `hashLatestOrchardRoot`).
>
>     Internal or root node
>       Inherited from the right child.
>
>     Serialized as `char[32]`.
>
> 17. [NU6.3 onward] `nIronwoodTxCount`
>
>     Leaf node
>       The number of transactions in the leaf block where `vActionsIronwood`
>       is non-empty.
>
>     Internal or root node
>       The sum of the `nIronwoodTxCount` field of both children.
>
>     Serialized as `CompactSize uint`.

Replace

> The fields marked "[NU5 onward]" are omitted before NU5 activation [^zip-0252].
>
> Each node, when serialized, is between 147 and 171 bytes long (between 212 and 244 bytes
> after NU5 activation). [...]

with

> The fields marked "[NU5 onward]" are omitted before NU5 activation [^zip-0252]. The fields
> marked "[NU6.3 onward]" are omitted before NU6.3 activation.
>
> Each node, when serialized, is between 147 and 171 bytes long (between 212 and 244 bytes
> after NU5 activation, and between 277 and 317 bytes after NU6.3 activation). [...]

The pseudocode node structure and `serialize` / `make_leaf` / `make_parent` functions are
extended with `hashEarliestIronwoodRoot`, `hashLatestIronwoodRoot`, and `nIronwoodTxCount`
in the same way the "# NU5 only" Orchard fields were added (present iff NU6.3 has activated;
the roots inherited from the left/right child and the count summed, in internal nodes).

`hashChainHistoryRoot` continues to be the BLAKE2b-256 digest of the serialized root node;
its value changes at NU6.3 only through the added node fields. The `hashBlockCommitments`
header field [^zip-0244] is unaffected beyond this.

# Rationale

**Reuse of the Orchard protocol.** Carrying the Ironwood pool as a second
Orchard-protocol bundle, rather than defining a new shielded protocol, keeps the
transaction-format and implementation surface small: the Action encoding, proving system,
authorization, and note encryption are inherited unchanged. The pools are distinguished
by their note commitment trees, nullifier sets, value pool balances, and bundle position,
not by separate circuits.

**Separate state.** Giving the Ironwood pool its own note commitment tree, anchor, and
nullifier set creates a clean state boundary from the legacy Orchard pool, so the two
pools do not share anonymity-set state and the turnstile can be accounted for
independently.

**`enableCrossAddressOrchard` polarity.** The flag is encoded in the enabled sense
(`1` = cross-address transfers enabled, the normal case; `0` = restricted to the spend
address), with bit 2 reserved as `0` before NU6.3. This is reverse compatible: a legacy
Orchard-pool spend after NU6.3 requires the restricted state, which is bit 2 = `0` —
exactly the value that signers treating bit 2 as a reserved-zero bit already produce. The
in-circuit constraint and the equivalent internal `disableCrossAddressOrchard` instance
value are discussed in [^ironwood-circuit].


# Open Issues

* **Placement of the turnstile / value-pool rules.** The "no new value into Orchard" rule
  and the ZIP 209 chain value pool balance accounting could instead live in
  [^ironwood-deploy]; the placement is to be decided.


# Deployment

This transaction format is deployed at NU6.3. Activation heights, the version 6 version
group ID, and the NU6.3 consensus branch ID are specified in [^ironwood-deploy].


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-chainvalue]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later. Section 4.17: Chain Value Pool Balances](protocol/protocol.pdf#chainvaluepoolbalances)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0203]: [ZIP 203: Transaction Expiry](zip-0203.rst)

[^zip-0209]: [ZIP 209: Prohibit Negative Shielded Chain Value Pool Balances](zip-0209.rst)

[^zip-0221]: [ZIP 221: FlyClient - Consensus-Layer Changes](zip-0221.rst)

[^zip-0224]: [ZIP 224: Orchard Shielded Protocol](zip-0224.rst)

[^zip-0225]: [ZIP 225: Version 5 Transaction Format](zip-0225.rst)

[^zip-0230]: [ZIP 230: Withdrawn Version 6 Transaction Format](zip-0230.rst)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^zip-0244-txiddigest]: [ZIP 244: Transaction Identifier Non-Malleability. Section: TxId Digest](zip-0244.rst#txid-digest)

[^zip-0244-authorizingdatacommitment]: [ZIP 244: Transaction Identifier Non-Malleability. Section: Authorizing Data Commitment](zip-0244.rst#authorizing-data-commitment)

[^zip-0252]: [ZIP 252: Deployment of the NU5 Network Upgrade](zip-0252.rst)

[^zip-2005]: [ZIP 2005: Orchard Quantum Recoverability](zip-2005.md)

[^ironwood-circuit]: [Ironwood Circuit (draft)](draft-zodl-valargroup-ironwood-circuit.md)

[^ironwood-deploy]: [Deployment of the Ironwood Network Upgrade (draft)](draft-zodl-valargroup-deploy-ironwood.md)
