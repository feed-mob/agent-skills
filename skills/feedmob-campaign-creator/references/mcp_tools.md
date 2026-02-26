# MCP Tools Reference

Complete API documentation for the 4 FeedMob admin MCP tools used in campaign creation workflow.

All tools use the prefix: `mcp__feedmob-reporting__*`

---

## Tool 1: Get Client Information

**Tool Name:** `mcp__feedmob-reporting__get_client`

**Purpose:** Retrieve client metadata including client_id and client_uuid required for campaign creation.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_name` | string | ✅ Yes | Exact or partial client name (case-insensitive search) |

### Returns

```json
{
  "client_id": 123,
  "client_uuid": "abc-def-ghi-jkl",
  "client_name": "Kraken",
  "status": "active",
  "created_at": "2024-01-15T00:00:00Z",
  ...
}
```

**Key fields:**
- `client_id` (number) - Required for subsequent tool calls
- `client_uuid` (string) - Required for campaign creation
- `client_name` (string) - Official client name

### Error Cases

| Error | Cause | Solution |
|-------|-------|----------|
| Client not found | Invalid or misspelled client name | Ask user to verify spelling, suggest partial match search |
| Multiple matches | Ambiguous client name | Display list of matches, ask user to select |
| API error | Service unavailable | Retry after a moment, inform user of issue |

### Example Usage

```
Input: mcp__feedmob-reporting__get_client(client_name="Kraken")

Output:
{
  "client_id": 123,
  "client_uuid": "abc-def-ghi",
  "client_name": "Kraken"
}

Extract:
- client_id: 123
- client_uuid: "abc-def-ghi"
```

---

## Tool 2: Get App Information

**Tool Name:** `mcp__feedmob-reporting__get_apps`

**Purpose:** Retrieve all apps for a client to select the correct app_info_id for campaign.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | number | ✅ Yes | Client ID from get_client response |

### Returns

```json
[
  {
    "app_info_id": 456,
    "app_name": "Kraken iOS App",
    "platform": "iOS",
    "bundle_id": "com.kraken.app",
    "status": "active",
    ...
  },
  {
    "app_info_id": 789,
    "app_name": "Kraken Android App",
    "platform": "Android",
    "package_name": "com.kraken.app",
    "status": "active",
    ...
  }
]
```

**Key fields:**
- `app_info_id` (number) - Required for campaign creation
- `app_name` (string) - Display name of the app
- `platform` (string) - iOS, Android, Web, or CTV

### Selection Logic

**Case 1: Single app matches platform**
```
User wants: iOS campaign
Apps returned: [{app_info_id: 456, platform: "iOS"}]
Action: Auto-select app_info_id: 456
```

**Case 2: Multiple apps match platform**
```
User wants: iOS campaign
Apps returned: [
  {app_info_id: 456, app_name: "Kraken iOS (US)", platform: "iOS"},
  {app_info_id: 457, app_name: "Kraken iOS (EU)", platform: "iOS"}
]
Action: Display table, ask user to select
```

**Case 3: No apps match platform**
```
User wants: iOS campaign
Apps returned: [{platform: "Android"}]
Action: Inform user no iOS app found, suggest checking client configuration
```

### Error Cases

| Error | Cause | Solution |
|-------|-------|----------|
| No apps found | Client has no apps configured | Inform user, suggest contacting admin to add apps |
| Invalid client_id | Client doesn't exist | Verify client_id from get_client step |
| API error | Service unavailable | Retry, inform user |

### Example Usage

```
Input: mcp__feedmob-reporting__get_apps(client_id=123)

Output:
[
  {
    "app_info_id": 456,
    "app_name": "Kraken iOS App",
    "platform": "iOS"
  },
  {
    "app_info_id": 789,
    "app_name": "Kraken Android App",
    "platform": "Android"
  }
]

Filter by platform (iOS):
Selected: app_info_id: 456
```

---

## Tool 3: Preview Campaign

**Tool Name:** `mcp__feedmob-reporting__preview_campaign`

**Purpose:** Validate campaign configuration and show preview before actual creation.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `campaign_name` | string | ✅ Yes | Standardized campaign name from naming skill |
| `client_id` | number | ✅ Yes | From get_client response |
| `client_uuid` | string | ✅ Yes | From get_client response |
| `app_info_id` | number | ✅ Yes | From get_apps response |

### Returns

```json
{
  "valid": true,
  "preview": {
    "campaign_name": "Kraken_iOS_US_CPI_Jampp",
    "client_id": 123,
    "client_name": "Kraken",
    "client_uuid": "abc-def-ghi",
    "app_info_id": 456,
    "app_name": "Kraken iOS App",
    "platform": "iOS",
    "geo": "US",
    "payment_model": "CPI",
    "partner": "Jampp",
    "integration_type": "MMP"
  },
  "validation_messages": []
}
```

**If validation fails:**
```json
{
  "valid": false,
  "preview": {...},
  "validation_messages": [
    "Campaign name already exists",
    "Invalid geo code format"
  ]
}
```

### Display Format

```
Campaign Preview:
├─ Name: Kraken_iOS_US_CPI_Jampp
├─ Client: Kraken (ID: 123)
├─ App: Kraken iOS App (ID: 456)
├─ Platform: iOS
├─ Geo: US
├─ Partner: Jampp
├─ Payment Model: CPI
└─ Integration: MMP

Validation: ✅ All checks passed

