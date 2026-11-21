    ZIP: Unassigned
    Title: Capping the Treasuries of Zcash Community Grants and the Coinholder-Controlled Fund
    Owners: T. S. Felstead <vaspholdings@privat.is>
    Credits: Julian (Zcash Community Forum)
    Status: Draft
    Category: Process
    Updates: 1016
    Created: 2026-11-15
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/1464>
    Pull-Request: <https://github.com/zcash/zips/pull/1466>


# Terminology

The key words "MUST", "SHALL", "SHOULD", "SHOULD NOT" and "MAY" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they
appear in all capitals.

The terms "Zcash Community Grants" (or "ZCG"), "ZCG Committee" and "Deferred Dev
Fund Lockbox" are to be interpreted as defined in ZIP 1015 [^zip-1015].

The terms "Coinholder-Controlled Fund" (or "CCF") and "Key-Holder
Organizations" are to be interpreted as defined in ZIP 1016 [^zip-1016].

"NSM" means the Network Sustainability Mechanism [^zip-0233] [^zip-0235].

"Programme" means either ZCG or the coinholder-directed grants programme funded
by the Coinholder-Controlled Fund.

"Spendable Treasury" means the funds a Programme can currently spend: for ZCG,
its treasury; for the CCF, the funds held by the Key-Holder Organizations on
its behalf, including those disbursed to them from the Deferred Dev Fund
Lockbox under ZIP 271 [^zip-0271]. It does not include funds in any lockbox
that can only be released by a consensus change. The CCF's 12% stream continues
to accrue to the Deferred Development Lockbox, so it is not part of the CCF's
Spendable Treasury until it is released.

"Measurement Date" means the last day of March, June, September and December.

"Reference Price" means the lower of the time-weighted average price of ZEC in
USD over the 182 days ending on a Measurement Date and the average over the
final 7 of those days, calculated as specified below.

"Committed Obligations" means payments a Programme has already approved but not
yet made, such as approved grants and milestones. It also includes the total
requested in any funding round whose vote has opened but not yet closed, so
that no transfer can pre-empt a decision already under way.

"Near-Term Obligations" means the part of a Programme's Committed Obligations
due to be paid within 24 months of a Measurement Date.

"Annual Spend" means the average yearly amount a Programme disbursed over the 24
months ending on a Measurement Date, or over its full history if that is
shorter, valued in USD at the time of each payment.

"Minimum Reserve" means USD 25,000,000 for ZCG and USD 37,500,000 for the
coinholder-directed grants programme, in the same 8:12 ratio as their funding
streams.

"Justified Reserve" means a Programme's Committed Obligations plus the greater
of its Minimum Reserve and two years of its Annual Spend less its Near-Term
Obligations.

"Measured Value" means the value of a Programme's Spendable Treasury on a
Measurement Date, calculated as specified below.

"Excess" means the amount by which a Programme's Measured Value exceeds its
Justified Reserve.

"Transfer Cap" means, for each Measurement Date, 50,000 ZEC for ZCG and 75,000
ZEC for the coinholder-directed grants programme. 50,000 ZEC is the one-time
transfer proposed for ZCG in the Future Dev and Legal Defense Fund ZIP
[^zip-1428]; 75,000 ZEC is the same amount in the 8:12 ratio of the funding
streams.


# Abstract

This ZIP applies one test to both grant programmes funded by the Zcash
Development Fund.

Each quarter, each programme works out what it needs: what it has already
committed to pay, plus a reserve based on its own spending, with a minimum in
proportion to its funding stream. Its spendable treasury is valued in USD at a
six-month time-weighted average price, or a recent average if lower. Anything
above what it needs is sent to
the Network Sustainability Mechanism, up to a cap of 50,000 ZEC for ZCG and
75,000 ZEC for the coinholder programme each quarter.

The test is the same for both programmes. Because their commitments and
spending differ, the amounts they may keep will differ too.

This ZIP does not change either funding stream, their expiry in November 2028,
or how either programme decides what to fund.


# Motivation

