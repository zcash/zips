    ZIP: Unassigned
    Title: Media Memos Protocol (MMP) Version 1
    Owners: kdenhartog@brave.com
    Status: Draft
    Category: Wallet
    Created: 2024-08-27
    License: MPL 2.0
    Pull-Request: <https://github.com/zcash/zips/pull/899>
# Abstract

This is the first version of the [^zip-tbd1] specification. It’s intended to be a basic implementation that can be used as a first iteration to build off as well as a fallback protocol in the future. As such, there may be certain capabilities or features that are intentionally excluded which can be added in later versions.

# Motivation

In order to define an interoperable version of the specification while allowing for extensibility a base version needs to be defined along with the [^zip-tbd1] specification. This first version is intended to be a simple method to define how messages are encrypted and stored on the [^IPFS] network and then subsequently retrieved by a recipient.

# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY",
"RECOMMENDED", "OPTIONAL", and "REQUIRED" in this document are to
be interpreted as described in BCP 14 [^BCP-14]_ when, and only when,
they appear in all capitals.

# Specification

## Example

Here's a basic example of the MMP URI for the version 1 specification.

`mmp:01:bafybeihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku?ttl=2024-07-02T14:30:00Z#key=Hy9X_k2mLpQrZtNbVc5hA7sDxEuFoP-iQnWyG4M6OjBv`

## Message Location Encoding Scheme

In this version, the intention is to remain focused on storing messages on the [^IPFS] network so that the protocol can operate in a maximally decentralized fashion. In order to accomplish this the message location in the MMP URI MUST be a CID of either version 0 or version 1. Both versions SHOULD be supported. Since CIDv1’s rely on the multicodec specification which includes multiple different encodings via multibase there’s a possibility that a codec is chosen that cannot be decoded. If this is the case, the message MUST be ignored. An implementation MAY return an error to the recipient if they choose. Additionally, for this reason implementers SHOULD use base64url codec by default.

## Message Encryption

In order to properly end-to-end encrypt the media contents and not need to redefine a new encryption process in detail this specification will reuse commonly implemented and defined cryptographic constructions. In this case, since it’s considered out of scope to support multi-messaging capabilities or extremely large file sizes the secretbox construction from libsodium will be sufficient. This makes it easier to implement this functionality safely without requiring re-implementation of the lower level cryptographic functionality which is important for a default fallback protocol.

## Encryption process

The Message Encryption process MUST utilize the secretbox construction from libsodium with the authentication tag attached. The XSalsa20Poly1305 stream cipher MUST be used also. In order to ensure proper usage both the key and nonce MUST not be reused. For this reason it is RECOMMENDED that implementers leverage the `crypto_secretbox_easy` API in libsodium. 

## Decryption process

The Message Decryption process MUST utilize the secretbox construction from libsodium with the authentication tag attached. The XSalsa20Poly1305 stream cipher MUST be used. The recipient MUST use the key provided in the 'key' query parameter to decrypt the message. Implementers are RECOMMENDED to leverage the `crypto_secretbox_open_easy` API in libsodium to ensure proper decryption and verification of the authentication tag. If decryption fails due to an incorrect key or tampering of the authentication tag (or it failing to be included), the implementation MAY return an `0101` ("Unable to Retrieve - decryption error") to the sender and let the user know the message failed to be received. 

## Message Storage

### Message Size

The size of the media content MUST NOT exceed 1GB after encryption in order to prevent excessive decryption times and denial of service attacks for the recipient. Implementations MAY set a lower limit when receiving messages based on the limits of their hardware. If they do, they SHOULD return a “message too large” error code to the sender if they opt to not decrypt the message due to the file size. In order to limit further bloat as well the message MUST NOT be further encoded beyond the bytes output by the secretbox construction.

### Message Availability

