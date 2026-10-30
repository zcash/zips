    ZIP: Unassigned
    Title: Future Dev and Legal Defense Fund Lockbox, and a ZCG Donation to the Network Sustainability Mechanism
    Owners: Sean Bowe (Tachyon Group) <ewillbefull@gmail.com>
            Zooko Wilcox (Shielded Labs) <zooko@shieldedlabs.net>
            Jason McGee (Shielded Labs) <jason@shieldedlabs.net>
    Status: Draft
    Category: Consensus / Process
    Created: 2026-10-29
    License: MIT
    Updates: 207, 209, 214, 237, 1015, 1016

# Terminology

The key words "MUST", "MUST NOT", "SHALL", "SHOULD", "SHOULD NOT", and "MAY" in
this document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The terms "Mainnet", "Testnet", "block subsidy", "funding stream", "coinbase
transaction", "chain value pool balance", and "Issued Supply" have the meanings
given in the Zcash Protocol Specification [^protocol]; the character § refers
to its sections.

"Zcash Community Grants" ("ZCG"), the "ZCG Committee", the "Financial Privacy
Foundation" ("FPF"), and the "Deferred Dev Fund Lockbox" have the meanings given
in ZIP 1015 [^zip-1015].

The "Network Sustainability Mechanism" ("NSM") and the "NSM Value Balance" have
the meanings given in ZIP 237 [^zip-0237]: ZEC removed from circulation is added
to the NSM Value Balance, and returns to circulation through future block
subsidies.


# Abstract

This ZIP makes two changes.

1. ZCG's 8% funding stream ends when this ZIP activates. For the rest of that
   stream's term, the same 8% of the block subsidy goes into a new lockbox, the
   **Future Dev and Legal Defense Fund Lockbox**, which holds it for future
   Zcash development and legal defense.

2. The ZCG Committee donates 50,000 ZEC to the NSM within 30 days of this ZIP's
   acceptance, by sending it to an address that no one can spend from. When
   this ZIP activates, everything sent to that address is removed from
   circulation and added to the NSM Value Balance.


# Motivation

The rapid rise in the price of ZEC has enlarged the monetary value of ZCG's
treasury to a much greater amount than ever before. This ZIP reduces the risks
and pressure that come with large amounts of money, donates to the Network
Sustainability Mechanism (providing increased long-term issuance), and accrues
funds in a lockbox for future use by the Zcash community.

ZCG's dashboard reports holdings of 91,452.98 ZEC and \$8,796,224, against
\$2,417,165 of outstanding grant liabilities [^zcg-dashboard]. FPF reported
\$4,718,359 of ZCG expenses in the first half of 2026, about \$9.4 million a
year [^fpf-q2-2026]. The 8% stream adds another 144 ZEC a day, 52,560 ZEC a
year; at \$1,300 per ZEC, that is about \$68 million a year, more than seven
times ZCG's spending [^stream-scenarios].

ZCG's treasury before and after the donation, at \$1,300 per ZEC
(details [^donation-scenarios]):

| | ZEC | Dollars | Value, less grant liabilities | Years of spending at 2026 levels |
| :-- | --: | --: | --: | --: |
| Before | 91,452.98 | \$8,796,224 | \$125.3 million | 13.3 |
| After | 41,452.98 | \$8,796,224 | \$60.3 million | 6.4 |


# Privacy Implications

The lockbox adds no addresses, keys, or notes. The donation is a public
transparent payment to a published address. This ZIP leaves the privacy of
every transaction unchanged.


# Specification

## Activation

Let $A$ be this ZIP's activation height on a network, and $N$ that network's
NU7 activation height; $A$ MUST be greater than $N$. Let $E$ be the end height
of `FS_FPF_ZCG_H3` under Revision 3 of ZIP 214 [^zip-0214]: the third halving
under ZIP 218's 25-second blocks [^zip-0218], $E = N + 3 \cdot (H_3 - N)$, where
$H_3$ is the pre-NU7 third-halving height (4406400 on Mainnet, 4476000 on
Testnet). With Mainnet's $N = 3543405$ [^zip-0259], $E = 6132390$. End heights
are exclusive, as in ZIP 207 [^zip-0207].

The lockbox rules below apply on a network where $A < E$; where $A \geq E$, the
ZCG stream has already ended, and they change nothing. The NSM donation address
rules apply from $A$ on every network.

## The Future Dev and Legal Defense Fund Lockbox

The Future Dev and Legal Defense Fund Lockbox holds funds for future Zcash
development and legal defense. No one can spend from it until a future ZIP
specifies how.

**Funding streams.** A new revision of ZIP 214 makes these changes at $A$:

* The end height of `FS_FPF_ZCG_H3` becomes $A$. Its recipient list keeps the
  addresses for the address periods before $A$, as ZIP 207 computes them,
  including ZIP 2008's change [^zip-2008].
* A new funding stream, `FS_FDLDF_H3`, pays 8/100 of the block subsidy from
  height $A$ to height $E$, to the recipient $\mathsf{FDLDF\_POOL}$ in every
  address period.

