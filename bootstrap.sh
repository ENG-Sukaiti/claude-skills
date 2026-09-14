#!/usr/bin/env bash
# Wire this device into Ibrahim's Claude Code setup.
# Idempotent: safe to re-run. Linux and macOS only.
#
# Resolves its own location, so this repo can be cloned anywhere:
#   git clone git@github.com:ENG-Sukaiti/claude-skills.git
#   cd claude-skills && ./bootstrap.sh
set -euo pipefail

SHARED="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"

info() { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }

echo
echo "Bootstrapping Claude Code on $(uname -s) / $(hostname -s)"
echo

[ -d "${SHARED}/skills" ] || { echo "ERROR: no skills/ beside this script ($SHARED)"; exit 1; }
mkdir -p "${CLAUDE_DIR}/skills"

# --- 1. global CLAUDE.md -> shared copy -------------------------------------
link_it() {                       # $1 = target in gSync, $2 = link path
  if [ -L "$2" ]; then
    [ "$(readlink "$2")" = "$1" ] && { info "$(basename "$2") already linked"; return; }
    rm "$2"
  elif [ -e "$2" ]; then
    mv "$2" "$2.bak-$(date +%Y%m%d%H%M%S)"
    warn "existing $(basename "$2") moved aside to $(basename "$2").bak-*"
  fi
  ln -s "$1" "$2"
  info "linked $2 -> $1"
}

link_it "${SHARED}/CLAUDE.md"                    "${CLAUDE_DIR}/CLAUDE.md"
for d in "${SHARED}"/skills/*/; do
  [ -d "$d" ] || continue
  n="$(basename "$d")"
  link_it "${SHARED}/skills/${n}" "${CLAUDE_DIR}/skills/${n}"
done

# --- 2. Notion MCP server (remote, hosted by Notion) ------------------------
if claude mcp get notion >/dev/null 2>&1; then
  info "notion MCP server already registered"
else
  claude mcp add --transport http --scope user notion https://mcp.notion.com/mcp >/dev/null
  info "registered notion MCP server (user scope)"
fi

echo
echo "Done. One manual step left on this device:"
echo "    start claude, run  /mcp  , pick 'notion', approve in the browser."
echo "OAuth tokens are per-device on purpose and are never synced."
echo
