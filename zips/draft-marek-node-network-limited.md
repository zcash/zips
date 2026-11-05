    ZIP: Unassigned
    Title: Limited Block Serving Service Flag
    Owners: Marek <marek@zfnd.org>
    Status: Draft
    Category: Network
    Created: 2026-11-03
    License: MIT


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

best tip
:   The tip of a node's best block chain.

limited peer
:   A peer that advertises `NODE_NETWORK_LIMITED` and not `NODE_NETWORK`.


# Abstract

This ZIP defines the service flag `NODE_NETWORK_LIMITED` for the Zcash
peer-to-peer protocol specified in ZIP 204 [^zip-0204]. A node that sets it
serves at least the most recent 2,304 blocks of its best chain, but not
necessarily older blocks. It is the Zcash counterpart of BIP 159
[^bip-0159].


# Motivation

A node that deletes old block bodies, such as a Zebra node with pruning
enabled, cannot set `NODE_NETWORK`, and ZIP 204 defines no other flag for
serving blocks. Peers cannot tell that such a node serves recent blocks: some
ignore it, and others request historical blocks it does not have.

The Version 2 P2P protocol draft [^draft-p2p-v2] defines the same flag. This
ZIP specifies it for the current protocol, so that it can be deployed without
the rest of that draft.


# Specification

## Service Flag

The service flag `NODE_NETWORK_LIMITED` is defined as bit 10
(`0x0000000000000400`) of the `services` field.

A node that sets `NODE_NETWORK_LIMITED` MUST be able to serve every block of
its best chain at a height greater than its best tip height minus 2,304, in
response to `getdata` requests with `MSG_BLOCK`.

A node that cannot serve the complete block chain SHOULD set
`NODE_NETWORK_LIMITED` if it meets this requirement. A node that sets
`NODE_NETWORK` MAY also set it.

## Serving

A limited peer SHOULD NOT serve blocks more than 2,304 blocks below its best
tip. It MAY disconnect a peer that requests a block more than 2,306 blocks
below its best tip; the 2-block margin allows for the best tip advancing while
a request is in flight.

## Requesting

A node MUST NOT request a block from a limited peer if that block is more than
2,304 blocks below the node's own best tip. A node SHOULD rely on limited
peers for blocks only while its best tip is within 1,152 blocks of the
network's best tip, leaving half of the window for chain reorganizations and
for differences between the two nodes' best tips.

## Address Relay

Nodes SHOULD relay addresses advertising `NODE_NETWORK_LIMITED` as they relay
other addresses.

## Deployment

This ZIP requires no network upgrade. Nodes ignore service flags they do not
recognize, so a node can set `NODE_NETWORK_LIMITED` as soon as it implements
this ZIP.


# Rationale

Bit 10 and the 2,304-block window match the Version 2 P2P protocol draft
[^draft-p2p-v2], so a node can advertise the same capability in both
protocols. Bit 10 is also the bit that BIP 159 assigns to the same capability
in Bitcoin.

The window is defined in blocks rather than time, so that a peer can check a
request against it without knowing the block target spacing. At 75, 25 and 10
seconds per block it covers about 48, 16 and 6.4 hours.

The 1,152-block margin for requesters, and the rule against serving older
blocks, follow BIP 159's 144-block reorganization buffer and its
fingerprinting countermeasure. BIP 159 does not specify disconnection; the
2-block margin follows Bitcoin Core's implementation [^bitcoin-core-limited].


# Security and Privacy Considerations

A limited peer that served every block it retains would reveal its retention
depth, which helps distinguish it from other nodes. Serving only the window
avoids this.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0204]: [ZIP 204: Zcash P2P Network Protocol](zip-0204.rst)

[^bip-0159]: [BIP 159: NODE_NETWORK_LIMITED service bit](https://github.com/bitcoin/bips/blob/master/bip-0159.mediawiki)

[^draft-p2p-v2]: [Draft ZIP: Version 2 Zcash P2P Network Protocol](draft-arya-jvff-p2p-quic-transport.md)

[^bitcoin-core-limited]: [Bitcoin Core: block requests below the NODE_NETWORK_LIMITED threshold (`net_processing.cpp`)](https://github.com/bitcoin/bitcoin/blob/master/src/net_processing.cpp)
