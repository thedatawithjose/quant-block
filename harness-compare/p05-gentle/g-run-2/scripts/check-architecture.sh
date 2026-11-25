#!/usr/bin/env bash
# Layer boundaries (see ARCHITECTURE.md). Exit 1 on any violation.
cd "$(dirname "$0")/.."
fail=0
chk() { # description, pattern, files...
  local d="$1" p="$2"; shift 2
  if grep -nE "$p" "$@" 2>/dev/null; then echo "ARCH VIOLATION: $d"; fail=1; fi
}
chk "renderer must not use Node/Electron APIs" "require\(|node:|from 'electron'|process\." renderer/*.js
chk "lib/ must not import electron (keep it unit-testable)" "require\('electron'\)" lib/*.js
chk "preload.js may only require electron" "require\('(node:|\./|\.\./)" preload.js
[ $fail -eq 0 ] && echo ">> Architecture boundaries OK"
exit $fail