ZIP 1016 created two funds from the block subsidy until the third halving in
November 2028: 8% to Zcash Community Grants, and 12% to the Coinholder-Controlled
Fund.

The split dates from the first Dev Fund. ZIP 1014 [^zip-1014] divided 20% of
the block subsidy between the Electric Coin Company (7%), the Zcash Foundation
(5%) and Major Grants (8%), the programme now called ZCG. When that Dev Fund
ended in 2024, ZIP 1015 kept 8% for ZCG and sent the remaining 12% to a lockbox,
to encourage the development of a decentralised way of allocating it. ZIP 1016
kept the same 8% and 12%, and directed the 12% to the Coinholder-Controlled
Fund. The ratio reflects how the original 20% was divided, not an assessment of
what either programme needs.

The ZEC price has since risen sharply. Both funds now receive far more in USD
than anyone expected when ZIP 1016 was adopted. Several proposals have
responded by changing ZCG's stream and treasury, including a fixed transfer of
ZEC to the NSM regardless of price. None applies the same test to the
Coinholder-Controlled Fund, which receives the larger stream.

ZCG itself first proposed reducing the funding of both programmes, with the
difference going to the NSM, then withdrew the proposal so that the community
could decide through Zcash's governance process [^zcg-plan].

If a higher price makes 8% too much, it makes 12% too much as well. Neither
programme should accumulate more money than it can justify. The question is not
which programme keeps its money, but how much each needs, judged the same way.

Equal scrutiny does not mean identical limits. The two programmes have different
mandates, commitments and spending patterns. This ZIP applies one method to
both, and lets the numbers differ where the facts differ.

One of the aims is governance minimisation. Less to decide, less to fight over.
A published formula, applied the same way every quarter, replaces repeated
one-off debates about the size of each treasury.


# Requirements

* The same method, price measurement and schedule apply to both Programmes.
* Work a Programme has already approved is protected.
* A Programme always keeps enough to pay its Committed Obligations and two years
  of its own spending, never less than its Committed Obligations plus its
  Minimum Reserve, and gives up less as the price falls.
* The minimum reserves are in the same 8:12 ratio as the funding streams,
  preserving the balance ZIP 1016 struck.
* The calculation can be checked by anyone using public data.
* Excess leaves the Programmes and returns to the protocol, not to any
  organisation or constituency.
* Funds in a lockbox are not moved automatically.
* Neither Programme's governance, grant process or funding stream is changed.


# Non-requirements

* Any change to the amount or duration of the ZCG or Coinholder-Controlled
  Fund funding streams defined in ZIP 1016.
* Any change to how either Programme decides what to fund.
* Any change to who elects the ZCG Committee or who votes on coinholder-directed
  grants.
* Deciding what happens to either Programme after November 2028.


# Specification

## Measured Value

On each Measurement Date, each Programme's Measured Value SHALL be calculated
as:

    Measured Value = (ZEC in the Spendable Treasury × Reference Price)
                   + (USD and USD-denominated stablecoins held, at face value)
                   + (other assets held, at market value)

## Justified Reserve

Each Programme's Justified Reserve SHALL be calculated as:

    Justified Reserve = Committed Obligations
                      + max(Minimum Reserve,
                            2 × Annual Spend − Near-Term Obligations)

Near-Term Obligations are subtracted so that payments already committed are not
counted twice: once as Committed Obligations, and again as part of the next two
years of spending.

The same formula SHALL be used for both Programmes.

## Reference Price

For each day, the daily price is the median ZEC/USD closing price across at
least three major exchanges with public price data.

The Reference Price SHALL be the lower of:

1. the mean of the daily prices over the 182 days ending on the Measurement
   Date; and
2. the mean of the daily prices over the 7 days ending on the Measurement Date.

The administrators of both Programmes SHALL agree and publish the list of
exchanges before the first Measurement Date. The same Reference Price SHALL be
used for both Programmes.

## Excess

