::

  ZIP: 313
  Title: Reduce Default Transaction Fee to 1000 zatoshis
  Owners: Aditya Bharadwaj <nighthawk24@gmail.com>
  Status: Proposed
  Community Status: Request for comments : https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566
  Category: Wallet
  Created: 2020-10-11
  License: MIT


Terminology
===========

The key words "MUST", "SHOULD", "SHOULD NOT", "MAY", "RECOMMENDED",
"OPTIONAL", and "REQUIRED" in this document are to be interpreted as
described in RFC 2119. [#RFC2119]_

"Z" refers to shielded address.
"T" refers to transparent address.

The term "default transaction fee" or "conventional transaction fee"
in this document is in reference to Z to Z transaction fee paid
to miners on the Zcash network for the work on including
the shielded transaction in a block.


Abstract
========

The goal of this ZIP is to gather wallet developers, miners & Zcash users
for social consensus on reducing the conventional transaction fees and
to get the Zcash conventional transaction fee reduced from 10,000 zatoshis
to 1,000 zatoshis.

In addition, this specification harmonizes transaction fees between different
kinds of transaction (involving shielded addresses, transparent addresses, or
both), as proposed in [#ecosystem-wide-tx-fee]_.

With reduced fees, it will be cheaper to transact on the Zcash network,
while also inviting novel use cases for privacy
preserving applications that would benefit from the Privacy,
Security and Programmable Money aspects of the Zcash chain.


Motivation
==========

The default transaction fee presently is 0.0001 ZEC or 10,000 zats.
With ZEC market price of $100, a user can send 10,000 transactions
for 1 ZEC, that turns out to 1 cent per transaction and it rises
with the increase in the price of ZEC.

With increase in light wallet adoptions on mobile clients, many users
will be new to the Zcash eco-system. And the fact that the
transaction fees are paid by the sender (not the receiver) is
new information to users who might use Zcash for e-commerce
and app interactions that might result in several transactions each day.

Privacy must not cost a premium. The cost of 10 shielded transactions
buys 1GB of mobile data `in India today <https://www.cable.co.uk/mobiles/worldwide-data-pricing/>`.

Zcash users must be able to do more with their ZEC balance
than worry about paying the premium for shielded transactions.


Requirements for consensus
-------------------------

The change to the conventional transaction fees must be undertaken sooner
as it gets difficult to gain consensus with the growth in the network
of wallets, exchanges, miners and third parties involved.

The following parties need to be part of the consensus:

* A guarantee from mining groups is required to include the lowered default fee transactions in the next block.
* Wallet developers need to provide commitment to update the software to use the new fee.
* Zcash documentation and community outreach must be undertaken to make the change known.


Security and privacy considerations
-----------

Unique transaction fees may reveal specific users or wallets or wallet versions which reduces privacy for those specific users and the rest of the network.
hence this change must be accepted by majority, if not all popular
shielded transaction software providers before announcing the change.

Varying/unique fees are bad for privacy, for the short term before blocks get full,
it’s fine for everyone to use a constant fee, as long as that is enough to compensate miners for including the transaction. [#nathan-1]_

Long term, the issue of fees needs to be re-visited in separate future proposals as the blocks start getting consistently full.
New ZIPs with flexible fees, such as [#ian-1]_, along with scaling solutions need to be evaluated and applied.

Denial Of Service Vulnerability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A transaction-rate-based denial of service attack occurs when an attacker generates enough transactions over a window of time to prevent legitimate transactions from being mined, or to hinder syncing blocks for full nodes or miners.

There are two primary protections to this kind of attack in Zcash: the block size limit, and variable transaction fees. The block size limit ensures that full nodes and miners can sync blocks even if they are completely full. However it does not protect users sending legitimate transactions to have their transactions confirmed in a timely manner.

Variable fees can mitigate this kind of denial of service because in there are more transactions available than can fit into a single block, a miner is assumed to choose the transactions that pay the highest fees. If legitimate wallets increase their fees during this condition, the attacker must also increase the fees of their transactions. This imposes a growing and ongoing cost to the attacker which limits the time window they can continue the attack.

This proposal does not alter how fees are paid from transactions to miners. However, it does require wallets to use a fixed flat fee. Therefore during a transaction rate DoS attack, legitimate fees may not rise, so an attacker can extend an attacker for a longer window for the same cost.

This ZIP does not address this concern. A future ZIP should address this issue for shielded wallets.


Activation
============

* The new default fee of 0.00001 or 1000 zats must start activation at block 1,080,000
* With a grace period of ~4 weeks (block 1,120,000) to upgrade to the reduced default transaction fee for zcashd and core clients used by exchanges & service providers.


Support
============

Zbay, Zecwallet Suite(Zecwallet Lite for Desktop/iOS/Android & Zecwallet FullNode) and Nighthawk Wallet Android & iOS have agreed to implement the reduced fees.


UX Guidance
============

Wallets must prevent users from altering the fee for shielded transactions.
Additionally, all wallet developers and operators should monitor the Zcash network for rapid growth in transaction rates. As we tend toward fuller blocks, we should proactively address the issue of growing mempool in a separate follow up ZIP.


ZIP Owners
-----------

The current ZIP Owner is Aditya Bharadwaj, representing the Nighthawk Wallet.
Additional Owners will be selected by consensus among the current Owners.
<span class="x x-first x-last">Acknowledgements</span>
~~~~~~~~~~~~~~~

Thanks to Nate Wilcox for improve the Denial of Service section.

ZIP Comments
============

Comments from the community on the ZIP should occur on the Zcash
Community Forum and the comment fields of the pull requests in
any open ZIPs. Owners will use these sources to judge rough consensus.


References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://www.rfc-editor.org/rfc/rfc2119.html>`_
.. [#nathan-1] `Conventional Shielded Fees <https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566/40>`_
.. [#ian-1] `Mechanism for fee suggester/oracle <https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566/31>`_
.. [#zooko-1] `Zooko tweet on reducing tx fees <https://twitter.com/zooko/status/1295032258282156034?s=20>`_
.. [#zooko-2] `Zooko tweet on sharing tx fee with wallet developer <https://twitter.com/zooko/status/1295032621294956545?s=20>`_
