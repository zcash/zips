    ZIP: Unassigned
    Title: Future Dev and Legal Defense Fund Lockbox, and Removal of 50,000 ZEC of ZCG Funds to the Network Sustainability Mechanism
    Owners: Sean Bowe (Tachyon Group) <ewillbefull@gmail.com>
            Zooko Wilcox (Shielded Labs) <zooko@shieldedlabs.net>
            Jason McGee (Shielded Labs) <jason@shieldedlabs.net>
    Status: Draft
    Category: Consensus / Process
    Created: 2026-10-29
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/future-dev-and-legal-defense-fund-zip/58611>
    Pull-Request: <https://github.com/zcash/zips/pull/1428>
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

A "v7 transaction" has the meaning given in ZIP 248 [^zip-0248], and its
explicit removal amount, $\mathsf{zip233\_amount}$, has the meaning given in
ZIP 233 [^zip-0233]: a v7 transaction can carry an amount that is removed from
circulation when the transaction is mined.


# Abstract

This ZIP makes two changes.

1. ZCG's 8% funding stream ends when this ZIP activates. For the rest of that
   stream's term, the same 8% of the block subsidy goes into a new lockbox, the
   **Future Dev and Legal Defense Fund Lockbox**, which holds it for future
   Zcash development and legal defense.

2. The ZCG Committee removes 50,000 ZEC from circulation, crediting it to the
   NSM, using ZIP 233's removal mechanism if it is available when this ZIP
   activates. An unspendable address is specified only as a last resort: it is
   used, and given consensus and wallet treatment under this ZIP, only if
   ZIP 233 is not available.


# Motivation

The rapid rise in the price of ZEC has enlarged the monetary value of ZCG's
treasury to a much greater amount than ever before. This ZIP reduces the risks
and pressure that come with large amounts of money, removes ZCG funds from
circulation, crediting the Network Sustainability Mechanism (providing
increased long-term issuance), and accrues funds in a lockbox for future use by
the Zcash community.

ZCG's dashboard reports holdings of 91,452.98 ZEC and \$8,796,224, against
\$2,417,165 of outstanding grant liabilities [^zcg-dashboard]. FPF reported
\$4,718,359 of ZCG expenses in the first half of 2026, about \$9.4 million a
year [^fpf-q2-2026]. The 8% stream adds another 144 ZEC a day, 52,560 ZEC a
year; at \$1,300 per ZEC, that is about \$68 million a year, more than seven
times ZCG's spending [^stream-scenarios].

ZCG's treasury before and after the removal, at \$1,300 per ZEC
(details [^removal-scenarios]):

| | ZEC | Dollars | Value, less grant liabilities | Years of spending at 2026 levels |
| :-- | --: | --: | --: | --: |
| Before | 91,452.98 | \$8,796,224 | \$125.3 million | 13.3 |
| After | 41,452.98 | \$8,796,224 | \$60.3 million | 6.4 |


# Privacy Implications

The Future Dev and Legal Defense Fund Lockbox adds no addresses, keys, or
notes. A ZIP 233 transaction carries its removal amount explicitly and visibly
[^zip-0233]. If selected for deployment, the address fallback uses transparent
payments to a published address. This ZIP leaves the privacy of every
transaction unchanged.


# Specification

## Activation

Let $A$ be this ZIP's activation height on a network. Let $E$ be the end height
of `FS_FPF_ZCG_H3` under Revision 3 of ZIP 214 [^zip-0214]: the third halving
under ZIP 218's 25-second blocks [^zip-0218], $E = N + 3 \cdot (H_3 - N)$, where
$N$ is the network's NU7 activation height and $H_3$ is the pre-NU7
third-halving height (4406400 on Mainnet, 4476000 on Testnet). With Mainnet's
$N = 3543405$ [^zip-0259], $E = 6132390$. End heights are exclusive, as in
ZIP 207 [^zip-0207].

The lockbox rules below apply on a network where $A < E$; where $A \geq E$, the
ZCG stream has already ended, and they change nothing. The rules for removing
funds from circulation depend on the mechanism selected by the deployment
ZIP, as the section "Removing funds from circulation" specifies.

## The Future Dev and Legal Defense Fund Lockbox

The Future Dev and Legal Defense Fund Lockbox is a second lockbox, separate
from the Deferred Dev Fund Lockbox, with its own chain value pool balance. It
holds funds for future Zcash development and legal defense. No disbursement
mechanism is currently defined for this lockbox; the Zcash community will need
to decide upon and specify a suitable decentralized mechanism for permitting
withdrawals from this lockbox in a future ZIP in order to make these funds
available for funding Zcash development and legal defense.

