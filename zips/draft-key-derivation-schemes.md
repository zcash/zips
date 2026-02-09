```
ZIP: TBD
Title: Legacy Wallet Key-Derivation Behaviors for Fund Recovery
Owners: Darío Paz <dorianvp@zingolabs.org>
        TBD
Credits: Kris Nuttycombe
Status: Draft
Category: Informational
Created: 2026-02-08
License: MIT
Pull-Request: <https://github.com/zcash/zips/pull/???>
```

# Terminology

This document uses terminology from the Zcash Protocol Specification and ZIP 32 [^ZIP32]. In particular:

`account index`: The ZIP 32 account index used to derive account-level spending keys.

`diversifier` / `diversified address`: A change in receiver encoding that allows generating many addresses from the same Sapling spending key (rather than generating new keys).

`legacy derivation`: Any historical wallet key generation/derivation behavior that differs from current best practice (e.g., BIP 39 seed phrases [^BIP-0039] + ZIP 32 HD derivation, and diversified addresses).

# Abstract

Over Zcash’s history, wallets have used multiple strategies to generate and derive keys. This ZIP documents select legacy behaviors that are relevant to fund recovery and wallet interoperability, with an initial focus on behaviors used by zcashd and Zecwallet Lite.

# Motivation

Users may possess seed material, wallet files, or partial backups produced by older wallets. If modern recovery tooling assumes today’s conventions (BIP 39 mnemonic → seed → ZIP 32 derivation, plus diversified addresses), it may fail to detect funds created under older schemes.

Documenting legacy behaviors helps implementers:

- Identify which recovery strategies to attempt given a wallet’s provenance.
- Avoid repeating past mistakes (e.g., generating new accounts when diversified addresses should be used).
- Build interoperable tooling that can recover funds without requiring the original wallet software.

# Specification

This ZIP is informational: it does not change consensus rules. It records historical wallet behaviors and recovery-relevant implications.

# Wallet behaviors

## `zcashd`

### Summary

Historically, `zcashd` generated keys from system randomness.

Starting in `zcashd` v4.7.0, the wallet introduced an “emergency recovery phrase” and began deriving all new addresses from the HD seed derived from that phrase using HD wallet functionality described in ZIP 32 and ZIP 316.

### Seed material

For Sapling, `zcashd` implemented HD derivation according to ZIP 32, but used a seed generated directly from system randomness, rather than seed material derived from a BIP 39 mnemonic phrase.

In `zcashd` v4.7.0, the wallet added support for deriving the wallet’s HD seed from a mnemonic phrase (BIP 39) and referred to the HD seed derived from the emergency recovery phrase as the wallet’s “mnemonic seed”.

### Derivation / address generation

Sapling keys are derived using ZIP 32.

After v4.7.0, new addresses are derived from the mnemonic seed using ZIP 32 and ZIP 316.

For legacy RPC behavior such as `z_getnewaddress`, `zcashd` derives Sapling addresses under a high account index `account = 0x7FFFFFFF` to avoid collision with Sapling addresses for account 0.

### Recovery implications

Recovery tooling may need to support Sapling HD derivation from wallet-internal seed material that is not reproducible from a BIP 39 mnemonic.

Additionally, recovery tooling that imports the zcashd emergency recovery phrase into other wallets may fail to discover funds received to Sapling addresses generated via `z_getnewaddress`, unless it also scans the legacy account 0x7FFFFFFF.

### Notes / TODOs

- Add references.
- Document the v4.7.0+ migration flow in more detail (how/when the emergency recovery phrase is generated, confirmation requirement, export mechanism via `z_exportwallet`, `zcashd-wallet-tool` behavior).
- Specify the exact derivation path structure used for the legacy account and any gap-limit expectations for recovery.

## Zecwallet Lite

### Summary

Zecwallet Lite incorrectly generated “new Sapling addresses” by deriving fresh accounts (incrementing ZIP 32 account index) when it should have generated diversified addresses from the same Sapling spending key.

### Seed material

(TODO: document whether mnemonic/seed originates from BIP 39 and how it was stored/encoded.)

### Derivation / address generation

Observed behavior:

**Expected**: same account spending key → many diversified addresses

**Actual**: new account index → new spending key → address

### Recovery implications

Funds may exist on addresses derived from multiple sequential account indices. Recovery tooling may need to scan across a range of account indices (a “gap limit” policy) even when a user believes they used “one account”.

### Notes / TODOs

- Identify affected versions/commits.
- Specify exact rule: when does ZWL increment account index, and by how much?
- Clarify relationship between transparent vs shielded indexes (if applicable).

## `zcash_client_sqlite`

TBD

# Security and Privacy Considerations

This ZIP documents behaviors that may expand the search space required for recovery (e.g., scanning multiple account indices). Implementations should:

- Avoid leaking derived addresses unnecessarily (e.g., through network queries).
- Provide user-visible controls for scan bounds (e.g., maximum account index / gap limit).
- Treat recovered seed material and derived keys as highly sensitive.

# Reference Implementation

None.

# Backwards Compatibility

Not applicable (informational).

# Acknowledgements

This ZIP was motivated by issue #1175 opened by Kris Nuttycombe.

# References

[^ZIP32]: [ZIP-32: Shielded Hierarchical Deterministic Wallets](zip-0032.rst)

[^BIP-0039]: [BIP 39: Mnemonic code for generating deterministic keys](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
