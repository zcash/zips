    ZIP: Unassigned
    Title: Miner Sentiment Polling
    Owners: Marek <marek@zfnd.org>
    Status: Draft
    Category: Process / Ecosystem
    Created: 2026-10-27
    License: MIT


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be
interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in all
capitals.

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

The term "Zcash Community Advisory Panel" (or "ZCAP") is to be interpreted as
described in ZIP 1015. [^zip-1015]

The terms below are to be interpreted as follows:

Election
:   A round of sentiment polling on the scope or timing of one or more upcoming
    network upgrades, consisting of a Coinholder Poll, a ZCAP Poll, or both, and
    the Miner Poll specified in this ZIP.

Coinholder Poll
:   The poll of ZEC holders held for an Election, such as the NU7 coinholder vote.
    [^nu7-poll-questions]

ZCAP Poll
:   The poll of ZCAP members held for an Election. [^nu7-poll-results]

Miner Poll
:   The poll of miners held for an Election, as specified in this ZIP.

Reference Poll
:   The Coinholder Poll of an Election or, if the Election has no Coinholder Poll,
    its ZCAP Poll.

Poll Organizer
:   The party or parties that call the Reference Poll of an Election; for example,
    Valar Group and Project Tachyon called the NU7 Coinholder Poll.
    [^nu7-poll-questions]

Poll Definition
:   The document that specifies a Miner Poll; see [Poll Definitions].

Election Identifier
:   The short string that identifies an Election in Miner Ballots.

Voting Period
:   The inclusive range of block heights in which Miner Ballots for an Election
    are counted, from the Voting Start Height to the Voting End Height.

Miner Data
:   The bytes of the script of the transparent input of a coinbase transaction
    that follow the encoding of the block height required by § 7.1.2
    ‘Transaction Consensus Rules’. [^protocol-txnconsensus]

Coinbase Memo
:   The memo field of a shielded output of a coinbase transaction, as recovered by
    decrypting the output using a sequence of 32 zero bytes as the outgoing
    viewing key, as specified in § 4.20.3 ‘Decryption using an Outgoing Viewing
    Key (Sapling and Orchard)’. [^protocol-decryptovk] [^zip-0213]

Miner Ballot
:   A string that encodes a miner's answers to the questions of an Election; see
    [Miner Ballots].

Answer Character
:   A byte that is an ASCII digit `1` to `9`, an uppercase ASCII letter `A` to
    `Z`, or a hyphen `-`.

Participation Threshold
:   The minimum percentage of the blocks in a Voting Period that answer a
    question, for the Miner Poll results on that question to be considered
    representative of miners.


# Abstract

This proposal specifies a process for gauging miners' sentiment on upcoming
network upgrades. For each Election, miners answer the same questions, with the
same options, as coinholders and the ZCAP.

A miner votes by including a compact ASCII Miner Ballot in the coinbase
transaction of each block it mines within a Voting Period, which the community
agrees upon through public review and which is fixed in block heights in
advance. The Miner Ballot goes in the Miner Data of the coinbase script or in a
Coinbase Memo. Each block in the Voting Period is one vote, and a block without
a valid Miner Ballot answers no question, so results are shares of all blocks in
the Voting Period and approximate shares of hashrate. Anyone can compute them
from the block chain.

Miner Poll results are published alongside Reference Poll results and have the
same standing. Miner Ballots are public and linked to the blocks that carry
them. No consensus change is required.


# Motivation

The scope of network upgrades is now decided with input from Coinholder Polls and
from polls of community panels such as the ZCAP; ZIP 259 cites both for NU7.
[^zip-0259]

Miners are not polled, although network upgrades affect them directly. NU7
changes the block target spacing and the block subsidy per block [^zip-0218], and
removes 60% of transaction fees from circulation [^zip-0235]. An upgrade also
activates safely only if miners run node software that supports it.

