    ZIP: Unassigned
    Title: Private Information Retrieval for Governance
    Owners: First Owner <email>
    Credits: First Credited
    Status: Draft
    Category: Standards Track
    Created: 2026-03-02
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The terms below are to be interpreted as follows:

PIR (Private Information Retrieval)

: A cryptographic protocol that allows a client to retrieve a record from
  a server-held database without the server learning which record was
  requested.

LWE (Learning With Errors)

: A lattice-based cryptographic assumption in which ciphertexts are noisy
  linear equations. Each LWE ciphertext encrypts a single scalar value.

RLWE (Ring Learning With Errors)

: A structured variant of LWE where operations take place in a polynomial
  ring $\mathbb{Z}[x]/(x^d + 1)$. A single RLWE ciphertext encrypts $d$
  values simultaneously.

CDKS transformation

: The Chen-Dai-Kim-Song packing procedure [^CDKS] that converts $d$ LWE
  ciphertexts into one RLWE ciphertext using ring automorphisms and
  key-switching matrices.

Nullifier

: A unique value derived from a Zcash note that is published when the note
  is spent. The set of all published nullifiers determines which notes have
  been consumed.

Exclusion tree

: A sorted Merkle tree over nullifier exclusion ranges. A client proves
  that a given nullifier does not appear in the tree by retrieving the
  authentication path for the enclosing exclusion range.

Exclusion range

: A leaf of the exclusion tree, stored as a pair $(low, width)$ where
  $low$ is the lower bound and $width = high - low$. The range certifies
  that no nullifier exists in the interval $[low, low + width)$.

Authentication path

: The sequence of 26 sibling hashes from a leaf to the root of the
  exclusion tree, sufficient to recompute the Merkle root and verify
  membership.

Poseidon hash

: An algebraic hash function designed for efficient evaluation inside
  zero-knowledge proof circuits [^Poseidon].


# Abstract

This document specifies a private information retrieval (PIR) scheme for
use in a Zcash governance system. A governance participant must prove that
notes intended for voting are unspent by retrieving exclusion proofs from
a nullifier exclusion tree without revealing which nullifier is being
checked.

The construction uses YPIR+SP, a single-server PIR protocol built on
SimplePIR with RLWE packing via the CDKS transformation. YPIR+SP requires
no client-side database hint and no server-side per-client state, making
it suitable for cold-start mobile wallets.

The nullifier exclusion tree is organized into a three-tier data structure
spanning 26 levels of depth: a plaintext broadcast tier (192 KB, cacheable),
a small PIR tier (48 MB), and a large PIR tier (6 GB). A complete
authentication path is retrieved in two sequential PIR queries plus the
plaintext download, for a total bandwidth of approximately 1.2 MB per query.

This document also surveys the PIR design space, explains the choice of
YPIR+SP over alternatives such as InsPIRe, and specifies the row layouts,
serialization formats, and client procedures for each tier.


# Motivation

A governance system must fetch exclusion proofs for nullifiers to prove
that Zcash mainnet notes intended for use in voting are unspent and, thus,
eligible to participate.

A user naively querying a centralized server for the unspent property
risks revealing the on-chain link to the server, breaking the privacy
that Zcash's shielded transactions are designed to provide.

The alternative of downloading the entire nullifier set is impractical:
approximately 50 million nullifiers produce a Merkle tree exceeding 6 GB,
far beyond what a mobile client can store or process.

PIR resolves this tension. A PIR server holds the full database and
accepts encrypted queries. The server homomorphically evaluates the
database against the query via matrix-vector multiplication, returning an
encrypted response. Because the server touches every record during
evaluation, it learns nothing about which record was requested. The
privacy guarantee rests entirely on the client-side encryption: as long as
the client's secret key remains private, the server cannot distinguish the
target record from any other.


# Privacy Implications

The PIR construction in this document uses a single untrusted server. The
server is assumed to be computationally bounded but arbitrarily curious
(the honest-but-curious model). Under the hardness of the Ring LWE
problem, the server learns nothing about which nullifier the client
queries.

The following information is public and available to all parties, including
the server:

- The total number of nullifiers (and therefore the tree size).
- The Tier 0 plaintext data, which includes the 2,048 subtree-root keys
  at depth 11. This reveals the distribution of nullifiers across
  top-level subtrees but not which subtree any specific client queries.
- The timing and size of PIR queries. All queries have identical size for
  a given database configuration, but the number and timing of queries may
  reveal that a client is participating in governance.

