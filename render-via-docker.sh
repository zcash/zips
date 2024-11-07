#!/bin/bash
set -efuxo pipefail

TAG='zcash-zips-render'

docker build -t "$TAG" .devcontainer
docker run -v "$(pwd):/zips" "$TAG" -w /zips make all
