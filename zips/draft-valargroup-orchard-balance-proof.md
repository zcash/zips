    ZIP: Unassigned
    Title: Orchard Proof-of-Balance
    Owners: Dev Ojha <dojha@berkeley.edu>
            Adam Tucker <adamleetucker@outlook.com>
            Roman Akhtariev <ackhtariev@gmail.com>
            Greg Nagy <greg@dhamma.works>
    Credits: Daira-Emma Hopwood
             Jack Grigg
    Status: Draft
    Category: Informational
    Created: 2026-03-03
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms below are to be interpreted as follows:

Pool snapshot

: A pair $(\mathsf{rt^{cm}}, \mathsf{rt^{excl}})$ consisting of the
  Orchard note commitment tree root and the nullifier non-membership tree
  root, both computed as of the end of a specified block height. The pool
  snapshot defines the set of notes eligible for claims.

Nullifier non-membership tree

: An Indexed Merkle Tree (IMT) whose leaves represent contiguous intervals
  between consecutive revealed nullifiers. A Merkle path to a leaf, together
  with a range check, proves that a given nullifier does not appear in the
  set of revealed nullifiers at the snapshot height. See [Nullifier
  Non-Membership Tree].

Alternate nullifier

: A value derived from an Orchard note and a nullifier domain, with similar
  cryptographic properties to the note's standard nullifier but unlinkable
  to it. A note has exactly one alternate nullifier for each nullifier
  domain. See [Alternate Nullifier Derivation].

Nullifier domain

: A unique identifier, encoded as an element of $\mathbb{F}_ {q_ {\mathbb{P}}}$,
  that scopes alternate nullifiers to a particular application instance. Two
  claims in the same domain for the same note produce the same alternate
  nullifier; claims in different domains are unlinkable.

Claim

: A zero-knowledge proof, together with a spend authorization signature,
  demonstrating that the prover holds an unspent Orchard note with a
  committed value at a given pool snapshot, and revealing the note's
  alternate nullifier in a specified domain.

Dummy signed note

: A synthetic Orchard note with value 0 (in the Claim circuit) that
  does not exist in any on-chain note commitment tree. It is constructed
  solely for obtaining a spend authorization signature from the holder's
  key. See [Wallet Signing].


# Abstract

This ZIP specifies a mechanism for proving ownership of unspent Orchard
notes at a snapshot of the shielded pool, without revealing the notes'
standard nullifiers or linking claims to past or future on-chain spending.

