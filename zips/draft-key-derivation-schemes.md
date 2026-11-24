    ZIP: Unassigned
    Title: Legacy Wallet Key-Derivation Behaviors for Fund Recovery
    Owners: Darío Paz <dorianvp@zingolabs.org>
    Credits: Kris Nuttycombe
             Oscar Pepper
             Evan Branigan
    Status: Draft
    Category: Informational
    Created: 2026-02-08
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/1175>
    Pull-Request: <https://github.com/zcash/zips/pull/1176>


# Terminology

This document uses terminology from the Zcash Protocol Specification [^protocol],
BIP 32 [^bip-0032], BIP 39 [^bip-0039], BIP 44 [^bip-0044], ZIP 32 [^zip-0032] and
ZIP 316 [^zip-0316].

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash Protocol Specification [^protocol-networks].

The terms below are to be interpreted as follows:

Account index
: The index at the `account` level of a ZIP 32 or BIP 44 derivation path.

Coin type
: The value at the `coin_type` level of a ZIP 32 or BIP 44 derivation path, as
  registered in SLIP 44 [^slip-0044]. This is 133 for Mainnet and 1 for Testnet.

Diversified address
: One of many addresses that a wallet derives from a single Sapling or Orchard
  full viewing key, each with its own diversifier. One incoming viewing key
  finds the funds of all diversified addresses of that key.

Mnemonic phrase
: A sequence of words that encodes entropy, as specified in BIP 39 [^bip-0039].

BIP 39 seed
: The 64-byte value that the BIP 39 seed derivation function (PBKDF2) calculates
  from a mnemonic phrase and a passphrase.

Phrase entropy
: The bytes that a mnemonic phrase encodes. A wallet gets them when it decodes
  the words of the phrase.

Legacy HD seed
: The 32-byte seed that `zcashd` generated from system randomness and used for
  Sapling key derivation, from v2.0.1 until the upgrade to v4.7.0.

Mnemonic seed
: The name that `zcashd` v4.7.0 and later use for the BIP 39 seed of the wallet's
  emergency recovery phrase.

Legacy account
: The account with index `0x7FFFFFFF` under the mnemonic seed of a `zcashd`
  wallet. It contains the addresses that the `getnewaddress` and
  `z_getnewaddress` RPC methods return.

Legacy derivation
: A key generation or key derivation behavior of an older wallet that a
  recovery tool has to implement to find the funds of that wallet.

Gap limit
: The number of consecutive unused indexes after which a recovery tool stops a
  derivation sequence.

The notation `m_Sapling` and `m_Orchard` is used as in ZIP 32 [^zip-0032] for the
Sapling and Orchard master keys. The notation `m` is the BIP 32 master key. An
apostrophe after an index identifies hardened derivation.


# Abstract

Zcash wallets have used many strategies to generate and derive keys. A recovery
tool finds the funds of an old wallet only if it implements the strategy that
the wallet used.

This ZIP describes the legacy behaviors that are important for fund recovery. It
specifies, for each wallet, the seed material, the derivation paths, the rules
that select the next index, and the procedure to recover funds. The first
version includes `zcashd`, Zecwallet Lite, and wallets that are based on the
`zcash_client_backend` and `zcash_client_sqlite` crates.

Consensus rules are unchanged. The privacy implications apply to recovery tools:
recovery uses many viewing keys and many addresses for one user, which can
reveal to an observer that these addresses have one owner.


# Motivation

Users can have seed material, wallet files, or partial backups that older
wallets made. Most recovery tools implement one scheme: a BIP 39 mnemonic
phrase, a BIP 39 seed, ZIP 32 derivation, and diversified addresses. Funds that
an older scheme created are invisible to such a tool. The user then concludes
that the funds are lost.

Two examples:

- A `zcashd` wallet from before v4.7.0 gets an emergency recovery phrase at the
  upgrade. A different wallet that imports this phrase finds only the funds of
  the unified accounts. The Sapling funds from before the upgrade are at other
  paths, as are the funds at `getnewaddress` and `z_getnewaddress` addresses.
- Zecwallet Lite made a new spending authority each time the user asked for a
  new Sapling address. A wallet that scans account 0 finds only the funds of the
  first address.

`zcashd` is deprecated, and Zecwallet Lite is unmaintained. The original
software becomes more difficult to run each year. A specification of these
behaviors lets implementers:

- identify the recovery strategies that apply to a given wallet;
- write tools that recover funds independently of the original wallet software;
- recognize these patterns when they design a new wallet.


# Privacy Implications

The implications below apply to software that implements the recovery
procedures in this document.

- Recovery can use many viewing keys and many transparent addresses for one
  user. A server that receives them (for example, a light wallet server that
  answers transparent address queries) learns that the addresses have one owner.
  Recovery tools need to keep such queries to a minimum.
- At the completion of recovery, the user frequently moves all found funds to
  one new wallet. This transaction connects the transparent addresses on chain. It also
  reveals the value that moves between pools.
- Recovered seed material, phrase entropy, and derived keys are as sensitive as
  the original wallet. The legacy HD seed of a `zcashd` wallet has the same
  entropy as its emergency recovery phrase: a person who gets one of them also
  has the other.
- A viewing key for one Zecwallet Lite Sapling address reveals the funds of that
  address only. Recovery uses one viewing key for each address.


# Requirements

- An implementer can derive, from the seed material and this document alone,
  each key that the documented wallet derived.
- The document identifies the funds that exist only in a wallet file, and the
  backup that is necessary for those funds.
- The document identifies the wallet versions and products that each behavior
  applies to.
- An implementer can do each procedure with independent software.


# Non-requirements

- Wallet file formats (for example `wallet.dat` and the Zecwallet Lite wallet
  file) are out of scope. The reference implementations parse these formats.
- The method that a recovery tool uses to move the recovered funds is out of
  scope.
- New wallets are out of scope. The behaviors in this ZIP are for recovery only.


# Specification

This ZIP is informational. Each subsection describes what a wallet did, then
what a recovery tool needs to do.

In all derivation paths, `coin_type` is the coin type of the network of the
wallet.

## `zcashd`

### Summary of `zcashd` behavior

The key generation of the `zcashd` wallet has three periods. The table gives the
source of new keys in each period.

| Key type    | Before v2.0.1 | v2.0.1 until v4.7.0 | v4.7.0 and later |
|-------------|---------------|---------------------|------------------|
| Transparent | Random        | Random              | Mnemonic seed    |
| Sprout      | Random        | Random              | Random           |
| Sapling     | Random        | Legacy HD seed      | Mnemonic seed    |
| Orchard     | None          | None                | Mnemonic seed    |

"Random" means that the wallet generated each key independently from system
randomness. Such a key exists only in the wallet file.

- Transparent keys were random until v4.7.0. The wallet generated them ahead of
  time and kept them in a keypool.
- Sprout spending keys were random in all versions.
- Sapling keys from v2.0.0 were random. Version 2.0.0 had Sapling as an
  experimental Testnet feature.
- From v2.0.1, the wallet derived Sapling keys with ZIP 32 from the legacy HD
  seed [^zcashd-2.0.1]. The wallet generated this seed directly from system
  randomness.
- From v4.7.0, the wallet has an emergency recovery phrase. It derives all new
  transparent, Sapling and Orchard keys from the mnemonic seed [^zcashd-4.7.0].

A wallet that the user made before v4.7.0 keeps all its old keys through each
upgrade. One `wallet.dat` file can contain keys from all three periods.

### Seed material of `zcashd`

#### Legacy HD seed

From v2.0.1, `zcashd` generated an HD seed for each wallet that had none. This
occurred when `zcashd` loaded the wallet, or, for an encrypted wallet, when the
user first unlocked it. The seed is 32 bytes from the system random number
generator. `zcashd` gave these bytes, unmodified, to the ZIP 32 Sapling master
key generation.

Before v4.7.0, the backup of this seed was the `wallet.dat` file or the
`z_exportwallet` file.

#### Emergency recovery phrase and mnemonic seed

`zcashd` v4.7.0 generates the emergency recovery phrase for each wallet that has
none. This occurs when `zcashd` loads the wallet, or, for an encrypted wallet,
when the user first unlocks it. The phrase is an English BIP 39 mnemonic phrase
of 24 words, which encodes 32 bytes of phrase entropy.

The source of the phrase entropy depends on the wallet:

- For a wallet with a legacy HD seed, the phrase entropy is the 32 bytes of the
  legacy HD seed. The phrase is an encoding of that seed.
