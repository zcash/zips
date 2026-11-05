    ZIP: Unassigned
    Title: Zcash Stablecoin Vaults
    Owners: Giacomo Barbieri <hey@jaack.me>
    Status: Draft
    Category: Consensus
    Created: 2026-11-05
    License: MIT
    Discussions-To: <https://github.com/iJaack/zsv/issues/1>

No ZIP number or network upgrade has been assigned. Deployment allocations and outstanding
review are listed below.

# Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHOULD" and "MAY" in this document are to be
interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.
Conformance requirements appear in the Specification section.

- **ZSV** means Zcash Stablecoin Vaults.
- **zUSD** is the provisional name of the single dollar-targeting stable asset defined here.
- **Principal** is debt attached to an active vault.
- **Bad debt** is stablecoin liability remaining after a vault closes without burning all its principal.
- **Stable supply** includes all unspent zUSD, including coins whose spending keys have been lost.
- A **report certificate** is one price report with the required matching reporter signatures.
- A **current vault reference** identifies the transaction that created its latest state.

# Abstract

This proposal adds native ZEC vaults and one protocol-defined stablecoin to Zcash. Borrowing
against sufficient collateral creates zUSD; repayment and liquidation destroy existing zUSD and
reduce the corresponding liability. Zcash consensus enforces ownership, collateral release,
issuance, burns and independent conservation of both assets.

The protocol provides no arbitrary asset registration, issuer authority, governance token or
general execution environment. It uses a dedicated transaction format, a separate ZEC vault
value pool and public zUSD outputs. Existing ZEC transaction formats remain available under
their applicable consensus rules. Public vaults and payments expose balances, amounts and
financial relationships; shielded zUSD requires a subsequent specified and reviewed protocol.

A fixed reporter quorum supplies ZEC/USD observations. Consensus verifies their authentication
and deterministic validity conditions, but cannot establish their economic truth. Full
liquidation records any uncovered principal as bad debt. Further borrowing stops while bad debt
remains; holders can retire that debt by burning existing zUSD without compensation. No
dollar-redemption claim or guaranteed market peg is created.

The proposal is independent of a Dev Fund allocation or reserve. Those mechanisms may be
considered separately. Research code and economic tests support selected design choices; native
format, authorization and deployment rules require implementation and independent review.

# Motivation

ZEC holders may want dollar-denominated liquidity while retaining exposure to their remaining
collateral. A native vault would let them borrow under rules checked by Zcash nodes, accepting
liquidation risk when collateral loses value. Holders of the issued asset would bear collateral,
oracle, liquidity and protocol risk.

A data commitment alone cannot lock ZEC or create a native stablecoin. General-purpose Zcash
Shielded Assets would support unrelated tokens and issuers. ZSV instead proposes one monetary
use case with a closed issuance path. The smaller asset domain reduces issuance cases, but the
financial and consensus complexity remains substantial.

Veylor provides related work on dollar access: its documented split-key swap exchanges shielded
ZEC for USDC held in Railgun on Ethereum. [^veylor] ZSV proposes borrowing against retained ZEC
and settling the issued asset on Zcash. This would serve a different financial use case and
avoid an external settlement chain for that path, while introducing collateral, oracle and
liquidation risk. Veylor's existence does not establish adoption or demand for ZSV, and ZSV's
public first version does not yet provide shielded dollar payments. No affiliation or
endorsement is implied.

The intended benefit is native borrowing and a transferable dollar-targeting asset without an
arbitrary token-launch interface. Whether that benefit justifies the oracle dependency, privacy
cost and additional consensus rules is a question for community review.

# Privacy Implications

This first version has public vaults and public stablecoin payments. It reveals collateral,
principal, owner keys, payment amounts and liquidation events. Creating a vault from previously
shielded ZEC requires exposing value to the permitted transparent input path. Key reuse and
transaction graph analysis can link borrowing, payments and repayment. Liquidation can reveal
financial distress.

Adding shielded payments later would not erase these disclosures. A fixed-asset shielded profile
could reuse selected ZSA transfer, note and proof techniques, but would need its own precise
proof statements, value-pool accounting and privacy review. Existing ZSA audits would not
automatically apply to a changed circuit. Private vaults also need liquidation information to
remain available without borrower cooperation; this version does not attempt that design.

# Requirements

The design goals are:

- Enforcement of collateral, debt, issuance and liquidation by Zcash consensus, with no bridge, external execution chain or custody committee.
- Exactly one additional native asset, issued only through valid collateralized borrowing.
- Atomic value accounting, with no alternative ordinary spend of locked collateral and no hidden erasure of stablecoin liabilities.
- Repayment, collateral additions, debt-free exit and payment transfers during an oracle outage.
- Deterministic branch-specific validation, bounded work and equivalent behavior across implementations.
- Continued ordinary ZEC activity without requiring unrelated users to submit ZSV operations.
- Defined vault operation without a reserve, Dev Fund allocation or privileged recovery key.

# Non-requirements

This proposal does not add arbitrary issuers, asset descriptions, NFTs, a VM, a governance
token, a bridge or external custody. It does not prevent off-protocol claims, inscriptions,
derivatives or speculation. It does not allocate block rewards or NSM value, establish on-demand
dollar redemption, or promise that zUSD trades at one dollar.

Dev Fund allocation and reserve stabilization are separate candidate work. Shielded payments and
wallet address standardization may require companion ZIPs. The oracle rules are part of this
core proposal; they are not an optional service that a node may configure differently.

# Specification

## Scope and activation parameters

This specification defines a new, dedicated transaction version with a fixed ZEC/zUSD domain. It
does not modify the meaning of an allocated transaction version or enable general ZSA issuance.
Deployment allocates its version/group identifiers, consensus branch context, activation heights
and fixed oracle roster. Until those allocations and the required implementation/review exist,
this is an unactivated proposal.

Validators MUST reject the new format before its network-specific activation. After activation,
ordinary ZEC transaction versions MUST retain their applicable validation rules. The new format
MUST NOT be interpreted as the existing v6 format or as withdrawn ZIP 230. An allocated existing
format is not available for reassignment by this draft. The existing format and Zebra
integration baseline is recorded in the pinned sources. [^sources]

At activation, the ZSV vault set and public zUSD UTXO set are empty, stable supply and bad debt
are zero, and no price report is active. Activation MUST NOT create ZEC, zUSD, a reserve balance
or a privileged allocation. Borrowing remains unavailable until a valid report certificate is
accepted.

## Encoding conventions and bounds

