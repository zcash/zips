::

  ZIP: unassigned
  Title: Genuine Protocol opt-in/out donation feature
  Owner: unassigned
  Advocate: mistfpga (zcash forums) <steve@mistfpga.net>
  Category: Protocol
  Created: 2019-07-17
  License: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0) [1]

Originally posted and discussed `on the Zcash Community Forum <https://forum.zcashcommunity.com/t/zip-proposal-a-genuine-opt-in-protocol-level-development-donation-option/33846>`__.


`RFC2119 <https://tools.ietf.org/html/rfc2119>`__. references will be in CAPS.

**The key words include "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL"**

For clarity in this ZIP defines these terms:

-  Signalling is defined as expressing a voice through whatever mechanism is implemented or sought for that decision. In the context of this zip it is primarily referred to in regards signalling what to do with funds. This could be done by miners, straw poll, coinbase, proof of value, some internet poll thing, etc.
-  Mining software in the context of this zip refers to pool software, local mining software, or staking software.
-  Custodial services include any service which a 3rd party controls the private keys of a 3d party, mining pools and online wallets are examples. 
-  Mining is defined as the action of processing transactions, so this include proof of stake, if zcash would switch to that.
-  User is defined that anyone that uses ZEC or the zcash technology.
-  Mining coins transferred via fees are considered rewards (infinite), coins generated via block generation are considered distribution (finite).
-  Opt-in v opt-out - Opting out is a purely selfish act in the context of this ZIP. They do not burn the coins therefore giving everyone value. They keep them.
-  Burning coins is purposefully taking them out of circulation forever at the protocol block distribution level.
-  Initial promise is defined as complete honour of distributing all rewards to the miner. - This is a non neutral phrase. I accept that.
-  Transaction sender is defined as anyone who sends a transaction across the zcash network, be it t-t, z-z, t-z, z-t.
-  Fee is the standard transaction fee that a sender puts on a transaction to get it included into a block and the miner is in control of
-  Transaction donation is an optional signalling string that create a transaction to the coins base donations.
-  Block Reward is defined as block distribution + mining fees.
-  Spirit is defined as what is the intended outcome of the zip.[2] 
-  Rolling burn is defined in its own zip.[3]

Out of Scope for this proposal
==============================

Governance on how decisions are made, this ZIP is not meant to be used as a form of governance. it is protocol level opt-in/out for supporting the zcash network development. (like the FR, just with opt-out)
 
Signalling. Whilst a lot of the zip relies on the ability to signal intent in one way or another, it does not put forward such a mechanism and is designed to work with various form of signalling. Or potentially without signalling at all.

Abstract
========

The spirit of this zip is:
-  To allow continual funding of the ECC, the foundation, or some combination of these should a user choose to do so.
-  To add a genuine opt-in feature, which is done at the users choice.

Motivation
==========

Technology changes, and it changes fast. What works now, may be easily breakable in 10 years, 20 years and certainly 50 years.

To help ensure ZEC can keep up with these changes, now and in 50 or 500 years time, there needs to be a continual funding for research into new technology and the ability for financial stability so the company can attract new talent.

The only source of indefinite wealth transfer is transaction fees or donations. This zip is specifically about voluntary donations. (including via mining fees)

Requirements
============

-  An additional opt-in mechanism, baked into the protocol. This is a condition of the foundation too [4]
-  Give an alterative to redistribution of either; the current block distribution structure, or emission curve.
-  The foundation MUST use this funding to fund zec development for the lifetime of their receipt of it.
-  To give a strong indication to the community and users that they have freedom to decide what they do with their coins and donations
-  Baking the addresses into the codebase you do not need the wallet software or pool software to keep track of donation addresses.
-  It prevents users from sending donations to old addresses.
-  It makes it easier for pools to add support and prove that they are actually donating the % they say they are.
-  Users MUST NOT be forced to signal.

Specification
=============

-  This zip MUST enforce the initial promise as defined by default.
-  The official client MUST default to be counted as initial promise
-  No signal MUST be counted as whatever the pool is signalling for, when using a pool.
-  Security MUST NOT be lessened
-  This zip MAY be set to opt-in via a user set flag
-  This zip MUST contain donation addresses in the coinbase, in a similar fashion to the current FR.
-  When sending transactions the sender MAY signal their donation.
-  A signal from a transaction sender MUST NOT override the default transaction processor signal for that transaction.
-  A transaction sender MAY elect to include separate donation fees which MUST NOT be overridden by the transaction processor if this used or not.

Raised objections and issues so far
=======================================

-  This adds complexity to the protocol, which is technically not needed and generally a bad idea.
-  This does not add anything that cannot already be done under the current protocol by users manually, although not to the same extent.
-  Block sizes, this may impact the motivation to increase block sizes should that need arise.
-  Signalling from shielded addresses to donations at taddresses?
-  Once zcash goes full z address, how will transparency of donations be proven?
-  ZEC is designed to not have high transaction fees or a secondary transaction fee market. *Is this a core principle?*
-  A similar goal can be achieved without initial promise and just burn - mistfpga: I dislike taking coins out of circulation intentionally - it is an attempt to avoid that.
-  Further note: If burn must be an option I would like to use something like the rolling burn option. [3]

Implications to other users
===========================

-  Wallet development will need to be considered.  Hopefully the requirements will lessen this impact after the first initial change.

-  What happens if the Foundation closes down, will the donations: 
  - go to into the mining fee
  - get burnt
  - get sent as change to the original sender
  - distributed via some other mechanism


Technical implementation
========================

Stuff that is already implemented in some form or another:

-  Optional fees are already implemented in some wallet software.
-  Optional Fees already cannot be overridden by miners.
-  Hardcoded donation addresses are already baked into the protocol so it should be minor work to adjust them to the signalling addresses.
-  Hardcoded donation address already cannot be changed by pools or software.
-  Signalling could be handled at the pool level
-  Pools already add their own addresses to the coinbase, including donations.

References
==========

[1] https://creativecommons.org/licenses/by-sa/4.0/
[2] If there is contradiction between Spirit and any other part of the proposal that needs to be addressed. in the even it is not addressed Spirit is assumed to overrule all.
[3] Link to rolling burn proposal.
[4] The foundation has stated that 
  The Foundation would only support proposals that:
   a) don’t rely on the Foundation being a single gatekeeper of funds
   b) don’t change the upper bound of ZEC supply
   and c) have some kind of **opt in** mechanism for choosing to disburse funds (from miners and/or users)
