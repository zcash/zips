::

  ZIP: XXX
  Title: Add support for Bolt protocol 
  Authors: J. Ayo Akinyele <ayo@boltlabs.io>
           Colleen Swanson <swan@boltlabs.io>
  Credits: Ian Miers <imiers@z.cash>
           Matthew Green <mgreen@z.cash>
  Category: Consensus
  Created: 2019-03-30
  License: MIT


Terminology
===========

The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119.

Abstract
========

This proposal specifies three possible approaches for integrating the blind off-chain lightweight transaction (Bolt) protocol into Zcash. 

Motivation
==========

Layer 2 protocols like Lightning enable scalable payments for Bitcoin. We want to implement a similar, privacy-preserving layer 2 protocol on top of Zcash.

Specification
=============

This specification details three potential approaches to integrating the features of Bolt into Zcash. 

1. General requirements for Bolt protocol
--------------------------

Private payment channels as designed by the Bolt protocol require the following capabilities to achieve the stated anonymity properties at layer 2:

(1) Ability to create a funding transaction such that the transaction inputs are anonymous.
(2) Ability to escrow funds to a multi-signature address with a fix for transaction malleability.
(3) Ability to verify additional fields from the transaction inputs/outputs as part of signature verification.
(4) Ability to do relative time locks for commitment transactions to support unilateral channel closing.
(5) Ability to do absolute and relative time locks to support multi-hop payments.
(6) Ability to validate Bolt-specific commitment opening message and closing signature:

- check the validity of the commitment opening.
- check the validity of randomized/blinded signature on the wallet commitment in closure token.
- check the validity of revocation token signature in the event of a channel dispute by merchant.
 
(7) Ability to verify the transaction output such that:

- if customer initiated closing, first output pays out to customer with a time lock (to allow merchant to dispute customer balance) and second output pays out to merchant immediately.
- if merchant initiated closing, a single output that pays the merchant the full balance of the channel with a time lock that allows for customer dispute.

**Channel Operation Assumptions**
 - Single-funded channel by customer with a minimum fee paid to the merchant.
 - Either the customer or the merchant can initiate channel closing.
 - If the customer initiates closing, then the merchant can dispute the closing transaction if they disagrees with the closure token in the closing transaction.
 - If the merchant initiates closing, the customer has the opportunity to post their own valid closing transaction. In this case, the merchant has an additional opportunity to validate this closing transaction and can dispute if necessary.

1.1 Conditions for Opening Channel 
-------------

To open a channel, a customer picks a channel-specific public key, commits to an initial wallet, and receives a signature from the merchant (using their long-term keypair) on that wallet. A wallet consists of a wallet-specific public key, a customer balance, and a total channel balance, and is linked to the customer's channel-specific public key. The channel specific public key, initial customer balance, total channel balance, and initial wallet commitment comprise the customer's channel token.

The keypairs used by both the merchant and the customer must support a blind signature scheme.

1.2 Conditions for Closing Channel
-------------

A customer should be able to close the channel by either opening the initial wallet commitment (if no payments made) or posting a closing token. 

A merchant should be able to close the channel by either posting their closing token or, if the customer posts an outdated version of their closure token (or opens the initial wallet commitment for the channel after one or more payments have been made), a revocation token.

2. Transparent/Shielded Tx: Using T/Z-addresses and Scripting Opcodes
-------------

We assume the following specific features are present:

(1) ``OP_CLTV`` - absolute lock time
(2) ``OP_CSV`` - relative lock time
(3) shielded address support
(4) 2-of-2 multi-sig transparent address support (via P2SH)
(5) Transaction non-malleability
(6) ``OP_BOLT`` opcode: takes two inputs as argument (an integer for mode and a serialized token of hex encoded bytes) and outputs a ``True`` or ``False`` on the stack: 

* Mode 1 (for customer-initiated close). This mode expects a channel token and a customer closure token of one of the following types:

  (a) An opening of the channel's initial wallet commitment. This type of closure token is to be used when no payments have been made on the specified channel. The opcode verifies that the provided commitment opening is valid with respect to the specified channel.
  
  (b) A signature under the merchant's longterm keypair on the customer's current wallet state, together with the wallet state. This type of closure token is to be used when one or more payment have been made on the channel. The opcode validates the merchant signature on the closure token first. Then, the opcode verifies two additional constraints: (1) there are two outputs in the closing transaction: one paying the merchant his balance and the other paying the customer, and (2) the customer’s payout is timelocked (to allow for merchant dispute). 

