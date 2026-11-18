    ZIP: Unassigned
    Title: Zcash Shielded Coinholder Voting
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

The key words "MUST" and "MAY" in this document are to be
interpreted as described in BCP 14 [^BCP14] when, and only when,
they appear in all capitals.

The terms below are to be interpreted as follows:

Vote chain
: The blockchain that serves as the single source of truth for voting
  operations. See [System Overview] for the state it maintains.

Voting round
: A complete instance of a coinholder vote, scoped to a single Zcash
  mainnet snapshot and a fresh Election Authority key.

Vote round ID
: A unique identifier for a voting round. See [Poll Creation] for the
  computation.

Poll runner
: The entity responsible for conducting a voting round.

Vote manager
: The on-chain role authorized to create voting rounds.

Bootstrap operator
: The entity that provisions the vote chain genesis and initial
  validator set.

Validator
: A vote chain consensus participant. See [Validator] under Roles for
  responsibilities and keypair details.

Nullifier service operator
: The entity that runs the nullifier exclusion PIR server. See
  [Nullifier Service Operator] under Roles for responsibilities.

Bonded validator
: A validator whose stake is active under the standard Cosmos SDK
  `x/staking` module [^cosmos-staking]: its delegation is committed,
  it participates in consensus, and it is eligible to produce blocks.

Submission server
: An untrusted service that accepts encrypted vote share payloads
  from voters and submits the corresponding share reveal
  transactions to the vote chain. Specified in
  `draft-valargroup-submission-server` [^draft-submission-server].

Election Authority (EA)
: A virtual signing key, jointly constructed by validators during a key
  ceremony so that no single party holds the private key. Used to encrypt
  vote shares and decrypt the final tally. See
  `draft-valargroup-ea-key-ceremony` [^draft-ceremony] for the
  ceremony protocol.

Snapshot height
: The Zcash mainnet block height at which eligible Orchard note balances
  are captured. See [Snapshot Configuration] for constraints.

For definitions of cryptographic terms including *alternate nullifier*,
*nullifier non-membership tree*, *nullifier domain*, *pool snapshot*, and
*claim*, see the Orchard Proof-of-Balance ZIP [^draft-balance-proof]. For
EA key ceremony terms, see `draft-valargroup-ea-key-ceremony`
[^draft-ceremony]. For PIR-related terms, see
`draft-valargroup-nullifier-pir` [^draft-pir].


# Abstract

This ZIP specifies how to operate the infrastructure for Zcash shielded
coinholder voting. It defines a purpose-built vote chain built on Cosmos
SDK, three operator roles (bootstrap operator, vote manager, validator),
and the lifecycle of a voting round from snapshot selection through tally
verification.

The vote chain stores vote commitments in a Poseidon Merkle tree, tracks
three nullifier sets to prevent double-voting, and accumulates encrypted
vote shares as homomorphic El Gamal ciphertexts. Each transaction
(delegation, vote, share reveal) is verified by a zero-knowledge proof
on-chain. Validators join through an automated onboarding script that
handles binary distribution, key generation, and on-chain registration.
A separate nullifier service provides private information retrieval of
exclusion proofs so voters can prove note non-spending without revealing
which notes they hold.

Tally correctness is independently verifiable: validators submit partial
decryptions which are Lagrange-combined on-chain. Any party with access
to the chain state can re-derive the combination from the stored
partials and confirm the decrypted result.


# Motivation

The Zcash Shielded Voting Protocol [^draft-voting-protocol] defines a
cryptographic protocol for private coinholder voting. This ZIP specifies
the deployment infrastructure required to run that protocol: the vote
chain, operator roles, and voting round lifecycle.


# Privacy Implications

- Zero-knowledge proofs and encryption hide the contents of
  delegations, votes, and share reveals, but not the network-layer
  metadata associated with their submission. A vote chain validator
  sees the source IP, submission timestamp, connection correlation,
  and P2P propagation pattern of every transaction it receives.
- PIR queries against the nullifier service are private in content
  but not in timing: a nullifier service operator sees the source IP
  and time of each query, which reveals that a given client is
  participating in the current voting round.
- The vote chain is a public ledger. Transaction contents are
  encrypted or zero-knowledge-proven, but their existence, ordering,
  and block-inclusion timing are a permanent public record.
- Bootstrap operators learn the network identities of validators
  during onboarding (see [Onboarding Validators]).
