    ZIP: XXX
    Title: Deferred Dev Fund Lockbox Disbursement
    Owners: Daira-Emma Hopwood <daira@jacaranda.org>
            Kris Nuttycombe <kris@nutty.land>
            Jack Grigg <jack@electriccoin.co>
    Status: Draft
    Category: Consensus / Process
    Created: 2025-02-19
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>

# Terminology

The key words "MUST", "SHOULD", "MAY", and "RECOMMENDED" in this document are
to be interpreted as described in BCP 14 [^BCP14] when, and only when, they
appear in all capitals.

# Abstract

This ZIP proposes an extension of protocol-based development funding, in the
context of multiple alternatives for distributing funds that have accrued to
the Deferred Dev Fund Lockbox. This proposal is intended to be evaluated in the
context of the Community And Coinholder Funding Model
[^draft-ecc-community-and-coinholder] and Zcash Governance Bloc
[^draft-ecc-zbloc] proposals; the mechanisms it describes are applicable to
both of these and may be applicable to other similar proposals as well.

At a high level, this ZIP proposes:
* A one-time disbursement of the full contents of the lockbox to a transparent
  P2SH multisig address, at the time of the activation of this ZIP. The
  key-holders for that address are then responsible for distributing the
  resulting funds in the form of development grants, according to the rules set
  by either [^draft-ecc-community-and-coinholder] or [^draft-ecc-zbloc], or
  another similar proposal.
* Extension of protocol-based development funding blocks starting from the
  scheduled end height of the current ``FS_DEFERRED`` and ``FS_FPF_ZCG``
  funding streams defined in ZIP 1015 [^zip-1015-funding-streams].
* A variety of different mechanisms that may be used for distributing funds
  that accrue during the period of the extension, which may vary depending upon
  the proposal that uses this mechanism.

# Requirements

* Funds are held in a multisig resistant to compromise of some of the parties'
  keys, up to a given threshold.
* No single party's non-cooperation or loss of keys is able to cause any
  Protocol-defined Ecosystem Funding to be locked up unrecoverably.
* The funds previously accrued to the Deferred Dev Fund Lockbox as the activation
  height of this ZIP will be usable immediately on activation.

# Specification

This ZIP proposes the creation of a new Zcash Development Fund. The balance of
this Fund consists of the contents of the ZIP 1015 Deferred Development Fund
Lockbox as of the activation height of this ZIP, plus any funds that later
accrue to either the lockbox or to one or more transparent multisig addresses
as specified by this ZIP.

### One-time lockbox disbursement

The coinbase transaction of the activation block of this ZIP MUST include an
additional output to a 2-of-3 P2SH multisig with keys held by the following
"Key-Holder Organizations": Zcash Foundation, the Electric Coin Company,
and Shielded Labs.

Let $v$ be the zatoshi amount in the Deferred Dev Fund Lockbox as of the end
of the block preceding the activation height. ($v$ can be predicted in advance
given that height.)

The additional coinbase output MUST contain at least one output that pays
$v$ zatoshi to the above P2SH multisig address, using a standard P2SH script
of the form $\texttt{OP\_HASH160}$ $\mathsf{RedeemScriptHash}(\mathsf{height})$
$\texttt{OP\_EQUAL}$ as the $\mathtt{scriptPubKey}$. $v$ zatoshi are added to
the transparent transaction value pool of the coinbase transaction to fund
this output, and deducted from the balance of the Deferred Dev Fund Lockbox.
The latter deduction occurs before any other change to the Deferred Dev Fund
Lockbox balance in the transaction, and MUST NOT cause the Deferred Dev Fund
Lockbox balance to become negative at that point.

Exactly one of the following options will also be taken. The proposal that
activates this ZIP must define values for the following two parameters:

* $\mathsf{stream\_value}$: the percentage of the block subsidy to send to 
  a new funding stream, as described in the options below.
* $\mathsf{stream\_end\_height}$: The ending block height of that stream.

Note: The value $v$ might need to be precalculated so that it is known at
the point when the relevant consensus check is done in node implementations.
If so, the specification should be written in terms of the precalculated
value.

### Option 1: Extend the lockbox funding stream

The ``FS_DEFERRED`` lockbox funding stream is set to receive
$\mathsf{stream\_value}\%$ of the block subsidy and is extended until block
height $\mathsf{stream\_end\_height}$. Both of these parameters must be
specified by the proposal under which this ZIP is activated.

#### Rationale for Option 1

Performing a one-time disbursement to a P2SH multisig address will provide a
source of grant funding for a limited period, allowing time for a lockbox
disbursement mechanism to be specified and deployed, as originally intended by 
ZIP 1015 [^zip-1015].

In particular, this provides an opportunity for transaction format changes that
may be required for such a mechanism to be included in the v6 transaction
format [^zip-0230]. It is desirable to limit the frequency of transaction
format changes because such changes are disruptive to the ecosystem. It is not
necessary that protocol rules for disbursement actually be implemented until
after the transaction format changes are live on the network. It is RECOMMENDED
that any such transaction format changes be included in the upcoming v6
transaction format in order to avoid such disruption.

By implementing a one-time disbursement along with a continuation of the
``FS_DEFERRED`` stream, we prioritize both the availability of grant funding
and the implementation of a more flexible and secure mechanism for disbursement
from the lockbox — making it possible to address the need to rotate keys and/or
alter the set of key holders in a way that reverting to hard-coded output
addresses for repeated disbursements would not.

### Option 2: Revert to hard-coded output address

