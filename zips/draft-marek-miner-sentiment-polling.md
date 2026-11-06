    ZIP: Unassigned
    Title: Miner Sentiment Polling
    Owners: Marek <marek@zfnd.org>
            Kris Nuttycombe <kris@nutty.land>
    Status: Draft
    Category: Process / Ecosystem
    Created: 2026-10-27
    License: MIT


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in § 3.12
‘Mainnet and Testnet’. [^protocol-networks]

The terms "best valid block chain" and "block height" are to be interpreted as
described in § 3.3 ‘The Block Chain’ [^protocol-blockchain], and the term "coinbase
transaction" as described in § 3.11 ‘Coinbase Transactions’.
[^protocol-coinbasetransactions]

The term "network upgrade" is to be interpreted as described in ZIP 200.
[^zip-0200]

The terms "coinbase bundle", "`nMinerSignals`", "`vMinerSignals`",
"`signalCode`", "`levelOfSupport`", and "`pollDigest`" are to be interpreted as
described in ZIP 248. [^zip-0248-coinbase]

The term "Zcash Community Advisory Panel" (or "ZCAP") is to be interpreted as
described in ZIP 1015. [^zip-1015]

The terms below are to be interpreted as follows:

Election
:   A round of sentiment polling on the scope or timing of one or more upcoming
    network upgrades, consisting of a ZCAP Poll and the Miner Poll specified in
    this ZIP.

ZCAP Poll
:   The poll of ZCAP members held for an Election. [^nu7-poll-results]

Miner Poll
:   The poll of miners held for an Election, as specified in this ZIP.

Poll Organizer
:   The ZCAP, as the organizer of the ZCAP Poll of an Election.

Poll Definition
:   The JSON document that specifies a Miner Poll; see [Poll Definitions].

Canonical Encoding
:   The byte sequence obtained from a Poll Definition by the procedure in
    [Canonical Encoding and Poll Digest].

Poll Digest
:   The BLAKE2b-128 hash of the Canonical Encoding of a Poll Definition, which
    identifies the Poll Definition in coinbase transactions.

Option Code
:   An integer from 1 to 255 that identifies one option of one question of a
    Poll Definition.

Level of Support
:   An integer from 0 to 255 that a miner assigns to an option: 0 means that the
    miner does not rate the option, 1 means maximal opposition, 128 means
    neutrality, and 255 means maximal support.

Miner Ballot
:   The Poll Digest and the list of (Option Code, Level of Support) pairs
    carried by the coinbase bundle of a block; see [Miner Ballots].

Voting Period
:   The inclusive range of block heights in which Miner Ballots for an Election
    are counted, from the Voting Start Height to the Voting End Height.

Participation Threshold
:   The minimum share of the blocks in a Voting Period that rate at least one
    option of a question, for the Miner Poll results on that question to be
    considered representative of miners.


# Abstract

This proposal specifies a process for gauging miners' sentiment on upcoming
network upgrades. For each Election, miners rate the options of the same
questions that the ZCAP answers.

The Poll Organizer publishes a Poll Definition: a JSON document that gives the
questions, an Option Code for each option, and a Voting Period fixed in block
heights. A normalization procedure maps the Poll Definition to a Canonical
Encoding, whose BLAKE2b-128 hash is its Poll Digest. A miner votes by putting
the Poll Digest and a Level of Support for each option it rates into the miner
signalling fields of the coinbase bundle defined in ZIP 248, in each block it
mines within the Voting Period. Each block in the Voting Period is one vote,
and a block without a valid Miner Ballot rates no option, so results are shares
of all blocks in the Voting Period and approximate shares of hashrate. Anyone
can compute them from the block chain and the Poll Definition.

Miner Poll results are published alongside ZCAP Poll results. Miner Ballots are
public and linked to the blocks that carry them. Consensus assigns no meaning to
Miner Ballots; the only consensus dependency is the encoding of the miner
signalling fields in ZIP 248.


# Motivation

The scope of network upgrades is decided with input from polls of the ZCAP,
whose NU7 results ZIP 259 cites. [^zip-0259] Coinholder polls, such as the NU7
coinholder vote [^nu7-poll-questions], are also held, but are not officially
recognized.

