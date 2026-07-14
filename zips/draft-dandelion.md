ZIP: Unassigned
    Title: Dandelion++ Transaction Propagation for Zcash P2P Nodes
    Owners: y4ssi <y4ssi@zodl.com>
    Status: Draft
    Category: Network
    Created: 2026-07-09
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/TODO>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and "RECOMMENDED"
in this document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

**Stem phase:** The unicast relay phase of the Dandelion++ protocol [^DPPLUSPLUS] in
which a transaction is forwarded to a single randomly-selected peer per epoch before
entering the fluff phase.

**Fluff phase:** The standard flood-broadcast phase of transaction propagation that
follows the stem phase.

**Stem peer:** The single P2P peer to which a Dandelion++ node relays stem-phase
transactions during a given epoch.

**IP-to-transaction correlation:** The ability of a network observer to determine
which IP address originated a given transaction by observing when and where the
transaction first appeared on the P2P network.


# Abstract

This ZIP specifies how Zcash full nodes SHOULD implement Dandelion++ [^DPPLUSPLUS]
transaction propagation. In Dandelion++, a newly-received transaction first travels
through a randomly-selected "stem" of peers (unicast per epoch) before entering a
standard flood broadcast ("fluff" phase). This makes it significantly harder for
network observers to determine which node originated a transaction, reducing
IP-to-transaction correlation.

