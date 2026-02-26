# Campaign Creation Workflow Guide

Step-by-step guide for the complete campaign creation process.

## Workflow Overview

```
User Request → Gather Info → Name Campaign → Get Client → Get App → Preview → Create → Success
```

---

## Step 1: Gather Requirements & Generate Campaign Name

### Required Information

Collect from user (or infer from request):

| Field | Description | Examples |
|-------|-------------|----------|
| Client Name | Official client name | Kraken, Mistplay, Chime |
| Platform | Target platform | iOS, Android, Web, CTV |
| Geo | Geographic region | US, UK, JP, GLOBAL |
| Partner Name | Media partner name | Jampp, Unity, Liftoff |
| Payment Model | Pricing model | CPI, CPA, CPS, CPE |
| Integration Type | Attribution method | Direct, MMP |
| Paid Action | Conversion event | install, purchase, signup |

### Auto-Invoke Naming Skill

**Action:** Automatically invoke the feedmob-campaign-naming skill

**Process:**
1. Pass all gathered information to naming skill
2. Naming skill generates standardized name
3. Display generated name to user
4. Allow user to request regeneration if needed

**Example:**
```
Input: Client=Kraken, Platform=iOS, Geo=US, Partner=Jampp, PaymentModel=CPI, Integration=MMP
Output: Kraken_iOS_US_CPI_Jampp
Display: "Generated campaign name: Kraken_iOS_US_CPI_Jampp"
```

**Name Format Rules (from naming skill):**
- Direct integration: `{Client}_{Platform}_{Geo}_{PaymentModel}_{Partner}_Agency`
- MMP integration: `{Client}_{Platform}_{Geo}_{PaymentModel}_{Partner}` (no "_Agency")

---

## Step 2: Retrieve Client Data

### Call MCP Tool

```
mcp__feedmob-reporting__get_client(client_name="Kraken")
```

### Process Response

**Success response:**
```json
{
  "client_id": 123,
  "client_uuid": "abc-def-ghi",
  "client_name": "Kraken",
  "status": "active"
}
```

**Extract:**
- `client_id`: 123
- `client_uuid`: "abc-def-ghi"

**Display:**
```
✅ Found client: Kraken
   ID: 123
   UUID: abc-def-ghi
```

### Error Handling

**Error: Client not found**
```
❌ Client "KrakenXYZ" not found.

Please verify the client name. Did you mean:
- Kraken
- Kraken Technologies

Which client should I use?
```

---

## Step 3: Retrieve App Data

### Call MCP Tool

```
mcp__feedmob-reporting__get_apps(client_id=123)
```

### Process Response

**Response:**
```json
[
  {
    "app_info_id": 456,
    "app_name": "Kraken iOS App",
    "platform": "iOS",
    "bundle_id": "com.kraken.app"
  },
  {
    "app_info_id": 789,
    "app_name": "Kraken Android App",
    "platform": "Android",
    "package_name": "com.kraken.app"
  }
]
```

### Selection Logic

**Case A: Single app matches platform**
```
Campaign platform: iOS
Available apps: [{"app_info_id": 456, "platform": "iOS"}]

Action: Auto-select
Display: "✅ Selected app: Kraken iOS App (ID: 456)"
```

**Case B: Multiple apps match platform**
```
Campaign platform: iOS
Available apps: [
  {"app_info_id": 456, "app_name": "Kraken iOS (US)", "platform": "iOS"},
  {"app_info_id": 457, "app_name": "Kraken iOS (EU)", "platform": "iOS"}
]

Display:
| # | App Name | Platform | App Info ID |
|---|----------|----------|-------------|
| 1 | Kraken iOS (US) | iOS | 456 |
| 2 | Kraken iOS (EU) | iOS | 457 |

Ask: "Which app should I use? (enter number)"
```

**Case C: No apps match platform**
```
Campaign platform: iOS
Available apps: [{"platform": "Android"}]

Display:
"❌ No iOS apps found for Kraken.
   Available platforms: Android

   Would you like to:
   1. Create campaign for Android instead
   2. Contact admin to add iOS app"
```

---

## Step 4: Preview Campaign

### Call MCP Tool

```
mcp__feedmob-reporting__preview_campaign(
  campaign_name="Kraken_iOS_US_CPI_Jampp",
  client_id=123,
  client_uuid="abc-def-ghi",
  app_info_id=456
)
```

### Process Response

**Success response:**
```json
{
  "valid": true,
  "preview": {
    "campaign_name": "Kraken_iOS_US_CPI_Jampp",
    "client_id": 123,
    "client_name": "Kraken",
    "app_info_id": 456,
    "app_name": "Kraken iOS App",
    "platform": "iOS",
    "geo": "US",
    "payment_model": "CPI",
    "partner": "Jampp"
  },
  "validation_messages": []
}
```