If a Programme's Measured Value exceeds its Justified Reserve, the Excess,
converted to ZEC at the Reference Price, SHALL be sent to the NSM, up to that
Programme's Transfer Cap. Any Excess above the Transfer Cap remains in the
Spendable Treasury and is measured again on the next Measurement Date.

## Reporting and transfer

Within 60 days of each Measurement Date, the administrators of each Programme
SHALL:

1. publish the calculation of its Measured Value and Justified Reserve, with
   enough detail for anyone to check it, listing its Committed Obligations
   individually where they are already public and otherwise in aggregate; and
2. if there is any Excess, and transfers are possible under the Deployment
   section, send the amount due under the Excess section to the NSM in one or
   more transactions, and publish their transaction IDs.

For ZCG, the administrators are the organisation administering its treasury.
For the CCF, they are the Key-Holder Organizations.

For the CCF, the calculation SHALL also report the balance of any unreleased
lockbox funds allocated to it. These remain CCF funds, but are reported
separately and excluded from its Measured Value.

The calculation MAY be published as part of a Programme's regular quarterly
report. If there is no Excess, publishing the calculation is all that is
required.

## Holdings in USD

Each Programme SHOULD hold, in the currency in which the payments are owed:

1. its Committed Obligations; and
2. its expected spending over the next 12 months that is not already a
   Committed Obligation, estimated from its Annual Spend.

Amounts owed in USD SHOULD be held in USD or USD-denominated stablecoins, where
the Programme's administrators can lawfully do so. Amounts owed in ZEC MAY be
held in ZEC.

These holdings are part of the Justified Reserve, not an addition to it. They
provide the liquidity to pay what falls due. They count towards the Measured
Value at face value, or, for ZEC, at the Reference Price.

This builds on ZCG's existing practice of converting approved grant amounts to
USD, and of aiming to keep around 10% of its treasury in USD [^zcg-hedging].
Basing the holding on what each Programme owes, when and in which currency,
rather than on a percentage, keeps it meaningful as the ZEC price moves, and
fits each Programme's own payment pattern [^julian-reply].

Each Programme's published calculation need only state the USD value of these
holdings. How and where they are held MAY be kept confidential, and SHOULD be
made available to the independent checker described under Privacy and security
considerations.

## Lockboxes

Funds in the Deferred Dev Fund Lockbox, or in any other lockbox that can only be
released by a consensus change, are not part of a Spendable Treasury and SHALL
NOT be moved automatically under this ZIP.

Any future ZIP that releases lockbox funds to a Programme SHALL apply the test
in this ZIP to the amount released, so that no release takes a Programme above
its Justified Reserve.

## Expiry

This ZIP applies from its acceptance until the ZCG and Coinholder-Controlled
Fund funding streams defined in ZIP 1016 end in November 2028. What happens
after that is left to a future ZIP.


# Rationale

## What this ZIP is for

This ZIP does not aim to maximise transfers to the NSM. The ZCG stream is
intended "to fund independent teams entering the Zcash ecosystem, to perform
major ongoing development (or other work) for the public good of the Zcash
ecosystem" [^zip-1015]. The Coinholder-Controlled Fund "may be used to
distribute larger grants to ecosystem participants, or left at rest"
[^zip-1016]. Spending on those purposes is what each Programme is for. This ZIP
only removes funds that are excess to a Programme's needs at the Reference
Price.

ZIP 1016 also says that coinholders are not obligated to fund any grants and
MAY leave the funds at rest. This ZIP keeps that freedom for everything up to
the Justified Reserve: a Programme's Committed Obligations plus at least two
years of its own spending, or its minimum reserve if that is higher. Only funds
above that are sent to the NSM. To that extent, this ZIP updates ZIP 1016.

## Why the same test for both programmes

The concern raised about ZCG is that its treasury is growing faster than it can
usefully be spent, at a price nobody anticipated. That concern applies at least
as strongly to the Coinholder-Controlled Fund, which receives 12% of the block
subsidy to ZCG's 8%.

A limit that applies to one programme and not the other is not a response to
treasury size. It shifts influence between constituencies. This ZIP takes no
position on which constituency should control more funding. It only requires
that both be judged the same way.

