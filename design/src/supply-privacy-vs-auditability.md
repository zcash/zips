# Supply Privacy vs Auditability

A ledger can either have fully visible balances or fully private balances known only to the direct participants, or some mix in between.

If balance are fully visible, the full supply can be audited easily by anyone, which provides a strong assurance that the monetary policy and supply scarcity hold. On the other hand, this is the worst possible privacy, revealing every participants holdings and the value and participants of every transfer.

By contrast, if the supply is fully private and known only to direct participants, this provides the strongest privacy. This protects users from theft and other harms to insufficient privacy. On the other hand, the monetary policy and supply scarcity is protected solely by a privacy-enabled integrity checking mechanism such as zero-knowledge proving systems.

## Current Zcash Design

The current Zcash design balances these trade-offs through the Turnstile Mechanism (see [ZIP 209](https://zips.z.cash/zip-0209)): Funds are either controlled by transparent addresses or shielded addresses. Different shielded protocols, such as Sprout, Sapling, or Orchard store funds in separate "shielded pools". Funds may only enter or exit a given pool by revealing the amount transferring in or out of the pool, which provides a running tally of the total presumed balance within that pool.

A supply integrity violation (aka a counterfeiting vulnerability) in transparent addresses can be caught quickly because any full node operator has access to all transparent balances and movements. A supply integrity violation specific to one of the shielded protocols will only impact internal balances and movements in the pool associated with that protocol. The overall supply outside of the affected pool cannot violate the public aggregate pool balance.

## Future Design Considerations

### One Pool per Shielded Protocol

The current turnstile approach can be reified with the introduction of a separate shielded pool for each new shielded protocol.

### Regularly Timed Pools

It is possible to introduce multiple pools over time for a single shielded protocol to explicitly force usage of a turnstile to detect supply integrity violations. This suggestion is not supported by a clear large majority of the Zcash development community.

Introducing would provide a similar balance of the trade-off as the current design with some differences, most notably introducing a new pool for a shielded protocol with an active counterfeiting attack does not mitigate the attack, it simply *may* detect the attack.

### Other Options

There are other possibilities for balancing this trade-off, including changing the trade-off goal towards the fully private side, such as by introducing multiple redundant private supply integrity mechanisms and then rotating them as new shielded protocols are deployed.
