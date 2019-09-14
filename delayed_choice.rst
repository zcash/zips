::

  ZIP: unassigned.
  Title: Delay the choice until more information can be ascertained.
  Owner: unassigned
  Author: @kek (zcash forums)
  Advocates: @kek (zcash forums) /  @mistfpga  (zcash forums) <steve@mistfpga.net>
  Category: Protocol
  Created: 2019-09-02
  License: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0) [1]
  

Originally posted and discussed `on the Zcash Community Forum <https://forum.zcashcommunity.com/t/kek-s-proposal-fund-ecc-for-2-more-years/34778>`__.


Terminology
===========

`RFC2119 <https://tools.ietf.org/html/rfc2119>`__ refrences will be in CAPS. 

**The key words include "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL"**

For clarity in this ZIP defines these terms:

-  Spirit is defined as what is the intended outcome of the zip.[2]

Out of Scope for this proposal
==============================

Everything except moving the development fund end date.

Abstract
========

The spirit of this proposal is to keep to the current structure of the ECC receiving funding from the block distribution for 2 years worth of blocks after the halving. (blocks >= 13125000)

Motivation
==========

To give more time to work out the full ramifications of any potential pivot/slow down, yet keep all in zec for 2 more years with as little disruption as possible.

Requirements
============

Nothing about distribution recipients changes.

Specification
=============

-  The ECC's percentage is capped at their projected 1.1m USD costs a month.
-  This number MUST not be greater than 10% of total block distribution of any one block.
-  This MUST end when blocks numbered >= 13125000 have been generated.
-  The last block this can apply to is 13124999
 
Raised objections and issues so far
===================================

-  This is just kicking the can down the road.
-  The zfnd has raised objections to a single point of failure in the ECC.

Implications to other users
===========================

-  The knock on impact of this zip to exchanges and wallet developers maybe non trivial.
-  The economics of doing this have not been calculated.

References
==========

[1] - https://creativecommons.org/licenses/by-sa/4.0/

[2] - If there is contradiction between Spirit and any other part of the proposal that needs to be addressed. in the even it is not addressed Spirit is assumed to overrule all.