## Why not identical limits

The two programmes are different. One funds work in advance; the other rewards
work already done. Their commitments, payment schedules and risks differ.
Identical limits would treat different things as if they were the same.

The fair approach is one method, applied to each programme's own facts. The
amounts may differ, but every difference can be traced to a published number.

## Why a reserve based on spending, with a minimum

A reserve of two years of actual spending lets each programme keep working
through a price fall without cutting grants already planned.

The minimum protects a programme whose spending is low or uneven, such as one
that pays grants retroactively. Without it, a quiet year would force a programme
to give up the funds it needs for the next.

The minimums are USD 25 million for ZCG, the illustrative figure suggested in
the current Dev Fund discussion [^twap-proposal], and USD 37.5 million for the
coinholder-directed programme. They are in the same 8:12 ratio as the funding
streams. Equal minimums would quietly shift the balance ZIP 1016 struck towards
ZCG. Proportional minimums leave it where it is. This ZIP does not reopen the
8:12 split.

Both figures are starting points for discussion. The 8:12 ratio keeps the
balance between the programmes, but it does not by itself show what either
needs. Open question 1 asks for evidence on that.

Spending is averaged over two years, so that one exceptional grant or a delayed
payment does not distort the reserve in either direction. Payments already
committed and due within those two years are counted once, as Committed
Obligations, and not again as future spending [^julian-reply].

## Why a cap of 50,000 ZEC

The Future Dev and Legal Defense Fund ZIP proposes that ZCG transfer 50,000 ZEC
to the NSM once, whatever the price. This ZIP takes that figure as the most
either programme gives up in any quarter, scaled 8:12 for the coinholder
programme.

So this ZIP is never harsher on ZCG in a single quarter than that proposal, and
is gentler when the price falls. Because the test repeats each quarter, a
treasury that is still above its reserve continues to be trimmed, gradually,
rather than growing again.

## Why a six-month average price

Both programmes pay for work priced in USD. A limit in ZEC would swing with the
price, as a fixed transfer of ZEC does: 50,000 ZEC is about USD 65 million at
USD 1,300, and USD 2.5 million at USD 50.

A six-month time-weighted average smooths out short-term spikes and makes the
measurement harder to manipulate.

It also lags. After a sharp fall, the six-month average will be higher than
the market price, so a Programme would be treated as richer than it is and
could be left below its Justified Reserve. Using the lower of the six-month
average and the average of the last seven days prevents this. A recent spike
cannot trigger a transfer either, because the six-month average is then the
lower figure. A seven-day average, rather than a single day's price, makes the
recent figure harder to push down to avoid a transfer.

## Why lockboxes are not moved automatically

Lockbox funds can only move through a consensus change, and are not available to
either programme today. Treating them as spendable would overstate what a
programme holds. Instead, this ZIP requires that any future release apply the
same test, so lockbox funds cannot be used to get around it.

## Why the NSM

Sending the excess to the NSM takes it out of circulation and returns it to the
protocol, where it is reissued over time. No organisation gains from it.

The NSM does not start reissuing funds straight away, so this is not about
paying miners sooner. It is about where excess goes: back to the protocol, not
to any organisation.

Sending excess to the NSM has costs, and Ian Miers has set them out
[^miers-nsm]. The NSM could become a reserve that a later upgrade redirects. It
adds to issuance from 2031, which complicates Zcash's issuance story. And it
ultimately pays miners. These costs are real. But redirecting NSM funds needs a
consensus change, the highest bar Zcash has, while ZEC held in a treasury can be
spent by whoever controls it. The alternatives are listed as an open question.

The same post proposes capping how much any one grantee can receive from the
dev fund. That addresses a different risk, and would complement this ZIP.

## Why the test ends in November 2028

The test exists because both funding streams keep adding to treasuries faster
than they can usefully be spent. When the streams end in November 2028, nothing
new flows in. A treasury can then only shrink as it is spent, and each
Programme will need what it holds to keep funding work until any successor
arrangement is agreed. Continuing to take funds away after that point would
risk leaving a Programme short, with no income to replace them.

