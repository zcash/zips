    ZIP: Unassigned
    Title: Private Information Retrieval for Nullifier Exclusion Proofs
    Owners: Dev Ojha <dojha@berkeley.edu>
            Roman Akhtariev <ackhtariev@gmail.com>
            Adam Tucker <adamleetucker@outlook.com>
            Greg Nagy <greg@dhamma.works>
    Status: Draft
    Category: Standards / Wallet
    Created: 2026-03-02
    License: MIT
    Pull-Request: https://github.com/zcash/zips/pull/1198


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

Packing key

: A set of $\log(d)$ key-switching matrices sent to the server as part of
  each YPIR+SP query. Each matrix encrypts an automorphism of the client's
  RLWE secret $s_2$ under $s_2$ itself, enabling the server to perform the
  CDKS transformation without learning $s_2$.

Interval Merkle tree

: A Merkle tree, where each leaf commits to a continuous range of valid values.
  A client proves inclusion of a value in one of the tree's intervals.

# Abstract

This document specifies a private information retrieval (PIR) scheme for
privately retrieving nullifier exclusion proofs from a Zcash nullifier
set. Any point-in-time protocol requiring proof-of-balance — such as
airdrops, stake-weighted polling, or governance voting — needs to verify
that notes are unspent by checking their nullifiers against the spent
set, without revealing which nullifier is being checked.

The construction uses YPIR+SP [^YPIR], a single-server PIR protocol built on
SimplePIR [^SimplePIR] whose security depends on LWE and RLWE. YPIR+SP requires
a single untrusted server, no client-side database hint and no DB 
pre-processing per client. This makes it suited for privacy in the Zcash 
setting.

The nullifier exclusion tree is a binary merkle tree, organized into a
three-tier data structure spanning 26 levels of depth: a plaintext broadcast
tier (192 KB, cacheable), a small PIR tier (24 MB), and a large PIR tier (6 GB).
A complete authentication path is retrieved in two sequential PIR queries plus
the plaintext download, for a total bandwidth of approximately 3.3 MB per
query (dominated by the Tier 2 upload).


# Motivation

Several point-in-time protocols for Zcash require a proof-of-balance:
proving that specific shielded notes are unspent at a given block height.
Usecases include airdrops, stake-weighted polling, and governance voting
systems, as described in [^draft-str4d-orchard-balance-proof]. Proving your 
balance requires proving you have a note in the note commitment tree, and it
has not been spent at that height. For privacy, we do not want to directly
reveal the client's nullifier in this balance snapshot. This means the client 
must be able to create a proof that the correct nullifier for a note was not
spent at the snapshot height. To achieve this, we make a Merkle tree of all
known nullifiers at snapshot height, and in zero knowledge prove exclusion of
the user's nullifier into this snapshot height. Hence the name "Nullifier
exclusion proof".

There is a problem though, how does the user get the exclusion proof?
A user directly querying a centralized server for the exclusion proof would
reveal their nullifier to the server, breaking the privacy guarantee.
The alternative of downloading the entire set of Orchard nullifiers is 
impractical. Its already ~2GB, and as Zcash scales this grows unboundedly.
The existing solution in the design of token holder voting prior to this ZIP is
to not allow snapshots of balances, but instead "snapshots of balances that
moved in a registration period". This lowers the download size to just grow in
the number of transactions during registration period. It comes at the cost of
voting friction (requiring users to move funds), safety, and anonymity as your 
not anonymous amongst all notes, only recently moved notes.

Private Information Retrieval (PIR) provides a cryptographic solution to 
retrieve the exclusion proofs. PIR allows a client to retrieve a record from a 
server-held database without the server learning which record was requested. 
The server processes the encrypted query by touching every record in the 
database, ensuring that its access pattern reveals nothing about the target. 
The client retrieves the exclusion proof from an untrusted server without 
revealing which nullifier it is checking (see [PIR Construction]).


# Privacy Implications

Query privacy rests entirely on the Regev encryption of the client's
selection vector (see [Regev Encryption]). Regev encryption ensures the query
is computationally indistinguishable from random under the LWE assumption. 
Therefore the server learns nothing about the target record. 
Every other component - CDKS packing, modulus switching, the packing key -
affects response correctness or cross-query linkability, but not the 
confidentiality of the query itself.

All queries have identical size for a given database configuration. The number of records the client must retrieve is based on the number of nullifiers they
must query for. The following are out of scope of this document:
- Padding the number of queries to lower metadata leakage of the number of 
notes the user owns at snapshot height.
- IP obfuscation


# Requirements


- No client-side database hint. A mobile wallet must be able to issue its
  first query without any prior large (MB) download or expensive preprocessing.
