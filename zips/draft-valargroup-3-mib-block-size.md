
    ZIP: Unassigned
    Title: Increase the Block Size Limit to 3 MiB
    Owners: Dev Ojha <dev@valargroup.dev>
            Evan Forbes <evan@valargroup.dev>
    Status: Draft
    Category: Consensus
    Created: 2026-11-06
    License: MIT


# Terminology

The key words "MUST", "MUST NOT", and "SHOULD" in this document are to be
interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

The terms "block chain", "consensus branch", and "network upgrade" follow
ZIP 200. [^zip-0200] Block and transaction encodings follow the Zcash Protocol
Specification. [^protocol]

MiB means 1,048,576 bytes. GiB means 1,073,741,824 bytes. The existing block
size limit is 2,000,000 bytes, not 2 MiB.

"Stale fraction" means distinct observed stale blocks divided by the sum of
canonical and observed stale blocks. The experiment below counts a block
only if at least one node recorded a successful commit. It does not count
every solved block that a miner discarded before submission.

"Reach 90%" means elapsed time from the miner's solution-ready event to
decoded block availability at 72 of the experiment's 80 nodes, including
the originating node at time zero.


# Abstract

This proposal increases the block size limit from 2,000,000 to 3,145,728 bytes
(3 MiB) in a network upgrade after NU7. It preserves ZIP 218's shielded action
limits and shared shielded budget. [^zip-0218] It also preserves the
2,000,000-byte transaction size limit and the existing signature-operation
limit.

The additional space primarily increases capacity for transparent
transactions. It prepares the block byte budget for future shielded
throughput without raising today's shielded scanning burden through an
action-limit increase. A future proposal to increase shielded action limits
would depend on adoption and operational validation of private information
retrieval (PIR), with measured wallet bandwidth and privacy costs.

The proposal also changes block-message size negotiation so that upgraded
peers can relay valid 3 MiB blocks. It leaves block target spacing to separate
proposals. Larger blocks increase full-node bandwidth, storage, and
potential validation work.


# Motivation

ZIP 218 separates the block byte budget from the shielded action budget.
The byte budget limits serialized data; the action budget limits shielded
work and compact sync bandwidth. Its action limits do not apply to the
transparent components of transactions. [^zip-0218]

Increasing the byte budget now allows more transparent transactions when
bytes are the binding constraint. Increasing transparent throughput is an
intermediate benefit, not Zcash's long-term scaling objective. Deploying
and measuring larger blocks also prepares the network for future shielded
throughput once wallets can handle it privately and efficiently.

This proposal separates those decisions. It increases block space while
retaining all shielded action limits. PIR adoption does not automatically
activate higher limits; any change requires a separate consensus proposal.


# Privacy Implications

This proposal does not change transaction disclosure, shielded proofs, or
the information that transparent transactions expose. It does not encourage
wallets to replace shielded transactions with transparent transactions.

At unchanged block target spacing, retaining the shielded action limits
preserves ZIP 218's bound on compact shielded fields per block and per day.
This does not bound every wallet download: transaction metadata, transparent
queries, and full-transaction retrieval can add traffic. A separately
activated spacing reduction would also increase the daily bound.

Longer block propagation can increase stale blocks and reorganization risk.
Wallets should not reduce their confirmation or anchor-depth policies on
the strength of the experiment below. The observed stale fraction does
not establish a reorganization-depth bound.


# Requirements

- Increase the maximum serialized block size to exactly 3 MiB.
- Preserve historical validity and all existing shielded action limits.
- Preserve transaction-size, signature-operation, and script limits.
- Support full-sized blocks through relay, synchronization, and mining.
- Bound resource use before accepting untrusted block bodies.


# Specification

## Activation and block size

Define the following constants:

$$\mathsf{ThreeMiBActivationHeight} : \mathbb{N}.$$

$$\mathsf{ThreeMiBBlockSizeLimit} : \mathbb{N} := 3\times2^{20} = 3{,}145{,}728.$$

A deployment ZIP will assign $\mathsf{ThreeMiBActivationHeight}$ for each
network. It MUST be greater than that network's NU7 activation height.
Let $A = \mathsf{ThreeMiBActivationHeight}$. For block height
$h \in \mathbb{N}$, define:

$$\mathsf{BlockSizeLimit}(h) := \begin{cases}2{,}000{,}000 & h < A,\\3{,}145{,}728 & h \geq A.\end{cases}$$

Replace the fixed block size bound in § 7.6 'Block Header Encoding and
Consensus' with the requirement that a block at height $h$ MUST have encoded
size at most $\mathsf{BlockSizeLimit}(h)$. [^protocol-blockheader]

Encoded size includes the block header, its Equihash solution, the encoded
transaction count, and every transaction, including the coinbase. It excludes
the 24-byte P2P message header and storage or RPC wrappers. No field receives
a size discount.

Validators MUST select the limit using the candidate block's height on its
parent chain. The local tip height and the peer's advertised height MUST NOT
determine consensus validity. Validators MUST retain the old limit below
$A$, including during initial synchronization, side-chain validation, and
reorganizations across activation.

## Transaction and computational limits

