---
name: opencode-desktop-repair
description: Repair OpenCode desktop when it shows "服务器无法连接", "Failed to fetch", or keeps reopening broken local state even after sessions were deleted. Use this whenever OpenCode desktop starts but its local server dies, old workspaces/sessions keep coming back, or the UI cannot reconnect while `opencode-cli web/serve` works fine.
---

# OpenCode Desktop Repair

This skill is for the specific failure mode where the OpenCode desktop shell keeps restoring bad local UI state from:

- `<USER_HOME>\AppData\Roaming\ai.opencode.desktop`
- `<USER_HOME>\.config\opencode\oh-my-openagent.jsonc`
- `<USER_HOME>\AppData\Roaming\OpenCode\EBWebView\Default`
- `<USER_HOME>\AppData\Roaming\OpenCode\EBWebView\Local State`

Typical symptoms:

- Desktop shows `服务器无法连接`
- Desktop shows `Failed to fetch`
- User deleted sessions, but OpenCode still restores old projects, old session ids, or old tabs
- `opencode-cli web` or `opencode-cli serve` works when launched directly, but `OpenCode.exe` becomes unstable

## Repair Flow

1. Confirm the backend vs desktop split.
   - If direct `opencode-cli web` or `opencode-cli serve` is stable, focus on desktop state.
   - If the CLI server itself is unstable, do not use this skill as the primary fix.

2. Inspect persisted desktop state before changing anything.
   - Read `<USER_HOME>\AppData\Roaming\ai.opencode.desktop\opencode.global.dat`
   - Look for stale `server.lastProject`, `sessionTabs`, `notification`, workspace paths, and session ids.
   - If it still references deleted/broken sessions or projects, proceed.

3. Back up and reset the desktop state store.
   - Stop `OpenCode.exe` and `opencode-cli.exe`.
   - Back up `<USER_HOME>\AppData\Roaming\ai.opencode.desktop`.
   - Recreate an empty `ai.opencode.desktop` directory.

4. Disable OMO auto-config if present.
   - If `<USER_HOME>\.config\opencode\oh-my-openagent.jsonc` exists, move it aside to a timestamped `.disabled_*` file.
   - Reason: this config can auto-load `OhMyOpenCodePlugin` even when the main `plugin` array is empty, and on desktop it may break server-auth injection.

5. Reset WebView state if desktop still shows fetch/reload failures.
   - Back up and clear:
     - `<USER_HOME>\AppData\Roaming\OpenCode\EBWebView\Default`
     - `<USER_HOME>\AppData\Roaming\OpenCode\EBWebView\Local State`
   - Recreate a fresh empty `Default` directory.
   - Reason: stale embedded-browser cache/storage can keep replaying broken front-end state even when the backend is healthy.

6. Use the local repair script when available.
   - Script: `<USER_HOME>\OpenCode-Repair-DesktopState.ps1`
   - Default behavior: backup state, clear desktop state, disable `oh-my-openagent.jsonc` when present, reset WebView state, relaunch `<USER_HOME>\OpenCode-NoProxy.cmd`
   - Example:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<USER_HOME>\OpenCode-Repair-DesktopState.ps1"
```

7. Verify the repair.
   - Check that `OpenCode.exe` and `opencode-cli.exe` stay alive for at least 30 seconds.
   - Confirm `opencode-cli.exe` is listening on a localhost port.
   - Unauthenticated external probes may return `401 Unauthorized`; that still proves the local server is alive.

## Notes

- This repair should not touch `<USER_HOME>\.claude\skills` or `<AGENTS_SKILLS_HOME>\skills`.
- This repair should not edit `<USER_HOME>\.config\opencode\opencode.jsonc`.
- Always preserve a timestamped backup so the user can roll back.

## Output

Report:

- whether the state store was reset
- backup location
- whether OpenCode was relaunched
- whether `OpenCode.exe` and `opencode-cli.exe` remained alive after restart
