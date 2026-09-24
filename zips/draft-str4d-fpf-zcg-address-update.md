    ZIP: TBD
    Title: Update to `FS_FPF_ZCG_H3` address list
    Owners: Jack Grigg <thestr4d@gmail.com>
    Status: Draft
    Category: Consensus
    Created: 2026-09-24
    License: MIT


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

In "Mainnet Recipients for `Revision 2`", replace:

> ```
> FS_FPF_ZCG_H3.AddressList[0..35] = ["t3cFfPt1Bcvgez9ZbMBFWeZsskxTkPzGCow"] * 36
> ```

with:

> ```
> N = FundingStream[FS_FPF_ZCG_H3].AddressIndex(NU7ActivationHeight - 1) + 1
> FS_FPF_ZCG_H3.AddressList[0..N-1] = ["t3cFfPt1Bcvgez9ZbMBFWeZsskxTkPzGCow"] * N
> FS_FPF_ZCG_H3.AddressList[N..35] = ["TBD"] * (36 - N)
> ```


# Deployment

This ZIP is proposed to be deployed with NU7.


# Reference implementation

TBD


# References

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)
