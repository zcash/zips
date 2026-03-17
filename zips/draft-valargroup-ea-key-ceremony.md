    ZIP: Unassigned
    Title: Election Authority Key Ceremony
    Owners: Dev Ojha <dojha@berkeley.edu>
            Roman Akhtariev <ackhtariev@gmail.com>
            Adam Tucker <adamleetucker@outlook.com>
            Greg Nagy <greg@dhamma.works>
    Status: Draft
    Category: Process
    Created: 2026-03-04
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The terms below are to be interpreted as follows:

Election Authority (EA)
: A logical role whose keypair $(\mathsf{ea\_sk}, \mathsf{ea\_pk})$
  governs El Gamal encryption [^elgamal] of vote shares for a given
  voting round.

EA key ceremony
: A per-round protocol that produces a fresh El Gamal keypair
  $(\mathsf{ea\_sk}, \mathsf{ea\_pk})$ and distributes key material to
  eligible validators.

Dealer
: The validator selected to generate the EA keypair and distribute key
  material to eligible validators.

Vote chain
: The blockchain that serves as the single source of truth for voting
  operations. See the Coinholder Voting Process
  ZIP [^draft-coinholder-voting] for infrastructure details.

Validator
: A vote chain consensus participant that maintains keypairs for
  consensus, account transactions, and Pallas-based key exchange.

Vote Manager (VM):
: A role defined in the vote chain that grants the permissions for validators
  to enter the set.

Voting round
: A complete instance of a coinholder vote, scoped to a single Zcash
  mainnet snapshot and a fresh EA key.

Share
: A Shamir secret share $f(i)$ of $\mathsf{ea\_sk}$, held by a single
  validator after the ceremony.

Threshold ($t$)
: The minimum number of shares required to reconstruct
  $\mathsf{ea\_sk}$ or perform threshold decryption.

# Abstract

This ZIP specifies the Election Authority (EA) key ceremony used in
Zcash shielded coinholder voting. The ceremony runs on a dedicated
Proof-of-Authority vote chain with rotating proposers whose bonded validators
serve as ceremony participants. Each voting round requires a fresh El Gamal keypair:
vote shares are encrypted under the EA public key, homomorphically
aggregated on-chain, and decrypted after the voting window closes to
produce a verifiable tally.

The ceremony is triggered automatically when a voting round enters the
PENDING state. The block proposer acts as the dealer: it generates the
EA keypair, splits the secret key into Shamir shares with threshold
$t = \lceil n/2 \rceil + 1$, encrypts each share to the recipient
validator's Pallas public key via ECIES. Validators decrypt and
acknowledge their shares; the ceremony confirms when a majority of
eligible validators have acknowledged.

After the voting window closes, at least $t$ validators submit partial
decryptions that are combined via Lagrange interpolation on-chain to
recover the aggregate plaintext. Any party can verify correct decryption
by re-deriving the Lagrange combination from the stored partial
decryptions.


# Motivation

The coinholder voting system encrypts individual vote shares under an
Election Authority public key so that no party learns individual vote
amounts during the voting window. After the window closes, the EA secret
key is used to decrypt the homomorphically aggregated ciphertext and
produce a verifiable tally.

Generating and distributing this key securely, automatically, and per-round
is critical: a long-lived key would accumulate risk, manual distribution
would not scale, and a single point of failure would compromise liveness.
This ZIP specifies the automated ceremony that addresses these concerns.


# Privacy Implications

- The dealer generates $\mathsf{ea\_sk}$ and learns it during key
  generation before erasing it. This is the primary trust assumption:
  the dealer is a consensus-participating validator, automatically
  rotated via block proposer selection. A future DKG upgrade path would
  eliminate this (see [Rationale]).
- Individual validators hold only a Shamir share of
  $\mathsf{ea\_sk}$, not the full key. An adversary needs to compromise
  at least $t$ validators (where $t = \lceil n/2 \rceil + 1$) to
  reconstruct the secret and decrypt individual vote shares.
  Voter identity remains protected because alternate nullifiers are
  unlinkable to on-chain spending.
- Each round uses a fresh $\mathsf{ea\_sk}$. Compromise of one round's
  key material does not affect privacy of past or future rounds.


# Requirements

- A fresh EA keypair is generated for each voting round with no manual
  intervention.
- The ceremony completes with partial validator availability (at least
  a majority of eligible validators).
- No single validator's non-cooperation blocks the ceremony indefinitely.
- The resulting keypair enables homomorphic aggregation and publicly
  verifiable decryption.
