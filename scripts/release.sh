#!/usr/bin/env zsh
set -e -u -o pipefail

uv run scripts/release.py "$@"
RELEASE_VERSION=$(<RELEASE_VERSION.txt)

uv lock
echo "- updated lock file"

git add CHANGELOG.md pyproject.toml uv.lock
git commit -m "$RELEASE_VERSION release"
echo "- created release commit"

git tag -a "$RELEASE_VERSION" -m "$RELEASE_VERSION"
echo "- created release tag"

rm -f RELEASE_VERSION.txt
