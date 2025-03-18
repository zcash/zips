```
  ZIP: Unassigned
  Title: Regtest: Definition of a Local Consensus test mode for Zcash Full-Nodes
  Owners: ZIP Editors
  Original-Authors: Francisco Gindre <pacu@zecdev.org>
  Credits: Daira-Emma Hopwood
           Zancas (Zingo Labs)
           idky137 (Zingo Labs)
  Status: Draft
  Category: Consensus
  Created: 2025-02-26
  License: MIT
  Pull-Request: <https://github.com/zcash/zips/pull/986>
```
# Regtest: Definition of a Local Consensus test mode for Zcash Full-Nodes


## Terminology 

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they 
appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as defined 
in the Zcash protocol specification [^protocol-networks].

## Abstract
Regtest is a testing mode inherited from the Bitcoin node. It provides a way to 
have a consensus node on a local network with a private state that a developer 
can control in order to reproduce certain situations deterministically for 
testing purposes. Regtest, as it was implemented on Zcashd, is similar to a 
“testnet” but without miners and remote peers.

## Motivation
It is necessary to define Regtest mode so that different implementations of Zcash
Full Nodes provide the same capabilities so that testing infrastructure can be 
interoperable. Regtest mode was inherited from Bitcoin functionality and never 
defined in a ZIP due to resource constraints and priorities. Differences between 
Zebra and Zcashd Regtest implementations found by developers involved in Zcashd 
deprecation motivated this ZIP as a way to document existing assumptions, 
expectations and functionalites of Regtest as well as new features that focus 
specifically on Zcash features. 


## Requirements
The scope of this ZIP is to define the behavior of a Zcash full-node when set up 
to run in Regtest mode. It focuses on highlighting and specifying the difference 
in behavior, values, expectations and assumpions in comparison to Testnet. It 
uses the Zcash protocol and existing ZIPs as guiding principles for the document 
structure. It also documents pre-existing and previously *undocumented* requirements, 
constants and values that are present in the Zcashd 6.1.0 implementation and 
`zcash_protocol` crate 0.4.3[^zcash_protocol]. This ZIP should be useful for Core 
Developers working on full node implementations but also a handbook for developers 
and QA testers to make use and take advantage of Regtest functionality to ensure 
test coverage of their codebases and a high quality assurance to Zcash users.

## Non-requirements
This ZIP does not attempt to address how Regtest should be implemented. Details 
on full-node architecture, implementation details, software distribution are out
of scope of this document.

## Specification

### Configuration Parameters
TODO: Gather existing Zcashd and compare them to Zebra parameters.

### Regtest nodes and Network connections
Nodes that start on Regtest mode should never connect to any external peers. 
Localhost connections MUST be enforced. Attempts to  configure a Regtest setup 
in a way that violate this principle should cause a `FatalError` informing the 
developer of the problem an pointing to the relevant documentation. 

### Global Effects on Network Upgrades 
Regtest mode must allow Network Upgrades to occur at configurable arbitrary 
block heights in a way that all one of more of them can be activated at once at 
a given height. Effects from network upgrades activating MUST be guaranteed to 
occur in the  intended order as it is defined on its **Testnet** or **Mainnet** 
implementation. This means that there is a hard requirement that guarantees a 
chronological order of NU's event so that it is not possible to enable a NU prior 
to one of its predecessors. Example: a configuration such as `NU1 -> NU3 -> NU2` 
should raise a critical error and fail the execution of the Regtest environment.
The rationale of this is to avoid unfeasible chain states. 

(TODO: check with Daira-Emma if this is really necessary or whether the ability 
to do such a mess with activation heights is actually a testing feature and not 
a bug.)

## Effects of Regtest mode by ZIP

