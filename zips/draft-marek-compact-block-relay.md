    ZIP: Unassigned
    Title: Compact Block Relay
    Owners: Marek <marek@zfnd.org>
    Status: Draft
    Category: Network
    Created: 2026-10-30
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/360>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

The terms "Mainnet" and "Testnet" are to be interpreted as described in
section 3.12 of the Zcash Protocol Specification. [^protocol-networks]

The terms "txid", "authorizing data commitment" (denoted `auth_digest`), and
"witnessed transaction identifier" ("wtxid") are to be interpreted as
described in ZIP 239. [^zip-0239]

best tip
:   The tip of a node's best fully validated block chain.

early relay
:   Announcing or sending a block before the sending node has fully validated
    it.

authenticated block
:   A block that passes the checks in [Early Relay].


# Abstract

This ZIP specifies compact block relay for the Zcash peer-to-peer network,
adapted from BIP 152. [^bip-0152] A compact block contains the block header,
short identifiers for the block's transactions, and its coinbase transaction;
the receiver reconstructs the block from transactions it already has. Peers
that both opt in may also relay a block before fully validating it, once its
header and transaction commitments have been checked.


# Motivation

As in Bitcoin before BIP 152, a Zcash node announces a block only after fully
validating it, and a peer that requests the block receives every transaction
in it, although it has usually already received most of them through
transaction relay. Both delay the propagation of new blocks between miners.

BIP 152 replaces transactions the receiver already has with short
identifiers, and allows a block to be relayed before it is fully validated.
It cannot be used in Zcash unchanged: Zcash block headers include an Equihash
solution, and since NU5 a transaction's txid does not commit to its
authorizing data [^zip-0244], so short identifiers and the checks made before
early relay need to cover the wtxid.


# Specification

All messages defined in this ZIP are serialized in the standard encoding for
P2P messages. [^zip-0204]

## Service Flag

The service flag `NODE_COMPACT_BLOCKS` is defined as bit 16
(`0x0000000000010000`). This value is subject to confirmation by the ZIP
Editors.

A node that sets `NODE_COMPACT_BLOCKS` in its `version` message supports the
messages defined in this ZIP and follows the rules in [Early Relay] and
[Peer Misbehaviour].

The messages defined in this ZIP MUST NOT be sent on a connection unless both
peers set `NODE_COMPACT_BLOCKS` in their `version` messages, and MUST NOT be
sent before the `version`/`verack` handshake completes. Support MUST NOT be
inferred from any other source, such as `addr` records, user agents, or
protocol versions. A node MUST ignore these messages on other connections.

## `sendcmpct`

The `sendcmpct` message is defined as a message where the `command` field is
(NUL-padded) `"sendcmpct"`, with the following payload:

| Bytes | Name | Data Type | Description |
|-------|------|-----------|-------------|
| 1 | `announce` | `uint8` | 1 to request `cmpctblock` announcements, 0 to stop them. |
| 8 | `version` | `uint64` | Compact block encoding version. |

This ZIP specifies version 1. A message with `announce` other than 0 or 1 is
malformed.

A node MAY send `cmpctblock` messages to a peer only while the most recent
`sendcmpct` received from that peer has `announce` = 1 and `version` = 1. A
`sendcmpct` with any other version disables announcements to its sender, and
is not a protocol violation.

A node MUST NOT request announcements from more than three peers at a time. It
SHOULD request them from the peers that most recently first announced blocks
it then added to its best chain; announcements of blocks it has not validated
MUST NOT be counted. A node MUST ignore `cmpctblock` messages it has not
requested. Disabling announcements MUST NOT cancel an outstanding
`getblocktxn` request.

There is no low-bandwidth mode and no compact block inventory type. Blocks
are requested with `getdata` and `MSG_BLOCK`, as before.

## `cmpctblock`

The `cmpctblock` message is defined as a message where the `command` field is
(NUL-padded) `"cmpctblock"`, with the following payload:

| Bytes | Name | Data Type | Description |
|-------|------|-----------|-------------|
| varies | `header` | Block header | Encoded as in section 7.6 of the Zcash Protocol Specification. [^protocol-blockheader] |
| 8 | `nonce` | `uint64` | Nonce used to compute short IDs. |
| varies | `shortidsCount` | `CompactSize` | Number of short IDs. |
| `6 * shortidsCount` | `shortids` | `uint8[6][]` | Short IDs of the transactions that are not prefilled, in block order. |
| varies | `prefilledCount` | `CompactSize` | Number of prefilled transactions. |
| varies | `prefilled` | `PrefilledTransaction[]` | Prefilled transactions, in block order. |

The header includes the Equihash solution, and does not include the
transaction count that follows it in a `headers` message. On Mainnet and
Testnet it is 1,487 bytes.

A `PrefilledTransaction` has the following format:

| Bytes | Name | Data Type | Description |
|-------|------|-----------|-------------|
| varies | `index` | `CompactSize` | Differentially encoded index of the transaction in the block. |
| varies | `tx` | Transaction | The transaction, encoded as in section 7.1 of the Zcash Protocol Specification. [^protocol-txnencoding] |

In a list of differentially encoded indexes, the first entry is the absolute
index, and each later entry is the absolute index minus the previous absolute
index minus 1. For example, `[0, 0, 2]` encodes the absolute indexes
`[0, 1, 4]`. Counts and indexes MUST be checked before allocation or
indexing, and count addition and index decoding MUST NOT overflow.

Let `n = shortidsCount + prefilledCount` be the number of transactions in the
block. A node MUST reject a `cmpctblock` message if:

- any of `shortidsCount`, `prefilledCount`, and `n` exceeds 37,037;
- the absolute prefilled indexes are not strictly increasing, or any is not
  less than `n`;
- the first prefilled transaction is not a coinbase transaction at index 0,
  or any other prefilled transaction is a coinbase transaction; or
- the sizes of the header, the `CompactSize` encoding of `n`, and the
  prefilled transactions, plus 54 bytes for each short ID, sum to more than
  2,000,000 bytes.

Senders SHOULD prefill only the coinbase transaction.

### Short Transaction IDs

The sender SHOULD choose `nonce` uniformly at random for each `cmpctblock`
message. The short ID of a transaction is computed as follows:

1. Let `h` be the SHA-256 hash of the encoded block header followed by
   `nonce`.
2. Let `k0` and `k1` be bytes 0 to 7 and 8 to 15 of `h`, each interpreted as
   a little-endian `uint64`.
3. Compute SipHash-2-4 with keys `(k0, k1)` of the transaction's 32-byte txid
   for v4 and earlier transactions, or of its 64-byte wtxid for v5 and later
   transactions.
4. The short ID is the first 6 bytes of the little-endian encoding of the
   result.

## `getblocktxn` and `blocktxn`

The `getblocktxn` message is defined as a message where the `command` field
is (NUL-padded) `"getblocktxn"`, with the following payload:

| Bytes | Name | Data Type | Description |
|-------|------|-----------|-------------|
| 32 | `blockHash` | `uint8[32]` | Hash of the block announced by `cmpctblock`. |
| varies | `indexesCount` | `CompactSize` | Number of requested transactions. |
| varies | `indexes` | `CompactSize[]` | Differentially encoded indexes of the requested transactions. |

The `indexesCount` field MUST NOT exceed 37,037, and the absolute indexes
MUST be strictly increasing and less than `n`.

The `blocktxn` message is defined as a message where the `command` field is
(NUL-padded) `"blocktxn"`, with the following payload:

| Bytes | Name | Data Type | Description |
|-------|------|-----------|-------------|
| 32 | `blockHash` | `uint8[32]` | `blockHash` from the request. |
| varies | `txCount` | `CompactSize` | Number of transactions. |
| varies | `tx` | Transaction[] | The requested transactions, in the order requested. |

A `blocktxn` message MUST contain exactly the requested transactions, which
MUST NOT exceed 2,000,000 bytes in total.

A node that sends a `cmpctblock` message MUST be able to answer a
`getblocktxn` request for any subset of the block's transactions, and SHOULD
retain the block for this purpose for 15 seconds. It SHOULD limit the
`blocktxn` messages it sends for one `cmpctblock` message, including repeated
and empty responses, to 2,000,000 bytes in total, and MAY ignore requests
beyond that limit or after that time. It MUST ignore requests for blocks it
has not announced on that connection or no longer retains, and requests for
indexes outside the block.