* Mode 2 (for merchant-initiated close). The opcode expects a channel token and a merchant closure token, which is signed using the customer's channel-specific public key. The opcode validates the customer signature on the provided closure token and verifies that the closing transaction contains a timelocked output paying the total channel balance to the merchant. The output must be timelocked to allow for the customer to post her own closing transaction with a different split of channel funds.

* Mode 3 (for merchant dispute of customer closure token). This mode is used in a merchant closing transaction to dispute a customer's closure token. The opcode expects a merchant revocation token. It validates the revocation token with respect to the wallet pub key posted by the customer in the customer's closing transaction. If valid, the customer's closure token will be invalidated and the merchant's closing transaction will be deemed valid.

**Privacy Limitations**: The aggregate balance of the channel will be revealed in the 2-of-2 multisig transparent address. Similarly, the final spliting of funds will be revealed to the network. However, for channel opening and closing, the identity of the participants remain hidden. Channel opening and closing will also be distinguishable on the network due to use of ``OP_BOLT`` opcodes.

2.1 Channel Opening
-------------
The customer creates a funding transaction that spends ZEC from a shielded address to a 2-of-2 multi-sig transparent address using a pay-to-script-hash (P2SH) output with a `pay-to-public-key-hash (P2PKH)` embedded inside the script. Here is what the funding transaction looks like when opening the channel.

2.2 Funding Transaction
-------------
The funding transaction is by default funded by only one participant, the customer.  

This transaction has 2 shielded inputs (but can be up to some N) and 1 output to a P2SH address (to a 2-of-2 multi-sig address) with a the merchant public key. Note that the customer can specify as many shielded inputs to fund the channel sufficiently (limited only by the overall transaction size).

* ``lock_time``: 0
* ``nExpiryHeight``: 0
* ``valueBalance``: ?
* ``nShieldedSpend``: 1 or N (if funded by both customer and merchant)
* ``vShieldedSpend[0]``: tx for customer’s note commitment and nullifier for the coins
  
  - ``cv``: commitment for the input note
  - ``root``: root hash of note commitment tree at some block height
  - ``nullifier``: unique serial number of the input note
  - ``rk``: randomized pubkey for spendAuthSig
  - ``zkproof``: zero-knowledge proof for the note
  - ``spendAuthSig``: signature authorizing the spend
  
* ``vShieldedSpend[1]``: tx for merchant’s note commitment and nullifier for the coins (if dual-funded)
  
  - ``cv``: commitment for the input note
  - ``root``: root hash of note commitment tree at some block height
  - ``nullifier``: unique serial number of the input note
  - ``rk``: randomized pubkey for spendAuthSig
  - ``zkproof``: zero-knowledge proof for the note
  - ``spendAuthSig``: signature authorizing the spend
* ``tx_out_count``: 1
* ``tx_out``: (using a P2SH address)

   - ``scriptPubKey`` must have the form ``0 <32-byte hash>``, where the latter is the hash of the script needed to spend the output.

To redeem this output, the redeeming transaction must present:

	scriptSig: 0 <mode> <<channel-token> <closing-token> or <rev-token>> <cust-sig> <merch-sig> <serializedScript>, 
	
where ``serializedScript`` is as follows: 
	
	2 <cust-pubkey> <merch-pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT

* ``bindingSig``: a signature proving that (1) the total value spent by Spend transfers - Output transfers = value balance field.

The customer broadcasts the funding transaction and waits for the network to confirm the transaction. Once the transaction is confirmed, the customer completes its initial commitment transaction and provides the channel token to the merchant so he can create his own commitment transaction.

2.3 Initial Wallet Commitment
-------------
The initial commitment transaction is generated by the customer during the channel establishment but is not broadcast to the network. The customer's commitment transaction (below) contains an output that can be spent immediately by the merchant or can be spent by the customer after a relative timeout (or a certain number of blocks). This approach allows the merchant to see the parent transaction and spend the output with a revocation token if the customer posted an outdated closure token.

The customer's commitment transaction is described below.

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set such that commitment transactions can be included in a current block.
* ``txin`` count: 1
    
   - ``txin[0]`` outpoint: references the funding transaction txid and output_index
   - ``txin[0]`` script bytes: 0
   - ``txin[0]`` script sig: 0 <mode> <<channel-token> <closing-token> or <rev-token>> <cust-sig> <merch-sig> <2 <cust-pubkey> <merch-pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT>

