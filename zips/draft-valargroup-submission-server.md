    ZIP: Unassigned
    Title: Vote Share Submission Server
    Owners: Dev Ojha <dojha@berkeley.edu>
            Roman Akhtariev <ackhtariev@gmail.com>
            Adam Tucker <adamleetucker@outlook.com>
            Greg Nagy <greg@dhamma.works>
    Status: Draft
    Category: Standards
    Created: 2026-03-06
    License: MIT


# Terminology

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The terms below are to be interpreted as follows:

Submission server

: An untrusted server that receives encrypted vote shares from voters and
  submits the corresponding share reveal transactions to the vote chain.

Temporal unlinkability

: The property that an observer watching the vote chain cannot attribute
  multiple share reveal transactions to a single voter based on
  submission timing.

Share payload

: The off-chain data a voter sends to a submission server for a single
  share, containing the information necessary to construct a Vote Reveal
  Proof. Defined in [^voting-protocol].

Voter

: A holder of voting authority (a VAN) who has produced a Vote
  Commitment containing encrypted shares and wishes to have those
  shares revealed on-chain.

Election authority (EA)

: The set of validators that collectively hold Shamir shares of the
  El Gamal secret key for a voting round.

For definitions of *Vote Commitment*, *Vote Commitment Tree*, *vote
share*, *Vote Reveal Proof*, *share nullifier*, and *blinded share
commitment*, see [^voting-protocol]. For *voting round*, *validator*,
and *vote chain*, see [^coinholder-voting].


# Abstract

This ZIP specifies the submission server, a protocol participant in
the Zcash shielded voting system that receives encrypted vote shares
from voters and submits them to the vote chain at client-specified
times. The server constructs a Vote Reveal Proof for each share and
submits the corresponding transaction at the time designated by the
voter, interleaving submissions from many voters into a stream that
destroys timing correlations.

Without temporal mixing, a voter who submits $N_s$ shares for $P$
proposals produces $N_s \times P$ transactions in a short burst. An
observer can group these by timing, and after the tally is published,
cross-reference the group against low-participation proposal options to
narrow the voter's balance to a small range. Client-controlled
submission timing eliminates this attack surface: each share carries a
$\mathsf{submit\_at}$ timestamp sampled uniformly from the remaining
voting window, spreading shares from a single voter across time and
interleaving them with shares from other voters.

Each share is sent to half of the available servers, balancing
censorship resistance (redundancy ensures an honest server can relay)
against amount privacy (limiting the servers that see each share's
ciphertext).

Voters who cast their vote near the end of the voting window use a
reduced *last-moment mode*: a single share carrying the full ballot
count is submitted immediately, sacrificing temporal mixing in exchange
for guaranteed inclusion before the deadline.


# Motivation

The Shielded Voting Protocol [^voting-protocol] encrypts vote amounts
under the election authority's public key and splits each vote into
$N_s$ shares. Encryption alone does not provide effective privacy when
combined with observable metadata.

Consider a voter with a large balance voting on $P$ proposals. If the
voter submits all $N_s \times P$ shares directly to the vote chain, an
observer sees a burst of transactions arriving together. After the
round, the published tally reveals the aggregate total and voter count
per (proposal, decision) pair. For proposal options with few voters, the
observer can narrow each voter's balance to a tight range. When the
timing burst is correlated across proposals, the observer can link all
of the voter's choices, and social context (forum posts, public
advocacy) can close the remaining gap.

The submission server solves this by introducing an intermediary that
holds shares and submits them at client-specified times spread across
the voting window. The $N_s \times P$ transactions from a single voter
are interleaved into a stream of thousands of similar transactions from
hundreds of voters. The timing fingerprint is destroyed.

The client samples a $\mathsf{submit\_at}$ timestamp for each share,
drawn uniformly from the remaining voting window. The server holds the
share until that time, then constructs the Vote Reveal Proof and
submits the transaction. This design gives the client control over its
own temporal mixing distribution while delegating proof construction
and reliable delivery to the always-on server. A mobile client may be
killed or lose connectivity at the scheduled submission time, but the
server guarantees delivery.


