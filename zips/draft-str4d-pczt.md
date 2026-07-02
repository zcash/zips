    ZIP: Unassigned
    Title: Partially Created Zcash Transaction Format
    Owners: Jack Grigg <jack@electriccoin.co>
    Credits: Daira-Emma Hopwood
             Kris Nuttycombe
             Ava Chow
    Status: [Revision 0] Draft
    Category: Standards / Wallet
    Created: 2024-12-09
    License: MIT (and BSD-2-Clause for paragraphs from BIP 174 and BIP 370)
    Discussions-To: <https://github.com/zcash/zips/issues/693>
    Pull-Request: <https://github.com/zcash/zips/pull/1063>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be
interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in
all capitals.

`I2LEOSP_\ell(k)` is the byte sequence $S$ of length $\ell/8$ representing in
little-endian order the integer $k$ in range $\{ 0\,..\, 2^\ell - 1 \}$.

In structures, a bare type `T` (e.g. `u32` for an unsigned 32-bit integer) is
always present and always has a value. `Option<T>` is an optional value; if it
is not set, a sentinel `None` is present instead.

`(A, B)` is a sequence of 2 elements, first type `A`, second type `B`.

`[T; N]` is a length-`N` sequence of elements of type `T` (such as an array in
Rust).

`List<T>` is a variable-length sequence of elements of type `T` (such as
`Vec<T>` in Rust).

`Map<K, V>` is a variable-length key-value map (such as `Map<K, V>` in Rust).

`Enum { A, B, ... }` is a tagged enumeration; a value of this type is exactly one
of the listed variants, identified by a discriminant assigned in listed order
starting from 0.

`UTF8String` is a variable-length human-readable string encoded with UTF-8.


# Abstract

This ZIP proposes a binary format for transactions that are in the process of
being created: it carries the information necessary for each participant in
the process — constructing inputs and outputs, computing zero-knowledge
proofs, producing signatures, and assembling the final transaction — to
perform its step, and holds the accumulated proofs and signatures while the
set is incomplete. Participants such as signers can be offline, as all
necessary information is provided in the format. Two versions of the format
are specified: v1, supporting the creation of v5 transactions; and v2,
supporting the creation of v5 and v6 transactions, including v6 workflows in
which a transaction is fully signed before its anchors, Merkle witnesses, and
proofs are known.


# Motivation

Creating a Zcash transaction is not a single-step, single-party operation. In
practice the logical steps of transaction creation — assembling inputs and
outputs, computing zero-knowledge proofs, authorizing spends, and serializing
the result — are frequently performed by distinct entities, on distinct devices,
at distinct times:

* **Offline and hardware signers.** A signing device typically holds spending
  key material but has limited computational and communication capacity. It
  cannot compute Halo 2 or Groth16 proofs, and may not be able to hold an entire
  transaction's worth of data in memory. It needs a format that carries exactly
  the information required to verify what is being authorized and to produce
  signatures, with everything else elidable.

* **Proof delegation.** The prover for a shielded spend requires the note's
  private data and full viewing key, but does not require any spending key
  material. Wallets on constrained devices can therefore delegate proving to a
  more capable device, if there is a standard way to hand over exactly the data
  the prover needs and to receive back the proof.

* **Multiparty transactions.** Threshold signing (for example FROST [^frost]),
  transparent multisig [^zip-0048], and transactions with inputs contributed by
  multiple parties all require a partially created transaction to be passed
  among participants, accumulating contributions that were produced in parallel,
  and merged deterministically.

* **Pre-authorization and deferred proving.** From the v6 transaction format
  onward [^zip-0229], the anchors of the Sapling, Orchard, and Ironwood
  components are authorizing data: signatures do not commit to them, and Merkle
  witnesses never appear in the final transaction. A transaction can therefore
  be fully authorized by its signers before the anchor is chosen, with witnesses
  computed and proofs produced later — including for transactions that spend
  Orchard-protocol notes created by a parent transaction that has not yet been
  mined. Workflows such as the scheduled Orchard-to-Ironwood migration
  [^draft-schell-ironwood-migration] use this to obtain a user's authorization
  for a chain of transactions in a single signing session, and to re-anchor and
  prove each transaction at its broadcast time. A partial-transaction format
  must be able to represent these intermediate states durably, potentially for
  days.

Bitcoin addressed the analogous problems with the Partially Signed Bitcoin
Transaction (PSBT) format, defined in BIP 174 [^bip-0174] and revised in BIP 370
[^bip-0370]. PSBTs cannot be used directly for Zcash: they have no
representation for shielded inputs and outputs, no notion of proofs as distinct
from signatures, and their key-value encoding tolerates unknown fields in a way
that is undesirable for signers that must understand everything they authorize.
This ZIP defines the Zcash equivalent, reusing the PSBT role structure and its
transparent-input semantics so that codebases which already support PSBTs can
integrate PCZTs with minimal changes.


# Privacy Implications

A PCZT necessarily contains strictly more information than the transaction that
is extracted from it. In particular, a PCZT may carry, for each shielded spend
or output: the counterparty address, the value, the note randomness, the value
commitment randomness (which opens the value commitment), the full viewing key
of the account spending a note, ZIP 32 derivation paths, the `ock` value (which
opens `out_ciphertext`), and user-facing address strings.

Anyone who receives a copy of a PCZT at a given stage of its lifecycle learns
all of the information present at that stage. Consequently:

* Participants SHOULD send a PCZT only to entities that are required for the
  remaining roles, and SHOULD use the Redactor role to remove fields that
  subsequent entities do not need.

* Delegating the Prover role reveals the private data of the notes being spent
  or created (but not spending authority) to the prover. Users who consider
  their proving delegate untrusted should treat it as learning the transaction's
  full contents.