Due to the nature of the tradeoffs on the [^IPFS] network there is not a guarantee that content will remain pinned or be replicated by others on the network. Especially since the content is encrypted and therefore unable to be seen by the sender or recipient. For this reason senders SHOULD expect to pin the message on the network for at least 7 days so that the recipient has enough time to retrieve the message. Implementations may opt to use a separate pinning service to extend this time period further. This time period that the sender intends to pin the message MUST be communicated to the recipient via the ttl query parameter. 

### Message Retention

Once the recipient has received the message they SHOULD store it locally as well to avoid loss of the message. Similarly, the sender SHOULD store the message to retain a message sent history. Implementers are generally expected to encrypt their message histories at rest.

## Query Parameters

### Time To Live Query Parameter Usage
Since we’re dealing with a decentralized storage of media in many cases we don’t necessarily have a guarantee that the message will be available when the recipient goes to retrieve the message. As such we need a way for the sender to communicate that a message will be available up to a given point in time and what that time is. While it’s expected that the message will be around at least until the expiration of the TTL there can never be a guarantee that the message will be retrievable even within the time period of the TTL. Therefore this parameter should convey a reasonable time frame that the sender (or a provider of their choosing) is willing to store the message on the [^IPFS] network. Beyond the TTL, the recipient SHOULD NOT expect the message to be stored and the sender MAY delete it. The value of the the query parameter MUST adhere to [RFC-3339].

### ABNF for TTL Query Parameter
```
timestamp = ”ttl=” date-time ; see RFC 3339 for date-time definition
```

## Fragment Parameters

### Encryption Key Fragment Parameter Usage

The encryption key MUST be provided as a query parameter named 'key' in the URL. This key MUST be a 32-byte (256-bit) random value encoded as a Base64url string without padding as defined by [^RFC7515] Appendix C. The key MUST be generated using a cryptographically secure random number generator and unique to each message sent. This includes if the same message is being re-encrypted to re-send the message. The 'key' fragment parameter MUST NOT be included anywhere other than the URI syntax which MUST be sent via the memo attachment field to ensure the key is not leaked.

### ABNF for Encryption Key Fragment Parameter

```
Base64URLCHAR = ALPHA / DIGIT / "-" / "_" / 
encrypt-key-param = "key=" 1*44Base64URLCHAR
```

# Security and Privacy Considerations

This section discusses potential security and privacy issues related to the Version 1 protocol.

## Resource Exhaustion Attacks 
Implementers should be aware of the potential for resource exhaustion attacks. This is best prevented by first checking the size of a message to make sure it conforms with implementation max limits. It’s also a good idea to set user limitations on both the sender and recipient. Additionally, senders should consider unnecessary additional costs that need to be accounted for by setting TTL query parameters at higher thresholds.

## Key Leakage Attacks
The encryption key is a critical component of the protocol's security. Care should be taken to transmit the key securely and avoid logging or caching of the URI which contains the key. If logging is necessary implementers are expected to drop the key query parameter to avoid key leakage. Additionally, care should be taken when sharing MMP URIs to avoid other forms of key leakage.

## IP address and ZCash Address Correlation Attacks
Senders who serve messages directly from a self hosted [^IPFS] node will likely inadvertently expose their IP address to the recipient since it’s highly unlikely any other node on the network will have the encrypted message pinned. To avoid correlation of IP address and ZCash addresses a pinning service or a secure proxy can help protect sender’s privacy. Similarly, recipients who retrieve messages directly from an [^IPFS] node may expose their IP address when retrieving a message. To avoid this recipients can use a gateway or a secure proxy for message retrieval to prevent correlation.

# MMP Version Registry entry

| 1 | [^ZIP-tbd2] | Media Memos Protocol (MMP) Version 1 | 2024-08-27 |

# References

[^ZIP-tbd1]: [ZIP TBD: Media Memos Protocol (MMP)](zip-tbd1.md)
[^RFC-3339]: [Date and Time on the Internet: Timestamps](https://datatracker.ietf.org/doc/html/rfc3339)
[^IPFS]: [IPFS Network](https://ipfs.tech/)
[^RFC-7515]: [JSON Web Signature (JWS)](https://datatracker.ietf.org/doc/html/rfc7515#appendix-C)