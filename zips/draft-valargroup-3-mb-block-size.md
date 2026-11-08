
    ZIP: Unassigned
    Title: Increase the Block Size Limit to 3 MB
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

MB means 1,000,000 bytes. The existing block
size limit is 2 MB; this proposal increases it to 3 MB.

"Orphan rate" means distinct observed orphan blocks divided by the sum of
canonical and observed orphan blocks. Here, an orphan block is a block outside
the final agreed chain. The experiment below counts a block
only if at least one node recorded a successful commit. It does not count
every solved block that a miner discarded before submission.

"Reach 90%" means elapsed time from the miner's solution-ready event to
decoded block availability at 72 of the experiment's 80 nodes, including
the originating node at time zero.


# Abstract

This proposal increases the block size limit from 2,000,000 to 3,000,000 bytes
(3 MB) in a network upgrade after NU7. It preserves ZIP 218's shielded action
limits and shared shielded budget. [^zip-0218] It also preserves the
2,000,000-byte transaction cap currently enforced by consensus and the existing signature-operation
limit.

The additional space primarily increases capacity for transparent
transactions. It prepares the block byte budget for future shielded
throughput without raising today's shielded scanning burden through an
action-limit increase. A future proposal to increase shielded action limits
would depend on adoption and operational validation of private information
retrieval (PIR), with measured wallet bandwidth and privacy costs.

The proposal also changes block-message size negotiation so that upgraded
peers can relay valid 3 MB blocks. This proposal does not change block target
spacing, but benchmarks for safety are done with 20-second target spacing in
mind. Larger blocks increase full-node bandwidth, storage, and
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

Longer block propagation can increase orphan blocks and reorganization risk.
Wallets should not reduce their confirmation or anchor-depth policies on
the strength of the experiment below. The observed orphan rate does
not establish a reorganization-depth bound.


# Requirements

- Increase the maximum serialized block size to exactly 3 MB.
- Preserve historical validity and all existing shielded action limits.
- Preserve transaction-size, signature-operation, and script limits.
- Support full-sized blocks through relay, synchronization, and mining.
- Bound resource use before accepting untrusted block bodies.


# Specification

## Activation and block size

Define the following constants:

$$\mathsf{ThreeMBActivationHeight} : \mathbb{N}.$$

$$\mathsf{ThreeMBBlockSizeLimit} : \mathbb{N} := 3\times10^6 = 3{,}000{,}000.$$

A deployment ZIP will assign $\mathsf{ThreeMBActivationHeight}$ for each
network. It MUST be greater than that network's NU7 activation height.
Let $A = \mathsf{ThreeMBActivationHeight}$. For block height
$h \in \mathbb{N}$, define:

$$\mathsf{BlockSizeLimit}(h) := \begin{cases}2{,}000{,}000 & h < A,\\3{,}000{,}000 & h \geq A.\end{cases}$$

Replace the fixed block size bound in § 7.6 'Block Header Encoding and
Consensus' with the requirement that a block at height $h$ MUST have encoded
size at most $\mathsf{BlockSizeLimit}(h)$. [^protocol-blockheader]

In the same section, qualify the comparison with Bitcoin's block size limit:
Zcash's 2,000,000-byte limit applies below $A$; the 3,000,000-byte limit applies
at or above $A$.

In ZIP 218's specification, replace the statement that the overall 2 MB block
size limit continues to apply with a reference to $\mathsf{BlockSizeLimit}(h)$
after this proposal activates. ZIP 218's shielded action limits remain
unchanged. [^zip-0218]

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
space admits more transactions. zcashd already enforces an explicit
2,000,000-byte transaction cap. The protocol specification states a
100,000-byte cap before Sapling; after Sapling, the block envelope also
limits the size of any included transaction. This proposal makes the
independent 2,000,000-byte post-activation transaction cap explicit, so
increasing the block envelope does not admit larger individual transactions.
[^zcashd-limits] [^protocol]

The block signature-operation limit remains 20,000, using the existing
counting rules, including P2SH signature operations. Existing script limits
and transaction-format bounds remain unchanged. [^zcashd-limits]

This proposal changes neither block target spacing nor the difficulty
algorithm, issuance schedule, funding streams, transaction expiry, or
coinbase maturity.

## Block relay and message framing

ZIP 204 currently limits each message payload to 2,097,152 bytes. That limit
cannot carry a valid 3 MB block. Amend its 'Maximum Message Size' rules as
follows. [^zip-0204]

