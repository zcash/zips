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
    Pull-Request: <https://github.com/zcash/zips/pull/???>


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

`UTF8String` is a variable-length human-readable string encoded with UTF-8.


# Abstract

This ZIP proposes a binary transaction format which contains the information
necessary for a signer to produce signatures for the transaction and holds the
signatures for inputs while they do not have a complete set of signatures. The
signer can be offline as all necessary information can be provided in the
transaction.


# Motivation

> TODO


# Privacy Implications

> TODO


# Requirements

> TODO


# Specification

> TODO

PCZTs do not support Sprout, and cannot be used to create v4 or earlier
transactions.

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
    - TODO: Update this if we determine that v4 transactions can be created.

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

## Structure

A PCZT is comprised of several top-level structures, that map to equivalent
regions of a Zcash transaction:
- `Global`: fields that are relevant to the transaction as a whole.
- `TransparentBundle`: fields relevant to the transparent protocol.
- `SaplingBundle`: fields relevant to the Sapling protocol.
- `OrchardBundle`: fields relevant to the Orchard protocol.

Each structure in turn contains a combination of:
- Transaction effecting data: required fields that are part of the final
  transaction, and are always present in the PCZT.
- Transaction authorizing data: fields that are initially empty, and are filled
  in as the PCZT is processed.
- Context data: information committed to by (or relevant to) the transaction
  effecting data, that enables various Roles to be performed.

The bundle substructures are not optional. This is because a PCZT does not
always contain a semantically-valid transaction, and there may be phases where
we need to store protocol-specific metadata before it has been determined
whether there are protocol-specific inputs or outputs.

### `Global`

The `Global` struct has the following fields:

- `tx_version: u32`

  The version of the transaction being created.

  - This is set by the Creator.
  - This is checked by the Constructor before adding inputs or outputs, to
    confirm that the transaction version will support the payment protocol for
    those inputs or outputs.
  - PCZT version 1: MUST be 5.
    - TODO: Determine whether it is actually possible to use the current Roles
      to create a v4 transaction.

- `version_group_id: u32`

  The version group ID of the transaction being created.

- `consensus_branch_id: u32`

  The consensus branch ID for the chain in which this transaction will be mined.

  Non-optional because this commits to the set of consensus rules that will
  apply to the transaction; differences therein can affect every role.

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

- `anchor: [u8; 32]`

  The Sapling anchor for this transaction.

  Set by the Creator.

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
  - `enableSpendsOrchard` flag (bit 0)
  - `enableOutputsOrchard` flag (bit 1)
  - Reserved, zeros (bits 2..=7)

  This is set by the Creator. The Constructor MUST only add spends and outputs
  that are consistent with these flags (i.e. are dummies as appropriate).

- `value_sum: (u64, bool)`

  The net value of Orchard spends minus outputs.

  This is initialized by the Creator, and updated by the Constructor as spends
  or outputs are added to the PCZT. It enables per-spend and per-output values
  to be redacted from the PCZT after they are no longer necessary.

- `anchor: [u8; 32]`

  The Orchard anchor for this transaction.

  Set by the Creator.

- `zkproof: Option<List<u8>>`

  The Orchard bundle proof.

  This is `None` until it is set by the Prover.

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

### Constructor

The Constructor adds spends and outputs to the PCZT.

Before any input or output may be added, the Constructor MUST check the
`Global.tx_modifiable` field. Transparent inputs may only be added if the
Transparent Inputs Modifiable flag is True. Transparent outputs may only be
added if the Transparent Outputs Modifiable flag is True. Shielded spends or
outputs may only be added if the Shielded Modifiable flag is True.

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
- `OrchardBundle.bsk` using `OrchardAction.rcv`.

A single entity is likely to be both a Constructor and an IO Finalizer.

### Updater

> Anyone can contribute

The Updater adds information to the PCZT that it has access to, and that is
necessary for subsequent entities to proceed, such as key paths for signing
spends.

A single entity is likely to be both a Constructor and Updater.

### Redactor

> Anyone can execute

The Redactor removes information that is unnecessary for subsequent
entities to proceed.

This can be useful, for example, when creating a transaction that has inputs
from multiple independent Signers; each can receive a PCZT with just the
information they need to sign, but (e.g.) not the `alpha` values for other
Signers.

### Prover

> Capability holders can contribute

The Prover needs all private information for a single spend or output.

In practice, the Updater that adds a given spend or output will either act as
the Prover themselves, or add the necessary data, offload to the Prover, and
then receive back the PCZT with private data stripped and proof added.

### Signer

> Capability holders can contribute

The Signer:
- Needs the spend authorization randomizers to create signatures.
- Needs sufficient information to verify that the proof is over the correct
  data, without needing to verify the proof itself.

Signers do not need to sign for all possible input types. For example, a Signer
may choose to only sign Orchard inputs.

A single entity is likely to be both an Updater and a Signer as it can update a
PCZT with necessary information prior to signing it.

### Combiner

> Anyone can execute

The Combiner can accept 1 or many PCZTs. The Combiner MUST merge them into one
PCZT (if possible), or fail. The resulting PCZT MUST contain all of the fields
from each of the PCZTs.

The Combiner MUST NOT combine two PCZTs if it encounters any field that is set
to different values in the PCZTs. (TODO: Add rest of Combiner rules.)

A Combiner MUST NOT combine two different PCZTs. PCZTs can be uniquely
identified by (TODO).

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

The Transaction Extractor checks whether all inputs have complete authorizing
information:

- If no `TransparentInput.script_sig` is `None`, then (TODO: finish)

If all of the above checks pass, the Transaction Extractor creates the Sapling
and Orchard binding signatures, and extracts the final transaction. It SHOULD
then verify the Sapling and Orchard bundle proofs and signatures of the final
transaction.

The Transaction Extractor does not need to know how to interpret transparent
scripts in order to extract the network serialized transaction. However it may
be able to in order to validate the network serialized transaction at the same
time.

A single entity is likely to be both a Spend Finalizer and Transaction Extractor.

## Extensibility

> TODO

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

This behaviour intentionally differs from BIP 174 [^bip-0174], (TODO: rationale).

- Once every spend and output has its zkproof field set, PCZT equality MUST include
  the SpendDescription and OutputDescription contents being identical.
  - In practice enforced by creating a TransactionData / CMutableTransaction from
    the PCZT, with spendAuthSigs and bindingSig empty, and then enforcing equality.
  - This is equivalent to BIP 174's equality definition (the partial transactions
    must be identical).


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

[^zip-0203]: [ZIP 203: Transaction Expiry](zip-0203.rst)

[^zip-0212]: [ZIP 212: Allow Recipient to Derive Ephemeral Secret from Note Plaintext](zip-0212.rst)

[^zip-0225]: [ZIP 225: Version 5 Transaction Format](zip-0225.rst)

[^zip-0231]: [ZIP 231: Memo Bundles](zip-0231.md)

[^zip-0320]: [ZIP 320: Defining an Address Type to which funds can only be sent from Transparent Addresses](zip-0320.rst)
