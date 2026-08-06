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
`get-headers`, `get-blocks`, `get-tx`, `get-hashes`, `get-block-range`,
`get-tree-roots`, and `get-object` request stream types, the service flags,
and the synchronization rules of that protocol, are to be interpreted as
defined there.

best chain
:   The best valid block chain, as described in section 3.3 of the Zcash
    Protocol Specification [^protocol-blockchain]; its *tip* is its highest
    block.

validated tip
:   The highest block that a node has accepted into its best chain under the
    v2 protocol's synchronization rules.

synchronization strategy
:   A procedure by which a node advances its validated tip toward the network
    chain tip, using the request streams of the v2 protocol.

checkpoint
:   A (height, block hash) pair that a synchronizing node treats as
    authoritative for the block at that height.

trusted commitment
:   As defined in the v2 protocol's checkpointed synchronization rules
    [^draft-p2p-v2]; extended in this ZIP to also bind, for snapshot
    synchronization, a state snapshot manifest.

synchronization artifact
:   The immutable, content-addressed byte object served via `get-object`, as
    defined in the v2 protocol [^draft-p2p-v2] — for example, a known-hash
    chunk file or a snapshot piece.

known-hash list
:   The block hashes of every height of a span of the chain, together with
    per-block sync-cost metadata, bound by a trusted commitment (for
    example, as the pinned hashes of a list of chunk artifacts).

anchor
:   The anchor of a `get-block-range` stream, as defined in the v2 protocol
    [^draft-p2p-v2]; in this ZIP, always a block hash verified against a
    trusted commitment (directly, or via a verified artifact).

work unit
:   A contiguous range of blocks (or a byte range of an artifact) scheduled
    for download as one request stream.

snapshot
:   A serialization of a node's chain state at a *snapshot height* `H`,
    divided into a *manifest* and content-addressed *pieces*, allowing a new
    node to begin operating at height `H` without downloading or validating
    the chain below it.


# Abstract

This ZIP recommends how a node synchronizes the block chain over the version
2 Zcash P2P network protocol. The v2 protocol defines the synchronization
primitives and the rules that any use of them must satisfy; this ZIP
recommends concrete *synchronization strategies* satisfying those rules —
headers-first synchronization, *checkpointed synchronization* over anchored
block-range streams, optionally accelerated by verified note commitment
tree roots, and *snapshot synchronization*, which makes a new node
operational in minutes — together with a download scheduling discipline and
the policy for selecting between the strategies.


# Motivation

The v2 protocol [^draft-p2p-v2] deliberately specifies synchronization
primitives, the rules constraining their use, and only one baseline
procedure — headers-first synchronization. This ZIP recommends the concrete
procedures, because the difference between a naive procedure and a good one
is measured in days.

Three costs dominate initial synchronization, in ascending order of what
removing them is worth:

1. **Round trips and scheduling.** The legacy protocol transferred blocks in
   small per-request batches against individually requested hashes; at
   typical peer round-trip times this bounds throughput at a few hundred
   small blocks per second regardless of bandwidth. The v2 protocol's
   `get-block-range` removes the round trip from the inner loop: blocks
   stream continuously against a single verified anchor, and per-block
   download handles are unnecessary.

2. **Validation CPU.** Under checkpointed synchronization, proofs and
   signatures below the final checkpoint are vouched for by the trusted
   commitment, and the dominant remaining CPU cost — measured at roughly
   70% of block-commit time in the Zebra implementation — is recomputing
   the note commitment trees, leaf by leaf, only to learn per-block roots
   that are already bound by header commitments. Verified tree roots
   (`get-tree-roots`) eliminate that recomputation without adding trust.

3. **The historical data itself.** A new node operator's goal is a node at
   the tip; the chain's full history — hundreds of gigabytes — is the
   overwhelming share of bytes and time, and most operators need it only
   eventually (to serve peers) or never (pruned operation). Snapshot
   synchronization removes it from the critical path entirely: the node
   installs a verified state snapshot at a recent height and is operational
   in minutes, backfilling history in the background if it chooses.

