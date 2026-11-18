    ZIP: Unassigned
    Title: Coinholder Elections for Zcash Community Grants
    Owners: Tom Howard <tom@zcashlabs.org>
    Status: Draft
    Category: Consensus Process
    Created: 2026-10-29
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/proposal-to-switch-zcg-elections-to-token-holder-voting/53533>
    Updates: 1015, 1016


# Terminology

The key words "MUST", "MUST NOT", "SHALL", and "SHOULD" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only when,
they appear in all capitals.

"Zcash Community Grants" ("ZCG"), "ZCG Committee", "Zcash Community Advisory
Panel" ("ZCAP"), and "Financial Privacy Foundation" ("FPF") have the meanings
given in ZIP 1015, subject to the amendment to ZCG's definition below.
[^zip-1015]

"Coinholder-Controlled Fund" ("CCF") has the meaning given in ZIP 1016.
[^zip-1016] "ZEC" is the native currency of Zcash Mainnet.

"Coinholder election" means an election in which eligible ZEC provides voting
weight, rather than membership in ZCAP. "Approval voting" means that a voter
can support any number of candidates and the candidates with the highest
approval totals fill the available seats, subject to committee eligibility
constraints.

"Effective Date" means the UTC date specified for the transition under
[Activation and transition]. This date is unassigned in this draft.


# Abstract

This ZIP changes the electorate that selects the Zcash Community Grants
Committee. ZEC holders would elect committee members through private,
ZEC-weighted approval voting, replacing elections by the Zcash Community
Advisory Panel. The committee would continue to evaluate and approve grants
under its existing mandate.

The proposal preserves the five-seat committee, staggered elections, one-year
terms, eligibility for reelection, conflict-of-interest rules, and existing
candidate nomination process. It changes neither ZCG's funding allocation nor
the use of its treasury. FPF would continue administering the program under
the existing financial, legal, and reporting constraints. ZCAP's separate
roles in determining the Discretionary Budget and committee compensation
would remain unchanged.

This ZIP specifies amendments to ZIPs 1015 and 1016 and requires corresponding
amendments to FPF's legal commitments so that the election results govern
committee selection under the program's binding arrangements. Publication or
adoption of a ZIP alone does not amend an existing agreement.

The voting mechanism is outside the scope of this proposal. The remaining
election rules and rollout details are to be completed before activation.
It introduces no changes to Zcash consensus rules or transaction privacy.
Election privacy nevertheless depends on the voting system, its operators,
and the information exposed during participation and tallying.


# Motivation

ZIP 1015 provides for a five-seat ZCG Committee selected by ZCAP or a successor
process. ZIP 1016 continues this arrangement while providing a separate
coinholder-directed funding channel. [^zip-1015-zcg] [^zip-1016]

In the June 2026 ZCG election, ZCAP used approval voting to fill two seats.
Voters could approve multiple candidates, and the two candidates with the
most approvals were elected. [^zcg-june-2026] This gives members of an advisory
panel the formal role of selecting the committee, while ZEC ownership alone
provides no participation right in that election.

ZEC holders have an economic interest in the long-term effects of development
funding. Giving them responsibility for electing ZCG members would connect
that interest to the selection of the people who allocate ZCG resources. It
would also allow participation without admission to a membership panel. The
proposal retains a representative committee, allowing holders to choose its
members without requiring a coinholder vote on each ZCG grant.

ZIP 1016 leaves the definition of the coinholder voting model to a separate
ZIP. [^zip-1016] No Active ZIP currently specifies a coinholder voting
mechanism for these elections. This proposal defines the election rules and
leaves the voting technology to separate work.

The change is deliberately limited to committee selection. It does not
transfer ZCG's grant decisions to the CCF or change the committee's duties,
budget authority, or FPF's administration of grants.


# Privacy Implications

ZEC-weighted voting can expose financial information if eligibility proofs or
ballots reveal balances, addresses, or links between holdings and choices.
This proposal calls for private ballots and independently verifiable aggregate
results. How the voting system protects individual balances and choices
depends on its design and operational assumptions.