`FS_CCF_H3` and the Deferred Dev Fund Lockbox are unchanged.

**The recipient.** A new revision of ZIP 207 adds the recipient identifier
$\mathsf{FDLDF\_POOL}$, which works as $\mathsf{DEFERRED\_POOL}$ does [^zip-2001]:
a stream paid to it produces no coinbase output, and its value goes into the
lockbox's balance instead. In § 7.8 and § 7.1.2, define
$\mathsf{totalFDLDFOutput}(h)$ as the sum of $\mathsf{fs.Value}(h)$ over the
streams paid to $\mathsf{FDLDF\_POOL}$ at height $h$, and add it to the coinbase
transaction's $\mathsf{totalOutputValue}$, beside
$\mathsf{totalDeferredOutput}(h)$.

**The balance.** In § 4.17, add the lockbox's chain value pool balance,

$$\mathsf{FDLDFBalance}(h) := \sum_{i=0}^{h} \mathsf{totalFDLDFOutput}(i),$$

and include it in $\mathsf{IssuedSupply}(h)$. Add it to the pools of ZIP 209
[^zip-0209], whose balances MUST be nonnegative and whose sum MUST NOT exceed
$\mathsf{MAX\_MONEY}$. No consensus rule moves value out of it.

## The NSM donation address

The NSM donation address is the Mainnet P2SH address

    t3QZUHYkaEQEuWosAc9HgMPKiQRdvuBPCQZ

Its script hash, `41c98a140039816273e50db317422c11c2bfcc88`, is HASH160 of the
one-byte script `6a`, `OP_RETURN`, which fails whatever a spender supplies. To
check this, decode the address with Base58Check, confirm its version prefix
(`1cbd`) and checksum, and compare its script hash with HASH160 of the byte
`0x6a`. Spending from it would require a second script with the same HASH160.

Let $\mathsf{DonatedValue}(h)$ be the total value of the transparent outputs in
block $h$, in any transaction including the coinbase transaction, whose script
is exactly the P2SH script `a91441c98a140039816273e50db317422c11c2bfcc8887`.
From $A$ on:

* A transaction MUST NOT spend an output with that script.
* At height $A$, the value of every such output up to and including block $A$,
  $\sum_{i=0}^{A} \mathsf{DonatedValue}(i)$, is removed from circulation; at
  each later height $h$, $\mathsf{DonatedValue}(h)$ is. Call this amount
  $\mathsf{NSMDonations}(h)$. In § 4.17, the transparent chain value pool
  balance decreases by $\mathsf{NSMDonations}(h)$, and ZIP 237's list of
  mechanisms for removal from circulation gains the source
  $\mathsf{NSMDonations}(h)$, so that it is added to the NSM Value Balance.

Anyone MAY send ZEC to the NSM donation address, and nothing sent there can be
returned. Wallets SHOULD NOT offer it as an ordinary payment destination.
Counts of circulating supply SHOULD exclude everything sent to it, before $A$
as well as after.

## The donation

The ZCG Committee SHALL cause 50,000 ZEC of the funds it administers to be sent
to the NSM donation address, in one or more Mainnet transactions. It SHALL do so
as soon as possible, and no later than 30 days after the date on which this ZIP
is accepted by the Zcash community.

Since the funds ZCG administers are held by FPF, the ZCG Committee fulfills this
obligation by directing FPF to create the transactions, as it directs FPF to
make grant payments under ZIP 1015. Only FPF's payments count toward the
donation.

The ZCG Committee SHALL publish the transaction identifier of each such
transaction to the Zcash community promptly after it is mined.

## Changes to ZIPs 1015 and 1016

In ZIP 1015's section on ZCG [^zip-1015-zcg], add: "ZCG funds MAY also be used
for the donation to the Network Sustainability Mechanism that [this ZIP]
specifies. That donation is not a grant."

In ZIP 1016's section on ZCG [^zip-1016], end ZCG's funding stream at this
ZIP's activation height, and state that from then until the third halving the
same 8% goes into the Future Dev and Legal Defense Fund Lockbox, as this ZIP
specifies. In its section on the Coinholder-Controlled Fund, give the 12%
stream's duration by `FS_CCF_H3`'s own start and end heights in ZIP 214, which
this ZIP leaves unchanged.


# Rationale

**A lockbox of its own.** The 8% is set aside, issued but locked, for future
development and legal defense, and a future ZIP decides how it is spent. A
separate balance keeps it apart from the Deferred Dev Fund Lockbox's purpose
and disbursement rules, and like that lockbox it needs no custodians or keys.

**A donation by address.** NU7 deploys ZIP 237's NSM but no way for a
transaction to remove ZEC from circulation directly: it deploys neither ZIP 233
nor ZIP 234 [^zip-0233] [^zip-0259]. Sending to an address that no one can spend
from lets the donation happen now; at $A$, it moves into the NSM, with every
earlier payment to the address. The consensus change is small: no
new transaction fields, address formats, or wallet changes. Payments from anyone
count, so the address serves every donor. If ZIP 233 is deployed later, both
mechanisms add to the same NSM Value Balance.

