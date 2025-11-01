
    ZIP: 270
    Title: Key Rotation for Tracked Signing Keys
    Owners: Jack Grigg <jack@electriccoin.co>
            Kris Nuttycombe <kris@electriccoin.co>
            Daira-Emma Hopwood <daira-emma@electriccoin.co>
            Arya <arya@zfnd.org>
    Status: Draft
    Category: Consensus
    Created: 2025-09-16
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/1047>

# Terminology

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The term "full validator" in this document is to be interpreted as defined in
the Zcash protocol specification [^protocol-blockchain].

The term "network upgrade" in this document is to be interpreted as described in
ZIP 200. [^zip-0200]

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in
§ 3.12 ‘Mainnet and Testnet’. [^protocol-networks]

# Abstract

This ZIP describes a mechanism for users to rotate their signing keys.

# Motivation

There are two facilities proposed to be added in the NU7 Network Upgrade that
define authorization keys in consensus:

* The Coinholder-Controlled Fund introduced by the Community and Coinholder
  Funding Model ZIP [^zip-1016] has a disbursement authorization key held by
  the Key-Holder Organizations. This key will initially be hard-coded into the
  consensus rules, and there needs to be some transaction-based mechanism to
  rotate it.
* Each ZSA Issuer has an issuance authorizing key [^zip-0227-issuance-keys]
  that it uses to authorize asset issuance. The corresponding validating key is
  initially set by the first issuance bundle containing that key.

It would be beneficial for this mechanism to support rotation of both of these
key types, and any similar key types defined by future facilities of the Zcash
consensus protocol.

## Use cases

### Small-scale single issuer (e.g. toy usage)

- Each issued asset uses `ik` as both the issuance key and rotation key (per default)
- User's backup includes `isk` (or its derivation root)
- If both consensus and the wallet is upgraded to prefer ML-DSA, then the
  wallet can migrate the user's assets to ML-DSA by deriving `ik_ML-DSA` (or
  generating and backing it up), then creating a single key rotation bundle
  that:
    - Rotates issuer `ik`'s issuance key from `ik` to `ik_ML-DSA`
    - Rotates issuer `ik`'s rotation key from `ik` to `ik_ML-DSA`

### ZSA asset bridges

