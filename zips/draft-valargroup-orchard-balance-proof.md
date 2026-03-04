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

- **Air drops** — distributing tokens proportional to shielded holdings.
- **Stake-weighted polling** — weighting votes by ZEC balance.
- **Proof-of-balance** — demonstrating solvency or collateral without
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


# Requirements

- A holder can prove ownership of an unspent Orchard note at a pool
  snapshot without revealing the note's standard nullifier.
- Double-claiming the same note within the same nullifier domain is
  detectable: the alternate nullifier is deterministic, so a duplicate
  claim produces an identical value that the verifier can reject.
- Claims are unlinkable to the holder's past or future on-chain spends,
  and to their claims in other nullifier domains.
- The holder proves spend authority (not merely viewing access).
- The construction allows a holder to participate in multiple independent
  applications using the same notes, provided each application uses a
  distinct nullifier domain. This is a natural consequence of the
  domain-separated alternate nullifier derivation.


# Non-requirements

- Application-specific protocols that consume claims (such as voting,
  air-drop distribution, or delegation) are out of scope.
- Privacy-preserving retrieval of non-membership Merkle paths (e.g., via
  PIR) is out of scope.
- Value denomination conversions (e.g., converting zatoshi to ballot
  counts) are application-specific and out of scope.
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

The nullifier non-membership tree is a Merkle tree whose leaves encode
the gaps between consecutive revealed nullifiers, enabling efficient
in-circuit proofs that a given nullifier is absent from the revealed set.

### Construction

Let $S = \{s_ 0, s_ 1, \ldots, s_ {m-1}\}$ be the set of all Orchard
nullifiers revealed on the consensus chain as of block height $h$, together
with a set of sentinel values (see [Sentinel Initialization]). Sort $S$ in
ascending order as elements of $\mathbb{F}_ {q_ {\mathbb{P}}}$.
Because sentinel initialization is mandatory, $S$ is non-empty.

For each pair of consecutive elements $(s_ i, s_ {i+1})$ where $s_ i < s_ {i+1}$
and $s_ {i+1} - s_ i > 1$, create a leaf with:

- $\mathsf{low} = s_ i + 1$ — the first value in the gap
- $\mathsf{width} = s_ {i+1} - s_ i - 2$ — the number of additional values
  in the gap beyond $\mathsf{low}$

The leaf represents the closed interval
$[\mathsf{low},\; \mathsf{low} + \mathsf{width}]$, which contains exactly
the field elements between $s_ i$ and $s_ {i+1}$ exclusive.

After processing all consecutive pairs, if $s_ {m-1} < q_ {\mathbb{P}} - 1$,
a terminal leaf MUST be added with:

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

The non-membership tree uses Poseidon [^poseidon] over
$\mathbb{F}_ {q_ {\mathbb{P}}}$ (the Pallas base field) for all hashing:

- **Leaf hash:** $\mathsf{Poseidon}(\mathsf{low}, \mathsf{width})$,
  a 2-input Poseidon hash with width $t = 3$.
- **Internal node hash:** $\mathsf{Poseidon}(\mathsf{left}, \mathsf{right})$,
  a 2-input Poseidon hash with width $t = 3$, where $\mathsf{left}$ and
  $\mathsf{right}$ are determined by the node's position bit at each level.

Implementations MUST use the Poseidon instantiation over $\mathbb{F}_ {q_ {\mathbb{P}}}$
with the standard parameter generation procedure from [^poseidon], targeting
128-bit security.

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

This specification uses a tree depth of
$\mathsf{MerkleDepth^{excl}} = 29$, supporting up to $2^{29} \approx 537$
million leaves. Each nullifier insertion splits one interval leaf into two
(adding one leaf), so the tree supports approximately 537 million distinct
nullifiers. As of early 2026, the Zcash Orchard pool contains roughly
51 million nullifiers, so depth 29 provides about one order of magnitude
of headroom.
Implementations MAY choose a different depth to suit their capacity
requirements, but the circuit MUST be parameterized accordingly based on
the chosen depth.

Unused leaf positions MUST be filled with a canonical empty leaf value
(the hash of the zero interval).