Does this look correct? (yes/no)
```

### Error Cases

| Error | Cause | Solution |
|-------|-------|----------|
| Campaign name exists | Duplicate name | Modify campaign name, add suffix like "_v2" |
| Invalid parameters | Missing or wrong type | Review all parameters, ensure correct types |
| Validation errors | Business rule violations | Display validation messages, ask user for corrections |
| API error | Service unavailable | Retry, inform user |

### Example Usage

```
Input: mcp__feedmob-reporting__preview_campaign(
  campaign_name="Kraken_iOS_US_CPI_Jampp",
  client_id=123,
  client_uuid="abc-def-ghi",
  app_info_id=456
)

Output:
{
  "valid": true,
  "preview": {
    "campaign_name": "Kraken_iOS_US_CPI_Jampp",
    "client_name": "Kraken",
    "app_name": "Kraken iOS App",
    "platform": "iOS"
  }
}

Display preview, wait for user confirmation.
```

---

## Tool 4: Create Campaign

**Tool Name:** `mcp__feedmob-reporting__create_campaign`

**Purpose:** Create the campaign in the FeedMob system after user confirms preview.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `campaign_name` | string | ✅ Yes | Standardized campaign name from naming skill |
| `client_id` | number | ✅ Yes | From get_client response |
| `client_uuid` | string | ✅ Yes | From get_client response |
| `app_info_id` | number | ✅ Yes | From get_apps response |

### Returns

```json
{
  "success": true,
  "campaign_id": 789,
  "campaign": {
    "campaign_id": 789,
    "campaign_name": "Kraken_iOS_US_CPI_Jampp",
    "client_id": 123,
    "app_info_id": 456,
    "status": "active",
    "created_at": "2024-02-10T12:00:00Z",
    ...
  },
  "message": "Campaign created successfully"
}
```

**Key fields:**
- `campaign_id` (number) - Unique identifier for the created campaign
- `success` (boolean) - Creation status
- `message` (string) - Success or error message

### Display Format

```
✅ Campaign created successfully!

Campaign Details:
├─ ID: 789
├─ Name: Kraken_iOS_US_CPI_Jampp
├─ Client: Kraken (ID: 123)
├─ App: Kraken iOS App (ID: 456)
└─ Status: Active

Next Steps:
1. Generate tracking links
2. Set up attribution mapping
3. Configure partner integration
4. Test tracking implementation
```

### Error Cases

| Error | Cause | Solution |
|-------|-------|----------|
| Duplicate campaign | Name already exists | Use different campaign name or add suffix |
| Invalid parameters | Wrong data types or missing fields | Review all parameters from previous steps |
| Permission denied | User lacks create permissions | Contact admin for permissions |
| API error | Service unavailable | Retry, inform user, escalate if persistent |

### Example Usage

```
Input: mcp__feedmob-reporting__create_campaign(
  campaign_name="Kraken_iOS_US_CPI_Jampp",
  client_id=123,
  client_uuid="abc-def-ghi",
  app_info_id=456
)

Output:
{
  "success": true,
  "campaign_id": 789,
  "message": "Campaign created successfully"
}

Display success message with campaign_id.
```

---

## Tool Call Sequence

The tools must be called in this exact order:

```
1. get_client(client_name)
   ↓
   Extract: client_id, client_uuid

2. get_apps(client_id)
   ↓
   Extract: app_info_id

3. preview_campaign(campaign_name, client_id, client_uuid, app_info_id)
   ↓
   Validate and display preview

4. create_campaign(campaign_name, client_id, client_uuid, app_info_id)
   ↓
   Return campaign_id
```

**Dependencies:**
- Step 2 depends on client_id from Step 1
- Step 3 depends on all data from Steps 1 & 2
- Step 4 depends on user confirmation of Step 3

**No parallel execution possible** - all steps are sequential.

---

## Best Practices

1. **Always validate responses** - Check for required fields before proceeding
2. **Display raw data** - Show what you receive from each tool call
3. **Extract explicitly** - Clearly state which values you're extracting
4. **Confirm with user** - Ask for approval at preview step
5. **Handle errors gracefully** - Provide clear messages and solutions
6. **Never assume** - Always get data from tools, never fabricate values

---

## Common Workflows

### Scenario 1: Standard Campaign Creation
```
get_client("Kraken")
  → client_id: 123, client_uuid: "abc-def"

get_apps(123)
  → [{app_info_id: 456, platform: "iOS"}]
  → Auto-select iOS app

preview_campaign("Kraken_iOS_US_CPI_Jampp", 123, "abc-def", 456)
  → Show preview, user confirms

create_campaign("Kraken_iOS_US_CPI_Jampp", 123, "abc-def", 456)
  → campaign_id: 789 ✅
```

### Scenario 2: Multiple Apps - User Selection
```
get_client("Mistplay")
  → client_id: 234, client_uuid: "xyz-abc"

get_apps(234)
  → [
      {app_info_id: 567, app_name: "Mistplay iOS (US)", platform: "iOS"},
      {app_info_id: 568, app_name: "Mistplay iOS (CA)", platform: "iOS"}
    ]
  → Display table, ask user to select
  → User selects: 567

preview_campaign("Mistplay_iOS_US_CPI_Unity", 234, "xyz-abc", 567)
  → Show preview, user confirms

create_campaign("Mistplay_iOS_US_CPI_Unity", 234, "xyz-abc", 567)
  → campaign_id: 890 ✅
```

### Scenario 3: Error Handling
```
get_client("Nonexistent Client")
  → Error: Client not found
  → Ask user to verify name
  → User corrects: "Chime"

get_client("Chime")
  → client_id: 345, client_uuid: "def-ghi"
  → Continue workflow...
```