Mitigations for traffic analysis (such as cover traffic or query batching
across clients) are out of scope for this document.


# Requirements

The following high-level goals guide the design. They are not conformance
requirements.

- No client-side database hint. A mobile wallet must be able to issue its
  first query without any prior download or preprocessing.
- Single untrusted server with no per-client state. The server holds only
  the public database and processes queries statelessly.
- Total bandwidth per query (upload plus download) under approximately
  2 MB, suitable for mobile networks.
- Two sequential network round-trips per query are acceptable.
- The hash function used in the exclusion tree must be efficient inside
  zero-knowledge proof circuits (Poseidon).
- 128-bit computational security with correctness error probability at
  most $2^{-40}$.


# Non-requirements

The following are explicitly out of scope:

- Multi-server PIR protocols.
- Stateful or preprocessing-based PIR constructions that require
  per-client server state.
- Updates to the database (assumed static)
- Sub-second end-to-end query latency. The two sequential PIR round-trips
  impose a latency floor determined by network conditions.
- Retrieval of data other than nullifier exclusion proofs.


# Specification

## PIR Construction

### Background

PIR allows a client to retrieve a record from a server-held database
without the server learning which record was requested. The server
processes the encrypted query by touching every record in the database,
ensuring that its access pattern reveals nothing about the target.

The underlying mechanism is homomorphic encryption. The client encrypts a
selection vector using Regev (LWE) encryption and sends it to the server.
The server multiplies the database matrix by the encrypted query,
producing an encrypted response. The client decrypts the response using
its secret key.

In SimplePIR [^SimplePIR], the database is reshaped into a
$\sqrt{N} \times \sqrt{N}$ matrix where each cell holds one byte. The
server computes the answer as a single matrix-vector product, achieving
throughput of approximately 10 GB/s. However, the client requires a
precomputed *hint* — the product of the database matrix with the public
encryption matrix — to decrypt the response. This hint is proportional to
$\sqrt{N}$ and can exceed 1 GB for large databases, making SimplePIR
unsuitable for cold-start clients.

### YPIR+SP

YPIR+SP [^YPIR] eliminates the hint by packing the SimplePIR response
into RLWE ciphertexts using the CDKS transformation [^CDKS].

RLWE ciphertexts encrypt $d$ values in a single ciphertext (as
coefficients of a polynomial in $\mathbb{Z}[x]/(x^d + 1)$), compared to
one value per LWE ciphertext. This yields approximately $500\times$ better
ciphertext rate, making it possible to compress the entire SimplePIR
column response — which would otherwise require the hint for decryption —
into a small number of RLWE ciphertexts that the client can decrypt
directly.

The protocol proceeds as follows:

1. The client generates LWE secret $s_1$, RLWE secret $s_2$, and a
   packing key $pk$ consisting of key-switching matrices for the CDKS
   automorphisms.
2. The client sends the query $(c_1, pk)$ to the server, where $c_1$ is
   the Regev-encrypted column selector.
3. The server computes the SimplePIR matrix-vector product
   $T = D \times c_1$, yielding $\sqrt{N}$ LWE ciphertexts.
4. The server packs $T$ into $\lceil \sqrt{N} / d_2 \rceil$ RLWE
   ciphertexts using the CDKS transformation with the client's packing
   key.
5. The server applies modulus switching to reduce the response size and
   returns the result.
6. The client decrypts the RLWE ciphertexts with $s_2$, recovering the
   column values directly.

Unlike standard YPIR (which is built on DoublePIR and retrieves a single
element), YPIR+SP returns an entire column of $\sqrt{N}$ values. This
makes it suitable for large records where multiple bytes are stacked
vertically in the database matrix.

### Parameters

Implementations MUST use the following parameters, which provide 128-bit
computational security and correctness error at most $2^{-40}$:

| Parameter | SimplePIR level | Packing level |
|---|---|---|
| Ring dimension $d$ | 1024 | 2048 |
| Ciphertext modulus $q$ | $2^{32}$ | $\approx 2^{56}$ (two 28-bit NTT-friendly primes) |
| Plaintext modulus | $N = 2^8$ | $p = 2^{20}$ |
| Noise width $\sigma$ | $11\sqrt{2\pi}$ | $6.4\sqrt{2\pi}$ |

These parameters support databases up to 64 GB ($\sqrt{N} \leq 2^{18}$).

### Security

