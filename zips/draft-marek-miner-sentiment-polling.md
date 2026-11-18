    ZIP: Unassigned
    Title: Miner Sentiment Polling
    Owners: Marek <marek@zfnd.org>
            Kris Nuttycombe <kris@nutty.land>
    Status: Draft
    Category: Standards / Ecosystem
    Created: 2026-10-27
    License: MIT


# Terminology

The key words "MUST", "SHOULD", "SHOULD NOT", "RECOMMENDED", and "MAY" in this
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

The terms below are to be interpreted as follows:

Miner Poll
:   A poll of miners conducted as specified in this ZIP.

Ecosystem Poll
:   A poll of some part of the Zcash community, other than miners, on a
    question such as the scope or timing of a network upgrade.

Poll Coordinator
:   The party that constructs and publishes the Poll Definition of a Miner Poll.

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
:   An integer from 0 to 255 that a miner assigns to an option that it rates. A
    greater Level of Support means greater support, and 0 means no support. A
    miner that does not rate an option abstains on it.

Miner Ballot
:   The Poll Digest and the list of (Option Code, Level of Support) pairs
    carried by the coinbase bundle of a block; see [Miner Ballots].

Voting Period
:   The range of block heights in which Miner Ballots for a Poll Definition
    are counted: from the Voting Start Height, inclusive, to the Voting End
    Height, exclusive.


# Abstract

This proposal specifies a mechanism for polling miners. A Poll Definition is a
JSON document that gives a set of questions, an Option Code for each option, a
Voting Period fixed in block heights, and the method by which the responses to
each question are to be interpreted. A canonicalization procedure maps the Poll
Definition to a Canonical Encoding, whose BLAKE2b-128 hash is its Poll Digest.

A miner votes by putting the Poll Digest and a Level of Support for each option
it rates into the miner signalling fields of the coinbase bundle defined in ZIP
248, in each block it mines within the Voting Period. Each block in the Voting
Period is one ballot. Anyone can compute the result from the block chain and
the Poll Definition.

This ZIP does not specify who holds Miner Polls or what weight their results
carry. It gives recommendations for a party that coordinates an Ecosystem Poll
and wants to poll miners on the same questions alongside it.


# Motivation

The scope of network upgrades is decided with input from polls of parts of the
Zcash community; for example, ZIP 259 cites the results of polls held for NU7.
[^zip-0259] [^nu7-poll-results] Miners are currently not polled, although
network upgrades affect them directly. NU7 changes the block target spacing and
the block subsidy per block [^zip-0218], and removes 60% of transaction fees
from circulation [^zip-0235]. An upgrade also activates safely only if miners
run node software that supports it.

Miners already have the ability to put free-form text in coinbase
transactions, but without a common format that text cannot be tallied. There
is no agreed way to identify the poll to which a miner responds, to encode the
miner's response, or to interpret the responses. Unless the method of
interpretation is fixed before miners respond, it can be chosen after their
responses are known.


# Privacy Implications

Miner Ballots are public by design and linked to the blocks that carry them and
to their coinbase outputs. Coinbase transactions are already linked to the
blocks that contain them, so a Miner Ballot reveals only the miner's ratings.

A Miner Poll has no ballot secrecy: the positions of mining pools and solo
miners become public. A mining pool votes with its hashers' work; individual
hashers are not identified, and their preferences are not recorded.


# Requirements

* A Miner Ballot identifies, unambiguously and compactly, the exact Poll
  Definition to which it responds.
* Two Poll Definitions that differ only in JSON formatting or member order
  have the same Poll Digest.
* Tools that implement different versions of the Unicode Standard compute the
  same Poll Digest for the same Poll Definition.
* The Poll Definition commits to how the responses to each question are
  interpreted.
* Miners can express graded support for each option, including no support, and
  can abstain on an option or on a whole question. A result distinguishes no
  support from abstention.
* Every block counts as a single ballot.
* The result is fully determined by the Poll Definition and public block chain
  data.
* A Miner Poll can ask the same questions, with the same options, as an
  Ecosystem Poll.


# Non-requirements

* Specifying who holds Miner Polls, when they are held, or what weight their
  results carry.
* Ballot secrecy for miners.
* A binding effect of the results, or activation signalling enforced by
  consensus.
* Separate representation of hashers within a mining pool.
* Miner Polls in blocks whose coinbase transaction does not use the transaction
  format of ZIP 248.


