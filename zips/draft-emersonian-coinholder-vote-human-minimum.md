    ZIP: Unassigned
    Title: Update to ZIP 1016: Minimum Human Participation and Published Proof-of-Personhood for Coinholder Votes
    Owners: Blake Benthall (emersonian) <e@emersonbenthall.com>
    Status: Draft
    Category: Process
    Created: 2026-11-08
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/zip-minimum-human-participation-in-coinholder-votes/59045>
    Pull-Request: <https://github.com/zcash/zips/pull/1450>
    Updates: 1016


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [^protocol-networks].

The terms "Coinholder-Controlled Fund" and "Key-Holder Organizations" in this
document are to be interpreted as described in ZIP 1016 [^zip-1016], as
amended by any ZIP that updates the membership of the Key-Holder Organizations
(see for example [^draft-mcgee-keyholders]).

"ZEC" refers to the native currency of Zcash on Mainnet.

The terms below are to be interpreted as follows:

Coinholder-amount voting round

: Any coinholder vote held under ZIP 1016 [^zip-1016-disbursement], in which
  each ballot is weighted by the amount of ZEC that the voter proves control of.
  This includes votes on grant applications, separate votes on competing
  proposals, and additional votes on whether funding of an existing grant should
  continue.

Coinholder poll

: A coinholder-amount voting round, or any other poll of ZEC holders that is
  organized, administered, or certified by one or more Key-Holder Organizations,
  or that a ZIP cites as evidence of coinholder support or opposition.

Ballot

: A single vote cast in a coinholder poll on a single question. A ballot is one
  of Approve, Reject, or Abstain (or the equivalent options of a poll that is
  not a yes/no question).

ZEC voted

: ZEC voted in a coinholder poll, for a given question, is the total amount of
  ZEC committed by all ballots cast on that question, including ballots that
  Abstain.

Verified coinholder-person

: A natural person who, for a given coinholder poll, has been verified under the
  Human Verification Methodology in effect for that poll as (a) being a unique
  natural person, and (b) controlling at least the Minimum Personhood Balance of
  ZEC at the snapshot height used for that poll.

Human Verification Methodology

