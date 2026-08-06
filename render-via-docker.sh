#!/bin/bash
set -efuxo pipefail

TAG='zcash-zips-render'

podman build -t "$TAG" .
podman run --rm --userns=keep-id -v "$(pwd):/zips" "$TAG"