The security of YPIR+SP relies on the Ring LWE assumption and circular
security (the packing key contains encryptions of automorphisms of the
secret key under itself). Both assumptions are standard in lattice-based
fully homomorphic encryption and are shared with Spiral, OnionPIR, and
HintlessPIR [^YPIR].

### Conformance

The server MUST implement YPIR+SP as described in this section with the
parameters specified in [Parameters].

The server MUST NOT retain any per-client state between queries.

The client MUST verify that the decrypted authentication path is
consistent with the published Merkle root of the exclusion tree.

The packing key MUST consist of $\lceil \log_2(d_2) \rceil = 11$
key-switching matrices as required by the CDKS transformation.

After modulus switching, the server MUST reduce the mask coefficients to
11 bits and the payload coefficients to 15 bits.

<details>
<summary>

### Rationale for YPIR+SP over standard YPIR
</summary>

Standard YPIR is built on DoublePIR and retrieves a single database
element per query. The DoublePIR second level selects a row, returning one
element per column. This means bytes of a large record cannot be stacked
vertically in the matrix.

In our data structure (see [Data Structure Layout]), the Tier 2 PIR
database has rows of 12,224 bytes. Retrieving a row of this size with
standard YPIR would require running $d$ parallel DoublePIR instances
(one per byte), each with its own 16 MB hint — a prohibitive cost.

YPIR+SP returns an entire column from the SimplePIR matrix. Large records
are naturally stacked vertically, and the full column is packed into RLWE
ciphertexts in a single pass. For a 32 GB database with 64 KB records,
YPIR+SP achieves 2.6 MB total communication (query plus response) compared
to standard YPIR's inability to handle the record size efficiently.
</details>

## Nullifier Exclusion Tree

The governance system requires each participant to prove that the
nullifiers associated with their voting notes do not appear in the set of
spent nullifiers. This proof takes the form of a zero-knowledge proof over
the authentication path of the enclosing exclusion range in a sorted
Merkle tree, building on the approach described in
"Air drops, Proof-of-Balance, and Stake-weighted Polling" [^draft-str4d-orchard-balance-proof].

### Tree Structure

The exclusion tree is a sorted binary Merkle tree with depth 26, holding
up to $N = 2^{26} \approx 67$ million leaves. The tree MUST use the
Poseidon hash function [^Poseidon] for all internal node computations, as
Poseidon is designed for efficient evaluation inside zero-knowledge proof
circuits.

An internal node is a 32-byte hash:
$\text{Hash}(\text{left\_child} \| \text{right\_child})$.

A leaf is a 64-byte record consisting of a 32-byte key and a 32-byte
value. The leaf hash is computed as
$\text{Hash}(\text{key} \| \text{value})$ and is not stored separately.

### Leaf Encoding

Each leaf represents an exclusion range. Implementations MUST encode
exclusion ranges as $(low, width)$ pairs, where $low$ is the lower bound
of the range and $width = high - low$.

To verify that a target nullifier $t$ falls within the exclusion range, a
client checks:

$$t - low < width$$

This is a single subtraction and a single unsigned comparison.

<details>
<summary>

### Rationale for (low, width) encoding
</summary>

The original formulation in "Air drops, Proof-of-Balance, and Stake-weighted Polling" [^draft-str4d-orchard-balance-proof] uses $(low, high)$ pairs. Verifying
$low \leq t < high$ requires two comparisons inside the ZKP circuit.

The $(low, width)$ encoding reduces this to one subtraction ($t - low$)
and one unsigned comparison ($< width$), saving one comparison gate in the
circuit. Since the exclusion range check is performed for every voting
proof, this saving applies to every governance participant.
</details>

### Authentication Path

A complete authentication path consists of 26 sibling hashes, one per
tree depth from the leaf (depth 26) to the root (depth 0). The client
MUST reconstruct the Merkle root from the retrieved path and verify it
against the published root.

## Data Structure Layout

The 26-level exclusion tree is partitioned into three tiers to balance
plaintext broadcast cost, PIR database size, and the number of PIR
queries. Each tier covers a contiguous range of tree depths.

```
Depth 0  ──────────────  root
  │
  │   TIER 0: Plaintext broadcast (11 levels)
  │   Depths 0–11
  │
Depth 11 ──────────────  2,048 subtree roots
  │
  │   TIER 1: Small PIR (8 levels)
  │   Depths 11–19
  │
Depth 19 ──────────────  524,288 subtree roots
  │
  │   TIER 2: Large PIR (7 levels)
  │   Depths 19–26
  │
Depth 26 ──────────────  leaves (up to 67,108,864)
```

