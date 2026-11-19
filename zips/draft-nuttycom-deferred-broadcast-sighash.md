
    ZIP: Unassigned
    Title: Sighash Variant for Deferred Broadcast
    Owners: Kris Nuttycombe <kris@nutty.land>
    Status: Draft
    Category: Consensus / Wallet
    Created: 2026-11-19
    License: MIT


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in § 3.12
‘Mainnet and Testnet’. [^protocol-networks]

The term "full validator" in this document is to be interpreted as defined in
§ 3.3 ‘The Block Chain’. [^protocol-blockchain]

The terms "consensus branch", "consensus branch ID", "epoch", and "network
upgrade" are to be interpreted as described in ZIP 200. [^zip-0200]

The terms "v7 transaction", "effecting data", "authorizing data", "sighash
variant", and "transaction identifier" are to be interpreted as described in
ZIP 248. [^zip-0248]

The term "binding signing key", written $\mathsf{bsk}$, is to be interpreted as
defined in § 4.13 ‘Balance and Binding Signature (Sapling)’ for a Sapling
bundle [^protocol-saplingbalance] and in § 4.14 ‘Balance and Binding Signature
(Orchard)’ for an Orchard or Ironwood bundle. [^protocol-orchardbalance]

The terms below are to be interpreted as follows:

Shielded bundle
:   A Sapling, Orchard, or Ironwood bundle of a v7 transaction, as defined in
    ZIP 248. [^zip-0248]

Signer
:   A party that makes a spend authorization signature or a transparent input
    signature for a transaction. Each participant in a threshold signing
    session is a signer.

Signing time
:   The time at which a signer makes its signature for a transaction.

Target height
:   The height of the next block after the chain tip, as seen by a wallet at a
    given time.

Completing a transaction
:   Carrying out the steps that make a signed v7 transaction ready to
    broadcast. The steps are: setting the `nConsensusBranchId` and
    `nExpiryHeight` fields; selecting the anchor of each shielded bundle and
    creating its proofs, if they do not already exist; and making the binding
    signature of each shielded bundle.

Deferred broadcast
:   Completing and broadcasting a transaction at a time later than its signing
    time. The device or party that does so might not hold any spending key.


# Abstract

ZIP 248 [^zip-0248] lets each signature in a v7 transaction select a signature
hash ("sighash") variant. Its only variant, variant 0, commits to all of the
effecting data of the transaction, including the consensus branch ID and the
expiry height.

This ZIP defines sighash variant 1, which commits to the same data except those
two fields. Variant 1 is available for spend authorization signatures and
transparent input signatures. Binding signatures continue to use variant 0.

The holder of a spending key can then authorize a transaction at one time, and
a device without that key can complete and broadcast it later, even after a
network upgrade. That device sets the consensus branch ID, the expiry height,
and the anchors as it would for a transaction signed at that moment, so these
fields do not reveal how long ago the transaction was signed. The use of
variant 1 is itself visible in the transaction.

A variant 1 signature does not expire, and it is valid on every consensus
branch that accepts the transaction. In a transaction with a shielded bundle,
making use of this requires the binding signing key of the bundle. The party
that constructed the bundle knows that key, and so does any party to which it
disclosed the value commitment randomness. This ZIP specifies the wallet
behaviour that these properties require.


# Motivation

Every signature in a version 5 or version 6 transaction commits to the
`nConsensusBranchId` and `nExpiryHeight` fields. [^zip-0244] [^zip-0229] So
does every variant 0 signature in a v7 transaction. [^zip-0248] A signer must
therefore know, at signing time, the consensus branch in which the transaction
will be mined and the last height at which it can be mined.

A signer knows both when it broadcasts immediately. It does not when signing
and broadcast are separated, for example:

* A hardware wallet or offline device signs, and another device broadcasts
  later.
* Several parties sign with a threshold signature scheme [^zip-0312], and
  collecting enough signature shares takes an unpredictable time.
* A wallet signs a schedule of transactions in one session and broadcasts them
  over days or weeks, as in the Orchard to Ironwood migration. [^zip-0318]
* A wallet holds its spending key only while the user is present, and
  broadcasts from a background task.

Signers that defer broadcast today work around each commitment at a cost:

* **Expiry height.** The default expiry height is about 50 minutes after the
  transaction is created. [^zip-0203] A signer that defers broadcast for
  longer must sign a later expiry height or disable expiry. Either choice
  differs from what other wallets do, and so marks the transaction. A later
  expiry height can also reveal the signing time. ZIP 318 limits that leak by
  computing the expiry height from 30-day periods, but the result still
  differs from the default. [^zip-0318]
* **Consensus branch ID.** A signature is valid on one consensus branch, so a
  signed transaction becomes invalid when a network upgrade activates. A
  signer can sign one copy for each consensus branch that might apply, as
  ZIP 318 requires. [^zip-0318] This multiplies the signing work, and it is
  possible only for network upgrades whose consensus branch IDs are known at
  signing time.

