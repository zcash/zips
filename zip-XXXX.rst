::

  ZIP: Unassigned
  Title: Decentralize the Dev Fee
  Owners: Matt Luongo <matt@thesis.co>
  Status: Draft
  Category: Process
  Created: 2019-09-27
  License: MIT

Motivation
==========

Who am I?
---------

My name is Matt Luongo. I'm an entrepreneur who's been full-time in the crypto
space since 2014, co-founding Fold, a Bitcoin payments company, and more
recently Keep, a private computation startup built on Ethereum. I've built some
`around Zcash <https://github.com/ethereum/EIPs/pull/2129>`_, and we've
considered investing more heavily in Zcash development on our latest project.

I'm deeply interested in privacy tech. For me, privacy is about consent --
consent to know my habits, beliefs, and preferences -- and I see privacy as
the next frontier in our pursuit of an economy that respects individual choice.

My perspective is as the founder of a for-profit company focused on building
self-sovereign technologyi who would like to develop on Zcash. We work in this
space ideologically, but our work isn't free; attracting and growing talent
requires funding.

If you're interested in more on my background, I've introduced myself more
`properly on the forum
<https://forum.zcashcommunity.com/t/introducing-matt-luongo-from-keep/34947>`_.

What's this about?
------------------

Since Zcon1, I've been looking to fund work to build an Ethereum / Zcash bridge.
I've spoken to the ECC, the Zcash Foundation, and a number of early Zcash
community members on how best to move forward with this project, and in the
process I've learned a lot about how the community works and dev governance has
been structured thus far.

Inevitably, I've become interested in the community's proposals for a new dev
fee, and thought about how the right structure might support work like ours.

I believe the Zcash community has an opportunity to deploy a new incentive
structure that will attract companies like ours to build and improve Zcash,
leading to a more resilient network, stronger technology, and wider usage.

The Zcash Narrative
-------------------

We're all here to build a robust, private, decentralized currency. But in the
dev fee proposals I've seen so far, the idea of a Zcash narrative that
distinguishes it from the competition is absent.

One direction proposed in ZIP XYZ claims that Zcash is a hedge against Bitcoin's
long-term privacy failure. Put simply, Zcash is "Bitcoin, but private".

I believe that Zcash should aim higher. Only one coin has successfully made a
store of value argument, which I like to call "worse is better". Don't upgrade
the network -- stability is more important than solving today's problems.
Bitcoin is chasing the Lindy effect, where worse is better, and that's great for
Bitcoin. For the rest of us, though, better is better. Zcash *should be better*.

Zcash is known for having the best tech in the space, built by one of the best
team's in the space. We should lean in to that reputation, nurturing the best
research and engineering talent to take Zcash to the next level, leveraging a
Zcash dev fee as a differentiator to build the world's best private medium of
exchange.

Evolving Zcash Governance
=========================

Principles of cryptocurrency governance
---------------------------------------

Most proof-of-work chains today have three major governing roles

1. Miners validate and secure the chain. They do some work to earn a reward.
   Miners are the first owners of newly minted coins, and are an integral part
   of network upgrades.
2. Users buy, hold, and spend the currency. In networks like Bitcoin, they also
   run full nodes, strengthening network resilience by decentralizing
   validation.
3. Developers maintain clients to power and interact with the network. They
   typically propose network upgrades.

On a chain like Bitcoin, any of these roles can veto a network upgrade.

1. Miners can veto activating a new fork by refusing to build off blocks using
   new network rules, orphaning a minority effort. They can also attack any fork
   attempt that doesn't change
2. Users can veto a fork by refusing to update their full nodes, rejecting
   blocks as invalid -- as demonstrated in the UASF fiasco resulting from the
   SegWit2x attempt to force a Bitcoin hardfork. Users can also vote with their
   dollars, acting as a fork resolution of last resort via market pressure.
3. Developers can refuse to update client codebases to follow a fork. While this
   might not seem like a strong veto, in practice that means any fork will need
   at least one additional development team, or the agreement of existing client
   software developers.

These roles together form a balance of power that makes contentious forks
difficult -- any change that a large swath of users disapproves of could split
the chain.

The state of play
-----------------

In Zcash, the addition of the Electic Coin Company (ECC) and the Zcash
Foundation skew this balance.

Both organizations are comprised of Zcash founders, developers, researchers, and
privacy proponents who have driven this ecosystem forward and represent its
values. Nevertheless, their mode of operation today skews a healthy balance of
power in Zcash governance.

The mechanisms of that skew are the Zcash trademark, held by the ECC, and
primary client software development, now split between the ECC and the
Foundation.

In a disagreement between miners, users, and developers, the ECC has the
unilateral option of enforcing the Zcash trademark, effectively allowing them
to choose a winning fork against the will of users, miners, and other
developers.

While the Foundation's maintenance of the `zebrad` client would normally allow
them to "soft veto" a network upgrade, they don't have a similar veto on the
Zcash trademark enforcement.

Compounding these issues, the Foundation and the ECC aren't arms-length entities
as they're organized today.

This situation poses a number of problems for new and existing Zcash users, as
well as both entities.

* The threat of a central entity overriding (or being forced to override) the
  will of users undermines self-sovereignty.
* The ECC and Foundation are both put at legal risk. As entangled entities,
  they're remarkably similar to a single entity when trying to minimize
  regulatory risk.
* Power between the two entites *hasn't* been decentralized. The ECC remains
  a unilateral power, as well as a single point of failure.

The "crowding out" problem
--------------------------

The last issue arising from this scheme is the one I'm most incentivized to
address.

The Zcash ecosystem, as it exists today, has little incentive for outside
developers to participate.

Zcash development has a high learning curve.

* The reference client is a fork of the Bitcoin reference implementation,
  building on a decade of poorly written legacy code.
