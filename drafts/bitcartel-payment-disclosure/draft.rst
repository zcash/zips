| Title: Payment Disclosure
| ZIP: 00? (DRAFT)
| Replaces: n/a
| Superseded-by: n/a
| Editor: Simon Liu <simon@z.cash>

==================
Payment Disclosure
==================

Abstract
--------

This ZIP describes a method of proving that a payment was sent to a shielded address.  In the typical case, this means enabling a sender to present a proof that they transferred funds to a recipient's shielded address.  The method described will be compatible with the Zcash Protocol [PROTOCOL] deployed at the launch of the Zcash network.

This document follows the common conventions defined for ZIPs in [ZIP-1].

.. [PROTOCOL] Zcash Protocol Specification: https://github.com/zcash/zips/blob/master/protocol/protocol.pdf
.. [ZIP-1] https://github.com/zcash/zips/blob/master/zips/0001.rst

Copyright Notice
----------------
This ZIP is published under the MIT License.

Motivation
----------
Payment disclosure is useful in a number of situations, for example:

* A sender may need to prove that their payment was sent and received by a recipient.  For example, a customer paid too much for an item and would like to claim a refund from the vendor.
* A third party needs to verify that a payment between sender and recipient was executed successfully.  For example, a regulator needs to confirm a transfer of funds between two parties.

When a transaction involves only transparent addresses, the sender and recipient can verify payment by examining the blockchain.  A third party can also perform this verification if they know the transparent addresses of the involved parties.

However, if the transaction involves shielded addresses, the blockchain by itself does not contain enough information from which a record of the payment can be reconstructed and verified.

Let us examine the types of transaction that might occur and when a method of payment disclosure would be useful:

transparent --> transparent
  The source, destination and amount are visible on the public blockchain.  Payment disclosure is not required.

transparent --> shielded
  The destination address and amount sent to that address cannot be confirmed. Payment disclosure is required.

shielded --> transparent
  The recipient can see the amount received at their destination address, but cannot identify the sender.  Payment disclosure is required.

shielded --> shielded
  The sender, recipient and amount are unknown.  Payment disclosure required.

TODO: Perhap use a table to make this easier to understand, from perspective of sender,recipient and third party?

Design Overview
---------------

Allow the sender to automatically or optionally create a payment disclosure when creating a transaction involving shielded addresses.

The sender or a third party can present this payment disclosure to the recipient to prove that funds were sent to their address.

Example
-------
A group of coworkers go out for dinner and decide to split the bill.  The restaurant only accepts physical cash.  Alice ends up paying the entire bill as her coworkers have no cash on them.

The next day Bob sends 1 ZEC to Alice's shielded address for his share of the bill.  Other coworkers do the same.  A week later Alice remembers that she is owed money so she checks her shielded address.  Alice sees that the balance is less than what it should be, so she asks her coworkers to confirm their payments.

Bob retrieves his payment disclosure and emails it to Alice.  Alice is travelling and only has access to her smartphone.  She visits a Zcash blockchain explorer and copies the payment disclosure into the search box. The explorer confirms that Bob paid his share.

Charlie attempts to retrieve the payment disclosure but can't find one.  Charlie had used the command line to send his funds to Alice, but never checked the status of the z_sendmany operation.  Checking the debug logs he discovers that the operation failed due to an incorrect parameter.  Charlie tells Alice that he will re-send his payment.


Design Considerations
---------------------
The payment disclosure does not prove that the party presenting the payment disclosure is the sender.

To mitigate against a replay attack, the recipient could enforce a policy where the first person to present a given payment disclosure is the honest sender.

To prevent a man-in-the-middle attack, the recipient could pose an interactive challenge involving some out-of-band secret which only the sender would pass.

A non-interactive solution is also possible:

#. The sender includes data, such as a refund address, in the memo field of a payment to a shielded address.  The memo field is non-malleable as it is part of the data signed by the sender when creating JoinSplitSig [PROTOCOL] §4.1.6 Signatures.  Currently, the public key to verify the signature is stored in the blockchain along with the transaction.
#. When presenting the payment disclosure to a recepient, the sender signs the payment disclosure with the JoinSplitSig private key which only they would know.  The JoinSplitSig key pair is ephemeral and normally discarded but the method described in this ZIP will retain the private portion.  The recipient can then use the public key to verify the signed disclosure.

Using the JoinSplitSig key pair in this way also means that a sender can make payments without having to first provide a refund address or other detail at the time of the original payment.  If at later date the sender and recipient need to confirm the payment, the sender can sign and send any data required to the recipient, who can in turn verify it.


Known Issues
------------
Both plaintext outputs of a joinsplit are currently encrypted with the same ephemeral secret key. (TODO: Is there an existing ticket which explains the rationale for this?)