* ``txout`` count: 2
* ``txouts``: 

  * ``to_customer``: a timelocked (using ``OP_CSV``) P2SH output sending funds back to the customer. So ``scriptPubKey`` is of the form ``0 <32-byte-hash>``.  
      - ``amount``: balance paid back to customer
      - ``nSequence: <time-delay>``
      - ``script sig: 1 <cust-sig> 0 <serializedScript>``
      - ``serializedScript``:
      
		OP_IF		  
	  	  OP_2 <revocation-pubkey> <merch-pubkey> OP_2
		OP_ELSE
		  <time-delay> OP_CSV OP_DROP <cust-pubkey>
		OP_ENDIF
		OP_CHECKSIGVERIFY
		
  * ``to_merchant``: A P2PKH to merch-pubkey output (sending funds back to the merchant), i.e.
      * ``scriptPubKey``: ``0 <20-byte-key-hash of merch-pubkey>``

The merchant can create their own initial commitment transaction as follows.

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set such that commitment transactions can be included in a current block.
* ``txin`` count: 1
    
   - ``txin[0]`` outpoint: references the funding transaction txid and output_index
   - ``txin[0]`` script bytes: 0
   - ``txin[0]`` script sig: 0 <mode> <<closing-token> <channel-token> or <rev-token>> <cust-sig> <merch-sig> <2 <cust-pubkey> <merch-pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT>

* ``txout`` count: 1
* ``txouts``: 

  * ``to_merchant``: a timelocked (using ``OP_CSV``) P2SH output sending all the funds back to the merchant. So ``scriptPubKey`` is of the form ``0 <32-byte-hash>``.  
      - ``amount``: balance paid back to merchant
      - ``nSequence: <time-delay>``
      - ``script sig: 1 <merch-sig> 0 <serializedScript>``
      - ``serializedScript``:
      
		OP_IF
	  	  OP_2 <closing-token> <cust-pubkey> OP_2
		OP_ELSE
		  <time-delay> OP_CSV OP_DROP <merchant-pubkey>
		OP_ENDIF
		OP_CHECKSIGVERIFY

After each payment on the channel, the customer obtains a closing token for the updated channel balance and provides the merchant a revocation token for the previous state along with the associated wallet public key (this invalidates the pub key). If the customer initiated closing, the merchant can use the revocation token to spend the funds of the channel if the customer posts an outdated commitment transaction.

2.4 Channel Closing
-------------
To close the channel, the customer can initiate by posting the most recent commitment transaction (in Section 2.3) that spends from the multi-signature transparent address with inputs that satisfies the script and the ``OP_BOLT`` opcode in mode 1. This consists of a closing token (i.e., merchant signature on the wallet state) or an opening of the initial wallet commitment (if there were no payments on the channel via mode 2). 

Once the timeout has been reached, the customer can post a transaction that claims the output of the customer closing transaction to a shielded output (see below for an example). Before the timeout, the merchant can claim the funds from the ``to_customer`` output by posting a revocation token, if they have one.

The merchant can immediately claim the ``to_merchant`` output from the customer closing transaction to a shielded address by presenting their P2PKH address. 

Because we do not know how to encumber the outputs of shielded outputs right now, we will rely on a standard transaction to move funds from the closing transaction into a shielded address as follows:

* ``version``: 2
* ``groupid``: specify group id
* ``locktime``: 0
* ``txin`` count: 1
   * ``txin[0]`` outpoint: ``txid`` and ``output_index``
   * ``txin[0]`` sequence: 0xFFFFFFFF
   * ``txin[0]`` script bytes: 0
   * ``txin[0]`` script sig: ``0 <cust-sig> <merch-sig>``
* ``nShieldedOutput``: 1
* ``vShieldedOutput[0]``:
   - ``cv``: commitment for the output note
   - ``cmu``: ...
   - ``ephemeralKey``:ephemeral public key
   - ``encCiphertext``: encrypted output note (part 1)
   - ``outCiphertext``: encrypted output note (part 2)
   - ``zkproof``: zero-knowledge proof for the note

The merchant can initiate closing by posting the initial commitment transaction (in Section 2.3) from establishing the channel that pays the merchant the full balance of the channel with a time lock that allows for customer dispute. The merchant can then post a separate standard transaction that moves those funds to a shielded address.

3. Custom Shielded Tx: Using Z-addresses and Scriptless
-------------
We assume the following features are present:

(a) ``lock_time`` - for absolute lock time
(b) A way to enforce relative lock time
(c) 2-of-2 multi-sig shielded address support
(d) All inputs/outputs are specified from/to a shielded address
(e) A method to encumber the outputs of a shielded transaction
(f) An extension to the transaction format to include BOLT (e.g., like ``vBoltDescription``)
(g) Extend the ``SIGHASH`` flags to cover the extended field

The goal here is to perform all the same validation steps for channel opening/closing without relying on the scripting system, as well as allowing for relative timelocks (the equivalent of ``OP_CSV``). In order to support multihop payments, we need absolute timelocks as well (the equivalent of ``OP_CLTV``). We also want to ensure that transactions are non-malleable in order to allow for unconfirmed dependency transaction chains.

**Limitations/Notes**: With extensions to shielded transaction format, it may be evident whenever parties are establishing private payment channels. We appreciate feedback on the feasibility of what is proposed for each aspect of the Bolt protocol.

3.1 Channel Opening
-------------
The customer creates a funding transaction that spends ZEC from a shielded address to a 2-of-2 multi-sig shielded address. Here is the flow (1) creating a multisig shielded address specifying both parties keys and (2) generating channel tokens.

3.2 Funding Transaction
-------------
The funding transaction is by default funded by only one participant, the customer. It could also be funded by the merchant. 

This transaction has 2 shielded inputs (but can be up to some N) and 1 output to a 2-of-2 shielded address with the merchant public key. If an ``vBoltDescription`` field is added, then we could use it to store the channel parameters and the channel token for opening the channel.

3.3 Initial Wallet Commitment
-------------
The initial wallet commitment will spend from the shielded address to two outputs: a P2SH output (for customer) and P2PKH (for merchant).  The first output pays the customer with a timelock (or the merchant with a revocation token) and the second output allows the merchant to spend immediately. It is not clear to us whether it will be possible to encumber the outputs of shielded outputs directly. 

We would appreciate feedback on the possibilities with creating commitment transactions via shielded transactions only.

3.4. Channel Closing
-------------
The channel closing consists of the customer broadcasting the most recent commitment transaction and requires that they present the closure token necessary to claim the funds. Similarly, the merchant would be able to claim the funds with the appropriate revocation token as well.

4. Bitcoin Compatible: Using T-address and Scripting Opcodes
-------------
We assume the following features are present:

(a) ``OP_CLTV`` - absolute lock time
(b) ``OP_CSV`` - relative lock time
(c) 2-of-2 multi-sig transparent address support
(d) Transaction non-malleability for t-addresses
(e) ``OP_BOLT`` opcode: takes two inputs as argument (a mode and a serialized token) and outputs a `True` or `False` on the stack. Same description from Section 2.

**Note**: We assume P2WSH as it enforces transaction non-malleability and allows unconfirmed transaction dependency chains. Another approach to transaction non-malleability would be acceptable.

**Privacy Limitations**. With T-addresses, we give up the ability to hide the initial balance for the funding transaction and final balances when closing the channel. Channel opening will be distinguishable on the network due to use of ``OP_BOLT`` opcodes.

4.1 Channel Opening
-------------
A channel is established when two parties successfully lock up funds in a multi-sig transparent address on the blockchain. The funds remain spendable by the customer in a commitment transaction that closes the channel and splits the funds as indicated by the last invocation of the (off-chain) pay protocol. The merchant can close the channel using their own commitment transaction, which claims the entire channel balance while giving the customer time to post the appropriate commitment transaction for closing.

The customer and merchant first initialize the channel by generating their respective keypairs and computing the channel tokens for the initial wallet commitment.

The customer then creates a funding transaction that deposits ZEC to a 2-of-2 multi-signature transparent address using a pay-to-witness-script-hash (P2WSH) output (alternatively, a P2WPKH nested in a P2SH could work). The customer obtains a signature for the funding transaction and commitment transaction from the merchant. The customer can then post the funding transaction to the blockchain.

4.2 Funding Transaction
-------------
The funding transaction is by default funded by only one participant, the customer. This transaction is a P2WSH SegWit transaction. Here is a high-level of what the funding transaction would look like:

	witness: 0 <mode> <<channel-token> <closing token> or <rev-token>> <cust-sig> <merch-sig> <2 <cust-pubkey> <merch-pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT>
	
	scriptSig: (empty)	
	scriptPubKey: 0 <32-byte-hash>