A node MUST ignore a `blocktxn` message that does not answer its outstanding
`getblocktxn` request on that connection, and SHOULD wait at most two seconds
for the answer.

## Sending Compact Blocks

A node MUST send each block announcement as `cmpctblock` to at most three
peers, and SHOULD do so only when the `cmpctblock` message is smaller than the
block. Other peers receive the announcement as before. A node MAY announce a
fully validated block with `cmpctblock` to any peer that requested
announcements.

### Early Relay

A node MAY relay a block before fully validating it only to peers that set
`NODE_COMPACT_BLOCKS`, and only after checking that:

- NU5 is active at the block's height;
- the block's parent is the node's best tip, and the block's coinbase height
  is one more than the best tip's height;
- the header has the expected difficulty, a valid Equihash solution, a hash
  that meets its target, and a valid time with respect to both the local
  clock and the median time past;
- the block is at most 2,000,000 bytes, its first transaction is a coinbase
  transaction, and no later transaction has a transparent input with a null
  previous output;
- the block passes the shielded action limits, and the subsidy and funding
  stream checks that do not depend on value pool state;
- the txids are distinct and reproduce `hashMerkleRoot`, and each
  transaction's consensus branch ID is valid at the block's height;
- the `auth_digest` values of all transactions reproduce the authorizing data
  root, which together with the parent's chain history reproduces
  `hashBlockCommitments`, as specified in ZIP 244; [^zip-0244] and
- the block has not been rejected or invalidated by the node.

While it completes validation, the node MAY announce the block, and MAY answer
`getdata` requests for it from those peers. It MUST stop early relay of the
block when its validation fails or is cancelled, or when its parent is no
longer the best tip, and MUST check these conditions before sending each
message. It SHOULD continue to answer `getblocktxn` requests for a
`cmpctblock` message it has already sent.

## Receiving Compact Blocks

Before retaining a `cmpctblock` message or querying its mempool, a node MUST
check the coinbase height, NU5 activation, the header's time, target, and
proof of work, and that the block's parent is its best tip. If these checks
fail, the node SHOULD treat the message as an announcement of the block hash.
A node SHOULD limit the compact blocks it retains and the `getblocktxn`
requests it sends, both per peer and in total.

The node then reconstructs the block:

1. Place the prefilled transactions at their indexes.
2. For each index that is not prefilled, if its short ID occurs only once in
   the message and exactly one mempool transaction has that short ID, place
   that transaction at the index.
3. If any index remains empty, send one `getblocktxn` request for all of
   them.
4. Check that the `blocktxn` response contains one transaction for each
   requested index, with the corresponding short ID.
5. Check the block size, the coinbase transaction, that the txids are
   distinct and reproduce `hashMerkleRoot`, and that the `auth_digest` values
   reproduce the commitments as in [Early Relay], then fully validate the
   block.

Step 5 is required because a short ID can match the wrong transaction, and
`hashMerkleRoot` does not commit to authorizing data.

If any step fails, or the response does not arrive in time, the node MUST
request the block from the same peer with `getdata` and `MSG_BLOCK`, using its
usual timeout. A reconstruction failure MUST NOT cause the node to treat the
block as invalid.

## Peer Misbehaviour

A node MAY treat a malformed message defined in this ZIP as it treats other
malformed P2P messages. This includes non-canonical `CompactSize` encodings,
indexes out of range, and counts or sizes that exceed the limits above.

A node MUST NOT penalize a peer for short ID collisions, failed
reconstructions, commitment mismatches in reconstructed blocks, `blocktxn`
timeouts, or an unknown parent.

A node MUST NOT penalize a peer that set `NODE_COMPACT_BLOCKS` when an
authenticated block it sent fails later validation; the node still rejects
the block. A node MAY penalize a peer that sends a full block failing the
proof of work, size, structure, or commitment checks in [Early Relay]. If the
node cannot authenticate a block because the parent's chain history is
unavailable, but the block passes the checks that do not depend on it, the
node MUST NOT penalize the peer for a later transaction or contextual
validation failure. Failures of local time policy and local invalidation are
not peer misbehaviour.

