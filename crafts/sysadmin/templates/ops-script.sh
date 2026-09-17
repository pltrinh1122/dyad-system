#!/usr/bin/env bash
# d-work: #<id>
# class: <reversible | destructive>
# undo: <one command, or: see <same>-undo.sh>
# change-log: workstation-corpus/CHANGELOG.md row "#<id> H<n>"
# postcondition: <the end state, in words>
# destructive: <none | each destructive command in words, one clause each>
set -euo pipefail
git rev-parse --short HEAD; sha256sum "$0"

postcondition() {
  # <read-only test of the end state; exit 0 when it holds>
  false
}
postcondition && { echo "already satisfied"; exit 0; }

# When `# destructive:` is not `none`: define confirm() and call it immediately before each destructive command.
confirm() {
  echo "step: $1"; echo "consequence: $2"; echo "undo: $3"
  [[ -t 0 ]] || { echo "no tty"; exit 2; }
  read -r -p "run this step? Y/N: " ans < /dev/tty
  [[ $ans == Y ]] || { echo "declined"; exit 2; }
}

set -x
# <each mutating command guarded by its own state check: test || cmd>
# <a destructive command: guard || { confirm "<step>" "<consequence>" "<undo>"; cmd; }>
set +x

postcondition || { echo "postcondition failed"; exit 1; }
echo "done"
