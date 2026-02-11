---
name: feedmob-campaign-creator
description: |
  Create FeedMob campaigns with guided workflow. Use when users request campaign creation,
  link generation, or new partner launches. Handles: (1) Campaign naming via feedmob-campaign-naming,
  (2) Client data retrieval, (3) App selection, (4) Campaign preview, (5) Campaign creation.
  Trigger keywords: create campaign, new campaign, generate campaign, campaign setup, link generation,
  partner launch, media plan campaign, 创建campaign, 生成活动, 新建campaign.
---

# FeedMob Campaign Creator

Create FeedMob campaigns through a guided 5-step workflow that ensures correct configuration and naming conventions.

## Overview

This skill orchestrates the complete campaign creation process:

```
User Request
    ↓
1. Campaign Naming (auto-invoke feedmob-campaign-naming skill)
    ↓
2. Get Client Data (client_id, client_uuid)
    ↓
3. Get App Data (app_info_id)
    ↓
4. Preview Campaign (validate before creation)
    ↓
5. Create Campaign (if user confirms)
    ↓
Campaign Created ✅
```

## Quick Start

**Simplest case:**
```
User: "Create a campaign for Kraken iOS in US, partner Jampp pays on install, integrated via AppsFlyer MMP"

Steps:
1. Auto-invoke feedmob-campaign-naming skill
2. Call get_client with client_name="Kraken"
3. Call get_apps with client_id from step 2
4. Call preview_campaign with all data
5. Show preview, ask user to confirm
6. Call create_campaign if confirmed
```

## Workflow Steps

### Step 1: Campaign Naming

**Automatically invoke feedmob-campaign-naming skill** to generate standardized campaign name.

Required information to gather:
- Client name
- Platform (iOS, Android, Web, CTV)
- Geo (US, UK, JP, etc.)
- Partner name
- Payment model (CPI, CPA, CPS, etc.)
- Integration type (Direct vs MMP)
- Paid action type (install, purchase, signup, etc.)

Display generated name to user for confirmation. User can request regeneration if needed.

### Step 2: Retrieve Client Data

Call MCP tool to get client information:

```
mcp__feedmob-reporting__get_clients
Parameters:
  - client_name: string (required)
```

**Extract these 2 values from response:**
- `client_id` (number) - Required for Steps 3, 4, 5
- `client_uuid` (string) - Required for Steps 4, 5

**Error handling:** If client not found, ask user to verify client name.

### Step 3: Retrieve App Data

Call MCP tool to get app information:

```
mcp__feedmob-reporting__get_apps
Parameters:
  - client_id: number (required) - from Step 2
```

Display available apps to user in a table format:

| App Name | Platform | App Info ID |
|----------|----------|-------------|
| Kraken iOS App | iOS | 456 |
| Kraken Android App | Android | 789 |

**Selection logic:**
- If only one app matches the platform → auto-select
- If multiple apps match → ask user to select

**Extract these 2 values from selected app:**
- `app_info_id` (number) - Required for Steps 4, 5
- `os` (string) - Platform value (iOS/Android/Web/CTV) - Required for Steps 4, 5

### Step 4: Preview Campaign

Before previewing, ask user for the **agency** parameter:

```
Is this an agency campaign?
- true (Agency campaign - MMP integration, name has "_Agency" suffix)
- false (Direct campaign - Direct integration, no "_Agency" suffix)
```

**Important:** Verify the campaign name from Step 1 matches the agency selection:
- If `agency=true`: Campaign name must end with `_Agency`
- If `agency=false`: Campaign name should NOT have `_Agency` suffix

Wait for user to provide this value.

Call MCP tool to preview campaign configuration.

**CRITICAL: All 6 parameters are REQUIRED for preview_campaign to work:**

```
mcp__feedmob-reporting__preview_campaign
Parameters (ALL REQUIRED):
  1. campaign_name: string - from Step 1 (e.g., "TextNow_iOS_UK_CPA_Jampp_Agency")
  2. client_id: number - from Step 2 get_clients response (e.g., 86)
  3. client_uuid: string - from Step 2 get_clients response (e.g., "feb2e0857d9f4f8681033abeb79b212e")
  4. app_info_id: number - from Step 3 get_apps response (e.g., 463)
  5. os: string - MUST be one of: "iOS", "Android", "Web", "CTV"
  6. agency: boolean - true (MMP integration, name has "_Agency"), false (Direct integration, no "_Agency")
```

