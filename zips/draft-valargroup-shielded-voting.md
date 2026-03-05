    ZIP: Unassigned
    Title: Shielded Voting Protocol
    Owners: Dev Ojha <dojha@berkeley.edu>
            Roman Akhtariev <ackhtariev@gmail.com>
            Adam Tucker <adamleetucker@outlook.com>
            Greg Nagy <greg@dhamma.works>
    Credits: Daira-Emma Hopwood
             Jack Grigg
    Status: Draft
    Category: Standards
    Created: 2026-03-04
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/1200>


# Terminology

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms below are to be interpreted as follows:

Ballot

: A unit of voting weight derived from a zatoshi balance. The
  conversion from zatoshi to ballots is defined in [Ballot Scaling].

Vote Authority Note (VAN)

: A commitment inserted into the Vote Commitment Tree that represents
  spendable voting authority. A VAN binds a voting hotkey, a ballot
  count, a voting round identifier, and a proposal authority bitmask.

Vote Commitment (VC)

: A commitment inserted into the Vote Commitment Tree that binds a
  voter's encrypted share distribution, proposal choice, and vote
  decision for a single proposal. A VC is created when a VAN is consumed
  to cast a vote.

Vote Commitment Tree (VCT)

: An append-only Poseidon Merkle tree maintained by the vote chain that
  stores both VANs and VCs as leaves.

Vote share

: One of $N_s$ encrypted portions of a voter's ballot count within a
  Vote Commitment. Each share is submitted independently for
  homomorphic accumulation.

Voting round

: A bounded period during which a set of proposals are open for voting.
  Each round is identified by a unique $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$ and
  is associated with a pool snapshot, an election authority public key,
  and a set of proposals.

Election authority (EA)

: The set of validators that collectively hold Shamir shares of the
  El Gamal secret key $\mathsf{ea}\_\mathsf{sk}$ for a voting round. No single
  validator holds the full key. At tally time, $t$ validators cooperate
  to produce partial decryptions of the aggregate ciphertext.

Submission server

: An untrusted server to which a voter delegates the construction and
  submission of Vote Reveal Proofs. The server learns encrypted shares
  and vote decisions but cannot decrypt share amounts or link shares to
  voter identities.

Governance nullifier

: An alternate nullifier (as defined in [^balance-proof]) scoped to the
  governance domain, published during delegation to prevent
  double-delegation of the same Orchard note within a voting round.

VAN nullifier

: A nullifier derived from a VAN commitment and published when the VAN
  is consumed (to cast a vote or delegate), preventing double-spending
  of voting authority.

Share nullifier

: A nullifier derived from a vote commitment and share index, published
  when a share is revealed, preventing double-counting.


# Abstract

This ZIP specifies a shielded voting protocol that allows holders of
Orchard notes to cast stake-weighted votes on proposals without revealing
their identity, individual balances, or vote allocations.

The protocol proceeds in three proving phases. First, a *delegation
proof* (building on the Orchard Proof-of-Balance [^balance-proof])
converts proven Orchard balance into a Vote Authority Note on a
purpose-built vote chain. Second, a *vote proof* consumes a VAN to
produce a Vote Commitment containing $N_s$ El Gamal-encrypted shares of
the voter's ballot count, split across vote options. Third, a *vote
reveal proof*, constructed by an untrusted submission server, opens
individual encrypted shares for homomorphic accumulation, without
revealing which Vote Commitment the share originated from.

After the voting window closes, anyone can publicly aggregate the
revealed El Gamal ciphertexts per proposal option. Validators holding
Shamir shares of the election authority key cooperate to produce partial
decryptions; the results are combined via Lagrange interpolation and
the aggregate total is publicly verified. Individual vote amounts are
never revealed.


# Motivation

Stake-weighted voting in privacy-preserving systems faces a fundamental
tension: demonstrating voting power requires proving a balance, but
linking that balance to a vote destroys the privacy that shielded
transactions provide.

This ZIP addresses that tension for Zcash's Orchard shielded pool. The
Orchard Proof-of-Balance [^balance-proof] provides the foundational
primitive, proving note ownership without revealing standard nullifiers.
This ZIP builds on that primitive to specify a complete voting protocol
with the following properties:

- **Unlinkable delegation.** A holder delegates voting power to a
  locally-generated hotkey via a zero-knowledge proof. The delegation
  is unlinkable to the holder's on-chain identity.
- **Private vote splitting.** Votes are decomposed into El Gamal-
  encrypted shares submitted independently, preventing balance
  reconstruction via timing or amount analysis.
- **Homomorphic tallying.** Encrypted shares are accumulated on-chain
  via component-wise point addition. Only the aggregate total per
  proposal option is ever decrypted.

The protocol is motivated by coinholder governance in the Zcash
ecosystem, where participants vote on proposals weighted by their ZEC
holdings. The same mechanism applies to any stake-weighted polling system
over an Orchard-like shielded pool.


# Privacy Implications

**Unlinkability to on-chain identity.** The delegation phase moves
voting authority from the holder's Orchard spending key to an unlinkable
governance hotkey. All subsequent voting transactions use this hotkey.
An observer who sees both the governance nullifiers (published during
delegation) and the standard nullifiers (published when notes are later
spent on-chain) cannot link them without knowledge of $\mathsf{nk}$.
This follows from the alternate nullifier unlinkability property
established in [^balance-proof].

**Balance hiding via vote splitting.** A voter's total ballot count is
decomposed into $N_s$ shares encrypted under the election authority's
public key. Each share is submitted independently (potentially via
different submission servers at randomized delays), preventing an
observer from reconstructing the voter's total weight from individual
submissions.

**Individual vote amounts hidden.** Each share is an El Gamal ciphertext
whose plaintext value is never revealed. Only the aggregate total per
(proposal, decision) pair is decrypted at tally time.

**Vote commitment unlinkability.** The Vote Reveal Proof proves
that a revealed share belongs to some valid Vote Commitment in the VCT
without revealing which one. Blinded per-share commitments prevent
observers from recomputing $\mathsf{shares}\_\mathsf{hash}$ from on-chain
ciphertexts and linking revealed shares back to a specific VC.

**Trust assumptions.** After the key ceremony, no single party holds
$\mathsf{ea}\_\mathsf{sk}$; each validator holds only a Shamir share. An
adversary must compromise at least $t$ validators (where
$t = \lceil n/2 \rceil + 1$) to reconstruct the key and decrypt
individual share ciphertexts. Even with access to the full key, privacy
against the EA relies on vote splitting: the EA would see encrypted
shares but cannot link them to specific voters or vote commitments.
Submission servers learn the encrypted share ciphertext, blind factor,
and blinded share commitments for each share they submit, along with
the proposal identifier and vote decision, but cannot decrypt plaintext
amounts or link shares to voter identities. The
primary trust requirement on submission servers is not leaking timing
metadata; using multiple independent servers with randomized delays for submission mitigates this risk.

**Non-membership tree queries.** Obtaining exclusion proofs for the
nullifier non-membership tree during delegation requires querying a data
source. Private information retrieval mitigates this leakage;
see [^pir-governance].


# Requirements

- A holder's on-chain identity (spending key, standard nullifiers) is
  not linkable to their voting activity.
- Double-delegation of the same Orchard note within a voting round is
  detectable via deterministic governance nullifiers.
- Double-voting with the same Vote Authority Note is detectable via
  deterministic VAN nullifiers.
- Double-counting of the same vote share is detectable via deterministic
  share nullifiers.
- Individual vote amounts are not revealed at any point; only aggregate
  totals per (proposal, decision) pair are recoverable.
- The aggregate tally is publicly verifiable: any party can confirm the
  homomorphic accumulation.
- The protocol supports up to 15 proposals per voting round.
- The Vote Commitment Tree has capacity for at least several million
  leaves (combined VANs and VCs) per voting round.
- The protocol supports delegation of voting authority to a third-party
  hotkey.
- The delegation phase is compatible with hardware wallets that support
  only the standard Orchard PCZT [^pczt] signing flow, without
  requiring firmware changes specific to the voting protocol.


# Non-requirements

- The consensus mechanism and operational parameters of the vote chain
  are out of scope for this ZIP.
- The election authority key ceremony (generation, threshold sharing,
  and distribution of $\mathsf{ea}\_\mathsf{sk}$ shares) is specified separately
  in [^ea-ceremony].
- The operational process for conducting a coinholder vote (validator
  setup, poll creation, deadlines) is out of scope; it is expected to
  be specified in a separate ZIP.
- Distributed key generation of the election authority's El Gamal keypair
  among validators (producing $\mathsf{ea}\_\mathsf{pk}$ without any single
  party constructing $\mathsf{ea}\_\mathsf{sk}$) is out of scope; the current
  design uses a trusted dealer.
- Post-quantum security of the El Gamal encryption layer is out of
  scope.
- Privacy-preserving retrieval of nullifier non-membership proofs is
  specified separately in [^pir-governance].


# Specification

## Protocol Overview

The protocol proceeds in five phases within a voting round.

**Phase 1: Delegation.** A holder proves ownership of unspent Orchard
notes at a pool snapshot (using the Claim circuit from [^balance-proof])
and delegates voting authority to a locally-generated governance hotkey.
The delegation produces a Vote Authority Note (VAN) that is inserted
into the Vote Commitment Tree on the vote chain. Governance nullifiers
are published to prevent double-delegation.

**Phase 2: Voting.** The governance hotkey consumes a VAN by publishing
its VAN nullifier, and produces two new VCT leaves: a replacement VAN
with the voted proposal's authority bit cleared, and a Vote Commitment
containing $N_s$ El Gamal-encrypted shares of the voter's ballot count.

**Phase 3: Share submission.** The voter sends each encrypted share as
an independent payload to one or more submission servers. Each payload
contains the data necessary for the server to construct a Vote Reveal
Proof.

**Phase 4: Share reveal.** Each submission server constructs a Vote
Reveal Proof (proving the share belongs to a valid VC in the VCT without
revealing which one) and submits it to the vote chain at a randomized
delay. The chain accumulates the revealed El Gamal ciphertexts
homomorphically.

