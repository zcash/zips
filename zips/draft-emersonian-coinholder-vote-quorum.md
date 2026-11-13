    ZIP: Unassigned
    Title: Update to ZIP 1016: Raise the Coinholder Vote Threshold to 1,000,000 ZEC
    Owners: Blake Benthall (emersonian) <e@emersonbenthall.com>
    Status: Draft
    Category: Process
    Created: 2026-11-08
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/zip-raise-the-coinholder-vote-threshold/59044>
    Pull-Request: <https://github.com/zcash/zips/pull/1449>
    Updates: 1016


# Terminology

The key words "MUST" and "SHOULD" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

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

ZEC voted

: For a given question in a coinholder-amount voting round, the total amount of
  ZEC committed by all ballots cast on that question, including ballots that
  abstain.


# Abstract

This ZIP raises the minimum amount of ZEC that must be voted for a
coinholder-amount voting round under ZIP 1016 [^zip-1016] to approve a grant,
from 420,000 ZEC to 1,000,000 ZEC. At current holdings, this means that no
single publicly known holder of ZEC, and not even the two largest known
holders together, can make a vote valid on their own. The top proposal in the
most recent round drew about 2.18 million ZEC, worth about US$3.1 billion, so
the new threshold is still well within reach of proposals with broad
support.

It also writes down how abstentions are counted, which ZIP 1016 never stated:
abstaining ZEC counts toward the 1,000,000 ZEC threshold, but not toward the
majority.

Nothing else about coinholder voting changes. Ballots are still weighted by
ZEC, and a simple majority of the ZEC voted for or against still decides the
result. The ZIP has no privacy implications.

A companion draft [^draft-human-minimum] would add a minimum number of
distinct human participants. The two can be adopted separately or together.


# Motivation

ZIP 1016 requires a minimum of 420,000 ZEC (2% of the total eventual supply)
to be voted, with a simple majority cast in favor, for a grant proposal to be
approved [^zip-1016-disbursement]. ZIP 1016 itself lists "Is 420,000 ZEC the
right threshold for coinholder votes?" as an open question
[^zip-1016-open-questions].

The threshold counts coins, not people. As of late 2026, at least two single
holders control a large share of it:

| Holder | ZEC held | Share of the 420,000 ZEC threshold | Share of 1,000,000 ZEC |
|---|---|---|---|
| Grayscale Zcash ETF (ZCSH) | ~594,293 ZEC (2026-10-30) [^grayscale] | 141% | 59% |
| Cypherpunk Technologies (Nasdaq: CYPH) | ~326,417 ZEC (2026-09-30) [^blockworks-q3] | 78% | 33% |

Under the current rule, one holder could supply the whole turnout of a
coinholder-amount voting round, and a vote in which no one else took part
would still be valid. The author does not claim that either entity has voted,
or would vote, in this way. The concern is that the rules allow it, so a
passing result cannot by itself show that coinholders in general, rather than
one balance sheet, supported a grant.

Raising the threshold to 1,000,000 ZEC puts it well above the largest known
single holding, and above the two largest combined. Recent high-interest
rounds have drawn far more than that: the top proposal in the Q3 2026 round
had about 2.18 million ZEC voted, worth about US$3.1 billion at the time
[^blockworks-q3]. The change should not stop well-supported proposals from
passing.


# Privacy Implications

This ZIP has no privacy implications. It changes a number in ZIP 1016 and
states how abstentions are counted. It does not change how ballots are cast,
what voters reveal, or what is published about them.


# Requirements

* No single holder of ZEC, as currently known, can satisfy the threshold of a
  coinholder-amount voting round alone.
* Voters and applicants can know the threshold in advance without any further
  calculation.
* The way abstentions are counted is stated, not left to each round's
  organizers.


# Non-requirements

* This ZIP does not change how ballots are weighted.
* This ZIP does not add a minimum number of human participants. That is left
  to a companion draft [^draft-human-minimum].
* This ZIP does not change the veto process of ZIP 1016 [^zip-1016-veto], the
  funding streams, or the membership of the Key-Holder Organizations.
* This ZIP does not set a minimum holding for individual voters.


# Specification

## Changes to the ZEC threshold

In the "Disbursement process" section of ZIP 1016 [^zip-1016-disbursement],
the paragraph beginning "For coinholder votes, a minimum of 420,000 ZEC" is
amended by replacing "420,000 ZEC (2% of the total eventual supply)" with
"1,000,000 ZEC". The rest of that paragraph, including the rules for competing
proposals, is unchanged.