- No single validator (other than the dealer during key generation)
  learns the full $\mathsf{ea\_sk}$.


# Non-requirements

- Distributed key generation that eliminates the trusted dealer (future
  upgrade; see [Rationale]).
- The voting protocol itself: delegation, vote casting, share submission,
  and share reveal circuits (see [^draft-voting-protocol]).
- Vote chain infrastructure setup (see [^draft-coinholder-voting]).


# Specification

## Chain Assumptions

This ZIP assumes that the vote chain is a Proof-of-Authority blockchain
providing the following primitives:

- A **CreateValidator** operation that bonds value to a validator. Used for authorizing a node entering the set.
- In-protocol rule-based **jailing** that removes a validator from the active
  consensus set without burning bonded stake, used as a liveness
  penalty (e.g., for ceremony non-participation as specified in
  [Confirmation]).

The authority to become a validator is granted by VM.

Proof-of-stake capability (bonding value) is the primitive that enables
validator participation. The VM sends Vote Chain bonded amount to a new validator to join the active set.

The requirement for the VM to approve a new Validator by sending them value
is what makes this a proof-of-stake rather than a proof-of-authority chain.

Jailing provides a liveness enforcement mechanism to expel validators who are down during the ceremony.

## El Gamal on Pallas

This section defines the El Gamal encryption scheme used throughout the
voting system. The Voting Protocol ZIP [^draft-voting-protocol] references
this section for vote share encryption.

### Setup

Let $G$ be the Pallas [^protocol-pallasandvesta] generator defined as
$\mathcal{G}^{\mathsf{Orchard}}$ in the Zcash protocol
specification [^protocol-orchardkeycomponents] (the Orchard spend
authorization base point). Let $\mathbb{F}_q$ denote the scalar field of
the Pallas curve. The EA keypair is:

- $\mathsf{ea\_sk} \in \mathbb{F}_q$: a random scalar.
- $\mathsf{ea\_pk} = \mathsf{ea\_sk} \cdot G$: the corresponding public
  key.

All El Gamal and ECIES operations in this ZIP MUST use this
generator. Using an arbitrary point would break the homomorphic property
and compatibility with the voting circuit.

### Encryption

To encrypt a value $v$ (expressed in ballots, i.e., zatoshi
floor-divided by 12,500,000) with randomness
$r \leftarrow \mathbb{F}_q$:

$$
\mathsf{Enc}(v, r) = (r \cdot G, \enspace v \cdot G + r \cdot \mathsf{ea\_pk})
$$

The ciphertext is a pair of Pallas points $(C_1, C_2)$.

### Additive Homomorphism

Given ciphertexts $\mathsf{Enc}(a, r_1)$ and $\mathsf{Enc}(b, r_2)$,
component-wise point addition yields a valid encryption of the sum:

$$
\mathsf{Enc}(a, r_1) + \mathsf{Enc}(b, r_2) = \mathsf{Enc}(a + b, \enspace r_1 + r_2)
$$

This allows anyone to publicly aggregate encrypted vote shares without
decryption. The vote chain accumulates per-(proposal, decision) aggregates
by summing ciphertexts as share reveal transactions arrive.

### Decryption

Given an aggregate ciphertext $(C_{1,\text{agg}}, C_{2,\text{agg}})$ and
$\mathsf{ea\_sk}$:

$$
C_{2,\text{agg}} - \mathsf{ea\_sk} \cdot C_{1,\text{agg}} = \mathsf{total\_value} \cdot G
$$

To recover $\mathsf{total\_value}$ from
$\mathsf{total\_value} \cdot G$, the decryptor performs a bounded
discrete logarithm lookup using baby-step-giant-step. This is feasible
because $\mathsf{total\_value}$ is bounded by total ZEC supply
(approximately $2.1 \times 10^{15}$ zatoshi, or $1.68 \times 10^{8}$
ballots).


## Chaum-Pedersen DLEQ Proof

The protocol uses a non-interactive Chaum-Pedersen proof of
discrete-log equality (DLEQ) [^chaum-pedersen] to verify correct usage
of secret key material during El Gamal decryption. The proof is
instantiated over the Pallas curve with a Fiat-Shamir challenge
derived from BLAKE2b-256 [^blake2].

**Statement.** Given two pairs of Pallas points $(G, P)$ and $(H, Q)$,
a DLEQ proof demonstrates:

$$\log_G(P) = \log_H(Q)$$