Miners already put free-form text in coinbase transactions, and ZIP 213
anticipated identifying text in shielded coinbase memos [^zip-0213], but without
a common format that text cannot be tallied. A common encoding makes the tally
reproducible by anyone, and asking the questions of the Reference Poll makes the
results directly comparable.


# Privacy Implications

Miner Ballots are public by design and linked to the blocks that carry them and
to their coinbase outputs. Coinbase outputs are already public: transparent
outputs directly, and shielded outputs because they decrypt with the all-zero
outgoing viewing key [^zip-0213]. A Miner Ballot therefore reveals only the
miner's answers.

Unlike a Coinholder Poll, a Miner Poll has no ballot secrecy: the positions of
mining pools and solo miners become public. A mining pool votes with its hashers'
work; individual hashers are not identified, and their preferences are not
recorded.


# Requirements

* Miners can answer exactly the questions of the Reference Poll, with exactly its
  options.
* Casting a Miner Ballot requires no consensus change or new transaction type.
* Existing node software can cast Miner Ballots through string-valued
  configuration.
* Every block counts as a single vote.
* Support for each option is reported as a share of all blocks in the Voting
  Period, including blocks without a Miner Ballot.
* The tally is fully determined by the Poll Definition and public block chain
  data.
* The community agrees upon the Voting Period of each Election through public
  review, and the Voting Period is fixed in advance and unambiguous.
* Miner Poll results are comparable with, and have the same standing as,
  Reference Poll results.


# Non-requirements

* Ballot secrecy for miners.
* A binding effect of the results, or activation signalling enforced by
  consensus.
* Separate representation of hashers within a mining pool.


# Specification

For each Election, the Poll Organizer MUST hold a Miner Poll on Mainnet as
specified below.

## Poll Definitions

For each Election, the Poll Organizer MUST publish a Poll Definition on the Zcash
Community Forum, in the announcement of the Reference Poll or in a post linked
from it. A Poll Definition gives:

* the Election Identifier;
* the network (Mainnet or Testnet);
* the Voting Start Height and the Voting End Height;
* the questions, and the options for each question;
* the Participation Threshold, as a percentage;
* links to the announcements of the Coinholder Poll and the ZCAP Poll, where
  they exist.

The questions and options MUST be identical in wording, order, and number to
those of the Reference Poll. Questions and the options of each question are
numbered from 1 in order of appearance; an explicit "Abstain" option is an
ordinary option. A question MUST NOT have more than 35 options, and an Election
MUST NOT have more than 489 questions, so that every Miner Ballot fits in a
512-byte Coinbase Memo.

The Election Identifier MUST have 1 to 16 characters, each a lowercase ASCII
letter `a` to `z`, an ASCII digit `0` to `9`, or a hyphen `-`. It MUST NOT equal
the Election Identifier of any earlier Poll Definition on the same network.

A published Poll Definition MUST NOT be changed. To change its questions,
options, Voting Period, or Participation Threshold, the Poll Organizer publishes a
new Poll Definition, which supersedes it and is subject to the requirements in
[Voting Period]. A Poll Definition can only be superseded before the block at its
Voting Start Height is mined, and a superseded Poll Definition is not tallied.
Once the Voting Period of a Poll Definition has started, its Miner Poll MUST be
tallied and its results published, even if a new Poll Definition is published
afterward.

## Voting Period

The Voting Period consists of the block heights from the Voting Start Height to
the Voting End Height inclusive. The Voting End Height MUST be greater than or
equal to the Voting Start Height. The Voting Period of each Election is agreed
upon as follows:

1. The Poll Organizer proposes the Voting Period, together with the questions, in
   the announcement of the Reference Poll and invites feedback on the forum.
2. The proposed Voting Period SHOULD coincide with the voting window of the
   Reference Poll. To convert times to block heights, the Poll Organizer SHOULD
   use the block target spacing in effect, accounting for any network upgrade
   scheduled to activate before the Voting End Height.
