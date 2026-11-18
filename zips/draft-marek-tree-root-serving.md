    ZIP: Unassigned
    Title: Note Commitment Tree Root Serving
    Owners: Marek <marek@zfnd.org>
    Credits: Arya
             Janito
    Status: Draft
    Category: Network
    Created: 2026-11-18
    License: MIT


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

tree roots
:   The roots of the Sapling, Orchard, and Ironwood note commitment trees after
    a block. [^protocol] [^zip-0229]


# Abstract

This ZIP defines the service flag `NODE_TREE_ROOTS` and the messages
`gettreeroots` and `treeroots` for the Zcash peer-to-peer protocol specified in
ZIP 204. [^zip-0204] With them, a node obtains the tree roots of a range of
blocks from a peer, and checks them against the block headers. A node syncing
from checkpoints can then maintain its chain history tree without updating its
note commitment trees.


# Motivation

The chain history tree commits to each block's tree roots. [^zip-0221] During
checkpoint sync, a node updates its note commitment trees only to obtain these
roots, and the updates take most of the time it spends committing blocks with
many shielded outputs.

Block headers commit to the roots, so any peer can supply them. The Version 2
P2P protocol draft [^draft-p2p-v2] defines the same capability. This ZIP
specifies it for the current protocol, so that it can be deployed without the
rest of that draft.


# Specification

All messages defined in this ZIP are serialized in the standard encoding for
P2P messages. [^zip-0204]

## Service Flag

The service flag `NODE_TREE_ROOTS` is defined as bit 3
(`0x0000000000000008`). A node MUST NOT send `gettreeroots` to a peer that did
not set it in its `version` message.

## `gettreeroots`

The `gettreeroots` message is defined as a message where the `command` field
is `"gettreeroots"`, with the following payload:

| Bytes | Name | Data Type | Description |
|-------|------|-----------|-------------|
| 4 | `startHeight` | `uint32` | Height of the first block. |
| 32 | `finalHash` | `uint8[32]` | Hash of the last block, in the byte order of `hashPrevBlock`. [^protocol-blockheader] |
| 4 | `count` | `uint32` | Number of blocks. |

The message requests the tree roots of the blocks at heights `startHeight` to
`end = startHeight + count - 1`, computed without wrapping. A message with
`count` 0 or greater than 4,000 is malformed.

## `treeroots`

The `treeroots` message is defined as a message where the `command` field is
(NUL-padded) `"treeroots"`, with the following payload:

| Bytes | Name | Data Type | Description |
|-------|------|-----------|-------------|
| 1 | `result` | `uint8` | 0 for roots, 1 for a refusal. |
| varies | `entriesCount` | `CompactSize` | Number of entries, present only if `result` is 0. |
| varies | `entries` | `TreeRoots[]` | Entries, present only if `result` is 0. |

A `TreeRoots` entry has the following format:

| Bytes | Name | Data Type | Description |
|-------|------|-----------|-------------|
| 32 | `saplingRoot` | `uint8[32]` | Sapling root, encoded as `anchorSapling`. [^protocol-txnencoding] |
| 32 | `orchardRoot` | `uint8[32]` | Orchard root, encoded as `anchorOrchard`. |
| 32 | `ironwoodRoot` | `uint8[32]` | Ironwood root, encoded as `anchorIronwood`. [^zip-0229] |
| 1 | `hasAuthDataRoot` | `uint8` | 1 if `authDataRoot` is present, otherwise 0. |
| 0 or 32 | `authDataRoot` | `uint8[32]` | The next block's `hashAuthDataRoot`. [^zip-0244] |

A message is malformed if `result` or `hasAuthDataRoot` is neither 0 nor 1,
`entriesCount` is greater than 4,000, or a root is not the canonical encoding
of a field element.

## Serving Roots

A node that sets `NODE_TREE_ROOTS` SHOULD answer each `gettreeroots` with a
`treeroots`, which is a refusal if it does not serve the request, and MUST NOT
send any other `treeroots`.

A node MUST NOT send entries unless its best chain has a block at height `end`
with hash `finalHash`. The entries MUST be the tree roots of at most `count`
consecutive blocks of that chain, starting at height `startHeight`. In the
entry for height `h`, `authDataRoot` MUST be present if and only if height
`h + 1` is at or after NU5 activation, and is then the `hashAuthDataRoot` of
that chain's block at height `h + 1`.

Computing `authDataRoot` reads the next block, so a node SHOULD bound the block
data it reads per request. A node that lacks a block it needs, or reaches that
bound, sends fewer entries.

## Requesting Roots

A node MUST NOT send `gettreeroots` on a connection while an earlier one on
that connection is unanswered, or after it stops waiting for an answer, since a
late answer cannot be matched to its request.

A node MUST ignore a `treeroots` received while no `gettreeroots` is
outstanding on the connection, MUST treat one with more than `count` entries as
malformed, and MUST treat one with no entries as a refusal.