The mechanism introduces two primitives: a *nullifier non-membership tree*
(an Indexed Merkle Tree of intervals between consecutive revealed
nullifiers) that enables efficient in-circuit proofs that a note was
unspent at the snapshot height, and *alternate nullifiers* (domain-separated
values derived from a note's standard nullifier using Poseidon) that
prevent double-claiming within an application domain while remaining
unlinkable across domains and to on-chain activity.

A Claim circuit combines these primitives with standard Orchard note
commitment integrity, Merkle membership, spend authority, and diversified
address integrity checks to produce a single proof per
note. An optional multi-note batching extension allows proving aggregate
balance across several notes in one proof.

Possible applications include private air drops, private proof-of-balance,
and private stake-weighted polling. Application-specific protocols (such
as coinholder voting) are specified in separate ZIPs that reference this
one.


# Motivation

Several applications in the Zcash ecosystem require a holder to
demonstrate that they controlled a certain balance at a point in time,
without revealing which specific notes they held or linking the
demonstration to their on-chain transaction history. Examples include:

- **Air drops**: distributing tokens proportional to shielded holdings.
- **Stake-weighted polling**: weighting votes by ZEC balance.
- **Proof-of-balance**: demonstrating solvency or collateral without
  revealing addresses.

The naive approach of revealing standard nullifiers would link the
claim to future spending, destroying the privacy that Zcash's shielded
transactions are designed to provide. An alternative approach of actually
spending the claimed notes (e.g., to oneself) with an anchor at the
snapshot height has the disadvantage that the same notes cannot be used
in concurrent applications, and it permanently commits the holder to the
claim by recording it on the main chain.

Domain-separated alternate nullifiers resolve both problems: they are
unlinkable to the standard nullifiers (even after the note is later spent
on-chain), and they are scoped to a specific application instance so that
the same notes can participate in independent, concurrent applications
without interference.

The concept of alternate nullifiers and nullifier non-membership trees for
proof-of-balance was first described by Daira-Emma Hopwood and Jack Grigg
in a 2023 draft. [^draft-str4d-orchard-balance-proof] This ZIP builds on
that work with a concrete instantiation informed by the implementation
experience of the Zcash coinholder voting system.

A key practical consideration is that many holders custody their spending
keys on hardware wallets such as Keystone. Without a delegation mechanism,
hardware wallet users must either export their spending keys to software
(negating the security benefit of hardware custody) or perform many more
hardware wallet signing interactions (one per protocol action rather than
a single delegation) each with limited ability to verify the signing
context on screen. This ZIP therefore specifies a PCZT-based signing flow (see
[Wallet Signing]) that works with any hardware wallet supporting
Orchard PCZT signing today, requiring no firmware changes.


# Privacy Implications

**Unlinkability to standard nullifiers.** The alternate nullifier
$\mathsf{nf_ {dom}}$ for a note is computed as a Poseidon hash keyed by the
nullifier deriving key $\mathsf{nk}$, which is secret. An observer who
sees both $\mathsf{nf_ {dom}}$ (published during a claim) and the standard
nullifier $\mathsf{nf^{old}}$ (published when the note is later spent on
the Zcash chain) cannot link them without knowledge of $\mathsf{nk}$.
This property holds under the assumption that Poseidon is a pseudorandom
function when keyed with a uniformly random field element (see
[Security Argument]).

**Cross-domain unlinkability.** If the same note participates in two
independent applications with different nullifier domains $\mathsf{dom_ 1}$
and $\mathsf{dom_ 2}$, the resulting alternate nullifiers
$\mathsf{nf_ {dom_ 1}}$ and $\mathsf{nf_ {dom_ 2}}$ are unlinkable. This
follows from the PRF property: distinct inputs produce outputs that are
computationally indistinguishable from independent random values.

**Spend authority prevents viewing-key delegation.** The circuit requires
a valid spend authorization signature, ensuring that a party with only a
viewing key cannot make claims on behalf of the holder.

**Non-membership tree queries.** Obtaining a Merkle path in the nullifier
non-membership tree requires querying a data source that holds the full
tree. A naive query reveals which path is being requested, potentially
linking the querier to a nullifier range. Private information retrieval
(PIR) techniques can mitigate this leakage [^pir-nullifier-exclusion]; their
specification is out of scope for this document.

**Hardware wallet device exposure.** When the PCZT-based hardware wallet
signing flow (see [Wallet Signing]) is used, the device observes
the PCZT but learns no information about the holder's real
Orchard balance or delegation context. The PCZT contains a 1-zatoshi
dummy note with no on-chain counterpart; the holder's actual note
commitments, values, and nullifiers are never transmitted to the device.
The application commitment, alternate nullifiers, and usage identifier are
committed via the dummy note's nullifier inside the ZKP circuit and
do not appear as plaintext fields in the PCZT. The output address
(application hotkey) is visible on the device but is freshly generated
per usage instance and is not linked to the holder's on-chain Orchard
addresses. An attacker with physical access to the device during signing
learns only that the holder is participating in a proof-of-balance
instance and the declared balance.


# Requirements

- A holder can prove ownership of an unspent Orchard note at a pool
  snapshot without revealing the note's standard nullifier.
- Double-claiming the same note within the same nullifier domain is
  detectable.
- Claims are unlinkable to the holder's past or future on-chain spends,
  and to their claims in other nullifier domains.
- The holder proves spend authority (not merely viewing access).
- The construction allows a holder to participate in multiple independent
  applications using the same notes, provided each application uses a
  distinct nullifier domain.


# Non-requirements

- Privacy-preserving retrieval of non-membership Merkle paths (e.g., via
  PIR) is out of scope.
- Value denomination conversions (e.g., converting zatoshi to
  application-specific units) are out of scope.
- Transaction-level encoding of claims is out of scope; this ZIP specifies
  only the proof statement and its verification.


# Specification

## Pool Snapshot

A pool snapshot at block height $h$ is a pair
$(\mathsf{rt^{cm}}, \mathsf{rt^{excl}})$ where:

- $\mathsf{rt^{cm}}$ is the root of the Orchard note commitment tree
  as of the end of block $h$. [^protocol-orchardcommitmenttree]
- $\mathsf{rt^{excl}}$ is the root of the nullifier non-membership tree
  constructed from the set of all Orchard nullifiers revealed on the
  consensus chain as of the end of block $h$.

The pool snapshot MUST be deterministically computable from the consensus
chain state at height $h$. Any party with access to the chain state MUST
be able to independently verify both roots.


## Nullifier Non-Membership Tree

The nullifier non-membership tree is a Merkle tree whose leaves are
commitments to the gaps between consecutive revealed nullifiers, enabling
efficient in-circuit proofs that a given nullifier is absent from the
revealed set.

The relationship between the sorted nullifier set and the tree is
illustrated below:

```
            /  \                          ..
           /    \                        /
       gcm_0    gcm_1               gcm_2      <-- Gap commitments (tree leaves)
      /\            /\              /\
  |(l_0, w_0)| |(l_1, w_1)|   |(l_2, w_2) ..  <-- Gap encodings (low, width)
s_0|          |s_1|         |s_2|          ..   <-- Sorted nullifier set + sentinels
```

Each gap between consecutive nullifiers is encoded as a
$(\mathsf{low}, \mathsf{width})$ pair, then committed via
$\mathsf{GapCommit}$ (see [Hash Function]) to produce a tree leaf.

### Construction

Let $S = \{s_ 0, s_ 1, \ldots, s_ {m-1}\} \subset \mathbb{F}_ {q_ {\mathbb{P}}}$ be the union of the set of all Orchard
nullifiers revealed on the consensus chain as of block height $h$ and
the sentinel values defined in [Sentinel Initialization]. Sort $S$ in
ascending order.
Because sentinel initialization is mandatory, $S$ is non-empty.

For each pair of consecutive elements $(s_ i, s_ {i+1})$ where $s_ i < s_ {i+1}$
and $s_ {i+1} - s_ i > 1$, compute a gap encoding:

- $\mathsf{low} = s_ i + 1$: the first value in the gap
- $\mathsf{width} = s_ {i+1} - s_ i - 2$: the number of additional values
  in the gap beyond $\mathsf{low}$

The gap encoding represents the closed interval
$[\mathsf{low},\; \mathsf{low} + \mathsf{width}]$, which contains exactly
the field elements between $s_ i$ and $s_ {i+1}$ exclusive. The
corresponding tree leaf is $\mathsf{GapCommit}(\mathsf{low}, \mathsf{width})$.

After processing all consecutive pairs, if $s_ {m-1} < q_ {\mathbb{P}} - 1$,
a terminal gap MUST be added with:

- $\mathsf{low} = s_ {m-1} + 1$
- $\mathsf{width} = (q_ {\mathbb{P}} - 1) - \mathsf{low}$

This ensures that all unrevealed values above the largest element of $S$ are
represented in the tree.

<details>
<summary>

### Rationale for (low, width) encoding
</summary>

An alternative encoding stores $(\mathsf{start}, \mathsf{end})$ pairs
directly, as proposed in [^draft-str4d-orchard-balance-proof]. The
$(\mathsf{low}, \mathsf{width})$ encoding precomputes
$\mathsf{width} = \mathsf{end} - \mathsf{low}$ during tree construction,
saving one field subtraction in the in-circuit interval check. Since tree
construction is performed once per snapshot while the circuit is evaluated
per claim, this trade-off favors prover efficiency.
</details>

### Hash Function

The non-membership tree uses Poseidon [^protocol-poseidon] with the
$\mathsf{P128Pow5T3}$ instantiation (width $t = 3$, rate 2) over the
Pallas base field $\mathbb{F}_ {q_ {\mathbb{P}}}$ for all hashing:

- **Gap commitment:** $\mathsf{GapCommit}(\mathsf{low}, \mathsf{width})$,
  a 2-input Poseidon hash (one permutation).
- **Internal node hash:** $\mathsf{PoseidonNodeHash}(\mathsf{left}, \mathsf{right})$,
  a 2-input Poseidon hash (one permutation), where $\mathsf{left}$ and
  $\mathsf{right}$ are determined by the node's position bit at each level.

Both functions use $\mathsf{P128Pow5T3}$ with $\mathsf{ConstantLength}\langle 2 \rangle$.
This is the same Poseidon instantiation used by Orchard for nullifier
derivation [^protocol-poseidon].

<details>
<summary>

### Rationale for Poseidon over Sinsemilla
</summary>

The Orchard note commitment tree uses Sinsemilla [^protocol-sinsemilla]
for Merkle hashing. The non-membership tree uses Poseidon instead because
Poseidon operates natively on field elements, making it significantly more
efficient inside Halo 2 arithmetic circuits. Sinsemilla is optimized for
bitstring inputs and incurs overhead when hashing field elements. Since
the non-membership tree is a new data structure not constrained by backwards
compatibility, the more circuit-efficient choice is appropriate.

Poseidon2 was considered but not adopted because no audited implementation was
available at the time of design. Poseidon already has an audited implementation
used by Orchard for nullifier derivation.
</details>

### Tree Depth

$\mathsf{MerkleDepth^{excl}}$ MUST be large enough to accommodate the
number of gap leaves. Each nullifier in the pool adds at most one leaf
(by splitting an existing gap), so the tree requires capacity for at
least $|N| + 17$ leaves, where $|N|$ is the size of the Orchard
nullifier set and 17 is the number of sentinels for the Pallas base
field. Concretely:

$$\mathsf{MerkleDepth^{excl}} \geq \lceil \log_ 2(|N| + 17) \rceil$$

A depth of $\mathsf{MerkleDepth^{excl}} = 29$ is RECOMMENDED. This
supports up to $2^{29} \approx 537$ million leaves. As of early 2026,
the Zcash Orchard pool contains roughly 51 million nullifiers, so
depth 29 provides about one order of magnitude of headroom.

Unused leaf positions MUST be filled with the canonical empty leaf value
$\mathsf{GapCommit}(0, 0)$. This is non-overlapping with every valid
gap encoding because the sentinel set always includes $0$ (see
[Sentinel Initialization]), so $\mathsf{low} = 0$ can never appear in
a valid gap.

### Sentinel Initialization

Before inserting any real nullifiers, the non-membership tree MUST be
initialized with sentinel values that partition $\mathbb{F}_ {q_ {\mathbb{P}}}$
into intervals each of width strictly less than $2^{250}$. The sentinel
set MUST include the value $0$.

For the Pallas base field ($q_ {\mathbb{P}} \approx 2^{254}$),
implementations MUST insert 17 sentinels $s_k \in \mathbb{F}_ {q_ {\mathbb{P}}}$ at:

$$s_k = k \cdot 2^{250}, \quad k \in \{0,1,\ldots,16\}.$$

This guarantees the width bound required by the in-circuit range checks:

- For $k = 0,\ldots,15$, the interval between consecutive sentinels has
  width exactly $2^{250} - 2$.
- The final tail interval has width
  $q_ {\mathbb{P}} - 16 \cdot 2^{250} - 2 < 2^{250}$.

The width bound is critical for the soundness of the in-circuit range
checks. If any interval had width $\geq 2^{250}$, the range check could
overflow, allowing a prover to falsely claim non-membership.

These sentinel values are constants defined by this specification.


## Nullifier Domains

A nullifier domain $\mathsf{dom}$ is an element of
$\mathbb{F}_ {q_ {\mathbb{P}}}$ that defines a double-claim detection scope.
Each independent claim context (such as a specific air-drop event, a single
poll, or an individual voting round) MUST use its own domain.

Applications MUST ensure that the domain value is unique across
independent claim contexts. Two claims that share the same domain and the
same underlying note will produce the same alternate nullifier, which is
the mechanism for double-claim prevention.

Applications SHOULD derive the domain deterministically by hashing a
protocol identifier with an application-specific instance value. The
protocol identifier SHOULD be the application's ZIP number, encoded as
a little-endian Pallas base field element, which guarantees
cross-application uniqueness. The instance value (such as a round or
event identifier) ensures uniqueness across instances of the same
application.

Applications MAY define their own domain derivation scheme provided it
satisfies the uniqueness requirement above.


## Alternate Nullifier Derivation

Given a nullifier domain $\mathsf{dom}$ and an Orchard note with standard
nullifier $\mathsf{nf^{old}}$, the alternate nullifier $\mathsf{nf_ {dom}}$
is computed as:

$$\mathsf{nf_ {dom}} = \mathsf{DeriveAlternateNullifier_ {nk}}(\mathsf{dom}, \mathsf{nf^{old}}) = \mathsf{Poseidon}(\mathsf{nk}, \mathsf{dom}, \mathsf{nf^{old}})$$

where:

- $\mathsf{nk} \in \mathbb{F}_ {q_ {\mathbb{P}}}$ is the nullifier deriving
  key from the holder's full viewing key.
- $\mathsf{dom} \in \mathbb{F}_ {q_ {\mathbb{P}}}$ is the nullifier domain
  (see [Nullifier Domains]).
- $\mathsf{nf^{old}} \in \mathbb{F}_ {q_ {\mathbb{P}}}$ is the note's
  standard Orchard nullifier, computed as
  $\mathsf{DeriveNullifier_ {nk}}(\text{ρ}^{\mathsf{old}}, \text{ψ}^{\mathsf{old}}, \mathsf{cm^{old}})$.

This is a 3-input Poseidon hash. Using the standard $\mathsf{P128Pow5T3}$
instantiation (width $t = 3$, rate 2), this requires two permutations.

### Properties

**Deterministic.** The same note in the same domain always produces the
same alternate nullifier, enabling double-claim detection.

**Unlinkable to standard nullifier.** An adversary who observes
$\mathsf{nf_ {dom}}$ and later observes $\mathsf{nf^{old}}$ (when the note
is spent on-chain) cannot link them without knowledge of $\mathsf{nk}$.

**Cross-domain unlinkable.** Alternate nullifiers for the same note in
different domains are computationally indistinguishable from independent
random values.

**Collision resistant.** Distinct notes in the same domain produce
distinct alternate nullifiers, under the collision resistance of Poseidon.

### Security Argument

The security of the alternate nullifier derivation relies on Poseidon
being a pseudorandom function (PRF) when keyed with a uniformly random
element of $\mathbb{F}_ {q_ {\mathbb{P}}}$.

**Unlinkability.** Model $\mathsf{Poseidon}(\mathsf{nk}, \cdot, \cdot)$
as a PRF keyed by $\mathsf{nk}$. An adversary who does not know
$\mathsf{nk}$ sees outputs that are indistinguishable from random. Given
$\mathsf{nf_ {dom}} = \mathsf{Poseidon}(\mathsf{nk}, \mathsf{dom}, \mathsf{nf^{old}})$
and $\mathsf{nf^{old}}$, the adversary cannot verify the relationship
without $\mathsf{nk}$. The nullifier deriving key $\mathsf{nk}$ is a
255-bit value derived from the spending key and is never revealed on-chain.

**Cross-domain unlinkability.** For two domains $\mathsf{dom_ 1} \neq \mathsf{dom_ 2}$,
the tuples $(\mathsf{dom_ 1}, \mathsf{nf^{old}})$ and
$(\mathsf{dom_ 2}, \mathsf{nf^{old}})$ are distinct inputs to the PRF.
Under the PRF assumption, their outputs are jointly indistinguishable from
independent random values.

**Collision resistance.** If $\mathsf{nf^{old}_ 1} \neq \mathsf{nf^{old}_ 2}$,
then $(\mathsf{nk}, \mathsf{dom}, \mathsf{nf^{old}_ 1})$ and
$(\mathsf{nk}, \mathsf{dom}, \mathsf{nf^{old}_ 2})$ are distinct Poseidon
inputs, so their outputs collide with negligible probability under
Poseidon's collision resistance.

<details>
<summary>

### Rationale for divergence from the Orchard-native construction
</summary>

The earlier draft [^draft-str4d-orchard-balance-proof] proposed an
alternate nullifier derivation structurally parallel to the standard
Orchard nullifier:

$$\mathsf{Extract}_ {\mathbb{P}}\!\left(\!\left[(\mathsf{PRF^{nfAlternate}_ {nk}}(\text{ρ}^{\mathsf{old}}, \mathsf{dom}) + \text{ψ}^{\mathsf{old}}) \bmod q_ {\mathbb{P}}\right] \mathcal{K}^\mathsf{Orchard} + \mathsf{cm^{old}}\right)$$

That construction has the advantage of sharing more circuit infrastructure
with the standard nullifier check.

The Poseidon-based construction adopted here was chosen for simplicity:
it requires only a single Poseidon hash rather than an additional
fixed-base scalar multiplication, and it reuses the standard nullifier
$\mathsf{nf^{old}}$ that the circuit already computes for the
non-membership check. The security assumption is comparable, as both
constructions rely on the hardness of distinguishing $\mathsf{nk}$-keyed
evaluations from random.

The current Zcash coinholder voting system was designed and implemented
around this construction. A future revision of this ZIP may revisit the
choice as part of a broader protocol revision. For example, if hardware
wallet firmware support (e.g., a Keystone testnet byte for governance
signing) restructures the spend authority flow in a way that favors
tighter integration with the standard Orchard nullifier derivation.
</details>


## Claim Circuit

A valid instance of a Claim proof $\pi$ assures the following statement.

### Public Inputs

Given a primary input:

- $\mathsf{rt^{cm}} ⦂ \{ 0 .. q_ {\mathbb{P}}-1 \}$
- $\mathsf{rt^{excl}} ⦂ \{ 0 .. q_ {\mathbb{P}}-1 \}$
- $\mathsf{rk} ⦂ \mathsf{SpendAuthSig^{Orchard}.Public}$
- $\mathsf{cv} ⦂ \mathsf{ValueCommit^{Orchard}.Output}$
- $\mathsf{nf_ {dom}} ⦂ \{ 0 .. q_ {\mathbb{P}}-1 \}$
- $\mathsf{dom} ⦂ \{ 0 .. q_ {\mathbb{P}}-1 \}$

### Auxiliary Inputs

the prover knows an auxiliary input:

- $\mathsf{g_ d^{old}} ⦂ \mathbb{P}^*$
- $\mathsf{pk_ d^{old}} ⦂ \mathbb{P}^*$
- $\mathsf{v^{old}} ⦂ \{ 0 .. 2^{\ell_ {\mathsf{value}}}-1 \}$
- $\text{ρ}^{\mathsf{old}} ⦂ \mathbb{F}_ {q_ {\mathbb{P}}}$
- $\text{ψ}^{\mathsf{old}} ⦂ \mathbb{F}_ {q_ {\mathbb{P}}}$
- $\mathsf{rcm^{old}} ⦂ \{ 0 .. 2^{\ell^{\mathsf{Orchard}}_ {\mathsf{scalar}}}-1 \}$
- $\mathsf{cm^{old}} ⦂ \mathbb{P}$
- $\mathsf{nf^{old}} ⦂ \{ 0 .. q_ {\mathbb{P}}-1 \}$
- $\mathsf{path^{cm}} ⦂ \{ 0 .. q_ {\mathbb{P}}-1 \}^{[\mathsf{MerkleDepth^{Orchard}}]}$
- $\mathsf{pos^{cm}} ⦂ \{ 0 .. 2^{\mathsf{MerkleDepth^{Orchard}}}\!-1 \}$
- $\mathsf{ak}^{\mathbb{P}} ⦂ \mathbb{P}^*$
- $\mathsf{nk} ⦂ \mathbb{F}_ {q_ {\mathbb{P}}}$
- $\mathsf{rivk} ⦂ \mathsf{Commit^{ivk}.Trapdoor}$
- $\mathsf{rivk\_ {internal}} ⦂ \mathsf{Commit^{ivk}.Trapdoor}$
- $\alpha ⦂ \{ 0 .. 2^{\ell^{\mathsf{Orchard}}_ {\mathsf{scalar}}}-1 \}$
- $\mathsf{rcv} ⦂ \{ 0 .. 2^{\ell^{\mathsf{Orchard}}_ {\mathsf{scalar}}}-1 \}$
- $\mathsf{low} ⦂ \mathbb{F}_ {q_ {\mathbb{P}}}$
- $\mathsf{width} ⦂ \mathbb{F}_ {q_ {\mathbb{P}}}$
- $\mathsf{path^{excl}} ⦂ \{ 0 .. q_ {\mathbb{P}}-1 \}^{[\mathsf{MerkleDepth^{excl}}]}$
- $\mathsf{pos^{excl}} ⦂ \{ 0 .. 2^{\mathsf{MerkleDepth^{excl}}}\!-1 \}$

such that the following conditions hold:

### Conditions

**Note commitment integrity.** $\hspace{0.5em}$
$\mathsf{NoteCommit^{Orchard}_ {rcm^{old}}}(\mathsf{repr}_ {\mathbb{P}}(\mathsf{g_ d^{old}}), \mathsf{repr}_ {\mathbb{P}}(\mathsf{pk_ d^{old}}), \mathsf{v^{old}}, \text{ρ}^{\mathsf{old}}, \text{ψ}^{\mathsf{old}}) \in \{ \mathsf{cm^{old}}, \bot \}$.

This is identical to the corresponding check in an Orchard Action
statement. [^protocol-actionstatement]

**Merkle path validity for** $\mathsf{cm^{old}}$. $\hspace{0.5em}$
$(\mathsf{path^{cm}}, \mathsf{pos^{cm}})$ is a valid Merkle path of depth
$\mathsf{MerkleDepth^{Orchard}}$, as defined in
§ 4.9 'Merkle Path Validity' [^protocol-merklepath], from
$\mathsf{Extract}_ {\mathbb{P}}(\mathsf{cm^{old}})$ to the anchor $\mathsf{rt^{cm}}$.

**Value commitment integrity.** $\hspace{0.5em}$
$\mathsf{cv} = \mathsf{ValueCommit^{Orchard}_ {rcv}}(\mathsf{v^{old}})$.

**Nullifier derivation.** $\hspace{0.5em}$
$\mathsf{nf^{old}} = \mathsf{DeriveNullifier_ {nk}}(\text{ρ}^{\mathsf{old}}, \text{ψ}^{\mathsf{old}}, \mathsf{cm^{old}})$.

**Spend authority.** $\hspace{0.5em}$
$\mathsf{rk} = \mathsf{SpendAuthSig^{Orchard}.RandomizePublic}(\alpha, \mathsf{ak}^{\mathbb{P}})$.

**Diversified address integrity.** $\hspace{0.5em}$
Let
$\mathsf{ivk} = \mathsf{Commit^{ivk}_ {rivk}}(\mathsf{Extract}_ {\mathbb{P}}(\mathsf{ak}^{\mathbb{P}}), \mathsf{nk})$
and
$\mathsf{ivk\_ {internal}} = \mathsf{Commit^{ivk}_ {rivk\_ {internal}}}(\mathsf{Extract}_ {\mathbb{P}}(\mathsf{ak}^{\mathbb{P}}), \mathsf{nk})$.
Then $\mathsf{pk_ d^{old}} = [\mathsf{ivk}]\, \mathsf{g_ d^{old}}$ or
$\mathsf{pk_ d^{old}} = [\mathsf{ivk\_ {internal}}]\, \mathsf{g_ d^{old}}$.

**Nullifier non-membership.** $\hspace{0.5em}$
Let $\mathsf{leaf} = \mathsf{GapCommit}(\mathsf{low}, \mathsf{width})$
(see [Hash Function]).
$(\mathsf{path^{excl}}, \mathsf{pos^{excl}})$ is a valid Merkle path of
depth $\mathsf{MerkleDepth^{excl}}$ from $\mathsf{leaf}$ to the anchor
$\mathsf{rt^{excl}}$, using $\mathsf{PoseidonNodeHash}$ (see [Hash Function])
at each level.

Additionally, let $x = \mathsf{nf^{old}} - \mathsf{low} \bmod q_ {\mathbb{P}}$.
Both of the following range checks MUST hold:

1. $x < 2^{250}$
2. $2^{250} - 1 - \mathsf{width} + x < 2^{250}$

These together enforce $\mathsf{low} \leq \mathsf{nf^{old}} \leq \mathsf{low} + \mathsf{width}$
over $\mathbb{F}_ {q_ {\mathbb{P}}}$, proving that the standard nullifier
falls within an interval of unrevealed values.

<details>
<summary>

### Derivation of the interval check
</summary>

To prove $\mathsf{low} \leq \mathsf{nf^{old}} \leq \mathsf{low} + \mathsf{width}$:

- Check 1 proves $\mathsf{nf^{old}} \geq \mathsf{low}$: if
  $\mathsf{nf^{old}} < \mathsf{low}$, the field subtraction wraps to a
  value $\geq q_ {\mathbb{P}} - 2^{250} \gg 2^{250}$, failing the range
  check. This relies on the sentinel initialization ensuring
  $\mathsf{width} < 2^{250}$ and therefore all legitimate offsets are
  small.

- Check 2 proves $\mathsf{nf^{old}} \leq \mathsf{low} + \mathsf{width}$:
  substituting, $2^{250} - 1 - \mathsf{width} + x = 2^{250} - 1 - (\mathsf{width} - x)$.
  This is in $[0, 2^{250})$ if and only if $\mathsf{width} - x \geq 0$,
  i.e., $x \leq \mathsf{width}$.
</details>

**Alternate nullifier integrity.** $\hspace{0.5em}$
$\mathsf{nf_ {dom}} = \mathsf{Poseidon}(\mathsf{nk}, \mathsf{dom}, \mathsf{nf^{old}})$
(see [Alternate Nullifier Derivation]).

### Circuit Implementation Notes

The first six conditions (note commitment integrity through diversified
address integrity) are adapted from the corresponding Orchard Action
statement checks. In particular, note-commitment Merkle membership uses
$\mathsf{Extract}_ {\mathbb{P}}(\mathsf{cm^{old}})$ as in the Orchard
Action statement. [^protocol-actionstatement] Implementations SHOULD share
circuit gadgets with an Orchard implementation to minimize new code
requiring review.

The nullifier non-membership check requires a Poseidon-based Merkle path
verification (29 levels, 30 total Poseidon calls per note) and two 250-bit
range checks.

The alternate nullifier integrity check is a single Poseidon hash
(two permutations at width 3).


## Spend Authorization Signature

Each Claim proof MUST be accompanied by a spend authorization signature
$\sigma$, which is a $\mathsf{SpendAuthSig^{Orchard}}$ signature under
the randomized key $\mathsf{rk}$ that is a public input to the circuit.

The signature MUST be computed over a sighash that binds the signature
to the specific claim, ensuring that it cannot be replayed for a
different set of public inputs. Applications MAY achieve this binding
directly (by including the public inputs in the sighash) or indirectly
(through values that the Claim circuit constrains to be consistent with
the public inputs).

The concrete sighash derivation is application-defined. The [Wallet Signing]
section specifies a PCZT-based signing flow that reuses the standard
ZIP 244 [^zip-244] sighash, enabling compatibility with existing hardware
wallets.


## Out-of-Circuit Verification

A verifier that receives a Claim proof $\pi$ together with a spend
authorization signature $\sigma$ MUST perform the following checks:

1. Verify $\pi$ against the public inputs
   $(\mathsf{rt^{cm}}, \mathsf{rt^{excl}}, \mathsf{rk}, \mathsf{cv}, \mathsf{nf_ {dom}}, \mathsf{dom})$.

2. Verify $\sigma$ as a valid $\mathsf{SpendAuthSig^{Orchard}}$ signature
   on the sighash (see [Spend Authorization Signature]), under the
   randomized key $\mathsf{rk}$.

3. Verify that $\mathsf{rt^{cm}}$ corresponds to the Orchard note
   commitment tree root at the declared snapshot height.

4. Verify that $\mathsf{rt^{excl}}$ corresponds to the nullifier
   non-membership tree root at the declared snapshot height.

5. Verify that $\mathsf{dom}$ is valid for the current application
   instance.

6. Verify that $\mathsf{nf_ {dom}}$ has not been previously accepted in the
   same nullifier domain. If it has, reject the claim as a double-claim.


## Multi-Note Batching

The Claim circuit defined in [Claim Circuit] proves a statement about a
single note. Applications that require proving aggregate balance across
multiple notes MAY use the following batching extension.

### Batched Claim Circuit

A batched Claim circuit for $N$ notes modifies the single-note circuit
as follows:

- The public inputs $\mathsf{rt^{cm}}$, $\mathsf{rt^{excl}}$,
  $\mathsf{rk}$, and $\mathsf{dom}$ are shared across all $N$ notes.
- Each note $i$ contributes its own value commitment
  $\mathsf{cv_ i}$ and alternate nullifier
  $\mathsf{nf_ {dom,i}}$ as public inputs.
- A single $\mathsf{ivk}$ (derived from the shared $\mathsf{ak}$ and
  $\mathsf{nk}$) is constrained to own all $N$ notes, ensuring they
  belong to the same holder.
- All $N$ note commitment integrity, value commitment integrity,
  Merkle path, nullifier derivation, non-membership, and alternate
  nullifier checks are performed independently per note.

### Note Padding

To avoid leaking the number of notes a holder is claiming, the circuit
SHOULD accept a fixed number of note slots $N_ {\max}$ (for example,
$N_ {\max} = 5$). Unused slots are filled with *padded notes*.

Each note slot carries a private boolean witness
$\mathsf{is\_real} \in \{0, 1\}$, constrained by
$\mathsf{is\_real} \cdot (1 - \mathsf{is\_real}) = 0$.
A padded note is a slot with $\mathsf{is\_real} = 0$.

A padded note MUST satisfy the following:

- **Value.** The value MUST be 0, enforced by the constraint
  $(1 - \mathsf{is\_real}) \cdot \mathsf{v^{old}} = 0$.
- **Value commitment.** The value commitment is computed for every slot
  (not gated). Padded notes commit to value 0 with a fresh
  $\mathsf{rcv}$.
- **Ownership.** The note is derived from the same full viewing key as
  real notes (using a distinct diversifier index per padded slot), so it
  passes the diversified address integrity check with the shared
  $\mathsf{ivk}$.
- **Note commitment integrity.** The commitment is recomputed from the
  padded note's plaintext (value 0, random nullifier, random
  $\text{ψ}$, fresh $\mathsf{rcm}$) and constrained to equal the
  witnessed $\mathsf{cm}$. This check is not gated by
  $\mathsf{is\_real}$.