**Phase 5: Tally.** After the voting window closes, at least $t$
validators produce partial decryptions of the aggregate ciphertext per
(proposal, decision) pair. The partial decryptions are stored on-chain and combined via
Lagrange interpolation to recover the total ballot count (via bounded
discrete-log search). Correctness is publicly verifiable: anyone can
recompute the Lagrange combination from the on-chain partial
decryptions.


## El Gamal Encryption on Pallas

The protocol uses additively homomorphic El Gamal encryption [^elgamal]
over the Pallas curve [^protocol-pallasandvesta] to encrypt vote share
amounts.

Let $G$ be the Pallas $\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$
generator [^protocol-concretespendauthsig] and let
$\mathsf{ea}\_\mathsf{pk} = [\mathsf{ea}\_\mathsf{sk}]\, G$ be the election authority's
public key for the current voting round.

To encrypt a ballot count $v$ with randomness $r$:

$$\mathsf{Enc}(v, r) = \bigl([r]\, G, [v]\, G + [r]\, \mathsf{ea}\_\mathsf{pk}\bigr)$$

The ciphertext is a pair of Pallas points $(C_1, C_2)$.

**Homomorphic property.** Given ciphertexts $\mathsf{Enc}(a, r_1)$ and
$\mathsf{Enc}(b, r_2)$, component-wise point addition yields a valid
encryption of $a + b$:

$$\mathsf{Enc}(a, r_1) + \mathsf{Enc}(b, r_2) = \mathsf{Enc}(a + b, r_1 + r_2)$$

**Decryption.** Given ciphertext $(C_1, C_2)$ and secret key
$\mathsf{ea}\_\mathsf{sk}$:

$$C_2 - [\mathsf{ea}\_\mathsf{sk}]\, C_1 = [v]\, G$$

The discrete logarithm $v$ is recovered via baby-step giant-step
[^bsgs], which is feasible because ballot counts are bounded (the total
ZEC supply yields at most $\approx 1.68 \times 10^8$ ballots).


## Data Structures

### Vote Authority Note (VAN)

A VAN represents spendable voting authority on the vote chain. Its
commitment is computed in two layers:

$$\mathsf{van}\_\mathsf{core} = \mathsf{Poseidon}\bigl(\mathsf{DOMAIN}\_\mathsf{VAN}, \mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}, \mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}}, \mathsf{num}\_\mathsf{ballots}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{proposal}\_\mathsf{authority}\bigr)$$

$$\mathsf{van} = \mathsf{Poseidon}\bigl(\mathsf{van}\_\mathsf{core}, \mathsf{gov}\_{\mathsf{comm}\_\mathsf{rand}}\bigr)$$

The first layer binds the structural fields; the second layer blinds
the commitment with randomness. These are two separate Poseidon
invocations ($\mathsf{ConstantLength}\langle 6 \rangle$ then
$\mathsf{ConstantLength}\langle 2 \rangle$), not a single 7-input
sponge absorption.

where:

- $\mathsf{DOMAIN}\_\mathsf{VAN} = 0$ — domain tag distinguishing VANs from VCs
  in the shared VCT.
- $\mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}} \in \mathbb{P}^*$ — diversified base of the
  governance hotkey address.
- $\mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}} \in \mathbb{P}^*$ — diversified transmission
  key of the governance hotkey address.
- $\mathsf{num}\_\mathsf{ballots} \in \{1 \ldots 2^{30}\}$ — total voting
  weight in ballots.
- $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}} \in \{ 0 .. q_{\mathbb{P}}-1 \}$ — scopes this VAN to a specific voting round.
- $\mathsf{proposal}\_\mathsf{authority} \in \{0 \ldots 2^{16}-1\}$ — bitmask
  encoding which proposals this VAN is authorized to vote on.
  $\mathsf{proposal}\_\mathsf{id}$ values 1–15 map to bits 1–15; bit 0 is
  reserved (see [Why Proposal Identifiers Start at 1]). Full authority
  is $2^{16} - 1 = 65535$.
- $\mathsf{gov}\_{\mathsf{comm}\_\mathsf{rand}} \in \{ 0 .. q_{\mathbb{P}}-1 \}$ —
  commitment randomness.

**VAN nullifier.** When a VAN is consumed (to vote or delegate), its
nullifier is:

$$\mathsf{van}\_\mathsf{nullifier} = \mathsf{Poseidon}\bigl(\mathsf{vsk.nk}, \mathsf{tag}_{\mathsf{van}}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{van}\bigr)$$

where $\mathsf{tag}_{\mathsf{van}}$ is the field-element encoding of the domain
separator `"vote authority spend"` and $\mathsf{vsk.nk}$ is the nullifier
deriving key from the governance hotkey's full viewing key.

**Lifecycle.** A VAN is created during delegation (Phase 1) and consumed
during voting (Phase 2), which produces a replacement VAN with updated
$\mathsf{proposal}\_\mathsf{authority}$. The VAN model is designed to
support future extensions such as partial delegation (splitting
$\mathsf{num}\_\mathsf{ballots}$ across multiple delegates), but this
ZIP specifies only the delegation and voting operations.

### Vote Commitment (VC)

A VC commits to a vote on a specific proposal:

$$\mathsf{vc} = \mathsf{Poseidon}\bigl(\mathsf{DOMAIN}\_\mathsf{VC}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{shares}\_\mathsf{hash}, \mathsf{proposal}\_\mathsf{id}, \mathsf{vote}\_\mathsf{decision}\bigr)$$

where:

- $\mathsf{DOMAIN}\_\mathsf{VC} = 1$ — domain tag.
- $\mathsf{shares}\_\mathsf{hash} \in \{ 0 .. q_{\mathbb{P}}-1 \}$ — a hash
  over blinded commitments to all $N_s$ encrypted shares (see
  [Shares Hash]).
- $\mathsf{proposal}\_\mathsf{id} \in \{1 \ldots 15\}$ — which proposal this
  vote targets.
- $\mathsf{vote}\_\mathsf{decision} \in \{ 0 .. q_{\mathbb{P}}-1 \}$ — the
  voter's choice (0-indexed into the proposal's declared options).

A VC is created during voting (Phase 2) and opened during share reveal
(Phase 4/5). The VC hash is posted on-chain as a public input of the
Vote Proof and inserted into the VCT, but its preimage fields
($\mathsf{shares}\_\mathsf{hash}$ and $\mathsf{vote}\_\mathsf{decision}$)
are private witnesses in that proof. During share reveal, the Vote
Reveal Proof proves membership in the VCT without exposing which VC is
being opened.

### Vote Share

A vote share is one of $N_s = 16$ encrypted portions of a voter's ballot
count within a VC. The value 16 is chosen as a sufficiently high number
to ensure amount privacy through share decomposition.

For share index $i \in \{0 \ldots N_s - 1\}$:

- $\mathsf{v}\_\mathsf{i} \in \{0 \ldots 2^{30} - 1\}$ — plaintext share
  amount in ballots (private, never revealed).
- $r_i$ — El Gamal encryption randomness (Pallas scalar, private).
- $\mathsf{blind}\_\mathsf{i} \in \{ 0 .. q_{\mathbb{P}}-1 \}$ — per-share
  blind factor for the blinded share commitment (independent of $r_i$).
- $\mathsf{enc}\_{\mathsf{share}\_\mathsf{i}} = \mathsf{Enc}(\mathsf{v}\_\mathsf{i}, r_i) = (C_{1,i}, C_{2,i})$
  — El Gamal ciphertext.

**Blinded share commitment:**

$$\mathsf{share}\_{\mathsf{comm}\_\mathsf{i}} = \mathsf{Poseidon}(\mathsf{blind}\_\mathsf{i}, C_{1,i,x}, C_{2,i,x})$$

where $C_{1,i,x}$ and $C_{2,i,x}$ denote the $x$-coordinates of the
ciphertext points.

### Shares Hash

The shares hash aggregates all $N_s$ blinded share commitments:

$$\mathsf{shares}\_\mathsf{hash} = \mathsf{Poseidon}(\mathsf{share}\_{\mathsf{comm}\_\mathsf{0}}, \mathsf{share}\_{\mathsf{comm}\_\mathsf{1}}, \ldots, \mathsf{share}\_{\mathsf{comm}_{N_s - 1}})$$

This is an $N_s$-input Poseidon sponge hash.

### Share Nullifier

When a share is revealed, its nullifier is:

$$\mathsf{share}\_\mathsf{nullifier} = \mathsf{Poseidon}\bigl(\mathsf{tag}_{\mathsf{share}}, \mathsf{vc}, \mathsf{share}\_\mathsf{index}, \mathsf{blind}\bigr)$$

where $\mathsf{tag}_{\mathsf{share}}$ is the field-element encoding of
`"share spend"`, $\mathsf{vc}$ is the vote commitment (private), and
$\mathsf{blind}$ is the blind factor for the revealed share.

### Vote Commitment Tree

The VCT is an incremental Merkle tree [^protocol-merkletree] of depth
$\mathsf{MerkleDepth}^{\mathsf{vct}} = 24$ that stores both VANs and VCs as leaves.
It uses the same append-only data structure as the Orchard note
commitment tree, but with Poseidon [^poseidon] over the Pallas
scalar field for internal node hashing instead of Sinsemilla,
using the same instantiation as the nullifier non-membership
tree [^balance-proof].

Domain separation between VANs and VCs is achieved structurally: the
first Poseidon input is $\mathsf{DOMAIN}\_\mathsf{VAN} = 0$ for VANs and
$\mathsf{DOMAIN}\_\mathsf{VC} = 1$ for VCs, making it impossible for a valid VAN
preimage to produce the same hash as a valid VC preimage.

Leaves are inserted in transaction order: a delegation transaction
inserts one VAN; a vote transaction inserts both a new VAN and a VC.

### Nullifier Sets

The vote chain maintains three disjoint nullifier sets:

1. **Governance nullifiers**: prevent double-delegation of mainchain
   Orchard notes within a voting round.
2. **VAN nullifiers**: prevent double-spending of voting authority.
3. **Share nullifiers**: prevent double-counting of revealed shares.

Each set is append-only within a voting round. The vote chain rejects
any transaction that publishes a nullifier already present in the
corresponding set.

### Domain Separator Tags

Several constructions in this protocol use a domain separator tag
encoded as a Pallas scalar. Each tag is defined by a fixed ASCII
string. To convert a tag string to a field element, interpret its
byte representation as an unsigned little-endian integer:

