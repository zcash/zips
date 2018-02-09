::

  ZIP: 143
  Title: Transaction Signature Verification for Overwinter
  Author: Jack Grigg <jack@z.cash>
          Daira Hopwood <daira@z.cash>
  Credits: Johnson Lau <jl2012@xbt.hk>
           Pieter Wuille <pieter.wuille@gmail.com>
           Bitcoin-ABC
  Category: Process
  Created: 2017-12-27
  License: MIT


Terminology
===========

The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119.


Abstract
========

This proposal defines a new transaction digest algorithm for signature verification from the Overwinter
network upgrade, in order to minimize redundant data hashing in verification, and to cover the input value by
the signature.


Motivation
==========

There are 4 ECDSA signature verification codes in the original Zcash script system: ``CHECKSIG``,
``CHECKSIGVERIFY``, ``CHECKMULTISIG``, ``CHECKMULTISIGVERIFY`` ("sigops"). According to the sighash type
(``ALL``, ``NONE``, or ``SINGLE``, possibly modified by ``ANYONECANPAY``), a transaction digest is generated
with a double SHA256 of a serialized subset of the transaction, and the signature is verified against this
digest with a given public key. The detailed procedure is described in a Bitcoin Wiki article. [#wiki-checksig]_
The transaction digest is additionally used for the JoinSplit signature (solely with sighash type ``ALL``).
[#zcash-protocol]_

Unfortunately, there are at least 2 weaknesses in the original SignatureHash transaction digest algorithm:

* For the verification of each signature, the amount of data hashing is proportional to the size of the
  transaction. Therefore, data hashing grows in O(n\ :sup:`2`) as the number of sigops in a transaction
  increases. While a 1 MB block would normally take 2 seconds to verify with an average computer in 2015, a
  1MB transaction with 5569 sigops may take 25 seconds to verify. This could be fixed by optimizing the digest
  algorithm by introducing some reusable “midstate”, so the time complexity becomes O(n). [#quadratic]_

* The algorithm does not involve the value being spent by the input. This is usually not a problem for online
  network nodes as they could request for the specified transaction to acquire the output value. For an
  offline transaction signing device ("cold wallet"), however, the lack of knowledge of input amount makes it
  impossible to calculate the exact amount being spent and the transaction fee. To cope with this problem a
  cold wallet must also acquire the full transaction being spent, which could be a big obstacle in the
  implementation of a lightweight, air-gapped wallet. By including the input value of part of the transaction
  digest, a cold wallet may safely sign a transaction by learning the value from an untrusted source. In the
  case that a wrong value is provided and signed, the signature would be invalid and no funds would be lost.
  [#offline-wallets]_

Deploying the aforementioned fixes in the original script system is not a simple task.


Specification
=============

A new transaction digest algorithm is defined::

  BLAKE2b-256 hash of the serialization of:
    1. header of the transaction (4-byte little endian)
    2. nVersionGroupId of the transaction (4-byte little endian)
    3. hashPrevouts (32-byte hash)
    4. hashSequence (32-byte hash)
    5. hashOutputs (32-byte hash)
    6. hashJoinSplits (32-byte hash)
    7. nLockTime of the transaction (4-byte little endian)
    8. nExpiryHeight of the transaction (4-byte little endian)
    9. sighash type of the signature (4-byte little endian)
   10. If we are serializing an input (ie. this is not a JoinSplit signature hash):
       a. outpoint (32-byte hash + 4-byte little endian) 
       b. scriptCode of the input (serialized as scripts inside CTxOuts) [TODO]
       c. value of the output spent by this input (8-byte little endian)
       d. nSequence of the input (4-byte little endian)

The new algorithm is based on the Bitcoin transaction digest algorithm defined in BIP 143, [#BIP0143]_ with
replay protection inspired by BUIP-HF v1.2. [#BUIP-HF]_

The new algorithm MUST be used for signatures created over the Overwinter transaction format.
[#ZIP-overwinter-tx-format]_ Combined with the new consensus rule that v1 and v2 transaction formats will be
invalid from the Overwinter upgrade, [#ZIP-overwinter-tx-format]_ this effectively means that all transactions
signatures from the Overwinter activation height will use the new algorithm. [#ZIP0000]_

The BLAKE2b-256 personalization field [#BLAKE2-personalization]_ is set to::

  "ZcashSigHash" || CONSENSUS_BRANCH_ID

``CONSENSUS_BRANCH_ID`` is the little-endian encoding of ``BRANCH_ID`` for the epoch of the block containing
the transaction. [#ZIP-activation-mechanism]_ Domain separation of the signature hash across parallel branches
provides replay protection: transactions targeted for one branch will have invalid signatures on other
branches.

Transaction creators MUST specify the epoch they want their transaction to be mined in. Across a network
upgrade, this means that if a transaction is not mined before the activation height, it will never be mined.

Semantics of the original sighash types remain unchanged, except the following:

#. The serialization format is changed;

#. All sighash types commit to the amount being spent by the signed input;

#. ``SINGLE`` does not commit to the input index. When ``ANYONECANPAY`` is not set, the semantics are
   unchanged since ``hashPrevouts`` and ``outpoint`` together implictly commit to the input index. When
   ``SINGLE`` is used with ``ANYONECANPAY``, omission of the index commitment allows permutation of the
   input-output pairs, as long as each pair is located at an equivalent index.

Field definitions
-----------------

The items 7, 9, 10a, 10d have the same meaning as the original algorithm. [#wiki-checksig]_

1: ``header``
`````````````
Deserialized into two transaction properties: ``fOverwintered`` and ``nVersion``. For transactions that use
this transaction digest algorithm, ``fOverwintered`` is always set. [#ZIP-overwinter-tx-format]_

2: ``nVersionGroupId``
``````````````````````
Provides domain separation of ``nVersion``. It is only defined if ``fOverwintered`` is set, which means that
it is always defined for transactions that use this algorithm. [#ZIP-overwinter-tx-format]_

3: ``hashPrevouts``
```````````````````
* If the ``ANYONECANPAY`` flag is not set, ``hashPrevouts`` is the BLAKE2b-256 hash of the serialization of
  all input outpoints;

* Otherwise, ``hashPrevouts`` is a ``uint256`` of ``0x0000......0000``.

4: ``hashSequence``
```````````````````
* If none of the ``ANYONECANPAY``, ``SINGLE``, ``NONE`` sighash type is set, ``hashSequence`` is the
  BLAKE2b-256 hash of the serialization of ``nSequence`` of all inputs;

* Otherwise, ``hashSequence`` is a ``uint256`` of ``0x0000......0000``.

5: ``hashOutputs``
``````````````````
* If the sighash type is neither ``SINGLE`` nor ``NONE``, ``hashOutputs`` is the BLAKE2b-256 hash of the
  serialization of all output amount (8-byte little endian) with ``scriptPubKey`` (serialized as scripts
  inside CTxOuts);

* If sighash type is ``SINGLE`` and the input index is smaller than the number of outputs, ``hashOutputs`` is
  the BLAKE2b-256 hash of the output (serialized as above) with the same index as the input;

* Otherwise, ``hashOutputs`` is a ``uint256`` of ``0x0000......0000``. [#01-change]_

6: ``hashJoinSplits``
`````````````````````
* If ``vjoinsplits`` is non-empty, ``hashJoinSplits`` is the BLAKE2b-256 hash of the serialization of all
  JoinSplits (in their canonical transaction serialization format) concatenated with the joinSplitPubKey;

  * Note that while signatures are ommitted, the JoinSplit proofs are included in the signature hash, as with
    v1 and v2 transactions.

* Otherwise, ``hashJoinSplits`` is a ``uint256`` of ``0x0000......0000``.

8: ``nExpiryHeight``
````````````````````
The block height after which the transaction becomes unilaterally invalid, and can never be mined.
[#ZIP-tx-expiry]_

10b: ``scriptCode``
``````````````````
[TODO: TBC]

* For ``P2PKH``, the ``scriptCode`` is ``0x1976a914{20-byte-pubkey-hash}88ac``.

* For ``P2SH``, the ``scriptCode`` is the ``script`` serialized as scripts inside ``CTxOut``.

10c: value
`````````
An 8-byte value of the amount of ZEC spent in this input.

Notes
-----

When generating ``hashPrevouts``, ``hashSequence``, ``hashOutputs``, and ``hashJoinSplits``, the BLAKE2b-256
personalization field is set to ``Zcash_Inner_Hash``.

The ``hashPrevouts``, ``hashSequence``, ``hashOutputs``, and ``hashJoinSplits`` calculated in an earlier
verification may be reused in other inputs of the same transaction, so that the time complexity of the whole
hashing process reduces from O(n\ :sup:`2`) to O(n).

Refer to the reference implementation, reproduced below, for the precise algorithm:

.. code:: cpp

  const unsigned char ZCASH_INNER_HASH_PERSONALIZATION[16] =
      {'Z','c','a','s','h','_','I','n','n','e','r','_','H','a','s','h'};

  uint256 hashPrevouts;
  uint256 hashSequence;
  uint256 hashOutputs;
  uint256 hashJoinSplits;

  if (!(nHashType & SIGHASH_ANYONECANPAY)) {
      CBLAKE2bWriter ss(SER_GETHASH, 0, ZCASH_INNER_HASH_PERSONALIZATION);
      for (unsigned int n = 0; n < txTo.vin.size(); n++) {
          ss << txTo.vin[n].prevout;
      }
      hashPrevouts = ss.GetHash();
  }

  if (!(nHashType & SIGHASH_ANYONECANPAY) && (nHashType & 0x1f) != SIGHASH_SINGLE && (nHashType & 0x1f) != SIGHASH_NONE) {
      CBLAKE2bWriter ss(SER_GETHASH, 0, ZCASH_INNER_HASH_PERSONALIZATION);
      for (unsigned int n = 0; n < txTo.vin.size(); n++) {
          ss << txTo.vin[n].nSequence;
      }
      hashSequence = ss.GetHash();
  }

  if ((nHashType & 0x1f) != SIGHASH_SINGLE && (nHashType & 0x1f) != SIGHASH_NONE) {
      CBLAKE2bWriter ss(SER_GETHASH, 0, ZCASH_INNER_HASH_PERSONALIZATION);
      for (unsigned int n = 0; n < txTo.vout.size(); n++) {
          ss << txTo.vout[n];
      }
      hashOutputs = ss.GetHash();
  } else if ((nHashType & 0x1f) == SIGHASH_SINGLE && nIn < txTo.vout.size()) {
      CBLAKE2bWriter ss(SER_GETHASH, 0, ZCASH_INNER_HASH_PERSONALIZATION);
      ss << txTo.vout[nIn];
      hashOutputs = ss.GetHash();
  }

  if (!txTo.vjoinsplit.empty()) {
      CBLAKE2bWriter ss(SER_GETHASH, 0, ZCASH_INNER_HASH_PERSONALIZATION);
      for (unsigned int n = 0; n < txTo.vjoinsplit.size(); n++) {
          ss << txTo.vjoinsplit[n];
      }
      ss << txTo.joinSplitPubKey;
      hashJoinSplits = ss.GetHash();
  }

  uint32_t leConsensusBranchId = htole32(consensusBranchId);
  unsigned char personalization[16] = {};
  memcpy(personalization, "ZcashSigHash", 12);
  memcpy(personalization+12, &leConsensusBranchId, 4);

  CBLAKE2bWriter ss(SER_GETHASH, 0, personalization);
  // fOverwintered and nVersion
  ss << txTo.GetHeader();
  // Version group ID
  ss << txTo.nVersionGroupId;
  // Input prevouts/nSequence (none/all, depending on flags)
  ss << hashPrevouts;
  ss << hashSequence;
  // Outputs (none/one/all, depending on flags)
  ss << hashOutputs;
  // JoinSplits
  ss << hashJoinSplits;
  // Locktime
  ss << txTo.nLockTime;
  // Expiry height
  ss << txTo.nExpiryHeight;
  // Sighash type
  ss << nHashType;

  if (nIn != NOT_AN_INPUT) {
      // The input being signed (replacing the scriptSig with scriptCode + amount)
      // The prevout may already be contained in hashPrevout, and the nSequence
      // may already be contained in hashSequence.
      ss << txTo.vin[nIn].prevout;
      ss << static_cast<const CScriptBase&>(scriptCode);
      ss << amount;
      ss << txTo.vin[nIn].nSequence;
  }

  return ss.GetHash();


Restrictions on public key type
===============================

[TODO: decide whether we want to implement this policy]

As a default policy, only compressed public keys are accepted in ``P2PKH`` and ``P2SH``. Each public key
passed to a sigop must be a compressed key: the first byte MUST be either ``0x02`` or ``0x03``, and the size
MUST be 33 bytes. Transactions that break this rule will not be relayed or mined by default.

Since this policy is preparation for a future softfork proposal, to avoid potential future funds loss, users
MUST NOT use uncompressed keys.


Example
=======

TBC


Deployment
==========

This proposal is deployed with the Overwinter network upgrade.


Backward compatibility
======================

This proposal is backwards-compatible with old UTXOs. It is **not** backwards-compatible with older software.
All transactions will be required to use this transaction digest algorithm for signatures, and so transactions
created by older software will be rejected by the network.


Reference Implementation
========================

TBC


References
==========

.. [#wiki-checksig] https://en.bitcoin.it/wiki/OP_CHECKSIG
.. [#zcash-protocol] `Zcash Protocol Specification, Section 4.6 <https://github.com/zcash/zips/blob/master/protocol/protocol.pdf>`_
.. [#quadratic]
   * `CVE-2013-2292 <https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2013-2292>`_
   * `New Bitcoin vulnerability: A transaction that takes at least 3 minutes to verify <https://bitcointalk.org/?topic=140078>`_
   * `The Megatransaction: Why Does It Take 25 Seconds? <http://rusty.ozlabs.org/?p=522>`_
.. [#offline-wallets] `SIGHASH_WITHINPUTVALUE: Super-lightweight HW wallets and offline data <https://bitcointalk.org/index.php?topic=181734.0>`_
.. [#BIP0143] `Transaction Signature Verification for Version 0 Witness Program <https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki>`_
.. [#BUIP-HF] `BUIP-HF Digest for replay protected signature verification across hard forks, version 1.2 <https://github.com/Bitcoin-ABC/bitcoin-abc/blob/master/doc/abc/replay-protected-sighash.md>`_
.. [#ZIP0000] ZIP???: Overwinter Network Upgrade
.. [#ZIP-activation-mechanism] ZIP???: Network Upgrade Activation Mechanism
.. [#ZIP-overwinter-tx-format] ZIP???: Overwinter Transaction Format
.. [#BLAKE2-personalization] `"BLAKE2: simpler, smaller, fast as MD5", Section 2.8 <https://blake2.net/blake2.pdf>`_
.. [#01-change] In the original algorithm, a ``uint256`` of ``0x0000......0001`` is committed if the input
   index for a ``SINGLE`` signature is greater than or equal to the number of outputs. In this ZIP a
   ``0x0000......0000`` is commited, without changing the semantics.
.. [#ZIP-tx-expiry] ZIP???: Transaction expiry
