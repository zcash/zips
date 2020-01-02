#!/bin/bash
set -efuxo pipefail

TAG='zcash-zips-render'

docker build -t "$TAG" .
docker run -v "$(pwd):/zips" "$TAG"
