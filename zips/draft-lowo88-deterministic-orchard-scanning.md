ZIP: unassigned
Title: Deterministic Orchard Wallet Scanning Standard
Owners: Lowo88 <lowo88@leoninedao.org>
Status: Draft
Category: Standards Track
Created: 2026-01-16
License: MIT

# Abstract

This ZIP specifies a standard algorithm for deterministic scanning of Orchard
notes in Zcash wallets. The specification ensures that wallet implementations
produce identical results when scanning the same block range, regardless of
implementation details, scan order, or timing.

# Motivation

Current Zcash wallet implementations lack a standardized approach to scanning
Orchard notes. This leads to several critical issues:

**Non-Deterministic Results**: Different wallets may produce different results
when scanning the same block range.

**Inconsistent Wallet State**: Wallet restores may produce different results.

**Interoperability Issues**: Users cannot reliably switch between wallet
implementations.

# Specification

The deterministic scanning algorithm processes blocks in strict sequential order
by height, processes transactions within each block in deterministic order,
and processes Orchard actions within each transaction in deterministic order.

## Key Requirements

1. **Block Processing Order**: Blocks MUST be processed in ascending height order
2. **Transaction Processing Order**: Transactions processed by index within block
3. **Action Processing Order**: Actions processed by index within transaction
4. **Scope Order**: External scope actions before Internal scope actions
5. **Deduplication**: First occurrence kept when duplicates found

# References

- ZIP 32: Shielded Hierarchical Deterministic Wallets
- ZIP 224: Orchard
- ZIP 316: Unified Addresses