| Tier | Depths | Siblings provided | Retrieval method |
|---|---|---|---|
| 0 | 0–11 | 11 | Plaintext broadcast |
| 1 | 11–19 | 8 | PIR query |
| 2 | 19–26 | 7 | PIR query |
| **Total** | | **26** | |

### Tier 0: Plaintext Broadcast (Depths 0–11)

The server MUST publish the following two data blocks as a plaintext
payload, identical for all clients:

**Block A — Subtree roots at depth 11:**

Each record contains:

| Field | Size | Purpose |
|---|---|---|
| `hash` | 32 bytes | Merkle hash of the subtree rooted at this node |
| `min_key` | 32 bytes | Smallest key in this subtree (for binary search) |

Count: $2^{11} = 2{,}048$ records $\times$ 64 bytes = **131,072 bytes
(128 KB)**.

**Block B — Internal hashes at depths 0–10:**

All internal nodes from the root down to depth 10, serialized in
breadth-first order.

Count: $2^0 + 2^1 + \cdots + 2^{10} = 2^{11} - 1 = 2{,}047$ hashes
$\times$ 32 bytes = **65,504 bytes (64 KB)**.

**Total Tier 0 payload: 192 KB.**

The Tier 0 payload is independent of the queried key and SHOULD be cached
by clients. It changes only when the exclusion tree is updated.

**Client procedure:**

1. Binary search the 2,048 `min_key` values in Block A to find subtree
   index $S_1 \in [0, 2047]$ such that
   $\text{min\_key}[S_1] \leq \text{target\_key} < \text{min\_key}[S_1 + 1]$.
2. Read 11 sibling hashes directly from the two blocks:
   - Depth-11 sibling: read `hash` from Block A at index $S_1 \oplus 1$.
   - Depths 1–10 siblings: read from Block B by walking the path
     determined by $S_1$ upward through the BFS-indexed tree.

### Tier 1: Small PIR (Depths 11–19)

The Tier 1 PIR database MUST contain one row per depth-11 subtree. Each
row contains a complete 8-level subtree (depths 11–19). The subtree root
(the depth-11 node) is not included, as the client already has it from
Tier 0.

| Property | Value | Derivation |
|---|---|---|
| Rows | $2^{11} = 2{,}048$ | One per depth-11 subtree |
| Content per row | 8-level subtree (depths 11–19) | See below |

**Internal nodes** (relative depths 1–7, absolute depths 12–18):

254 nodes ($2^8 - 2$) $\times$ 32 bytes = **8,128 bytes**.

**Leaf records** (relative depth 8, absolute depth 19):

These are Tier 2 subtree roots, each containing a 32-byte hash and a
32-byte `min_key` for binary search.

256 records $\times$ 64 bytes = **16,384 bytes**.

**Row total: 24,512 bytes (23.9 KB).**

Rows MUST be padded to 32,768 bytes (32 KB) for PIR alignment.

| Metric | Value |
|---|---|
| Raw database size | 2,048 rows $\times$ 24,512 B = **47.9 MB** |
| Padded database size | 2,048 rows $\times$ 32,768 B = **64 MB** |

**Row serialization (24,512 bytes):**

Internal nodes MUST be serialized in breadth-first order (depth 1
left-to-right, then depth 2, and so on through depth 7):

```
Bytes 0–8,127:       internal_nodes[0..253]    254 × 32 B = 8,128 B
Bytes 8,128–16,319:  leaf_hashes[0..255]       256 × 32 B = 8,192 B
Bytes 16,320–24,511: leaf_min_keys[0..255]     256 × 32 B = 8,192 B
                                                Total:      24,512 B
```

**BFS indexing:** A node at relative depth $d$, horizontal position $p$
(0-indexed) has internal node index $(2^d - 2) + p$ for
$d \in [1, 7]$, $p \in [0, 2^d)$. The sibling of position $p$ at any
depth is at position $p \oplus 1$. The parent of position $p$ is at
position $p \gg 1$ at depth $d - 1$.

**Client procedure:**

1. Issue a PIR query for row $S_1$ (the subtree index from Tier 0).
2. Binary search the 256 `min_key` values at the end of the row to find
   sub-subtree index $S_2 \in [0, 255]$.
3. Read 8 sibling hashes directly from the row:
   - Depth-19 sibling: the leaf record at index $S_2 \oplus 1$ (its
     `hash` field).
   - Depths 12–18 siblings: walk the internal nodes from position $S_2$
     upward, reading the sibling hash at each level.