### Sentinel Initialization

Before inserting any real nullifiers, the non-membership tree MUST be
initialized with sentinel values that partition $\mathbb{F}_ {q_ {\mathbb{P}}}$
into intervals each of width strictly less than $2^{250}$.

For the Pallas base field ($q_ {\mathbb{P}} \approx 2^{254}$),
implementations MUST insert 17 sentinels at:

$$s_k = k \cdot 2^{250}, \quad k \in \{0,1,\ldots,16\}.$$

This guarantees the width bound required by the in-circuit range checks:

- For $k = 0,\ldots,15$, the interval between consecutive sentinels has
  width exactly $2^{250} - 2$.
- The final tail interval has width
  $q_ {\mathbb{P}} - 16 \cdot 2^{250} - 2 < 2^{250}$.

The width bound is critical for the soundness of the in-circuit range
checks. If any interval had width $\geq 2^{250}$, the range check could
overflow, allowing a prover to falsely claim non-membership.

Sentinel values are fixed per deployment and MUST be published alongside the
tree specification so that any party can reconstruct the tree independently.


## Nullifier Domains

A nullifier domain $\mathsf{dom}$ is an element of
$\mathbb{F}_ {q_ {\mathbb{P}}}$ that defines a double-claim detection scope.
Each independent claim context (such as a specific air-drop event, a single
poll, or an individual voting round) MUST use its own domain.

Applications MUST ensure that the domain value is unique across
independent claim contexts. Two claims that share the same domain and the
same underlying note will produce the same alternate nullifier, which is
the mechanism for double-claim prevention.

Applications SHOULD derive the domain deterministically from public
parameters that bind it to a specific context. For example:

$$\mathsf{dom} = \mathsf{Poseidon}(\text{"BalanceProofDomain"}, \mathsf{snapshot\_height}, \mathsf{purpose\_hash})$$

where $\mathsf{purpose\_hash}$ is a hash of an application-specific
identifier string. This derivation prevents accidental domain collisions
across independent applications using the same snapshot.

Applications MAY define their own domain derivation scheme provided it
satisfies the uniqueness requirement above.


## Alternate Nullifier Derivation

Given a nullifier domain $\mathsf{dom}$ and an Orchard note with standard
nullifier $\mathsf{nf^{old}}$, the alternate nullifier $\mathsf{nf_ {dom}}$
is computed as:

$$\mathsf{nf_ {dom}} = \mathsf{DeriveAlternateNullifier_ {nk}}(\mathsf{tag}, \mathsf{dom}, \mathsf{nf^{old}}) = \mathsf{Poseidon}(\mathsf{nk}, \mathsf{tag}, \mathsf{dom}, \mathsf{nf^{old}})$$

where:

- $\mathsf{nk} \in \mathbb{F}_ {q_ {\mathbb{P}}}$ is the nullifier deriving
  key from the holder's full viewing key.
- $\mathsf{tag} \in \mathbb{F}_ {q_ {\mathbb{P}}}$ is an application-defined
  domain separator constant that identifies the protocol type (e.g.,
  governance, air-drop). This value is fixed per application and known to
  both prover and verifier.
- $\mathsf{dom} \in \mathbb{F}_ {q_ {\mathbb{P}}}$ is the nullifier domain.
- $\mathsf{nf^{old}} \in \mathbb{F}_ {q_ {\mathbb{P}}}$ is the note's
  standard Orchard nullifier, computed as
  $\mathsf{DeriveNullifier_ {nk}}(\text{ρ}^{\mathsf{old}}, \text{ψ}^{\mathsf{old}}, \mathsf{cm^{old}})$.

This is a 4-input Poseidon hash. Using the standard $\mathsf{P128Pow5T3}$
instantiation (width $t = 3$, rate 2), this requires two permutations
to absorb four input elements.

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

