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
`get-headers`, `get-blocks`, `get-hashes`, `get-block-range`,
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

Checkpoints themselves also motivate this machinery. The Zebra
implementation compiles in known-hash lists covering every block — over 100
MB of hashes that grow with the chain — because the legacy protocol offered
no way to fetch and verify them. Under this ZIP, a binary compiles in only
the expected hashes of the list itself, chunked by height range (a few
kilobytes); the full known-hash list is then obtained verifiably from the
P2P network with `get-hashes`, as specified in
[Synchronization Data](#synchronizationdata).


# Specification

The synchronization rules of the v2 protocol [^draft-p2p-v2] apply to every
strategy below and are not restated here.

## Synchronization Data

A node's trusted commitment binds the data its strategies rely on:

- **Known-hash lists**, as pinned SHA-256 hashes of the list's *chunks*:
  each chunk is the canonical serialization of the `get-hashes` entries
  for a fixed height range. A node obtains the entries from its peers with
  `get-hashes` and verifies them by reassembling each chunk and comparing
  its hash against the commitment. The same bytes MAY instead be obtained
  as chunk artifacts from any source — bundled with the release,
  `get-object` requests to `NODE_SYNC_ARTIFACTS` peers, or out-of-band
  mirrors — accepted only if their hashes match the commitment. A
  verified known-hash list makes every listed hash an anchor, and its span
  metadata gives per-height sizes and costs for scheduling.

  The commitment MAY additionally bind a single SHA-256 hash of the
  *spentness hints*: the hint bits for every transparent output created
  at or below the final checkpoint (see
  [Spentness Hints](#spentnesshints)), serialized in canonical order,
  obtained like any artifact and verified whole against this hash. The
  hints are committed separately from the entry chunks — one hash rather
  than one per range — because they are a function of the final
  checkpoint height as well as of the chain: extending the commitment's
  coverage would change every per-range hint hash anyway, while the
  entry-chunk hashes stay stable. A commitment from an older release
  simply covers a lower final checkpoint: its hints remain valid for that
  shorter span, and the node synchronizes above it normally.
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
   remainder is re-requested from any peer, anchored at the next expected
   hash, as the v2 protocol's `get-block-range` truncation rules provide.

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
   commitment), anchoring each request's `final_hash` at a hash the node
   has already authenticated, so that entries describe known blocks
   rather than the responder's view of a best chain.
2. Verify the entries against headers that checkpointed synchronization has
   authenticated. Which check applies depends on what the block's header
   commits to at that height, which changes at Heartwood — *not* at NU5:

   - **Between Sapling activation and Heartwood activation**, the fourth
     header field (`hashFinalSaplingRoot`) is the block's Sapling note
     commitment tree root. Each supplied Sapling root is checked directly
     against it.
   - **From Heartwood activation**, ZIP 221 [^zip-0221] repurposes that
     field to carry the chain history root (`hashChainHistoryRoot`, and
     from NU5 `hashBlockCommitments`, which binds the chain history root
     together with the authorizing data commitment of ZIP 244
     [^zip-0244]). A direct comparison against a note commitment tree root
     is therefore *not* a valid check anywhere above Heartwood. The node
     instead rebuilds the chain history tree from the supplied roots and
     counts and checks the rebuilt values against each header. Each
     block's header commits to the history tree containing its *parent's*
     data, so an entry is verified only once the *following* block's
     header has been checked against it.
   - **Before a pool's activation** at the entry's height, the entry's
     root field is 32 zero bytes and its count is 0, as the v2 protocol
     requires [^draft-p2p-v2]; an entry that deviates fails verification.
   - **A root that no header commits to** at the entry's height is not
     verifiable by this procedure. The chain history tree leaf of ZIP 221
     binds the Sapling and (from NU5) Orchard roots, but defines no
     Ironwood field, so no header authenticates an Ironwood root.

3. A **verified** root replaces the recomputation: the node adopts the
   root, maintains tree *frontiers* only at strategy boundaries (where
   full per-block validation resumes), and stores what its serving
   obligations require. A node MUST NOT adopt a root that the procedure of
   step 2 has not verified against an authenticated header, and MUST
   recompute that pool's tree from the blocks' note commitments instead.
   Two cases in particular are not verified by an entry's own arrival:

   - Because verification above Heartwood runs one block behind, the
     highest entry of a response is unverified until the entry for the
     following block is obtained and checked against its header. A node
     either extends the requested range by one entry or holds the highest
     entry unadopted.
   - Entries MAY be obtained and verified in any order, but each entry is
     adopted only when its own check passes; an entry at the boundary of a
     range is not adopted merely because its neighbours were.

4. An entry that fails verification is discarded with a misbehavior penalty
   (per the v2 protocol); the node falls back to recomputing that span's
   trees locally.

No additional trust is involved: every adopted root is authenticated by a
header that is itself authenticated by the trusted commitment, and a root
that no header authenticates is never adopted.

**Frontier artifacts.** Adopting verified roots leaves the node without
the tree *frontiers* it needs to resume appending note commitments where
full validation begins. The trusted commitment MAY bind the hash of a
*frontier artifact* — the serialized Sapling, Orchard, and Ironwood
frontiers at the final checkpoint — obtained like any artifact. A
frontier whose recomputed root matches the root verified for that height
by the procedure above is adopted, so the binding itself carries no
trust: a wrong frontier fails the root comparison and the node falls
back to rebuilding that pool's tree from the span's note commitments.
The Ironwood frontier cannot be verified this way (no header
authenticates an Ironwood root); it is authenticated only by the
commitment's hash, or rebuilt from the pool's note commitments — a
bounded cost, since the pool postdates NU6.3 activation.

### Spentness Hints

After tree work is eliminated, the dominant remaining state cost of
committing historical blocks is random access: looking up and deleting each
transparent input's spent output, and inserting (and, under full
validation, membership-testing) each revealed nullifier. Spentness hints —
adapted from Bitcoin's SwiftSync [^swiftsync] — eliminate the random access
and make historical commits order-independent, at the cost of a small hint
bitmap bound by the trusted commitment, which vouches for its correctness
exactly as it vouches for the known block hashes: the bitmap is a
deterministic function of the chain, regenerable and auditable by any
synchronized node, and its pinned hash is updated by each release that
updates the checkpoints.
Hints apply only within the reach of the trusted commitment: a node MUST
NOT apply them above the final checkpoint.

**Transparent outputs.** The spentness hints (see
[Synchronization Data](#synchronizationdata)) carry one bit per
transparent output created at or below the *terminal height* — the final
checkpoint — in canonical order (by block height, then transaction index,
then output index): whether the output is still unspent at that height.
The `txouts` metadata of the verified entry chunks gives each height's bit
count, so a node can check the bitmap's length before downloading any
block bodies, and a work unit anywhere in the span can locate its first
bit without processing the blocks below it. During the span:

- An output hinted *unspent* is written to the transparent UTXO set as it
  is created — and, during the span, never looked up or deleted.
- An output hinted *spent* is never stored.
- Transparent inputs perform no lookup at all.

The constructed UTXO set is then exactly the set of outputs unspent at
the terminal height, without a single random read: every output hinted
spent is one the committed chain spends within the span, on the
authority of the commitment.

**Nullifiers.** The nullifier sets never shrink, so no hint is needed at
all: revealed nullifiers are simply inserted as they are encountered —
insertion is sequential-write work, not the random reads the hints exist
to remove — and per-spend membership tests below the final checkpoint
are vouched for by the trusted commitment. When backfilling below a
snapshot, the reconstructed sets are compared with the snapshot's at `H`
(see [Snapshot Synchronization](#snapshotsynchronization)).

**Value pools.** No lookups are needed for value tracking either: shielded
pool balances are sums of the blocks' value balance fields, which commute,
and the transparent pool balance at the terminal height is the sum of the
constructed UTXO set's amounts. These are consensus quantities: they MUST
be accumulated with checked arithmetic that detects overflow.

**What order-independence does and does not cover.** The state construction
above reads no state written by an earlier block, so the *construction* —
the UTXO set, the nullifier sets, and the value pool
totals — is order-independent, and blocks and ranges MAY be verified and
committed in any order within the span. The per-input reads and per-output
deletes disappear entirely.

Order-independence does not extend to consensus rules whose outcome is not
a function of the terminal totals. A node applying hints MUST account for
each of the following, either by checking it in height order or by
recording it as covered by the trusted commitment under the v2 protocol's
validated advancement rule:

- **Non-negative pool balances at every block.** ZIP 209 [^zip-0209]
  requires rejecting a block at which any chain value pool balance would
  become negative. A terminal total says nothing about a running balance
  that dips negative at an interior height and recovers; below the final
  checkpoint this rule is among those vouched for by the trusted
  commitment, and above it, blocks are committed in height order under
  full validation.
- **Coinbase maturity and the pre-NU5 shielded-coinbase rule**, which
  depend on the creation height and coinbase status of the *spent* output
  — exactly the lookup that hints remove. This is why hints are confined
  to the reach of the trusted commitment, where these per-spend checks
  are vouched for; above the final checkpoint, blocks are committed in
  height order with the lookups performed.

A node SHOULD obtain and verify the hint bitmap — its hash against the
commitment, and its bit count against the span's transparent output
total, summed from the verified entry chunks' `txouts` metadata — before
processing any block bodies with hints, so that an unavailable or
malformed bitmap costs nothing but its fetch; a bitmap that fails either
check is discarded and the span is synchronized without hints. A
published bitmap that is wrong despite matching its pinned hash is a
defect of the commitment itself, exactly as a wrong checkpoint hash would
be; because the bitmap is deterministic, publishers and third parties can
regenerate and cross-check it, and release processes SHOULD do so.

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
   of each pool; the chain history tree; and the chain value pool
   balances, which the node needs as the starting point for the
   pool-balance consensus rules above `H`.
   The parts that the chain commits to — the Sapling, Orchard, and Ironwood
   frontiers (via their header-committed roots) and the chain history tree
   (via `hashBlockCommitments` of the following block, ZIP 221 [^zip-0221])
   — MUST be verified against headers authenticated by the trusted
   commitment. Because the chain history tree at `H` is committed by the
   *following* block's header, the trusted commitment MUST authenticate
   the header at height `H + 1` for that verification to be possible; a
   commitment that stops at `H` leaves the chain history tree unverified,
   and the node MUST treat it as an uncommitted component. The parts the
   chain does not commit to (the transparent UTXO set, the nullifier sets,
   the Sprout tree, and the chain value pool balances) are authenticated
   solely by the manifest commitment, which therefore carries the same
   trust as the node's binary — the trust model of the checkpoints
   themselves.
4. **Begin operating at `H`**: validate blocks above `H` under the
   consensus rules (or checkpointed synchronization, where commitments
   reach above `H`), participate fully in relay, and serve the blocks it
   accumulates, advertising service flags as the v2 protocol requires of a
   node that lacks the complete chain [^draft-p2p-v2].
5. **Backfill in the background.** The node SHOULD backfill the history
   below `H` using checkpointed synchronization, at low priority, and
   advertise `NODE_NETWORK` when complete. On completion, backfill
   reconciles the snapshot's uncommitted components against the chain the
   node has just replayed. (The hint bitmap's bits are relative to the
   final checkpoint rather than `H`, so backfill below a snapshot
   proceeds without transparent hints; as background work, it is not on
   the critical path that hints exist to shorten.)

   The reconciliation discharges the snapshot's trust only to the extent
   that each component is actually compared, so each MUST be covered
   explicitly, and over complete entries: a comparison over outpoints
   alone would let a fabricated or amount-inflated UTXO entry pass
   unnoticed. Backfill therefore verifies, at `H`:

   - **The transparent UTXO set**, compared as complete entries — the
     outpoint, the value, the `scriptPubKey`, the creation height, and
     the coinbase flag, in a canonical encoding — between the set the
     replay constructs and the set the snapshot supplied, so that a
     phantom outpoint, an inflated value, or an altered script is caught.
   - **The nullifier sets**, by the same whole-value comparison per pool.
   - **The Sprout note commitment tree**, which no header commits to, by
     recomputing it from the JoinSplit note commitments of the replayed
     blocks and comparing the resulting root and frontier. Sprout is a
     closed pool of bounded size, so this is inexpensive.
   - **The chain value pool balances**, by recomputing them over the
     replayed span (with checked arithmetic, see
     [Spentness Hints](#spentnesshints)) and comparing them to the
     snapshot's.

   When all four check out, the snapshot's uncommitted components have been
   verified against the chain and the node's trust base is that of a fully
   synchronized node. Until they do, they remain trusted on the strength of
   the commitment. A mismatch in any of them means the snapshot was wrong:
   the node discards it and falls back to checkpointed synchronization from
   genesis. A node MAY instead operate indefinitely without deep history
   (pruned operation), never advertising `NODE_NETWORK`; such a node never
   discharges the snapshot's trust.

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
- **Exact blame.** A block failing its arrival check is attributable with
  certainty to the delivering peer, as is an artifact piece that fails
  its hash after being delivered entirely by one peer; both are handled
  per the v2 protocol's error and misbehavior rules, and the failed unit
  is reassigned elsewhere. A piece assembled from ranges delivered by
  several peers is *not* attributable when it fails its hash — the v2
  protocol forbids assigning a penalty in that case — so the node
  re-fetches the piece with each candidate peer serving it whole, which
  isolates a misbehaving peer; a scheduler that assigns each piece to a
  single peer (as the unit sizes above make natural) keeps blame exact
  from the start.

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
and the only data trusted without chain verification
(the spentness hints and the snapshot's uncommitted state components)
carries exactly the trust of
the binary that shipped the commitment, as the checkpoints already do.
The snapshot components' trust is discharged, for each component the
reconciliation of
[Snapshot Synchronization](#snapshotsynchronization) step 5 actually
compares, when backfill completes; a node that never backfills never
discharges it. The spentness hints stand or fall with the commitment
itself, exactly as the checkpoint hashes do, and are auditable in the
same way: the bitmap is a deterministic function of the chain that any
synchronized node can regenerate and cross-check. Malicious
synchronization data from peers produces failure, not
fraud: every verification failure is detected and routed around, and is
attributed and penalized where blame is provable under the v2 protocol's
misbehavior rules. (One failure is deliberately *not* attributed: an
assembled artifact
piece whose ranges came from several peers — see
[Download Scheduling](#downloadscheduling).)

**Serving capacity.** Snapshot-synchronized and pruned nodes cannot serve
deep history; if they became the majority, historical blocks and artifacts
could become scarce. The service flags let nodes advertise what they serve,
operators of full nodes are encouraged to retain `NODE_NETWORK` and
`NODE_SYNC_ARTIFACTS`, and artifacts remain regenerable by any backfilled
node and servable from out-of-band mirrors.

**Fingerprinting.** The heights, ranges, and units a node requests reveal
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
Distribution can be purely in-band: the known-hash list is reassembled
via `get-hashes`, and hint, frontier, and snapshot artifacts are served
by `NODE_SYNC_ARTIFACTS` peers via `get-object` — which requires that
seeders and any configured initial peers include such nodes.
Implementations MAY additionally bundle current artifacts with releases,
or serve them from out-of-band HTTPS mirrors interchangeably with
`get-object` peers.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^draft-p2p-v2]: [Draft ZIP: Version 2 Zcash P2P Network Protocol](draft-arya-jvff-p2p-quic-transport.md)

[^zip-0209]: [ZIP 209: Prohibit Negative Shielded Chain Value Pool Balances](zip-0209.rst)

[^zip-0221]: [ZIP 221: FlyClient - Consensus-Layer Changes](zip-0221.rst)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^assumeutxo]: [Bitcoin Core: assumeutxo design and usage](https://github.com/bitcoin/bitcoin/blob/master/doc/assumeutxo.md)

[^swiftsync]: [Ruben Somsen: SwiftSync — speeding up IBD with pre-generated hints](https://gist.github.com/RubenSomsen/a61a37d14182ccd78760e477c78133cd)

[^era1]: [era1 archival file format specification](https://github.com/eth-clients/e2store-format-specs/blob/main/formats/era1.md)
