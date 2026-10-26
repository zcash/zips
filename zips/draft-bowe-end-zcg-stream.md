    ZIP: Unassigned
    Title: Ending the ZCG Funding Stream in Favor of the NSM
    Owners: Sean Bowe <ewillbefull@gmail.com>
    Status: Draft
    Category: Consensus / Consensus Process
    Created: 2026-10-26
    License: MIT
    Updates: 207, 214, 237, 1016

# Terminology

The key words "MUST" and "MUST NOT" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet", "Testnet", "block subsidy", "funding stream", "coinbase
transaction", and "chain value pool balance" have the meanings given in the Zcash
Protocol Specification. [^protocol] The character § refers to sections of that
specification.

"Zcash Community Grants" ("ZCG") has the meaning given in ZIP 1015. [^zip-1015]

"Network Sustainability Mechanism" ("NSM") refers to the mechanism specified in
ZIP 237. [^zip-0237] The "NSM fund" refers to the balance called the "NSM Value
Balance" in that ZIP. The operation of the NSM fund is specified separately from
this funding allocation.

"Issued Supply" has the meaning given in § 4.17 ‘Chain Value Pool Balances’.
[^protocol-chainvaluepoolbalances]

All heights and indices introduced here are nonnegative integers. All subsidy
amounts and stream values are integer zatoshis in
$\{0, \ldots, \mathsf{MAX\_MONEY}\}$, where $\mathsf{MAX\_MONEY}$ is the monetary
bound defined in § 5.3 ‘Constants’. [^protocol-constants] One ZEC on Mainnet, or one
TAZ on Testnet, is 100,000,000 zatoshis.


# Abstract

This ZIP ends the Zcash Community Grants funding stream and redirects its
remaining 8% share of the block subsidy to the Network Sustainability Mechanism
for the rest of the stream's existing term. ZCG's accumulated resources allow
grant-making to continue from its existing treasury.

The redirected value is withheld from issuance and credited directly to the NSM
fund. This ZIP specifies the source, amount, and duration of those contributions;
their subsequent treatment is governed by the NSM specification.

This ZIP changes future subsidy allocations only. ZCG's existing assets and the
rules governing them are unchanged, and the 12% Coinholder-Controlled Fund
stream retains its existing allocation and duration. The ZEC supply cap,
historical block validity, and existing transaction formats are preserved.


# Motivation

ZCG has accumulated sufficient resources to continue its grant-making role
without an automatic share of each block subsidy. This ZIP therefore ends that
funding stream and directs its remaining allocation to the NSM.

## Existing resources

The public dashboard linked from ZCG's website reports 91,452.98 ZEC,
\$8,796,224 in USD, and \$2,417,165 in outstanding grant liabilities in the view
recorded for this proposal. [^zcg-dashboard] Valuing those holdings at explicit
prices gives:

| Assumed ZEC price | Reported holdings less reported grant liabilities |
| --: | --: |
| \$1,300 | \$125.3 million |
| \$1,000 | \$97.8 million |
| \$500 | \$52.1 million |

The valuations exclude future funding-stream receipts. [^financial-scenarios]

For comparison, the Financial Privacy Foundation (FPF) reported \$1,530,844 in
ZCG expenses for Q1 2026, equivalent to \$6.12 million on an annualized basis.
[^fpf-q1-2026] At an illustrative
\$10 million in annual spending, the balances above represent about 12.5 years
of spending at \$1,300 per ZEC, or 5.2 years at \$500. [^financial-scenarios]

## Continued inflows

At a block subsidy of 1.5625 ZEC and a 75-second block target spacing, the 8%
allocation is 144 ZEC per target-spaced day, or 52,560 ZEC per 365-day year.
At \$1,300 per ZEC, that is approximately \$187,200 per day or \$68.3 million
per year: more than eleven times the annualized Q1 expense figure.
[^stream-scenarios] NU7 deploys ZIP 218's 25-second block spacing and subsidy
rescaling, leaving this daily allocation approximately unchanged, apart from
integer rounding. [^zip-0259]

A fixed share of issuance increases in dollar value when ZEC appreciates,
regardless of the recipient's existing reserves, spending, or approved
commitments.

## Future allocations

ZIP 1016 provides distinct community and coinholder funding channels.
[^zip-1016] This ZIP preserves ZCG's authority over its existing resources and
the Coinholder-Controlled Fund's 12% stream. It favors coinholder decisions on
additional subsidy-funded grants over continued automatic accumulation by a
separate grants committee.