$$\mathsf{tag} = \sum_{j=0}^{\ell-1} b_j \cdot 256^j$$

where $b_0, \ldots, b_{\ell-1}$ are the ASCII byte values of the string
and $\ell$ is its length. All tag strings in this protocol are shorter
than 32 bytes, so the resulting integer is less than $2^{256}$ and fits
in $\mathbb{F}_{q_{\mathbb{P}}}$ without reduction.

The protocol defines three tags:

| Tag constant | String | Length |
|---|---|---|
| $\mathsf{tag}\_{\mathsf{gov}}$ | `"governance authorization"` | 24 bytes |
| $\mathsf{tag}\_{\mathsf{van}}$ | `"vote authority spend"` | 20 bytes |
| $\mathsf{tag}\_{\mathsf{share}}$ | `"share spend"` | 11 bytes |


## Governance Hotkey

The governance hotkey is a separate Orchard key hierarchy generated on
a general-purpose device (e.g., a mobile phone). It is distinct from
the holder's Orchard spending key, which may reside on a hardware
wallet. The hotkey provides the key material for all voting operations
after delegation.

A governance hotkey consists of:

- A fresh spend-authorizing key $\mathsf{vsk}$, from which
  $\mathsf{vsk.ak} = [\mathsf{vsk}]\, G$ is derived.
- A nullifier deriving key $\mathsf{vsk.nk}$, derived from the hotkey's
  spending key via the standard Orchard key hierarchy.
- A CommitIvk trapdoor $\mathsf{rivk}\_\mathsf{v}$, derived from the
  hotkey's spending key.
- A diversified address
  $(\mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}, \mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}})$
  at a chosen diversifier index, where
  $\mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}} = [\mathsf{ivk}\_\mathsf{v}]\, \mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}$
  and $\mathsf{ivk}\_\mathsf{v} = \mathsf{CommitIvk}\_{\mathsf{rivk}\_\mathsf{v}}\!\bigl(\mathsf{Extract}\_{\mathbb{P}}(\mathsf{vsk.ak}),\; \mathsf{vsk.nk}\bigr)$.

The Delegation Proof does not constrain the hotkey address to match the
holder's key; the output address is bound to the delegation
transitively through the VAN commitment and the rho binding (see
[Delegation Proof]), which the holder's hardware wallet authenticates
via the spend authorization signature.

The hotkey MAY be generated deterministically from a seed (e.g., via
Blake2b with a voting-specific personalization) or sampled randomly.
The generation method is an application concern; the protocol requires
only that the resulting key material satisfies the standard Orchard
key relationships above.


## Ballot Scaling

Orchard note values are denominated in zatoshi. To reduce the bit-width
of values flowing through El Gamal encryption and downstream range
checks, the protocol converts zatoshi to ballots:

$$\mathsf{num}\_\mathsf{ballots} = \left\lfloor \frac{\sum v_i}{12{,}500{,}000} \right\rfloor$$

where $v_i$ are the values of the delegated Orchard notes. One ballot
equals 0.125 ZEC.

This conversion is enforced in the Delegation Proof circuit. The prover
witnesses $\mathsf{num}\_\mathsf{ballots}$ and a remainder $r$, and the circuit
constrains:

1. $\mathsf{num}\_\mathsf{ballots} \times 12{,}500{,}000 + r = \sum v_i$
2. $0 \leq r < 2^{24}$
3. $\mathsf{num}\_\mathsf{ballots} \geq 1$ and $\mathsf{num}\_\mathsf{ballots} \leq 2^{30}$

The 30-bit upper bound on $\mathsf{num}\_\mathsf{ballots}$ accommodates up to
$\approx 134$ million ZEC, well above the 21 million ZEC supply cap.
The minimum of 1 ballot prevents dust delegations (holdings below
0.125 ZEC) from producing voting authority.

<details>
<summary>

### Rationale for remainder range
</summary>

The remainder is range-checked to 24 bits ($< 16{,}777{,}216$), which
is wider than the divisor ($12{,}500{,}000$). A prover can set
$r > 12{,}500{,}000$, effectively shorting themselves one ballot. This
is harmless: $\mathsf{num}\_\mathsf{ballots}$ does not appear in any governance
nullifier, so the only effect is the prover voting with slightly less
weight than they could. The wider check avoids a custom non-power-of-two
range check in circuit.
</details>


## Delegation Phase

### Delegation Proof

The Delegation Proof establishes that a holder owns unspent Orchard
notes at a pool snapshot and converts the proven balance into a VAN on
the vote chain.

The per-note ownership checks (note commitment integrity, Merkle path
validity, nullifier derivation, diversified address integrity, and
nullifier non-membership) are identical to those in the Batched Claim
circuit defined in [^balance-proof]. This section specifies only the
conditions that extend beyond the Balance Proof.

#### Public Inputs

Given a primary input:

- $\mathsf{signed}\_{\mathsf{note}\_\mathsf{nullifier}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ —
  nullifier of the dummy signed note (for spend authorization binding).
- $\mathsf{rk} ⦂ \mathsf{SpendAuthSig}^{\mathsf{Orchard}}\mathsf{.Public}$ —
  randomized spend authorization verification key.
- $\mathsf{rt}^{\mathsf{cm}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — Orchard note
  commitment tree root at the snapshot height.
- $\mathsf{rt}^{\mathsf{excl}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — nullifier
  non-membership tree root at the snapshot height.
- $\mathsf{van} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — the initial VAN
  commitment.
- $\mathsf{gov}\_{\mathsf{null}\_\mathsf{1}}, \ldots, \mathsf{gov}\_{\mathsf{null}\_\mathsf{5}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ —
  governance nullifiers for each note slot.
- $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$
- $\mathsf{cmx}\_\mathsf{new} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — output note
  commitment (to the governance hotkey address).

#### Auxiliary Inputs

The prover knows, in addition to the per-note witnesses defined
in [^balance-proof]:

- $\mathsf{vpk} = (\mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}, \mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}})$ —
  governance hotkey diversified address.
- $\mathsf{gov}\_{\mathsf{comm}\_\mathsf{rand}}$ — VAN commitment randomness.
- Signed note data: $\mathsf{g}\_\mathsf{d}^{\mathsf{signed}}, \mathsf{pk}\_\mathsf{d}^{\mathsf{signed}},
  \text{ρ}^{\mathsf{signed}}, \text{ψ}^{\mathsf{signed}},
  \mathsf{rcm}^{\mathsf{signed}}, \mathsf{cm}^{\mathsf{signed}}$ (value = 0).
- Output note data: $\mathsf{g}\_\mathsf{d}^{\mathsf{new}}, \mathsf{pk}\_\mathsf{d}^{\mathsf{new}},
  \mathsf{v}^{\mathsf{new}}, \text{ρ}^{\mathsf{new}},
  \text{ψ}^{\mathsf{new}}, \mathsf{rcm}^{\mathsf{new}}$ (address = hotkey).

#### Conditions

**Per-note conditions (5 note slots, with padding).** For each note
$i \in \{1 \ldots 5\}$, the following conditions from the Batched Claim
circuit [^balance-proof] apply:

- Note commitment integrity.
- Merkle path validity in $\mathsf{rt}^{\mathsf{cm}}$ (skipped for padded
  notes).
- Diversified address integrity (same $\mathsf{ivk}$ owns all notes).
- Standard nullifier derivation (kept private).
- Nullifier non-membership in $\mathsf{rt}^{\mathsf{excl}}$ (skipped for padded
  notes).
- Padded notes have value 0.

**Governance nullifier derivation.** For each real note $i$:

$$\mathsf{gov}\_{\mathsf{null}\_\mathsf{i}} = \mathsf{Poseidon}\bigl(\mathsf{nk}, \mathsf{tag}_{\mathsf{gov}}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{nf}^{\mathsf{old}}_i\bigr)$$

where $\mathsf{tag}_{\mathsf{gov}}$ is the field-element encoding of
"governance authorization" and $\mathsf{nf}^{\mathsf{old}}_i$ is the note's
standard nullifier (computed in-circuit but never revealed). This is an
instantiation of the alternate nullifier derivation defined
in [^balance-proof], with $\mathsf{tag} = \mathsf{tag}_{\mathsf{gov}}$ and
$\mathsf{dom} = \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$.

**Signed note integrity.** The signed note is a dummy note with value 0.
Its note commitment $\mathsf{cm}^{\mathsf{signed}}$ is correctly constructed, and
$\mathsf{signed}\_{\mathsf{note}\_\mathsf{nullifier}}$ is correctly derived from it.

**Rho binding.** The signed note's $\text{ρ}^{\mathsf{signed}}$ is
deterministically bound to the delegation context:

$$\text{ρ}^{\mathsf{signed}} = \mathsf{Poseidon}\bigl(\mathsf{cmx}\_\mathsf{1}, \mathsf{cmx}\_\mathsf{2}, \mathsf{cmx}\_\mathsf{3}, \mathsf{cmx}\_\mathsf{4}, \mathsf{cmx}\_\mathsf{5}, \mathsf{van}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}\bigr)$$

This makes the spend authorization signature non-replayable and scoped
to the exact delegation context.

**Spend authority.** $\mathsf{rk} = \mathsf{SpendAuthSig}^{\mathsf{Orchard}}\mathsf{.RandomizePublic}(\alpha, \mathsf{ak}^{\mathbb{P}})$.

**Diversified address integrity for signed note.** The signed note's
address belongs to $(\mathsf{ak}, \mathsf{nk})$.

**Output note commitment.** $\mathsf{cmx}\_\mathsf{new}$ is a correctly
constructed note commitment to an output note addressed to the
governance hotkey.

**VAN integrity.** The public VAN commitment matches the claimed
governance hotkey, ballot count, round, and full proposal authority
(using the two-layer construction defined in [Vote Authority Note
(VAN)]):

$$\mathsf{van}\_\mathsf{core} = \mathsf{Poseidon}\bigl(\mathsf{DOMAIN}\_\mathsf{VAN}, \mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}, \mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}}, \mathsf{num}\_\mathsf{ballots}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{MAX}\_{\mathsf{PROPOSAL}\_\mathsf{AUTHORITY}}\bigr)$$