- Validator power distribution affects the trust model for the EA
  key ceremony. See `draft-valargroup-ea-key-ceremony`
  [^draft-ceremony] for EA-specific privacy implications.


# Requirements

- A new poll runner can set up infrastructure and conduct a voting round
  by following this specification and the referenced companion ZIPs.
- A Zcash coinholder with eligible Orchard funds at the round's
  snapshot height can participate in the voting round using a
  conforming wallet client.
- The vote chain operates as a public, verifiable ledger — anyone can run
  a monitoring node to audit.
- The system operates with partial validator availability.


# Non-requirements

- Governance policy decisions such as proposal eligibility, quorum
  requirements, and fund disbursement rules (see ZIP 1016 [^zip-1016]).


# Specification

## Proposals and Decisions

The voting process specified by this ZIP allows a poll runner to put
one or more questions — *proposals* — to eligible voters. For each
proposal, voters choose exactly one of a predefined set of labeled
*options*; the chosen option is the voter's *decision* for that
proposal.

### Structure of a proposal

Each proposal has:

- A **title**, short and human-readable.
- An optional **description** providing additional context.
- Between 2 and 8 **options**, each carrying a human-readable label.
  Option labels MUST be non-empty ASCII strings.

Proposals in a voting round are assigned 1-indexed sequential
identifiers; options within a proposal are assigned 0-indexed
sequential indices.

### Decisions

A **decision** is a voter's chosen option for a specific proposal,
represented as the option's 0-indexed position within that proposal's
option list. Decisions are recorded in the encrypted share
accumulator, keyed by `(proposal_id, vote_decision)`; see
`draft-valargroup-voting-protocol` [^draft-voting-protocol] for the
cryptographic construction.

### Kinds of polls that can be expressed

A voting round can carry **1 to 15 independent proposals**, and each
proposal can offer **2 to 8 labeled options**. This is sufficient for:

- Yes/no questions ("Approve proposal X?" with options Yes / No).
- Multiple-choice preference questions (for example, choosing among
  named candidates or funding tiers).
- Rating-style questions using a fixed option ladder.

The following ballot shapes are out of scope for this specification:

- Free-form write-in answers.
- Ranked-choice or weighted-ranking ballots.
- More than 15 proposals in a single voting round, or more than 8
  options in a single proposal.

The 15-proposal upper bound is imposed by the zero-knowledge vote
authority bitmask (1 bit is reserved as a sentinel). Polls requiring
more proposals or richer ballot structures are split across multiple
rounds or expressed through an external layer.

## System Overview

The coinholder voting system operates on a purpose-built Cosmos SDK vote
chain. Zcash mainnet snapshots provide the set of eligible Orchard note
balances.

The vote chain stores:

- A **Vote Commitment Tree** (VCT): a Poseidon Merkle tree of vote
  commitments.
- Three **nullifier sets**: governance nullifiers (alternate nullifiers
  from note claims), VAN nullifiers (from delegation consumption), and
  share nullifiers (from share reveals).
- An **encrypted share accumulator** per (proposal, decision): the
  homomorphic sum of El Gamal ciphertexts for each vote option.

The vote chain verifies a zero-knowledge proof for each transaction type:
delegation, vote, and share reveal. The proof circuits are specified in
`draft-valargroup-voting-protocol` [^draft-voting-protocol].

## Deployment Architecture

A complete deployment consists of:

- **Vote chain nodes** — one or more `svoted` instances running CometBFT
  consensus. Each `svoted` binary additionally includes the
  **submission server** (an untrusted service that accepts vote
  share payloads from clients and submits the corresponding share
  reveal transactions at client-specified times). The submission
  server shares the node's process but is functionally decoupled
  from chain consensus; see `draft-valargroup-submission-server`
  [^draft-submission-server].
- **Nullifier service** — a PIR server that provides private nullifier
  exclusion proofs to voters (see [Nullifier Service]).
- **Vote configuration document** — a per-round document published
  by the vote manager that lists the network endpoints of the vote
  chain nodes and nullifier service operators participating in the
  round. The document format and distribution rules are specified
  in `draft-valargroup-shielded-voting-wallet-api`
  [^draft-wallet-api]; see also [Vote Configuration Publication].

## Roles

### Bootstrap Operator