## Deployment

This ZIP applies on Mainnet and Testnet from NU5 activation. It does not
require a network upgrade. Peers that do not set `NODE_COMPACT_BLOCKS` use
block relay as before.


# Rationale

This ZIP differs from BIP 152 as follows:

- The header is the Zcash block header, including the Equihash solution.
- Short IDs are computed from the wtxid for v5 and later transactions, so
  version 1 of the encoding is not Bitcoin's version 1.
- Only high-bandwidth announcements are defined.
- Support is signalled by a service flag rather than a protocol version, and
  an unsupported version disables announcements rather than being negotiated.
- The coinbase transaction is always prefilled, and all counts and sizes are
  bounded.
- Early relay requires checking authorizing data, and is limited to children
  of the best tip.

Zebra and zcashd ignore unknown P2P messages after the handshake
[^zebra-codec] [^zcashd-messages], so a service flag is not needed to avoid
disconnection. It is needed because both peers have to agree on the encoding,
and on not penalizing authenticated blocks that fail later validation; an
ignored message establishes neither. A protocol version signals support for a
network upgrade, not for an optional relay policy. [^zip-0201]

The limit of 37,037 transactions is the 2,000,000-byte block size limit
divided by 54 bytes, a lower bound on the size of a transaction.

Bit 16 avoids the service flags allocated in Zcash and Bitcoin
[^bitcoin-services], the range 24 to 31 reserved for temporary experiments,
and bits 12 to 14, which are used by pending Bitcoin proposals.
[^bitcoin-utreexo] [^bitcoin-utxo-sharing]


# Security and Privacy Considerations

A short ID identifies a transaction only probabilistically. A node that
skipped the checks in step 5 of [Receiving Compact Blocks] could accept a
block whose authorizing data differs from the data committed to by its
header.

An early relayed block can be invalid. Receiving one does not indicate that
the block is valid, and nodes MUST fully validate it before accepting it.

A `getblocktxn` request reveals which transactions the sender did not have,
and the timing of announcements can reveal a node's peers. Setting
`NODE_COMPACT_BLOCKS` reveals that a node supports this ZIP.


# Reference Implementation

Zebra implements this ZIP behind the default-off option
`experimental_early_block_relay`, using temporary service bit 25. [^zebra] It
will use the bit confirmed for this ZIP; until then, it does not negotiate
compact block relay with peers that use the confirmed bit.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-txnencoding]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.1: Transaction Encoding and Consensus](protocol/protocol.pdf#txnencoding)

[^protocol-blockheader]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.6: Block Header Encoding and Consensus](protocol/protocol.pdf#blockheader)

[^zip-0201]: [ZIP 201: Network Peer Management for Overwinter](zip-0201.rst)

[^zip-0204]: [ZIP 204: Zcash P2P Network Protocol](zip-0204.rst)

[^zip-0239]: [ZIP 239: Relay of Version 5 Transactions](zip-0239.rst)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^bip-0152]: [BIP 152: Compact Block Relay](https://github.com/bitcoin/bips/blob/master/bip-0152.mediawiki)

[^zebra]: [Zebra, revision 4b8a202e41d41b8ab84a703c72ef77fd03d4d000](https://github.com/ZcashFoundation/zebra/tree/4b8a202e41d41b8ab84a703c72ef77fd03d4d000)

[^zebra-codec]: [Zebra P2P message codec](https://github.com/ZcashFoundation/zebra/blob/4b8a202e41d41b8ab84a703c72ef77fd03d4d000/zebra-network/src/protocol/external/codec.rs)

[^zcashd-messages]: [zcashd P2P message processing](https://github.com/zcash/zcash/blob/master/src/main.cpp)

[^bitcoin-services]: [Bitcoin Core service flags](https://github.com/bitcoin/bitcoin/blob/master/src/protocol.h)

[^bitcoin-utreexo]: [Proposed BIP 183: Utreexo — Peer Services, Bitcoin BIPs pull request #1923](https://github.com/bitcoin/bips/pull/1923)

[^bitcoin-utxo-sharing]: [Proposed BIP: P2P UTXO Set Sharing, Bitcoin BIPs pull request #2137](https://github.com/bitcoin/bips/pull/2137)