That is, the same scalar $x$ satisfies $P = x \cdot G$ and
$Q = x \cdot H$.

A proof is a pair of Pallas scalars $(e, z)$, serialized as 64 bytes
($e \mathbin\| z$, 32 bytes each).

### Proof Generation

The prover, holding secret $x$, computes:

1. Sample $k \leftarrow \mathbb{F}_q$ uniformly at random.
2. $R_1 = k \cdot G, \quad R_2 = k \cdot H$.
3. $e = \mathsf{DLEQChallenge}(G, P, H, Q, R_1, R_2)$.
4. $z = k + e \cdot x$.
5. Output $(e, z)$.

### Proof Verification

The verifier, given $(G, P, H, Q)$ and a proof $(e, z)$, checks:

1. Parse $e$ and $z$ as canonical Pallas scalar field elements. Reject
   if either is a non-canonical encoding.
2. $R_1 = z \cdot G - e \cdot P$.
3. $R_2 = z \cdot H - e \cdot Q$.
4. $e' = \mathsf{DLEQChallenge}(G, P, H, Q, R_1, R_2)$.
5. Accept if and only if $e' = e$.

### Challenge Derivation

The Fiat-Shamir challenge binds the proof to the full statement and
the prover's commitments:

$$e = \mathsf{HashToScalar}\bigl(\text{"svote-dleq-v1"} \mathbin\| \mathsf{compress}(G) \mathbin\| \mathsf{compress}(P) \mathbin\| \mathsf{compress}(H) \mathbin\| \mathsf{compress}(Q) \mathbin\| \mathsf{compress}(R_1) \mathbin\| \mathsf{compress}(R_2)\bigr)$$

where $\mathsf{compress}$ denotes the 32-byte affine compressed point
encoding and $\mathsf{HashToScalar}$ applies BLAKE2b-256 (unkeyed) to
the concatenation and maps the 32-byte digest to a Pallas scalar. The
domain tag `"svote-dleq-v1"` (13 bytes, ASCII) prevents cross-protocol
challenge reuse.

All input points MUST be validated as on-curve Pallas points at
deserialization time. The proof contains only scalars; each MUST be a
canonical encoding in $\mathbb{F}_q$.

### Partial Decryption Proof

Each validator $i$ proves that their partial decryption was computed
using their correct Shamir share $f(i)$. The DLEQ proof is
instantiated with:

- $P = \mathsf{VK}_i = f(i) \cdot G$ — the validator's public
  verification key, derived from their Shamir share.
- $H = C_{1,\text{agg}}$ — the first component of the aggregate
  ciphertext.
- $Q = D_i = f(i) \cdot C_{1,\text{agg}}$ — the validator's partial
  decryption.
- $x = f(i)$ — the validator's Shamir share (private).

The proof demonstrates
$\log_G(\mathsf{VK}_i) = \log_{C_{1,\text{agg}}}(D_i)$, confirming
that the same share used to derive $\mathsf{VK}_i$ was used to compute
$D_i$.


## ECIES on Pallas

Share distribution uses ECIES [^ecies] instantiated on Pallas with the
following parameters:

- **Key Encapsulation (KEM)**: ephemeral Diffie-Hellman on Pallas with
  generator $G$.
- **Key Derivation (KDF)**: $k = \mathsf{SHA256}(\mathsf{compress}(E) \| \mathsf{x}(S))$,
  where $\mathsf{compress}$ is the 32-byte compressed Pallas point encoding
  and $\mathsf{x}(S)$ extracts the $x$-coordinate by taking the compressed
  encoding and clearing bit 7 of byte 31 (the sign bit).
- **Symmetric Encryption (DEM)**: ChaCha20-Poly1305 with a zero nonce.

A fresh ephemeral scalar MUST be generated for each recipient validator
to prevent cross-validator key correlation. After decryption, the
recipient MUST verify that $f(i) \cdot G = \mathsf{VK}_i$.

## Pallas Key Registration

Before participating in any ceremony, a validator MUST register a
Pallas public key on the vote chain.

The submitted key MUST be a 32-byte compressed Pallas point that is on
the curve and is not the identity point. Each validator operator address
MAY register at most one Pallas key; duplicate registrations MUST be
rejected.

The registered key persists across rounds and is used for ECIES key
exchange during each ceremony the validator participates in.

## Ceremony Protocol

Each voting round triggers a fresh EA key ceremony after the round enters
the **PENDING** state.

### Eligibility

All validators with a registered Pallas public key at the time of round
creation are eligible for the ceremony.