$$\mathsf{van} = \mathsf{Poseidon}\bigl(\mathsf{van}\_\mathsf{core}, \mathsf{gov}\_{\mathsf{comm}\_\mathsf{rand}}\bigr)$$

where $\mathsf{MAX}\_{\mathsf{PROPOSAL}\_\mathsf{AUTHORITY}} = 2^{16} - 1$.

**Ballot scaling.** $\mathsf{num}\_\mathsf{ballots} = \lfloor \sum v_i / 12{,}500{,}000 \rfloor$,
with $\mathsf{num}\_\mathsf{ballots} \geq 1$, as defined in [Ballot Scaling].

#### Out-of-Circuit Verification

A verifier that receives a Delegation Proof $\pi$ together with a spend
authorization signature $\sigma$ MUST perform the following checks:

1. Verify $\pi$ against the public inputs.
2. Verify $\sigma$ as a valid $\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$
   signature on the application-defined sighash, under $\mathsf{rk}$.
3. Verify that $\mathsf{rt}^{\mathsf{cm}}$ and $\mathsf{rt}^{\mathsf{excl}}$ correspond
   to the published pool snapshot for $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$.
4. Verify that no $\mathsf{gov}\_{\mathsf{null}\_\mathsf{i}}$ appears in the governance
   nullifier set. If any does, reject as a double-delegation.
5. Verify that $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$ matches an active round.
6. Insert $\mathsf{van}$ into the VCT.
7. Add all $\mathsf{gov}\_{\mathsf{null}\_\mathsf{i}}$ to the governance nullifier set.

### Delegation Message

A delegation transaction submitted to the vote chain MUST contain:

| Field | Type | Description |
|---|---|---|
| $\pi\_\mathsf{del}$ | Proof | The Delegation Proof |
| $\sigma\_\mathsf{del}$ | Signature | SpendAuthSig under $\mathsf{rk}$ |
| $\mathsf{signed}\_{\mathsf{note}\_\mathsf{nullifier}}$ | Pallas scalar | Dummy note nullifier |
| $\mathsf{rk}$ | Pallas point | Randomized verification key |
| $\mathsf{rt}^{\mathsf{cm}}$ | Pallas scalar | Note commitment tree root |
| $\mathsf{rt}^{\mathsf{excl}}$ | Pallas scalar | Non-membership tree root |
| $\mathsf{van}$ | Pallas scalar | VAN commitment |
| $\mathsf{gov}\_{\mathsf{null}\_1} \ldots \mathsf{gov}\_{\mathsf{null}\_5}$ | Pallas scalar each | Governance nullifiers |
| $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$ | Pallas scalar | Round identifier |
| $\mathsf{cmx}\_\mathsf{new}$ | Pallas scalar | Output note commitment |


## Vote Phase

### Vote Proof

The Vote Proof demonstrates that a holder of a valid VAN is casting a
vote: consuming the old VAN, producing a new VAN with decremented
proposal authority, and constructing a Vote Commitment that binds $N_s$
El Gamal-encrypted shares to the chosen proposal and decision.

#### Public Inputs

Given a primary input:

- $\mathsf{van}\_\mathsf{nullifier} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ —
  nullifier of the old VAN (prevents double-voting).
- $\mathsf{r}\_\mathsf{vpk} ⦂ \mathsf{SpendAuthSig}^{\mathsf{Orchard}}\mathsf{.Public}$ —
  randomized voting public key.
- $\mathsf{van}\_{\mathsf{new}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — the new VAN
  commitment with decremented proposal authority.
- $\mathsf{vc} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — the vote commitment.
- $\mathsf{rt}^{\mathsf{vct}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — root of the
  Vote Commitment Tree.
- $\mathsf{anchor}\_\mathsf{height} ⦂ \mathbb{N}$ — VCT snapshot height.
- $\mathsf{proposal}\_\mathsf{id} ⦂ \{1 \ldots 15\}$ — which proposal.
- $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$
- $\mathsf{ea}\_\mathsf{pk} ⦂ \mathbb{P}^*$ — election authority public key
  (x and y coordinates).

#### Auxiliary Inputs

The prover knows:

- $\mathsf{vote}\_\mathsf{decision} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — the voter's choice.
- $\mathsf{vsk.ak} ⦂ \mathbb{P}^*$ — voting spend authorization
  validating key.
- $\mathsf{vsk.nk} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — nullifier
  deriving key from the governance hotkey's full viewing key.
- $\mathsf{rivk}\_\mathsf{v} ⦂ \mathsf{Commit}^{\mathsf{ivk}}\mathsf{.Trapdoor}$ —
  CommitIvk randomness for the voting key.
- $\alpha_v$ — spend authorization randomizer for the voting hotkey.
- $\mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}} ⦂ \mathbb{P}^*$ — diversified base from the
  VAN.
- $\mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}} ⦂ \mathbb{P}^*$ — diversified transmission
  key from the VAN.
- $\mathsf{num}\_\mathsf{ballots}$ — total voting weight in ballots.
- $\mathsf{proposal}\_{\mathsf{authority}\_\mathsf{old}}$,
  $\mathsf{proposal}\_{\mathsf{authority}\_\mathsf{new}}$ — old and new bitmasks.
- $\mathsf{gov}\_{\mathsf{comm}\_\mathsf{rand}}$ — VAN commitment randomness (shared
  between old and new VAN).
- $\mathsf{path}^{\mathsf{vct}}, \mathsf{pos}^{\mathsf{vct}}$ — Merkle proof for the
  old VAN in the VCT.
- $\mathsf{van}_{\mathsf{old}}$ — old VAN commitment.
- $\mathsf{v}\_\mathsf{0}, \ldots, \mathsf{v}_{N_s - 1}$ — plaintext share values.
- $r_0, \ldots, r_{N_s - 1}$ — El Gamal encryption randomness per share.
- $\mathsf{blind}\_\mathsf{0}, \ldots, \mathsf{blind}_{N_s - 1}$ — per-share blind
  factors.

#### Conditions

##### VAN Ownership and Spending

**Condition 1: Merkle tree membership.** The old VAN exists in the VCT:
$(\mathsf{path}^{\mathsf{vct}}, \mathsf{pos}^{\mathsf{vct}})$ is a valid Merkle path of
depth $\mathsf{MerkleDepth}^{\mathsf{vct}}$ from $\mathsf{van}_{\mathsf{old}}$ to the
anchor $\mathsf{rt}^{\mathsf{vct}}$, using Poseidon for internal node hashing.

**Condition 2: Old VAN integrity.** The old VAN commitment matches the
claimed fields (using the two-layer construction defined in
[Vote Authority Note (VAN)]):

$$\mathsf{van}\_{\mathsf{core}\_\mathsf{old}} = \mathsf{Poseidon}\bigl(\mathsf{DOMAIN}\_\mathsf{VAN}, \mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}, \mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}}, \mathsf{num}\_\mathsf{ballots}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{proposal}\_{\mathsf{authority}\_\mathsf{old}}\bigr)$$

$$\mathsf{van}\_\mathsf{old} = \mathsf{Poseidon}\bigl(\mathsf{van}\_{\mathsf{core}\_\mathsf{old}}, \mathsf{gov}\_{\mathsf{comm}\_\mathsf{rand}}\bigr)$$

**Condition 3: Diversified address integrity.** The VAN's address
belongs to the voting key:

$$\mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}} = [\mathsf{ivk}\_\mathsf{v}]\, \mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}$$

where $\mathsf{ivk}\_\mathsf{v} = \mathsf{CommitIvk}_{\mathsf{rivk}\_\mathsf{v}}\!\bigl(\mathsf{Extract}_{\mathbb{P}}(\mathsf{vsk.ak}),\; \mathsf{vsk.nk}\bigr)$ [^protocol-concretecommitivk].

**Condition 4: Spend authority.** The randomized voting public key is
a valid rerandomization:

$$\mathsf{r}\_\mathsf{vpk} = \mathsf{vsk.ak} + [\alpha_v]\, G$$

**Condition 5: VAN nullifier.** The public $\mathsf{van}\_\mathsf{nullifier}$
is correctly derived:

$$\mathsf{van}\_\mathsf{nullifier} = \mathsf{Poseidon}\bigl(\mathsf{vsk.nk}, \mathsf{tag}_{\mathsf{van}}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{van}_{\mathsf{old}}\bigr)$$

where $\mathsf{tag}_{\mathsf{van}}$ is the field-element encoding of
`"vote authority spend"`.

<details>
<summary>

### Rationale for VAN nullifier domain separation
</summary>

The VAN nullifier uses $\mathsf{vsk.nk}$ (the governance hotkey's
nullifier deriving key) as the Poseidon key, while the governance
nullifier uses $\mathsf{nk}$ (the holder's nullifier deriving key).
When the hotkey is a separate key from the holder's, these are distinct
field elements, and cross-circuit collision resistance follows from the
key difference alone. When the hotkey reuses the holder's key hierarchy
(e.g., in an all-software flow without hardware wallet separation),
$\mathsf{vsk.nk} = \mathsf{nk}$ and collision resistance relies on
the domain tags being distinct: `"vote authority spend"` and
`"governance authorization"` differ in both byte length and content,
producing distinct field elements. The domain tags provide
defense-in-depth in both cases.
</details>

##### New VAN Construction

**Condition 6: Proposal authority decrement.** Bit
$\mathsf{proposal}\_\mathsf{id}$ is cleared in the authority bitmask:

- $\mathsf{proposal}\_{\mathsf{authority}\_\mathsf{old}}$ is decomposed into 16 boolean
  wires $b_0, \ldots, b_{15}$ that recompose to the original value.
- The bit at position $\mathsf{proposal}\_\mathsf{id}$ is asserted to be 1
  (the voter has authority for this proposal).
- $\mathsf{proposal}\_{\mathsf{authority}\_\mathsf{new}}$ is the recomposition with bit
  $\mathsf{proposal}\_\mathsf{id}$ cleared; all other bits are unchanged.

**Condition 7: New VAN integrity.** The new VAN is correctly
constructed (using the two-layer construction defined in
[Vote Authority Note (VAN)]):

$$\mathsf{van}\_{\mathsf{core}\_\mathsf{new}} = \mathsf{Poseidon}\bigl(\mathsf{DOMAIN}\_\mathsf{VAN}, \mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}, \mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}}, \mathsf{num}\_\mathsf{ballots}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{proposal}\_{\mathsf{authority}\_\mathsf{new}}\bigr)$$