This means that a payment disclosure which includes the ephemeral secret key intended to decipher the note ciphertext belonging to a particular joinsplit output, creates a privacy leak by also deciphering the other joinsplit output and revealing it's amount and payment address.

Note the current implementation of the ``z_sendmany`` RPC call:

- When sending from a transparent address to shielded addresses, each shielded address will occupy one output of a joinsplit.  Thus a payment address to a different recipient could be revealed.

- When sending involves chained joinsplits, for each joinsplit, one output is for payment to a recipient's address, while the other output is used as change back to the sender.  Thus the change address will be revealed, which is the sender's own shielded address.

A proposal to prevent information leakage of change addresses is currently under development [KDFT].  TODO: Does this block ZIP approval?

Alao note that an independent third party cannot know for sure if the sender and recipient are not colluding to hide value transfer.  JoinSplits have two inputs and two outputs.  The recipient may identify their receiving address for one output, but not disclose the fact that the other output also belongs to them.

TODO: What happens if a transaction is created (at which point a payment disclosure can be created) but never gets mined and is stuck in the mempool?  Should the payment disclosure be retained or purged?

.. [KDFT] https://github.com/zcash/zcash/issues/2102


Specification
-------------
When creating a shielded transaction, for each JoinSplit output, a data structure is created to record the following fields:

- transaction id
- index [0..len-1] of JoinSplit in array of JoinSplits contained in transaction
- index [0..1] of JoinSplit output
- recipient's payment address is a shielded address ``(a_pk, pk_enc)`` [PROTOCOL] §3.1 Payment Addresses and Keys
- symmetric key used to encrypt the note, also referred to as the ephemeral secret key ``esk`` [PROTOCOL] §4.10.1 Generate a new KA (public, private) key pair ``(epk, esk)``.
- JoinSplitSig private key used to sign the JoinSplit transaction ``joinSplitPrivKey`` [PROTOCOL] §4.4 Sending Notes

The payment disclosure data should be persisted to disk or a database so it can be retrieved later.

When persisting, third party applications should expect serialization of payment disclosure to follow Zcash and upstream convention.

::

    ADD_SERIALIZE_METHODS;
    ...
    READWRITE(txid);
    ...
    READWRITE(joinSplitPrivKey);

A new RPC call will be introduced to allow the sender to retrieve the payment disclosure data for a given shielded output index.

``z_getpaymentdisclosure txid joinsplit_index output_index [message]``

- Returns the payment disclosure in hexadecimal format.
- Message is an optional parameter, a UTF-8 string.  We may want to restrict/sanitize this user input, e.g. number of characters, allowed characters.

The sender want sthe payment disclosure to be non-malleable, to prevent an attacker modifying details like the refund address.  To achieve this, the sender will sign the payment disclosure with the JoinSplitSig private key and append the signature to the end of the payment disclosure data.

A new RPC call will be introduced to allow a third party to verify a payment disclosure.

``z_validatepaymentdisclosure paymentdisclosure``

Validates a payment disclosure and returns JSON output as follows:

::

    {
    valid : true,
    rawhex : "0011...ff",
    version: 0
    txid: "4e...",
    jsindex: 0,
    outputindex: 1,
    paymentaddress: zABC123...,
    value: 10.56100002
    message: "pay me at z007",
    signature: "10ab23..."
    }

Valid field is true if all the following conditions hold:

- txid is confirmed in the blockchain
- jsindex is valid for the txid
- outputindex is within range [0..1]
- paymentaddress is a valid shielded address for the network we are on
- value is within range [0..MAX_MONEY]
- message is within constraints e.g. number of characters, allowed characters
- signature is valid for all of the above fields

Otherwise an error field is returned explaining why the payment disclosure is invalid:

::

    {
    valid : false,
    ...
    error : "The payment disclosuse is invalid because..."
    }


Implementation
--------------
TODO: Link to commits in Github

A reference implementation will be added to zcashd as an experimental feature.  To enable payment disclosure, set the following two options to true:

* `-paymentdisclosure=1`
* `-experimentalfeatures=1`

A third party trying to validate payment disclosure must track all transactions and thus enable the option:

* `-txindex=1`

In this implementation we will assume that once the feature is enabled, the node will create and store a payment disclosure for every transaction sent which involves a shielded address.

When the sender calls RPC call ``z_sendmany`` and creates a shielded transaction in ``asyncrpcoperation.cpp``:

#. retain the ephemeral joinSplitPrivKey used to sign the transaction
#. retain the ephemeral secret key used for symmetric encryption of the note plaintext

Record relevant data in a struct (or class) defined as follows:

::

    struct PaymentDisclosureKey {
        uint256 txid            // primitives/transaction.h
        size_t js;              // Index into CTransaction.vjoinsplit
        uint8_t n;              // Index into JSDescription fields of length ZC_NUM_JS_OUTPUTS
    };

    struct PaymentDisclosureInfo {
        uint8_t version;          // 0 = experimental, 1 = first production version, etc.
        uint256 esk;              // zcash/NoteEncryption.cpp
        uint256 joinSplitPrivKey; // primitives/transaction.h
    };

Persist the object in a LevelDB key-value store, saved in a subfolder of the configured datadir:

    ``DATADIR/paymentdisclosure/``

Where key-value entries are:

::

    Key: PaymentDisclosureKey
    Value: PaymentDisclosureInfo

Given the above, by default on Linux, the payment disclosure database will be saved under:

    ``$HOME/.zcash/paymentdisclosure/``

The sender may optionally:

- log records to ``debug.log`` using a new debug category ``paymentdisclosure``
- have the records returned in result of RPC call ``z_getoperationresult``

If the sender needs to provide a payment disclosure to the recipient or a third party, the sender will use RPC call ``z_getpaymentdisclosure`` to generate a Payment Disclosure.

``z_getpaymentdisclosure txid joinsplit_index output_index [message]``

To create a valid Payment Disclosure an implementation must:

#. Check the txid was confirmed in the blockchain
#. Create a ``PaymentDisclosureKey`` from parameters to RPC call
#. Use the key to retrieve its value ``PaymentDisclosureInfo`` from storage
#. Create and populate a ``PaymentDisclosure``

    ::
    
        struct PaymentDisclosurePayload {
            uint8   version;        // 0 = experimental, 1 = first production version, etc.
            uint256 esk;            // zcash/NoteEncryption.cpp
            uint256 txid;           // primitives/transaction.h
            size_t js;              // Index into CTransaction.vjoinsplit
            uint8_t n;              // Index into JSDescription fields of length ZC_NUM_JS_OUTPUTS
            std::string message     // parameter to RPC call
        };

#. Serialize ``PaymentDisclosurePayload`` and sign the raw data using the ``joinSplitPrivKey`` to generate a signature ``payloadSig``.  Sample C++ code to do this:

    ::
    
        // Serialize and hash
        CHashWriter ss(SER_GETHASH, 0);
        ss << payload << nHashType;
        uint256 dataToBeSigned = ss.GetHash();
    
        // Compute the payload signature
        unsigned char[64] payloadSig;
        if (!(crypto_sign_detached(&payloadSig[0], NULL,
            dataToBeSigned.begin(), 32,
            joinSplitPrivKey
            ) == 0))
        {
            throw std::runtime_error("crypto_sign_detached failed");
        }
    
        // Sanity check
        if (!(crypto_sign_verify_detached(&payloadSig[0],
            dataToBeSigned.begin(), 32,
            joinSplitPubKey.begin()
            ) == 0))
        {
            throw std::runtime_error("crypto_sign_verify_detached failed");
        }


#. Construct and serialize a PaymentDisclosure object using the data generated so far.

    ::
    
        struct PaymentDisclosure {
            PaymentDisclosurePayload    payload;
            unsigned char[64]           payloadSig;
        }

#. Return to the caller a JSON object containing the hex string of the serialized PaymentDisclosure.  If there were errors generating the payment disclosure, return a standard JSON-RPC error with an appropriate error message.

::

    {
      "hex" : "091234ABCDEF234781248273842738491....."
    }


This raw hex string can be given to the recipient or a third party to use with the new RPC call ``z_validatepaymentdisclosure``:

``z_validatepaymentdisclosure paymentdisclosure``


To validate a payment disclosure, perform the following steps:

1. Deserialize the raw hex string into a ``PaymentDisclosure`` object
2. Retrieve the ``joinSplitPubKey`` for the transaction and verify the payment disclosure signature ``payloadSig``.
3. Retrieve the note ciphertext from the blockchain for ``txid``, ``js``, ``n``.
4. Use the ``esk`` to decrypt the ciphertext into plain text
5. Return JSON output as described above in the specification. 

Possible error messages which could cause validation to fail include:

- "txid was not confirmed in blockchain"
- "could not find data for txid, please reindex with txindex=1"
- "output index invalid, must be 0 or 1"
- "transaction does not contain any joinsplits"
- "joinsplit index is greater than number of joinsplits"
- "message is too big"
- "message contains invalid character sequences"
- "verification of payment disclosure signature failed"
- ...


References
----------
| https://github.com/zcash/zcash/issues/2036
| https://github.com/Electric-Coin-Company/zecc-private/wiki/Engineering-meeting-notes
| https://github.com/zcash/zcash/issues/737
