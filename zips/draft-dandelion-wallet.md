ZIP: Unassigned
    Title: Direct Wallet Transaction Submission via Dandelion++ P2P Relay
    Owners: y4ssi <y4ssi@zodl.com>
    Status: Draft
    Category: Standards / Network / Wallet
    Created: 2026-07-09
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/TODO>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and "RECOMMENDED"
in this document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

**Light client:** A Zcash wallet that does not store or validate a full copy of
the block chain, relying instead on a compact-block server for block data.

**Compact-block server:** A server implementing the lightwalletd gRPC protocol
[^zip-0307], or a compatible implementation such as Zaino, that serves compact
blocks and transaction-related RPCs to light clients.

**Submission intermediary:** Any server to which a wallet sends a
newly-constructed transaction for broadcast, including but not limited to a
compact-block server.

**Dandelion++ stem phase / fluff phase / stem peer:** As defined in draft-dandelion (PR [#1329](https://github.com/zcash/zips/pull/1329)).
[^draft-dandelion]

**IP-to-transaction correlation:** The ability of a network observer to determine
which IP address originated a given transaction by observing when and where the
transaction first appeared on the P2P network.


# Abstract

This ZIP specifies how Zcash light-client wallets MAY submit newly-constructed
transactions directly to a full node peer via the Zcash P2P network — using the
Dandelion++ stem-phase forwarding defined in draft-dandelion (PR [#1329](https://github.com/zcash/zips/pull/1329)) [^draft-dandelion] — instead of
through a compact-block server, while continuing to use compact-block servers
exclusively for chain synchronisation.

Under the current architecture, a wallet's submission intermediary (a
compact-block server such as lightwalletd or Zaino) learns both the wallet's IP
address and the transaction it submits at the same instant, letting a passive
observer correlate transaction origin with network identity. This ZIP removes
that correlation for the submission path.

No consensus-rule changes are required. This ZIP covers the **wallet side**
(sometimes called "Component A"); the full-node relay behaviour it depends on is
specified in draft-dandelion (PR [#1329](https://github.com/zcash/zips/pull/1329)) (Component B). [^draft-dandelion]


# Motivation

ZIP 307 [^zip-0307] defines a light-client architecture in which a compact-block
server mediates between the wallet and the P2P network. This is appropriate for
block synchronisation: a well-designed wallet fetches whole block ranges, so the
server learns little about which notes are the wallet's.

Transaction submission is different. When a wallet calls the `SendTransaction`
gRPC RPC, the compact-block server receives:

1. the wallet's IP address,
2. the exact serialised transaction, and
3. the submission timestamp.

That is enough to link a transaction to a network identity. For shielded
transactions the on-chain data reveals nothing about the sender, yet the
submission channel leaks exactly the information that shielding is designed to
protect.

Existing mitigations impose costs:

- **Tor** — Zashi supports Tor [^ZASHI-TOR], but it adds latency and a
  dependency, and its effectiveness depends on the wallet always routing through
  it.
- **Self-hosted server** — avoids the third-party trust assumption but is
  impractical for most mobile users.
- **Zaino** [^ZAINO] — improves server-side privacy by design but still sits
  between the wallet and the network for submission, preserving the
  IP-correlation window.

This ZIP proposes that a wallet with access to one or more Zcash P2P peer
endpoints SHOULD submit transactions via those peers under Dandelion++ rather
than via a compact-block server. Because the P2P network is a decentralised mesh
and the receiving node relays the transaction through its stem peer without
advertising it locally, no single entity learns both the transaction and the
submitting IP together for the transaction's onward propagation.


# Requirements

1. A compliant wallet implementing this ZIP MUST NOT call the `SendTransaction`
   gRPC RPC on a compact-block server for a transaction submitted via the P2P
   path (concurrent submission would re-expose the origin IP through the
   centralised channel).

2. A compliant wallet MUST send the transaction to a full node using the P2P
   handshake and message flow in the Specification below.

3. A compliant wallet MUST continue to use compact-block servers (or equivalent)
   for block synchronisation, note-witness retrieval, and other read-only chain
   queries.

4. The P2P submission path MUST be an optional enhancement: a wallet that cannot
   reach a full node peer MUST fall back to the existing `SendTransaction` RPC
   without degrading other functionality.

5. The receiving full node SHOULD implement the Dandelion++ relay behaviour of
   draft-dandelion (PR [#1329](https://github.com/zcash/zips/pull/1329)). [^draft-dandelion] A wallet submitting via P2P gains no privacy benefit if
   the node immediately floods the transaction; however, a non-implementing node
   simply flood-broadcasts it, which is a safe fallback.


# Specification

## Peer discovery

A wallet implementing this ZIP MUST obtain at least one full-node peer address.
Acceptable mechanisms include, but are not limited to:

- a hard-coded or user-configured list of trusted full nodes;
- the Zcash mainnet DNS seeders [^ZCASHSEEDS];
- a peer address returned by a compact-block server via an optional extension RPC
  (not defined here);
- a peer address provided directly by the user.

The wallet MUST complete the Zcash P2P `version`/`verack` handshake before
submitting a transaction. The wallet MUST advertise a protocol version at least
equal to the receiving network's minimum accepted protocol version, or the peer
will reject the handshake.

## Transaction submission message

After the handshake, the wallet submits the transaction using the standard Zcash
P2P `tx` message [^ZCASHP2P]. No new P2P message type is required.

The wallet SHOULD set the `fRelay` field in its `version` message to `false` so
that the peer does not push unsolicited `inv` messages back to the wallet,
reducing leakage about the wallet's connectivity.

## Dandelion++ submission hint (unadvertised `tx`)

To request that the receiving full node treat the transaction as a stem-phase
candidate (rather than immediately flooding it), the wallet MUST send the `tx`
message with **no prior `inv` announcement** on this connection. This is the
"unadvertised `tx`" convention of draft-dandelion §Stem-phase forwarding (PR [#1329](https://github.com/zcash/zips/pull/1329)). [^draft-dandelion]

Rationale: advertising via `inv` before `tx` is the normal relay path, which
signals the sending node already received the transaction from elsewhere.
Sending `tx` without a prior `inv` on a freshly-opened connection is a reliable
signal that this is the transaction's first appearance.

## No concurrent centralised submission

The wallet MUST NOT resubmit the same transaction via a compact-block server
`SendTransaction` RPC while the P2P submission is in flight or within the
stem-phase timeout window. Concurrent submission would reveal the originating IP
via the centralised channel.

## Fallback

If the P2P submission does not result in the transaction appearing in a block
within a configurable timeout (RECOMMENDED default: 30 minutes), the wallet MAY
fall back to `SendTransaction` on a compact-block server.


# Privacy Implications

- The wallet's P2P peer(s) see the wallet's IP and the transaction, but only
  before stem-phase forwarding begins. With Dandelion++ stem/fluff the peer
  relays the transaction to its own stem peer without advertising it locally,
  breaking the origin-IP↔txid association for all subsequent hops.

- The compact-block server used for synchronisation is decoupled from the
  submission path and learns only that the wallet is synchronising blocks, not
  which transactions it submitted.

- An adversary who controls **both** the wallet's compact-block server and the
  wallet's P2P peer can still correlate if the wallet uses the same IP for both.
  Wallets SHOULD use distinct network paths (e.g. Tor for one channel, or
  separate Tor circuits) if this threat model is relevant.

- Dandelion++ does not protect against a global passive adversary monitoring all
  P2P traffic. It significantly raises the cost of IP-to-transaction correlation
  for realistic adversaries operating relay nodes or monitoring subsets of the
  network.

- Shielded transactions already hide their *contents* via zero-knowledge proofs;
  this ZIP closes the complementary *network-metadata* leak (which IP originated
  the packet). The two protections are orthogonal.

- Once a transaction enters the fluff phase it is indistinguishable from any
  other transaction on the network.


# Rationale

## Why not just use Tor for all wallets?

Tor addresses IP privacy comprehensively but adds latency (typically
200–500 ms), requires maintaining Tor client code per wallet, and may be
unavailable on some platforms. Dandelion++ is a lightweight complement. The two
are not mutually exclusive: a wallet using Tor **and** P2P Dandelion++ submission
is strictly more private than either alone.

## Why keep compact-block servers for synchronisation?

They provide an efficient protocol for delivering shielded-note data to mobile
wallets. Replacing bulk sync with a direct P2P full-sync would require
downloading hundreds of gigabytes, impractical on mobile. Separating the
submission channel from the sync channel also lets a wallet choose independent
providers for each, reducing the trust surface.

## Why an unadvertised `tx` rather than a new P2P message type?

A new message type would require a network upgrade and coordination across all
node implementations. The existing `tx` message with a semantic convention (no
prior `inv`) achieves the same signalling with no protocol change, allowing
incremental deployment. Non-implementing nodes flood-broadcast normally (safe
fallback).

## Relationship to Zaino

A Zaino [^ZAINO] instance co-located with a Zebra node could implement the
draft-dandelion (PR [#1329](https://github.com/zcash/zips/pull/1329)) relay path
natively, routing wallet submissions received via `SendTransaction`
through the local node's stem path. This would help wallets that cannot open a
direct P2P connection, without wallet-software changes. It is RECOMMENDED as a
complement to (not a replacement for) this ZIP.


# Reference Implementation

Wallet-side (Component A):

- **Android**: [zcash/zcash-android-wallet-sdk#2010](https://github.com/zcash/zcash-android-wallet-sdk/pull/2010)
- **iOS (Swift)**: [zcash/zcash-swift-wallet-sdk#1804](https://github.com/zcash/zcash-swift-wallet-sdk/pull/1804)

Both SDKs add an opt-in `DandelionSubmitConfig` (`DirectP2P` / `directP2P`) that
resolves peers via the mainnet DNS seeders, opens a TCP connection to a full
node, performs the `version`/`verack` handshake (advertising protocol version
170150, the current mainnet minimum), and sends the raw `tx` without a prior
`inv`. Chain synchronisation continues to use the lightwalletd endpoint. A
fallback to `SendTransaction` is available when no P2P peer is reachable.

Full-node relay (Component B) is specified and implemented in draft-dandelion (PR [#1329](https://github.com/zcash/zips/pull/1329)):
[zcashfoundation/zebra#10928](https://github.com/zcashfoundation/zebra/pull/10928).


# Changelog

- 2026-07-09: Initial draft.


# References

[^BCP14]: [Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/info/bcp14)

[^zip-0307]: [ZIP 307: Light Client Protocol for Payment Detection](https://zips.z.cash/zip-0307)

[^draft-dandelion]: draft-dandelion: Dandelion++ Transaction Propagation for Zcash P2P Nodes. PR: https://github.com/zcash/zips/pull/1329
(In preparation — see zcash/zips#1329.)

[^DPPLUSPLUS]: Venkatakrishnan, S.B., Fanti, G., Viswanath, P. "Dandelion++: Lightweight
Cryptocurrency Networking with Formal Anonymity Guarantees." ACM SIGMETRICS 2018.
https://arxiv.org/abs/1805.11060

[^ZCASHSEEDS]: Zcash mainnet DNS seeds are defined in the Zcash Protocol
Specification, section 3.12 (Network Upgrades).

[^ZCASHP2P]: Zcash P2P message format follows Bitcoin's protocol with
Zcash-specific extensions. See the Zcash Protocol Specification for the canonical
definition of the `version`, `verack`, `inv`, and `tx` messages.

[^ZAINO]: [Zaino: Zcash Chain Indexer and Light Wallet Server](https://github.com/ZcashFoundation/zaino)

[^ZASHI-TOR]: Zashi Tor integration. https://github.com/Electric-Coin-Company/zashi-android