All integers are unsigned little-endian unless stated otherwise. Hashes are raw 32-byte
consensus digest bytes, not reversed display hex. A compressed secp256k1 key K is exactly 33
bytes: prefix 02 or 03 followed by the canonical field encoding of a valid non-infinity point's
x-coordinate. Invalid/noncanonical keys fail. New asset outputs have no script, arbitrary
metadata or asset identifier.

Counts are canonical CompactSize. Each count below is at most 64, so its only valid encoding is
one byte. Resolved payment inputs and newly created payment outputs have strictly positive
values. Zero is permitted only for operation fields that explicitly allow it. Each ZEC payment
value, each transaction's ZEC input/output sums and value-balance sides, and the persistent
vault-pool balance MUST fit MAX_MONEY = 2,100,000,000,000,000 zatoshi. Each zUSD payment value,
each transaction's stable input/output sums and value-balance sides, and the persistent stable
supply MUST fit S_MAX = 100,000,000,000 micro-zUSD. These are per-transaction and state bounds;
they do not limit the sum of all transfers across a block, which can reuse value through valid
same-block dependencies. Signed maximum-burn and minimum-receipt limits are unsigned u64 bounds,
not additional input or output value. A serialized ZSV transaction, including authorization, is
at most 65,536 bytes. Existing block size limits remain in force. Each block contains at most
256 transactions of this new version, at most 1,024 required secp256k1 signature slots across
them, and at most 4,096 new native ZEC plus stable output entries across them. Slots count
native input signatures, stable input signatures and any operation signature whether valid or
not; outputs count both explicit output vectors. The oracle permits at most one certificate and
at most 7 Ed25519 report signatures per block. Check these counts before signature verification
and state insertion. These are exact proposed limits, not benchmark-calibrated production
recommendations. There is no lifetime UTXO cap or permitted-wallet list.

The fee/residual calculation uses checked signed arithmetic of sufficient width. Core
collateral-ratio and liquidation products use checked u128. A new format has no coinbase input,
shielded bundle, JoinSplit, general script vector, asset selector or optional opaque extension
field.

## Effect body E

In the encoding tables, `+` denotes byte concatenation, and fields are listed in wire order.

A transaction consists of E followed immediately by its authorization tail A, with no trailing
bytes. E is:

| Field | Bytes / rule |
|---|---|
| header | u32: high bit 1; remaining 31 bits equal the unallocated ZSV_VERSION |
| versionGroupId | u32: unallocated ZSV_VERSION_GROUP_ID |
| consensusBranchId | u32: exactly the active upgrade branch ID |
| lockTime | u32, required 0 |
| expiryHeight | u32, H<=expiryHeight<500,000,000 and expiryHeight>0, where H is inclusion height |
| nZecInputs | CompactSize,0..64 |
| zecInputs | nZecInputs*(prevTxid32 + prevOutputIndexu32) |
| nZecOutputs | CompactSize,0..64 |
| zecOutputs | nZecOutputs*(valueu64 + recipientKey33) |
| nStableInputs | CompactSize,0..64 |
| stableInputs | nStableInputs*(prevTxid32 + prevOutputIndexu32) |
| nStableOutputs | CompactSize,0..64 |
| stableOutputs | nStableOutputs*(valueu64 + recipientKey33) |
| operationTag | u8, one of 0..5 below |
| operationPayload | exactly the tag's payload |
| hasOracle | u8, exactly 0 or 1 |
| oracleEffects | absent if 0; if 1 the exact 45-byte certificate effects below |

Native input sequence numbers are implicitly final (0xffffffff); they have no wire field. Native
outputs create ordinary transparent ZEC UTXOs with the exact standard script
`0x21||recipientKey33||0xac` (P2PK). The input must resolve to a real unspent transparent output
whose locking script matches that exact P2PK grammar. Its value comes from native branch state,
not transaction data. Existing coinbase-maturity, duplicate-spend, money-range and other
applicable native input rules continue to apply. Existing ZEC transaction versions and their
accepted scripts remain unchanged; users may send ZEC to a P2PK output through an ordinary
transaction before using it here.

Stable outputs create entries only in the new zUSD payment UTXO namespace. They are not native
ZEC transparent outputs. Stable input indices resolve only in that namespace. Native and stable
`(txid,index)` namespaces are distinct: an equal byte tuple does not make the two assets
interchangeable. Every input must exist, be unspent on the exact candidate branch, have an
in-range positive value and have the expected fixed-key ownership. Repeated outpoints within a
namespace fail. Same-block dependencies use previously validated transaction outputs in block
order.

Only one optional operation is allowed. Tag 0 means NONE and has no payload; it permits pure
stable transfers. If hasOracle=0 and tag=NONE, at least one stable input is required. If
hasOracle=1, tag must be NONE and both stable counts must be 0. Native fee inputs and outputs
remain permitted in an oracle transaction. Other empty uses of the new version fail; ordinary
ZEC transactions continue using their existing formats.

## Vault state and operation payloads

A current vault is stored in a dedicated ZEC vault value pool, keyed by its `VaultRef`, the raw
32-byte effects txid of the OPEN or UPDATE that created it. Because each transaction has at most
one operation, no operation index is needed. The state record is `(ownerKey33, collateralu64,
principalu64)`. OPEN/UPDATE create one successor at their own txid; UPDATE consumes the previous
ref and preserves its owner. CLOSE/LIQUIDATE consume without a successor. Current refs are
unique; inserting an existing current ref fails.

Vault collateral is not also an ordinary transparent output. There is no OP_TRUE collateral
script and no spendable duplicate. Its amount enters the native ZEC vault value pool and can
leave only through a valid operation and the fee equation below. All node paths need this
accounting, including direct finalization/checkpoints; ordinary native spends can resolve only
actual native UTXOs, never the vault pool.

| Tag | Payload |
|---|---|
|0 NONE|empty|
|1 OPEN|ownerKey33 + newCollateralu64 + newPrincipalu64 + oracleID32|
|2 UPDATE|priorVaultRef32 + newCollateralu64 + newPrincipalu64 + oracleID32 + ownerPayoutIndexu32|
|3 CLOSE|priorVaultRef32 + ownerPayoutIndexu32|
|4 LIQUIDATE|priorVaultRef32 + oracleID32 + maxBurnu64 + minCollateralu64 + liquidatorKey33 + ownerPayoutIndexu32 + liquidatorPayoutIndexu32|
|5 RETIRE_BAD_DEBT|burnAmountu64|

