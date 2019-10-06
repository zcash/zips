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
