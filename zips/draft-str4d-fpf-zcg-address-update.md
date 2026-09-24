    ZIP: TBD
    Title: Update to `FS_FPF_ZCG_H3` address list
    Owners: Jack Grigg <thestr4d@gmail.com>
    Status: Draft
    Category: Consensus
    Created: 2026-09-24
    License: MIT


# Terminology

The key word "MAY" in this document is to be interpreted as described in BCP 14
[^BCP14] when, and only when, it appears in all capitals.


# Abstract

This ZIP updates the address list for the `FS_FPF_ZCG_H3` funding stream,
reflecting operational changes by the recipient.


# Motivation

The recipient of the `FS_FPF_ZCG_H3` funding stream notified the ZIP Editors
that there was a need to receive the funding stream into a new address. This
change can only happen at network upgrade boundaries, because the funding
stream recipient addresses are part of the consensus rules.


# Requirements

- Funding stream outputs for `FS_FPF_ZCG_H3` start being received at the new
  address shortly after the NU activates that deploys this ZIP.


# Specification

## Changes to ZIP 214

In "Mainnet Recipients for `Revision 2`" [^zip-0214], replace:

> ```
> FS_FPF_ZCG_H3.AddressList[0..35] = ["t3cFfPt1Bcvgez9ZbMBFWeZsskxTkPzGCow"] * 36
> ```

with:

> ```
> N = FundingStream[FS_FPF_ZCG_H3].AddressIndex(NU7ActivationHeight - 1) + 1
> FS_FPF_ZCG_H3.AddressList[0..N-1] = ["t3cFfPt1Bcvgez9ZbMBFWeZsskxTkPzGCow"] * N
> FS_FPF_ZCG_H3.AddressList[N..35] = ["TBD"] * (36 - N)
> ```

## Consensus node implementor note

Once a mainnet activation height has been specified in ZIP 259 [^zip-0259],
implementations MAY use a fixed array of addresses in the correct sequence,
instead of dynamically calculating `N`.


# Rationale

The ZIP modifies the existing address list such that the new address will start
being used from the first funding period that begins after NU7 activation. This
means that depending on the precise value of `NU7ActivationHeight`, the updated
address might begin usage anywhere from "immediately" to "about a month" after
activation. This approach was chosen for its simplicity, given the lack of time
before NU7 activation. An alternative approach that instead changed the address
at NU activation would require more significant changes to ZIP 214 [^zip-0214]
(and possibly ZIP 207 [^zip-0207]).


# Deployment

This ZIP is proposed to be deployed with NU7.


# Reference implementation

TBD


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)
