    ZIP: Unassigned
    Title: Coinholder Grants for Ecosystem Work
    Owners: Giacomo Barbieri <hey@jaack.me>
    Status: Draft
    Category: Process
    Created: 2026-11-05
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/coinholder-grants-need-to-fund-ecosystem-work/58764>
    Updates: 1016

# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" are interpreted as
specified in BCP 14 [^bcp14] when they appear in all capitals.

The **Fund** and **Keyholders** are the Coinholder-Controlled Fund and its
Key-Holder Organizations under ZIP 1016. The **Administrator** is the existing
organization authorized to administer the coinholder grants program.
A **milestone** is a separately described and priced deliverable or completed
service period. An **assessor** is an Administrator staff member or independent
expert who evaluates delivery against the approved criteria.

# Abstract

This ZIP adds prospective grants alongside the coinholder program's
retroactive grants. Coinholders can approve defined work before delivery;
payment follows verified completion of the work or its milestones. It makes
eligibility for business development, developer relations, merchant onboarding,
education, regional communities, and ongoing support explicit alongside
technical contributions.

The existing Administrator verifies delivery, using independent experts where
needed. Keyholders execute payments under the existing custody and veto rules.
Compensation is denominated in USD and paid in ZEC at a published payment-time
exchange rate. Routine milestone payments require no additional funding vote.

The process includes review and payment deadlines, written reasons for adverse
decisions, reconsideration, and escalation of unresolved disputes. Public
records distinguish approved commitments from executed payments. Evidence can
be verified confidentially where public disclosure would expose users or
partners.

No changes to consensus, block-subsidy allocations, or voting weights are
proposed. Treasury backing remains open for community discussion; USD
denomination does not require cash reserves or a new custodian.

# Motivation

The retroactive-only program was deliberately ratified in 2025 [^ratification]
and remains explicit in the Q4 2026 call [^q4-call]. It requires contributors to
complete work before knowing whether they will be paid. This limits what
people without substantial reserves can undertake, including sustained
technical support, integration work, education, and merchant onboarding.

ZIP 1016 already anticipates scheduled payments, missed milestones, and
additional votes on continued funding [^zip-1016]. It also refers voters to
ZIP 1015's evaluation factors, including well-specified work, reasonable costs,
and ecosystem growth [^zip-1015]. This proposal supplies a prospective
application and verification process while clarifying access for ecosystem
work discussed in the motivating forum thread [^discussion].

Advance approval reduces uncertainty about the funding decision. Payment after
delivery still requires working capital between milestones and remains subject
to disputes, liquidity constraints, and existing veto rules. Eligibility also
cannot guarantee that voters will fund public goods. This proposal does not
replace a separately governed program or guarantee category allocations.

# Privacy Implications

Support records, partner confirmations, and adoption evidence can identify
users or expose commercial relationships. Confidential assessment and public
summaries can reduce disclosure, but introduce trust in assessors. Published
funding and payment metadata may still permit correlation. The process changes
no voting protocol or wallet behavior. Operational privacy requirements appear
in the Specification.

# Requirements

The design aims to provide:

* An actionable decision before delivery, with payment for verified work.
* Clear access for technical and nontechnical ecosystem contributions.
* USD compensation settled in ZEC and visible outstanding commitments.
* Accountable verification, timely decisions, and a route for disputes.
* Proportionate evidence, privacy protection, and prevention of double funding.
* Compatibility with existing voting, custody, and veto responsibilities.

# Specification

## 1. Scope and eligibility

ZIP 1016's voting thresholds, quarterly grant voting, minimum 30-day community
review, custody requirements, and veto grounds continue to apply. Once this
ZIP is activated, the Administrator MUST accept both retroactive and prospective
applications under the process below. Other operational rules remain applicable
unless expressly modified here.

