    ZIP: XXX
    Title: Erasure-Coded Block Propagation
    Owners: Arya <arya@zfnd.org>
    Status: Draft
    Category: Network
    Created: 2026-08-12
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/352>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and
"RECOMMENDED" in this document are to be interpreted as described in BCP 14
[^BCP14] when, and only when, they appear in all capitals.

The term "v2 protocol" in this document refers to the version 2 Zcash P2P
network protocol [^draft-p2p-v2]. The terms "peer", "request stream",
"announcement stream", "compact block", and "misbehavior penalty", the
`get-blocks` and `get-tx` request stream types, and the relay rules of that
protocol, are to be interpreted as defined there.

source symbol
:   One of `K` equal-sized substrings of a serialized block (the last
    zero-padded), from which coded symbols are generated.

coded symbol
:   A symbol generated from a block's source symbols by an erasure code;
    under a *systematic* code, the first `K` coded symbols are the source
    symbols themselves, and subsequent symbols are *repair symbols*.

piece
:   The relay unit of this protocol: one coded symbol together with the
    metadata needed to place and (where possible) authenticate it.

decode
:   Recovery of the `K` source symbols — and hence the serialized block —
    from any sufficiently large set of distinct coded symbols.


# Abstract

This ZIP sketches an extension to the v2 Zcash P2P protocol that
disseminates newly mined blocks as erasure-coded *pieces*: a node
reconstructs a block from any sufficiently large subset of distinct pieces,
gathered concurrently from all of its peers, instead of obtaining the block
(or its missing transactions) from one responder. It surveys the design
space — random linear network coding, fountain codes, and the piece-based
dissemination of deployed systems — selects a systematic RaptorQ code as the
recommended construction, and defines the new stream types, authentication
rules, and misbehavior handling the extension needs. A final section relates
this design to DAG-structured synchronization of the chain's content-addressed
artifacts.


# Motivation

Compact block relay (BIP 152 [^bip-0152], as adapted by the v2 protocol
[^draft-p2p-v2]) removes most of a block's bytes from the critical path, but
it retains a structural dependency on individual responders:

1. **Single-responder reconstruction.** A node that cannot reconstruct a
   compact block — because transactions are missing from its mempool — must
   round-trip `get-tx` requests to a peer that has the block, and a slow or
   withholding peer stalls that branch of relay until the node retries
   elsewhere. Relay latency is dominated by these tails, and block
   withholding by the announcing peer costs the victim a timeout.

2. **All-or-nothing transfer.** Every byte of a block a node receives from a
   peer duplicates every byte received from any other peer. Bandwidth spent
   on concurrent downloads from several peers — the natural defense against
   withholding — is wasted in the common case.

3. **Miner latency sensitivity.** Propagation latency translates directly
   into orphan rate, which taxes small miners disproportionately, and a
   trailing-finality layer [^draft-trailing-finality] adds a second latency-
   sensitive object class (BFT proposals referencing recent blocks) to the
   same network.

Erasure coding removes the dependency: if a block is expanded into coded
symbols such that *any* `K` distinct symbols (plus a small overhead)
reconstruct it, then every peer can contribute useful bytes, no single peer
is depended upon for any specific byte, and withholding by any subset of
peers only reduces the aggregate rate. The ideas the design space draws on:

- **Random linear network coding (RLNC)** [^ho-rlnc]: relays transmit random
  linear combinations of the symbols they hold, so intermediate nodes
  *recode* rather than merely forward, achieving multicast capacity without
  coordination. Its costs are per-symbol coefficient vectors, Gaussian
  elimination at decode, and — most acutely for an adversarial P2P setting —
  the difficulty of authenticating recoded symbols, which requires
  homomorphic signatures or discarding authentication until decode.
