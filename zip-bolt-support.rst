::

  ZIP: XXX
  Title: Add support for Blind Off-chain Lightweight Transactions (Bolt) protocol
  Authors: J. Ayo Akinyele <ayo@boltlabs.io>
           Colleen Swanson <swan@boltlabs.io>
  Credits: Ian Miers <imiers@z.cash>
           Matthew Green <mgreen@z.cash>
  Category: Consensus
  Created: 2019-07-15
  License: MIT


Terminology
===========

The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119. [#RFC2119]_

Abstract
========

This proposal specifies three possible approaches for integrating the blind off-chain lightweight transaction (Bolt) protocol [#bolt-paper]_ into Zcash.

Motivation
==========

Layer 2 protocols like Lightning enable scalable payments for Bitcoin but lack the mechanisms to provide strong privacy guarantees on the payment network. Zcash offers private transactions but currently lacks features that would enable a lightning-style payment channel. This proposal specifies an integration of the Bolt privacy-preserving Lightning protocol on top of Zcash [#bolt-paper]_.

Specification
=============

This specification details an initial approach to integrating the features of Bolt into Zcash in a future network upgrade and depends on the WTP ZIP [#wtp-programs]_ that introduces Whitelisted Transparent Programs (WTPs). Our prototype implementation can be found here: [#BoltWTP]_.

1. General requirements for Bolt protocol
--------------------------

Bolt private payment channels require the following capabilities to provide anonymity properties for users on a payment network:

(1) Ability to create a escrow transaction such that the transaction inputs are anonymous.
(2) Ability to escrow funds to a multi-signature style address via non-malleable transactions.
(3) Ability to specify relative time locks for commitment transactions to support unilateral channel closing.
(4) Ability to specify absolute and relative time locks to support HTLCs for multi-hop payments.
(5) Ability to validate Bolt-specific opening and closing transactions:

    - check the validity of randomized/blinded signature on the wallet commitment in closing token
    - check the validity of revocation token in the event of a channel dispute by merchant

(6) Ability to verify transaction outputs using WTPs such that:

    - if customer-initiated closing, one output pays out to customer with a time lock (to allow merchant to dispute customer balance) and one output pays out to merchant immediately
    - if merchant-initiated closing, a single output pays the merchant the full balance of the channel with a time lock that allows for customer dispute

**Channel Operation Assumptions.**
 - Channels funded by the customer alone and dual-funded channels are both supported.
 - Either the customer or the merchant can initiate channel closing.
 - If the customer initiates closing, then the merchant can dispute the closing transaction if they disagrees with the closing token in the closing transaction.
 - If the merchant initiates closing, the merchant posts a transaction claiming all the funds in the channel for themselves with a timelock. This gives the customer the opportunity to post their own valid closing transaction with the current channel balances. If the customer posts their own closing transaction, the merchant has an additional opportunity to dispute if necessary.

1.1 Customer and Merchant Signing Keys
-------------

The customer and the merchant both have key pairs from a suitable signature scheme. These are denoted as:
``<cust-pk>, <cust-sk>`` and 
``<merch-pk>, <merch-sk>``, respectively, where ``pk`` stands for "public key" and ``sk`` stands for the corresponding "secret key".

The merchant must be able to issue blind signatures, so they have an additional keypair; this keypair is denoted as:
``<MERCH-PK>, <MERCH-SK>``.

The customer key pair is specific to the channel and must not be reused. The merchant key pair is long term and should be used for all customer channels. 

1.2 Wallets
-------------
A Bolt channel allows a customer to make or receive a sequence of payments off chain. These payments are tracked and validated using a sequence of *wallets*. A wallet consists of the customer's public key (which ties the wallet to the channel), a wallet-specific public key (which can be from any suitable signature scheme), denoted ``<wpk>``, and the current customer and merchant balances.

After each payment, the customer receives an updated wallet and blind signatures from the merchant on the wallet contents allowing channel close as specified below.

1.2 Opening a Channel: Overview
-------------
To open a channel, the customer and merchant exchange key information and set the channel token ``<channel-token> = <cust-pk>, <merch-pk>, <MERCH-PK>``. 

They agree on their respective initial balances ``initial-cust-balance`` and ``initial-merch-balance``.

The customer picks an inital wallet public key ``<wpk>``.

The customer and merchant escrow the necessary funds in a funding transaction, denoted ``escrow-tx``. 

1.3 Closing a Channel: Overview
-------------

A customer should be able to close the channel by posting a *closing token* ``close-token``, which is a blind signature from the merchant under ``<MERCH-PK>`` on a special closing wallet that contains ``<cust-pk>, <wpk>, <balance-cust>, <balance-merch>, CLOSE``. We use ``cust-close-tx`` to denote the transaction posted by the customer to initiate channel closure.

A merchant should be able to close the channel by either posting a special closing transaction ``merch-close-tx`` (detailed in Section 2.3.2) or, if the customer posts an outdated version of their closing token, a signed revocation token, ``revocation-token`` as detailed below. The revocation token ``revocation-token`` is a signature under the wallet public key ``<wpk>`` on the special revocation message ``<wpk> || REVOKED``. The transaction posted by the merchant to dispute is denoted ``dispute-tx``.

The customer and merchant may also negotiate off-chain to form a *mutual close transaction*, ``mutual-close-tx``. Off-chain collaboration to create ``mutual-close-tx`` reduces the required number of on-chain transactions and eliminates the time delays.

2. Transparent/Shielded Tx: Using T/Z-addresses and WTPs
-------------

We assume the following specific features are present:

(1) Support for whitelisted transparent programs (WTPs) that enables 2-of-2 multi-sig style transactions
(2) Can specify absolute lock time in transaction
(3) Can specify relative lock time in transparent program
(4) Can specify shielded inputs and outputs
(5) A non-SegWit approach that fixes transaction malleability
(6) ``OP_BOLT`` logic expressed as WTPs. We will use the Bolt WTPs defined in Section 2.1: ``open-channel``, ``cust-close``, and ``merch-close``.

**Privacy Limitations**. The aggregate balance of the channel will be revealed in the funding transaction ``escrow-tx``. Similarly, the final splitting of funds will be revealed to the network. However, for channel opening and closing, the identity of the participants remains hidden. Channel opening and closing will also be distinguishable on the network due to use of WTPs.

**Channel Opening**. The funding transaction ``escrow-tx`` spends ZEC from one or more shielded addresses to a transparent output that is encumbered by a Bolt transparent program. See Section 2.1 for what the funding transaction looks like when instantiated using WTPs.

2.1 Bolt WTPs
--------------

Transparent programs take as input a ``predicate``, ``witness``, and ``context`` and then output a ``True`` or ``False`` on the stack. Bolt-specific transparent programs are deterministic and any malleation of the ``witness`` will result in a ``False`` output. The WTPs are as follows:

1. ``open-channel`` program. The purpose of this WTP is to encumber the funding transaction such that either party may initiate channel closing as detailed above in Section 1.3. The program is structured as follows:

	a. ``predicate``: The predicate consists of ``<<channel-token> || <merch-close-address>>``, where ``<channel-token> = <<cust-pk> || <merch-pk> || <MERCH-PK>>`` contains three public keys, one for the customer and two for the merchant, and an address ``<merch-close-address>`` for the merchant at which to receive funds from a customer-initiated close.
	
	b. ``witness``: The witness is defined as follows, where the first byte is used to denote witness type:
	
    		1. ``<<0x0> || <balance-cust> || <balance-merch> || <cust-sig> || <merch-sig>>``
    		2. ``<<0x1> || <balance-cust> || <balance-merch> || <cust-sig> || <wpk> || <closing-token>>``
  	
	c. ``verify_program`` behaves as follows:
	
    		1. If witness is of type ``0x0``, check that 2 new outputs are created, with the specified balances (unless one of the balances is zero), and that the signatures verify.
    		2. If witness is of type ``0x1``, check that 2 new outputs are created (unless one of the balances is zero), with the specified balances:
		
      			+ one paying ``<balance-merch>`` to ``<merch-close-address>`` 
      			+ one paying a ``cust-close`` WTP containing ``<channel-token>`` and ``<wallet> = <<wpk> || <balance-cust> || <balance-merch>>``
			
      			Also check that ``<cust-sig>`` is a valid signature and that ``<closing-token>`` contains a valid signature under ``<MERCH-PK>`` on ``<<cust-pk> || <wpk> || <balance-cust> || <balance-merch> || CLOSE>``.

2. ``cust-close`` program. The purpose of this WTP is to allow the customer to initiate channel closure as specified in Section 1.3. The program is specified as follows:

	a. ``predicate``: ``<<channel-token> || <block-height> || <wallet>>``, where
	
		1. ``<channel-token> = <<cust-pk> || <merch-pk> || <MERCH-PK>>``,
		2. ``<block_height>`` is the earliest block-height when balance can be spend, and
		3. ``<wallet> = <<wpk> || <balance-cust> || <balance-merch>>``.
	b. ``witness``: The witness is defined as one of the following, where the first byte is used to denote witness type:
	
		1. ``<<0x0> || <cust-sig>>``
		2. ``<<0x1> || <merch-sig> || <address> || <revocation-token>>``
	c. ``verify_program`` behaves as follows:
	
		1. If witness is of type ``0x0``, check that ``<cust-sig>`` is valid and ``<block-height>`` has been reached
		2. If witness is of type ``0x1``, check that 1 output is created paying ``<balance-cust>`` to ``<address>``. Also check that ``<merch-sig>`` is a valid signature on ``<<address> || <revocation-token>>`` and that ``<revocation-token>`` contains a valid signature under ``<wpk>`` on ``<<wpk> || REVOKED>``.

3. ``merch-close``. The purpose of this WTP is to allow a merchant to initiate channel closure as specified in Section 1.3. The program is specified as follows:

	a. ``predicate``: ``<<channel-token> || <block-height> || <merch-close-address>>``.
	b. ``witness`` is defined as one of the following, where the first byte is used to denote witness type:
	
		1. ``<<0x0> || <merch-sig>>``
		2. ``<<0x1> || <cust-sig> || <wallet> || <closing-token>>``, where ``<wallet> = <<wpk> || <balance-cust> || <balance-merch>>``.
	c. ``verify_program`` behaves as follows:
		
			1. If witness is of type ``0x0``, check that ``<merch-sig>`` is valid and ``<block-height>`` has been reached
			2. If witness is of type ``0x1``, check that 2 new outputs are created (unless one of the balances is zero), with the specified balances:
			
				+ one paying ``<balance-merch>`` to ``<merch-close-address>`` 
 				+ one paying a ``cust_close`` WTP containing ``<wallet> = <<wpk> || <balance-cust> || <balance-merch>>``  and ``<channel-token>``. 
				
				Also check that ``<cust-sig>`` is a valid signature and that ``<closing-token>`` contains a valid signature under ``<MERCH-PK>`` on ``<<cust-pk> || <wpk> || <balance-cust> || <balance-merch> || CLOSE>``.


2.2 Channel establishment and Funding Transaction
-------------
The funding transaction ``escrow-tx`` by default has 2 shielded inputs (but can be up to some N) and an ``open-channel`` WTP output with predicate ``<<channel-token> <merch-close-address>>``. 

* ``lock_time``: 0
* ``nExpiryHeight``: 0
* ``valueBalance``: funding amount + transaction fee
* ``nShieldedSpend``: 1 or N (if funded by both customer and merchant)
* ``vShieldedSpend[0]``: tx for customer’s note commitment and nullifier for the coins

  - ``cv``: commitment for the input note
  - ``root``: root hash of note commitment tree at some block height
  - ``nullifier``: unique serial number of the input note
  - ``rk``: randomized pubkey for spendAuthSig
  - ``zkproof``: zero-knowledge proof for the note
  - ``spendAuthSig``: signature authorizing the spend

* ``vShieldedSpend[1..N]``: additional tx for customer's note commitment and nullifier for the coins

  - ``cv``: commitment for the input note
  - ``root``: root hash of note commitment tree at some block height
  - ``nullifier``: unique serial number of the input note
  - ``rk``: randomized pubkey for spendAuthSig
  - ``zkproof``: zero-knowledge proof for the note
  - ``spendAuthSig``: signature authorizing the spend
* ``tx_out_count``: 1
* ``tx_out``: (via a transparent program)

  - ``scriptPubKey``: ``PROGRAM PUSHDATA( <open-channel> || <<channel-token> || <merch-close-address>> )``

* ``bindingSig``: a signature that proves that (1) the total value spent by Spend transfers - Output transfers = value balance field.

The customer and merchant collaborate to create the customer's initial closing token ``closing-token`` and the merchant closing transaction ``merch-close-tx`` before signing and sending ``escrow-tx`` to the network. Once the transaction has been confirmed, the payment channel is established.

2.3 Channel Closing
-------------
2.3.1 Customer-initiated channel closing.
----
To initiated channel closure, a customer posts the transaction ``cust-close-tx`` that spends from ``escrow-tx`` and contains two outputs: (1) an output that can be spent immediately by the merchant and (2) a ``cust-close`` WTP output that can be spent either by the customer after a relative timeout or by the merchant with a revocation token. This approach allows the merchant to dispute if the customer posts a transaction containing a spent closing token (i.e., a closing token that is valid from the network's perspective but outdated from the merchant's perspective).

The transaction ``cust-close-tx`` is as follows:

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set such that closing transactions can be included in a current block.
* ``txin`` count: 1

   - ``txin[0]`` outpoint: references the funding transaction txid and output_index
   - ``txin[0]`` script bytes: 0
   - ``txin[0]`` scriptSig: ``PROGRAM PUSHDATA( <open-channel> || <<0x1> || <balance-cust> || <balance-merch> || <cust-sig> || <wpk> || <closing-token>> )``

* ``txout`` count: 2
* ``txouts``:

  * ``to_customer``: a ``cust-close`` WTP output.
  
      - ``amount``: ``<balance-cust>``
      - ``nSequence: <time-delay>``
      - ``scriptPubKey``: ``PROGRAM PUSHDATA( <cust-close> || <<channel-token> || <wallet>>  )``

  * ``to_merchant``: a P2PKH output sending funds to the merchant, i.e.
  
      * ``scriptPubKey``: ``0 <20-byte-key-hash of merch-close-address>``
      * ``amount``: ``<balance-merch>``
      * ``nSequence``: 0

To redeem the ``to_customer`` output, the customer posts a secondary closing transaction after the appropriate time delay with the following ``scriptSig``:

	``PROGRAM PUSHDATA( <cust-close> || <<0x0> || <cust-sig> || <block-height>> )``

where the ``witness`` consists of a first byte ``0x0`` to indicate the witness type followed by the customer signature and the current block height (used to ensure that timeout reached). 

If the customer posts a spent closing token, the merchant can dispute and redeem the ``to_customer`` output by posting a transaction ``dispute-tx`` that spends from ``cust-close-tx`` with the following ``scriptSig``:

	``PROGRAM PUSHDATA( <cust-close> || <<0x1> || <merch-sig> || <revocation-token>> )``

where the ``witness`` consists of a first byte ``0x1`` to indicate the witness type followed by the merchant signature and the revocation token.

2.3.2 Merchant-initiated channel closure
----
To initiate channel closure, the merchant posts the following transaction ``merch-close-tx`` (formed and signed during channel establishment) that spends from ``escrow-tx``:

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set such that closing transactions can be included in a current block.
* ``txin`` count: 1

   - ``txin[0]`` outpoint: references the funding transaction txid and output_index
   - ``txin[0]`` script bytes: 0
   - ``txin[0]`` scriptSig: ``PROGRAM PUSHDATA( <open-channel> || <<0x0> || <balance-cust> || <balance-merch> || <cust-sig> || <merch-sig>> )``

* ``txout`` count: 1
* ``txouts``:

  * ``to_merchant``: a ``merch-close`` WTP output.
  
      - ``amount``: sum of ``<balance-cust>`` and ``<balance-merch>``
      - ``nSequence: <time-delay>``
      - ``scriptPubKey``: ``PROGRAM PUSHDATA( <merch-close> || <<channel-token> || <merch-close-address>> )``

To spend this output, the merchant posts a secondary closing transaction after the appropriate time delay with the following ``scriptSig``:

	``PROGRAM PUSHDATA( <merch-close> || <<0x0> || <merch-sig> || <block-height>> )``

where the ``witness`` consists of a first byte ``0x0`` to indicate witness type, followed by the merchant signature and the current block height (used to ensure that the timeout has been reached). 

If the customer sees ``merch-close-tx`` on chain, and the current customer balance in the channel is actually non-zero, the customer should post their own closing transaction. This closing transaction is nearly identical to that specified in the customer-initiated channel closure section above and allows for merchant dispute in the same way:

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set such that closing transactions can be included in a current block.
* ``txin`` count: 1

   - ``txin[0]`` outpoint: references the ``merch-close-tx`` txid and output_index
   - ``txin[0]`` script bytes: 0
   - ``txin[0]`` scriptSig: ``PROGRAM PUSHDATA( <merch-close> || <<0x1> || <balance-cust> || <balance-merch> || <cust-sig> || <wpk> || <closing-token>> )``

* ``txout`` count: 2
* ``txouts``:

  * ``to_customer``: a ``cust-close`` WTP output.
  
      - ``amount``: ``<balance-cust>``
      - ``nSequence: <time-delay>``
      - ``scriptPubKey``: ``PROGRAM PUSHDATA( <cust-close> || <<channel-token> || <wallet>>  )``

  * ``to_merchant``: a P2PKH output sending funds to the merchant, i.e.
  
      * ``scriptPubKey``: ``0 <20-byte-key-hash of merch-close-address>``
      * ``amount``: ``<balance-merch>``
      * ``nSequence``: 0


2.3.3 Mutual closing
-------------
The customer and merchant can alternatively collaborate off-chain to create a mutual closing transaction ``mutual-close-tx`` that spends from ``escrow-tx``. This transaction is as follows:


* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set such that closing transactions can be included in a current block.
* ``txin`` count: 1

   - ``txin[0]`` outpoint: references the funding transaction txid and output_index
   - ``txin[0]`` script bytes: 0
   - ``txin[0]`` scriptSig: ``PROGRAM PUSHDATA( <open-channel> || <<0x0> || <balance-cust> || <balance-merch> || <cust-sig> || <merch-sig>> )``

* ``txout`` count: 2
* ``txouts``:

  * ``to_customer``: an output paying ``<balance-cust>``
  * ``to_merchant``: an output paying ``<balance-merch>``
     

Reference Implementation
========================

.. [#BoltWTP] _`Bolt WTP implementation for Zcash <https://github.com/boltlabs-inc/librustzcash>`

References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#bolt-paper]  `Bolt: Anonymous Payment Channels for Decentralized Currencies <https://eprint.iacr.org/2016/701>`_
.. [#wtp-programs]  `ZIP XXX: Whitelisted Transparent Programs (Draft) <https://github.com/zcash/zips/pull/248>`_