## Verifying Roots

A node MUST NOT use the entry for the block at height `h` unless it has
authenticated that block and the header at height `h + 1`, for example against
its checkpoints, and:

- the root of each pool whose network upgrade (Sapling, NU5, or NU6.3) is not
  active at height `h` is the root of that pool's empty tree;
- if `h` is at or after Sapling activation and before Heartwood activation,
  `saplingRoot` equals the block's `hashFinalSaplingRoot`
  [^protocol-blockheader]; and
- if `h + 1` is at or after Heartwood activation, the header at height `h + 1`
  commits to the `hashChainHistoryRoot` of the chain history tree after the
  block, computed with the supplied roots as specified in ZIP 221 and ZIP 258
  [^zip-0221] [^zip-0258], or to all zero bytes if that header's block
  activates Heartwood. If the commitment is `hashBlockCommitments`, it is
  computed with `authDataRoot`, which MUST be present, as `hashAuthDataRoot`.
  [^zip-0244]

A node MUST still check the next block's authorizing data root against the
verified `authDataRoot`; if they differ, the block is invalid, not the entry.

## Peer Misbehaviour

A node MUST NOT answer a malformed `gettreeroots` with entries or use a
malformed `treeroots`, and MAY treat either as it treats other malformed P2P
messages. It MAY penalize a peer that sends an entry that fails the checks in
[Verifying Roots].

## Deployment

This ZIP requires no network upgrade.


# Rationale

`finalHash` binds a request to the requester's chain: a node on another chain
refuses, instead of sending roots that fail verification. Refusals let the
requester try another peer at once.

From NU5, a header commits to the preceding chain history tree together with
its own block's `hashAuthDataRoot`. [^zip-0244] Sending that digest lets a node
verify an entry before it has the next block, and tell an invalid entry from an
invalid block.

Bit 3 matches the Version 2 P2P protocol draft [^draft-p2p-v2], so a node can
advertise the same capability in both protocols.

4,000 entries take at most 516,004 bytes, within the 2 MiB message size limit.
[^zip-0204]


# Security and Privacy Considerations

A node uses an entry only after checking it against authenticated headers, so a
peer can only withhold or delay roots. A node that has stopped updating its
note commitment trees depends on peers serving roots until it obtains the trees
by other means.

A request does not bind the block at height `end + 1`, so a peer whose best
chain diverges there can send an entry for height `end` that fails the checks,
and be penalized.

A request reveals which heights a node is syncing, as `getheaders` and
`getdata` do.


# Test Vectors

The hashes and roots below are arbitrary bytes, except for the empty-tree
roots.

A `gettreeroots` payload for 2 blocks from height 100,000, with `finalHash`
bytes `00` to `1f`:

```
a0860100
000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
02000000
```

A `treeroots` payload with one entry of the empty-tree roots and no
`authDataRoot`:

```
00 01
fbc2f4300c01f0b7820d00e3347c8da4ee614674376cbc45359daa54f9b5493e
ae2935f1dfd8a24aed7c70df7de3a668eb7a49b1319880dde2bbd9031ae5d82f
ae2935f1dfd8a24aed7c70df7de3a668eb7a49b1319880dde2bbd9031ae5d82f
00
```

A `treeroots` payload with one entry of roots of bytes `01`, `02`, and `03`,
and `authDataRoot` bytes `04`:

```
00 01
0101010101010101010101010101010101010101010101010101010101010101
0202020202020202020202020202020202020202020202020202020202020202
0303030303030303030303030303030303030303030303030303030303030303
01
0404040404040404040404040404040404040404040404040404040404040404
```


# Reference Implementation

Zebra serves tree roots, and uses them for checkpoint sync with the option
`fast_tree_sync`. [^zebra] Its handling of timed-out requests does not yet
conform to [Requesting Roots].


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3] or later](protocol/protocol.pdf)

[^protocol-txnencoding]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.1: Transaction Encoding and Consensus](protocol/protocol.pdf#txnencoding)

[^protocol-blockheader]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.6: Block Header Encoding and Consensus](protocol/protocol.pdf#blockheader)

[^zip-0204]: [ZIP 204: Zcash P2P Network Protocol](zip-0204.rst)

[^zip-0221]: [ZIP 221: FlyClient - Consensus-Layer Changes](zip-0221.rst)

[^zip-0229]: [ZIP 229: Version 6 Transaction Format](zip-0229.md)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^zip-0258]: [ZIP 258: Deployment of the NU6.3 Network Upgrade](zip-0258.md)

[^draft-p2p-v2]: [Draft ZIP: Version 2 Zcash P2P Network Protocol](draft-arya-jvff-p2p-quic-transport.md)

[^zebra]: [Zebra pull request #12427: fast checkpoint sync with peer-supplied note commitment tree roots](https://github.com/ZcashFoundation/zebra/pull/12427)