- Single untrusted server with no per-client state. The server holds only
  the public database and processes queries statelessly. A client could query
  multiple for queries 
- Total bandwidth per query (upload plus download) under
  10MB, suitable for mobile networks.
- Two sequential network round-trips per query are acceptable.
- The hash function used in the exclusion tree must be efficient inside
  zero-knowledge proof circuits.
- 128-bit computational security with correctness error probability at
  most $2^{-40}$. Re-sampling fixes this


# Non-requirements

The following are explicitly out of scope:

- Incremental database updates. The PIR database is computed once from
  the nullifier set at a given snapshot height and is treated
  as static for the duration of the protocol epoch.
- Sub-second end-to-end query latency. The two sequential PIR round-trips
  impose a latency floor determined by network conditions.
- Retrieval of data other than nullifier exclusion proofs.


# Specification

## PIR Construction

Next-generation PIR designs (YPIR, InsPIRe) build on top of SimplePIR, aiming to eliminate the hint and shrink response sizes. So we explain SimplePIR first.

### SimplePIR

In SimplePIR [^SimplePIR], the database is reshaped into a
$\sqrt{N} \times \sqrt{N}$ matrix where each cell holds one byte. The
server computes the answer as a single matrix-vector product, achieving
throughput that is constrained by the hardware's memory-bandwidth.

The client encrypts a selection vector using Regev (LWE) encryption [^Regev05] and sends it to the server.

The client requires a precomputed *hint* — the product of the database matrix with the public encryption matrix — to decrypt the response. This hint is proportional to $\sqrt{N}$ and can exceed 1 GB for large databases, making SimplePIR unsuitable for cold-start clients.

### Regev Encryption

Regev encryption [^Regev05] is the LWE-based scheme that encrypts the
client's selection vector. It is the single component on which query
privacy depends (see [Privacy Implications]).

The scheme operates in two number spaces. The *plaintext space*
$\mathbb{Z}_p$ (with $p = 2^8$) holds database values. The *ciphertext
space* $\mathbb{Z}_q$ (with $q = 2^{32}$) holds encrypted values. The
ratio $\Delta = \lfloor q / p \rfloor$ is the scaling factor that spaces
plaintext values apart in the larger ciphertext space, leaving room for
noise.

All parties agree on a public random matrix $A$ of dimensions
$n \times \sqrt{N}$, where $n = 1024$ is the LWE security parameter.
Its transpose $A^T$ is a $\sqrt{N} \times n$ matrix. The client samples
a secret vector $s$ of length $n$ and a small noise vector $e$ (each
entry drawn from a discrete Gaussian with standard deviation $\sigma$).

To encrypt a selection vector $\mu$ (zeros everywhere except a 1 at the
target row):

$$c = A^T \cdot s + e + \Delta \cdot \mu$$

The term $A^T \cdot s$ is a mask that only the client can remove (since
only the client knows $s$). The noise $e$ ensures that $c$ is
computationally indistinguishable from a uniformly random vector under
the LWE assumption: even an adversary who knows $A$ cannot recover $s$
or $\mu$.

To decrypt (given $s$):

1. Subtract the mask: $c - A^T \cdot s = e + \Delta \cdot \mu$.
2. Round each element to the nearest multiple of $\Delta$.
3. Divide by $\Delta$ to recover $\mu$.

This works because the noise $e$ is small relative to the spacing
$\Delta$. For example, with $\Delta = \lfloor 2^{32} / 256 \rfloor = 2^{24} \approx 16{,}000{,}000$ and noise magnitude on the order of tens,
rounding reliably recovers the correct plaintext.

Regev encryption is linearly homomorphic: the server can multiply the
database matrix $D$ by the encrypted query $c$ and obtain an encrypted
version of the selected row, $D \cdot c = D \cdot A^T \cdot s + D \cdot e + \Delta \cdot (D \times \mu)$, without learning which row
was selected. This matrix-vector product is the entirety of the server's
per-query work in SimplePIR.

A critical property for PIR is that the matrix $A$ is independent of the
message $\mu$. This allows the server to precompute the product $D \cdot A^T$ once, yielding the *hint* that clients use for decryption.

### Hint

After the server computes $\mathsf{answer} = D \cdot c$, the client
holds:

$$\mathsf{answer} = D \cdot A^T \cdot s + D \cdot e + \Delta \cdot (\text{selected row})$$

To isolate the selected row, the client must subtract $D \cdot A^T \cdot s$. Computing this requires $D \cdot A^T$, which depends on the
entire database — information the client does not have.

The *hint* is the precomputed product $H = D \cdot A^T$, a matrix of
dimensions $\sqrt{N} \times n$. With the hint in hand, the client
computes $H \cdot s = D \cdot A^T \cdot s$ and subtracts it from the
answer, leaving $D \cdot e + \Delta \cdot (\text{selected row})$.
Standard rounding then recovers the row values.

