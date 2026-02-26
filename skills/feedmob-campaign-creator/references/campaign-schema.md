# Campaign Data Structure Reference

Documentation of the campaign data structure and field specifications.

## Campaign Object

Complete campaign object structure returned by MCP tools.

```json
{
  "campaign_id": 789,
  "campaign_name": "Kraken_iOS_US_CPI_Jampp",
  "client_id": 123,
  "client_name": "Kraken",
  "client_uuid": "abc-def-ghi-jkl",
  "app_info_id": 456,
  "app_name": "Kraken iOS App",
  "platform": "iOS",
  "geo": "US",
  "partner": "Jampp",
  "payment_model": "CPI",
  "integration_type": "MMP",
  "status": "active",
  "created_at": "2024-02-10T12:00:00Z",
  "updated_at": "2024-02-10T12:00:00Z"
}
```

---

## Field Specifications

### Core Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `campaign_id` | number | Auto | Unique campaign identifier (generated on creation) | 789 |
| `campaign_name` | string | ✅ Yes | Standardized campaign name | `Kraken_iOS_US_CPI_Jampp` |
| `client_id` | number | ✅ Yes | Client identifier | 123 |
| `client_uuid` | string | ✅ Yes | Client UUID for API operations | `abc-def-ghi` |
| `app_info_id` | number | ✅ Yes | App identifier | 456 |

### Derived Fields

These fields are extracted from the campaign name or retrieved from related entities:

| Field | Type | Description | Extraction Source |
|-------|------|-------------|-------------------|
| `client_name` | string | Official client name | From `get_client` response |
| `app_name` | string | App display name | From `get_apps` response |
| `platform` | string | Target platform | From app metadata or campaign name |
| `geo` | string | Geographic region | From campaign name parsing |
| `partner` | string | Media partner name | From campaign name parsing |
| `payment_model` | string | Pricing model | From campaign name parsing |
| `integration_type` | string | Attribution method | From campaign name parsing (Agency suffix) |

### Status Fields

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `status` | string | Campaign status | `active`, `paused`, `archived` |
| `created_at` | timestamp | Creation timestamp | ISO 8601 format |
| `updated_at` | timestamp | Last update timestamp | ISO 8601 format |

---

## Campaign Name Format

The campaign name follows a strict standardized format:

### Format Variants

**Direct Integration (with Agency suffix):**
```
{Client}_{Platform}_{Geo}_{PaymentModel}_{Partner}_Agency
```

**MMP Integration (no Agency suffix):**
```
{Client}_{Platform}_{Geo}_{PaymentModel}_{Partner}
```

### Component Specifications

| Component | Description | Examples | Rules |
|-----------|-------------|----------|-------|
| Client | Client name | Kraken, Mistplay, Chime | No spaces, use company name |
| Platform | Target platform | iOS, Android, Web, CTV | Capitalization matters |
| Geo | Geographic code | US, UK, JP, CA, GLOBAL | ISO 2-letter codes or GLOBAL |
| PaymentModel | Pricing model | CPI, CPA, CPS, CPE, CPCV | Standard acronyms |
| Partner | Media partner | Jampp, Unity, Liftoff | No spaces in partner name |
| _Agency | Integration suffix | _Agency | Present ONLY for direct integration |

### Validation Rules

**Campaign Name Rules:**
1. Components separated by underscores `_`
2. No spaces allowed
3. Case-sensitive (use proper capitalization)
4. "_Agency" suffix only for direct integration
5. Must be unique across all campaigns

**Examples:**

✅ Valid:
- `Kraken_iOS_US_CPI_Jampp` (MMP integration)
- `Mistplay_Android_CA_CPA_Unity_Agency` (Direct integration)
- `Chime_Web_GLOBAL_CPS_Liftoff` (Web campaign, no Agency)

❌ Invalid:
- `kraken_ios_us_cpi_jampp` (wrong capitalization)
- `Kraken iOS US CPI Jampp` (spaces instead of underscores)
- `Kraken_iOS_US_CPI` (missing partner)
- `Kraken_iOS_US_CPI_Jampp_Agency` (Agency suffix on MMP integration)

---

## Platform Values

Supported platform values and their specifications:

| Platform | Value | App Identifier | Notes |
|----------|-------|----------------|-------|
| iOS | `iOS` | `bundle_id` | Apple App Store apps |
| Android | `Android` | `package_name` | Google Play apps |
| Web | `Web` | `domain` | Web applications |
| CTV | `CTV` | `app_id` | Connected TV apps |

**Case sensitivity:** Must use exact capitalization as shown above.

---

## Geo Codes

Geographic region codes following ISO 3166-1 alpha-2 standard:

| Region | Code | Full Name |
|--------|------|-----------|
| United States | `US` | United States |
| Canada | `CA` | Canada |
| United Kingdom | `UK` | United Kingdom |
| Japan | `JP` | Japan |
| Australia | `AU` | Australia |
| Germany | `DE` | Germany |
| France | `FR` | France |
| Global | `GLOBAL` | All regions |

**Note:** Use `GLOBAL` for campaigns targeting multiple regions.

---

## Payment Models

Standard payment model codes:

| Model | Code | Description | Paid Action Event |
|-------|------|-------------|-------------------|
| Cost Per Install | `CPI` | Pay per app install | `install` |
| Cost Per Action | `CPA` | Pay per conversion action | `purchase`, `signup`, etc. |
| Cost Per Sale | `CPS` | Pay per completed sale | `purchase` |
| Cost Per Engagement | `CPE` | Pay per engagement event | `level_complete`, etc. |
| Cost Per Completed View | `CPCV` | Pay per video view | `video_complete` |

---

## Integration Types

Two integration types supported:

### Direct Integration
- Campaign name includes `_Agency` suffix
- Attribution handled directly by FeedMob
- Example: `Kraken_iOS_US_CPI_Jampp_Agency`

### MMP Integration
- Campaign name does NOT include `_Agency` suffix
- Attribution handled by MMP (AppsFlyer, Adjust, etc.)
- Example: `Kraken_iOS_US_CPI_Jampp`

---

## Validation Rules

### Required Field Validation

All 4 core fields must be provided:
- ✅ `campaign_name`: Non-empty string, valid format
- ✅ `client_id`: Positive integer, must exist in system
- ✅ `client_uuid`: Valid UUID format
- ✅ `app_info_id`: Positive integer, must exist for client

### Business Logic Validation

1. **Uniqueness:** Campaign name must be unique across all campaigns
2. **Client-App Association:** `app_info_id` must belong to `client_id`
3. **Platform Consistency:** Platform in name must match app platform
4. **Name Format:** Must follow standardized naming convention

### Error Messages

| Validation Error | Error Message | Resolution |
|------------------|---------------|------------|
| Duplicate name | "Campaign name already exists" | Add suffix like `_v2` or `_2024` |
| Invalid client | "Client ID not found" | Verify client exists, re-run get_client |
| Invalid app | "App ID not found for client" | Verify app exists, re-run get_apps |
| Platform mismatch | "Platform in name doesn't match app platform" | Fix campaign name or select correct app |
| Invalid format | "Campaign name doesn't follow naming convention" | Regenerate name using naming skill |

---

## Example Campaigns

### Example 1: iOS MMP Campaign
```json
{
  "campaign_name": "Kraken_iOS_US_CPI_Jampp",
  "client_id": 123,
  "client_uuid": "abc-def-ghi",
  "app_info_id": 456,
  "platform": "iOS",
  "geo": "US",
  "payment_model": "CPI",
  "partner": "Jampp",
  "integration_type": "MMP"
}
```

### Example 2: Android Direct Campaign
```json
{
  "campaign_name": "Mistplay_Android_CA_CPA_Unity_Agency",
  "client_id": 234,
  "client_uuid": "xyz-abc-def",
  "app_info_id": 567,
  "platform": "Android",
  "geo": "CA",
  "payment_model": "CPA",
  "partner": "Unity",
  "integration_type": "Direct"
}
```

### Example 3: Web Global Campaign
```json
{
  "campaign_name": "Chime_Web_GLOBAL_CPS_Liftoff",
  "client_id": 345,
  "client_uuid": "def-ghi-jkl",
  "app_info_id": 678,
  "platform": "Web",
  "geo": "GLOBAL",
  "payment_model": "CPS",
  "partner": "Liftoff",
  "integration_type": "MMP"
}
```

---

## Data Flow

### Campaign Creation Data Flow

```
User Input
  ↓
Campaign Name Generation (feedmob-campaign-naming skill)
  ↓
Client Data Retrieval (get_client)
  ├─ client_id
  └─ client_uuid
  ↓
App Data Retrieval (get_apps)
  └─ app_info_id
  ↓
Campaign Preview (preview_campaign)
  ├─ Validate all fields
  ├─ Check uniqueness
  └─ Verify associations
  ↓
Campaign Creation (create_campaign)
  └─ campaign_id (generated)
```

### Data Dependencies

```
campaign_name ← feedmob-campaign-naming skill
client_id, client_uuid ← get_client(client_name)
app_info_id ← get_apps(client_id) + user selection
campaign_id ← create_campaign(all above)
```

---

## Best Practices

1. **Always use feedmob-campaign-naming skill** to generate campaign names
2. **Validate platform consistency** between name and selected app
3. **Confirm preview with user** before creating campaign
4. **Handle duplicate names gracefully** by suggesting modifications
5. **Preserve data types** - IDs are numbers, not strings
6. **Display all extracted data** to user for verification