# Privacy Implications

**Temporal mixing.** The client's primary privacy mechanism is
spreading share submissions across the voting window by sampling
independent $\mathsf{submit\_at}$ timestamps. The submission server
executes these schedules reliably, interleaving shares from many
voters into a uniform stream. Without this mixing, an observer can
group shares by submission time and, after tally publication, use
low-participation proposal options to reconstruct individual balances.

**Per-server information.** Each submission server learns the encrypted
share ciphertext and blind factor for the single share it reveals, the
blinded share commitments for all $N_s$ shares, the proposal
identifier, and the vote decision. It cannot learn the plaintext share
amount (encrypted under $\mathsf{ea}\_\mathsf{pk}$), the ciphertexts
or blind factors of shares assigned to other servers, the voter's
identity, or which VCT leaf the vote commitment corresponds to.

**Redundancy vs. restriction tension.** Censorship resistance requires
sending each share to multiple servers (so an honest server can relay
even if others censor). Amount privacy requires restricting the number
of servers that see each share (to limit the set that could collude
with the EA to gain an information advantage). These requirements pull
in opposite directions; the resolution is specified in [Server
Selection].

**Decision and share count visibility.** Vote decisions are public
inputs to the Vote Reveal Proof and appear in every share reveal
transaction on-chain.

Because share counts are visible, an observer who also sees the
aggregate weight for each decision after tally publication can, in
low-participation options, narrow individual voter balances to a
range. The protocol limits this inference in two ways: encrypted amounts keep exact balances hidden, and non-uniform share
decomposition strategies break the direct relationship between share
count and voter balance (see [Open Design Questions]). Encrypting
decisions entirely would close this channel but at substantial circuit
cost (see [Why Not Encrypt Decisions]).

Decision visibility also means a malicious submission server could
selectively delay or drop shares for a particular decision; the
redundancy mechanisms in [Decision Censorship Resistance] address this.

**Voter identity isolation.** Even a fully compromised election
authority (one that reconstructs $\mathsf{ea}\_\mathsf{sk}$ and
decrypts every share) cannot determine which voter cast a given vote.
The delegation phase of the Shielded Voting Protocol [^voting-protocol]
moves voting authority from the holder's Orchard spending key to a
locally-generated, unlinkable governance hotkey. All vote commitments
and share reveals reference only this hotkey. The link between on-chain
identity and governance hotkey is broken by the zero-knowledge
delegation proof and the alternate nullifier unlinkability property
established in [^balance-proof]; the EA never sees anything that
connects the two.

**Timing metadata.** Submission servers see $\mathsf{submit\_at}$
timestamps but these are independently sampled per share and do not
reveal the voter's identity or total ballot count. A server that logs
receipt timestamps could correlate shares received in the same session,
but because each share is sent to independently selected server
subsets, no single server sees all of a voter's shares. Voters who
distribute shares across multiple servers limit any single server's
view of their submission pattern.

**Last-moment privacy trade-off.** Voters who cast within the
last-moment buffer (see [Last-Moment Voting]) submit a single share
carrying their full ballot count with immediate delivery. This
sacrifices temporal mixing entirely: the share's on-chain arrival time
directly reflects when the voter cast. The trade-off is accepted
because each share requires the server to construct a Vote Reveal
Proof (a computationally expensive ZKP), and with little time
remaining the server may not complete all 16 proofs before the
deadline — resulting in a partially counted or entirely lost vote.
A single share requires only one proof, prioritizing inclusion over
mixing.


# Requirements

- An observer watching the vote chain cannot attribute multiple share
  reveal transactions to a single voter based on submission timing.
- A single malicious submission server cannot prevent a voter's shares
  from reaching the chain, provided at least one server handling those
  shares is honest.
