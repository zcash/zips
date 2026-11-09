    ZIP: Unassigned
    Title: Update to ZIP 1015: ZCG Committee Members May Not Apply for Grants During Their Term
    Owners: Blake Benthall (emersonian) <e@emersonbenthall.com>
    Status: Draft
    Category: Process
    Created: 2026-11-08
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/zip-restriction-of-zcg-member-grant-applications/59046>
    Pull-Request: <https://github.com/zcash/zips/pull/1451>
    Updates: 1015, 1016


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

The terms "Zcash Community Grants" (or "ZCG"), "ZCG Committee", "Financial
Privacy Foundation" (or "FPF"), "Autonomous Entities", and "Discretionary Budget" in
this document are to be interpreted as defined or used in ZIP 1015 [^zip-1015].

The term "Coinholder-Controlled Fund" in this document is to be interpreted as
described in ZIP 1016 [^zip-1016].

The terms below are to be interpreted as follows:

Member

: A person who holds a seat on the ZCG Committee, whether elected, appointed,
  or filling a vacancy.

Term

: The period from the time a person becomes a Member until the time they stop
  being a Member, for any reason. Consecutive terms, including a term that
  follows reelection, are treated as one continuous Term.

ZCG Grant

: Any grant, contract, bounty, retroactive award, or other payment approved by
  the ZCG Committee and paid from funds administered by FPF for Zcash Community
  Grants. This includes an extension, renewal, increase, or new milestone of an
  existing grant. It does not include payments from the Discretionary Budget
  described in [Permitted payments to Members](#permitted-payments-to-members).

Associated Applicant

: For a given Member, any of the following:

  1. the Member;
  2. any organization of which the Member is an officer, director, or
     full-time employee, or in which the Member has a financial interest; and
  3. any immediate family member of the Member, or any organization associated
     with an immediate family member in the way described in item 2.

  "Financial interest" and "immediate family relationship" have the same
  meaning as in the definition of "Association" in ZIP 1015, item 7 of the
  section "Zcash Community Grants (ZCG)" [^zip-1015-zcg].

Application

: A request for a ZCG Grant, by whatever name or method it is made, including
  a response to a request for proposals and a request made on someone's behalf.


# Abstract

This ZIP bars members of the ZCG Committee from applying for, or receiving,
Zcash Community Grants while they sit on the Committee. The bar covers the
member personally, organizations they lead, work for full-time, or have a
financial interest in, and their immediate family. It also covers being named
on someone else's application as a team member, contractor, or other paid
participant.

Grants that a member already held before taking their seat may continue on
their existing terms, but cannot be extended, renewed, or increased during the
member's term. Pending applications are suspended until the term ends.
Committee compensation and expense reimbursement under ZIP 1015 are not
affected.

A grant approved in breach of this ZIP must not be paid. FPF reports breaches
publicly, and a member who knowingly breaches the rule is expected to leave
the Committee.

This ZIP has limited privacy implications. Members publish the organizations
they are associated with, but the names of their family members are not
published.


# Motivation

ZIP 1015 gives the five-seat ZCG Committee final authority over grants paid
from the 8% ZCG funding stream [^zip-1015-zcg]. The only conflict-of-interest
rule it sets for Members is that they recuse themselves when voting on
proposals where they have a financial interest, under the conflict-of-interest
policy of the FPF Board. Nothing in ZIP 1015 or ZIP 1016 [^zip-1016] stops a Member, or
an organization they run, from applying for a grant from the same Committee.

Recusal does not remove the conflict in a body this small. A Member who
recuses still sits with the other four Members on every other decision, often
over the same months in which their own application is under review. The other
Members have to judge a colleague's request knowing that the colleague will
later vote on theirs, or on grants that matter to them. Even when every Member
acts in good faith, coinholders and applicants cannot tell from the outside
that a decision was made on the merits. A grant to a sitting Member looks like
a grant to an insider, and that cost falls on the whole program.

A clear bar is easier to apply than case-by-case recusal. It tells candidates
in advance what they give up by joining the Committee, it needs no judgment
call about whether an interest is large enough, and it can be checked from
public records.


# Privacy Implications

This ZIP does not create any new disclosure duty for applicants. It does ask
each Member to publish the organizations they are associated with, and to tell
FPF confidentially when an immediate family member intends to apply. Members
already have to recuse when they have a financial interest, so they already
need to know and declare most of this.

The ZIP does not require the names of a Member's family members to be
published. Where a family relationship is the reason for a reported
breach, the public record identifies the Application and the Member but not
the family member. Readers may still be able to infer the relationship.


# Requirements

* A sitting Member cannot obtain a ZCG Grant for themselves, for an
  organization they are associated with, or for their immediate family.
* A Member cannot get around the rule by being named on someone else's grant.
* The rule is simple to check, and does not depend on a judgment about how
  large a conflict is.
* People who already hold grants are not forced to choose between their
  existing work and serving on the Committee, but cannot grow that work while
  they serve.
* Ordinary Committee compensation and expense reimbursement keep working.
* A grant made in breach of the rule is not paid.


# Non-requirements

* This ZIP does not set a cooling-off period after a Member's Term ends. (See
  [Open questions](#open-questions).)
* This ZIP does not change who selects the ZCG Committee, the length of a
  Term, or the limits on associations with BP/ECC, ZF, and FPF in ZIP 1015.
* This ZIP does not apply to grants from the Coinholder-Controlled Fund, which
  are decided by coinholder-amount voting rounds rather than by the ZCG
  Committee.


# Specification

## Bar on Applications during a Term

During a Member's Term:

1. an Associated Applicant of that Member MUST NOT submit an Application;
2. the ZCG Committee MUST NOT approve, and FPF MUST NOT pay, a ZCG Grant to an
   Associated Applicant of that Member, except as permitted in
   [Grants held before a Term begins](#grants-held-before-a-term-begins); and
3. the Member MUST NOT be named in any Application, or be paid from any ZCG
   Grant, as a team member, contractor, subcontractor, advisor, or in any other
   paid role.

The bar applies whoever the applicant is and however the Application is made,
including through an intermediary, a fiscal sponsor, or an Autonomous Entity
operating under FPF.

## Grants held before a Term begins

A ZCG Grant approved before a Member's Term began, to that Member or to one of
their Associated Applicants, MAY continue to be paid on its existing terms
during the Term. During the Term:

* the grant MUST NOT be extended, renewed, increased, or given new milestones
  or scope;
* the Member MUST recuse from every decision about that grant, including
  milestone approvals and reviews of whether funding should continue; and
* the Member MUST disclose the grant on the Zcash Community Forum within 14
  days after their Term begins.

A grant of indefinite duration that comes up for periodic review during the
Term, as described in item 2 of the section "Zcash Community Grants (ZCG)" of
ZIP 1015 [^zip-1015-zcg], MAY be continued at its existing level, but MUST NOT
be increased.

## Pending Applications

An Application from an Associated Applicant that is pending when a Member's
Term begins MUST be suspended, and MUST NOT be decided during the Term. The
applicant MAY withdraw it, or MAY ask for it to be considered after the Term
ends.

## Permitted payments to Members

This ZIP does not restrict:

* compensation paid to a Member for their work on the Committee under item 9
  of the section "Zcash Community Grants (ZCG)" of ZIP 1015 [^zip-1015-zcg];
  or
* reimbursement of a Member's reasonable travel expenses under item 8 of that
  section.

These payments MUST be approved and reported in the same way as other
payments from the Discretionary Budget.

## Disclosure by Members

Each Member MUST publish on the Zcash Community Forum, within 14 days after
their Term begins and again within 14 days after any change, a list of the
organizations that are their Associated Applicants under item 2 of the
definition. A Member MUST tell FPF, confidentially, when an immediate family
member or an organization associated with one intends to apply, so that the
Application can be refused before it is reviewed.

## Breaches

If an Application is found to breach this ZIP:

* the ZCG Committee MUST refuse it, or, if it has already been approved, MUST
  revoke the approval;
* FPF MUST NOT make any further payment on it; and
* FPF MUST report the breach in its next transparency report under ZIP 1015
  [^zip-1015-transparency], stating which Application was affected and which
  Member it related to, without naming any immediate family member.

A Member who knowingly breaches this ZIP, or who knowingly fails to disclose
an Associated Applicant, SHOULD resign from the Committee. FPF SHOULD seek to
recover any payment made as a result of a knowing breach.

## Changes to ZIP 1015

In the section "Zcash Community Grants (ZCG)" of ZIP 1015 [^zip-1015-zcg],
the following paragraph is added at the end of item 7:

> ZCG Committee members, the organizations they are associated with, and
> their immediate family members MUST NOT apply for or receive Zcash
> Community Grants during the member's term, except as provided in ZIP
> [this ZIP].

## Changes to ZIP 1016

In the section "Zcash Community Grants" of ZIP 1016 [^zip-1016], the
following sentence is added after the first paragraph, which makes the ZCG
funding stream subject to the rules in ZIP 1015:

> The restrictions on grants to ZCG Committee members in ZIP [this ZIP] also
> apply.

## Effective date

This ZIP takes effect on the date its Status becomes Active. It applies to
Applications submitted on or after that date, and to decisions made on or
after that date about earlier Applications and grants.

FPF SHOULD include the bar in its agreements with Members and in the terms of
ZCG Grants, so that it is enforceable under those agreements as well as under
this ZIP.


# Rationale

## Why a bar rather than recusal

The Committee has five seats, so one recusal removes a fifth of the
decision-makers, and the remaining four have a working relationship with the
applicant. Recusal handles a Member's interest in a single vote. It does not
handle the effect that an insider's application has on everyone else at the
table. A bar is also easier to explain to applicants and coinholders.

## Why organizations and family are included

A bar that covered only the Member personally could be avoided by applying
through a company the Member runs or partly owns, or through a relative.
ZIP 1015 already uses financial interest, officer and director roles,
full-time employment, and immediate family to define "Association"
[^zip-1015-zcg], so this ZIP reuses that definition rather than inventing a
new one.

## Why existing grants may continue

Many people suited to the Committee are active builders who may already hold
a grant. Forcing them to drop that work would shrink the pool of candidates
and could harm users who rely on it. Letting the grant run on its existing
terms, while freezing its size and requiring recusal, keeps the work going
without letting a Member's position help it grow.

## Why only the ZCG Committee

The ZCG Committee decides its own grants. Coinholder-Controlled Fund grants
are decided by coinholder-amount voting rounds, where Members have no special
role. Applying this bar to the Coinholder-Controlled Fund would be a separate
question, and is left open.


# Open questions

* Should the bar continue for a period after the Term ends, for example six
  or twelve months, to stop a Member arranging a grant to take effect after
  they leave?
* Is the organization test too wide? A Member who works full-time at a large
  organization would bar that whole organization from ZCG Grants. An
  alternative is to bar only organizations where the Member is an officer,
  director, or owner of more than a set share.
* Should a Member's Associated Applicants also be barred from grants from the
  Coinholder-Controlled Fund?
* Should a knowing breach remove the Member automatically, rather than only
  asking them to resign? ZIP 1015 has no removal procedure today.


# References

[^BCP14]: [Information on BCP 14, "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Zcash Community Grants](zip-1015.rst#zcash-community-grants-zcg)

[^zip-1015-transparency]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Transparency and Accountability](zip-1015.rst#transparency-and-accountability)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)
