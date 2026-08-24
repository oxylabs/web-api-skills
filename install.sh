#!/usr/bin/env bash
# Install the Oxylabs Web API skills for Claude Code.
#
#   ./install.sh              # personal: ~/.claude/skills (available in every project)
#   ./install.sh --project    # this repo only: ./.claude/skills
#
# Re-running overwrites the installed copies, so it doubles as an upgrade.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
DEST="${HOME}/.claude/skills"
[[ "${1:-}" == "--project" ]] && DEST="$(pwd)/.claude/skills"

mkdir -p "$DEST"
for skill in "$SRC"/*/; do
  name="$(basename "$skill")"
  rm -rf "$DEST/$name"
  cp -R "$skill" "$DEST/$name"
  echo "installed $name -> $DEST/$name"
done

echo
echo "Done. Set your key so the skills can call the API:"
echo "  export OXYLABS_WEB_API_KEY=your_api_key_here"
echo "Then start a new Claude Code session and run /skills to confirm they loaded."
