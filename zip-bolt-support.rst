::

  ZIP: XXX
  Title: Add support for Bolt protocol 
  Authors: J. Ayo Akinyele <ayo@boltlabs.io>
           Colleen Swanson <swan@boltlabs.io>
  Credits: Ian Miers <imiers@z.cash?>
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

Layer 2 protocols like Lightning enable scalable payments for Bitcoin. We want to implement a similar protoocol on top of Lightninng such that we can build scalable and private payments on top of Zcash.

Specification
=============

This specification details three potential approaches to integrating the features of Bolt into Zcash. 

1. General requirements for Bolt protocol
--------------------------

Private payment channels as designed by the Bolt protocol require the following capabilities to achieve the stated anonymity properties at layer 2:

1. Ability to create a funding transaction such that the transaction inputs are anonymous.
2. Ability to escrow funds to a multi-signature address with a fix for transaction malleability.
3. Ability to verify additional fields from the transaction inputs/outputs as part of signature verification.
4. Ability to do relative time locks for commitment transactions to support unilateral channel closing.
5. Ability to do absolute and relative time locks to support multi-hop payments.
6. Ability to validate Bolt-specific commitment opening message and closing signature:

- check the validity of the commitment opening
- check the validity of randomized/blinded signature on the wallet commitment in closure token
- check the validity of revocation token signature in the event of a channel dispute by merchant
 
7. Ability to verify the transaction output such that:

- first output pays out to customer with a time lock
- second output pays out to merchant immediately

**Channel Operation Assumptions.**
 - Single-funded channel by customer with a minimum fee paid to the merchant.
 - Customer initiates the closing transaction. Or, merchant can broadcast a message to the customer node that requests for the customer to initiate closing.
 - If the customer initiates closing, then Merchant can dispute the closing transaction if it disagrees with the refund token in the closing transaction.

2. Custom Shielded Tx: Using T/Z-addresses and Scripting Opcodes
-------------

We assume the following specific features are present:

(a) ``OP_CLTV`` - absolute lock time
(b) ``nExpiryHeight`` - relative lock time
(c) shielded address support
(d) 2-of-2 multi-sig transparent address support (via P2SH)
(e) Transaction non-malleability
(f) ``OP_BOLT`` opcode: takes two inputs as argument (an integer for mode and a serialized token of hex encoded bytes) and outputs a ``True`` or ``False`` on the stack:

- Mode 1 (``OPEN``). The opcode expects a channel token and validates that the channel opening is correct. That is, validates that the opening of the initial wallet commitment specified with the customer’s channel token. 
- Mode 2 (``CLOSE``). The opcode expects a channel closure token (with refund token and hash of wallet pub key for latest state embedded) as part of closing transaction. It validates the signature on the closure token first. Then, validates the refund token and verifies two additional constraints: (1) there are two outputs in the closing transaction: one paying the merchant his balance and the other paying the customer, (2) the customer’s payout is timelocked (to allow for merchant dispute).
- Mode 3 (``DISPUTE``). The opcode expects a revocation token. It validates the revocation token with respect to the wallet pub key posted by customer in closing transaction. If valid, then it means that the refund token will be invalidated.

**Privacy Limitations**. The aggregate balance of the channel will be revealed in the 2-of-2 multisig transparent address. However, the identity of the participants will remain hidden.
Channel opening and closing will be distinguishable on the network due to use of ``OP_BOLT`` opcodes.

2.1 Channel Opening
-------------
Alice and Bob initialize the channel by producing an initial wallet commitment from generating the channel tokens via the Establish protocol.

Alice (as customer) and Bob create a funding transaction that spends ZEC from shielded addresses to a 2-of-2 multi-sig transparent address using a pay-to-script-hash (P2SH) output with a `pay-to-public-key-hash (P2PKH)` embedded inside the script. Here is what the funding transaction looks like when opening the channel.

2.2 Funding Transaction
-------------
The funding transaction is by default funded by only one participant, the customer. It could also be funded by the merchant. 

This transaction has 2 shielded inputs and 1 output to a P2SH address and makes use of Bech32 addresses:

* ``lock_time``: 0
* ``nExpiryHeight``: 0
* ``valueBalance``: ?
* ``nShieldedSpend``: 1 or 2 (if funded by both customer and merchant)
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
* ``tx_out``: (using a P2SH output)

  - ``scriptPubKey`` must have the form ``0 <32-byte hash>``, where the latter is the hash of the script needed to spend the output.