3. After considering the feedback, the Poll Organizer publishes the final Poll
   Definition. Its Voting Period MUST have been proposed on the forum, as in
   step 1, at least 7 days earlier, so a Voting Period changed in response to
   feedback is proposed again. With the final Poll Definition, the Poll
   Organizer MUST answer on the forum each objection to the Voting Period raised
   during the feedback period, stating how it was addressed or why it was not.
   The final Poll Definition MUST be published at least 14 days before the
   block at the Voting Start Height is expected to be mined.

## Miner Ballots

A Miner Ballot is a string of ASCII bytes with the following ABNF syntax
[^RFC5234]. The prefix is given as bytes because quoted ABNF strings are
case-insensitive.

```abnf
miner-ballot  = %x7A.70.6F.6C.6C.3A election-id ":" answer-string  ; "zpoll:"
election-id   = 1*16( %x61-7A / DIGIT / "-" )
answer-string = 1*answer
answer        = %x31-39 / %x41-5A / "-"
```

The $i$-th Answer Character of the answer string answers question $i$:

* a digit `1` to `9` selects options 1 to 9 respectively;
* a letter `A` to `Z` selects options 10 to 35 respectively;
* a hyphen `-` leaves the question unanswered.

The answer string is the longest run of Answer Characters immediately following
`zpoll:` ‖ election-id ‖ `:`. It ends at the first byte that is not an Answer
Character, or at the end of the containing data.

A Miner Ballot is valid for an Election $E$ if and only if:

* its election-id equals the Election Identifier of $E$;
* its answer string has exactly one character per question of $E$;
* each character of its answer string that is not a hyphen selects an option
  that exists for the corresponding question;
* at least one character of its answer string is not a hyphen.

## Casting Miner Ballots

A miner casts a Miner Ballot by including it in the coinbase transaction of a
block it mines at a height within the Voting Period: in the Miner Data, in the
Coinbase Memo of one or more shielded outputs, or in both. A Coinbase Memo that
carries a Miner Ballot MUST be a text memo as defined in ZIP 302 [^zip-0302]: its
first byte MUST be `0xF4` or smaller, and it MUST be valid UTF-8 after trailing
zero bytes are stripped.

The bytes of a Miner Ballot MUST be consecutive, and the byte immediately
following it, if any, MUST NOT be an Answer Character. In the Miner Data, both
requirements apply to the raw bytes, including script opcodes. Placing the whole
Miner Ballot in a single data push satisfies the first requirement, and ending
the Miner Data, or the text of a text memo before its zero padding, with the
Miner Ballot satisfies the second.

A miner SHOULD include its Miner Ballot in every block it mines during the Voting
Period. Since each block counts separately, a miner MAY change its Miner Ballot
during the Voting Period. A mining pool that casts Miner Ballots SHOULD publish
its Miner Ballot to its hashers before the Voting Start Height.

## Determining the Miner Ballot of a Block

For an Election $E$ and a block $B$ at a height within the Voting Period of $E$,
the Miner Ballot of $B$ for $E$ is determined as follows:

1. Search the raw bytes of the Miner Data of $B$, without parsing them as script,
   for occurrences of `zpoll:` ‖ Election Identifier of $E$ ‖ `:`. The first
   occurrence that, together with its answer string, forms a Miner Ballot valid
   for $E$ gives the Miner Ballot of $B$.
2. Otherwise, search the Coinbase Memos of the shielded outputs of the coinbase
   transaction of $B$ in the same way, in the order in which the outputs appear
   in the transaction encoding. Skip each Coinbase Memo that is not a ZIP 302
   text memo: one whose first byte is greater than `0xF4`, or that is not valid
   UTF-8 after trailing zero bytes are stripped. The first Miner Ballot valid for
   $E$ found in this order gives the Miner Ballot of $B$.
3. Otherwise, $B$ has no Miner Ballot for $E$.