Define $\mathsf{TransactionSizeLimit} : \mathbb{N} := 2{,}000{,}000$ bytes.
For every block at or above $A$, each transaction, including the coinbase,
MUST have encoded size at most $\mathsf{TransactionSizeLimit}$.
Pre-activation transaction rules remain unchanged.

The transaction bound remains independent of the block bound. The additional
space admits more transactions while preserving the existing explicit
transaction-size cap. [^zcashd-limits]

Implementations MUST continue to enforce ZIP 218's existing per-pool limits
and shared global shielded budget. Orchard and Ironwood actions continue to
consume the same shared budget. Extra transparent bytes do not exempt a
mixed transaction's shielded components from those limits. [^zip-0218]

The block signature-operation limit remains 20,000, using the existing
counting rules, including P2SH signature operations. Existing script limits
and transaction-format bounds remain unchanged. [^zcashd-limits]

This proposal changes neither block target spacing nor the difficulty
algorithm, issuance schedule, funding streams, transaction expiry, or
coinbase maturity.

## Block relay and message framing

ZIP 204 currently limits each message payload to 2,097,152 bytes. That limit
cannot carry a valid 3 MiB block. Amend its 'Maximum Message Size' rules as
follows. [^zip-0204]

Define $\mathsf{ThreeMiBProtocolVersion} : \mathbb{N}$, to be assigned by the
deployment ZIP. For a connection whose negotiated protocol version is at
least this value, the maximum `block` message payload is 3,145,728 bytes.
For older negotiated versions, retain the 2,097,152-byte maximum. Other
commands retain their existing payload and item-count limits.

Nodes MUST reject a declared payload length above the applicable maximum
before allocating a buffer for that payload. A decoder MUST consume exactly
one block from a `block` payload and reject trailing data, truncated fields,
and invalid encodings. Existing checksum checks remain in force.

Upgraded nodes MUST support the larger `block` payload on upgraded
connections even when their local tip is below $A$. They still apply the
height-dependent consensus bound when validating the block. This permits
initial synchronization and out-of-order delivery across activation without
accepting oversized pre-activation blocks.

Senders MUST NOT send a payload above the peer connection's negotiated
maximum. The deployment MUST update minimum peer versions and apply
ZIP 201's upgrade peer-management rules so that upgraded nodes can retain
compatible peers at activation. [^zip-0201]

## Mining and node interfaces

`getblocktemplate` MUST report `sizelimit` for the candidate height, normally
one above the selected parent. Template selection MUST reserve space for
the complete header, encoded transaction count, and completed coinbase.
Miners MUST re-evaluate the limit when a parent change crosses activation.

Block submission and retrieval interfaces MUST support every otherwise-valid
block within the applicable limit. This includes proposal validation, RPC
submission, historical retrieval, and local block import. Hex-encoded RPC
block data alone can occupy 6,291,456 characters; request limits also need
room for the enclosing request.

Deserializers MUST distinguish the block envelope limit from transaction
and field limits. Increasing the block limit MUST NOT implicitly increase
`tx`, inventory, address, or header-message limits. Nodes SHOULD bound
aggregate queued block bytes and decoded memory, rather than relying only
on a count of blocks or connections.

This proposal does not increase mempool memory defaults or change ZIP 317's
fee calculation. ZIP 401's cost limit remains a node resource policy, not a
fixed entitlement to a number of full blocks. [^zip-0317] [^zip-0401]


# Rationale

## Throughput and resource costs

The new byte budget is $3{,}145{,}728/2{,}000{,}000 = 1.572864$ times the old
budget, an increase of approximately 57.3%. Transaction throughput depends
on the workload. Transparent transactions can use the additional space,
but signature operations, script execution, and UTXO access can become
binding constraints. Action-limited shielded workloads do not receive a
corresponding increase in transactions per block.

The following bounds assume every canonical block reaches 3 MiB and blocks
arrive at the stated target spacing:

| Target spacing | Raw block payload rate | Raw block data per day |
|----------------|------------------------|------------------------|
| 25 seconds | 125,829 bytes/second | 10.125 GiB |
| 20 seconds | 157,286 bytes/second | 12.65625 GiB |

These figures exclude repeated relay, stale blocks, transport overhead,
indexes, and state growth. They describe full-block traffic, not light-wallet
compact sync. Disk and memory costs can grow differently from serialized
bytes, especially for blocks with many small transparent outputs.

Keeping the 20,000 signature-operation limit bounds counted operations; it
does not bound all validation work. Transparent-heavy blocks require
measurements of script execution, UTXO reads and writes, memory, and
validation-to-mining-tip latency.

## Propagation experiment

The November 5–6, 2026 private-network run used 80 Zakura nodes across 12
cloud regions, a 20-second target, a 4,000,000-byte block ceiling, and doubled
shielded action limits. The experimental shared budget was 660 actions.
These experimental limits are not proposed consensus changes. The saved
summary records the run, binary hashes, sample definitions, and results.
[^experiment]

The final agreed chain contained 913 live blocks at heights 206 through
1118. Commit traces recorded 34 additional distinct blocks outside that
chain. The observed stale fraction was:

$$\frac{34}{913+34}\approx3.59\%.$$

The corresponding stale-per-canonical ratio is 3.72%. After the recorded
launch-verification boundary, the counts were 882 canonical and 32 stale
blocks, giving 3.50%. The headline 3.6% result includes startup and uses a
retrospective interval, approximately 02:23–07:44 UTC on November 6.

The propagation sample contains 809 action-full canonical blocks after that
boundary. Each contained 660 Ironwood actions and occupied 3,026,379 bytes,
or 96.2% of 3 MiB. The sample therefore measures blocks close to the proposed
byte limit, not full 4 MiB blocks. It also exceeds the shielded action limit
retained by this proposal.

| Decoded block availability | Mean | Median | 95th percentile | Samples |
|----------------------------|------|--------|-----------------|---------|
| Reach 90% of nodes | 1.20 s | 1.02 s | 2.18 s | 809 |
| Reach 95% of nodes | 1.75 s | 1.58 s | 3.39 s | 809 |
| Reach all nodes | 4.05 s | 3.92 s | 7.05 s | 735 |

Timing starts when the miner records a solved block and ends when each node
records its first decoded block receipt. It includes submission, gossip,
decoding, and scheduling. It does not measure validated mining-tip adoption.
Cross-host clock error affects these durations. One node dropped some
peer-message trace rows; every sample has 79 or 80 recorded arrivals,
including the origin. The all-node row excludes incomplete observations.

The 3.6% point estimate is below 5% and supports further evaluation of the
3 MiB limit. It does not establish a Mainnet-wide bound. The fleet used one
client and a different transaction mix from the transparent-heavy workload
expected under this proposal. The receipt sample excludes stale blocks, and
the stale count excludes solved blocks never observed committed.

Better gossip may reduce propagation delay and stale blocks. This proposal
does not assume that improvement before it is measured. A matched run with
3 MiB blocks, unchanged action limits, and representative transparent
transactions remains necessary before deployment.

## Separating block space from shielded action limits

Shielded wallet bandwidth remains the constraint on increasing Ironwood
actions. The experiment tests propagation under a heavier shielded workload;
it does not demonstrate that wallets can afford that workload.

A future action-limit proposal should follow PIR adoption and operational
testing. It should quantify query bandwidth, server cost, privacy assumptions,
failure behavior, and wallet recovery costs. This ZIP creates neither an
automatic action-limit increase nor an exception for PIR-enabled wallets.


# Reference implementation

**TODO:** link implementations and activation vectors. The experiment's
private-network byte override is evidence for propagation, not a reference
implementation of this height-dependent consensus and negotiation change.

Implementations need coverage for:

- Blocks of 2,000,000 and 2,000,001 bytes on both sides of activation;
  blocks of 3,145,728 and 3,145,729 bytes after activation.
- Transactions of 2,000,000 and 2,000,001 bytes inside otherwise-valid
  post-activation blocks; coinbase and transaction-count encoding overhead.
- Unchanged action and signature-operation boundaries, including mixed
  pools, transparent components, and P2SH accounting.
- Larger blocks received before the local tip reaches activation, historical
  replay, and reorganizations that cross activation in either direction.
- Negotiated old and new peers; exact payload limits, malformed lengths,
  trailing bytes, truncation, and unchanged limits for other commands.
- Mining templates and submission across a parent change; storage round trips,
  checkpoint synchronization, and full-block RPC retrieval.
- Many-small-transaction and output-heavy blocks, bounded decoder allocations,
  concurrent downloads, and peers that send large bodies slowly.


# Deployment

Deploy through a network upgrade after NU7. A deployment ZIP will assign
activation heights, consensus branch IDs, and the new protocol version.
This proposal can activate with a separately specified spacing change, but
does not require a 20-second target.

Before advancing to Proposed status, publish reproducible experiment inputs
and resolve the deployment assignments. Validate the byte and computational
boundaries across independent clients. Run matched 3 MiB transparent and
mixed workloads at the selected spacing, including constrained bandwidth,
propagation tails, stale blocks, UTXO growth, and mining-tip adoption.


# References

[^BCP14]: [Information on BCP 14](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification](protocol/protocol.pdf)

[^protocol-blockheader]: [Zcash Protocol Specification, § 7.6: Block Header Encoding and Consensus](protocol/protocol.pdf#blockheader)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](https://zips.z.cash/zip-0200)

[^zip-0201]: [ZIP 201: Network Peer Management for Overwinter](https://zips.z.cash/zip-0201)

[^zip-0204]: [ZIP 204: Zcash P2P Network Protocol](https://zips.z.cash/zip-0204)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](https://zips.z.cash/zip-0218)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](https://zips.z.cash/zip-0317)

[^zip-0401]: [ZIP 401: Addressing Mempool Denial-of-Service](https://zips.z.cash/zip-0401)

[^zcashd-limits]: [zcashd: consensus limits](https://github.com/zcash/zcash/blob/master/src/consensus/consensus.h)

[^experiment]: [November 2026 larger-block experiment: local evidence summary](draft-valargroup-3-mib-block-size/experiment-summary.json)
