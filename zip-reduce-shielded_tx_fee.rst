::

  ZIP: 313
  Title: Reduce Default Transaction Fee to 1000 zatoshis
  Owners: Aditya Bharadwaj <nighthawkwallet@protonmail.com>
  Status: Proposed
  Community Status: Request for comments : https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566
  Category: Wallet
  Created: 2020-10-11
  License: MIT


Terminology
===========

The key words "MUST" and "SHOULD" in this document are to be interpreted as
described in RFC 2119. [#RFC2119]_

The term "conventional transaction fee" in this document is in reference
to the value of a transaction fee that is conventionally used by wallets,
and that a user can reasonably expect miners on the Zcash network to accept
for including a transaction in a block.


Abstract
========

The goal of this ZIP is to gather wallet developers, miners & Zcash users
for social consensus on reducing the conventional transaction fees and
to get the Zcash conventional transaction fee reduced from 10,000 zatoshis
to 1,000 zatoshis.

In addition, this specification harmonizes transaction fees between different
kinds of transaction (involving shielded addresses, transparent addresses, or
both), as proposed in [#ecosystem-wide-tx-fee]_.


Motivation
==========

The default transaction fee presently is 0.0001 ZEC or 10,000 zatoshis.
At a ZEC market price of USD 100, for example, a user can send 10,000
transactions for 1 ZEC. This works out to 1 U.S. cent per transaction and
it rises with any increase in the price of ZEC.

With increase in light wallet adoptions on mobile clients, many users
will be new to the Zcash eco-system. And the fact that the
transaction fees are paid by the sender (not the receiver) is
new information to users who might use Zcash for e-commerce
and app interactions that might result in several transactions each day.

Privacy must not cost a premium. The cost of 10 shielded transactions
buys 1GB of mobile data `in India today <https://www.cable.co.uk/mobiles/worldwide-data-pricing/>`.

Zcash users must be able to do more with their ZEC balance
than worry about paying the premium for shielded transactions.

With reduced fees, it will be cheaper to transact on the Zcash network,
while also inviting novel use cases for privacy-preserving applications
that would benefit from the privacy, security, and programmable money
aspects of the Zcash chain.

The harmonization of fees between different kinds of transaction can be
expected to improve usability, consistency, and predictability.

Requirements for adoption
-------------------------

The change to the conventional transaction fees should be undertaken soon
as it gets difficult to gain consensus with the growth in the network
of wallets, exchanges, miners and third parties involved.

The following parties need to be part of the consensus:

* Support from mining groups is required to include the lowered default fee transactions in the next block.
* Wallet developers need to provide commitment to update the software to use the new fee.
* Zcash documentation and community outreach must be undertaken to make the change known.


Security and privacy considerations
-----------------------------------

Unique transaction fees may reveal specific users or wallets or wallet versions,
which would reduce privacy for those specific users and the rest of the network.
Hence this change should be accepted by a majority of shielded transaction
software providers before deploying the change.

Varying/unique fees are bad for privacy. For the short term before blocks get full,
it is fine for everyone to use a constant fee, as long as it is enough to compensate
miners for including the transaction. [#nathan-1]_

Long term, the issue of fees needs to be re-visited in separate future proposals as the
blocks start getting consistently full. New ZIPs with flexible fees, such as [#ian-1]_,
along with scaling solutions need to be evaluated and applied.

Denial Of Service Vulnerability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A transaction-rate-based denial of service attack occurs when an attacker generates enough transactions over a window of time to prevent legitimate transactions from being mined, or to hinder syncing blocks for full nodes or miners.

There are two primary protections to this kind of attack in Zcash: the block size limit, and
transaction fees. The block size limit ensures that full nodes and miners can keep up with
the block chain even if blocks are completely full. However, users sending legitimate
transactions may not have their transactions confirmed in a timely manner.

Variable fees could mitigate this kind of denial of service: if there are more
transactions available than can fit into a single block, then a miner will typically
choose the transactions that pay the highest fees. If legitimate wallets were to
increase their fees during this condition, the attacker would also increase the
fees of their transactions. It is sometimes argued that this would impose a cost
to the attacker that would limit the time window they can continue the attack.
However, there is little evidence that the actual costs involved would be a sufficient
disincentive.

This proposal does not alter how fees are paid from transactions to miners. However,
it does establish a fixed flat fee that wallets are expected to use. Therefore during a
transaction rate denial-of-service attack, legitimate fees from those wallets will not
rise, so an attacker can extend an attack for a longer window for the same cost.

This ZIP does not address this concern. A future ZIP should address this issue.
Wallet developers and operators should monitor the Zcash network for rapid growth
in transaction rates.


Activation
==========

Wallets implementing this specification will use a default fee of 0.00001 ZEC
(1000 zatoshis) from block 1,080,000.


Support
=======

The developers of the following wallets intend to implement the reduced fees:
* Zbay;
* Zecwallet Suite (Zecwallet Lite for Desktop/iOS/Android & Zecwallet FullNode);
* Nighthawk Wallet for Android & iOS;
* zcashd built-in wallet.


Acknowledgements
================

Thanks to Nathan Wilcox for suggesting improvements to the denial of service section.
Thanks to Daira Hopwood for reviewing and fixing the wording in this ZIP.


References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://www.rfc-editor.org/rfc/rfc2119.html>`_
.. [#nathan-1] `Conventional Shielded Fees <https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566/40>`_
.. [#ian-1] `Ian Miers. Mechanism for fee suggester/oracle <https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566/31>`_
.. [#zooko-1] `Zooko Wilcox. Tweet on reducing tx fees <https://twitter.com/zooko/status/1295032258282156034?s=20>`_
.. [#zooko-2] `Zooko Wilcox. Tweet on sharing tx fee with wallet developer <https://twitter.com/zooko/status/1295032621294956545?s=20>`_