- **Fountain codes — Raptor/RaptorQ** (RFC 5053 [^rfc5053], RFC 6330
  [^rfc6330]): rateless, systematic, linear-time codes that recover `K`
  source symbols from any `K + ε` received symbols with overwhelming
  probability (`ε` = 2 gives failure probability below 10^-6). Symbols are
  identified by a public 24-bit identifier, so any node holding the block
  can deterministically regenerate any symbol — no per-symbol trust in the
  encoder is needed.
- **Solana's Turbine shreds** [^turbine]: blocks are sharded into
  erasure-coded *shreds*, each individually authenticated (Merkle root
  signed by the slot leader), and fanned out through a tree so each node
  uploads only a fraction of the block. The individually-authenticated-piece
  idea transfers to Zcash; the leader signature does not (proof-of-work
  blocks have no accountable proposer before the block is complete).
- **Streamed partial blocks ("flashblocks")** [^flashblocks]: a block is
  streamed in increments as it is built, so validation and propagation
  overlap block construction. For proof-of-work block *discovery* this is
  inapplicable — a block does not exist until its header meets the target —
  but the overlap idea reappears here as decode-as-you-receive and, for the
  trailing-finality layer, as streaming BFT proposal bodies.

This ZIP is deliberately staged: a first deployment that needs no consensus
change, and a second stage, requiring a header commitment, that reaches
per-piece authentication.


# Specification [specification]

## Piece Construction

For a block with serialized size `k` bytes, let `T` be the symbol size and
`K = ceil(k / T)` the number of source symbols. The block's coded symbols are
generated by the systematic RaptorQ code of RFC 6330 [^rfc6330] with the
block's serialized bytes as the source object, using a single source block
and symbol size `T = 1152` bytes.

A *piece* is encoded as:

| Size   | Field        | Description                                                     |
|--------|--------------|-----------------------------------------------------------------|
| 32     | `block_hash` | Hash of the block the piece belongs to.                         |
| 4      | `block_size` | Serialized size `k` of the block in bytes (`uint32`, little-endian). |
| 3      | `symbol_id`  | RFC 6330 FEC Payload ID: the 24-bit Encoding Symbol ID (`uint24`, little-endian). |
| `T`    | `symbol`     | The coded symbol.                                               |

`block_size` determines `K`; symbols with `symbol_id < K` are source
symbols (a byte range of the block), and higher identifiers are repair
symbols. Any node that holds the full block can regenerate any symbol, so
every relaying node is a potential source of fresh repair symbols without
having received them — the recoding benefit RLNC seeks, obtained without
coefficient vectors or homomorphic authentication, at the cost that only
nodes holding the *complete* block (not merely some pieces) can generate
new symbols.

A node SHOULD begin decoding as symbols arrive and SHOULD cancel its
remaining piece subscriptions for a block (see below) as soon as decoding
succeeds.

## Stream Types

Two stream types are added to the v2 protocol's registry (identifiers
provisional, coordinated with [^draft-trailing-finality]):

### `get-pieces`

Stream type: `0x0C` (bidirectional request stream)

**Request:**

| Size   | Field        | Description                                                      |
|--------|--------------|------------------------------------------------------------------|
| 32     | `block_hash` | Hash of the requested block.                                     |
| 4      | `first_id`   | First requested Encoding Symbol ID (`uint32`, little-endian; MUST NOT exceed 2^24 − 1). |
| 4      | `max_symbols`| Maximum number of symbols requested (`uint32`, little-endian). MUST NOT exceed 4,096. |

**Response:** `0x00` followed by pieces (each encoded as above) with
consecutive `symbol_id` starting at `first_id`, or `0x02` (not found) if the
responder does not hold or cannot regenerate symbols of that block. The
responder MAY finish early; the requester re-requests a disjoint identifier
range — typically from another peer — for the shortfall.

The request uses fixed-length integer encodings and is smaller than a Tor
cell body, per the v2 protocol's length-leakage discipline [^draft-p2p-v2].

### Piece announcements

Stream type: `0x14` (unidirectional announcement stream)