- No single submission server learns enough information to reconstruct
  a voter's total ballot count or link shares across proposals.
- The submission server can construct Vote Reveal Proofs without
  access to the voter's private key material.
- The protocol tolerates submission server unavailability: if a server
  goes offline, shares assigned to other servers are unaffected.


# Non-requirements

- The Vote Reveal Proof circuit and its public/auxiliary inputs are
  specified in [^voting-protocol]; this ZIP does not re-specify them.
- The share submission payload format is defined in [^voting-protocol].
- The vote chain's verification of share reveal transactions (nullifier
  checks, ciphertext accumulation) is specified in [^voting-protocol].
- Client-side share decomposition (splitting $\mathsf{num}\_\mathsf{ballots}$
  into $N_s$ shares) is specified in [^voting-protocol].
- The consensus mechanism of the vote chain is out of scope.


# Specification

## Server Role

A submission server is an always-on service that accepts share payloads
from voters over an authenticated channel and submits the corresponding
share reveal transactions to the vote chain. Each validator on the vote
chain embeds a submission server as a helper process.

For each share payload received, the server MUST:

1. Validate the payload: verify that the vote commitment exists in the
   VCT at the claimed position, that the blinded share commitment at
   the claimed index is consistent with the provided ciphertext and
   blind factor, that the share nullifier has not already been
   published, and that $\mathsf{submit\_at} \leq \mathsf{vote\_end\_time}$.
2. Enqueue the share for submission at the client-specified
   $\mathsf{submit\_at}$ time (or immediately if
   $\mathsf{submit\_at} = 0$).
3. At the scheduled time, obtain the current VCT Merkle path for the
   vote commitment.
4. Derive the share nullifier.
5. Construct the Vote Reveal Proof.
6. Submit the share reveal transaction to the vote chain.

If the share reveal transaction is rejected (e.g., because another
server already revealed the same share), the server SHOULD discard the
payload without retry.

## Submission Timing

Each share payload includes a $\mathsf{submit\_at}$ field: a Unix
timestamp (seconds) specifying when the server SHOULD submit the
corresponding share reveal transaction. The server MUST NOT submit the
share before this time.

- When $\mathsf{submit\_at} > 0$, the server enqueues the share and
  submits it at or shortly after the specified time. Small inter-share
  jitter (on the order of seconds) SHOULD be applied to avoid
  simultaneous transaction bursts when multiple shares target nearby
  timestamps.
- When $\mathsf{submit\_at} = 0$, the server MUST submit the share as
  soon as possible (last-moment mode; see [Last-Moment Voting]).

The server MUST reject any payload where
$\mathsf{submit\_at} > \mathsf{vote\_end\_time}$ with an error.

### Client-Side Delay Sampling

The client is responsible for choosing $\mathsf{submit\_at}$ for each
share. For normal votes (cast outside the last-moment buffer), the
client MUST sample each share's submission time independently from a
uniform distribution over the remaining voting window:

$$\mathsf{submit\_at} \leftarrow \mathsf{Uniform}(\mathsf{now}, \; \mathsf{vote\_end\_time} - \mathsf{last\_moment\_buffer})$$

The upper bound excludes the last-moment buffer to ensure all shares
are submitted before the window in which last-moment voters begin
casting. See [Last-Moment Voting] for the buffer definition.

The client MUST NOT batch shares or assign identical timestamps.
Independent sampling ensures that shares from a single voter are spread
across time and interleaved with shares from other voters.

## Last-Moment Voting

A voter who casts within the *last-moment buffer* (the final portion
of the voting window) uses a reduced submission mode:

### Last-Moment Buffer

The last-moment buffer is defined as:

$$\mathsf{last\_moment\_buffer} = \min\!\left(\left\lfloor 0.1 \times (\mathsf{vote\_end\_time} - \mathsf{ceremony\_start}) \right\rfloor, \; 3600\right)$$

That is, 10% of the total round duration (from ceremony completion to
vote end), capped at 1 hour. A voter is in last-moment mode when:

$$\mathsf{now} \geq \mathsf{vote\_end\_time} - \mathsf{last\_moment\_buffer}$$

### Single-Share Mode

In last-moment mode, the client MUST:

1. Place the entire ballot count into a single share (share index 0).
   The remaining $N_s - 1$ share slots carry zero value.
2. Build only one share payload (for share index 0).
3. Set $\mathsf{submit\_at} = 0$ (immediate submission).

The server processes immediate shares without inter-share jitter delay.

### Privacy Rationale

Last-moment mode sacrifices temporal mixing for guaranteed inclusion.
Each share requires the server to construct a Vote Reveal Proof — a
computationally expensive ZKP — before submitting the transaction.
With 16 shares and little time remaining, the server may not complete
all 16 proofs before the voting window closes, resulting in lost votes.
A single share requires only one proof, maximizing the likelihood that
the vote is included before the deadline. Getting the vote counted is
more important than preserving temporal mixing when the window is
nearly closed.

The on-chain footprint of a last-moment vote is indistinguishable from
a single normal share reveal (same transaction format, same proof
type). An observer cannot determine whether a share reveal near the
deadline is a last-moment vote or a normally-timed share that happened
to be scheduled late.

## Server Selection

Each share MUST be sent to exactly $\lceil s/2 \rceil$ of the $s$
available submission servers, where $s$ is the number of active
validators (since each validator embeds a submission server). See
[Why Half the Servers] for the design rationale.

The client MUST select the $\lceil s/2 \rceil$ servers uniformly at
random for each share independently. Shares from the same vote
commitment SHOULD be distributed across different server subsets to
minimize any single server's view of the voter's activity.

## Per-Server Share Isolation

A submission server receives only the ciphertext and blind factor for
the single share it is responsible for revealing. The remaining
$N_s - 1$ shares are sent to other servers, each of which receives
only its own share's raw data.

To construct the Vote Reveal Proof, the server needs all $N_s$ blinded
share commitments (to recompute $\mathsf{shares}\_\mathsf{hash}$), but
these commitments are blinded with independent random factors and do
not expose the ciphertexts or blind factors of other shares.

This isolation ensures that a compromised server learns at most one
share's encrypted amount per vote commitment. Even if the server could
decrypt that share (by colluding with $t$ validators to reconstruct
$\mathsf{ea}\_\mathsf{sk}$), it would learn only a fraction of the
voter's total ballot count.

## Decision Censorship Resistance

Submission servers see the vote decision for each share they handle,
because the decision is a public input to the Vote Reveal Proof and
appears in the share reveal transaction. A malicious server could
selectively drop shares for decisions it opposes.

Because each share is sent to $\lceil s/2 \rceil$ servers, a censoring
server is effective only if all servers receiving that share collude.
Under the assumption that fewer than half the servers are malicious, at
least one honest server will relay each share. Alternative mitigation
strategies are discussed in [Why Not Encrypt Decisions] and [Why Not
TEE-Based Proof Construction].

## Duplicate Share Handling

Because each share is sent to $\lceil s/2 \rceil$ servers, multiple
servers will attempt to reveal the same share. The vote chain's share
nullifier set prevents double-counting: the first valid share reveal
transaction is accepted, and subsequent attempts for the same share
nullifier are rejected.

Servers MUST treat a share-nullifier-already-exists rejection as a
success (the share was revealed by another server) and discard the
payload. Servers MUST NOT retry or escalate rejected submissions.

## Availability and Fault Tolerance

If a submission server goes offline after receiving shares but before
submitting them, those shares are lost on that server. Because each
share is sent to $\lceil s/2 \rceil$ servers, the share will still be
revealed by another server unless all $\lceil s/2 \rceil$ recipients
fail simultaneously.

