    ZIP: Unassigned
    Title: Media Memos Protocol (MMP)
    Owners: Kyle Den Hartog <kdenhartog@brave.com>
    Status: Draft
    Category: Wallet
    Created: 2024-08-27
    License: MPL 2.0
    Pull-Request: <https://github.com/zcash/zips/pull/899>


# Abstract

In this specification we’ll define how to include an on-chain pointer to a off-chain rich media message which is larger than 512 UTF-8 characters while maintaining the confidentiality guarantees of the memos defined in [^ZIP-302].

# Motivation

Today it's not possible to send a message larger than 512 UTF-8 characters in a memo. In this ZIP we'll define how this can be done while still maintaining confidentiality between the two communicating parties so that larger messages can be sent and received without needing to store all data on chain. This will allow for use cases like including a PDF invoice with a transaction or sending large personalized messages or videos directly to a ZCash address.

# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY",
"RECOMMENDED", "OPTIONAL", and "REQUIRED" in this document are to
be interpreted as described in BCP 14 [^BCP-14]_ when, and only when,
they appear in all capitals.

Definitions of commonly used terms used throughout this ZIP:
 - Scheme - This is the scheme of the URI necessary to identify that this is a MMP message. It SHALL match the definition of a scheme as defined in [^RFC-3986] section 3.1.
 - Version - This is the version of the Media Memo Protocol in use in order to support extensions of the protocol.
 - Message Location - A URL (or derived URL as defined by a separate version spec) which can be used to locate the ciphertext of the message.
 - Query Parameters - This is an extensible model for including additional query parameters directly within the MMP message URI. It SHALL match the definition of a query as defined by [^RFC-3986] section 3.4.

# Requirements

This spec should allow ZCash users to include rich media messages in their transactions through the use of memos as defined in RFC-302. Additionally, in order to maintain cryptographic agility and account for different means of sending messages, it should be extensible by design while still maintaining interoperability.

# Specification

## Message URI syntax

The current memo zip requires that the content of the message is less than 512 ASCII characters which is a sufficient size to include a URI which includes the sufficient details to locate and decrypt the message. Here is how the format of the pointer will be:

## ABNF definition of message URI syntax
    mmp-uri                     = mmp ":" version ":" cid query-params
    mmp-uri                     = /1*512VCHAR; Limit to 512 ASCII VCHARs
    scheme                      = "mmp"
    version                       = 1*2DIGIT
    message-location      = 1*256VCHAR
    query-params            = "?" encrypt-key-param "&" param *("&" param)
    param                        = param-name "=" param-value
    param-name              = 1*ALPHA
    param-value              = 1*VCHAR

## Example of message URI

mmp:v1:bafybeihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku?ttl=2024-07-02T14:30:00Z&key=Hy9X_k2mLpQrZtNbVc5hA7sDxEuFoP-iQnWyG4M6OjBv

## Protocol Versioning

Since the version number determines the various associated properties of the protocol (including cryptographic properties to support cryptographic agility) there can be a wide range of capabilities that MAY NOT be interoperable. As such, all valid implementations of this protocol MUST implement at least version 1 to ensure a fallback for messaging. 

## Message Location

This message location is a URL which can be used to locate a message. It’s used to locate the encrypted ciphertext of the media which is stored at the URL location. It MUST be defined by each protocol version specification. For example in V1, this will be defined as a CID that can be used to get the message from IPFS, but in future iterations it could be a URL that points to a S3 bucket, Torrent file, or elsewhere. It MAY contain additional details about how a path as defined by [^RFC-3986] can be used if a version wants to support this. If the URL contains additional information such as a different scheme (e.g. `https://`) it MUST be defined how it’s encoded within the protocol versioning specification since this URI 

## Query Parameters

All query parameters are optional and MAY be included. Any required query parameters MUST be defined by the version specification. The exception here is the key parameter which are defined in this document because of its expected ubiquitous use across versions.

### Encryption Key Query Parameter
In all versions of the Media Memo Protocol that require passing a secret key between sender and recipients the key parameter MUST be used to. The key parameter MUST be the first query parameter if used so it should follow directly after a ? symbol. Reuse of this query parameter for many protocols will ensure the greatest possible interoperability.

### ABNF for Encryption Key Query Parameter
    encrypt-key-param = "key=" 1*64VCHAR
    Protocol flow