## Why quarterly, and why no consensus change

Both Programmes already report and run funding rounds quarterly, so the test
can reuse figures they already produce. Sixty days after each Measurement Date
allows the calculation to be published with the regular quarterly report.

A consensus change would take longer, add code to every node implementation,
and be harder to adjust. The calculation needs none. Transfers need a way to
remove funds from circulation, which ZIP 233 would provide, but this ZIP does
not itself change the protocol. It places obligations on the organisations
that administer each Programme, in the same way as ZIP 1015 and
ZIP 1016 already do. It can be changed by a later ZIP if the figures prove
wrong.

If transfers are delayed, a Programme does not keep its excess. The test
measures the treasury balance, so any excess still held when transfers become
possible is measured and sent in the usual way, subject to the Transfer Cap.

## ZIP 233 and NU7.1

ZIP 233 [^zip-0233] provides a general-purpose mechanism for voluntarily
removing ZEC from circulation into the NSM. It depends on the extensible
transaction format in ZIP 248 [^zip-0248].

The published timeline for NU7.1 places transaction-format changes outside its
scope [^nu71-timeline]. nuttycom has proposed activating ZIP 248 in any network
upgrade that follows the current polling, partly because it would enable
ZIP 233 [^nu71-timeline]. Transfers under this ZIP depend on that mechanism, as
does the one-time transfer proposed in the Future Dev and Legal Defense Fund
ZIP. Any decision to deploy it should depend on complete specifications,
implementation readiness and thorough technical review.

## Interaction with other proposals

This ZIP can be adopted alone or alongside other proposals for the Dev Fund. If
another ZIP transfers funds out of a Programme or ends a funding stream, this
ZIP applies to whatever remains in that Programme's Spendable Treasury.

## Illustration

FPF has published ZCG's figures as of 18 November 2026 (block 3,586,555)
[^fpf-figures]: 95,170.30 ZEC, USD 8,448,418 in cash, and USD 1,922,171 of
approved but unpaid grant milestones, approved in USD and paid in ZEC. ZCG spent
USD 12,845,314 over the 24 full months to October 2026, so its Annual Spend is
about USD 6.42 million, and its USD 25 million minimum applies. Its Justified
Reserve is about USD 26.9 million.

All prices in this section are based on the dashboard price FPF used for its
snapshot, USD 946.61. Earlier drafts used a round USD 800 with figures from 12
November. They were updated so that every figure can be checked against one
published, dated source.

On those figures, the first quarterly transfer for ZCG would be:

| ZEC price | ZCG Excess | Sent to the NSM | Future Dev and Legal Defense Fund ZIP |
|---|---:|---:|---|
| USD 946.61 | about 75,700 ZEC | 50,000 ZEC (capped) | 50,000 ZEC, and the 8% stream |
| USD 473.31 | about 56,100 ZEC | 50,000 ZEC (capped) | 50,000 ZEC, and the 8% stream |
| USD 236.65 | about 17,100 ZEC | about 17,100 ZEC | 50,000 ZEC, and the 8% stream |

Under this ZIP, ZCG keeps its 8% stream and its Justified Reserve at every
price.

ZCG already meets the rule on holdings in USD. It holds USD 8.45 million,
against USD 6.42 million needed for its Committed Obligations and 12 months of
expected new spending at its 24-month average, or USD 8.44 million at its rate
over the last 12 months.

For the coinholder-directed programme, FPF reports 147,998.25 ZEC and no cash
[^fpf-figures]. That figure appears to include funds still in the Deferred Dev
Fund Lockbox: ZIP 271 released 78,750 ZEC, and the programme has paid out
7,887.13 ZEC, which suggests a Spendable Treasury of about 70,900 ZEC. Its
fourth-quarter 2026 round requested USD 5.87 million, which this ZIP treats as
committed until the vote closes. Its spending since launch annualises to about
USD 8.1 million, so its USD 37.5 million minimum applies. On those figures, the
programme would send about 25,000 ZEC to the NSM at USD 946.61, and nothing at
the lower prices. If more of its holdings are spendable, it would send more.