Define $\mathsf{ThreeMBProtocolVersion} : \mathbb{N}$, to be assigned by the
deployment ZIP. For a connection whose negotiated protocol version is at
least this value, the maximum `block` message payload is 3,000,000 bytes.
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
block data alone can occupy 6,000,000 characters; request limits also need
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

## Choice of block size

The authors chose 3 MB as an attainable limit for current Zakura and Zebra
Andale implementations while keeping orphan rates within a reasonable range.
This is an engineering target, not a claim that 3 MB is an optimal threshold.
The experiment below provides preliminary Zakura evidence near that size.
Matched measurements across both clients remain necessary before deployment.

## Throughput and resource costs

The new byte budget is $3{,}000{,}000/2{,}000{,}000 = 1.5$ times the old
budget, an increase of 50%. Transaction throughput depends
on the workload. Transparent transactions can use the additional space,
but signature operations, script execution, and UTXO access can become
binding constraints. Action-limited shielded workloads do not receive a
corresponding increase in transactions per block.

The following bounds assume every canonical block reaches 3 MB and blocks
arrive at the stated target spacing:

| Target spacing | Raw block payload rate | Raw block data per day | Capacity relative to 2 MB at 25 seconds |
|----------------|------------------------|------------------------|----------------------------------------|
| 25 seconds | 120,000 bytes/second | 10.368 GB | 1.5× |
| 20 seconds | 150,000 bytes/second | 12.96 GB | 1.875× |

These figures exclude repeated relay, orphan blocks, transport overhead,
indexes, and state growth. They describe full-block traffic, not light-wallet
compact sync. Disk and memory costs can grow differently from serialized
bytes, especially for blocks with many small transparent outputs.

Keeping the 20,000 signature-operation limit bounds counted operations; it
does not bound all validation work. Transparent-heavy blocks require
measurements of script execution, UTXO reads and writes, memory, and
validation-to-mining-tip latency.

## Propagation experiment

A November 2026 private-network experiment used 80 Zakura nodes across 12
regions at a 20-second target spacing. Blocks filled twice ZIP 218's normal
shielded action limit: 660 Ironwood actions. The measured blocks occupied
3,026,379 bytes, approximately 3 MB and slightly above the proposed limit.

| Measurement | Mean | Median | 95th percentile |
|-------------|------|--------|-----------------|
| Peer-to-peer block propagation | TODO | TODO | TODO |
| Block propagation to 90% of nodes | 1.20 s | 1.02 s | 2.18 s |

The 90% result covers 809 canonical blocks. It measures time from the miner's
solution-ready event to decoded block availability at 72 of 80 nodes. It
includes submission and network delivery, rather than validated mining-tip
adoption. The saved summary does not contain a separate peer-to-peer timing
measurement; that row remains TODO.

The observed orphan rate was **3.6%**, including startup. The rate counts
blocks committed by at least one node that were absent from the final agreed
chain. It excludes solved blocks that no node recorded as committed.

These results support further evaluation of 3 MB blocks. They do not establish
a Mainnet orphan-rate bound. Cross-host clock error affects propagation
timing, and the propagation sample excludes orphan blocks.

**TODO:** Add peer-to-peer propagation measurements with explicit send and
receive boundaries. Add results from experiments with different block sizes
and shielded/transparent transaction mixes, including the proposed unchanged
shielded action limits. Report propagation to 90% of nodes and orphan rates
for each configuration, including Zakura and Zebra Andale results.


## Validation benchmarks

The original Zcash block-size increase prompted analysis of verification
costs across different input/output mixes. [^zcashd-worst-case] A fixed
signature-operation limit does not capture every validation cost.

Before deployment, benchmark the following workloads at the proposed limit:

| Workload | Costs to examine |
|----------|------------------|
| Many small transparent transactions | Per-transaction overhead and UTXO lookups |
| Output-heavy transparent transactions | UTXO growth and database writes |
| Signature-heavy transparent transactions | Signature verification and script execution |
| Mixed transparent and shielded transactions | Combined UTXO and proof-verification work under unchanged action limits |

For each workload, report validation-to-mining-tip time, UTXO reads and writes,
and peak memory. Record client version, hardware, and cache conditions so
others can reproduce the results.

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
  blocks of 3,000,000 and 3,000,001 bytes after activation.
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
boundaries across independent clients. Run matched 3 MB transparent and
mixed workloads at the selected spacing, including constrained bandwidth,
propagation tails, orphan blocks, UTXO growth, and mining-tip adoption.


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

[^zcashd-worst-case]: [zcashd issue #1077: Worst-case block verification costs](https://github.com/zcash/zcash/issues/1077)
