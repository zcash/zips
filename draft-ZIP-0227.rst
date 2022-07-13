::

  ZIP: 227
  Title: Issuance of Zcash Shielded Assets
  Owners: Daniel Benarroch <daniel@qed-it.com>
          Pablo Kogan <pablo@qed-it.com>
          Aurelien Nicolas <aurel@qed-it.com>
  Credits: Daira Hopwood
           Jack Grigg
           Shahaf Nacshon
           Vivek Arte
  Status: Draft
  Category: Consensus
  Created: 2022-05-01
  License: MIT
  Discussions-To: <https://github.com/zcash/zips/issues/618>


Terminology
===========

The key word "MUST" in this document is to be interpreted as described in RFC 2119 [#RFC2119]_.

The term "network upgrade" in this document is to be interpreted as described in ZIP 200 [#zip-0200]_.

The term "Orchard" in this document is to be interpreted as described in ZIP 224 [#zip-0224]_.

We define the following additional terms:

- Asset: A type of note that can be transferred on the Zcash block chain. ZEC is the default (and currently the only defined) asset for the Zcash mainnet.
- Zcash Shielded Asset: an asset with issuance defined on the Zcash block chain, and, for now, belonging to the Orchard anonymity pool.
- Wrapped Asset: a ZSA asset with native issuance defined outside the Zcash block chain.

Abstract
========

ZIP 226 [#zip-0226]_ and ZIP 227 [#zip-0227]_ propose in conjunction the Zcash Shielded Assets (ZSA) protocol, which is an extension of the
Orchard protocol that enables the creation, transfer and burn of custom assets on the Zcash chain. The creation of such assets is defined
in ZIP 227 [#zip-0227]_. The transfer and burn of such assets is defined in ZIP 226 [#zip-0226]_.

Motivation
==========

The current Orchard protocol does not support custom assets, which is an important aspect for the proper
evolution of the Zcash ecosystem. Enabling multi-asset support on the Zcash chain will open the door for a host of
applications and enhance the ecosystem with application developers and asset custody institutions for issuance and
bridging purposes.

Overview & Rationale
====================

This ZIP specifies the issuance mechanism of the Zcash Shielded Assets (ZSA) protocol and must work conjunction with ZIP 226 [#zip-0226]_, as the issuance mechanism is only valid for the ZSA transfer protocol, as it produces notes that can only be transferred under ZSA.

In short, we are going to enable only *transparent* issuance, since we believe that as a first step, transparency is important to properly test the applications that will be most used in the Zcash ecosystem, while enabling tracking of supply of assets. In essence, any user of the blockchain can issue new asset types, yet only a single issuer (a set of keys) can issue that specific asset type, as the asset identifiers are tied to the issuer keys.

We have designed the protocol such that at the time of issuance, the issuer can already allocate all the tokens to the corresponding owners by creating the corresponding (shielded) output notes to the corresponding addresses. As is implied, the issuance mechanism is itself transparent, but the allocation is totally private. Furthermore, in a single issuance transaction, the issuer can create multiple asset types (and allocate all of those too). Finally, a key component of our design is the `finiteIssuance` boolean that defines whether a specific asset type can have more tokens issued or not.

The issuance mechanism is broad enough for issuers to either create native assets on Zcash (i.e.: assets that originate on the Zcash blockchain), as well as for institutions to create bridges from other chains and import wrapped assets. In fact, the protocol described below enables, what we hope will be a useful set of, applications:

- By setting the `finiteIssuance = 1` from the first issuance instance of that asset type, the issuer is in essence creating a one-time issuance transaction. This is useful when the max supply is capped from the beginning and the distribution is known in advance. All tokens are issued at once and distributed as needed.
- When the `finiteIssuance = 0`, the issuer can keep creating tokens of that type (in a transparent manner). The boolean value can be changed with any new issuance transaction, and could be set to `1` either when the issuer keys have been compromised, and hence stopping all issuances of that asset type (the boolean cannot be reversed), or whenever the issuer decides that the max supply has been reached.
- Note that this mechanism can be used with the burning process to control and affect the supply of any custom asset.


Asset Identifier Generation
===========================

For every new asset, there must be a new and unique identifier of the asset. Our design decision is not to have a chosen name for the asset type, but to delegate it to an off-chain mapping, as this would imply a land-grab “war”. From this asset identifier, which is a global byte string (valid across all Zcash protocols), we derive the specific type used within the notes, as defined by the specific protocol (e.g.: for now Orchard-style, using Pallas curve)

The main requirement for the asset identifier is for it to be collision-free, as two different issuers should not be able to issue the same asset type. As such we need the asset identifier to be:

- pseudorandom
- deterministic
- dependent on the issuer ID

We define the asset identifier `assetID` (represented as a string) as

:math:`\mathsf{assetID := GroupHash^{\mathbb{P}}}\mathsf{(issuerID || assetDesc)}`

where

- `assetDesc` is the asset description, which includes any information pertaining to the issuance.
- `issuerID` is the public key of the issuer, used to verify the signature on the transaction and is defined as `ik` (issuer key or issuer verification key):


:math:`\mathsf{ik := SpendAuthSig^{Orchard}.DerivePublic(isk)}`


which uses the same signature as the spend authorization signature, where `isk` is the issuer secret key. The verification key is derived from `isk`. In order to differentiate the `isk` and `ik` keys from the actual spend authorization key, we derive another branch of keys from the main spending key `sk` as such:

:math:`\mathsf{isk := ToScalar^{Orchard}(︀ PRF^{expand}_{sk} ([10])}`

This allows the issuer to use the same wallet it usually uses to transfer assets, while keeping a disconnect from the other keys. It provides further anonymity and the ability to delegate issuance of an asset (or in the future, generate a multi-signature protocol) while the rest of the keys in the wallet safe.

Then we let `issuanceInfo := (assetID, finiteSupply)`, where 

- `assetID` is as defined above.
- `finiteSupply` is a boolean variable that defines whether this issuance transaction of the specific asset type is the final issuance of tokens or not. Once `finiteSupply` is set, it cannot be unset. This allows expanding the functionality of the issuance mechanism:
    - Provides `assetID` revocation in case of compromise (issue last issuance with 0 token value)
    - Supports NFT issuance (where the first issuance with value of 1 is also the last)


Issuance Protocol
=================

The issuance protocol allows for a single issuance to be sent to many receivers, as the issuerID does not have to match the address ownership of the notes output. Furthermore, every transaction can contain many issuance instances. The design presented in this ZIP enables several use cases for issuance of shielded assets.

- The issuer knows in advance the receivers of the issued asset.
- The asset is of non-fungible type, where each asset type can be made part of a single “series”
- The supply of the asset is limited or not
- The assets can be wrapped versions of assets in other chains (as long as there is a bridge that supports it)

The protocol is as follows:

- For each asset type issued, generate a sequence of output notes, each with the following fields:
    - ZSA output note :math:`\mathsf{ note =(d, pkd, v, \rho, \psi, \mathsf{type}_\mathbb{P}, rcm)}`, where :math:`\mathsf{type}_\mathbb{P} := \mathsf{GroupHash^{\mathbb{P}}}\mathsf{(assetID)}`
- Generate commitment of the note. `cm` as

:math:`cm = \mathsf{NoteCommit^{ZSA}_{rcm}}(\mathsf{repr\mathbb{_P}(g_d)}, \mathsf{repr\mathbb{_P}(pk_d)}, v, \rho, \psi,\mathsf{type}_\mathbb{P})`

- Sign the issuance note with the `issuerID` as the signing key, using RedPallas as its signature scheme, on the `SIGHASH` of the transaction. Note that the `SIGHASH` will change as we include a new bundle in the Zcash transaction to enable this issuance mechanism on chain.

Consensus Changes
-----------------

Issuance requires the following additions to the global state: 

First, Zcash clients must keep a mapping `issuanceSupplyInfos` from `assetID` to `issuanceSupplyInfo := (totalSupply, finiteSupply)`.

**Consensus rules**

For each issuance instance,

- Check that `assetID` is properly constructed,
- Check that each commitment `cm` is properly constructed from each “output” note,
- Check that the issuance instance has a valid signature based on the `issuerID`,
- Check that :math:`\mathsf{type}_\mathbb{P}` is properly projected into the correct curve from `assetID`. That is, that :math:`\mathsf{type}_\mathbb{P} :=  \mathsf{GroupHash^{\mathbb{P}}}\mathsf{(assetID)}`
- If `issuanceSupplyInfo[assetID].finiteSupply`is true, reject. Otherwise, set `issuanceSupplyInfo[assetID].finiteSupply = finiteSupply` .
- Add the sum of all the values in all output notes per `assetID` to `issuanceSupplyInfo[assetID].totalSupply`
- After verification, add note commitment to the merkle tree.

Other Considerations
====================

Fee Structures
--------------

The fee mechanism described in this ZIP may be replaced by a future “Fee Mechanism” ZIP proposal. However, we do need to have some basic fees for the Issuance protocol, as it differs from the usual transfer mechanism in that it adds a whole new structure to the transaction bundle, it adds a new global structure for validators to keep in memory and in turn it adds new consensus rules that are independent of previous structures.

There are two main factors that will affect the fee mechanism:

- The transaction size, which may take a big part of the block
- The computational power needed to verify and mine the transaction

There is a single parameter that defines both, as there is no privacy or ZKP involved at this stage - the number of output notes in the issuance bundle:

- it trivially defines the bundle size
- it defines the computational power as the validator must compute as many note commitments as there are output notes


Test Vectors
============

- LINK TBD

Reference Implementation
========================

- LINK TBD
- LINK TBD

Deployment
==========

This ZIP is proposed to activate with Network Upgrade 6.

References
==========

.. [#RFC2119] `RFC 2119: Key words for use in RFCs to Indicate Requirement Levels <https://www.rfc-editor.org/rfc/rfc2119.html>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <zip-0200.html>`_
.. [#zip-0224] `ZIP 224: Orchard <zip-0224.html>`_
.. [#zip-0226] `ZIP 226: Transfer and Burn of Zcash Shielded Assets <zip-0226.html>`_
.. [#zip-0227] `ZIP 227: Issuance of Zcash Shielded Assets <zip-0227.html>`_