* The redaction guidance attached to individual fields below ("this can be
  redacted") identifies the points in the lifecycle after which each sensitive
  field is no longer needed.

* Long-lived PCZTs (for example, pre-authorized transactions awaiting proving
  and broadcast) extend the window during which this information exists outside
  the wallet's normal storage. Wallets SHOULD protect stored PCZTs as they would
  protect their own note databases.

Once the final transaction is extracted, none of this additional information is
present in it; the on-chain privacy properties of the transaction itself are
unchanged.


# Requirements

The format must be able to represent a v5 or v6 transaction at every
intermediate state of its creation, across the role separations described
above; in particular, each of the following must be independently performable
by distinct entities, in an order constrained only by data dependencies:
adding inputs and outputs, deciding that the input/output set is final,
attaching key-path and other lookup metadata, computing proofs, producing
signatures, merging parallel contributions, and extracting the final
transaction.

The format must not require spending key material to be present. (Spending keys
for dummy spends, which authorize nothing of value, are the one exception, and
must be removable before signers see the PCZT.)

Signers must be able to determine, from the PCZT alone, exactly what they are
authorizing: amounts, recipients, and the correspondence between the fields
they sign over and the values shown to the user. It must be possible to remove
data that a given signer does not need before the PCZT is sent to it.

Merging two PCZTs derived from the same transaction must be deterministic, and
must fail loudly on any conflict rather than silently discarding data.

For v6 transactions, the format must support pre-authorization: signatures can
be produced while the anchors, Merkle witnesses, and proofs are absent, with
those fields supplied later without invalidating the signatures. [^zip-0229]

The encoding must be compact enough for memory-constrained signing devices, and
must be strictly versioned: an implementation must never misinterpret data
produced under a different version of this specification.


# Specification

A PCZT consists of a versioned binary encoding (defined in the "Encoding"
section) of a structured set of fields (defined in the "Structure" section).
The fields are grouped per payment protocol, and are populated and consumed by
entities acting in well-defined roles (defined in the "Roles" section), each of
which advances the PCZT towards a complete transaction. The lifecycle of a
transaction created via PCZTs is:

1. A Creator initializes the PCZT with global transaction fields.
2. Constructors add transparent inputs and outputs, shielded spends and
   outputs, and (for Orchard-protocol bundles) the actions containing them.
3. An IO Finalizer declares the input/output set complete, computes the binding
   signature keys, and signs any dummy spends.
4. Updaters attach information needed by later roles (key derivation paths,
   full viewing keys, Merkle witnesses, anchors).
5. Provers attach zero-knowledge proofs; Signers attach signatures. From the v6
   transaction format onward these two roles are fully independent and may run
   in either order or in parallel.
6. Combiners merge PCZTs processed in parallel by different entities;
   Redactors remove fields that later entities do not need.
7. A Spend Finalizer assembles script signatures for transparent inputs, and a
   Transaction Extractor produces (and verifies) the final transaction.

PCZTs do not support Sprout, and cannot be used to create v4 or earlier
transactions. (The v4 transaction format predates the ZIP 244 [^zip-0244]
transaction digest algorithm; several of the role separations specified here,
in particular the independence of proving from signing, do not hold for it.)

## Versioning

The PCZT format evolves via revisions to this ZIP. Implementors of this ZIP are
advised to review it regularly for new revisions (at least once per Network
Upgrade).

While evolution of the PCZT format is expected to be gradual, newer versions MAY
change anything about the format (e.g. adding or removing fields, or using a
different encoding scheme). Fields that are only present in a specific PCZT
version will be annotated with a version (or version range, or set of versions)
below; any non-annotated field is present in all PCZT versions.

The following versions are currently specified:

- v1
  - Supports creation of v5 transactions [^zip-0225].
- v2
  - Supports creation of v5 transactions [^zip-0225] and v6 transactions
    [^zip-0229].
  - Adds an `IronwoodBundle` carrying the *Ironwood-pool* component of a v6
    transaction.
  - Adds a `note_version` field to the Orchard-protocol bundles, so that a
    bundle can carry notes using the ZIP 2005 [^zip-2005] quantum-recoverable
    note plaintext format.
  - Makes the shielded bundle anchors optional, so that (for v6 transactions)
    a PCZT can be signed before its anchors are chosen, and re-anchored
    without invalidating signatures.
  - Omits canonically-empty bundles from the encoding, reducing the size of
    the byte streams exchanged with constrained signing devices.

A PCZT version does not pin a transaction version: a v2 PCZT may carry either
a v5 or a v6 transaction, subject to the per-field rules below. A v1 PCZT can
only carry a v5 transaction.

## Encoding

The PCZT encoding is an 8-byte header followed by a version-specific encoding:

    [0x50, 0x43, 0x5a, 0x54] || I2LEOSP_32(version) || VERSION_SPECIFIC_ENCODING

- The first 4 bytes are magic bytes: the ASCII encoding of the string "PCZT".
- The next 4 bytes are the little-endian encoding of the version.
- The remaining bytes should be parsed according to the version.

If a parser encounters a version number it does not recognise, it MUST NOT parse
the remainder of the data, and should instead return an error indicating that
this ZIP should be reviewed for new versions.

Binary PCZT files should use the `.pczt` file extension.

### v1 Encoding

Version 1 PCZTs are encoded using the Postcard Wire Format [^postcard]. The
schema for the encoding is canonically defined in the `pczt` Rust crate
[^pczt-rust]. Its nested structure is reproduced below for convenience, using
the struct names from the "Structure" part of the specification; fields within
each struct are encoded in the order they appear in the ZIP.
```
PCZT
- Global
  - fields...
- TransparentBundle
  - List<TransparentInput>
    - fields...
  - List<TransparentOutput>
    - fields...
- SaplingBundle
  - List<SaplingSpend>
    - fields...
  - List<SaplingOutput>
    - fields...
  - fields...
- OrchardBundle
  - List<OrchardAction>
    - cv_net
    - OrchardSpend
      - fields...
    - OrchardOutput
      - fields...
    - rcv
  - fields...
```

Fields annotated below as present only in v2 PCZTs are absent from the v1
encoding entirely (they are not encoded as `None`). A v1 PCZT can represent
only a subset of the states representable in a v2 PCZT; serializing to the v1
encoding MUST fail if:

- `Global.tx_version` is not 5;
- the `IronwoodBundle` is not the canonical empty bundle (see the v2 Encoding
  section);
- `OrchardBundle.note_version` is not `V2`; or
- any bundle anchor that would be required before signing a v5 transaction is
  absent.

### v2 Encoding

Version 2 PCZTs are likewise encoded using the Postcard Wire Format
[^postcard], with the schema canonically defined in the `pczt` Rust crate
[^pczt-rust]. The v2 encoding differs from the v1 encoding as follows:

```
PCZT
- Global
  - fields...
- Option<TransparentBundle>
- Option<SaplingBundle>
- Option<OrchardBundle>
- Option<IronwoodBundle>
```

- Each bundle is wrapped in an `Option`. A bundle that is exactly equal to the
  **canonical empty bundle** for its slot MUST be encoded as `None`, and a
  parser encountering `None` MUST reconstruct exactly the canonical empty
  bundle, so that re-serialization round-trips and copies of a PCZT that take
  different serialization paths continue to be combinable. A bundle that
  differs from the canonical empty bundle in any field (including its `flags`,
  `note_version`, or `anchor`) MUST be encoded as `Some`.

  The canonical empty bundles are:

  - `TransparentBundle`: empty `inputs` and `outputs` lists.
  - `SaplingBundle`: empty `spends` and `outputs` lists, `value_sum = 0`,
    `anchor = None`, `bsk = None`.
  - `OrchardBundle`: empty `actions` list, `flags = 0b00000011` (spends and
    outputs enabled), `value_sum = (0, false)`, `anchor = None`,
    `note_version = V2`, `zkproof = None`, `bsk = None`.
  - `IronwoodBundle`: empty `actions` list, `flags = 0b00000111` (spends,
    outputs, and cross-address transfers enabled), `value_sum = (0, false)`,
    `anchor = None`, `note_version = V3`, `zkproof = None`, `bsk = None`.

- The `IronwoodBundle` slot is new; it has the same structure as
  `OrchardBundle` (see the `IronwoodBundle` section below).

- The `OrchardBundle` and `IronwoodBundle` structures gain a `note_version`
  field, encoded after `anchor`.

- The `anchor` field of the `SaplingBundle`, `OrchardBundle`, and
  `IronwoodBundle` structures is `Option<[u8; 32]>` rather than `[u8; 32]`.

## Structure

A PCZT is comprised of several top-level structures, that map to equivalent
regions of a Zcash transaction:
- `Global`: fields that are relevant to the transaction as a whole.
- `TransparentBundle`: fields relevant to the transparent protocol.
- `SaplingBundle`: fields relevant to the Sapling protocol.
- `OrchardBundle`: fields relevant to the *Orchard-pool* component of the
  Orchard protocol.
- `IronwoodBundle` (PCZT v2): fields relevant to the *Ironwood-pool* component
  of the Orchard protocol [^zip-0229].

Each structure in turn contains a combination of:
- Transaction effecting data: required fields that are part of the final
  transaction, and are always present in the PCZT.
- Transaction authorizing data: fields that are initially empty, and are filled
  in as the PCZT is processed.
- Context data: information committed to by (or relevant to) the transaction
  effecting data, that enables various Roles to be performed.

The bundle substructures are not logically optional. This is because a PCZT
does not always contain a semantically-valid transaction, and there may be
phases where we need to store protocol-specific metadata before it has been
determined whether there are protocol-specific inputs or outputs. (The v2
*encoding* omits bundles that exactly equal their canonical empty values, but
a parser reconstructs those values, so every PCZT logically contains all of
the bundle substructures.)

### `Global`

The `Global` struct has the following fields:

- `tx_version: u32`

  The version of the transaction being created.

  - This is set by the Creator.
  - This is checked by the Constructor before adding inputs or outputs, to
    confirm that the transaction version will support the payment protocol for
    those inputs or outputs.
  - PCZT version 1: MUST be 5.
  - PCZT version 2: MUST be 5 or 6.

- `version_group_id: u32`

  The version group ID of the transaction being created.

  This MUST be consistent with `tx_version` [^zip-0225] [^zip-0229].

- `consensus_branch_id: u32`

  The consensus branch ID for the chain in which this transaction will be mined.

  Non-optional because this commits to the set of consensus rules that will
  apply to the transaction; differences therein can affect every role.

  If `tx_version` is 6, this MUST correspond to a network upgrade at which the
  v6 transaction format is supported (NU6.3 or later) [^zip-0229].

- `fallback_lock_time: Option<u32>`

  The transaction locktime to use if no inputs specify a required locktime.

  - This is set by the Creator.
  - If omitted, the fallback locktime is assumed to be 0.

- `expiry_height: u32`

  The ZIP 203 [^zip-0203] expiry height to use.

- `coin_type: u32`

  The SLIP 44 [^slip-0044] coin type, indicating the network for which this
  transaction is being constructed.

  This is technically information that could be determined indirectly from the
  `consensus_branch_id` (or from BIP 44 [^bip-0044] or ZIP 32 [^zip-0032] paths
  added by Updaters) but is included explicitly to enable easy identification.
  Note that this field is not included in the transaction and has no consensus
  effect (`consensus_branch_id` fills that role).

  - This is set by the Creator.
  - Roles that encode network-specific information (for example, derivation paths
    for key identification) should check against this field for correctness.

- `tx_modifiable: u8`

  A bitfield for various transaction modification flags.

  - Bit 0 is the Transparent Inputs Modifiable Flag and indicates whether
    transparent inputs can be modified.
    - This is set to `true` by the Creator.
    - This is checked by the Constructor before adding transparent inputs, and
      may be set to `false` by the Constructor.
    - This is set to `false` by the IO Finalizer if there are shielded spends or
      outputs.
    - This is set to `false` by a Signer that adds a signature that does not use
      `SIGHASH_ANYONECANPAY` (which includes all shielded signatures).
    - The Combiner merges this bit towards `false`.
  - Bit 1 is the Transparent Outputs Modifiable Flag and indicates whether
    transparent outputs can be modified.
    - This is set to `true` by the Creator.
    - This is checked by the Constructor before adding transparent outputs, and
      may be set to `false` by the Constructor.
    - This is set to `false` by the IO Finalizer if there are shielded spends or
      outputs.
    - This is set to `false` by a Signer that adds a signature that does not use
      `SIGHASH_NONE` (which includes all shielded signatures).
    - The Combiner merges this bit towards `false`.
  - Bit 2 is the Has `SIGHASH_SINGLE` Flag and indicates whether the transaction
    has a `SIGHASH_SINGLE` transparent signature who's input and output pairing
    must be preserved.
    - This is set to `false` by the Creator.
    - This is updated by a Constructor.
    - This is set to `true` by a Signer that adds a signature that uses
      `SIGHASH_SINGLE`.
    - This essentially indicates that the Constructor must iterate the
      transparent inputs to determine whether and how to add a transparent
      input.
    - The Combiner merges this bit towards `true`.
  - Bits 3-6 MUST be 0 for version 1 PCZTs.
  - Bit 7 is the Shielded Modifiable Flag and indicates whether shielded spends
    or outputs can be modified.
    - This is set to `true` by the Creator.
    - This is checked by the Constructor before adding shielded spends or
      outputs, and may be set to `false` by the Constructor.
    - This is set to `false` by the IO Finalizer if there are shielded spends or
      outputs.
    - This is set to `false` by every Signer (as all signatures commit to all
      shielded spends and outputs).
    - The Combiner merges this bit towards `false`.

- `proprietary: Map<UTF8String, List<u8>>`

  Proprietary fields related to the overall transaction. See "Proprietary Use
  fields" below.

### `TransparentBundle`

The  `TransparentBundle` struct has the following fields:

- `inputs: List<TransparentInput>`

  The transparent coins that will be spent by this transaction.

- `outputs: List<TransparentOutput>`

  The transparent coins that will be created by this transaction.

#### `TransparentInput`

The `TransparentInput` struct has the following fields:

- `prevout_txid: [u8; 32]`

  This is filled in by the Constructor when adding an input.

- `prevout_index: u32`

  This is filled in by the Constructor when adding an input.

- `sequence: Option<u32>`

  The sequence number of this input.

  - This is set by the Constructor.
  - If omitted, the sequence number is assumed to be the final sequence number
    (`0xffffffff`).

- `required_time_lock_time: Option<u32>`

  The minimum Unix timstamp that this input requires to be set as the
  transaction's lock time.

  - This is set by the Constructor.
  - This MUST be greater than or equal to 500000000.

- `required_height_lock_time: Option<u32>`

  The minimum block height that this input requires to be set as the
  transaction's lock time.

  - This is set by the Constructor.
  - This MUST be greater than 0 and less than 500000000.

- `script_sig: Option<List<u8>>`

  A satisfying witness for the `script_pubkey` of the input being spent.

  This is set by the Spend Finalizer.

- `value: u64`

  This is required by the Transaction Extractor, to derive the shielded sighash
  needed for computing the binding signatures.

- `script_pubkey: List<u8>`

  This is required by the Transaction Extractor, to derive the shielded sighash
  needed for computing the binding signatures.

- `redeem_script: Option<List<u8>>`

  The script required to spend this output, if it is P2SH.

  Set to `None` if this is a P2PKH output.

- `partial_signatures: Map<[u8; 33], List<u8>>`

  A map from a pubkey to a signature created by it.

  - Each pubkey should appear in `script_pubkey` or `redeem_script`.
  - Each entry is set by a Signer, and should contain an ECDSA signature that is
    valid under the corresponding pubkey.
  - These are required by the Spend Finalizer to assemble `script_sig`.

- `sighash_type: u8`

  The sighash type to be used for this input.

  - Signers MUST use this sighash type to produce their signatures. Signers that
    cannot produce signatures for this sighash type MUST NOT provide a signature.
  - Spend Finalizers MUST fail to finalize inputs which have signatures not
    matching this sighash type.

- `bip32_derivation: Map<[u8; 33], Zip32Derivation>`

  A map from a pubkey to the BIP 32 derivation path at which its corresponding
  spending key can be found.

  - The pubkeys should appear in `script_pubkey` or `redeem_script`.
  - Each entry is set by an Updater.
  - Individual entries may be required by a Signer.
  - It is not required that the map include entries for all of the used pubkeys.
    In particular, it is not possible to include entries for non-BIP-32 pubkeys.

- `ripemd160_preimages: Map<[u8; 20], List<u8>>`

  Mappings of the form `key = RIPEMD160(value)`.

  - These may be used by the Signer to inspect parts of `script_pubkey` or
    `redeem_script`.

- `sha256_preimages: Map<[u8; 32], List<u8>>`

  Mappings of the form `key = SHA256(value)`.

  - These may be used by the Signer to inspect parts of `script_pubkey` or
    `redeem_script`.

- `hash160_preimages: Map<[u8; 20], List<u8>>`

  Mappings of the form `key = RIPEMD160(SHA256(value))`.

  - These may be used by the Signer to inspect parts of `script_pubkey` or
    `redeem_script`.

- `hash256_preimages: Map<[u8; 32], List<u8>>`

  Mappings of the form `key = SHA256(SHA256(value))`.

  - These may be used by the Signer to inspect parts of `script_pubkey` or
    `redeem_script`.

- `proprietary: Map<UTF8String, List<u8>>`

  Proprietary fields related to the coin being spent. See "Proprietary Use
  fields" below.

#### `TransparentOutput`

The `TransparentOutput` struct has the following fields:

- `value: u64`

  This is filled in by the Constructor when adding an output.

- `script_pubkey: List<u8>`

  This is filled in by the Constructor when adding an output.

- `redeem_script: Option<List<u8>>`

  The script required to spend this output, if it is P2SH.

  Set to `None` if this is a P2PKH output.

- `bip32_derivation: Map<[u8; 33], Zip32Derivation>`

  A map from a pubkey to the BIP 32 derivation path at which its corresponding
  spending key can be found.

  - The pubkeys should appear in `script_pubkey` or `redeem_script`.
  - Each entry is set by an Updater.
  - Individual entries may be required by a Signer.
  - It is not required that the map include entries for all of the used pubkeys.
    In particular, it is not possible to include entries for non-BIP-32 pubkeys.

- `user_address: Option<UTF8String>`

  The user-facing address to which this output is being sent, if any.

  - This is set by an Updater.
  - Signers MUST parse this address (if present) and confirm that it contains
    `recipient` (either directly, or e.g. as a receiver within a Unified
    Address).

- `proprietary: Map<UTF8String, List<u8>>`

  Proprietary fields related to the coin being created. See "Proprietary Use
  fields" below.

### `SaplingBundle`

The  `SaplingBundle` struct has the following fields:

- `spends: List<SaplingSpend>`

  The Sapling notes that will be spent by this transaction.

- `outputs: List<SaplingOutput>`

  The Sapling notes that will be created by this transaction.

- `value_sum: i128`

  The net value of Sapling spends minus outputs.

  This is initialized by the Creator, and updated by the Constructor as spends
  or outputs are added to the PCZT. It enables per-spend and per-output values
  to be redacted from the PCZT after they are no longer necessary.

- `anchor: [u8; 32]` (PCZT v1) / `anchor: Option<[u8; 32]>` (PCZT v2)

  The Sapling anchor for this transaction.

  - If `tx_version` is 5, this MUST be set by the Creator, and MUST NOT
    subsequently change: the v5 signature hash commits to the anchor, so
    changing it would invalidate signatures.
  - If `tx_version` is 6, this is set by the Creator or by an Updater, and MAY
    be replaced by an Updater at any time before proving (see "Anchors and
    pre-authorization"). It MUST be set before the Prover runs.

- `bsk: Option<[u8; 32]>`

  The Sapling binding signature signing key.

  - This is `None` until it is set by the IO Finalizer.
  - The Transaction Extractor uses this to produce the binding signature.

#### `SaplingSpend`

The  `SaplingSpend` struct has the following fields:

- `cv: [u8; 32]`

  This is filled in by the Constructor when adding a spend.

- `nullifier: [u8; 32]`

  This is filled in by the Constructor when adding a spend.

- `rk: [u8; 32]`

  This is filled in by the Constructor when adding a spend.

- `zkproof: Option<[u8; 192]>`

  The Sapling Spend proof.

  This is set by the Prover.

- `spend_auth_sig: Option<[u8; 64]>`

  The spend authorization signature.

  This is set by the Signer.

- `recipient: Option<[u8; 43]>`

  The raw encoding [^protocol-saplingpaymentaddrencoding] of the Sapling payment
  address that received the note being spent.

  - This is set by the Constructor.
  - This is required by the Prover.

- `value: Option<u64>`

  The value of the input being spent.

  This may be used by Signers to verify that the value matches `cv`, and to
  confirm the values and change involved in the transaction.

  This exposes the input value to all participants. For Signers who don't need
  this information, or after signatures have been applied, this can be redacted.

- `rcm: Option<[u8; 32]>`

  The note commitment randomness.

  - This is set by the Constructor. It MUST NOT be set if the note has an `rseed`
    (i.e. was created after ZIP 212 [^zip-0212] activation).
  - The Prover requires either this or `rseed`.

- `rseed: Option<[u8; 32]>`

  The seed randomness for the note being spent.

  - This is set by the Constructor. It MUST NOT be set if the note has no
    `rseed` (i.e. was created before ZIP 212 [^zip-0212] activation).
  - The Prover requires either this or `rcm`.

- `rcv: Option<[u8; 32]>`

  The value commitment randomness.

  - This is set by the Constructor.
  - The IO Finalizer compresses it into `bsk`.
  - This is required by the Prover.
  - This may be used by Signers to verify that the value correctly matches `cv`.

  This opens `cv` for all participants. For Signers who don't need this
  information, or after proofs / signatures have been applied, this can be
  redacted.

- `proof_generation_key: Option<([u8; 32], [u8; 32])>`

  The proof generation key `(ak, nsk)` corresponding to the recipient that
  received the note being spent.

  - This is set by the Updater.
  - This is required by the Prover.

- `witness: Option<(u32, [[u8; 32]; 32])>`

  A witness from the note to the bundle's anchor.

  - This is set by the Updater.
  - This is required by the Prover.

- `alpha: Option<[u8; 32]>`

  The spend authorization randomizer.

  - This is chosen by the Constructor.
  - This is required by the Signer for creating `spend_auth_sig`, and may be
    used to validate `rk`.
  - After `zkproof` / `spend_auth_sig` has been set, this can be redacted.

- `zip32_derivation: Option<Zip32Derivation>`

  The ZIP 32 derivation path at which the spending key can be found for the note
  being spent.

- `dummy_ask: Option<[u8; 32]>`

  The spend authorizing key for this spent note, if it is a dummy note.

  - This is chosen by the Constructor.
  - This is required by the IO Finalizer, and is cleared by it once used.
  - Signers MUST reject PCZTs that contain `dummy_ask` values.

- `proprietary: Map<UTF8String, List<u8>>`

  Proprietary fields related to the note being spent. See "Proprietary Use
  fields" below.

#### `SaplingOutput`

The  `SaplingOutput` struct has the following fields:

- `cv: [u8; 32]`

  This is filled in by the Constructor when adding an output.

- `cmu: [u8; 32]`

  This is filled in by the Constructor when adding an output.

- `ephemeral_key: [u8; 32]`

  This is filled in by the Constructor when adding an output.

- `enc_ciphertext: List<u8>`

  The encrypted note plaintext for the output.

  This is filled in by the Constructor when adding an output.

  Represented as a `List<u8>` because its length depends on the transaction
  version.

  Once we have memo bundles [^zip-0231], we will be able to set memos
  independently of Outputs. For now, the Constructor sets both at the same time.

- `out_ciphertext: List<u8>`

  The encrypted note plaintext for the output.

  This is filled in by the Constructor when adding an output.

  Represented as a `List<u8>` because its length depends on the transaction
  version.

- `zkproof: Option<[u8; 192]>`

  The Sapling Output proof.

  This is set by the Prover.

- `recipient: Option<[u8; 43]>`

  The raw encoding [^protocol-saplingpaymentaddrencoding] of the Sapling payment
  address that will receive the output.

  - This is set by the Constructor.
  - This is required by the Prover.

- `value: Option<u64>`

  The value of the output.

  This may be used by Signers to verify that the value matches `cv`, and to
  confirm the values and change involved in the transaction.

  This exposes the output value to all participants. For Signers who don't need
  this information, or after signatures have been applied, this can be redacted.

- `rseed: Option<[u8; 32]>`

  The seed randomness for the output.

  - This is set by the Constructor.
  - This is required by the Prover, instead of disclosing `shared_secret` to
    them.

- `rcv: Option<[u8; 32]>`

  The value commitment randomness.

  - This is set by the Constructor.
  - The IO Finalizer compresses it into `bsk`.
  - This is required by the Prover.
  - This may be used by Signers to verify that the value correctly matches `cv`.

  This opens `cv` for all participants. For Signers who don't need this
  information, or after proofs / signatures have been applied, this can be
  redacted.

- `ock: Option<[u8; 32]>`

  The `ock` value used to encrypt `out_ciphertext`.

  This enables Signers to verify that `out_ciphertext` is correctly encrypted.

  This may be `None` if the Constructor added the output using an OVK policy of
  "None", to make the output unrecoverable from the chain by the sender.

- `zip32_derivation: Option<Zip32Derivation>`

  The ZIP 32 derivation path at which the spending key can be found for the
  output.

- `user_address: Option<UTF8String>`

  The user-facing address to which this output is being sent, if any.

  - This is set by an Updater.
  - Signers MUST parse this address (if present) and confirm that it contains
    `recipient` (either directly, or e.g. as a receiver within a Unified
    Address).

- `proprietary: Map<UTF8String, List<u8>>`

  Proprietary fields related to the note being created. See "Proprietary Use
  fields" below.

### `OrchardBundle`

The  `OrchardBundle` struct has the following fields:

- `actions: List<OrchardAction>`

  The Orchard actions in this bundle.

  Entries are added by the Constructor, and modified by an Updater, IO
  Finalizer, Signer, Combiner, or Spend Finalizer.

- `flags: u8`

  The flags for the Orchard bundle.

  Contains:
  - `enableSpends` flag (bit 0)
  - `enableOutputs` flag (bit 1)
  - `enableCrossAddress` flag (bit 2) (PCZT v2; MUST be 0 in PCZT v1, and in
    the `OrchardBundle` of any transaction that will be mined under NU6.3 or
    later [^zip-0229] [^zip-0258])
  - Reserved, zeros (bits 3..=7)

  This is set by the Creator. The Constructor MUST only add spends and outputs
  that are consistent with these flags (i.e. are dummies as appropriate; and,
  when `enableCrossAddress` is 0, each action's output is addressed to the
  same protocol-level address as its spend — see "Fabricated same-address
  outputs").

- `value_sum: (u64, bool)`

  The net value of Orchard spends minus outputs.

  This is initialized by the Creator, and updated by the Constructor as spends
  or outputs are added to the PCZT. It enables per-spend and per-output values
  to be redacted from the PCZT after they are no longer necessary.

- `anchor: [u8; 32]` (PCZT v1) / `anchor: Option<[u8; 32]>` (PCZT v2)

  The Orchard anchor for this transaction.

  - If `tx_version` is 5, this MUST be set by the Creator, and MUST NOT
    subsequently change: the v5 signature hash commits to the anchor, so
    changing it would invalidate signatures.
  - If `tx_version` is 6, this is set by the Creator or by an Updater, and MAY
    be replaced by an Updater at any time before proving (see "Anchors and
    pre-authorization"). It MUST be set before the Prover runs.

- `note_version: NoteVersion` (PCZT v2)

  The note plaintext version for notes in this bundle, where `NoteVersion` is
  `Enum { V2, V3 }`:

  - `V2` denotes the ZIP 212 [^zip-0212] note plaintext format (lead byte
    `0x02`).
  - `V3` denotes the ZIP 2005 [^zip-2005] quantum-recoverable note plaintext
    format (lead byte `0x03`).

  Every note in a bundle has the same note version. For an `OrchardBundle`
  this MUST be `V2`; for an `IronwoodBundle` this MUST be `V3`. [^zip-0229]

  In PCZT v1, the note version of the `OrchardBundle` is implicitly `V2`.

- `zkproof: Option<List<u8>>`

  The Orchard bundle proof.

  This is `None` until it is set by the Prover.

  If `tx_version` is 6 and the bundle's `anchor` is replaced after this field
  has been set, this field MUST be cleared (the proof commits to the anchor,
  so it is no longer valid).

- `bsk: Option<[u8; 32]>`

  The Orchard binding signature signing key.

  - This is `None` until it is set by the IO Finalizer.
  - The Transaction Extractor uses this to produce the binding signature.

#### `OrchardAction`

The  `OrchardAction` struct has the following fields:

- `cv_net: [u8; 32]`

  This is filled in by the Constructor when adding an action.

- `spend: OrchardSpend`

  This is filled in by the Constructor when adding an action.

- `output: OrchardOutput`

  This is filled in by the Constructor when adding an action.

- `rcv: Option<[u8; 32]>`

  The value commitment randomness.

  - This is set by the Constructor.
  - The IO Finalizer compresses it into the bsk.
  - This is required by the Prover.
  - This may be used by Signers to verify that the value correctly matches `cv`.

  This opens `cv` for all participants. For Signers who don't need this
  information, or after proofs / signatures have been applied, this can be
  redacted.

##### `OrchardSpend`

The  `OrchardSpend` struct has the following fields:

- `nullifier: [u8; 32]`

  This is filled in by the Constructor when adding a spend.

- `rk: [u8; 32]`

  This is filled in by the Constructor when adding a spend.

- `spend_auth_sig: Option<[u8; 64]>`

  The spend authorization signature.

  This is set by the Signer.

- `recipient: Option<[u8; 43]>`

  The raw encoding [^protocol-orchardpaymentaddrencoding] of the Orchard payment
  address that received the note being spent.

  - This is set by the Constructor.
  - This is required by the Prover.

- `value: Option<u64>`

  The value of the input being spent.

  - This is required by the Prover.
  - This may be used by Signers to verify that the value matches `cv`, and to
    confirm the values and change involved in the transaction.

  This exposes the input value to all participants. For Signers who don't need
  this information, or after signatures have been applied, this can be redacted.

- `rho: Option<[u8; 32]>`

  The rho value for the note being spent.

  - This is set by the Constructor.
  - This is required by the Prover.

- `rseed: Option<[u8; 32]>`

  The seed randomness for the note being spent.

  - This is set by the Constructor.
  - This is required by the Prover.

- `fvk: Option<[u8; 96]>`

  The full viewing key that received the note being spent.

  - This is set by the Updater.
  - This is required by the Prover.

- `witness: Option<(u32, [[u8; 32]; 32])>`

  A witness from the note to the bundle's anchor.

  - This is set by the Updater.
  - This is required by the Prover.
  - If `tx_version` is 6, this MAY be absent when the spend is signed, and
    added later by an Updater — including for a spend of a note that has not
    yet been added to the note commitment tree (see "Anchors and
    pre-authorization"). Signatures do not commit to it.

- `alpha: Option<[u8; 32]>`

  The spend authorization randomizer.

  - This is chosen by the Constructor.
  - This is required by the Signer for creating `spend_auth_sig`, and may be
    used to validate `rk`.
  - After `zkproof` / `spend_auth_sig` has been set, this can be redacted.

- `zip32_derivation: Option<Zip32Derivation>`

  The ZIP 32 derivation path at which the spending key can be found for the note
  being spent.

- `dummy_sk: Option<[u8; 32]>`

  The spending key for this spent note, if it is a dummy note.

  - This is chosen by the Constructor.
  - This is required by the IO Finalizer, and is cleared by it once used.
  - Signers MUST reject PCZTs that contain `dummy_sk` values.

- `proprietary: Map<UTF8String, List<u8>>`

  Proprietary fields related to the note being spent. See "Proprietary Use
  fields" below.

##### `OrchardOutput`

The  `OrchardOutput` struct has the following fields:

- `cmx: [u8; 32]`

  This is filled in by the Constructor when adding an output.

- `ephemeral_key: [u8; 32]`

  This is filled in by the Constructor when adding an output.

- `enc_ciphertext: List<u8>`

  The encrypted note plaintext for the output.

  This is filled in by the Constructor when adding an output.

  Encoded as a `List<u8>` because its length depends on the transaction version.

  Once we have memo bundles [^zip-0231], we will be able to set memos
  independently of Outputs. For now, the Constructor sets both at the same time.

- `out_ciphertext: List<u8>`

  The encrypted note plaintext for the output.

  This is filled in by the Constructor when adding an output.

  Encoded as a `List<u8>` because its length depends on the transaction version.

- `recipient: Option<[u8; 43]>`

  The raw encoding [^protocol-orchardpaymentaddrencoding] of the Orchard payment
  address that will receive the output.

  - This is set by the Constructor.
  - This is required by the Prover.

- `value: Option<u64>`

  The value of the output.

  This may be used by Signers to verify that the value matches `cv`, and to
  confirm the values and change involved in the transaction.

  This exposes the value to all participants. For Signers who don't need this
  information, we can drop the values and compress the rcvs into the bsk global.

- `rseed: Option<[u8; 32]>`

  The seed randomness for the output.

  - This is set by the Constructor.
  - This is required by the Prover, instead of disclosing `shared_secret` to them.

- `ock: Option<[u8; 32]>`

  The `ock` value used to encrypt `out_ciphertext`.

  This enables Signers to verify that `out_ciphertext` is correctly encrypted.

  This may be `None` if the Constructor added the output using an OVK policy of
  "None", to make the output unrecoverable from the chain by the sender.

- `zip32_derivation: Option<Zip32Derivation>`

  The ZIP 32 derivation path at which the spending key can be found for the
  output.

- `user_address: Option<UTF8String>`

  The user-facing address to which this output is being sent, if any.

  - This is set by an Updater.
  - Signers MUST parse this address (if present) and confirm that it contains
    `recipient` (either directly, or e.g. as a receiver within a Unified
    Address).

- `proprietary: Map<UTF8String, List<u8>>`

  Proprietary fields related to the note being created. See "Proprietary Use
  fields" below.

### `IronwoodBundle` (PCZT v2)

The `IronwoodBundle` struct carries the *Ironwood-pool* component of a v6
transaction [^zip-0229]. The *Ironwood pool* is a second value pool of the
Orchard protocol, so the `IronwoodBundle` has exactly the same structure,
field semantics, and role interactions as the `OrchardBundle`, with the
following differences:

- `flags`: the `enableCrossAddress` flag (bit 2) is meaningful and is normally
  1 for an `IronwoodBundle` (cross-address transfers are the usual case in the
  *Ironwood pool*, and are consensus-disabled in the *Orchard pool* from NU6.3
  onward) [^zip-0229] [^zip-0258].
- `anchor` refers to a root of the **Ironwood** note commitment tree, which is
  distinct from the Orchard note commitment tree.
- `note_version` MUST be `V3`: every *Ironwood-pool* output note uses the
  ZIP 2005 [^zip-2005] quantum-recoverable note plaintext format.

An `IronwoodBundle` that is not the canonical empty bundle MUST NOT be present
in a PCZT whose `tx_version` is 5; roles MUST reject such a PCZT.

### Other Internal Structures

#### `Zip32Derivation`

The  `Zip32Derivation` struct has the following fields:

- `seed_fingerprint: [u8; 32]`

  The ZIP 32 seed fingerprint [^zip-0032-seedfp].

- `derivation_path: List<u32>`

  The sequence of indices corresponding to the shielded HD path.

  Indices can be hardened or non-hardened (i.e. the hardened flag bit may be
  set). When used with a Sapling or Orchard spend, the derivation path will
  generally be entirely hardened; when used with a transparent input, the
  derivation path will generally include a non-hardened section matching either
  the BIP 44 [^bip-0044] path, or the path at which ephemeral addresses are
  derived for ZIP 320 [^zip-0320] transactions.

## Interpretation

### Determining Lock Time

The `nLockTime` field of a transaction is determined by inspecting the
`Global.fallback_lock_time` and each `TransparentInput.required_time_locktime`
and `TransparentInput.required_height_locktime` field. If none of the
transparent inputs have a `TransparentInput.required_time_locktime` and
`TransparentInput.required_height_locktime`, then `Global.fallback_lock_time`
must be used. If `Global.fallback_lock_time` is not provided, then it is assumed
to be 0.

If one or more inputs have a `TransparentInput.required_time_locktime` or
`TransparentInput.required_height_locktime`, then the field chosen is the one
which is supported by all of the inputs. This can be determined by looking at
all of the inputs which specify a locktime in either of those fields, and
choosing the field which is present in all of those inputs. Inputs not
specifying a lock time field can take both types of lock times, as can those
that specify both. The lock time chosen is then the maximum value of the chosen
type of lock time.

If a PCZT has both types of locktimes possible because one or more inputs
specify both `TransparentInput.required_time_locktime` and
`TransparentInput.required_height_locktime`, then a locktime determined by
looking at the `TransparentInput.required_height_locktime` fields of the inputs
must be chosen.

### Anchors and pre-authorization

In the v5 transaction format, the Sapling and Orchard anchors are transaction
effecting data: the signature hash commits to them [^zip-0244]. In the v6
transaction format, the anchors of all shielded bundles are authorizing data:
the transaction identifier and signature hash omit them, and they are instead
committed to by the authorizing data commitment [^zip-0229]. Merkle witnesses
never appear in the transaction in either format; they are consumed only by
the proofs, which are themselves authorizing data.

For a PCZT whose `tx_version` is 5:

- Every shielded bundle anchor MUST be set at the time the bundle's first
  spend is added, and MUST NOT change thereafter.

For a PCZT whose `tx_version` is 6 (which requires PCZT v2):

- A shielded bundle anchor MAY be absent until proving. An Updater MAY set an
  absent anchor, and MAY replace a previously set anchor, at any time before
  the Prover runs for that bundle.
- Setting or replacing a bundle's anchor MUST clear any proof fields already
  set in that bundle (`SaplingSpend.zkproof` for the Sapling bundle;
  `OrchardBundle.zkproof` or `IronwoodBundle.zkproof` for the Orchard-protocol
  bundles): proofs commit to the anchor as a circuit public input.
- Signatures (spend authorization signatures and binding signatures) do not
  commit to the anchors or witnesses, so setting or replacing them does not
  invalidate signatures, and Signers MAY sign while they are absent.
- A `SaplingSpend.witness` or `OrchardSpend.witness` MAY likewise be absent
  until proving, and set by an Updater once known.
- When setting an anchor for a bundle in which witnesses are already present,
  or a witness for a bundle whose anchor is already present, the Updater MUST
  verify that each witness's Merkle path roots to the bundle's anchor, and the
  Prover MUST perform the same check before creating a proof.

This enables two workflows that are impossible for v5 transactions:

- **Re-anchoring**: a fully signed transaction can be updated to use a more
  recent anchor at broadcast time (for example, an anchor shared by many
  wallets [^draft-schell-ironwood-migration]), requiring only re-proving. The
  transaction identifier is unchanged by re-anchoring.
- **Spending unmined notes**: every field of a v6 signature hash is computable
  for a transaction that spends an Orchard-protocol note created by a parent
  transaction that has not yet been mined, because Orchard-protocol nullifiers
  depend only on note data (ρ is fixed by the action that created the note),
  not on the note's position in the note commitment tree. Such a transaction
  can be constructed and fully signed before the parent transaction is even
  broadcast, with its witnesses, anchor, and proofs supplied after the parent
  is mined.

Note that the second workflow is not available for Sapling spends even under
the v6 format: a Sapling nullifier depends on the spent note's position in the
note commitment tree, which is unknown until the note is mined. For Sapling,
deferred anchors enable only the re-anchoring workflow.

Fields that remain effecting data — notably `Global.expiry_height`,
`Global.fallback_lock_time`, per-input lock time requirements, and all values —
are committed to by signatures in both formats and can never change after
signing.

### Fabricated same-address outputs (NU6.3)

From NU6.3 activation, every *Orchard-pool* action is required by consensus to
be created with cross-address transfers disabled: the action's output must be
addressed to the same protocol-level address as its spend
[^draft-dairaemma-nu6.3-wallets]. To spend in the *Orchard pool* under this
restriction, a wallet pairs each real spend with a fabricated, zero-valued
output addressed to the spent note's own receiver, and fills that output's
`enc_ciphertext` with random bytes rather than a real encryption (see
[^draft-dairaemma-nu6.3-wallets] for the privacy rationale).

In a PCZT, such a fabricated output still carries its explicit `recipient`,
`value`, and `rseed` fields, but no `user_address`. A Signer encountering an
output whose `value` is zero and whose ciphertext does not decrypt MUST NOT
reject the PCZT on that basis alone; it SHOULD classify the output as a
tolerable dummy output (verifying, if it wishes, that `cmx` is consistent with
the explicit `recipient`, `value`, and `rseed`).

Conversely, an action whose output is real but whose spend carries no
spendable value (for example, in a note-splitting transaction) uses a
fabricated zero-valued spend note addressed to the wallet's own receiver.
Such a spend is a real spend from the Signer's perspective: it has no
`dummy_sk`, and its `spend_auth_sig` MUST be produced through the normal
Signer flow using the spend authorizing key for that receiver's address.
Only fully-dummy actions (fabricated spend *and* fabricated output, at a
common freshly random address) carry `dummy_sk` and are signed by the IO
Finalizer.

### Proprietary Use fields

The following fields of type `Map` are reserved for proprietary use:
- `Global.proprietary`
- `TransparentInput.proprietary`
- `TransparentOutput.proprietary`
- `SaplingSpend.proprietary`
- `SaplingOutput.proprietary`
- `OrchardSpend.proprietary`
- `OrchardOutput.proprietary`

The map keys can be any variable-length string that software can use to identify
whether the particular data in the proprietary maps can be used by it.

The proprietary use maps are for private use by individuals and organizations who
wish to use PCZT in their processes. It is useful when there are additional data
that they need attached to a PCZT but such data are not useful or available for
the general public. The proprietary use maps are not to be used by any public
specification, and there is no expectation that any publicly available software
be able to understand any specific meanings of any keys. These fields MUST be
used for internal processes only.

## Roles

### Creator

> Single entity

The Creator creates the base PCZT with no information about spends or outputs.

The Creator chooses the transaction version and consensus branch ID, and
initializes the global fields and the (empty) bundles. For a v5 transaction,
the Creator sets the shielded bundle anchors; for a v6 transaction, the
Creator MAY leave the anchors unset, to be provided later by an Updater (see
"Anchors and pre-authorization").

### Constructor

The Constructor adds spends and outputs to the PCZT.

Before any input or output may be added, the Constructor MUST check the
`Global.tx_modifiable` field. Transparent inputs may only be added if the
Transparent Inputs Modifiable flag is True. Transparent outputs may only be
added if the Transparent Outputs Modifiable flag is True. Shielded spends or
outputs may only be added if the Shielded Modifiable flag is True.

When adding a shielded spend whose bundle anchor is set, the Constructor MUST
either provide a `witness` whose Merkle path roots to that anchor, or (for
zero-valued notes, whose Merkle paths are not checked by the circuits) any
placeholder witness. When `tx_version` is 6, the Constructor MAY instead add a
spend with no `witness` — including a spend of a note that does not yet exist
in the note commitment tree — leaving the witness to be provided by an Updater
(see "Anchors and pre-authorization"). When `tx_version` is 5, every non-dummy
spend added MUST be of a note that exists in the note commitment tree with a
witness to the bundle's anchor, since the anchor can no longer change.

If a transparent input being added specifies a required time lock, then the
Constructor must iterate through all of the existing transparent inputs and
ensure that the time lock types are compatible. Additionally, if during this
iteration, it finds that any transparent inputs have signatures, it must ensure
that the newly added transparent input does not change the transaction's
locktime. If the newly added transparent input has an incompatible time lock,
then it must not be added. If it changes the transaction's locktime when there
are existing signatures, it must not be added.

If the Has `SIGHASH_SINGLE` Flag is True, then the Constructor must iterate
through the transparent inputs and find those which have signatures that use
`SIGHASH_SINGLE`. The same number of transparent inputs and outputs must be
added before those transparent inputs and their corresponding outputs.

A single entity is likely to be both a Creator and Constructor.

### IO Finalizer

> Anyone can execute

The IO Finalizer declares that no further inputs and outputs can be added to the
transaction by setting the appropriate bits in `Global.tx_modifiable` to 0.

The IO Finalizer also updates:
- `SaplingBundle.bsk` using `SaplingSpend.rcv` and `SaplingOutput.rcv`.
- `OrchardBundle.bsk` (and, in PCZT v2, `IronwoodBundle.bsk`) using
  `OrchardAction.rcv`.

While doing so, it MUST check that each bundle's `value_sum` is consistent
with the value commitments and `rcv` values it is aggregating, and fail
otherwise.

The IO Finalizer then computes the transaction's shielded signature hash, and
uses each `SaplingSpend.dummy_ask` and `OrchardSpend.dummy_sk` to produce the
`spend_auth_sig` for the corresponding dummy spends, clearing the dummy key
fields once used. This ensures that no Signer needs to parse spending key
material from a PCZT.

For a bundle whose `flags` have `enableCrossAddress` set to 0, the IO
Finalizer MUST verify that each action's output `recipient` equals its spend
`recipient` (see "Fabricated same-address outputs"), and fail otherwise.

A single entity is likely to be both a Constructor and an IO Finalizer.

### Updater

> Anyone can contribute

The Updater adds information to the PCZT that it has access to, and that is
necessary for subsequent entities to proceed, such as key paths for signing
spends, full viewing keys and Merkle witnesses for proving, and (for v6
transactions) the shielded bundle anchors.

When setting or replacing a bundle anchor, or setting a witness, the Updater
MUST follow the rules in "Anchors and pre-authorization": anchors of v5
transactions never change; replacing a v6 bundle's anchor clears its proofs;
witnesses of non-zero-valued spends must root to the bundle's anchor whenever
both are present.

A single entity is likely to be both a Constructor and Updater.

### Redactor

> Anyone can execute

The Redactor removes information that is unnecessary for subsequent
entities to proceed.

This can be useful, for example, when creating a transaction that has inputs
from multiple independent Signers; each can receive a PCZT with just the
information they need to sign, but (e.g.) not the `alpha` values for other
Signers.

### Verifier

> Anyone can execute

The Verifier is not a step in the transaction lifecycle, but a way of
inspecting a PCZT and checking the internal consistency of its fields — for
example, that a spend's `nullifier` is consistent with its explicit note data
and `fvk`, that an output's `cmx` is consistent with its explicit `recipient`,
`value`, and `rseed`, or that a bundle satisfies the cross-address restriction.
Signers typically perform a subset of these checks before signing; a separate
Verifier can perform them on behalf of an entity (such as a hardware signer)
that lacks the capacity to do so itself and trusts the Verifier's judgement.

### Prover

> Capability holders can contribute

The Prover needs all private information for a single spend or output.

For Sapling, the Prover requires, per spend: the explicit note data
(`recipient`, `value`, and `rcm` or `rseed`), `rcv`, `proof_generation_key`,
and `witness`; and per output: `recipient`, `value`, `rseed`, and `rcv`. For
the Orchard-protocol bundles, the Prover requires, per action: the spend's
explicit note data (`recipient`, `value`, `rho`, `rseed`), `fvk`, `witness`,
and `alpha`; the output's `recipient`, `value`, and `rseed`; and the action's
`rcv`. In all cases the bundle's `anchor` MUST be set before proving.

Before creating a proof, the Prover MUST verify that the Merkle path in each
non-zero-valued spend's `witness` roots to the bundle's `anchor`, and fail
otherwise. (A proof created from an inconsistent witness/anchor pair would
simply be invalid; checking first surfaces the error at the responsible role.)

In practice, the Updater that adds a given spend or output will either act as
the Prover themselves, or add the necessary data, offload to the Prover, and
then receive back the PCZT with private data stripped and proof added.

Proofs are authorizing data: creating them does not require spending key
material, and (from the v6 transaction format onward, where anchors are also
authorizing data) proving is fully independent of signing and may occur before
it, after it, or in parallel with it.

### Signer

> Capability holders can contribute

The Signer:
- Needs the spend authorization randomizers to create signatures.
- Needs sufficient information to verify that the proof is over the correct
  data, without needing to verify the proof itself.

Signers do not need to sign for all possible input types. For example, a Signer
may choose to only sign Orchard inputs.

Before signing, a Signer:

- MUST reject a PCZT that contains `dummy_ask` or `dummy_sk` values (the IO
  Finalizer signs dummy spends and clears these fields; their presence means
  the Signer is being asked to parse spending key material).
- MUST, for each output carrying a `user_address`, parse that address and
  confirm that it contains the output's `recipient` (either directly, or e.g.
  as a receiver within a Unified Address).
- SHOULD verify that the explicit values and note data it relies upon for user
  confirmation are consistent with the effecting data being signed (for
  example, that values match value commitments via `rcv`, and that ciphertexts
  of non-fabricated outputs decrypt to the explicit note data — see
  "Fabricated same-address outputs" for the exception).

Having produced a signature, the Signer MUST update `Global.tx_modifiable` as
specified in that field's description. (A shielded signature pins all
effecting data; a transparent signature pins whatever its sighash type commits
to.)

For a v6 transaction, a Signer MAY sign a PCZT whose shielded bundle anchors,
witnesses, or proofs are absent: signatures commit to none of these. A Signer
asked to do so SHOULD be aware (and, where applicable, make its user aware)
that a spend whose witness is absent may be of a note that does not yet exist
on chain — the signature authorizes the spend regardless of whether the note
is ever created. For a v5 transaction, the bundle anchors are part of the
signature hash, and MUST be present before signing.

A single entity is likely to be both an Updater and a Signer as it can update a
PCZT with necessary information prior to signing it.

### Combiner

> Anyone can execute

The Combiner can accept 1 or many PCZTs. The Combiner MUST merge them into one
PCZT (if possible), or fail. The resulting PCZT MUST contain all of the fields
from each of the PCZTs.

The merge rules are as follows:

- **Global fields.** The transaction effecting data in `Global` (`tx_version`,
  `version_group_id`, `consensus_branch_id`, `fallback_lock_time`,
  `expiry_height`) and `coin_type` MUST be equal in all inputs.
  `Global.tx_modifiable` is merged bit by bit as specified in that field's
  description (the modifiable flags merge towards `false`; the Has
  `SIGHASH_SINGLE` flag merges towards `true`; bits 3-6 MUST be 0 in all
  inputs).

- **Lists of inputs, outputs, spends, and actions.** If the IO Finalizer has
  run on either input for a shielded bundle (indicated by its `bsk` being
  set), then the bundles MUST have equal numbers of entries and equal
  `value_sum` fields. Otherwise, if one input's list is a strict prefix
  extension of the other's (it contains additional entries beyond those held
  in common), the additional entries are appended — but only if the
  shorter input's `Global.tx_modifiable` permits modification of the
  corresponding kind (transparent inputs, transparent outputs, or shielded
  spends and outputs); otherwise the merge MUST fail. Entries held in common
  are merged pairwise by position.

- **Required (always-present) fields** of entries merged pairwise — the
  transaction effecting data such as `prevout_txid`, `cv`, `nullifier`, `rk`,
  `cmx`, `ephemeral_key`, `enc_ciphertext`, `out_ciphertext`, and the bundle
  `flags` and `note_version` — MUST be equal, or the merge MUST fail.

- **Optional fields** merge as follows: if one side is absent, the result is
  the other side; if both sides are present, they MUST be equal, or the merge
  MUST fail. Note that this differs from BIP 174, which in some cases keeps
  one of two conflicting values; see the Rationale.

  In PCZT v2, this rule applies to the shielded bundle anchors: an absent
  anchor merges with a set one. Two inputs whose anchors are both set MUST
  have equal anchors.

- **Map fields** (`partial_signatures`, `bip32_derivation`, the preimage maps,
  and the `proprietary` maps) merge by key union; if a key is present on both
  sides, the values MUST be equal, or the merge MUST fail.

A Combiner MUST NOT combine two different PCZTs — that is, two PCZTs that do
not represent the same transaction. Two PCZTs represent the same transaction
if and only if they were derived from a common ancestor PCZT by sequences of
the roles defined in this ZIP, which the merge rules above verify structurally:
all transaction effecting data held in common must be identical. Once a PCZT's
input/output set has been finalized, its effecting data uniquely determines
the transaction identifier of the transaction that will be extracted from it,
and PCZTs can be considered to be uniquely identified by that transaction
identifier. (For a v6 transaction the identifier is independent of the
anchors, so re-anchored copies of a PCZT still represent the same
transaction.)

For every field that a Combiner understands, it MAY refuse to combine PCZTs if
it detects that there will be inconsistencies or conflicts for that field in the
combined PCZT.

The Combiner does not need to know how to interpret transparent scripts in order
to combine PCZTs. It can do so without understanding scripts or the network
serialization format.

In general, the result of a Combiner combining two PCZTs from independent
participants A and B should be functionally equivalent to a result obtained from
processing the original PCZT by A and then B in a sequence. Or, for participants
performing `fA(pczt)` and `fB(pczt)`:
`Combine(fA(pczt), fB(pczt)) == fA(fB(pczt)) == fB(fA(pczt))`

### Spend Finalizer

> Anyone can execute

For each transparent input, the Spend Finalizer determines if there is enough
data to pass validation. If there is, it must construct and set
`TransparentInput.script_sig`. All other optional data in `TransparentInput`
(except for `TransparentInput.proprietary`) SHOULD be cleared from the PCZT.

### Transaction Extractor

> Anyone can execute

The Transaction Extractor checks whether the PCZT is complete and internally
consistent:

- `Global.tx_version`, `Global.version_group_id`, and
  `Global.consensus_branch_id` MUST identify a supported transaction format
  (see the `Global` field descriptions), and the transparent inputs' lock time
  requirements MUST be satisfiable (see "Determining Lock Time").
- If `Global.tx_version` is 5, the `IronwoodBundle` MUST be the canonical
  empty bundle.
- Every `TransparentInput.script_sig` MUST be set.
- Every `SaplingSpend` MUST have `zkproof` and `spend_auth_sig` set, and every
  `SaplingOutput` MUST have `zkproof` set.
- Every `OrchardBundle` or `IronwoodBundle` containing actions MUST have its
  bundle `zkproof` set, of the canonical length for its number of actions, and
  every action MUST have `spend_auth_sig` set.
- Every non-empty shielded bundle MUST have its `anchor` and `bsk` set.
- No action's `rk` may be the identity point (this would be rejected by
  consensus [^zip-0256]).

If all of the above checks pass, the Transaction Extractor computes the
shielded signature hash, uses each bundle's `bsk` to create the Sapling,
Orchard, and (for v6) Ironwood binding signatures over it, and extracts the
final transaction. If a binding signature verification key derived from the
bundle's value commitments and value balance does not match its `bsk`, the
extraction MUST fail. The Transaction Extractor SHOULD then verify the proofs
and signatures of the final transaction, so that an invalid transaction is
detected before it is broadcast.

The Transaction Extractor does not need to know how to interpret transparent
scripts in order to extract the network serialized transaction. However it may
be able to in order to validate the network serialized transaction at the same
time.

A single entity is likely to be both a Spend Finalizer and Transaction Extractor.

## Extensibility

The PCZT format is extended by revising this ZIP, in one of two ways:

- **New fields within an existing PCZT version.** This is not possible: the
  Postcard encoding is positional, so a parser cannot skip a field it does not
  know about. Unlike PSBTs, PCZTs deliberately have no non-proprietary
  arbitrary key-value maps; every field of a given PCZT version is known
  up-front, which guarantees that a Signer's view of a PCZT is complete. The
  `proprietary` maps are the only extension point within a version, and are
  reserved for private use (see "Proprietary Use fields").

- **New PCZT versions.** A revision of this ZIP may define a new version of
  the version-specific encoding, which may change anything about the format:
  adding or removing fields, changing field types (as v2 does for the bundle
  anchors), adding bundles for new payment protocols (as v2 does for the
  *Ironwood pool*), or changing the encoding scheme entirely. The 4-byte
  version field in the encoding header namespaces the versions; a parser
  encountering an unknown version MUST NOT attempt to parse the remainder.

Implementations SHOULD be able to parse every specified PCZT version, and to
emit the oldest version capable of representing a given PCZT's state, when
interoperating with entities (such as hardware signers with infrequent
firmware updates) that may not support the newest version. Conversion between
versions is lossless exactly when the target version can represent the PCZT's
state; the v1 Encoding section enumerates the states that v1 cannot represent.

Forks of Zcash that modify the transaction format should not reuse the PCZT
magic bytes (see the Rationale for `Global.coin_type`).

# Rationale

## Including a `Global.coin_type` field

This makes the PCZT format useful to forks of Zcash that have common transaction
versions. It was motivated by the PSBT format's lack of a "network" field which
led to proprietary fields being used to track that information between specific
vendors. It is also encoded into a PCZT in `Zip32Derivation.derivation_path` at
later stages (and implicitly encoded elsewhere); having the Creator encode it
up-front enables later Roles to check their data against it for correctness.

Note however that the field is not as useful to Zcash forks as a "network" field
would be in PSBTs, because the PCZT format does not contain non-proprietary
arbitrary maps; every field must be known up-front. If a fork makes additions to
its transaction format, those additions cannot be represented in a way that is
compatible with existing PCZT parsers, and constructing transactions that make
use of those additions would require forking the PCZT format (which should then
use different magic bytes for its encoding).

## Transparent protocol choices

The contents of `TransparentBundle`, and the actions that Roles take regarding
transparent inputs and outputs, is taken directly from BIP 174 [^bip-0174] and
BIP 370 [^bip-0370], and intended to follow the behaviour of PSBT version 2 when
used solely with non-SegWit inputs and outputs. The rationale is that this makes
integration of PCZTs simpler for codebases that already support PSBTs.

## Separate Shielded Modifiable Flag from Transparent Modifiable Flags

The PSBT format allows Constructor and Signer roles to be interleaved when
inputs are not using `SIGHASH_ALL`. Due to how Zcash sighash digests are
specified, signing any input causes all non-transparent effecting data to be
pinned. The Shielded and Transparent Modifiable Flags were split apart to reduce
the semantic delta between PSBTs and purely-transparent PCZTs.

## Adding an IO Finalizer role

The effective `SaplingBundle.bsk` and `OrchardBundle.bsk` for a PCZT change when
a Constructor adds a shielded spend or output. They are required by the
Transaction Extractor, however leaving their computation to that role would
require preserving all `*.rcv` values until then, which reveals the
opening of all `*.cv` values to all participants. However, we cannot require the
Constructor to update `*.bsk` due to an interaction with the Combiner role:

- If Constructors add shielded spends or outputs in series, they should always
  update `*.bsk` when doing so, even if `*.rcv` is present.
- If Constructors add shielded spends or outputs in parallel and then a Combiner
  merges the results, `*.bsk` must *never* be updated.

We can't control which of these two situations happens, ergo we need an IO
Finalizer role that is responsible for updating `*.bsk`.

The IO Finalizer role also produces signatures for all dummy spends, and can
clear their spending keys. This ensures that there is never a need for a Signer
to parse spending key material from a PCZT, which we want to discourage for
security reasons.

## Combiner rejecting non-identical duplicates

This behaviour intentionally differs from BIP 174 [^bip-0174], which specifies
that when two PSBTs have conflicting values for the same key, "the Combiner
must choose the value from the PSBT it considers to be correct" (in practice,
often last-wins). That rule silently discards data: a conflicting contribution
from a buggy or malicious participant can overwrite, for example, a derivation
path or preimage that a later Signer relies upon, without any participant
being alerted. Because every PCZT field is typed and known up-front, there is
no analogue of PSBT's unknown key-value pairs for which "keep one of them" is
the only available policy; requiring equality is always possible, and turns
every conflict into a loud failure at the Combiner rather than a silent
divergence discovered later (or not at all).