OracleID is the exact identifier of the block's parent-selected pricing observation defined by
the oracle specification. For OPEN with D=0, and UPDATE without a price requirement, oracleID is
exactly 32 zero bytes. A price-requiring operation uses the active nonzero ID; no alternate or
stale observation is accepted. This prevents an irrelevant observation from needlessly
restricting oracle-free repayment/deposit, and makes its wire encoding unique.

OPEN requires C>0. UPDATE requires C'>0 and a changed `(C,D)` pair; `(0,0)` uses CLOSE. Nonzero
D' must satisfy the minimum-debt rule. The owner auth key for OPEN is its encoded key;
UPDATE/CLOSE use the actual prior state's owner. LIQUIDATE uses its encoded liquidator key.
RETIRE has no operation-owner signature: actual stable input authorization controls the burn.

A mandatory payout index names an ordinary native ZEC output in this same transaction. The named
output must have exactly the required amount and exact P2PK recipient. UPDATE with C'<C requires
a payout of C-C' to the immutable owner. UPDATE without released collateral uses the sentinel
0xffffffff. CLOSE pays exactly oldC to the owner. Every valid current vault has positive
collateral, so this payout always uses an output index. LIQUIDATE pays z to the liquidator and
C-z to the owner. A zero required payout uses sentinel 0xffffffff and consumes no output. A
positive payout requires an index in range; sentinel is invalid. Both positive liquidation
payout indices must be distinct, even for self-liquidation when ownerKey=liquidatorKey. One
output cannot satisfy two mandatory payouts. Extra native outputs remain allowed and are covered
by all signatures and value conservation.

The exact collateral payouts cannot silently pay fees. Any positive residual fee must be
supplied by other actual native value (normally free ZEC inputs). Minted stable outputs may use
any valid recipient keys chosen in the fully signed transaction: borrowing and sending value to
another recipient can be atomic. No amount is inferred from a memo or claimed caller balance.

## Per-asset value equations

Define C_before as the actual prior vault collateral, or 0 for NONE/OPEN/RETIRE; C_after is
OPEN/UPDATE's encoded collateral, or 0 for NONE/CLOSE/LIQUIDATE/RETIRE. Let Mint and Burn come
only from the validated core operation:

- OPEN: Mint=D', Burn=0.
- UPDATE: Mint=max(D'-D,0), Burn=max(D-D',0).
- CLOSE: Mint=0, Burn=D (close can atomically repay all principal).
- LIQUIDATE: Mint=0, Burn=x from the specified exact liquidation formula.
- RETIRE_BAD_DEBT: Mint=0, Burn=r, with 0 < r <= B at transaction entry.
- NONE: Mint=Burn=0.

Then require:

```
sum(stableInputs) + Mint = sum(stableOutputs) + Burn
Fee = sum(nativeZecInputs) + C_before - C_after - sum(nativeZecOutputs)
0 <= Fee <= MAX_MONEY
```

The fee is counted in ordinary ZEC fee/coinbase accounting, including any separately active
fee-disposition rules. Stable value cannot pay it. These rules do not introduce a positive
consensus minimum fee; relay/mining fee policy remains separate. The vault value pool changes by
C_after-C_before, and total stable supply changes by Mint-Burn. Live principal changes and
bad-debt handling follow the core; RETIRE decreases B and S together without touching active
collateral or principal. Borrowing requires B=0 at transaction entry, so it cannot be
self-financed by another operation in the same transaction (and only one operation is allowed).

## Hashes and authorization

Let `H(label,bytes)` be BLAKE2b-256 with the ASCII label right-padded with zero bytes to a
16-byte personalization. All labels below are exact and case-sensitive; no NUL is appended to
message bytes. Let G be the raw 32-byte genesis block hash of the configured network. G comes
from trusted network configuration, never transaction data. Hashing APIs therefore need explicit
network context; branch IDs alone do not distinguish Mainnet from Testnet. The header already
commits the branch ID.

```
txid = H("ZSV_TxId_v1", G || E)
contextHash = H("ZSV_Context_v1", R)
signatureDigest(role,index) = H("ZSV_Sign_v1", G || txid || contextHash || u8(role) || u16LE(index))
authDigest = H("ZSV_Auth_v1", txid || A)
```

R is authoritative resolved input context, encoded in this exact order:

```
CompactSize(nZecInputs)
  for each native input, in wire order:
    prevTxid32 || prevOutputIndexu32 || actualValueu64 || actualP2pkKey33
CompactSize(nStableInputs)
  for each stable input, in wire order:
    prevTxid32 || prevOutputIndexu32 || actualValueu64 || actualOwnerKey33
u8(hasPriorVault)  # 1 for UPDATE/CLOSE/LIQUIDATE, else 0
  if 1: priorVaultRef32 || actualOwnerKey33 || actualCollateralu64 || actualPrincipalu64
```

No caller-supplied prevout value/key or prior vault record can replace these state lookups.
Signatures bind every effect, input reference, value, key, operation, oracle bound and payout.
There are no selectable SIGHASH modes and no implicit whole-parent-state checkpoint. Same
effects on the same live inputs can be valid on competing branches when the contextual
oracle/expiry/policy rules also pass; this is normal fork behavior, not a replay across networks
or upgrades.

A secp256k1 authorization consists of `u8(signatureLength) ||strictDER(signature)`, with length
8..72. The DER is the shortest valid ASN.1 encoding of the ECDSA pair; round-trip canonical DER
is required, 1<=r<n and 1<=s<=floor(n/2), where n is the secp256k1 subgroup order. No appended
hash-type byte, extra push opcode or trailing data is allowed. Verify ECDSA against the
indicated 32-byte digest and authoritative key. Low-S and minimal DER are consensus rules for
this version.

A contains exactly these slots, without counts or padding:

1. One signature for every native input, in wire order, role 0/index 0..nZecInputs-1, verified with its actual P2PK key.
2. One signature for every stable input, in wire order, role 1/index 0..nStableInputs-1, verified with its actual owner key.
3. For OPEN/UPDATE/CLOSE/LIQUIDATE, exactly one operation signature, role 2/index 0, using the operation auth key defined above. NONE/RETIRE have no such slot.
4. If hasOracle=1, exactly popcount(signerMask) raw 64-byte Ed25519 report signatures in ascending reporter-set index order, under the separate oracle message/ZIP215 validation rules.