This is not intended to imply that funds for Zcash development and legal
defense cannot come from other sources.

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
Future Dev and Legal Defense Fund Lockbox's own balance, defined below — not
into the Deferred Dev Fund Lockbox's. In § 7.8 and § 7.1.2, define
$\mathsf{totalFDLDFOutput}(h)$ as the sum of $\mathsf{fs.Value}(h)$ over the
streams paid to $\mathsf{FDLDF\_POOL}$ at height $h$, and add it to the coinbase
transaction's $\mathsf{totalOutputValue}$, beside
$\mathsf{totalDeferredOutput}(h)$.

**The balance.** In § 4.17, add the Future Dev and Legal Defense Fund
Lockbox's chain value pool balance,

$$\mathsf{FDLDFBalance}(h) := \sum_{i=0}^{h} \mathsf{totalFDLDFOutput}(i),$$

and include it in $\mathsf{IssuedSupply}(h)$. Add it to the pools of ZIP 209
[^zip-0209], whose balances MUST be nonnegative and whose sum MUST NOT exceed
$\mathsf{MAX\_MONEY}$. No consensus rule moves value out of it.

## Removing funds from circulation

The section "The removal of ZCG funds" requires the ZCG Committee to remove
50,000 ZEC from circulation, crediting it to the NSM. The intended means is
ZIP 233 [^zip-0233], which lets a sender voluntarily remove a specified amount
of ZEC from circulation; ZIP 237 credits removed value to the NSM Value
Balance [^zip-0237].

The deployment ZIP that sets $A$ MUST identify the removal mechanism to be
used on each network. If ZIP 233 will be active at $A$, it MUST select
ZIP 233 and MUST NOT deploy the address fallback below. Only if ZIP 233 will
not be active at $A$ MAY the deployment ZIP explicitly select that fallback
as a last resort.

Unless the fallback is explicitly selected, the address MUST NOT be used to
fulfill this ZIP's removal obligation, and implementations MUST NOT give the
address or its script any special consensus accounting or wallet recognition
under this ZIP. In particular, payments to it MUST NOT be credited to the NSM
Value Balance. The absence of ZIP 233 alone does not select the fallback.

### Removal with ZIP 233 transactions

Where ZIP 233 is selected, its own consensus rules perform the removal: a v7
transaction [^zip-0248] carries an explicit removal amount,
$\mathsf{zip233\_amount}$, which is removed from circulation when the
transaction is mined, and which ZIP 237 adds to the NSM Value Balance. On such
a network, this ZIP adds no consensus rules.

### Last-resort NSM removal address

All rules in this subsection, including the ZIP 237 changes and wallet
handling, apply only on a network where the deployment ZIP selects the address
fallback. Its consensus rules take effect at height $A$ and remain in effect
at every later height: the address becomes a permanent feature of the
protocol.

The NSM removal address is the Mainnet P2SH address

    t3QZUHYkaEQEuWosAc9HgMPKiQRdvuBPCQZ

Its script hash, `41c98a140039816273e50db317422c11c2bfcc88`, is HASH160 of the
one-byte redeem script `0x6a`: the single opcode `OP_RETURN`, a script that
fails whatever a spender supplies. To check this, decode the address with
Base58Check, confirm its P2SH prefix (`[0x1c, 0xbd]`) and checksum, and compare
its script hash with HASH160 of the byte `0x6a`.

Let $\mathsf{RemovalOutput}(h)$ be the total value of the transparent outputs
in block $h$, in any transaction including the coinbase transaction, whose
script is exactly the P2SH script
`a91441c98a140039816273e50db317422c11c2bfcc8887`.

**Changes to ZIP 237.** Register the following mechanism for removal from
circulation in the list defined in ZIP 237 [^zip-0237]:

| Mechanism | Source |
|---|---|
| Payments to the NSM removal address | $\mathsf{NSMAddressRemovals}(\mathsf{height})$ |

$$\mathsf{NSMAddressRemovals}(h) := \begin{cases} 0 & \text{if } h < A \\ \displaystyle\sum_{i=0}^{A} \mathsf{RemovalOutput}(i) & \text{if } h = A \\ \mathsf{RemovalOutput}(h) & \text{if } h > A \end{cases}$$