To redeem this output, the redeeming transaction must present:

	scriptSig: 0 0 <channel-token> <channel-pubkey> <cust-sig> <merch-sig> <serializedScript>, 
	
where ``serializedScript`` is as follows: 
	
	2 <cust-pubkey> <merchant-pubkey> 2 OP_CHECKMULTISIGVERIFY 
	OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT

* ``bindingSig``: a signature that proves that (1) the total value spent by Spend transfers - Output transfers = value balance field.

[TODO: provide example transaction here.]

2.3 Initial Wallet Commitment
-------------
The initial commitment transaction is generated by the customer during the channel initialization but does not broadcast to the network.

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set such that commitment transactions can be included in a current block.
* ``txin`` count: 1

- ``txin[0]`` outpoint: references the funding transaction txid and output_index
- ``txin[0]`` script bytes: 0
- ``txin[0]`` witness: 0 <channel-token> <wallet-pubkey> <cust-sig> <merch-sig> <2 <cust_fund_pubkey> <merch_fund_pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT>
* nShieldedOutput: 2

- ``vShieldedOutput[0-1]``: 
- ``cv``: commitment for the input note
- ``cmu``:...
- ``ephemeralKey``:ephemeral public key
- ``encCiphertext``: encrypted output note (part 1)
- ``outCiphertext``: encrypted output note (part 2)
- ``zkproof``: zero-knowledge proof for the note

[TODO: update commitment transaction to reflect transaction in reference implementation.]

2.4 Channel Closing
-------------
To close the channel, the customer can initiate by posting a commitment transaction that spends from the multi-signature transparent address with a witness that satisfies the script and the ``OP_BOLT`` opcode.

[TODO: update with transaction details.]

3. Custom Shielded Tx: Using Z-addresses and Scriptless
-------------
We assume the following specific features are present:

(a) ``lock_time`` - for absolute lock time
(b) ``nExpiryHeight`` - for relative lock time
(c) 2-of-2 multi-sig shielded address support
(d) Inputs come from a shielded address and outputs to a shielded address
(e) A method to encumber the outputs of a shielded transaction.
(f) An extension to the transaction format to include BOLT

The goal here is to perform all the same validation steps for channel opening/closing without relying on the scripting system, as well as allowing for relative timelocks (the equivalent of ``OP_CSV``). In order to support multihop payments, we need absolute timelocks as well (the equivalent of ``OP_CLTV``). We also want to ensure that transactions are non-malleable in order to allow for unconfirmed dependency transaction chains.

4. Bitcoin Compatible: Using T-address and Scripting Opcodes
-------------
We assume the following features are present:

(a) ``OP_CLTV`` - absolute lock time
(b) ``OP_CSV`` - relative lock time
(c) 2-of-2 multi-sig transparent address support
(d) Transaction non-malleability
(e) ``OP_BOLT`` opcode: takes two inputs as argument (a mode and a serialized token) and outputs a `True` or `False` on the stack:

- Mode 1 (``OPEN``). The opcode expects a channel token and validates that the channel opening is correct. That is, validates  that the opening of the initial wallet commitment specified with the customer’s channel token. 
- Mode 2 (``CLOSE``). The opcode expects a channel closure token (with refund token and hash of wallet pub key for latest state embedded) as part of closing transaction. It validates the signature on the closure token first. Then, validates the refund token and verifies two additional constraints: (1) there are two outputs in the closing transaction: one paying the merchant his balance and the other paying the customer, (2) the customer’s payout is timelocked (to allow for merchant dispute).
- Mode 3 (``DISPUTE``). The opcode expects a revocation token. It validates the revocation token with respect to the wallet pub key posted by customer in closing transaction. If valid, then it means that the refund token will be invalidated.

**Note**: that we wrote this specification assuming P2WSH because this enables transaction non-malleability and allows unconfirmed transaction dependency chains. Another approach to transaction non-malleability would be acceptable.

**Privacy Limitations**. With T-addresses, we give up the ability to hide the initial balance for the funding transaction and final balances when closing the channel. Channel opening and closing will be distinguishable on the network due to use of ``OP_BOLT`` opcodes.

4.1 Channel Opening
-------------
A channel is established when two parties successfully lock up funds in a multi-sig transparent address on the blockchain. The funds remain spendable by both parties and split according to the updated balance in a commitment transaction.