Each record on the stream carries one piece. A node advertises willingness
to receive unsolicited pieces via the `pieces` field of its `init` record
(one byte, 0 or 1, appended to the `init` record from the protocol version
deploying this extension). A node MUST NOT open a piece announcement stream
to a peer that set `pieces = 0`.

To bound duplication without coordination, a sender SHOULD send piece
`symbol_id = s` of a block to peer `p` only if
`(s mod N) = (H(nonce_p) mod N)`, where `N` is the sender's count of
piece-subscribed peers and `H(nonce_p)` is a hash of the peer's handshake
nonce: each subscribed peer then receives a distinct symbol stripe, and the
stripes jointly cover the identifier space. Receivers make no assumption
about which symbols arrive from whom.

## Interaction with Compact Block Relay

Piece relay complements rather than replaces compact block relay: a node
with a well-synchronized mempool reconstructs from a compact block using no
block-body bandwidth at all, which coding cannot beat. A node SHOULD treat
a compact block announcement and piece arrival as racing sources for the
same block, use whichever completes first, and cancel the loser. A node
that has failed compact-block reconstruction SHOULD prefer `get-pieces`
spread across several peers over `get-tx` to the announcing peer when the
missing set is large.

## Authentication and Misbehavior

**Stage 1 (no consensus change).** A piece is not verifiable in isolation:
nothing binds `symbol` to `block_hash` until the block is decoded and
hashed. The v2 protocol's attribution rules for multi-source assembly
[^draft-p2p-v2] therefore apply unchanged: a node MUST NOT assign a
misbehavior penalty when a block assembled from pieces delivered by more
than one peer fails its hash check, SHOULD discard the pieces and fall back
to `get-blocks` from a single peer (which is attributable), and MUST bound
the memory committed to undecoded pieces per block and per peer. Source
symbols of a *systematic* code partially mitigate garbage injection: a
decoded-then-failed block can be re-checked symbol-by-symbol against the
re-encoding of the correct block once obtained, and peers that supplied
wrong symbols SHOULD then incur the misbehavior penalty for provably
misdelivered data, since the correct symbol at each identifier is
deterministic.

**Stage 2 (header commitment).** A future network upgrade MAY commit, via a
ZIP 244-style commitment in the block header, to the Merkle root of the
block's coded symbols up to a fixed repair bound. Each piece then carries a
Merkle path, is verifiable against the (proof-of-work-checked) header
before decode — the property Turbine obtains from leader signatures —
and misdelivery becomes attributable per piece. The stage-1 wire format
reserves no bytes for this; stage 2 is a new piece encoding under a new
protocol version.

## DAG Synchronization [dagsynchronization]

Historical synchronization already has a content-addressed structure: the
sync ZIP [^draft-sync] names chunk artifacts and snapshot pieces by hash,
and `get-object` fetches them from any holder. That is a DAG — commitments
name manifests, manifests name pieces — traversed today in a fixed pattern.
Two generalizations are worth specifying once piece relay exists:

- **Coded artifacts.** Applying the same RaptorQ construction to
  synchronization artifacts makes every artifact fetchable as symbol ranges
  from any subset of holders, subsuming `get-object`'s byte-range
  re-requesting and removing the incentive to schedule whole pieces against
  single peers. Artifact hashes already authenticate the decoded object;
  stage-1 attribution rules carry over.
- **DAG-addressed chain sync.** Naming each object (header ranges, block
  bodies, tree-root batches) by hash in a manifest DAG rooted in a trusted
  commitment would let a synchronizing node fetch the entire history as one
  work-stealing traversal — any peer, any subtree, any order — with
  verification purely local to each edge. This subsumes the checkpointed
  strategy's linear work queue and is the natural end state of the sync
  ZIP's artifact machinery; it is left to a successor ZIP.