To respond to the message, it's as simple as sending a new message. There isn't a concept of threading built within the protocol itself. Although this could be handled ad a higher layer if desired. Some basic error handling should be defined as well. In general the message should be assumed to be a “broadcast and forget” model where as long as the message has been published it’s not necessary to maintain threading or further capabilities in the message order. Further complex threading, complex protocol features, and complex error handling should be defined in a new message format spec. However this protocol does support some basic error handling to be able to inform the counterparty that a message wasn’t able to be received for some reason.


## Basic Error Handling

While it is possible to define other methods of version specific error handling here are default error codes which MUST be understood by an implementation. Usage of these rather than protocol specific definitions will allow for more interoperable support. Further error codes can be defined in a protocol version doc in which case a version should be included in the definition. Error Codes defined by a MMP Version Specification MUST NOT override the semantics or values of these error codes.

### Default Error Codes
Here are the following definitions of the default error codes:

- Unsupported Version: `0001`
    - Please resend using version 1. Version 1 is specifically chosen here to avoid needing to go through a negotiation protocol to determine a supported version.
- Unable to Retrieve: `0100`
    - This should include a TTL parameter that the recipient would prefer. If the sender resends the message they MAY opt to use a different TTL value in the follow up response which is advisable in order to avoid resource exhaustion attacks where the recipient sends many errors to try and get the sender to re-encrypt and re-pin the same message multiple times. Therefore, the included TTL parameter in this error code is just a recommended time.
- Unable to Retrieve - decryption error: `0101`
    - This error code `0101` MAY be returned when the recipient attempts to decrypt a message but the decryption process fails. This typically occurs in two scenarios:
        - The provided decryption key is incorrect.
        - The message has been tampered with, causing the authentication check to fail.
- Unable to Retrieve - content unavailable: `0102`
    - The recipient attempted to retrieve the encrypted message and was unable to. This may mean that the recipient was unable to parse or retrieve the message via the URL. This may mean that the message wasn’t still pinned or that they received a 404 on pickup for example. Additionally, it may mean that the protocol necessary to pick the message up may not be supported. For example, if the URL provided is .onion TLD and TOR protocol isn’t supported then the recipient would not be able to retrieve the message.

# Security and Privacy Considerations

## Encryption Key Message Security

This still requires further review, but in general we should be able to extend the confidentiality guarantees of the memo field in order to securely send a symmetric key without the need for a key agreement protocol as well. This section should be updated further before finalization with greater detail about this.

## Protocol Version Specifications

Since the cryptographic and protocol security will be defined within separate protocol specification documents, these MUST include further security and privacy consideration sections which highlight specific tradeoffs that have been made. It’s generally expected that these sections will follow the guidelines of [^ZIP-0000] which suggests the usage of [^RFC-3552] and [^RFC-6973] as a starting point.

# Protocol Versions Registry

In order to support additional protocol versions and make it easy to find the documentation of a protocol version for implementers we’ll establish a first come first serve registration process. The version number MUST be the next integer available in the registry table. Minor or patch versions won't be used. The requirements to register a new version are the following:

1. It MUST be published as a ZIP and have reached “Final” Status.
2. Once the ZIP has been finalized a version identifier can be gotten by registering it with a table entry. The table entry should include the ZIP number defining the version, the ZIP’s title, the next version number, and the date of registration.
3. Once this is done the version number MUST NOT be changed or reused

## Registry Table
| MMP Version | ZIP Number | Title | Registration Date  |
| --- | --- | --- | --- |
| 1 | [^ZIP-tbd2] | Media Memos Protocol (MMP) Version 1 | 2024-08-27 |
| ... | ... | ... | ... |

# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)
[^ZIP-0302]: [ZIP 302: Standardized Memo Field Format](zip-0302.rst)
[^RFC-3986]: [Uniform Resource Identifier (URI): Generic Syntax](https://datatracker.ietf.org/doc/html/rfc3986)
[^ZIP-0000]: [ZIP 0: ZIP Process](zip-0000.rst)
[^RFC-3552]: [Guidelines for Writing RFC Text on Security Considerations](https://datatracker.ietf.org/doc/html/rfc3552)
[^RFC-6973]: [Privacy Considerations for Internet Protocols](https://datatracker.ietf.org/doc/html/rfc6973)
[^ZIP-tbd2]: [ZIP TBD2: Media Memos Protocol (MMP) Version 1](zip-tbd2.md)