Because $A$ is independent of the query, the hint is the same for every
client and every query. It is computed once by the server and can be
distributed via CDN or bundled with the application. However, the hint
must be recomputed whenever the database changes, and its size is
proportional to $\sqrt{N}$, which becomes prohibitive for large
databases.

#### SimplePIR Hint

On a database of $N$ bytes, the hint size is roughly $4\sqrt{N}$ KB
[^SimplePIR]:

| Database size | Hint size            |
|---------------|----------------------|
| 100 KB        | $\approx$ 1.25 MB   |
| 10 MB         | $\approx$ 12.6 MB   |
| 1 GB          | 128 MB               |

For the Tier 2 database in this document (6 GB, see
[Tier 2: Large PIR (Depths 18–26)]), the hint would exceed 300 MB — far
beyond what a cold-start mobile client can download before its first
query. This motivates the move to YPIR+SP, which eliminates the hint
entirely by packing the SimplePIR response into RLWE ciphertexts (see
[YPIR+SP]).

### YPIR+SP

YPIR+SP [^YPIR] eliminates the hint by packing the SimplePIR response
into RLWE ciphertexts using the CDKS transformation [^CDKS].

RLWE ciphertexts encrypt $d$ values in a single ciphertext (as
coefficients of a polynomial in $\mathbb{Z}[x]/(x^d + 1)$ ), compared to
one value per LWE ciphertext. This yields dramatically less ciphertext
overhead, making it possible to compress the entire SimplePIR row
response — which would otherwise require the hint for decryption — into
a small number of RLWE ciphertexts that the client can decrypt directly.

The protocol proceeds as follows:

1. The client generates LWE secret $s_1$, RLWE secret $s_2$, and a
   packing key $pk$ consisting of key-switching matrices for the CDKS
   automorphisms.
2. The client sends the query $(c_1, pk)$ to the server, where $c_1$ is
   the Regev-encrypted row selector.
3. The server computes the SimplePIR matrix-vector product
   $T = D \times c_1$, yielding $\sqrt{N}$ LWE ciphertexts.
4. The server packs $T$ into $\lceil \sqrt{N} / d_2 \rceil$ RLWE
   ciphertexts using the CDKS transformation with the client's packing
   key.
5. The server applies modulus switching to reduce the response size and
   returns the result.
6. The client decrypts the RLWE ciphertexts with $s_2$, recovering the
   row values directly.

Unlike standard YPIR (which is built on DoublePIR and retrieves a single
element), YPIR+SP returns an entire row of the database matrix. This
makes it suitable for large records that span many bytes.

#### Parameters

Implementations MUST use the following parameters, which provide 128-bit
computational security and correctness error at most $2^{-40}$:

| Parameter | SimplePIR level | Packing level |
|---|---|---|
| Lattice dimension $n$ / Ring degree $d$ | 1024 | 2048 |
| Ciphertext modulus $q$ | $2^{32}$ | $\approx 2^{56}$ (two 28-bit NTT-friendly primes) |
| Plaintext modulus $p$ | $2^8$ | $2^{20}$ |
| Noise width $\sigma$ | $11\sqrt{2\pi}$ | $6.4\sqrt{2\pi}$ |

These parameters are taken from Table 1 of the YPIR paper [^YPIR] and
support databases up to 64 GB ($\sqrt{N} \leq 2^{18}$).

#### Security

The security of YPIR+SP relies on the LWE assumption at the SimplePIR
level (Regev encryption of the row selector) and the Ring LWE
assumption at the packing level, together with circular security (the
packing key contains encryptions of automorphisms of the secret key
under itself). In other words, the key material is encrypted with itself.

The LWE and RLWE assumptions are standard in lattice-based
cryptography. Circular security is a well-studied additional assumption
shared with Spiral and OnionPIR [^YPIR].

### Conformance

The client MUST verify that the decrypted authentication path is
consistent with the published Merkle root of the exclusion tree.

The client MUST generate a fresh RLWE secret $s_2$ and derive a new
packing key for every query. Reuse of $s_2$ across queries enables
cross-query linkability (see [Privacy Implications]).


<details>
<summary>

### Rationale for YPIR+SP over standard YPIR
</summary>

For the Tier 2 PIR database (24,512-byte rows; see
[Data Structure Layout]), standard YPIR would require 24,512 parallel
DoublePIR instances (one per byte), each with its own 16 MB hint — a
prohibitive cost. YPIR+SP avoids this: the full row is packed into RLWE
ciphertexts in a single pass, achieving ~2.6 MB total communication for
the 6 GB Tier 2 database (see [Bandwidth Summary]). See
[Construction Choice] for a comparison with other PIR schemes.
</details>