Checkpoints themselves also motivate the artifact machinery. The Zebra
implementation compiles in known-hash lists covering every block — over 100
MB of hashes that grow with the chain — because the legacy protocol offered
no way to fetch and verify them. Under this ZIP, a binary need only pin the
SHA-256 hashes of the chunk artifacts (a few kilobytes); the artifacts
themselves are obtained and verified as specified in
[Synchronization Data](#synchronizationdata).


# Specification

The synchronization rules of the v2 protocol [^draft-p2p-v2] apply to every
strategy below and are not restated here.

## Synchronization Data

A node's trusted commitment binds the data its strategies rely on:

- **Known-hash lists**, as the pinned SHA-256 hashes of chunk artifacts.
  A node obtains the artifacts from any source — bundled with its release,
  `get-object` requests to `NODE_SYNC_ARTIFACTS` peers, or out-of-band
  mirrors — and accepts them only if their hashes match the commitment.
  Equivalently, a node MAY obtain the same data via `get-hashes` and verify
  it by reassembling the chunk artifacts and comparing their hashes. A
  verified known-hash list makes every listed hash an anchor, and its span
  metadata gives per-height sizes and costs for scheduling.
- **A snapshot manifest hash**, for snapshot synchronization (see
  [Snapshot Synchronization](#snapshotsynchronization)).

Chunk artifacts are deterministic functions of the chain, so any node that
has synchronized the covered span can regenerate them byte-identically and
serve them; artifact pieces SHOULD be no larger than the `get-object`
per-request maximum [^draft-p2p-v2] so each piece is independently fetchable
and verifiable.

## Recommended Strategies

A node implements headers-first synchronization (the v2 protocol's fallback
rule requires it) and MAY implement the others.

### Headers-First Synchronization

Headers-first synchronization is specified in the v2 protocol
[^draft-p2p-v2], where it is characterized as the baseline, full-validation
method. It is also the strategy for the chain near the tip, above the reach
of commitments, whatever strategy covered the history below.

### Checkpointed Synchronization

A node MAY synchronize the span of the block chain covered by a verified
known-hash list as follows:

1. **Obtain and verify the known-hash list** for the target span (see
   [Synchronization Data](#synchronizationdata)).

2. **Partition the span into work units**: contiguous block ranges, sized
   using the span metadata toward a byte target (see
   [Download Scheduling](#downloadscheduling)), each ending at a listed
   height. Any listed hash can end a unit, so unit boundaries are chosen
   freely — by bytes, not by a fixed block count — and each unit's
   request carries the byte target as its `max_bytes` bound.

3. **Stream each unit with `get-block-range`**, anchored at the unit's
   final hash. Each delivered block is verified on arrival under the v2
   protocol's `get-block-range` delivery rules [^draft-p2p-v2] and — as a
   cross-check — matched against the known-hash list at its height. A
   truncated or cancelled unit keeps its verified prefix, and the
   remainder is re-requested from any peer per the v2 protocol's
   resumption rule.

4. **Commit** each completed range in height order, applying whatever
   abbreviated validation local policy permits for
   checkpoint-authenticated blocks under the v2 protocol's validated
   advancement rule — with tree work eliminated where
   [Verified Tree Roots](#verifiedtreeroots) are available.

A node with a commitment that binds only spaced checkpoint hashes (rather
than a full known-hash list) applies the same procedure with units
anchored at checkpoint heights; interior per-block cross-checks and
advance sizing are then unavailable, but neither is needed — steps 2 and 3
already bound each unit in bytes and authenticate every delivered block
against its anchor.

### Verified Tree Roots

A node MAY avoid the note commitment tree recomputation that dominates the
CPU cost of committing checkpoint-authenticated blocks (see
[Motivation](#motivation)) by obtaining each historical block's tree roots
with `get-tree-roots` from `NODE_TREE_ROOTS` peers and verifying them
against header commitments:

1. For each block in the span, obtain the entry (Sapling, Orchard, and
   Ironwood roots, shielded transaction counts, and authorizing data
   commitment).
2. Verify the entries against headers that checkpointed synchronization has
   authenticated: from NU5, rebuild the chain history tree of ZIP 221
   [^zip-0221] from the supplied roots and counts, and check each block's
   `hashBlockCommitments` (which binds the history tree root and the
   authorizing data commitment, ZIP 244 [^zip-0244]) against the rebuilt
   values — each block's header commits to the history tree containing its
   parent's data, so verification runs one block behind the supplied
   entries. Between Sapling and NU5, check each supplied Sapling root
   directly against the header's `hashFinalSaplingRoot`. Before a pool's
   activation, the supplied root MUST be the empty tree root.
3. A verified root replaces the recomputation: the node adopts the root,
   maintains tree *frontiers* only at strategy boundaries (where full
   per-block validation resumes), and stores what its serving obligations
   require.
4. An entry that fails verification is discarded with a misbehavior penalty
   (per the v2 protocol); the node falls back to recomputing that span's
   trees locally.

No additional trust is involved: every adopted root is authenticated by a
header that is itself authenticated by the trusted commitment.

### Spentness Hints

After tree work is eliminated, the dominant remaining state cost of
committing historical blocks is random access: looking up and deleting each
transparent input's spent output, and inserting (and, under full
validation, membership-testing) each revealed nullifier. Spentness hints —
adapted from Bitcoin's SwiftSync [^swiftsync] — eliminate the random access
and make historical commits order-independent, at the cost of a small hint
artifact whose wrongness can only ever cause synchronization to fail, never
to accept invalid state.

The node draws a uniformly random secret *salt* for each synchronization
attempt, and maintains additive aggregates of salted hashes
(`H(salt ‖ item)`, summed with wrapping addition), one per aggregate
described below. An attacker who cannot predict the salt cannot craft items
whose hashes cancel.

**Transparent outputs.** A *spentness hint artifact* — bound by the trusted
commitment and fetched like any other artifact — carries one bit per
transparent output created in the synchronized span, in canonical order
(by block height, then transaction index, then output index): whether the
output is still unspent at the span's terminal height. During the span:

- An output hinted *unspent* is written to the transparent UTXO set as it
  is created — and, during the span, never looked up or deleted.
- An output hinted *spent* is never stored; its outpoint is added to the
  transparent aggregate.
- Every transparent input subtracts its referenced outpoint from the
  transparent aggregate. No lookup is performed.

At the terminal height, the transparent aggregate MUST be exactly zero:
the multiset of outputs hinted spent then equals the multiset of outputs
actually spent, so the constructed UTXO set is exactly the set of
never-spent outputs, without a single random read.

**Nullifiers.** The nullifier sets never shrink, so no per-item hint is
needed; what the hint mechanism provides instead is lookup-free
construction and verification:

- When synchronizing below a snapshot (backfill), the snapshot's nullifier
  set for each pool serves as the hint: the node adds every member of the
  snapshot set to that pool's aggregate — verifying while streaming it in
  sorted order that its elements are strictly increasing, hence distinct —
  and subtracts every nullifier revealed by the span's blocks. A zero
  aggregate at the snapshot height proves the nullifiers revealed in the
  span are exactly the snapshot set, and therefore that no nullifier was
  revealed twice.
- Without a snapshot, the node accumulates revealed nullifiers per pool
  and constructs each set in one batch (for example, by external sort) at
  the terminal height, checking distinctness in the same pass; per-spend
  membership tests below the final checkpoint are vouched for by the
  trusted commitment.

**Value pools.** No lookups are needed for value tracking either: shielded
pool balances are sums of the blocks' value balance fields, which commute,
and the transparent pool balance at the terminal height is the sum of the
constructed UTXO set's amounts.

Because no step reads state written by an earlier block, blocks and ranges
MAY be verified and committed in any order within the span, and the
per-input reads and per-output deletes disappear entirely. A nonzero
aggregate at the terminal height means the hints, the snapshot sets, or
the delivered blocks were wrong; the node discards the affected state and
falls back to checkpointed synchronization without hints.

### Snapshot Synchronization

A node with no chain state MAY become operational at a *snapshot height*
`H` in minutes, deferring or omitting the history below it:

1. **Obtain the manifest** whose SHA-256 hash is bound by the trusted
   commitment, from any source (`get-object`, mirrors, bundled). The
   manifest lists the snapshot's content-addressed pieces and their sizes.
2. **Fetch and verify the pieces** from
   `NODE_SYNC_ARTIFACTS` peers via `get-object` and/or out-of-band mirrors,
   scheduling them like any other work units (see
   [Download Scheduling](#downloadscheduling)); a piece is accepted only if
   its hash matches the manifest.
3. **Verify the state against the chain where possible.** The snapshot
   contains, at minimum: the transparent UTXO set; the Sprout, Sapling,
   Orchard, and Ironwood nullifier sets; the note commitment tree frontiers
   of each pool; the chain history tree; and the chain value pool balances.
   The parts that the chain commits to — the Sapling, Orchard, and Ironwood
   frontiers (via their header-committed roots) and the chain history tree
   (via `hashBlockCommitments` of the following block, ZIP 221 [^zip-0221])
   — MUST be verified against headers authenticated by the trusted
   commitment. The parts the chain does not commit to (the transparent UTXO
   set, the nullifier sets, the Sprout tree) are authenticated solely by
   the manifest commitment, which therefore carries the same trust as the
   node's binary — the trust model of the checkpoints themselves.
4. **Begin operating at `H`**: validate blocks above `H` under the
   consensus rules (or checkpointed synchronization, where commitments
   reach above `H`), participate fully in relay, and serve the blocks it
   accumulates, advertising service flags as the v2 protocol requires of a
   node that lacks the complete chain [^draft-p2p-v2].
5. **Backfill in the background.** The node SHOULD backfill the history
   below `H` using checkpointed synchronization, at low priority, and
   advertise `NODE_NETWORK` when complete. Backfill SHOULD use the
   snapshot's own sets as spentness hints (see
   [Spentness Hints](#spentnesshints)): when the aggregates check out at
   `H`, the node has *verified* the snapshot's transparent UTXO set and
   nullifier sets against the chain, discharging the only components of
   the snapshot that were trusted without chain verification. A node MAY
   instead operate indefinitely without deep history (pruned operation),
   never advertising `NODE_NETWORK`.

Snapshot heights SHOULD lie at least the v2 protocol's reorganization
margin below the network tip at the time the commitment is published, and
snapshot artifacts SHOULD be deterministic functions of the chain state at
`H`, so that any node of the same implementation that reaches `H` can
regenerate and serve them. A wrong or corrupted snapshot cannot cause
acceptance of a false state — a piece that does not match the manifest, or
a frontier that fails header verification, is rejected and the node falls
back to checkpointed synchronization; the commitment's only unverifiable
claims are those with no on-chain commitment (see step 3). (This is the trust
model of Bitcoin's assumeutxo [^assumeutxo] and of Ethereum's era archives
[^era1], with the difference that Zcash's header commitments make the tree
components independently verifiable.)

## Download Scheduling

Bulk download is a scheduling problem: divide known work across untrusted
peers of unknown and changing capacity, so that aggregate throughput
approaches the client's link capacity and no single peer can stall
progress. A node SHOULD apply the following discipline to bulk transfers
(`get-block-range` units and `get-object` pieces):

- **Work units of 16–64 MiB**, realized for block ranges by the request's
  `max_bytes` bound (with the known-hash span metadata, where available,
  used to plan unit boundaries in advance), and for artifacts by manifest
  piece sizes. Units near the commit frontier SHOULD be smaller, so the
  frontier advances promptly; deep lookahead units MAY be larger.
- **Pull-based assignment with per-peer budgets.** Maintain an estimate of
  each peer's delivery rate (for example, an exponentially weighted moving
  average); let each peer's connection pull the next unassigned unit
  whenever its in-flight bytes fall below roughly 2–3 seconds of its
  estimated rate. Fast peers thereby draw more work with no explicit
  balancing step.
- **Concurrency across peers.** Per-connection throughput is typically
  bounded by a single CPU core (see the v2 protocol's bulk transfer
  guidance [^draft-p2p-v2]); a node SHOULD download from at least 4–8
  peers concurrently, preferring `NODE_NETWORK` peers for deep history and
  respecting the flow control window guidance of the v2 protocol.
- **Bounded lookahead.** In-flight plus downloaded-but-uncommitted data
  SHOULD be bounded in bytes (a budget on the order of 256 MiB to 1 GiB),
  not in blocks; block counts calibrated to near-tip synchronization are
  meaningless across eras whose block sizes differ by three orders of
  magnitude.
- **Stall detection, twice over.** Cancel (with `CANCELLED`) and reassign a
  unit whose peer delivers no bytes for a few seconds, falls below an
  absolute configured rate floor, or sustains a rate far below the current
  peer median (for example, a quarter). Cancelled block-range units keep
  their verified prefix and are resumed per step 3 of
  [Checkpointed Synchronization](#checkpointedsynchronization).
- **End-game duplication.** When unassigned work runs out before the
  fastest peers do, assign remaining units redundantly to the fastest
  peers and cancel the losers; this bounds the tail of the download at the
  cost of at most one duplicate unit per peer.
- **Exact blame.** A block failing its arrival check, or an artifact piece
  failing its hash, is attributable with certainty to the delivering peer
  and is handled per the v2 protocol's error and misbehavior rules; the
  failed unit is reassigned elsewhere.

## Strategy Selection

A synchronizing node SHOULD proceed as follows:

1. A new node with no chain state, holding a snapshot commitment, SHOULD
   use snapshot synchronization: it is operational after transferring the
   snapshot (gigabytes) rather than the history (hundreds of gigabytes),
   and no other strategy changes what the node ultimately trusts.
2. For spans covered by known-hash commitments — backfill below a
   snapshot, or the whole chain when no snapshot is used — it SHOULD use
   checkpointed synchronization, with verified tree roots where peers
   serve them and spentness hints where its commitment (or snapshot)
   provides them.
3. Above the reach of its commitments, and within the reorganization
   margin of the tip, it uses headers-first synchronization.
4. Every strategy degrades toward headers-first synchronization when its
   prerequisites are unavailable (no artifacts obtainable, no serving
   peers, verification failures), per the v2 protocol's fallback rule;
   scarcity of `NODE_TREE_ROOTS` or `NODE_SYNC_ARTIFACTS` peers slows
   synchronization but never blocks it.


# Security and Privacy Considerations

The security properties of the strategies are analyzed in the v2 protocol's
security considerations [^draft-p2p-v2]. All strategies here satisfy its
synchronization rules, so the choice between them — including every
fallback — affects performance, not the integrity of the resulting chain.
The trust base is unchanged by acceleration: every accelerating input is
either authenticated against the chain or bound by the trusted commitment,
and the only data trusted without chain verification (the snapshot's
uncommitted state components) carries exactly the trust of the binary that
shipped the commitment, as the checkpoints already do — and even that trust
is discharged when hint-verified backfill completes (see
[Spentness Hints](#spentnesshints)). Malicious synchronization data
produces failure, not fraud: every verification failure is detected,
attributed, penalized, and routed around.

**Serving capacity.** Snapshot-synchronized and pruned nodes cannot serve
deep history; if they became the majority, historical blocks and artifacts
could become scarce. The service flags let nodes advertise what they serve,
operators of full nodes are encouraged to retain `NODE_NETWORK` and
`NODE_SYNC_ARTIFACTS`, and artifacts remain regenerable by any backfilled
node and servable from out-of-band mirrors.

**Fingerprinting.** The heights, strides, and units a node requests reveal
its implementation, configuration, and synchronization progress. This is
comparable to the fingerprinting surface of headers-first synchronization
and of the `user_agent` field, and carries the same mitigation: nodes
concerned about it can align their request patterns with common
implementations.


# Deployment

This ZIP depends on the v2 protocol [^draft-p2p-v2], which specifies the
request streams, service flags, and synchronization rules used here. No
version gating is required beyond the v2 protocol's own deployment: each
primitive is refused by nodes that do not serve it, and every strategy
degrades gracefully (see [Strategy Selection](#strategyselection)).
Implementations SHOULD bundle current chunk artifacts and snapshot
manifests with releases while serving peers are scarce; the same
content-addressed artifacts MAY be served by out-of-band HTTPS mirrors
interchangeably with `get-object` peers.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^draft-p2p-v2]: [Draft ZIP: Version 2 Zcash P2P Network Protocol](draft-arya-jvff-p2p-quic-transport.md)

[^zip-0221]: [ZIP 221: FlyClient - Consensus-Layer Changes](zip-0221.rst)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^assumeutxo]: [Bitcoin Core: assumeutxo design and usage](https://github.com/bitcoin/bitcoin/blob/master/doc/assumeutxo.md)

[^swiftsync]: [Ruben Somsen: SwiftSync — speeding up IBD with pre-generated hints](https://gist.github.com/RubenSomsen/a61a37d14182ccd78760e477c78133cd)

[^era1]: [era1 archival file format specification](https://github.com/eth-clients/e2store-format-specs/blob/main/formats/era1.md)