### Dealer Selection

The next block proposer is automatically selected as the dealer.

### Key Generation and Distribution

Let $n$ be the number of eligible validators and
$t = \lceil n/2 \rceil + 1$ (minimum 2) be the threshold.

The dealer:

1. Generates $\mathsf{ea\_sk} \leftarrow \mathbb{F}_q$ and
   computes $\mathsf{ea\_pk} = \mathsf{ea\_sk} \cdot G$.
2. Constructs a random polynomial
   $f(x) = \mathsf{ea\_sk} + a_1 x + \cdots + a_{t-1} x^{t-1}$
   of degree $t - 1$ with $f(0) = \mathsf{ea\_sk}$ and random
   coefficients
   $a_1, \ldots, a_{t-1} \leftarrow \mathbb{F}_q$.
3. Evaluates $f(i)$ for $i = 1, \ldots, n$ to produce $n$ Shamir
   shares [^shamir].
4. For each eligible validator $V_i$, encrypts the share $f(i)$ to
   $\mathsf{pk}_i$ using the ECIES construction defined in
   [ECIES on Pallas], producing $(E_i, \mathsf{ct}_i)$.
5. Publishes to the chain: $\mathsf{ea\_pk}$, the threshold $t$, all
   $(E_i, \mathsf{ct}_i)$ pairs, and all $\mathsf{VK}_i$.
6. Securely erases $\mathsf{ea\_sk}$, the polynomial coefficients, and
   all share values from memory.

### Validator Acknowledgment

Each eligible validator $V_i$:

1. Decrypts share $f(i)$ from $(E_i, \mathsf{ct}_i)$ per
   [ECIES on Pallas], which includes verification that
   $f(i) \cdot G = \mathsf{VK}_i$.
2. Stores $f(i)$ securely on disk.
3. Submits an ACK message to the chain containing the commitment
   $\mathsf{SHA256}(\texttt{"ack"} \| \mathsf{ea\_pk} \| \mathsf{validator\_address})$.

### Confirmation

The ceremony confirms under one of the following conditions:

- **Fast path**: all eligible validators ACK. The ceremony confirms
  immediately.
- **Timeout path**: after the ACK phase timeout (30 minutes), if at least
  $t$ eligible validators have ACK'd, the ceremony confirms. Non-ACK'd
  validators are stripped from the round and increment a
  consecutive-miss counter. After 3 consecutive misses, the validator
  MUST be jailed.
- **Failure**: if fewer than $t$ eligible validators ACK within the
  timeout, the ceremony resets and a new dealer is selected.

The $t$-ACK requirement ensures that enough shares are available for
threshold decryption during the tally phase.

On successful confirmation, the round transitions from **PENDING** to
**ACTIVE**.

### Validator Set Changes

**Joining**: in the threshold model, new validators joining after the
ceremony cannot receive an independent share without a new dealing round.
A validator attempting to join the set during an active voting round MUST wait for the round to complete.