The bootstrap operator generates the vote chain genesis block and
provisions the initial validator set. At genesis, a single vote
manager account is created with a balance of the chain's native token
(denom `usvote`) sized to fund all planned validators. From that
account the bootstrap operator funds each validator via
`MsgAuthorizedSend`, a transfer message gated by the vote chain's
ante handler: the vote manager MAY send to any address, and bonded
validators MAY send to the vote manager or to other bonded
validators; all other transfers — including the standard Cosmos bank
`MsgSend` and `MsgMultiSend` messages — are rejected.

The amount transferred to each validator at bonding time determines
their consensus voting power. An even distribution across validators
reduces the risk of consensus capture. The bootstrap operator's
activities are confined to genesis. The keypair that controls the
genesis `vote_manager` address continues afterwards as the initial
vote manager (see [Vote Manager]), and MAY transfer that role via
`MsgSetVoteManager`.

### Vote Manager

The vote manager is the only account authorized to initialize the
chain's voting round (see [Poll Creation]).

The vote manager address is set in the genesis block (see
[Genesis Validator Setup]). The current vote manager MAY transfer
the role to another address via `MsgSetVoteManager`; the transfer
is atomic and moves the full account balance to the new address.
No other account can claim or reassign the role.

### Validator

Validators participate in consensus, the EA key ceremony (see
`draft-valargroup-ea-key-ceremony` [^draft-ceremony]), and automatic
tally computation. Each validator maintains three keypairs:

- **Consensus keypair**: used for CometBFT consensus.
- **Account keypair**: used for submitting chain transactions.
- **Pallas keypair**: used for ECIES key exchange during the EA ceremony.

Validators join the network by following the flow described in
[Onboarding Validators].

Each validator additionally runs the submission server bundled
into the `svoted` binary, which receives encrypted vote share
payloads from voters and submits the corresponding share reveal
transactions on their behalf. See `draft-valargroup-submission-server`
[^draft-submission-server].

### Nullifier Service Operator

A nullifier service operator runs the nullifier exclusion PIR
server that wallet clients query to obtain Merkle non-membership
proofs for the Zcash mainnet nullifier set at the snapshot
height. The PIR server is a separate binary, distributed
independently of the vote chain node, with its own ingest pipeline
and HTTP query endpoint. Specified in
`draft-valargroup-nullifier-pir` [^draft-pir].

## Vote Chain Infrastructure

### Genesis Validator Setup

The bootstrap operator obtains the vote chain binary `svoted`
either from a published release of the reference implementation
(see [Reference implementation]) or by building from source, and
initializes a new single-validator chain for the voting round.

Initialization proceeds as follows:

1. **Choose a chain identifier.** Each voting round uses its own
   chain identifier so that transactions signed for one round
   cannot be misinterpreted by software configured for another
   round.

2. **Generate the bootstrap operator's keypairs.** Generate a
   CometBFT consensus keypair, a Cosmos account keypair, and a
   Pallas keypair (see [Validator] for the role of each).

3. **Construct the genesis block.** Populate the genesis state
   with:
   - The chain identifier from step 1.
   - The vote manager singleton, set to an address controlled by
     the bootstrap operator (see [Bootstrap Operator]).
   - An initial balance for the vote manager account, in the
     chain's native token (`usvote`), sized to fund the planned
     validator set via subsequent authorized transfers.
   - A minimum ceremony validator count required before the EA
     key ceremony can proceed.
   - The bootstrap operator's own validator entry, bonded with
     consensus voting power and with its Pallas public key
     registered.
   - The standard Cosmos SDK module states (auth, bank, staking)
     as required by the Cosmos SDK runtime.

4. **Start the node.** Starting `svoted` begins block production
   and the chain transitions out of the genesis state.

The genesis state does not pre-populate voting rounds, nullifier
sets, tally results, or PIR data; these are all populated through
subsequent on-chain transactions during the voting round.

After the chain is producing blocks, the bootstrap operator
publishes the initial vote configuration document listing the
genesis node's public URL, so that joining validators and wallet
clients can find the network. See [Vote Configuration Publication].

### Onboarding Validators

A new validator joins the vote chain by following these steps:

1. **Acquire the vote chain binary.** Obtain `svoted` either from
   a published release of the reference implementation (see
   [Reference implementation]) or by building from source. Binary
   releases MUST be verified against a published checksum before
   use.

2. **Discover the network and initialize.** Read the vote
   configuration document for the target poll (see
   [Vote Configuration Publication]) to find at least one active
   validator. Fetch the chain's genesis block from that validator
   and initialize a local node directory.