Anchors used to pose the same problem. The version 6 transaction format made
them authorizing data, so that proofs can be created after signing against an
anchor chosen at that time [^zip-0229], and the v7 format keeps this property.
[^zip-0248] The consensus branch ID and the expiry height are the remaining
fields that a signer must predict. The sighash variants of ZIP 248 allow a
signature to omit them without another change to the transaction format.


# Privacy Implications

The sighash variant of each signature is encoded in the authorizing data, so an
observer of the block chain can see which transactions contain variant 1
signatures. If only transactions with deferred broadcast used variant 1, its
presence would reveal the deferral. This ZIP therefore recommends that a wallet
that supports deferred broadcast use variant 1 for every v7 transaction that
contains a shielded bundle.

Among transactions that use variant 1, this ZIP aims to hide how long before
broadcast a transaction was signed. The consensus branch ID, the expiry height,
and the anchors are chosen at completion by the rules for a transaction signed
at that time, so they carry no information about the signing time. The
workarounds described in [Motivation] do not achieve this.

Some signed data can still reveal information about the signing time:

* The fee, if the conventional fee for a transaction of that shape changes
  between signing and broadcast.
* The lock time, if the signer derives it from the block height at signing
  time.
* The transaction version and the bundle variants, which reflect the choices
  available at signing time.

An observer of unmined transactions can also learn that a transaction was
completed twice. Two completions of one signed transaction have the same
effecting data apart from the two fields. A wallet that signs again produces
different effecting data.

A wallet that delegates completion to another party reveals to that party
whatever it provides. A binding signing key reveals nothing about notes or
addresses. The private inputs of the proofs reveal the values and addresses of
the notes concerned.

This ZIP does not affect the timing of broadcasts or other information visible
at the network layer.


# Requirements

* A variant 1 signature remains valid whatever the values of
  `nConsensusBranchId` and `nExpiryHeight`.
* A variant 1 signature commits to all other data that a variant 0 signature
  commits to.
* A completed transaction has the consensus branch ID, expiry height, and
  anchors that it would have if it had been signed at the time of completion.
* In a transaction that contains a shielded bundle, only a party that knows
  the binding signing key of every shielded bundle can change the transaction
  identifier, make the transaction valid after it expires, or make it valid on
  another consensus branch.
* The transaction format, the transaction identifier, and the authorizing data
  commitment do not change.
* The consensus rules for the consensus branch ID and the expiry height do not
  become weaker.
* A variant 1 signature digest costs no more hash compressions than a
  variant 0 signature digest.


# Non-requirements

* This ZIP does not change the version 5 or version 6 transaction formats or
  their sighash algorithms.
* This ZIP does not protect a variant 1 signature against replay on another
  consensus branch by a party that knows the value commitment randomness of
  its shielded bundles. [Cross-chain replay] states which parties can replay
  a transaction, and under which conditions.
* This ZIP does not protect a transaction that has no shielded bundle and
  whose transparent inputs all use variant 1. Any party can change its
  transaction identifier or replay it on another consensus branch.
* This ZIP does not support signing a spend of a transparent output of a
  transaction that has not yet been completed. A transparent input refers to
  that transaction by its transaction identifier, and each completion has a
  different one.


# Specification

## Sighash variant 1

This ZIP defines sighash variant 1 for v7 transactions. [^zip-0248] A signature
that uses variant 1 has `sighashVariant = 0x01`. The `associatedData` of
variant 1 is the empty byte string. The `sighashInfo` of such a signature is
therefore the single byte `0x01`, encoded with `sizeSighashInfo = 1`.

Variant 1 is defined for bundle variant 0 of the transparent, Sapling, Orchard,
and Ironwood bundle types. The following table lists the signatures of those
bundles and the sighash variants that are defined for each of them.

| Bundle      | `bundleType` | Signature                                      | Variant 0 | Variant 1 |
|-------------|--------------|------------------------------------------------|-----------|-----------|
| Transparent | 0            | Signatures checked by the scripts of one input | ✅        | ✅        |
| Sapling     | 2            | `vSpendAuthSigsSapling[i]`                     | ✅        | ✅        |
| Sapling     | 2            | `bindingSigSapling`                            | ✅        | ❌        |
| Orchard     | 3            | `vSpendAuthSigsOrchard[i]`                     | ✅        | ✅        |
| Orchard     | 3            | `bindingSigOrchard`                            | ✅        | ❌        |
| Ironwood    | 4            | `vSpendAuthSigsOrchard[i]`                     | ✅        | ✅        |
| Ironwood    | 4            | `bindingSigOrchard`                            | ✅        | ❌        |

The sighash variant of a transparent input is given by the `sighashInfo` field
of its `TransparentInputAuth`. It applies to every signature that is checked
when the scripts of that input are evaluated.

Each signature selects its sighash variant independently of the other
signatures in the transaction. A transaction MAY contain both variant 0
signatures and variant 1 signatures.

