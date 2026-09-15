    ZIP: XXX
    Title: Update to ZIP 1016: Key-Holder Organizations
    Owners: Jason McGee <jason@shieldedlabs.net>
    Status: Draft
    Category: Process
    Created: 2026-09-14
    License: MIT
    Discussions-To: <URL TBD>
    Updates: 1016, 271


# Terminology

The key words "MUST" and "SHALL" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The terms "Electric Coin Company" (or "ECC") and "Bootstrap Project" (or "BP")
in this document are to be interpreted as described in ZIP 1014 [^zip-1014].

"Zcash Foundation" (or "ZF") refers to the Delaware not-for-profit corporation
of that name, recognized as a public charity under Section 501(c)(3) of the
U.S. Internal Revenue Code.

"Shielded Labs" refers to the Association of that name registered in the Swiss
canton of Zug under the Unique Identifier CHE-243.302.798.

"Zcash Open Development Lab" (or "ZODL") refers to Znewco, Inc., a corporation
incorporated in the State of Texas, USA, doing business as Zcash Open
Development Lab.


# Abstract

This ZIP updates ZIP 1016 [^zip-1016] and ZIP 271 [^zip-0271] to replace the
Electric Coin Company with Zcash Open Development Lab as one of the three
Key-Holder Organizations for the Coinholder-Controlled Fund, and to define the
term "Key-Holder Organizations" in ZIP 1016 as Zcash Foundation, Shielded Labs,
and Zcash Open Development Lab.


# Motivation

ZIP 271 names the Electric Coin Company, Zcash Foundation, and Shielded Labs as
the Key-Holder Organizations that hold keys to the multisig address that
received the one-time lockbox disbursement at NU6.1 activation. ZIP 1016
assigns those organizations responsibility for administering the
Coinholder-Controlled Fund according to coinholder votes.

In January 2026, ECC's engineering and product team left ECC following a
governance dispute with Bootstrap, the nonprofit that oversees ECC. The team's
position was that changes to their terms of employment made it impossible to
continue their work and amounted to a constructive discharge. Bootstrap's
position was that the dispute concerned the organization's obligations as a
tax-exempt charity under federal law and the fiduciary duties its directors
owe. [^coindesk-1] [^coindesk-2]

The former ECC team formed a new company, Zcash Open Development Lab, to
continue development of the Zcash protocol and related software. ZODL
announced $25 million in seed funding in March 2026. [^coindesk-3]

Bootstrap and ZODL later reached an agreement resolving the dispute. Under that
agreement, Bootstrap renounced any authority as a Key-Holder Organization under
ZIP 271 over the lockbox multisig, and stated that the new company or others
would submit a new ZIP to transfer legal authority over the relevant key in
accordance with the ZIP process. [^bootstrap-statement] This is that ZIP.
Bootstrap has since changed its name to Sovright. [^sovright-rename]

This ZIP updates the text of ZIP 1016 and ZIP 271 to reflect the current
Key-Holder Organizations.


# Specification

## Key-Holder Organizations

The Key-Holder Organizations are Zcash Foundation, Shielded Labs, and Zcash
Open Development Lab.

Zcash Open Development Lab holds the key to the ZIP 271 disbursement address
previously held by the Electric Coin Company, and assumes all rights and
obligations of a Key-Holder Organization under ZIP 1016 and ZIP 271.

## Changes to ZIP 1016

ZIP 1016 uses the term "Key-Holder Organizations" but does not define it. This
ZIP adds the definition.

In the section **Terminology**, instead of:

> The terms "Electric Coin Company" (or "ECC"), "Bootstrap Project" (or "BP")
> and "Zcash Foundation" (or "ZF") in this document are to be interpreted as
> described in ZIP 1014.

it will be modified to read:

> The terms "Electric Coin Company" (or "ECC") and "Bootstrap Project" (or
> "BP") in this document are to be interpreted as described in ZIP 1014.
>
> "Zcash Foundation" (or "ZF") refers to the Delaware not-for-profit
> corporation of that name, recognized as a public charity under Section
> 501(c)(3) of the U.S. Internal Revenue Code.

After the paragraph defining "Shielded Labs", the following paragraphs are
added:

> "Zcash Open Development Lab" (or "ZODL") refers to Znewco, Inc., a
> corporation incorporated in the State of Texas, USA, doing business as Zcash
> Open Development Lab.
>
> The "Key-Holder Organizations" are Zcash Foundation, Shielded Labs, and Zcash
> Open Development Lab.

No other changes are made to ZIP 1016. In particular, the section
**Administrative obligations and constraints** continues to refer to the
Electric Coin Company, because it carries forward obligations imposed on ECC by
ZIP 1015 in respect of the previous `FS_FPF_ZCG` funding stream.

## Changes to ZIP 271

In the section **One-time lockbox disbursement**, instead of:

> The coinbase transaction of the activation block of this ZIP MUST include one
> or more lockbox disbursement output(s) to a 2-of-3 P2SH multisig with keys
> held by the following "Key-Holder Organizations": Zcash Foundation, the
> Electric Coin Company, and Shielded Labs.

it will be modified to read:

> The coinbase transaction of the activation block of this ZIP MUST include one
> or more lockbox disbursement output(s) to a 2-of-3 P2SH multisig with keys
> held by the Key-Holder Organizations. At the time of the disbursement, the
> Key-Holder Organizations were Zcash Foundation, the Electric Coin Company,
> and Shielded Labs. The Key-Holder Organizations are defined in ZIP 1016, as
> updated by ZIP XXX.

This change does not alter any consensus rule. The disbursement address,
amount, and activation height are unchanged.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-0271]: [ZIP 271: Deferred Dev Fund Lockbox Disbursement](zip-0271.md)

[^coindesk-1]: [CoinDesk, 8 January 2026: Top privacy token Zcash falls 14% after key developer team quits over governance clash](https://www.coindesk.com/tech/2026/01/08/zcash-developer-team-behind-ecc-quits-after-governance-clash-with-bootstrap-board)

[^coindesk-2]: [CoinDesk, 8 January 2026: Zcash governance clash tanked the token. Here's why it may not be as big as it seems.](https://www.coindesk.com/business/2026/01/08/zcash-governance-dispute-may-not-be-as-big-as-it-seems)

[^coindesk-3]: [CoinDesk, 9 March 2026: Josh Swihart's Zcash Open Development Lab raises $25 million in seed funding](https://www.coindesk.com/business/2026/03/09/josh-swihart-s-zcash-open-development-lab-raises-usd25-million-in-seed-funding)

[^bootstrap-statement]: [Bootstrap Board statement on resolution of governance dispute, DATE TBD](URL TBD)

[^sovright-rename]: [Sovright: Why We Changed Our Name](https://sovright.com/rename.html)