$$\mathsf{van}\_\mathsf{new} = \mathsf{Poseidon}\bigl(\mathsf{van}\_{\mathsf{core}\_\mathsf{new}}, \mathsf{gov}\_{\mathsf{comm}\_\mathsf{rand}}\bigr)$$

The new VAN reuses the old VAN's diversified address and commitment
randomness; only $\mathsf{proposal}\_\mathsf{authority}$ changes.

##### Vote Commitment Construction

**Condition 8: Shares sum correctness.**

$$\sum_{i=0}^{N_s - 1} \mathsf{v}\_\mathsf{i} = \mathsf{num}\_\mathsf{ballots}$$

**Condition 9: Shares range check.** Each share is bounded:

$$0 \leq \mathsf{v}\_\mathsf{i} < 2^{30} \quad \text{for each } i \in \{0 \ldots N_s - 1\}$$

This bound is critical for two reasons: (1) it ensures the base-field
share sum and the scalar-field El Gamal encoding agree (no modular
reduction in either field), and (2) it keeps the aggregate discrete log
small enough for efficient baby-step giant-step recovery at tally time.

**Condition 10: Shares hash integrity.** The blinded share commitments
and their aggregate hash are correctly computed:

$$\mathsf{share}\_{\mathsf{comm}\_\mathsf{i}} = \mathsf{Poseidon}\bigl(\mathsf{blind}\_\mathsf{i}, C_{1,i,x}, C_{2,i,x}\bigr) \quad \text{for each } i$$

$$\mathsf{shares}\_\mathsf{hash} = \mathsf{Poseidon}\bigl(\mathsf{share}\_{\mathsf{comm}\_\mathsf{0}}, \ldots, \mathsf{share}\_{\mathsf{comm}_{N_s - 1}}\bigr)$$

**Condition 11: El Gamal encryption integrity.** Each ciphertext is a
valid encryption of its share under $\mathsf{ea}\_\mathsf{pk}$:

$$C_{1,i} = [r_i]\, G$$
$$C_{2,i} = [\mathsf{v}\_\mathsf{i}]\, G + [r_i]\, \mathsf{ea}\_\mathsf{pk}$$

The circuit constrains equality on the $x$-coordinates of the computed
and witnessed ciphertext points. Constraining only $x$-coordinates is
sufficient because the shared randomness $r_i$ binds both curve points,
leaving no prover freedom in the $y$-coordinates.

**Condition 12: Vote commitment integrity.** The public vote commitment
matches the private vote details:

$$\mathsf{vc} = \mathsf{Poseidon}\bigl(\mathsf{DOMAIN}\_\mathsf{VC}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{shares}\_\mathsf{hash}, \mathsf{proposal}\_\mathsf{id}, \mathsf{vote}\_\mathsf{decision}\bigr)$$

#### Out-of-Circuit Verification

A verifier that receives a Vote Proof $\pi$ together with a vote
spend authorization signature $\sigma$ MUST perform the following
checks:

1. Verify $\pi$ against the public inputs.
2. Verify $\sigma$ as a valid $\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$
   signature on the application-defined sighash, under
   $\mathsf{r}\_\mathsf{vpk}$.
3. Verify that $\mathsf{van}\_\mathsf{nullifier}$ does not appear in the VAN
   nullifier set. If it does, reject as double-voting.
4. Verify that $\mathsf{rt}^{\mathsf{vct}}$ matches a published VCT root at
   $\mathsf{anchor}\_\mathsf{height}$.
5. Verify that $\mathsf{proposal}\_\mathsf{id}$ is valid for the current round
   and within the voting window.
6. Verify that $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$ matches an active round.
7. Verify that $\mathsf{ea}\_\mathsf{pk}$ matches the published election
   authority public key for this round.
8. Insert $\mathsf{van}_{\mathsf{new}}$ and $\mathsf{vc}$ into the VCT.
9. Add $\mathsf{van}\_\mathsf{nullifier}$ to the VAN nullifier set.

### Vote Message

A vote transaction submitted to the vote chain MUST contain:

| Field | Type | Description |
|---|---|---|
| $\pi_{\text{vote}}$ | Proof | The Vote Proof |
| $\sigma_{\text{vote}}$ | Signature | SpendAuthSig under $\mathsf{r}_{\mathsf{vpk}}$ |
| $\mathsf{van}\_\mathsf{nullifier}$ | Pallas scalar | Old VAN nullifier |
| $\mathsf{r}_{\mathsf{vpk}}$ | Pallas point | Randomized voting public key |
| $\mathsf{van}_{\mathsf{new}}$ | Pallas scalar | New VAN commitment |
| $\mathsf{vc}$ | Pallas scalar | Vote commitment |
| $\mathsf{rt}^{\mathsf{vct}}$ | Pallas scalar | VCT root |
| $\mathsf{anchor}\_\mathsf{height}$ | integer | VCT anchor height |
| $\mathsf{proposal}\_\mathsf{id}$ | $\{1 \ldots 15\}$ | Proposal identifier |
| $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$ | Pallas scalar | Round identifier |
| $\mathsf{ea}_{\mathsf{pk}}$ | Pallas point | EA public key |


## Share Reveal Phase

### Vote Reveal Proof

The Vote Reveal Proof opens a single encrypted share from a Vote
Commitment, revealing the El Gamal ciphertext for homomorphic
accumulation, without revealing the plaintext amount or which Vote
Commitment the share came from. This proof is constructed by the
submission server, not the voter.

#### Public Inputs

Given a primary input:

- $\mathsf{share}\_\mathsf{nullifier} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ —
  prevents double-counting.
- $C_{1,x}, C_{2,x} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — the $x$-coordinates
  of the El Gamal ciphertext $(C_1, C_2)$ for this share. The full
  points are carried in the share reveal message for homomorphic
  accumulation, but only the $x$-coordinates are circuit public inputs.
- $\mathsf{proposal}\_\mathsf{id} ⦂ \{1 \ldots 15\}$ — which proposal.
- $\mathsf{vote}\_\mathsf{decision} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — the voter's choice.
- $\mathsf{rt}^{\mathsf{vct}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — root of the
  Vote Commitment Tree.
- $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$

#### Auxiliary Inputs

The prover (submission server) knows:

- $\mathsf{vc} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$ — the vote commitment
  being opened (hidden from the verifier).
- $\mathsf{path}^{\mathsf{vct}}, \mathsf{pos}^{\mathsf{vct}}$ — Merkle proof for the VC
  in the VCT.
- $\mathsf{shares}\_\mathsf{hash} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$
- $\mathsf{share}\_\mathsf{index} \in \{0, 1, \ldots, N_s - 1\}$ — which share is being revealed.
- $\mathsf{share}\_{\mathsf{comm}\_0} \ldots \mathsf{share}\_{\mathsf{comm}\_{N_s - 1}}$ —
  all $N_s$ blinded share commitments (to recompute
  $\mathsf{shares}\_\mathsf{hash}$).
- $\mathsf{blind}$ — the blind factor for the revealed share
  (at position $\mathsf{share}\_\mathsf{index}$).

#### Conditions

##### Vote Commitment Membership

**Condition 1: Merkle tree membership.** The VC exists in the VCT:
$(\mathsf{path}^{\mathsf{vct}}, \mathsf{pos}^{\mathsf{vct}})$ is a valid Merkle path
from $\mathsf{vc}$ to $\mathsf{rt}^{\mathsf{vct}}$, without revealing which
leaf. The VC value is a private witness.

**Condition 2: Vote commitment integrity.** The VC is correctly
constructed from its components:

$$\mathsf{vc} = \mathsf{Poseidon}\bigl(\mathsf{DOMAIN}\_\mathsf{VC}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}, \mathsf{shares}\_\mathsf{hash}, \mathsf{proposal}\_\mathsf{id}, \mathsf{vote}\_\mathsf{decision}\bigr)$$

This binds the public $\mathsf{proposal}\_\mathsf{id}$ and
$\mathsf{vote}\_\mathsf{decision}$ to the private VC, ensuring that the
revealed share is attributed to the correct proposal and decision.

##### Share Opening

**Condition 3: Shares hash integrity.** The $\mathsf{shares}\_\mathsf{hash}$ is
recomputed from the witness share commitments:

$$\mathsf{shares}\_\mathsf{hash} = \mathsf{Poseidon}\bigl(\mathsf{share}\_{\mathsf{comm}\_\mathsf{0}}, \ldots, \mathsf{share}\_{\mathsf{comm}_{N_s - 1}}\bigr)$$

The recomputed $\mathsf{shares}\_\mathsf{hash}$ is constrained equal to the one
inside the VC (via condition 2). The share commitments are blinded
(see [Why Blinded Share Commitments]), so they do not reveal the
ciphertexts or blind factors of other shares to the prover.

**Condition 4: Share membership.** The commitment derived from the
public $x$-coordinates $C_{1,x}, C_{2,x}$ and the witness blind
factor matches the share commitment at position
$\mathsf{share}\_\mathsf{index}$:

$$\mathsf{Poseidon}\bigl(\mathsf{blind}_{\mathsf{share}\_\mathsf{index}}, C_{1,x}, C_{2,x}\bigr) = \mathsf{share}\_\mathsf{comms}[\mathsf{share}\_\mathsf{index}]$$

The circuit encodes $\mathsf{share}\_\mathsf{index}$ as a one-hot selector
vector over $N_s$ positions. The mux extracts the corresponding
$\mathsf{share}\_\mathsf{comm}$ via a dot product and constrains equality with
the commitment derived from the public ciphertext coordinates and the
witness blind factor. Only the blind factor for the revealed share is
needed; the remaining $N_s - 1$ share commitments used in condition 3
are opaque witnesses that do not expose their underlying ciphertexts
or blind factors.

##### Nullifier

**Condition 5: Share nullifier.** The public
$\mathsf{share}\_\mathsf{nullifier}$ is correctly derived:

$$\mathsf{share}\_\mathsf{nullifier} = \mathsf{Poseidon}\bigl(\mathsf{tag}_{\mathsf{share}}, \mathsf{vc}, \mathsf{share}\_\mathsf{index}, \mathsf{blind}\bigr)$$

