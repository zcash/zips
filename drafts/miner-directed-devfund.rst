::

  ZIP: unassigned.
  Title: Miner Directed Dev Fund
  Owner: unassigned
  Author: Andrew Miller (@amiller on zcash forums)
  Advocates: Andrew Miller
  Category: Protocol
  Created: 2019-06-19
  ZIP Status: Draft
  License: public domain
  
Originally posted and discussed `on the Zcash Community Forum <https://forum.zcashcommunity.com/t/dev-fund-proposal-miner-directed-dev-fund-was-20-to-any-combination-of-ecc-zfnd-parity-or-burn/33864>`__.


Terminology
===========

`RFC2119 <https://tools.ietf.org/html/rfc2119>`__ refrences will be in CAPS. 

**The key words include "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL"**

For clarity, this ZIP defines these terms:

- 2nd Halvening Period - the 4-year period of time, roughly from October 2020 - October 2024, during which at most 5,250,000 ZEC will be minted
- DF% - Dev Fund Percentage, the portion of newly minted ZEC in each block reserved for a dev fund
- MR% - Miner Reward Percentage, the portion of newly minted ZEC in each block given to miners (so that DF% + MR% = 100%).

Out of Scope for this proposal
===============================
This proposal does not (currently) specify any process for reaching agreement on or modifying the fixed set of development entities.
This proposal does not specify how miners should reach a decision on how to direct the dev fund, or how developers should appeal to miners to do so. 
Other dev fund proposals include specific processes for accountability and to support community decision making, such as monthly developer calls, lists of planned features and goals, etc. Any of these can be compatible with this proposal as well, by providing non-binding advice to miners, by reaching agreement on implementation defaults, by guiding the choice of the fixed set of developers, etc.
This proposal only provides a guideline for the 2nd halvening period.

Abstract
========
This proposal reserves a portion (20%) of the newly minted coins in each block for the dev fund. A fixed set of developer entities would be eligible to receive these funds. The fund would be miner directed in the sense that the miner of each block can determine how to allocate these funds to eligible developers.

Motivation
==========
Like most dev fund proposals, this is motivated by the potential value to the Zcash community of using newly minted coins to hire developers to continue improving Zcash.[2]

Unlike most other dev fund proposals, this proposal is distinct in providing a fine-grained “opt-in” [1] feature, since miners have the choice to provide a small amount of dev funding or none at all.

Requirements
================
- Simplicity: A design goal of this proposal is to be simple to define and implement, without specifying much process for on-chain or off-chain governance
- Opt-in: the proposed dev fund is not mandatory, since miners can decide not to allocate any funds at all to the developer entities
- Incentive compatible: miners cannot directly pay the dev fund to themselves
   
Specification
===============
During the 2nd halvening period, a fixed portion (DF%=20%) of the newly minted coins in each block are reserved for a Miner Directed Dev Fund (MDDF). A hardcoded set of developer entities (e.g., ECC, Zfnd, Parity, or others), represented in the code their t-address or z-address public keys, are eligible to receive funding from the MDDF. The fund is “miner directed” in the sense that the miner in each block chooses how to allocate the MDDF coins among the developer entities, simply by creating outputs in the coinbase transaction. The DF% is a maximum - miners can also “opt out” by minting a lower number of coins for the MDDF, or none at all.

This proposal is explicitly limited in scope to the 2nd halvening period. After the 2nd halvening, the entire block reward in each block is awarded to the miner
The upper bound on the rate of newly minted coins MUST remain the same as before this proposal (i.e., at most 25 ZEC minted per 10 minutes during the 2nd halvening period)
implementations MAY define a default opt-in allocation (e.g., DF%/2 to ECC and DF%/2 to Zfnd)
implementations SHOULD support changing the allocation (overriding any such default) through a configuration option

Examples
--------
The following examples illustrate how miners can build the outputs of the coinbase transactions to allocate the MDDF to eligible developers. Assume $Dev1, $Dev2 are the hardcoded t-addresses of eligible developers, and $Miner is the address of the mining pool mining this block. Assume the total newly minted coins are 6.25 ZEC per block during the 2nd halvening period, and that DF%=20%, MR%=80%.

**Example 1: Split equally between two developers**

The transaction outputs of the coinbase transaction are as follows:

- 5.0 ZEC to $Miner
- 0.625 ZEC to $Dev1
- 0.625 ZEC to $Dev2

**Example 2: Opt-out of the dev fund**

The transaction outputs of the coinbase transaction are as follows:

- 5.0 ZEC to $Miner
  
Issues & Further Discussion
===========================
Raised objections and issues so far:

- Miners may have adverse incentives, such as:
Stonewalling any development of Proof-of-Work alternatives, such as GPU-friendly variants or proof-of-stake.
Extortion for more funds. To illustrate: "We’ll direct all 20% of the dev fund to DeveloperX, but only if they promise to keep just 5% and pass 15% back to the mining pool.”

- Blocking the dev fund out of greed.
This proposal modifies the terms of what some may consider a social contract: Given the original code in Zcash implementations prior to NU5, by the end of the issuance schedule when all 21M ZEC have been minted, a total of 90% of all minted coins would have originally been awarded to miners. Under this proposal, less reward would be available to miners, than would be according to the original minting schedule as implemented in Zcashd prior to NU5.

- Several others, notably the Blocktown Capital proposal, have suggested that a 20% dev fund would set a precedent for a perpetual 20% dev fund [3]. This proposal is explicitly limited in scope to the 2nd halvening period. Thus adopting this proposal on its own, if there are no further updates, would result in the the dev fund ending in 2024.

References
==========
- [1] The future of Zcash in the year 2020 2 acityinohio
- [2] Notes on reaching agreement about a potential Zcash dev fund - amiller
- [3] Executive Summary: Blocktown Proposal for Zcash 2020 Network Upgrade

**Changelog:**

- 2019-06-19 initial post
- 2019-08-28 update to be more like a zip draft
   renamed to Miner Directed Dev Fund (MDDF)
   removed references to “Burn”, instead opt-out is in terms of coins never being minted in the first place
- 2019-08-29 address informal preZIP feedback
   add example, requirements, fix incomplete sentence about default allocations
- 2019-09-15 move to github