Miners are currently not polled, although network upgrades affect them
directly. NU7 changes the block target spacing and the block subsidy per block
[^zip-0218], and removes 60% of transaction fees from circulation [^zip-0235].
An upgrade also activates safely only if miners run node software that
supports it.

Miners already have the ability to put free-form text in coinbase
transactions, but without a common format that text cannot be tallied. This
ZIP proposes that the coinbase bundle defined by ZIP 248 include structured
miner signalling fields, and gives those fields a meaning: it specifies how a
poll is defined and identified, how a miner responds to it, and how responses
are tallied. Asking the questions of the ZCAP Poll makes the
results directly comparable.


# Privacy Implications

Miner Ballots are public by design and linked to the blocks that carry them and
to their coinbase outputs. Coinbase transactions are already linked to the
blocks that contain them, so a Miner Ballot reveals only the miner's ratings.

Unlike a ZCAP Poll, a Miner Poll has no ballot secrecy: the positions of mining
pools and solo miners become public. A mining pool votes with its hashers' work;
individual hashers are not identified, and their preferences are not recorded.


# Requirements

* Miners can respond to exactly the questions of the ZCAP Poll, with exactly its
  options.
* A Miner Ballot identifies, unambiguously and compactly, the exact Poll
  Definition to which it responds.
* Two Poll Definitions that differ only in JSON formatting, member order, or
  Unicode normalization form have the same Poll Digest.
* Miners can express graded support for or opposition to each option, and can
  decline to rate an option.
* Every block counts as a single vote.
* Support for each option is reported relative to all blocks in the Voting
  Period, including blocks without a Miner Ballot.
* The tally is fully determined by the Poll Definition and public block chain
  data.
* The community agrees upon the Voting Period of each Election through public
  review, and the Voting Period is fixed in advance and unambiguous.
* Miner Poll results are comparable with ZCAP Poll results.


# Non-requirements

* Ballot secrecy for miners.
* A binding effect of the results, or activation signalling enforced by
  consensus.
* Separate representation of hashers within a mining pool.
* Miner Polls in blocks whose coinbase transaction does not use the transaction
  format of ZIP 248.


# Specification

For each Election, the Poll Organizer MUST hold a Miner Poll on Mainnet as
specified below.

## Poll Definitions

A Poll Definition is a JSON text [^RFC8259] that conforms to I-JSON [^RFC7493]
and is a single JSON object with the following members:

| Member | Type | Meaning |
|--------|------|---------|
| `version` | integer | The version of this format. MUST be 1. |
| `id` | string | The Election Identifier: 1 to 16 characters, each a lowercase ASCII letter `a` to `z`, an ASCII digit `0` to `9`, or a hyphen `-`. |
| `title` | string | A non-empty, human-readable title for the Miner Poll. |
| `network` | string | `"mainnet"` or `"testnet"`. |
| `zcapPoll` | string | The URL of the announcement of the ZCAP Poll. |
| `votingStartHeight` | integer | The Voting Start Height, from 1 to 499999999. |
| `votingEndHeight` | integer | The Voting End Height, from `votingStartHeight` to 499999999. |
| `participationThresholdBasisPoints` | integer | The Participation Threshold, in hundredths of a percent, from 0 to 10000. |
| `questions` | array | One or more questions, each a JSON object as below. |

Each question is a JSON object with the following members:

| Member | Type | Meaning |
|--------|------|---------|
| `title` | string | The non-empty text of the question. |
| `description` | string | Further explanation of the question; MAY be empty. |
| `options` | array | One or more options, each a JSON object as below. |

Each option is a JSON object with the following members:

| Member | Type | Meaning |
|--------|------|---------|
| `code` | integer | The Option Code of the option, from 1 to 255. |
| `label` | string | The non-empty text of the option. |

In addition:

* Each object MUST have exactly the members listed for it.
* Every number MUST be written as an integer, without a fraction or exponent
  part.
* The Option Codes of all options of all questions MUST be distinct. A Poll
  Definition therefore has at most 255 options in total.

