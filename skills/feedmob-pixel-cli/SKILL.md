---
name: feedmob-pixel-cli
description: Use when an AI agent needs to query FeedMob Pixel Dashboard data with the `fpc` / feedmob-pixel-cli command, including setup checks, advertiser/event type/TV/category discovery, dashboard summaries, Direct CTV attributed registration interpretation, category records, CSV exports, or read-only raw Dashboard API GET/HEAD requests. Use for FeedMob Pixel Dashboard API work where valid values must be discovered first and tokens must not be exposed.
---

# FeedMob Pixel CLI

## Overview

Use the installed `fpc` command as the safe read-only interface to the FeedMob Pixel Dashboard API. The CLI prints JSON to stdout by default, sends diagnostics to stderr, and can export category records to CSV.

For command details and less-common options, read [references/cli-reference.md](references/cli-reference.md).

## Compatibility

This skill is agent-neutral. Claude Code, Codex, and other Agent Skills-compatible runtimes should use this `SKILL.md` plus the linked `references/` files. The `agents/openai.yaml` file is optional UI metadata for OpenAI/Codex surfaces; Claude Code can ignore it.

## Start

Verify the command first:

```bash
command -v fpc
```

If `fpc` is missing on this machine, recommend the npm package install:

```bash
npm install -g @feedmob/feedmob-pixel-cli
command -v fpc
fpc --version
```

If npm only prints `added packages`, continue with `fpc --help` or `fpc doctor`.

Then check setup:

```bash
fpc doctor
```

If `doctor` reports missing setup, ask the user to provide a Dashboard API token through a local environment variable or private env file:

```bash
export FEEDMOB_PIXEL_API_TOKEN='fmpat_xxx'
```

For persistent local setup, prefer `~/.fpc/.env` with mode `600`, or point `FPC_ENV_FILE` at a private env file. Avoid `fpc init --token` unless the user explicitly wants a token stored in `~/.fpc/config.json`.

Never print, log, paste, commit, or screenshot tokens. Do not store production payloads, cookies, or sensitive headers in repos, fixtures, or logs.

## Discovery-First Flow

Do not invent advertiser, event type, TV platform, or category values. Discover them in order:

```bash
fpc advertisers list
fpc tv-platforms list --advertiser chime
fpc categories list \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --registration-date-mode auto \
  --impression-start 2026-06-01 \
  --impression-end 2026-06-30
```

Use `category.value` or `category.slug` from `categories list` for records and exports. Only drill into categories where `canViewDetails` is `true`.

## Read Data

Use `summary get` for totals, category breakdowns, the current attribution window, and Direct CTV attributed registration records:

```bash
fpc summary get \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --registration-date-mode auto \
  --impression-start 2026-06-01 \
  --impression-end 2026-06-30
```

Summary output includes `attributionWindow` and an `attributed` object. `attributed.total` is the sum of Direct CTV category counts, such as `Direct - LG CTV` and `Direct - TCL CTV`; `attributed.records` contains records fetched from those Direct CTV categories. Do not treat `attributed.total` as `assistedTotal`: dashboard assisted and total registration figures remain `assistedTotal` and `totalRegistrations`.

If `--max-attribution-hours` is omitted, `fpc` uses 14 days (`336` hours). For broad summary reads, cap attributed record fetching with `--attributed-max-pages N`.

Use `records list` for category drill-down:

```bash
fpc records list direct-lg-ctv \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --page 1 \
  --per-page 100
```

For broader reads, add `--all-pages --max-pages N`. Keep `--per-page` at or below `500`.

## Export CSV

Export only when the user asks for a file or offline analysis:

```bash
fpc records export direct-lg-ctv \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --impression-start 2026-06-01 \
  --impression-end 2026-06-30 \
  --out ./direct-lg-ctv.csv
```

The export command writes CSV to `--out` and prints JSON file metadata to stdout.

## Raw Escape Hatch

Use raw requests only when high-level commands do not cover the read:

```bash
fpc request get /api/v1/dashboard_api/summary \
  --query advertiser=chime \
  --query tv=lg-tv
```

Raw requests are limited to `GET` and `HEAD`. Do not attempt POST, PUT, PATCH, or DELETE workflows with this CLI.

## Date Rules

Use one date axis per command.

When the user explicitly provides impression dates and does not provide registration dates, set `--registration-date-mode auto`, pass only impression start/end dates, and let the backend derive the registration date window.

When the user explicitly provides registration dates, set `--registration-date-mode manual` and omit impression dates entirely. Registration dates take precedence if both date types appear in the request. Do not pass `false`; in `fpc`, `manual` is the supported way to disable auto-linking:

```bash
fpc summary get \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --registration-date-mode manual \
  --registration-start 2026-06-01 \
  --registration-end 2026-06-30
```

Do not combine `--impression-start/--impression-end` with `--registration-start/--registration-end` in normal agent workflows. Do not use `--date-filter-mode` unless the user explicitly asks for a low-level API experiment.

## Safety Rules

- Treat stdout as JSON and parse it with structured tools when possible.
- Send progress and diagnostics to stderr if wrapping commands.
- Do not query the database for Pixel Dashboard API data when `fpc` can read it.
- Do not create, revoke, rotate, or manage API tokens with this CLI.
- Do not expose the `_request.url` if it contains sensitive query context the user did not ask to see.
- Prefer discovered values over user-provided guesses; if a value is missing, run discovery again.
