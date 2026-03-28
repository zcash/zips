ZIP: ???
Title: Structured Memo Protocol for Application-Layer Attestation (NSM1)
Owners: Frontier Compute <ops@frontiercompute.io>
Credits: Zk-nd3r
Status: Draft
Category: Standards Track
Created: 2026-03-28
License: MIT
Discussions-To: <https://forum.zcashcommunity.com/>
Pull-Request: <https://github.com/zcash/zips/pulls>

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in BCP 14
when, and only when, they appear in all capitals, as shown here.

## Abstract

This ZIP specifies a structured memo envelope for protocol events committed to
Zcash shielded transactions. The envelope carries a version byte, event type,
cohort identifier, payload hash, timestamp, optional serial hash, and
human-readable note. It is designed for application protocols that need compact
on-chain commitments while keeping participant-identifying data off-chain.

This draft is based on the deployed `NSM1` memo protocol currently used by the
Nordic Shield lifecycle attestation system. In that deployment, event payloads
are hashed with BLAKE2b-256 using the personalization string
`NordicShield_`, inserted into an append-only Merkle tree, and periodically
anchored to Zcash using a memo of type `0x09`.

## Motivation

Zcash shielded memos are expressive enough to carry structured application
commitments, but the ecosystem lacks a compact convention for representing
typed lifecycle events that can be independently recomputed by external
verifiers.

Applications that track ownership, deployment, billing, transfer, and exit
events need:

- deterministic hash construction
- stable event typing
- a memo format that can be parsed without application-specific heuristics
- a way to commit large event histories without writing full plaintext records
  to the chain

This ZIP standardizes the memo structure and event commitment rules used by one
such deployment so that other builders can implement compatible tooling,
verification, and future extensions.

## Requirements

An implementation of this ZIP:

- MUST treat the memo payload as a binary structure before any wallet-specific
  memo encoding.
- MUST encode integers in big-endian byte order.
- MUST NOT place participant PII directly in the memo payload.
- MUST derive event payload hashes deterministically from the underlying event
  fields.
- MUST preserve event insertion order when deriving Merkle roots.
- MUST allow verifiers to recompute both the event leaf hash and the anchored
  root from public artifacts plus application-provided witness data.

## Specification

### Memo Envelope

Before memo encoding, the binary payload format is:

```text
byte 0      : version            = 0x01
byte 1      : type               = 0x01..0x0c
bytes 2..5  : cohort_id          = u32 big-endian
bytes 6..37 : payload_hash       = 32 bytes
bytes 38..45: timestamp          = u64 big-endian unix seconds
bytes 46..77: serial_hash        = 32 bytes, or 32 zero bytes when unused
bytes 78..n : note               = UTF-8 human-readable note, optional
```

For human-readable transport, the memo envelope SHOULD be rendered as:

```text
NSM1:{type}:{payload}
```

where:

- `NSM1` is the protocol marker
- `{type}` is the two-digit lowercase hexadecimal event type
- `{payload}` is the hexadecimal encoding of the full binary layout above

### Event Types

This draft defines the following event type assignments:

| Type | Name | Payload definition | Status |
| --- | --- | --- | --- |
| `0x01` | `PROGRAM_ENTRY` | `BLAKE2b_32(wallet_hash)` | Deployed |
| `0x02` | `OWNERSHIP_ATTEST` | `BLAKE2b_32(wallet_hash || serial_number)` | Deployed |
| `0x03` | `CONTRACT_ANCHOR` | `BLAKE2b_32(serial_number || contract_sha256)` | Deployed |
| `0x04` | `DEPLOYMENT` | `BLAKE2b_32(serial_number || facility_id || timestamp_be)` | Deployed |
| `0x05` | `HOSTING_PAYMENT` | `BLAKE2b_32(serial_number || month_be || year_be)` | Deployed |
| `0x06` | `SHIELD_RENEWAL` | `BLAKE2b_32(wallet_hash || year_be)` | Deployed |
| `0x07` | `TRANSFER` | `BLAKE2b_32(old_wallet || new_wallet || serial_number)` | Deployed |
| `0x08` | `EXIT` | `BLAKE2b_32(wallet_hash || serial_number || timestamp_be)` | Deployed |
| `0x09` | `MERKLE_ROOT` | raw 32-byte Merkle root | Deployed |
| `0x0A` | `STAKING_DEPOSIT` | `BLAKE2b_32(wallet_hash || amount_zat_be || validator_id)` | Reserved |
| `0x0B` | `STAKING_WITHDRAW` | `BLAKE2b_32(wallet_hash || amount_zat_be)` | Reserved |
| `0x0C` | `STAKING_REWARD` | `BLAKE2b_32(wallet_hash || epoch_be || reward_zat_be)` | Reserved |

Implementations of the deployed `NSM1` flow currently use the first nine event
types in production. The staking event types are reserved and MUST NOT be
assumed stable until separately activated.

### Hash Construction

Unless otherwise specified, event payload hashes use BLAKE2b with:

- digest length: 32 bytes
- personalization: `NordicShield_`

The hash input for each event type is defined in the table above. The
`MERKLE_ROOT` event is a special case whose payload hash is the 32-byte Merkle
root itself, without an additional BLAKE2b compression step.