This ZIP does not define variant 1 for any other bundle type or bundle variant.
A ZIP that registers another bundle type or bundle variant specifies whether
variant 1 is defined for its signatures.

## Variant 1 signature digest

A signature that uses variant 1 commits to the digest defined in this section.
The digest has the structure of the variant 0 signature digest of ZIP 248
[^zip-0248], with `txid_digest` replaced by `effects_sig_digest`:

```
signature_digest
├── sighashVariant
├── effects_sig_digest
│   ├── header_sig_digest
│   ├── value_pool_deltas_digest
│   └── effects_bundles_digest
├── amounts_sig_digest
├── scriptpubkeys_sig_digest
├── bundleType
├── bundleVariant
└── signature_context
```

All digests are personalized BLAKE2b-256 hashes. All personalization strings
are 16 bytes long.

The `nConsensusBranchId` and `nExpiryHeight` fields of the transaction are not
inputs to any part of this digest. The consensus branch ID is also not part of
any personalization string used in this digest.

### V1: signature_digest

A BLAKE2b-256 hash of the following values:

```
V1.1: sighashVariant            (1 byte, 0x01)
V1.2: effects_sig_digest        (32-byte hash output)
V1.3: amounts_sig_digest        (32-byte hash output)
V1.4: scriptpubkeys_sig_digest  (32-byte hash output)
V1.5: bundleType                (compactSize encoding)
V1.6: bundleVariant             (compactSize encoding)
V1.7: signature_context         (bundle-defined byte string)
```

The personalization field of this hash is set to:

```
"ZcashSigHash_v7_" (2 underscore characters)
```

This is the personalization of the variant 0 signature digest. The value of
`sighashVariant` separates the two digests.

`amounts_sig_digest` and `scriptpubkeys_sig_digest` are the digests of those
names defined in ZIP 248. [^zip-0248] They commit to the values and to the
script public keys of the coins spent by all transparent inputs of the
transaction.

`bundleType` and `bundleVariant` identify the bundle that contains the
signature.

`signature_context` is the byte string that ZIP 248 defines for a variant 0
signature in the same position. It is the final field, with no length prefix.

* For a transparent input, it is the concatenation of these fields of the
  input being signed: `prevout` (36 bytes), `value` (8-byte signed
  little-endian), `scriptPubKey` (with `compactSize` length prefix),
  `nSequence` (4-byte unsigned little-endian), and `input_index` (2-byte
  unsigned little-endian).
* For `vSpendAuthSigsSapling[i]`, it is the 2-byte unsigned little-endian
  encoding of $i$.
* For `vSpendAuthSigsOrchard[i]` in an Orchard bundle or an Ironwood bundle,
  it is the 2-byte unsigned little-endian encoding of $i$.

### V1.2: effects_sig_digest

A BLAKE2b-256 hash of the following values:

```
V1.2a: header_sig_digest         (32-byte hash output)
V1.2b: value_pool_deltas_digest  (32-byte hash output)
V1.2c: effects_bundles_digest    (32-byte hash output)
```

The personalization field of this hash is set to:

```
"ZTxSigEffectHash"
```

`value_pool_deltas_digest` and `effects_bundles_digest` are the values T.2 and
T.3 of the transaction identifier digest defined in ZIP 248. [^zip-0248] They
commit to the complete value pool delta map and to the effecting data of every
bundle in the transaction.

### V1.2a: header_sig_digest

A BLAKE2b-256 hash of the following values:

```
V1.2a.i:   version          (4-byte little-endian version identifier including overwintered flag)
V1.2a.ii:  nVersionGroupId  (4-byte little-endian version group identifier)
V1.2a.iii: lock_time        (4-byte little-endian nLockTime value)
```

The personalization field of this hash is set to:

```
"ZTxSigHeaderHash"
```

## Consensus rules

The following rules apply to v7 transactions from the activation of this ZIP.
Full validators MUST enforce them.

* A signature whose `sighashInfo` is the single byte `0x01` MUST be verified
  against the digest defined in [Variant 1 signature digest].

* The `sighashInfo` of each `TransparentInputAuth`, of each element of
  `vSpendAuthSigsSapling`, and of each element of `vSpendAuthSigsOrchard` in an
  Orchard or Ironwood bundle MUST be an encoding that is defined for that
  signature. ZIP 248 and this ZIP define two such encodings: the single byte
  `0x00` and the single byte `0x01`.

* The `sighashInfo` of `bindingSigSapling`, and of `bindingSigOrchard` in an
  Orchard or Ironwood bundle, MUST be the single byte `0x00`.

* For each `TransparentInputAuth` whose `sighashInfo` specifies sighash
  variant 1, the `hash_type` byte of every nonempty signature supplied to
  `OP_CHECKSIG`, `OP_CHECKSIGVERIFY`, `OP_CHECKMULTISIG`, or
  `OP_CHECKMULTISIGVERIFY` when validating that input MUST be `SIGHASH_ALL`
  (`0x01`).

