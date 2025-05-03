> ZIP: unassigned
> Title: Air drops, Proof-of-Balance, and Stake-weighted Polling
> Owners: Daira-Emma Hopwood <daira@electriccoin.co>
>         Jack Grigg <jack@electriccoin.co>
> Status: Draft
> Category: Informational
> Created: 2023-12-07
> License: MIT


# Terminology

The key words "MUST", "MUST NOT", and "MAY" in this document are to be
interpreted as described in BCP 14 [#BCP14]_ when, and only when, they appear in
all capitals.

"Pool snapshot" refers to a snapshot of the state of balances in a shielded pool
as of the end of a specified block.

"Claim" refers to a proof by a ZEC holder (TODO: support ZSAs) that they held a
set of notes summing to a committed value at the time of a given pool snapshot.


# Abstract

This ZIP specifies a mechanism that effectively takes a snapshot of the state of
shielded balances in the Orchard pool, and allows holders to prove that they had
at least a given balance as of the snapshot, in such a way that they cannot claim
the same balance more than once. The privacy of holders is retained, in the sense
that claims cannot be linked to their past or future spends.

Possible applications include private air drops, private proof-of-balance, and
private stake-weighted polling.


# Motivation

TODO: Explain why this can't be done more simply, and how the problem is
isomorphic to air-drops and stake-weighted polling.

> Do we need to be able to construct a note in another token corresponding to the
> claimed value? Can that be done just with the existing ZSA spec + a public value
> commitment?


# Requirements

Who is eligible to vote / claim an airdrop?
* Most likely approach: snapshot the Zcash chain at some height. Eligible notes
  exist in the commitment tree at that height, but don’t exist in the nullifier
  set at that height.

Does the Zcash side need to prove spend authority?
* Yes, it does (otherwise if people gave out their viewing keys to others, those
  others could vote / claim the airdrop instead).
* UX effect: anyone who moved their funds to a different spend authority after
  the snapshot and then lost their old spending keys become unable to vote /
  claim the airdrop.


# Specification

Sketch:

A "nullifier non-membership tree" is a Merkle tree of sorted disjoint
(start, end) pairs representing the gaps between revealed nullifiers at a pool
snapshot. That is, the union of the regions start..=end is exactly the
complement of the set of revealed nullifiers at the snapshot.

An "alternate nullifier" is a value derived from a note, with similar
cryptographic properties to its standard nullifier, but including a "nullifier
domain" as input to the derivation. It is distinct from and unlinkable with the
standard nullifier, or any of the other alternate nullifiers for that note in
other nullifier domains. A note has exactly one alternate nullifier for each
nullifier domain.

An entity that wants to conduct an air-drop, stake-weighted poll, etc. does the
following:

* Choose a pool snapshot at a particular block height.
* Choose a previously unused nullifier domain $\mathsf{dom}$.
  * > TODO: how to ensure it is previously unused? What are the consequences if it isn't?
  * Maybe the domain is derived from the pool snapshot and a string identifying
    the air-drop/poll? Then a wallet that supports this protocol can display the
    string and the block height/date of the snapshot to the wallet user.
* Deterministically construct a nullifier non-membership tree as of the snapshot,
  with root $\mathsf{rt^{excl}}$. Anyone can check that this root is correct using
  public information.
* Keep track of a set of alternate nullifiers revealed by the statement below and
  make sure that they don't repeat.

To participate, a holder proves the following informal statement:

"Given:
* a value commitment $\mathsf{cv}$;
* a nullifier domain $\mathsf{dom}$;
* an alternate nullifier $\mathsf{nf_{dom}}$;
* a pool snapshot $(\mathsf{rt^{cm}}, \mathsf{rt^{excl}})$;

I am the holder of a note $\mathbf{n}$ that is unspent at pool snapshot
$(\mathsf{rt^{cm}}, \mathsf{rt^{excl}})$, such that $\mathbf{n}$ has value
commitment $\mathsf{cv}$ and alternate nullifier $\mathsf{nf_{dom}}$ in
nullifier domain $\mathsf{dom}$."

### Another possible approach

Have the holder *actually* spend the claimed notes (e.g. to themself) with an
anchor at the pool snapshot. This has the disadvantage that they cannot
participate in concurrent polls/air-drops.

## Alternate nullifier derivation

Given a nullifier domain $\mathsf{dom}$ and an Orchard note
$\mathbf{n} = (\mathsf{d^{old}}, \mathsf{pk_d^{old}}, \mathsf{v^{old}}, \text{ρ}^{\mathsf{old}}, \text{φ}^{\mathsf{old}}, \mathsf{rcm^{old}})$
with note commitment $\mathsf{cm^{old}}$, the alternate nullifier $\mathsf{nf_{dom}}$
for $\mathbf{n}$ is computed as:
$$
\begin{array}{rcl}
\mathsf{nf_{dom}} &\!\!\!=\!\!\!& \mathsf{DeriveAlternateNullifier_{nk}}(\text{ρ}^{\mathsf{old}}, \text{φ}^{\mathsf{old}}, \mathsf{cm^{old}}, \mathsf{dom}) \\
&\!\!\!=\!\!\!& \mathsf{Extract}_{\mathbb{P}}\big(\big[(\mathsf{PRF^{nfAlternate}_{nk}} (\text{ρ}^{\mathsf{old}}, \mathsf{dom}) + \text{φ}) \bmod q_{\mathbb{P}}\big]\, \mathcal{K}^\mathsf{Orchard} + \mathsf{cm^{old}}\big)
\end{array}
$$

Here $\mathsf{PRF^{nfAlternate}}$ is another instantiation of Poseidon. In order
for $\mathsf{dom}$ to be an arbitrary field element without any loss of security,
it would have to use an instantiation of Poseidon with a 4-element to 4-element
permutation.

> TODO: security analysis, in particular for collision attacks and for linkability across domains.


<details>
<summary>

### Rationale for not using a similar nullifier derivation to ZSA split notes
</summary>

The nullifier derivation in draft ZIP 226 for ZSA split notes is:
$$
\mathsf{nf} = \mathsf{Extract}_{\mathbb{P}}\big(\big[(\mathsf{PRF^{nfOrchard}_{nk}} (\text{ρ}^{\mathsf{old}}) + \text{φ}') \bmod q_{\mathbb{P}}\big]\, \mathcal{K}^\mathsf{Orchard} + \mathsf{cm^{old}} + \mathcal{L}^\mathsf{Orchard}\big)
$$ This fails to do what we want in two ways:
* It is nondeterministic, due to the random $\text{φ}'$.
* If $\text{φ}'$ were required to be $\text{φ}^{\mathsf{old}}$ and
  $\mathcal{L}^\mathsf{Orchard}$ were replaced by a hash-to-curve of
  $\mathsf{dom}$, then nullifiers for different domains (including the original
  ZEC domain) would be linkable, since they would differ by a predictable point.
  (There are two possible points corresponding to a given nullifier, but this is
  only a trivial obstable to linking them.)
</details>

## Making a claim

For each note that the holder wants to claim, they prove an instance of the
circuit below, and provide this proof together with a spend authorization
signature (constructed as though they were spending the note).

> It is easy to add up value commitments and then open them if desired, or use them in another zk proof.

> Can we make it more efficient to claim that you hold multiple notes?

## Circuit

A valid instance of a Claim statement, $\pi$, assures that given a primary input:
* $\mathsf{cv} ⦂ \mathsf{ValueCommit^{Orchard}.Output}$
* $\mathsf{dom} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$
* $\mathsf{nf_{dom}} ⦂ \{0 .. q_{\mathbb{P}}-1 \}$
* $\mathsf{rk} ⦂ \mathsf{SpendAuthSig^{Orchard}.Public}$

the prover knows an auxiliary input:

* $\mathsf{path} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}^{[\mathsf{MerkleDepth^{Orchard}}]}$
* $\mathsf{pos} ⦂ \{ 0 .. 2^{\mathsf{MerkleDepth^{Orchard}}}\!-1 \}$
* $\mathsf{g_d^{old}} ⦂ \mathbb{P}^*$
* $\mathsf{pk_d^{old}} ⦂ \mathbb{P}^*$
* $\mathsf{v^{old}} ⦂ \{ 0 .. 2^{\ell_{\mathsf{value}}}-1 \}$
* $\text{ρ}^{\mathsf{old}} ⦂ \mathbb{F}_{q_{\mathbb{P}}}$
* $\text{φ}^{\mathsf{old}} ⦂ \mathbb{F}_{q_{\mathbb{P}}}$
* $\mathsf{rcm^{old}} ⦂ \{ 0 .. 2^{\ell^{\mathsf{Orchard}}_{\mathsf{scalar}}}-1 \}$
* $\mathsf{cm^{old}} ⦂ \mathbb{P}$
* $\mathsf{nf^{old}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}$
* $\alpha ⦂ \{ 0 .. 2^{\ell^{\mathsf{Orchard}}_{\mathsf{scalar}}}-1 \}$
* $\mathsf{ak}^{\mathbb{P}} ⦂ \mathbb{P}^*$
* $\mathsf{nk} ⦂ \mathbb{F}_{q_{\mathbb{P}}}$
* $\mathsf{rivk} ⦂ \mathsf{Commit^{ivk}.Trapdoor}$
* $\mathsf{rcv} ⦂ \{ 0 .. 2^{\ell^{\mathsf{Orchard}}_{\mathsf{scalar}}}-1 \}$
* $\mathsf{path^{excl}} ⦂ \{ 0 .. q_{\mathbb{P}}-1 \}^{[\mathsf{MerkleDepth^{excl}}]}$
* $\mathsf{pos^{excl}} ⦂ \{ 0 .. 2^{\mathsf{MerkleDepth^{excl}}}\!-1 \}$
* $\mathsf{start} ⦂ \{ 0 .. 2^{\mathsf{MerkleDepth^{Orchard}}}\!-1 \}$
* $\mathsf{end} ⦂ \{ 0 .. 2^{\mathsf{MerkleDepth^{Orchard}}}\!-1 \}$

such that the following conditions hold:

**Note commitment integrity** $\hspace{0.5em} \mathsf{NoteCommit^{Orchard}_{rcm^{old}}}(\mathsf{repr}_{\mathbb{P}}(\mathsf{g_d^{old}}), \mathsf{repr}_{\mathbb{P}}(\mathsf{pk_d^{old}}), \mathsf{v^{old}}, \text{ρ}^{\mathsf{old}}, \text{φ}^{\mathsf{old}}) \in \{ \mathsf{cm^{old}}, \bot \}$.

**Merkle path validity for** $\mathsf{cm^{old}} \hspace{0.5em} (\mathsf{path^{cm}}, \mathsf{pos^{cm}})$ is a valid Merkle path of depth $\mathsf{MerkleDepth^{Orchard}}$, as defined in § 4.9 'Merkle Path Validity', from $\mathsf{cm^{old}}$ to the anchor $\mathsf{rt^{cm}}$.

**Value commitment integrity** $\hspace{0.5em} \mathsf{cv} = \mathsf{ValueCommit^{Orchard}_{rcv}}(\mathsf{v^{old}})$.

**Nullifier integrity** $\hspace{0.5em} \mathsf{nf^{old}} = \mathsf{DeriveNullifier_{nk}}(\text{ρ}^{\mathsf{old}}, \text{φ}^{\mathsf{old}}, \mathsf{cm^{old}})$.

**Spend authority** $\hspace{0.5em} \mathsf{rk} = \mathsf{SpendAuthSig^{Orchard}.RandomizePublic}(\alpha, \mathsf{ak}^{\mathbb{P}})$.

**Diversified address integrity** $\hspace{0.5em} \mathsf{ivk} = \bot$ or $\mathsf{pk_d^{old}} = [\mathsf{ivk}]\, \mathsf{g_d^{old}}$ where $\mathsf{ivk} = \mathsf{Commit^{ivk}_{rivk}}(\mathsf{Extract}_{\mathbb{P}}(\mathsf{ak}^{\mathbb{P}}), \mathsf{nk})$.

**Merkle path validity for** $(\mathsf{start}, \mathsf{end}) \hspace{0.5em} (\mathsf{path^{excl}}, \mathsf{pos^{excl}})$ is a valid Merkle path of depth $\mathsf{MerkleDepth^{excl}}$, as defined in § 4.9 'Merkle Path Validity', from $\mathsf{excl}$ to the anchor $\mathsf{rt^{excl}}$, where $\mathsf{excl} = \mathsf{MerkleCRH^{Orchard}}(\mathsf{MerkleDepth^{excl}}, \mathsf{start}, \mathsf{end})$.

**Nullifier in excluded range** $\hspace{0.5em} \mathsf{start} \leq \mathsf{nf^{old}} \leq \mathsf{end}$.

**Alternate nullifier integrity** $\hspace{0.5em} \mathsf{nf_{dom}} = \mathsf{DeriveAlternateNullifier_{nk}}(\text{ρ}^{\mathsf{old}}, \text{φ}^{\mathsf{old}}, \mathsf{cm^{old}}, \mathsf{dom})$.

## Circuit implementation

All of these but the last three checks are identical to the corresponding parts
of an Action statement.

**Merkle path validity for** $(\mathsf{start}, \mathsf{end})$ is almost identical
to the other Merkle path validity check.

Alternate nullifier integrity is probably very similar to **Nullifier integrity**.

**Nullifier in excluded range** is fairly straightforward. Nullifiers are
arbitrary field elements so be careful of overflow. Since we can check outside
the circuit that $\mathsf{start} \leq \mathsf{end}$, the check becomes
equivalent to $0 \leq \mathsf{nf^{old}} - \mathsf{start} \leq \mathsf{end} - \mathsf{start}$.

## Rationale

> TODO


# References

[#BCP14]: Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>
[#protocol] Zcash Protocol Specification, Version 2023.4.0 or later <protocol/protocol.pdf>