Servers SHOULD persist enqueued shares (including their
$\mathsf{submit\_at}$ timestamps) to durable storage so that shares
survive process restarts. A server that restarts during the voting
window SHOULD resume submission of any persisted shares whose
$\mathsf{submit\_at}$ times have not yet passed. For shares whose
$\mathsf{submit\_at}$ has already elapsed, the server SHOULD submit
them as soon as possible after restart.

Servers SHOULD NOT persist share data beyond the end of the voting
round. After the round transitions to TALLYING, all share payloads,
ciphertexts, blind factors, and blinded share commitments SHOULD be
securely erased.


# Rationale

## Why a Dedicated Submission Server

Naively submitting votes reveals balance through metadata. Even with
encrypted amounts, an observer can group transactions by timing, and
after tally publication, use low-participation proposal options to
narrow individual balances. The submission server solves this by
providing reliable, always-on execution of client-specified submission
schedules and by constructing Vote Reveal Proofs on the voter's behalf.

Fully client-side temporal mixing (where the wallet itself staggers
submissions over the voting window) was considered but rejected for
reliability: mobile clients may be killed, lose connectivity, or enter
low-power states during the multi-hour voting window. The hybrid
design — client chooses when, server guarantees delivery — preserves
client autonomy over timing while ensuring reliable execution.

## Why Half the Servers

The $\lceil s/2 \rceil$ parameter balances two competing concerns:

- **Censorship resistance** requires redundancy: if a share is sent to
  only one server and that server censors it, the share is lost.
  Sending to multiple servers ensures that an honest server can relay.
- **Amount privacy** requires restriction: validators who run
  submission servers also hold Shamir shares of
  $\mathsf{ea}\_\mathsf{sk}$. A validator that sees a share's
  ciphertext and colludes with others could gain
  an information advantage. Limiting the number of servers that see
  each share limits the collusion surface.

Sending to half the servers ensures that even if up to
$\lfloor s/2 \rfloor - 1$ servers are malicious, at least one honest
server receives each share. At the same time, no more than half the
validator set sees any individual share's ciphertext.

For censorship resistance, the adversary model assumes fewer than half
the servers are malicious (consistent with the CometBFT assumption of
fewer than one-third Byzantine validators, which is strictly stronger).
Under this assumption, any subset of $\lceil s/2 \rceil$ randomly
chosen servers contains at least one honest server.

For information restriction, limiting each share to half the servers
means that no more than half the validator set (who also hold Shamir
shares of $\mathsf{ea}\_\mathsf{sk}$) sees any individual share's
ciphertext. Combined with the threshold secret sharing requirement
($t = \lceil n/2 \rceil + 1$ validators needed to decrypt), a
single server that sees a share cannot decrypt it alone.

Alternative parameters were considered: sending to all servers
maximizes censorship resistance but gives every validator access to
every share's ciphertext, undermining information restriction. Sending
to a single server minimizes information exposure but provides no
censorship resistance.

## Why Servers Are Co-located with Validators

Submission servers are embedded in validator nodes rather than operated
as independent infrastructure. This follows from the protocol's
existing trust model: validators already participate in the EA key
ceremony and hold Shamir shares. Adding a separate server operator
class would introduce a new trust assumption without clear benefit.
Co-location also simplifies deployment (a single binary) and ensures
that the submission server has direct access to the vote chain for
transaction submission.

The dual role creates a tension: validators need decryption capability
for the tally, but the protocol does not want any single validator to
decrypt shares early. Threshold secret sharing
(see [^ea-ceremony]) addresses this: $t = \lceil n/2 \rceil + 1$
validators must collude to reconstruct $\mathsf{ea}\_\mathsf{sk}$,
and the server selection rule ensures each share is visible to at most
half the validators.

## Why Client-Controlled Timing

The client samples from a uniform distribution over the remaining
window (excluding the last-moment buffer) rather than, for example,
exponential or Gaussian. Because each share's $\mathsf{submit\_at}$ is
sampled independently, a single voter's shares may cluster by chance.
However, uniform sampling ensures that the *aggregate* stream of share
reveals across all voters is roughly uniform over time. An individual
voter's cluster is indistinguishable from coincidental proximity of
shares belonging to different voters, provided the total volume of
share reveals is sufficiently large.

