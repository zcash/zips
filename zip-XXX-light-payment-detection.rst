::

  ZIP: XXX
  Title: Light Client Protocol for Payment Detection
  Authors: George Tankersley <gtank@z.cash>
           Jack Grigg <jack@z.cash>
  Credits: Matthew Green <mgreen@z.cash>
  Category: Standards Track
  Created: 2018-09-17
  License: MIT


Terminology
===========

The terms below are to be interpreted as follows:

Light client
  A client that is not a full participant in the network of Zcash peers. It can send and
  receive payments, but does not store or validate a copy of the blockchain.

Abstract
========

This proposal defines a protocol for a Zcash light client supporting Sapling shielded
transactions.

Motivation
==========

Currently a client that wishes to send or receive shielded payments must be a full node
participanting in the Zcash network. This requires an amount of available bandwidth,
space, and processing power that may be unsuitable for some classes of user. This light
client protocol addresses that need, and is appropriate for low-power,
bandwidth-conscious, or otherwise limited machines (such as mobile phones).

High-Level Design
=================

There are three logical components to a Zcash light client system:

- **Zcash node** that provides chain state and serves as a root of trust for the system.

- **Proxy server** that extracts blockchain data from zcashd to store and serve it in a
  lower-bandwidth format.

- **Light client** that subscribes to the stream from a proxy server and uses that data to
  update its own view of the chain state. The light client MAY be attached to a wallet
  backend that will track particular Sapling notes.

.. figure:: arch.png
    :align: center
    :figclass: align-center

    Outline of the light wallet architecture

Security Model
==============

In this model, we propose **payment detection privacy** as our main security goal. That
is, the proxy should not learn which transactions (received from the blockchain) are
addressed to a given light wallet. If we further assume network privacy (via Tor or
similar), the proxy should not be able to link different connections or queries as
deriving from the the same wallet.

In particular, the underlying Zcash node / proxy combination is assumed to be "honest but
curious" and is trusted to provide a correct view of the current best chain state and to
faithfully transmit queries and responses. Methods for weakening this assumption are
discussed in appendix FOO.

This ZIP does not address how to spend notes privately.

Compact Stream Format
=====================

A key observation in this protocol is that the current zcashd encrypted field is several
hundred bytes long, due to the inclusion of a transaction “memo”. The need to download
this entire field imposes a substantial bandwidth cost on each light wallets, which may be
a limited mobile device on a restricted-bandwidth plan. While more efficient techniques
can be developed in the future, for the moment we propose ignoring the memo field during
payment detection. Futhermore, we can also ignore any information that is not directly
relevant to a Sapling shielded transaction.

A **compact block** is a packaging of ONLY the data from a block needed to:

1. Detect a payment to your shielded Sapling address
2. Detect a spend of your shielded Sapling notes
3. Update your witnesses to generate new Sapling spend proofs.

A compact block and its component compact transactions are encoded on the wire using the
following Protocol Buffers [XXX] format:

.. code:: proto

    message BlockID {
         uint64 blockHeight = 1;
         bytes blockHash = 2;
    }

    message CompactBlock {
        BlockID id = 1;
        repeated CompactTx vtx = 3;
    }

    message CompactTx {
        uint64 txIndex = 1;
        bytes txHash = 2;

        repeated CompactSpend spends = 3;
        repeated CompactOutput outputs = 4;
    }

    message CompactSpend {
        bytes nf = 1;
    }

    message CompactOutput {
        bytes cmu = 1;
        bytes epk = 2;
        bytes ciphertext = 3;
    }

Encoding Details
----------------

``blockHash``, ``txHash``, ``nf``, ``cmu``, and ``epk`` are encoded as
specified in the Zcash Protocol Spec.

The output and spend descriptions are handled differently, as described in the following
sections.

Output Compression
------------------

In the normal Zcash protocol, the output ciphertext consists of the AEAD encrypted form of
a *note plaintext* (see Zcash Spec section 5.5):

+------------+----------+----------+-------------+-----------------------------------+
| 8-bit 0x01 | 88-bit d | 64-bit v | 256-bit rcm | memo (512 bytes) + tag (16 bytes) |
+------------+----------+----------+-------------+-----------------------------------+

A recipient detects their transactions by trial-decrypting this ciphertext. On a full node
that has the entire block chain, the primary cost is computational. For light clients
however, there is an additional bandwidth cost: every ciphertext on the block chain must
be received from the server (or network node) the light client is connected to. This
results in a total of 580 bytes per output that must be streamed to the client.

However, we don't need all of that just to detect payments. The first 52 bytes of the
ciphertext contain the contents and opening of the note commitment, which is all of the
data needed to spend the note and to verify that the note is spendable. If we ignore the
memo and the authentication tag, we're left with a 32-byte ephemeral key, the 32-byte note
commitment, and only the first 52 bytes of the ciphertext for each output needed to
decrypt, verify, and spend a note. This totals to 116 bytes per output, for an 80%
reduction in bandwidth use.

However, skipping the full ciphertext means that we can no longer calculate the
authentication tag for the entire ciphertext and will need to do something else to
validate the integrity of the decrypted note plaintext.

Since the note commitment is sent outside the ciphertext and is authenticated by the
binding signature over the entire transaction, it serves as an adequate check on the
validity of the decrypted plaintext (assuming you trust the entity assembling
transactions). We therefore recalculate the note commitment from the decrypted plaintext.
If the recalculated commitment matches the one in the output, we accept note as valid and
spendable.

Spend Compression
-----------------

Recall that a full Sapling Spend description is 384 bytes long:

+-------+--------------+-----------+
| Bytes | Name         | Type      |
+=======+==============+===========+
| 32    | cv           | char[32]  |
+-------+--------------+-----------+
| 32    | anchor       | char[32]  |
+-------+--------------+-----------+
| 32    | nullifier    | char[32]  |
+-------+--------------+-----------+
| 32    | rk           | char[32]  |
+-------+--------------+-----------+
| 192   | zkproof      | char[192] |
+-------+--------------+-----------+
| 64    | spendAuthSig | char[64]  |
+-------+--------------+-----------+

The only part necessary for detection is the nullifier, which allows a light client to
detect when one of its own notes has been spent. This means we only need to take 32 bytes
of each Spend, for a 90% improvement in bandwidth use.

Proxy operation
===============

The proxy's purpose is to provide a scalable and bandwidth-efficient interface between a
Zcash node and any number of light clients. It accomplishes this by parsing a blockwise
stream of transactions from the node and converting them into the compact format described
above.

The proxy stores



Client operation
================

Appendix FOO
============

You can require the proxy to give you all the block headers to validate.

Reference Implementation
========================

This proposal is supported by a set of libraries and reference code made available by the
Zcash Company.

[NOTE: 2018-09-17 WE HAVE NOT YET FINISHED OR RELEASED THESE.]

References
==========

[bipXXX] define a light client

[XXX] protobufs