A signer may appear in several roles; every required role still has its own signature slot. This
prevents treating a fee input signature as authority over an unrelated vault. The effects txid
excludes all signatures, allowing dependent transactions to be constructed before authorization.
authDigest commits the complete tail. For this version, the transaction Merkle tree leaf is
txid, and the corresponding ZIP244 authorization-data tree leaf is authDigest. Existing Merkle
and block-commitment algorithms are unchanged. It is not a pre-v5 placeholder leaf. ZIP239
witnessed relay treats this version as witness-bearing: wtxid is the exact 64 bytes
txid||authDigest, in raw digest order. The version-dispatch rules are extended accordingly;
older-version hashes and their relay behavior are unchanged. At the pinned Zebra source, these
roles correspond to `zebra-chain/src/block/merkle.rs::AuthDataRoot`, `block/commitment.rs` and
`transaction/hash.rs::WtxId` (whose byte conversion concatenates these two 32-byte hashes).
[^zip-0244] [^zip-0239]

## Oracle effects integration

The oracle effect structure is:

```
observedHeightu32 || observedBlockHash32 || priceu64 || signerMasku8
```

This is 45 bytes. The mask's high bit is 0 and popcount is 5..7 for the fixed seven-reporter
deployment roster. The active roster ID is derived from the specified sorted keys and is not
repeated on wire. Oracle signatures bind their separate network/branch/roster/report message.
OracleID excludes the signer mask/signatures, so differing valid quorums over identical content
identify the same observation. The Oracle rules below provide exact ancestry, age, ordering and
rotation rules.


## Units, ranges and arithmetic

| Symbol | Proposed value or definition |
|---|---|
| q | 100,000,000 zatoshi per ZEC |
| m | 1,000,000 micro-zUSD per zUSD |
| C | Vault collateral in zatoshi; 0 <= C <= MAX_MONEY |
| MAX_MONEY | 21,000,000 * q = 2,100,000,000,000,000 zatoshi, subject to the base protocol's native ZEC amount rule |
| D | Vault principal in micro-zUSD |
| P | Accepted micro-USD per ZEC; integer 1 <= P <= 2^64 - 1 |
| D_MIN | 100 * m = 100,000,000 micro-zUSD |
| S_MAX | 100,000 * m = 100,000,000,000 micro-zUSD |
| R_OPEN | 250 percent |
| R_LIQ | 200 percent |
| K_LIQ | 105 percent, including the 5 percent liquidation bonus |
| S | Outstanding native zUSD supply |
| B | Explicit bad debt |

These opening, liquidation, bonus, debt-floor and supply-cap values are fixed draft defaults
carried from the prototype. In particular, the small initial supply ceiling bounds nominal
outstanding liabilities; it does not prove their dollar value or economic safety. Changing a
value requires the versioned consensus change defined by the activation specification; there is
no runtime operator setter.

All encoded monetary amounts are unsigned integers. Additions and subtractions MUST reject
overflow or underflow. Products and divisions in the rules below MUST produce the exact
mathematical integer result. A checked unsigned 128-bit implementation suffices for these
ranges: even MAX_MONEY * (2^64 - 1) * 100 is less than 2^128. No floating point, saturating
arithmetic, silent truncation, approximate ratio, or overflow-dependent validity is permitted.

`floor_div(a,b)` is integer floor for a >= 0 and b > 0. `ceil_div(a,b)` is `a / b + (a % b !=
0)` using integer quotient and remainder. An implementation using `a + b - 1` must establish
that the intermediate does not overflow.

A debt-bearing vault is safe for opening/withdrawal exactly when:

    C * P * 100 >= D * q * 250

A vault is liquidatable exactly when D > 0 and:

    C * P * 100 < D * q * 200

Equality at 250 percent passes the opening test. Equality at 200 percent is not liquidatable.
Debt-free vault operations do not need a conversion price.

## State and transaction shape

At activation, the new value pool, vault set, S and B start empty/zero. Existing ZEC is not
reissued into a trusted fixture. Ordinary native input authorization and ZEC supply rules
continue to apply.

Each live vault has an immutable owner authorization key, collateral C > 0, principal D, and one
current native reference. D MUST be zero or at least D_MIN. The wire proposal defines a current
reference as the creating transaction identifier alone, because each transaction has at most one
financial operation. A transition consumes the current reference once and creates at most one
successor. A spent or nonexistent reference cannot be revived by asserting its former balances.

A native transaction contains at most one optional financial operation: NONE, OPEN, UPDATE,
CLOSE, LIQUIDATE or RETIRE_BAD_DEBT. It can also contain permitted native ZEC inputs/outputs and
native zUSD inputs/outputs. NONE permits an ordinary zUSD transfer with no issuance or burn.
OPEN incorporates initial borrowing; CLOSE incorporates full repayment. This gives atomic
opening/borrowing and repayment/closure without an arbitrary program or action list.

A transaction with NONE and no oracle certificate requires at least one zUSD input, as specified
by the wire grammar. Unrelated ordinary ZEC transactions remain valid under their existing
format rules.

The owner signs the entire authorized transaction body and relevant resolved previous values
under the new native signing domain. Recipient selection for newly borrowed zUSD is covered by
that signature. This is equivalent in financial effect to the model's Borrow followed by
Transfer, although the model credits the owner first. No conversion between Ed25519 and
secp256k1 identities, pre-registered model/native key map, fixture chain domain, account nonce
or whole-parent-state intent is adopted by these core rules.

For each transaction define native zUSD input value I_s, native output value O_s, permitted mint
M and permitted burn R. The required native stable value balance is:

    I_s + M = O_s + R

Only the explicit rules below authorize M or R. Output omission, a memo, a claimed burn field or
an inaccessible key is not an accounting burn. S counts the total value of consensus-recognized
unspent zUSD outputs, including outputs whose private keys have been lost.

For a vault-changing transaction, write C_old = 0 for OPEN and C_new = 0 for CLOSE/LIQUIDATE.
Its ZEC balance is:

    I_zec + C_old = O_zec + C_new + F_zec

For NONE and RETIRE_BAD_DEBT both collateral terms are zero. F_zec is a nonnegative native
transaction fee accounted for by the ordinary block/coinbase fee rules. No zUSD fee, collateral
subsidy or increase in ZEC supply is authorized. Normal relay/mining policy may require a
positive fee; this equation does not invent a positive consensus minimum. Exact indexed
collateral payouts described below cannot silently have fees subtracted from them.

After each ordered transaction:

    S = sum(live vault principal) + B
    S = sum(value in native unspent zUSD outputs)
    vaultPoolBalance = sum(live vault collateral)
    0 <= vaultPoolBalance <= MAX_MONEY
    0 <= S <= S_MAX
    0 <= B <= S

The second equality is replaced only by an explicitly specified public/shielded value-pool
equality in a later shielded extension. It is not a requirement to determine whether an owner
still knows a private key.

## Oracle use

