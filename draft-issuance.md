```
ZIP: 
Title: Smooth Out The Block Subsidy Issuance
Owners: Jason McGee <jason@shieldedlabs.com>
        Mark Henderson <mark@equilibrium.co>
        Tomek Piotrowski <tomek@eiger.co>
        Mariusz Pilarek <mariusz@eiger.co>
Original-Authors: Nathan Wilcox
Credits: Nathan Wilcox
         Mark Henderson
         Jason McGee
Status: Draft
Category: Consensus
Created: 2023-08-23
License: BSD-2-Clause
```

# Terminology

The key words “MUST”, “SHOULD”, “SHOULD NOT”, “MAY”, “RECOMMENDED”, “OPTIONAL”,
and “REQUIRED” in this document are to be interpreted as described in RFC 2119. [1]

"Network upgrade" - to be interpreted as described in ZIP 200. [2]

“Block Subsidy” - to be interpreted as described in ZIP TBD [3]

“Issuance” - to be interpreted as described in ZIP TBD [3]

“We” - the ZIP authors, owners listed in the above front matter

“`ZsfBalanceAfter(h)`” is the total ZEC available in the Zcash Sustainability Fund (ZSF) after the transactions
in block `h`, described in ZIP #TODO reference#. The Sustainability Fund is used to pay out Block Subsidies
from unmined ZEC, and other fund deposits.

“`BLOCK_SUBSIDY_FRACTION`” = 41 / 100,000,000 or `0.00000041`

"`NUMBER_OF_BLOCKS_IN_4_YEARS`" = `(365.25 * 24 * 60 * 60/75 * 4)`, or `1_683_072`

# Abstract

This ZIP proposes a change to how nodes calculate the block subsidy.

Instead of following a step function around the four-year halving cycle inherited
from Bitcoin, we propose a slow exponential “smoothing” of the curve. The new issuance
scheme would approximate the current 4 year cycle, and results in the last
zatoshi being issued in around 114 years.

# Motivation

Zcash’s economic model is inherited from Bitcoin and includes the concept of a halving
mechanism to regulate the issuance of new coins. This approach, though foundational, invites
 a reevaluation amid Zcash’s ongoing evolution. As the network matures, the need to address
potential future challenges and ensure a sustained and stable economic ecosystem becomes
apparent. The transition to a smoothed emissions curve offers an opportunity to adjust the network's
issuance dynamics while maintaining the supply cap of 21,000,000 coins. By doing so, Zcash
endeavors to optimize its economic framework, accommodating changing circumstances while
maintaining predictability and stability in rewards distribution.

This proposal outlines a solution to address challenges associated with the existing block
subsidy issuance mechanism in the Zcash network. The primary goal of this proposal is to
introduce a more predictable and stable issuance of ZEC by smoothing out the issuance
curve while preserving the supply cap. It's important to note that this proposal does
not seek to alter the fundamental aspects of Zcash's issuance policy. The average block
subsidy amount over time will remain the same and the funds for block subsidies will last
a similar amount of time. Instead, it focuses solely on enhancing the predictability
and consistency of the block subsidy issuance process.

Smoothing the emissions curve helps ensure that the network remains economically
viable and stable as it transitions from a traditional issuance mechanism to one
that maintains a sustainable and predictable issuance of rewards over time. It
prevents abrupt changes in the rate of newly issued coins, which could lead to
disruptions in the network's economic model and potentially impact its security
and sustainability. A smoother emissions curve allows for a more gradual and controlled
transition, providing ZEC stakeholders and participants with a clear understanding of
how rewards will be distributed over time.



# Specification

Smoothing the issuance curve is possible using an exponential decay formula that
satisfies the following requirements:

## Issuance Goals

1. Block subsidies are monotonically decreasing, as long as `ZsfBalanceAfter(h)` is monotonically decreasing
2. Block subsidies approximate a continuous function
3. When `ZSF_BALANCE(h) > 0` then block subsidies for block `h`
MUST always be `> 0`, preventing a final “unmined” zatoshi
4. For any 4 year period, all paid out block subsidies MUST equal approximately
half of `ZSF_BALANCE` at the beginning of that 4 year period
5. This functionality MUST be introduced as part of a network upgrade

The above requirements assume no deflationary action, i.e. that no ZEC is added
to `ZSF_BALANCE`. They are referenced below as **Rn**.

## Issuance Calculation

Given the block height `h` define a function **S**, such that:

**S(h)** = Block subsidy for a given `h`, that satisfies above requirements.

Using an exponential decay function for **BlockSubsidy** satisfies **G1** and **G2** above:

`BlockSubsidy(h) = BLOCK_SUBSIDY_FRACTION * ZsfBalanceAfter(h - 1)`

Finally, to satisfy **G3** above we need to always round up to at least 1 Zatoshi
if `ZsfBalanceAfter(h - 1) > 0`:

`BlockSubsidy(h) = ceiling(BLOCK_SUBSIDY_FRACTION * ZsfBalanceAfter(h - 1))`

# Rationale

## `BLOCK_SUBSIDY_FRACTION`

The value `41 / 100_000_000` satisfies the approximation:

`(1 - BLOCK_SUBSIDY_FRACTION)^NUMBER_OF_BLOCKS_IN_4_YEARS ≈ 0.5`

Meaning after a period of 4 years around half of `ZSF_BALANCE` will be paid out
as block subsidies, thus satisfying **G4**.


## Other Notes

The suggested implementation avoids using float numbers. Rust and C++ will both round
the result of the final division up, satisfying **R3** above.

# Appendix: Simulation

We encourage readers to run the following Rust code, which simulates block subsidies.
According to this simulation, assuming no deflationary action, block subsidies would
last for approximately 113 years:

## Rust Code

```rust
fn main() {
    // approximate available subsidies in August of 2023
    let mut available_subsidies: i64 = 4671731 * 100_000_000;
    let mut block: u32 = 0;

    while available_subsidies > 0 { 
        let block_subsidy = (available_subsidies * 41 + 99_999_999) / 100_000_000;
        available_subsidies -= block_subsidy;

        println!(
            "{} ({} years): {}({} ZEC) {}({} ZEC)",
            block,                             // current block
            block / 420_768,                   // ~ current year
            block_subsidy,                     // block subsidy in zatoshis
            block_subsidy / 100_000_000,       // block subsidy in ZEC
            available_subsidies,               // available subsidies in zatoshis
            available_subsidies / 100_000_000  // available subsidies in ZEC
        );

        block += 1;
    }   
}
```

Last line of output of the above program is:

`47699804 (113 years): 1(0 ZEC) 0(0 ZEC)`

Note the addition of 99,999,999 before division to force rounding up of non-zero values.


# References

[1] RFC-2119: https://datatracker.ietf.org/doc/html/rfc2119

[2] ZIP-200: https://zips.z.cash/zip-0200

[3] ZIP-XXX: Placeholder for the ZSF ZIP