Alice and Bob first initialize the channel by generating their respective keypairs and computing the channel tokens for the initial wallet commitment.

Alice (as customer) then creates a funding transaction that deposits ZEC to a 2-of-2 multi-signature transparent address using a pay-to-witness-script-hash (P2WSH) output (alternatively, a P2WPKH nested in a P2SH could work). Alice obtains a signature for the funding transaction from Bob.

Once the funding transaction has been confirmed on the blockchain, Alice and Bob have effectively activated and established the channel.

4.2 Funding Transaction
-------------
The funding transaction is by default funded by only one participant, the customer. This transaction is a P2WSH segwit transaction. Here is a high-level of what the funding transaction would look like:

	witness: 0 <channel-token> <cust-sig> <merch-sig> <2 <cust-pubkey> <merch-pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT>
	
	scriptSig: (empty)	
	scriptPubKey: 0 <32-byte-hash>

This is a standard Segwit P2WSH transaction. Note that the witness and empty ``scriptSig`` are provided by a subsequent transaction that spends the funding transaction output. The ``scriptPubKey`` of the funding transaction indicates that a witness script should be provided with a given hash; the ``witnessScript`` (≤ 10,000 bytes) is popped off the initial witness stack of a spending transaction and the SHA256 of witnessScript must match the 32-byte hash of the following:

	2 <cust-pubkey> <merch-pubkey> 2 OP_CHECKMULTISIGVERIFY	
	OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT

The channel token consists of the customer’s channel public key and wallet commitment from initializing the channel. The unique channel identifier is the hash of the channel public key.

The ``<channel-token>`` is a serialized token with the following structure: (a) Initial wallet commitment, initial wallet public key and the channel public key.
	
4.3 Initial Wallet Commitment
-------------
This wallet commitement below is created first during channel initialization, but the customer does not broadcast to the network.

* ``version``: specify version number
* ``groupid``: specify group id
* ``locktime``: should be set such that the commitment can be included in current block 
* ``txin`` count: 1

  - ``txin[0]`` outpoint: txid and outpoint _index of the funding transaction
  - ``txin[0]`` script bytes: 0
  - ``txin[0]`` witness: ``0 <channel-token> <cust-sig> <merch-sig> <2 <cust_fund_pubkey> <merch_fund_pubkey> 2 OP_CHECKMULTISIGVERIFY OP_DUP OP_HASH160 <hash-of-channel-token> OP_EQUALVERIFY OP_BOLT>``

* ``txouts``: 
* ``to_customer``: a timelocked (using ``OP_CSV``) version-0 P2WSH output sending funds back to the customer. So scriptPubKey is of the form ``0 <32-byte-hash>``. A customer node may create a transaction spending this output with:

  - ``nSequence: <time-delay>``
  - ``witness: <refund-token> <cust-sig> 0 <witnessScript>``
  - ``witness script:``
  
	OP_IF
	  # Merchant can spend if revoked CT available
	  OP_2 <revocation-pubkey> <merch-pubkey> OP_2   
	OP_ELSE
	  # Customer must wait 
	  <time-delay> OP_CSV OP_DROP <customer-pubkey>
	OP_ENDIF
	OP_CHECKSIGVERIFY OP_BOLT

* ``to_merchant``: A P2WPKH to merch-pubkey output (sending funds back to the merchant), i.e.
* ``scriptPubKey``: ``0 <20-byte-key-hash of merch-pubkey>``

Or, if a revoked commitment transaction is available, the merchant may spend the output with the above witness script and witness stack:

	<revocation-sig> 1 <witnessScript>
			
To spend this output, the merchant publishes a transaction with:
	
	witness: <merch-sig> <merch-pubkey> <witnessScript>

4.4 Channel Closing
-------------
The customer initiates channel closing by posting a closing transaction that spends from the multi-signature address with a witness that satisfies the witnessScript and the ``OP_BOLT`` opcode: the refund token and the two transaction outputs to the customer (``txout[0]``) and merchant (``txout[1]``). Note that the refund token consists of (a) Mode ID: 2 and (2) a merchant signature on the latest wallet public key and the updated balance of the channel.  The customer’s transaction output is timelocked, while the merchant is able to spend immediately.


Reference Implementation
========================

We are currently working on a reference implementation based on section 2 in a fork of Zcash here: https://github.com/boltlabs-inc/zcash.

References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_

TODO: Add references to BOLT v2 protocol specification