Applications MUST demonstrate a specific benefit to Zcash and its ecosystem.
Eligible fields MUST explicitly include protocol work, security, infrastructure,
applications, developer tools, BD and integrations, DevRel, merchant onboarding,
education, regional communities, localization, accessibility, and ongoing support
or maintenance. Eligibility establishes a route to apply, not an entitlement
to funding. Coinholders retain discretion to reject proposals.

This ZIP creates no category quotas, startup advances, separate fund, standing
review committee, or new voting mechanism. It neither determines the outcome
of ZCG/ZAP proposals nor reallocates their grant-selection authority.

## 2. Applications and approval

A retroactive application MUST identify the completed contribution or service
period, requested compensation, attributable work, and evidence. A completed
period of an ongoing service MAY qualify; future periods MUST NOT be presented
as completed work. Existing retroactive denomination and payment rules remain
applicable.

A prospective application MUST specify:

* Its scope, intended benefit, delivery term, and completion evidence.
* Separately priced milestones and acceptance criteria, or one final
  deliverable where staged delivery is unsuitable.
* A total USD amount, milestone amounts, and delivery/payment schedule.
* The Administrator's verification procedure, required expertise, conflicts,
  and independent alternative if the Administrator itself is conflicted.
* Correction, reconsideration, dispute, expiry, and termination terms.
* Other funding for overlapping work and any confidential-evidence arrangements.

Criteria MUST distinguish deliverables within the contributor's control from
longer-term outcomes they aim to support. Immediate transaction growth MUST NOT
be the sole mandatory measure for every eligible contribution. Guidance MUST
include evidence examples suitable for technical work and ecosystem services.

Before voting, the Administrator MUST publish requested USD amounts, outstanding
USD commitments, and the Fund's ZEC balance with a valuation timestamp. A current
USD valuation of ZEC MUST NOT be described as a fixed reserve or a guarantee
of future payment capacity.

A passing vote and a confirmed commitment MUST be reported separately. A
commitment is confirmed only after an allocation under the applicable published
funding rules, acceptance of administrative duties, required agreements and
compliance checks, and publication of the approved scope, USD amounts, schedule,
and effective date. Work undertaken before confirmation remains at the
applicant's risk.

The agreement MUST make accepted milestones payable under the approved terms,
subject to existing veto rules. A proposal that passes without a full allocation
MUST be reported as uncommitted; its budget and scope MUST NOT be silently
reduced. A revised prospective award requires community review and another vote.
This does not change partial-funding rules for retroactive grants.

## 3. Verification and timing

The existing Administrator MUST verify delivery against the approved criteria
and obtain independent expert assessment where necessary. Assessors MUST
have their identity, relevant expertise, and material conflicts published before
assessment. Conflicted assessors MUST recuse themselves and be replaced. A
grantee MUST NOT certify its own entitlement to payment. Where the Administrator
itself is materially conflicted, the independent alternative identified in the
voted proposal MUST perform verification.

The following calendar-day deadlines are proposed defaults. Different deadlines
MAY apply only if expressly included in the grant terms approved by coinholders:

* Within 14 days of a milestone submission, the Administrator MUST issue an
  acceptance, correction request, or rejection against the approved criteria.
* Correction requests and rejections MUST identify the unmet criteria and
  evidence considered. Corrected submissions receive a new 14-day review period;
  assessors MUST NOT introduce new acceptance criteria through that process.
* Accepted milestones MUST be paid within 7 days of acceptance and satisfaction
  of the agreed payment prerequisites, subject to the existing legal and veto
  rules. Missing prerequisites MUST be identified promptly to the applicant.

Silence is not acceptance. The Administrator MUST report missed deadlines with
a reason and next action date; an applicant MAY invoke reconsideration over an
unexplained delay. Expert availability or internal administration MUST NOT
be used to reopen the merits of the approved grant.

After valid acceptance, the Administrator coordinates payment by Keyholders
under ZIP 1016. Routine milestone payments and assessor replacements under the
approved procedure MUST NOT require another coinholder vote. Assessment does
not confer payment-signing authority or override keyholder veto powers.