At height $A$, everything sent to the address up to and including block $A$ is
removed from circulation at once; at each later height $h$, block $h$'s
payments are. In § 4.17, the transparent chain value pool balance decreases by
$\mathsf{NSMAddressRemovals}(h)$, which ZIP 237 adds to the NSM Value Balance.

Nothing sent to this address can be returned.

**Wallet handling.** The NSM removal address looks like any other Mainnet P2SH
address; nothing about it warns a user that funds sent to it cannot be
recovered. Software that accepts payment destinations (e.g. typed or pasted by
a user, read from a payment request URI, or kept in an address book)

* SHOULD recognize the NSM removal address, by its script hash or its exact
  string, at every such entry point;
* SHOULD present a payment to it as an irreversible removal of funds from
  circulation, not an ordinary payment; and
* SHOULD NOT offer it as an ordinary payment destination.

## The removal of ZCG funds

The ZCG Committee SHALL cause 50,000 ZEC of the funds it administers to be
removed from circulation, crediting it to the NSM, in one or more Mainnet
transactions using the mechanism selected by the deployment ZIP. The specified
removal amounts MUST total that amount, excluding transaction fees. If the
address fallback is selected, these are the amounts paid to that address. The
ZCG Committee SHALL do so as soon as possible, and no later than 30 days after
Mainnet reaches height $A$.

Payments to the NSM removal address before height $A$ count toward the removal
and are added to the NSM Value Balance at height $A$ — but only where the
fallback is selected. The ZCG Committee MUST NOT pay the address before block
height $A$ on Mainnet.

Since the funds ZCG administers are held by FPF, the ZCG Committee fulfills
this obligation by directing FPF to create the transactions, as it directs FPF
to make grant payments under ZIP 1015.

The ZCG Committee SHALL publish the transaction identifier of each such
transaction to the Zcash community promptly after it is mined.

## Changes to ZIPs 1015 and 1016

In ZIP 1015's section on ZCG [^zip-1015-zcg], add: "ZCG funds MAY also be used
for the removal from circulation that [this ZIP] specifies, which credits the
Network Sustainability Mechanism. That removal is not a grant."

In ZIP 1016's section on ZCG [^zip-1016], end ZCG's funding stream at this
ZIP's activation height, and state that from then until the third halving the
same 8% goes into the Future Dev and Legal Defense Fund Lockbox, as this ZIP
specifies. In its section on the Coinholder-Controlled Fund, give the 12%
stream's duration by `FS_CCF_H3`'s own start and end heights in ZIP 214.


# Rationale

**A lockbox of its own.** The 8% is set aside, issued but locked, for future
development and legal defense, and a future ZIP decides how it is spent. A
separate balance keeps the fund apart from the Deferred Dev Fund Lockbox's
purpose and disbursement rules, and lets a future disbursement mechanism
authorize withdrawals from each lockbox separately — under ZIP 270's tracked
signing keys [^zip-0270], for example, each can have authorizing keys of its
own. Like that lockbox, it needs no custodians or keys today, and its
disbursement mechanism can take the same technical approach as the one being
designed for the Deferred Dev Fund Lockbox.

**An address only as a last resort.** ZIP 233 is the protocol's purpose-built
way to remove funds from circulation: an explicit amount in a v7 transaction,
with no address. NU7 deploys neither ZIP 233 nor ZIP 248's v7 format
[^zip-0233] [^zip-0259], and this ZIP cannot anticipate whether they will be
available when it activates, so it reserves the address solely for the case
where they are not. If needed, the fallback requires no new transaction fields
or address formats, recognizes only one script, and is permanent, so value
sent to the address at any height is added to the NSM Value Balance; if
ZIP 233 activates later, both mechanisms add to the same balance.

**No spending prohibition.** Spending from the NSM removal address would
require a redeem script other than `OP_RETURN` with the same script hash — a
preimage attack on RIPEMD-160. This ZIP adds no rule against such a spend: an
attack of that kind would threaten the much larger value held in ordinary
transparent outputs, and a rule for this one address would not change that.

**The removal's size.** 50,000 ZEC is about 55% of ZCG's ZEC. Anyone can check
the removal on the chain, and ZCG keeps the rest of its treasury and its grants
program.

**Accounting.** The lockbox's balance stays in the Issued Supply. A ZIP 233
removal subtracts its amount from the Issued Supply when its transaction is
mined; where the fallback is selected, a payment to the NSM removal address
leaves the transparent pool at the height ZIP 237 credits it. In each case,
the value moves to the NSM Value Balance in the same block, keeping ZIP 237's
invariant: in each block from NU7 on, the Issued Supply plus the NSM Value
Balance grows by exactly the scheduled block subsidy.

