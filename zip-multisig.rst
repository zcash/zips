  ZIP: XXX
  Title: Multisig and threshold-sig shielded transactions 
  Authors: Omer Shlomovits <omer@kzencorp.com>
  Credits: Ariel Nof <nofdinar@gmail.com>
  Category: Informational 
  Created: 2019-03-31
  License: MIT


 Terminology
===========

 The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119.

 Abstract
========

`SpendAuthSig` is a Schnorr based signature used in Sapling to sign transactions.
In this ZIP we describe an efficient protocol for threshold signing. The protocol can be used
to protect private signing keys by distributing them among several parties, who upon request
can run the threshold protocol to generate a signature. The transaction will remain shielded but privacy will not hold between co-signers.  

 Motivation
==========

Support for multisig transactions will level up the security available to Zcash users, and broaden the types of users who can safely take advantage of Zcash’s robust privacy while mitigating other threats to their funds.

 Specification
==========

here is a non-formal description of a 2-party multisig: 

**2p-KeyGen**
1) Each party `P_i` chooses a random `ask_i` and computes `ak_i = ask_i *  G` (`G` is Jubjub ec generator)
2) The parties run a secure variant of ECDH to exchange `ak_i` and prove knowledge of `ask_i`
3) The parties set `ak = ak_1 + ak_2` as the SpendAuthSig public-key

**2p-Signing**
1) The parties run a coin-toss protocol to get random `alpha`
2) Each party locally computes `vk = ak + alpha * G`
3) Each party computes a pseudo-random function F with random key `T_i` and input `vk||m` for message `m`. We call the result  `r_i`
4) Each party computes `R_i = r_i *  G` 
5) The parties run the ECDH variant and define `R = R_1 + R_2`
6) Party `P_1` locally computes `S_1 = r_1 + H(R||vk||m) * (ask_1 + alpha)` and sends it to `P_2`
7) Party `P_2` locally computes `S_2 = r_2 + H(R||vk||m) * ask_2` and sends it to `P_1`
8) The parties set `S = S_1 + S_2` and each checks that `verify(m,(R,S)) =1`. If the equality holds, than it outputs `(S,R)`