Any other Miner Ballots for $E$ in $B$ have no effect.

## Tallying

The tally of a Miner Poll is computed over the best valid block chain of the
network given in its Poll Definition, once that chain contains a block at height
Voting End Height + 99, giving the block at the Voting End Height 100
confirmations.

Each block in the Voting Period counts as a single vote. Its Miner Ballot, as
determined in [Determining the Miner Ballot of a Block], counts exactly once,
regardless of who mined it or the value of its coinbase outputs. A block without
a Miner Ballot for the Election counts as answering no question.

Let:

* $N$ be the number of blocks in the Voting Period, i.e. Voting End Height −
  Voting Start Height + 1;
* $P$ be the number of blocks in the Voting Period that have a Miner Ballot for
  the Election;
* $c_{q,o}$ be the number of those blocks whose Miner Ballot selects option $o$
  for question $q$;
* $A_q = \sum_o c_{q,o}$ be the number of those blocks whose Miner Ballot answers
  question $q$.

The results of the Miner Poll consist of:

* for each question $q$ and option $o$, the count $c_{q,o}$ and the percentage
  $100 \cdot c_{q,o} / N$;
* for each question $q$, the count $N - A_q$ of blocks that do not answer $q$,
  and the percentage $100 \cdot (N - A_q) / N$;
* $N$, $P$, and the overall participation $100 \cdot P / N$ as a percentage;
* for each question $q$, whether $100 \cdot A_q / N$ is at least the
  Participation Threshold;
* the height and hash of the block at the Voting End Height in the block chain
  that was tallied.

Percentages in the results, and in any summary of them by the Poll Organizer,
MUST be relative to $N$. The counts are authoritative.

The results on question $q$ are representative of miners if and only if
$100 \cdot A_q / N$ is at least the Participation Threshold.

## Publication and Standing of Results

The Poll Organizer MUST publish the Miner Poll results in the same forum thread
as the Reference Poll results, no later than 7 days after the block at height
Voting End Height + 99 is mined.

Miner Poll results have the same standing as the Reference Poll results of the
same Election. Any summary of an Election's results by the Poll Organizer MUST
present the Miner Poll results with the same prominence and detail as the
Reference Poll results. A ZIP that cites an Election's Coinholder Poll or ZCAP
Poll results, as ZIP 259 does for NU7 [^zip-0259], SHOULD also cite that
Election's Miner Poll results.

This ZIP does not specify how Miner Poll results are combined with Coinholder
Poll or ZCAP Poll results.

## Testnet-specific considerations

Miner Polls SHOULD be rehearsed on Testnet before the first Miner Poll on
Mainnet. Miner Polls on Testnet are rehearsals only: they are not the Miner Poll
of any Election and have no significance for Zcash governance.

Miner Ballots have the same encoding on both networks, and Election Identifiers
are unique only per network. A Poll Definition on Testnet that rehearses a Miner
Poll on Mainnet SHOULD use the Election Identifier, questions, and options of
that Mainnet Poll Definition, so that miners rehearse exactly the Miner Ballots
they will cast on Mainnet. The 7-day and 14-day requirements in [Voting Period]
do not apply on Testnet.

## Example

This subsection is non-normative.

Consider a hypothetical Mainnet Election with Election Identifier `nu8` and five
questions, which have 4, 4, 4, 3, and 4 options.

The 15-byte Miner Ballot `zpoll:nu8:2311-` selects option 2 for question 1,
option 3 for question 2, and option 1 for questions 3 and 4; it leaves question 5
unanswered. A miner placing it in the Miner Data of a block at height 3,600,000
can use the 20-byte coinbase script `0380ee360f7a706f6c6c3a6e75383a323331312d`:
the height encoding `0380ee36`, the push opcode `0f`, and the Miner Ballot. As a
Coinbase Memo, the Miner Ballot is its 15 bytes followed by 497 zero bytes. The
same 15 bytes followed by `0xFF` and 496 zero bytes are not valid UTF-8, so that
memo is not a text memo and carries no Miner Ballot.