| ZIP  | Title | Regtest Behavior |
|------|--------------------------------------------------------------|-------------------------------------------------------------|
| 32   | [Shielded Hierarchical Deterministic Wallets](https://github.com/zcash/zips/blob/main/zips/zip-0032.rst) | No change |
| 143  | [Transaction Signature Validation for Overwinter](https://github.com/zcash/zips/blob/main/zips/zip-0143.rst) | No change |
| 155  | [addrv2 message](https://github.com/zcash/zips/blob/main/zips/zip-0155.rst) | Address should only be pointing to localhost |
| 173  | [Bech32 Format](https://github.com/zcash/zips/blob/main/zips/zip-0173.rst) | No changes |
| 200  | [Network Upgrade Mechanism](https://github.com/zcash/zips/blob/main/zips/zip-0200.rst) | See section below |
| 201  | [Network Peer Management for Overwinter](https://github.com/zcash/zips/blob/main/zips/zip-0201.rst) | No changes |
| 202  | [Version 3 Transaction Format for Overwinter](https://github.com/zcash/zips/blob/main/zips/zip-0202.rst) | No changes |
| 203  | [Transaction Expiry](https://github.com/zcash/zips/blob/main/zips/zip-0203.rst) | No changes |
| 205  | [Deployment of the Sapling Network Upgrade](https://github.com/zcash/zips/blob/main/zips/zip-0205.rst) | Change in activation Height |
| 206  | [Deployment of the Blossom Network Upgrade](https://github.com/zcash/zips/blob/main/zips/zip-0206.rst) | Change in activation Height |
| 207  | [Funding Streams](https://github.com/zcash/zips/blob/main/zips/zip-0207.rst) | No changes |
| 208  | [Shorter Block Target Spacing](https://github.com/zcash/zips/blob/main/zips/zip-0208.rst) | See Section below |
| 209  | [Prohibit Negative Shielded Chain Value Pool Balances](https://github.com/zcash/zips/blob/main/zips/zip-0209.rst) | No changes |
| 211  | [Disabling Addition of New Value to the Sprout Chain Value Pool](https://github.com/zcash/zips/blob/main/zips/zip-0211.rst) | No changes |
| 212  | [Allow Recipient to Derive Ephemeral Secret from Note Plaintext](https://github.com/zcash/zips/blob/main/zips/zip-0212.rst) | No changes |
| 213  | [Shielded Coinbase](https://github.com/zcash/zips/blob/main/zips/zip-0213.rst) | No changes |
| 214  | [Consensus rules for a Zcash Development Fund](https://github.com/zcash/zips/blob/main/zips/zip-0214.rst) | No changes |
| 215  | [Explicitly Defining and Modifying Ed25519 Validation Rules](https://github.com/zcash/zips/blob/main/zips/zip-0215.rst) |  No changes |
| 216  | [Require Canonical Jubjub Point Encodings](https://github.com/zcash/zips/blob/main/zips/zip-0216.rst) |  No changes |
| 221  | [FlyClient - Consensus-Layer Changes](https://github.com/zcash/zips/blob/main/zips/zip-0221.rst) |  No changes |
| 224  | [Orchard Shielded Protocol](https://github.com/zcash/zips/blob/main/zips/zip-0224.rst) |  No changes |
| 225  | [Version 5 Transaction Format](https://github.com/zcash/zips/blob/main/zips/zip-0225.rst) |  No changes |
| 236  | [Blocks should balance exactly](https://github.com/zcash/zips/blob/main/zips/zip-0236.rst) | No changes |
| 239  | [Relay of Version 5 Transactions](https://github.com/zcash/zips/blob/main/zips/zip-0239.rst) | No changes |
| 243  | [Transaction Signature Validation for Sapling](https://github.com/zcash/zips/blob/main/zips/zip-0243.rst) | No changes |
| 244  | [Transaction Identifier Non-Malleability](https://github.com/zcash/zips/blob/main/zips/zip-0244.rst) | No changes |
| 250  | [Deployment of the Heartwood Network Upgrade](https://github.com/zcash/zips/blob/main/zips/zip-0250.rst) | Change in activation Height |
| 251  | [Deployment of the Canopy Network Upgrade](https://github.com/zcash/zips/blob/main/zips/zip-0251.rst) | Change in activation Height |
| 252  | [Deployment of the NU5 Network Upgrade](https://github.com/zcash/zips/blob/main/zips/zip-0252.rst) | Change in activation Height |
| 253  | [Deployment of the NU6 Network Upgrade](https://github.com/zcash/zips/blob/main/zips/zip-0253.md) | Change in activation Height |
| 300  | [Cross-chain Atomic Transactions](https://github.com/zcash/zips/blob/main/zips/zip-0300.rst) | No changes |
| 301  | [Zcash Stratum Protocol](https://github.com/zcash/zips/blob/main/zips/zip-0301.rst) | See section below |
| 308  | [Sprout to Sapling Migration](https://github.com/zcash/zips/blob/main/zips/zip-0308.rst) | No changes |
| 316  | [Unified Addresses and Unified Viewing Keys](https://github.com/zcash/zips/blob/main/zips/zip-0316.rst) | [Revision 0] Changes on HRP of String encoding, [Revision 1] See section below |
| 317  | [Proportional Transfer Fee Mechanism](https://github.com/zcash/zips/blob/main/zips/zip-0317.rst) | No changes |
| 320  | [Defining an Address Type to which funds can only be sent from Transparent Addresses](https://github.com/zcash/zips/blob/main/zips/zip-0320.rst) | Changes on HRP of String encoding |
| 321  | [Payment Request URIs](https://github.com/zcash/zips/blob/main/zips/zip-0321.rst) | No changes |
| 401  | [Addressing Mempool Denial-of-Service](https://github.com/zcash/zips/blob/main/zips/zip-0401.rst) | No changes |
| 1014 | [Establishing a Dev Fund for ECC, ZF, and Major Grants](https://github.com/zcash/zips/blob/main/zips/zip-1014.rst) | should include regtest recipients |
| 1015 | [Block Subsidy Allocation for Non-Direct Development Funding](https://github.com/zcash/zips/blob/main/zips/zip-1015.rst) | No changes |
| 2001 | [Lockbox Funding Streams](https://github.com/zcash/zips/blob/main/zips/zip-2001.rst) | No changes |


### Behevior for ZIP-155
Peer-to-peer communications on Regtest MUST be restricted to localhost nodes. 
See "Regtest nodes and Network connections"

### Behaviour for ZIP-200 Network Upgrade Mechanism
Regtest nodes should implement a way to configure parameters such as Network 
Upgrade activation heights and their respective consensus branch IDs. For 
convenience these should be defined on this ZIP and to be used in all libraries 
that enable Regtest testing. Configuration should favor that such values can be 
altered and/or added if necessary, for example to develop a new Network Upgrade.
Regtest client libraries SHOULD accommodate to such flexibility. 

### Behavior for ZIP-208 Shorter Block Target Spacing
In Regtest mode, block generation is dictated by whomever is ordering the node 
o generate one or more new blocks at will. Difficulty adjustments to enforce a 
blocktime MAY be ignored if  the node has been set with that intention. Values 
referred by ZIP-208 such as `BlossomActivationHeight` shall be populated with 
whatever value the regtest mode was configured with. Regtest allows developers 
to set their own Network Upgrade activation heights and  references to Blossom 
activation should be replaced with the value present in the node configuration.

### Behavior for ZIP-301 Zcash Stratum Protocol
Regtest nodes MUST never expose connections or connect to public networks or other 
machines on a private network.

Regtest support of this ZIP MUST ensure that such requirement is enforced and 
guaranteed, failing when a configuration attempts to violate that premise.

### Effects on ZIP-316

#### Revision 0
The HRP for regtest is defined as `uregtest`. Receivers included inside regtest 
UAs MUST also be regtest variants of their type. The example below shows how a 
regtest UA

Example: 
```
uregtest1....
|
|
-> Sapling -> zregtest1...
|
-> orchard -> uregtest1...
```

#### Revision 1
From [Address Expiration Metadata](https://github.com/zcash/zips/blob/main/zips/zip-0316.rst#address-expiration-metadata) section: 
> When honoring an Address Expiry Time, the reason that a sender SHOULD choose a 
`nExpiryHeight` that is expected to occur within 24 hours of the time of transaction 
construction is to, when possible, ensure that the expiry time is respected to 
within a day.

Time is fluid on Regtest mode. Given that blocktimes are reduced there is a 
conflict between expected timespans for address expiration and the real timestamps
of the transactions in a Regtest generated blockchain where a desktop computer can 
generate a block (or more) per second. 

Approaches:

A. Regtest manages a separate clock where the timestamps can appear to be "real"
in terms of the average blocktime per second of mainnet (~72 seconds) for scenarios 
where time is of the essence of the test.

B. Adjust ZIP-316 implementations on regtest so that the expiration window can 
be adjusted according to Regtest block cadence. 

#### Unified Incoming Viewing Keys encoding.
UIVKs MUST be encoded with the `uivkregtest` HRP on Regtest.

#### Unified Full Viewing Keys encoding.
UFVKs MUST be encoded with the `uviewregtest` HRP on Regtest.

### Effects on ZIP-320 (TEX Addresses)

[ZIP-320, Defining an Address Type to which funds can only be sent from Transparent Addresses](https://github.com/zcash/zips/blob/main/zips/zip-0320.rst) 
defines an encoding or transparent-source-only addresses with a `tex` HRP. 
On Regtest that that value MUST be `texregtest`.

## Effects of Regtest mode on protocol definitions

The following section describes how Regtest mode affects definitions present on 
the [Zcash protocol](https://zips.z.cash/protocol/protocol.pdf).
### Constants

#### Coin type:
Regtest reuses Testnet's coin type
```Rust
/// The regtest cointype reuses the testnet cointype
pub const COIN_TYPE: u32 = 1;
```
#### Sapling address encoding
From the Zcash protocol `[^protocol-saplingpaymentaddrencoding]:
> For addresses on Mainnet , the Human-Readable Part (as defined in [ZIP-173](https://zips.z.cash/zip-0173)) 
is “zs”. For addresses on Testnet , the Human-Readable Part is “ztestsapling”.

On Regtest mode this MUST be `zregtestsapling`

#### Sapling Incoming Viewing Keys encoding
From the Zcash protocol `[^protocol-saplinginviewingkeyencoding]:
> For incoming viewing keys on Mainnet, the Human-Readable Part is “zivks”. For 
incoming viewing keys on Testnet, the Human-Readable Part is“zivktestsapling”

On Regtest this value MUST be `zivkregtestsapling`

#### Sapling Full Viewing Keys encoding 
From the Zcash protocol `[^protocol-saplingfullviewingkeyencoding]:
> For full viewing keys on Mainnet, the Human-Readable Part is “zviews”. For 
full viewing keys on Testnet, the
Human-Readable Part is“zviewtestsapling”


On Regtest this value MUST be `zviewregtestsapling`

#### Sapling Spending Keys encoding 
From the Zcash protocol `[^protocol-saplingspendingkeyencoding]:
> For spending keys on Mainnet, the Human-Readable Part is 
`secret-spending-key-main`. For spending keys on Testnet, the Human-Readable Part 
is `secret-spending-key-test`

On Regtest this value MUST be `secret-spending-key-regtest`

#### Sapling Extended Spending Keys encoding8
These keys are defined on the [Sapling Crypto crate](https://docs.rs/sapling-crypto/latest/sapling_crypto/zip32/struct.ExtendedSpendingKey.html).

On Regtest their HRP encoding MUST be `secret-extended-key-regtest`

#### Sapling Extended Viewing Keys encoding
These keys are defined on the [Sapling Crypto crate](https://docs.rs/sapling-crypto/latest/sapling_crypto/zip32/struct.ExtendedFullViewingKey.html), 

On Regtest their HRP encoding MUST be `zxviewregtestsapling`

#### Transparent Address Public Key Script Hash B58 prefix
The prefix for a Base58Check-encoded regtest transparent `PublicKeyHash` MUST be
the same as the testnet prefix.

```Rust
pub const B58_PUBKEY_ADDRESS_PREFIX: [u8; 2] = [0x1d, 0x25];
```
#### Transparent Address ScriptHash Base58 Prefix
/// The prefix for a Base58Check-encoded regtest transparent `ScriptHash` must 
be the same as the testnet prefix
```Rust
pub const B58_SCRIPT_ADDRESS_PREFIX: [u8; 2] = [0x1c, 0xba];
```
#### Sprout payment address encoding
Zcash Protocol `[^protocol-sproutpaymentaddrencoding]` defines:
> Two bytes [0x16, 0x9A], indicating this version of the raw encoding of a Sprout 
shielded payment address onMainnet. (Addresses on Testnet use `[0x16, 0xB6]` 
instead.)

Regtest uses the same prefix as **Testnet**

# References
[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)
[^protocol]: [Zcash Protocol Specification, Version 2022.3.8 or later](protocol/protocol.pdf)
[^protocol-introduction]: [Zcash Protocol Specification, Version 2022.3.8. Section 1: Introduction](protocol/protocol.pdf#introduction)
[^protocol-blockchain]: [Zcash Protocol Specification, Version 2022.3.8. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)
[^protocol-networks]: [Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)
[^zcash_protocol]: [Zcash protocol Rust crate 0.4.3](https://docs.rs/zcash_protocol/0.4.3)