- For all other wallets, the phrase entropy is 32 bytes from the system random
  number generator.

`zcashd` then calculates the mnemonic seed, which is the BIP 39 seed of the
phrase with the empty passphrase. `zcashd` accepts the phrase only if the
mnemonic seed gives a valid unified spending key for account 0 and valid
transparent keys for the legacy account. For a rejected phrase:

- in the random case, `zcashd` generates new entropy and tries again;
- in the legacy HD seed case, `zcashd` adds 1 (modulo 256) to the first byte of
  the entropy and tries again, a maximum of 256 times.

The probability of a rejected phrase is negligible. For almost all wallets with
a legacy HD seed, the phrase entropy is equal to that seed.

Such a wallet has two seeds that come from one phrase:

| Seed           | How to get it from the phrase                       | Keys                                    |
|----------------|-----------------------------------------------------|-----------------------------------------|
| Legacy HD seed | Decode the words to the 32 bytes of phrase entropy  | Sapling keys derived before the upgrade |
| Mnemonic seed  | BIP 39 seed derivation, empty passphrase (64 bytes) | All keys derived after the upgrade      |

<div class="warning"></div>

The legacy HD seed is the phrase entropy, which is outside the BIP 39 seed
derivation. A tool that calculates only the BIP 39 seed of the phrase finds only
the keys from after the v4.7.0 upgrade.

After the upgrade, `zcashd` generates new addresses only when the user has
confirmed the backup of the phrase. The user gets the phrase from the
`z_exportwallet` file and confirms it with `zcashd-wallet-tool`. The option
`-walletrequirebackup=false` disables this requirement.

### Derivation and address generation in `zcashd`

#### Sapling keys from the legacy HD seed (v2.0.1 until v4.7.0)

Each time the user ran `z_getnewaddress` for a Sapling address, the wallet
derived a new extended spending key from the legacy HD seed, at this path:

    m_Sapling / 32' / coin_type' / k'

The index `k` comes from a counter in the wallet file (`saplingAccountCounter`).
The first value is 0, and each derivation adds 1. The wallet omitted an index
whose key it already had.

The RPC method returned the default diversified address of that key. This was
the only address of the key that the wallet gave to the user. Each Sapling
address has its own spending authority, at its own ZIP 32 account index.

#### Unified accounts from the mnemonic seed (v4.7.0 and later)

`z_getnewaccount` makes accounts from the mnemonic seed with indexes 0, 1, 2,
and higher. Derivation follows ZIP 32 [^zip-0032] and ZIP 316 [^zip-0316].
`z_getaddressforaccount` returns diversified unified addresses for an account.
The transparent receiver of a unified address has a BIP 44 address index that is
equal to the diversifier index of the unified address.

#### Sapling addresses in the legacy account (v4.7.0 and later)

Each time the user runs `z_getnewaddress` for a Sapling address, the wallet
derives a new extended spending key from the mnemonic seed, at this path:

    m_Sapling / 32' / coin_type' / 0x7FFFFFFF' / i'

The last level is the `address_index` level that ZIP 32 permits below the
account level [^zip-0032-sapling-key-path]. `zcashd` uses hardened derivation
for it.

The index `i` comes from a counter in the wallet file. The first value is 0, and
each derivation adds 1. The wallet omits an index whose key it already has. The
RPC method returns the default diversified address of the key. Each such address
has its own spending authority.

Unified accounts have indexes that begin at 0. The account index `0x7FFFFFFF`
keeps the legacy keys apart from them.

#### Transparent addresses in the legacy account (v4.7.0 and later)

From v4.7.0, `getnewaddress` derives the key from the mnemonic seed with BIP 44,
on the external chain of the legacy account:

    m / 44' / coin_type' / 0x7FFFFFFF' / 0 / i

The internal chain of the legacy account supplies the transparent change
addresses and the keypool keys:

    m / 44' / coin_type' / 0x7FFFFFFF' / 1 / i

`zcashd` takes the addresses for miner rewards from the keypool.

The wallet file has one counter for each chain. The first value is 0, and each
derivation adds 1. The wallet omits an index for which BIP 32 derivation fails.

When v4.7.0 generates the mnemonic seed, it replaces the unused random keys in
the keypool with internal chain keys. Random keys that the wallet already gave
to the user remain in the wallet.

#### Semantics of the legacy transparent pool