where $\mathsf{tag}_{\mathsf{share}}$ is the field-element encoding of
`"share spend"` and $\mathsf{blind}$ is the blind factor for the
revealed share. The VC and blind are private, making the nullifier
unlinkable to a specific VC without knowledge of these witnesses.

#### Out-of-Circuit Verification

A verifier that receives a Vote Reveal Proof $\pi$ MUST perform the
following checks:

1. Verify $\pi$ against the public inputs.
2. Verify that $\mathsf{share}\_\mathsf{nullifier}$ does not appear in the
   share nullifier set. If it does, reject as double-counting.
3. Verify that $\mathsf{rt}^{\mathsf{vct}}$ matches a published VCT root.
4. Verify that $\mathsf{proposal}\_\mathsf{id}$ is valid for the current round.
5. Verify that $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$ matches an active round.
6. Add $\mathsf{share}\_\mathsf{nullifier}$ to the share nullifier set.
7. Accumulate $\mathsf{enc}\_\mathsf{share}$ into the aggregate ciphertext for
   $(\mathsf{proposal}\_\mathsf{id}, \mathsf{vote}\_\mathsf{decision})$:

$$\mathsf{agg}[\mathsf{proposal}\_\mathsf{id}][\mathsf{vote}\_\mathsf{decision}] \mathrel{+}= \mathsf{enc}\_\mathsf{share}$$

where $+$ denotes component-wise Pallas point addition.

### Share Reveal Message

A share reveal transaction submitted to the vote chain MUST contain:

| Field | Type | Description |
|---|---|---|
| $\pi_{\text{reveal}}$ | Proof | The Vote Reveal Proof |
| $\mathsf{share}\_\mathsf{nullifier}$ | Pallas scalar | Share nullifier |
| $\mathsf{enc}\_\mathsf{share}$ | $(C_1, C_2)$ | El Gamal ciphertext (two Pallas points) |
| $\mathsf{proposal}\_\mathsf{id}$ | $\{1 \ldots 15\}$ | Proposal identifier |
| $\mathsf{vote}\_\mathsf{decision}$ | Pallas scalar | Vote decision |
| $\mathsf{rt}^{\mathsf{vct}}$ | Pallas scalar | VCT root |
| $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$ | Pallas scalar | Round identifier |

Note: the Vote Reveal Proof has no spend authorization signature
because it is constructed by the submission server, not the voter.

### Share Submission Payload

The voter sends each share to a submission server as an off-chain
payload. For share $i$, the payload MUST contain:

| Field | Description |
|---|---|
| $\mathsf{vc}$ | The vote commitment |
| VCT position | Position of $\mathsf{vc}$ in the VCT |
| $\mathsf{shares}\_\mathsf{hash}$ | Hash of all blinded share commitments |
| $\mathsf{proposal}\_\mathsf{id}$ | Proposal identifier |
| $\mathsf{vote}\_\mathsf{decision}$ | Vote decision |
| $\mathsf{share}\_\mathsf{index}$ | Which share to reveal (0-indexed) |
| $\mathsf{enc}\_\mathsf{share}$ | El Gamal ciphertext $(C_1, C_2)$ for this share |
| $\mathsf{blind}$ | Blind factor for this share |
| $\mathsf{share}\_{\mathsf{comm}\_0} \ldots \mathsf{share}\_{\mathsf{comm}\_{N_s - 1}}$ | All $N_s$ blinded share commitments |

The server receives only the ciphertext and blind factor for the
single share it is responsible for revealing. The remaining $N_s - 1$
shares are sent to other servers, each of which receives only its own
share's raw data. To recompute $\mathsf{shares}\_\mathsf{hash}$ in
condition 3 of the Vote Reveal Proof, the server uses the blinded
share commitments, which do not expose the ciphertexts or blind
factors of the other shares (see [Why Per-Server Share Isolation]).


## Submission Server

The submission server is an untrusted party that constructs Vote Reveal
Proofs on behalf of voters. Delegating proof construction to a
server provides two benefits:

- **Reliability.** A mobile client may be killed or lose connectivity
  during proof generation. Servers are always-on.
- **Temporal unlinkability.** If a voter submitted all $N_s$ shares
  directly, an observer could link them by timing. Servers stagger
  submissions at randomized delays across the voting window, mixing
  shares from many voters.

For each payload received, the server:

1. Waits a randomized delay.
2. Obtains the current VCT Merkle path for the VC.
3. Derives the share nullifier.
4. Constructs the Vote Reveal Proof.
5. Submits the share reveal transaction to the vote chain.

**What the server learns:** the encrypted share ciphertext and blind
factor for a single share, the blinded share commitments for all $N_s$
shares, the proposal identifier, and the vote decision. **What it
cannot learn:** the plaintext share amount (El Gamal encrypted under
$\mathsf{ea}\_\mathsf{pk}$), the ciphertexts or blind factors of other
shares (hidden behind blinded commitments), the voter's identity (the
VC hides the link), or which VCT leaf the VC corresponds to (the
Merkle path is a private witness in the proof).

Voters MAY distribute shares across multiple independent servers to
further limit any single server's view of their voting activity.
Specification of server selection, communication protocols, and timing
parameters is deferred to the operational voting process ZIP.


## Homomorphic Tally

After the voting window closes, the tally proceeds in three steps.

**Step 1: Public aggregation.** For each
$(\mathsf{proposal}\_\mathsf{id}, \mathsf{vote}\_\mathsf{decision})$ pair, the aggregate
ciphertext is the component-wise sum of all revealed shares attributed
to that pair:

$$\mathsf{agg} = \Bigl(\sum C_{1,j}, \sum C_{2,j}\Bigr)$$

This is publicly computable from on-chain data. Any party can
independently verify the aggregation.

**Step 2: Threshold decryption.** At least $t$ validators each produce
a partial decryption of the aggregate ciphertext using their Shamir
share and post it on-chain. The partial decryptions are combined via
Lagrange interpolation:

$$\sum C_{2,j} - \sum_{i \in S} [\lambda_i]\, D_i = [\mathsf{total}\_\mathsf{ballots}]\, G$$

where $D_i = [s_i]\, \sum C_{1,j}$ is validator $V_i$'s partial
decryption and $\lambda_i$ are the Lagrange coefficients for the
participating set $S$. The value $\mathsf{total}\_\mathsf{ballots}$ is recovered
via baby-step giant-step discrete-log search (feasible because the total
is bounded by ZEC supply). No party reconstructs $\mathsf{ea}\_\mathsf{sk}$
during this process.

**Step 3: Public verification.** The individual partial decryptions
$D_i$ and the aggregate ciphertext are all on-chain. Anyone can
recompute the Lagrange combination for any qualifying subset of $t$
validators and confirm the claimed $\mathsf{total}\_\mathsf{ballots}$.

Individual vote amounts are never revealed; only the aggregate total
per (proposal, decision) pair. The threshold decryption procedure is specified in [^ea-ceremony].


## Election Authority Key

Each voting round uses a fresh election authority keypair
$(\mathsf{ea}\_\mathsf{sk}, \mathsf{ea}\_\mathsf{pk})$ produced by an automated threshold
secret sharing ceremony among the vote chain's validator set. A trusted
dealer generates $\mathsf{ea}\_\mathsf{sk}$, splits it into Shamir
shares [^shamir], distributes the shares to eligible validators via
ECIES [^ecies], and deletes the full key. After the ceremony, no single party
holds $\mathsf{ea}\_\mathsf{sk}$; each validator holds only its share. The round
transitions to active status once a quorum of validators have verified
their shares and acknowledged receipt.

At tally time, at least $t = \lceil n/2 \rceil + 1$ validators
cooperate to produce partial decryptions of the aggregate ciphertext
and post them on-chain. The partial decryptions are combined via
Lagrange interpolation - the full secret key is never reconstructed.

The ceremony protocol, including dealer selection, ECIES share distribution, validator
acknowledgment, confirmation thresholds, timeout and jailing rules, and threshold
decryption procedures, is specified in [^ea-ceremony].


## Vote Chain

The vote chain is a purpose-built chain that records all governance
transactions. It maintains:

- The **Vote Commitment Tree**: an append-only Poseidon Merkle tree
  storing VANs and VCs.
- Three **nullifier sets**: governance, VAN, and share nullifiers.
- An **encrypted share accumulator**: per
  $(\mathsf{proposal}\_\mathsf{id}, \mathsf{vote}\_\mathsf{decision})$, the running
  component-wise sum of revealed El Gamal ciphertexts.

For each transaction type, the chain verifies the corresponding proof,
checks nullifier freshness, updates the VCT, and (for share reveals)
accumulates the ciphertext. All verification is ZKP-based - the chain
never observes plaintext vote amounts or voter identities.

The vote chain's consensus mechanism, block structure, transaction
encoding, and API are out of scope for this ZIP.


# Rationale

## Why a Separate Vote Chain

Voting transactions (delegation proofs, vote proofs, share reveals) are
not standard Zcash shielded transactions. They require a new commitment
tree (the VCT), new nullifier sets, and an encrypted share accumulator
with homomorphic aggregation. Implementing these as a sidechain avoids
modifying the Zcash consensus layer and keeps the governance mechanism
independent of mainchain upgrade cycles.

## Why Poseidon for the VCT

The Orchard note commitment tree uses Sinsemilla [^protocol-concretesinsemilla]
for Merkle hashing. The VCT uses Poseidon instead because all three ZKPs
in this protocol require VCT Merkle membership proofs, and Poseidon
operates natively on field elements, making it significantly more
efficient inside Halo 2 [^halo2] arithmetic circuits than Sinsemilla
(which is optimized for bitstring
inputs). Since the VCT is new infrastructure with no backwards-
compatibility constraint, the more circuit-efficient primitive is
appropriate. This is the same rationale as for the nullifier
non-membership tree in [^balance-proof].

## Why Ballot Scaling

Expressing vote values in ballots ($\lfloor \text{zatoshi} / 12{,}500{,}000 \rfloor$) rather
than raw zatoshi reduces bit-width throughout the protocol: El Gamal
scalar multiplications are faster, range checks are tighter, and the
bounded discrete-log search at tally time has a smaller search space.
The 0.125 ZEC minimum also prevents dust delegations from bloating vote
chain state.