For event types that carry a serial number, the `serial_hash` memo field MUST
be:

```text
BLAKE2b_32(serial_number)
```

with the same personalization string `NordicShield_`.

If no serial number is applicable, `serial_hash` MUST be 32 zero bytes.

### Merkle Tree Commitments

Applications using this memo protocol SHOULD aggregate event payload hashes into
an append-only binary Merkle tree. For the deployed `NSM1` protocol:

- each event produces one leaf
- leaves are ordered by insertion sequence
- parent nodes are `BLAKE2b_32(left || right)`
- Merkle node personalization is `NordicShield_MRK`
- if a level has odd cardinality, the final node is duplicated

An inclusion proof consists of:

- leaf hash
- sibling hashes
- sibling positions
- derived Merkle root
- anchor transaction identifier
- anchor block height

### On-Chain Anchoring

When anchoring a Merkle root to Zcash:

- the event type MUST be `0x09`
- the payload hash MUST be the raw current Merkle root
- the memo SHOULD be encoded as `NSM1:09:{payload}`

The deployed `NSM1` implementation broadcasts shielded memo commitments using
`zingo-cli`. The current deployment anchors every 10 events or every 24 hours,
whichever occurs first.

### Verification Procedure

To verify a committed event, a verifier:

1. recomputes the event payload hash from the application fields
2. reconstructs the memo payload and event leaf hash
3. walks the Merkle proof path to derive the root
4. retrieves the referenced anchor transaction
5. confirms that the memo contains the same `0x09` root commitment
6. confirms that the transaction is mined on the intended chain

## Rationale

This design separates protocol semantics from wallet transport.

The binary layout is fixed-width for all critical fields so parsers can extract
event type, cohort identifier, and proof-relevant material without needing to
understand any free-form note text. BLAKE2b-256 is used for compactness and
performance. Personalization strings provide domain separation between event
payload hashing and Merkle internal-node hashing.

Anchoring Merkle roots rather than full event records minimizes chain load while
preserving independent verifiability. The memo remains short and constant-sized
for the root-commitment case even as the underlying event history grows.

## Privacy Considerations

This protocol is intended to avoid writing participant-identifying plaintext
data to chain. Implementations MUST ensure that `wallet_hash`, `serial_hash`,
contract digests, and other memo inputs are derived values rather than directly
identifying customer records.

The optional note field may leak application metadata if misused. Protocols
using this ZIP SHOULD either omit the note field or constrain it to operational
strings that do not identify participants.

## Security Considerations

This protocol provides integrity and auditability, not confidentiality of the
underlying application database. Security depends on:

- correct construction of event hashes
- correct Merkle insertion ordering
- correct association between proof bundles and the anchored root that covers
  them
- correct wallet-side retrieval of the mined memo-bearing transaction

This ZIP does not address:

- fraudulent off-chain data entry before hashing
- theft of the key used to authorize anchor transactions
- application-level authorization of transfers or exits

The deployed `NSM1` stack currently uses single-operator anchor signing, with a
separate FROST migration design under development for threshold authorization of
future root anchors.

## Backwards Compatibility

This ZIP codifies the deployed version-`0x01` `NSM1` format. Existing proof
bundles remain valid as long as verifiers preserve the original event hash
construction, Merkle hashing rules, and anchor transaction references.

Future incompatible memo layouts MUST use a new version byte and SHOULD use a
distinct human-readable protocol marker.

## Reference Implementation

Reference implementations are available at:

- [Frontier-Compute/zec-pay](https://github.com/Frontier-Compute/zec-pay), which implements the deployed `NSM1` memo protocol, Merkle tree maintenance, proof bundle generation, and root anchoring flow.
- [Frontier-Compute/nsm1-verify](https://github.com/Frontier-Compute/nsm1-verify), which provides a standalone Rust and WASM verifier for NSM1 leaf hashes and Merkle proofs.

In the deployed `zec-pay` implementation:

- event payload hashes are computed with BLAKE2b-256 and personalization `NordicShield_`
- Merkle internal nodes use personalization `NordicShield_MRK`
- root anchors are transmitted as `NSM1:09:{root}`

## Test Vectors

A companion test vector package SHOULD provide:

- one event hash vector for each deployed event type `0x01` through `0x09`
- the exact input fields used to derive the payload hash
- the expected `leaf_hash`
- the hash personalization strings used

The deployed `NSM1` implementation publishes those vectors separately as:

- [Frontier-Compute/zec-pay/TEST_VECTORS.md](https://github.com/Frontier-Compute/zec-pay/blob/main/TEST_VECTORS.md)
- [TEST_VECTORS.md](./TEST_VECTORS.md)

## Acknowledgements

This draft draws on the deployed Nordic Shield `NSM1` protocol and the Zcash
shielded memo and Orchard tooling ecosystem.

## References

[^zip-guide]: [ZIP guide](https://zips.z.cash/zip-guide).

[^zec-pay]: [Frontier-Compute/zec-pay](https://github.com/Frontier-Compute/zec-pay).

[^nsm1-verify]: [Frontier-Compute/nsm1-verify](https://github.com/Frontier-Compute/nsm1-verify).