A price-dependent operation MUST bind the exact canonical report identifier accepted by the
oracle specification, not merely a height or a caller-asserted price. It MUST reject if that
report is absent, no longer canonical, or outside its allowed validity/anchoring window. The
Oracle rules below use seven configured reporters, five matching signatures and a maximum
twelve-block anchored observation age. Those acceptance and ordering rules are specified in the
Oracle rules below, not redefined here.

Operations without a price requirement use the canonical zero/absent oracle identifier specified
by the wire format. Repayment, collateral addition without borrowing, debt-free
withdrawal/closure, ordinary transfer and bad-debt retirement remain possible during oracle
outages. No validator fetches a price from the web or uses its local wall clock.

## OPEN

OPEN supplies C_new > 0, immutable owner authorization and D_new. The owner authorizes the
transaction. Native ZEC inputs fund C_new through the value balance above; existing collateral
cannot simultaneously remain spendable elsewhere.

D_new MUST be zero or at least D_MIN. If D_new > 0, B at transaction entry MUST be zero; the
exact fresh canonical report is required; the 250-percent inequality MUST hold for
(C_new,D_new); and S + D_new MUST be <= S_MAX. Set M = D_new, R = 0, S' = S + D_new and B' = B.
If D_new = 0, no oracle is required.

## UPDATE

UPDATE consumes one current vault and retains its owner. Let delta_C = C_new - C_old and delta_D
= D_new - D_old, understood as mathematical signed differences rather than a wrapping unsigned
calculation.

C_new MUST be strictly positive. D_new MUST be zero or >= D_MIN. An unchanged pair (C_new,D_new)
= (C_old,D_old) is rejected. A transition to (0,0) uses CLOSE; no empty live vault is retained.
These restrictions remove two needless successor forms accepted by the account prototype and are
explicit proposed encoding/state changes.

If delta_D > 0, B at transaction entry MUST be zero, a fresh exact canonical report MUST be
bound, the final state MUST satisfy the 250-percent inequality, and S + delta_D MUST be <=
S_MAX. Set M = delta_D and R = 0.

If delta_D < 0, burn R = -delta_D actual native zUSD and set M = 0. If delta_D = 0 both are
zero. There is no owner-authorized debt forgiveness. Repayment that leaves debt strictly between
zero and D_MIN is invalid.

If C_new < C_old and D_new > 0, a fresh exact canonical report and the final 250-percent
inequality are also required, even when debt decreases. If C_new < C_old, the indexed owner
payout MUST equal C_old - C_new; it MUST use the owner's prescribed native payment lock. If
C_new >= C_old, no collateral-release payout exists. Deposits fund the increase through native
inputs.

Set S' = S + M - R and B' = B. Owner authorization is required for all UPDATE forms, including
pure deposit and pure repayment, matching the reference policy. A future third-party
repayment/deposit facility requires an explicit change; it is not silently inferred from the
absence of collateral release.

## CLOSE

CLOSE consumes one current vault, requires its owner authorization, burns exactly R = D_old
actual native zUSD, pays exactly C_old to the owner's indexed native payout and creates no
successor. M = 0, S' = S - D_old and B' = B. It needs no oracle even when D_old > 0 because the
entire debt is paid in the same transaction.

This combines the existing model's Repay(full debt) followed by Close. The model's standalone
Close requires debt already zero; the native combined encoding does not forgive the old
principal.

## LIQUIDATE

LIQUIDATE consumes and closes one current vault. It requires the exact fresh canonical report,
D_old > 0, and the strict 200-percent liquidation inequality. Borrower authorization is
unnecessary. The liquidator authorizes the complete transaction and can be any holder, including
the borrower.

Compute using the original C and D:

    x = min(D, floor_div(C * P * 100, q * 105))
    z = ceil_div(x * q * 105, P * 100)

The verifier MUST establish 0 <= z <= C. It MUST require x <= signed_max_burn and z >=
signed_min_collateral. R = x and M = 0. The transaction consumes actual native zUSD sufficient
for x and returns permitted change through the stable value equation.

The indexed liquidator payout MUST be exactly z zatoshi under the signed liquidator payment key.
The indexed owner payout MUST be exactly C-z under the immutable owner's payment key. Payout
indices MUST be unambiguous and cannot count the same output twice; the zero-value sentinel
convention is specified by the wire format. No successor vault remains.

Set:

    S' = S - x
    B' = B + (D - x)

This retains the model's full-vault liquidation policy and rounding. If x = 0, z = 0 and the
operation remains valid when the signed bounds permit it. No zUSD input is then required solely
for the zero burn, and the owner receives C; the entire D becomes bad debt. The native ZEC
fee/value rules still apply. There is no claim that anyone has an economic incentive to submit
that dust liquidation.

Liquidation with insufficient actual liquidator zUSD rejects; it does not reduce x to the
caller's balance or silently leave a partial vault. A price crash can create B > 0 even with
honest reporters and immediate execution.

## RETIRE_BAD_DEBT

This new proposed operation makes recovery possible without a reserve or privileged reset. A
holder chooses an integer r satisfying 0 < r <= B at transaction entry. The holder must
authorize spending actual zUSD inputs. Set R = r, M = 0, S' = S-r and B' = B-r. No vault is
consumed or changed, no oracle is needed, and no ZEC is paid by the protocol.

The holder receives no redemption claim, future repayment right, reward entitlement, priority,
governance privilege or ownership of another vault. Ordinary input change is returned under the
signed transaction. The operation is an uncompensated token burn against recorded bad debt.

A NONE or RETIRE_BAD_DEBT transaction cannot create zUSD or borrow. The one-operation grammar
prevents combining bad-debt retirement with newly minted debt in the same transaction. A later
transaction can borrow only after preceding valid retirement has actually reduced B to zero.

This operation is absent from the current Rust model and collateral profile. Its new conformance
vectors and future implementation must be tracked separately from passing legacy tests.

## Loss and liveness policy

Borrowing is prohibited while B > 0. Existing transfers, valid debt repayment, deposits,
permitted withdrawals/closure, liquidation and RETIRE_BAD_DEBT continue. The freeze is based on
recorded B at the operation's ordered transaction entry; latent losses in unliquidated vaults
are not magically detected.

Only a valid RETIRE_BAD_DEBT reduces B in this core version. No clock, oracle report, miner
field, operator key or bookkeeping reset may erase liabilities. S decreases by the same amount,
preserving the debt/supply identity. A future separately approved reserve mechanism could fund
voluntary retirement using tokens it actually owns; no such funding or reserve authority is
activated by this core.