* What Zcash brings to the table involves a greater understanding of applied
  cryptography than most projects. SNARKs are often still referred to as "moon
  math", after all.
* As the recent network-level attack demonstrates, full-stack privacy is hard.

Most outside developers need to see a clear path to longer-term funding before
they can commit to the cost of that curve.

Even those developers who already have the expertise to work on this system are
frustrated by the lack of longer-term funding. For evidence, look at Parity's
exit from Zcash after `zebrad` development, or Summa's struggles to work on
Zcash.

Sustainably attracting talent to Zcash can increase innovation *and* ecosystem
resilience.

Moving Forward
==============

The below proposal is an effort to cleanly resolve the problems with Zcash's
current governance, while

* maintaining a balance of power between stakeholders
* removing single points of failure / control
* growing development and usage of Zcash
* and supporting the best interests of miners, users, and developers *today*.

Decentralizing development
--------------------------

A few proposals have suggested the introduction of a mysterious "third entity"
to resolve disagreements between the Foundation and the ECC.

I prefer a different approach, refocusing the role of the Foundation and making
room for the ECC to innovate alongside outside developers.

In this proposal, the Foundation shall support community development through
running the forum and events, gathering community sentiment, managing short-term
development grants, and conducting the diligence behind the assignment and
disbursement of a development fee. This development fee shall be funded by 20%
of the block reward, with as much as half of the fee burned each month based on
market conditions.

The Foundation shall receive 25% of the dev fee. If the volume-weighted average
price of ZEC over the month means the foundation would receive greater than
$500k that month, the foundation shall burn the remaining ZEC such that their
max benefit is $500k that month.

The remaining 75% of the dev fee shall be distributed between development teams
working to maintain clients.

* One third of the remaining fee (25% of the total) shall be reserved for the
  role of the "principal developer", a developer with additional voice in Zcash
  governance. The principal developer allocation shall be capped similarly to
  the Foundation's at $500k per month based on a volume-weighted average price.
* The remaining two thirds of the fee (50% of the total), called the "outside
  development fee", shall be distributed between at least two developers,
  chosen semi-annually by the Foundation. Unlike those of the Foundation and
  principal developer, these allocations aren't limited by market conditions,
  and don't carry a burn requirement.

The role of dev fee recipients
------------------------------

Dev fee recipients are distinguished from grant recipients in the scope and
timelines of their work, as well as the specificity of direction. The intent
is to allow teams to focus on a core competency, while encouraging research and
adjacent work.

Dev fee recipients are chosen semi-annually by the Foundation based on their
ability to move Zcash forward. Recipients will typically be development teams,
though "full stack" teams that can communicate well with the community, expand
Zcash usage, and widely share their work should be advantaged.

Recipients shall submit quarterly plans to the community for their efforts, as
well as monthly progress updates.

All work funded by the dev fee will be open source, under licenses compatible
with the existing Zcash clients.

Though the Foundation shall periodically judge the efficacy of dev fee
recipients, deciding on and driving roadmaps for Zcash is the role of dev fee
recipients, in partnership with the community. This role is neatly balanced by
users running full nodes and miners, either of which can veto a network upgrade.

While dev fee recipients are not required to work exclusively on Zcash,
considering the nature of their work, recipients must guarantee they aren't
obliged to the interests of competing projects.

The role of the principal developer
-----------------------------------

The role of the principal developer is as a "first among equals" amongst the dev
fee recipients.

The principal developer shall make a number of guarantees.

1. Zcash shall be their exclusive focus, submitting financials periodically to
   the Foundation as assurance.
2. They shall maintain a well-run board and employ a qualified CFO.
3. In addition to the existing open-source requirements, they shall agree to
   assign any trademarks or patents relevant to Zcash to the Foundation.

In exchange, the principal developer is granted an indefinite dev fee allocation
and a wide remit to pursue longer-term research relevant to Zcash, as well as
a voice on the board of the Foundation.

Minimum viable Foundation
-------------------------

To manage the dev fee and fulfill its community and diligence duties, the
Foundation shall maintain a board of 5 independent members. Rather than the
structure in the current bylaws, the board will consist of

* 1 seat voted on by ZEC holders directly.
* 1 seat representing a newly created research advisory board, whose primary
  role will be technical diligence of potential recipients of the dev fee.
* 1 seat for the "principal developer", a privileged recipient of the Zcash
  dev fee acting as "first among equals" amongst a variety of dev fee recipients
  building on Zcash.
* 2 seats elected by the board, as the board is currently selected according to
  the bylaws. The board's discretion here means these could be selected via a
  community election, or via the remaining 3 seats' direct vote.

The Foundation requires a professional board. Board member selection should
heavily favor candidates with existing formal public or private sector board
experience. Each board member shall be paid reasonably by the Foundation.

Each board member should bring a unique network and set of skills to bear to
increase the impact of the Foundation.

Outside the seat for the principal developer, no board members shall have an
ongoing commercial interest in any recipients of the dev fee.

The ECC as the principal developer
----------------------------------

I propose that the ECC be considered as the initial principal developer,
receiving an indefinite dev fee allocation in exchange for their exclusive
focus on Zcash research and development, and assigning all patents and marks
relevant to Zcash to the Foundation.

I believe this arrangement is best for the Zcash ecosystem, and with proper
management of funds, should satisfy the ongoing needs of the ECC.

The dev call
------------

The Foundation shall organize a bi-weekly call for all dev fee recipients and
other third party developers. The call will be live-streamed for community
participation, though the speaking participants will be invite only. At a
minimum, a single representative from each dev fee recipient should attend.

The Foundation shall also maintain a simple chat solution for development of
the protocol. While the chat logs should be publicly viewable, it need not be
open to public participation.