## 4. USD compensation paid in ZEC

Prospective awards MUST be denominated in USD and paid in ZEC. USD amounts
MUST be specified to whole cents. For a milestone owing $D$ USD at a payment-time
rate of $P$ USD per ZEC, the payment is $D/P$ ZEC, rounded up to the nearest
zatoshi (0.00000001 ZEC). The reference rate MUST be finite and positive;
otherwise the unavailable-price procedure applies. Exchange-rate changes alter
the ZEC delivered, not the approved USD amount, and require no new grant vote.
A fixed ZEC ceiling MUST NOT reduce the USD amount owed.

Before application review begins, the Administrator MUST publish a consistent
price source, valuation time, maximum quote age before broadcast, and fallback
procedure for unavailable prices or payment routes. Stale quotes MUST be
refreshed. Network and payment costs MUST be separately budgeted and MUST NOT
reduce the recipient's approved amount.

Keyholders MAY pay directly from existing ZEC holdings. This ZIP requires no
cash reserve, hedging, asset conversion, or new custodian. The Administrator
MUST track outstanding USD obligations separately from ZEC balances and
executed payments. Payment valuation does not guarantee a recipient's eventual
sale proceeds.

If funds are insufficient for a due payment, the Administrator MUST disclose
the shortfall and seek resolution through the applicable program process.
The USD obligation MUST NOT be silently reduced or converted into a fixed-ZEC
award. Treasury backing and management of price and liquidity risk remain open
for community discussion.

## 5. Reconsideration, disputes, and changes

An applicant MAY request reconsideration within 14 days of a rejection or
contested correction request, identifying the disputed criteria or evidence.
The Administrator MUST obtain a second assessment from an independent expert
who did not make the contested assessment. If the Administrator itself is
conflicted, the independent alternative identified in the voted proposal
handles reconsideration. The responsible verifier MUST issue a reasoned
reconsideration decision within 14 days of the request.

An applicant MAY escalate missed review, reconsideration, or payment deadlines
without waiting for a rejection. Administrative complaints MUST receive a
reasoned response within 14 days. A missed deadline creates no automatic
acceptance or transfer of funds.

Unresolved substantive disputes MUST be referred to Keyholders with both
assessments and the applicant's response for the next coinholder decision
eligible under the applicable community-review rules, consistent with ZIP
1016's further-vote process. The Administrator MUST publish the expected vote
cycle or explain why no cycle has been scheduled. A quarterly escalation may
therefore extend beyond the ordinary review deadlines.

Only the disputed portion pauses unless a veto or approved grant terms require
otherwise. Accepted, undisputed milestones remain payable. Existing legal
compliance and veto decisions are governed by ZIP 1016; reconsideration cannot
override them.

Increases in the USD award, material scope or acceptance changes, and renewals
MUST receive community review and a new coinholder decision. Administrative
variations expressly permitted by the voted terms need no new vote. Expiry
alone MUST NOT cancel an accepted unpaid milestone or extinguish a live dispute.
Closure reports MUST reconcile completed work, payments, and remaining or
terminated obligations.

## 6. Evidence, privacy, and overlapping funding

Public applications MUST provide enough information to assess the work and
its value. Underlying evidence MAY be reviewed confidentially where necessary,
with public attestations stating what was verified and material limitations.
Confidential arrangements MUST specify access, retention, and deletion duties
and collect no more information than needed.

The process MUST NOT require public disclosure of private keys, seed phrases,
individual wallet histories, or personal beneficiary information as adoption
evidence. Existing lawful recipient-compliance requirements remain applicable.

Applicants MUST disclose previous and pending funding for overlapping work.
The Administrator MUST check overlaps before commitment and payment. Duplicate
compensation for an already funded scope MUST NOT be paid unless expressly
disclosed and approved as a distinct reward. A milestone MUST NOT be paid twice
under one authorization.

