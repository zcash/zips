::

  ZIP: XXX
  Title: 20% Split Evenly Between the ECC and the Zcash Foundation, and a Voting System Mandate
  Owner: aristarchus (Zcash Community Forum handle)
  Status: Draft
  Category: Process
  Created: 2019-06-19
  License: MIT

Originally posted and discussed `on the Zcash Community Forum <https://forum.zcashcommunity.com/t/dev-fund-proposal-20-split-between-the-ecc-and-the-foundation/33862>`__.

Terminology
========

To understand this ZIP it is critical that people understand the right terminology so their requirements can be quickly checked.

**The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and "OPTIONAL"**

Have special meaning and people should familiarise themselves with it. - https://tools.ietf.org/html/rfc2119

For clarity in this zip I define these terms:

* 2nd Halvening period - the 4-year period of time, roughly from October 2020 - October 2024, during which at most 5,250,000 ZEC will be minted
* DF% - Dev Fund Percentage, the portion of newly minted ZEC in each block reserved for a dev fund

Abstract
========

This proposal would allocate a 20% Dev Fund Percentage to be split evenly between the ECC and the Zcash Foundation during the 2nd Halvening period. This proposal aims to be simple to implement, without a single point of failure, and comes with mandates for transparency, accountability and a mandate to build a dev fund voting mechanism to be used during the 3rd Halvening period. This proposal is designed to strike a balance between ensuring that high quality development work can continue uninterrupted, with the need to further decentralize Zcash development funding as soon as possible.

Motivation
========

Strengths of this proposal:

1. Simple to implement. I would rather developers spend time scaling Zcash rather than implementing the dev funding mechanism.
2. Developers will have several years to work on a great decentralized development funding voting mechanism.
3. 20% is a large enough percentage that there should be enough dev funding for many different Zec price scenarios. To those who want to decrease this percentage: Overpaying for security is a gift to miners, to the detriment of every other stakeholder in the Zcash community. I will even make the strong statement that intentionally overpaying the miners for security is stealing from the other stakeholders.
4. With two entities receiving funds there is no single point of failure.

Requirements
========

1. DF% must be 20 percent, split evenly between company and foundation for years 5-8.
2. Dev Fund must only to be spent on research, development and adoption of zcash
3. A voting system for dev funding must be built and implemented after year 8.

Specification
========

Voting System Requirements
-----------------

Here are the general properties of the mandated voting mechanism. I don’t want to specify the technical implementation details, since I believe this is a job suited for the engineers building this system.

1. Voting should be private.
2. Only Zec holders can vote.
3. Voting should happen on-chain.
4. In order to vote, you must lock your zec so it cannot be spent for a period of time. This is to force the voters to have ‘skin in the game’ and prevent someone nefarious from buying a lot of zec just before an election and then dumping it immediately after.
5. Voters can choose how long to lock their zec, and their voting power is proportional to the time that the zec is locked. For example, someone who votes with 10 zec and locks it for 6 months would have the same voting power as someone who votes with 20 zec and locks it for 3 months. Of course there must be a maximum lock time, perhaps a year, to prevent anyone from getting ‘infinite’ voting power by locking their zec permanently.
6. The final results of the vote should be transparent to and verifiable by everyone.
7. The system should be totally open and allow anyone/any organization to compete for funding to develop zcash.

Transparency and Accountability for the ECC and the Zcash Foundation
-----------------

These requirements would apply to both the company and the foundation. The mandate is to adhere to these accountability requirements originally put forward by the foundation:

* Monthly public developer calls, detailing current technical roadmap and updates
* Quarterly tech roadmap reports and updates
* Quarterly financial reports, detailing spending levels/burn rate and cash/ZEC on hand
* A yearly, audited financial report akin to the Form 990 for US-based nonprofits
* Yearly reviews of organization performance, along the lines of our State of the Zcash Foundation report [1]

Requirements Specifically for the ECC
-----------------

Motivated by the Foundation’s proposal that the ECC become a non-profit ( https://www.zfnd.org/blog/dev-fund-guidance-and-timeline/), I am going to list general requirements for the ECC to abide by if they choose to receive funds and work on behalf of zec holders.

1. Because I share the foundation’s concern that the ECC could be “beholden to its shareholders”, I am mandating that the ECC should be working in the service of the Zcash community and **shall serve no other masters**. The original investors/founders who are not still working in the service of the Zcash community should not have control over the use of the new dev funds.
2. The revenue received from the Dev Fund should not be used to give further rewards to, even indirectly, the investors, founders, or shareholders of the ECC, who are not working on Zcash after the first halving. **They have already received the founders reward and this new dev fund is not supposed to further benefit them.**
3. The ECC should offer competitive pay and **a stake in upside of the success of Zcash as a way to attract the best and brightest**. I do want the ECC be able to **maintain a world class team** capable of competing with the tech giants of the world (Google, Apple etc.).
4. The ECC should **continue to engage with regulators** and advocate for privacy preserving technology. The **legal structure of the ECC must not hamper these critical efforts** in any way.

I am not mandating non-profit status for the ECC. Maybe that is the best legal structure, maybe something else is better.

Finally, in the event that the voting system isn’t implemented by year 8, the 20% of funds intended to go to the ‘voting dev fund’ should by default be sent to a burn address.

References
========

[1] https://www.zfnd.org/blog/foundation-in-2019/

[2] https://www.zfnd.org/blog/dev-fund-guidance-and-timeline/

Changelog:

* 2019-06-19 initial post
* 2019-26-07 listed three strengths of this proposal
* 2019-08-13 Voting System Requirements
* 2019-08-20 Requirements Specifically for the ECC
* 2019-08-29 update to be more like a zip draft
