::

  ZIP: Unassigned {numbers are assigned by ZIP editors}
  Title: Shielded Labs Crosslink v1: Protocol Overview and Architecture
  Owners: Nate Wilcox <nate@shieldedlabs.com>
  Credits: Daira-Emma Hopwood
           Jack Grigg
           Kris Nuttycombe
  Status: Draft
  Category: Informational
  Created: 2026-04-08
  License: MIT
  Discussions-To: TBD (no specific discussion thread yet)


Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [#BCP14]_ when, and only
when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [#protocol-networks]_.

The terms below are to be interpreted as follows:

Zcash Trailing Finality Layer (TFL)
  An initiative by the former Electric Coin Company (ECC) to augment the
  Zcash Proof-of-Work consensus with a Proof-of-Stake finality layer,
  documented in the TFL book [#tfl-book]_. The TFL initiative produced the
  theoretical design basis for Shielded Labs Crosslink v1.

Crosslink Consensus Construction from the TFL Book (CCC-TFLv2)
  The abstract hybrid consensus construction documented in the TFL book
  [#tfl-book]_, version 2. CCC-TFLv2 describes how to integrate a best-chain
  (PoW) protocol with a BFT (PoS) protocol and provides a formal security
  analysis of the resulting hybrid. This construction is the direct theoretical
  basis for ``CCC-SL``.

Shielded Labs Crosslink v1
  The complete protocol and working implementation produced by the Shielded
  Labs non-profit, extending CCC-TFLv2 with additional practical and
  theoretical design details necessary for a production deployment. Shielded
  Labs Crosslink v1 is a superset of the TFL in several respects: it includes
  a fully prototyped working implementation, and it extends the older TFL
  design with additional components (``CFP-SL``, ``RSM-SL-v1``, ``CNTP-SL``)
  that are not fully specified in the TFL book. This ZIP and its companions
  specify the protocols of Shielded Labs Crosslink v1.

Crosslink Consensus Construction from Shielded Labs (CCC-SL)
  The abstract hybrid consensus construction that is the core of Shielded Labs
  Crosslink v1, inspired by CCC-TFLv2. CCC-SL treats the Zcash PoW protocol
  and ``CFP-SL`` as somewhat opaque subprotocols, each performing their own
  consensus, while requiring specific cross-referencing modifications to each.
  CCC-SL is specified in ZIP [#zip-ccc-sl]_.

Crosslink Finalization Protocol from Shielded Labs (CFP-SL)
  The Proof-of-Stake BFT protocol used as the finalization subprotocol in
  Shielded Labs Crosslink v1, with "adaptation modifications" to interface
  with ``CCC-SL``. ``CFP-SL`` provides Crosslink Finality by running Byzantine
  Fault Tolerant consensus over snapshots of the Zcash PoW chain.

Roster State Module (RSM)
  An abstract interface required by ``CFP-SL``. The RSM provides the latest
  ``Active Roster Mapping`` from cryptographically self-authenticating vote
  verifier identities to their associated voting weights. The Active Roster
  Mapping also defines ``Roster Evolution Rules``, which are a subset of
  ledger state evolution rules composing Zcash's ledger state consensus.

RSM-SL-v1
  The specific instantiation of the Roster State Module for Shielded Labs
  Crosslink v1. RSM-SL-v1 defines all staking rules that users interact with
  directly: staking ZEC to a Finalizer identity, unbonding periods, amount
  quantization, slashing conditions, and related rules.

Crosslink Network Transport Protocol from Shielded Labs (CNTP-SL)
  The network transport layer for Shielded Labs Crosslink v1, enabling
  ``CFP-SL`` to safely and efficiently disseminate finality updates.
  ``CNTP-SL`` provides pragmatic protections against network threats (DoS,
  message tampering, etc.) and improvements over the status quo Zcash p2p
  protocol, including transport-layer encryption, faster block and ledger
  syncing, and firewall traversal.

Active Roster Mapping
  A mapping from Finalizer vote-verifier public keys to their associated
  voting weights, maintained by the Roster State Module. This mapping defines
  which parties are authorized to participate in ``CFP-SL`` voting at a given
  point in the ledger history.

Finalizer
  A participant in the ``CFP-SL`` subprotocol who holds an active entry in
  the Active Roster Mapping and participates in BFT consensus to finalize
  PoW blocks.

Roster Evolution Rules
  The subset of ledger state evolution rules (within Zcash's consensus) that
  govern how the Active Roster Mapping changes over time: new stakers joining,
  unstaking and unbonding, slashing, and similar events.

Crosslink Finality
  The finality property provided by Shielded Labs Crosslink v1, as defined in
  the zebra-crosslink design documentation [#zebra-crosslink-terminology]_.
  Crosslink Finality has five key characteristics:

  1. **Accountable**: Safety violations can be attributed to specific
     Finalizers, enabling slashing penalties.
  2. **Irreversible**: Once a block achieves Crosslink Finality, it cannot be
     reverted by the protocol under any circumstances permitted by the security
     assumptions.
  3. **Objectively verifiable**: Any third party with access to the chain data
     can independently verify whether a given block has achieved Crosslink
     Finality without trusting any particular node.
  4. **Globally consistent**: All honest nodes that agree on the chain data
     agree on which blocks have achieved Crosslink Finality.
  5. **Asymmetric cost-of-attack defense**: An adversary seeking to violate
     Crosslink Finality must expend significantly more resources than honest
     participants spend to maintain it.

Trailing Finality
  A protocol property wherein transactions become final some time after first
  appearing in PoW blocks.

Bounded Availability
  The property that the best-chain ledger does not grow unboundedly ahead of
  the finalized ledger during a finality stall, preventing indefinite
  accumulation of unfinalized transactions.

Finality Gap
  The number of best-chain (PoW) blocks that have not yet been finalized by
  ``CFP-SL`` at a given time.

Stalled Mode
  A mode entered when the finality gap exceeds a threshold ``L``, indicating
  an exceptional or emergency condition. In Stalled Mode, PoW block producers
  are constrained by the ``CCC-SL`` rules to produce only stalled blocks.


Abstract
========

This ZIP describes the high-level design goals, motivations, and architecture
of **Shielded Labs Crosslink v1**, a complete protocol and implementation
produced by the Shielded Labs non-profit to add Crosslink Finality to the
Zcash network.

Shielded Labs Crosslink v1 builds on the Zcash Trailing Finality Layer (TFL)
initiative and its ``CCC-TFLv2`` hybrid construction, extending it into a
deployable system with a fully specified finalization protocol (``CFP-SL``),
staking rules (``RSM-SL-v1``), and network transport layer (``CNTP-SL``). The
core hybrid consensus mechanism is ``CCC-SL``, which is formally specified in
ZIP [#zip-ccc-sl]_.

This document is intended as the top-level overview for the entire Shielded
Labs Crosslink v1 protocol suite. It does not itself specify consensus rules,
but provides the rationale, component definitions, architecture diagram, and
cross-references needed to understand and evaluate the companion ZIPs.


Background: The TFL Initiative and CCC-TFLv2
=============================================

The Zcash Trailing Finality Layer (TFL) was an initiative by the former
Electric Coin Company (ECC) to introduce Crosslink Finality to Zcash through
a hybrid Proof-of-Work / Proof-of-Stake consensus design. The TFL design book
[#tfl-book]_ documents this initiative and produces the Crosslink Consensus
Construction (version 2, ``CCC-TFLv2``), which provides the theoretical
framework and security analysis for integrating a PoW chain with a BFT
finality layer.

Shielded Labs Crosslink v1 is a successor to the TFL initiative, produced by
the Shielded Labs non-profit. While ``CCC-TFLv2`` provides the abstract
consensus foundation, many practical design and implementation details were
left unspecified in the TFL book. Shielded Labs has extended the TFL work in
several important ways:

* **CCC-SL**: A fully specified consensus construction closely following
  CCC-TFLv2 but with practical adaptations and Zcash-specific details.

* **CFP-SL**: A complete specification and prototype implementation of the
  BFT finalization protocol (the ``Π_bft`` component left abstract in
  CCC-TFLv2).

* **RSM-SL-v1**: A full specification of the staking rules and roster
  management (the "PoS staking mechanics" left unspecified in CCC-TFLv2).

* **CNTP-SL**: A network transport layer for finality updates (entirely new
  relative to CCC-TFLv2, which does not address the network layer).

* **Working prototype**: A complete prototype implementation based on Zebra
  [#zebra-crosslink]_ demonstrating all components working together.

Readers who wish to understand the theoretical foundations of the consensus
construction are encouraged to read the TFL book [#tfl-book]_ alongside these
ZIPs, with the understanding that Shielded Labs Crosslink v1 may use different
terminology and make different design trade-offs in some areas.


Motivation
==========

Probabilistic vs. Crosslink Finality
--------------------------------------

The current Zcash consensus protocol uses Nakamoto-style Proof-of-Work, which
provides only *probabilistic* finality: a transaction confirmed at depth ``k``
can theoretically be reversed by an adversary with sufficient hash rate.
Although deep reorgs are costly and increasingly unlikely as depth increases,
they are not impossible. This limitation has several practical consequences:

* **Exchange and service delays**: Exchanges and other services must wait for
  many confirmations before crediting deposits, increasing friction for users.

* **Bridge trust assumptions**: Cross-chain bridges and atomic swaps must
  account for reorg risk, often requiring conservative confirmation depths or
  additional trust assumptions.

* **Wallet complexity**: Wallets must communicate uncertainty about
  transaction finality to users, complicating UX.

Crosslink Finality — the property that a finalized transaction *cannot* be
reversed by the protocol — removes these limitations. Any system that can
rely on Crosslink Finality can offer faster, safer service with simpler
reasoning about transaction status.

Why Proof-of-Stake for Finality?
---------------------------------

Proof-of-Stake (PoS) consensus protocols using Byzantine Fault Tolerant (BFT)
algorithms are well-established approaches for providing Crosslink Finality.
Tendermint, PBFT, Casper, and related protocols all achieve this goal with
strong theoretical foundations. Integrating a BFT PoS layer into Zcash as a
*finality layer* — rather than replacing PoW entirely — allows the ecosystem to:

1. **Retain PoW security**: The PoW chain continues to provide its well-understood
   liveness and censorship-resistance properties.

2. **Add PoS staking rewards**: ZEC holders can participate in network security
   by staking ZEC (directly or by delegating to a Finalizer), earning protocol
   rewards.

3. **Minimize disruption**: The transition preserves existing wallets, services,
   and tooling with minimal required changes.

4. **Enable future evolution**: A successful hybrid PoW/PoS transition builds
   confidence and infrastructure for potential future full PoS transitions.

Why CCC-SL Rather Than Snap-and-Chat?
---------------------------------------

An earlier candidate for the hybrid construction was the Snap-and-Chat
protocol from the Ebb-and-Flow paper [#ebb-and-flow]_. The TFL initiative
identified several issues with Snap-and-Chat [#tfl-book]_, motivating the
development of CCC-TFLv2 (and by extension CCC-SL):

* Snap-and-Chat's "sanitization" step complicates transaction finality
  semantics in ways that interact poorly with Zcash's shielded transaction
  model.

* Snap-and-Chat does not implement bounded availability, which is a safety
  property important for protecting users during finality stalls.

* The security analysis of CCC-TFLv2 / CCC-SL is more rigorous and complete
  than what is available for Snap-and-Chat.

The Case for Bounded Availability
-----------------------------------

A key design goal of CCC-SL is *bounded availability*: preventing the PoW
chain from growing unboundedly ahead of the finalized chain during a finality
stall. Without this property, a period of ``CFP-SL`` failure could allow
unbounded accumulation of unfinalized transactions. When ``CFP-SL`` recovered,
users would face uncertainty about which transactions would ultimately be
finalized and which would be reversed.

Bounded availability addresses this by entering "Stalled Mode" when the
finality gap exceeds a threshold ``L``. In Stalled Mode, PoW block producers
are constrained to produce only "stalled blocks" — blocks that do not include
new user transactions spending into the unfinalized zone. This limits user
exposure during finalization failures.


Requirements
============

Shielded Labs Crosslink v1 MUST satisfy the following requirements:

Finality Requirements
---------------------

* The protocol MUST provide Crosslink Finality for transactions included in
  finalized blocks.

* The expected time-to-finality SHOULD be below 30 minutes under normal
  network conditions.

* The protocol MUST maintain Local Finalization Linearity: from any single
  node's perspective, the locally-finalized chain can only grow forward, never
  roll back.

Safety Requirements
--------------------

* The cost-of-attack for a 1-hour rollback of the PoW chain MUST NOT be
  reduced compared to the current Zcash consensus protocol, given a reasonably
  rigorous security argument.

* The cost-of-attack to halt the chain MUST be larger than the 24-hour revenue
  of PoW mining rewards, given a reasonably rigorous security argument.

Backward Compatibility Requirements
-------------------------------------

* All currently supported wallet operations (addresses, payment flow, ZEC
  transfers, backup/restore, etc.) MUST continue to function without change
  through the protocol transition, assuming wallets rely on the lightwalletd
  protocol or a full-node API.

* Mining pool operators relying on zcashd-compatible ``GetBlockTemplate``
  MUST NOT be required to make software changes, with the narrow exception of
  software that hardcodes block reward amounts rather than deriving them from
  ``GetBlockTemplate``.

* The ZEC supply cap and issuance schedule MUST be preserved.

* Block explorers that display transaction and block information MUST continue
  to function with the same user experience through the transition.

Bounded Availability Requirements
-----------------------------------

* ``CCC-SL`` MUST implement bounded availability: the finality depth of any
  non-stalled bc-block MUST NOT exceed ``L``, where ``L`` is a protocol
  parameter. (Stalled blocks may exist at any finality depth; Bounded
  Availability bounds the depth of *transaction-carrying* blocks only.)

* ``L`` MUST be set significantly larger than the bc-confirmation-depth ``σ``,
  with a minimum of ``L ≥ 2σ``.

Staking Requirements
--------------------

* ZEC holders MUST be able to earn protocol rewards by operating as Finalizers
  or delegating ZEC to Finalizers via ``RSM-SL-v1``.

* Finalizers MUST NOT have discretionary control over delegated funds; they
  MUST NOT be able to steal delegated ZEC.

* The protocol MUST allow slashing of Finalizer stake for provable misbehavior.


Non-requirements
================

The following are explicitly out of scope for Shielded Labs Crosslink v1:

* Minimizing time-to-finality as a primary goal over other considerations such
  as protocol simplicity or impact on existing use cases.

* In-protocol liquid staking derivatives.

* Maximizing the Finalizer count ceiling. The design may have a relatively low
  ceiling of hundreds to a few thousand Finalizers.

* Reducing overall network energy usage (this cannot be achieved for a
  hybrid PoW/PoS design without loss of security).


Specification
=============

Protocol Component Overview
-----------------------------

Shielded Labs Crosslink v1 is composed of five major protocol components that
interact with the existing Zcash PoW consensus and ledger rules:

1. **CCC-SL** — the hybrid consensus construction at the core of Crosslink v1.
2. **CFP-SL** — the BFT PoS finalization protocol run by Finalizers.
3. **RSM-SL-v1** — the Roster State Module that manages the Active Roster
   Mapping and staking rules.
4. **CNTP-SL** — the network transport layer for finality updates.
5. **Zcash PoW consensus** (existing, with minimal CCC-SL modifications).

Component Diagram
-----------------

The following diagram illustrates the components of Shielded Labs Crosslink v1
and their interactions. Arrows indicate data flow or dependency::

                 ┌──────────────────────────────────────────────────────────┐
                 │              Shielded Labs Crosslink v1                  │
                 │                                                          │
   ┌──────────┐  │  ┌────────────────────────────────────────────────────┐  │
   │  Zcash   │  │  │    CCC-SL  (Crosslink Consensus Construction       │  │
   │  PoW     │◄─┼──│             from Shielded Labs)                    │  │
   │  (Π_bc)  │──┼─►│  • context_bft field in bc-block headers          │  │
   └──────────┘  │  │  • Finality gap / Stalled Mode enforcement        │  │
        ▲        │  │  • Locally finalized chain (localfin)             │  │
        │        │  │  • Locally bounded-available chain (localba)      │  │
        │        │  └──────────────────────┬─────────────────────────────┘  │
        │        │                         │                                 │
        │        │  ┌──────────────────────▼─────────────────────────────┐  │
        │        │  │    CFP-SL  (Crosslink Finalization Protocol        │  │
        │        │  │             from Shielded Labs)                    │  │
        └────────┼──│  • BFT PoS consensus over PoW chain snapshots     │  │
                 │  │  • headers_bc in bft-proposals and bft-blocks     │  │
                 │  │  • Final Agreement property                       │  │
                 │  │  • Adaptation modifications for CCC-SL interface  │  │
                 │  └────────────┬──────────────────┬────────────────────┘  │
                 │               │                  │                        │
                 │  ┌────────────▼───────────┐  ┌──▼──────────────────────┐ │
                 │  │  RSM-SL-v1             │  │  CNTP-SL                │ │
                 │  │  (Roster State Module) │  │  (Crosslink Network     │ │
                 │  │                        │  │   Transport Protocol)   │ │
                 │  │  • Active Roster       │  │                         │ │
                 │  │    Mapping             │  │  • Finality update      │ │
                 │  │  • Roster Evolution    │  │    dissemination        │ │
                 │  │    Rules               │  │  • Transport encryption │ │
                 │  │  • Staking rules:      │  │  • Faster sync          │ │
                 │  │    - ZEC delegation    │  │  • Firewall traversal   │ │
                 │  │    - Unbonding periods │  │  • DoS protection       │ │
                 │  │    - Slashing          │  │                         │ │
                 │  │    - Quantization      │  │                         │ │
                 │  └────────────────────────┘  └─────────────────────────┘ │
                 │                                                           │
                 └───────────────────────────────────────────────────────────┘

Component Descriptions
-----------------------

CCC-SL: Crosslink Consensus Construction from Shielded Labs
  CCC-SL is the core hybrid consensus construction specifying how the Zcash
  PoW subprotocol and ``CFP-SL`` interact. It is closely based on CCC-TFLv2
  and provides the following key mechanisms:

  * **Cross-referencing fields**: Each PoW block header includes a
    ``context_bft`` field referencing a ``CFP-SL`` block; each ``CFP-SL``
    proposal includes a ``headers_bc`` field with ``σ`` PoW block headers.
    These fields allow each chain to objectively verify properties of the
    other.

  * **Locally finalized chain**: Each node maintains a locally finalized
    bc-chain (``localfin``) that only ever advances forward, never rolling
    back.

  * **Locally bounded-available chain**: Each node also maintains a confirmed
    (but not necessarily finalized) bc-chain view (``localba``) at a chosen
    confirmation depth.

  * **Stalled Mode**: When the finality gap (number of unfinalized PoW blocks)
    exceeds ``L``, CCC-SL enforces Stalled Mode, constraining PoW block
    producers to produce only stalled blocks.

  CCC-SL is formally specified in ZIP [#zip-ccc-sl]_.

CFP-SL: Crosslink Finalization Protocol from Shielded Labs
  CFP-SL is the BFT Proof-of-Stake consensus protocol run by Finalizers to
  provide Crosslink Finality. It operates over snapshots of the Zcash PoW chain:
  each CFP-SL proposal commits to a sequence of PoW block headers, and
  finalized CFP-SL blocks determine which PoW blocks are considered final.

  CFP-SL is a modified version of an off-the-shelf BFT protocol, with
  adaptation modifications to:

  * Include ``headers_bc`` in proposals and blocks (required by CCC-SL).
  * Consult the Active Roster Mapping from ``RSM-SL-v1`` for voter weights.
  * Verify PoW header validity before voting on proposals.

  The specific off-the-shelf BFT algorithm used by CFP-SL will be specified in
  a companion ZIP. CFP-SL must satisfy the **Final Agreement** property: in any
  execution where safety assumptions hold, all honest nodes' views of finalized
  CFP-SL blocks are consistent.

RSM-SL-v1: Roster State Module (Shielded Labs v1)
  RSM-SL-v1 is the specific instantiation of the abstract Roster State Module
  interface required by CFP-SL. It maintains the Active Roster Mapping that
  determines which Finalizer identities are authorized to vote in CFP-SL and
  with what weight.

  RSM-SL-v1 defines all staking rules that users interact with directly,
  including:

  * **ZEC delegation**: Staking ZEC to a Finalizer vote-verifier identity.
  * **Unbonding periods**: The mandatory waiting period before staked ZEC can
    be withdrawn after unbonding.
  * **Amount quantization**: Minimum and increment sizes for staking amounts.
  * **Slashing**: Conditions and amounts for penalizing provably misbehaving
    Finalizers, enforced as Roster Evolution Rules.
  * **Roster Evolution Rules**: Ledger state evolution rules that govern how
    the Active Roster Mapping changes over time as part of Zcash's broader
    ledger state consensus.

  RSM-SL-v1 is specified in ZIP [#zip-rsm-sl-v1]_.

CNTP-SL: Crosslink Network Transport Protocol from Shielded Labs
  CNTP-SL is the network transport layer providing the communication substrate
  for Shielded Labs Crosslink v1. Although not strictly logically required for
  a correct Crosslink deployment (any sufficiently reliable broadcast network
  would suffice), CNTP-SL provides important practical properties:

  * **Finality update dissemination**: Efficient propagation of CFP-SL blocks
    and finality updates to all network participants, including light clients.
  * **DoS protection**: Network-layer defenses against denial-of-service
    attacks targeting the finalization protocol.
  * **Transport-layer encryption**: Authenticated, encrypted communication
    between Crosslink v1 nodes.
  * **Faster sync protocols**: Improved block and ledger synchronization
    compared to the status quo Zcash p2p protocol.
  * **Firewall traversal**: Support for nodes behind NAT/firewalls.

  CNTP-SL will be specified in a companion ZIP.

Interaction Between Components
--------------------------------

The components of Shielded Labs Crosslink v1 interact as follows:

1. **Zcash PoW ↔ CCC-SL**: CCC-SL augments PoW block validity rules with
   the ``context_bft`` cross-reference requirement and the Stalled Mode
   policy. Honest PoW block producers consult their CFP-SL node to determine
   the current BFT chain tip for ``context_bft``.

2. **CCC-SL ↔ CFP-SL**: CCC-SL defines the interface requirements CFP-SL must
   satisfy (Final Agreement, the ``headers_bc`` format, and the
   ``bftLastFinal`` function). CFP-SL produces finalized blocks that CCC-SL
   uses to compute ``localfin``. CFP-SL proposals include PoW block headers
   that CCC-SL verifies.

3. **CFP-SL ↔ RSM-SL-v1**: CFP-SL queries RSM-SL-v1 for the current Active
   Roster Mapping to determine voter weights and authorized identities for each
   round of BFT consensus. RSM-SL-v1's Roster Evolution Rules are enforced as
   part of Zcash ledger state transitions, so the Active Roster Mapping changes
   as the PoW ledger evolves.

4. **CFP-SL ↔ CNTP-SL**: CNTP-SL provides the network transport over which
   CFP-SL messages (proposals, votes, finalized blocks) are communicated
   between Finalizers and propagated to all network participants.

5. **Zcash PoW ↔ RSM-SL-v1**: The Roster Evolution Rules in RSM-SL-v1 are
   expressed as standard Zcash ledger state evolution rules, enforced by the
   PoW consensus mechanism. Staking and unstaking transactions appear on the
   PoW chain and update the Active Roster Mapping.

Relationship to the Existing Zcash Protocol
---------------------------------------------

The Zcash PoW subprotocol within Shielded Labs Crosslink v1 is closely related
to the existing Zcash NU5/NU6 consensus protocol but is not identical. The
CCC-SL construction requires the following changes (specified in detail in ZIP
[#zip-ccc-sl]_):

* Each PoW block header MUST include a ``context_bft`` field referencing a
  CFP-SL block, committing the PoW block producer to their view of the
  finalization chain.

* PoW block validity rules are extended with contextual checks enforcing the
  finality gap constraint and Stalled Mode policy.

The RSM-SL-v1 staking rules add new transaction types and ledger state to the
Zcash protocol, specified in ZIP [#zip-rsm-sl-v1]_.

Network Upgrade Mechanism
--------------------------

Shielded Labs Crosslink v1 would be deployed via the existing Zcash network
upgrade mechanism [#zip-0200]_ as a consensus rule change. The precise
activation height(s) will be determined in subsequent process ZIPs once all
component specifications are finalized.

Reward Distribution
--------------------

Activating Shielded Labs Crosslink v1 requires adjusting the Zcash block
reward to provide rewards to Finalizers (via RSM-SL-v1) while maintaining the
existing ZEC supply schedule. The specific reward allocation between PoW miners
and Finalizers is not specified in this ZIP; it will be addressed in a separate
funding ZIP.

The ZEC supply cap of 21 million ZEC and the overall issuance schedule MUST
be preserved.


Security Considerations
=======================

Hybrid Protocol Security
-------------------------

The security of Shielded Labs Crosslink v1 depends on the security of both the
Zcash PoW subprotocol and ``CFP-SL``, as well as the correctness of ``CCC-SL``.
The CCC-SL specification (ZIP [#zip-ccc-sl]_) includes a security analysis
establishing the key properties: Crosslink Finality, Prefix Consistency, and
Bounded Availability.

CFP-SL Failure
---------------

If ``CFP-SL`` experiences a safety failure (e.g., due to more than one-third
of staked weight being controlled by adversarial Finalizers), the CCC-SL
construction's finalization safety hazard detection will record the event. The
bounded availability property limits the damage from CFP-SL liveness failures
by entering Stalled Mode when the finality gap grows too large.

PoW Protocol Failure
---------------------

If the Zcash PoW subprotocol experiences a deep reorg, but CFP-SL has not yet
finalized the affected blocks, CCC-SL will simply not finalize those blocks. If
the reorg affects already-finalized blocks, the finalization safety hazard
detection will record the event — but such an event can only occur if safety
assumptions about CFP-SL (e.g., that fewer than one-third of staked weight is
adversarial) are also violated.

Staked ZEC Risk
---------------

ZEC staked to Finalizers via RSM-SL-v1 may be subject to slashing penalties
for provable misbehavior. The protocol design MUST ensure that slashing
penalties cannot be imposed on honest Finalizers, and that the slashing
conditions and amounts are deterministic and auditable.

Privacy Considerations
-----------------------

Shielded Labs Crosslink v1 introduces new on-chain data (CFP-SL blocks,
Finalizer votes, cross-references between chains, and staking transactions).
Care must be taken to ensure that this new data does not leak information about
shielded transactions. The privacy implications of Finalizer identity and
staking is analyzed in ZIP [#zip-rsm-sl-v1]_.


Reference Implementation
========================

A complete prototype implementation of Shielded Labs Crosslink v1 is being
developed based on Zebra in the ``zebra-crosslink`` repository [#zebra-crosslink]_
and integrated in the ``crosslink_monolith`` repository [#crosslink-monolith]_.
These implementations are experimental and should not be used in production.


Appendix: Divergences Between Reference Sources
================================================

The Shielded Labs Crosslink v1 ZIPs draw on three main reference sources:

1. **The TFL book** [#tfl-book]_ — the original ECC design document specifying
   ``CCC-TFLv2``.
2. **The zebra-crosslink design book** [#zebra-crosslink-cl2]_ — Shielded Labs'
   working design documentation, which is based on the TFL book but records
   intentional divergences.
3. **These ZIPs** (this document and the CCC-SL construction ZIP) — the formal
   protocol specifications for Shielded Labs Crosslink v1.

The zebra-crosslink design book ``book/src`` is treated as the authoritative
source for terminology and design decisions when sources diverge. The following
known divergences exist between these sources:

Finality Terminology
---------------------

* **TFL book** uses "Assured Finality" as the name of the formal safety
  property of the hybrid construction.
* **zebra-crosslink** ``security-properties.md`` [#zebra-crosslink-security]_
  refers to the same concept as "Irreversible Finality".
* **zebra-crosslink** ``terminology.md`` [#zebra-crosslink-terminology]_
  defines "Crosslink Finality" as the user-facing name for this property, with
  five defining characteristics (accountable, irreversible, objectively
  verifiable, globally consistent, asymmetric cost-of-attack defense).
* **These ZIPs** adopt "Crosslink Finality" as the primary term, following
  ``terminology.md`` as the authoritative source.

Stalled Mode
------------

* **CCC-TFLv2** (TFL book) and **CCC-SL** (these ZIPs) include Stalled Mode:
  when the finality depth exceeds ``L``, bc-block producers MUST produce only
  stalled blocks (blocks that do not include new unfinalized-output-spending
  transactions).
* **zebra-crosslink** explicitly omits Stalled Mode from its current design.
  The ``cl2-construction.md`` file in the zebra-crosslink design book contains
  a prominent warning: "The ``zebra-crosslink`` design in this book diverges
  from this text by *not* including 'Stalled Mode' rules."
* **These ZIPs** retain Stalled Mode from CCC-TFLv2, as it is a key component
  of the Bounded Availability property. This divergence from the current
  zebra-crosslink implementation is intentional and will need to be resolved
  before deployment.

``finality_depth`` Naming
--------------------------

* **TFL book** defines ``finality_depth(H)`` as the height of ``H`` minus the
  height of ``snapshot(LF(H))``, and uses ``finality_depth(H) > L`` as the
  condition for Stalled Mode.
* **These ZIPs** use the equivalent expression
  ``tip_height(H) - fin_height(H) > L``, where ``fin_height(H)`` is the
  height of ``candidate(H)``. The quantity ``candidate(H)`` is closely
  related to ``snapshot(LF(H))`` via the ``lastCommonAncestor`` function.
  The two formulations are equivalent in normal operation.

Construction Name
-----------------

* **TFL book** and **zebra-crosslink** refer to the hybrid construction as
  "Crosslink 2" (or "CL2").
* **These ZIPs** use "CCC-SL" (Crosslink Consensus Construction from Shielded
  Labs) to distinguish the Shielded Labs adaptation from the abstract
  CCC-TFLv2 construction.


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#protocol] `Zcash Protocol Specification, Version 2022.3.8 or later <protocol/protocol.pdf>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <zip-0200.rst>`_
.. [#zip-ccc-sl] `ZIP [Unassigned]: CCC-SL: Crosslink Consensus Construction from Shielded Labs <draft-shieldedlabs-crosslink-construction.rst>`_
.. [#zip-rsm-sl-v1] `ZIP [Unassigned]: RSM-SL-v1: Crosslink Ledger State and Ledger Mutations <draft-shieldedlabs-crosslink-ledger-state.rst>`_
.. [#tfl-book] `Zcash Trailing Finality Layer Design Book <https://electric-coin-company.github.io/tfl-book/>`_
.. [#ebb-and-flow] `Ebb-and-Flow Protocols: A Resolution of the Availability-Finality Dilemma. David Neu, Joachim Neu, Ertem Nusret Tas, David Tse. <https://eprint.iacr.org/2020/1091.pdf>`_
.. [#zebra-crosslink] `ShieldedLabs zebra-crosslink repository <https://github.com/ShieldedLabs/zebra-crosslink>`_
.. [#crosslink-monolith] `ShieldedLabs crosslink_monolith repository <https://github.com/ShieldedLabs/crosslink_monolith>`_
.. [#zebra-crosslink-terminology] `Shielded Labs zebra-crosslink design book: Terminology <https://github.com/ShieldedLabs/zebra-crosslink/blob/main/book/src/design/terminology.md>`_
.. [#zebra-crosslink-cl2] `Shielded Labs zebra-crosslink design book: Crosslink 2 Construction <https://github.com/ShieldedLabs/zebra-crosslink/blob/main/book/src/design/cl2-construction.md>`_
.. [#zebra-crosslink-security] `Shielded Labs zebra-crosslink design book: Security Properties <https://github.com/ShieldedLabs/zebra-crosslink/blob/main/book/src/design/security-properties.md>`_
