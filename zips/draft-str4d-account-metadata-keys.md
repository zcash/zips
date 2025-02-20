
    ZIP: Unassigned
    Title: Account Metadata Keys
    Owners: Jack Grigg <jack@electriccoin.co>
            Daira-Emma Hopwood <daira@electriccoin.co>
            Kris Nuttycombe <kris@electriccoin.co>
    Status: Draft
    Category: Standards / Wallet
    Created: 2025-02-18
    License: MIT


# Terminology

The key words "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.


# Abstract

This ZIP specifies the key tree for Account Metadata Keys. These are derived
from the same seed as a ZIP 32 [^zip-0032] account, and can be used by wallets
to derive encryption keys for local / off-chain metadata.


# Motivation

A wallet's main data source is the Zcash chain: from this it can detect notes
received by an account, determine whether those notes are spent, build witnesses
for spending, recover on-chain memo data, and so on. However, wallets also
generate significant quantities of off-chain metadata as they are used, such as:

- Local annotations about transactions in the wallet.
- Mappings between Zcash addresses and user-meaningful recipient names.
- The exchange rate from ZEC to another currency that was used to determine how
  much ZEC to send in a payment.

This metadata is valuable to users, and highly desirable to ensure to be backed up.
If the user's device is wiped or lost and the user recovers their wallet from a
backed-up mnemonic phrase, they will lose all of this metadata if it is not
stored somewhere.

For other kinds of phone data, it is expected by users that their phone's normal
backup storage will have saved (most of) their data, such that access to e.g.
the associated Apple or Google account will be sufficient for data recovery.
However, metadata such as mappings between Zcash addresses and recipient names can
be particularly sensitive, meaning that users may not want these to be backed up
unencrypted in their phone's normal backup storage. Similarly, the inability to
alter on-chain data means that permanently storing metadata in transaction memo
fields may also not be an option.

Additionally, it is currently the case that users only need to back up a single
secret (a mnemonic seed phrase), once, in order to recover all information for
accounts derived from that secret. If metadata were encrypted using independent
key material, these keys would also need to be backed up, leading to fragility
of wallet restoration.


# Requirements

- The user should not need to update their existing backups of secret material.
- It should be possible to store metadata about accounts for which we don't
  control spend authority (i.e. imported UFVKs).
- The key tree must be future-extensible.


# Specification

## Metadata key tree

This ZIP registers the following ZIP 32 Registered Key Derivation [^zip-0032-rkd]
tree:

- $\mathsf{ContextString} = \texttt{“MetadataKeys”}$
- ZIP number: TBD

The tree has the following general structure, specified in more detail below:

- $m_{\mathsf{metadata}}$: Metadata Key tree
  - $m_{\mathsf{metadata}} / TBD' / \mathsf{coinType}' / \mathsf{account}'$ - Account Metadata Key
    - $\ldots / 0'$ - Account-level Inherent Metadata Key
      - $\ldots / \ldots$ - (Reserved for future updates to this ZIP)
      - $\ldots / (\mathtt{0x7FFFFFFFF}', \mathsf{PrivateUseSubject})$ - Private-use Inherent Metadata Key
    - $\ldots / 1'$ - Account-level External Metadata Key
      - $\ldots / (0', \mathsf{FVKTypedItem})$ - Imported UFVK Metadata Key
        - $\ldots / \ldots$ - (Reserved for future updates to this ZIP)
        - $\ldots / (\mathtt{0x7FFFFFFFF}', \mathsf{PrivateUseSubject})$ - Private-use External Metadata Key
      - $\ldots / \ldots$ - (Reserved for future updates to this ZIP)
    - $\ldots / \ldots$ - (Reserved for future updates to this ZIP)

Non-leaf keys in the key tree MUST NOT be used directly to encrypt metadata.
Encryption keys are leaves in this key tree. The sole exception to this is
private-use keys (for which part of their key derivation is outside the scope of
this specification): encryption keys MAY be derived from the private-use key
leaves.

### Account Metadata Key

The Account Metadata Key is the root of a subtree that corresponds to a ZIP 32
account represented elsewhere in the overall tree. It is derived from the seed
$\mathsf{S}$ as:

$\mathsf{AccountMetadataKey} = \mathsf{CKDreg}(\mathsf{CKDreg}(\mathsf{RegKD}(\texttt{“MetadataKeys”}, \mathsf{S}, \mathsf{ZipNumber}), \mathsf{coinType}, [\,]), \mathsf{account}, [\,])$

or, in path notation:

```
m_metadata / TBD' / coin_type' / account'
```

### Inherent metadata keys

The Account-level Inherent Metadata Key's subtree contains keys used for
metadata associated with the Account Metadata Key's corresponding account. The
key is derived as:

$\mathsf{CKDreg}(\mathsf{AccountMetadataKey}, 0, [\,])$

### External metadata keys

The Account-level External Metadata Key's subtree contains keys used for
metadata associated with imported UFVKs. Unlike the inherent metadata keys which
can leverage the inherent domain separation provided by the account index, here
domain separation between metadata keys is provided by the UFVKs themselves.

As UFVKs may in general change over time (due to the inclusion of new
higher-preference FVK items, or removal of older deprecated FVK items), there is
no guarantee that the exact same set of FVK items will be present at both backup
creation time and recovery time. Instead, the most preferred FVK item within a
UFVK is used as the domain separator, and the Imported UFVK Metadata Key is
derived as:

$\mathsf{CKDreg}(\mathsf{CKDreg}(\mathsf{AccountMetadataKey}, 1, [\,]), 0, \mathsf{FVKTypedItem})$

where $\mathsf{FVKTypedItem}$ is the encoding of the most preferred FVK
item within the ZIP 316 raw encoding of a UFVK. [^zip-0316]

Usage of the Imported UFVK Metadata Key trees SHOULD follow ZIP 316 preference
order: [^zip-0316]

- For encryption-like usage, the key tree corresponding to the most preferred
  FVK item within a UFVK SHOULD be used.
- For decryption-like usage, each key tree SHOULD be tried in preference order
  until metadata can be recovered. If metadata is recovered via an FVK item that
  is not the most preferred, wallets SHOULD update their metadata backups by
  re-encrypting the metadata using the key tree corresponding to the most
  preferred FVK item.

## Standardised metadata protocols

The following metadata protocols have been standardised:

- None at time of writing.

The remaining range of child indices from 0 to $\texttt{0x7FFFFFFFE}$ inclusive
are reserved for future updates to this ZIP. Wallet developers can propose new
standardised metadata protocols by writing a 2000-series ZIP that specifies the
protocol as an update to this ZIP.

## Private-use metadata keys

In some contexts there is a need for deriving ad-hoc key trees for private use
by wallets, without ecosystem coordination and without any kind of compatibility
guarantees. This ZIP reserves child index $\mathtt{0x7FFFFFFFF}$ (the maximum
valid hardened child index) within its key tree for this purpose.

- Let $K$ be either the Account-level Inherent Metadata Key, or an Imported UFVK
  Metadata Key.
- Let $\mathsf{PrivateUseSubject}$ be a globally unique non-empty sequence of at
  most 252 bytes that identifies the desired private-use context.
- Return $\mathsf{CKDreg}(K, \mathtt{0x7FFFFFFFF}, \mathsf{PrivateUseSubject})$

:::warning
It is the responsibility of wallet developers to ensure that they do not use
colliding $\mathsf{PrivateUseSubject}$ values, and to analyse their private use for
any security risks related to potential cross-protocol attacks (in the event that
two wallet developers happen to select a colliding $\mathsf{PrivateUseSubject}$).
Wallet developers that are unwilling to accept these risks SHOULD propose new
standardised metadata protocols instead, to benefit from ecosystem coordination
and review.
:::


# Reference implementation

- https://github.com/Electric-Coin-Company/zcash-android-wallet-sdk/pull/1686


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0032]: [ZIP 32: Shielded Hierarchical Deterministic Wallets](zip-0032.rst)

[^zip-0032-rkd]: [ZIP 32: Shielded Hierarchical Deterministic Wallets, Section: Registered key derivation](zip-0032.rst#specification-registered-key-derivation)

[^zip-0316]: [ZIP 316: Unified Addresses and Unified Viewing Keys](zip-0316.rst)