## Why Delegation to a Hotkey

The protocol requires voters to produce Halo 2 zero-knowledge proofs
(delegation proof, vote proof) and construct vote commitments, operations that demand general-purpose computation on private key
material. Hardware wallets that custody Orchard spending keys cannot
perform these operations: they support signature generation but not
arbitrary-circuit ZKP construction.

Delegation to a governance hotkey resolves this by separating spend
authorization from vote execution. The hardware wallet signs a single
$\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$ during delegation, authorizing the
transfer of voting power to a software-controlled hotkey. All subsequent
voting operations (VAN consumption, vote commitment construction, share
submission) use the hotkey's key material and run on a general-purpose
device.

Without this separation, hardware wallet users would need to either
export spending keys to a software environment, negating the security
benefit of hardware custody, or forgo participation in governance
entirely. Delegation preserves the hardware wallet's role as the sole
custodian of spending keys while enabling full participation in the
voting protocol.

## Why a Dummy Signed Note

The Delegation Proof includes a dummy signed note (value 0) whose rho is
deterministically bound to the delegation context. This mechanism exists
to obtain a $\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$ from hardware
wallets (e.g., Keystone) that support only the standard Orchard PCZT
signing flow.

Without voting-specific firmware, the hardware wallet interprets the
delegation as a standard Orchard Action and signs the transaction
sighash accordingly. The dummy note's rho binding ensures this signature
is non-replayable and scoped to the exact delegation context (all note
commitments, the VAN, and the voting round), even though the hardware
wallet is unaware of governance semantics. The sighash that the hardware
wallet signs commits to a structure that appears to be a fund-moving
transaction - this is an inherent consequence of reusing the standard
signing flow and cannot be avoided without firmware changes.

When hardware wallet firmware adds voting-aware signing (e.g., a
governance network byte analogous to the testnet byte), the firmware can
display the delegation context to the user (notes, amounts, voting
round) and sign a governance-specific sighash that binds directly to
the delegation parameters. The signed note scaffolding (signed note
integrity, signed note nullifier, rho binding, and output note
commitment) can then be removed from the circuit. This migration is
purely subtractive: the simplified circuit is a strict subset of the
current one, and only the Delegation Proof changes. The Vote Proof
and Vote Reveal Proof are unaffected.

## Why $N_s$ Shares Per Vote

Splitting a vote into $N_s$ shares serves two purposes. First, it
provides temporal unlinkability: shares are submitted independently at
randomized times, preventing an observer from attributing all shares
to a single voter by timing correlation. Second, it limits the election
authority's view: even if the EA decrypts individual ciphertexts, it
sees only individual shares, not a voter's complete ballot allocation.

## Why Blinded Share Commitments

Each share commitment includes a random blind factor:
$\mathsf{share}\_{\mathsf{comm}\_\mathsf{i}} = \mathsf{Poseidon}(\mathsf{blind}\_\mathsf{i}, C_{1,i,x}, C_{2,i,x})$.
Without blinding, an observer could compute
$\mathsf{Poseidon}(C_{1,i,x}, C_{2,i,x})$ for each on-chain ciphertext
and compare against the $\mathsf{shares}\_\mathsf{hash}$ values committed in
VCs, linking revealed shares back to specific vote commitments. The
blind factor makes this reverse computation infeasible.

## Why Per-Server Share Isolation

Each submission server receives only the ciphertext and blind factor
for the single share it reveals, plus the blinded share commitments
for all $N_s$ shares. It does not receive the raw ciphertexts or blind
factors of shares assigned to other servers. This limits the data any
single server can observe: even a compromised server learns only one
share's plaintext-encrypted ciphertext and blind, not the full set.
The blinded share commitments are sufficient for the server to
recompute $\mathsf{shares}\_\mathsf{hash}$ in the proof (condition 3),
while the blinding prevents the server from correlating other shares'
ciphertexts with their commitments.

## Why Server-Delegated Share Reveal

The Vote Reveal Proof is constructed by the submission server
rather than the voter's client for two reasons: mobile devices are
unreliable for background ZKP computation, and server-side construction
enables temporal mixing of shares from many voters. The trust
requirement on the server is minimal: it learns encrypted shares and
vote decisions but cannot decrypt amounts or link shares to identities.

## Why Reusing VAN Address and Randomness

When a vote consumes a VAN and produces a new one, the new VAN reuses
the old VAN's diversified address ($\mathsf{vpk}\_{\mathsf{g}\_\mathsf{d}}$,
$\mathsf{vpk}\_{\mathsf{pk}\_\mathsf{d}}$) and commitment randomness
($\mathsf{gov}\_{\mathsf{comm}\_\mathsf{rand}}$). Only
$\mathsf{proposal}\_\mathsf{authority}$ changes. This is safe because VAN
commitments are blinded Poseidon hashes - the shared fields are never
externally observable (both old and new commitments appear as opaque
field elements in the VCT), so address rotation would provide no
additional unlinkability.

## Why Proposal Identifiers Start at 1

The $\mathsf{proposal}\_\mathsf{authority}$ bitmask is 16 bits wide, but
$\mathsf{proposal}\_\mathsf{id}$ values start at 1, yielding 15 usable
proposal slots rather than 16. Bit 0 is reserved.

This follows from how lookup arguments work in Halo 2. A lookup table
that validates $(\mathsf{proposal}\_\mathsf{id}, 2^{\mathsf{proposal}\_\mathsf{id}})$
must include a default row that satisfies the lookup when the selector
is inactive. The circuit uses the identity row $(0, 1)$ for this
purpose: when the selector $q = 0$, the lookup input evaluates to
$(0, 1)$, which must be present in the table for the proof to verify.
Because every inactive row matches this entry, $\mathsf{proposal}\_\mathsf{id} = 0$
cannot be used as a valid proposal identifier: a prover could trivially
satisfy the lookup with $\mathsf{proposal}\_\mathsf{id} = 0$ even when no
authority check is intended. An additional non-zero gate
($\mathsf{proposal}\_\mathsf{id} \cdot \mathsf{proposal}\_\mathsf{id}^{-1} = 1$)
provides defense-in-depth by rejecting $\mathsf{proposal}\_\mathsf{id} = 0$
on active rows.

## Why Threshold Secret Sharing

The election authority key is split into Shamir shares rather than distributed intact to all validators. This
ensures that compromise of any single validator (or any minority below
$t$) does not expose the full decryption key. The threshold
$t = \lceil n/2 \rceil + 1$ ensures that an adversary controlling fewer
than half of validators cannot reach the decryption threshold. Under
the standard CometBFT [^cometbft] assumption (fewer than one-third Byzantine),
this provides an additional safety margin for vote-amount privacy.

The protocol uses a trusted dealer rather than distributed key
generation (DKG). Feldman VSS commitments [^feldman] (which would let each
validator verify that its share is consistent with
$\mathsf{ea}\_\mathsf{pk}$) are omitted for initial scope; the dealer is
trusted to distribute correct shares, and any tampering would be
caught at tally time. Distributed key generation is a potential future
enhancement (see [Open issues]).

## Why No Per-Validator DLEQ Proofs

Each validator's partial decryption $D_i = [s_i]\, \sum C_{1,j}$ is
posted on-chain without a Chaum–Pedersen DLEQ proof [^chaum-pedersen]
attesting that $s_i$ matches the validator's committed share. This is a
deliberate simplification.

Without DLEQ proofs, a malicious validator can post a bogus $D_i$. Any
Lagrange combination that includes this $D_i$ will produce an incorrect
message point, causing the baby-step giant-step search to fail or
return an implausible result. However, a bogus $D_i$ cannot cause a
wrong tally to be accepted: the decrypted result is publicly
verifiable (anyone can check that the claimed
$\mathsf{total}\_\mathsf{ballots}$ satisfies the decryption equation for
the on-chain aggregate ciphertext), so a tally derived from a corrupted
subset will always be detected.

The missing DLEQ proofs are therefore a liveness issue, not a
correctness one. A single malicious validator can force the tally
procedure to try alternative subsets of size $t$ to find a fully honest
quorum, delaying finalization. Under the CometBFT assumption that fewer
than one-third of validators are Byzantine, such an honest quorum
always exists.

Adding per-validator DLEQ proofs would allow immediate identification
and exclusion of misbehaving validators, reducing verification to
$O(1)$ per partial decryption. This is left as a future enhancement
(see [Open issues]).

## Why a Send-Based VAN Model

The Vote Proof consumes the old VAN and produces a new one with the
voted proposal's authority bit cleared. This is a UTXO-style
"send": each vote appends two leaves to the VCT (new VAN + VC) and
requires the voter to hold a current Merkle path.

An alternative design was considered in which the VAN is eliminated
entirely and delegation is performed by out-of-band sharing of a
private key (hash-committed to on-chain). Under this model the Vote
Proof would not consume or re-create a VAN, removing the proposal
authority decrement step and the corresponding VCT growth. The primary
appeal is reduced client sync overhead: voters would not need to track
VAN re-insertions or maintain up-to-date Merkle paths for their own
VANs.

The send-based model is retained because it preserves the ability to
add partial delegation in a future extension, splitting
$\mathsf{num}\_\mathsf{ballots}$ across multiple delegates, each
receiving a fraction of the holder's voting weight. The VAN's explicit
ballot count and proposal authority bitmask are the data model that
would enable this; a future VAN-to-VAN delegation proof could consume
one VAN and produce two with subdivided ballot counts. Partial
delegation is not specified in this ZIP but the VAN model keeps the
design space open. Under the keysharing alternative, the delegate holds
the full key and therefore the full voting weight; there is no
in-protocol mechanism to subdivide it, and adding one later would
require a fundamentally different data model.

The sync savings of the alternative are also smaller than they first
appear: even without VAN re-creation, clients still need to update
VCT Merkle paths for their Vote Commitments (which the submission
server requires for the Vote Reveal Proof). The VAN model adds
incremental path-update overhead but does not introduce a new
category of sync obligation. If a future design change eliminated the
need for clients to track VCT paths entirely (for example by moving
Merkle path retrieval fully to the submission server), the tradeoff
would shift in favor of removing the VAN. See [Open issues].

## Why Classical El Gamal Rather Than Post-Quantum Encryption