**The donation's size.** 50,000 ZEC is about 55% of ZCG's ZEC. Anyone can check
its payment on the chain, and ZCG keeps the rest of its treasury and its grants
program.

**Accounting.** The lockbox's balance stays in the Issued Supply. A donation
moves value from the transparent pool to the NSM Value Balance in the same
block. Both keep ZIP 237's invariant: in each block from NU7 on, the Issued
Supply plus the NSM Value Balance grows by exactly the scheduled block subsidy.

**Other proposals.** ZIP draft #1414 sends the 8% stream to the NSM
[^draft-end-zcg-stream], and draft #1423 winds ZCG down [^draft-wind-down-zcg].
Where they overlap with this ZIP, they are alternatives to it.


# Deployment

The lockbox and the NSM donation address are consensus changes, proposed for a
network upgrade after NU7 that activates before height $E$; that upgrade's
deployment ZIP sets $A$ for each network [^zip-0200]. The donation needs no
network upgrade: it is due within 30 days of this ZIP's acceptance.


# Reference implementation

None yet.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification](https://zips.z.cash/protocol/protocol.pdf)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](https://zips.z.cash/zip-0200)

[^zip-0207]: [ZIP 207: Funding Streams](https://zips.z.cash/zip-0207)

[^zip-0209]: [ZIP 209: Prohibit Out-of-Range Chain Value Pool Balances](https://zips.z.cash/zip-0209)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](https://zips.z.cash/zip-0214)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](https://zips.z.cash/zip-0218)

[^zip-0233]: [ZIP 233: Network Sustainability Mechanism: Removing Funds From Circulation](https://zips.z.cash/zip-0233)

[^zip-0237]: [ZIP 237: Network Sustainability Mechanism: Halving-Preserving Issuance](https://zips.z.cash/zip-0237)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](https://zips.z.cash/zip-0259)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](https://zips.z.cash/zip-1015)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Zcash Community Grants](https://zips.z.cash/zip-1015#zcash-community-grants-zcg)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](https://zips.z.cash/zip-1016)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](https://zips.z.cash/zip-2001)

[^zip-2008]: [ZIP 2008: Update to `FS_FPF_ZCG_H3` address list](https://zips.z.cash/zip-2008)

[^draft-end-zcg-stream]: [Draft: Ending the ZCG Funding Stream in Favor of the NSM (zcash/zips#1414)](https://github.com/zcash/zips/pull/1414)

[^draft-wind-down-zcg]: [Draft: Winding Down Zcash Community Grants (zcash/zips#1423)](https://github.com/zcash/zips/pull/1423)

[^fpf-q2-2026]: [Financial Privacy Foundation: Q2 2026 Report, p. 5 (ZCG statistics, with total expenses for Q1 and Q2 2026)](https://9ba4718c-5c73-47c3-a024-4fc4e5278803.usrfiles.com/ugd/9ba471_0836532577dd4f0eab3cf5080820e622.pdf). Q2's total includes \$1,216,687 of Discretionary Fund usage, versus \$54,108 in Q1, so neither quarter alone indicates recurring spending.

[^zcg-dashboard]: [Zcash Community Grants website](https://zcashcommunitygrants.org/) and its linked [Zcash Community Grants + Coinholder Grants Dashboard](https://docs.google.com/spreadsheets/d/1FQ28rDCyRW0TiNxrm3rgD8ai2KGUsXAjPieQmI1kKKg/edit?usp=sharing), accessed October 26, 2026. The recorded inputs are 91,452.98 ZEC, USD 8,796,224, and USD 2,417,165 in grant liabilities. The dashboard's block reference is 3,526,011 (October 21, 2026, 22:37:53 UTC), and the worksheet is marked “Updates required”. The figures are reported dashboard inputs and have not been independently reconciled.

[^stream-scenarios]: The 8% of a 1.5625 ZEC block subsidy, at 1,152 blocks of 75 seconds a day: `0.08 * 1.5625 * 1,152 = 144` ZEC a day, `144 * 365 = 52,560` ZEC a year; at USD 1,300 per ZEC, USD 68,328,000 a year. ZIP 218's 25-second blocks, each with a third of the subsidy, leave the daily amount the same, apart from rounding. Annual spending: `(1,530,844 + 3,187,515) * 2 = 9,436,718` USD, from the Q2 2026 report.

[^donation-scenarios]: From the dashboard figures above, at USD 1,300 per ZEC: before the donation, `91,452.98 * 1,300 + 8,796,224 - 2,417,165 = 125,267,933` USD; after it, `41,452.98 * 1,300 + 8,796,224 - 2,417,165 = 60,267,933` USD. Years of spending divide these by the 2026 rate of USD 9,436,718 a year. The figures assume no conversion costs and no further receipts, returns, or obligations beyond the dashboard's grant liabilities.