**Leaving**: a departing validator retains their share $f(i)$ and cannot
be forced to delete it. Under the threshold model, a single share does
not reveal $\mathsf{ea\_sk}$. Key rotation (generating a fresh
$\mathsf{ea\_sk'}$ for future rounds) further limits exposure.

## Tally

After the voting window closes and the round transitions to **TALLYING**:

1. For each (proposal, decision) pair, the aggregate ciphertext
   $(C_{1,\text{agg}}, C_{2,\text{agg}})$ is the component-wise sum of all
   submitted share ciphertexts. This aggregation is publicly verifiable —
   anyone can replay the addition from on-chain data.

2. At least $t$ validators submit partial decryptions to the chain.
   Each participating validator $V_i$ computes:

   $$D_i = f(i) \cdot C_{1,\text{agg}}$$

   Each $D_i$ MUST be accompanied by a Chaum-Pedersen DLEQ proof
   demonstrating correct share usage (see [Partial Decryption Proof]).

3. The partial decryptions are combined via Lagrange interpolation in
   the exponent. Given partial decryptions $\{(i, D_i)\}$ from a set
   $S$ of at least $t$ validators, the Lagrange coefficients are:

   $$\lambda_i = \prod_{j \in S,\, j \neq i} \frac{-j}{i - j}$$

   The combined result is:

   $$\mathsf{ea\_sk} \cdot C_{1,\text{agg}} = \sum_{i \in S} \lambda_i \cdot D_i$$

4. The aggregate plaintext is recovered:

   $$\mathsf{total\_value} \cdot G = C_{2,\text{agg}} - \mathsf{ea\_sk} \cdot C_{1,\text{agg}}$$

   $\mathsf{total\_value}$ is recovered via baby-step-giant-step.

5. The on-chain tally handler Lagrange-combines the partial decryptions
   and publishes $\mathsf{total\_value}$ for each (proposal, decision)
   pair.

6. Any party MAY verify tally correctness by re-deriving the Lagrange
   combination from the stored partial decryptions and confirming the
   decrypted result.

Individual vote amounts are never revealed — only the aggregate total per
(proposal, decision).

## Key Retention

Each validator's share file for each round SHOULD be retained
indefinitely (32 bytes per share) to allow future retally or audit.

## Timing Parameters

| Parameter                      | Value        | Notes                         |
| ------------------------------ | ------------ | ----------------------------- |
| Ceremony deal timeout          | ~30 blocks   | TBD; time for dealer message  |
| ACK phase timeout              | 30 minutes   | Fixed                         |
| Consecutive ceremony miss jail | 3 misses     | Validator jailed, not slashed |
| Slashing fractions             | 0            | Jailing only, no token burns  |


# Rationale

## Why Per-Round Keys

Scoping $\mathsf{ea\_sk}$ to a single round limits the impact of key
compromise to that round only. Validator rotation between rounds is
handled naturally — departing validators cannot decrypt future rounds.
This avoids the complexity of re-initialization or long-lived key
management.

## Why ECIES on Pallas

ECIES on Pallas reuses the Pallas curve already present in the Orchard
protocol, avoiding additional curve dependencies. ChaCha20-Poly1305
provides authenticated encryption.

## Why CometBFT / Cosmos SDK

The vote chain is built on CometBFT consensus [^cometbft] with the
Cosmos SDK [^cosmos-sdk] application framework. CometBFT provides
instant finality (no probabilistic confirmation), deterministic block
proposer rotation (used for dealer selection), and a well-defined
validator set with bonded stake. The Cosmos SDK provides staking
primitives — `CreateValidator`, delegation, jailing — out of the box,
as well as a module-based architecture that allows voting-specific logic
(Pallas key registration, ceremony orchestration, share aggregation) to
be implemented as custom modules alongside the standard staking
infrastructure. This avoids building consensus and validator management
from scratch while inheriting battle-tested BFT guarantees from over
100 production Cosmos chains.

## Why Jailing, Not Slashing

Ceremony non-participation is penalized by jailing (excluding from
future ceremonies) rather than token slashing. This is a liveness
signal, not a safety violation.

## Why Threshold Secret Sharing

The election authority key is split into Shamir shares rather than distributed intact to all validators. This
ensures that compromise of any single validator (or any minority below
$t$) does not expose the full decryption key. The threshold
$t = \lceil n/2 \rceil + 1$ ensures that an adversary controlling fewer
than half of validators cannot reach the decryption threshold. Under
the standard CometBFT [^cometbft] assumption (fewer than one-third Byzantine),
this provides an additional safety margin for vote-amount privacy.

The decryption threshold $t$ is set equal to the number of ACKs
required for ceremony confirmation. This is a deliberate constraint:
if $t$ were strictly greater than the ACK requirement, the ceremony
could confirm with fewer acknowledged validators than are needed for
threshold decryption, making it impossible to decrypt the tally and
creating an unrecoverable liveness failure. By requiring at least $t$
ACKs before confirmation, the protocol guarantees that enough shares
are available for decryption whenever the ceremony succeeds.

The protocol uses a trusted dealer rather than distributed key
generation (DKG). Feldman VSS commitments [^feldman] (which would let each
validator verify that its share is consistent with
$\mathsf{ea}\_\mathsf{pk}$) are omitted for initial scope; the dealer is
trusted to distribute correct shares, and any tampering would be
caught at tally time. Distributed key generation is a potential future
enhancement (see [Open issues]).

## Why Per-Validator DLEQ Proofs

Each validator's partial decryption $D_i = f(i) \cdot C_{1,\text{agg}}$
is posted on-chain with a Chaum-Pedersen DLEQ proof (see
[Partial Decryption Proof]) attesting that $f(i)$ matches the
validator's committed verification key $\mathsf{VK}_i$.

Without DLEQ proofs, a malicious validator could post a bogus $D_i$.
Any Lagrange combination that includes such a $D_i$ would produce an
incorrect message point, causing the baby-step giant-step search to
fail or return an implausible result.

Per-validator DLEQ proofs allow immediate identification and exclusion of misbehaving validators.

## Why Classical El Gamal Rather Than Post-Quantum Encryption

The protocol uses El Gamal on the Pallas curve, which is vulnerable to a
quantum adversary running Shor's algorithm. A sufficiently powerful
quantum computer could recover $\mathsf{ea}\_\mathsf{sk}$ from
$\mathsf{ea}\_\mathsf{pk}$ and decrypt individual vote share ciphertexts,
breaking vote-amount privacy for any round whose on-chain ciphertexts
were recorded.

Post-quantum aggregatable encryption — a scheme that is both
quantum-resistant and additively homomorphic — would eliminate this
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
computer exists. Voter *identity* is unaffected — alternate nullifier
unlinkability relies on Poseidon preimage resistance, not on El Gamal
— but *how much* a voter allocated to each option would be exposed.

This tradeoff is accepted for initial deployment. Per-round key rotation
(each round uses a fresh $\mathsf{ea}\_\mathsf{sk}$) limits a classical
compromise to a single round, and vote splitting across $N_s$ shares
means a quantum adversary would recover individual shares rather than
complete ballot allocations unless it also breaks the vote commitment
unlinkability (which depends on the Poseidon-based blinded share
commitments, not on El Gamal). Post-quantum migration is tracked as an
open issue.


# Open Issues

- Feldman VSS commitments from the dealer during the key ceremony
  would let each validator verify that its Shamir share is consistent
  with $\mathsf{ea}\_\mathsf{pk}$, removing the trust assumption on the
  dealer. See [Why Threshold Secret Sharing].
- Distributed key generation (DKG) would eliminate the trusted dealer
  entirely, producing $\mathsf{ea}\_\mathsf{pk}$ without any single party
  ever holding $\mathsf{ea}\_\mathsf{sk}$. See [Why Threshold Secret Sharing].
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
- The exact production parametrization — threshold fraction, ACK
  timeout duration, consecutive-miss jail limit, and their interaction
  with expected validator set sizes — requires further evaluation
  against operational data from vote chain testnets before values are
  finalized.


# Reference implementation

[^ref-impl] — a Go and Rust implementation built on Cosmos SDK with
Halo 2 zero-knowledge proof circuits.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^draft-coinholder-voting]: [Draft ZIP: Zcash Shielded Coinholder Voting](draft-valargroup-coinholder-voting-setup.md)

[^draft-voting-protocol]: [Draft ZIP: Shielded Voting Protocol](draft-valargroup-shielded-voting)

[^blake2]: [J.-P. Aumasson, S. Neves, Z. Wilcox-O'Hearn, and C. Winnerlein, "BLAKE2: simpler, smaller, fast as MD5", 2013](https://blake2.net/blake2.pdf)

[^chaum-pedersen]: [D. Chaum and T. P. Pedersen, "Wallet Databases with Observers", CRYPTO 1992](https://link.springer.com/chapter/10.1007/3-540-48071-4_7)

[^elgamal]: [T. ElGamal, "A public key cryptosystem and a signature scheme based on discrete logarithms", IEEE Transactions on Information Theory, vol. 31, no. 4, pp. 469-472, 1985](https://doi.org/10.1109/TIT.1985.1057074)

[^feldman]: [P. Feldman, "A practical scheme for non-interactive verifiable secret sharing", FOCS 1987](https://doi.org/10.1109/SFCS.1987.4)

[^ecies]: [V. Shoup, "A Proposal for an ISO Standard for Public Key Encryption", version 2.1, 2001](https://www.shoup.net/papers/iso-2_1.pdf)

[^shamir]: [A. Shamir, "How to share a secret", Communications of the ACM, vol. 22, no. 11, pp. 612-613, 1979](https://doi.org/10.1145/359168.359176)

[^protocol-pallasandvesta]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.9.6: Pallas and Vesta](protocol/protocol.pdf#pallasandvesta)

[^protocol-orchardkeycomponents]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 4.2.3: Orchard Key Components](protocol/protocol.pdf#orchardkeycomponents)

[^cometbft]: [CometBFT: Byzantine Fault Tolerant consensus engine](https://docs.cometbft.com/)

[^cosmos-sdk]: [Cosmos SDK: Framework for building application-specific blockchains](https://docs.cosmos.network/)

[^ref-impl]: [z-cale/zally: Zcash Shielded Voting reference implementation](https://github.com/z-cale/zally)