3. **Generate keypairs.** Generate the validator's consensus
   keypair, account keypair, and Pallas keypair (see [Validator]).

4. **Sync the chain.** Start the node, connect to the active
   validators listed in the vote configuration document via
   CometBFT peer-exchange, and sync to the current height.

5. **Register in the vote configuration document.** Propose an
   update to the document adding the new validator's public URL.

6. **Wait for funding.** The vote manager reviews the proposed
   update, applies it, and funds the new validator's account via
   an authorized transfer (see [Bootstrap Operator] for the
   funding mechanism).

7. **Register on-chain.** Once funds are received, submit the
   validator registration transaction that wraps a standard
   Cosmos staking validator creation message together with the
   validator's Pallas public key, atomically binding the key to
   the new validator.

The amount transferred at step 6 determines the new validator's
consensus voting power. The vote chain rejects raw Cosmos staking
validator creation messages: every validator MUST be registered
through the wrapped form so that a Pallas public key is bound at
creation time. A validator without a registered Pallas key is
bonded for consensus but cannot participate in the EA ceremony
(see [Validator]).

The reference implementation (see [Reference implementation])
includes an automated `join.sh` script that performs the above
steps. The script is parameterized by the vote configuration
document URL; the same script is used for any poll and is not
specialized per poll.

### Nullifier Service

The nullifier service is an external service that lets voters
privately verify that their Orchard nullifiers are absent from
the Zcash mainnet nullifier set at the snapshot height, using
private information retrieval. A voter's PIR query reveals
neither which nullifier is being checked nor the answer to any
observer of the network.

The service is run by a nullifier service operator (see
[Nullifier Service Operator]) using the implementation referenced
in [Reference implementation]. The PIR construction and database
layout are specified in `draft-valargroup-nullifier-pir`
[^draft-pir].

The service operates as a three-stage pipeline:

1. **Ingest**: fetch the Zcash mainnet nullifier set up to the
   chosen snapshot height from a Zcash node and persist it to
   local storage.
2. **Export**: build the nullifier non-membership tree (an Indexed
   Merkle Tree as specified in
   `draft-valargroup-orchard-balance-proof` [^draft-balance-proof])
   and export the PIR database tiers as specified in
   `draft-valargroup-nullifier-pir` [^draft-pir]. The exported
   files allow the server to restart without rebuilding the tree
   from raw nullifiers.
3. **Serve**: accept PIR queries from voters and return encrypted
   responses over HTTP. The operator publishes the service URL by
   adding it to the vote configuration document (see
   [Vote Configuration Publication]).

The PIR client-server query and response wire format is not yet
specified in any normative document. See [Open Issues].

### Vote Configuration Publication

The vote manager publishes a vote configuration document for the
chain's voting round, in the format and via the publication
channel described in `draft-valargroup-shielded-voting-wallet-api`
[^draft-wallet-api]. Wallets and joining validators fetch the
document from that channel; the vote chain itself does not
provide a service-discovery endpoint.

The vote manager publishes the initial document once the genesis
validator is producing blocks. New validators and nullifier service
operators are added by proposing updates to the document, which the
vote manager reviews and applies; for validators this proposal is
automated by the join.sh flow described in [Onboarding Validators],
while nullifier service operators propose their entries directly.
The document is incremental — new entries are added without
removing earlier ones — and any active entry can serve as an entry
point for new joiners; there is no distinguished seed node.

Each voting round runs on its own vote chain with its own
publication channel. The vote manager announces the channel URL
out-of-band before the round opens, so that wallet implementers
can configure their wallets to fetch from it — either as a
bundled default or as a user-supplied setting. There is no
automated cross-poll discovery; a new poll requires the vote
manager to communicate the new channel to wallets and end users
through whatever distribution path they choose.

## Conducting a Voting Round

### Snapshot Configuration

A voting round is anchored to a Zcash mainnet snapshot: a specific
mainnet block height at which the eligible Orchard pool is
captured. The poll runner chooses this snapshot height subject
to the following constraint:

- The height MUST be at or after NU5 activation, since the
  protocol requires Orchard.

Choosing the snapshot height is the start of round setup, not a
single automatic action. The poll runner is responsible for the
following coordinated activities:

1. **Determine the snapshot's commitment values.** Compute the
   Orchard note commitment tree root ($\mathsf{nc}\_\mathsf{root}$)
   and the nullifier non-membership Indexed Merkle Tree root
   ($\mathsf{nullifier}\_\mathsf{imt}\_\mathsf{root}$) at the
   chosen height. These values are deterministic given the
   height; they are derived from Zcash mainnet state.

2. **Ensure the nullifier service has the snapshot's PIR
   database.** The poll runner coordinates with each nullifier
   service operator (see [Nullifier Service Operator]) so that
   their ingest and export pipelines (see [Nullifier Service])
   have run to the chosen height before the round opens, so
   wallets can query exclusion proofs against that snapshot.

3. **Use the values during chain bootstrap.**
   $\mathsf{nc}\_\mathsf{root}$ and
   $\mathsf{nullifier}\_\mathsf{imt}\_\mathsf{root}$ are passed
   into the genesis state (see [Genesis Validator Setup]) and
   into the voting round initialization transaction (see
   [Poll Creation]) so that on-chain verifiers and wallet
   clients use them as ZKP public inputs.

### Poll Creation

The vote manager initializes the chain's voting round by submitting
a transaction carrying the client-supplied subset of the `VoteRound`
structure specified in `draft-valargroup-shielded-voting-wallet-api`
[^draft-wallet-api]. The vote manager supplies `snapshot_height`,
`snapshot_blockhash`, `proposals_hash`, `vote_end_time`,
`nullifier_imt_root`, `nc_root`, `proposals`, `title`, and
`description`; the transaction's signer becomes the `creator` field
of the resulting `VoteRound`. The chain derives the remaining
fields (`vote_round_id`, `status`, `ea_pk`, `created_at_height`)
at inclusion or during the round lifecycle.

The chain rejects the transaction if the signer is not the current
vote manager, or if the `proposals` field violates the constraints
in [Proposals and Decisions].

The vote chain derives the 32-byte `vote_round_id` from the
transaction fields after inclusion, using the Poseidon construction
specified in the "Voting Round Identifier" section of
`draft-valargroup-shielded-voting`
[^draft-voting-protocol-vri]. The result is a Pallas field element
so that the round ID can enter ZKP circuits as a public input.

The round enters the **PENDING** state. The EA key ceremony (see
`draft-valargroup-ea-key-ceremony` [^draft-ceremony]) runs
automatically. On successful completion, the
round transitions to **ACTIVE**, the voting window opens, and the
transition timestamp is recorded as `ceremony_phase_start`. Clients use
`ceremony_phase_start` together with `vote_end_time` to compute the
last-moment buffer for submission timing, as specified in the
"Last-Moment Buffer" section of `draft-valargroup-submission-server`
[^draft-submission-server-lmb].

### Round Lifecycle

1. **PENDING**: round created, awaiting EA key ceremony.
2. **ACTIVE**: ceremony complete, voting window open. Voters may delegate,
   vote, and submit shares (see `draft-valargroup-voting-protocol`
   [^draft-voting-protocol]).
3. **TALLYING**: `vote_end_time` has passed. Validators submit
   partial decryptions, the chain combines them, and tally
   decryption runs automatically (see
   `draft-valargroup-ea-key-ceremony` [^draft-ceremony]). The
   chain enforces a bounded timeout on the TALLYING state: if a
   tally is not submitted within this timeout, the round
   auto-finalizes with no tally, preserving liveness.
4. **FINALIZED**: tally published and verifiable. A round that
   auto-finalized due to a TALLYING timeout publishes no tally.

## Coinholder Participation

For a Zcash coinholder to participate in a voting round, they
must satisfy an eligibility precondition and follow a wallet-
driven participation flow. The protocol details for each step
are specified in companion ZIPs; this section ties them together
from the coinholder's perspective.

### Eligibility

Voting weight derives from the value held in a coinholder's
Orchard notes at the round's snapshot height (see
[Snapshot Configuration]). Funds held in Sapling or transparent
pools at the snapshot height carry no voting weight; coinholders
who wish to participate with such funds MUST migrate them to
Orchard before the snapshot height.

### Wallet Setup

A wallet client obtains the vote configuration document for the
round (see [Vote Configuration Publication]), which lists the
vote chain endpoints, the nullifier service endpoints, and the
protocol versions in use. The configuration document schema and
the wallet-side validation rules are specified in
`draft-valargroup-shielded-voting-wallet-api`
[^draft-wallet-api].