: The document described in [Human Verification
  Methodology](#human-verification-methodology).

Personhood Attestation

: The Personhood Attestation for a coinholder poll is the report described in
  [Personhood Attestation](#personhood-attestation).


# Abstract

This ZIP updates ZIP 1016 [^zip-1016] so that a coinholder-amount voting round
can only approve a grant, or otherwise bind the Key-Holder Organizations, if:

* the ZEC threshold of ZIP 1016 is met, as it stands or as raised by the
  companion quorum draft [^draft-quorum];
* ballots were cast on the question by at least 50 distinct verified
  coinholder-persons; and
* the Key-Holder Organizations published their Human Verification Methodology
  in advance, and publish a Personhood Attestation for the result.

It requires the Key-Holder Organizations to publish the methodology they use
to verify that participants are distinct humans, in a way that preserves the
privacy of voters and of their vote choices. A coinholder poll that does not
meet these conditions is advisory only.

This ZIP does not change how ballots are weighted. Coinholder-amount voting
rounds continue to be decided by the amount of ZEC voted. The human
participation requirement is a floor on legitimacy, not a second vote.


# Motivation

ZIP 1016 requires a minimum amount of ZEC to be voted, with a simple majority
in favor, for a grant proposal to be approved [^zip-1016-disbursement]. That
threshold counts coins, never people. As of late 2026, the Grayscale Zcash ETF
alone held about 594,293 ZEC [^grayscale], more than the whole 420,000 ZEC
threshold, and Cypherpunk Technologies about 326,417 ZEC [^blockworks-q3].
A single holder could therefore make a vote valid with no one else taking
part. The author does not claim that anyone has done so. The concern is that a
result alone cannot show that coinholders in general, rather than one balance
sheet, supported a grant.

The companion quorum draft [^draft-quorum] raises the threshold to 1,000,000
ZEC, but any coin threshold can be met by whoever accumulates enough coins.
This ZIP therefore also requires a minimum number of distinct humans to have
taken part.

Counting humans requires a method for verifying personhood. Today no ZIP
defines "coinholder" [^zip-1016], and the voting model that ZIP 1016 says will
be "specified in another ZIP [TBD]" [^zip-1016-ccf] has not been written. The
Key-Holder Organizations already organize and certify votes, and so act as de
facto election administrators. If they are to count humans, the community
needs to be able to see and critique how they do it, before the vote rather
than after.

Zcash's purpose is financial privacy. Any proof-of-personhood process for
Zcash coinholder polls must therefore be designed so that verifying that a
voter is a unique human does not reveal who that voter is, which shielded
addresses they control, or how they voted.


# Privacy Implications

Counting distinct humans means that someone has to check personhood, and any
such check can leak information. A careless process could link a voter's
legal identity to their shielded holdings, reveal which addresses or notes
they control, or record how they voted. Any of these would undermine the
financial privacy that Zcash exists to provide, and could expose voters to
coercion or targeting.

This ZIP does not choose a proof-of-personhood technology. Instead, the
Specification limits what a Human Verification Methodology may require and
what may be published. Participants do not have to publish their legal
identity, move funds out of a shielded pool, or reveal a shielded address or
viewing key, and no link between a person and their ballot is recorded. The
Personhood Attestation reports counts only. The methodology also has to say
what data is collected, who sees it, and how long it is kept, so that the
community can judge the remaining privacy risk before each vote.

Taking part in personhood verification is optional. A coinholder who does not
want to be verified can still vote, and their ZEC is counted as before.


# Requirements

* A coinholder-amount voting round cannot bind the Key-Holder Organizations
  unless a minimum number of distinct humans participated.
* The method by which humans are counted is published before voting begins,
  and cannot be changed during a voting window.
* The process does not require publication of any voter's identity, the
  addresses they control, or the link between a person and their ballot.
* The outcome of every coinholder poll states whether it met the conditions
  to be binding, so that the community can tell a binding result from an
  advisory one.


# Non-requirements

* This ZIP does not introduce person-weighted (one-person-one-vote) decision
  making, and does not change the weighting of ballots by ZEC amount.
* This ZIP does not specify a particular proof-of-personhood technology.
  Choosing one is left to the Key-Holder Organizations, subject to the
  publication, privacy, and audit requirements below.
* This ZIP does not change the ZEC threshold of ZIP 1016. That is the
  subject of the companion quorum draft [^draft-quorum].
* This ZIP does not change the veto process of ZIP 1016 [^zip-1016-veto], the
  funding streams, or the membership of the Key-Holder Organizations.
* This ZIP does not specify the general voting model that ZIP 1016 defers to
  "another ZIP [TBD]", although it constrains any such model.


# Specification

## Changes to ZIP 1016

In the "Disbursement process" section of ZIP 1016 [^zip-1016-disbursement],
the following sentence is added after the sentence that sets the minimum
amount of ZEC to be voted:

> In addition, ballots on a grant proposal MUST have been cast by at least 50
> distinct verified coinholder-persons, and the other conditions in ZIP [this
> ZIP] MUST be met, for the grant proposal to be approved.

In the "Testnet-specific considerations" section of ZIP 1016, the following
sentence is added after the sentence about the Mainnet ZEC threshold: "The
minimum number of verified coinholder-persons applied to Mainnet coinholder
votes does not apply to these rehearsals, but Testnet rehearsals SHOULD
exercise the Human Verification Methodology."

## Minimum human participation

A question in a coinholder-amount voting round MUST NOT be treated as approved
unless ballots on that question were cast by at least 50 distinct verified
coinholder-persons. Ballots that Abstain count toward this minimum.

Each verified coinholder-person counts at most once toward this minimum for a
given question, regardless of how many addresses, wallets, or ballots they
use.

A verified coinholder-person counts toward this minimum regardless of how much
ZEC they hold above the Minimum Personhood Balance, and regardless of which
way they voted.

Coinholders who do not take part in personhood verification MAY still vote.
Their ZEC counts toward ZEC voted and toward the majority as before. They do
not count toward the minimum number of verified coinholder-persons.

## Human Verification Methodology

The Key-Holder Organizations MUST jointly publish a Human Verification
Methodology, and MUST publish it on the Zcash Community Forum and at a stable
URL linked from the announcement of each coinholder poll.

The Human Verification Methodology for a coinholder poll MUST be published at
least 30 days before the voting window for that poll opens, matching the
existing 30-day community review period for grant applications
[^zip-1016-disbursement]. It MUST NOT be changed between that publication and
the publication of the Personhood Attestation for that poll, except to
correct a security vulnerability, in which case the change and the reason for
it MUST be published immediately.

The Human Verification Methodology MUST describe at least:

1. Verification method: how a participant demonstrates that they are a
   unique natural person, including any third-party services, credentials,
   in-person events, social attestation, or cryptographic protocols used.
2. Uniqueness: how the process prevents one person from being counted
   more than once for the same question (Sybil resistance), and the known
   limits of that protection.
3. Coinholder link: how a verified person is linked to control of at
   least the Minimum Personhood Balance of ZEC at the poll's snapshot height,
   without revealing which addresses or notes they control.
4. Minimum Personhood Balance: the minimum amount of ZEC that a person
   must control to be counted as a verified coinholder-person. This MUST be
   greater than zero, and SHOULD be no more than 1 ZEC.
5. Privacy: what data is collected about participants, who can see it,
   how the link between a person and their ballot is kept from being
   recorded or disclosed, and how long any data is retained.
6. Accessibility: how a coinholder can take part regardless of
   jurisdiction, wallet software, or whether they hold ZEC in shielded or
   transparent addresses, and what alternatives exist for those who cannot
   use the primary method.
7. Administration: which Key-Holder Organization or contracted third
   party operates each part of the process, and any conflicts of interest
   they have in the poll's outcome.
8. Audit: how an independent party, or the public, can check the count of
   verified coinholder-persons without learning their identities.
9. Disputes: how a participant, applicant, or member of the community can
   challenge a verification decision or the published count, and who decides.

The Human Verification Methodology:

* MUST NOT require that a participant's legal identity be published, or be
  disclosed to any party other than one named in the methodology under item 7.
* MUST NOT record or publish any link between a verified coinholder-person and
  the content of their ballot.
* MUST NOT require that a participant move funds out of a shielded pool, or
  reveal a shielded address or viewing key to any party.
* SHOULD prefer methods in which no single party learns both a participant's
  identity and the fact that they took part in the poll.
* SHOULD be the same for every question in a voting window.

Any Key-Holder Organization MAY additionally publish its own objections to, or
reservations about, a jointly published methodology.

## Personhood Attestation

Within 7 days after a voting window closes, and before any disbursement is
signed on the basis of a vote held in that window, the Key-Holder
Organizations MUST publish a Personhood Attestation that states, for each
question:

* the ZEC voted, the ZEC in favor, the ZEC against, and the ZEC abstaining
  (ZEC voted includes abstaining ZEC);
* the number of distinct verified coinholder-persons who cast a ballot on it;
* whether each of the conditions in this ZIP was met; and
* a reference to the Human Verification Methodology that was in effect.

The Personhood Attestation MUST be signed by each Key-Holder Organization
that agrees with it. A Key-Holder Organization that does not agree with the
attestation MUST publish its reasons.

The Personhood Attestation MUST NOT contain any information that identifies a
verified coinholder-person or links them to their ballot.

## Binding and advisory results

A coinholder poll is "binding" only if:

1. a Human Verification Methodology was published for it as required above;
2. the minimum amount of ZEC required by ZIP 1016, as amended at the time
   the voting window opens, was voted on the question;
3. ballots on the question were cast by at least 50 distinct verified
   coinholder-persons; and
4. a Personhood Attestation for it has been published, and is signed by at
   least two Key-Holder Organizations.

A coinholder poll that is not binding is "advisory". In particular:

* The Key-Holder Organizations MUST NOT sign a disbursement from the
  Coinholder-Controlled Fund on the basis of a coinholder-amount voting round
  that is not binding. A grant proposal on which the vote is advisory is not
  approved, whatever the outcome of the ballots.
* Where a vote on whether funding of an existing grant should continue is
  advisory, the existing grant continues on its existing terms, as if the
  vote had not been held.
* A ZIP or Key-Holder Organization communication MUST NOT describe the result
  of an advisory coinholder poll as a decision, approval, or mandate of
  coinholders. It MAY report the result, labeled as advisory, with the
  Personhood Attestation.

The Key-Holder Organizations' veto rights under ZIP 1016
[^zip-1016-veto] are unchanged and apply only to binding votes.

## Scope

This ZIP applies to every coinholder-amount voting round under ZIP 1016
[^zip-1016], including separate votes on competing proposals and votes on the
continuation of an existing grant.

For a coinholder poll that is not a coinholder-amount voting round, such as a
sentiment poll on a protocol change, this ZIP does not decide what weight the
community gives the result. The poll's organizers SHOULD apply the Human
Verification Methodology, and the result MUST be reported as binding or
advisory under the rules above.

## Activation

This ZIP takes effect for any coinholder poll whose voting window opens on or
after the later of:

* the date this ZIP's Status becomes Active; and
* 30 days after the first Human Verification Methodology is published.

Until then, coinholder-amount voting rounds continue under the existing rules
of ZIP 1016.


# Rationale

## Why a human minimum rather than human-weighted votes

Changing to one-person-one-vote would be a larger change to ZIP 1016's
funding model, which was adopted on the basis of giving coinholders a voice
in proportion to their holdings. A minimum number of distinct participants
keeps coin-weighted decisions, but requires evidence that a grant was
approved by more than a handful of parties. It is a quorum of people, not a
vote of people.

Parallel person-based polls, such as the coinperson poll planned for
December 2026 [^coinperson], can inform whether a stronger, bicameral
requirement is warranted in a future ZIP.

## Why 50 humans

50 is low enough that any genuinely community-supported proposal should be
able to reach it, and high enough that a single holder, or a small group of
insiders, cannot reach it without visibly recruiting others. The number of
distinct participants in past rounds has not been published, so the
threshold can be revisited once Personhood Attestations provide data.

## Why the Key-Holder Organizations publish the methodology

The Key-Holder Organizations already agree the grant application process,
decide which proposals are in competition, and sign disbursements
[^zip-1016-disbursement]. They are the parties who would act on a
personhood count, and are the natural parties to be accountable for it.
Requiring publication before the voting window opens means that the method
can be reviewed alongside the grant applications, and cannot be adjusted
after the fact to change an outcome.

The ZIP sets requirements on what the methodology must disclose and protect,
rather than choosing a technology, because proof-of-personhood methods are
changing quickly and each has different privacy and accessibility trade-offs.

## Why privacy constraints

A proof-of-personhood process that links identities to shielded holdings or
to ballots would undermine the financial privacy that Zcash exists to
provide, and could expose voters to coercion. The constraints in this ZIP are
intended to make the count of humans checkable without making any individual
human visible.


# Open questions

* Should this ZIP stay separate from the quorum draft [^draft-quorum], or be
  merged with it after community polling?
* Should the human minimum scale with the size of the grant, for example
  requiring more verified coinholder-persons for grants above a given amount?
* Should the Minimum Personhood Balance be fixed in this ZIP rather than set
  by the methodology?
* Should the Personhood Attestation require all of the Key-Holder
  Organizations, rather than two?
* Should Zcash Community Grants, or another party independent of the
  Key-Holder Organizations, audit the Personhood Attestation?
* ZIP 1016 only recommends that the Key-Holder Organizations sign the
  transactions for an approved grant. Should signing be made mandatory for
  binding votes?


# References

[^BCP14]: [Information on BCP 14, "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-1016-ccf]: [ZIP 1016: Community and Coinholder Funding Model, Coinholder-Controlled Fund](zip-1016.md#coinholder-controlled-fund)

[^zip-1016-disbursement]: [ZIP 1016: Community and Coinholder Funding Model, Disbursement process](zip-1016.md#disbursement-process)

[^zip-1016-veto]: [ZIP 1016: Community and Coinholder Funding Model, Veto process](zip-1016.md#veto-process)

[^draft-quorum]: Draft ZIP: Update to ZIP 1016: Raise the Coinholder Vote Threshold to 1,000,000 ZEC (separate draft)

[^draft-mcgee-keyholders]: [Draft ZIP: Update to ZIP 1016 & ZIP 271: Key-Holder Organizations](draft-mcgee-keyholders-organizations.md)

[^grayscale]: [Grayscale Zcash ETF (ZCSH) holdings, as of 2026-10-30](https://www.thezcashetf.com/)

[^blockworks-q3]: [Blockworks, Zcash Token Holder Report, Q3 2026](https://app.blockworks.com/report/zcash-token-holder-report-q3-2026)

[^coinperson]: [coinperson.org](https://coinperson.org/)
