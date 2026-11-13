    ZIP: Unassigned
    Title: ZCG Treasury Committee, Budget, and Hedging Plan
    Owners: Blake Benthall (emersonian) <e@emersonbenthall.com>
    Status: Draft
    Category: Process
    Created: 2026-11-08
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/zip-establish-the-zcg-treasury-committee/59048>
    Pull-Request: <https://github.com/zcash/zips/pull/1453>
    Updates: 1015


# Terminology

The key words "MUST", "MUST NOT", "SHALL", "SHOULD", and "MAY" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they
appear in all capitals.

The terms "Zcash Community Grants" (or "ZCG"), "ZCG Committee", "Financial
Privacy Foundation" (or "FPF"), "Autonomous Entities", "Zcash Community
Advisory Panel" (or "ZCAP"), and "Discretionary Budget" in this document are to
be interpreted as defined or used in ZIP 1015 [^zip-1015]. In this ZIP the ZCG
Committee is also called the grants committee, to distinguish it from the
Treasury Committee.

The terms "Coinholder-Controlled Fund" and "Key-Holder Organizations" in this
document are to be interpreted as described in ZIP 1016 [^zip-1016].

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [^protocol-networks].

"ZEC" refers to the native currency of Zcash on Mainnet.

The terms below are to be interpreted as follows:

ZCG Funding Stream

: Any funding stream whose recipient is FPF, or a successor administrator, for
  the use of Zcash Community Grants. At the time of writing these are
  `FS_FPF_ZCG` [^zip-1015-funding-streams] and `FS_FPF_ZCG_H3` [^zip-0214]
  [^zip-1016-zcg]. The term includes any later funding stream defined for the
  same purpose, under any name.

Accrued ZCG Funds

: All of the following:

  1. each amount paid to a recipient address of a ZCG Funding Stream, from the
     block in which the payment is mined;
  2. each amount donated or otherwise contributed to FPF, or a successor
     administrator, for the use of Zcash Community Grants, from the time it is
     received;
  3. each amount returned to the ZCG program, such as an unspent grant
     tranche, a recovered grant payment, or an unspent part of the
     Discretionary Budget; and
  4. all assets that any of the above is converted into or earns, including
     fiat currency, stablecoins, other digital assets, deposits, interest,
     yield, and the proceeds of any hedging position.

  Funds remain Accrued ZCG Funds for as long as they are held, in whatever
  account, wallet, custodian, or asset they are held. They cease to be Accrued
  ZCG Funds only when paid out for a grant or an administration expense under
  the Reference Text.

Reference Text

: The section "Zcash Community Grants (ZCG)" of ZIP 1015 [^zip-1015-zcg], as
  amended from time to time.

Accrual Rate

: The share of the block subsidy, or of any other issuance defined by the
  consensus rules, that is paid to ZCG Funding Streams, together with the start
  and end heights of those streams.

Treasury Committee