## Counting ZEC voted

For the purpose of the threshold:

* ZEC committed by ballots that approve, reject, or abstain all counts toward
  ZEC voted.
* The simple majority is computed over ZEC committed by ballots that approve
  or reject. Abstaining ZEC does not count in favor or against.
* ZEC voted is measured on each question separately. Ballots cast on a
  different proposal, including a competing proposal, do not count.

The Key-Holder Organizations MUST report, for each question, the ZEC voted,
the ZEC in favor, the ZEC against, and the ZEC abstaining when they publish
the result of a coinholder-amount voting round.

## Testnet

In the "Testnet-specific considerations" section of ZIP 1016, "The threshold
of 420,000 ZEC" is replaced with "The threshold of 1,000,000 ZEC".

## Open question removed from ZIP 1016

The open question "Is 420,000 ZEC the right threshold for coinholder votes?"
is removed from ZIP 1016.

## Activation

This ZIP applies to any coinholder-amount voting round whose voting window
opens on or after the date this ZIP's Status becomes Active. The Key-Holder
Organizations SHOULD announce the new threshold when they announce the first
round to which it applies.


# Rationale

## Why 1,000,000 ZEC

1,000,000 ZEC is about 4.76% of the eventual supply of 21,000,000 ZEC. It is
well above the largest publicly known single holding (the Grayscale Zcash ETF,
at about 594,293 ZEC on 2026-10-30 [^grayscale]), and above the two largest
known holdings combined (about 920,710 ZEC). It is still well below the
turnout of recent high-interest rounds: the top proposal in the Q3 2026 round
had about 2.18 million ZEC voted [^blockworks-q3], worth about US$3.1 billion
at the price of ZEC on 30 September 2026. The new threshold is less than half
of that turnout.

Turnout in the Q1 2026 round peaked near 500,000 ZEC, so some past proposals
that passed would not have reached the new threshold. This is intended.

## Why a fixed number

A fixed number was chosen over a percentage of circulating supply so that
voters and applicants know the threshold in advance. Holdings change, and
1,000,000 ZEC will not stay above the largest single holding forever. A minimum
number of human participants, as proposed in the companion draft
[^draft-human-minimum], is the more durable protection, but it needs a
proof-of-personhood process that does not exist yet. This ZIP can be adopted
now, without waiting for that.

## Why abstentions count toward the threshold

Recent rounds have reported abstentions, but ZIP 1016 never said how they
count. Counting them toward turnout, but not toward the majority, treats an
abstaining voter as someone who took part without taking a side. The
alternative, excluding them, would make it harder for a well-attended but
divided vote to be valid.


# Open questions

* Should ZEC that abstains count toward the 1,000,000 ZEC threshold? This draft
  says yes.
* Should the threshold be reviewed on a schedule, for example whenever a
  single known holding passes 80% of it?
* Is 1,000,000 ZEC too high for routine grant rounds with lower turnout? An
  alternative is 600,000 ZEC, just above the largest known single holding.
* This draft sets a minimum total of ZEC voted on a question. It does not set
  a minimum holding for an individual voter. Should it?


# References

[^BCP14]: [Information on BCP 14, "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-1016-disbursement]: [ZIP 1016: Community and Coinholder Funding Model, Disbursement process](zip-1016.md#disbursement-process)

[^zip-1016-veto]: [ZIP 1016: Community and Coinholder Funding Model, Veto process](zip-1016.md#veto-process)

[^zip-1016-open-questions]: [ZIP 1016: Community and Coinholder Funding Model, Open questions](zip-1016.md#open-questions)

[^draft-mcgee-keyholders]: [Draft ZIP: Update to ZIP 1016 & ZIP 271: Key-Holder Organizations](draft-mcgee-keyholders-organizations.md)

[^draft-human-minimum]: Draft ZIP: Update to ZIP 1016: Minimum Human Participation and Published Proof-of-Personhood for Coinholder Votes (separate draft)

[^grayscale]: [Grayscale Zcash ETF (ZCSH) holdings, as of 2026-10-30](https://www.thezcashetf.com/)

[^blockworks-q3]: [Blockworks, Zcash Token Holder Report, Q3 2026](https://app.blockworks.com/report/zcash-token-holder-report-q3-2026)