Borrowing resumes automatically when the actual B value reaches zero and the normal
fresh-price/collateral/cap conditions pass. If no holder is willing to retire tokens, the freeze
can persist indefinitely. The protocol does not guarantee recapitalization, price recovery or a
dollar redemption right. This is an explicit complete loss policy with a remaining economic
availability risk, rather than an unspecified administrative recovery hook.


## Complete block transition and persistence

Validation MUST begin from the candidate block's exact parent state, independently of the node's
currently selected tip. The candidate includes ordinary native UTXOs and value pools, the ZEC
vault pool/current vault set, stable UTXOs, S, B, canonical oracle state, fee accounting and
activation context. No caller-asserted balance or post-state replaces validation against that
parent.

Validators MUST apply every ordinary and ZSV transaction in block order to a private candidate
state. Later transactions see the valid outputs, spent references and state changes of earlier
transactions in that block. The oracle placement rules below determine when a certificate
becomes usable. A missing, already spent or duplicate input/reference is invalid; creating an
output or current vault reference MUST NOT overwrite an existing unspent entry in its namespace.
The absence of a ZSV operation in an ordinary transaction cannot authorize access to the
separate vault or stable value pools.

Each transaction MUST satisfy its native and ZSV rules, exact payouts, per-asset balances,
monetary bounds and applicable state invariants before the next transaction is evaluated. The
vault-pool delta is applied atomically with ordinary ZEC input/output and fee deltas, so
collateral is never counted as both an ordinary output and a vault balance. A block that fails
any transaction, oracle, resource, commitment or ordinary consensus check MUST be rejected with
no persistent changes to any of these states.

Only a fully valid block may commit the complete candidate transition. Reorganization,
finalization and restart MUST reconstruct the same parent-derived state as ordered replay of the
accepted branch. Mempool admission is provisional and MUST NOT substitute for block-context
validation. Checkpoint and direct-finalization paths MUST enforce equivalent rules and establish
matching ZSV state; a path that merely skips the new checks or imports asserted ZSV balances is
invalid. This specification requires equivalent results, not a particular database layout or
caching strategy.

## Oracle rules

### Deployment roster and domains

For each activated ZSV consensus branch, the deployment specification MUST provide seven
distinct Ed25519 public keys, ordered lexicographically by their 32-byte encodings. The keys
MUST use canonical encodings of non-identity points in Ed25519's prime-order subgroup. In group
notation, each decoded key A satisfies A != identity and [ell]A = identity, where ell is the
Ed25519 subgroup order. Canonical encoding means re-encoding the decoded point using the RFC
8032 compressed encoding reproduces the 32-byte input exactly.

The reporter set is fixed for that consensus branch. There is no oracle transaction,
administrator signature, voting token or runtime configuration that changes the roster, quorum
or freshness period. A roster change requires an explicitly specified network upgrade. Local
configuration MUST NOT override the deployment roster.

Define:

```text
reporterSetID = SHA256(
    ASCII("ZSV/OracleSet/v1\0") ||
    u8(7) || u8(5) ||
    key[0] || ... || key[6]
)
```

Here `\0` is one zero byte, concatenation is byte concatenation, and SHA256 returns its 32 raw
digest bytes. The active network's genesis hash is the 32-byte consensus serialization used for
block-hash fields, not the human-readable reversed hexadecimal presentation. The active
consensus branch ID is encoded as an unsigned 32-bit little-endian integer.

### Report encoding

A report's effect fields have the following exact encoding. There is no CompactSize or other
length prefix within this structure:

| Field | Bytes | Encoding |
|---|---:|---|
| observedHeight | 4 | unsigned little-endian |
| observedBlockHash | 32 | raw consensus block-hash serialization |
| price | 8 | unsigned little-endian, micro-USD per ZEC |
| signerMask | 1 | bit i corresponds to roster key i |

The first three fields form the 44-byte `reportBody`. The complete effect structure is 45 bytes.
`price` MUST be in `1..=2^64-1`; zero is invalid. Bit 7 of `signerMask` MUST be zero. Its
population count MUST be 5, 6 or 7. The authorization section contains exactly that many 64-byte
Ed25519 signatures, in increasing signer-index order. Signature count is derived from the mask;
no independently asserted count is accepted.

Every included signature verifies the same 126-byte message:

```text
oracleMessage =
    ASCII("ZSV/Oracle/v1\0") ||        # 14 bytes
    networkGenesisHash ||              # 32 bytes
    LE32(activeConsensusBranchID) ||    # 4 bytes
    reporterSetID ||                    # 32 bytes
    reportBody                         # 44 bytes

oracleID = SHA256(oracleMessage)
```

`oracleID` deliberately excludes the signer mask and signatures. Different valid quorum subsets
for the same observation therefore identify the same price report. The transaction's ordinary
effect/authentication digests still commit the mask and signatures as specified by the
transaction format.

Ed25519 signature verification MUST follow ZIP 215's exact verification criteria [^zip-0215]: A
and R decode to Ed25519 points, S_sig < ell, and the cofactored equation [8][S_sig]B_Ed = [8]R +
[8][k]A holds with k = SHA512(R_bytes || A_bytes || oracleMessage) interpreted as a
little-endian integer modulo ell, using the supplied R and A encodings as specified by ZIP 215
and RFC 8032. Implementations MUST NOT substitute a different library's unspecified "strict
Ed25519" acceptance rules or the uncofactored equation. The deployment-key restrictions above
are additional restrictions on the fixed roster; they do not change ZIP 215's acceptance rules
for signature R encodings. An included invalid signature invalidates the certificate even when
five other signatures verify. In this signature equation, S_sig is the signature scalar and B_Ed
is the standard Ed25519 base point, independent of stable supply S and bad debt B. SHA512 here
is the 64-byte SHA-512 hash; it is distinct from the SHA256 report identifier.

The effect structure and authorization together use 365 bytes for five signatures and 493 bytes
for seven signatures, excluding enclosing transaction framing. There is no price median,
averaging rule or node-local price selection: a certificate authorizes one identically signed
price tuple.

### Inclusion, observed ancestry and freshness

Let H be the candidate block height, A the first height of the active consensus branch and h the
report's `observedHeight`. Validators MUST enforce all of the following before accepting a
report:

1. `A - 1 <= h < H`, with A positive for an activated ZSV branch.
2. `h + 12` is representable as a u32, and `H <= h + 12`.
3. `observedBlockHash` equals the actual ancestor block hash at height h on the candidate block's parent chain.
4. If an observation was already accepted under this active branch and reporter set, h is strictly greater than that observation's height.
5. The price, signer mask, signature lengths and every signature satisfy the rules above.