`zcashd` treats all transparent funds outside the unified accounts as one pool.
This pool contains the funds at:

- random keys from before v4.7.0;
- imported transparent keys;
- legacy account keys, on the external and the internal chain.

An RPC method that spends from this pool (for example `sendtoaddress` or
`sendmany`) can select inputs from any of these addresses. It sends the change
to a new internal chain address. Funds that arrived at one address can be at a
different address later. A recovery tool needs to scan all keys of the
pool.

TODO: confirm the exact list of RPC methods and the `ANY_TADDR` behavior of
`z_sendmany` against the `zcashd` source.

### Recovery of `zcashd` funds

#### Recovery from the emergency recovery phrase

A recovery tool that has the emergency recovery phrase needs to do all the steps
below. The counters exist only in `wallet.dat`. For this reason, the tool
selects a gap limit for each step.

1. Calculate the mnemonic seed: the BIP 39 seed of the phrase, with the empty
   passphrase.
2. Unified accounts: for account indexes 0, 1, 2, and higher, derive the unified
   full viewing key from the mnemonic seed. Scan for Sapling, Orchard and
   transparent funds.
3. Legacy account, Sapling: for `i` = 0, 1, 2, and higher, derive the key at
   `m_Sapling / 32' / coin_type' / 0x7FFFFFFF' / i'` from the mnemonic seed. Scan
   with its viewing key.
4. Legacy account, transparent: for `i` = 0, 1, 2, and higher, derive the keys
   at `m / 44' / coin_type' / 0x7FFFFFFF' / 0 / i` and
   `m / 44' / coin_type' / 0x7FFFFFFF' / 1 / i` from the mnemonic seed. Find the
   unspent outputs at their addresses.
5. Sapling keys from before the upgrade: decode the phrase to its 32 bytes of
   phrase entropy. Use these bytes as the legacy HD seed. For `k` = 0, 1, 2, and
   higher, derive the key at `m_Sapling / 32' / coin_type' / k'` from the legacy
   HD seed. Scan with its viewing key.

Step 5 finds funds only for a wallet that had a legacy HD seed, that is, a
wallet from v2.0.1 or later that the user updated to v4.7.0.

In step 5, the first byte of the phrase entropy can be different from the first
byte of the legacy HD seed, as "Emergency recovery phrase and mnemonic seed"
specifies. The `getwalletinfo` RPC method gives the fingerprint of the legacy HD
seed (`legacy_seedfp`). A tool that has this fingerprint subtracts 1 (modulo
256) from the first byte, a maximum of 255 times, until the fingerprint of the
candidate seed is equal to it.

#### Funds that need the wallet file

These keys exist only in the wallet file:

- all Sprout keys;
- transparent keys that the wallet generated before v4.7.0;
- Sapling keys that v2.0.0 generated on Testnet;
- keys that the user imported (for example with `importprivkey` or
  `z_importkey`).

Recovery of these funds needs the `wallet.dat` file, or the keys in a
`z_exportwallet` or `dumpwallet` file. The v4.7.0 release notes recommend that
users move funds from old addresses to newly generated addresses, to make the
phrase sufficient for all funds [^zcashd-4.7.0].

#### Recovery from a `wallet.dat` file

A tool that has the `wallet.dat` file reads all keys directly, with their HD key
paths and seed fingerprints. This method recovers all funds of the wallet,
including the random keys. The reference implementation uses this method.

### Open questions for `zcashd`

- ZIP 32 gives v4.6.0 as the first version with Sapling addresses in the legacy
  account [^zip-0032-sapling-key-path]. The release notes and the source give
  v4.7.0. One of the two documents needs a correction.
- Recommend gap limits for steps 2 to 5.
- Describe in more detail the wallets that were encrypted at the time of each
  upgrade.

## Zecwallet Lite

### Scope of the Zecwallet Lite behavior

This section applies to the products that used the `zecwalletlitelib` light
client library [^zecwallet-light-cli]:

- Zecwallet Lite for desktop;
- Zecwallet Lite for Android and iOS (`zecwallet-mobile`);
- the command-line client `zecwallet-light-cli`;
- forks of that library, for example `zwl-lib` [^zwl-lib].

Zecwallet FullNode was a user interface for the `zcashd` RPC interface. Its keys
follow the `zcashd` section above.

