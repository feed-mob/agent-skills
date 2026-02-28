---
name: opencode-agent
description: 'Delegate coding tasks to an attached OpenCode server via `opencode run --attach`. Use when: (1) building new features, (2) refactoring, (3) reviewing changes, (4) iterative coding with background monitoring. This skill is server-only and always uses `--attach` with `--dir` (server-side path).'
metadata:
  {
    "openclaw": { "emoji": "🤖", "requires": { "anyBins": ["opencode"] } },
  }
---

# OpenCode Agent

Use this skill to run coding tasks through a remote OpenCode server.

## Required Command Pattern

Always use this shape:

```bash
opencode run --attach <server_url> "<task>" --dir "<server_path>"
```

Example:

```bash
opencode run --attach http://127.0.0.1:4096 "what is in this folder" --dir "/home/richard/FeedMob"
```

## Configuration

Read these values from environment variables:

```bash
# Example values
export OPENCODE_SERVER_URL=http://127.0.0.1:4096
export OPENCODE_SERVER_DIR=/home/richard/FeedMob

# Check values
printenv OPENCODE_SERVER_URL && printenv OPENCODE_SERVER_DIR
```

If either value is missing, ask the user to provide the missing value(s) before running commands. Never assume, infer, or hardcode `OPENCODE_SERVER_URL` or `OPENCODE_SERVER_DIR`.

Preflight requirement before any attached run:

1. Run `printenv OPENCODE_SERVER_URL && printenv OPENCODE_SERVER_DIR`.
2. If the command fails or a value is missing/empty, ask the user for the missing value(s).
3. Only proceed after both values are explicitly provided.
4. Check existing projects by running `opencode run --attach $OPENCODE_SERVER_URL 'pwd && ls -1d */ || true' --dir "$OPENCODE_SERVER_DIR"`, then list results for the user.
5. Create a new folder for new tasks by running `opencode run --attach $OPENCODE_SERVER_URL 'mkdir -p <task-folder>' --dir "$OPENCODE_SERVER_DIR"`.

## PTY Required

OpenCode is interactive. Always run with `pty:true`.

```bash
# Correct
bash pty:true command:"opencode run --attach $OPENCODE_SERVER_URL 'Explain async/await in JavaScript' --dir '$OPENCODE_SERVER_DIR'"

# Wrong (no PTY)
bash command:"opencode run --attach $OPENCODE_SERVER_URL 'Explain async/await in JavaScript' --dir '$OPENCODE_SERVER_DIR'"
```

## Server-Side Directory Rule

`--dir` is required by this skill and points to a path on the machine where `opencode server` is running.

- Do not treat `--dir` as a client/local path unless server and client are the same machine.
- Prefer absolute paths for `--dir`.
- The `workdir` field in bash does not replace `--dir` for attached OpenCode execution.

## One-Shot Usage

```bash
bash pty:true command:"opencode run --attach $OPENCODE_SERVER_URL 'Add error handling to API calls' --dir '$OPENCODE_SERVER_DIR'"
```

## Background Usage

```bash
# Start
bash pty:true background:true command:"opencode run --attach $OPENCODE_SERVER_URL 'Refactor auth module and run tests' --dir '$OPENCODE_SERVER_DIR'"

# Monitor
process action:log sessionId:XXX
process action:poll sessionId:XXX

# Respond if needed
process action:submit sessionId:XXX data:"yes"

# Stop
process action:kill sessionId:XXX
```

## Bash Tool Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| command | string | The shell command to run |
| pty | boolean | Use for coding agents! Allocates a pseudo-terminal for interactive CLIs |
| workdir | string | Working directory (agent sees only this folder's context) |
| background | boolean | Run in background, returns `sessionId` for monitoring |
| timeout | number | Timeout in seconds (kills process on expiry) |
| elevated | boolean | Run on host instead of sandbox (if allowed) |

## Process Tool Actions (for background sessions)

| Action | Description |
| --- | --- |
| list | List all running/recent sessions |
| poll | Check if session is still running |
| log | Get session output (with optional offset/limit) |
| write | Send raw data to stdin |
| submit | Send data + newline (like typing and pressing Enter) |
| send-keys | Send key tokens or hex bytes |
| paste | Paste text (with optional bracketed mode) |
| kill | Terminate the session |

## Rules

1. Always use `opencode run --attach`.
2. Always include `--dir`.
3. Always use `pty:true`.
4. Keep users updated when running background sessions (start, milestone, error, finish).
5. If a session hangs, inspect logs first, then restart or ask user for direction.
6. Never assume environment variable values; ask the user when missing.

## Troubleshooting

```bash
# Start server
opencode server --port 4096
```

- Connection issue: verify `OPENCODE_SERVER_URL` points to a live server.
- Path issue: verify `OPENCODE_SERVER_DIR` exists on the server machine.
- No output: confirm `pty:true` is set and check `process action:log`.
