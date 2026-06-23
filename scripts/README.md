# scripts/ — Portability Notes

## `smart-autopush.sh` is a host-specific symlink

`scripts/smart-autopush.sh` is committed as a **symlink** pointing at
`/Users/myk/.claude/scripts/smart-push.sh` on the maintainer's host.

This means the symlink is **non-portable**: on any other machine, the target
path will not exist and the symlink will be broken.

### On the maintainer host (`myk`)

The symlink resolves correctly and behaves identically to
`~/.claude/scripts/smart-push.sh`. Use either one.

### On any other host

Replace the symlink with a wrapper script that delegates to the local
`~/.claude/scripts/smart-push.sh` (which is the canonical location maintained
in the `mykcs/.claude` repo):

```bash
# Remove the broken symlink
rm scripts/smart-autopush.sh

# Option A: recreate the symlink against the host-local path
ln -sf "$HOME/.claude/scripts/smart-push.sh" scripts/smart-autopush.sh

# Option B: replace with a portable wrapper
cat > scripts/smart-autopush.sh <<'EOF'
#!/usr/bin/env bash
exec "$HOME/.claude/scripts/smart-push.sh" "$@"
EOF
chmod +x scripts/smart-autopush.sh
```

### Why we did not inline the script

`smart-push.sh` lives in `mykcs/.claude` and is updated frequently. Inlining
it would create a second copy that drifts. The symlink + this README preserves
single-source-of-truth at the cost of a one-time setup step on non-maintainer
hosts.