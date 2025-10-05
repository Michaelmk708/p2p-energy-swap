#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${HOME}/.local/bin/p2p"
mkdir -p "${HOME}/.local/bin"
ln -sf "${ROOT_DIR}/p2p" "${TARGET}"
echo "Linked ${TARGET} -> ${ROOT_DIR}/p2p"
case ":$PATH:" in
  *":${HOME}/.local/bin:"*) echo "~/.local/bin is already on PATH";;
  *) echo "NOTE: Add this to your shell rc to use 'p2p' anywhere:\n  export PATH=\"$HOME/.local/bin:$PATH\"";;
cesac
