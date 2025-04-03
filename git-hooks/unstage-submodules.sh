#!/bin/sh
# Copyright 2025 The Fuchsia Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# This script unstages submodules prior to commiting, but only if the current
# repository is fuchsia.git.
#
# fuchsia.git is the only repository that has submodules that shouldn't be
# updated manually. Its submodules only exist for the purpose of Code Search and
# are never initialized locally, but may still incidentally be `git add`ed
# because Git recognizes them as "old-form" submodules.

set -euf

# Provide a safety hatch in case the user really does intend to commit
# submodules, or the unstaging logic happens to be buggy.
if [ -n "${FUCHSIA_DONT_UNSTAGE_SUBMODULES:-}" ]; then
  exit 0
fi

# Get the remote, but don't fail if for some reason there's no remote named
# "origin".
remote="$(git remote get-url origin 2>/dev/null || echo "no remote")"

# Exit early if the repository is not fuchsia.git.
case "$remote" in
*/fuchsia) ;;
*) exit 0 ;;
esac

staged_submodules="$(
  git submodule status |
  awk '{ print $2 }' |
  # We have to use `git status` rather than `git diff` since `git diff`
  # excludes submodules that have `ignore = all` in .gitmodules.
  xargs git status --porcelain |
  # "M" as the first character indicates a staged modified file. Remove the "M"
  # prefix and any subsequent whitespace before the filename. The combination of
  # `-n` and `/p` causes sed to only print matching lines.
  sed -n '/^M/s/^M\s*//p'
)"

repo_root="$(git rev-parse --show-toplevel)"

submodule_count=0
last_submodule=

IFS='
'
for file in $staged_submodules; do
  # Unstage the submodule, but don't change its checked-out revision.
  git reset --quiet HEAD -- "${repo_root}/${file}"
  submodule_count=$((submodule_count+1))
  last_submodule="$file"
done

if [ $submodule_count -eq 1 ]; then
  echo "info: unstaged submodule ${last_submodule} (see https://fxbug.dev/290956668)"
elif [ $submodule_count -gt 1 ]; then
  echo "info: unstaged ${submodule_count} submodules (see https://fxbug.dev/290956668)"
fi