- **Merkle membership.** The Merkle path is computed for the padded
  note, but the root equality check is gated:
  $\mathsf{is\_real} \cdot (\mathsf{root} - \mathsf{rt^{cm}}) = 0$.
  For padded notes ($\mathsf{is\_real} = 0$) the constraint is
  trivially satisfied regardless of the computed root, effectively
  skipping the membership check.
- **Nullifier non-membership.** The IMT non-membership check is NOT
  gated by $\mathsf{is\_real}$. Padded notes MUST provide a valid
  non-membership proof against $\mathsf{rt^{excl}}$. Because padded
  nullifiers are random field elements, they fall within an unrevealed
  interval with overwhelming probability.
- **Nullifier derivation.** The standard nullifier is derived in-circuit
  (not gated). It is used for the non-membership check and the alternate
  nullifier derivation but is never revealed.
- **Alternate nullifier.** The alternate nullifier is derived and
  published for every slot (not gated). The application verifier MAY
  ignore alternate nullifiers corresponding to zero-value slots.


## Sub-Circuit Instantiation

When the Claim circuit is used as a sub-circuit of an application-specific
circuit, the application circuit has direct access to the private witnesses
including the note value $\mathsf{v^{old}}$. In this case, the value
commitment $\mathsf{cv}$ MAY be omitted from the public inputs if the
application circuit binds to the note values through its own mechanism.
For example, an application circuit that converts note values to
application-specific units (such as vote weight) may bind to
$\mathsf{v^{old}}$ directly within the circuit and expose the converted
result through its own public outputs. All other conditions of the Claim
circuit MUST still be enforced.