The following JSON Schema [^json-schema] expresses the structural requirements
above. It does not express the requirements that `votingEndHeight` is at least
`votingStartHeight`, that Option Codes are distinct, or that numbers have no
fraction or exponent part.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Miner Sentiment Poll Definition, version 1",
  "type": "object",
  "additionalProperties": false,
  "required": ["version", "id", "title", "network", "zcapPoll",
               "votingStartHeight", "votingEndHeight",
               "participationThresholdBasisPoints", "questions"],
  "properties": {
    "version": { "const": 1 },
    "id": { "type": "string", "pattern": "^[a-z0-9-]{1,16}$" },
    "title": { "type": "string", "minLength": 1 },
    "network": { "enum": ["mainnet", "testnet"] },
    "zcapPoll": { "type": "string", "format": "uri" },
    "votingStartHeight": { "type": "integer", "minimum": 1, "maximum": 499999999 },
    "votingEndHeight": { "type": "integer", "minimum": 1, "maximum": 499999999 },
    "participationThresholdBasisPoints": { "type": "integer", "minimum": 0, "maximum": 10000 },
    "questions": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/question" } }
  },
  "$defs": {
    "question": {
      "type": "object",
      "additionalProperties": false,
      "required": ["title", "description", "options"],
      "properties": {
        "title": { "type": "string", "minLength": 1 },
        "description": { "type": "string" },
        "options": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/option" } }
      }
    },
    "option": {
      "type": "object",
      "additionalProperties": false,
      "required": ["code", "label"],
      "properties": {
        "code": { "type": "integer", "minimum": 1, "maximum": 255 },
        "label": { "type": "string", "minLength": 1 }
      }
    }
  }
}
```

The questions and options MUST be identical in wording, order, and number to
those of the ZCAP Poll. An explicit "Abstain" option of the ZCAP Poll is an
ordinary option.

The Election Identifier MUST NOT equal the Election Identifier of any earlier
Poll Definition on the same network.

## Canonical Encoding and Poll Digest

The Canonical Encoding of a Poll Definition is computed as follows:

1. Parse the Poll Definition as I-JSON. If it is not valid UTF-8, is not valid
   JSON, has an object with two members of the same name, or has a string that
   contains an unpaired surrogate, it is not a valid Poll Definition.
2. Replace each string value by its Normalization Form C (NFC). [^UAX15]
3. Check the result against the requirements of [Poll Definitions]. If it does
   not meet them, it is not a valid Poll Definition.
4. Serialize the result with the JSON Canonicalization Scheme (JCS)
   [^RFC8785], and encode it as UTF-8.

The Poll Digest of a Poll Definition is the 16-byte BLAKE2b-128 hash
[^RFC7693] of its Canonical Encoding, with the 16-byte personalization string
`"Zcash_MinerPoll_"`. When a Poll Digest is written as text, it is written as
32 lowercase hexadecimal digits, in the order of the bytes of the hash output.

Since every member name is an ASCII string and every number is an integer, JCS
reduces to the following for a Poll Definition: members of each object are
sorted by name, no whitespace is emitted outside strings, integers are written
in decimal without leading zeros, and strings are escaped as by ECMAScript's
`JSON.stringify`.

## Publication of Poll Definitions

For each Election, the Poll Organizer MUST publish a Poll Definition and its
Poll Digest on the Zcash Community Forum, in the announcement of the ZCAP Poll
or in a post linked from it. The Poll Organizer SHOULD publish the Poll
Definition as an attached file, so that miners can load it into the tools they
use to prepare Miner Ballots without retyping it.

A published Poll Definition MUST NOT be changed. To change its questions,
options, Voting Period, or Participation Threshold, the Poll Organizer publishes a
new Poll Definition, which has a different Poll Digest, supersedes the earlier
one, and is subject to the requirements in [Voting Period]. A Poll Definition can
only be superseded before the block at its Voting Start Height is mined, and a
superseded Poll Definition is not tallied. Once the Voting Period of a Poll
Definition has started, its Miner Poll MUST be tallied and its results
published, even if a new Poll Definition is published afterward.

The Voting Periods of two Poll Definitions on the same network SHOULD NOT
overlap, since a block carries at most one Poll Digest. Questions that would be
asked in concurrent Miner Polls SHOULD be combined into a single Poll
Definition.

## Voting Period

The Voting Period consists of the block heights from the Voting Start Height to
the Voting End Height inclusive. The Voting Period of each Election is agreed
upon as follows:

1. The Poll Organizer proposes the Voting Period, together with the questions, in
   the announcement of the ZCAP Poll and invites feedback on the forum.
2. The proposed Voting Period SHOULD coincide with the voting window of the ZCAP
   Poll. To convert times to block heights, the Poll Organizer SHOULD use the
   block target spacing in effect, accounting for any network upgrade scheduled
   to activate before the Voting End Height.
3. The whole Voting Period MUST be at or after the activation height of the
   network upgrade that deploys ZIP 248 on the network of the Poll Definition.
4. After considering the feedback, the Poll Organizer publishes the final Poll
   Definition. Its Voting Period MUST have been proposed on the forum, as in
   step 1, at least 7 days earlier, so a Voting Period changed in response to
   feedback is proposed again. With the final Poll Definition, the Poll
   Organizer MUST answer on the forum each objection to the Voting Period raised
   during the feedback period, stating how it was addressed or why it was not.
   The final Poll Definition MUST be published at least 14 days before the
   block at the Voting Start Height is expected to be mined.

## Miner Ballots

A miner casts a Miner Ballot for a Poll Definition $P$ in a block it mines at a
height within the Voting Period of $P$ by setting the miner signalling fields of
the coinbase bundle of that block's coinbase transaction as follows:

* `pollDigest` is the Poll Digest of $P$;
* for each option of $P$ that the miner rates, `vMinerSignals` has one entry
  whose `signalCode` is the Option Code of that option and whose
  `levelOfSupport` is the miner's Level of Support for it.

`vMinerSignals` SHOULD NOT have entries whose `levelOfSupport` is 0; such an
entry has the same effect as no entry. ZIP 248 requires the entries to be in
strictly ascending order of `signalCode`.

A Level of Support $\ell$ from 1 to 255 has the score
$s(\ell) = (\ell - 128) / 127$, which ranges from $-1$ (maximal opposition)
through $0$ (neutrality) to $1$ (maximal support).

A miner SHOULD include its Miner Ballot in every block it mines during the Voting
Period. Since each block counts separately, a miner MAY change its Miner Ballot
during the Voting Period. A mining pool that casts Miner Ballots SHOULD publish
its Miner Ballot to its hashers before the Voting Start Height.

## Preparing a Miner Ballot

Software that prepares Miner Ballots SHOULD:

1. load a Poll Definition from a file, and reject it if it is not a valid Poll
   Definition;
2. compute and display its Poll Digest, so that the miner can compare it with
   the Poll Digest published by the Poll Organizer;
3. display the `network`, the Voting Period, and each question with its
   `description` and options;
4. for each option, let the miner choose a Level of Support from 0 to 255,
   with 0 as the default;
5. include the resulting Miner Ballot only in the coinbase transactions of
   blocks on the network of the Poll Definition, at heights within its Voting
   Period.

This ZIP does not specify how such software stores a miner's ratings, or how it
configures the software that constructs coinbase transactions.

## Determining the Miner Ballot of a Block

For a Poll Definition $P$ and a block $B$ at a height within the Voting Period of
$P$, $B$ has a Miner Ballot for $P$ if and only if:

* the coinbase transaction of $B$ has a coinbase bundle;
* `nMinerSignals` is greater than 0, and `pollDigest` equals the Poll Digest of
  $P$;
* each `signalCode` in `vMinerSignals` is an Option Code of $P$; and
* at least one `levelOfSupport` in `vMinerSignals` is nonzero.

If $B$ has a Miner Ballot for $P$, then $L_{B,o}$, the Level of Support of $B$
for option $o$, is the `levelOfSupport` of the entry whose `signalCode` is the
Option Code of $o$, or 0 if there is no such entry. If $B$ has no Miner Ballot
for $P$, then $L_{B,o} = 0$ for every option $o$.

## Tallying

The tally of a Miner Poll is computed over the best valid block chain of the
network given in its Poll Definition, once that chain contains a block at height
Voting End Height + 99, giving the block at the Voting End Height 100
confirmations.

Each block in the Voting Period counts as a single vote, regardless of who mined
it or the value of its coinbase outputs. A block rates option $o$ if
$L_{B,o} > 0$. A block without a Miner Ballot rates no option.

Let:

* $N$ be the number of blocks in the Voting Period, i.e. Voting End Height −
  Voting Start Height + 1;
* $P$ be the number of blocks in the Voting Period that have a Miner Ballot;
* $h_{o,\ell}$, for $\ell$ from 1 to 255, be the number of blocks $B$ in the
  Voting Period with $L_{B,o} = \ell$;
* $R_o = \sum_{\ell=1}^{255} h_{o,\ell}$ be the number of blocks that rate
  option $o$;
* $T_o = \sum_{\ell=1}^{255} (\ell - 128) \cdot h_{o,\ell}$;
* $A_q$ be the number of blocks that rate at least one option of question $q$.

The net support for option $o$ is $T_o / (127 \cdot N)$, the sum of the scores
of all blocks in the Voting Period for $o$, divided by $N$, where a block that
does not rate $o$ contributes 0. It ranges from $-1$ to $1$. The mean score of
option $o$ among the blocks that rate it is $T_o / (127 \cdot R_o)$, if $R_o > 0$.

The results of the Miner Poll consist of:

* for each option $o$: the counts $h_{o,\ell}$ that are nonzero, $R_o$, $T_o$,
  the percentage $100 \cdot R_o / N$ of blocks that rate it, its net support as
  a percentage from −100% to 100%, and its mean score among the blocks that
  rate it;
* for each question $q$: $A_q$, the percentage $100 \cdot A_q / N$, and whether
  $10000 \cdot A_q / N$ is at least `participationThresholdBasisPoints`;
* $N$, $P$, and the overall participation $100 \cdot P / N$ as a percentage;
* the Poll Digest;
* the height and hash of the block at the Voting End Height in the block chain
  that was tallied.

Net support, and any summary of support or opposition by the Poll Organizer,
MUST be relative to $N$. The counts are authoritative.

The results on question $q$ are representative of miners if and only if
$10000 \cdot A_q / N$ is at least `participationThresholdBasisPoints`.

## Publication of Results

The Poll Organizer MUST publish the Miner Poll results in the same forum thread
as the ZCAP Poll results, no later than 7 days after the block at height
Voting End Height + 99 is mined.

A ZIP that cites an Election's ZCAP Poll results, as ZIP 259 does for NU7
[^zip-0259], SHOULD also cite that Election's Miner Poll results.

This ZIP does not specify what weight Miner Poll results carry relative to ZCAP
Poll results, or how the two are combined. Coinholder polls are outside its
scope.

## Testnet-specific considerations

Miner Polls SHOULD be rehearsed on Testnet before the first Miner Poll on
Mainnet. Miner Polls on Testnet are rehearsals only: they are not the Miner Poll
of any Election and have no significance for Zcash governance.

A Poll Definition on Testnet has `"network": "testnet"` and Testnet block
heights, so its Poll Digest differs from that of any Poll Definition on Mainnet.
A Poll Definition on Testnet that rehearses a Miner Poll on Mainnet SHOULD use
the questions and options of that Mainnet Poll Definition, so that miners
rehearse the same ratings with the same tools. The 7-day and 14-day
requirements in [Voting Period] do not apply on Testnet.

## Example

This subsection is non-normative.

Consider the following hypothetical Poll Definition on Testnet:

```json
{
  "version": 1,
  "id": "nu7-example",
  "title": "NU7 Miner Sentiment (example)",
  "network": "testnet",
  "zcapPoll": "https://forum.zcashcommunity.com/t/nu7-sentiment-polls-results/57590",
  "votingStartHeight": 3700000,
  "votingEndHeight": 3740319,
  "participationThresholdBasisPoints": 2500,
  "questions": [
    {
      "title": "NSM issuance curve",
      "description": "How should the block subsidy be issued after NU7?",
      "options": [
        { "code": 1, "label": "Smooth issuance curve" },
        { "code": 2, "label": "Preserve halvings" },
        { "code": 3, "label": "Do not include issuance smoothing in NU7" }
      ]
    },
    {
      "title": "NSM reissuance",
      "description": "When should burned funds start to be reissued?",
      "options": [
        { "code": 4, "label": "As soon as possible" },
        { "code": 5, "label": "February 2027" },
        { "code": 6, "label": "February 2031" }
      ]
    },
    {
      "title": "v4 transaction disablement",
      "description": "When should v4 transactions stop being accepted?",
      "options": [
        { "code": 7, "label": "Immediately at NU7 activation" },
        { "code": 8, "label": "One year after this poll" },
        { "code": 9, "label": "Do not set a date" }
      ]
    },
    {
      "title": "25-second block target spacing",
      "description": "Should NU7 reduce the block target spacing to 25 seconds?",
      "options": [
        { "code": 10, "label": "Yes" },
        { "code": 11, "label": "No" }
      ]
    }
  ]
}
```

Its Canonical Encoding is the following 1181 bytes (shown here on one line):

```
{"id":"nu7-example","network":"testnet","participationThresholdBasisPoints":2500,"questions":[{"description":"How should the block subsidy be issued after NU7?","options":[{"code":1,"label":"Smooth issuance curve"},{"code":2,"label":"Preserve halvings"},{"code":3,"label":"Do not include issuance smoothing in NU7"}],"title":"NSM issuance curve"},{"description":"When should burned funds start to be reissued?","options":[{"code":4,"label":"As soon as possible"},{"code":5,"label":"February 2027"},{"code":6,"label":"February 2031"}],"title":"NSM reissuance"},{"description":"When should v4 transactions stop being accepted?","options":[{"code":7,"label":"Immediately at NU7 activation"},{"code":8,"label":"One year after this poll"},{"code":9,"label":"Do not set a date"}],"title":"v4 transaction disablement"},{"description":"Should NU7 reduce the block target spacing to 25 seconds?","options":[{"code":10,"label":"Yes"},{"code":11,"label":"No"}],"title":"25-second block target spacing"}],"title":"NU7 Miner Sentiment (example)","version":1,"votingEndHeight":3740319,"votingStartHeight":3700000,"zcapPoll":"https://forum.zcashcommunity.com/t/nu7-sentiment-polls-results/57590"}
```

and its Poll Digest is `441d8c3e7f9727b8157840ae274f7f5b`.

A miner who strongly supports a smooth issuance curve, is neutral on preserving
halvings, strongly opposes leaving issuance smoothing out of NU7, moderately
supports reissuance from February 2027, strongly supports 25-second spacing,
strongly opposes keeping the current spacing, and does not rate the other
options, rates option 1 at 255, option 2 at 128, option 3 at 1, option 5 at 200,
option 10 at 255, and option 11 at 1. The miner signalling fields of its
coinbase bundles are then the 29 bytes

```
06 01ff 0280 0301 05c8 0aff 0b01 441d8c3e7f9727b8157840ae274f7f5b
```

that is, `nMinerSignals` = 6, six (`signalCode`, `levelOfSupport`) pairs, and
the Poll Digest.

The Voting Period has $N = 40320$ blocks. Suppose that 20000 blocks carry the
Miner Ballot above, 10000 blocks carry a Miner Ballot that rates option 1 at 1,
option 3 at 255, option 10 at 1, and option 11 at 255, and the remaining 10320
blocks carry no Miner Ballot. Then:

* Option 1 is rated by $R_1 = 30000$ blocks (74.40%), with
  $T_1 = 20000 \cdot 127 - 10000 \cdot 127 = 1270000$. Its net support is
  $1270000 / (127 \cdot 40320) \approx 24.80\%$, and its mean score among the
  blocks that rate it is $1/3$.
* Option 2 is rated by 20000 blocks (49.60%), all neutral, so its net support
  is 0%.
* Option 5 is rated by 20000 blocks, with $T_5 = 20000 \cdot 72 = 1440000$. Its
  net support is approximately 28.12%, and its mean score among the blocks that
  rate it is $72/127 \approx 0.567$.
* Question 1 is answered by $A_1 = 30000$ blocks (74.40%), and question 2 by
  20000 blocks (49.60%); both are at least the Participation Threshold of 25%.
  No block rates an option of question 3, so its results are not representative
  of miners.

The following table shows how coinbase bundles at heights in the Voting Period
are interpreted for this Poll Definition:

| Miner signalling fields | Result |
|-------------------------|--------|
| `06 01ff 0280 0301 05c8 0aff 0b01 441d…7f5b` | Miner Ballot, as above. |
| `00` | No Miner Ballot: no signals. |
| `01 0cff 441d…7f5b` | No Miner Ballot: 12 is not an Option Code of this Poll Definition. |
| `01 0100 441d…7f5b` | No Miner Ballot: no nonzero Level of Support. |
| `01 01ff` followed by any other Poll Digest | No Miner Ballot for this Poll Definition. |
| `02 0aff 01ff 441d…7f5b` | Cannot occur: signal codes are not in ascending order, so ZIP 248 makes the block invalid. |


# Rationale

## Rationale for counting blocks

The number of blocks mined approximates a miner's share of hashrate, and proof of
work makes Sybil voting pointless, since more Miner Ballots require more work.
Mining pools represent their hashers, who can switch pools if they disagree with
their pool's Miner Ballot.

Blocks are not weighted by coinbase output value or timestamp, which keeps the
tally independent of transaction fees, the block subsidy, and timestamps chosen
by miners. A change to the block target spacing within a Voting Period changes
the number of blocks per unit of time for all miners alike, so counting blocks
still approximates share of hashrate.

Rented hashrate could buy an outcome at the cost of that hashrate, and public
Miner Ballots make bribes verifiable; both are reasons why the results indicate
sentiment and are not binding.

## Rationale for counting blocks without Miner Ballots

Net support is relative to all blocks in the Voting Period, as the version bits
mechanism of BIP 9 counts a block that does not signal against activation.
[^bip-0009] Relative to the blocks that rate an option, 10 blocks from one pool
that rate it at 255 would show maximal support; relative to the Voting Period,
they show a net support of about 0.025% for the Voting Period of the
[Example]. A miner's influence on net
support is thus bounded by its share of the blocks in the Voting Period, however
few other miners vote.

This is possible because the electorate of a Miner Poll, the blocks in the Voting
Period, is fully observable, as the membership of the ZCAP is. The mean score
among the blocks that rate an option, and any other statistic of those blocks,
follows from the published counts $h_{o,\ell}$.

The Participation Threshold flags low turnout. It applies to each question:
since a Miner Ballot can leave options unrated, a heavily answered question
would otherwise make the results on an unanswered question appear
representative. It is given in basis points so that the Poll Definition
contains only integers.

The tally does not group blocks by miner, because coinbase outputs and pool tags
are chosen by miners and do not reliably identify them.

## Rationale for ratings

ZCAP Polls have asked single-choice questions, multiple-choice questions with a
maximum number of selections, and questions that would be better answered by
ranking or scoring. A Level of Support for each option can express all of these:
a single choice is a rating of 255 for one option, and a multiple choice is a
rating of 255 for each selected option. It also lets a miner express opposition,
which a choice cannot, and distinguish neutrality (128) from not rating an
option (0). The results are comparable with those of the ZCAP Poll option by
option, although ratings carry more information than choices.

The miner signalling fields of ZIP 248 encode a Level of Support in one byte.
Reserving 0 for "not rated" leaves 255 levels, which have an exact midpoint at
128, so the score is symmetric about neutrality. No maximum number of selections
is enforced, because ratings are not selections; a Poll Organizer that wants to
compare with a multiple-choice ZCAP question can count, for example, blocks that
rate an option above 128.

## Rationale for coinbase bundle fields

Only the miner of a block controls its coinbase transaction, so proof of work
authenticates the Miner Ballot. The miner signalling fields of ZIP 248 are
structured, so a Miner Ballot is found without searching free-form text, cannot
be confused with a pool tag, and does not take space from `coinbaseData`. A
Miner Ballot for a poll with dozens of options is a few dozen bytes. Consensus
requires only that signal codes be in ascending order, which gives each Miner
Ballot a single encoding.

Three alternatives were rejected:

* An ASCII ballot in the coinbase script or a shielded coinbase memo: it needs
  no consensus change, but a ballot has to be found by searching text that pool
  tags share, its length is limited by the space in the coinbase script, and
  it can express only choices, not graded support.
* Block header version bits: consensus only requires the block version number to
  be at least 4 [^protocol-blockheader], but a bit expresses only yes or no.
* Separate transactions: anyone can create them, and they are not tied to block
  production.

The cost of using the ZIP 248 fields is that Miner Polls are possible only after
the network upgrade that deploys ZIP 248.

## Rationale for the Poll Digest

The Poll Digest binds a Miner Ballot to the exact text of the questions and
options that the miner rated, and to the Voting Period and Participation
Threshold under which they will be tallied. Option Codes therefore need to be
unique only within a Poll Definition, a miner still configured for a superseded
or earlier Poll Definition never contributes to a later one, and a Poll
Definition on Testnet never counts on Mainnet. Sixteen bytes make an accidental
collision negligible; a deliberate collision gains nothing, since the Poll
Organizer publishes the Poll Definition and the Poll Digest together. The
personalization string separates Poll Digests from other BLAKE2b hashes used in
Zcash.

The Canonical Encoding makes the Poll Digest independent of how the Poll
Definition was formatted, so that tools written in different languages compute
the same Poll Digest from the same document. JCS is a published standard with
implementations in many languages. Restricting the document to integers and
ASCII member names avoids the parts of JCS that are hardest to implement:
floating-point serialization and sorting by UTF-16 code units. NFC
normalization makes strings that are canonically equivalent in Unicode, and
therefore display identically, produce the same Poll Digest. Rejecting unknown
members makes every byte of the Canonical Encoding meaningful to the tools that
display the Poll Definition, so a miner can see everything its Miner Ballot
commits to.

## Rationale for leaving tooling unspecified

Interoperability requires only that miners and tallying software agree on the
Poll Definition and on the encoding of a Miner Ballot in the coinbase bundle.
How a miner's ratings reach the software that constructs coinbase transactions
differs between node implementations and mining setups, and needs no common
format.

## Rationale for block-height Voting Periods

Block heights are deterministic, whereas block timestamps are chosen by miners.
Changes to the block target spacing are accounted for when the Voting Period is
chosen. The 7-day feedback period and the public answers to objections make
agreement on the Voting Period reviewable. As for the questions of the ZCAP Poll,
that agreement is reached through public review; this ZIP does not define a
separate vote on the Voting Period. The 14-day notice period gives mining pools
time to reconfigure.


# Deployment

Miner Polls depend on the miner signalling fields of the coinbase bundle
defined in ZIP 248, and can be held only in blocks after the activation of the
network upgrade that deploys ZIP 248.


# Reference implementation

None yet. A reference implementation is needed of:

* software that prepares a Miner Ballot from a Poll Definition and includes it
  in coinbase transactions;
* tallying.


# Open issues

* Whether one poll per block is sufficient, or whether ZIP 248 should allow a
  coinbase bundle to carry signals for more than one Poll Digest.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3] or later](protocol/protocol.pdf)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^protocol-coinbasetransactions]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.11: Coinbase Transactions](protocol/protocol.pdf#coinbasetransactions)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-blockheader]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.6: Block Header Encoding and Consensus](protocol/protocol.pdf#blockheader)

[^bip-0009]: [BIP 9: Version bits with timeout and delay](https://github.com/bitcoin/bips/blob/master/bip-0009.mediawiki)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](zip-0218.md)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235.md)

[^zip-0248-coinbase]: [ZIP 248: Extensible Transaction Format — Coinbase Bundle](zip-0248.rst#coinbase-bundle)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^nu7-poll-questions]: [NU7 Coinholder Vote: poll questions and scope](https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912)

[^nu7-poll-results]: [NU7 Sentiment Polls Results](https://forum.zcashcommunity.com/t/nu7-sentiment-polls-results/57590)

[^RFC7493]: [RFC 7493: The I-JSON Message Format](https://www.rfc-editor.org/rfc/rfc7493.html)

[^RFC7693]: [RFC 7693: The BLAKE2 Cryptographic Hash and Message Authentication Code (MAC)](https://www.rfc-editor.org/rfc/rfc7693.html)

[^RFC8259]: [RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259.html)

[^RFC8785]: [RFC 8785: JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785.html)

[^UAX15]: [Unicode Standard Annex #15: Unicode Normalization Forms](https://www.unicode.org/reports/tr15/)

[^json-schema]: [JSON Schema: A Media Type for Describing JSON Documents, Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core)