These figures are illustrative only, and MUST be recalculated from published
figures on the first Measurement Date. They are a dated snapshot, not a verified
surplus [^julian-reply].

### Over time

A quarterly cap is not directly comparable with a one-off transfer. The table
below compares the two proposals for ZCG over eight quarters, from FPF's
snapshot to the November 2028 halving, when the funding streams end. It assumes
ZCG's 8% stream adds about 13,150 ZEC a quarter; spending of USD 8.44 million a
year, the last 12 months' rate, including one-off security bounties;
Committed Obligations paid on FPF's expected dates and counted once; and ZEC
sold each quarter to keep Committed Obligations and 12 months of spending in
USD. The Reference Price is approximated by the lower of the previous six
months' average and the current price. Under the Future Dev and Legal Defense
Fund ZIP, the 50,000 ZEC transfer is made in the first quarter and the 8% stream
goes to its new lockbox from then on. Transfers to the NSM are treated as no
longer available to ZCG. The model behind these figures is published, so anyone
can check or rerun it [^model].

| Price path | Proposal | Sent to the NSM | ZCG's value in November 2028 | Remaining runway at USD 8.44 million a year |
|---|---|---:|---:|---:|
| Flat at USD 946.61 | This ZIP | about 165,000 ZEC | about USD 25.0 million | about 3.0 years |
| | Future Dev and Legal Defense Fund ZIP | 50,000 ZEC | about USD 34.3 million | about 4.1 years |
| Slide to USD 500 | This ZIP | about 136,300 ZEC | about USD 25.0 million | about 3.0 years |
| | Future Dev and Legal Defense Fund ZIP | 50,000 ZEC | about USD 15.6 million | about 1.8 years |
| Slide to USD 200 | This ZIP | about 80,200 ZEC | about USD 19.1 million | about 2.3 years |
| | Future Dev and Legal Defense Fund ZIP | 50,000 ZEC | about USD 4.1 million | about 0.5 years |

Under the Future Dev and Legal Defense Fund ZIP, about 105,200 ZEC of ZCG's
stream is also diverted to its new lockbox in every case. In the slide to USD
500, the price falls to USD 730, 650 and 575 over the first three quarters, then
stays at USD 500. In the slide to USD 200, it falls to USD 750, 500, 300 and
then 200 over the first four quarters, and stays at USD 200.

At a steady price, this ZIP takes more out of ZCG than a fixed transfer, because
it removes everything above the Justified Reserve, and ZCG ends with that
reserve. The difference is in a fall. This ZIP sizes each transfer to the price
at the time. In a slide to USD 500, ZCG never falls below its USD 25 million
minimum. In a slide to USD 200, transfers stop as the price drops, and ZCG keeps
more than two years of runway. A fixed transfer, with the stream redirected,
cannot adjust. In a slide to USD 500 it leaves ZCG with less than two years of
runway. In a slide to USD 200, ZCG runs out of ZEC in the sixth quarter, and
ends with about half the USD it needs for its commitments and next year's
spending.

The hardest case for this ZIP is a strong market followed by a sharp fall. If
the price rises to USD 1,900 over two quarters and then falls to USD 300, this
ZIP sends about 100,000 ZEC in the first two quarters. ZCG then falls to about
USD 18 to 19 million, below its USD 25 million minimum, for about a year, until
its stream rebuilds it. Its commitments are still met, and its runway does not
fall below two years, but transfers already made cannot be undone
[^julian-reply]. Open question 9 considers a fix.

The coinholder-directed programme is not shown, because its 12% stream accrues
to the Deferred Dev Fund Lockbox rather than its Spendable Treasury, and its
spendable holdings need to be confirmed first.


# Privacy and security considerations

The calculation uses only aggregate balances, public price data, total spending
and approved commitments, which each programme already publishes. It needs no
private information about individual grant recipients.

