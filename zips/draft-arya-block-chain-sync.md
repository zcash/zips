    ZIP: XXX
    Title: Block Chain Synchronization
    Owners: Arya <arya@zfnd.org>
    Status: Draft
    Category: Network
    Created: 2026-08-06
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/352>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and
"RECOMMENDED" in this document are to be interpreted as described in BCP 14
[^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet" and "Testnet" are to be interpreted as described in
section 3.12 of the Zcash Protocol Specification. [^protocol-networks]

The term "block chain" in this document is to be interpreted as described in
section 3.3 of the Zcash Protocol Specification. [^protocol-blockchain]

The term "v2 protocol" in this document refers to the version 2 Zcash P2P
network protocol [^draft-p2p-v2]. The terms "peer" and "request stream", the
`get-headers`, `get-blocks`, `get-tx`, and `get-hashes` request stream
types, and the synchronization rules of that protocol, are to be interpreted
as defined there.

best chain
:   The consensus block chain that a node considers current, as determined by
    the consensus rules; its *tip* is its highest block.

validated tip
:   The highest block that a node has accepted into its best chain under the
    v2 protocol's synchronization rules.

synchronization strategy
:   A procedure by which a node advances its validated tip toward the network
    chain tip, using the request streams of the v2 protocol.

checkpoint
:   A (height, block hash) pair that a synchronizing node treats as
    authoritative for the block at that height.

checkpoint spacing
:   The height interval between a node's consecutive checkpoints.

hash chunk
:   A list of checkpointed block hashes covering a contiguous span of block
    heights, used as the unit of commitment and verification.

trusted commitment
:   Data, obtained by a node through a channel it already trusts (for
    example, compiled into its binary or supplied by local configuration),
    that binds the block hashes of its checkpoints — for example, a list of
    hash chunk hashes.


# Abstract

This ZIP recommends how a node synchronizes the block chain over the version
2 Zcash P2P network protocol. The v2 protocol defines the synchronization
primitives — `get-headers`, `get-blocks`, `get-hashes` — and the rules that
any use of them must satisfy; this ZIP recommends concrete *synchronization
strategies* satisfying those rules — headers-first synchronization and
*checkpointed synchronization* — and how a node selects between them.


# Motivation

The recommended checkpointed strategy exists because headers-first
synchronization is expensive for deep history. A serialized Zcash block
header is 1487 bytes on Mainnet and Testnet (including the Equihash
solution), and `get-headers` responses are limited to 160 headers, so
synchronizing the header chain from genesis at a Mainnet height of roughly
3.4 million blocks transfers about 5 GB of headers in more than 21,000
sequential round trips — and every one of those headers is transferred again
inside its full block. Nodes that ship with checkpoints do not need the
standalone header pass for the checkpointed span: the authenticity of a
downloaded block there is established by its hash chain to a checkpoint.
What they need from the network is block *hashes* — 32 bytes each, up to
50,000 per `get-hashes` response — as checkpoint data to verify and as
download handles for `get-blocks`.

Checkpoints themselves also motivate this design. The Zebra implementation
compiles in checkpoint lists that record a block hash at least every 400
blocks — several hundred kilobytes of hashes that grow with the chain and
must be regenerated for each release. Under the checkpointed strategy, a
node can instead compile in only a short list of hash chunk hashes (its
trusted commitment), obtain the chunks themselves from untrusted peers via
`get-hashes`, and verify them; the compiled-in data shrinks from hundreds of
kilobytes to a few kilobytes without weakening the trust model, since both
are trusted only because they are part of the binary.


# Specification

The synchronization rules of the v2 protocol [^draft-p2p-v2] apply to every
strategy below and are not restated here.

In addition to those rules, this ZIP recommends that a node SHOULD spread
block downloads across multiple peers rather than depending on one — this
turns the v2 protocol's stalling timeout into a recovery mechanism — and
SHOULD compare the chains offered by several peers (for example, by their
advertised `start_height` and by probing with `get-headers`) before
committing its download budget to one.

## Recommended Strategies

A node implements headers-first synchronization (the v2 protocol's fallback
rule requires it) and MAY implement checkpointed synchronization.

### Headers-First Synchronization

Headers-first synchronization is specified in the v2 protocol
[^draft-p2p-v2]. It is the full-validation strategy: it assumes no trusted
commitments, and every accepted block is validated under the consensus
rules.

### Checkpointed Synchronization

A node MAY synchronize the portion of the block chain covered by a trusted
commitment as follows. Per the v2 protocol, the commitment scheme — the
checkpoint spacing, the chunk boundaries, and the hash function used to
commit to each chunk — is local to the synchronizing node.

1. **Obtain checkpoint hashes.** The node requests the hashes of its
   checkpoint heights with `get-hashes` requests whose `stride` is its
   checkpoint spacing.

2. **Verify them against the trusted commitment.** The node reassembles the
   returned hashes into hash chunks and verifies each chunk against the
   trusted commitment. A response that does not match is discarded without
   a misbehavior penalty and the request MAY be retried with a different
   peer. Hashes are checkpoints only once verified.

3. **Obtain per-height hashes.** For each inter-checkpoint range being
   synchronized, the node requests the hashes of every block in the range
   with `get-hashes` requests with `stride = 1`. These hashes cannot be
   verified in isolation and serve only as download handles; a mismatch
   with the checkpoints is detected in step 5.

4. **Download blocks.** The node downloads the corresponding blocks with
   `get-blocks` requests, observing the v2 protocol's download parameters.

5. **Validate against the checkpoints.** For each inter-checkpoint range,
   the node verifies that the downloaded blocks form a hash chain: each
   block's header hashes to the hash by which the block was requested, each
   block's `hashPrevBlock` is the hash of its predecessor, the first
   block's `hashPrevBlock` is the checkpoint (or previously validated
   block) below the range, and the last block's hash is the verified
   checkpoint hash at the top of the range. A range that fails this check
   is discarded and MAY be re-fetched from different peers, without a
   misbehavior penalty; provably invalid blocks are scored as specified by
   the v2 protocol. The node then accepts the range's blocks, applying
   whatever abbreviated validation its local policy permits for
   checkpoint-authenticated blocks under the v2 protocol's validated
   advancement rule.