# Specification

## Poll Definitions

A Poll Definition is a JSON text [^RFC8259] that conforms to I-JSON [^RFC7493]
and is a single JSON object with the following members:

| Member | Type | Meaning |
|--------|------|---------|
| `version` | integer | The version of this format. MUST be 1. |
| `title` | string | A non-empty, human-readable title for the Miner Poll. |
| `url` | string | The URL of a public announcement of the Miner Poll. |
| `votingStartHeight` | integer | The Voting Start Height, which is the height of the first block of the Voting Period, from 1 to 499999999. |
| `votingEndHeight` | integer | The Voting End Height, which is one more than the height of the last block of the Voting Period. It MUST be greater than `votingStartHeight` and at most 500000000. |
| `questions` | array | One or more questions, each a JSON object as below. |

Each question is a JSON object with the following members:

| Member | Type | Meaning |
|--------|------|---------|
| `title` | string | The non-empty text of the question. |
| `description` | string | Further explanation of the question; MAY be empty. |
| `tally` | object | The method of interpretation of the question, as below. |
| `options` | array | Two or more options, each a JSON object as below. |

The `tally` object of a question has the following members:

| Member | Type | Meaning |
|--------|------|---------|
| `method` | string | MUST be `"star"`; see [Interpretation of Results]. |
| `winners` | integer | The number of options to be chosen, from 1 to one less than the number of options of the question. |

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
above. It does not express the requirements that `votingEndHeight` is greater
than `votingStartHeight`, that `winners` is less than the number of options,
that Option Codes are distinct, or that numbers have no fraction or exponent
part.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Miner Sentiment Poll Definition, version 1",
  "type": "object",
  "additionalProperties": false,
  "required": ["version", "title", "url",
               "votingStartHeight", "votingEndHeight", "questions"],
  "properties": {
    "version": { "const": 1 },
    "title": { "type": "string", "minLength": 1 },
    "url": { "type": "string", "format": "uri" },
    "votingStartHeight": { "type": "integer", "minimum": 1, "maximum": 499999999 },
    "votingEndHeight": { "type": "integer", "minimum": 2, "maximum": 500000000 },
    "questions": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/question" } }
  },
  "$defs": {
    "question": {
      "type": "object",
      "additionalProperties": false,
      "required": ["title", "description", "tally", "options"],
      "properties": {
        "title": { "type": "string", "minLength": 1 },
        "description": { "type": "string" },
        "tally": { "$ref": "#/$defs/tally" },
        "options": { "type": "array", "minItems": 2, "items": { "$ref": "#/$defs/option" } }
      }
    },
    "tally": {
      "type": "object",
      "additionalProperties": false,
      "required": ["method", "winners"],
      "properties": {
        "method": { "const": "star" },
        "winners": { "type": "integer", "minimum": 1, "maximum": 254 }
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

## Canonical Encoding and Poll Digest

The Canonical Encoding of a Poll Definition is computed as follows:

1. Parse the Poll Definition as I-JSON. If it is not valid UTF-8, is not valid
   JSON, has an object with two members of the same name, or has a string that
   contains an unpaired surrogate, it is not a valid Poll Definition.
2. Check the result against the requirements of [Poll Definitions]. If it does
   not meet them, it is not a valid Poll Definition.
3. Serialize the result with the JSON Canonicalization Scheme (JCS)
   [^RFC8785], and encode it as UTF-8.

Each string is serialized with the sequence of Unicode code points that it has
in the Poll Definition. As JCS requires, no Unicode normalization is applied to
it.

The Poll Digest of a Poll Definition is the 16-byte BLAKE2b-128 hash
[^RFC7693] of its Canonical Encoding, with the 16-byte personalization string
`"Zcash_MinerPoll_"`. When a Poll Digest is written as text, it is written as
32 lowercase hexadecimal digits, in the order of the bytes of the hash output.

Since every member name is an ASCII string and every number is an integer, JCS
reduces to the following for a Poll Definition: members of each object are
sorted by name, no whitespace is emitted outside strings, integers are written
in decimal without leading zeros, and strings are escaped as by ECMAScript's
`JSON.stringify`.

Any change to a Poll Definition other than its whitespace, the order of the
members of its objects, or the way its strings are escaped changes its Poll
Digest. A Miner Ballot therefore commits to the questions, options, Voting
Period, and method of interpretation of the Poll Definition to which it
responds.

## Miner Ballots

A miner casts a Miner Ballot for a Poll Definition $P$ in a block it mines at a
height within the Voting Period of $P$ by setting the miner signalling fields of
the coinbase bundle of that block's coinbase transaction as follows:

* `pollDigest` is the Poll Digest of $P$;
* for each option of $P$ that the miner rates, `vMinerSignals` has one entry
  whose `signalCode` is the Option Code of that option and whose
  `levelOfSupport` is the miner's Level of Support for it.

An entry whose `levelOfSupport` is 0 records that the miner does not support
the option. A miner abstains on an option by including no entry for it, and
abstains on a question by including no entry for any of its options. ZIP 248
requires the entries to be in strictly ascending order of `signalCode`, so
`vMinerSignals` has at most one entry for each option. ZIP 248 also omits
`pollDigest` when `vMinerSignals` is empty, so a miner that rates no option of
$P$ casts no Miner Ballot for $P$.

Since each block counts separately, a miner MAY change its Miner Ballot during
the Voting Period. A miner that wants its Miner Ballot to count in proportion to
its hashrate SHOULD include it in every block it mines during the Voting
Period. A mining pool that casts Miner Ballots SHOULD publish its Miner Ballot
to its hashers before the Voting Start Height.

## Preparing a Miner Ballot

Software that prepares Miner Ballots SHOULD:

1. load a Poll Definition from a file, and reject it if it is not a valid Poll
   Definition;
2. compute and display its Poll Digest, so that the miner can compare it with
   the Poll Digest published by the Poll Coordinator;
3. display the Voting Period, and each question with its `description`, its
   options, and its method of interpretation, including its number of winners;
4. for each option, let the miner either choose a Level of Support from 0 to
   255 or leave the option unrated, with unrated as the default;
5. include the resulting Miner Ballot only in the coinbase transactions of
   blocks at heights within the Voting Period.

This ZIP does not specify how such software stores a miner's ratings, or how it
configures the software that constructs coinbase transactions.

## Determining the Miner Ballot of a Block

For a Poll Definition $P$ and a block $B$ at a height within the Voting Period of
$P$, $B$ has a Miner Ballot for $P$ if and only if:

* the coinbase transaction of $B$ has a coinbase bundle;
* `nMinerSignals` is greater than 0, and `pollDigest` equals the Poll Digest of
  $P$; and
* each `signalCode` in `vMinerSignals` is an Option Code of $P$.

The values of `levelOfSupport` do not affect whether $B$ has a Miner Ballot. In
particular, $B$ has a Miner Ballot when every `levelOfSupport` in
`vMinerSignals` is 0.

If $B$ has a Miner Ballot for $P$, then $B$ rates option $o$ if and only if
`vMinerSignals` has an entry whose `signalCode` is the Option Code of $o$. If
$B$ rates $o$, then $L_{B,o}$, the Level of Support of $B$ for $o$, is the
`levelOfSupport` of that entry. If $B$ does not rate $o$, then $L_{B,o} = 0$.

If $B$ has no Miner Ballot for $P$, then $B$ rates no option, and
$L_{B,o} = 0$ for every option $o$.

Blocks before the activation of ZIP 248 have no coinbase bundle, and so have no
Miner Ballot.

## Interpretation of Results

A Poll Definition does not name a network. The result of a Miner Poll is
defined for a Poll Definition and a network, over the best valid block chain of
that network, once that chain contains the last block of the Voting Period,
which is the block at height Voting End Height − 1. Parties that compute the
result SHOULD wait until that block has at least 100 confirmations.

Let $N$ be the number of blocks in the Voting Period, i.e. Voting End Height −
Voting Start Height, and let $V$ be the set of blocks in the Voting Period.
$N$ is at least 1, because the Voting End Height is greater than the Voting
Start Height. Each block in $V$ is one ballot, regardless of who mined it or
the value of its coinbase outputs. An option that a block does not rate counts
with a Level of Support of 0 in the scoring and the runoff below, whether or
not the block has a Miner Ballot.

A Miner Ballot gives each option a score, which is sufficient information to
interpret the responses to a question by several voting methods. Score voting
is supported directly: the score totals $S_o$ computed in the first step below
are its result, and a published result includes them. STAR voting adds a runoff
between the two options with the greatest score totals. STAR voting is
RECOMMENDED, and the winners of a question are defined by it.

For a question $q$, let $A_q$ be the number of blocks in $V$ that rate at least
one option of $q$. A block that has a Miner Ballot and rates no option of $q$
abstains on $q$. If $A_q = 0$, $q$ has no result. Otherwise, for a question
whose `tally` has `"method": "star"` and `"winners": W`, the winners of $q$ are
chosen by $W$ rounds of STAR voting [^star-voting], as follows. Let $C$ be the
set of options of $q$. In each round:

1. **Scoring.** For each option $o$ in $C$, let the score total
   $S_o = \sum_{B \in V} L_{B,o}$.
2. **Finalists.** A pair of distinct options $\{a, b\}$ in $C$ is a possible
   finalist pair if no option in $C \setminus \{a, b\}$ has a score total
   greater than $S_a$ or greater than $S_b$. If the score totals of the options
   in $C$ are distinct, there is exactly one possible finalist pair; if score
   totals are equal, there can be several.
3. **Runoff.** For a possible finalist pair $\{a, b\}$, let $R_{a,b}$ be the
   number of blocks $B$ in $V$ with $L_{B,a} > L_{B,b}$, and $R_{b,a}$ the
   number with $L_{B,b} > L_{B,a}$. The runoff winner of the pair is the option
   with the greater of these counts. If $R_{a,b} = R_{b,a}$, it is the option
   with the greater score total. If the score totals are also equal, the pair
   has no runoff winner.
4. **Winner.** If every possible finalist pair has a runoff winner, and all of
   those runoff winners are the same option, that option wins the round, and
   is removed from $C$. Otherwise, the round is tied.

The winners of $q$ are the winners of its rounds, in order. With $W = 1$ this
is single-winner STAR voting; with $W > 1$ it is Bloc STAR voting. Since $W$ is
less than the number of options, $C$ has at least two options in every round.
If a round is tied, the result of $q$ consists of the winners of the earlier
rounds and the tied round, and later rounds are not computed.

The result computed as above is the interpretation to which the Poll
Definition commits, but it informs the community's judgment rather than
replacing it. For example, the winner of a runoff can have a much lower score
total than the other finalist, and this ZIP cannot determine in advance how the
community would judge such a result. Likewise, this ZIP does not specify how a
tied round is resolved or interpreted, and that may differ from one Miner Poll
to another. A Poll Coordinator MAY state, in the announcement at `url`, how it
intends a tied round to be interpreted.

A published result of a Miner Poll SHOULD include:

* the Poll Digest;
* the height and hash of the last block of the Voting Period in the block
  chain that was tallied;
* $N$, and the number of blocks in $V$ that have a Miner Ballot;
* for each option $o$, and each Level of Support $\ell$ from 0 to 255, the
  number of blocks in $V$ that rate $o$ with a Level of Support of $\ell$,
  where nonzero;
* for each question $q$: $A_q$ and the percentage $100 \cdot A_q / N$; the
  number of blocks in $V$ that abstain on $q$; and, for each round, the score
  totals, the possible finalist pairs, their runoff counts, and the winner, or
  that the round is tied.

The counts of blocks by option and Level of Support determine everything else in
the result, and are authoritative. Any percentage in a summary of the result
SHOULD be relative to $N$.

## Recommendations for Poll Coordinators

When an Ecosystem Poll is coordinated, it is RECOMMENDED that the party
coordinating it also act as Poll Coordinator for a Miner Poll that accompanies
it, as follows:

* The Poll Definition SHOULD have the same questions and options as the
  Ecosystem Poll, identical in wording and order, so that the results of the two
  polls can be compared. The exception is an explicit "Abstain" option of the
  Ecosystem Poll, which SHOULD be left out of the Poll Definition: a miner
  abstains on a question by rating none of its options, and a published result
  gives the number of blocks that do so.
* A question for which the Ecosystem Poll allows a single selection SHOULD have
  `"winners": 1`. A question for which it allows up to $k$ selections, such as
  the election of $k$ members of a committee, SHOULD have `"winners": k`.
* The Voting Period SHOULD coincide with the voting window of the Ecosystem
  Poll. To convert times to block heights, the Poll Coordinator SHOULD use the
  block target spacing in effect, accounting for any network upgrade scheduled
  to activate before the Voting End Height.
* The Poll Coordinator SHOULD publish the Poll Definition, as a file, and its
  Poll Digest together with the announcement of the Ecosystem Poll, and at
  least 14 days before the block at the Voting Start Height is expected to be
  mined, so that mining pools have time to reconfigure.
* The Poll Coordinator SHOULD NOT change a Poll Definition once it is
  published. To change it, the Poll Coordinator SHOULD publish a new Poll
  Definition, which has a different Poll Digest, before the block at the Voting
  Start Height of the original is mined, and state that it supersedes the
  original.
* The Voting Periods of two Miner Polls held on the same network SHOULD NOT
  overlap, since a block carries at most one Poll Digest. Questions that would
  be asked in concurrent Miner Polls SHOULD be combined into a single Poll
  Definition.
* The Poll Coordinator SHOULD publish the result of the Miner Poll alongside
  the result of the Ecosystem Poll.

This ZIP does not specify what weight the result of a Miner Poll carries
relative to the result of an Ecosystem Poll, or how the two are combined.

## Testnet-specific considerations

It is RECOMMENDED that a Miner Poll on Mainnet be rehearsed on Testnet. Block
heights on Testnet differ from those on Mainnet, so the rehearsal normally
needs its own Poll Definition, whose Voting Period is given in Testnet block
heights and whose Poll Digest therefore differs. That Poll Definition SHOULD
use the questions, options, and methods of interpretation of the Mainnet Poll
Definition, so that miners rehearse the same ratings with the same tools.

Miner Ballots for the same Poll Definition can be cast on more than one
network. The result on each network is computed from the block chain of that
network alone.

## Example

This subsection is non-normative.

Consider the following hypothetical Poll Definition:

```json
{
  "version": 1,
  "title": "NU7 Miner Sentiment (example)",
  "url": "https://forum.zcashcommunity.com/t/nu7-sentiment-polls-results/57590",
  "votingStartHeight": 3700000,
  "votingEndHeight": 3740320,
  "questions": [
    {
      "title": "NSM issuance curve",
      "description": "How should the block subsidy be issued after NU7?",
      "tally": { "method": "star", "winners": 1 },
      "options": [
        { "code": 1, "label": "Smooth issuance curve" },
        { "code": 2, "label": "Preserve halvings" },
        { "code": 3, "label": "Do not include issuance smoothing in NU7" }
      ]
    },
    {
      "title": "NSM reissuance",
      "description": "When should burned funds start to be reissued?",
      "tally": { "method": "star", "winners": 1 },
      "options": [
        { "code": 4, "label": "As soon as possible" },
        { "code": 5, "label": "February 2027" },
        { "code": 6, "label": "February 2031" }
      ]
    },
    {
      "title": "v4 transaction disablement",
      "description": "When should v4 transactions stop being accepted?",
      "tally": { "method": "star", "winners": 1 },
      "options": [
        { "code": 7, "label": "Immediately at NU7 activation" },
        { "code": 8, "label": "One year after this poll" },
        { "code": 9, "label": "Do not set a date" }
      ]
    },
    {
      "title": "25-second block target spacing",
      "description": "Should NU7 reduce the block target spacing to 25 seconds?",
      "tally": { "method": "star", "winners": 1 },
      "options": [
        { "code": 10, "label": "Yes" },
        { "code": 11, "label": "No" }
      ]
    },
    {
      "title": "NU8 priorities",
      "description": "Which two of these features should be prioritized for NU8?",
      "tally": { "method": "star", "winners": 2 },
      "options": [
        { "code": 12, "label": "Zcash Shielded Assets" },
        { "code": 13, "label": "Memo bundles" },
        { "code": 14, "label": "Quantum recoverability" },
        { "code": 15, "label": "Transparent pool deprecation" }
      ]
    }
  ]
}
```

Its Canonical Encoding is the following 1575 bytes (shown here on one line):

```
{"questions":[{"description":"How should the block subsidy be issued after NU7?","options":[{"code":1,"label":"Smooth issuance curve"},{"code":2,"label":"Preserve halvings"},{"code":3,"label":"Do not include issuance smoothing in NU7"}],"tally":{"method":"star","winners":1},"title":"NSM issuance curve"},{"description":"When should burned funds start to be reissued?","options":[{"code":4,"label":"As soon as possible"},{"code":5,"label":"February 2027"},{"code":6,"label":"February 2031"}],"tally":{"method":"star","winners":1},"title":"NSM reissuance"},{"description":"When should v4 transactions stop being accepted?","options":[{"code":7,"label":"Immediately at NU7 activation"},{"code":8,"label":"One year after this poll"},{"code":9,"label":"Do not set a date"}],"tally":{"method":"star","winners":1},"title":"v4 transaction disablement"},{"description":"Should NU7 reduce the block target spacing to 25 seconds?","options":[{"code":10,"label":"Yes"},{"code":11,"label":"No"}],"tally":{"method":"star","winners":1},"title":"25-second block target spacing"},{"description":"Which two of these features should be prioritized for NU8?","options":[{"code":12,"label":"Zcash Shielded Assets"},{"code":13,"label":"Memo bundles"},{"code":14,"label":"Quantum recoverability"},{"code":15,"label":"Transparent pool deprecation"}],"tally":{"method":"star","winners":2},"title":"NU8 priorities"}],"title":"NU7 Miner Sentiment (example)","url":"https://forum.zcashcommunity.com/t/nu7-sentiment-polls-results/57590","version":1,"votingEndHeight":3740320,"votingStartHeight":3700000}
```

and its Poll Digest is `f2e5bc060e401bddc741565ebf91d2c9`.

Suppose that a miner, Miner A, rates option 1 at 255, option 2 at 128, option 3
at 1, option 5 at 200, option 10 at 255, option 11 at 1, option 12 at 255,
option 13 at 200, and option 14 at 50, and does not rate options 4, 6, 7, 8, 9,
or 15. The miner signalling fields of its coinbase bundles are then the 35 bytes

```
09 01ff 0280 0301 05c8 0aff 0b01 0cff 0dc8 0e32 f2e5bc060e401bddc741565ebf91d2c9
```

that is, `nMinerSignals` = 9, nine (`signalCode`, `levelOfSupport`) pairs, and
the Poll Digest.

Suppose that Miner B rates option 1 at 1, option 3 at 255, option 10 at 1,
option 11 at 255, option 13 at 255, option 14 at 100, and option 15 at 255. The
Voting Period has $N = 40320$ blocks, of which Miner A mines 20000 and Miner B
mines 10000, each with its Miner Ballot; the remaining 10320 blocks have no
Miner Ballot. Then:

* Question 1: the score totals are $S_1 = 20000 \cdot 255 + 10000 \cdot 1 =
  5110000$, $S_2 = 2560000$, and $S_3 = 2570000$, so the finalists are options 1
  and 3. In the runoff, 20000 blocks rate option 1 above option 3 and 10000 rate
  option 3 above option 1, so option 1 wins. $A_1 = 30000$ (74.40%).
* Question 2: Miner B abstains. $S_5 = 4000000$ and $S_4 = S_6 = 0$, so the
  possible finalist pairs are $\{5, 4\}$ and $\{5, 6\}$. Option 5 wins both
  runoffs, 20000 to 0, so option 5 wins although options 4 and 6 are tied.
  $A_2 = 20000$ (49.60%).
* Question 3: both miners abstain, so no block rates any of its options, and
  it has no result.
* Question 4: option 10 wins the runoff against option 11, 20000 to 10000.
* Question 5 has two winners. In the first round, the score totals are
  $S_{12} = 5100000$, $S_{13} = 6550000$, $S_{14} = 2000000$, and
  $S_{15} = 2550000$, so the finalists are options 13 and 12. Although option 13
  has the greater score total, 20000 blocks rate option 12 above option 13 and
  only 10000 rate option 13 above option 12, so option 12 wins the first round.
  In the second round, the finalists are options 13 and 15; 20000 blocks rate
  option 13 above option 15, and none rate option 15 above option 13, so option
  13 wins. The winners are options 12 and 13.

The following table shows how coinbase bundles at heights in the Voting Period
are interpreted for this Poll Definition:

| Miner signalling fields | Result |
|-------------------------|--------|
| `09 01ff 0280 … 0e32 f2e5…d2c9` | Miner Ballot, as above. |
| `00` | No Miner Ballot: no signals. |
| `01 10ff f2e5…d2c9` | No Miner Ballot: 16 is not an Option Code of this Poll Definition. |
| `01 0100 f2e5…d2c9` | Miner Ballot that rates option 1 at 0, and abstains on questions 2 to 5. |
| `01 01ff` followed by any other Poll Digest | No Miner Ballot for this Poll Definition. |
| `02 0aff 01ff f2e5…d2c9` | Cannot occur: signal codes are not in ascending order, so ZIP 248 makes the block invalid. |


# Rationale

## Rationale for separating mechanism from governance

Who polls miners, on what, and with what weight are matters for the Zcash
community's governance processes, which change more often than a data format
and a tally procedure should. This ZIP therefore specifies only the mechanism,
and limits itself to recommendations on its use. Recommending that whoever
coordinates an Ecosystem Poll also construct the Poll Definition keeps the
questions of the two polls identical without assigning that role to any
particular party.

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

## Rationale for STAR voting

STAR (Score Then Automatic Runoff) voting uses a score ballot, which a Level of
Support provides directly, and combines the expressiveness of score voting with
a majoritarian runoff: the runoff gives the result to whichever finalist more
ballots prefer, which reduces the incentive to exaggerate scores. Question 5 of
the [Example] shows the runoff overriding the score totals. Bloc STAR voting,
which repeats STAR voting with each winner removed, chooses several winners
without a separate ballot format, so the same Miner Ballot can answer a question
that has one winner and a question that has several. An option that a Miner
Ballot does not rate counts as if it were rated 0, the lowest possible score,
as a candidate left blank does in STAR voting.

STAR voting is usually described with scores from 0 to 5. The scores here range
from 0 to 255 because that is the range of `levelOfSupport`; a finer scale does
not change the method.

The method of interpretation is part of the Poll Definition, and so is committed
to by the Poll Digest, so that miners know before voting how their ratings will
be used, and no one can choose a method after seeing the ratings. The `method`
member allows later versions of this ZIP to add other methods.

A tie in the runoff is broken by score totals, as in STAR voting. Other ties
are not broken. Breaking them by the order of the options would let whoever
writes the Poll Definition favour an option, and breaking them with randomness
derived from the block chain would let the miner of the last block of the
Voting Period influence the outcome. Since a Miner Poll measures sentiment and
does not decide anything, a tie is itself a meaningful result, and how to treat
it is left to the community. A tie in score totals has no effect when every way
of breaking it leads to the same winner, as in question 2 of the [Example], so
it does not make the round tied. With tens of thousands of blocks in a Voting
Period, ties that do affect the winner are unlikely except among options that
few blocks rate.

## Rationale for distinguishing no support from abstention

A Miner Ballot that rates an option at 0 says that the miner considered the
option and does not support it. A Miner Ballot with no entry for an option says
nothing about that option. The two count alike in the scoring and the runoff,
so the distinction does not change the winners, but a result records it.

A Miner Ballot that rates every option of a question at 0 answers the question.
It shows that the miner understood the options and approves of none of them,
and it counts toward participation in that question. A Miner Ballot that rates
none of the options of a question abstains on it. A question on which many
miners abstain, while they answer the other questions, may have been unclear.

For this reason a Poll Definition does not need an "Abstain" option. Such an
option would be scored, and could win a round, as if it were one of the
choices, when abstention is already expressed by rating nothing.

## Rationale for reporting participation

The winners of a question depend only on the blocks that rate its options, so a
single miner could decide a question that few others answer. A published result
therefore gives $A_q$, the number of blocks that rate an option of the
question, alongside $N$. Participation is reported for each question, since a
Miner Ballot can leave a question unanswered, and overall participation would
overstate it for such a question.

This ZIP sets no minimum participation for a result to count. A threshold would
only turn the published participation into a yes or a no, and nothing
determines what its value should be, so fixing one in the Poll Definition would
invite disputes over the number instead of the result. Readers judge
participation from the published counts.

The tally does not group blocks by miner, because coinbase outputs and pool
tags are chosen by miners and do not reliably identify them.

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
  it can express only choices, not scores.
* Block header version bits: consensus only requires the block version number to
  be at least 4 [^protocol-blockheader], but a bit expresses only yes or no.
* Separate transactions: anyone can create them, and they are not tied to block
  production.

The cost of using the ZIP 248 fields is that Miner Polls are possible only after
the network upgrade that deploys ZIP 248.

## Rationale for the Poll Digest

The Poll Digest binds a Miner Ballot to the exact text of the questions and
options that the miner rated, and to the Voting Period and methods of
interpretation under which they will be tallied. Option Codes therefore need to
be unique only within a Poll Definition, and a miner still configured for a
superseded or earlier Poll Definition never contributes to a later one. Sixteen
bytes make an accidental collision negligible; a deliberate collision gains
nothing, since the Poll Coordinator publishes the Poll Definition and the Poll
Digest together. The personalization string separates Poll Digests from other
BLAKE2b hashes used in Zcash.

A Poll Definition has no identifier of its own, because the Poll Digest already
identifies its contents; the `title` serves for display. It does not name a
network either. The tally for a network reads only the block chain of that
network, so a Miner Ballot cast on Testnet never counts on Mainnet, and a
rehearsal on Testnet normally has different block heights and therefore a
different Poll Digest.

The Canonical Encoding makes the Poll Digest independent of how the Poll
Definition was formatted, so that tools written in different languages compute
the same Poll Digest from the same document. JCS is a published standard with
implementations in many languages. Restricting the document to integers and
ASCII member names avoids the parts of JCS that are hardest to implement:
floating-point serialization and sorting by UTF-16 code units. Rejecting
unknown members makes every byte of the Canonical Encoding meaningful to the
tools that display the Poll Definition, so a miner can see everything its Miner
Ballot commits to.

Strings are hashed as written, as JCS requires. Normalizing them first, for
example to Normalization Form C [^UAX15], would make strings that are
canonically equivalent in Unicode produce the same Poll Digest. However, the
result of normalization depends on the version of the Unicode Standard that a
tool implements. A code point that is unassigned in one version can become a
combining mark in a later one, and normalization then reorders the marks
around it, so two tools could compute different Poll Digests for the same
document. Normalization is also unnecessary: the Poll Coordinator publishes the
Poll Definition as a file, and miners load that file instead of retyping it.

## Rationale for leaving tooling unspecified

Interoperability requires only that miners and tallying software agree on the
Poll Definition and on the encoding of a Miner Ballot in the coinbase bundle.
How a miner's ratings reach the software that constructs coinbase transactions
differs between node implementations and mining setups, and needs no common
format.

## Rationale for block-height Voting Periods

Block heights are deterministic, whereas block timestamps are chosen by miners.
Changes to the block target spacing are accounted for when the Voting Period is
chosen. The Voting Period includes its start height and excludes its end
height, as the height range of a funding stream does in ZIP 207 [^zip-0207].
The number of blocks is then the difference of the two heights, and one Voting
Period can end at the height at which another starts without the two
overlapping. The recommended 14-day notice period gives mining pools time to
reconfigure.


# Deployment

Miner Polls depend on the miner signalling fields of the coinbase bundle
defined in ZIP 248, and can be held only in blocks after the activation of the
network upgrade that deploys ZIP 248.


# Reference implementation

None yet. A reference implementation is needed of:

* software that prepares a Miner Ballot from a Poll Definition and includes it
  in coinbase transactions;
* computation of the result of a Miner Poll.


# Open issues

* Whether one poll per block is sufficient, or whether ZIP 248 should allow a
  coinbase bundle to carry signals for more than one Poll Digest.
* Whether a proportional multi-winner method, such as Proportional STAR, should
  be offered in addition to Bloc STAR for questions such as committee elections.
* Whether a Poll Definition should commit to how a tied round is to be
  interpreted, with leaving ties unresolved as one of the choices.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3] or later](protocol/protocol.pdf)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^protocol-coinbasetransactions]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.11: Coinbase Transactions](protocol/protocol.pdf#coinbasetransactions)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-blockheader]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.6: Block Header Encoding and Consensus](protocol/protocol.pdf#blockheader)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](zip-0218.md)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235.md)

[^zip-0248-coinbase]: [ZIP 248: Extensible Transaction Format — Coinbase Bundle](zip-0248.rst#coinbase-bundle)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^nu7-poll-results]: [NU7 Sentiment Polls Results](https://forum.zcashcommunity.com/t/nu7-sentiment-polls-results/57590)

[^star-voting]: [STAR Voting](https://www.starvoting.org/)

[^RFC7493]: [RFC 7493: The I-JSON Message Format](https://www.rfc-editor.org/rfc/rfc7493.html)

[^RFC7693]: [RFC 7693: The BLAKE2 Cryptographic Hash and Message Authentication Code (MAC)](https://www.rfc-editor.org/rfc/rfc7693.html)

[^RFC8259]: [RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259.html)

[^RFC8785]: [RFC 8785: JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785.html)

[^UAX15]: [Unicode Standard Annex #15: Unicode Normalization Forms](https://www.unicode.org/reports/tr15/)

[^json-schema]: [JSON Schema: A Media Type for Describing JSON Documents, Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core)
