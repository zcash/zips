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
In this ZIP We describe an efficient protocol for threshold signing. The protocol can be used
to protect private signing keys by distributing them among several parties, who upon request
can run the threshold protocol to generate a signature. The transaction will remain shielded but privacy will not hold between co-signers.  

 Motivation
==========

Support for multisig transactions will level up the security available to Zcash users, and broaden the types of users who can safely take advantage of Zcash’s robust privacy while mitigating other threats to their funds.