Small participation sets, distinctive voting weights, repeated elections, and
network metadata can still create inference or correlation risks. A private
ballot also does not by itself establish resistance to coercion or vote
buying. These risks need independent review in the context of the voting
system used for ZCG elections.

Candidates would continue to participate through the existing nomination and
disclosure process. This ZIP does not alter Zcash transaction formats,
shielded payment privacy, or the information grantees provide to FPF.


# Requirements

* Replace ZCAP membership with eligible ZEC as the basis for voting in ZCG
  committee elections, using private, verifiable coinholder voting.
* Preserve approval voting and the existing committee structure, nomination
  process, election cadence, term lengths, and eligibility constraints.
* Preserve ZCG's grant mandate, funding, treasury, administration, and all
  governance responsibilities other than the election of committee members.
* Make the election outcome binding on FPF through explicit amendments to
  ZIPs 1015 and 1016 and the corresponding legal commitments.
* Protect voter balances and choices while allowing independent verification
  of the tally and its application to the available seats.
* Transition prospectively, without shortening or extending existing terms
  or reopening completed elections.


# Specification

The following requirements govern ZCG committee selection and its legal
implementation. They do not change Zcash consensus rules.

## Electorate and ballot

From the Effective Date, ZCG Committee members MUST be selected by coinholder
election instead of a ZCAP election or another membership-panel election.
FPF MUST arrange the election, with technical and administrative support
as needed. ZCAP membership MUST NOT be a condition of voter eligibility.
Any individual or organization controlling eligible ZEC MUST be permitted
to vote; the association limits on committee members do not restrict voters.

Elections MUST use ZEC-weighted approval voting. For each candidate, the
ballot MUST allow approval or non-approval. A voter MUST be permitted to
approve any number of candidates, including none. The same eligible voting
weight MUST be usable independently for each candidate; it MUST NOT be
divided by the number of candidates approved.

Each candidate's score is the sum of the valid ZEC voting weight approving
that candidate. In an election that meets quorum, available seats MUST be
filled in descending order of score, subject to the eligibility and
association limits in point 7 of ZIP 1015's "Zcash Community Grants (ZCG)"
section, including associations of members whose terms continue. Approval of
a candidate does not require a separate majority of the participating weight.

An election MUST meet the minimum ZEC participation threshold in force for
CCF grant votes under ZIP 1016 when voting opens. [^zip-1016] Turnout is the
total eligible ZEC represented by valid ballots. The same ZEC MUST be counted
only once toward turnout, regardless of how many candidates it approves.
An election that falls short of quorum MUST NOT fill any seats.

## Election administration and record

Elections MUST protect individual choices and balances and allow independent
verification of the aggregate tally. Elections MUST follow any applicable
Active ZIPs governing ZEC eligibility, voting weight, ballot validation,
or tally verification.

When FPF opens nominations, it MUST announce the voting window, number of
seats, and candidate eligibility rules. FPF MUST publish the voter
eligibility rules and voting instructions in time for
voters to prepare before any eligibility cutoff and participate in the vote.
The final candidate list and its mapping to the ballot MUST be published
before voting opens. The election record MUST include the quorum threshold,
turnout, and verified aggregate tally. It MUST explain how the quorum and
candidate eligibility rules determined the outcome.

Tie resolution and procedures for an invalid or interrupted election or an
election that falls short of quorum remain open in this draft. These rules
MUST be resolved in this ZIP before it becomes Active, including how
vacancies are handled without changing the existing one-year terms or
granting FPF discretion to appoint unelected candidates.

## Activation and transition

This ZIP MUST NOT take effect while its status is Draft. Before activation,
the ZIP process MUST establish community adoption, this ZIP MUST specify an
Effective Date, and FPF MUST publish confirmation that the legal requirements
below have been satisfied.

The new electorate MUST apply to elections whose nomination period opens on
or after the Effective Date, including elections to fill vacancies. An
election already underway before that date MUST finish under its announced
rules. Completed elections and the terms of sitting members are unaffected.