### Participation Flow

For each Orchard note the coinholder uses as voting weight, the
wallet performs:

1. **Retrieve a non-membership proof.** Query a nullifier service
   endpoint to retrieve a Merkle non-membership proof for the
   note's alternate nullifier against the snapshot's
   `nullifier_imt_root`, as specified in
   `draft-valargroup-nullifier-pir` [^draft-pir].

2. **Submit a delegation transaction.** Construct a Delegation
   Proof asserting ownership of the eligible note without
   revealing which note it is, and submit the transaction to a
   vote chain endpoint listed in the vote configuration document.
   This produces a Vote Authority Note (VAN) on the vote
   commitment tree. The proof construction and the on-chain
   handling are specified in the Delegation Phase of
   `draft-valargroup-shielded-voting` [^draft-voting-protocol].

For each proposal the coinholder votes on, the wallet performs:

3. **Submit a vote transaction.** Construct a Vote Proof
   consuming the current VAN and producing a new VAN with the
   relevant proposal authority bit cleared, plus a Vote
   Commitment binding the chosen option, as specified in the
   Vote Phase of `draft-valargroup-shielded-voting`
   [^draft-voting-protocol].

4. **Submit encrypted vote shares.** Send the share payloads to
   submission server endpoints, which queue them and submit
   share reveal transactions on the coinholder's behalf at
   client-specified times. Share decomposition, server selection,
   and the last-moment buffer rules are specified in
   `draft-valargroup-submission-server`
   [^draft-submission-server].

After `vote_end_time`, the coinholder may verify the final tally
following [Verification and Auditing].

## Verification and Auditing

The vote chain is publicly readable. Any party running a full
node of the chain — a validator, the vote manager, or an
independent observer — can verify all aspects of a voting round
by replaying chain state and applying the verification
procedures defined in companion ZIPs.

This section uses the following procedures imported by
reference:

- **Out-of-Circuit Verification of the Claim proof** in
  `draft-valargroup-orchard-balance-proof`
  [^draft-balance-proof] — the abstract balance-proof primitive
  on which the Delegation Proof is built.
- **Out-of-Circuit Verification of the Delegation Proof, the
  Vote Proof, and the Vote Reveal Proof** in
  `draft-valargroup-shielded-voting` [^draft-voting-protocol].
- **Authentication Path** verification and the exclusion-range
  check for the nullifier non-membership tree, in
  `draft-valargroup-nullifier-pir` [^draft-pir].
- **Proof Verification** (DLEQ verification of partial
  decryptions) and the **Tally** procedure (Lagrange combination
  and plaintext recovery), in `draft-valargroup-ea-key-ceremony`
  [^draft-ceremony].

A full-node operator combines these procedures to verify a
voting round across three layers:

- **Per-transaction zero-knowledge proof verification.** Each
  delegation, vote, and share reveal transaction carries a Halo
  2 proof that is checked at inclusion against the
  Out-of-Circuit Verification rules in
  `draft-valargroup-shielded-voting`. Those rules apply the
  Claim proof verification from the balance proof ZIP and the
  Authentication Path / exclusion-range checks from the PIR
  ZIP transitively, so a single proof verification enforces the
  structural correctness of all three layers at once.

- **Nullifier set integrity.** The chain maintains three
  nullifier sets — governance nullifiers (from delegation), VAN
  nullifiers (from voting), and share nullifiers (from share
  reveals) — and rejects any transaction that would re-use a
  previously published nullifier. A full-node operator confirms
  set integrity by replaying every accepted transaction and
  checking that no nullifier appears twice.

- **Tally correctness.** A full-node operator re-aggregates the
  encrypted share ciphertexts per (`proposal_id`, `vote_decision`)
  from the on-chain share reveal transactions, applies the DLEQ
  Proof Verification to each stored partial decryption,
  re-derives the Lagrange combination, and confirms the
  decrypted aggregate following the Tally procedure in
  `draft-valargroup-ea-key-ceremony`.

Because every input to verification — proofs, nullifiers,
ciphertexts, and partial decryptions — is stored on the public
vote chain, no full-node operator needs to trust any other
participant. A round that auto-finalized due to a TALLYING
timeout (see [Round Lifecycle]) verifies as having no tally;
this is itself a verifiable property of the chain state.


# Rationale