Mempool-level DAG constructions (Narwhal-style DAG mempools
[^narwhal]) couple data availability to consensus and are out of scope for
a proof-of-work relay network; they may become relevant to the
trailing-finality layer's proposal dissemination.


# Rationale

- **RaptorQ over RLNC:** deterministic public symbol generation preserves
  the v2 protocol's misbehavior model (provable misdelivery, stage 2) and
  costs no per-symbol coefficients; recoding-at-relays is recovered for
  complete-block holders, which in block relay is every node within one
  decode of the frontier.
- **Symbol size 1152:** small enough that a piece (1,191 bytes) fits a
  single QUIC packet on common paths and wastes at most one symbol of
  padding on small blocks; large enough that a 2 MB block is under 1,800
  symbols, keeping identifier and Merkle (stage 2) overheads negligible.
- **Striped announcement fanout:** approximates Turbine's tree without
  membership or signatures — the sender-local stripe rule needs no
  agreement between senders, and over-coverage from overlapping stripes is
  the redundancy that tolerates withholding.


# Security and Privacy Considerations

Stage 1 trades attribution for latency on the piece path and contains the
loss: assembly failure is detected (hash check), bounded (per-block and
per-peer piece budgets), non-fatal (fallback to attributable `get-blocks`),
and partially recoverable after the fact (systematic symbol re-check).
An attacker can waste a victim's bandwidth and memory up to the budgets by
sending garbage repair symbols, and can no longer stall relay by
withholding, which is the intended trade. Piece traffic is uniform-size
records on a dedicated stream type, adding no length-leakage surface beyond
the v2 protocol's analysis [^draft-p2p-v2]; the timing of piece arrival
reveals block-frontier position, comparable to block announcements today.


# Deployment

This extension is gated on a protocol version to be assigned per ZIP 204
[^zip-0204-assignment] and is independent of network upgrade activation.
Support is additionally advertised by a service flag (`NODE_CODED_RELAY`,
bit 6 proposed) so that piece-capable peers can find one another during
partial deployment. Stage 2 is contingent on a header-commitment network
upgrade and is not scheduled by this ZIP.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^draft-p2p-v2]: [Draft ZIP: Version 2 Zcash P2P Network Protocol](draft-arya-jvff-p2p-quic-transport.md)

[^draft-sync]: [Draft ZIP: Block Chain Synchronization](draft-arya-block-chain-sync.md)

[^draft-trailing-finality]: [Draft ZIP: Trailing Finality over the v2 P2P Protocol](draft-arya-trailing-finality.md)

[^zip-0204-assignment]: [ZIP 204: Zcash P2P Network Protocol — Assigning Protocol Versions to Network Upgrades](https://zips.z.cash/zip-0204#assigning-protocol-versions-to-network-upgrades)

[^bip-0152]: [BIP 152: Compact Block Relay](https://github.com/bitcoin/bips/blob/master/bip-0152.mediawiki)

[^rfc5053]: [RFC 5053: Raptor Forward Error Correction Scheme for Object Delivery](https://www.rfc-editor.org/rfc/rfc5053.html)

[^rfc6330]: [RFC 6330: RaptorQ Forward Error Correction Scheme for Object Delivery](https://www.rfc-editor.org/rfc/rfc6330.html)

[^ho-rlnc]: [T. Ho et al. A Random Linear Network Coding Approach to Multicast. IEEE Transactions on Information Theory, 2006.](https://doi.org/10.1109/TIT.2006.881746)

[^turbine]: [Solana Documentation: Turbine Block Propagation](https://docs.anza.xyz/consensus/turbine-block-propagation)

[^flashblocks]: [Flashblocks: streamed partial block construction (Base / OP Stack)](https://docs.base.org/chain/flashblocks)

[^narwhal]: [G. Danezis et al. Narwhal and Tusk: A DAG-based Mempool and Efficient BFT Consensus. EuroSys 2022.](https://doi.org/10.1145/3492321.3519594)