The five-seat committee, staggered election schedule, one-year terms,
eligibility for reelection, candidate nomination process, conflict-of-interest
requirements, and association limits MUST continue. Except for replacing the
electorate and implementing coin weighting and ballot privacy as specified
here, existing election procedures MUST continue.

This is a change to a community process. Activation does not require a network
upgrade or changes to ZIP 214's funding-stream definitions. A rehearsal
SHOULD be held before the first election. Rehearsals MUST NOT select ZCG
Committee members or confer authority over ZCG funds.

## Legal implementation by FPF

FPF MUST arrange amendments, in suitable legal language, to the restricted-fund
agreements and other binding commitments through which it implements ZIPs
1015 and 1016. The amendments MUST require FPF to recognize the candidates
elected under this ZIP as the ZCG Committee members for the relevant seats
and terms, subject to the existing eligibility requirements and applicable
law. A separate ZCAP ratification MUST NOT be required.

Before the Effective Date, FPF MUST obtain advice from qualified Cayman
Islands counsel on the necessary amendments, consents, and corporate
approvals, and complete those steps. The binding instruments MUST identify
the parties entitled to enforce the election obligations and the applicable
enforcement procedure. This ZIP does not itself confer legal standing on
every ZEC holder or automatically amend an agreement or FPF's constitutional
documents.

FPF MUST publish confirmation of the completed legal arrangements and their
effect on committee selection, protecting privileged advice and confidential
information. If a necessary authorization cannot be obtained, FPF MUST report
the obstacle and the transition MUST be deferred pending its resolution.
Existing arrangements continue in the meantime; this does not authorize FPF
to replace elections with discretionary appointments.

## Changes to ZIP 1015

In "Terminology", replace the definition of "Zcash Community Grants" with:

> "Zcash Community Grants", also called "ZCG", refers to the committee
> selected under the ZIP "Coinholder Elections for Zcash Community Grants"
> to decide on the funding of grants intended to fund the Zcash ecosystem.

In "Zcash Community Grants (ZCG)", replace point 5 with:

> 5. ZCG awards are subject to approval by a five-seat ZCG Committee. From the
>    Effective Date, the ZCG Committee SHALL be selected by ZEC-weighted
>    coinholder approval voting under the ZIP "Coinholder Elections for Zcash
>    Community Grants", subject to its transition rules. Elections SHALL be
>    staggered to ensure continuity within the Committee.

Immediately after the paragraph requiring FPF to recognize the ZCG slice as
a Restricted Fund donation, insert:

> The contractual constraints on the ZCG Restricted Fund MUST include FPF's
> obligation to implement committee selection under the ZIP "Coinholder
> Elections for Zcash Community Grants". FPF MUST arrange the corresponding
> legal amendments and approvals before that ZIP's Effective Date. All other
> restrictions on the use and administration of ZCG funds continue in effect.
> These commitments remain subject to the Enforcement section of this ZIP.

Add references to this ZIP at those amendments and in the References section,
using its assigned identifier when available. These amendments take effect
under [Activation and transition]. Points 8 and 9, including ZCAP's or its
successor process's roles in determining the Discretionary Budget and member
compensation, MUST remain unchanged. Coinholder elections MUST NOT be
interpreted as replacing those separate roles.

## Changes to ZIP 1016

In "Non-requirements", replace the first bullet with:

> * Changes to ZCG or its governance, other than the committee-election
>   amendments specified in the ZIP "Coinholder Elections for Zcash Community
>   Grants", remain outside this proposal's scope.

In "Zcash Community Grants", append to the first paragraph:

> Those rules include the amendments to ZIP 1015 specified in the ZIP
> "Coinholder Elections for Zcash Community Grants", effective according to
> that ZIP's activation and transition provisions.

In "Administrative obligations and constraints", append to the first
paragraph:

> FPF MUST implement the committee-election amendments in the ZIP "Coinholder
> Elections for Zcash Community Grants", including the corresponding changes
> to its legally binding commitments governing ZCG funds.