## Wallet Signing

The signing flow proceeds in five steps:

1. The wallet generates an application hotkey on the local device.
2. The wallet constructs a dummy signed note whose nullifier commits
   to the delegation context.
3. The wallet builds a PCZT containing the dummy signed note.
4. The hardware wallet device signs the PCZT and returns the signature.
5. The wallet extracts the signature and assembles the delegation
   submission.

Each interaction with the hardware wallet device delegates up to
$N_{\max}$ Orchard notes (we utilize the default batch size of 5).
A holder with more than $N_{\max}$ notes repeats the flow for each batch,
producing a separate application commitment per batch. The holder MAY choose
to delegate fewer batches than their full note set, claiming only the balance
covered by the delegated batches.

### Dummy Signed Note Construction

The wallet constructs a dummy Orchard note as follows:

1. **Address.** The signed note's address is derived from the holder's
   full viewing key at diversifier index 0 with external scope:
   $\mathsf{addr}^{\mathsf{signed}} = \mathsf{fvk.address\_at}(0, \mathsf{External})$.
   A fixed index is used because the address is a private witness inside
   the ZKP circuit and is never publicly transmitted.

2. **Nullifier commitment.** Because the dummy note
   has no on-chain existence, its fields (including $\text{ρ}$) can be
   freely chosen. This design utilizes that freedom: $\text{ρ}$ is set to
   a hash of the delegation context so that the note commitment, and
   therefore the sighash, cryptographically binds the hardware wallet's
   signature to the exact set of notes being delegated. This avoids
   requiring a custom signing protocol; the hardware wallet signs a
   standard Orchard PCZT, and the binding is enforced by the ZKP circuit
   rather than by device firmware.

   Concretely, the signed note's $\text{ρ}$ is set to:

$$\text{ρ}^{\mathsf{signed}} = \mathsf{Poseidon}\bigl(\mathsf{cmx}\_\mathsf{1}, \ldots, \mathsf{cmx}\_{N_{\max}}, \mathsf{app\_commitment}, \mathsf{instance\_id}\bigr)$$

   where $\mathsf{cmx}\_\mathsf{1} \ldots \mathsf{cmx}\_{N_{\max}}$ are the
   extracted note commitments of the $N_{\max}$ delegated note slots
   (real notes plus zero-value padding notes),
   $\mathsf{app\_commitment}$ is an application-defined commitment
   (e.g., a VAN commitment in the voting protocol [^voting-protocol]),
   and $\mathsf{instance\_id}$ is the usage identifier that uniquely
   identifies the proof-of-balance instance.

   With $N_{\max} = 5$ this is a 7-input Poseidon hash using the
   $\mathsf{P128Pow5T3}$ instantiation (width $t = 3$, rate 2) over
   $\mathbb{F}_{q_{\mathbb{P}}}$. The seven inputs are absorbed in four
   permutations.

3. **Value.** The note value MUST be set to 1 zatoshi (0.00000001 ZEC)
   in the PCZT. The Claim circuit treats the signed note value as 0
   regardless of the PCZT value.

