::

  ZIP: XXX
  Title: Reduce default Shielded Transaction fee to 1000 zats
  Owners: Aditya Bharadwaj <nighthawk24@gmail.com>
  Original-Author: Aditya Bharadwaj
  Status: Draft
  Community Status: Request for comments : https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566
  Category: Consensus
  Created: 2020-10-11
  License: MIT


Terminology
===========

The key words "MUST", "SHOULD", "SHOULD NOT", "MAY", "RECOMMENDED",
"OPTIONAL", and "REQUIRED" in this document are to be interpreted as
described in RFC 2119. [#RFC2119]_

"Z" refers to shielded address.
"T" refers to transparent address.

The term "default transaction fee" in this document is in reference
to Z to Z transaction fee paid to miners on the Zcash network
for the work on including the shielded transaction in a block.


Abstract
========

The goal of this ZIP is to discuss ideas around fee reduction,
collect feedback from wallet developers, miners & Zcash users
for consensus on reducing the default transaction fees and
get the Zcash default transaction fee reduced from 10,000 zats
to 1000 zats.

With reduced fees, it will be cheaper to transact on the Zcash network,
while also inviting novel use cases for privacy
preserving applications that would benefit from the Privacy,
Security and Programmable Money aspects of the Zcash chain.


Out of Scope for this Proposal
============

Discussion around transaction fees for T to T, T to Z or Z to T.


Motivation
============

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

The change to the default transaction fees must be undertaken sooner
as it gets difficult to gain consensus with the growth in the network
of wallets, exchanges, miners and other parties involved.

The following parties need to be part of the consensus:

* The technical aspects of a lower default fee need to be evaluated.
* A guarantee from mining groups is required to include the lowered
default fee transactions in the next block.
* Wallet developers need to update the software to use the new fee.
* Zcash documentation and community outreach must be undertaken to
make the change known.


Security and privacy considerations
-----------

Unique transaction fees can cause linkability within transactions,
hence this change must be accepted by majority, if not all popular
shielded transaction software providers before announcing the change


ZIP Editors
-----------

The current ZIP Editor is Aditya Bharadwaj, representing the Nighthawk Wallet.
Additional Editors will be selected by consensus among the current Editors.


ZIP Comments
============

Comments from the community on the ZIP should occur on the Zcash
Community Forum and the comment fields of the pull requests in
any open ZIPs. Editors will use these sources to judge rough consensus.


References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://www.rfc-editor.org/rfc/rfc2119.html>`_
.. [#zooko-1] `Zooko tweet on reducing tx fees <https://twitter.com/zooko/status/1295032258282156034?s=20>`_
.. [#zooko-2] `Zooko tweet on sharing tx fee with wallet developer <https://twitter.com/zooko/status/1295032621294956545?s=20>`_