Continuing to add to a discretionary treasury increases the resources dependent
on its custody and governance arrangements. Ending further inflows limits that
exposure without changing control of funds already allocated.

The remaining allocation goes instead to the NSM, a protocol-defined mechanism,
through the stream's existing expiry.


# Privacy Implications

The redirected amount is derived from public consensus state and subsidy rules.
The redirection introduces no recipient addresses, notes, spending keys, or
participant identifiers. The proposal leaves transparent and shielded transaction
privacy properties unchanged.


# Requirements

* End automatic block subsidy payments to ZCG at activation without changing its
  existing treasury or the rules governing those assets.
* Redirect the remaining 8% allocation to the NSM fund through the stream's
  existing expiry, using the existing per-stream integer rounding rule.
* Specify the contributions from this stream, leaving the treatment of the NSM
  fund to its own specification.
* Preserve historical block validity, monetary bounds, and the existing formula
  for the miner's share of each block subsidy.
* Preserve the Coinholder-Controlled Fund stream and deferred pool arrangements,
  and avoid introducing transaction fields or address formats.


# Specification

Stream definitions and value accounting below are consensus requirements. The
amendments to ZIP 1016 are consensus-process requirements.

## Activation and dependencies

Let $A$ be this ZIP's activation height and $N$ be the NU7 activation height on
the relevant network. Let $S$ and $E$ be the inclusive start and exclusive end
heights of `FS_FPF_ZCG_H3` under ZIP 214, after applying any other consensus
changes effective at $A$, but before applying this ZIP. [^zip-0214]

NU7 deploys Revision 3 of ZIP 214, which preserves the start heights from
Revision 2 and moves the end heights to the third halving under ZIP 218's
25-second block spacing. [^zip-0218] If $N$ precedes the pre-NU7 third-halving
height $E_{75}$, the revised end height is $E = N + 3(E_{75} - N)$.
The pre-NU7 end heights are 4406400 on Mainnet and 4476000 on Testnet.
With the NU7 activation parameters currently specified in ZIP 259: [^zip-0259]

| Network | $N$ | $S$ | $E$ |
| :------ | --: | --: | --: |
| Mainnet | 3543405 | 3146400 | $13219200 - 2N$ |
| Testnet | 4465026 | 3536500 | 4497948 |

Revision 3 does not reactivate a stream that expired before NU7. This ZIP changes
the destination of the remaining allocation; its expiry is unchanged.

The activation parameters MUST satisfy $S < A < E$ and $N \leq A$ on each
network. The NU7 changes to funding streams, fee accounting, and the NSM Value
Balance MUST be effective at $A$.

All changes in this ZIP take effect together at $A$. Blocks before $A$ MUST
continue to be validated under their existing rules.

## Funding streams and recipients

In a new revision of ZIP 214, replace the exclusive end height of
`FS_FPF_ZCG_H3` with $A$ on each network. Its start height, fraction, and recipient
at every height before $A$ are unchanged. Its recipient list is the prefix of the
existing list of length $\mathsf{fs.NumRecipients}$, recalculated using the new
end height as specified in § 7.10 ‘Payment of Funding Streams, Deferred Lockbox,
and Lockbox Disbursement’, using the address-period calculation from Revision 2
of ZIP 207. [^protocol-fundingstreams] [^zip-0207] This calculation preserves
pre-NU7 indices, triples the remaining block count in the address period at
NU7 activation, and gives each subsequent period 105000 blocks.

The existing Mainnet recipient list includes the address change specified by
ZIP 2008. [^zip-2008] Apply that change before truncating the list, preserving
the prescribed recipient at every height before $A$.

Add the following funding stream on each network:

| Stream | Numerator | Denominator | Start height | End height |
| :----- | --------: | ----------: | -----------: | ---------: |
| `FS_NSM_H3` | 8 | 100 | $A$ | $E$ |

Extend the allowed recipient identifiers in ZIP 207 [^zip-0207] and § 7.10 with
the symbolic identifier $\mathsf{NSM\_FUND}$, distinct from
$\mathsf{DEFERRED\_POOL}$ and all address encodings. Every entry in
`FS_NSM_H3`'s recipient list is $\mathsf{NSM\_FUND}$; its list length and
recipient-index calculation use the same NU7 address-period rules. This
identifier has no associated payment address or spending key.

In ZIP 207's post-NU6 coinbase-output rule and the corresponding rule in § 7.10,
extend the exception for $\mathsf{DEFERRED\_POOL}$ to also exclude
$\mathsf{NSM\_FUND}$. Crediting the NSM fund is an accounting operation and
produces no coinbase output. Former ZCG recipient addresses retain their ordinary address
semantics, with no mandatory ZCG payment at or after $A$.