: The ZCG Treasury Committee established under
  [ZCG Treasury Committee](#zcg-treasury-committee).

Treasury Decision

: A decision of a kind listed in
  [Treasury Decisions](#treasury-decisions).

Grant Decision

: A decision of a kind listed in [Grant Decisions](#grant-decisions).

Program Budget

: The budget for the ZCG program set by the Treasury Committee under
  [Program Budget](#program-budget).

Treasury Plan

: The ten-year budget, treasury policy, and hedging strategy described in
  [Treasury Plan](#treasury-plan).

Activation Date

: The date on which this ZIP becomes Active under ZIP 0 [^zip-0000].


# Abstract

This ZIP changes how Zcash Community Grants (ZCG) manages its funds.

ZCG is required to form a separate Treasury Committee of at least three people.
Only the Treasury Committee may buy, sell, or convert ZEC, hedge, or set
budgets. The ZCG grants committee makes grant decisions only, and no person may
sit on both committees. ZCAP selects every member for a one-year term, sets
their pay, and can remove a member by a two-thirds vote. Until the Treasury
Committee is formed, the grants committee may not decide to buy or sell ZEC.

The Treasury Committee must publish a ten-year budget, a treasury plan, and a
strategy for hedging the risk of a fall in the price of ZEC by 31 March 2027,
and update them every year.

This ZIP does not decide whether funds already held by ZCG can be taken by a
later ZIP.

The ZIP has privacy implications for the disclosure of treasury addresses,
trades, and the personal holdings of committee members, which are discussed
below.


# Motivation

ZCG's balance is held largely in ZEC, while many grant obligations are
understood by grantees in US dollar terms. The ZCG Funding Stream is scheduled
to end at the third halving (Mainnet height 6132390 under ZIP 214 Revision 3
[^zip-0214], expected in late 2028), and could end sooner. A fall in the price
of ZEC can therefore reduce ZCG's ability to fund work by a large fraction
within months, with no change to any ZIP.

At the time of writing, the ZCG Committee both chooses grants and decides, with
FPF, how ZCG's funds are held and when ZEC is sold. These are different skills,
and combining them creates conflicts: a committee under pressure to fund a
popular grant may sell ZEC at a poor time, and a committee that decides when
ZCG sells ZEC has information that could be misused. ZCG also does not publish
a multi-year budget, a treasury policy, or a hedging policy.

ZCG holds funds that grantees and the community rely on over many years, and
it has a matching duty to manage them well over that period. A separate committee
with its own members, a published plan, and clear limits on what each committee may decide is intended
to meet that duty.


# Privacy Implications

Publishing treasury addresses, viewing keys, or detailed trade records lets
anyone link ZCG's holdings and movements over time. This is intended, since the
community needs to verify how Accrued ZCG Funds are managed, but it can
also reveal ZCG's counterparties, the timing of its trades, and, through grant
payments, information about grantees. Publishing planned trades before they are
executed could also allow others to trade against ZCG.

Holding ZEC in shielded pools improves the privacy of ZCG and its grantees but
makes public verification depend on ZCG choosing to publish viewing keys or
attestations.

Disclosure of the personal ZEC holdings of Treasury Committee members, which
this ZIP requires in order to manage conflicts of interest, reveals sensitive
financial information about individuals.

The Specification addresses these trade-offs by allowing details of a trade to
be withheld until it has been executed, and by limiting personal disclosures
to what is needed to identify conflicts.


# Requirements

* Decisions about how ZCG's funds are held, converted, and hedged, and how much
  ZCG may spend, are made by a body separate from the body that chooses grants,
  with no overlapping members.
* While that separate body is being formed, the grants committee does not
  decide to buy or sell ZEC.
* A ten-year budget, treasury plan, and ZEC-depreciation hedging strategy are
  published by 31 March 2027 and kept current.
* Converting or hedging Accrued ZCG Funds is possible without being treated as
  a transfer out of the restricted fund.


# Non-requirements

* This ZIP does not set or change the rate at which funds accrue to ZCG.
* This ZIP does not decide whether funds already accrued to ZCG may be taken by
  a later ZIP, network upgrade, or vote.
* This ZIP does not change how the ZCG Committee is selected, or FPF's ability
  to veto a decision that would violate Cayman Islands law under point 6 of the
  Reference Text.


# Specification

## Adoption

This ZIP takes effect on the Activation Date.

## Treasury management

Converting Accrued ZCG Funds from one asset to another, moving them between
accounts, wallets, or custodians controlled by the ZCG program's administrator,
and opening or closing hedging positions, do not take funds out of ZCG's
restricted fund, provided that:

* the resulting assets remain Accrued ZCG Funds and are accounted for in ZCG's
  restricted fund;
* the action is a Treasury Decision made by the Treasury Committee, or is
  permitted by
  [Interim restriction on the grants committee](#interim-restriction-on-the-grants-committee);
* after the first Treasury Plan is published, the action is consistent with the
  Treasury Plan then in effect; and
* the action is reported in ZCG's next quarterly report.

Reasonable transaction, custody, and hedging costs are administration expenses
under the Reference Text. A loss caused by a fall in the price of an asset, or
by closing a hedge at a loss, is not a misuse of Accrued ZCG Funds if the
action that led to it complied with this section.

## ZCG Treasury Committee

### Formation

ZCG SHALL establish a ZCG Treasury Committee no later than 45 days after the
Activation Date.

ZCAP, or any successor process that selects members of the ZCG Committee, MUST
select all members of the Treasury Committee, including its initial members,
using the same voting process it uses to select members of the ZCG Committee.
The ZCG Committee and FPF MUST NOT appoint Treasury Committee members.

The initial members SHALL adopt the Treasury Committee's charter, and publish
it on the Zcash Community Forum, within 30 days after they are selected.

### Membership

The Treasury Committee MUST have at least three members.

No person SHALL be a member of both the ZCG Committee and the Treasury
Committee at the same time.

No person who is a member of the ZCG Committee on the Activation Date SHALL be
appointed to the Treasury Committee, even if they later leave the ZCG
Committee. Former members who left the ZCG Committee before the Activation
Date are eligible.

The restrictions on association with BP/ECC, ZF, and FPF in point 7 of the
Reference Text apply to the Treasury Committee in the same way as to the ZCG
Committee. A majority of Treasury Committee members MUST NOT have an
association, as defined in that point, with FPF.

Members SHOULD have relevant experience, such as in treasury management,
finance, risk management, or digital asset custody.

### Terms

Each member serves a term of one year, as for members of the ZCG Committee
under point 7 of the Reference Text. A member MAY be selected again for further
terms.

So that seats come up for selection at different times, ZCAP MAY give some of
the initial members a first term of six months. Every later term is one year.

A member MAY resign at any time by notice posted on the Zcash Community Forum.

A vacancy, however it arises, SHALL be filled by ZCAP for the rest of the
term, within 45 days after it arises.

### Charter

The charter MUST specify:

* quorum and voting rules;
* a personal trading policy meeting the requirements of
  [Conflicts of interest and personal trading](#conflicts-of-interest-and-personal-trading);
  and
* how the charter may be amended.

The charter MUST NOT conflict with this ZIP, and MUST NOT give the ZCG
Committee any power to remove Treasury Committee members, to direct Treasury
Decisions, or to amend the charter.

### Compensation

Treasury Committee members SHALL be paid for their work, at a rate set by ZCAP
or its successor process in the same way as compensation of ZCG Committee
members under point 9 of the Reference Text. Compensation is an administration
expense, and the rate SHALL be published.

### Removal

A Treasury Committee member MAY be removed before the end of their term only
by the process in this section.

Grounds. A member may be removed for:

* a material breach of this ZIP or the charter, including the disclosure and
  personal trading rules;
* acting outside the authority given by this ZIP;
* fraud, dishonesty, or a criminal conviction related to their role;
* missing three consecutive meetings, or more than half of the meetings in any
  six-month period, without good reason; or
* being unable to carry out their duties.

Motion. Any member of ZCAP, the ZCG Committee, or the Treasury Committee, or
FPF, MAY file a motion to remove a member. The motion MUST be posted on the
Zcash Community Forum, and MUST state the grounds and the facts relied on.

Response. The member named in the motion MUST be given at least 14 days after
the motion is posted to respond publicly before any vote opens.

Vote. ZCAP SHALL then vote on the motion, using the same voting process it
uses to select members of the ZCG Committee, over a period of at least seven
days. The member is removed if at least two-thirds of the votes cast are in
favor, and at least half of ZCAP's members vote. ZCAP SHALL publish the
result and the number of votes for and against.

Suspension. Where a motion alleges a breach of the personal trading rules, or
misuse of funds, a majority of the other Treasury Committee members MAY
suspend the member from all Treasury Decisions until the vote ends, and MUST
publish that they have done so.

Effect. A removed member leaves office when the result is published. They are
not eligible to be selected to the Treasury Committee or the ZCG Committee
for three years afterwards. Their seat is filled as a vacancy under
[Terms](#terms).

### Authority

Treasury Decisions made by the Treasury Committee are final and do not require
the approval of the ZCG Committee or FPF's board, but are subject to veto if FPF
determines that they would violate Cayman Islands law or FPF's reporting
requirements or other obligations, in the same way as ZCG Committee decisions
under point 6 of the Reference Text. FPF SHALL execute Treasury Decisions that
are not vetoed, and SHALL publish the reasons for any veto.

The Treasury Committee has no authority to use Accrued ZCG Funds other than as
the Reference Text permits, or to transfer them out of the ZCG program.

### Conflicts of interest and personal trading

Each Treasury Committee member MUST disclose, on appointment and in each
quarterly report, whether they hold, or have a financial interest in, ZEC or
financial instruments whose value depends on the price of ZEC, and the
approximate size of that holding in ranges set by the charter.

A Treasury Committee member MUST NOT trade ZEC, or instruments whose value
depends on the price of ZEC, while they know of a Treasury Decision that has not
yet been fully executed and disclosed, or within a period set by the charter
before and after such a decision.

A Treasury Committee member MUST recuse themselves from a Treasury Decision in
which they have a personal financial interest other than their general holding
of ZEC, such as an interest in a proposed counterparty or custodian.

### Transparency of the Treasury Committee

The Treasury Committee SHALL publish minutes of each meeting within 14 days of
the meeting. Details of a planned trade or hedge MAY be withheld from the
minutes until it has been executed, and SHALL be published no later than ZCG's
next quarterly report after execution.

## Separation of grant and treasury decisions

### Treasury Decisions

The following are Treasury Decisions:

* buying, selling, or converting ZEC or any other asset held as Accrued ZCG
  Funds, including the amount and timing of any sale or purchase;
* setting asset allocation and the size of any liquidity reserve;
* opening, adjusting, or closing a hedging position;
* selecting custodians, exchanges, banks, and other treasury counterparties,
  and, together with FPF, setting the custody and signing arrangements for
  Accrued ZCG Funds;
* setting the Program Budget; and
* preparing, adopting, and updating the Treasury Plan.

### Grant Decisions

The following are Grant Decisions:

* approving, rejecting, modifying, renewing, or terminating grants;
* issuing requests for proposals;
* setting and assessing grant milestones; and
* approving disbursements from the Discretionary Budget under point 8 of the
  Reference Text.

### Rules on separation

The ZCG Committee MUST NOT make Treasury Decisions.

The Treasury Committee MUST NOT make Grant Decisions, and MUST NOT make a
Treasury Decision for the purpose of favoring or disfavoring a particular grant
or applicant.

The ZCG Committee MUST NOT approve a grant, or a disbursement from the
Discretionary Budget, that would cause total commitments in a budget period to
exceed the amount set for that period in the Program Budget. The ZCG Committee
MAY ask the Treasury Committee to amend the Program Budget, and SHALL publish any
such request.

Whether a grant is denominated in ZEC or in another currency is a Grant
Decision, but the ZCG Committee SHALL follow any policy on grant denomination
set in the Treasury Plan.

## Interim restriction on the grants committee

From the Activation Date until the Treasury Committee is established, the ZCG
Committee MUST NOT make any decision to buy, sell, or convert ZEC, and MUST NOT
set or change any budget.

During that period, FPF MAY convert ZEC only to the extent needed to pay grant
installments and administration expenses that were approved before or during
that period and that fall due within the following 30 days. Such conversions
SHALL be made at or shortly before the time of payment, without discretion as
to timing, and SHALL be reported in ZCG's next quarterly report.

The ZCG Committee MAY continue to make Grant Decisions during that period.

## Program Budget

The Treasury Committee SHALL set a Program Budget for each calendar year,
stating the maximum total amount that may be committed in that year for:

* grants; and
* administration expenses, including the Discretionary Budget.

The Program Budget MUST provide for the Discretionary Budget and committee
compensation as determined by ZCAP under points 8 and 9 of the Reference Text.

The Treasury Committee SHALL publish the Program Budget, and any amendment to
it, on the Zcash Community Forum within 7 days of adopting it.

Until the first Program Budget is adopted, no budget limit under this ZIP
applies to Grant Decisions.

## Treasury Plan

### Deadline

The Treasury Committee SHALL publish the Treasury Plan on the Zcash Community
Forum and on the ZCG website no later than 31 March 2027. If the Treasury
Committee is established later than 30 January 2027, the deadline is instead
60 days after it is established.

The Treasury Committee SHOULD publish a draft of the Treasury Plan for comment
at least 21 days before publishing the final version, and SHOULD respond
publicly to substantive comments.

FPF SHALL provide the Treasury Committee with the financial information,
custody details, and professional support that it reasonably needs to prepare
the Treasury Plan. The cost of independent financial or legal advice for this
purpose is an administration expense.

### Ten-year budget

The Treasury Plan MUST include a budget for each calendar year from 2027 to
2036 inclusive that:

1. states the balance of Accrued ZCG Funds by asset, with its value in ZEC and
   in US dollars, as of a stated recent date;
2. projects income under at least the following Accrual Rate scenarios:
   * the ZCG Funding Stream continues to its scheduled end at Mainnet height
     6132390 and is not renewed;
   * the ZCG Funding Stream is renewed after that height at its current
     percentage of the block subsidy; and
   * the ZCG Funding Stream ends at the first network upgrade after the
     Treasury Plan is published;
3. considers at least three ZEC price scenarios, one of which assumes that the
   price of ZEC falls by at least 75% from its price at the time the Treasury
   Plan is prepared and does not recover during the budget period;
4. sets out planned spending by category, including at least major grants,
   smaller grants and community programs, requests for proposals, and
   administration (including the Discretionary Budget, committee compensation,
   and treasury costs);
5. shows existing commitments separately from planned new spending;
6. states the expected runway in each scenario; and
7. states the minimum spending needed to keep the ZCG program operating, and
   how long existing Accrued ZCG Funds alone could sustain it.

### Treasury policy

The Treasury Plan MUST include a treasury policy that specifies:

1. target ranges for holdings in ZEC, fiat currency, stablecoins, and other
   assets, with reasons, and a minimum low-risk liquidity reserve sufficient
   to pay committed grants for a stated period;
2. custody and key management arrangements, including signing thresholds and
   backups, consistent with the "Security precautions" section of ZIP 1016;
3. whether ZEC is kept in shielded pools, and how the community can verify
   balances (for example by viewing keys or periodic attestations);
4. limits on exposure to any single bank, custodian, exchange, stablecoin
   issuer, or other counterparty;
5. confirmation that Accrued ZCG Funds will not be lent to related parties,
   pledged for unrelated obligations, or used for speculative trading, and
   that leverage will be used, if at all, only within a hedge described in the
   hedging strategy;
6. whether grants are denominated in ZEC, in US dollars, or a mix; and
7. how treasury actions will be reported in ZCG's quarterly reports and
   dashboard.

### Hedging strategy

The Treasury Plan MUST include a strategy for managing the risk that a fall in
the price of ZEC leaves ZCG unable to meet its commitments. The strategy MUST:

1. measure ZCG's exposure: the gap between its ZEC holdings and its
   obligations fixed in other currencies, now and over the budget period;
2. describe the methods to be used, which MAY include scheduled conversion of
   income, a low-risk reserve matched to committed grants, denominating some
   grants in ZEC, put options or collars, or other methods, with each method's
   expected cost, counterparty and custody risks, legal constraints, and
   likely effect on the ZEC market;
3. set limits on the size and type of positions, so that no position increases
   ZCG's overall exposure to the price of ZEC;
4. set a schedule or triggers for review and rebalancing; and
5. explain how it balances reducing risk against keeping ZCG's interests
   aligned with the success of ZEC.

### Updates and reporting

The Treasury Committee SHALL review the Treasury Plan at least once a year, and
SHALL publish an updated Treasury Plan, extended so that it covers the next ten
calendar years, no later than 31 March of each year from 2028.

Each ZCG quarterly report required by ZIP 1015 SHALL include:

* the balance of Accrued ZCG Funds by asset, with its value in ZEC and in US
  dollars;
* the treasury actions taken in the quarter and their results; and
* actual commitments and spending compared with the Program Budget, with an
  explanation of any material difference.

### Status of the Treasury Plan obligations

The obligations in [Program Budget](#program-budget) and
[Treasury Plan](#treasury-plan) are added to the obligations that FPF accepts on
behalf of ZCG under the section "Transparency and Accountability" of ZIP 1015
[^zip-1015-transparency].

## Enforcement

Any member of the community MAY publicly report a suspected breach of this ZIP.
FPF or the committee concerned SHALL respond publicly within 30 days.

A breach of this ZIP by FPF is a violation of FPF's obligations under ZIP 1015,
to which the enforcement provisions of ZIP 1015 apply
[^zip-1015-enforcement].

## Changes to ZIP 1015

In the section "Zcash Community Grants (ZCG)", after the paragraph beginning
"FPF SHALL be contractually required to recognize the ZCG slice of the Dev Fund
as a Restricted Fund donation", insert:

> Treasury management decisions for these funds, including any decision to buy
> or sell ZEC and the setting of budgets, are made by the ZCG Treasury
> Committee as specified in ZIP [this ZIP]. The ZCG Committee MUST NOT make
> such decisions.

In the section "Transparency and Accountability", add to the list of
obligations:

> * Publication and annual update of a Program Budget and of a ten-year budget,
>   treasury plan, and ZEC-depreciation hedging strategy, as specified in
>   ZIP [this ZIP].

## Testnet-specific considerations

This ZIP has no effect on Testnet. Testnet funds are not Accrued ZCG Funds.


# Rationale

## Rationale for allowing conversion and hedging

Read literally, a rule that accrued funds may not be moved for any purpose other
than grants could prevent ZCG from converting ZEC to pay a grant denominated in
US dollars, or from hedging. The ZIP therefore treats any action that keeps the
value inside the restricted fund as treasury management, and requires the
policy governing it to be published.

## Rationale for a separate Treasury Committee

Separating the people who choose grants from the people who decide when to sell
ZEC reduces the risk that grant pressure drives poorly timed sales, and limits
the number of people with advance knowledge of ZCG's trades. It is a common
arrangement in endowments and foundations, where an investment or finance
committee is distinct from the program committee. ZCAP selects every
member, including the first ones, so that the grants committee never chooses
the people who decide when its funds are sold. Members serve one-year terms,
are paid at a rate ZCAP sets, and can be removed only by a two-thirds ZCAP
vote after public charges and a chance to respond, as for any other role that
handles this much money.

The interim restriction prevents the grants committee from making large
discretionary sales or purchases while the new committee is being formed. The
narrow exception for conversions needed to pay approved grants is included so
that grantees are not left unpaid during that period.

## Rationale for the deadline

A deadline of 31 March 2027 allows time to form the Treasury Committee and hold
a comment period on a draft plan, and puts the first Treasury Plan in place well
before the scheduled end of the ZCG Funding Stream in late 2028.


# Open questions

* Is 45 days long enough for ZCAP to select the initial members, or should the
  window be 60 days?
* Should a community petition, for example by a set number of Forum members,
  also be able to start a removal motion?
* Should the size of the Discretionary Budget move from ZCAP to the Treasury
  Committee, given that the Treasury Committee sets the Program Budget?
* Is the 30-day exception for conversions needed to pay approved grants during
  the interim period acceptable, or should all conversions wait for the
  Treasury Committee?
* The 31 March 2027 deadline can be met without the 60-day extension only if
  this ZIP becomes Active by mid-December 2026. Is that realistic?


# References

[^BCP14]: [Information on BCP 14, "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0000]: [ZIP 0: ZIP Process](zip-0000.rst)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Zcash Community Grants (ZCG)](zip-1015.rst#zcash-community-grants-zcg)

[^zip-1015-transparency]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Transparency and Accountability](zip-1015.rst#transparency-and-accountability)

[^zip-1015-enforcement]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Enforcement](zip-1015.rst#enforcement)

[^zip-1015-funding-streams]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Funding Streams](zip-1015.rst#funding-streams)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-1016-zcg]: [ZIP 1016: Community and Coinholder Funding Model, Zcash Community Grants](zip-1016.md#zcash-community-grants)