### Summary of Zecwallet Lite behavior

Each time the user asked for a new Sapling address, Zecwallet Lite derived a new
spending key at the next ZIP 32 account index. A wallet with $N$ Sapling
addresses has $N$ independent Sapling spending authorities, at account indexes
0 to $N - 1$.

### Seed material of Zecwallet Lite

Zecwallet Lite follows BIP 39:

- A new wallet gets 32 bytes of entropy from the system random number generator.
- The wallet file contains these 32 bytes of entropy.
- The seed phrase that the user sees is the English BIP 39 mnemonic phrase of 24
  words for this entropy.
- The seed for key derivation is the BIP 39 seed (64 bytes) of that phrase, with
  the empty passphrase.

The phrase is sufficient to derive all keys that the wallet derived.

### Derivation and address generation in Zecwallet Lite

All paths below begin at the BIP 39 seed. In each rule, `n` is 0 for the first
key of a type. For each subsequent key, `n` is the highest existing index of
that type plus 1.

| Key type    | Path                                 | Address                                |
|-------------|--------------------------------------|----------------------------------------|
| Sapling     | `m_Sapling / 32' / coin_type' / n'`  | Default diversified address of the key |
| Transparent | `m / 44' / coin_type' / 0' / 0 / n`  | P2PKH address of the key               |
| Orchard     | `m_Orchard / 32' / coin_type' / n'`  | Orchard receiver of a unified address  |

- The Sapling rule is the legacy behavior. The path is a valid ZIP 32 account
  path, in which the wallet used the account level as an address counter.
- The transparent rule is the external chain of BIP 44 account 0.
- The Orchard rule applies to the library versions that have Orchard. The
  account level is an address counter here also.

TODO: identify the first version of each product that has Orchard.

Each key type has its own counter.

The wallet has a gap rule (`GAP_RULE_UNUSED_ADDRESSES`) for Sapling and
transparent addresses. Its value is 5 on desktop and 0 on Android and iOS. On
desktop, when the wallet sees that one of the last 5 derived addresses of a type
was used, it derives more addresses of that type until 5 unused addresses follow
the last used address. On Android and iOS, the wallet
derives a new address only when the user asks for one.

The wallet can also contain imported keys, which are independent of the seed.

### Affected versions of Zecwallet Lite

The Sapling behavior is in the last published version of `zecwallet-light-cli`
[^zecwallet-light-cli]. It is in the `zwl-lib` fork from v1.7.12 or earlier
[^zwl-lib], and in `zecwallet-mobile` up to version 1.8.8 or later
[^zingolib-2060]. All examined versions of the library have this behavior.
Recovery tools need to treat every version that offers more than one Sapling
address as affected.

TODO: identify the first affected version of each product.

### Recovery of Zecwallet Lite funds

A recovery tool that has the seed phrase needs to do these steps:

1. Calculate the BIP 39 seed of the phrase, with the empty passphrase.
2. Sapling: for `i` = 0, 1, 2, and higher, derive the extended spending key at
   `m_Sapling / 32' / coin_type' / i'`. Scan with its viewing key.
3. Transparent: for `i` = 0, 1, 2, and higher, derive the key at
   `m / 44' / coin_type' / 0' / 0 / i`. Find the unspent outputs at its address.
4. Orchard: for `i` = 0, 1, 2, and higher, derive the Orchard spending key at
   `m_Orchard / 32' / coin_type' / i'`. Scan with its viewing key.

The tool stops a sequence at the gap limit. A user can make an address and leave
it unused, which makes a gap limit of 1 or more necessary. The desktop gap rule
makes 5 the minimum for desktop wallets. Mobile users made addresses with a
button, in any quantity. The tool needs to let the user select a larger limit.

Step 2 requires trial decryption of the full chain for each index. A tool can
use many viewing keys in one pass over the chain.

<div class="note"></div>

When the mobile application restores a wallet from the seed phrase, it derives
the first addresses only, because the gap rule is 0 on Android and iOS. Funds at
Sapling addresses with a higher index are absent from the balance. These funds
are still spendable, and the procedure above finds them.

Funds at imported keys need the wallet file or the imported keys.

A current wallet that imports the phrase and scans account 0 finds the funds of
Sapling index 0, transparent index 0, and Orchard index 0. To find all funds,
the wallet needs to import each index `i` as a separate ZIP 32 account.