* The `nConsensusBranchId` field of a v7 transaction MUST equal the consensus
  branch ID of the epoch of the block that contains the transaction. This rule
  applies whichever sighash variants the signatures of the transaction use.

The consensus rules for `nExpiryHeight` in § 7.1.2 ‘Transaction Consensus
Rules’ [^protocol-txnconsensus] are unchanged. The transaction identifier and
the authorizing data commitment are computed as specified in ZIP 248
[^zip-0248], so the transaction identifier still commits to both fields.

## Requirements for signing

A variant 1 signature does not limit the consensus branch or the heights at
which a transaction can be mined. In a transaction that contains a shielded
bundle, the binding signatures commit to `nConsensusBranchId` and
`nExpiryHeight`, so only a party that knows every binding signing key can
choose them. In a transaction with no shielded bundle whose transparent inputs
all use variant 1, no signature commits to these fields. Any party can change
them, and with them the transaction identifier.

In a threshold signing session, the requirements below apply to each
participant.

* A wallet that supports deferred broadcast SHOULD use variant 1 for every
  spend authorization signature and transparent input signature of a v7
  transaction that contains a shielded bundle, whether or not it defers the
  broadcast of that transaction.

* A signer SHOULD use variant 0 for a v7 transaction that contains no shielded
  bundle, unless the broadcast of that transaction is deferred.

* A signer SHOULD use the same sighash variant for every signature that it
  makes for a transaction.

* A signer that uses variant 1 SHOULD sign only transactions with
  `lock_time = 0`, unless the purpose of the transaction requires a lock time.

* A signer that asks a user to confirm the details of a transaction before it
  makes a variant 1 signature SHOULD tell the user that the signature does not
  limit when the transaction can be mined. It MUST NOT present an expiry height
  as a limit on the authorization.

## Requirements for completing a transaction

A wallet that completes a v7 transaction containing a variant 1 signature:

* MUST set `nConsensusBranchId` to the consensus branch ID of the epoch that
  contains the target height.

* MUST set `nExpiryHeight` as it does for a transaction that it signs at the
  time of completion. The signing time MUST NOT affect the value. The value
  SHOULD be the target height plus the default expiry delta in effect at the
  target height. [^zip-0203]

* SHOULD select the anchor of each shielded bundle as it does for a
  transaction that it creates at the time of completion, and SHOULD create the
  proofs of the bundle against that anchor.

* MUST make the binding signature of each shielded bundle after it sets
  `nConsensusBranchId` and `nExpiryHeight`.

A wallet SHOULD complete a transaction only when it is about to broadcast it.

A completed transaction becomes invalid if it expires, or if a network upgrade
activates, before it is mined. A wallet MAY then complete it again. Each
completion has a different transaction identifier. All completions spend the
same inputs, so at most one can be mined, and nodes handle them as they handle
any transactions that spend the same input.

## Requirements for wallets that hold variant 1 signatures

A variant 1 signature stays valid until the transaction can no longer be
mined. That happens when one of its inputs is spent, or when consensus stops
accepting its transaction version or one of its bundle variants. The passing
of an expiry height and the activation of a network upgrade do not end it.

The following requirements apply to a wallet that has made, or that stores,
variant 1 signatures for a transaction. In them, the wallet decides that a
transaction has been mined by its usual confirmation policy.

* The wallet MUST NOT treat the transaction as cancelled or failed because the
  expiry height of a completion has passed.

* If the wallet creates another transaction to take its place, for example to
  make the same payment, the new transaction MUST spend at least one input of
  the transaction that it replaces. Then at most one of the two can be mined.

* To cancel the transaction, the wallet MUST spend at least one of its inputs
  in another transaction. It MUST treat the cancellation as effective only
  when that other transaction has been mined.

* Until the transaction is mined, the wallet SHOULD identify it by the
  nullifiers and transparent outputs that it spends, and not by a transaction
  identifier.

* The wallet SHOULD give a binding signing key, or the value commitment
  randomness from which it is derived, only to a party that needs it to check
  or to complete the transaction. Once the spend authorization signatures and
  proofs of the transaction are public, every party that knows the binding
  signing key of every shielded bundle can complete the transaction again. It
  can do so at any later time, on any consensus branch that accepts the
  transaction.

## Changes to ZIP 248

In the changes below, "ZIP TBD" stands for the number that the ZIP Editors
assign to this ZIP, and `[#zip-tbd]_` stands for a reference to it.

In ‘Sighash Variants’, after:

> ```
> Variant 0 is the "commit to all effecting data" sighash algorithm.
> ```

add:

> ```
> Variant 1 commits to all effecting data except the consensus branch ID and
> the expiry height. It is defined in ZIP TBD. [#zip-tbd]_
> ```

In ‘Variant 0 Signature Digest’, replace:

> ```
> For sighash variant 0 (the only variant
> currently defined for v7 transactions), the digest algorithm is as specified
> below.
> ```

with:

> ```
> For sighash variant 0, the digest algorithm is as specified below. The digest
> algorithm for sighash variant 1 is specified in ZIP TBD. [#zip-tbd]_
> ```

In ‘Bundle-local rules’, replace:

> ```
> * For each ``TransparentInputAuth`` whose ``sighashInfo`` specifies sighash
>   variant 0, the ``hash_type`` byte of every nonempty signature supplied to
> ```

with:

> ```
> * For each ``TransparentInputAuth`` whose ``sighashInfo`` specifies sighash
>   variant 0 or sighash variant 1, the ``hash_type`` byte of every nonempty
>   signature supplied to
> ```

and add the rule:

> ```
> * The ``sighashInfo`` of ``bindingSigSapling``, and of ``bindingSigOrchard``
>   in an Orchard or Ironwood bundle, MUST specify sighash variant 0.
>   [#zip-tbd]_
> ```

In ‘Transparent Sighash Algorithms’, replace the whole paragraph with:

> ```
> For the transparent bundle at ``bundleVariant = 0``, sighash variants 0 and 1
> are defined. The ``associatedData`` of each is the empty byte string. A
> signature made with variant 0 commits to the digest defined in `Variant 0
> Signature Digest`_. A signature made with variant 1 commits to the variant 1
> signature digest defined in ZIP TBD. [#zip-tbd]_ In both cases
> ``bundleType = 0``, ``bundleVariant = 0``, and ``signature_context`` is as
> defined in `S.7: Transparent Signature Context`_.
> ```

In ‘Sapling Sighash Algorithms’, replace the first paragraph with:

> ```
> For the Sapling bundle at ``bundleVariant = 0``, sighash variants 0 and 1 are
> defined for a ``spendAuthSig``, and only sighash variant 0 is defined for a
> ``bindingSig``. The ``associatedData`` of each variant is the empty byte
> string. A signature made with variant 0 commits to the digest defined in
> `Variant 0 Signature Digest`_. A ``spendAuthSig`` made with variant 1 commits
> to the variant 1 signature digest defined in ZIP TBD. [#zip-tbd]_ In both
> cases ``bundleType = 2`` and ``bundleVariant = 0``.
> ```

In ‘Orchard Protocol Sighash Algorithms’, replace the first paragraph with:

> ```
> For the Orchard and Ironwood bundles at ``bundleVariant = 0``, sighash
> variants 0 and 1 are defined for a ``spendAuthSig``, and only sighash variant
> 0 is defined for a ``bindingSig``. The ``associatedData`` of each variant is
> the empty byte string. A signature made with variant 0 commits to the digest
> defined in `Variant 0 Signature Digest`_. A ``spendAuthSig`` made with
> variant 1 commits to the variant 1 signature digest defined in ZIP TBD.
> [#zip-tbd]_ In both cases ``bundleType = 3`` for Orchard or
> ``bundleType = 4`` for Ironwood, and ``bundleVariant = 0``.
> ```

In ‘References’, add:

> ```
> .. [#zip-tbd] `ZIP TBD: Sighash Variant for Deferred Broadcast <draft-nuttycom-deferred-broadcast-sighash.md>`_
> ```

## Changes to the Protocol Specification

These changes are written relative to the protocol specification as modified
by ZIP 248. [^zip-0248] Each change applies from the activation of this ZIP.

### § 4.10 ‘SIGHASH Transaction Hashing’

ZIP 248 adds the following sentence to this section. [^protocol-sighash]

> The SIGHASH algorithms used for v7 transactions are defined in ZIP 248.

After it, add:

> A signature in a v7 transaction that uses sighash variant 1, as defined in
> ZIP TBD, does not commit to a consensus branch ID or to the `nExpiryHeight`
> field. The consensus branch ID of such a transaction is constrained by the
> rule on its `nConsensusBranchId` field in § 7.1.2 ‘Transaction Consensus
> Rules’.

### § 7.1.2 ‘Transaction Consensus Rules’

This section contains the following rule. [^protocol-txnconsensus]

> [NU5 onward] If $\mathsf{effectiveVersion} \geq 5$, the `nConsensusBranchId`
> field MUST match the consensus branch ID used for SIGHASH transaction hashes,
> as specified in [ZIP-244].

After it, add:

> If $\mathsf{effectiveVersion} \geq 7$, the `nConsensusBranchId` field MUST
> equal the consensus branch ID of the epoch of the block that contains the
> transaction, whichever sighash variants the signatures of the transaction
> use.

## Applicability

All of these changes apply identically to Mainnet and Testnet.


# Security Considerations

## Cross-chain replay

A replay applies the effects of a signed transaction on a second block chain,
without a new signature from the signer. This section considers a second chain
that shares history with the first and has a different consensus branch ID,
such as the other side of a chain split at a network upgrade.

