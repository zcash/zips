```
  ZIP: Unassigned
  Title: Regtest: Definition of a Local Consensus Test Mode for Zcash Full Nodes
  Owners: Francisco Gindre <pacu@zecdev.org>
  Original-Authors: Francisco Gindre <pacu@zecdev.org>
  Credits: Daira-Emma Hopwood
           Zancas (Zingo Labs)
           idky137 (Zingo Labs)
           Kris Nuttycombe
  Status: Draft
  Category: Informational
  Created: 2025-02-26
  License: MIT
  Pull-Request: <https://github.com/zcash/zips/pull/986>
```

# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY",
"REQUIRED", "SHALL", "SHALL NOT", "RECOMMENDED", "NOT RECOMMENDED",
and "OPTIONAL" in this document are to be interpreted as described in
BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted
as defined in the Zcash protocol specification [^protocol-networks].

# Abstract

Regtest is a testing mode inherited from the Bitcoin node. It provides a
way to have a consensus node on a local network with private state that a
developer can control in order to reproduce certain situations
deterministically for testing purposes. Regtest, as implemented in zcashd,
is similar to Testnet but without miners and remote peers.

# Motivation

It is necessary to define Regtest mode so that different implementations of
Zcash full nodes provide the same capabilities and so that testing
infrastructure can be interoperable. Regtest mode was inherited from Bitcoin
and never defined in a ZIP. Differences between Zebra and zcashd Regtest
implementations found by developers involved in zcashd deprecation motivated
this ZIP as a way to document existing assumptions, expectations and
functionalities of Regtest, and to document regtest-only features.

This ZIP documents differences in behavior, values, expectations and
assumptions in comparison to Testnet. It uses the Zcash protocol
specification and existing ZIPs as guiding principles for the document
structure. It also documents pre-existing and previously *undocumented*
requirements, constants and values that are present in the zcashd 6.1.0
implementation and `zcash_protocol` crate 0.4.3 [^zcash_protocol].

This ZIP is intended for full node implementors but also as a reference
for developers and QA testers who use Regtest functionality to ensure test
coverage of their codebases.

# Requirements

The following are the user-facing goals that Regtest mode is intended to
satisfy:

1. Developers need to be able to efficiently generate deterministic
   sequences of blocks and transactions on a local node.
2. Consensus checks that would prevent efficient local block generation
   (such as proof-of-work difficulty) need to be relaxed or bypassed.
3. Developers need to be able to specify the activation heights of Network
   Upgrades at launch, via command-line parameters or a configuration file.
4. Regtest nodes need to operate in isolation from public networks and
   remote peers.
5. It should be possible to activate all Network Upgrades at a single
   height, while maintaining the invariant that a Network Upgrade is only
   active if all of its predecessors are also active.
6. Block generation should be available on demand, rather than on a
   mining schedule.
7. Address encodings should use distinct Human-Readable Parts (HRPs) to
   prevent confusion with Mainnet or Testnet addresses.
8. Regtest functionality should enable developers to achieve thorough
   test coverage of their codebases.

# Non-requirements

This ZIP does not attempt to address how Regtest mode should be
implemented. Details on full-node architecture, implementation details, and
software distribution are out of scope.

# Specification

## Configuration Parameters

Regtest mode is activated by starting a node with a `regtest` network
identifier. Implementations MUST provide configuration mechanisms for at
least the following, which MUST only be accepted when the node is running
in Regtest mode:

- **Network Upgrade activation heights.** The operator MUST be able to
  specify the activation height for each Network Upgrade. Upgrades that
  are not explicitly configured SHOULD default to inactive
  (`NO_ACTIVATION_HEIGHT`). Implementations SHOULD auto-activate
  predecessor upgrades when a later upgrade is configured (see
  [Global Effects on Network Upgrades](#global-effects-on-network-upgrades)).

- **Funding stream parameters.** The operator MUST be able to configure
  funding stream recipients, height ranges, and numerators. Funding
  streams SHOULD be disabled by default.

- **One-time lockbox disbursement parameters.** The operator MUST be able
  to configure lockbox disbursement recipients and heights.

- **Coinbase shielding requirement.** The operator SHOULD be able to
  toggle whether coinbase outputs are required to be shielded. This
  SHOULD default to not required.

Implementations MAY expose additional Regtest-only configuration, such as
proof-of-work parameter overrides or halving interval adjustments.

In zcashd, these are configured via command-line flags: `-nuparams`,
`-fundingstream`, `-onetimelockboxdisbursement`, and
`-regtestshieldcoinbase`. In zebrad, they are configured via TOML
configuration fields under `[network.testnet_parameters]`, including
`activation_heights`, `funding_streams`, `lockbox_disbursements`, and the
`allow_unshielded_coinbase_spends` builder option.

## Regtest Nodes and Network Connections

Regtest nodes MUST be configured with no default seed nodes or fixed seeds.
Mining MUST NOT require peers. Regtest nodes MUST NOT connect to external
peers. Implementations MUST provide mechanisms that restrict connections to
localhost.

Note: In zcashd, isolation is achieved by clearing `vFixedSeeds` and
`vSeeds` and setting `fMiningRequiresPeers = false`, rather than by
actively rejecting external connections.

## Proof of Work and Block Generation

Regtest mode SHOULD use reduced Equihash parameters (N=48, K=5) compared to
Mainnet and Testnet (N=200, K=9) to allow rapid block generation.

The following proof-of-work settings apply in Regtest mode:

- Block generation MUST be available on demand (e.g. via RPC calls such
  as `generate` or `generatetoaddress`).
- Difficulty retargeting MUST be disabled by default.
- Minimum-difficulty blocks MUST be allowed from genesis.

Implementations MAY provide a mechanism for overriding proof-of-work
parameters at runtime for test scenarios that require specific difficulty
behavior. In zcashd, the `UpdateRegtestPow` function serves this purpose.

## Subsidy and Halving

The pre-Blossom subsidy halving interval for Regtest is 144 blocks
(compared to 840,000 on Mainnet), with no slow-start interval. Coinbase
outputs are not required to be shielded by default, but implementations
SHOULD provide a mechanism to enable this requirement (see
[Configuration Parameters](#configuration-parameters)).

## Funding Streams

Funding streams are not enabled by default on Regtest. They MAY be
configured at runtime (see
[Configuration Parameters](#configuration-parameters)). Implementations
MUST NOT accept funding stream configuration on networks other than
Regtest.

## Global Effects on Network Upgrades

Regtest mode MUST allow Network Upgrades to occur at configurable block
heights. One or more Network Upgrades MAY be activated at the same height.

Network Upgrades MUST NOT be activated out of order. If a Network Upgrade
is active at a given height, all of its predecessors MUST also be active at
that height. The ordering of Network Upgrades is:

> Sprout → Overwinter → Sapling → Blossom → Heartwood → Canopy → NU5 →
> NU6 → NU6.1

In zcashd, when a Network Upgrade is explicitly configured via `-nuparams`,
all predecessor upgrades that have not been explicitly configured are
automatically activated at the same height. For example, specifying only
`-nuparams=CANOPY_BRANCH_ID:205 -nuparams=NU5_BRANCH_ID:210` will
automatically activate Overwinter, Sapling, Blossom, and Heartwood at
height 205. All Network Upgrades other than Sprout default to
`NO_ACTIVATION_HEIGHT` (disabled) if not configured.

It MUST be possible to configure activation heights for not-yet-released
Network Upgrades in order to enable testing of new protocol features in
advance of Mainnet or Testnet activation. Client libraries SHOULD also
accommodate such flexibility.

# Effects of Regtest Mode by ZIP

The following table presents the ZIP catalog and a one-line summary of the
Regtest changes that apply.

| ZIP  | Title | Regtest Behavior |
|------|-------|------------------|
| 32   | [Shielded Hierarchical Deterministic Wallets](https://zips.z.cash/zip-0032) | No change |
| 143  | [Transaction Signature Validation for Overwinter](https://zips.z.cash/zip-0143) | No change |
| [155](#behavior-for-zip-155)  | [addrv2 message](https://zips.z.cash/zip-0155) | Addresses MUST only point to localhost |
| 173  | [Bech32 Format](https://zips.z.cash/zip-0173) | No change |
| [200](#behavior-for-zip-200-network-upgrade-mechanism)  | [Network Upgrade Mechanism](https://zips.z.cash/zip-0200) | See section below |
| 201  | [Network Peer Management for Overwinter](https://zips.z.cash/zip-0201) | No change |
| 202  | [Version 3 Transaction Format for Overwinter](https://zips.z.cash/zip-0202) | No change |
| 203  | [Transaction Expiry](https://zips.z.cash/zip-0203) | No change |
| 205  | [Deployment of the Sapling Network Upgrade](https://zips.z.cash/zip-0205) | Configurable activation height |
| 206  | [Deployment of the Blossom Network Upgrade](https://zips.z.cash/zip-0206) | Configurable activation height |
| [207](#behavior-for-zip-207-funding-streams)  | [Funding Streams](https://zips.z.cash/zip-0207) | Disabled by default; configurable |
| [208](#behavior-for-zip-208-shorter-block-target-spacing)  | [Shorter Block Target Spacing](https://zips.z.cash/zip-0208) | See section below |
| 209  | [Prohibit Negative Shielded Chain Value Pool Balances](https://zips.z.cash/zip-0209) | Disabled by default; can be enabled via `SetRegTestZIP209Enabled` |
| 211  | [Disabling Addition of New Value to the Sprout Chain Value Pool](https://zips.z.cash/zip-0211) | No change |
| 212  | [Allow Recipient to Derive Ephemeral Secret from Note Plaintext](https://zips.z.cash/zip-0212) | No change |
| 213  | [Shielded Coinbase](https://zips.z.cash/zip-0213) | Coinbase shielding not required by default |
| 214  | [Consensus rules for a Zcash Development Fund](https://zips.z.cash/zip-0214) | No change |
| 215  | [Explicitly Defining and Modifying Ed25519 Validation Rules](https://zips.z.cash/zip-0215) | No change |
| 216  | [Require Canonical Jubjub Point Encodings](https://zips.z.cash/zip-0216) | No change |
| 221  | [FlyClient - Consensus-Layer Changes](https://zips.z.cash/zip-0221) | No change |
| 224  | [Orchard Shielded Protocol](https://zips.z.cash/zip-0224) | No change |
| 225  | [Version 5 Transaction Format](https://zips.z.cash/zip-0225) | No change |
| 236  | [Blocks should balance exactly](https://zips.z.cash/zip-0236) | No change |
| 239  | [Relay of Version 5 Transactions](https://zips.z.cash/zip-0239) | No change |
| 243  | [Transaction Signature Validation for Sapling](https://zips.z.cash/zip-0243) | No change |
| 244  | [Transaction Identifier Non-Malleability](https://zips.z.cash/zip-0244) | No change |
| 250  | [Deployment of the Heartwood Network Upgrade](https://zips.z.cash/zip-0250) | Configurable activation height |
| 251  | [Deployment of the Canopy Network Upgrade](https://zips.z.cash/zip-0251) | Configurable activation height |
| 252  | [Deployment of the NU5 Network Upgrade](https://zips.z.cash/zip-0252) | Configurable activation height |
| 253  | [Deployment of the NU6 Network Upgrade](https://zips.z.cash/zip-0253) | Configurable activation height |
| 300  | [Cross-chain Atomic Transactions](https://zips.z.cash/zip-0300) | No change |
| [301](#behavior-for-zip-301-zcash-stratum-protocol)  | [Zcash Stratum Protocol](https://zips.z.cash/zip-0301) | See section below |
| 308  | [Sprout to Sapling Migration](https://zips.z.cash/zip-0308) | No change |
| [316](#effects-on-zip-316)  | [Unified Addresses and Unified Viewing Keys](https://zips.z.cash/zip-0316) | [Revision 0] Changes to HRP of string encoding, [Revision 1] See section below |
| 317  | [Proportional Transfer Fee Mechanism](https://zips.z.cash/zip-0317) | No change |
| [320](#effects-on-zip-320-tex-addresses)  | [Defining an Address Type to which funds can only be sent from Transparent Addresses](https://zips.z.cash/zip-0320) | Changes to HRP of string encoding |
| 321  | [Payment Request URIs](https://zips.z.cash/zip-0321) | No change |
| 401  | [Addressing Mempool Denial-of-Service](https://zips.z.cash/zip-0401) | No change |
| [1014](#behavior-for-zip-1014-development-fund) | [Establishing a Dev Fund for ECC, ZF, and Major Grants](https://zips.z.cash/zip-1014) | Funding streams disabled by default; configurable |
| 1015 | [Block Subsidy Allocation for Non-Direct Development Funding](https://zips.z.cash/zip-1015) | No change |
| 2001 | [Lockbox Funding Streams](https://zips.z.cash/zip-2001) | No change |


## Behavior for ZIP-155

Peer-to-peer communications on Regtest MUST be restricted to localhost
nodes. See [Regtest Nodes and Network Connections](#regtest-nodes-and-network-connections).

## Behavior for ZIP-200 Network Upgrade Mechanism

It MUST be possible to configure a Regtest node with a mapping between
Network Upgrade activation heights and consensus branch IDs. It MUST be
possible for such configuration to enable the development of functionality
for not-yet-released Network Upgrades, in order to enable testing of new
protocol features in advance of Mainnet or Testnet activation. Client
libraries SHOULD also accommodate such flexibility.

## Behavior for ZIP-207 Funding Streams

Funding streams are not enabled by default on Regtest. They MAY be
configured at runtime (see
[Configuration Parameters](#configuration-parameters)).

## Behavior for ZIP-208 Shorter Block Target Spacing

In Regtest mode, block generation is performed on demand. Difficulty
retargeting is disabled by default. Values referenced by ZIP-208 [^zip-0208]
such as `BlossomActivationHeight` MUST be populated with whatever value the
Regtest node was configured with.

Regtest allows developers to set their own Network Upgrade activation
heights, so references to Blossom activation SHOULD use the value present
in the node configuration rather than a hardcoded constant.

## Behavior for ZIP-301 Zcash Stratum Protocol

Regtest nodes MUST NOT expose connections or connect to public networks
or other machines on a network. See
[Regtest Nodes and Network Connections](#regtest-nodes-and-network-connections).

## Behavior for ZIP-1014 Development Fund

Funding streams and development fund recipients are not configured by
default on Regtest. They MAY be configured at runtime (see
[Configuration Parameters](#configuration-parameters)).

## Effects on ZIP-316

### Revision 0

The HRP for Regtest Unified Addresses is defined as `uregtest`. Receivers
included inside Regtest UAs MUST also be Regtest variants of their
respective type.

Example:
```
uregtest1....
|
|-> Sapling  -> zregtestsapling1...
|
|-> Orchard  (encoded within the UA)
```

### Revision 1

From the [Address Expiration Metadata](https://zips.z.cash/zip-0316#address-expiration-metadata)
section:

> When honoring an Address Expiry Time, the reason that a sender SHOULD
> choose a `nExpiryHeight` that is expected to occur within 24 hours of
> the time of transaction construction is to, when possible, ensure that
> the expiry time is respected to within a day.

Time is compressed in Regtest mode because blocks can be generated at a
rate of one or more per second. This creates a conflict between expected
timespans for address expiration and the actual timestamps of transactions
in a Regtest-generated blockchain.

This remains an open question. Possible approaches include:

A. Regtest manages a separate clock where timestamps appear consistent
   with Mainnet's average block spacing (~75 seconds) for scenarios where
   time-based behavior is under test.

B. Adjust ZIP-316 implementations on Regtest so that the expiration window
   can be adjusted according to Regtest block cadence.

### Unified Incoming Viewing Keys Encoding

UIVKs MUST be encoded with the `uivkregtest` HRP on Regtest.

### Unified Full Viewing Keys Encoding

UFVKs MUST be encoded with the `uviewregtest` HRP on Regtest.

## Effects on ZIP-320 (TEX Addresses)

ZIP-320 [^zip-0320] defines an encoding for transparent-source-only
addresses with a `tex` HRP. On Regtest, this value MUST be `texregtest`.

# Effects of Regtest Mode on Protocol Definitions

The following section describes how Regtest mode affects definitions present
in the Zcash protocol specification [^protocol].

## Constants

### Coin Type

Regtest reuses Testnet's coin type:

```
COIN_TYPE: 1
```

### Sapling Payment Address Encoding

From the Zcash protocol specification [^protocol-saplingpaymentaddrencoding]:

> For addresses on Mainnet, the Human-Readable Part (as defined in
> ZIP 173) is "zs". For addresses on Testnet, the Human-Readable Part is
> "ztestsapling".

On Regtest, this MUST be `zregtestsapling`.

### Sapling Incoming Viewing Keys Encoding

From the Zcash protocol specification [^protocol-saplinginviewingkeyencoding]:

> For incoming viewing keys on Mainnet, the Human-Readable Part is
> "zivks". For incoming viewing keys on Testnet, the Human-Readable Part
> is "zivktestsapling".

On Regtest, this MUST be `zivkregtestsapling`.

### Sapling Full Viewing Keys Encoding

From the Zcash protocol specification [^protocol-saplingfullviewingkeyencoding]:

> For full viewing keys on Mainnet, the Human-Readable Part is "zviews".
> For full viewing keys on Testnet, the Human-Readable Part is
> "zviewtestsapling".

On Regtest, this MUST be `zviewregtestsapling`.

### Sapling Extended Spending Keys Encoding

These keys are defined in ZIP 32 [^zip-0032]. On Regtest, the HRP
encoding MUST be `secret-extended-key-regtest`.

### Sapling Extended Full Viewing Keys Encoding

These keys are defined in ZIP 32 [^zip-0032]. On Regtest, the HRP
encoding MUST be `zxviewregtestsapling`.

### Transparent Address Public Key Hash Base58 Prefix

The prefix for a Base58Check-encoded Regtest transparent `PublicKeyHash`
MUST be the same as the Testnet prefix:

```
B58_PUBKEY_ADDRESS_PREFIX: [0x1d, 0x25]
```

### Transparent Address Script Hash Base58 Prefix

The prefix for a Base58Check-encoded Regtest transparent `ScriptHash`
MUST be the same as the Testnet prefix:

```
B58_SCRIPT_ADDRESS_PREFIX: [0x1c, 0xba]
```

### Sprout Payment Address Encoding

The Zcash protocol specification [^protocol-sproutpaymentaddrencoding]
defines:

> Two bytes [0x16, 0x9A], indicating this version of the raw encoding of
> a Sprout shielded payment address on Mainnet. (Addresses on Testnet use
> [0x16, 0xB6] instead.)

Regtest uses the same prefix as Testnet: `[0x16, 0xB6]`.

# Rationale

Regtest mode has existed since the early days of Zcash as inherited
Bitcoin functionality. It was never formally specified because its primary
consumers were internal developers and automated tests. As additional full
node implementations (such as Zebra) have emerged, the lack of a formal
specification has led to inconsistencies that affect developers who rely on
Regtest for testing wallets, libraries, and other ecosystem tools.

The auto-fill behavior for predecessor Network Upgrades (where specifying a
later upgrade automatically activates all predecessors) is documented as a
convenience feature. Implementations MAY choose a different mechanism for
ensuring upgrade ordering, provided that the invariant that predecessor
upgrades are active whenever a successor upgrade is active is maintained.

# Security and Privacy Considerations

Regtest mode is intended exclusively for local testing. Because Regtest
nodes are intended to operate on isolated local networks, the security
properties of Mainnet and Testnet (such as resistance to Sybil attacks
or privacy guarantees of the peer-to-peer network) do not apply.

Developers SHOULD NOT use Regtest mode for any purpose involving real
funds. Regtest uses reduced proof-of-work parameters (Equihash N=48, K=5)
that provide no meaningful security against block forgery.

The address encodings defined in this ZIP (using `regtest`-prefixed HRPs)
are designed to prevent accidental cross-network address reuse between
Regtest and Mainnet.

# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)
[^protocol]: [Zcash Protocol Specification, Version 2024.5.1 or later](protocol/protocol.pdf)
[^protocol-networks]: [Zcash Protocol Specification, Version 2024.5.1. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)
[^protocol-saplingpaymentaddrencoding]: [Zcash Protocol Specification, Version 2024.5.1. Section 5.6.4: Sapling Payment Address](protocol/protocol.pdf#saplingpaymentaddrencoding)
[^protocol-saplinginviewingkeyencoding]: [Zcash Protocol Specification, Version 2024.5.1. Section 5.6.4.1: Sapling Incoming Viewing Key](protocol/protocol.pdf#saplinginviewingkeyencoding)
[^protocol-saplingfullviewingkeyencoding]: [Zcash Protocol Specification, Version 2024.5.1. Section 5.6.4.2: Sapling Full Viewing Key](protocol/protocol.pdf#saplingfullviewingkeyencoding)
[^protocol-sproutpaymentaddrencoding]: [Zcash Protocol Specification, Version 2024.5.1. Section 5.6.3: Sprout Payment Address](protocol/protocol.pdf#sproutpaymentaddrencoding)
[^zcash_protocol]: [zcash_protocol Rust crate 0.4.3](https://docs.rs/zcash_protocol/0.4.3)
[^zip-0032]: [ZIP 32: Shielded Hierarchical Deterministic Wallets](https://zips.z.cash/zip-0032)
[^zip-0320]: [ZIP 320: Defining an Address Type to which funds can only be sent from Transparent Addresses](https://zips.z.cash/zip-0320)