## Other proposals

Draft #1423 would wind ZCG down [^draft-wind-down-zcg]. Where it overlaps
with this ZIP, it is an alternative to it.

`draft-dairaemma-governance-zap` [^draft-dairaemma-governance-zap] requires
that "the `FS_FPF_ZCG_H3` funding stream SHALL continue at its existing value
and for the duration specified in ZIP 214 Revision 3", therefore it and this
proposal are incompatible. It explicitly names legal defense as a possible
use of ZAP Grants, which would not require a further consensus change for
disbursement.


# Deployment

The lockbox rules — and, if the fallback is selected, the NSM removal address
rules — are consensus changes, proposed for a network upgrade after NU7 that
activates before height $E$; that upgrade's deployment ZIP sets $A$ for each
network [^zip-0200]. The expected deployment activates ZIPs 248 and 233 in the
same upgrade, so the fallback is not selected; it is selected only as a last
resort, if ZIP 233 will not be active at $A$. The removal of ZCG funds follows
the schedule in the section "The removal of ZCG funds".


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

[^zip-0248]: [ZIP 248: Extensible Transaction Format](https://zips.z.cash/zip-0248)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](https://zips.z.cash/zip-0259)

[^zip-0270]: [ZIP 270: Key Rotation for Tracked Signing Keys](https://zips.z.cash/zip-0270)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](https://zips.z.cash/zip-1015)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Zcash Community Grants](https://zips.z.cash/zip-1015#zcash-community-grants-zcg)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](https://zips.z.cash/zip-1016)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](https://zips.z.cash/zip-2001)

[^zip-2008]: [ZIP 2008: Update to `FS_FPF_ZCG_H3` address list](https://zips.z.cash/zip-2008)

[^draft-dairaemma-governance-zap]: [`draft-dairaemma-governance-zap`: Zcash Adoption Pool (ZAP)](draft-dairaemma-governance-zap.md)

[^draft-wind-down-zcg]: [Draft: Winding Down Zcash Community Grants (zcash/zips#1423)](https://github.com/zcash/zips/pull/1423)

[^fpf-q2-2026]: [Financial Privacy Foundation: Q2 2026 Report, p. 5 (ZCG statistics, with total expenses for Q1 and Q2 2026)](https://9ba4718c-5c73-47c3-a024-4fc4e5278803.usrfiles.com/ugd/9ba471_0836532577dd4f0eab3cf5080820e622.pdf). Q2's total includes \$1,216,687 of Discretionary Fund usage, versus \$54,108 in Q1, so neither quarter alone indicates recurring spending.

[^zcg-dashboard]: [Zcash Community Grants website](https://zcashcommunitygrants.org/) and its linked [Zcash Community Grants + Coinholder Grants Dashboard](https://docs.google.com/spreadsheets/d/1FQ28rDCyRW0TiNxrm3rgD8ai2KGUsXAjPieQmI1kKKg/edit?usp=sharing), accessed October 26, 2026. The recorded inputs are 91,452.98 ZEC, USD 8,796,224, and USD 2,417,165 in grant liabilities. The dashboard's block reference is 3,526,011 (October 21, 2026, 22:37:53 UTC), and the worksheet is marked “Updates required”. The figures are reported dashboard inputs and have not been independently reconciled.

[^stream-scenarios]: The 8% of a 1.5625 ZEC block subsidy, at 1,152 blocks of 75 seconds a day: `0.08 * 1.5625 * 1,152 = 144` ZEC a day, `144 * 365 = 52,560` ZEC a year; at USD 1,300 per ZEC, USD 68,328,000 a year. ZIP 218's 25-second blocks, each with a third of the subsidy, leave the daily amount the same, apart from rounding. Annual spending: `(1,530,844 + 3,187,515) * 2 = 9,436,718` USD, from the Q2 2026 report.

[^removal-scenarios]: From the dashboard figures above, at USD 1,300 per ZEC: before the removal, `91,452.98 * 1,300 + 8,796,224 - 2,417,165 = 125,267,933` USD; after it, `41,452.98 * 1,300 + 8,796,224 - 2,417,165 = 60,267,933` USD. Years of spending divide these by the 2026 rate of USD 9,436,718 a year. The figures assume no conversion costs and no further receipts, returns, or obligations beyond the dashboard's grant liabilities.