Variant 0 prevents such a replay, because every signature commits to the
consensus branch ID. [^zip-0200] Variant 1 removes that protection from the
signatures that use it. Two other cases are the same for both variants. Chains
with the same consensus branch ID have no replay protection. Chains that share
no history, such as Mainnet and Testnet, have no inputs in common.

A replay cannot change the effects of a transaction. It spends the same inputs
and creates the same outputs, with the same values and recipients. A
transaction can be replayed on the second chain only if all of the following
hold:

1. The second chain accepts the transaction version, the bundle types and
   variants, and sighash variant 1, and the transaction meets the other
   consensus rules of that chain.
2. Every input exists and is unspent on the second chain. For a transparent
   input, the output that it refers to exists there with the same transaction
   identifier and index. For a shielded spend, the note commitment is in the
   note commitment tree there, and the nullifier in the transaction has not
   been revealed there.
3. Every variant 0 signature in the transaction is made again. The transaction
   identifier differs on the second chain, so no variant 0 signature remains
   valid.
4. The proofs of each shielded bundle are valid for an anchor of the second
   chain.

An input created before the chains diverged satisfies condition 2 until it is
spent on the second chain. Inputs created later are restricted:

* A transparent output created later by a transaction of version 5 or above
  never satisfies it, because the identifier of that transaction commits to
  the consensus branch ID.
* An Orchard or Ironwood note created later satisfies it only if the
  transaction that created the note was itself replayed.
* A Sapling note created later also needs the same position in the note
  commitment tree of both chains, because its nullifier depends on that
  position.

Conditions 3 and 4 determine which parties can replay a transaction:

* **Any party.** A transaction with no shielded bundle, in which every
  transparent input uses variant 1, has no variant 0 signature and no proof.
  Any party that sees it can replay it.
* **A party that knows the binding signing key of every shielded bundle.**
  This party can make the binding signatures again. If every other signature
  uses variant 1, it can replay the transaction with the existing proofs,
  provided that their anchors are from before the chains diverged. Those
  anchors are valid on both chains, because an anchor can refer to the final
  treestate of any earlier block. [^protocol-transactions]
* **A party that knows the private inputs of every proof.**
  [^protocol-spendstatement] [^protocol-actionstatement] These inputs include
  the value commitment randomness, from which the binding signing keys are
  derived. This party can also create new proofs, so it can replay such a
  transaction whatever its anchors.

No party can replay a transaction that has a variant 0 spend authorization
signature or transparent input signature without the key that made that
signature.

The constructor of a shielded bundle chooses its value commitment randomness
and the spend authorization randomizer $\alpha$ of each spend. The spend
authorization signatures commit to the value commitments and to `rk`, so these
choices are fixed once the transaction is signed. They cannot be recovered
from the transaction or from a full viewing key. The second and third parties
above are therefore the constructor, and any party to which it disclosed these
values:

* When a hardware wallet signs, the constructor is the companion wallet that
  holds the full viewing key. [^zip-0374]
* In a FROST signing session, the constructor is the Coordinator. It discloses
  the openings of the value commitments to each participant, so each
  participant knows the binding signing keys. See
  [Threshold signing with FROST].

An observer of the block chain cannot replay a transaction that contains a
shielded bundle. Neither can the recipient of one of its outputs, or a holder
of the full viewing key that does not know these values.

A signer prevents the replay of a signed transaction on a chain by spending
one of its inputs on that chain in another transaction.


# Rationale

## Omitting the consensus branch ID

Variant 0 commits to the consensus branch ID to provide two-way replay
protection: a signature made for one consensus branch is invalid on every
other. [^zip-0200] That protection is what prevents deferred broadcast across
a network upgrade.

A variant 1 signature still commits to the transaction version, the version
group ID, and the type and variant of every bundle. ZIP 248 fixes the
semantics of each bundle type and variant for the lifetime of a transaction
version. [^zip-0248] A network upgrade therefore cannot change the meaning of
the data that the signer authorized. It can stop accepting a transaction
version or a bundle variant, in which case the transaction can no longer be
mined and the signer loses nothing.

A signer accepts two risks by using variant 1:

* If the block chain splits into two lasting consensus branches, a party that
  can complete the transaction can have it mined on both. See
  [Cross-chain replay].
* A network upgrade can change consensus rules that are not part of the
  semantics of a bundle, such as how fees are distributed. The transaction is
  then mined under rules that differ from those in force at signing time.

## Omitting the expiry height

Variant 0 commits to the expiry height so that the signer limits the time
during which the transaction can be mined. [^zip-0203] A signer that defers
broadcast cannot know the target height at broadcast. If the expiry height
stays under the signature, the signer must disable expiry or sign a distant
expiry height, with the costs described in [Motivation].

A variant whose `associatedData` carried an upper bound on the expiry height
was considered. It would let the signer keep a limit on the validity of its
signature. It was rejected because the bound would be visible in the
transaction and would reveal the signing time, as a distant expiry height
does.

