```
ZIP: 
Title: Establish the Zcash Sustainability Fund on the Protocol Level
Owners: Jason McGee <jason@shieldedlabs.com>
        Mark Henderson <mark@equilibrium.co>
        Tomek Piotrowski <tomek@eiger.co>
        Mariusz Pilarek <mariusz@eiger.co>
Original-Authors: Nathan Wilcox
Credits: Nathan Wilcox
         Mark Henderson
         Jason McGee
         Tomek Piotrowski
         Mariusz Pilarek
Status: Draft
Category: Ecosystem
Created: 2023-08-
License: BSD-2-Clause
```

# Terminology

The key words "MUST", "SHOULD", "SHOULD NOT", "MAY", "RECOMMENDED", "OPTIONAL", and "REQUIRED" in this document are to be interpreted as described in RFC 2119. [1]

The term "network upgrade" in this document is to be interpreted as described in ZIP 200. [2]

The term "Block Rewards" refers to the algorithmic
issuance of ZEC to every block's creator -- part of the consensus rules.

"Issuance" - The method by which unmined or unissued ZEC is converted to ZEC available to users of the network

"We" - the ZIP authors, owners listed in the above front matter

"`MAX_MONEY`" is the ZEC supply cap. For simplicity, this ZIP defines it to be `21,000,000 ZEC`, although this is slightly larger than the actual supply cap of the original ZEC issuance mechanism.

# Abstract 

This ZIP describes the motivation, the necessary changes for, and the implementation specifications for the Zcash Sustainability Fund (ZSF). The ZSF is a proposed alteration to the block rewards system and accounting of unmined ZEC that allows for other sources of funding besides unissued ZEC. This new mechanism for deposits -- that new applications or protocol designs can use to strengthen the long-term sustainability of the network  -- will likely be an important step for future economic upgrades, such as a transition to Proof of Stake or Zcash Shielded Assets, and other potential protocol fees and user applications.

The changes in this ZIP are ultimately minimal, only requiring for the node to track state in the form of a `ZSF_BALANCE`, and for a new transaction field to be added, called `ZSF_DEPOSIT`. While wallet developer would be encouraged to add the `ZSF_DEPOSIT` field to their UIs, no changes or new behavior are absolutely required for developers or ZEC holders.

This ZIP does not change the current ZEC issuance schedule. Any additional amounts paid into the sustainability fund are reserved for use in future ZIPs.

# Motivation

The Zcash network's operation and development relies fundamentally on the block reward system inherited from Bitcoin. This system currently looks sometihng like this:

- At Every New Block:
    - Miner and funding streams rewarded a constant amount via unissued ZEC (this constant amount halves at specified heights)
    - Transaction fees `(inputs - outputs)`

The Zcash Sustainability Fund is a proposed replacement to that payout mechanism, with the relevant parts in *bold* below:

- **Unmined ZEC is now accounted for as `ZSF_BALANCE`**
- **Transaction includes optional contributions to ZSF via a `ZSF_DEPOSIT` field**
- Thus, at Every New Block:
    - Miner and funding streams rewarded the same constant amount, **but from `ZSF_BALANCE`** (this constant amount still halves at specified heights)
    - Transaction fees `(inputs - outputs)`, **including the `ZF_DEPOSIT` amount**

This design gives similar clarity and algorithmic control benefits, while also allowing other sources of funds for Block Rewards in addition to newly issued ZEC, via ZSF Deposits.

For example, an end-user wallet application could have an option to contribute a portion of a transaction to the ZSF, which would be included in a `ZSF_DEPOSIT` field in the transaction, to be taken into account by the Zcash nodes.

This ZIP is explicitly agnostic as to the recipients of block rewards so that acceptance or adoption of the Sustainability Fund does not introduce or bundle reallocation decisions with the primary proposal.

This quite simple alternation has -- in our opinion -- a multitude of benefits:

1. **Long Term Consensus Sustainability:** This mechanism supports long-term consensus sustainability by addressing concerns about the sustainability of the network design shared by Bitcoin-like systems through the establishment of deposits into the Sustainability Fund to augment block rewards, ensuring long-term sustainability as the issuance rate of Zcash drops and newly issued ZEC decreases over time.
2. **Benefits to ZEC Holders:** Deposits to the ZSF slow down the payout of ZEC, temporarily reducing its available supply, benefiting current holders of unencumbered active ZEC in proportion to their holdings without requiring them to opt into any scheme, introducing extra risk, active oversight, or accounting complexity.
3. **Recovery of "Soft-Burned" Funds:** In some instances, such as miners not claim all available rewards, some ZEC goes unaccounted for though not formally burned. This proposal would recover it through the `ZSF_BALANCE` mechanism described below.