`FS_CCF_H3` retains its existing numerator, denominator, start height, end height,
and recipient identifiers. The deferred pool and its disbursement rules are
unchanged.

## Redirected amount

In § 7.8 ‘Calculating Block Subsidy, Funding Streams, Lockbox Disbursement, and
Founders' Reward’, [^protocol-subsidies] retain the existing definition of
$\mathsf{fs.Value}(h)$ for each funding stream, and add
$\mathsf{totalNSMOutput}(h)$: the sum of those values over active streams whose
recipient is $\mathsf{NSM\_FUND}$. This ZIP introduces only `FS_NSM_H3`, so:

$$
\mathsf{totalNSMOutput}(h) := \begin{cases}
\left\lfloor \dfrac{8 \cdot \mathsf{BlockSubsidy}(h)}{100} \right\rfloor,
& A \leq h < E \\
0, & \text{otherwise.}
\end{cases}
$$

Here $h$ is a block height and $\mathsf{totalNSMOutput}$ is a nonnegative
zatoshi-valued function with the bounds given in Terminology.
$\mathsf{BlockSubsidy}$ is the total block subsidy under the consensus rules in
effect at $h$, including ZIP 218's rescaling and ZIP 237's definition as
$\mathsf{ScheduledBlockSubsidy}(h) + \mathsf{AdditionalBlockSubsidy}(h)$.

The definition of $\mathsf{MinerSubsidy}$ continues to subtract the values of all
funding streams, including `FS_NSM_H3`. The 8% and 12% stream values MUST be
rounded down separately, as under the existing rules; their combined value MUST
NOT be calculated by rounding a single 20% allocation.

## Coinbase accounting

In § 7.1.2 ‘Transaction Consensus Rules’, [^protocol-txnconsensus] add
$\mathsf{totalNSMOutput}(h)$ to the definition of the coinbase transaction's
$\mathsf{totalOutputValue}$, in addition to its existing components, including
$\mathsf{totalDeferredOutput}(h)$. Retain the NU7 definition of
$\mathsf{totalInputValue}$ from ZIP 235: [^zip-0235]

$$
\mathsf{BlockSubsidy}(h) + \mathsf{MinerFees}(h) + \mathsf{totalDeferredInput}(h).
$$

Here $\mathsf{MinerFees}(h)$ excludes
$\mathsf{NSMFeeContribution}(h)$, the 60% of aggregate transaction fees
removed from circulation under ZIP 235, rounded down once per block.
That fee contribution is separate from this ZIP's subsidy contribution.

The requirement that $\mathsf{totalOutputValue}$ equal
$\mathsf{totalInputValue}$ continues to apply. [^zip-0236] A block whose coinbase
transaction fails this equality MUST be rejected. Consequently the value
claimable through coinbase outputs is reduced by exactly
$\mathsf{totalNSMOutput}(h)$; a miner cannot claim the redirected allocation or
choose a smaller deposit.

Crediting this stream's contribution to the NSM MUST NOT itself increase any
chain value pool balance or $\mathsf{IssuedSupply}$. The addition to
$\mathsf{totalOutputValue}$ is solely for coinbase value accounting and creates
no spendable output.

These rules apply to both version 5 and version 6 coinbase transactions, the
transaction versions retained by NU7. NU7 introduces no new transaction format.
[^zip-0259] No NSM field or transaction encoding is added by this ZIP.

## Crediting the redirected contributions

Extend ZIP 237's definition of the NSM Value Balance to include subsidy withheld
by this ZIP. In its amendment to § 4.17, retain the initialization at $N - 1$
and replace the recurrence branch, for $h \geq N$, with:

$$
\begin{aligned}
\mathsf{NSMValueBalance}(h) := {}& \mathsf{NSMValueBalance}(h - 1) - \mathsf{AdditionalBlockSubsidy}(h) \\\\
&+ \mathsf{NSMValueRemoved}(h) + \mathsf{totalNSMOutput}(h).
\end{aligned}
$$

Here $\mathsf{NSMValueRemoved}(h)$ retains its ZIP 237 meaning and includes ZIP 235's
$\mathsf{NSMFeeContribution}(h)$. Each redirected subsidy contribution MUST be
credited exactly once, in the block at height $h$, and MUST NOT also be included
in $\mathsf{NSMValueRemoved}(h)$. Since $\mathsf{totalNSMOutput}(h) = 0$ before $A$,
the recurrence is unchanged before this ZIP activates, including when $A > N$.