The cost of omitting the expiry height is that a signature stays valid until
an input of the transaction is spent. Without the requirements in
[Requirements for wallets that hold variant 1 signatures], a wallet could
regard an expired payment as cancelled, make the payment again from different
notes, and then see both payments mined.

## Fields that variant 1 still commits to

* The transaction version and the version group ID, because they determine
  how every other field is interpreted.
* The lock time, because a signer chooses it on purpose. Unlike the expiry
  height, its usual value, zero, is independent of the signing time.
* The value pool delta map, and so the fee, because the fee is an effect of
  the transaction. A party that completes the transaction cannot change what
  the signer pays.

## Structure of the variant 1 digest

The variant 1 digest replaces one 32-byte input of the variant 0 digest with
another, so the preimage of `signature_digest` keeps its layout and length.
With one-byte encodings of the bundle type and variant, the fields before
`signature_context` occupy 99 bytes. The digest for a shielded spend
authorization signature therefore needs one BLAKE2b compression, as it does
for variant 0.

`effects_sig_digest` is computed once per transaction, from the value pool
delta digest and the effects bundles digest that the transaction identifier
also uses. `header_sig_digest` has a 12-byte input and `effects_sig_digest`
has a 96-byte input, so each needs one compression. Both have their own
personalization strings because they hash different data from the
corresponding digests of the transaction identifier.

A signer that makes only variant 1 signatures does not need the transaction
identifier, so it can sign before the consensus branch ID and the expiry
height are known.

`effects_sig_digest` has the same value for every completion of a signed
transaction. A wallet can use it to recognize a mined transaction as a
completion of a transaction that it signed.

## Rationale for binding signatures using variant 0

A party without key material can change a field of a transaction exactly when
no signature in the transaction commits to that field. If every signature
used variant 1, any party could change the consensus branch ID and the expiry
height:

* The transaction identifier would be malleable by third parties, which
  ZIP 244 set out to prevent. [^zip-0244]
* Any party could make an expired transaction valid again. A recipient could
  do this to a payment that the sender believed had been cancelled.

One variant 0 signature is enough to prevent both. The binding signature is
the natural choice:

* Making it requires the binding signing key and no spend authority, so a
  device that holds no spending key can make it.
* The binding signing key is derived from the value commitment randomness of
  the bundle. The party that creates the proofs already knows that
  randomness. No observer and no recipient knows it.
* The binding signing key is the discrete logarithm of a group element that
  anyone can compute from the transaction. Giving it to another party reveals
  nothing about notes or addresses.
* The binding signature is made last in any case.

The restriction is a consensus rule and not a recommendation, so that every
transaction that uses variant 1 with a shielded bundle has the same form. With
a recommendation, two forms would appear on the block chain, and the form
would reveal something about the wallet that produced the transaction.

## Threshold signing with FROST

This section describes ZIP 312 [^zip-0312] as revised by two open proposals.
[^zip-0312-pr895] [^zip-0312-pr1459]

Variant 1 needs no change to the signing protocol. The randomizer is derived
from the signing commitments and not from the message. The variant 1 digest
commits to every randomized validating key, as the variant 0 digest does, so
the Coordinator still completes the first round of every session before it
derives a randomizer.

Variant 1 removes one cause of failed sessions. With variant 0, a session that
does not finish before the expiry height, or before a network upgrade
activates, starts again with new nonces. New signing commitments give a new
randomizer and a new randomized validating key, so the transaction and its
proofs are built again. With variant 1, a session can finish at any time.

Variant 1 also changes what an approval by a threshold of participants means:

* The approval has no time limit. The Coordinator can keep the aggregated
  signatures and broadcast the transaction at any later time. Only another
  signing session, which spends one of the inputs, cancels the approval.
* Each participant in the session can complete the transaction. The
  Coordinator sends each participant the openings of the value commitments, so
  that the participant can check the values that it authorizes. From them the
  participant can compute every binding signing key. Once the transaction has
  been broadcast, its spend authorization signatures and proofs are public.
  Any one participant can then complete it again after it expires, or on
  another consensus branch on which its anchor is valid. Each participant also
  holds the full viewing key and knows the randomizers, so it can create new
  proofs where the anchor is not valid.

A threshold of participants is therefore still required to authorize the
effects of a transaction. It is not required to choose when, or on which
consensus branch, an authorized transaction is mined. [Open issues] lists the
changes that ZIP 312 needs.

## Rationale for permitting transparent-only transactions

A transaction with no shielded bundle has no binding signature. If all of its
transparent inputs use variant 1, any party can change its consensus branch ID
and expiry height. This draft permits such transactions because offline
signing is common for transparent funds. [Open issues] lists stronger
alternatives.

A signer that holds the key for one transparent input at the time of
completion can avoid this property: it signs that input with variant 0 at
that time.

## Rationale for the completion requirements