## Instantiations

### Nullifier Exclusion Tree

The server MUST construct the exclusion tree and the corresponding PIR
databases (Tiers 0, 1, and 2) once from the nullifier set at the start
of each protocol epoch. The databases are static for the duration of
the epoch.

#### Tree Structure

The exclusion tree is a sorted binary Merkle tree with depth 26, holding
up to $N = 2^{26} \approx 67$ million leaves. The tree MUST use the
Poseidon hash function [^Poseidon] for all internal node computations, as
Poseidon is designed for efficient evaluation inside zero-knowledge proof
circuits.

An internal node is a 32-byte hash:
$\mathsf{Hash}(\mathsf{left\_child} \| \mathsf{right\_child})$.

A leaf is a 64-byte record consisting of a 32-byte key and a 32-byte
value. The leaf hash is computed as
$\mathsf{Hash}(\mathsf{key} \| \mathsf{value})$ and is not stored separately.

#### Tree Construction

The tree is built from the set of all Orchard nullifiers revealed on the
consensus chain as of the snapshot height. The construction follows the
algorithm defined in [^draft-valargroup-orchard-balance-proof],
summarized here for the aspects relevant to the PIR data layout.

**Step 1: Sentinel initialization.** Before processing real nullifiers,
the builder MUST insert 17 sentinel values into the sorted set:

$$s_k = k \cdot 2^{250}, \quad k \in \{0, 1, \ldots, 16\}$$

These sentinels partition $\mathbb{F}_{q_\mathbb{P}}$ (the Pallas base
field, $q_\mathbb{P} \approx 2^{254}$) into intervals each of width
strictly less than $2^{250}$, as required for the soundness of the
in-circuit range checks defined in
[^draft-valargroup-orchard-balance-proof].

**Step 2: Build the sorted set.** Let $S$ be the union of the 17
sentinels and all revealed Orchard nullifiers at the snapshot height.
Sort $S$ in ascending order by canonical integer representation in
$\{0, \ldots, q_\mathbb{P} - 1\}$.

**Step 3: Derive exclusion ranges.** For each pair of consecutive
elements $(s_i, s_{i+1})$ in $S$ with $s_{i+1} - s_i > 1$, create a
leaf:

- $\mathsf{low} = s_i + 1$
- $\mathsf{width} = s_{i+1} - s_i - 2$

Consecutive elements with $s_{i+1} - s_i = 1$ produce no leaf (there is
no unrevealed value between them).

If $s_{m-1} < q_\mathbb{P} - 1$ (where $s_{m-1}$ is the largest element
in $S$), a terminal leaf MUST be added with
$\mathsf{low} = s_{m-1} + 1$ and
$\mathsf{width} = (q_\mathbb{P} - 1) - \mathsf{low}$.

**Leaf count.** Starting from 17 sentinels (which produce at most 17
initial interval leaves), each additional nullifier splits one interval
into at most two, adding at most one leaf. After inserting $k$ distinct
nullifiers the tree contains at most $17 + k$ real leaves. As of early
2026 the Orchard pool contains approximately 51 million nullifiers,
yielding approximately 51 million leaves — within the $2^{26} \approx
67$ million capacity of the depth-26 tree.

**Step 4: Pad to $2^{26}$ leaves.** The three-tier layout requires a
complete binary tree with exactly $2^{26}$ leaf positions. The builder
MUST pad the tree as follows.

The canonical empty leaf has $\mathsf{key} = 0$ and
$\mathsf{value} = 0$ (i.e., $\mathsf{low} = 0$, $\mathsf{width} = 0$),
with leaf hash $\mathsf{Hash}(0 \| 0)$, consistent with the empty-leaf
definition in [^draft-valargroup-orchard-balance-proof].

Real exclusion-range leaves MUST occupy the rightmost (highest-index)
leaf positions, sorted in ascending order by $\mathsf{low}$. The
remaining leftmost positions MUST be filled with canonical empty leaves.
Because the smallest sentinel is $s_0 = 0$, all real leaves have
$\mathsf{low} \geq 1$, so the key ordering across the full leaf array is
non-decreasing: empty leaves (key 0) precede all real leaves (key
$\geq 1$). This ordering is required by the binary search procedures in
[Tier 0: Plaintext Broadcast (Depths 0–11)],
[Tier 1: Small PIR (Depths 11–18)], and
[Tier 2: Large PIR (Depths 18–26)].

In those procedures, the `min_key` of any subtree consisting entirely of
empty leaves is 0. Because no valid target nullifier equals 0 (it is a
sentinel), the binary search condition
$\mathsf{min\_key}[S] \leq t < \mathsf{min\_key}[S + 1]$ cannot be
satisfied when both $S$ and $S + 1$ index empty-only subtrees (since
$\mathsf{min\_key}[S + 1] = 0 \not> t$ for any $t > 0$). The search
therefore always resolves to a subtree containing real leaves.