**Parameter Checklist - Verify ALL 6 before calling:**
- ✅ campaign_name: string from Step 1
- ✅ client_id: number from Step 2
- ✅ client_uuid: string from Step 2
- ✅ app_info_id: number from Step 3
- ✅ os: string (iOS/Android/Web/CTV)
- ✅ agency: boolean (true/false) - from user input (true=MMP/Agency, false=Direct)

**Example call:**
```
mcp__feedmob-reporting__preview_campaign(
  campaign_name="TextNow_iOS_UK_CPA_Jampp_Agency",
  client_id=86,
  client_uuid="feb2e0857d9f4f8681033abeb79b212e",
  app_info_id=463,
  os="iOS",
  agency=true
)
```

**If preview succeeds:**
Display the preview data returned by the API.

**If preview fails:**
Display manual preview using collected data:
```
Campaign Preview:
├─ Campaign Name: [campaign_name from Step 1]
├─ Client: [client_name] (ID: [client_id])
├─ Client UUID: [client_uuid]
├─ App: [app_name] (App Info ID: [app_info_id])
├─ Platform: [os]
├─ Agency: [agency] ([integration type: "MMP Integration" if true, "Direct Integration" if false])
└─ Status: Ready to create

Proceed to create campaign? (yes/no)
```

Wait for user confirmation before proceeding to Step 5.

### Step 5: Create Campaign

If user confirms, call MCP tool to create campaign.

**CRITICAL: All 6 parameters are REQUIRED for create_campaign to work:**

```
mcp__feedmob-reporting__create_campaign
Parameters (ALL REQUIRED):
  1. campaign_name: string - from Step 1 (e.g., "TextNow_iOS_UK_CPA_Jampp_Agency")
  2. client_id: number - from Step 2 get_clients response (e.g., 86)
  3. client_uuid: string - from Step 2 get_clients response (e.g., "feb2e0857d9f4f8681033abeb79b212e")
  4. app_info_id: number - from Step 3 get_apps response (e.g., 463)
  5. os: string - MUST be one of: "iOS", "Android", "Web", "CTV"
  6. agency: boolean - true (MMP integration, name has "_Agency"), false (Direct integration, no "_Agency")
```

**Parameter Checklist - Verify ALL 6 before calling:**
- ✅ campaign_name: string from Step 1
- ✅ client_id: number from Step 2
- ✅ client_uuid: string from Step 2
- ✅ app_info_id: number from Step 3
- ✅ os: string (iOS/Android/Web/CTV)
- ✅ agency: boolean (true/false) - from user input (true=MMP/Agency, false=Direct) in Step 4

**Example call:**
```
mcp__feedmob-reporting__create_campaign(
  campaign_name="TextNow_iOS_UK_CPA_Jampp_Agency",
  client_id=86,
  client_uuid="feb2e0857d9f4f8681033abeb79b212e",
  app_info_id=463,
  os="iOS",
  agency=true
)
```

Display success message:

```
✅ Campaign created successfully!
Campaign ID: 4845
Campaign UUID: 6fbed37183cd494e96baaec9999677d9
Campaign Name: TextNow_iOS_UK_CPA_Jampp_Agency
Integration Type: MMP Integration (Agency=true)

Next steps:
- Generate tracking links
- Set up attribution
- Configure partner integration
```

## MCP Tool Reference

All tools use prefix: `mcp__feedmob-reporting__*`

| Tool | Parameters (ALL REQUIRED) | Returns |
|------|-----------|---------|
| `get_clients` | `client_name` (string) | `client_id`, `client_uuid`, metadata |
| `get_apps` | `client_id` (number) | Array of apps with `app_info_id`, `app_name`, `os` |
| `preview_campaign` | `campaign_name` (string), `client_id` (number), `client_uuid` (string), `app_info_id` (number), `os` (string), `agency` (boolean) | Preview object with validation |
| `create_campaign` | `campaign_name` (string), `client_id` (number), `client_uuid` (string), `app_info_id` (number), `os` (string), `agency` (boolean) | `campaign_id`, `campaign_uuid`, created object |