This ZIP covers only the **full-node P2P relay behavior** (sometimes called
"Component B"). A companion mechanism for wallets to submit transactions directly
to a node via P2P rather than through a compact-block server is described in
draft-dandelion-wallet (PR [#1330](https://github.com/zcash/zips/pull/1330)). [^draft-dandelion-wallet]


# Motivation

Currently, Zcash transactions are immediately flood-broadcast to all connected peers
the moment they enter a node's mempool. A passive network adversary can observe the
timing of transaction appearances at many vantage points to identify the originating
node with high confidence, even for shielded transactions whose content is cryptographically
protected.

Dandelion++ addresses this by introducing an intermediate "stem" phase during which
the transaction is relayed to only one peer. The originating node is hidden in the
anonymity set of all nodes along the stem path.


# Requirements

1. Each Dandelion++ node MUST maintain an **epoch** with a randomly-chosen duration
   in the range [600, 720] seconds (10 minutes ± 120 second jitter).

2. At the start of each epoch, the node MUST select a single **stem peer** uniformly
   at random from its currently-connected outbound peers. If no outbound peers are
   available, the node operates in fluff mode for that epoch.

3. For each transaction received locally (via RPC, direct P2P submission, or
   relayed from a peer), the node MUST:

   a. Enter the transaction into **stem phase**: route it exclusively to the stem peer
      using a unicast P2P message.
   b. Record the stem-phase start time. If the transaction has not entered fluff
      within **30 seconds**, the node MUST promote it to fluff phase.
   c. If the stem peer disconnects or becomes unavailable before the transaction
      is acknowledged, the node MUST immediately promote the transaction to fluff
      phase rather than silently dropping it.

4. During stem phase, the node MUST NOT advertise the transaction to any other peer.
   Specifically:

   a. The transaction MUST NOT be included in responses to `mempool` P2P requests
      from remote peers.
   b. The transaction MUST NOT be returned by any RPC that exposes mempool contents
      (e.g. `getrawmempool`, `getrawtransaction` with `verbose=0` on unconfirmed
      transactions) until it enters fluff phase.

5. Once the transaction enters fluff phase, it MUST be broadcast normally using
   the existing `inv`/`tx` flood mechanism.


# Specification

## Epoch management

A new **epoch** begins immediately when the node starts and whenever the previous
epoch expires. The epoch duration is:

```
epoch_duration = BASE_EPOCH_DURATION + uniform_random(0, MAX_EPOCH_JITTER)
```

where `BASE_EPOCH_DURATION` = 600 s and `MAX_EPOCH_JITTER` = 120 s.

The stem peer for an epoch is selected uniformly at random from the addresses of
currently-connected outbound peers at the moment the epoch begins. If no outbound
peers are connected, the stem peer is `None` and the node operates in **fluff mode**
for the entire epoch (all transactions are immediately flood-broadcast).

## Stem-phase forwarding

When a node enters a new transaction into stem phase, it SHOULD send the transaction
identifier to the stem peer using the standard `inv` P2P message with type
`MSG_TX`. The stem peer is expected to request the full transaction via `getdata`
and continue the stem relay using its own stem peer for the current epoch.

> **Note:** The Dandelion++ paper defines a separate "unadvertised `tx`" convention
> (sending the raw `tx` message to the stem peer without a prior `inv`) as a
> signal that the transaction should be treated as stem-phase by the recipient.
> This convention is OPTIONAL under this ZIP. Nodes that do not implement it
> MUST fall back gracefully to standard `inv` forwarding, which provides the
> same privacy property at the forwarding node. A future ZIP MAY standardize
> the unadvertised-`tx` convention once implementations converge.

## Stem-phase mempool filtering

Implementations MUST ensure that stem-phase transactions are not observable by
remote peers before entering fluff. This applies to:

1. Responses to `mempool` P2P requests — the node MUST filter stem-phase
   transaction IDs from the list returned to any remote peer.

2. Transaction-related RPCs — the node SHOULD suppress stem-phase transactions
   from any RPC that returns mempool contents. Implementations MAY defer this
   to a subsequent release.

## Fail-closed routing

If the stem peer is not reachable at the time a stem-phase transaction should be
forwarded (e.g. the peer has been evicted from the ready set), the node MUST
promote the transaction to fluff immediately. The node MUST NOT silently discard
the transaction, and MUST NOT fall back to routing to a different peer without
updating the propagation state (which would result in the transaction being
advertised to a non-stem peer during what the node still records as stem phase).

## Fluff phase

After the 30-second stem timeout, or when a stem-peer failure triggers early
promotion, the transaction enters fluff phase and MUST be broadcast to all
connected peers using the normal `inv` + `getdata` + `tx` mechanism.


# Rationale

## Why per-epoch rather than per-transaction stem peer selection?

The Dandelion++ paper recommends per-transaction selection for maximum anonymity.
However, per-epoch selection has an important advantage: an adversary who controls
multiple peers cannot learn which peer consistently forwards a given sender's
transactions by comparing which peer they saw first for each transaction. With
per-epoch selection, an adversary learns only one stem identity per 10-minute window.
The privacy trade-off is well-documented in [^DPPLUSPLUS].

## Why 30 seconds for the stem timeout?

The Dandelion++ paper recommends a stem timeout in the range 30–60 seconds. The
lower bound is used here to minimize transaction propagation delay under normal
conditions. If a transaction is rejected by the stem peer (e.g. due to policy),
the 30-second timeout ensures it is not silently dropped.

## Why not a new P2P message type?

Defining a new P2P message type would require a network upgrade and coordination
across all Zcash full node implementations. Using the existing `inv` message for
stem forwarding achieves the same routing behavior with no protocol-level changes,
allowing incremental deployment. Nodes that do not implement this ZIP process the
`inv` normally and flood-broadcast the transaction, which is the safe fallback.


# Reference Implementation

## Component B — Full-node Dandelion++ relay (Zebra)

Reference implementation proposed upstream:
[zcashfoundation/zebra#10928](https://github.com/zcashfoundation/zebra/pull/10928).

Verified end-to-end on a 3-node regtest network (2026-07-09). See
`docs/dandelion-e2e-regtest.md` in that PR for the complete test procedure,
build flags, and result evidence (txid accepted, 30 s stem-retention confirmed,
adversary observer saw no `inv` during the stem window).

Implemented:

- Epoch management with 10 min base + up to 2 min jitter
  (`zebra-network/src/dandelion/epoch.rs`)
- Per-transaction propagation state, 30 s stem timeout, `stem_txids()`
  (`zebra-network/src/dandelion/state.rs`)
- Fail-closed stem unicast via `PeerSet::route_to_peer` with `PeerError::NoReadyPeers`
  (`zebra-network/src/peer_set/set.rs`)
- Gossip task wired into `zebrad` startup; `MempoolChangeKind::StemAdded` routes
  locally-submitted txs through stem; peer-relayed `Added` goes directly to fluff
  (`zebrad/src/components/mempool/dandelion_gossip.rs`, `mempool.rs`)
- Phase 4 — stem-phase hiding from all exposure surfaces:
  - `MempoolTransactionIds` P2P response (inbound handler)
  - `TransactionsById` P2P getdata handler (adversary cannot fetch full tx during stem)
  - `getrawmempool` RPC (verbose and non-verbose)
  - `getrawtransaction` RPC
  - Zebra indexer gRPC `mempool_change` stream (suppresses `StemAdded` events;
    Zaino/lightwalletd only sees the tx once it enters fluff)
- 10 unit tests (epoch, propagation state, Phase 4 filter) + 2 routing tests

Remaining (optional / future coordination): unadvertised-`tx` wire convention
(requires other implementations to recognize the signal).

## Component A — Wallet direct P2P submission

Proposed upstream to the Zcash wallet SDKs:

- **Android**: [zcash/zcash-android-wallet-sdk#2010](https://github.com/zcash/zcash-android-wallet-sdk/pull/2010)
- **iOS (Swift)**: [zcash/zcash-swift-wallet-sdk#1804](https://github.com/zcash/zcash-swift-wallet-sdk/pull/1804)

Both SDKs add a `DandelionSubmitConfig` opt-in (`DirectP2P` / `directP2P`) that:
1. Resolves peers via the Zcash mainnet DNS seeders (same set as Zebra defaults).
2. Opens a TCP connection directly to a full node.
3. Performs the Zcash P2P version/verack handshake.
4. Sends the raw `tx` message **without a prior `inv`** (the unadvertised-tx
   convention described in §Stem-phase forwarding above).
5. Disconnects.

Chain synchronisation always uses the lightwalletd endpoint regardless of this setting.
A fallback to lwd submission is available when all P2P peers are unreachable.

The wallet-side specification (peer discovery, tx message format, error handling) is
in the companion draft (PR [#1330](https://github.com/zcash/zips/pull/1330)). [^draft-dandelion-wallet]


# Changelog

- 2026-07-09: Initial draft. Component B reference implementation complete (Zebra).
- 2026-07-09: Component A reference implementations added (Android + iOS SDKs).
  Updated Reference Implementation section to list all PRs.
- 2026-07-09: Reference implementations proposed upstream — Zebra Component B to
  `zcashfoundation/zebra`, and Component A to `zcash/zcash-android-wallet-sdk#2010`
  and `zcash/zcash-swift-wallet-sdk#1804`.


# References

[^BCP14]: [Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/info/bcp14)

[^DPPLUSPLUS]: Venkatakrishnan, S.B., Fanti, G., Viswanath, P. "Dandelion++: Lightweight
Cryptocurrency Networking with Formal Anonymity Guarantees." ACM SIGMETRICS 2018.
https://arxiv.org/abs/1805.11060

[^zip-0307]: [ZIP 307: Light Client Protocol for Payment Detection](https://zips.z.cash/zip-0307)

[^draft-dandelion-wallet]: draft-dandelion-wallet: Direct Wallet Transaction Submission via Dandelion++ P2P Relay. PR: https://github.com/zcash/zips/pull/1330
(In preparation — see zcash/zips#1330.)
