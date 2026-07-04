# FeedMob Pixel CLI Reference

Use this reference when the core `SKILL.md` workflow does not contain enough command detail.

## Command Surface

`fpc` is the installed command for the `@feedmob/feedmob-pixel-cli` package.

```bash
fpc doctor
fpc init
fpc advertisers list
fpc tv-platforms list --advertiser <advertiser>
fpc categories list [filters]
fpc summary get [filters]
fpc records list <category> [filters]
fpc records export <category> [filters] --out <path>
fpc request get <path> --query key=value
fpc request head <path> --query key=value
```

Output is always JSON on stdout. The legacy `--json` flag is a no-op and is not needed.

## Install And Update

Recommend installing the published npm package first:

```bash
npm install -g @feedmob/feedmob-pixel-cli
command -v fpc
fpc --version
```

The npm package is `@feedmob/feedmob-pixel-cli`; the installed command is `fpc`.

Some npm versions hide successful install script output and only print `added packages`. If that happens, start with:

```bash
fpc --help
fpc doctor
```

`fpc` checks the latest npm version on each run and prints update notices to stderr.

Check whether the globally installed package is outdated:

```bash
fpc --version
npm outdated -g @feedmob/feedmob-pixel-cli
```

No output from `npm outdated` means the global install is current. If npm prints a row for `@feedmob/feedmob-pixel-cli`, update and confirm the installed version:

```bash
npm install -g @feedmob/feedmob-pixel-cli@latest
fpc --version
fpc doctor
```

To see the latest published version without comparing it to the installed version:

```bash
npm view @feedmob/feedmob-pixel-cli version
```

## Authentication And Config

Preferred local token setup:

```bash
mkdir -p ~/.fpc
chmod 700 ~/.fpc
printf '%s\n' 'FEEDMOB_PIXEL_API_TOKEN=fmpat_xxx' > ~/.fpc/.env
chmod 600 ~/.fpc/.env
fpc doctor
```

One-off shell setup:

```bash
export FEEDMOB_PIXEL_API_TOKEN='fmpat_xxx'
fpc doctor
```

Custom private env file:

```bash
FPC_ENV_FILE=/path/to/fpc.env fpc doctor
```

Supported token environment names are `FEEDMOB_PIXEL_API_TOKEN`, `FPC_TOKEN`, and `FEEDPIX_TOKEN`. Prefer `FEEDMOB_PIXEL_API_TOKEN` for new setup.

`fpc init --token <token>` stores the token in `~/.fpc/config.json`; avoid this unless explicitly requested.

## Setup Checks

`fpc doctor` reports setup status without printing the token:

```json
{
  "setup": {
    "ok": false,
    "missing": ["token"]
  }
}
```

If `setup.ok` is false:

- `missing` contains `token`: ask the user to configure a token privately.
- `checks.metadata.error.status` is `401`: report auth failure and ask for a valid Dashboard API token.
- network errors: report reachability failure and retry only if the user wants.

## Filters

Common filters:

```bash
--advertiser <value>
--event-type <value>
--tv <value>
--registration-date-mode auto|manual
--impression-start YYYY-MM-DD
--impression-end YYYY-MM-DD
--registration-start YYYY-MM-DD
--registration-end YYYY-MM-DD
--date-filter-mode and|or
--max-attribution-hours <hours>
```

Summary-specific options:

```bash
--attributed-per-page <number>
--attributed-max-pages <number>
```

## Date Modes

Use one date axis per command.

Use `--registration-date-mode auto` when the user explicitly provides impression dates and does not provide registration dates. Pass only impression dates and let the backend derive the registration date window.

```bash
fpc summary get \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --registration-date-mode auto \
  --impression-start 2026-06-01 \
  --impression-end 2026-06-30
```

Use `--registration-date-mode manual` whenever the user explicitly provides registration dates. Pass only registration dates; omit impression dates entirely. Registration dates take precedence if both date types appear in the request. Do not pass `false`; `fpc` supports `auto` and `manual`.

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

