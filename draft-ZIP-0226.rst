::

  ZIP: 226
  Title: Transfer and Burn of Zcash Shielded Assets
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

- Asset: A type of note that can be transferred on the Zcash block chain.

  - ZEC is the default (and currently the only defined) asset for the Zcash mainnet.

- Zcash Shielded Asset: an asset with issuance defined on the Zcash block chain, and, for now, belonging to the Orchard anonymity pool.
- Wrapped Asset: a ZSA asset with native issuance defined outside the Zcash block chain.

Abstract
========

ZIP 226 and ZIP 227 propose in conjunction the Zcash Shielded Assets (ZSA) protocol, which is an extension of the
Orchard protocol that enables the creation, transfer and burn of custom assets on the Zcash chain. The creation of such assets is defined
in ZIP 227 [#zip-0227]_. The transfer and burn of such assets is defined in ZIP 226 [#zip-0226]_.

Motivation
==========

The current Orchard protocol does not support custom assets, which is an important aspect for the proper evolution of the Zcash ecosystem. Enabling multi-asset support on the Zcash chain will open the door for a host of applications and enhance the ecosystem with application developers and asset custody institutions for issuance and bridging purposes.

Overview
========
In order to be able to represent different asset types in Orchard, one needs to define a new data field that uniquely represents the *type* of the asset in question, which we call :math:`\mathsf{type}`.

The type will be used to enforce the balance of an action description [#protocol-actions]_ is preserved across assets (see the Orchard Binding Signature [#protocol-binding]_ , and by extension of an Orchard transaction. Mainly, the sum of all the :math:`\mathsf{value^{net}}`, as :math:`\mathsf{value^{old}-value^{new}}`, derived from each action description, must be balanced only **with respect to the same asset type**. This is specially important since we will allow different action descriptions to transfer notes of different asset types, where the overall balance is checked without revealing which assets (or how many different types) are being transferred.

As was initially proposed by Jack Grigg and Daira Hopwood [#initial-zsa-issue]_, we propose to make this happen by changing the value base point, :math:`\mathcal{V}^{\mathsf{Orchard}}`, in the Homomorphic Pedersen Commitment that generates the value commitment, :math:`\mathsf{cv^{net}}`, of the *net value* in an Orchard Action.

Because in a single transaction all value commitments are balanced, there must be as many different value base points as there are asset types in the transaction. We propose to make the :math:`\mathsf{type}` identifier an auxiliary input to the proof, represented already as a point in the Pallas curve. The circuit then should check that the same :math:`\mathsf{type}` is used in the old note commitment, in the new note commitment **and** in the value commitment as the base point of the value. This ensures that (1) the input and output notes are of the same type, and (2) that only actions with the same asset type identifier will balance out in the binding and balance signature.

In order to ensure the security of the transfers, and as we will explain below, we are replacing input dummy notes for custom assets, as we need to enforce that the type of the output note of that split action is the output of a PRF.

Finally, in this ZIP we also describe the *burn* mechanism, which is a direct extension of the transfer mechanism. The burn process uses a similar mechanism than what is used in Orchard to unshield ZEC, by using the :math:`\mathsf{valueBalance}` of the asset in question. Burning assets is useful for many purposes, including bridging of wrapped assets and removing supply of native assets.

Orchard Protocol Changes
========================

Most of the protocol is kept the same as the Orchard protocol released with NU5, except the following that will be deployed to mainnet in subsequent network upgrades.

Asset Types
-----------

In the OSA protocol, we include a new variable, the asset type identifier, :math:`\mathsf{type}`, which is generated as a 32-byte string during issuance (as described in the Issuance ZIP [#zip-0227]_). The :math:`\mathsf{type}` will then be publicly hashed into the corresponding group, in this case the Pallas curve, by using the :math:`\mathsf{GroupHash}`
function. In fact, every ZSA note will contain the group element representation of the asset type identifier. This will enable a much more elegant and simple version of the circuit, as we will see.

We denote the string as :math:`\mathsf{type}` and we denote the equivalent group representation as :math:`\mathsf{type}_{\mathbb{G}}` when mapped into a specific group, :math:`\mathbb{G}`. Note that the type of the ZEC asset will be kept as the original value base-point, :math:`\mathcal{V}^\mathsf{Orchard}`

In future network and protocol upgrades, the same asset type string can be carried on, with potentially a mapping into a different curve or group. In that case, the turnstile should know how to transform the asset type from one group to another one.

Note Structure & Commitment
---------------------------

First, we need to adapt the components that define the assets, i.e.: *notes*. A ZSA note differs from an Orchard note by including the type of asset, :math:`\mathsf{type}_\mathbb{P}`. So an ZSA note looks like:


:math:`(\mathsf{g_d, pk_d, v, \rho, \psi, type}_{\mathbb{P}})`


Where :math:`\mathsf{type}_\mathbb{P}` is the unique random group element that identifies each asset in the Pallas curve [#protocol-pallasandvesta]_, [#pasta-evidence]_ of the Orchard protocol. 

In this case, the note commitment, :math:`\mathsf{NoteCommit^{ZSA}_{rcm}}`, will differ from :math:`\mathsf{NoteCommit^{Orchard}_{rcm}}` in that for non-ZEC assets, the type will be added as an input to the commitment computation. As we will see, the recursive structure of the Sinsemilla-base commitment [#protocol-concretesinsemillacommit]_ allows us to add the type as a final recursive step, and hence keep a single instance of the hash function in the circuit for the note commitment verification.

Since the commitment output is still indistinguishable with the original Orchard ZEC note commitments, by definition of the Sinsemilla hash, ZSA note commitments will be added to the same Merkle Commitment Tree. In essence, we have


:math:`\mathsf{NoteCommit^{ZSA}_{rcm}(repr_{\mathbb{P}}(g_d), repr_{\mathbb{P}}(pk_d), v, \rho, \psi, type_\mathbb{P})} \in \{\mathsf{cm},\bot\}`


The nullifier is generated in the same manner as in the Orchard protocol.

Value Commitment
----------------

The Orchard Protocol uses a Sinsemilla-based Homomorphic Pedersen Commitment [#protocol-concretevaluecommit]_ which is instantiated as

:math:`\mathsf{cv^{net}:=ValueCommit^{Orchard}_{rcv}(v^{net})}:= \mathsf{[v^{net}]}\mathcal{V}^{\mathsf{Orchard}}+[\mathsf{rcv}]\mathcal{R}^{\mathsf{Orchard}}`

Where :math:`\mathsf{v^{net} = v^{old} - v^{new}}` and

:math:`\mathcal{V}^{\mathsf{Orchard}}:=\mathsf{GroupHash^{\mathbb{P}}}(\texttt{"z.cash:Orchard-cv", "v")}`

:math:`\mathcal{R}^{\mathsf{Orchard}}:=\mathsf{GroupHash^{\mathbb{P}}}(\texttt{"z.cash:Orchard-cv", "r")}`

In the case of the Orchard protocol, we see that the base points :math:`\mathcal{V}^{\mathsf{Orchard}}` and
:math:`\mathcal{R}^{\mathsf{Orchard}}` are fixed for every value commitment, as the values represent the amount of ZEC
being transferred.

In the case of the ZSA protocol, the value of different asset types in a given transaction will be committed using a **different value base point**. This enables the final balance of the transaction to be securely computed, such that each asset type is balanced independently, as the assets are not meant to be fungible. The value commitment then becomes


:math:`\mathsf{cv^{net}:=ValueCommit^{ZSA}_{rcv}(v^{net}_{type},\mathcal{V}^{\mathsf{ZSA}}_{\mathsf{type}})}:= \mathsf{[v^{net}_{type}]}\mathcal{V}^{\mathsf{ZSA}}_{\mathsf{type}}+[\mathsf{rcv}]\mathcal{R}^{\mathsf{Orchard}}`


where :math:`\mathsf{v^{net}_{type}} = \mathsf{v^{old}_{type} - v^{new}_{type}}` such that :math:`\mathsf{v^*_{type}}` is the value of the note of type :math:`\mathsf{type}`, and


:math:`\mathcal{V}^{\mathsf{ZSA}}_{\mathsf{type}}:=\mathsf{type_\mathbb{P}}= \mathsf{GroupHash^{\mathbb{P}}}\texttt{("z.cash:Orchard-cv",type\_params)}`

:math:`\mathcal{R}^{\mathsf{Orchard}}:=\mathsf{GroupHash^{\mathbb{P}}}\texttt{("z.cash:Orchard-cv", "r")}`

Where :math:`\mathcal{V}^{\mathsf{ZSA}}_{\mathsf{ZEC}} =\mathcal{V}^{\mathsf{Orchard}}`.

Value Balance Verification
--------------------------

In order to verify the balance of the different assets, verifier performs exactly the same the process as for the Orchard protocol [#protocol-binding]_. The main reason is because no custom assets can be unshielded, so all custom assets are contained within the shielded ZSA pool. This means that the net balance of the input and output values is zero, with only one type of value balance published, that of ZEC, :math:`\mathsf{v^{balanceOrchard}}`, so no net amount of any type will be revealed, and neither the nnumber of types in the transaction. The only exception to this is in the case that an asset is *burnt*, as we will see below.

For a total of :math:`m` actions in a transfer, the prover can still sign the `SIGHASH` of the transaction using the binding signature key

:math:`\mathsf{bsk} = \sum_{\mathsf{ \forall i\in \{1,...,m\}}} \mathsf{rcv_{i}}`

Then we have that the verifier computes

:math:`\mathsf{bvk = (\sum cv_i^{net})}  - \mathsf{ ValueCommit_0^{Orchard}(v^{balanceOrchard})} = \sum \mathsf{rcv_{i}^{net}}\mathcal{R}^{\mathsf{Orchard}}`


And uses it to verify the binding signature, as described in §4.14 of the Zcash Specification [#protocol-binding]_, by verifying the `bindingSignature` on the `SIGHASH` message.

As in the Orchard protocol, the binding signature verification key, :math:`\mathsf{bvk}`, will only be valid (and hence verify the signature correctly, as long as all the value commitments (and corresponding value balances) are equal to zero. In contrast, in this protocol, the value commitments only cancel out **per asset type**, as the Pedersen commitments add up homomorphically only with respect to the same value base point.

Split Notes
-----------

One of the key functionalities in a UTXO based protocol is the fact that input notes are usually split in two (or more) output notes, as in most cases, not all the value in a single note is sent to a single output. This is called a 1-to-many (Orchard) transaction. In order to cope with this today, the input note of the second (third and more) Action (which we call split notes and split Actions respectively) is a *dummy spend note* [#protocol-dummynotes]_. Basically, the input note is “faked” inside of the proof in order to hide which action contains the *real* spend note.

This, however, brings some issues when it comes to adding multiple asset types, as the output note of the split Actions *cannot* be of *any* asset type, it must be enforced to be an actual output of a GroupHash computation (in fact we want it to be of the same type as the original input note, but the binding signature takes care that the proper balancing is performed). If not, then the prover could essentially input a multiple (or linear combination of) an existing type, with the goal to attack the network by overflowing the ZEC value balance and hence counterfeiting ZEC funds.

In order to prevent this, we make some modifications to the circuit. Specifically we remove the dummy note functionality for custom assets and we enforce that *every* input note to an ZSA Action must be proven to exist in the set of note commitments in the Merkle Tree. We then enforce this real note to be “unspendable” in the sense that its value
will be zeroed in split Actions and the nullifier will be randomized, making the note not spendable in the specific Action. Then, the proof itself ensures that the output note is of the same type as the input note. In the circuit, the split note functionality will be activated by a boolean private input to the proof.

Note that this is enough to create a chain of induction that ensures that all output notes of a transfer are actual outputs of a GroupHash, preventing any malleability attacks, as they originate in the Issuance protocol, which is publicly verified. Furthermore, we do not care about whether the note is owned by the sender, or whether it was nullified before. Wallets and other clients have a choice to make to ensure the asset type is the preserved for the output note of a split Action, for the value balance verification:

1. The split input note could be the same note as the original (non-split) Action, 
2. The split input note could be a different unspent note of the same type (note that the note will not actually be spent)
3. The split input note could be an already spent note of the same type (note that by zeroing the value in the circuit, we prevent double spending)

The specific circuit changes are presented below.

Circuit Statement
=================

The advantage of the design described above, with respect to the circuit statement, is that every *ZSA Action statement* is kept closely similar to the Orchard Action statement [#protocol-actionstatement]_, except for a few additions that ensure the security of the asset type system.

**Asset Type Equality:** the following constraints must be added to ensure that the input and output note are of the
same type:

- The asset type, :math:`\mathsf{type_\mathbb{P}}`, for the note is witnessed once, as an auxiliary input.
- The witnessed asset type, :math:`\mathsf{type_\mathbb{P}}`, is added to the old note commitment input.
- The witnessed asset type, :math:`\mathsf{type_\mathbb{P}}`, is added to the new note commitment input.

**Correct Value Commitment Type:** the following constraints must be added to ensure that the value commitment is computed using the witnessed type, as represented in the notes

- The fixed-base multiplication constraints between the value and the value base point of the value commitment,:math:`\mathsf{cv}`, is replaced with a variable-base multiplication between the two
- The witness to the value base-point is the auxiliary input :math:`\mathsf{type}_\mathbb{P}`.

**Enforce Secure Type for Split Actions:** the following constraints must be added to prevent senders from malling with the asset type for the output note in the consequent actions of the split:

- The Value Commitment Integrity should be changed
    - Replace the input note value by a generic value, `v'`, as :math:`\mathsf{cv^net} = \mathsf{ValueCommit_rcv^OrchardType(v’ - v^new, type}_\mathbb{P})`
- Add a boolean “split” variable as an auxiliary witness. This variable is to be activated `split = 1` if the Action in question is a split and `split = 0` if the Action is actually spending an input note:
    - If `split = 1` then set `v' = 0` otherwise `v'=v^old` from the auxiliary input
- The Merkle Path Validity should check the existance of the note commitment as usual (and not like with dummy notes):
    - Check that (path, pos) is a valid Merkle path of depth :math:`\mathsf{MerkleDepth^Orchard}`, from :math:`\mathsf{cm^old}` to the anchor :math:`\mathsf{rt^Orchard}`.
- The Nullifier Integrity will be changed to prevent the identification of notes
    - Replace the :math:`\psi_{old}` value with a generic :math:`\psi'` as :math:`\mathsf{nf_old = DeriveNullifier_nk}(\rho^\mathsf{old}, \psi', \mathsf{cm^old})`
    - if `split = 1` set :math:`\psi' = \mathsf{randomSample}`, otherwise set :math:`\psi' = \psi^{old}`

**Enabling Backwards Compatibility with ZEC Notes:** the following constraints must be added to enable backwards compatibility with the Orchard ZEC notes.

The old note commitment is computed using a “rolling-aggregate” sinsemilla commitment. This means that the commitment is computed by adding new chunks or windows to the accumulated value. This method will be used in order to maintain a single commitment instance for the old note commitment, that will be used both for Orchard ZEC notes and for ZSA notes. The original Orchard ZEC notes will be conserved and not actually be converted into ZSA notes, as we will always need to compute them.

- The input note in the old note commitment integrity must either include a type (ZSA note) or not (ZEC-Orchard note)
    - If the type auxiliary input is set :math:`\mathsf{type}_\mathbb{P}` = :math:`\mathcal{V}^\mathsf{Orchard}`
        - NoteCommitment has a “compatibility” path that computes the note commitment as in plain Orchard (i.e.: without including the type)
        - This path also uses the original domain separator for ZEC note commitment
    - Else, 
        - The NoteCommitment adds the type, :math:`\mathsf{type}_\mathbb{P}`, as a final “chunk” of the Sinsemilla commitment
        - The NoteCommitment uses a different domain separator for ZSA note commitment


Backward Compatibility
----------------------

In order to have a "clean" backwards compatibility with the ZEC notes, we have designed the circuit to support both ZEC and ZSA notes. As we specify above, there are three main reasons we can do this:
- The input notes with a type denote the ZSA custom assets, generating a note commitment that includes the type; whereas the notes without a type, denote the ZEC notes, and generate a note commitment that does not include the type, in order to maintain the referencability to the Merkle tree
- The value commitment is abstracted to allow for the value base-point as a variable private input to the proof
- The ZEC-based actions will still include dummy input notes, whereas the ZSA-based actions will include split input notes

Burn Mechanism
==============
The burn mechanism may be needed for off-boarding the wrapped assets from the chain, or enabling advanced tokenomics on native tokens. It is part of the Issuance/Burn protocol, but given that it can be seen as an extension of the Transfer protocol, we add it here for readability.

In essence, the burn mechanism is a transparent / revealing extension to the transfer protocol that enables a specific amount of any asset type to be sent into “oblivion”. Our burn mechanism does NOT send assets to a non-spendable address, it simply reduces the total number of assets in circulation at the consensus level. It is enforced at the consensus level, by using an extension of the value balance mechanism used for ZEC assets.

First, contrary to the strict transfer transaction, we allow the sender to include a :math:`\mathsf{valueBalvalueBalance_{type}}` variable for every asset type that is being burnt. As we will show in the transaction structure, this is separate from the regular :math:`\mathsf{valueBalance^Orchard}` that is the default transparent value for the ZEC asset.

For every custom asset that is burnt, we add to the `assetBurn` vector the tuple :math:`(\mathsf{valueBalance_{type}, type}_\mathbb{P})` such that the validator of the transaction can compute the value commitment with the corresponding value base point of that asset. This ensures that the values are all balanced out with respect to the asset types in the transfer.


:math:`\mathsf{assetBurn = [(v^{type}, type_\mathbb{P})}| \forall \mathsf{type}_\mathbb{P}  \textit{ s.t.}\mathsf{v^{type}\neq 0}]`

The value balances for each asset type in `assetBurn` represents the amount of that asset type that is being burnt. In the case of ZEC, the value balance represents either the transaction fee, or the amount of ZEC changing anonymity pools (to Sapling or Transparent).

Finally, the validator needs to verify the Balance and Binding Signature by adding the value balances for all assets, as committed using their respective types as the value base point of the Pedersen Commitment. This is done as follows

:math:`\mathsf{bvk = (\sum cv_i^{net})}  - \mathsf{ ValueCommit_0^{Orchard}(v^{balanceOrchard})} - \sum_{\forall \mathsf{type}\textit{ s.t. }\mathsf{v^{type}\neq 0}} \mathsf{Value Commit_0^{ZSA}(v^{type}type_\mathbb{P}) } = \sum \mathsf{rcv_{i,j}^{net}}\mathcal{R}^{\mathsf{Orchard}}`

In the case that the balance of all the action values related to a specific asset will be zero, there will be no value added to the vector. This way, the number of assets, nor their types will be revealed, except in the case that an asset is burnt.

**Note:** Even if this mechanism allows having transparent ↔  shielded asset transfers in theory, the transparent protocol will not be changed with this ZIP to adapt to a multiple asset structure. This means that unless future consensus rules changes do allow it, the unshielding is not not be possible for custom assets.

ZSA Transaction Structure
=========================
Similar to NU5 transaction structure, with the following modifications to the Orchard bundle, as defined in [#protocol-transactionstructure]_:

+-----------------+-------------+-----------------------------------+-------------------------+
| Bytes           | Name        | Data Type                         | Description             |
+=================+=============+===================================+=========================+
| newActionSize * | vActionsZSA | ActionDescription[nActionOrchard] |                         |
| nActionsZSA     |             |                                   |                         |
+-----------------+-------------+-----------------------------------+-------------------------+
| varies          | nAssetBurn  | compactSize                       | number of assets burnt  |
+-----------------+-------------+-----------------------------------+-------------------------+
| 40*nAssetBurn   | vAssetBurn  | bytes[40][nAssetBurn]             | 32 bytes asset type_t,  |
|                 |             |                                   | 8 bytes of valueBalance |
+-----------------+-------------+-----------------------------------+-------------------------+

Other Considerations
====================

Transaction Fees
----------------

In order to maintain the ZEC economic incentive, the first version of the fees mechanism will be exactly the same as
the current Orchard protocol and will always be paid in ZEC denomination. The ECC and GMU team produced a study on
fees market on Zcash [#fees-study-GMU]_

Security and Privacy
--------------------

- Even if the Orchard protocol and ZSA protocol do not share the same anonymity pool (nodes can keep track of the notes that where published with different transaction structures), the migration from one to the other is done automatically and seamlessly. The Orchard bundle will be replaced by the ZSA bundle and all ZEC notes will be fully spendable with the new transaction structure.
- When including new assets we would like to maintain the amount and types of assets private, which is achieved with the design
- We prevent the "roadblock" attack on the asset type by ensuring the output notes receive a type of an asset that exists on the global state

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
.. [#protocol-actions] `Zcash Protocol Specification, Version 2021.2.16 [NU5 proposal]. Section 3.7: Action Transfers and their Descriptions <protocol/protocol.pdf#actions>`_
.. [#protocol-binding] `Zcash Protocol Specification, Version 2021.2.16 [NU5 proposal]. Section 4.14: Balance and Binding Signature (Orchard) <protocol/protocol.pdf#actions>`_
.. [#protocol-pallasandvesta] `Zcash Protocol Specification, Version 2021.2.16 [NU5 proposal]. Section 5.4.9.6: Pallas and Vesta <protocol/protocol.pdf#pallasandvesta>`_
.. [#pasta-evidence] `Pallas/Vesta supporting evidence <https://github.com/zcash/pasta>`_
.. [#protocol-concretesinsemillacommit] `Zcash Protocol Specification, Version 2021.2.16 [NU5 proposal]. Section 5.4.8.4: Sinsemilla commitments <protocol/protocol.pdf#concretesinsemillacommit>`_
.. [#protocol-concretevaluecommit] `Zcash Protocol Specification, Version 2021.2.16 [NU5 proposal]. Section 5.4.8.3: Homomorphic Pedersen commitments (Sapling and Orchard) <protocol/protocol.pdf#concretevaluecommit>`_
.. [#protocol-dummynotes] `Zcash Protocol Specification, Version 2021.2.16 [NU5 proposal]. Section 4.8.3: Dummy Notes (Orchard) <protocol/protocol.pdf#>`_
.. [#protocol-actionstatement] `Zcash Protocol Specification, Version 2021.2.16 [NU5 proposal]. Section 4.17.4: Action Statement (Orchard) <protocol/protocol.pdf#actionstatement>`_
.. [#protocol-transactionstructure] `Zcash Protocol Specification, Version 2021.2.16 [NU5 proposal]. Section 7.1: Transaction Encoding and Consensus (Transaction Version 5)  <protocol/protocol.pdf#>`_
.. [#fees-study-GMU] `A Study of Decentralized Markets on the Zcash Blockchain <https://electriccoin.co/wp-content/uploads/2022/05/A-Study-of-Decentralized-Markets-on-the-Zcash-Blockchain.pdf>`_