**Unlinkability.** Model $\mathsf{Poseidon}(\mathsf{nk}, \cdot, \cdot, \cdot)$
as a PRF keyed by $\mathsf{nk}$. An adversary who does not know
$\mathsf{nk}$ sees outputs that are indistinguishable from random. Given
$\mathsf{nf_ {dom}} = \mathsf{Poseidon}(\mathsf{nk}, \mathsf{tag}, \mathsf{dom}, \mathsf{nf^{old}})$
and $\mathsf{nf^{old}}$, the adversary cannot verify the relationship
without $\mathsf{nk}$. The nullifier deriving key $\mathsf{nk}$ is a
255-bit value derived from the spending key and is never revealed on-chain.

**Cross-domain unlinkability.** For two domains $\mathsf{dom_ 1} \neq \mathsf{dom_ 2}$,
the tuples $(\mathsf{tag}, \mathsf{dom_ 1}, \mathsf{nf^{old}})$ and
$(\mathsf{tag}, \mathsf{dom_ 2}, \mathsf{nf^{old}})$ are distinct inputs to the PRF.
Under the PRF assumption, their outputs are jointly indistinguishable from
independent random values.

**Collision resistance.** If $\mathsf{nf^{old}_ 1} \neq \mathsf{nf^{old}_ 2}$,
then $(\mathsf{nk}, \mathsf{tag}, \mathsf{dom}, \mathsf{nf^{old}_ 1})$ and
$(\mathsf{nk}, \mathsf{tag}, \mathsf{dom}, \mathsf{nf^{old}_ 2})$ are distinct Poseidon
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
non-membership check. The security assumption is comparable — both
constructions rely on the hardness of distinguishing $\mathsf{nk}$-keyed
evaluations from random.

The current Zcash coinholder voting system was designed and implemented
around this construction. A future revision of this ZIP may revisit the
choice as part of a broader protocol revision — for example, if hardware
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

**Nullifier derivation.** $\hspace{0.5em}$
$\mathsf{nf^{old}} = \mathsf{DeriveNullifier_ {nk}}(\text{ρ}^{\mathsf{old}}, \text{ψ}^{\mathsf{old}}, \mathsf{cm^{old}})$.

The standard nullifier is computed inside the circuit but is NOT a public
input — it is used only as an intermediate value for the non-membership
check and the alternate nullifier derivation. It is never revealed.

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
Let $\mathsf{leaf} = \mathsf{Poseidon}(\mathsf{low}, \mathsf{width})$.
$(\mathsf{path^{excl}}, \mathsf{pos^{excl}})$ is a valid Merkle path of
depth $\mathsf{MerkleDepth^{excl}}$ from $\mathsf{leaf}$ to the anchor
$\mathsf{rt^{excl}}$, using Poseidon for internal node hashing.

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
$\mathsf{nf_ {dom}} = \mathsf{Poseidon}(\mathsf{nk}, \mathsf{tag}, \mathsf{dom}, \mathsf{nf^{old}})$.

### Circuit Implementation Notes