CLI flag to API query mapping:

| CLI flag | API query |
| --- | --- |
| `--event-type` | `eventType` |
| `--tv` | `tv` |
| `--registration-date-mode` | `registrationDateMode` |
| `--impression-start` | `impressionStartDate` |
| `--impression-end` | `impressionEndDate` |
| `--registration-start` | `registrationStartDate` |
| `--registration-end` | `registrationEndDate` |
| `--date-filter-mode` | `dateFilterMode` |
| `--max-attribution-hours` | `maxImpressionToRegistration` |
| `--per-page` | `perPage` |

## Discovery Commands

Advertisers:

```bash
fpc advertisers list
```

TV platforms:

```bash
fpc tv-platforms list --advertiser chime
```

Categories:

```bash
fpc categories list \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --registration-date-mode auto \
  --impression-start 2026-06-01 \
  --impression-end 2026-06-30
```

Use category `value` or `slug` for record commands. Respect `canViewDetails`.

## Summary And Records

Summary:

```bash
fpc summary get \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --registration-date-mode auto \
  --impression-start 2026-06-01 \
  --impression-end 2026-06-30
```

The summary JSON includes dashboard totals, category counts, `attributionWindow`, and an `attributed` object. `attributed.total` is the dashboard's Direct CTV attributed registration count: the sum of Direct CTV category counts such as `Direct - LG CTV` and `Direct - TCL CTV`. `attributed.records` contains records fetched from those Direct CTV categories.

Do not infer attributed categories from `assistedCount > 0`. `fpc` treats categories as Direct CTV when the slug matches `direct-*-ctv` or the name matches patterns like `Direct - LG CTV`. `assistedTotal` and `totalRegistrations` remain separate dashboard figures for assisted registrations and total registrations.

If `--max-attribution-hours` is omitted, `fpc` uses a 14-day attribution window (`336` hours). Explicit `--max-attribution-hours` values are reflected in `attributionWindow`.

By default, `summary get` fetches all attributed record pages with `--attributed-per-page 500`. Use `--attributed-max-pages` to limit how many record pages are fetched per attributed category:

```bash
fpc summary get \
  --advertiser chime \
  --event-type registration \
  --tv tcl-tv \
  --impression-start 2026-07-03 \
  --impression-end 2026-07-03 \
  --max-attribution-hours 72 \
  --attributed-max-pages 1
```

One records page:

```bash
fpc records list direct-lg-ctv \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --page 1 \
  --per-page 100
```

Multiple pages:

```bash
fpc records list direct-lg-ctv \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --all-pages \
  --max-pages 5
```

`--per-page` defaults to `100` and is capped at `500`.

## CSV Export

```bash
fpc records export direct-lg-ctv \
  --advertiser chime \
  --event-type registration \
  --tv lg-tv \
  --impression-start 2026-06-01 \
  --impression-end 2026-06-30 \
  --out ./direct-lg-ctv.csv
```

The command writes the CSV response to `--out` and prints metadata like:

```json
{
  "path": "/absolute/path/direct-lg-ctv.csv",
  "bytes": 123,
  "contentType": "text/csv"
}
```

## Raw Requests

Only use raw requests for read-only API coverage gaps.

```bash
fpc request get /api/v1/dashboard_api/summary \
  --query advertiser=chime \
  --query tv=lg-tv
```

```bash
fpc request head /api/v1/dashboard_api/advertisers
```

Paths must be relative to the configured base URL. The CLI normalizes common paths:

- `/api/...` becomes `/rails/api/...`
- `/dashboard_api/...` becomes `/rails/api/v1/dashboard_api/...`

## Error Shape

Errors are JSON:

```json
{
  "error": {
    "type": "auth_error",
    "message": "Unauthorized",
    "status": 401
  }
}
```

Handle errors by reporting the type, message, and status. Do not expose tokens or sensitive headers.
