# Permanent Storage vs Risk

A user may prefer to store her funds off-line indefinitely. This allows her maximum flexibility in planning her use of the funds. On the other hand, this requires the Zcash protocol to always support all payment sub-protocols indefinitely.

The risk that older sub-protocols or their implementations no longer work correctly, have security vulnerabilities, or require extensive effort to maintain grows over time. If the protocol supports older sub-protocols indefinitely, the chance that one of the older protocols might be an attack surface for a counterfeit attack or a privacy failure impacts all current users of newer sub-protocols even if they never use older protocols.

Alternatively, older sub-protocols can be removed by removing funds in older protocols, for example by introducing "legacy sub-protocol fees". Doing this would ensure older sub-protocols could eventually be removed which would make the current overall Zcash protocol simpler and safer against the risks of counterfeiting or privacy bugs. However, doing so would prevent users from storing their funds off-line indefinitely.

## Current Zcash Protocol

The current Zcash protocol has never removed funds from older sub-protocols. A more modest step was introduced in [ZIP 211](https://zips.z.cash/zip-0209) which prevents funds from entering the oldest shielded sub-protocol, the Sprout pool.

Because this trade-off and the desire of removing older sub-protocols was not clearly shared around Zcash's launch or early years, it may be likely some significant proportion of users expect or have already planned to store funds off-line indefinitely, which complicates any attempt to shift the Zcash protocol design towards the lower risk of removing old sub-protocols.

## Potential Future Changes

Some design exploration has been discussed in Zcash Arborist protocol development calls about ways to balance these risks by introducing out-of-band redemption of old funds, or introducing the ability to spend old funds in newer proving systems. This area needs more exploration.