## Error Handling

| Error | Solution |
|-------|----------|
| Client not found | Ask user to verify client name, suggest similar clients if available |
| No apps found | Verify client has apps configured, check platform spelling |
| Multiple apps match | Display list and ask user to select |
| Preview validation fails | Display errors, ask user for corrections |
| Creation fails | Display error message, suggest troubleshooting steps |

## Complete Example

**User Request:**
> "Create a campaign for Kraken iOS in US, partner Jampp pays on install, integrated via AppsFlyer MMP"

**Execution:**

**Step 1: Generate Campaign Name**
- Auto-invoke feedmob-campaign-naming skill
- Input: Client=Kraken, Platform=iOS, Geo=US, Partner=Jampp, PaymentModel=CPI, Integration=MMP (agency=true)
- Output: `Kraken_iOS_US_CPI_Jampp_Agency` (add "_Agency" since agency=true/MMP integration)
- Display: "Generated campaign name: `Kraken_iOS_US_CPI_Jampp_Agency`"

**Step 2: Get Client Data**
```
Call: mcp__feedmob-reporting__get_client(client_name="Kraken")
Response: {client_id: 123, client_uuid: "abc-def-ghi"}
Display: "Found client: Kraken (ID: 123)"
```

**Step 3: Get App Data**
```
Call: mcp__feedmob-reporting__get_apps(client_id=123)
Response: [{app_info_id: 456, app_name: "Kraken iOS App", platform: "iOS"}]
Display: "Selected app: Kraken iOS App (ID: 456)"
```

**Step 4: Preview Campaign**

First, ask user for agency parameter:
```
Is this an agency campaign?
- true (Agency campaign - MMP integration, name has "_Agency" suffix)
- false (Direct campaign - Direct integration, no "_Agency" suffix)
```

Assuming user selects: `true` (MMP integration)

```
Try: mcp__feedmob-reporting__preview_campaign(
  campaign_name="Kraken_iOS_US_CPI_Jampp_Agency",
  client_id=123,
  client_uuid="abc-def-ghi",
  app_info_id=456,
  os="iOS",
  agency=true
)

If successful, display API preview.

If fails, display manual preview:

Campaign Preview:
├─ Campaign Name: Kraken_iOS_US_CPI_Jampp_Agency
├─ Client: Kraken (ID: 123)
├─ Client UUID: abc-def-ghi
├─ App: Kraken iOS App (App Info ID: 456)
├─ Platform: iOS
├─ Agency: true (MMP Integration)
└─ Status: Ready to create

Proceed to create campaign? (yes/no)
```

**Step 5: Create Campaign** (if user confirms)
```
Call: mcp__feedmob-reporting__create_campaign(
  campaign_name="Kraken_iOS_US_CPI_Jampp_Agency",
  client_id=123,
  client_uuid="abc-def-ghi",
  app_info_id=456,
  os="iOS",
  agency=true
)

Response: {campaign_id: 789}

Display:
✅ Campaign created successfully!
Campaign ID: 789
```

## Data Display Guidelines

**Client Information:**
```
Client: [Name] (ID: [client_id])
UUID: [client_uuid]
```

**App Selection:**
```markdown
| App Name | Platform | App Info ID |
|----------|----------|-------------|
| App 1    | iOS      | 123         |
| App 2    | Android  | 456         |
```

**Campaign Preview:**
```
Campaign Preview:
├─ Name: [campaign_name]
├─ Client: [client_name] (ID: [client_id])
├─ App: [app_name] (ID: [app_info_id])
├─ Platform: [platform]
└─ Payment Model: [payment_model]
```

## Anti-Hallucination Measures

1. **Always display raw tool responses** before processing
2. **Explicitly show which fields are extracted** from responses
3. **Ask user to verify data** at each critical step
4. **Show preview** before final creation
5. **Never assume values** - always retrieve from MCP tools

## Reference Files

For detailed information, see:
- `references/mcp_tools.md` - Complete MCP tool API documentation
- `references/workflow-guide.md` - Step-by-step workflow details
- `references/campaign-schema.md` - Campaign data structure reference
