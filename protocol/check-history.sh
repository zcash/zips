#!/usr/bin/env bash
# Check that protocol.tex has an unreleased change-history block if it has changed since
# the last release, and warn if an already-released block has changed.
#
# The latest released version is read from protocol.tex itself: the first \historyentry.
# If that entry is for \docversion, an unreleased block exists and the check passes.
# Otherwise the entry names a released version. Its tag is looked up under both forms used
# in this repository ("v2026.9.0" and "2025.6.3"), fetched shallowly if absent, and
# protocol.tex must then be identical to the tagged copy. A release whose tag is not yet
# pushed passes with a notice.
#
# Why: a PR adds its history item to the unreleased block. If a release happens between the
# PR's base and its merge, git's context matching can place that item in the block that has
# since been released, which no review of the PR's diff can show. This happened when #1443
# was merged: its item landed under 2026.8.0.
#
# Usage: protocol/check-history.sh [REVISION]
# Without a revision, the working tree's protocol.tex is checked; with one, that revision's.

set -euo pipefail
cd "$(dirname "$0")"

rev="${1:-}"
if [ -n "$rev" ]; then
    tex_contents=$(git show "$rev:protocol/protocol.tex")
else
    tex_contents=$(cat protocol.tex)
fi

# grep reads all of its input: an early exit (grep -m1, head) would make the writer fail with
# SIGPIPE under pipefail.
entries=$(printf '%s\n' "$tex_contents" | grep -E '^\\historyentry\{' || true)
first="${entries%%$'\n'*}"
if ! [[ $first =~ ^\\historyentry\{([^}]*)\}\{([^}]*)\} ]]; then
    echo "::error file=protocol/protocol.tex::could not parse the first \\historyentry: $first"
    exit 1
fi
version="${BASH_REMATCH[1]}"

if [ "$version" = '\docversion' ]; then
    echo "ok: protocol.tex has an unreleased change-history block"
    exit 0
fi

tag=""
for candidate in "v$version" "$version"; do
    if git rev-parse -q --verify "refs/tags/$candidate^{commit}" >/dev/null 2>&1 \
       || git fetch -q --depth=1 origin "refs/tags/$candidate:refs/tags/$candidate" 2>/dev/null; then
        tag="$candidate"
        break
    fi
done
if [ -z "$tag" ]; then
    echo "::notice file=protocol/protocol.tex::version $version is not tagged yet; nothing to compare against"
    exit 0
fi

# Pathspecs are relative to the current directory, protocol/.
if [ -n "$rev" ]; then
    changed=$(git diff --quiet "$tag" "$rev" -- protocol.tex && echo no || echo yes)
else
    changed=$(git diff --quiet "$tag" -- protocol.tex && echo no || echo yes)
fi
if [ "$changed" = no ]; then
    echo "ok: protocol.tex is unchanged since release $version ($tag)"
    exit 0
fi

# The released blocks: from the first dated \historyentry to the end of the Change History section.
released_blocks() {
    awk '/^\\historyentry\{[^\\]/ { p = 1 } /^\\intropart/ { if (p) exit } p'
}
if ! diff -u \
     <(git show "$tag:protocol/protocol.tex" | released_blocks) \
     <(printf '%s\n' "$tex_contents" | released_blocks) >/dev/null; then
    echo "::warning file=protocol/protocol.tex::a released change-history block differs from its text at $tag; a merge or rebase may have put new items under a released version (a deliberate retroactive edit is fine)"
fi

echo "::error file=protocol/protocol.tex::protocol.tex has changed since release $version ($tag), but its first change-history entry is still $version. Add \\historyentry{\\docversion}{} with an itemize block above it, and move any new items that a merge placed under a released version into that block."
exit 1
