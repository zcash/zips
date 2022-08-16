::

  ZIP: 317
  Title: Proportional Output Fee Mechanism (POFM)
  Owners: Aditya Bharadwaj <nighthawk24@gmail.com>
  Credits: Madars Virza, Kris Nuttycombe
  Status: Draft
  Community Status: Request for comments : https://forum.zcashcommunity.com/t/zip-proportional-output-fee-mechanism-pofm/42808
  Category: Wallet
  Created: 2022-08-15
  License: MIT


Terminology
===========

The key words "MUST", "SHOULD", "SHOULD NOT", "MAY", "RECOMMENDED",
"OPTIONAL", and "REQUIRED" in this document are to be interpreted as
described in RFC 2119. [#RFC2119]_

"Z" refers to shielded address.
"T" refers to transparent address.

"POFM" refers to the proposed change in conventional fee as described in 
this ZIP.

The term "default transaction fee" in this document is in reference
to Z to Z, T to Z & Z to T transaction fee paid to miners on the Zcash network
for the work on including the shielded transaction in a block.


Abstract
========

The goal of this ZIP is to change the conventional transaction fees for
Shielded transactions and get buy-in from wallet developers, miners & Zcash users.

With an updated transaction fee formula, miners will be compensated fairly for
including transactions with a high number of outputs, while still allowing low fees 
for regular shielded transaction use cases.


Out of Scope for this Proposal
============

Discussion around transaction fees for T to T.


Motivation
============

In light of recent network activity, it is time to review and update the 
standard 1,000 zats transaction fees set in ZIP-313.


The conventional transaction fee presently is 0.00001 ZEC or 1,000 zats per
ZIP-313, that allowed exploration of novel use cases of the Zcash blockchain.
The Zcash network has operated for almost 2 years of 1,000 zats fee per shielded 
transaction without consideration for the total number of inputs and outputs in the transaction.
This has resulted in high output transactions with 1,100 outputs costing the same as 
transactions with 2 outputs.


Requirements for gathering consensus
-------------------------

Wallet developers must update the fees to the proposed formula by Madars and 
Kris Nuttycombe [#madars-1]_

min_fee = base_fee * max(0, #inputs + #outputs - 4)

Where #inputs and #outputs also take into account transparent inputs and outputs. 
Otherwise, the fee structure (if not otherwise changed) will preferentially encourage 
usage of the transparent part of the chain.

The change to the conventional transaction fees must be undertaken soon
as the Zcash network has been under heavy load with high-output transactions while 
regular shielded transactions with 2 outputs are affected when relying on current 
light wallet infrastructure.

The following parties need to be part of the consensus:

* The technical aspects of a changing conventional fee based on outputs 
need to be evaluated.
* A guarantee from mining groups is required to include the updated POFM 
transactions in the next block.
* Wallet developers need to update the software to use the new fee.
* Zcash documentation and community outreach must be undertaken to
make the change known.


Requirements for adoption
-------------------------

The change to the conventional transaction fees should be undertaken soon
as it gets difficult to gain consensus with the growth in the network
of wallets, exchanges, miners, and third parties involved.

The following parties need to be part of the consensus:

* Support from mining groups is required to include the updated conventional
  fee transactions in the next block.
* Wallet developers need to provide a commitment to update the software to use
  the new fee.
* Zcash documentation and community outreach must be undertaken to make the
  change known.


Security and privacy considerations
-----------------------------------

Unique transaction fees may reveal specific users or wallets or wallet versions,
which would reduce privacy for those specific users and the rest of the network.
Hence this change should be accepted by a majority of shielded transaction
software providers before deploying the change.

Long term, the issue of fees needs to be re-visited in separate future
proposals as the blocks start getting consistently full. New ZIPs with 
scaling solutions, will need to be evaluated and applied.


Denial of Service Vulnerability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A transaction-rate-based denial of service attack occurs when an attacker
generates enough transactions over a window of time to prevent legitimate
transactions from being mined, or to hinder syncing blocks for full nodes
or miners.

There are two primary protections to this kind of attack in Zcash: the
block size limit, and transaction fees. The block size limit ensures that
full nodes and miners can keep up with the blockchain even if blocks are
completely full. However, users sending legitimate transactions may not
have their transactions confirmed in a timely manner.

Variable fees could mitigate this kind of denial of service: if there are
more transactions available than can fit into a single block, then a miner
will typically choose the transactions that pay the highest fees. If
legitimate wallets were to increase their fees during this condition, the
attacker would also increase the fees of their transactions. It is
sometimes argued that this would impose a cost to the attacker that would
limit the time window for which they can continue the attack. However, there
is little evidence that the actual costs involved would be a sufficient
disincentive.

This proposal does not alter how fees are paid from transactions to miners.

Wallet developers and operators should monitor the Zcash network for rapid
growth in transaction rates.


Specification
=============

Wallets implementing this specification will use a conventional fee in the form of 
min_fee = base_fee * max(0, #inputs + #outputs - 4) 
starting from block 1,800,000.


Transaction relaying
--------------------

zcashd, and potentially other node implementations, implement fee-based
restrictions on relaying of mempool transactions. Nodes that normally relay
transactions are expected to do so for transactions that pay at least the
conventional fee, unless there are other reasons not to do so for robustness
or denial-of-service mitigation.


Mempool size limiting
---------------------

zcashd limits the size of the mempool as described in [#zip-0401]_. This
specifies a *low\_fee\_penalty* that is added to the "eviction weight" if the
transaction pays a fee less than the proposed increase with POFM.


Support
=======

The developers of the following wallets intend to implement the updated fee mechanism:

* Zecwallet Suite (Zecwallet Lite for Desktop/iOS/Android & Zecwallet FullNode);
* Nighthawk Wallet for Android & iOS;
* ECC Mobile SDKs for iOS & Android
* zcashd built-in wallet 


Acknowledgements
================

Thanks to Madars Virza for suggesting the fee mechanism. And Kris Nuttycombe to 
suggest optimization.

.. [#madars-1] `Madars concrete soft-fork proposal <https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566/89?u=aiyadt>`_