Committed Obligations are listed individually only where they are already
public. Others, such as security bounties whose recipients have not been named,
are given in aggregate, with the detail available to the independent checker
described below.

Sending ZEC to the NSM is irreversible. Each published calculation SHOULD be
checked by at least one party independent of the administering organisation
before any transfer is made. Transfers to the NSM are visible on chain, so
anyone can confirm that the amount sent matches the published calculation.

Each transfer requires the administrators to use their signing keys, and for
the CCF to coordinate a multisig signature. This adds a few signing events each
year to what the Programmes already do. Administrators SHOULD use the same key
management procedures as for grant payments.

A Programme could try to avoid a transfer by approving grants or raising its
spending just before a Measurement Date. Publishing the calculation, listing
Committed Obligations, and basing the reserve on a full year of actual spending
make this visible and limit its effect.

Funds that keep flowing to a Programme are held under its administrators' keys,
whereas funds in a protocol lockbox are held by no one until they are released.
This ZIP limits that exposure in a different way: each quarter, holdings above
the Justified Reserve leave the Programme's keys for the NSM. This applies to
both Programmes, so it bounds the amount held by the Key-Holder Organizations
as well as by ZCG's administrator, and it avoids a later release in which a
large lockbox balance moves into keys in a single transaction.

Prices are taken across several exchanges. Pushing the price up cannot trigger
a transfer, because the lower of the two averages is used, and would benefit no
individual party in any case. Pushing the seven-day average down to avoid a
transfer would mean holding the price down across several exchanges for a week;
it would be costly and visible, and would only delay the transfer to the
following quarter's measurement.


# Deployment

This ZIP needs no consensus change. It SHALL take effect on the first
Measurement Date at least 30 days after it is accepted, so that the list of
exchanges can be agreed and published first.

The quarterly calculation applies from that date. Transfers SHALL begin only
once ZIP 233 [^zip-0233], or another independently approved general-purpose
mechanism for removing funds from circulation into the NSM, is active and the
administrators are authorised to use it. Until then, the calculation is
published but no transfer is made, and no catch-up transfers accumulate.


# Open questions

1. Is two years of spending the right reserve, and are USD 25 million and
   USD 37.5 million the right minimums? The 8:12 ratio keeps the balance
   between the programmes, but does not by itself show what either needs. What
   evidence should set the minimums?
2. Should the Transfer Cap apply per quarter, as here, or in total?
3. What counts as a Committed Obligation? For example, should approved
   operating costs be included?
4. Which exchanges should set the Reference Price, and who checks the
   calculation?
5. Is quarterly the right frequency?
6. Is 12 months the right horizon for expected new spending held in the
   currency it is owed in, or should it be longer? bloxster has suggested
   holding two to three years of spending in USD.
7. Should excess go to the NSM, as here, be burned permanently, or stay locked
   until a later decision?
8. Is 24 months the right period for averaging spending? The coinholder-directed
   programme has a shorter history, so its average will rest on less data at
   first. Its spending is also lumpy: FPF reports that 98% of its payments to
   date went out on a single day, after the third-quarter 2026 round. While a
   Programme's minimum applies, its average does not change the result.
9. Should the test value ZEC at half the Reference Price when deciding whether
   there is an Excess? In a strong market followed by a sharp fall, transfers
   made at the high price can leave a Programme below its minimum after the
   fall. Testing at half price would still send most of the Excess when prices
   are high, but in the illustration it raises ZCG's low point after a crash
   from about USD 18 million to about USD 21 million, and after a fall to USD
   200 from about USD 17 million to about USD 23 million.


# Acknowledgements

Thanks to Julian for his analysis of ZCG's dashboard and quarterly figures
[^julian-figures], and for his review of this draft [^julian-reply]. His
comments led to the two-year averaging of spending, the removal of
double-counted commitments from the Justified Reserve, the comparison over time,
and basing USD holdings on when payments fall due and in which currency. His
downside case, a transfer after a strong market followed by a sharp fall, led
to open question 9.