After the paragraph that applies ZCG provisions to the Key-Holder
Organizations' administration of the CCF, insert:

> The committee-election amendments specified in the ZIP "Coinholder
> Elections for Zcash Community Grants" apply only to selection of ZCG
> Committee members and FPF's implementation of that selection. They do not
> change the Coinholder-Controlled Fund's Key-Holder Organizations, grant
> approval rules, voting thresholds, veto process, or legal arrangements.

Add references to this ZIP at those insertions and in the References section,
using its assigned identifier when available. All other provisions of ZIP
1016 continue in effect.


# Rationale

## Retaining a grants committee

Coinholder elections retain ZCG's existing division of work: an elected
committee evaluates applications, and FPF administers the program. Direct
coinholder voting on individual ZCG grants would be a broader redesign and
would duplicate aspects of the CCF. This proposal changes who chooses the
representatives while preserving what those representatives do.

## Preserving approval voting

Approval voting is already used for ZCG elections. [^zcg-december-2025]
Weighting approvals by ZEC preserves the ability to support multiple
candidates without splitting voting weight among them. The CCF's minimum
participation threshold applies to the election as a whole. Once quorum is
met, the approval totals determine the order in which candidates fill seats.

FPF published the June 2026 voting window when it opened nominations.
[^zcg-june-2026-nominations] The same practice fits the staggered election
calendar and gives FPF room to accommodate any voter eligibility cutoff.

## Concentration and participation

Coin weighting gives larger holders more influence, and a sufficiently large
participating holder could determine all seats being contested. It does not
provide one-person-one-vote representation or guarantee decentralization.
Depending on the voting rules, temporarily borrowed balances can count and
custodians may vote without reflecting each beneficial owner's preference.
These are tradeoffs of the proposed electorate, not problems eliminated by
ballot privacy. Public nominations, staggered terms, and existing committee
constraints remain useful but do not remove those risks.

The applicable voting rules can limit which holdings qualify and how voters
prepare to participate. Adequate notice matters to participation. Quorum and
failure rules need to balance legitimacy against the risk of leaving seats
unfilled.

## Express amendments and legal commitments

ZIP 1015 already permits a successor selection process, but leaves ZCAP
selection as an option. An express amendment makes the replacement electorate
unambiguous. Updating ZIP 1016 ensures that its continuation of ZIP 1015's
obligations carries the same rule forward.

The legal arrangements are necessary to make FPF's obligation executable
under the restricted-fund framework. The proposal retains the existing
Enforcement provision; it does not implement automatic on-chain enforcement
or alter funding streams. The distinction between process adoption and
contractual implementation is essential to the intended binding effect.


# Open questions

* How are tied scores at the seat boundary, zero-support candidates,
  insufficient eligible candidates, and elections that are interrupted or
  fall short of quorum handled while preserving the existing terms and cadence?
* Which FPF agreements and corporate instruments need amendment, whose
  consent is required, and who can enforce the revised election obligations?
* What Effective Date allows the legal work, independent security and privacy
  review, wallet preparation, and rehearsal to finish before nominations open?


# References

[^BCP14]: [Information on BCP 14 — RFC 2119 and RFC 8174](https://www.rfc-editor.org/info/bcp14)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-zcg]: [ZIP 1015: Zcash Community Grants (ZCG)](zip-1015.rst#zcash-community-grants-zcg)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zcg-june-2026]: [Zcash Foundation: ZCAP Poll Now Open — ZCG Election, June 2026](https://forum.zcashcommunity.com/t/zcap-poll-now-open-zcg-election-june-2026/56156)

[^zcg-june-2026-nominations]: [FPF: Zcash Community Grants Nominations Now Open for June Election](https://forum.zcashcommunity.com/t/zcash-community-grants-zcg-nominations-now-open-for-june-election/55720)

[^zcg-december-2025]: [FPF: ZCAP SIV Poll — ZCG Elections, December 2025](https://forum.zcashcommunity.com/t/zcap-siv-poll-zcg-elections-open-now/53685)