4. **Rseed.** A fresh random $\mathsf{rseed}$ is sampled for the note.

5. **Note construction.** The note is constructed via standard Orchard
   note construction using the address, value (1 zatoshi), rho, and
   rseed above.

For fewer than $N_{\max}$ real notes, the wallet pads the remaining
slots with zero-value dummy notes at diversifier indices $1000 + i$
(external scope) from the holder's full viewing key. These padding notes
enter the $\text{ρ}$ commitment via their $\mathsf{cmx}$ values but do
not correspond to real on-chain notes.

### PCZT Construction

The wallet constructs a PCZT as a single-action Orchard transaction:

#### Spend Side

- The single spend consumes the dummy signed note constructed above.
- A dummy Merkle authentication path (all-zero siblings, position 0)
  is used. The path is not verified on-chain; spend authorization is
  established by the ZKP circuit.
- The Orchard bundle builder generates the spend authorization
  randomizer $\alpha$ and the randomized verification key
  $\mathsf{rk} = \mathsf{ak} + [\alpha]\, G$ internally.

#### Output Side

- A single output of 1 zatoshi is addressed to the application hotkey.
- The output memo SHOULD contain a human-readable delegation description.
  For example, a voting application might use:

  `"I am authorizing this hotkey managed by my wallet to participate`
  `in {instance_name} with {amount}.{frac} ZEC."`

  where `{instance_name}` identifies the proof-of-balance instance and
  `{amount}.{frac}` is the holder's eligible ZEC balance.