The first five conditions (note commitment integrity through diversified
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


## Out-of-Circuit Verification

A verifier that receives a Claim proof $\pi$ together with a spend
authorization signature $\sigma$ MUST perform the following checks:

1. Verify $\pi$ against the public inputs
   $(\mathsf{rt^{cm}}, \mathsf{rt^{excl}}, \mathsf{rk}, \mathsf{nf_ {dom}}, \mathsf{dom})$.

2. Verify $\sigma$ as a valid $\mathsf{SpendAuthSig^{Orchard}}$ signature
   on the application-defined sighash, under the randomized key
   $\mathsf{rk}$.

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
- Each note $i$ contributes its own alternate nullifier
  $\mathsf{nf_ {dom,i}}$ as a public input.
- A single $\mathsf{ivk}$ (derived from the shared $\mathsf{ak}$ and
  $\mathsf{nk}$) is constrained to own all $N$ notes, ensuring they
  belong to the same holder.
- All $N$ note commitment integrity, Merkle path, nullifier derivation,
  non-membership, and alternate nullifier checks are performed
  independently per note.

### Note Padding

To avoid leaking the number of notes a holder is claiming, the circuit
SHOULD accept a fixed number of note slots $N_ {\max}$ (for example,
$N_ {\max} = 5$). Unused slots are filled with *padded notes*: randomly
generated note data with value 0. Padded notes satisfy all circuit
checks (the commitment is valid, the Merkle path can use any valid leaf,
and the non-membership check passes for random nullifiers with overwhelming
probability).

An $\mathsf{is\_real}$ flag (private witness, constrained to be boolean)
distinguishes real notes from padded notes:

- Padded notes MUST have $\mathsf{v^{old}} = 0$.
- Merkle membership and non-membership checks MAY be skipped for padded
  notes (conditioned on $\mathsf{is\_real} = 0$) as an optimization, but
  performing them is also sound since padded notes use valid dummy data.


# Rationale

## Why Alternate Nullifiers Instead of Actual Spends

The most obvious approach to proof-of-balance (actually spending the
notes to oneself at the snapshot anchor) fails because it consumes the
notes on-chain. A holder who participates in one application cannot reuse
the same notes in a concurrent application. Alternate nullifiers avoid
this by operating entirely off the main chain: the standard nullifiers are
never revealed, and the notes remain spendable.

## Why (low, width) Leaf Encoding

Storing $\mathsf{width} = \mathsf{end} - \mathsf{low}$ in the leaf
instead of $\mathsf{end}$ eliminates one field subtraction from the
in-circuit interval check. The tree builder performs this subtraction once
during construction; the circuit evaluates the check once per claim per
note. Since the number of claims vastly exceeds the number of tree
rebuilds, the net constraint savings is significant.

## Why Poseidon for the Non-Membership Tree

The Orchard note commitment tree uses Sinsemilla for Merkle hashing.
Sinsemilla operates on bitstrings and requires decomposition of field
elements into bits before hashing, incurring overhead in an arithmetic
circuit. Poseidon operates natively on field elements, avoiding this
decomposition. Since the non-membership tree is new infrastructure with
no backwards-compatibility constraint, the more circuit-efficient
primitive is used.

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


# Deployment

This ZIP does not specify a consensus change. Deployment considerations
are application-specific.

For applications using hardware wallets (e.g., Keystone), the spend
authorization signature is obtained through a PCZT-based signing flow
where the hardware wallet signs a transaction that encodes the claim
context. The hardware wallet need not understand the claim semantics; it
signs a standard Orchard spend authorization. Applications that support
Keystone firmware with voting-aware context display can provide richer
user assurance, but both modes use the same underlying circuit and
signature scheme.


# Reference implementation

A reference implementation of the Claim circuit (including the
non-membership tree, alternate nullifier derivation, and multi-note
batching for $N_ {\max} = 5$) exists in the coinholder voting codebase used
for this design.

At the time of writing, some implementation repositories are not publicly
accessible. Public, stable links will be added before finalization of
this ZIP.


# Open issues

- The Poseidon instantiation ($\mathsf{P128Pow5T3}$) and its round
  constants remain to be explicitly referenced or pinned once a canonical
  parameter set for Zcash usage is published.
- The interaction between multi-note batching and the sighash scheme
  (what exactly is signed, and how it binds to all $N$ notes) requires
  further specification per application.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-orchardcommitmenttree]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.1: Note Commitment Trees](protocol/protocol.pdf#merkletree)

[^protocol-actionstatement]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 4.17.4: Action Statement (Orchard)](protocol/protocol.pdf#actionstatement)

[^protocol-merklepath]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 4.9: Merkle Path Validity](protocol/protocol.pdf#merklepath)

[^protocol-sinsemilla]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.1.9: Sinsemilla Hash Function](protocol/protocol.pdf#concretesinsemillahash)

[^poseidon]: [Poseidon: A New Hash Function for Zero-Knowledge Proof Systems](https://eprint.iacr.org/2019/458)

[^pir-nullifier-exclusion]: [Draft ZIP: Private Information Retrieval for Nullifier Exclusion Proofs](https://github.com/zcash/zips/pull/1198)

[^draft-str4d-orchard-balance-proof]: [Draft ZIP: Air drops, Proof-of-Balance, and Stake-weighted Polling](draft-str4d-orchard-balance-proof)
