::

  ZIP: XXX
  Title: Multipart Memos
  Owners: Jack Grigg <jack@electriccoin.co>
  Status: Draft
  Category: Standards
  Created: 2019-06-27
  License: MIT


Terminology
===========

The key words "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be
interpreted as described in RFC 2119. [#RFC2119]_


Abstract
========

This proposal defines a mechanism for encoding memos to recipients that are larger than a
single encrypted memo field.


Motivation
==========

Shielded outputs within transactions contain an encrypted 512-byte memo field, decryptable
only by the recipient that the output is for. This is sufficient for many use cases, such
as disclosing information about the sender to the recipient. However, there are potential
use cases that may require more than 512 bytes of data to be transferred alongside the
transaction payment to the recipient.

It is possible to send multiple outputs to the same recipient address within a single
transaction, and it is also possible for some or all of these outputs to have zero value
(dummy outputs). This can be leveraged to convey more information to the recipient than
fits in a single memo field. Transaction builders generally randomise the order of
shielded outputs for indistinguishability reasons, and so it would be helpful to have an
unambiguous mechanism to establish a canonical ordering across memos sent to a particular
recipient.


Specification
=============

We reserve the ZIP 302 [#zip-0302]_ type byte 0x20 for indicating a multipart memo.

A multipart memo is treated for the purpose of this ZIP as an opaque data blob of length
at most 65536 bytes. It has an associated type that defines the internal encoding. We
define type 0x00 to indicate human-readable text, which should be encoded as UTF-8 with no
trailing zero bytes, and decoded replacing any incorrect UTF-8-encoded byte sequences with
the replacement character U+FFFD. Specifications of other possible encodings are left for
future ZIPs.

A transaction MUST NOT contain more than one multipart memo per recipient address.

Encoding of ``MultipartHeader``
-------------------------------

- 0xF5 (ZIP 302 [#zip-0302]_ format byte)
- 0x20 (Multipart Memo type byte)
- Length of data (1-2 bytes, as a 16-bit ULEB)
- data (at most 508 bytes):

  - 0x00
  - Total number of parts, including this header (1 byte)
  - Type (1-9 bytes, as a 64-bit ULEB)
  - Total length of encoded multipart memo (2 bytes, as a 16-bit little-endian integer)
  - Memo part (remaining bytes)

Encoding of ``MultipartChunk``
------------------------------

- 0xF5 (ZIP 302 [#zip-0302]_ format byte)
- 0x20 (Multipart Memo type byte)
- Length of data (1-2 bytes, as a 16-bit ULEB)
- data (2-508 bytes):

  - Memo part number (1 byte)
  - Memo part (1-507 bytes)

Sender processing
-----------------

For each recipient address that has a multipart memo:

- Calculate the length of the ULEB-encoded multipart memo type, ``type_len``.
- Generate a ``MultipartHeader`` containing the first ``504 - type_len`` bytes of the
  encoded multipart memo.
- Add a shielded output to the transaction containing the ``MultipartHeader`` along with
  any payment to the recipient address. If no payment is being sent to the recipient
  address, a dummy (zero-value) shielded output is used.
- Split the remaining encoded multipart memo into 507-byte chunks, and assign memo part
  numbers starting from 1.
- For each chunk, add a dummy shielded output to the transaction containing the chunk
  encoded as a ``MultipartChunk``.

Senders SHOULD NOT create transactions with shielded outputs to a recipient address that
contain ``MultipartChunk``-encoded memos, where no shielded output to the same recipient
address containing a ``MultipartHeader`` exists.

Transactions SHOULD NOT contain ``MultipartChunk`` memos in shielded outputs with value.

Transactions MAY contain additional shielded outputs (dummy or real) to a multipart memo
recipient address that use other memo encodings not defined in this ZIP (including no memo
at all).

Recipient processing
--------------------

The recipient trial-decrypts every shielded output of the transaction as usual. For
outputs that are successfully decrypted, the recipient additionally looks for the presence
of a ``MultipartHeader``. If one is found, the recipient scans the other decrypted outputs
for ``MultipartChunk``-encoded memos. Once all memo parts are retrieved, the recipient
concatenates them in ascending part order to obtain the full encoded multipart memo.

Recipients SHOULD reject multipart memos as invalid if any of the following issues are
encountered:

- Missing ``MultipartChunk`` memo part numbers.
- Duplicated ``MultipartChunk`` memo part numbers.
- Any ``MultipartChunk`` in a shielded output with value.
- Total number of ``MultipartChunk``-containing outputs is not consistent with the
  ``MultipartHeader``.
- Total length of the reconstructed multipart memo data does not match the
  ``MultipartHeader``.


Rationale
=========

Having a type inside the multipart memo enables future ZIPs to specify a data format
within the multipart memo, similarly to the base memo field format [#zip-0302]_.

The total length of the encoded multipart memo is specified in the first memo part to make
assembling the full memo simpler and less error-prone, instead of indirectly relying on
the lengths of each part (and being able to successfully decrypt all parts).

The total length of an encoded multipart memo is restricted to 64kiB in order to bound the
privacy leakage associated with generating transactions containing many shielded outputs.
A 64kiB multipart memo would require 130 shielded outputs, whereas the maximum number of
shielded outputs that a transaction could contain while still fitting into a block is
around 2100.


Security and Privacy Considerations
===================================

Transactions that use multipart memos will be larger and have more shielded outputs, which
is observable in the block chain.

Transactions containing invalid multipart memo encodings may pose a privacy threat
depending on how the recipient acts on the transaction. In particular:

- Recipients SHOULD NOT accept any value received alongside a ``MultipartChunk``.
- Recipients MAY accept any value received alongside the ``MultipartHeader`` if the
  overall multipart memo is invalid, but MUST NOT act on any part of the invalid memo.


Reference Implementation
========================

TBD


References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#zip-0302] `ZIP 302: Standardized Memo Field Format <https://github.com/zcash/zips/blob/master/zip-0302.rst>`_