#### ZIP-32 Derivation

The spend MUST include a ZIP 32 [^zip-32] derivation path so that the
hardware wallet device can derive the correct spending key:

$$\mathsf{path} = [32', \mathsf{coin\_type}', \mathsf{account}']$$

where $\mathsf{coin\_type}$ is 133 for Zcash mainnet.

#### Finalization

The wallet applies the PCZT Creator and IoFinalizer roles. The
IoFinalizer computes the ZIP 244 [^zip-244] transaction identifier
(sighash) that the hardware wallet device will sign.

### Device Display

During signing, the hardware wallet device displays the PCZT as a
standard Orchard transaction. The user sees fields such as:

    Amount: 0.00000001 ZEC
    Fee: 0 ZEC

    Orchard
    From
    #1 0.00000001 ZEC Mine
    <shielded>

    To
    #1 0.00000001 ZEC
    {application hotkey address}
    Memo: I am authorizing this hotkey managed by my
          wallet to participate in {instance_name} with
          {amount}.{frac} ZEC

The 0.00000001 ZEC amount (1 zatoshi) and 0 ZEC fee confirm that no
real funds are being transferred. The "To" address matches the
application hotkey address displayed in the wallet application. The memo
provides human-readable context for what the user is authorizing.

The hardware wallet device has no awareness of application semantics. It
interprets the PCZT identically to any other Orchard transaction.

### Signature Extraction and Submission

After receiving the signed PCZT from the hardware wallet device, the
wallet:

1. Parses the signed PCZT structurally and reads the `spend_auth_sig`
   field from the relevant action. Some devices (e.g., Keystone) redact
   sensitive fields ($\alpha$, rseed, ZIP-32 derivation) after signing,
   so the wallet MUST extract the signature by parsing the PCZT structure
   rather than by byte-diffing against the unsigned version.

2. Recomputes the sighash that the device signed. This is the ZIP 244
   transaction identifier computed over the PCZT.

3. Assembles the delegation submission by combining the hardware wallet
   signature and sighash with the Claim proof and other public inputs.
   The submission format is application-defined.

The delegation submission is sent to the application verifier. The
wallet does not need the hardware wallet device again for the remainder
of the usage instance; all subsequent operations use the application
hotkey.

# Rationale

## Why Alternate Nullifiers Instead of Actual Spends

The most obvious approach to proof-of-balance (actually spending the
notes to oneself at the snapshot anchor) fails because it consumes the
notes on-chain. A holder who participates in one application cannot reuse
the same notes in a concurrent application. Alternate nullifiers avoid
this by operating entirely off the main chain: the standard nullifiers are
never revealed, and the notes remain spendable.

## Why Sentinel Initialization

Without sentinels, the initial non-membership tree would contain a single
leaf spanning the entire field $[0, q_ {\mathbb{P}}-1]$, with width
$\approx 2^{254}$. The in-circuit range checks use 250-bit windows
(25 limbs of the 10-bit lookup table). An interval wider than $2^{250}$
would allow the upper-bound range check to wrap, enabling a prover to
falsely claim non-membership for a value outside the interval.

Sentinels partition the field into intervals each narrower than $2^{250}$
at initialization. Real nullifier insertions only split intervals into
smaller ones, so the width bound is maintained permanently.

## Why 1 Zatoshi Instead of 0

The dummy signed note uses a value of 1 zatoshi (0.00000001 ZEC) in the
PCZT rather than 0. When an Orchard Action has a 0-value
note, Keystone's suppress the display of transaction fields
(amount, fee, addresses, memo), presenting the user with insufficient
information to make an informed signing decision. Setting the value to
1 zatoshi causes the device to render all fields normally.

The Claim circuit enforces that the signed note value is 0 regardless of
the PCZT value. The 1-zatoshi value exists solely in the serialized PCZT
for the benefit of the device's display logic and has no effect on
protocol security or fund safety.

## Why a Dummy Note Instead of a Real Note

A holder's real Orchard notes are not spent or consumed during
delegation. The dummy signed note is constructed specifically for the
proof-of-balance flow and never appears in any on-chain note commitment
tree. This design has three advantages:

- **No fund risk.** Because the proof-of-balance transaction is never
  broadcast to the Zcash mainchain and the signed note has no on-chain
  existence, there is no scenario in which the delegation signing could
  result in loss of funds.
- **Note reusability.** Because real notes are never consumed on
  mainchain, they remain fully spendable and available for other
  applications that use the proof-of-balance mechanism. Alternate
  nullifiers are domain-separated by $\mathsf{instance\_id}$, so the
  same notes can participate in concurrent proof-of-balance instances
  without conflict.
- **PCZT compatibility.** The dummy note reuses the standard Orchard
  Action structure, allowing the PCZT to pass through the
  hardware wallet's existing PCZT parser and signer without
  modification.

## Why the Dummy Note's ρ Provides Non-Replayability

Because the dummy signed note does not correspond to any on-chain note,
its inputs can be freely chosen. The design sets
$\text{ρ}^{\mathsf{signed}}$ to a Poseidon hash of the delegated note
commitments, the application commitment, and the usage identifier.
Because $\text{ρ}$ enters the note commitment (and therefore the
sighash), the hardware wallet's signature is cryptographically bound to
the exact delegation context. An attacker cannot replay the signature
for a different set of notes, a different application commitment, or a
different usage instance.

This binding is enforced by the Claim circuit, which the application
verifier checks. The hardware wallet device does not need to understand
the binding; it is sufficient that the device signs the sighash derived
from the PCZT containing the committed $\text{ρ}$. No custom signing
protocol is required — the standard Orchard PCZT flow is reused, and
all existing hardware wallets that support Orchard signing are
compatible without firmware changes.

## Why ZIP 244 Sighash

The PCZT uses the standard ZIP 244 [^zip-244] transaction
identifier as the sighash. This is the only sighash format that
existing hardware wallet Orchard signing implementations can produce.
Using an application-specific sighash would require firmware changes,
which this specification explicitly avoids.

The ZIP 244 sighash commits to the full Orchard bundle structure
(including the dummy note's commitment, which embeds the bound
$\text{ρ}$), providing the necessary cryptographic binding without
a custom signature scheme.

## Why Not a Custom Signing Protocol

A future version of this specification could define a custom signing
protocol purpose-built for proof-of-balance, rather than reusing the
standard Orchard PCZT format. This would require ecosystem-wide
coordination (firmware updates to all participating hardware wallets)
but could yield several improvements:

- **Binding application actions to the signature.** Many use cases want
  to prove balance *and* take an action in a single step (e.g., casting
  a vote). A custom signing protocol could commit to the application
  action directly in the signature, reducing the number of ZKPs required
  by downstream protocols.
- **Removing the hotkey indirection.** With a richer signing format, the
  holder could authorize actions directly from the hardware wallet
  without delegating to an application hotkey, simplifying the trust
  model.
- **Improved on-device display.** A custom format could present
  application-aware context (e.g., "Vote on proposal X with Y ZEC")
  rather than the generic Orchard transaction fields shown today.

This specification intentionally avoids a custom signing protocol to
maximize compatibility with existing wallets. The trade-off is accepted:
downstream protocols may require additional ZKPs or hotkey indirection
that a purpose-built signing format could eliminate.


# Deployment

This ZIP does not specify a consensus change. Deployment considerations
are application-specific.

The hardware wallet signing flow specified in [Wallet Signing]
requires no firmware changes and no changes to Zcash mainchain consensus
rules. Any hardware wallet that supports Orchard PCZT signing can
participate immediately.

Software wallets that hold the spending key directly do not need the
PCZT construction; they follow the same Claim proof specification but
sign the application-defined sighash directly.


# Reference implementation

A reference implementation of the Claim circuit (including the
non-membership tree, alternate nullifier derivation, and multi-note
batching for $N_ {\max} = 5$) is available at
[valargroup/voting-circuits](https://github.com/valargroup/voting-circuits).


# Open issues


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-orchardcommitmenttree]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.1: Note Commitment Trees](protocol/protocol.pdf#merkletree)

[^protocol-actionstatement]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 4.17.4: Action Statement (Orchard)](protocol/protocol.pdf#actionstatement)

[^protocol-merklepath]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 4.9: Merkle Path Validity](protocol/protocol.pdf#merklepath)

[^protocol-sinsemilla]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.1.9: Sinsemilla Hash Function](protocol/protocol.pdf#concretesinsemillahash)

[^protocol-poseidon]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.2: Pseudo Random Functions](protocol/protocol.pdf#concreteprfs)

[^poseidon]: [Poseidon: A New Hash Function for Zero-Knowledge Proof Systems](https://eprint.iacr.org/2019/458)

[^pir-nullifier-exclusion]: [Draft ZIP: Private Information Retrieval for Nullifier Exclusion Proofs](https://github.com/zcash/zips/pull/1198)

[^draft-str4d-orchard-balance-proof]: [Draft ZIP: Air drops, Proof-of-Balance, and Stake-weighted Polling](draft-str4d-orchard-balance-proof.md)

[^voting-protocol]: [Shielded Voting Protocol](draft-valargroup-shielded-voting.md)

[^zip-244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^zip-32]: [ZIP 32: Shielded Hierarchical Deterministic Wallets](zip-0032.rst)