- Once every spend and output has its zkproof field set, PCZT equality MUST include
  the SpendDescription and OutputDescription contents being identical.
  - In practice enforced by creating a TransactionData / CMutableTransaction from
    the PCZT, with spendAuthSigs and bindingSig empty, and then enforcing equality.
  - This is equivalent to BIP 174's equality definition (the partial transactions
    must be identical).

## Optional anchors in PCZT v2

The v6 transaction format moves the shielded bundle anchors from effecting
data to authorizing data, expressly so that a transaction can be
pre-authorized using spending key material with the anchor and proofs updated
later [^zip-0229]. A PCZT is precisely the artifact that holds a transaction
during such a deferral, so the v2 format makes the anchor's absence
representable rather than requiring a sentinel value. The all-zeroes byte
string was rejected as a sentinel because it is a valid Pallas base field
element and therefore a syntactically valid anchor; an explicit `Option`
cannot be confused with data.

The deferral rules are gated on `tx_version`, not on the PCZT version: a v5
transaction carried in a v2 PCZT still commits to its anchors in its signature
hash, so its anchors must be fixed before signing exactly as in PCZT v1.

Making the *witness* deferrable requires no format change (it was already
optional, being consumed only by the Prover); v2 merely permits states — a
signed spend with no witness — that v1 role implementations were not required
to support. The combination enables the pre-signed transaction chains
described in the Motivation: for Orchard-protocol notes, nullifiers depend
only on note data, so every field that a v6 signature commits to is knowable
before the note being spent is mined.