A certificate included at height I can price operations only in descendants at heights `I + 1`
through `h + 12`, inclusive, while it remains the parent-selected observation. The earliest
possible pricing height is `h + 2`. The twelve-block bound is a maximum observation age, not a
guaranteed transaction-validity period. A certificate included at `h + 12` has no remaining
pricing lifetime. There is no signed arbitrary expiry field, no free-running sequence field and
no future-dated report. The observed height supplies the monotonic sequence. An inclusion delay
consumes the report's lifetime; re-inclusion cannot refresh it.

At the first ZSV activation or a change of the active consensus branch/domain, the block pricing
observation is empty. A valid certificate under the new domain can be recorded in that block,
but becomes usable only in its descendants under the rules below. An observation signed for an
older branch cannot authorize new price-dependent operations. Reports may use the last block
before activation as their observed ancestor, provided their signatures use the newly active
domain. Existing vault/payment/liability state is not reset by this oracle-domain change.

### Block order and transaction restrictions

A block contains at most one ZSV oracle certificate. If present, it MUST occur in the first
non-coinbase transaction. That transaction MUST contain no vault operation or stablecoin
input/output. Ordinary ZEC inputs and outputs may fund its network fee, subject to the new
transaction format's ordinary ZEC rules. The certificate is not carried in coinbase and does not
create value.

At block entry, validators MUST select the pricing observation from the exact parent's committed
oracle state under the active domain. That selection is fixed for all operations in the
candidate block. A valid certificate in the candidate block MUST update only the oracle state
committed for descendants; it MUST NOT replace the block's pricing observation. With no
certificate, retain the applicable parent observation in committed state, including its original
observation height. Expiry makes it unusable for pricing but does not erase its height for the
strictly advancing report rule. A second certificate, or one after any other non-coinbase
transaction, invalidates the block. There is no requirement to include a certificate; a
coinbase-only block remains valid under the ordinary block rules.

Every borrowing, debt-bearing withdrawal and liquidation operation MUST bind `oracleID` and MUST
use the fixed parent-selected pricing observation. The candidate height MUST be no greater than
that observation's `observedHeight + 12`. A newly included certificate cannot rescue an absent
or expired pricing observation in the same block. An operation naming an observation other than
the block's pricing observation, or naming an expired or absent observation, is invalid even if
that observation carries an otherwise valid quorum certificate. The operation's ordinary
transaction expiry applies independently and cannot extend the oracle window.

No node-local clock, URL fetch, API response, observed mempool certificate or external service
result is consulted during consensus validation. A producer may omit a certificate or choose
among admissible certificates for descendants; all operations in the current block still use its
parent-selected observation.

### Outages, conflicting reports and recovery

An absent or expired block pricing observation disables borrowing, debt-bearing withdrawal and
liquidation. It does not disable collateral additions, repayment, stable transfers, debt-free
withdrawal/closure or an explicitly specified bad-debt retirement that burns actual stable
value. Expiry does not itself move collateral, forgive debt, trigger a privileged settlement or
authorize liquidation using a fabricated fallback price.

A later valid certificate can resume price-dependent operations from the following block, if
still fresh, subject to all other protocol rules, including any bad-debt issuance freeze. Report
failure alone does not reset liabilities or replace reporter keys. If the committee cannot
recover, the specified remedy is a reviewed network upgrade rather than an administrator bypass.

Two certificates with different prices for the same observation height cannot both be accepted
on one branch because observed heights strictly advance and a block admits at most one
certificate. Competing forks may accept different valid certificates. Fork choice and
reorganization select the corresponding complete vault/oracle/payment state. Evidence of
reporter equivocation does not automatically change the committee, seize funds or suspend the
chain in v1; no slashable reporter bond is specified.


# Rationale

## A dedicated fixed-asset protocol

The proposal uses a dedicated transaction format and implicit zUSD payment fields. There is no
caller-chosen asset identifier or issuer path. A dedicated ZEC vault value pool removes
collateral from ordinary spendable outputs; the experimental `OP_DROP OP_TRUE` marker is not
used as a native lock.

General ZSA issuance, a generic VM and external custody were considered. General issuance and a
VM broaden the permitted activity, while external custody fails the requirement that Zcash
enforce vault rules. Selected ZSA transfer and proof techniques may still be useful in a future
shielded profile. The public first version trades payment privacy for a smaller initial
specification; it does not claim to deliver a private dollar payment instrument.

One financial operation per transaction limits ordering ambiguity. Open-with-debt and
repay-and-close remain atomic. A vault update replaces one current state; it does not accumulate
reusable owner-local identifiers. The specified native signatures use one owner-key scheme
instead of the prototype's permanent mapping between two key schemes.

## Economic policy

The 250% borrowing ratio, 200% liquidation ratio, 5% bonus, 100-zUSD minimum debt and
100,000-zUSD liability ceiling are concrete proposed initial values taken from the research
model. They are not calibrated safety guarantees. A 20% collateral-price decline moves a vault
from 250% to 200% before oracle delay, execution costs or market gaps. Full liquidation can
create bad debt despite valid accounting.

The ceiling limits initial nominal exposure; it does not bound ZEC value lost to a false price,
guarantee liquidation depth or ensure a market peg. Repayment supplies a source of demand, but
holders receive no unconditional one-dollar redemption right. A reserve held in ZEC shares the
collateral's drawdown risk.

Retiring bad debt requires burning actual tokens. It transfers no collateral and creates no
privileged reset authority. A holder may nevertheless have no incentive to absorb the loss, so
borrowing can remain stopped indefinitely. Small shortfalls can trigger the freeze. Adding an
incentivized recapitalization or redemption system would change the economic proposal and needs
separate specification and review.

## Oracle and governance

Using the parent observation prevents a certificate included in the same block from invalidating
already-signed operations, even when reports arrive every block. Wallets can sign for the next
block using the current tip's committed oracle state. Transactions delayed beyond that block or
affected by a reorganization may still need re-signing. The cost is one block of additional
price delay: even a fresh crash report cannot change borrowing or liquidation prices in its
inclusion block. This tradeoff requires economic calibration; no history of user-selectable
prices or extra reporter authority is introduced.

The reporter quorum is an explicit external trust dependency. Signature thresholds do not prove
independent organizations, independent market sources or truthful prices. Fixed upgrade-selected
membership removes a runtime membership administrator but makes key replacement and recovery
slower. The freshness bound is measured in blocks; its wall-clock duration depends on actual
block production.

