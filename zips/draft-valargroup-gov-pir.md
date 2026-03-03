    ZIP: Unassigned
    Title: Private Information Retrieval for Governance
    Owners: Dev Ojha <dojha@berkeley.edu>
      Roman Akhtariev <>,
      Adam Tucker <>,
      Greg Nagy <>
    Status: Draft
    Category: Standards
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

Packing key

: A set of $\log(d)$ key-switching matrices sent to the server as part of
  each YPIR+SP query. Each matrix encrypts an automorphism of the client's
  RLWE secret $s_2$ under $s_2$ itself, enabling the server to perform the
  CDKS transformation without learning $s_2$. The packing key is
  approximately 462 KB and is visible to the server in plaintext; a fresh
  packing key (derived from a fresh $s_2$) must be generated per query to
  prevent cross-query linkability (see [Privacy Implications]).

Interval Merkle tree

: A Merkle tree, where each leaf commits to a continuous range of valid values.
  A client proves inclusion of a value in one of the tree's intervals.

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
plaintext download, for a total bandwidth of approximately 5.4 MB per
query (dominated by the Tier 2 upload).

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
with up to $2^{26} \approx 67$ million leaf slots, the exclusion tree
exceeds 6 GB, far beyond what a mobile client can store or process.

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
server is assumed to follow the protocol faithfully but may attempt to
learn which record the client queries (the honest-but-curious model).
Under the hardness of the LWE and Ring LWE problems (see [Security]),
such a server learns nothing about which nullifier the client queries.