## Omitting empty bundles in PCZT v2

A PCZT logically always contains every bundle substructure (see "Structure"),
but most transactions leave at least one shielded protocol unused, and PCZTs
are routinely transferred over constrained transports (QR codes, NFC, serial
links to hardware signers). Omitting bundles that exactly equal their
canonical empty values reduces the encoded size at no informational cost. The
omission rule is defined byte-exactly (equality with a canonical empty value)
so that serialization is deterministic: two copies of the same PCZT serialize
identically regardless of the software that produced them, and re-encoding
cannot flip a bundle between present and absent representations of the same
state.

## Carrying the Ironwood component as a second Orchard-shaped bundle

ZIP 229 defines the *Ironwood pool* as a second value pool of the Orchard
protocol, reusing the Action structure, proof system, and encodings, with the
pools distinguished by their note commitment trees, nullifier sets, value
balances, and component position [^zip-0229]. The PCZT v2 format mirrors this
exactly: the `IronwoodBundle` reuses the `OrchardBundle` structure, and the
`note_version` field (rather than a structural difference) captures the one
note-level distinction between the pools. This keeps implementation surface
shared, exactly as it is in the transaction format itself.


# Reference implementation

- Core PCZT format and roles:
  - https://github.com/zcash/librustzcash/tree/main/pczt