The requirements in [Requirements for completing a transaction] give a
completed transaction the consensus branch ID, expiry height, and anchors of a
transaction that is signed at the same moment. An observer cannot distinguish
the two by those fields.

The recommendation to use variant 1 for every transaction that contains a
shielded bundle puts transactions that are signed and broadcast immediately
into the same set. For those transactions the cost is small, because the
binding signatures still commit to both fields. The recommendation excludes
transactions with no shielded bundle, where no signature would commit to
them.


# Deployment

This ZIP has not been scheduled for deployment. It depends on the v7
transaction format [^zip-0248] and can activate in the network upgrade that
activates that format, or in a later one. Before this ZIP activates, variant 1
is not a defined sighash variant, and a transaction that uses it is invalid.


# Reference implementation

None yet.


# Open issues

* **Transparent-only transactions.** Should every v7 transaction be required
  to contain at least one variant 0 signature? That rule would make every v7
  transaction identifier non-malleable by parties without key material. It
  would also prevent deferred broadcast of a transaction that has a single
  signer and no shielded bundle. A narrower alternative defines variant 1 for
  transparent inputs only in transactions that contain a shielded bundle.
* **Rejection of undefined variants.** ZIP 248 describes the set of sighash
  variants as closed, but states no consensus rule that rejects an undefined
  `sighashVariant` or a `sighashInfo` of the wrong length. This ZIP states
  that rule for the signatures that it covers. The general rule belongs in
  ZIP 248.
* **Variant registry.** ZIP 248 has no registry for sighash variants. The
  number 1 is provisional until the ZIP Editors confirm it.
* **Choice of transaction format.** ZIP 248 recommends that a wallet use the
  oldest transaction format that supports the features a transaction
  requires. Until v7 transactions are common, the use of the v7 format
  together with variant 1 can therefore suggest deferred broadcast.
* **Partially created transactions.** ZIP 374 [^zip-0374] needs fields that
  record the sighash variant of each signature, and needs to say which role
  sets the consensus branch ID and the expiry height.
* **Threshold signing.** ZIP 312 defines the message of a signing session as
  the SIGHASH transaction hash. [^zip-0312] For a v7 transaction it needs to
  say that the message is the digest for the sighash variant of the signature,
  and that each participant checks which variant it is asked to sign. Its
  proposed revision says that the sessions of one transaction sign the same
  message. [^zip-0312-pr1459] That does not hold for a v7 transaction, because
  ZIP 248 puts the index of the spend in each digest. Its threat model needs
  to say that an approval made with variant 1 has no time limit, and which
  parties can complete the transaction. It is open whether a participant could
  check the values that it authorizes without the openings of the value
  commitments, so that only the Coordinator could complete the transaction.
* **Test vectors.** Test vectors for the variant 1 signature digest are
  needed. They should show that the digest is unchanged when
  `nConsensusBranchId` or `nExpiryHeight` changes, that it changes when any
  other effecting data changes, and that it differs from the variant 0 digest
  of the same transaction.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2026.9.1 [NU7] or later](protocol/protocol.pdf)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^protocol-transactions]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 3.4: Transactions and Treestates](protocol/protocol.pdf#transactions)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-sighash]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 4.10: SIGHASH Transaction Hashing](protocol/protocol.pdf#sighash)

[^protocol-saplingbalance]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 4.13: Balance and Binding Signature (Sapling)](protocol/protocol.pdf#saplingbalance)

[^protocol-orchardbalance]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 4.14: Balance and Binding Signature (Orchard)](protocol/protocol.pdf#orchardbalance)

[^protocol-spendstatement]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 4.18.2: Spend Statement (Sapling)](protocol/protocol.pdf#spendstatement)

[^protocol-actionstatement]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 4.18.4: Action Statement (Orchard)](protocol/protocol.pdf#actionstatement)

[^protocol-txnconsensus]: [Zcash Protocol Specification, Version 2026.9.1 [NU7]. Section 7.1.2: Transaction Consensus Rules](protocol/protocol.pdf#txnconsensus)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0203]: [ZIP 203: Transaction Expiry](zip-0203.rst)

[^zip-0229]: [ZIP 229: Version 6 Transaction Format](zip-0229.md)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^zip-0248]: [ZIP 248: Extensible Transaction Format](zip-0248.rst)

[^zip-0312]: [ZIP 312: FROST for Spend Authorization Multisignatures](zip-0312.rst)

[^zip-0312-pr895]: [ZIP 312: Specify key generation, change randomizer handling (zcash/zips pull request 895)](https://github.com/zcash/zips/pull/895)

[^zip-0312-pr1459]: [ZIP 312: Key generation: DKG base point, recovery data, several spends, clarifications (zcash/zips pull request 1459)](https://github.com/zcash/zips/pull/1459)

[^zip-0318]: [ZIP 318: Orchard to Ironwood Migration](zip-0318.md)

[^zip-0374]: [ZIP 374: Partially Created Zcash Transaction Format](zip-0374.md)