This is a standard SegWit P2WSH transaction. Note that the witness and empty ``scriptSig`` are provided by a subsequent transaction that spends the funding transaction output. The ``scriptPubKey`` of the funding transaction indicates that a witness script should be provided with a given hash; the ``witnessScript`` (≤ 10,000 bytes) is popped off the initial witness stack of a spending transaction and the SHA256 of witnessScript must match the 32-byte hash of the following:

	2 <cust-pubkey> <merch-pubkey> 2 OP_CHECKMULTISIGVERIFY	
	OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT
	
4.3 Initial Wallet Commitment
-------------
This wallet commitement below is created first during channel initialization, but the customer does not broadcast to the network.

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set so that the commitment can be included in current block 
* ``txin`` count: 1

  - ``txin[0]`` outpoint: ``txid`` and ``outpoint_index`` of the funding transaction
  - ``txin[0]`` script bytes: 0
  - ``txin[0]`` witness: ``0 <mode> <<channel-token> <closing token> or <rev-token>> <cust-sig> <merch-sig> <2 <cust_fund_pubkey> <merch_fund_pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT>``

* ``txouts``: 
* ``to_customer``: a timelocked (using ``OP_CSV``) version-0 P2WSH output sending funds back to the customer. So scriptPubKey is of the form ``0 <32-byte-hash>``. A customer node may create a transaction spending this output with:

  - ``nSequence: <time-delay>``
  - ``witness: <closing-token> <cust-sig> 0 <witnessScript>``
  - ``witness script:``
  
	OP_IF
	  # Merchant can spend if revocation token available
	  OP_2 <rev-pubkey> <merch-pubkey> OP_2
	OP_ELSE
	  # Customer must wait 
	  <time-delay> OP_CSV OP_DROP <cust-pubkey>
	OP_ENDIF
	OP_CHECKSIGVERIFY 

* ``to_merchant``: A P2WPKH to merch-pubkey output (sending funds back to the merchant), i.e.
   * ``scriptPubKey``: ``0 <20-byte-key-hash of merch-pubkey>``

Or, if a revoked commitment transaction is available, the merchant may spend the ``to_customer`` output with the above witness script and witness stack:

	3 <rev-token> 1 <witnessScript>
			
To spend ``to_merchant`` output, the merchant publishes a transaction with:
	
	witness: <merch-sig> <merch-pubkey> <witnessScript>

The merchant can create their own initial commitment transaction as follows.

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set so that the commitment can be included in current block 
* ``txin`` count: 1

  - ``txin[0]`` outpoint: ``txid`` and ``outpoint_index`` of the funding transaction
  - ``txin[0]`` script bytes: 0
  - ``txin[0]`` witness: ``0 <mode> <<channel-token> <closing token> or <rev-token>> <cust-sig> <merch-sig> <2 <cust_fund_pubkey> <merch_fund_pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT>``

* ``txout`` count: 1
* ``txouts``: 

  * ``to_merchant``: a timelocked (using ``OP_CSV``) P2WSH output sending all the funds back to the merchant. So ``scriptPubKey`` is of the form ``0 <32-byte-hash>``.  
      - ``amount``: balance paid back to merchant
      - ``nSequence: <time-delay>``
      - ``witness: 1 <merch-sig> 0 <witnessScript>``
      - ``witnessScript``:
      
		OP_IF
	  	  OP_2 <closing-token> <cust-pubkey> OP_2
		OP_ELSE
		  <time-delay> OP_CSV OP_DROP <merchant-pubkey>
		OP_ENDIF
		OP_CHECKSIGVERIFY


4.4 Channel Closing
-------------
The customer initiates channel closing by posting a closing transaction that spends from the multi-signature address with a witness that satisfies the witnessScript and the ``OP_BOLT`` opcode in mode 1. This consists of a closing token (i.e., merchant signature on the wallet state) or an opening of the initial wallet commitment (if there were no payments on the channel via mode 2). 

Once the timeout has been reached, the customer can post a transaction that claims the output of the customer closing transaction to another output. Before the timeout, the merchant can claim the funds from the ``to_customer`` output by posting a revocation token (via mode 3), if they have one. The merchant can immediately claim the ``to_merchant`` output from the customer closing transaction by presenting their P2WPKH address.

The merchant can initiate closing by posting the initial commitment transaction (in Section 4.3) from establishing the channel that pays the merchant the full balance of the channel with a time lock that allows for customer dispute.

Reference Implementation
========================

We are currently working on a reference implementation based on section 2 in a fork of Zcash here: https://github.com/boltlabs-inc/zcash.

References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