**Separate vote chain (not Zcash mainnet)**: the vote chain is purpose-built
for governance with ZKP-optimized state transitions (Poseidon hashing, custom
transaction types). Zcash mainnet's transaction throughput and scripting model
are not designed for interactive multi-phase voting protocols.

**Orchard-only snapshots**: the voting protocol is built on Orchard's
circuit-friendly primitives (Poseidon hashing, Pallas curve). Sapling
and transparent pools use incompatible cryptographic constructions.
The corresponding requirement on coinholders is stated in
[Eligibility].

**Cosmos SDK**: provides a mature BFT consensus engine (CometBFT),
validator lifecycle management (bonding, jailing for missed blocks or
missed ceremony acknowledgements, consensus power distribution), and a
transaction pipeline that can be extended with custom message types and
ante handlers for ZKP verification. The alternative — building a chain
from scratch — would duplicate well-tested consensus infrastructure.

**Funding equals voting power**: bonding serves three purposes: it
determines which validators participate in consensus and the EA key
ceremony (and thus can decrypt the tally), it enables jailing of
inactive validators who miss blocks or ceremony acknowledgements, and
an even funding split gives each validator a roughly equal probability
of becoming the block proposer — not important for correctness, but
important for liveness.

**Automated validator onboarding**: `join.sh` eliminates manual
coordination between the bootstrap operator and joining validators. The
self-registration, admin-approval, and auto-bonding flow allows the
network to grow without requiring validators to build from source or
understand Cosmos SDK tooling.

**Vote manager reassignment**: only the current vote manager can
transfer the role (via `MsgSetVoteManager`). This is a deliberate
single-party control: the vote manager can create rounds but cannot
forge votes, and the worst-case mitigation for a compromised vote
manager is to spin up a new chain.


# Reference implementation

- [^ref-vote-sdk] — Cosmos SDK vote chain (`svoted`) implementing
  the chain-side state, ceremony, tally, and submission server.
- [^ref-nullifier-pir] — PIR server and client for privately
  retrieving nullifier non-membership proofs.


# Open Issues

- **Role consolidation**: evaluate whether the bootstrap operator and
  vote manager concepts (already the same keypair at genesis; see
  [Bootstrap Operator]) merit separate treatment in the specification.
- **PIR client-server wire format**: the query and response wire
  format used between wallet clients and the nullifier service
  (see [Nullifier Service]) is not currently specified in any
  ZIP. The PIR draft scopes its outer transport out of remit, and
  the wallet API ZIP describes only the endpoint URLs. A normative
  spec home is needed before wallet clients and nullifier service
  servers from independent implementations can interoperate.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^draft-balance-proof]: [Draft ZIP: Orchard Proof-of-Balance](draft-valargroup-orchard-balance-proof.md)

[^draft-voting-protocol]: [Draft ZIP: Zcash Shielded Voting Protocol](draft-valargroup-shielded-voting.md)

[^draft-voting-protocol-vri]: [Draft ZIP: Zcash Shielded Voting Protocol, Section: Voting Round Identifier](draft-valargroup-shielded-voting.md#voting-round-identifier)

[^draft-ceremony]: [Draft ZIP: Election Authority Key Ceremony](draft-valargroup-ea-key-ceremony.md)

[^draft-pir]: [Draft ZIP: Private Information Retrieval for Nullifier Exclusion Proofs](draft-valargroup-nullifier-pir.md)

[^draft-submission-server]: [Draft ZIP: Vote Share Submission Server](draft-valargroup-submission-server.md)

[^draft-wallet-api]: [Draft ZIP: Shielded Voting Wallet API](draft-valargroup-shielded-voting-wallet-api.md)

[^draft-submission-server-lmb]: [Draft ZIP: Vote Share Submission Server, Section: Last-Moment Buffer](draft-valargroup-submission-server.md#last-moment-buffer)

[^draft-onchain-voting]: [Draft ZIP: On-chain Accountable Voting](draft-ecc-onchain-accountable-voting.md)

[^cosmos-staking]: [Cosmos SDK `x/staking` module documentation](https://docs.cosmos.network/main/build/modules/staking)

[^ref-vote-sdk]: [valargroup/vote-sdk: Cosmos SDK vote chain for shielded voting](https://github.com/valargroup/vote-sdk)

[^ref-nullifier-pir]: [valargroup/vote-nullifier-pir: PIR system for nullifier non-membership proofs](https://github.com/valargroup/vote-nullifier-pir)