#### Leaf Encoding

Each leaf represents an exclusion range. Implementations MUST encode
exclusion ranges as $(low, width)$ pairs, where $low$ is the lower bound
of the range and $width = high - low$. Both $low$ and $width$ are
elements of $\mathbb{F}_ {q_ \mathbb{P}}$ (the Pallas base field [^protocol-pallasandvesta]), as are
nullifiers.

To verify that a target nullifier $t$ falls within the exclusion range,
the circuit MUST check:

$$\mathsf{int}(t - low \bmod q_\mathbb{P}) < \mathsf{int}(width)$$

where $\mathsf{int}(\cdot)$ denotes the canonical integer representation
in $\{0, \ldots, q_\mathbb{P} - 1\}$. The subtraction is performed in
$\mathbb{F}_ {q_ \mathbb{P}}$; the comparison is an unsigned integer
comparison on the canonical representatives.

The tree builder MUST ensure that $\mathsf{int}(low) + \mathsf{int}(width) < q_\mathbb{P}$
for every leaf, so that the exclusion range does not wrap around the
field modulus. Under this invariant, $t - low$ does not wrap for any
$t$ in the range, and the single unsigned comparison is sufficient.

<details>
<summary>

#### Rationale for (low, width) encoding
</summary>

The original formulation in "Air drops, Proof-of-Balance, and Stake-weighted Polling" [^draft-str4d-orchard-balance-proof] uses $(start, end)$ pairs. Verifying
$start \leq t \leq end$ requires two comparisons inside the ZKP circuit.

The $(low, width)$ encoding reduces this to one subtraction ($t - low$)
and one unsigned comparison ($< width$), saving one comparison gate in the
circuit. Since the exclusion range check is performed for every balance
proof, this saving applies to every protocol participant.
</details>

#### Authentication Path

A complete authentication path consists of 26 sibling hashes, one per
tree depth from the leaf (depth 26) to the root (depth 0). The client
MUST reconstruct the Merkle root from the retrieved path and verify it
against the published root.

#### Data Structure Layout

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
  │   TIER 1: Small PIR (7 levels)
  │   Depths 11–18
  │
Depth 18 ──────────────  262,144 subtree roots
  │
  │   TIER 2: Large PIR (8 levels)
  │   Depths 18–26
  │
Depth 26 ──────────────  leaves (up to 67,108,864)
```

| Tier | Depths | Siblings provided | Retrieval method |
|---|---|---|---|
| 0 | 0–11 | 11 | Plaintext broadcast |
| 1 | 11–18 | 7 | PIR query |
| 2 | 18–26 | 8 | PIR query |
| **Total** | | **26** | |

##### Tier 0: Plaintext Broadcast (Depths 0–11)

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
   index $S_1 \in \lbrack 0, 2047\rbrack$ such that
   $\mathsf{min\_key}\lbrack S_1\rbrack \leq \mathsf{target\_key} < \mathsf{min\_key}\lbrack S_1 + 1\rbrack$.
2. Read 11 sibling hashes directly from the two blocks:
   - Depth-11 sibling: read `hash` from Block A at index $S_1 \oplus 1$.
   - Depths 1–10 siblings: read from Block B by walking the path
     determined by $S_1$ upward through the BFS-indexed tree.

##### Tier 1: Small PIR (Depths 11–18)

The Tier 1 PIR database MUST contain one row per depth-11 subtree. Each
row contains a complete 7-level subtree (depths 11–18). The subtree root
(the depth-11 node) is not included, as the client already has it from
Tier 0.

| Property | Value | Derivation |
|---|---|---|
| Rows | $2^{11} = 2{,}048$ | One per depth-11 subtree |
| Content per row | 7-level subtree (depths 11–18) | See below |

**Internal nodes** (relative depths 1–6, absolute depths 12–17):

126 nodes ($2^7 - 2$) $\times$ 32 bytes = **4,032 bytes**.

**Leaf records** (relative depth 7, absolute depth 18):

These are Tier 2 subtree roots, each containing a 32-byte hash and a
32-byte `min_key` for binary search.

128 records $\times$ 64 bytes = **8,192 bytes**.

**Row total: 12,224 bytes (11.9 KB).**

The PIR value size for Tier 1 MUST be set to the row size (12,224 bytes)
or the next implementation-required alignment boundary. Tier 1 and
Tier 2 are independent PIR databases and do not share a value size.

| Metric | Value |
|---|---|
| Database size | 2,048 rows $\times$ 12,224 B = **23.9 MB** |

**Row serialization (12,224 bytes):**

Internal nodes MUST be serialized in breadth-first order (depth 1
left-to-right, then depth 2, and so on through depth 6):

```
Bytes 0–4,031:      internal_nodes[0..125]    126 × 32 B = 4,032 B
Bytes 4,032–8,127:  leaf_hashes[0..127]       128 × 32 B = 4,096 B
Bytes 8,128–12,223: leaf_min_keys[0..127]     128 × 32 B = 4,096 B
                                               Total:      12,224 B