Steps 1–5 pipeline naturally: distinct ranges MAY be fetched and validated
concurrently from different peers, subject to the download parameters, and
contiguous validated ranges extend the node's validated tip in height
order.

## Strategy Selection

A synchronizing node SHOULD proceed as follows:

1. If it has a trusted commitment covering heights above its current
   validated tip, it SHOULD use checkpointed synchronization for the
   covered span, up to the reorganization margin of the synchronization
   rules: checkpointed synchronization strictly dominates headers-first
   synchronization over that span in bandwidth, round trips, and validation
   cost.

2. For heights above the span covered by its trusted commitment — including
   the entire chain, if it has no trusted commitment — it uses
   headers-first synchronization.

3. If a peer refuses `get-hashes` (with `REFUSED` or
   `UNSUPPORTED_STREAM_TYPE`), the node MAY retry with other peers, and
   SHOULD fall back to headers-first synchronization if too few of its
   peers serve `get-hashes` to sustain checkpointed synchronization.


# Security and Privacy Considerations

The security properties of the strategies are analyzed in the v2 protocol's
security considerations [^draft-p2p-v2]. Both recommended strategies satisfy
its synchronization rules, so the choice between them — including falling
back from checkpointed to headers-first synchronization — affects
performance, not the integrity of the resulting chain.

**Fingerprinting.** The heights and strides a node requests reveal its
checkpoint spacing and synchronization progress, which may identify its
implementation and version. This is comparable to the fingerprinting
surface of headers-first synchronization and of the `user_agent` field, and
carries the same mitigation: nodes concerned about it can align their
request patterns with common implementations.


# Deployment

This ZIP depends on the v2 protocol [^draft-p2p-v2], which specifies the
`get-hashes` request stream and the synchronization rules. No version gating
is required beyond the v2 protocol's own deployment: refusal of `get-hashes`
degrades gracefully to headers-first synchronization (see
[Strategy Selection](#strategyselection)).


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^draft-p2p-v2]: [Draft ZIP: Version 2 Zcash P2P Network Protocol](draft-arya-jvff-p2p-quic-transport.md)
