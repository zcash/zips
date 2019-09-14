::

  ZIP: unassigned
  Title: ZIP proposal Keep the block distribution as initially defined. 90% to miners
  Owner: unassigned
  Advocate: mistfpga (zcash forums) <steve@mistfpga.net>
  Category: Protocol
  Created: 2019-08-01
  License: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0) [1]

Originally posted and discussed `on the Zcash Community Forum <https://forum.zcashcommunity.com/t/zip-proposal-keep-the-block-distribution-as-initaly-defined-90-to-miners/33843>`__.


`RFC2119 <https://tools.ietf.org/html/rfc2119>`__. references will be in CAPS.

**The key words include "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL"**

For clarity in this ZIP defines these terms:

-  Mining software in the context of this zip refers to pool software, local mining software, or staking software.
-  Mining is defined as the action of processing transactions, so this include proof of stake, if zcash would switch to that.
-  Mining coins transferred via fees are considered rewards (infinite), coins generated via block generation are considered distribution (finite).
-  Block distribution is defined as the block reward - transaction fees.
-  Spirit is defined as what is the intended outcome of the zip.[2]
-  Initial promise is non neutral language referencing the block distribution rules as initially set out.[3]

Abstract
========

The spirit of this zip is to is to ensure that the FR ends.  It is not the intention of this zip to stop protocol based donations.

It is a simplistic short zip.

Hopefully it will be compatible with a number of other zips and can be worked into them.

Out of Scope for this proposal
==============================

-  Governance on how decisions are made, this ZIP is not meant to be used as a form of governance. 
-  Future funding
-  It does not cover other donations or revenue streams. 

Motivation
==========

-  The Founders Reward is set to expire in 2020.
-  To honour the initial promise of giving 90% of total block distribution to miners. Therefore the protocol giving them 100% of the block distribution after the first halving.

Requirements
============

-  The FR MUST end at the fist halving.
-  This zip SHOULD NOT preclude the ECC from sourcing funding elsewhere, or from donations.

Specification
=============

-  The existing Founders’ Reward consensus rules [4],[5] MUST be preserved.
-  Specifically, `FoundersReward(height) MUST equal 0 if Halving(height) >= 1` (For clarity once the halving happens the FR stops. as per the rules outlined in [4],[5])
-  This line of code is only meant to stop the FR not protocol based donations.
-  Enforcing some kind of mandatory donation via whatever mechanism would be seen as continuation of the FR.

Implications to other users 
===========================

-  Block distribution payouts to FR addresses will need to be removed from the codebase. (I think this already happens though)
-  Pools and other software may need to make adjustments for this.
 
Technical implementation
========================

-  ?

References
==========

[1] https://creativecommons.org/licenses/by-sa/4.0/
[2] If there is contradiction between Spirit and any other part of the proposal that needs to be addressed. in the even it is not addressed Spirit is assumed to overrule all.
[3] Cant find the document! the one with the graph in it. will update.
[4] Section 7.7: Calculation of Block Subsidy and Founders Reward. Zcash Protocol Specification, Version 2019.0.0 [Overwinter+Sapling] 
[5] Section 7.8: Payment of Founders’ Reward. Zcash Protocol Specification, Version 2019.0.0 [Overwinter+Sapling]