### Display Preview

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Campaign Preview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Campaign Name: Kraken_iOS_US_CPI_Jampp

Client Information:
├─ Name: Kraken
├─ ID: 123
└─ UUID: abc-def-ghi

App Information:
├─ Name: Kraken iOS App
├─ ID: 456
└─ Platform: iOS

Campaign Details:
├─ Geo: US
├─ Partner: Jampp
├─ Payment Model: CPI
└─ Integration: MMP

Validation: ✅ All checks passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Does this look correct? (yes/no)
```

### Validation Errors

**If validation fails:**
```json
{
  "valid": false,
  "validation_messages": [
    "Campaign name 'Kraken_iOS_US_CPI_Jampp' already exists",
    "Invalid geo code 'USA' (must be 2-letter ISO code)"
  ]
}
```

**Display:**
```
❌ Validation Errors:
   1. Campaign name already exists
   2. Invalid geo code 'USA' (use 'US' instead)

Would you like to:
1. Modify campaign name (add suffix like '_v2')
2. Use different geo code
3. Cancel campaign creation
```

---

## Step 5: Create Campaign

### Call MCP Tool (after user confirms)

```
mcp__feedmob-reporting__create_campaign(
  campaign_name="Kraken_iOS_US_CPI_Jampp",
  client_id=123,
  client_uuid="abc-def-ghi",
  app_info_id=456
)
```

### Process Response

**Success response:**
```json
{
  "success": true,
  "campaign_id": 789,
  "campaign": {
    "campaign_id": 789,
    "campaign_name": "Kraken_iOS_US_CPI_Jampp",
    "status": "active",
    "created_at": "2024-02-10T12:00:00Z"
  },
  "message": "Campaign created successfully"
}
```

### Display Success

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Campaign Created Successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Campaign ID: 789
Name: Kraken_iOS_US_CPI_Jampp
Status: Active
Created: 2024-02-10 12:00:00 UTC

Next Steps:
1. Generate tracking links
2. Set up attribution mapping
3. Configure partner integration
4. Test tracking implementation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Error Handling

**Duplicate campaign error:**
```
❌ Campaign creation failed
   Error: Campaign name 'Kraken_iOS_US_CPI_Jampp' already exists

Suggested solution:
Add a suffix to make it unique:
- Kraken_iOS_US_CPI_Jampp_v2
- Kraken_iOS_US_CPI_Jampp_2024

Would you like me to try with a different name?
```

---

## Complete End-to-End Example

### User Request
> "Create a campaign for Mistplay Android in Canada, partner Unity pays on purchase, direct integration"

### Execution

**Step 1: Generate Name**
```
Invoke: feedmob-campaign-naming skill
Input: Client=Mistplay, Platform=Android, Geo=CA, Partner=Unity, PaymentModel=CPA, Integration=Direct
Output: Mistplay_Android_CA_CPA_Unity_Agency
Display: "Generated campaign name: Mistplay_Android_CA_CPA_Unity_Agency"
```

**Step 2: Get Client**
```
Call: get_client(client_name="Mistplay")
Response: {client_id: 234, client_uuid: "xyz-abc-def"}
Display: "✅ Found client: Mistplay (ID: 234)"
```

**Step 3: Get Apps**
```
Call: get_apps(client_id=234)
Response: [
  {app_info_id: 567, app_name: "Mistplay Android App", platform: "Android"}
]
Display: "✅ Selected app: Mistplay Android App (ID: 567)"
```

**Step 4: Preview**
```
Call: preview_campaign("Mistplay_Android_CA_CPA_Unity_Agency", 234, "xyz-abc-def", 567)
Response: {valid: true, preview: {...}}
Display preview, ask for confirmation
User: "yes"
```

**Step 5: Create**
```
Call: create_campaign("Mistplay_Android_CA_CPA_Unity_Agency", 234, "xyz-abc-def", 567)
Response: {success: true, campaign_id: 890}
Display: "✅ Campaign created successfully! Campaign ID: 890"
```

---

## Decision Trees

### Multi-App Selection
```
get_apps returns multiple apps for platform
  ↓
Filter by platform from campaign name
  ↓
Count matches
  ├─ 1 match → Auto-select
  ├─ 2+ matches → Display table, ask user
  └─ 0 matches → Display error, suggest alternatives
```

### Error Recovery
```
Tool call fails
  ↓
Identify error type
  ├─ Not found → Ask user to verify input
  ├─ Validation error → Display issues, ask for corrections
  ├─ Duplicate → Suggest name modification
  └─ API error → Retry once, then escalate
```

### User Confirmation
```
preview_campaign shows preview
  ↓
Ask: "Does this look correct?"
  ├─ "yes" → Proceed to create_campaign
  ├─ "no" → Ask what to change, restart from appropriate step
  └─ unclear → Re-display preview, ask again
```