Arithmetic for the redirected contributions MUST be evaluated exactly without
overflow, including intermediate products and sums. A block that would produce
a stream value outside its specified bounds MUST be rejected. The existing chain
value pool and Issued Supply bounds remain in force. [^zip-0209]

Contributions MUST be accounted for on the validated chain. On a reorganization,
contributions from disconnected blocks MUST NOT be counted toward that chain's
deposits.

At and after $E$, this stream contributes zero to
$\mathsf{totalNSMOutput}$.

## Funding policy

In ZIP 1016's ‘Zcash Community Grants’ subsection, [^zip-1016] replace the funding
period with $[S, A)$. From $A$ through $E - 1$, the former ZCG allocation is
assigned to the NSM as specified above.

In the first paragraph of ZIP 1016's ‘Coinholder-Controlled Fund’ subsection,
replace the references to the duration and end height of the ZCG stream with
references to `FS_CCF_H3`'s own start and end heights under ZIP 214. Its 12%
allocation and existing duration are preserved independently of ZCG's cutoff.

This ZIP leaves ZCG's existing treasury and the rules governing it unchanged.

## Boundary cases and arithmetic examples

At $A - 1$, the existing ZCG stream is still in effect and the NSM stream has no
value. At $A$, the ZCG stream has ended and the NSM stream first takes effect.
The last height at which the NSM stream can have a nonzero value is $E - 1$.
There is no gap or overlap between the two allocations.

For a block in $[A, E)$ with no other funding streams or Founders' Reward, the
following examples give all amounts in zatoshis. Here $B$ is the total block
subsidy, $D$ is the NSM deposit, $C$ is the 12% CCF deposit, and $M$ is the miner
subsidy, excluding transaction fees and any deferred-pool disbursement.

| $B$ | $D = \lfloor 8B/100 \rfloor$ | $C = \lfloor 12B/100 \rfloor$ | $M = B - D - C$ |
| --: | --: | --: | --: |
| 156250000 | 12500000 | 18750000 | 125000000 |
| 52083333 | 4166666 | 6249999 | 41666668 |
| 99 | 7 | 11 | 81 |
| 1 | 0 | 0 | 1 |
| 0 | 0 | 0 | 0 |


# Rationale

## Ending automatic funding

The financial examples in Motivation support this ZIP's conclusion that
additional automatic allocations are no longer necessary.

Those examples use a range of prices and a spending level above the annualized
Q1 figure. The proposal leaves treasury management and grant selection with the
existing institutions.

Reducing the stream rather than ending it would continue allocating new subsidy
to a program that this ZIP concludes is already sufficiently funded. A
price-triggered cap or automatic restart would introduce a different funding
policy and additional dependencies. This ZIP instead makes a single prospective
allocation change.

## Preserving existing resources and commitments

The proposal does not recover previously allocated funds. ZCG retains its
treasury under the same rules, including the ability to meet existing commitments
and approve further grants. The Coinholder-Controlled Fund also retains its
separate allocation and duration. The specification preserves historical block
validity and leaves existing assets untouched.

## Directing the remainder to the NSM

ZIP 237 specifies a protocol-defined mechanism for reissuing value over time to
support network sustainability. [^zip-0237] Crediting the NSM allocates the
remainder to that purpose. The contribution is withheld from issuance; its
subsequent treatment, including reissuance, remains governed by ZIP 237.

Preserving the existing expiry limits the change to the remainder of the
allocation already specified in ZIP 214.

## Accounting

The reduction in claimable coinbase value and the corresponding NSM contribution
account for the same redirected amount. The existing per-stream rounding and
miner-subsidy formula preserve the miner's share for a given total subsidy.
The proposal changes the destination of the former ZCG allocation; the
fraction deducted from that subsidy is unchanged.

Each redirected zatoshi increases the NSM Value Balance instead of the Issued
Supply. Together with ZIP 235's fee accounting, the recurrence therefore
preserves ZIP 237's invariant: the sum of the Issued Supply and the NSM Value
Balance increases by exactly the Scheduled Block Subsidy in each block from
NU7 onward.


# Deployment

This ZIP is not included in NU7 as currently specified by ZIP 259. [^zip-0259]
It is proposed for a network upgrade that activates before the existing ZCG
stream expires and satisfies the dependencies in ‘Activation and dependencies’.
The specification builds on NU7's funding-stream rules and ZIPs 235 and 237.