## `zcash_client_backend` and `zcash_client_sqlite`

Wallets that are based on the `zcash_client_backend` and `zcash_client_sqlite`
crates [^librustzcash] have used BIP 39 mnemonic phrases for key derivation in
all versions. Accounts follow ZIP 32, and addresses follow ZIP 316.

The transparent addresses of these wallets get their indexes from three rules:

- The default transparent address of an account is at child index 0 of the BIP
  44 external chain: `m / 44' / coin_type' / account' / 0 / 0`.
- Sequential BIP 44 derivation gives more transparent receivers, each at the
  next address index.
- Unified address derivation, as ZIP 316 specifies, also gives transparent
  receivers. Each one has a BIP 44 address index that is equal to the
  diversifier index of the unified address.

Diversifier indexes can have large gaps between them. A recovery tool needs a
transparent gap limit that allows for this.

TODO: this section comes from review comments on the pull request. Verify it
against the source. Add the crate versions for each behavior, the ephemeral
(ZIP 320) address chain, and the gap limits that the crates use.


# Reference implementation

- zexcavator [^zexcavator] is a wallet recovery tool. It will implement the
  recovery procedures of this ZIP.
- The parser in `zecwallet-utils` [^zecwallet-utils] reads Zecwallet Lite wallet
  files. It gets the entropy and the derived keys with their indexes.


# Open issues

- Issue #1175 proposes that this ZIP describes all historic and present key
  generation schemes, and replaces issue #503. More wallets need sections (for
  example the mobile SDK wallets, YWallet, and hardware wallets).
- The open questions and TODO items in each wallet section.
- Decide if the recovery procedures use BCP 14 conformance key words.


# Acknowledgements

Kris Nuttycombe opened issue #1175, which is the motivation for this ZIP. Kris
also supplied the details of the `zcashd` v4.7.0 upgrade and of the
`zcash_client_sqlite` behavior. Oscar Pepper and the Zingo Labs team analyzed
the Zecwallet Lite derivation [^zingolib-2060]. Evan Branigan traced the
derivation and gap rule in `zwl-lib`.


# References

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0032]: [ZIP 32: Shielded Hierarchical Deterministic Wallets](zip-0032.rst)

[^zip-0032-sapling-key-path]: [ZIP 32: Shielded Hierarchical Deterministic Wallets. Section "Sapling key path"](zip-0032.rst#sapling-key-path)

[^zip-0316]: [ZIP 316: Unified Addresses and Unified Viewing Keys](zip-0316.rst)

[^bip-0032]: [BIP 32: Hierarchical Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)

[^bip-0039]: [BIP 39: Mnemonic code for generating deterministic keys](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)

[^bip-0044]: [BIP 44: Multi-Account Hierarchy for Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)

[^slip-0044]: [SLIP 44: Registered coin types for BIP-0044](https://github.com/satoshilabs/slips/blob/master/slip-0044.md)

[^zcashd-2.0.1]: [zcashd v2.0.1 release notes: "Hierarchical Deterministic Key Generation for Sapling"](https://github.com/zcash/zcash/blob/master/doc/release-notes/release-notes-2.0.1.md)

[^zcashd-4.7.0]: [zcashd v4.7.0 release notes: "Emergency Recovery Phrases"](https://github.com/zcash/zcash/blob/master/doc/release-notes/release-notes-4.7.0.md)

[^zecwallet-light-cli]: [zecwallet-light-cli: Zecwallet light client library and command-line interface](https://github.com/adityapk00/zecwallet-light-cli)

[^zwl-lib]: [zwl-lib: fork of the Zecwallet light client library](https://github.com/zingolabs/zwl-lib)

[^zingolib-2060]: [zingolib issue 2060: address_index level (legacy) sapling key derivation](https://github.com/zingolabs/zingolib/issues/2060)

[^librustzcash]: [librustzcash: Rust crates for Zcash, which include zcash_client_backend and zcash_client_sqlite](https://github.com/zcash/librustzcash)

[^zexcavator]: [zexcavator: Zcash wallet recovery tool](https://github.com/zingolabs/zexcavator)

[^zecwallet-utils]: [zecwallet-utils: parser for Zecwallet Lite wallet files](https://github.com/zingolabs/zecwallet-utils/tree/main/crates/parser)