```

**BFS indexing:** A node at relative depth $d$, horizontal position $p$
(0-indexed) has internal node index $(2^d - 2) + p$ for
$d \in \lbrack 1, 6\rbrack$, $p \in \lbrack 0, 2^d)$. The sibling of position $p$ at any
depth is at position $p \oplus 1$. The parent of position $p$ is at
position $p \gg 1$ at depth $d - 1$.

**Client procedure:**

1. Issue a PIR query for row $S_1$ (the subtree index from Tier 0).
2. Binary search the 128 `min_key` values at the end of the row to find
   sub-subtree index $S_2 \in \lbrack 0, 127\rbrack$.
3. Read 7 sibling hashes directly from the row:
   - Depth-18 sibling: the leaf record at index $S_2 \oplus 1$ (its
     `hash` field).
   - Depths 12–17 siblings: walk the internal nodes from position $S_2$
     upward, reading the sibling hash at each level.

##### Tier 2: Large PIR (Depths 18–26)

The Tier 2 PIR database MUST contain one row per depth-18 subtree. Each
row contains a complete 8-level subtree (depths 18–26). The subtree root
(the depth-18 node) is not included, as the client already has it from
Tier 1.

| Property | Value | Derivation |
|---|---|---|
| Rows | $2^{18} = 262{,}144$ | One per depth-18 subtree |
| Content per row | 8-level subtree (depths 18–26) | See below |

**Internal nodes** (relative depths 1–7, absolute depths 19–25):

254 nodes ($2^8 - 2$) $\times$ 32 bytes = **8,128 bytes**.

**Leaf records** (relative depth 8, absolute depth 26 — the actual tree
leaves):

Each leaf contains a 32-byte key and a 32-byte value. No separate hash
field is stored; the leaf hash is computed as
$\mathsf{Hash}(\mathsf{key} \| \mathsf{value})$.

256 leaves $\times$ 64 bytes = **16,384 bytes**.

**Row total: 24,512 bytes (23.9 KB).**

The PIR value size for Tier 2 MUST be set to the row size (24,512 bytes)
or the next implementation-required alignment boundary.

| Metric | Value |
|---|---|
| Database size | 262,144 rows $\times$ 24,512 B = **5.98 GB** |

**Row serialization (24,512 bytes):**

```
Bytes 0–8,127:       internal_nodes[0..253]    254 × 32 B = 8,128 B
Bytes 8,128–16,319:  leaf_keys[0..255]         256 × 32 B = 8,192 B
Bytes 16,320–24,511: leaf_values[0..255]       256 × 32 B = 8,192 B
                                                Total:      24,512 B