If the Voting Period has 100,000 blocks and only 10, all mined by one pool, carry
`zpoll:nu8:2311-`, option 2 of question 1 has 10 votes (0.01%) and 99,990 blocks
(99.99%) do not answer question 1. Question 1 is answered in only 0.01% of the
Voting Period, so its results are not representative of miners unless the
Participation Threshold is at most 0.01%.

If instead 99,990 blocks carry `zpoll:nu8:2311-` and 10 carry `zpoll:nu8:23113`,
overall participation is 100% and questions 1 to 4 are each answered in 100% of
the Voting Period. Question 5, however, is answered in only 0.01%, so its results
are not representative of miners unless the Participation Threshold is at most
0.01%.

The following table shows how Miner Data is interpreted for this Election:

| Data | Result |
|------|--------|
| `zpoll:nu8:2311-` | Valid, as above. |
| `/ExamplePool/ zpoll:nu8:2311-` | Valid. |
| `zpoll:nu8:2311-/ExamplePool/` | Valid; `/` ends the answer string. |
| `zpoll:nu8:9 zpoll:nu8:2311-` | Valid; the first occurrence is invalid, so the second counts. |
| `zpoll:nu8:2311` | Invalid: four answers for five questions. |
| `zpoll:nu8:2311-X` | Invalid: the answer string has six characters. |
| `zpoll:nu8:2314-` | Invalid: question 4 has no option 4. |
| `zpoll:nu8:-----` | Invalid: no question is answered. |
| `ZPOLL:nu8:2311-` | Not a Miner Ballot: the prefix is case-sensitive. |
| `zpoll:nu7:2311-` | Not a Miner Ballot for `nu8`. |


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

Percentages are relative to all blocks in the Voting Period, as the version bits
mechanism of BIP 9 counts a block that does not signal against activation.
[^bip-0009] Relative to Miner Ballots cast, the 10 Miner Ballots from one pool in
the [Example] would show 100% support for their options; relative to the Voting
Period, they show 0.01%. A miner's influence on any percentage is thus bounded by
its share of the blocks in the Voting Period, however few other miners vote.

This is possible because, unlike that of a Coinholder Poll, the electorate of a
Miner Poll is fully observable. Shares among the blocks that answer a question,
which correspond to the shares of participating ZEC reported for a Coinholder
Poll, follow from the published counts $c_{q,o}$ and $A_q$.

The Participation Threshold flags low turnout, like the 1,000,000 ZEC threshold
of the NU7 Coinholder Poll. [^nu7-poll-questions] Unlike that threshold, which
applied to participation in at least one question, it applies to each question:
since a Miner Ballot can leave questions unanswered, a heavily answered question
would otherwise make the results on an unanswered question appear
representative.

The tally does not group blocks by miner, because coinbase outputs and pool tags
are chosen by miners and do not reliably identify them.

## Rationale for using coinbase transactions

Only the miner of a block controls its coinbase transaction, so proof of work
authenticates the Miner Ballot. No consensus change is needed: consensus
constrains the Miner Data only by the height encoding, the length limit
[^protocol-txnconsensus], and the block-level limit on signature operations
inherited from Bitcoin, to which the ASCII bytes of a Miner Ballot contribute
nothing; and shielded coinbase outputs are publicly decryptable [^zip-0213]. The
Zcash Stratum protocol keeps the extra nonce in the block header nonce
[^zip-0301], leaving room in the Miner Data.

Two alternatives were rejected:

* Block header version bits: consensus only requires the block version number to
  be at least 4 [^protocol-blockheader], but a bit expresses only yes or no.
* Separate transactions: anyone can create them, and they are not tied to block
  production.

## Rationale for the Miner Ballot encoding