The protocol uses El Gamal on the Pallas curve, which is vulnerable to a
quantum adversary running Shor's algorithm. A sufficiently powerful
quantum computer could recover $\mathsf{ea}\_\mathsf{sk}$ from
$\mathsf{ea}\_\mathsf{pk}$ and decrypt individual vote share ciphertexts,
breaking vote-amount privacy for any round whose on-chain ciphertexts
were recorded.

Post-quantum aggregatable encryption, a scheme that is both
quantum-resistant and additively homomorphic, would eliminate this
risk. However, no such scheme is mature enough for production use.
Lattice-based homomorphic encryption exists in theory, but practical
instantiations have ciphertext sizes, proving costs, and threshold
decryption complexities that are orders of magnitude larger than
El Gamal on an elliptic curve. The homomorphic tally
(component-wise point addition of Pallas points) and the threshold
decryption (Shamir/Feldman secret sharing with Lagrange interpolation
over a scalar field) are both simple precisely because El Gamal
operates in the same algebraic setting as the rest of the protocol.
Replacing it would require a fundamentally different threshold
protocol and circuit design for the Vote Proof and Vote Reveal Proof.

The practical consequence is that vote-amount privacy has a finite
horizon tied to quantum computing timelines. Ciphertexts are stored
on-chain permanently; an adversary who records them today could decrypt
individual share amounts once a cryptographically relevant quantum
computer exists. Voter *identity* is unaffected (alternate nullifier
unlinkability relies on Poseidon preimage resistance, not on El Gamal),
but *how much* a voter allocated to each option would be exposed.

This tradeoff is accepted for initial deployment. Per-round key rotation
(each round uses a fresh $\mathsf{ea}\_\mathsf{sk}$) limits a classical
compromise to a single round, and vote splitting across $N_s$ shares
means a quantum adversary would recover individual shares rather than
complete ballot allocations unless it also breaks the vote commitment
unlinkability (which depends on the Poseidon-based blinded share
commitments, not on El Gamal). Post-quantum migration is tracked as an
open issue.

## Why VCT Depth 24

The Orchard note commitment tree uses depth 32, supporting $2^{32}$
(~4.3 billion) leaves. Governance voting produces far fewer leaves:
each voter generates one VAN per delegation and two leaves (a new VAN
plus a VC) per vote. Even 10,000 voters each voting on 50 proposals
produce roughly 1 million leaves, well within the $2^{24}$
(~16.7 million) capacity of a depth-24 tree.

The reduced depth saves constraint rows in every circuit that performs
a Merkle membership proof (Vote Proof and Vote Reveal Proof), since
each level adds a Poseidon hash region. Moving from 32 to 24 levels
removes 8 hash regions per proof, reducing prover cost and verification
time without any practical capacity risk.


## Why Domain Tags in the VCT

Both VANs and VCs are leaves in the same Merkle tree. The domain tags
($\mathsf{DOMAIN}\_\mathsf{VAN} = 0$, $\mathsf{DOMAIN}\_\mathsf{VC} = 1$) as the first
Poseidon input make it structurally impossible for a valid VAN preimage
to produce the same hash as a valid VC preimage, regardless of the
remaining inputs.


# Deployment

This ZIP does not specify a consensus change to the Zcash mainchain.
Deployment considerations are specific to the vote chain and will be
addressed in the operational voting process ZIP.

The protocol is designed to support two hardware wallet modes for the
delegation phase. In the pre-firmware mode, the spend authorization
signature is obtained through a standard PCZT-based signing flow: the
hardware wallet signs what it interprets as an Orchard Action, and the
dummy signed note mechanism (see [Why a Dummy Signed Note]) ensures
correctness. In the post-firmware mode, the hardware wallet recognizes
a governance-specific network byte, displays the delegation context
(notes, amounts, voting round) to the user, and signs a
governance-specific sighash. Both modes produce a valid
$\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$ that the Delegation Proof
consumes. The post-firmware circuit is a strict subset of the
pre-firmware circuit (see [Open issues]).


# Reference implementation

A reference implementation of the three ZKP circuits (Delegation Proof,
Vote Proof, and Vote Reveal Proof) and the vote chain state machine
exists in the coinholder voting codebase used for this design.

At the time of writing, some implementation repositories are not
publicly accessible. Public, stable links will be added before
finalization of this ZIP.


# Open issues

- Per-validator Chaum–Pedersen DLEQ proofs for partial decryptions
  would allow immediate identification of misbehaving validators at
  tally time, converting the current liveness cost (subset search) to
  $O(1)$ verification. See [Why No Per-Validator DLEQ Proofs].
- Feldman VSS commitments from the dealer during the key ceremony
  would let each validator verify that its Shamir share is consistent
  with $\mathsf{ea}\_\mathsf{pk}$, removing the trust assumption on the
  dealer. See [Why Threshold Secret Sharing].
- Distributed key generation (DKG) would eliminate the trusted dealer
  entirely, producing $\mathsf{ea}\_\mathsf{pk}$ without any single party
  ever holding $\mathsf{ea}\_\mathsf{sk}$. See [Why Threshold Secret Sharing].
- Hardware wallet firmware with voting-aware signing (e.g., a
  governance network byte) would allow a simplified Delegation Proof
  circuit that removes the dummy signed note scaffolding (signed note
  integrity, rho binding, output note commitment). The migration is
  purely subtractive: the post-firmware circuit is a strict subset of
  the pre-firmware circuit. See [Why a Dummy Signed Note].
- Partial delegation (a VAN-to-VAN delegation proof that consumes
  one VAN and produces two with subdivided $\mathsf{num}\_\mathsf{ballots}$)
  is enabled by the send-based VAN model but not specified in this
  ZIP. Specifying the circuit and transaction type would allow a
  holder to distribute voting weight across multiple delegates.
  See [Why a Send-Based VAN Model].
- A simplified non-send VAN model, replacing VAN consumption and
  re-creation with out-of-band key delegation, would remove the
  proposal authority decrement step from the Vote Proof and reduce
  per-vote VCT growth. This is currently not adopted because it
  forecloses partial delegation and clients still need VCT Merkle path
  updates regardless. If future design changes remove the client's need
  to track VCT paths (e.g., full server-side path retrieval), this
  tradeoff should be revisited.
  See [Why a Send-Based VAN Model].
- Post-quantum aggregatable encryption would eliminate the long-term
  "harvest now, decrypt later" risk to vote-amount privacy. On-chain
  El Gamal ciphertexts are permanent; a future quantum adversary could
  decrypt individual share amounts for any recorded round. No production-
  ready post-quantum scheme currently offers both additive homomorphism
  and efficient threshold decryption. If such a scheme matures, the
  El Gamal layer (encryption in the Vote Proof, ciphertext verification
  in the Vote Reveal Proof, and the homomorphic tally procedure) could
  be replaced without changing the commitment, nullifier, or Merkle
  membership components of the protocol.
  See [Why Classical El Gamal Rather Than Post-Quantum Encryption].
- The VCT depth of 24 ($2^{24} \approx 16.7$ million leaves) is
  sufficient for current governance usage projections, but may need to
  be increased via a vote chain upgrade if participation grows
  significantly (e.g., more voters, more proposals per round, or more
  frequent rounds reusing the same tree). Increasing the depth requires
  updating the Merkle membership circuits in both the Vote Proof and
  Vote Reveal Proof, reproving the verification key, and coordinating
  a CometBFT chain upgrade. See [Why VCT Depth 24].


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-pallasandvesta]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.9.6: Pallas and Vesta](protocol/protocol.pdf#pallasandvesta)

[^protocol-concretespendauthsig]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.7.1: Spend Authorization Signature (Orchard)](protocol/protocol.pdf#concretespendauthsig)

[^poseidon]: [Poseidon: A New Hash Function for Zero-Knowledge Proof Systems](https://eprint.iacr.org/2019/458)

[^balance-proof]: [Orchard Proof-of-Balance](draft-valargroup-orchard-balance-proof)

[^pir-governance]: [Private Information Retrieval for Nullifier Exclusion Proofs](draft-valargroup-nullifier-pir)

[^ea-ceremony]: [Election Authority Key Ceremony](draft-valargroup-ea-key-ceremony)

[^chaum-pedersen]: [Chaum, D. and Pedersen, T.P. "Wallet Databases with Observers." CRYPTO 1992](https://link.springer.com/chapter/10.1007/3-540-48071-4_7)

[^elgamal]: [T. ElGamal, "A public key cryptosystem and a signature scheme based on discrete logarithms", IEEE Transactions on Information Theory, vol. 31, no. 4, pp. 469-472, 1985](https://doi.org/10.1109/TIT.1985.1057074)

[^shamir]: [A. Shamir, "How to share a secret", Communications of the ACM, vol. 22, no. 11, pp. 612-613, 1979](https://doi.org/10.1145/359168.359176)

[^feldman]: [P. Feldman, "A practical scheme for non-interactive verifiable secret sharing", in Proceedings of the 28th IEEE Symposium on Foundations of Computer Science, pp. 427-437, 1987](https://doi.org/10.1109/SFCS.1987.4)

[^ecies]: [V. Shoup, "A Proposal for an ISO Standard for Public Key Encryption", version 2.1, 2001](https://www.shoup.net/papers/iso-2_1.pdf)

[^bsgs]: [D. Shanks, "Class number, a theory of factorization, and genera", in Proceedings of Symposia in Pure Mathematics, vol. 20, pp. 415-440, 1971](https://doi.org/10.1090/pspum/020/0316385)

[^halo2]: [S. Bowe, J. Grigg, and D. Hopwood, "Recursive Proof Composition without a Trusted Setup", 2019](https://eprint.iacr.org/2019/1021)

[^cometbft]: [CometBFT Specification](https://docs.cometbft.com/v1/spec/)

[^protocol-merkletree]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.8: Note Commitment Trees](protocol/protocol.pdf#merkletree)

[^protocol-concretesinsemilla]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.1.9: Sinsemilla Hash Function](protocol/protocol.pdf#concretesinsemillahash)

[^protocol-concretecommitivk]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.9.4: CommitIvk](protocol/protocol.pdf#concretecommitivk)

[^pczt]: [zcash/zips issue #693: Standardize a protocol for creating shielded transactions offline (PCZT)](https://github.com/zcash/zips/issues/693)