- `ik` is a FROST key shared among the bridge validators
- Rotation key is held by the bridge operator (or operators via FROST)
- Bridge operator can change the bridge validator set by rotating `ik`
- Two bridge operators can choose to use the same validator set `ik_C`:
    - Bridge operator A uses `rotation_key_A` to rotate their `ik_A` issuer to
      `ik_C` (with `ik_C`'s consent)
    - Bridge operator B uses `rotation_key_B` to rotate their `ik_B` issuer to
      `ik_C` (with `ik_C`'s consent)
    - If bridge operator A decides to unmerge, they use `rotation_key_A` to
      rotate their `ik_A` issuer to `ik_A'` (or back to `ik_A` would work I
      guess), with the consent of `ik_A'` but not `rotation_key_B` or `ik_C`

### Issuer merging

An issuer can choose to transfer all of their controlled assets to another issuer, by creating a single key rotation bundle that:
- Rotates issuer `ik_A`'s issuance key from `ik_A` to `ik_B`, authorized by `rotation_key_A` and `ik_B`
- Rotates issuer `ik_A`'s rotation key from `rotation_key_A` to `rotation_key_B`, authorized by `rotation_key_A` and `rotation_key_B`
- Issuer B now can issue all of issuer `ik_A`'s assets, without knowledge of `ik_A` (but needs to continue to use `ik_A` as the identifier for those assets due to how `assetDigest` is defined)

# Privacy Implications

The mechanisms defined in this ZIP are only suitable for rotation of keys that
are publically visible in the state of the consensus protocol.

# Requirements

- The mechanism must support both keys that are initially hard-coded in
  consensus rules, and keys that are "register on first use".
- The key rotation mechanism must not impose any additional requirements
  beyond those of the signature scheme for the public key used to verify
  the rotation being authorized.

# Non-requirements

- This ZIP does not address rotation of spending keys associated with user
  addresses. If users need to rotate spending keys (for example if a wallet
  seed is compromised), it is RECOMMENDED to transfer all funds out of the
  wallet into a new wallet, and to inform counterparties that the old addresses
  should no longer be used.
- If a threshold signature scheme is used, the threshold need not be
  consensus-visible.

# Specification

## Tracked signing keys

A tracked signing key is a signing key that is tracked by full validators, and provided
by them as part of verifying changes to the global chain state made by any relevant
transaction.

Theses are distinct from untracked (normal) signing keys, which are provided by
transactions themselves, and are only used within the context of validating that single
transaction.

Each tracked signing key has an associated `protocol_type`, identifying the signing
protocol that the key is for. Tracked signing keys MUST use a protocol type defined in
this ZIP.

The following protocol types are currently valid in consensus:

| Protocol typecode | Description |
| ----------------- | ----------- |
| 0                 | `RedPallas` |
| 1                 | `BIP340`    |

Additional protocol types MAY be added to this ZIP via modifications specified
in other ZIPs.

## Rotation keys

Every tracked signing key has, in any given chain state, a corresponding
"rotation key" that authorizes key rotation operations that change the tracked
signing key.

Rotation keys are themselves tracked signing keys, and thus can also be
rotated. As of the current revision of this ZIP, a rotation key is always its
own rotation key; there are no "depth-2" rotation keys.

Rotation keys MAY be any valid protocol type.

## Key usage

Each tracked signing key has an associated "usage", specifying which
sub-protocol (within the overall Zcash protocol) it is used within.

The set of defined key usages for tracked signing keys is as follows:

| Usage typecode | Description                    |
| -------------- | ------------------------------ |
| 1              | ZIP TBD: Lockbox disbursements |
| 2              | ZIP 227: ZSA Issuance          |

Additional key usages MAY be added to this ZIP via modifications specified in
other ZIPs.

Particular key usages MAY require a strict subset of the defined protocol
types.

Note that no Rotation usage type is defined. 

## Key identifiers

Each tracked signing key has a corresponding "key identifier" `key_id` that
represents it in the global chain state.

`key_id` is treated as an opaque byte string within the context of this ZIP.
The format for any particular `key_id` is defined by the corresponding key
usage in its relevant ZIP.

Consensus rule: `(key_usage, key_id)` MUST be globally unique.

## Key Rotation Bundle

The transaction format for transaction version 6 is modified to contain an
additional section:

+-------------------------+---------------------+-----------------+--------------------------------------------------------------+
| varies                  | ``nKeyRotations``   | ``compactSize`` | The number of KeyRotationAction entries in ``vKeyRotations`` |
+-------------------------+---------------------+-----------------+--------------------------------------------------------------+
| ??? * ``nKeyRotations`` | ``vKeyRotations``   | ???             | A sequence of key rotation action descriptions               |
+-------------------------+---------------------+-----------------+--------------------------------------------------------------+

## Global state

A `key_pointer` is the tuple `(key_usage, key_id)`.
    - `key_usage` is defined above
    - `key_id` is a byte string defined at key registration or by consensus

The global chain state tracks:
- a mapping of current keys `key_pointer -> (application_key, rotation_key)` where:
    - `application_key` is the public key used to authorize subprotocol
      operations, such as ZSA issuance or lockbox disbursement.
    - `rotation_key` is the public key used to authorize rotations of both
      `application_key` and `rotation_key`. 

## Key registration

When registering a new key, the initial rotation key MAY be the same as the
signing key. This will be the case for ZSA issuance keys.

## Key rotation

A Key Rotation operation modifies the global state, by replacing the current
key for a given key pointer with a new key.

- `key_pointer`: A pointer to the key to be rotated.
    - The original key that caused the creation of the map entry:
        - protocol type (e.g. `RedPallas`, `BIP340`)
        - `pubkey`
- `new_key`: The new key to replace it with:
    - protocol type (e.g. `RedPallas`, `BIP340`) that is supported in consensus by `key_usage`
    - `pubkey`
- `rotation_auth_sig`
    - Using protocol of the existing `rotation_key` key that authorizes rotation of `prev_key`
        - in the case of `key_usage = rotation_key` would be precisely `prev_key`)
- `evidence_sig`
    - A signature that is performed using `new_key` to prevent accidentally bricking yourself (or mischief from rotating to a key held by someone else). This should be required at least if `key_usage == rotation_key`. The new key is "consenting" to be rotated in by signing the txid.

A key rotation operation proceeds as follows:

- Resolve `key_pointer` to obtain the existing key `prev_key`, and its current `rotation_key`.
- Verify `rotation_auth_sig` with `rotation_key`.
- Verify `evidence_sig` with `new_key`.
- Update the global state at `key_pointer` to replace `prev_key` with `new_key`.

WIP alternate encoding:
- `key_pointer`: A pointer to the global map entry that currently uses existing key `prev_key` in global state:
    - `key_usage: lockbox_sig | zsa_issuance`
    - `key_depth`
    - `key_id`: The original key that caused the creation of the map entry:
        - protocol type (e.g. `RedPallas`, `BIP340`)
        - `pubkey`

### Key Rotation Actions

```rust
struct KeyRotation {
  /// The purpose of the key that is being rotated. Key purpose cannot change.
  key_purpose: KeyPurpose,
  /// The original key in the chain of keys that we're rotating. This implies the current rotation key.
  orig_key_pubkey: Vec<u8>,
  /// The protocol type of the new key being registered. Allowed changes to the protocol type are controlled by consensus;
  /// at present, this must always correspond to the protocol type for the existing key being rotated.
  new_key_protocol: KeyProtocol,
  /// The pubkey that will replace the current key for the given purpose in the chain descending from `orig_key_pubkey`.
  new_key_pubkey: Vec<u8>,
  /// The signature that validates against the rotation key for the key being replaced. This should sign the txid.
  rotation_auth_sig: Vec<u8>,
  /// A signature that proves control over the signing keys for `new_key_pubkey`. This should also sign the txid.
  evidence_sig: Vec<u8>,
}
```

+-------------------------------+---------------------+-----------------+--------------------------------------------------------------+
+-------------------------------+---------------------+-----------------+--------------------------------------------------------------+
+-------------------------------+---------------------+-----------------+---------------------------------------------------------------------+
+-------------------------------+---------------------+-----------------+---------------------------------------------------------------------+
+-------------------------------+---------------------+-----------------+---------------------------------------------------------------------+

A new Key Rotation bundle

* Vec of rotation operations, applied to consensus in order (to match e.g. order that txs are applied within blocks):
  * Pointer to the global map entry that currently uses existing key `prev_key` in global state:
    * `key_usage: key_rotation | lockbox_sig | zsa_issuance`
    * The original key that cause the creation of the map entry:
      * protocol type (e.g. `RedPallas`, `BIP340`)
      * `pubkey`
  * New key `new_key` to replace it with:
    * protocol type (e.g. `RedPallas`, `BIP340`) that is supported in consensus by `key_usage`
    * `pubkey`
  * `rotation_auth_sig`
    * Using protocol of the existing `key_rotation` key that authorizes rotation of `prev_key`
      * in the case of `key_usage = key_rotation` would be precisely `prev_key`)
  * `evidence_sig`
    * A signature that is performed using `new_key` to prevent accidentally bricking yourself (or mischief from rotating to a key held by someone else). This should be required at least if `key_usage == key_rotation`. The new key is "consenting" to be rotated in by signing the txid.