ASCII suits string-valued node configuration, ZIP 302 text memos, and block
explorers. Compactness matters because the 100-byte coinbase script is shared
with the height encoding and pool tags; the example Miner Ballot is 15 bytes.
Positional answers need no question numbers, and a hyphen lets a miner skip a
question that has no "Abstain" option.

The Election Identifier and the exact-length and option-range checks keep stale
configurations from counting toward a later Election. Ending the answer string at
the first byte that is not an Answer Character makes a length field unnecessary.
The case-sensitive prefix gives the encoding a single canonical form; an
incompatible future encoding would use a different prefix.

The Miner Ballot has no network field, and Election Identifiers are unique only
per network, so that a rehearsal on Testnet can use exactly the Miner Ballots of
the Miner Poll on Mainnet, keeping Testnet as close to Mainnet as possible. A
Miner Ballot counts on the network whose block carries it: a miner that copies a
rehearsal configuration to Mainnet votes with it on Mainnet.

The Miner Data is searched as raw bytes because consensus does not require it to
be a well-formed script [^protocol-txnconsensus], and a tally that depended on
parsing could differ between implementations that handle malformed scripts
differently.

## Rationale for the precedence of Miner Ballots

The rule is deterministic, and duplicate Miner Ballots carry no penalty. The
Miner Data is checked first because it is always present and needs no
decryption.

## Rationale for block-height Voting Periods

Block heights are deterministic, whereas block timestamps are chosen by miners.
Changes to the block target spacing are accounted for when the Voting Period is
chosen. The 7-day feedback period and the public answers to objections make
agreement on the Voting Period reviewable. As for the questions of the Reference
Poll, that agreement is reached through public review; this ZIP does not define
a separate vote on the Voting Period. The 14-day notice period gives mining pools
time to reconfigure.


# Reference implementation

Miners can cast Miner Ballots with Zebra: its `mining.extra_coinbase_data` option
places text in the Miner Data, and its `mining.miner_memo` option sets the
Coinbase Memo of the miner's output when `mining.miner_address` has a shielded
receiver. [^zebra-mining-config]


# Open issues

* A reference implementation of tallying.
* The interaction with memo bundles [^zip-0231], if they are deployed.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3] or later](protocol/protocol.pdf)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^protocol-coinbasetransactions]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.11: Coinbase Transactions](protocol/protocol.pdf#coinbasetransactions)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-decryptovk]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 4.20.3: Decryption using an Outgoing Viewing Key (Sapling and Orchard)](protocol/protocol.pdf#decryptovk)

[^protocol-txnconsensus]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.1.2: Transaction Consensus Rules](protocol/protocol.pdf#txnconsensus)

[^protocol-blockheader]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.6: Block Header Encoding and Consensus](protocol/protocol.pdf#blockheader)

[^bip-0009]: [BIP 9: Version bits with timeout and delay](https://github.com/bitcoin/bips/blob/master/bip-0009.mediawiki)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0213]: [ZIP 213: Shielded Coinbase](zip-0213.rst)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](zip-0218.md)

[^zip-0231]: [ZIP 231: Memo Bundles](zip-0231.md)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235.md)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^zip-0301]: [ZIP 301: Zcash Stratum Protocol](zip-0301.rst)

[^zip-0302]: [ZIP 302: Standardized Memo Field Format](zip-0302.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^nu7-poll-questions]: [NU7 Coinholder Vote: poll questions and scope](https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912)

[^nu7-poll-results]: [NU7 Sentiment Polls Results](https://forum.zcashcommunity.com/t/nu7-sentiment-polls-results/57590)

[^RFC5234]: [RFC 5234: Augmented BNF for Syntax Specifications: ABNF](https://www.rfc-editor.org/rfc/rfc5234.html)

[^zebra-mining-config]: [Zebra: mining configuration](https://github.com/ZcashFoundation/zebra/blob/main/zebra-rpc/src/config/mining.rs)