## 7. Reporting

The Administrator MUST publish application formats, eligibility and evidence
guidance, grant status, outstanding USD commitments, and executed payment
records. Payment records MUST identify the USD amount settled, ZEC delivered,
reference rate and timestamp, and execution evidence consistent with privacy
obligations. Approval alone MUST NOT be reported as an executed payment.

Eligibility exclusions MUST receive written reasons. After each round, the
Administrator SHOULD summarize recurring application weaknesses without
attributing motives to anonymous voters or implying that eligibility ensures
approval.

## 8. Compatibility and deployment

This process change requires community acceptance of a change to the previously
ratified retroactive-only program. ZIP publication or an ordinary grant vote
alone does not activate it. Existing grants retain their approved terms.

The related process draft in PR #1112 [^process-draft] requires completed work.
Its owners and ZIP Editors will need to coordinate the prospective exception,
including references to a numbered successor if adopted before this proposal.

Before accepting prospective applications, the Administrator and Keyholders
MUST publish the ratification decision, first affected cycle, amended operative
documents, responsible and funded administration, grant and dispute procedures,
payment-rate method, and confirmation that governing agreements permit the
prospective commitments and scheduled payments. Existing custody and veto
responsibilities remain in force. No consensus-software activation is proposed.

# Rationale

Advance approval makes a conditional funding decision available before delivery;
an advisory poll alone would leave a further discretionary award decision after
the work. Milestone payments reduce how much a contributor must finance at once
without introducing startup advances.

Using the existing Administrator with independent expertise keeps verification
practical without a new committee or a quarterly vote on each payment. Written
criteria, recusals, second assessment, and escalation constrain judgment and
delay risks; they do not make assessment trustless. The proposed 14-day review
and 7-day payment periods provide a clear starting point for discussion while
allowing different timelines in the voted grant terms.

USD denomination makes the compensation amount predictable in dollars while
preserving payment through ZEC. The Fund may retain ZEC, leaving it exposed to
changes in the ZEC needed to meet its obligations. The conversion formula does
not itself guarantee solvency. This draft leaves treasury policy to discussion
rather than prescribe reserve assets or custody arrangements.

The forum discussion also raises an objection that process reform cannot
provide reliable public-goods funding if voters decline such work. Eligibility
clarity does not solve that willingness problem, and this ZIP establishes no
spending mandate or replacement for ZCG/ZAP.

# Questions for Community Discussion

* Are the proposed 14-day review, 7-day payment, and 14-day reconsideration
  periods practical, and which grants need different terms?
* What expert-selection and conflict procedures will make independent
  reconsideration credible without adding a standing committee?
* How should the Fund manage outstanding USD commitments against a ZEC treasury?
  This draft prescribes no reserve asset, custodian, or hedging policy.
* Which organization will undertake and have funding for the administrative
  workload beyond the present arrangement?
* What ratification route and timetable should apply, and how should this
  proposal be coordinated with PR #1112 and keyholder agreements?

# References

[^bcp14]: [BCP 14](https://www.rfc-editor.org/info/bcp14).

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md).

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst).

[^ratification]: [Zcash Coinholders Approve Retroactive Grants Program](https://shieldedlabs.net/zcash-coinholders-approve-retroactive-grants-program/), 4 September 2025.

[^q4-call]: [Q4 2026 Coinholder-Directed Retroactive Grant Program — Call for Proposals](https://forum.zcashcommunity.com/t/q4-2026-coinholder-directed-retroactive-grant-program-call-for-proposals/58598).

[^discussion]: [Coinholder grants need to fund ecosystem work](https://forum.zcashcommunity.com/t/coinholder-grants-need-to-fund-ecosystem-work/58764).

[^process-draft]: [Coinholder-Directed Retroactive Grants Program draft, PR #1112](https://github.com/zcash/zips/pull/1112). Draft in the sources inspected on 5 November 2026.
