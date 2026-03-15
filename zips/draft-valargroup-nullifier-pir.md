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

: Auxiliary key material sent as part of each YPIR+SP query that enables
  the server to apply the CDKS packing procedure to ciphertexts
  encrypted for the client, without learning the client's packing-level
  secret key.

Interval Merkle tree

: A Merkle tree, where each leaf commits to a continuous range of valid values.
  A client proves inclusion of a value in one of the tree's intervals.

Protocol Epoch

: A bounded time period during which the nullifier exclusion tree and its
  derived PIR databases, computed from a specific snapshot height, are treated
  as static. Each consuming protocol defines its own epoch duration (e.g. a
  voting round in a snapshot-based governance system [^draft-voting-protocol]).

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

For the Orchard nullifier set of size 49,813,801 (as of block height 3,268,870), the nullifier exclusion tree is a binary merkle tree, organized into a
three-tier data structure spanning 26 levels of depth:

1. Plaintext broadcast tier (192 KB, cacheable)
2. Small PIR tier (24 MB)
3. Large PIR tier (6 GB).

The client retrieves the 26 sibling hashes for the depth-26 PIR tree in two
sequential PIR queries plus the plaintext download, then appends 3
deterministic empty-subtree siblings to obtain the depth-29 authentication
path. Total bandwidth is approximately 3.5 MB on
the first query, or approximately 3.3 MB once the Tier 0 plaintext is cached
(dominated by the Tier 2 upload).


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
impractical. As of block height 3,268,870 with 49,813,784 nullifiers, it's already 1.48 GiB (assuming binary serialization). As Zcash scales, this grows unboundedly.

The existing solution in the design of token holder voting prior to this ZIP is
to not allow snapshots of balances, but instead "snapshots of balances that
moved in a registration period". This lowers the download size to just grow in
the number of transactions during registration period. It comes at the cost of
voting friction (requiring users to move funds), safety, and anonymity as you're
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

All queries have identical size for a given database configuration. However,
each unspent note requires exactly one pair of PIR queries (Tier 1 + Tier 2),
so an observer who can count a client's queries learns the exact number of
unspent notes that client's wallet held at the snapshot height. The following
approaches to mitigating this metadata leakage are out of scope for this
document:
- Padding the query count (e.g. to a fixed number or the next power of two)
  to hide the true number of unspent notes.
- IP obfuscation or mixing network round-trips across multiple servers to
  prevent an observer from attributing queries to a single client.


# Requirements


- No client-side preprocessing. A mobile wallet must be able to issue
  its first query without any prior download beyond the query itself
  or any client state carried over from a previous session.
- Single untrusted server with no per-client state. The server holds only
  the public database and processes queries statelessly. A client could
  query multiple independent servers without requiring coordination
  between them.
- Total bandwidth per query (upload plus download) under
  10MB, suitable for mobile networks.
- Two sequential network round-trips per query are acceptable.
- The hash function used in the exclusion tree must be efficient inside
  zero-knowledge proof circuits.
- 128-bit computational security with correctness error probability at
  most $2^{-40}$. A client can detect and recover from a correctness
  error by re-issuing the query.


# Non-requirements

The following are explicitly out of scope:

- Incremental database updates. The PIR database is computed once from
  the nullifier set at a given snapshot height and is treated
  as static for the duration of the Protocol Epoch.
- Sub-second end-to-end query latency. The two sequential PIR round-trips
  impose a latency floor determined by network conditions.
- Retrieval of data other than nullifier exclusion proofs.
- YPIR transport-level wire format between client and server.
- Noise analysis. Refer to YPIR paper for noise and security analysis. We directly use the suggested values with no amendments [^YPIR].
- The outer transport and wire-level encoding of queries and responses is out of scope for this ZIP.


# High-level summary

This subsection is non-normative.


<Rest of content providing context for understanding the Specification.>

The nullifier exclusion tree is split into three tiers:

- Tier 0 contains the top levels of the tree and is downloaded in plaintext by all clients.
- Tier 1 contains depth-11 to depth-18 subtrees and is served as a PIR database.
- Tier 2 contains depth-18 to depth-26 subtrees and is served as a PIR database.

## PIR Construction

Each proof retrieval consists of one plaintext download plus two
sequential PIR queries:

1. The client obtains Tier 0 and uses the target nullifier to identify
   the Tier 1 subtree index.
2. The client issues a PIR query for the corresponding Tier 1 row.
3. From the Tier 1 row, the client derives the Tier 2 row index and
   issues a second PIR query.
4. From Tier 0 and the recovered Tier 1 and Tier 2 rows, the client
   reconstructs the depth-26 authentication path used for nullifier
   non-membership.
5. The client appends the 3 deterministic empty-subtree siblings needed
   by the depth-29 Claim circuit.

For each PIR tier, the client hides the selected row with Regev
encryption, the server evaluates the corresponding SimplePIR-style
matrix-vector product, and YPIR+SP packs the resulting response into
RLWE ciphertexts so that the client does not need a precomputed
database hint.

# Specification

## PIR Operations

`Server_Setup`

: Server-side initialization: fix the deployed parameter set
  ([Parameters]); construct the tier databases and row serializations
  ([Instantiations]); expand the fixed public seeds and derived
  public/query-independent material ([Public Seeds]); encode each
  serialized PIR row into plaintext words
  ([Canonical Plaintext Packing]); and optionally perform
  query-independent preprocessing ([Precomputation]).

`Client_Query`

: Client-side query construction: sample fresh query material
  ([Client Key Generation]); construct the row-selector encryption
  ([Regev Encryption]); form the deployed transmitted query object
  ([Client Query Generation]); and send that query using an
  implementation-defined transport encoding.

`Server_Answer`

: Server-side response computation: reconstruct omitted
  public/query-independent query material from the fixed public seeds
  ([Public Seeds]); evaluate the query over the active PIR database tier
  ([Server Computation]); and return the resulting abstract server
  response object using an implementation-defined transport encoding.

`Client_Recover`

: Client-side response processing: decode the server response by
  packing-level RLWE decryption ([Packing-level RLWE Decryption]) and
  row recovery ([Client Recovery of the Selected Row]).

The protocol proceeds in the order:
1. `Server_Setup`
2. `Client_Query`
3. `Server_Answer`
4. `Client_Recover`.

A `Server_Setup` instantiation is tied to one fixed database state.
`Client_Query`, `Server_Answer`, and `Client_Recover` MAY be invoked
repeatedly against that instantiation. After any database update, the
server MUST create a new `Server_Setup` instantiation before answering
queries for the updated state.

## Parameters

Implementations MUST use the following parameters for the YPIR+SP
instantiation specified by this ZIP:

| Parameter | Value |
|---|---|
| Selector LWE dimension $n$ | 2048 |
| Ring degree $d$ | 2048 |
| Ciphertext modulus $q$ | $q_{2,1} \cdot q_{2,2}$ |
| Packing/plaintext modulus $p$ | $2^{14}$ |
| Noise width $\sigma$ | $6.4\sqrt{2\pi}$ |
| Gadget length $L_\mathsf{ks}$ | 3 |

The ciphertext modulus is the product of two 28-bit
NTT-friendly primes:

$$q_{2,1} = 268\,369\,921 \qquad q_{2,2} = 249\,561\,089$$

Their product is

$$q = q_{2,1} \cdot q_{2,2} = 66\,974\,689\,739\,603\,969 \approx 2^{56}.$$

Throughout this ZIP, $q$ denotes both the selector-level and packing-level
ciphertext modulus. That is,

$$q = q_{2,1} \cdot q_{2,2}.$$

Both primes satisfy $q_{2,1} \equiv q_{2,2} \equiv 1 \pmod{2d}$ (with
$d = 2048$), the condition
required for the Number Theoretic Transform over the polynomial ring
$\mathbb{Z}_q[x]/(x^d + 1)$. Using a CRT (Chinese Remainder Theorem)
representation of the modulus enables all packing-level arithmetic to
remain within 64-bit machine words.

For transmission after packing, implementations MUST use split modulus
switching with target coefficient moduli
$q_\mathsf{mask} = 268\,369\,921$ and $q_\mathsf{payload} = 2^{20}$.

For packing-key generation and CDKS key-switching, implementations MUST
use gadget base
$B_\mathsf{ks} = 2^{19}$ and gadget length
$L_\mathsf{ks} = \lceil \log_{B_\mathsf{ks}}(q) \rceil = 3$.

Concretely, each automorphism-specific key-switch matrix therefore has
exactly $L_\mathsf{ks} = 3$ columns.

The scaling factor $\Delta = \lfloor q / p \rfloor$ maps plaintext
values into the ciphertext space:
$\Delta = \lfloor q / 2^{14} \rfloor = 4\,087\,810\,653\,052$.

For the nullifier-exclusion-tree instantiation in [Instantiations], the
PIR database values are the raw serialized tier rows:

| Tier | Serialized row length and PIR value size |
|---|---|
| Tier 1 | 12,224 bytes |
| Tier 2 | 24,512 bytes |

No explicit file-level or wire-level zero-padding bytes are appended to
these rows before they are loaded into the PIR database.

## Coefficient Representatives

Unless otherwise specified, every element of $\mathbb{Z}_q$
in this ZIP is serialized and decomposed using its canonical representative in
$\{0, \ldots, q-1\}$.

When this ZIP refers to sampling from $D_{\mathbb{Z},\sigma}$, the sampled values
are integers. After sampling, each coefficient is reduced modulo the relevant
ciphertext modulus to obtain an element of $\mathbb{Z}_q$.

Centered representatives MUST NOT be used for serialization, public-seed
expansion, or gadget decomposition unless explicitly stated.

For [PackingKeyGeneration], [Split Modulus Switching], and all transport-facing
objects, coefficients MUST be interpreted via canonical representatives.

## Regev Encryption

Row selection is represented in LWE form over $\mathbb{Z}_q$, with selector dimension $n = 2048$, ciphertext modulus
$q = q_{2,1} \cdot q_{2,2}$, plaintext modulus $p = 2^{14}$, and scaling factor
$\Delta = \lfloor q / p \rfloor$.

Let $m$ be the number of database rows and let
$\mu_i \in \mathbb{Z}_p^m$ denote the row-selector vector for row index $i$,
where $\mu_i[j] = 1$ exactly when $j = i$ and $\mu_i[j] = 0$ otherwise.

Let $A \in \mathbb{Z}_q^{n \times m}$ be the implicit public matrix derived from
$\mathsf{seed\_A}$ as specified in
[Expansion of $\mathsf{seed\_A}$ (Row-Selector Public Randomness)] and
[Negacyclic Extraction of the Deployed Selector Matrix].

The deployed selector path does not sample an independent LWE secret vector.
Instead, for each query the client samples one fresh ring secret
$s^\star \in R_q = \mathbb{Z}_q[X]/(X^d + 1)$ as specified in
[Client Key Generation], with $d = n = 2048$. The selector LWE secret
vector $\mathbf{s} \in \mathbb{Z}_q^n$ is derived from $s^\star$ as
specified in [Client Key Generation].

For each query, the client MUST also sample a fresh noise vector
$e \leftarrow D_{\mathbb{Z},\sigma}^{m}$ and reduce each entry modulo $q$.
Let $d^{-1}$ denote the
multiplicative inverse of the ring degree $d$ modulo $q$. The client MUST
form the deployed selector as

$$
c = A^T \cdot \mathbf{s} + d^{-1} \cdot e + \Delta \cdot d^{-1} \cdot \mu_i.
$$

This scales both the sampled noise and the unique nonzero selector entry
by $d^{-1}$ before ring-based encryption and extraction.

When the deployed ring-generated selector path is viewed in LWE form, the same
fresh secret $\mathbf{s}$ is paired with the public matrix induced by the seeded ring blocks under the negacyclic extraction convention.

## YPIR+SP

YPIR+SP [^YPIR] eliminates the hint by packing the SimplePIR response
into RLWE ciphertexts using the CDKS transformation [^CDKS].

RLWE ciphertexts encrypt $d$ values in a single ciphertext (as
coefficients of a polynomial in $\mathbb{Z}[x]/(x^d + 1)$ ), compared to
one value per LWE ciphertext. This yields dramatically less ciphertext
overhead, making it possible to compress the entire SimplePIR row
response — which would otherwise require the hint for decryption — into
a small number of RLWE ciphertexts that the client can decrypt directly.

## Server Computation

Given a query $Q = (c_\mathsf{online}, pk_\mathsf{condensed})$ and
the active PIR database tier, the server MUST compute the response
as follows. Let $m$ be the number of database rows, $W$ the number
of 14-bit plaintext-word columns (from [Canonical Plaintext Packing]),
and let $d = 2048$.

The server operates on the row-serialized and plaintext-packed database prepared during `Server_Setup`; any equivalent use of precomputed query-independent artifacts is permitted only as specified in [Precomputation].

1. **Selector hint.** Let
   $A \in \mathbb{Z}_q^{n \times m}$ be the implicit public matrix
   from [Negacyclic Extraction of the Deployed Selector Matrix].
   Compute

   $$
   H = A \cdot \mathsf{DB} \in \mathbb{Z}_q^{n \times W},
   $$

   where $\mathsf{DB} \in \mathbb{Z}_q^{m \times W}$ is the packed
   plaintext database from [Canonical Plaintext Packing].
   Column $k$ of $H$ is the $\mathbf{a}$-component of the
   corresponding SimplePIR-level ciphertext.

2. **Database scan.** Compute the query-dependent scalar components

   $$
   b'_k = \sum_{j=0}^{m-1}
     \mathsf{DB}[j][k] \cdot c_\mathsf{online}[j]
   \pmod{q}
   $$

   for each plaintext-word column $k \in \{0, \ldots, W-1\}$.
   For indices $k \geq W$ (padding positions in the final chunk),
   define $b'_k = 0$ and $\mathbf{h}_k = \mathbf{0} \in \mathbb{Z}_q^n$.

3. **Reconstruct packing key.** Recover the full packing key $pk$
   from $pk_\mathsf{condensed}$ and $\mathsf{seed\_pack}$ using the
   convention in [Packing-Level Ciphertext Convention].