A new funding stream consisting of $\mathsf{stream\_value}\%$ of the block
subsidy is defined to begin when the existing ZIP 1015 funding streams
[^zip-1015-funding-streams] end. The new streams will distribute funds to a
3-of-5 P2SH multisig with keys held by the same Key-Holder Organizations as
above. The resulting Fund is considered to include both this stream of funds,
and funds from the one-time lockbox disbursement described above.

Option 2 can be realized by either of the following mechanisms:

#### Mechanism 2a: Classic funding stream

A new funding stream is definedthat pays directly to the above-mentioned 3-of-5
multisig address on a block-by-block basis. It is defined to start at the end
height of the existing ``FS_DEFERRED`` funding stream and end at
$\mathsf{stream\_end\_height}$ and consists of $\mathsf{stream\_value}\%$ of the
block subsidy.

#### Mechanism 2b: Periodic lockbox disbursement

Constant parameter $N = 35000$ blocks $=
\mathsf{PostBlossomHalvingInterval}/48$ (i.e. approximately one month of
blocks).

The ``FS_DEFERRED`` lockbox funding stream is extended to end at height
$\mathsf{stream\_end\_height}$ and has its per-block output value set to
$\mathsf{stream\_value}\%$ A consensus rule is added to disburse from the
Deferred Dev Fund Lockbox to a 2-of-3 P2SH multisig with keys held by the same
Key-Holder Organizations as above, starting at block height
$\mathsf{activation\_height} + N$ and continuing at periodic intervals of $N$
blocks until $\mathsf{stream\_end\_height}$. Each disbursement empties the
lockbox. 

This is equivalent to specifying
$\frac{\mathstrut\mathsf{stream\_end\_height} \,-\, \mathsf{activation\_height}}{N}$ [One-time lockbox disbursement]s, 
that all output to the same address.

#### Rationale for periodic disbursement

Classic funding streams [^zip-0207] produce many small output values, due to
only being able to direct funds from a single block's subsidy at a time. This
creates operational burdens to utilizing the funds — in particular due to block
and transaction sizes limiting how many outputs can be combined at once, which
increases the number of required transactions and correspondingly the overall
fee.

The periodic lockbox disbursement mechanism can produce the same effective
funding stream, but with aggregation performed for free: the output to the
funding stream recipient is aggregated into larger outputs every $N$ blocks. In
the specific case of Mechanism 2b, the recipient multisig address would receive
around 40 outputs, instead of around 1,300,000.

# Privacy and Security Implications

As development funding is a public good on the Zcash network, there are not
relevant privacy concerns related to this proposal; all disbursement of
(but not necessarily subsequent distribution) of development funds is 
transparent and auditable by any participant in the network.

#### Security implications of the One-Time Lockbox Disbursement

After the activation block of this ZIP has been mined, all development funds
previously accrued to the in-protocol lockbox will be held instead by a 2-of-3
multisig address. The key-holders for this address will have the capability to
spend these funds. Compromise or loss of 2 of these 3 keys would result in
total loss of funds; as such, in the event of the compromise or loss of a
single key, the Key-Holders MUST establish a new multisig key set and address,
and transfer remaining unspent funds held by the original address before
additional loss or compromise occurs.

Because this is a one-time disbursement, additional key rotation infrastructure
is not required.

#### Security implications for Option 1

Funds will continue to securely accrue to the Deferred Development Lockbox
until a disbursement mechanism for the lockbox is implemented in a future
network upgrade. Such a disbursement mechanism should be designed to include an
in-protocol option for key rotation, such that it is not necessary to perform a
network upgrade to recover from key loss or compromise, or to change the size
of the signing set or the number of signatures required to reach threshold.

#### Security implications for Mechanism 2a

As of the activation height of this ZIP, development funds will begin accruing
as additional outputs spendable by a 2-of-3 multisig address on a
block-by-block basis. Key-Holders will need to perform regular multiparty
signing ceremonies in order to shield the resulting coinbase outputs. Each such
signing ceremony involves shared spending authority being used to sign
thousands of inputs to large shielding transactions; for practical reasons,
this is often handled using a scripted process that has spending authority over
these funds. This process is an attractive target for compromise; for this
reason it is RECOMMENDED that address rotation (in this case, by means of
hard-coding a sequence of addresses, each of which receives a time-bounded 
subset of the block reward fractional outputs) be implemented, as was done
for the ECC funding stream described in ZIP 1014 [^zip-1014].

In the case of key compromise or loss, it may be necessary to perform an
emergency Network Upgrade to perform a manual key rotation to ensure that
future development funds are not lost.

#### Security implications for Mechanism 2b

Due to the aggregation of funds recommended by Option 2b, it is no longer
necessary to use scripts with spending privileges to perform shielding and/or
distribution operations; instead, these operations can be performed by human
operators using an interactive protocol that does not require sharing spending
key material.

As with Option 2a, key compromise or loss would require an emergency Network
Upgrade to perform manual key rotation to mitigate the potential for loss of
funds.

# References

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0207-consensus-rules]: [ZIP 207: Funding Streams — Consensus Rules](zip-0207#consensus-rules)

[^zip-0230]: [ZIP 230: Version 6 Transaction Format](zip-0230.rst)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-funding-streams]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Funding Streams](zip-1015#funding-streams)

[^draft-ecc-zbloc]: [draft-ecc-zbloc: Zcash Governance Bloc](draft-ecc-zbloc.md)

[^draft-ecc-community-and-coinholder]: [draft-ecc-community-and-coinholder: Community and Coinholder Funding Model](draft-ecc-community-and-coinholder.md)