A malicious server that deviates from the protocol cannot break query
privacy (which depends only on the client's Regev encryption), but it
can return incorrect results. The client detects this because the
decrypted authentication path must be consistent with the published
Merkle root (see [Conformance]); a corrupted response will fail this
verification.

The single most critical component for user privacy is the correctness of
Regev encryption on the client side. The query vector — a Regev-encrypted
row selector that picks the target database row (see [YPIR+SP]) —
is what the server multiplies against the entire database. If Regev
encryption is implemented correctly, the query is computationally
indistinguishable from random and the server learns nothing about the
target row. Every other component in the protocol — CDKS packing,
modulus switching, the packing key — affects correctness of the response
or cross-query linkability, but not the confidentiality of the query
itself. A bug in packing may produce a garbled answer; a bug in Regev
encryption leaks which record the client asked for.

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

The packing key $pk$ — approximately 462 KB of key-switching matrices —
is sent to the server in plaintext as part of every query. If a client
reuses the same packing key across queries, the server can compare the
bytes and trivially conclude the queries came from the same client, even
though it cannot determine which records were requested. This linkability
reveals the number of queries a participant makes and enables correlation
with external timing or network metadata.

Clients must therefore generate a fresh RLWE secret $s_2$ and derive a
new packing key for every query. Regenerating from the same $s_2$ with
fresh randomness is insufficient: the server receives key-switching
matrices that encrypt known automorphisms of $s_2$, and could test
consistency across two key sets to link them to the same underlying
secret.


# Requirements

The following high-level goals guide the design. They are not conformance
requirements.

- No client-side database hint. A mobile wallet must be able to issue its
  first query without any prior download or preprocessing.
- Single untrusted server with no per-client state. The server holds only
  the public database and processes queries statelessly.
- Total bandwidth per query (upload plus download) under
  10MB, suitable for mobile networks (see actual results [Bandwidth Summary]).
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
- Incremental database updates. The PIR database is computed once from
  the nullifier set at the start of each governance round and is treated
  as static for the duration of that round.
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
selection vector using Regev (LWE) encryption [^Regev05] and sends it to the server.
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

### Parameters

Implementations MUST use the following parameters, which provide 128-bit
computational security and correctness error at most $2^{-40}$:

| Parameter | SimplePIR level | Packing level |
|---|---|---|
| Ring dimension $d$ | 1024 | 2048 |
| Ciphertext modulus $q$ | $2^{32}$ | $\approx 2^{56}$ (two 28-bit NTT-friendly primes) |
| Plaintext modulus $p$ | $2^8$ | $2^{20}$ |
| Noise width $\sigma$ | $11\sqrt{2\pi}$ | $6.4\sqrt{2\pi}$ |

These parameters are taken from Table 1 of the YPIR paper [^YPIR] and
support databases up to 64 GB ($\sqrt{N} \leq 2^{18}$).

### Security

The security of YPIR+SP relies on the LWE assumption at the SimplePIR
level (Regev encryption of the row selector) and the Ring LWE
assumption at the packing level, together with circular security (the
packing key contains encryptions of automorphisms of the secret key
under itself). In other words, the key material is encrypted with itself.

The LWE and RLWE assumptions are standard in lattice-based
cryptography. Circular security is a well-studied additional assumption
shared with Spiral and OnionPIR [^YPIR].

### Conformance

The server MUST implement YPIR+SP as described in this section with the
parameters specified in [Parameters].

The client MUST verify that the decrypted authentication path is
consistent with the published Merkle root of the exclusion tree.


<details>
<summary>

### Rationale for YPIR+SP over standard YPIR
</summary>

Standard YPIR is built on DoublePIR and retrieves a single database
element per query. This means a large multi-byte record cannot be
retrieved in a single query.

In our data structure (see [Data Structure Layout]), the Tier 2 PIR
database has rows of 12,224 bytes. Retrieving a row of this size with
standard YPIR would require running 12,224 parallel DoublePIR instances
(one per byte), each with its own 16 MB hint — a prohibitive cost.

YPIR+SP returns an entire row from the SimplePIR matrix, and the full
row is packed into RLWE ciphertexts in a single pass. For a 32 GB
database with 64 KB records,
YPIR+SP achieves 2.6 MB total communication (query plus response) compared
to standard YPIR's inability to handle the record size efficiently.
</details>

## Instantiations

### Nullifier Exclusion Tree

The governance system requires each participant to prove that the
nullifiers associated with their voting notes do not appear in the set of
spent nullifiers. This proof takes the form of a zero-knowledge proof over
the authentication path of the enclosing exclusion range in a sorted
Merkle tree, building on the approach described in
"Air drops, Proof-of-Balance, and Stake-weighted Polling" [^draft-str4d-orchard-balance-proof].

The server MUST construct the exclusion tree and the corresponding PIR
databases (Tiers 0, 1, and 2) once from the nullifier set at the start
of each governance round. The databases are static for the duration of
the round.

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

#### Leaf Encoding

Each leaf represents an exclusion range. Implementations MUST encode
exclusion ranges as $(low, width)$ pairs, where $low$ is the lower bound
of the range and $width = high - low$. Both $low$ and $width$ are
elements of $\mathbb{F}_{q_\mathbb{P}}$ (the Pallas base field [^protocol-pallasandvesta]), as are
nullifiers.

To verify that a target nullifier $t$ falls within the exclusion range,
the circuit MUST check:

$$\mathsf{int}(t - low \bmod q_\mathbb{P}) < \mathsf{int}(width)$$

where $\mathsf{int}(\cdot)$ denotes the canonical integer representation
in $\{0, \ldots, q_\mathbb{P} - 1\}$. The subtraction is performed in
$\mathbb{F}_{q_\mathbb{P}}$; the comparison is an unsigned integer
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
circuit. Since the exclusion range check is performed for every voting
proof, this saving applies to every governance participant.
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
   index $S_1 \in [0, 2047]$ such that
   $\mathsf{min\_key}[S_1] \leq \mathsf{target\_key} < \mathsf{min\_key}[S_1 + 1]$.
2. Read 11 sibling hashes directly from the two blocks:
   - Depth-11 sibling: read `hash` from Block A at index $S_1 \oplus 1$.
   - Depths 1–10 siblings: read from Block B by walking the path
     determined by $S_1$ upward through the BFS-indexed tree.

##### Tier 1: Small PIR (Depths 11–19)

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

The PIR value size for Tier 1 MUST be set to the row size (24,512 bytes)
or the next implementation-required alignment boundary. Tier 1 and
Tier 2 are independent PIR databases and do not share a value size.

| Metric | Value |
|---|---|
| Database size | 2,048 rows $\times$ 24,512 B = **47.9 MB** |

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

##### Tier 2: Large PIR (Depths 19–26)

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
$\mathsf{Hash}(\mathsf{key} \| \mathsf{value})$.

128 leaves $\times$ 64 bytes = **8,192 bytes**.

**Row total: 12,224 bytes (11.9 KB).**

The PIR value size for Tier 2 MUST be set to the row size (12,224 bytes)
or the next implementation-required alignment boundary. Tier 1 and
Tier 2 are independent PIR databases and do not share a value size.

| Metric | Value |
|---|---|
| Database size | 524,288 rows $\times$ 12,224 B = **5.97 GB** |

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
3. Binary search the 128 leaf keys to find the target key and retrieve
   its value.
4. Read 7 sibling hashes from the row:
   - Depth-26 sibling: the leaf at index
     $(\mathsf{target\_position} \oplus 1)$. Compute its hash as
     $\mathsf{Hash}(\mathsf{key} \| \mathsf{value})$. This is the only hash
     the client computes during the PIR retrieval phase.
   - Depths 20–25 siblings: read from the 126 internal nodes by walking
     upward from the target leaf position.

##### Bandwidth Summary

| Component | Upload | Download | Round trip |
|---|---|---|---|
| Tier 0 payload | — | 192 KB | 192 KB |
| PIR Query 1 (Tier 1, 48 MB) | 544 KB | ~84 KB | ~628 KB |
| PIR Query 2 (Tier 2, 6 GB) | 4.5 MB | ~48 KB | ~4.5 MB |
| **Total (first query)** | **5.0 MB** | **~324 KB** | **~5.4 MB** |
| **Total (Tier 0 cached)** | **5.0 MB** | **~132 KB** | **~5.2 MB** |

Upload is dominated by the Tier 2 row selector ($c_1$, proportional
to the number of database rows) and the packing key ($pk$, ~462 KB
fixed). Downloads are small because RLWE packing compresses the row
response efficiently.

##### Client Computation Summary

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

Standard YPIR (DoublePIR-based) retrieves a single element per query,
which cannot serve the 12,224-byte rows in our Tier 2 layout (see
[Data Structure Layout]). Both YPIR+SP and InsPIRe [^InsPIRe] build on
SimplePIR and return full row data; the following table compares their
communication costs for a 32 GB database:

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
risk for a governance system that must be trustworthy from launch.

We choose YPIR+SP because it achieves a hintless design with appropriate
communication and throughput for a mobile governance system, built on the
well-understood CDKS transformation.

It is our intent to continue researching and productionizing InsPIRe
concurrently. Should InsPIRe mature and undergo sufficient auditing, a
future ZIP may specify it as a replacement or alternative.

## Parameter Selection

The parameters in [Parameters] are taken directly from the YPIR paper's
recommendations for 128-bit security with correctness error at most
$2^{-40}$. These are not expected to require modification for mainnet
deployment as long as the nullifier tree remains within the 64 GB
database limit ($\sqrt{N} \leq 2^{18}$). Tuning would only be
considered if observed tree sizes or client device capabilities
require it.

## Data Structure Split

The 11 + 8 + 7 tier split balances three competing concerns:

1. **Tier 0 broadcast size.** The plaintext tier covers 11 levels,
   producing $2^{11} = 2{,}048$ subtree roots (128 KB) plus 2,047
   internal hashes (64 KB), totaling 192 KB — small enough for CDN
   distribution or even bundling in application code. Increasing Tier 0
   to 12 levels would roughly double the broadcast with diminishing
   returns.

2. **Tier 1 PIR database size.** Each of the 2,048 rows contains an
   8-level subtree (24,512 bytes), yielding a 48 MB database. This is
   small enough for efficient PIR processing.

3. **Tier 2 PIR database size.** The remaining 7 levels produce 524,288
   rows of 12,224 bytes each, yielding a 6 GB database. This is the
   binding constraint for PIR scheme selection and determines server
   hardware requirements.

Only 2 PIR queries are needed, and they are inherently sequential: the
Tier 2 row index depends on the Tier 1 result. Pipelining is not
possible without speculative execution (querying multiple candidate
Tier 2 rows), which would increase bandwidth. The plaintext tier
requires no PIR query at all.

## Per-Tier PIR Value Sizing

Tier 1 and Tier 2 are independent PIR databases with separate queries.
There is no requirement that they share a PIR value size. Configuring
each tier's value size to match its actual row size — 24,512 bytes for
Tier 1 and 12,224 bytes for Tier 2 — avoids wasted padding and reduces
the effective database size the server must scan per query.

A naive approach would use a single uniform value size (e.g., 32 KB)
for both tiers. This would inflate Tier 1 from 48 MB to 64 MB (74.8%
utilization) and Tier 2 from 6 GB to 16 GB (37.3% utilization). Since
YPIR+SP touches every byte of the database per query, unused padding
directly increases server computation time. Per-tier sizing eliminates
this overhead.


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

A full reference implementation of the governance-specific layers — the
three-tier Poseidon tree, the Tier 1 / Tier 2 query orchestration, and the
client-side balance proof integration described in this ZIP — is to be
provided before this ZIP advances to Proposed status.



# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^XPIR]: [XPIR: Private Information Retrieval for Everyone](https://hal.science/hal-01396142)

[^SimplePIR]: [One Server for the Price of Two: Simple and Fast Single-Server Private Information Retrieval](https://eprint.iacr.org/2022/949)

[^YPIR]: [YPIR: High-Throughput Single-Server PIR with Silent Preprocessing](https://eprint.iacr.org/2024/270)

[^InsPIRe]: [InsPIRe: Communication-Efficient PIR with Server-side Preprocessing](https://eprint.iacr.org/2025/1352)

[^CDKS]: [Efficient Homomorphic Conversion Between Ring LWE Ciphertexts](https://eprint.iacr.org/2020/015)

[^Regev05]: [On Lattices, Learning with Errors, Random Linear Codes, and Cryptography](https://doi.org/10.1145/1568318.1568324)

[^Poseidon]: [Poseidon: A New Hash Function for Zero-Knowledge Proof Systems](https://eprint.iacr.org/2019/458)

[^ypir-impl]: [YPIR reference implementation (artifact branch)](https://github.com/menonsamir/ypir/tree/artifact)

[^protocol-pallasandvesta]: [Zcash Protocol Specification, Section 5.4.9.6: Pallas and Vesta](protocol/protocol.pdf#pallasandvesta)

[^draft-str4d-orchard-balance-proof]: [Air drops, Proof-of-Balance, and Stake-weighted Polling](draft-str4d-orchard-balance-proof)