4. **Pack.** For each packing chunk $j$, form the $d$ SimplePIR-level
   ciphertexts
   $t_{j,z} = (\mathbf{h}_{jd+z},\; d \cdot b'_{jd+z} \bmod q)$
   for $z \in \{0, \ldots, d-1\}$, where $\mathbf{h}_k$ is column $k$
   of $H$. The factor of $d$ restores the $d^{-1}$ pre-scaling
   applied in [Client Query Generation]. Compute

   $$
   \widehat{C}_j =
   \mathsf{ApplyCDKSTransformation}((t_{j,0}, \ldots, t_{j,d-1}), pk)
   $$

   as defined in [CDKS Transformation].

5. **Modulus switching.** Apply [Split Modulus Switching] to each
   $\widehat{C}_j$.

The resulting sequence of modulus-switched packed RLWE ciphertexts
is the server response $R$.

### Canonical Plaintext Packing

For YPIR plaintext packing, implementations MUST map each serialized
`L_value`-byte row into 14-bit plaintext words by interpreting the row as
a contiguous little-endian bitstream:

- Bit 0 is the least-significant bit of byte 0.
- Within each byte, bits are ordered from least significant to most
  significant.
- Word index $k$ is formed from bits $14k$ through $14k + 13$, with bit
  $14k$ becoming the least-significant bit of that 14-bit word.

For a row of `L_value` bytes, let
$W_\mathsf{value} = \lceil 8L_\mathsf{value} / 14 \rceil$. If the final
14-bit word is only partially filled by row bits, the missing high bits
of that word MUST be zero. If additional all-zero words are needed to
complete the final packing chunk of length $d = 2048$, those words are
internal YPIR padding and are not part of the serialized tier-row format
defined by this ZIP.

### Precomputation

$H$ and the row-0 components of the CDKS packing tree depend only
on $\mathsf{seed\_A}$ and the database; they do not depend on the
client's query or packing key. An implementation MAY precompute
these query-independent artifacts before any query arrives and
reuse them across queries to the same database, provided that:

- every retained artifact is a deterministic function of the
  database and the fixed public seeds only;
- the artifacts are recomputed when the database changes;
- the resulting packed ciphertexts are identical to those produced
  by evaluating $\mathsf{ApplyCDKSTransformation}$ directly.

In particular, the gadget-decomposition digit polynomials
$f^{(u)}_\ell$ computed in step 2 of each $\mathsf{AutoKS}_\ell$
call ([CDKS Transformation]) depend only on row 0, so they may be
stored and reused with different packing keys.

### CDKS Transformation

Let $d = 2048$ and let $L = \log_2(d) = 11$.

For one packing chunk, let

$$
T = (t_0, \ldots, t_{d-1})
$$

be the ordered sequence of $d$ SimplePIR-level ciphertexts to be packed,
where each

$$
t_j = (\mathbf{a}_j, b_j) \in \mathbb{Z}_q^d \times \mathbb{Z}_q
$$

decrypts under the selector secret
$\mathbf{s} = (s^\star_0, \ldots, s^\star_{d-1})$ from
[Client Key Generation].

Define the lifted packing-level RLWE ciphertext

$$
\overline{t}_j = (\overline{a}_j(X), \overline{b}_j(X)) \in R_q^2
$$

by:

$$
\overline{b}_j(X) = b_j
$$

and

$$
\overline{a}_j(X) = -\widetilde{a}_j(X),
$$

where, writing
$\mathbf{a}_j = (a_{j,0}, \ldots, a_{j,d-1})$,

$$
\widetilde{a}_j(X) =
a_{j,0}
- a_{j,d-1}X
- a_{j,d-2}X^2
- \cdots
- a_{j,1}X^{d-1}.
$$

This is the negacyclic lifting: the
message carried by $t_j$ becomes the coefficient-0 plaintext of
$\overline{t}_j$, and the remaining coefficients contain only the induced
RLWE noise terms.

For each level $\ell \in \{1, \ldots, L\}$, define:

$$
Y_\ell = X^{d / 2^\ell} \in R_q,
\qquad
t_\ell = 2^\ell + 1.
$$

Level $\ell$ uses the key-switch matrix at packing-key index
$r = L - \ell$ in $pk = \mathsf{GeneratePackingKey}(s^\star)$
(since $k_{L-\ell} = d/2^{L-\ell} + 1 = 2^\ell + 1 = t_\ell$). Write

$$K_\ell = K_{L-\ell} = (K_{L-\ell,\,0},\; K_{L-\ell,\,1},\; K_{L-\ell,\,2}).$$

For any packing-level RLWE ciphertext
$C = (a(X), b(X)) \in R_q^2$, define

$$\mathsf{AutoKS}_\ell(C)$$

as follows:

1. Apply the ring automorphism to both rows:
   $(a', b') = (\tau_{t_\ell}(a),\; \tau_{t_\ell}(b))$.
2. Gadget-decompose $a'$ (row 0 of the automorphed ciphertext):

   $$
   a' = \sum_{u=0}^{L_\mathsf{ks}-1} B_\mathsf{ks}^u \cdot f^{(u)}
   $$

   with digit polynomials $f^{(u)}$ as defined in
   [PackingKeyGeneration].
3. For each gadget digit $u \in \{0, \ldots, L_\mathsf{ks}-1\}$,
   multiply the key-switch ciphertext $K_{L-\ell,\,u}$ by $f^{(u)}$
   (scalar-polynomial ring multiplication applied to both rows of
   $K_{L-\ell,\,u}$).
4. Sum the products:

   $$
   S = \sum_{u=0}^{L_\mathsf{ks}-1} K_{L-\ell,\,u} \cdot f^{(u)}
   \;\in R_q^2.
   $$

5. Form the output ciphertext:

   $$
   \mathsf{AutoKS}_\ell(C) = (0,\; b') + S.
   $$

   Concretely, row 0 of the output is row 0 of $S$, and row 1 is
   $b' +{}$ row 1 of $S$.

Under the convention in [Packing-Level Ciphertext Convention], the
output decrypts under $s^\star$ to $\tau_{t_\ell}(m)$ (plus noise),
where $m$ is the plaintext of $C$.

Define the recursive packing function
$\mathsf{CDKS}_\ell(C_0, \ldots, C_{2^\ell-1})$ on lifted ciphertexts by:

1. Base case:

   $$
   \mathsf{CDKS}_0(C_0) = C_0.
   $$

2. Recursive case for $\ell \geq 1$:
   - Let

     $$
     C^\mathsf{even} =
     \mathsf{CDKS}_{\ell-1}(C_0, \ldots, C_{2^{\ell-1}-1})
     $$

     and

     $$
     C^\mathsf{odd} =
     \mathsf{CDKS}_{\ell-1}(C_{2^{\ell-1}}, \ldots, C_{2^\ell-1}).
     $$

   - Form the two branch combinations

     $$
     C^\mathsf{sum}_\ell = C^\mathsf{even} + Y_\ell \cdot C^\mathsf{odd},
     $$

     $$
     C^\mathsf{diff}_\ell = C^\mathsf{even} - Y_\ell \cdot C^\mathsf{odd}.
     $$

   - Output

     $$
     \mathsf{CDKS}_\ell(C_0, \ldots, C_{2^\ell-1})
     =
     C^\mathsf{sum}_\ell + \mathsf{AutoKS}_\ell(C^\mathsf{diff}_\ell).
     $$

Define the chunk-level function
$\mathsf{ApplyCDKSTransformation}(T, pk)$ as follows:

1. Lift each SimplePIR-level ciphertext $t_j$ in
   $T = (t_0, \ldots, t_{d-1})$ to $\overline{t}_j$ by the negacyclic
   lifting rule above.
2. Compute

   $$
   \widehat{C} =
   \mathsf{CDKS}_L(\overline{t}_0, \ldots, \overline{t}_{d-1}).
   $$

3. Return $\widehat{C}$.

The packed ciphertext for the chunk is therefore

$$
\widehat{C} = \mathsf{ApplyCDKSTransformation}(T, pk).
$$

For $d = 2048$, the transform runs for exactly 11 levels. Slot $\ell$
of $\widehat{C}$ MUST correspond to input position $\ell$ in the
ordered chunk $(t_0, \ldots, t_{d-1})$.

Note,

- the $d$-scaling of each $b'_k$ in [Server Computation] step 4
  restores the $d^{-1}$ pre-scaling from [Client Query Generation],
  so that the effective packed/decrypted selector semantics are
  $A^T \mathbf{s} + e + \Delta \mu_i$ (see
  [Why A Is Negacyclic But the Database Is Not]);
- the canonical packing-key index order remains
  $\tau_{2049}, \tau_{1025}, \tau_{513}, \tau_{257}, \tau_{129},
  \tau_{65}, \tau_{33}, \tau_{17}, \tau_{9}, \tau_{5}, \tau_{3}$ as
  specified in [PackingKeyGeneration]; level $\ell$ uses the matrix at
  index $r = L - \ell$ as derived in [CDKS Transformation];
- when the seeded condensed representation is used, the server
  reconstructs the omitted public rows of the packing key from
  $\mathsf{seed\_pack}$ as specified in [Public Seeds].

### Packing

Let $T = (t_0, \ldots, t_{W_\mathsf{value}-1})$ be the ordered sequence of
SimplePIR-level LWE ciphertexts corresponding to the selected PIR value,
where $L_\mathsf{value}$ is the PIR value size in bytes fixed for the
queried tier in [Parameters] and $W_\mathsf{value}$ is determined from
$L_\mathsf{value}$ by [Canonical Plaintext Packing], before any
additional all-zero word padding used only to complete the final
ciphertext chunk. The server MUST pack $T$ so that the resulting
packing-level ciphertexts decrypt, under the client's fresh
packing-level secret, to the same ordered plaintext words.

Define the function
$\mathsf{PackSimplePIRResponse}(T, pk, L_\mathsf{value})$ as follows:

1. Let $d = 2048$ be the packing-level ring degree from [Parameters] and
   let $m = \lceil W_\mathsf{value} / d \rceil$.
2. Partition $T$ into $m$ consecutive chunks of length $d$:
   $(t_{j,0}, \ldots, t_{j,d-1})$ for $j \in \{0, \ldots, m-1\}$. If the
   final chunk is shorter than $d$, pad it with SimplePIR-level
   encryptions of zero so that it has exactly $d$ inputs.
3. For each chunk $j$, compute

   $$
   \widehat{C}_j =
   \mathsf{ApplyCDKSTransformation}((t_{j,0}, \ldots, t_{j,d-1}), pk)
   $$

   to produce one packing-level RLWE ciphertext
   $\widehat{C}_j = (\widehat{a}_j, \widehat{b}_j) \in R_q^2$.
4. Return the ordered packed sequence
   $\widehat{R} = (\widehat{C}_0, \ldots, \widehat{C}_{m-1})$.

The order of slots within each $\widehat{C}_j$ MUST match the order of
the 14-bit plaintext words obtained from the canonical byte-to-word
mapping in [Canonical Plaintext Packing]. Slot $\ell$ of $\widehat{C}_j$ MUST correspond
to word index $jd + \ell$ of that packed representation. Any additional
slots introduced only to complete the final ciphertext chunk MUST decode
to zero.

### Split Modulus Switching

The packed sequence $\widehat{R}$ is represented over the packing-level
modulus $q$. Before transport, the server MUST apply split modulus
switching to $\widehat{R}$ as specified in this section.

Define the function
$\mathsf{SplitModulusSwitchRLWECiphertext}((a, b))$ for a packing-level
RLWE ciphertext $(a, b) \in R_q^2$ as follows:

1. Let $q_\mathsf{mask} = 268\,369\,921$ and
   $q_\mathsf{payload} = 2^{20}$ as specified in [Parameters].
2. For each coefficient $a_k$ of $a$, let
   $a'_k = \lfloor (q_\mathsf{mask} / q) \cdot a_k \rceil \bmod q_\mathsf{mask}$,
   where $\lfloor \cdot \rceil$ denotes rounding to the nearest integer.
3. For each coefficient $b_k$ of $b$, let
   $b'_k = \lfloor (q_\mathsf{payload} / q) \cdot b_k \rceil \bmod q_\mathsf{payload}$.
4. Return the modulus-switched ciphertext
   $C' = (a', b') \in R_{q_\mathsf{mask}} \times R_{q_\mathsf{payload}}$.

Define the function
$\mathsf{SplitModulusSwitchRLWEResponse}(\widehat{R})$ by applying
$\mathsf{SplitModulusSwitchRLWECiphertext}$ coefficient-wise to each
packed ciphertext in $\widehat{R}$ and returning the resulting ordered
sequence $R = (C'_0, \ldots, C'_{m-1})$.

This ordered sequence

$$R = (C'_0, \ldots, C'_{m-1})$$

is the abstract server response object specified by this ZIP. Any conforming
transport or API framing MUST preserve the order of the ciphertexts and
the distinction between the two components of each
$C'_j = (a'_j, b'_j)$.

For client-side decoding, define the function
$\mathsf{LiftModulusSwitchedRLWECiphertext}((a', b'))$ as follows:

1. For each coefficient $a'_k$ of $a'$, let
   $\widetilde{a}_k = \lfloor (q / q_\mathsf{mask}) \cdot a'_k \rceil \bmod q$.
2. For each coefficient $b'_k$ of $b'$, let
   $\widetilde{b}_k = \lfloor (q / q_\mathsf{payload}) \cdot b'_k \rceil \bmod q$.
3. Return the lifted ciphertext
   $\widetilde{C} = (\widetilde{a}, \widetilde{b}) \in R_q^2$.

### Packing-level RLWE Decryption

Define the function
$\mathsf{DecryptPackingRLWECiphertext}((a, b), s^\star)$ for a packing-level
RLWE ciphertext $(a, b) \in R_q^2$ as follows, where $(a, b)$
are ordered as in [Packing-Level Ciphertext Convention]:

1. Compute $u = b + a \cdot s^\star \in R_q$.
2. Let $\Delta_2 = \lfloor q / p_2 \rfloor$, where $p_2 = 2^{14}$ is
   the packing-level plaintext modulus from [Parameters].
3. For each coefficient of $u$, round to the nearest multiple of
   $\Delta_2$ and divide by $\Delta_2$ to recover the corresponding
   plaintext slot in $\mathbb{Z}_{p_2}$.
4. Return the resulting plaintext slot vector
   $(v_0, \ldots, v_{d-1})$ in $\mathbb{Z}_{p_2}^d$.

## Client Work

### Client Key Generation

For each query, the client MUST sample one fresh packing/query secret

$$
s^\star(X) = \sum_{j=0}^{d-1} s^\star_j X^j \in R_q,
$$

where $d = 2048$, each coefficient $s^\star_j$ is sampled independently from
$D_{\mathbb{Z},\sigma}$, and each sampled coefficient is then reduced modulo
$q$.

This same fresh $s^\star$ is used in two roles:

1. as the packing-level RLWE secret for [PackingKeyGeneration] and
   [Packing-level RLWE Decryption], and
2. as the source of the selector LWE secret used in [Regev Encryption].

The selector LWE secret is defined coefficient-wise from the same polynomial:

$$
\mathbf{s} = (s^\star_0, \ldots, s^\star_{d-1}) \in \mathbb{Z}_q^n,
\qquad n = d = 2048.
$$

That is, the selector LWE secret is exactly the coefficient vector of the fresh
RLWE secret polynomial, in increasing coefficient order from $X^0$ through
$X^{d-1}$.

The client MUST sample a fresh $s^\star$ for every PIR query. Reuse of $s^\star$
across queries is not allowed.

### PackingKeyGeneration

Define the function $\mathsf{GeneratePackingKey}(s^\star)$ as follows, where
$s^\star \in R_q$ is the fresh client secret sampled in
[Client Key Generation].

For any odd integer $k \in \{1, 3, \ldots, 2d - 1\}$, define the
packing-level ring automorphism
$\tau_k : R_q \rightarrow R_q$ by

$$\tau_k(f(X)) = f(X^k) \bmod (X^d + 1).$$

The canonical CDKS automorphism order for this ZIP is

$$k_r = d / 2^r + 1 \qquad \text{for } r \in \{0, \ldots, 10\}.$$

Equivalently, the 11 automorphisms are
$\tau_{2049}, \tau_{1025}, \tau_{513}, \tau_{257}, \tau_{129},
\tau_{65}, \tau_{33}, \tau_{17}, \tau_{9}, \tau_{5}, \tau_{3}$, in
that order. The packing key MUST contain exactly one key-switch matrix
for each of those automorphisms, indexed by increasing matrix index
$r$.

For any polynomial $f = \sum_{j=0}^{d-1} f_j X^j \in R_q$, define
its base-$B_\mathsf{ks}$ gadget decomposition

$$f = \sum_{u=0}^{L_\mathsf{ks}-1} B_\mathsf{ks}^u \cdot f^{(u)}$$

where each coefficient of each digit polynomial $f^{(u)}$ is the unique
integer in $\{0, \ldots, B_\mathsf{ks} - 1\}$ obtained from the
canonical base-$B_\mathsf{ks}$ expansion of the corresponding
coefficient of $f$ in $\{0, \ldots, q - 1\}$.

The digit index $u$ runs over the $L_\mathsf{ks} = 3$ gadget digits.

The function $\mathsf{GeneratePackingKey}(s^\star)$ proceeds as follows:

1. Construct 33 seeded public ring elements
   $\rho_{r,u} \in R_q$ for
   $r \in \{0, \ldots, 10\}$ and
   $u \in \{0, 1, 2\}$ by expanding $\mathsf{seed\_pack}$ as specified
   in [Expansion of $\mathsf{seed\_pack}$ (Packing Public Randomness)].
2. For each matrix index $r$ and gadget digit $u$, sample a noise
   polynomial $e_{r,u} \leftarrow D_{\mathbb{Z},\sigma}^d$, with
   $\sigma$ as specified in [Parameters], and form one packing-level
   RLWE ciphertext $K_{r,u}$ under secret $s^\star$ whose plaintext is

   $$B_\mathsf{ks}^u \cdot \tau_{k_r}(s^\star),$$

   using the convention in [Packing-Level Ciphertext Convention].

   The seeded element $\rho_{r,u}$ determines the public row of
   $K_{r,u}$: row 0 is $-\rho_{r,u}$. Let $\beta_{r,u}$
   denote the second row (row 1) of $K_{r,u}$.

3. For each $r \in \{0, \ldots, 10\}$, define the key-switch matrix for
   automorphism $\tau_{k_r}$ as

   $$K_r = (K_{r,0}, K_{r,1}, K_{r,2}).$$
4. Let

   $$pk = (K_0, \ldots, K_{10}).$$

5. Return $pk$.

The complete packing key therefore contains exactly 11 matrices and
exactly 33 RLWE ciphertexts.

Concrete byte encoding of the packing key is out of scope for this ZIP.

For the seeded representation deployed by this ZIP, the client transmits
only the condensed packing-key component
$pk_\mathsf{condensed} = (\beta_{0,0}, \beta_{0,1}, \beta_{0,2}, \ldots, \beta_{10,2})$,
that is, the second rows (row 1 per
[Packing-Level Ciphertext Convention]) of the 33 RLWE ciphertexts in
row-major $(r,u)$ order. The corresponding public rows (row 0) are not
transmitted; the server reconstructs them from $\mathsf{seed\_pack}$ as
specified in [Public Seeds].

In the reference implementation, the transmitted condensed packing-key
component occupies
$11 \cdot 3 \cdot 2048 \cdot 8 = 540{,}672$ bytes.

### Client Query Generation

For each PIR query, the client MUST construct fresh query material for
the selected row index $i$ as follows:

1. Sample a fresh $s^\star$ as specified in [Client Key Generation].
2. Construct the row-selector vector $\mu_i$ as specified in [Regev
   Encryption].
3. Generate the deployed row selector
   $c = A^T \cdot \mathbf{s} + d^{-1} \cdot e + \Delta \cdot d^{-1} \cdot \mu_i$
   as specified in [Regev Encryption], where $d^{-1}$ is taken modulo $q$.
4. Generate the packing key
   $pk = \mathsf{GeneratePackingKey}(s^\star)$ as specified in
   [PackingKeyGeneration].
5. Form the abstract query material

   $$
   (c, pk).
   $$

6. For the deployed seeded representation specified by this ZIP, the
   client MUST transmit only the query-dependent selector component
   $c_\mathsf{online}$ and the condensed packing-key component
   $pk_\mathsf{condensed}$.

Here:

- $c_\mathsf{online} = c \in \mathbb{Z}_q^m$ is the deployed selector
  defined in [Regev Encryption]. Each entry $c_\mathsf{online}[j]$
  is the scalar ($b$-value) component of the $j$-th LWE-form selector
  ciphertext; the corresponding $\mathbf{a}$-vector components are
  reconstructed by the server from $\mathsf{seed\_A}$.
- $pk_\mathsf{condensed}$ contains only the second rows (row 1 per
  [Packing-Level Ciphertext Convention]) of the 33 packing-key RLWE
  ciphertexts in $pk$, in row-major $(r, u)$ order.

The corresponding public/query-independent components of the selector
and packing key MUST NOT be transmitted. They are reconstructed by the
server from the fixed public seeds $\mathsf{seed\_A}$ and
$\mathsf{seed\_pack}$ as specified in [Public Seeds].

7. Form the deployed transmitted query object

   $$
   Q = (c_\mathsf{online}, pk_\mathsf{condensed}).
   $$

The client MUST generate fresh query material separately for each PIR
query. Reuse of $s^\star$ or of query material derived from it is not
allowed.

Using the fixed public seeds together with the transmitted query object
$Q$, the server obtains enough information to evaluate the selected row
query while preserving the privacy of the row index. In particular,
$c_\mathsf{online}$ carries the query-dependent selector information,
while $pk_\mathsf{condensed}$ enables response packing under the client's
fresh $s^\star$ once the omitted public rows are reconstructed.

Any conforming transport or API framing MUST preserve the order of the
components of $Q$ and the ordering of the automorphism and gadget-digit
indices within $pk_\mathsf{condensed}$.

### Client Recovery of the Selected Row

Let `L_value` be the PIR value size fixed for the selected database tier
in [Parameters], and let `L_row` be the row serialization length defined
by this ZIP for that tier (12,224 bytes for Tier 1 and 24,512 bytes for
Tier 2). For this ZIP, `L_value = L_row` for both tiers: Tier 1 uses
12,224 bytes and Tier 2 uses 24,512 bytes, as specified in [Parameters].
Let $W_\mathsf{value}$ be the
number of plaintext words produced by the canonical byte-to-word mapping
defined in [Canonical Plaintext Packing], before any all-zero word
padding used only to complete the final ciphertext chunk.

Given the server's response to a PIR query, the client MUST recover the
selected tier row of length $L_\mathsf{row}$ for the queried tier. It
only requires that the response decode, under the client's fresh
packing-level secret and the YPIR+SP semantics described above, to the
exact serialized row bytes defined for the selected tier.

Define the function
$\mathsf{DecodeYPIRSPResponse}(R, L_\mathsf{value}, L_\mathsf{row})$ as
follows:

1. Compute
   $\widetilde{C}_j = \mathsf{LiftModulusSwitchedRLWECiphertext}(C'_j)$
   for each $C'_j$.
2. Compute
   $\mathsf{DecryptPackingRLWECiphertext}(\widetilde{C}_j, s^\star) = (v_{j,0}, \ldots, v_{j,d-1})$
   for each $\widetilde{C}_j$, obtaining slot values in $\mathbb{Z}_{p_2}$.
3. Form the concatenated slot sequence
   $V = v_{0,0} \| \ldots \| v_{0,d-1} \| v_{1,0} \| \ldots \| v_{m-1,d-1}$.
4. Let $W = V[0..W_\mathsf{value}-1]$.
5. Reconstruct a byte string $B$ by writing the least-significant 14 bits
   of each word in $W$ in order as a contiguous bitstream, regrouping
   that bitstream into 8-bit bytes using the inverse of the canonical
   byte-to-word mapping in [Canonical Plaintext Packing].
6. Verify that any unused high bits of the final 14-bit word are zero.
   If the final ciphertext chunk contained additional all-zero padding
   words beyond $W_\mathsf{value}$, verify that those omitted words also
   decrypt to zero.
7. Return the first $L_\mathsf{row}$ decoded bytes as the returned row
   of the selected PIR database.

## Common Conventions and Public Material

### Security

The security of YPIR+SP is best viewed as relying primarily on the RLWE assumption for the ring-based query-generation and response-packing machinery, together with a circular-security assumption for the automorphism/key-switching material used in packing.

The RLWE assumption is standard in lattice-based
cryptography. Circular security is a well-studied additional assumption shared with Spiral and OnionPIR [^YPIR].

### Packing-Level Ciphertext Convention

A packing-level RLWE ciphertext under secret $s^\star \in R_q$
is a pair $(c_0, c_1) \in R_q^2$ stored as a two-row polynomial
matrix:

- Row 0 (public row): $c_0 = -\rho$, the negation of the public
  random ring element.
- Row 1 (second row): $c_1 = \rho \cdot s^\star + e + m$, where $e$
  is a noise polynomial and $m$ is the plaintext polynomial.

Decryption recovers $m + e$ as $c_1 + c_0 \cdot s^\star$.

When this ZIP writes a packing-level RLWE ciphertext as $(a, b)$,
$a$ denotes row 0 and $b$ denotes row 1. The decryption identity is
therefore $b + a \cdot s^\star$.

Throughout this ZIP, "public row" means row 0 and "second row" means
row 1 under this convention. When [PackingKeyGeneration] refers to
the seeded public element $\rho_{r,u}$ determining the public row of
$K_{r,u}$, the stored row 0 is $-\rho_{r,u}$. The second row
$\beta_{r,u}$ transmitted in $pk_\mathsf{condensed}$ is row 1 of
$K_{r,u}$.

### Public Seeds

This ZIP binds exactly two fixed public seeds for the deployed YPIR+SP
path:

- $\mathsf{seed\_A} = \mathtt{0x00}^{32}$ for the active row-selector
  public-randomness path.
- $\mathsf{seed\_pack} = \mathtt{0x02} \,\|\, \mathtt{0x00}^{31}$ for
  packing public randomness.

These public seeds are query-independent and MUST NOT be confused with
the client's fresh private per-query secret $s^\star$ from
[Client Key Generation]. This ZIP does not define additional public-seed
domains for unused paths outside the deployed YPIR+SP construction.

#### ChaCha20 RNG Initialization

For each public seed in this section, implementations MUST initialize a
ChaCha20 RNG instance directly from the 32-byte seed, with no stream
override and no additional nonce-based domain separation.

More precisely, this ZIP uses the standard 20-round ChaCha stream cipher
[^ChaCha20]. For a seed
$\mathsf{seed} = (\mathsf{seed}[0], \ldots, \mathsf{seed}[31])$, the
initial 16-word ChaCha state is:

$$
(\mathtt{0x61707865}, \mathtt{0x3320646e}, \mathtt{0x79622d32},
\mathtt{0x6b206574}, k_0, \ldots, k_7, 0, 0, 0, 0),
$$

where $(k_0, \ldots, k_7)$ are the eight 32-bit little-endian words of
the 32-byte seed, in order.

For each seed expansion, this RNG instance is initialized exactly once
and then consumed continuously from byte position 0 onward. It MUST NOT
be reinitialized between successive public ring elements derived from
the same seed. Whenever this ZIP refers to reading successive 64-bit RNG
outputs, it means:

1. Partition the keystream into consecutive 8-byte chunks
   $(K[0..7], K[8..15], K[16..23], \ldots)$.
2. Interpret each chunk as one 64-bit unsigned integer in little-endian
   order.
3. Consume those 64-bit integers in that order, with no skipping,
   rewinding, or rejection sampling.

#### Public-Ring-Element Expansion

For the packed RLWE layer, each seeded public ring element is sampled as
an element of

$$
R_q = \mathbb{Z}_q[X]/(X^d + 1)
$$

using canonical representatives in $\{0, \ldots, q-1\}$.

To sample one seeded public ring element
$a(X) = \sum_{j=0}^{d-1} a_j X^j \in R_q$ from a ChaCha20-based seeded
RNG, implementations MUST proceed as follows:

1. For coefficient indices $j = 0, \ldots, d-1$ in increasing order:
   - Read one 64-bit output word $w$ from the RNG.
   - Set
     $a_j = w \bmod q$,
     interpreted in $\{0, \ldots, q-1\}$.
2. Return the resulting polynomial $a(X)$.

No rejection sampling is used.

Implementations MUST NOT instead sample public ring elements by drawing
separate residues independently modulo $q_{2,1}$ and $q_{2,2}$ and then
CRT-composing them.

#### Expansion of $\mathsf{seed\_A}$ (Row-Selector Public Randomness)

$\mathsf{seed\_A}$ defines the public randomness used by the deployed
row-selector query. No alternate stream selection or nonce-derived
domain separation is applied.

Implementations MUST expand $\mathsf{seed\_A}$ as follows:

1. Initialize the ChaCha20-based seeded RNG from $\mathsf{seed\_A}$ as
   specified in [ChaCha20 RNG Initialization].
2. Let $d = 2048$ be the ring dimension from [Parameters].
3. Let the selector consist of consecutive ring blocks indexed in
   increasing order.
4. For each block index, sample one public ring element in
   $R_q = \mathbb{Z}_q[X]/(X^d + 1)$ by the procedure in
   [Public-Ring-Element Expansion].
5. Use these sampled ring elements, in order, as the public
   query-independent randomness of the deployed selector-generation
   procedure.

These seeded ring elements are converted into the implicit selector
public matrix $A$ by the procedure defined in
[Negacyclic Extraction of the Deployed Selector Matrix].

#### Negacyclic Extraction of the Deployed Selector Matrix

This subsection defines the implicit public matrix
$A \in \mathbb{Z}_q^{n \times m}$ used in [Regev Encryption], as derived
from the seeded ring elements expanded from $\mathsf{seed\_A}$.

Let $d = n = 2048$, let
$R_q = \mathbb{Z}_q[X]/(X^d + 1)$, and let

$$
a(X) = \sum_{j=0}^{d-1} a_j X^j \in R_q
$$

be one seeded ring element expanded from $\mathsf{seed\_A}$.

Define the negacyclic matrix
$\mathsf{NCyc}(a) \in \mathbb{Z}_q^{d \times d}$ by requiring that, for
every
$\mathbf{x} = (x_0, \ldots, x_{d-1}) \in \mathbb{Z}_q^d$ with
$x(X) = \sum_{j=0}^{d-1} x_j X^j$,

$$
\mathsf{NCyc}(a)\,\mathbf{x}
$$

is the coefficient vector, in increasing order from $X^0$ through
$X^{d-1}$, of

$$
a(X)\cdot x(X) \bmod (X^d + 1).
$$

Equivalently, for each
$c \in \{0, \ldots, d-1\}$, column $c$ of $\mathsf{NCyc}(a)$ is the
coefficient vector of

$$
a(X)\cdot X^c \bmod (X^d + 1).
$$

Let $m$ be the number of database rows for the queried PIR tier, and let

$$
B = \left\lceil \frac{m}{d} \right\rceil.
$$

Implementations MUST expand exactly $B$ seeded ring elements from
$\mathsf{seed\_A}$ in the order specified in
[Expansion of $\mathsf{seed\_A}$ (Row-Selector Public Randomness)].
Let these elements be
$a^{(0)}(X), \ldots, a^{(B-1)}(X)$.

For each block index $b \in \{0, \ldots, B-1\}$, define

$$
A^{(b)} = \mathsf{NCyc}(a^{(b)}).
$$

The implicit public matrix $A$ is the horizontal concatenation

$$
A = \left[ A^{(0)} \mid A^{(1)} \mid \cdots \mid A^{(B-1)} \right],
$$

with the final block truncated on the right if necessary so that $A$
has exactly $m$ columns.

Equivalently, for
$j \in \{0, \ldots, m-1\}$, let
$b = \lfloor j/d \rfloor$ and $c = j \bmod d$.
Then column $j$ of $A$ is column $c$ of $\mathsf{NCyc}(a^{(b)})$.

#### Expansion of $\mathsf{seed\_pack}$ (Packing Public Randomness)

The packing public randomness consists of 33 public ring elements
$a_{r,u} \in R_q$, indexed by:

- $r \in \{0, \ldots, 10\}$,
- $u \in \{0, 1, 2\}$.

The iteration order is row-major in $(r,u)$, with $r$ outermost.

Implementations MUST expand $\mathsf{seed\_pack}$ as follows:

1. Initialize the ChaCha20-based seeded RNG from $\mathsf{seed\_pack}$
   as specified in [ChaCha20 RNG Initialization].
2. For each index pair $(r,u)$ in row-major order:
   - Sample one ring element
     $a_{r,u} \in R_q = \mathbb{Z}_q[X]/(X^d + 1)$
     by the procedure in [Public-Ring-Element Expansion], with
     $d = 2048$.

These 33 seeded ring elements are the public-random part of the packing
public parameters. The client transmits only the complementary
second rows (row 1); the corresponding public rows (row 0) are
reconstructed by the server from $\mathsf{seed\_pack}$ using the
convention in [Packing-Level Ciphertext Convention].

## Instantiations

### Nullifier Exclusion Tree

The server MUST construct the exclusion tree and the corresponding PIR
databases (Tiers 0, 1, and 2) once from the nullifier set at the start
of each Protocol Epoch. The databases are static for the duration of
the epoch.

For each nullifier snapshot, the server MUST establish a distinct
`Server_Setup` instantiation from the tier databases and associated
public/query-independent material derived from that snapshot. A
`Server_Setup` instantiation for one nullifier snapshot MUST NOT be used
to answer queries against a different snapshot.

#### Tree Structure

The exclusion tree is a sorted binary Merkle tree with depth 26, holding
up to $N = 2^{26} \approx 67$ million leaves. The tree MUST use the
same Poseidon-based non-membership tree specified in
[^draft-valargroup-orchard-balance-proof]. In particular,
implementations MUST use the same field, Poseidon instantiation, and
hash definitions as that ZIP:

- Internal node hash:
  $\mathsf{Poseidon}(\mathsf{left}, \mathsf{right})$ over
  $\mathbb{F}_{q_\mathbb{P}}$.
- Leaf hash:
  $\mathsf{Poseidon}(\mathsf{low}, \mathsf{width})$ over
  $\mathbb{F}_{q_\mathbb{P}}$.

Poseidon is used because it is efficient inside zero-knowledge proof
circuits.

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
with leaf hash $\mathsf{Poseidon}(0, 0)$, consistent with the empty-leaf
definition in [^draft-valargroup-orchard-balance-proof].

Real exclusion-range leaves MUST occupy the leftmost (lowest-index) leaf
positions, sorted in ascending order by $\mathsf{low}$. The remaining
rightmost positions MUST be filled with canonical empty leaves.

For Tier 0 and Tier 1 subtree metadata, define `min_key` as follows:

Let $\mathsf{max\_key} \in \mathbb{F}_{q_\mathbb{P}}$ denote the field
element whose canonical integer representation is $q_\mathbb{P} - 1$;
equivalently, $\mathsf{max\_key} = -1 \bmod q_\mathbb{P}$.

- If the subtree contains at least one real exclusion-range leaf,
  `min_key` is the `low` value of that subtree's leftmost real leaf.
- If the subtree consists entirely of empty leaves, implementations MUST
  encode $\mathsf{min\_key} = \mathsf{max\_key}$.

Clients use predecessor search over these `min_key` values: for target
nullifier $t$, they select the largest index $S$ such that
$\mathsf{min\_key}[S] \leq t$. Because
all empty-only subtrees form a suffix and are encoded with
$\mathsf{min\_key} = \mathsf{max\_key}$, this search is performed with respect to
the canonical integer ordering on $\mathbb{F}_{q_\mathbb{P}}$. After the
Tier 2 descent, the client MUST still verify that the decoded
`(low, width)` interval contains the target key, and reject otherwise.

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

#### Authentication Path

The PIR tiers provide 26 sibling hashes, one per tree depth from the
leaf (depth 26) to the root of the depth-26 PIR tree (depth 0). To form
the authentication path consumed by the Claim circuit, the client MUST
append 3 additional sibling hashes corresponding to the canonical empty
subtrees above that depth-26 root, yielding a complete depth-29
authentication path. See [Tree Depth vs. Circuit Depth]. After decrypting the PIR responses for Tiers 1 and
2 and appending those 3 deterministic siblings, the client MUST
reconstruct the depth-29 Merkle root and verify it against the published
depth-29 root of the exclusion tree.

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

1. Binary search the 2,048 `min_key` values in Block A to find the
   largest subtree index $S_1 \in \lbrack 0, 2047\rbrack$ such that
   $\mathsf{min\_key}\lbrack S_1\rbrack \leq \mathsf{target\_key}$,
   where any empty-only suffix subtree is encoded with
   $\mathsf{min\_key} = \mathsf{max\_key}$ as described in [Tree Construction].
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

The PIR value size for this tier is given in [Parameters]. Rows are
loaded into the PIR database exactly as serialized below.

| Metric | Value |
|---|---|
| Database size | 2,048 rows $\times$ 12,224 B = **23.9 MB** |

**Row serialization (12,224 bytes):**

Internal nodes MUST be serialized in breadth-first order (depth 1
left-to-right, then depth 2, and so on through depth 6):

```
Bytes 0–4,031:      internal_nodes[0..125]        126 × 32 B = 4,032 B
Bytes 4,032–12,223: leaf_records[0..127]          128 × 64 B = 8,192 B
                    where each record is:
                    bytes 0–31:   hash
                    bytes 32–63:  min_key
                                                     Total:      12,224 B
```

**BFS indexing:** A node at relative depth $d$, horizontal position $p$
(0-indexed) has internal node index $(2^d - 2) + p$ for
$d \in \lbrack 1, 6\rbrack$, $p \in \lbrack 0, 2^d)$. The sibling of position $p$ at any
depth is at position $p \oplus 1$. The parent of position $p$ is at
position $p \gg 1$ at depth $d - 1$.

Leaf record $i \in \lbrack 0, 127\rbrack$ begins at byte offset
$4032 + 64i$. Within that record, the `hash` field occupies bytes
$4032 + 64i \ldots 4063 + 64i$ and the `min_key` field occupies bytes
$4064 + 64i \ldots 4095 + 64i$.

**Client procedure:**

1. Issue a PIR query for row $S_1$ (the subtree index from Tier 0).
2. Binary search the 128 `min_key` fields in the interleaved leaf
   records to
   find the largest sub-subtree index $S_2 \in \lbrack 0, 127\rbrack$
   such that
   $\mathsf{leaf\_records}[S_2].\mathsf{min\_key} \leq \mathsf{target\_key}$.
   Any empty-only suffix subtree in this array is encoded with
   $\mathsf{min\_key} = \mathsf{max\_key}$.
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

Each leaf contains a 32-byte `low` value and a 32-byte `width` value as
specified in [Leaf Encoding]. No separate hash field is stored; the leaf
hash is computed as $\mathsf{Hash}(\mathsf{low} \| \mathsf{width})$.

256 leaves $\times$ 64 bytes = **16,384 bytes**.

**Row total: 24,512 bytes (23.9 KB).**

The PIR value size for this tier is given in [Parameters]. Rows are
loaded into the PIR database exactly as serialized below.

| Metric | Value |
|---|---|
| Database size | 262,144 rows $\times$ 24,512 B = **5.98 GB** |

**Row serialization (24,512 bytes):**

```
Bytes 0–8,127:       internal_nodes[0..253]        254 × 32 B = 8,128 B
Bytes 8,128–24,511:  leaf_records[0..255]          256 × 64 B = 16,384 B
                     where each record is:
                     bytes 0–31:   low
                     bytes 32–63:  width
                                                       Total:      24,512 B
```

Leaf record $i \in \lbrack 0, 255\rbrack$ begins at byte offset
$8128 + 64i$. Within that record, the `low` field occupies bytes
$8128 + 64i \ldots 8159 + 64i$ and the `width` field occupies bytes
$8160 + 64i \ldots 8191 + 64i$.

**Client procedure:**

1. Compute the Tier 2 row index as $S_1 \times 128 + S_2$.
2. Issue a PIR query for this row.
3. Binary search only the populated prefix of the 256 interleaved leaf
   records to find the largest index $\mathsf{target\_position}$ such
   that
   $\mathsf{leaf\_records}[\mathsf{target\_position}].\mathsf{low} \leq
   \mathsf{target\_key}$.
   Any trailing records corresponding to empty right-padding are not part
   of this search.
   Let $(low, width)$ be the leaf record at that position. The client
   MUST verify that $\mathsf{target\_key}$ is contained in the exclusion
   interval encoded by $(low, width)$ as specified in [Leaf Encoding];
   otherwise it MUST reject the row as invalid.
4. Read 8 sibling hashes from the row:
   - Depth-26 sibling: the leaf at index
     $(\mathsf{target\_position} \oplus 1)$. Let
     $(low_\mathsf{sib}, width_\mathsf{sib})$ be the leaf record at that
     position. Compute its hash as
     $\mathsf{Hash}(\mathsf{low}_\mathsf{sib} \| \mathsf{width}_\mathsf{sib})$.
     This is the only hash the client computes during the PIR retrieval
     phase.
   - Depths 19–25 siblings: read from the 254 internal nodes by walking
     upward from the target leaf position.

##### Bandwidth Summary

| Component | Upload | Download | Round trip |
|---|---|---|---|
| Tier 0 payload | — | 192 KB | 192 KB |
| PIR Query 1 (Tier 1, 24 MB) | 544 KB | ~48 KB | ~592 KB |
| PIR Query 2 (Tier 2, 6 GB) | 2.6 MB | ~84 KB | ~2.7 MB |
| **Total (first query)** | **3.2 MB** | **~324 KB** | **~3.5 MB** |
| **Total (Tier 0 cached)** | **3.2 MB** | **~132 KB** | **~3.3 MB** |

Upload is dominated by the Tier 2 query-dependent selector component
($\mathsf{packed\_query\_row}$, proportional to the number of database
rows) and the transmitted condensed packing-key component.

In our implementation, the packing key component occupies 540,672 bytes (528 KiB).

Downloads are small because RLWE packing compresses the row response
efficiently.

##### Client Computation Summary

| Step | Binary search | Hashes computed | Sibling hashes read |
|---|---|---|---|
| Tier 0 | Over 2,048 keys | 0 | 11 |
| Tier 1 | Over 128 keys | 0 | 7 |
| Tier 2 | Over 256 keys | 1 (sibling leaf hash) | 8 |
| **Total** | | **1** | **26** |

All internal node hashes are served directly by Tier 0, Tier 1, and Tier
2. The client computes exactly 1 hash during proof retrieval: the
sibling leaf hash in Tier 2.


# Rationale

## Parameter Selection

The parameters in [Parameters] follow the referenced YPIR implementation [^ypir-impl].

The binding constraint is the Tier 2 database (see
[Tier 2: Large PIR (Depths 18–26)]). With a depth-26 exclusion tree
holding up to $2^{26} \approx 67$ million leaves, Tier 2 contains
$2^{18} = 262{,}144$ rows of 24,512 bytes each, totaling approximately
6 GB. This is well within the 64 GB ceiling. This leaves roughly an order of
magnitude of headroom before the parameters would need to be revised,
accommodating substantial growth of the Orchard nullifier set without
any change to the cryptographic configuration.

Even under the depth-29 tree supported by the Claim circuit
(see [Tree Depth vs. Circuit Depth]), an analogous three-tier layout
would produce at most $2^{21} \approx 2$ million Tier 2 rows. At the
current row size this yields approximately 48 GB, still within the
64 GB bound.

The YPIR authors provide a concrete security analysis for the parameter
family underlying these choices in [^YPIR], targeting at least 128-bit
computational security with correctness error at most $2^{-40}$. The
shared-modulus YPIR+SP constants above are taken from the referenced
implementation used by this ZIP.

## Rationale for representing $q$ as two primes

The packed RLWE layer uses a ciphertext modulus represented as the
product of two 28-bit NTT-friendly primes rather than as a single large
prime. This CRT representation gives the implementation enough modulus
headroom for the packing and key-switching steps while still allowing
the polynomial arithmetic to be carried out efficiently in 64-bit
machine words. In other words, the construction needs a modulus of
roughly 56 bits overall, but realizes it as two smaller compatible
factors so that the NTT-based implementation remains practical.

## Construction Choice

SimplePIR is the baseline design that requires a client-download hint.
Next-generation designs such as YPIR and InsPIRe aim to eliminate that
step and reduce communication.

### Why SimplePIR Is Not Enough

In SimplePIR [^SimplePIR], the database is reshaped into a
$\sqrt{N} \times \sqrt{N}$ matrix $D$ where each cell holds one byte.
To retrieve row $i$, the client constructs a unit selection vector
$\mu$, encrypts it under Regev [^Regev05], and sends the ciphertext to
the server. The server then computes one matrix-vector product, so the
online work is dominated by memory bandwidth rather than computation.

The public random matrix $A$ (and its transpose $A^T$) is not
transmitted; both client and server expand it deterministically from a
shared seed using ChaCha20 [^ChaCha20] (see [Public Seeds] and
[Regev Encryption]). Regev encryption is linearly homomorphic, so the
server can evaluate the encrypted selector without learning which row
was chosen.

A critical property is that $A$ is independent of the message $\mu$.
This allows the server to precompute the product $D \cdot A^T$ once,
yielding the SimplePIR hint. After the server computes
$\mathsf{answer} = D \cdot c$, the client would subtract
$D \cdot A^T \cdot \mathbf{s}$ using that hint and then recover the
selected row by rounding. Because the hint depends on the full
database, it must be recomputed whenever the database changes, and its
size grows with $\sqrt{N}$.

On a database of $N$ bytes, the hint size is roughly $4\sqrt{N}$ KB
[^SimplePIR]:

| Database size | Hint size            |
|---------------|----------------------|
| 100 KB        | $\approx$ 1.25 MB   |
| 10 MB         | $\approx$ 12.6 MB   |
| 1 GB          | 128 MB               |

For the Tier 2 database in this document (6 GB, see
[Tier 2: Large PIR (Depths 18–26)]), the hint would exceed 300 MB. That
is far beyond what a cold-start mobile client can download before its
first query.

### Why YPIR+SP Fits This ZIP

YPIR+SP builds on SimplePIR and inherits its matrix layout and the
server's linear homomorphic evaluation of the client's row-selector
query over the database. Its key improvement is that it eliminates the
database-dependent hint by packing the intermediate LWE-form response
into a more compact RLWE form.

YPIR+SP uses one fresh 2048-coefficient secret polynomial per query:
$s^\star$, whose coefficient vector defines the deployed row-selector
LWE secret $\mathbf{s}$ and which is also used to derive the packing
material and decrypt the packed response.

The client does not separately decrypt the intermediate SimplePIR
response. Instead, the server uses `pk` to pack that response into RLWE
ciphertexts decryptable under `s^\star`, and the client recovers the
returned response via the packing-level RLWE decryption procedure. This
eliminates the `Client_Download` step while also compressing the query
responses, making the construction practical for this ZIP.

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

The YPIR+SP packing key contains exactly 11 automorphism-specific
key-switch matrices because the packing-level ring degree is
$d = 2048 = 2^{11}$. CDKS packing follows a radix-2 butterfly recursion,
so it requires one automorphism for each halving level of that
recursion. Therefore the number of required automorphisms is
$\log_2(d) = 11$. This is a structural property of the CDKS packing
procedure for this ring size, not an arbitrary parameter choice.

InsPIRe achieves superior communication metrics through a novel packing
mechanism (InspiRING, requiring only 2 key-switching matrices instead of
11) and homomorphic polynomial evaluation. However, its underlying
cryptography is complex, has no known production usage, and is one year
younger than YPIR+SP, complicating auditability and imposing production
risk for a system that must be trustworthy from launch.

### Rationale for YPIR+SP over standard YPIR

For the Tier 2 PIR database (24,512-byte PIR values carrying 24,512-byte
serialized rows; see
[Data Structure Layout]), standard YPIR would require 24,512 parallel
DoublePIR instances (one per byte), each with its own 16 MB hint — a
prohibitive cost. YPIR+SP avoids this: the full row is packed into RLWE
ciphertexts in a single pass, achieving ~2.6 MB total communication for
the 6 GB Tier 2 database (see [Bandwidth Summary]). See
[Construction Choice] for a comparison with other PIR schemes.

We choose YPIR+SP because it achieves a hintless design with appropriate
communication and throughput for mobile clients, built on the
well-understood CDKS transformation.

It is our intent to continue researching and productionizing InsPIRe
concurrently. Should InsPIRe mature and undergo sufficient auditing, a
future ZIP may specify it as a replacement or alternative.

## Split Modulus Switching

Packing and split modulus switching solve different problems.

The CDKS packing step reduces the number of ciphertexts in the server's
response by combining many SimplePIR-level LWE ciphertexts into a small
number of packing-level RLWE ciphertexts. However, those packed RLWE
ciphertexts are still represented over the full packing modulus $q$.
Packing therefore compresses the response structurally, but it does not
yet make each packed ciphertext cheap to transmit.

Split modulus switching is the second compression step. It reduces the
coefficient representation of each packed RLWE ciphertext before the
server sends it to the client. In other words, packing changes "many
ciphertexts into few ciphertexts", while split modulus switching changes
"wide ciphertexts into narrower ciphertexts". This reduction in wire
size is what enables the small download sizes summarized in [Bandwidth
Summary].

A packing-level RLWE ciphertext has the form $(a, b)$, where $a$ is the
mask polynomial (stored as $-\rho$) and $b$ is the payload polynomial.
During decryption the client computes $u = b + a \cdot s$
(see [Packing-Level Ciphertext Convention]), so $a$ contributes through
multiplication by the secret key, while $b$ more directly carries the
encoded plaintext.

We use different target moduli for the two ciphertext components because
they contribute differently during decryption. The mask polynomial is
multiplied by the secret key and can therefore be compressed more
aggressively. The payload polynomial carries the encoded plaintext more
directly, so it requires slightly more precision in order to preserve
correct decoding after decryption and rounding.

This asymmetric compression follows the YPIR design: it reduces response
size substantially without sacrificing the correctness margin needed for
recovering the packed PIR value.

## Why A Is Negacyclic But the Database Is Not

In the deployed selector path, the query uses ring structure, but the
server still evaluates it as an implicit LWE selector. The earlier
negacyclic extraction rule defines exactly which implicit public matrix
$A$ corresponds to the seeded ring elements, so the ring-based query can
be viewed coefficient-wise, before packing restoration, as the deployed
selector
$A^T \mathbf{s} + d^{-1} e + \Delta d^{-1} \mu_i$.

On the packing-enabled path, the server's packing procedure later restores
that factor by multiplying the packed $b$ contribution by $d$ modulo
$q$, yielding the effective selector semantics
$A^T \mathbf{s} + e + \Delta \mu_i$ at the packed/decrypted level.

Accordingly, the deployed query is not generated from an unstructured LWE
matrix directly. Instead, the client encrypts a polynomial selector using
ring structure, and the server's first pass still consumes the resulting
LWE-form selector and produces the same kind of per-row LWE outputs that
SimplePIR expects. YPIR+SP then packs those outputs into RLWE
ciphertexts.

This design gives the implementation the main benefit of ring structure
without moving the full database representation into the ring. Keeping the
public randomness for $A$ in negacyclic form enables NTT-friendly
preprocessing and compact seeded expansion. Keeping the database in the
ordinary SimplePIR matrix layout preserves the high-throughput online
matrix-vector scan, avoiding the memory overhead and throughput loss that
would result from representing the full database in the ring [^YPIR].

In short, deriving $A$ from seeded ring elements enables compact public
randomness and NTT-accelerated preprocessing, while keeping the database
in the ordinary matrix domain preserves the fast SimplePIR-style online
evaluation path. The RLWE packing step is then applied only to the
resulting LWE-form outputs.

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
24,512-byte PIR values). Alternative splits such as 10 + 8 + 8 (violates the
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
This ZIP fixes per-tier PIR value sizes equal to the serialized row
lengths: 12,224 bytes for Tier 1 and 24,512 bytes for Tier 2. Any
additional zero-fill required to map those byte strings into the
underlying YPIR plaintext representation is internal to the YPIR
implementation and does not change the serialized tier-row format.

## Tree Depth vs. Circuit Depth

The PIR data structure uses a tree of depth 26, which is sufficient for
the current Orchard nullifier set (~51 million nullifiers, well within
the $2^{26} \approx 67$ million leaf capacity). The Claim circuit
defined in [^draft-valargroup-orchard-balance-proof], however, fixes
the non-membership Merkle path depth at 29, supporting up to
$2^{29} \approx 537$ million leaves.

These depths intentionally differ. The PIR server's tiered data
structure materializes only the depth-26 tree, because that is sufficient
for the current nullifier set and keeps Tier 2 within the desired size
bound. The server also publishes a depth-29 root obtained by extending
the depth-26 root upward with 3 completely empty sibling subtrees. Those
top 3 siblings are deterministic: each is the root hash of a completely
empty subtree, computable from the canonical empty leaf hash. The client
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

## Rationale for (low, width) encoding

The original formulation in "Air drops, Proof-of-Balance, and Stake-weighted Polling" [^draft-str4d-orchard-balance-proof] uses $(start, end)$ pairs. Verifying
$start \leq t \leq end$ requires two comparisons inside the ZKP circuit.

The $(low, width)$ encoding reduces this to one subtraction ($t - low$)
and one unsigned comparison ($< width$), saving one comparison gate in the
circuit. Since the exclusion range check is performed for every balance
proof, this saving applies to every protocol participant.

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
three-tier Poseidon tree, the Tier 1 / Tier 2 query orchestration described in this ZIP — is provided in [^nullifier-pir-impl].



# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^XPIR]: [XPIR: Private Information Retrieval for Everyone](https://hal.science/hal-01396142)

[^SimplePIR]: [One Server for the Price of Two: Simple and Fast Single-Server Private Information Retrieval](https://eprint.iacr.org/2022/949)

[^YPIR]: [YPIR: High-Throughput Single-Server PIR with Silent Preprocessing](https://eprint.iacr.org/2024/270)

[^InsPIRe]: [InsPIRe: Communication-Efficient PIR with Server-side Preprocessing](https://eprint.iacr.org/2025/1352)

[^CDKS]: [Efficient Homomorphic Conversion Between Ring LWE Ciphertexts](https://eprint.iacr.org/2020/015)

[^Regev05]: [On Lattices, Learning with Errors, Random Linear Codes, and Cryptography](https://doi.org/10.1145/1568318.1568324)

[^ChaCha20]: [ChaCha20 and Poly1305 for IETF Protocols (RFC 8439)](https://www.rfc-editor.org/rfc/rfc8439)

[^Poseidon]: [Poseidon: A New Hash Function for Zero-Knowledge Proof Systems](https://eprint.iacr.org/2019/458)

[^nullifier-pir-impl]: [Nullifier PIR reference implementation](https://github.com/valargroup/vote-nullifier-pir)

[^ypir-impl]: [YPIR reference implementation (artifact branch)](https://github.com/menonsamir/ypir/tree/artifact)

[^protocol-pallasandvesta]: [Zcash Protocol Specification, Section 5.4.9.6: Pallas and Vesta](protocol/protocol.pdf#pallasandvesta)

[^draft-str4d-orchard-balance-proof]: [Air drops, Proof-of-Balance, and Stake-weighted Polling](draft-str4d-orchard-balance-proof)

[^draft-valargroup-orchard-balance-proof]: [Orchard Proof-of-Balance](draft-valargroup-orchard-balance-proof)

[^draft-voting-protocol]: [Draft ZIP: Zcash Shielded Voting Protocol](draft-valargroup-voting-protocol.md)