## Consensus keys & Rotation Keys

### Rotation keys

A rotation key provides the keyholder with the capability to create a valid signature authorizing the effects of a key rotation bundle.

# Notes / Open Questions

- When rotating ZSA rotation keys, an entry can be added or modified to map the latest ik(s) to the original ik
    - Creating the first ZSA issuance key may need a pointer to the existing or original rotation-key/ik without replacing it
- Should the AssetBurn encoding include an asset_desc_hash instead of an asset_base?
- Could we defer the parts of this outside the orchard tx encoding to NU7.1 or NU8? It'll need another format change but at least it'll be a simple one, and while this is a small change on its own, NU7's scope has crept a little more than would be ideal. On the other hand, we did already defer this from NU6.1 to NU7. Spending from lockbox inputs seems closer to trivial, maybe we could allow spending from lockbox inputs in NU7 and do key rotation in the following NU?
    - The Deferred Dev Fund Lockbox Disbursement ZIP that was voted on requires key rotation due to its Requirements section having these two requirements:
        - Funds are held in a multisig resistant to compromise of some of the parties' keys, up to a given threshold.
        - No single party’s non-cooperation or loss of keys is able to cause any Protocol-defined Ecosystem Funding to be locked up unrecoverably.
    - The combination of these two requirements forces us to specify and implement key rotation as part of Lockbox Disbursement.
- Have a separate rotation key, independent of the signing key.
  - Rotation key can rotate either itself or the signing key.
  - Signing key can authorize transactions (ZSA issuance or lockbox disbursement).
  - For ZSAs, the initial rotation key is the same as the signing key.

## Previously considered global state alternative (WIP)

The global chain state tracks maps of:
- `current_key -> Vec<original_key>`, and
- `original_key -> key_state`
where
- `original_key` is the original key that was added to the global state as a
  tracked signing key
- `current_key` is a tracked signing key that should be expected instead of
  `original_key`
- `key_state = (current_key, Vec<parent_original_key>, Vec<child_original_key>)`
  - `current_key` is the key required to authenticate control of the key slot
  - `parent_original_key` is a `original_key` of a `current_key` that may
    authorize mutations to the `current_key` and `child_original_key` of this
    `key_state`
  - `child_original_key` is a `original_key` for a `key_state` for which
    mutations may be authorized by the `current_key` of this `key_state`

If a the `key_state` of an `original_key` has no `parent_original_key`, it may
mutate itself.


## Rationale

- Separate key usages: enables independent rotation (e.g. if a key-holder org accidentally uses their lockbox disbursement key for issuing an asset, they can recover from that mistake)

- Vec of rotation operations that each rotate a single key:
    - It is equivalent to a struct that contains optional fields (would need to define optionality of those fields, and either representation requires defining ordering)
    - It enables extending rotation key concept in future to permit multiple rotation keys, without requiring a transaction format change.


# Deployment

This ZIP is proposed to activate with Network Upgrade 7. [^draft-arya-deploy-nu7]


# Reference implementation

TBD


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.1 [NU6.1] or later](protocol/protocol.pdf)

[^draft-arya-deploy-nu7]: [draft-arya-deploy-nu7: Deployment of the NU7 Network Upgrade](draft-arya-deploy-nu7.md)

