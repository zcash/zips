
    ZIP: XXX
    Title: Disabling Addition of New Value to the Transparent Chain Value Pool
    Owners: Arya <arya@zfnd.org>
            Daira-Emma Hopwood <daira@jacaranda.org>
    Status: Draft
    Category: Consensus
    Created: 2025-08-13
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/1115>
    Pull-Request: <https://github.com/zcash/zips/pull/1067>


# Terminology

The key word "MUST" and "OPTIONAL" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The term "network upgrade" in this document is to be interpreted as described
in ZIP 200. [^zip-0200]

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The term "transparent protocol" in this document refers to the
payment protocol derived from Bitcoin that provides no privacy.

The term "Sprout shielded protocol" in this document refers to the shielded
payment protocol present at Zcash launch. [^protocol]

The term "Sapling shielded protocol" in this document refers to the shielded
payment protocol introduced in the Sapling network upgrade. [^zip-0205]

The term "Orchard shielded protocol" in this document refers to the shielded
payment protocol introduced in the NU5 network upgrade. [^zip-0252]

The term "transparent chain value pool balance" in this document is to be
interpreted as described in § 4.17 ‘Chain Value Pool Balances’.
[^protocol-chainvaluepoolbalances]


# Abstract

This proposal disables the ability to add new value to the transparent chain
value pool balance. This takes a step toward being able to remove the
transparent protocol, thus reducing the overall complexity and attack surface
of Zcash and increasing user privacy without causing the loss of users' funds.


# Motivation

There are three separate major motivations for this ZIP:

- Since Zcash is a private blockchain, user expectations of privacy are better
  protected by deprecating the transparent pool, which is not private.

- At the launch of the Zcash network, two payment protocols were supported:
  the Sprout shielded protocol, which was relatively closely based on
  the original Zerocash proposal [^zerocash], and the transparent protocol
  derived from Bitcoin.

  The Sprout shielded protocol was later obsoleted by the Sapling and then
  Orchard shielded protocols, which introduced significant efficiency and
  functionality improvements for shielded transactions. The transparent protocol
  has stayed largely the same.

  Removing the ability to add to the transparent chain value pool balance is a
  first step toward reducing complexity and potential risk in the overall Zcash
  protocol, and reducing potential user confusion about the level of privacy they
  obtain from Zcash.

- The transparent scripting system is too complicated to implement in a zk-SNARK
  circuit, which precludes likely approaches to scaling Zcash [^tachyon].

This proposal disables adding new value to the transparent chain value pool,
thus requiring funds to be moved over time into the Sapling or Orchard shielded
pools.

The implication of this is that when coinbase outputs (miner subsidy, fees, and
funding stream outputs) are shielded, they cannot later be unshielded, which
will have the effect of increasing the total proportion of funds held in shielded
pools relative to the transparent pool.


# Specification

Define the *total transparent input value* of a transaction as follows:

- if it is a coinbase transaction, its total input value as defined in § 7.1.2
  ‘Transaction Consensus Rules’ [^protocol-txnconsensus];
- otherwise, the total value of its transparent inputs.

Consensus rule: The total value of transparent outputs in a transaction MUST be
less than or equal to its total transparent input value.

Note: The facility to send to transparent addresses, and/or to give out transparent
addresses on which funds can be received, has always been OPTIONAL for a particular
Zcash wallet implementation.


# Rationale

The implication of this is that when coinbase outputs (miner subsidy, fees, and
funding stream outputs) are shielded, they cannot later be unshielded, which
will have the effect of increasing the total proportion of funds held in shielded
pools relative to the transparent pool.

The code changes needed are very small and simple, and their security is easy to
analyse.

This ZIP is similar to ZIP 211 [^zip-0211] in that it disallows new funds to be
added to the transparent chain value pool balance as ZIP 211 disallowed new funds
to be added to the Sprout chain value pool balance. The consensus rule does not
take the same form because there is no field corresponding to `vpub_old` for the
transparent protocol.

Rejected alternatives:

- Disallow all transparent outputs (this implies the proposed rule).
- Allow at most a single transparent output per transaction in addition to
  the proposed rule.

These were rejected as they seem too impractical at the time of this writing.
In particular, exchanges that need to use the transparent pool for regulatory
reasons would likely need to delist Zcash, and the ecosystem of decentralized
exchanges that support Zcash is insufficiently established to replace the role
that centralized exchanges play today.


# Security and Privacy Considerations

The security motivations for making this change are described in the Motivation section.
Privacy concerns that led to the current design are discussed in the Rationale section.

Since all clients MUST change their behaviour at the same time from this proposal's activation
height, there is no additional client distinguisher.


# Deployment

This ZIP is not currently proposed to activate in a specific network upgrade.


# Reference Implementation

TODO


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-chainvaluepoolbalances]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 4.17: Chain Value Pool Balances](protocol/protocol.pdf#chainvaluepoolbalances)

[^protocol-txnconsensus]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 7.1.2: Transaction Consensus Rules](protocol/protocol.pdf#txnconsensus)

[^zip-0205]: [ZIP 205: Deployment of the Sapling Network Upgrade](zip-0205.rst)

[^zip-0211]: [ZIP 211: Disabling Addition of New Value to the Sprout Chain Value Pool](zip-0211.rst)

[^zip-0252]: [ZIP 252: Deployment of the NU5 Network Upgrade](zip-0252.rst)

[^zerocash]: [Zerocash: Decentralized Anonymous Payments from Bitcoin (extended version)](https://eprint.iacr.org/2014/349)

[^tachyon]: [Tachyon: Scaling Zcash with Oblivious Synchronization](https://seanbowe.com/blog/tachyon-scaling-zcash-oblivious-synchronization/)