# Specification

In practice, The Zcash Sustainability Fund is a single global balance maintained by the node state and contributed to via a single transaction field. This provides the economic and security support described in the motivation section, while also importantly keeping the fund payouts extremely simple to describe and implement.

The two modifications are:
1. The re-accounting of unmined ZEC as a node state field called `ZSF_BALANCE`
2. The addition of a transaction field called `ZSF_DEPOSIT`

Please note that a **network upgrade is required** for this work to be fully implemented.

## `ZSF_BALANCE`

The ZEC issuance mechanism is re-defined to remove funds from `ZSF_BALANCE`, which is initially set to `MAX_MONEY` at the genesis block.

Consensus nodes are then required to track new per-block state:

- `ZSF_BALANCE[H] : u64 [zatoshi]`

The state is a single 64 bit integer (representing units of `zatoshi`) at any given block height, ``H``, representing the Sustainability Fund balance at that height, ``H``. The `ZSF_BALANCE` can be calculated using the following formula:

`ZsfBalanceAfter(height) = MAX_MONEY + sum_{h = 0}^{height} (ZsfDeposit(height) + Unclaimed(height) - BlockSubsidy(height))`

where Unclaimed(height) is the portion of the block subsidy that is unclaimed for the block at the given height. 

### `ZSF_BALANCE` Requirements

- The value of `ZSF_BALANCE` SHOULD equal `0` for all blocks prior to the activation height `H`. 
- The above described formula `TOTAL ZEC TO EXIST (MAX_MONEY) - CLAIMED BLOCK SUBSIDIES OF PAST BLOCKS + SUM OF ALL ZSF DEPOSITS FROM PAST TRANSACTIONS` MUST hold for all future blocks.

## `ZSF_DEPOSIT`

Each transaction can dedicate some of its excess funds to the ZSF, and the remainder becomes the miner fee, with any excess miner fee/reward going to the ZSF

This is achieved by adding a new field to all transactions:

- `ZSF_DEPOSIT : u64 [zatoshi]`

The `ZSF_BALANCE[H]` for a block at height `H` can be calculated given a value of `ZSF_BALANCE[H-1]` and the set of transactions contained in that block. First, the `ZSF_DEPOSIT[H]` is calculated based solely on `ZSF_BALANCE[H-1]`. This is subtracted from the previous block's balance to be distributed as part of the block reward. Second, the sum of all the `ZSF_DEPOSIT` fields of all transactions in the block is added to the balance.

It is safe and consistent to treat older transactions using pre-Sustainability Fund formats as if they have this field implicitly present with a value of 0 where that simplifies designs or implementations.

#### Consensus Rule Changes

- Transparent inputs to a transaction insert value into a transparent transaction value pool associated with the transaction. Transparent outputs **and sustainability fund deposits** remove value from this pool.

### `ZSF_DEPOSIT` Requirements

- There MUST be only one `ZSF_DEPOSIT` field per transaction
- ZIP 225 [3] MUST be updated to include `ZSF_DEPOSIT`. ZIP 244 MAY be updated as well.
- Separate programming language implementations (C++, Rust, etc) MUST guarantee that the calculations described above are consistent

# Rationale

All technical decisions in this ZIP are balanced between the necessary robustness of the ZSF mechanics, and simplicity of implementation. 

## `ZSF_BALANCE` as node state

Tracking the `ZSF_BALANCE` value as a node state using the above formula is very simple in terms of implementation, and should work correctly given that the node implementations calculate the value according to the specifications.

### Alternative: `ZSF_BALANCE` as block header commitment

An alternative to node state could be to include the `ZSF_BALANCE` field as a block header and require a block header commitment.

Requiring block-header-rooted commitments of global fund balances such as the Sustainability Fund ensures that any consensus deviating bugs in accounting of this balance are immediately detected in the earliest impacted block. It also removes some of the need for explorer sites and other analytics services from tracking this value independently, assuming the committed value is made available by common APIs. This helps ensure that all explorers track and report the correct value.

## `ZSF_DEPOSIT` as explicit transaction field

An explicit value distinguishes the ZEC destined to Sustainability Fund deposits from the implicit transaction fee. Explicitness also ensures any arithmetic flaws in any implementations are more likely to be observed and caught immediately.

# References

**[1]: [Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/rfc/rfc2119.html)**

**[2]: [ZIP 200: Network Upgrade Mechanism](https://zips.z.cash/zip-0200)**

**[3]: [ZIP 225: Version 5 Transaction Format](https://zips.z.cash/zip-0225)**