```

**Client procedure:**

1. Compute the Tier 2 row index as $S_1 \times 128 + S_2$.
2. Issue a PIR query for this row.
3. Binary search the 256 leaf keys to find the target key and retrieve
   its value.
4. Read 8 sibling hashes from the row:
   - Depth-26 sibling: the leaf at index
     $(\mathsf{target\_position} \oplus 1)$. Compute its hash as
     $\mathsf{Hash}(\mathsf{key} \| \mathsf{value})$. This is the only hash
     the client computes during the PIR retrieval phase.
   - Depths 19–25 siblings: read from the 254 internal nodes by walking
     upward from the target leaf position.

##### Bandwidth Summary

| Component | Upload | Download | Round trip |
|---|---|---|---|
| Tier 0 payload | — | 192 KB | 192 KB |
| PIR Query 1 (Tier 1, 24 MB) | 544 KB | ~48 KB | ~592 KB |
| PIR Query 2 (Tier 2, 6 GB) | 2.5 MB | ~84 KB | ~2.6 MB |
| **Total (first query)** | **3.0 MB** | **~324 KB** | **~3.3 MB** |
| **Total (Tier 0 cached)** | **3.0 MB** | **~132 KB** | **~3.1 MB** |

Upload is dominated by the Tier 2 row selector ($c_1$, proportional
to the number of database rows) and the packing key ($pk$, ~462 KB
fixed). Downloads are small because RLWE packing compresses the row
response efficiently.

##### Client Computation Summary

| Step | Binary search | Hashes computed | Sibling hashes read |
|---|---|---|---|
| Tier 0 | Over 2,048 keys | 2,047 (reconstruct depths 0–10) | 11 |
| Tier 1 | Over 128 keys | 0 | 7 |
| Tier 2 | Over 256 keys | 1 (sibling leaf hash) | 8 |
| **Total** | | **2,048** | **26** |

All hashing occurs during Tier 0 reconstruction, which can be performed
once and cached. During the latency-sensitive PIR phase (Tiers 1 and 2),
the client computes exactly 1 hash.


# Rationale

## Construction Choice

YPIR+SP and InsPIRe build on SimplePIR while supporting full-row retrieval (see [YPIR+SP]).

The following table compares communication costs for a 32 GB database:

| Metric | SimplePIR | DoublePIR | YPIR | YPIR+SP | InsPIRe |
|---|---|---|---|---|---|
| Hint | 724 MB | 16 MB | **0** | **0** | **0** |
| Query | 724 KB | 1.4 MB | 2.5 MB | 2.2 MB | ~1.1 MB |
| Response | 724 KB | 32 KB | 12 KB | 444 KB | ~96 KB |
| Throughput | 10.4 GB/s | 9.9 GB/s | 12.1 GB/s | 6.1 GB/s | up to 9.4 GB/s |

<details>
<summary>

### Sources for comparison table
</summary>

The SimplePIR, DoublePIR, and YPIR columns are from Table 2 of the YPIR
paper [^YPIR] (32 GB database, single-bit retrieval). The YPIR+SP column
is from Table 7 of the same paper (32 GB database, 64 KB records). The
InsPIRe column is from Table 4 of the InsPIRe paper [^InsPIRe] (32 GB
database, 32 KB entries, full InsPIRe variant): ~1.1 MB query, ~96 KB
response, and up to 9.4 GB/s throughput (9,360 MB/s).
</details>

InsPIRe achieves superior communication metrics through a novel packing
mechanism (InspiRING, requiring only 2 key-switching matrices instead of
11) and homomorphic polynomial evaluation. However, its underlying
cryptography is complex, has no known production usage, and is one year
younger than YPIR+SP, complicating auditability and imposing production
risk for a system that must be trustworthy from launch.

We choose YPIR+SP because it achieves a hintless design with appropriate
communication and throughput for mobile clients, built on the
well-understood CDKS transformation.

It is our intent to continue researching and productionizing InsPIRe
concurrently. Should InsPIRe mature and undergo sufficient auditing, a
future ZIP may specify it as a replacement or alternative.

## Data Structure Split

The 11 + 7 + 8 tier split balances three competing concerns:

1. **Tier 0 broadcast size.** The plaintext tier covers 11 levels,
   producing $2^{11} = 2{,}048$ subtree roots (128 KB) plus 2,047
   internal hashes (64 KB), totaling 192 KB — small enough for CDN
   distribution or even bundling in application code. Increasing Tier 0
   to 12 levels would roughly double the broadcast with diminishing
   returns.

2. **Tier 1 PIR database size.** Each of the 2,048 rows contains a
   7-level subtree (12,224 bytes), yielding a 24 MB database. This is
   small enough for efficient PIR processing.

3. **Tier 2 PIR database size.** The remaining 8 levels produce 262,144
   rows of 24,512 bytes each, yielding a 6 GB database. This is the
   binding constraint for PIR scheme selection and determines server
   hardware requirements.

Compared to an 11 + 8 + 7 split, moving one Merkle layer from Tier 1
into Tier 2 halves the number of Tier 2 rows (from 524,288 to 262,144)
at the cost of doubling the row size (from 12,224 to 24,512 bytes).
Because the YPIR query upload scales linearly with the number of
database rows while the response scales with row size, this trade-off
reduces the dominant upload cost by approximately 44% (from 4.5 MB to
2.5 MB) with no net change in total download (the total YPIR instances
that impact response size across both tiers remains constant at 11).

Moving to 12 + 8 + 6 split showed an inverse effect of doubling
the number of rows for both Tier 2 and Tier 1. Thus, increasing query sizes
which is the dominant communication cost.

Two hard constraints from the YPIR library further limit the design space.
YPIR requires `num_items` $\geq 2^{11}$, setting a floor of 2,048
rows for any PIR tier. YPIR also requires `item_size_bits` $\geq
2{,}048 \times 14 = 28{,}672$, setting a floor of 3,584 bytes per row.
The 11 + 7 + 8 split satisfies both (Tier 1 has 2,048 rows; Tier 2 has
24,512-byte rows). Alternative splits such as 10 + 8 + 8 (violates the
Tier 1 row minimum) and 13 + 8 + 5 (violates the Tier 2 minimum item
size) are infeasible without modifying YPIR.

As a result, 11 + 7 + 8 tier split is the optimal.

Only 2 PIR queries are needed, and they are inherently sequential: the
Tier 2 row index depends on the Tier 1 result. Pipelining is not
possible without speculative execution (querying multiple candidate
Tier 2 rows), which would increase bandwidth. The plaintext tier
requires no PIR query at all.

## Per-Tier PIR Value Sizing

A uniform value size (e.g., 32 KB) would inflate Tier 1 from 24 MB to
64 MB and Tier 2 from 6 GB to 8 GB. Since YPIR+SP touches every byte
per query, unused padding directly increases server computation time.
Per-tier sizing eliminates this overhead.

## Tree Depth vs. Circuit Depth

The PIR data structure uses a tree of depth 26, which is sufficient for
the current Orchard nullifier set (~51 million nullifiers, well within
the $2^{26} \approx 67$ million leaf capacity). The Claim circuit
defined in [^draft-valargroup-orchard-balance-proof], however, fixes
the non-membership Merkle path depth at 29, supporting up to
$2^{29} \approx 537$ million leaves.

These depths intentionally differ. The tree used by the PIR server has
depth 29 (matching the circuit), but only the bottom 26 levels contain
meaningful variation. The top 3 levels of the authentication path, from
the depth-26 subtree root up to the depth-29 tree root, have
deterministic siblings: each is the root hash of a completely empty
subtree, computable from the canonical empty leaf hash. The client
appends these 3 known sibling hashes to the 26 siblings retrieved via
PIR, producing a full depth-29 authentication path for the circuit.

This costs approximately 1,000 additional constraints in the Claim
circuit (3 extra Poseidon hashes, each roughly 330 constraints at width
$t = 3$). This overhead does not increase the minimum SRS degree for
the polynomial commitment scheme, because the total circuit size remains
within the same power-of-two bound.

The benefit is that the circuit's proving and verification keys support
trees up to depth 29 without regeneration. As the Orchard nullifier set
grows beyond $2^{26}$, only the PIR tier structure and server databases
need to be updated. The circuit parameters remain unchanged. Changing
the circuit depth would require new key generation and distribution to
all clients, an operationally costly step that this headroom avoids.


# Deployment

This section will be completed before this ZIP advances to Proposed
status.

<div class="note"></div>

Server deployment benefits from AVX-512 support for the ring-packing
step (the CDKS LWE-to-RLWE transformation), which involves NTT-based
polynomial arithmetic that is compute-bound. However, the dominant
per-query cost — the SimplePIR database scan — is memory-bandwidth
bound and does not benefit from wider SIMD lanes.


# Reference implementation

The underlying PIR primitive is implemented in the YPIR library [^ypir-impl],
which provides the single-server private information retrieval scheme described
in [^YPIR], including the YPIR+SP variant used by this ZIP.

A full reference implementation of the application-specific layers — the
three-tier Poseidon tree, the Tier 1 / Tier 2 query orchestration desribed in this ZIP — is provided in [^nullifier-pir-impl].



# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^XPIR]: [XPIR: Private Information Retrieval for Everyone](https://hal.science/hal-01396142)

[^SimplePIR]: [One Server for the Price of Two: Simple and Fast Single-Server Private Information Retrieval](https://eprint.iacr.org/2022/949)

[^YPIR]: [YPIR: High-Throughput Single-Server PIR with Silent Preprocessing](https://eprint.iacr.org/2024/270)

[^InsPIRe]: [InsPIRe: Communication-Efficient PIR with Server-side Preprocessing](https://eprint.iacr.org/2025/1352)

[^CDKS]: [Efficient Homomorphic Conversion Between Ring LWE Ciphertexts](https://eprint.iacr.org/2020/015)

[^Regev05]: [On Lattices, Learning with Errors, Random Linear Codes, and Cryptography](https://doi.org/10.1145/1568318.1568324)

[^Poseidon]: [Poseidon: A New Hash Function for Zero-Knowledge Proof Systems](https://eprint.iacr.org/2019/458)

[^nullifier-pir-impl]: [Nullifier PIR reference implementation](https://github.com/valargroup/vote-nullifier-pir)

[^ypir-impl]: [YPIR reference implementation (artifact branch)](https://github.com/menonsamir/ypir/tree/artifact)

[^protocol-pallasandvesta]: [Zcash Protocol Specification, Section 5.4.9.6: Pallas and Vesta](protocol/protocol.pdf#pallasandvesta)

[^draft-str4d-orchard-balance-proof]: [Air drops, Proof-of-Balance, and Stake-weighted Polling](draft-str4d-orchard-balance-proof)

[^draft-valargroup-orchard-balance-proof]: [Orchard Proof-of-Balance](draft-valargroup-orchard-balance-proof)
