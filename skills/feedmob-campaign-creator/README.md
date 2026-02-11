# FeedMob Campaign Creator

A skill for creating FeedMob campaigns through a guided 5-step workflow that integrates with the feedmob-campaign-naming skill and FeedMob admin MCP tools.

## Purpose

This skill orchestrates the complete campaign creation process from name generation to campaign creation, ensuring:
- Standardized campaign naming conventions
- Correct client and app associations
- Validation before creation
- Clear user communication at each step

## Use Cases

1. **New Partner Launch** - Create campaigns for new media partners
2. **Campaign Setup** - Set up campaigns for existing clients and partners
3. **Link Generation** - Generate tracking links for new campaigns
4. **Media Plan Execution** - Implement campaigns from media plans

## Trigger Keywords

The skill activates when users say:
- "create campaign"
- "new campaign"
- "generate campaign"
- "campaign setup"
- "link generation"
- "partner launch"
- "media plan campaign"
- "创建campaign" (Chinese)
- "生成活动" (Chinese)
- "新建campaign" (Chinese)

## Dependencies

### MCP Tools (Required)

All 4 FeedMob admin MCP tools must be available:

| Tool | Purpose | Status |
|------|---------|--------|
| `mcp__feedmob-reporting__get_client` | Retrieve client metadata | ✅ Available |
| `mcp__feedmob-reporting__get_apps` | Retrieve app information | ✅ Available |
| `mcp__feedmob-reporting__preview_campaign` | Preview campaign before creation | ✅ Available |
| `mcp__feedmob-reporting__create_campaign` | Create campaign in system | ✅ Available |

### Related Skills

- **feedmob-campaign-naming** - Auto-invoked for campaign name generation

## Workflow Overview

### 5-Step Process

```
1. Campaign Naming
   └─ Auto-invoke feedmob-campaign-naming skill
   └─ Generate standardized campaign name

2. Client Data Retrieval
   └─ Call get_client MCP tool
   └─ Extract client_id and client_uuid

3. App Data Retrieval
   └─ Call get_apps MCP tool
   └─ User selects app if multiple matches
   └─ Extract app_info_id

4. Campaign Preview
   └─ Call preview_campaign MCP tool
   └─ Display preview to user
   └─ Wait for user confirmation

5. Campaign Creation
   └─ Call create_campaign MCP tool
   └─ Display success with campaign_id
```

## Architecture

### Data Flow

```
User Request
  ↓
[Step 1] feedmob-campaign-naming skill → campaign_name
  ↓
[Step 2] get_client(client_name) → client_id, client_uuid
  ↓
[Step 3] get_apps(client_id) → app_info_id
  ↓
[Step 4] preview_campaign(...) → validation + preview
  ↓
[User confirms]
  ↓
[Step 5] create_campaign(...) → campaign_id ✅
```

### Sequential Dependencies

All steps must execute sequentially:
- Step 2 requires campaign_name from Step 1
- Step 3 requires client_id from Step 2
- Step 4 requires all data from Steps 1-3
- Step 5 requires user confirmation of Step 4

**No parallel execution possible** due to data dependencies.

## File Structure

```
feedmob-campaign-creator/
├── SKILL.md                           # Main skill documentation
├── README.md                          # This file
└── references/
    ├── mcp_tools.md                  # MCP tool API reference
    ├── workflow-guide.md             # Detailed workflow steps
    └── campaign-schema.md            # Campaign data structure
```

## Key Features

### 1. Automatic Name Generation
- Seamlessly invokes feedmob-campaign-naming skill
- No manual name formatting required
- Ensures naming convention compliance

### 2. Intelligent App Selection
- Auto-selects when only one app matches platform
- Presents selection menu when multiple apps available
- Validates platform consistency

### 3. Preview Before Creation
- Shows complete campaign configuration
- Validates all business rules
- Requires explicit user confirmation

### 4. Comprehensive Error Handling
- Clear error messages for all failure cases
- Suggested resolutions for common issues
- Graceful recovery workflows

### 5. Anti-Hallucination Design
- Displays raw MCP tool responses
- Explicitly shows extracted values
- Never assumes or fabricates data

## Testing

### Manual Test Cases

**Test 1: Standard Campaign Creation**
```
User: "Create a campaign for Kraken iOS in US, partner Jampp pays on install, integrated via AppsFlyer MMP"

Expected:
1. Generate name: Kraken_iOS_US_CPI_Jampp
2. Get client data for Kraken
3. Get apps, auto-select iOS app
4. Preview campaign
5. Create campaign → campaign_id returned
```