Mainnet and Testnet activation heights for this ZIP are unassigned; the NU7
activation heights are separate parameters. A deployment ZIP will specify this
ZIP's activation heights and the network upgrade parameters under ZIP 200.
[^zip-0200] The amendments above take effect under that upgrade; earlier rules
continue to apply to historical blocks.


# Reference implementation

None yet.


# References

[^BCP14]: [Information on BCP 14 — RFC 2119 and RFC 8174](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification](protocol/protocol.pdf)

[^protocol-chainvaluepoolbalances]: [Zcash Protocol Specification, § 4.17: Chain Value Pool Balances](protocol/protocol.pdf#chainvaluepoolbalances)

[^protocol-constants]: [Zcash Protocol Specification, § 5.3: Constants](protocol/protocol.pdf#constants)

[^protocol-txnconsensus]: [Zcash Protocol Specification, § 7.1.2: Transaction Consensus Rules](protocol/protocol.pdf#txnconsensus)

[^protocol-subsidies]: [Zcash Protocol Specification, § 7.8: Calculating Block Subsidy, Funding Streams, Lockbox Disbursement, and Founders' Reward](protocol/protocol.pdf#subsidies)

[^protocol-fundingstreams]: [Zcash Protocol Specification, § 7.10: Payment of Funding Streams, Deferred Lockbox, and Lockbox Disbursement](protocol/protocol.pdf#fundingstreams)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0209]: [ZIP 209: Prohibit Out-of-Range Chain Value Pool Balances](zip-0209.rst)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](zip-0218.md)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235.md)

[^zip-0236]: [ZIP 236: Blocks should balance exactly](zip-0236.rst)

[^zip-0237]: [ZIP 237: Network Sustainability Mechanism: Halving-Preserving Issuance](zip-0237.md)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-2008]: [ZIP 2008: Update to `FS_FPF_ZCG_H3` address list](zip-2008.md)

[^fpf-q1-2026]: [Financial Privacy Foundation: Q1 2026 Report, pp. 5–7 (financial position as of March 31, 2026)](https://9ba4718c-5c73-47c3-a024-4fc4e5278803.usrfiles.com/ugd/9ba471_3d015c48c0a1484a9f8f590b231be31f.pdf). [Publication and supplements](https://www.financialprivacyfoundation.org/post/fpf-q1-2026-report-supplements).

[^zcg-dashboard]: [Zcash Community Grants website](https://zcashcommunitygrants.org/) and its linked [Zcash Community Grants + Coinholder Grants Dashboard](https://docs.google.com/spreadsheets/d/1FQ28rDCyRW0TiNxrm3rgD8ai2KGUsXAjPieQmI1kKKg/edit?usp=sharing), accessed October 26, 2026. The recorded inputs are 91,452.98 ZEC, USD 8,796,224, and USD 2,417,165 in grant liabilities. The dashboard's block reference is 3,526,011 (October 21, 2026, 22:37:53 UTC), and the worksheet is marked “Updates required”. The figures are reported dashboard inputs and have not been independently reconciled.

[^financial-scenarios]: Calculations from the recorded dashboard inputs: at a price of P USD per ZEC, reported holdings less reported grant liabilities equal `91,452.98 * P + 8,796,224 - 2,417,165` USD. At P = 1,300, 1,000, and 500, the results are USD 125,267,933, 97,832,039, and 52,105,549, respectively. Spending comparisons divide these values by an illustrative USD 10,000,000 per year. The calculations assume realization of the stated valuations without conversion costs, constant nominal spending, no further receipts or investment returns, and no obligations beyond the dashboard's grant-liability entry.

[^stream-scenarios]: Calculations using ZIP 214's 8% allocation and the subsidy and block target spacing described in ZIP 218: `0.08 * 1.5625 * (86,400 / 75) = 144` ZEC per day; `144 * 365 = 52,560` ZEC per year. At USD 1,300 per ZEC, these are USD 187,200 and USD 68,328,000. At 25-second spacing, the per-stream integer rule gives 4,166,666 zatoshis per block, or 143.99997696 ZEC per target-spaced day. The illustrations use the scheduled subsidy before the third halving, a fixed price, and the target block rate. The Q1 annualized comparison is `1,530,844 * 4 = 6,123,376` USD, and `68,328,000 / 6,123,376` is approximately 11.16. See [ZIP 214](https://zips.z.cash/zip-0214), [ZIP 218](https://zips.z.cash/zip-0218), and the Q1 report.