### Tier 2: Large PIR (Depths 19–26)

The Tier 2 PIR database MUST contain one row per depth-19 subtree. Each
row contains a complete 7-level subtree (depths 19–26). The subtree root
(the depth-19 node) is not included, as the client already has it from
Tier 1.

| Property | Value | Derivation |
|---|---|---|
| Rows | $2^{19} = 524{,}288$ | One per depth-19 subtree |
| Content per row | 7-level subtree (depths 19–26) | See below |

**Internal nodes** (relative depths 1–6, absolute depths 20–25):

126 nodes ($2^7 - 2$) $\times$ 32 bytes = **4,032 bytes**.

**Leaf records** (relative depth 7, absolute depth 26 — the actual tree
leaves):

Each leaf contains a 32-byte key and a 32-byte value. No separate hash
field is stored; the leaf hash is computed as
$\text{Hash}(\text{key} \| \text{value})$.

128 leaves $\times$ 64 bytes = **8,192 bytes**.

**Row total: 12,224 bytes (11.9 KB).**

Rows MUST be padded to 32,768 bytes (32 KB) for PIR alignment.

| Metric | Value |
|---|---|
| Raw database size | 524,288 rows $\times$ 12,224 B = **5.97 GB** |
| Padded database size | 524,288 rows $\times$ 32,768 B = **16 GB** |

**Row serialization (12,224 bytes):**

```
Bytes 0–4,031:      internal_nodes[0..125]    126 × 32 B = 4,032 B
Bytes 4,032–8,127:  leaf_keys[0..127]         128 × 32 B = 4,096 B
Bytes 8,128–12,223: leaf_values[0..127]       128 × 32 B = 4,096 B
                                               Total:      12,224 B
```

**Client procedure:**

1. Compute the Tier 2 row index as $S_1 \times 256 + S_2$.
2. Issue a PIR query for this row.
3. Scan the 128 leaf keys to find the target key and retrieve its value.
4. Read 7 sibling hashes from the row:
   - Depth-26 sibling: the leaf at index
     $(\text{target\_position} \oplus 1)$. Compute its hash as
     $\text{Hash}(\text{key} \| \text{value})$. This is the only hash
     the client computes during the PIR retrieval phase.
   - Depths 20–25 siblings: read from the 126 internal nodes by walking
     upward from the target leaf position.

### Bandwidth Summary

| Component | Direction | Size |
|---|---|---|
| Tier 0 payload | Server to Client | 192 KB |
| PIR Query 1 (round trip) | Both | ~500 KB |
| PIR Query 2 (round trip) | Both | ~500 KB |
| **Total (first query)** | | **~1.2 MB** |
| **Total (Tier 0 cached)** | | **~1.0 MB** |

### Client Computation Summary

| Step | Binary search | Hashes computed | Sibling hashes read |
|---|---|---|---|
| Tier 0 | Over 2,048 keys | 2,047 (reconstruct depths 0–10) | 11 |
| Tier 1 | Over 256 keys | 0 | 8 |
| Tier 2 | Over 128 keys | 1 (sibling leaf hash) | 7 |
| **Total** | | **2,048** | **26** |

All hashing occurs during Tier 0 reconstruction, which can be performed
once and cached. During the latency-sensitive PIR phase (Tiers 1 and 2),
the client computes exactly 1 hash.


# Rationale

## PIR Background

Early PIR schemes, while mathematically sound, imposed prohibitive costs
on either the server or the client. Some required the server to store
large, client-specific keys, creating a stateful architecture that could
not scale to millions of users [^XPIR]. Others shifted the burden to the
client, requiring them to download massive compressed representations of
the database ("hints") before a single query could be issued, barring
cold-start applications such as mobile wallets [^SimplePIR].

YPIR [^YPIR] introduced a packing mechanism based on the CDKS
transformation [^CDKS] that compresses the hint as part of the query
response, eliminating the offline download entirely.

## Construction Choice

Our choice of YPIR+SP stems from the fact that standard YPIR (built on
DoublePIR) is only suitable for small record sizes. In our data structure
(see [Data Structure Layout]), the Tier 2 PIR layer has rows of 12,224
bytes — far too large for DoublePIR's per-element retrieval model.

YPIR+SP and InsPIRe [^InsPIRe] are both SimplePIR-based constructions
that eliminate hints and return column data. The following table compares
communication costs for a 32 GB database:

| Metric | SimplePIR | DoublePIR | YPIR | YPIR+SP | InsPIRe |
|---|---|---|---|---|---|
| Hint | 724 MB | 16 MB | **0** | **0** | **0** |
| Query | 724 KB | 1.4 MB | 2.5 MB | 2.2 MB | ~236 KB |
| Response | 724 KB | 32 KB | 12 KB | 444 KB | ~12 KB |
| Throughput | 10.4 GB/s | 9.9 GB/s | 12.1 GB/s | 6.1 GB/s | up to 9.4 GB/s |

InsPIRe achieves superior communication metrics through a novel packing
mechanism (InspiRING, requiring only 2 key-switching matrices instead of
11) and homomorphic polynomial evaluation. However, its underlying
cryptography is complex, has no known production usage, and is one year
younger than YPIR+SP, complicating auditability and imposing production
risk for a governance system that must be trustworthy from launch.

We choose YPIR+SP because it achieves a hintless design with appropriate
communication and throughput for a mobile governance system, built on the
well-understood CDKS transformation.

It is our intent to continue researching and productionizing InsPIRe
concurrently. Should InsPIRe mature and undergo sufficient auditing, a
future ZIP may specify it as a replacement or alternative.

## Data Structure Split

The 11 + 8 + 7 tier split balances three competing concerns:

1. **Tier 0 broadcast size.** The plaintext tier covers 11 levels,
   producing $2^{11} = 2{,}048$ subtree roots. At 64 bytes each, this is
   128 KB — small enough for CDN distribution or even bundling in
   application code. Increasing Tier 0 to 12 levels would double the
   broadcast to 256 KB with diminishing returns.

2. **Tier 1 PIR database size.** Each of the 2,048 rows contains an
   8-level subtree (24,512 bytes), yielding a 48 MB database (64 MB
   padded). This is small enough for efficient PIR processing.

3. **Tier 2 PIR database size.** The remaining 7 levels produce 524,288
   rows of 12,224 bytes each, yielding a 6 GB database (16 GB padded).
   This is the binding constraint for PIR scheme selection and determines
   server hardware requirements.

Only 2 PIR queries are needed, and they are inherently sequential: the
Tier 2 row index depends on the Tier 1 result. The plaintext tier
requires no PIR query at all.


# Deployment

This section will be completed before this ZIP advances to Proposed
status.


# Reference implementation

No reference implementation exists at this time.


# Open issues

1. **Tier 2 cache-line utilization.** Rows use 12,224 of 32,768 padded
   bytes (37.3% utilization). The spare 20,544 bytes per row could store
   auxiliary data such as neighboring subtree information for approximate
   key positioning.

2. **Tree updates.** When leaves change, Tier 2 rows and all ancestor
   nodes are affected. Tier 1 rows change if any descendant leaf changes.
   Tier 0 always changes. Incremental update cost depends on the PIR
   scheme's ability to handle database mutations efficiently.

3. **Query sequentiality.** The two PIR queries are inherently
   sequential — Query 2's row index depends on Query 1's result.
   Pipelining is not possible without speculative execution (querying
   multiple candidate Tier 2 rows), which would increase bandwidth.

4. **Parameter tuning for mainnet.** The parameters in
   [PIR Construction] are derived from the YPIR paper's recommendations
   for 128-bit security. Deployment may require tuning based on observed
   tree sizes and client device capabilities.

5. **CDN strategy for Tier 0.** The 192 KB plaintext payload is cacheable
   and identical for all clients. The distribution mechanism (bundled in
   software updates, served via CDN, or included in protocol messages)
   remains to be determined.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^XPIR]: [XPIR: Private Information Retrieval for Everyone](https://hal.science/hal-01396142)

[^SimplePIR]: [One Server for the Price of Two: Simple and Fast Single-Server Private Information Retrieval](https://eprint.iacr.org/2022/949)

[^YPIR]: [YPIR: High-Throughput Single-Server PIR with Silent Preprocessing](https://eprint.iacr.org/2024/270)

[^InsPIRe]: [InsPIRe: Communication-Efficient PIR with Server-side Preprocessing](https://eprint.iacr.org/2025/1352)

[^CDKS]: [Efficient Homomorphic Conversion Between Ring LWE Ciphertexts](https://eprint.iacr.org/2020/015)

[^Poseidon]: [Poseidon: A New Hash Function for Zero-Knowledge Proof Systems](https://eprint.iacr.org/2019/458)

[^draft-str4d-orchard-balance-proof]: [Orchard Balance Proof](draft-str4d-orchard-balance-proof)