Thanks to FPF for publishing ZCG's and the coinholder-directed programme's
holdings, obligations and spending, with the source of each figure
[^fpf-figures].


# References

[^BCP14]: [Information on BCP 14: "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0233]: [ZIP 233: Network Sustainability Mechanism: Removing Funds From Circulation](https://zips.z.cash/zip-0233)

[^zip-0235]: [ZIP 235: Network Sustainability Mechanism](https://zips.z.cash/zip-0235)

[^zip-0271]: [ZIP 271: Deferred Dev Fund Lockbox Disbursement](https://zips.z.cash/zip-0271)

[^zip-0248]: [ZIP 248: Extensible Transaction Format (draft, PR #1156)](https://github.com/zcash/zips/pull/1156)

[^nu71-timeline]: [Zcash Community Forum, "ZCG and the Dev Fund: Timeline for Proposals and Polling"](https://forum.zcashcommunity.com/t/zcg-and-the-dev-fund-timeline-for-proposals-and-polling/58906)

[^zcg-hedging]: [aquietinvestor, Zcash Community Forum, "Dev Fund: plans for top two proposal runoff", post 13, 18 July 2024](https://forum.zcashcommunity.com/t/dev-fund-plans-for-top-two-proposal-runoff/48332/13); [aquietinvestor, "Dev fund & stablecoins", post 14, 16 November 2025](https://forum.zcashcommunity.com/t/dev-fund-stablecoins/53183/14)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](https://zips.z.cash/zip-1014)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](https://zips.z.cash/zip-1015)

[^model]: [ZCG eight-quarter treasury model, Python script and README](https://gist.github.com/vaspholdings/de30a0ea297fc2e9e9e7cc776b43a487)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](https://zips.z.cash/zip-1016)

[^zcg-plan]: [Zcash Community Grants, Zcash Community Forum, "ZCG gets too much ZEC. Here's our plan to fix that.", 29 October 2026 (withdrawn)](https://forum.zcashcommunity.com/t/zcg-gets-too-much-zec-heres-our-plan-to-fix-that/58566)

[^twap-proposal]: [Dev Ojha (ValarDragon), Zcash Community Forum, 29 October 2026, post 28](https://forum.zcashcommunity.com/t/zcg-gets-too-much-zec-heres-our-plan-to-fix-that/58566/28)

[^zip-1428]: [Future Dev and Legal Defense Fund ZIP, PR #1428](https://github.com/zcash/zips/pull/1428)

[^julian-figures]: [Julian, Zcash Community Forum, post 122 in "ZCG and the Dev Fund: Timeline for Proposals and Polling", 14 November 2026](https://forum.zcashcommunity.com/t/zcg-and-the-dev-fund-timeline-for-proposals-and-polling/58906/122)

[^fpf-figures]: [FPF, Zcash Community Forum, "ZCG and Coinholder Grants: holdings, obligations and spending as of 19 November 2026", in "One ZIP for Both Taps: Fixing the Colossal Treasury Problem", 19 November 2026](https://forum.zcashcommunity.com/t/one-zip-for-both-taps-fixing-the-colossal-treasury-problem/59325)

[^julian-reply]: [Julian, Zcash Community Forum, reply in "One ZIP for Both Taps: Fixing the Colossal Treasury Problem", 16 November 2026](https://forum.zcashcommunity.com/t/one-zip-for-both-taps-fixing-the-colossal-treasury-problem/59325)

[^miers-nsm]: [Ian Miers (secparam), Zcash Community Forum, post 13 in "End ZCG and send its funds to the NSM", 26 October 2026](https://forum.zcashcommunity.com/t/end-zcg-and-send-its-funds-to-the-nsm/58515/13)

[^zooko-figures]: [Zooko Wilcox, Zcash Community Forum, post 4 in "The ZCG Lockbox: One Tap Off, the Bigger One Left Running"](https://forum.zcashcommunity.com/t/the-zcg-lockbox-one-tap-off-the-bigger-one-left-running/59027/4)