**Test 2: Multiple App Selection**
```
User: "Create a campaign for Mistplay iOS in Canada, partner Unity pays on purchase, direct integration"

Expected:
1. Generate name: Mistplay_Android_CA_CPA_Unity_Agency
2. Get client data for Mistplay
3. Get apps, display multiple iOS apps, ask user to select
4. Preview campaign with selected app
5. Create campaign → campaign_id returned
```

**Test 3: Error Handling**
```
User: "Create a campaign for NonexistentClient iOS in US..."

Expected:
1. Generate name successfully
2. Get client fails with "not found" error
3. Display error, ask user to verify name
4. User corrects name
5. Retry and continue workflow
```

### Integration Test

Run complete workflow from start to finish:

```bash
# In Claude Code CLI
> Create a campaign for Kraken iOS in US, partner Jampp pays on install, integrated via AppsFlyer MMP
```

Verify:
- ✅ feedmob-campaign-naming skill is invoked
- ✅ All 4 MCP tools are called in correct order
- ✅ Data flows correctly between steps
- ✅ Preview is displayed before creation
- ✅ Campaign is created with correct campaign_id

## Common Issues & Troubleshooting

### Issue 1: MCP Tools Not Found

**Symptom:** Error "Tool not found: mcp__feedmob-reporting__get_client"

**Solution:**
- Verify MCP server is running
- Check MCP server configuration
- Restart Claude Code CLI

### Issue 2: Naming Skill Not Invoked

**Symptom:** Campaign name not generated automatically

**Solution:**
- Verify feedmob-campaign-naming skill exists
- Check skill is properly loaded
- Manually invoke skill if needed

### Issue 3: Client Not Found

**Symptom:** "Client not found" error

**Solution:**
- Verify client name spelling
- Try partial name match
- Check client exists in system
- Use official client name (e.g., "Kraken" not "Kraken Technologies")

### Issue 4: Platform Mismatch

**Symptom:** "Platform doesn't match app platform" error

**Solution:**
- Verify campaign name platform matches selected app
- Regenerate campaign name if needed
- Select correct app for platform

## Best Practices

### For Users

1. **Provide complete information upfront** - Include client, platform, geo, partner, and integration type in initial request
2. **Use official client names** - Use exact client names as they appear in the system
3. **Verify preview carefully** - Double-check all details before confirming creation
4. **Report issues clearly** - Include full error messages when asking for help

### For Developers

1. **Never skip preview step** - Always show preview and wait for confirmation
2. **Display raw responses** - Show what MCP tools return before processing
3. **Explicit extraction** - Clearly state which values you're extracting
4. **Handle errors gracefully** - Provide clear messages and suggested solutions
5. **Follow sequential workflow** - Never parallelize dependent steps

## Integration with Other Skills

### feedmob-campaign-naming

**Relationship:** Parent → Child (auto-invoked)

This skill automatically invokes feedmob-campaign-naming at Step 1 to generate standardized campaign names. No manual name formatting required.

**Data flow:**
```
feedmob-campaign-creator (Step 1)
  ↓
Invoke: feedmob-campaign-naming skill
  ↓
Returns: standardized campaign_name
  ↓
Continue to Step 2 with generated name
```

## Future Enhancements

Potential improvements for future versions:

1. **Batch Campaign Creation** - Create multiple campaigns at once
2. **Campaign Templates** - Pre-configured templates for common scenarios
3. **Link Generation** - Auto-generate tracking links after creation
4. **Campaign Cloning** - Duplicate existing campaigns with modifications
5. **Validation Cache** - Cache client/app data to speed up repeated operations

## Contributing

When modifying this skill:

1. **Update all relevant files** - SKILL.md, references, and README.md
2. **Test thoroughly** - Run all test cases before committing
3. **Document changes** - Update examples if workflow changes
4. **Maintain consistency** - Follow existing patterns and conventions
5. **Version reference docs** - Keep MCP tool signatures up to date

## Support

For issues or questions:

1. Check Common Issues section above
2. Review reference documentation in `references/`
3. Test MCP tools directly to isolate issues
4. Report bugs with full error messages and context

## Version History

- **v1.0** (2024-02-10) - Initial implementation
  - 5-step guided workflow
  - Auto-invocation of feedmob-campaign-naming skill
  - Integration with 4 FeedMob admin MCP tools
  - Comprehensive error handling
  - Anti-hallucination safeguards
