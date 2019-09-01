::

  ZIP: XXX
  Title: User-Defined Assets and Wrapped Assets
  Owners: Jack Grigg <jack@electriccoin.co>
  Credits: Daira Hopwood <daira@electriccoin.co>
  Status: Draft
  Category: Consensus
  Created: 2019-08-19
  License: MIT


Terminology
===========

The key words "MUST" and "MAY" in this document are to be interpreted as described in
RFC 2119. [#RFC2119]_

The term "network upgrade" in this document is to be interpreted as described in ZIP 200
[#zip-0200]_.

The term "Sapling" in this document is to be interpreted as described in ZIP 205
[#zip-0205]_.

We define the following additional terms:

- Asset: A type of note that can be transferred on the Zcash block chain. ZEC is the
  default (and currently the only defined) asset for the Zcash mainnet.

- User-Defined Asset (UDA): an asset with issuance defined on the Zcash block chain.

- Wrapped Asset: an asset with issuance defined outside the Zcash block chain.

Abstract
========

This proposal defines a modification to the consensus rules and the Sapling circuit
to enable the creation and transferral of User-Defined Assets, as well as wrapping
externally-issued assets inside the Zcash shielded pool.


Motivation
==========

The Zcash block chain provides strong layer 1 privacy for transactions in a single asset
type (ZEC on mainnet; TAZ on testnet) via the shielded pools. In a perfect world, all
asset types across all mediums would enable strong privacy at their base layer. There are
various reasons why this is unlikely to occur in the near term, and thus it would be
useful if these other assets could benefit from Zcash's deployment of privacy technology.

Separately, there has been significant interest over the past few years in user-defined
assets, where issuance is controlled above layer 1, but the asset is transacted on layer 1
alongside the base asset. The most notable instance of this has been ERC-20 tokens on the
Ethereum block chain. Adding this functionality to the Zcash network, particularly when
coupled with privacy, enables interesting new use cases such as private polling.

Both of these goals can be served by enabling multiple asset types to exist within a
shielded pool.


Conventions
===========

We use the following notation as defined in the Zcash protocol specification
[#spec-notation]_, reproduced here for convenience:

- *a* || *b* means the concatenation of sequences *a* then *b*.


Specification
=============

The proposal leverages the use of homomorphic Pedersen commitments in the Sapling design.
Value commitments for Sapling spends and outputs are balanced as follows:

.. code::

    cv_s1 = [v1] G_zec + [r1] H
    cv_s2 = [v2] G_zec + [r2] H
    cv_o1 = [v3] G_zec + [r3] H
    cv_o1 = [v4] G_zec + [r4] H

    (cv_s1 + cv_s2) - (cv_o1 + cv_o2) - [valueBalance] G_zec = bvk = [bsk] H

which leads to:

- ZEC balance: ``(v1 + v2) - (v3 + v4) = valueBalance``
- bindingSig secret key: ``(r1 + r2) - (r3 + r4) = bsk``

The key intuition is that if we have another value commitment value base G_asset, which
is independent of the ZEC base G_zec, then we can balance multiple asset types
simultaneously:

.. code::

    cv_s1 = [v1] G_zec + [r1] H
    cv_s2 = [v2] G_asset + [r2] H
    cv_o1 = [v3] G_zec + [r3] H
    cv_o2 = [v4] G_asset + [r4] H
    cv_o3 = [v5] G_asset + [r5] H

    (cv_s1 + cv_s2) - (cv_o1 + cv_o2 + cv_o3)
      - [valueBalance] G_zec
      - [assetBalance] G_asset = bvk = [bsk] H

which leads to:

- ZEC balance: ``v1 - v3 = valueBalance``
- BTC balance: ``v2 - (v4 + v5) = assetBalance``
- bindingSig secret key: ``(r1 + r2) - (r3 + r4 + r5) = bsk``

The circuit changes in this ZIP are specified relative to the Sapling circuit. In a
production deployment, they would be implemented as part of a new circuit derived from
Sapling, and would (most likely, if note commitments for ZEC are altered) form a new
shielded pool. We refer to the new circuit and shielded pool inline below as AssetPool.

Asset definitions
-----------------

An asset is defined by its asset type: a byte string that uniquely identifies the asset
amongst all possible assets.

Each asset type has an associated value commitment generator, derived as follows:

.. code::

    TODO: Specify GroupHash using Rescue

As the derivation process is fallible, an asset type MUST result in a valid value
commitment generator. Asset types that do not result in valid generators are invalid.

Modifications to the Sapling design
-----------------------------------

The NoteCommit^Sapling function [#note-commit]_ is replaced with a note commitment that
includes the note's asset type alongside its value:

.. code::

    AssetNoteCommit_rcm(g_d, pk_d, asset_type, v)
      := WindowedPedersenCommit_rcm([1]^6 || asset_type || I2LEBSP_64(v) || g_d || pk_d)

    TODO: Pick a different domain separator

The ValueCommit function [#value-commit]_ is replaced with a value commitment computed
using the note's asset type and the common randomness base:

.. code::

    AssetValueCommit_rcv(asset, v) = [v] AssetGenerator(asset) + [rcv] R

The value balancing equation within AssetPool is generalised to allow multiple assets.

Modifications to the circuit
----------------------------

Inside the AssetPool Spend and Output circuits, the following modifications are made
relative to Sapling:

- The asset type for the note is witnessed.
- The asset type is added to the note commitment input.
- ``AssetGenerator(asset)`` is computed inside the circuit.
- The fixed-base multiplication with ``FixedGenerators::ValueCommitmentValue`` is replaced
  with a variable-base multiplication by the output of ``AssetGenerator(asset)``.

Modifications to transactions
-----------------------------

A new transaction format is defined that adds several new fields:

- A vector of AssetPool SpendDescriptions.
- A vector of AssetPool OutputDescriptions.
- AssetPool-specific ``valueBalance`` and ``bindingSig`` fields.
- A vector of ``(assetType, value, authority)`` fields, for handling issuance and
  absorption of non-ZEC assets.

An AssetPool SpendDescription is serialized identically to a Sapling SpendDescription. It
has the following semantic changes:

- The ``cmu`` field contains the output of ``AssetNoteCommit``.
- The ``cv`` field contains the output of ``AssetValueCommit``.

An AssetPool OutputDescription is structurally identical to a Sapling OutputDescription,
but has a different serialization format. It has the following semantic changes:

- The ``cv`` field contains the output of ``AssetValueCommit``.
- The note plaintext inside the ``encCiphertext`` field is extended to include the asset
  type of the note.

The AssetPool-specific ``valueBalance`` and ``bindingSig`` fields are used to move ZEC
into and out of AssetPool, for example to pay transaction fees. They function identically
to their Sapling equivalents.

TODO: Define (assetType, value, authority) usage.

Issuance
--------

TBD

Consensus rules
---------------

Once the TODO network upgrade activates, the following new consensus rules are enforced:

- TODO: Enumerate these

For the avoidance of doubt: transaction fees are only paid in ZEC.

Rationale
=========

The circuit modifications required for this proposal are a relatively small change to the
Sapling circuit, enabling UDAs and Wrapped Assets to reuse most of the engineering effort
that has been put into developing the Sapling ecosystem.

In addition to this, there are two other reasons for leveraging the Pedersen commitments:

- Multiple asset types, including ZEC, can be spent within the same transaction. This
  enables, for example, native atomic swaps.

- All asset types share the same privacy set. A new-format transaction that involves UDAs
  is indistinguishable from a transaction that only deals in ZEC. This comes at the cost
  of making `encCiphertext` larger for all transactions, to include the asset type even if
  the note is for ZEC.

Whitelisting asset types makes auditing the assets simpler, and helps to ensure that there
is a well-defined boundary around per-asset issuance.


Security and Privacy Considerations
===================================

Deriving each asset's generator from its asset type via GroupHash ensures that every
generator is independent from all others (in that it has an unknown relationship to any
other generator). Assuming that ECDLP is hard, provers cannot obtain a relationship
between asset generators, and thus cannot transmute one asset into another.

If the circuit witnessed the asset generator instead of the asset type (in order to avoid
constraining the derivation inside the circuit), the prover would be free to witness
whatever generator they want, including ones that they know are multiples of a legitimate
generator. This would enable a counterfeiting attack:

- An adversary could transmute note values that are in-range for a legitimate asset (with
  a generator derived from its asset type), into note values that are out-of-range for an
  invalid but related asset type. This could then be leveraged to overflow the value
  balance and counterfeit the invalid assets. The counterfeit funds could then be
  transmuted back into the legitimate asset.


Reference Implementation
========================

TBD

A toy implementation (that modifies the Sapling code) is available here:

- https://github.com/str4d/librustzcash/tree/funweek-uda-demo
- https://github.com/str4d/zcash/tree/funweek-uda-demo


Acknowledgements
================

The approach taken here for balancing shielded value across multiple asset types was
initially outlined by Daira Hopwood during the development of Sapling [#sapling-gvc]_.


References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Activation Mechanism <https://github.com/zcash/zips/blob/master/zip-0200.rst>`_
.. [#zip-0205] `ZIP 205: Deployment of the Sapling Network Upgrade <https://github.com/zcash/zips/blob/master/zip-0205.rst>`_
.. [#spec-notation] `Section 2: Notation. Zcash Protocol Specification, Version 2019.0.6 [Overwinter+Sapling+Blossom] <https://zips.z.cash/protocol/protocol.pdf#notation>`_
.. [#note-commit] `Section 5.4.7.2: Windowed Pedersen commitments. Zcash Protocol Specification, Version 2019.0.6 [Overwinter+Sapling+Blossom] <https://zips.z.cash/protocol/protocol.pdf#concretewindowedcommit>`_
.. [#value-commit] `Section 5.4.7.3: Homomorphic Pedersen commitments. Zcash Protocol Specification, Version 2019.0.6 [Overwinter+Sapling+Blossom] <https://zips.z.cash/protocol/protocol.pdf#concretehomomorphiccommit>`_
.. [#sapling-gvc] `Comment on Generalized Value Commitments <https://github.com/zcash/zcash/issues/2277#issuecomment-321106819>`_