## Why Not Encrypt Decisions

Because vote decisions are public, an observer who also sees the
published aggregate weight can, for low-participation options, narrow
the range of individual voter balances — even though exact amounts
remain encrypted. Encrypting decisions would close this channel but at
significant cost: a per-option ciphertext approach requires each share
to carry $k$ ciphertexts ($\mathrm{Enc}(v)$ for the chosen option,
$\mathrm{Enc}(0)$ for the remaining $k - 1$), multiplying per-share
circuit cost by $k$. A validator-decrypted variant hides per-option
counts from the public but not from validators, and making the
bucketing publicly verifiable requires an additional proof system that
scales with total share count.

The protocol instead limits share-count informativeness through
non-uniform share decomposition (see [Open Design Questions]), which
breaks the direct relationship between share count and individual
voter balances without adding circuit complexity.

## Why Not TEE-Based Proof Construction

Running Vote Reveal Proof construction inside a Trusted Execution
Environment would allow the server to handle decrypted decisions
without observing them, providing censorship resistance without the
circuit cost of decision encryption. However, TEEs introduce
infrastructure complexity (all validators would need compatible
hardware), rely on vendor-specific trust assumptions, and are subject
to side-channel attacks that have been demonstrated against SGX and
similar platforms. The multi-server redundancy approach achieves
adequate censorship resistance under the existing honest-majority
assumption without these additional dependencies.

## Open Design Questions

Several design questions affect the submission server's effectiveness
but are not yet resolved:

- **Share decomposition strategy.** For normal votes, the ballot count
  is split roughly evenly across $N_s = 16$ shares (floor division,
  remainder added to the last share). For last-moment votes, the full
  count goes into a single share (see [Last-Moment Voting]). Alternative
  decomposition strategies (such as powers-of-two denominations that
  make shares from different voters indistinguishable by amount, or
  base-10 decomposition with PRF-randomized remainders) could
  strengthen the mixing guarantee but are not yet adopted.
- **Client confirmation via PIR.** Voters currently have no
  privacy-preserving way to confirm that their shares were submitted.
  A PIR-based confirmation mechanism (querying the vote chain for
  share nullifiers without revealing which nullifiers are being
  checked) would close this gap. The Nullifier PIR
  ZIP [^pir-governance] provides a foundation, but adapting it for
  share nullifier queries requires additional specification.
- **Balance amendment.** A voter who is the sole participant on an
  unpopular proposal option may have their exact balance revealed by
  the tally (the aggregate equals their individual contribution).
  An opt-in mechanism to amend the voting ballot — lowering, rounding,
  or padding the declared balance and proving the amendment in ZK —
  would mitigate this. This is orthogonal to the submission server but
  affects the end-to-end privacy guarantee.
- **TEE-based proof construction.** Running Vote Reveal Proof
  construction inside a Trusted Execution Environment would allow the
  server to handle decrypted decisions without observing them,
  providing censorship resistance without decision encryption's circuit
  cost. Side-channel risks and infrastructure barriers make this a
  longer-term option.


# Reference Implementation

Reference implementation will be provided before this ZIP advances beyond Draft status.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^voting-protocol]: [Draft ZIP: Shielded Voting Protocol](draft-valargroup-shielded-voting)

[^ea-ceremony]: [Draft ZIP: Election Authority Key Ceremony](draft-valargroup-ea-key-ceremony)

[^coinholder-voting]: [Draft ZIP: Zcash Shielded Coinholder Voting](draft-valargroup-shielded-voting-setup)

[^balance-proof]: [Draft ZIP: Orchard Proof-of-Balance](draft-valargroup-orchard-balance-proof)

[^pir-governance]: [Draft ZIP: Private Information Retrieval for Nullifier Exclusion Proofs](draft-valargroup-nullifier-pir)