Changing consensus parameters or the reporter set requires a network upgrade under the specified
deployment process. No token vote, issuer key or reserve operator can change them. The roster,
parameter calibration and operational arrangements need public review before deployment.

## Reserve and funding boundary

The core has no reserve state, block-reward allocation, discretionary incentive spending or NSM
withdrawal. A companion proposal could add native reserve cash and already-issued token
inventory, but would need explicit funding, trade, allowance, closure and final-disposition
rules.

The research studies identify remaining risks: stale-price trading, limited market response,
losses occurring after a one-time reserve burn, and cheap terminal auctions under weak
competition. Accounting tests do not resolve these incentives. A proposed reduction in another
funding recipient's allocation does not itself allocate the difference to ZSV.

## Community discussion

No community endorsement, editor approval or public review outcome is claimed. The alias-named
draft is intended to start that discussion. Objections, alternatives and responses will be
recorded here when they exist. The mathematical studies and coding-agent adversarial reviews are
preliminary evidence, not the qualified independent expert review required for release of a
security-sensitive ZIP. [^zip-0000]

# Backward compatibility

Activation introduces a consensus change and requires upgraded validators. Existing ZEC
transaction formats and payment pools retain their rules. The new format supports a restricted
public funding path; wallet support and safe address presentation remain necessary for users to
construct it.

The prototype's V4/Sapling signatures, JSON envelopes, trusted funding coinbase, model account
nonces and whole-parent-checkpoint intents are not native consensus formats. Existing model
vectors remain research fixtures and are not migrated into network state. No experimental
fixture balance or key becomes a live allocation.

# Deployment

No target network upgrade or activation height is selected. Deployment needs explicit Mainnet
and Testnet activation parameters, transaction identifiers, domain inputs and public reporter
keys. These are deployment allocations, not node-local settings. Neither a ZIP number nor
merging a draft activates the feature.

Before a Released status such as Proposed, ZIP 0 requires the applicable editor/community
process and qualified independent security/privacy review for a proposal with these
implications. A complete reference implementation generally need not precede Proposed.
Implementation, testing and network activation are later, distinct milestones. [^zip-0000]

The deployment evidence should cover independent serialization and signature implementations,
cross-implementation valid/invalid block vectors, value conservation, every
acceptance/finalization path, reorgs and database restart, resource benchmarks, oracle
compromise/outage scenarios and economic losses. These checks cannot establish a guaranteed
market peg.

# Reference implementation

The [ZSV research
repository](https://github.com/iJaack/zsv/tree/d0f8529f08653744b7702670bc628b20b7d17b00)
provides a signed account model, economic studies and offline profiles linked to pinned Zebra
code. Its original code is MIT-licensed; upstream dependencies retain their own licenses. It is
not a complete implementation of this ZIP.

The model tests collateralized issuance, repayment, liquidation, explicit bad debt and optional
reserve accounting. The collateral profile verifies serialized fixture ZEC UTXOs and native P2PK
signatures with an experimental guard. The guard is outside Zebra's node verifier, and zUSD
remains a model balance. At that revision, 110 reference Rust tests, 39 Zebra-linked tests and
96 Python tests passed; all 351 combined economic cases reproduced. [^verification]

This candidate introduces rules beyond that code: a dedicated transaction and value-pool format,
normalized single-operation transitions, a different oracle policy, native signature domains and
permissionless retirement of bad debt. Passing the earlier tests is not evidence that those new
rules are implemented. The accompanying [conformance
material](https://github.com/iJaack/zsv/tree/main/zips/draft-ijaack-zsv) contains 54 financial
cases, seven unsigned wire/context/hash examples covering all operation tags and oracle framing,
and a canonical-signature oracle fixture. These are not a complete signed native transaction or
full-block consensus suite.

# Outstanding allocations and review

The protocol choices in Specification are proposed rules, subject to public review. The
remaining work before calling this a deployment-ready specification is:

1. Allocate the new transaction/group identifiers and upgrade context; select Mainnet/Testnet activation and the public reporter roster through the deployment process.
2. Independently review and implement the byte, digest, authorization and branch-state rules, and produce signed transaction and full-block conformance vectors.
3. Obtain qualified consensus/cryptographic/privacy review and resource benchmarks, and justify the economic parameters, oracle operations and loss policy against adversarial conditions.
4. Publish the forum announcement and add its discussion URL; rerun upstream rendering after metadata changes. This draft has been rendered with the ZIP repository's `render.sh --pandoc` path.

The public-first scope and Owners contact are confirmed. No editor-assigned number, named
reviewer, oracle operator or activation approval has been invented to fill these entries.

# References

[^BCP14]: [BCP 14: Key words for requirement levels](https://www.rfc-editor.org/info/bcp14).

[^zip-0000]: [ZIP 0: ZIP Process](https://github.com/zcash/zips/blob/ff594de6e95bb9e9e7d2ace09510281531c30447/zips/zip-0000.rst), reviewed 30 October 2026. The [Markdown template](https://github.com/zcash/zips/blob/ff594de6e95bb9e9e7d2ace09510281531c30447/zips/zip-template.md) provides the document structure.

[^verification]: [ZSV verification receipt at the collateral milestone](https://github.com/iJaack/zsv/blob/d0f8529f08653744b7702670bc628b20b7d17b00/docs/verification.md).

[^sources]: [Pinned Zcash and Zebra research sources](https://github.com/iJaack/zsv/blob/d0f8529f08653744b7702670bc628b20b7d17b00/docs/sources.md). The consensus research baseline is separate from the current ZIP-process reference above.

[^zip-0215]: [ZIP 215: Explicitly Defining and Modifying Ed25519 Validation Rules](https://github.com/zcash/zips/blob/2bdf39494320e5e04057ac93b1794031ebfb00b5/zips/zip-0215.rst).

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](https://github.com/zcash/zips/blob/2bdf39494320e5e04057ac93b1794031ebfb00b5/zips/zip-0244.rst).

[^zip-0239]: [ZIP 239: Relay of Version 5 Transactions](https://github.com/zcash/zips/blob/2bdf39494320e5e04057ac93b1794031ebfb00b5/zips/zip-0239.rst).

[^veylor]: [Veylor: How it works](https://veylor.cash/how-it-works/), read 5 November 2026. The described split-key swap is coordinated by an Ethereum contract; it is not native Zcash stablecoin issuance. [Contract source at the revision linked by Veylor](https://github.com/JustZappIt/zecSwap/blob/32cc6efca0f22589655eb2e61b00ec6d582e8570/contracts/src/ZecSwap.sol).