- Transparent-specific logic:
  - https://github.com/zcash/librustzcash/blob/main/zcash_transparent/src/pczt.rs
  - https://github.com/zcash/librustzcash/tree/main/zcash_transparent/src/pczt
- Sapling-specific logic:
  - https://github.com/zcash/sapling-crypto/blob/main/src/pczt.rs
  - https://github.com/zcash/sapling-crypto/tree/main/src/pczt
- Orchard-specific logic:
  - https://github.com/zcash/orchard/blob/main/src/pczt.rs
  - https://github.com/zcash/orchard/tree/main/src/pczt


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^pczt-rust]: [Source code for the `pczt` Rust crate](https://github.com/zcash/librustzcash/tree/main/pczt)

[^postcard]: [The Postcard Wire Specification](https://postcard.jamesmunns.com/)

[^protocol-saplingpaymentaddrencoding]: [Zcash Protocol Specification, Version 2024.5.1 [NU6]. Section 5.6.3.1: Sapling Payment Addresses](protocol/protocol.pdf#saplingpaymentaddrencoding)

[^protocol-orchardpaymentaddrencoding]: [Zcash Protocol Specification, Version 2024.5.1 [NU6]. Section 5.6.4.2: Orchard Raw Payment Addresses](protocol/protocol.pdf#orchardpaymentaddrencoding)

[^bip-0044]: [BIP 44: Multi-Account Hierarchy for Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)

[^bip-0174]: [BIP 174: Partially Signed Bitcoin Transaction Format](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)

[^bip-0370]: [BIP 370: PSBT Version 2](https://github.com/bitcoin/bips/blob/master/bip-0370.mediawiki)

[^slip-0044]: [SLIP-0044 : Registered coin types for BIP-0044](https://github.com/satoshilabs/slips/blob/master/slip-0044.md)

[^zip-0032]: [ZIP 32: Shielded Hierarchical Deterministic Wallets](zip-0032.rst)

[^zip-0032-seedfp]: [ZIP 32: Shielded Hierarchical Deterministic Wallets. Section "Seed Fingerprints"](zip-0032.rst#seed-fingerprints)

[^zip-0048]: [ZIP 48: Transparent Multisig Wallets](zip-0048.md)

[^zip-0203]: [ZIP 203: Transaction Expiry](zip-0203.rst)

[^zip-0212]: [ZIP 212: Allow Recipient to Derive Ephemeral Secret from Note Plaintext](zip-0212.rst)

[^zip-0225]: [ZIP 225: Version 5 Transaction Format](zip-0225.rst)

[^zip-0229]: [ZIP 229: Version 6 Transaction Format](zip-0229.md)

[^zip-0231]: [ZIP 231: Memo Bundles](zip-0231.md)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^zip-0256]: [ZIP 256: Deployment of Consensus Bug Fixes Between NU6.1 and NU6.2](zip-0256.md)

[^zip-0258]: [ZIP 258: Deployment of the NU6.3 Network Upgrade](zip-0258.md)

[^zip-0320]: [ZIP 320: Defining an Address Type to which funds can only be sent from Transparent Addresses](zip-0320.rst)

[^zip-2005]: [ZIP 2005: Ironwood Quantum Recoverability](zip-2005.md)

[^frost]: [RFC 9591: The Flexible Round-Optimized Schnorr Threshold (FROST) Protocol for Two-Round Schnorr Signatures](https://datatracker.ietf.org/doc/rfc9591/)

[^draft-schell-ironwood-migration]: [Orchard to Ironwood Migration (draft)](draft-schell-ironwood-migration.md)

[^draft-dairaemma-nu6.3-wallets]: [NU6.3 Consequences for Wallets (draft)](draft-dairaemma-nu6.3-consequences-for-wallets.md)
