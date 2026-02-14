---
name: install-weekly-hubspot-report-bundle
description: "Automatically installs and configures weekly-hubspot-report and weekly-hubspot-report-pipeline skills from feedmob-skills repository. Supports git clone or manual zip upload, runs npx skills add commands, and guides environment variable setup for FEMINI_API_TOKEN, FEEDAI_API_TOKEN, and AWS credentials. Use when: user needs HubSpot reporting, install HubSpot skills, generate weekly ticket reports, configure report pipeline, or when weekly-hubspot-report* skills are mentioned but not available. Triggers: install HubSpot skills, setup HubSpot reporting, HubSpot weekly report, configure HubSpot, feedmob-skills installation."
---

# Install Weekly HubSpot Report Bundle

Automatically installs the HubSpot reporting skills and guides environment variable setup.

## What This Skill Does

This skill helps you install and configure two HubSpot reporting skills:

1. **weekly-hubspot-report** - Generates comprehensive weekly HubSpot ticket reports with AI-driven insights
2. **weekly-hubspot-report-pipeline** - Orchestrates report generation and uploads results to S3

**Why you need these skills:** FeedMob's support team uses these skills to automatically generate comprehensive weekly reports from HubSpot tickets, providing AI-driven insights into client health, SLA risks, team workload, and trending issues. The reports are automatically uploaded to S3 for easy sharing with stakeholders.

## Installation & Setup Workflow

When triggered by HubSpot reporting requests, follow these steps:

### Step 1: Check if Skills Are Already Installed

Before installing, check if the skills are already available:

1. Try to list or search for "weekly-hubspot-report" in available skills
2. Check if previous attempts to use these skills succeeded

**If skills are already available:**

Ask the user:
> I found that the HubSpot reporting skills appear to be already installed. Would you like me to:
> 1. Proceed with environment variable setup (Recommended)
> 2. Reinstall the skills to get the latest version
> 3. Skip everything and try generating a report

If user chooses option 1, skip to Step 4 (Environment Setup).
If option 2, continue with installation.
If option 3, attempt to use the skills directly.

**If skills are not available:**

Inform the user and ask for confirmation:
> I'll install the HubSpot reporting skills from the feedmob-skills repository. This will:
> 1. Obtain the feedmob-skills repository (git clone or zip upload) into `/tmp/feedmob-skills`
> 2. Install `weekly-hubspot-report-pipeline` skill
> 3. Install `weekly-hubspot-report` skill
> 4. Guide you through environment variable setup
>
> The installation takes about 30-60 seconds. Proceed? (yes/no)

Wait for user confirmation before continuing to Step 2.

### Step 2: Obtain feedmob-skills Repository

Use either git clone (default) or manual zip upload.

#### Option A: Git Clone (Default)

Check if the repository already exists and clone if needed:

```bash
if [ -d "/tmp/feedmob-skills" ]; then
    echo "Repository exists. Pulling latest changes..."
    cd /tmp/feedmob-skills && git pull
else
    echo "Cloning feedmob-skills repository..."
    git clone git@github.com:feed-mob/feedmob-skills.git /tmp/feedmob-skills
fi
```

If SSH clone fails, try HTTPS fallback:

```bash
git clone https://github.com/feed-mob/feedmob-skills.git /tmp/feedmob-skills
```

If both git methods fail, continue with Option B.

#### Option B: Manual Zip Upload

If git access is unavailable, ask the user to upload a zip file of the repository and then place it at `/tmp/feedmob-skills`.

Ask the user:
> I couldn't fetch the repository with git. Please upload `feedmob-skills` as a zip file, and I'll place it into `/tmp/feedmob-skills` for installation.

After upload, perform these steps:

```bash
# Example uploaded file path (adjust to actual uploaded location)
ZIP_PATH="/tmp/feedmob-skills.zip"

# Clean and prepare target directory
rm -rf /tmp/feedmob-skills
mkdir -p /tmp/feedmob-skills

# Extract archive into /tmp
unzip -q "$ZIP_PATH" -d /tmp/

# Normalize common extracted folder names
if [ -d "/tmp/feedmob-skills-main" ]; then
  cp -R /tmp/feedmob-skills-main/. /tmp/feedmob-skills/
elif [ -d "/tmp/feedmob-skills" ]; then
  :
else
  echo "Could not find extracted feedmob-skills directory"
  exit 1
fi

# Verify required skill directories exist
ls /tmp/feedmob-skills/skills/weekly-hubspot-report
ls /tmp/feedmob-skills/skills/weekly-hubspot-report-pipeline
```

If extraction or verification fails, share the error and refer to [references/troubleshooting.md](references/troubleshooting.md).

### Step 3: Install Skills Using npx

Install both skills in the correct order (pipeline first, then main skill).

First, determine the target agent and set `AGENT_NAME` accordingly:
- `opencode`
- `codex`
- `claude-code`
- `openclaw`

Example:

```bash
AGENT_NAME="opencode"
```

**Install weekly-hubspot-report-pipeline:**

```bash
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent "$AGENT_NAME" -y
```

Show progress:
> [1/2] Installing weekly-hubspot-report-pipeline...

**Install weekly-hubspot-report:**

```bash
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent "$AGENT_NAME" -y
```

Agent-specific examples:

```bash
# OpenCode
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent opencode -y
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent opencode -y

# Codex
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent codex -y
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent codex -y

# Claude Code
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent claude-code -y
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent claude-code -y

# OpenClaw
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent openclaw -y
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent openclaw -y
```

Show progress:
> [2/2] Installing weekly-hubspot-report...

**If installation succeeds:**

> ✅ Both skills installed successfully!
>
> **Next:** Let's set up the required environment variables.

Continue to Step 4.

**If installation fails:**

Capture the error output and check for common issues:
- Skill name typo (verify: `ls /tmp/feedmob-skills/skills/`)
- Permission errors  
- Conflicting skill versions
- npx not found (install Node.js)

Show error to user and refer to [references/troubleshooting.md](references/troubleshooting.md).

### Step 4: Check Current Environment Setup

First, check what environment variables are already configured. Ask the user:

> I'll help you set up the HubSpot reporting skills. Let me check your current environment configuration.
>
> These skills require several environment variables. Would you like me to:
> 1. Guide you through setting them all up from scratch
> 2. Check which ones might already be configured
> 3. Show me the reference documentation
>
> (Recommend option 2 if you've used these skills before)

### Step 5: Identify Required Environment Variables

Explain what environment variables are needed and what they're for:

> **Required Environment Variables:**
>
> **For `weekly-hubspot-report` (report generation):**
> - `FEMINI_API_TOKEN` - FeedMob Femini API token for HubSpot data access
> - `FEEDAI_API_TOKEN` - FeedAI API token for AI-driven insights
>
> **For `weekly-hubspot-report-pipeline` (S3 upload):**
> - `WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID` - AWS access key for S3
> - `WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY` - AWS secret key for S3
> - `WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET` - S3 bucket name (e.g., feedmob-reports)
> - `WEEKLY_HUBSPOT_REPORT__AWS_REGION` - AWS region (optional, default: us-west-2)
>
> Would you like me to guide you through setting these up?

### Step 6: Guide User Through Environment Variable Setup

For each missing or needed environment variable, provide step-by-step instructions. Use the comprehensive guide from [references/environment-setup.md](references/environment-setup.md).

**Interactive approach:**

1. Ask which variables the user needs help with:
   > Which environment variables do you need help setting up?
   > 1. FEMINI_API_TOKEN
   > 2. FEEDAI_API_TOKEN  
   > 3. AWS credentials (all of them)
   > 4. All of the above

2. For each variable, provide clear setup instructions based on the user's shell:

**Example for FEMINI_API_TOKEN:**

> **Setting up FEMINI_API_TOKEN:**
>
> 1. Add to your shell configuration file:
>
> For **bash** users (`~/.bashrc`):
> ```bash
> echo 'export FEMINI_API_TOKEN="your-token-here"' >> ~/.bashrc
> source ~/.bashrc
> ```
>
> For **zsh** users (`~/.zshrc`):
> ```bash
> echo 'export FEMINI_API_TOKEN="your-token-here"' >> ~/.zshrc
> source ~/.zshrc
> ```
>
> 2. **OR** add to project `.env` file (if using dotenv):
> ```bash
> echo 'FEMINI_API_TOKEN=your-token-here' >> .env
> ```
>
> 3. Verify it's set:
> ```bash
> [ -n "$FEMINI_API_TOKEN" ] && echo "✓ FEMINI_API_TOKEN is set" || echo "✗ FEMINI_API_TOKEN is not set"
> ```
>
> **Where to get the token:**
> Contact your FeedMob team administrator for the FEMINI_API_TOKEN value.

3. Repeat for each variable the user needs

### Step 7: Verify Setup

After the user has configured their environment variables, guide them to verify:

> **Let's verify your environment setup:**
>
> Run these commands to check if variables are set correctly:
>
> ```bash
> # Check report generation variables
> [ -n "$FEMINI_API_TOKEN" ] && echo "✓ FEMINI_API_TOKEN is set" || echo "✗ FEMINI_API_TOKEN not set"
> [ -n "$FEEDAI_API_TOKEN" ] && echo "✓ FEEDAI_API_TOKEN is set" || echo "✗ FEEDAI_API_TOKEN not set"
>
> # Check AWS variables  
> [ -n "$WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID" ] && echo "✓ AWS_ACCESS_KEY_ID is set" || echo "✗ AWS_ACCESS_KEY_ID not set"
> [ -n "$WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY" ] && echo "✓ AWS_SECRET_ACCESS_KEY is set" || echo "✗ AWS_SECRET_ACCESS_KEY not set"
> [ -n "$WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET" ] && echo "✓ AWS_S3_BUCKET: $WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET" || echo "✗ AWS_S3_BUCKET not set"
> echo "AWS_REGION: ${WEEKLY_HUBSPOT_REPORT__AWS_REGION:-us-west-2 (default)}"
> ```
>
> This will confirm each variable is set without exposing sensitive token values.
>
> Do all variables show values? (yes/no)

**If no:**
- Ask which variables are still missing
- Provide troubleshooting help from [references/troubleshooting.md](references/troubleshooting.md)

**If yes:**
- Congratulate and move to next step

### Step 8: Test the Configuration

Once environment variables are set, guide the user to test:

> ✅ **Environment setup complete!**
>
> **Next Steps:**
>
> 1. Restart your terminal or agent session to ensure variables are loaded
> 2. Try generating a test report:
>    - "Generate a HubSpot weekly report for last week"
>    - "Create HubSpot ticket analysis and upload to S3"
>
> **If you encounter errors:**
> - Check the error message for which variable is missing
> - See troubleshooting guide: [references/troubleshooting.md](references/troubleshooting.md)
> - Verify variables are loaded in current session with presence checks (no token output)
>
> Would you like to try generating a report now?

## Quick Reference

### Environment Variables Checklist

Copy and customize these commands for your shell:

**For Bash (~/.bashrc):**
```bash
# HubSpot Report Generation
export FEMINI_API_TOKEN="your-femini-token-here"
export FEEDAI_API_TOKEN="your-feedai-token-here"

# AWS S3 Upload Configuration
export WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID="your-aws-access-key"
export WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET="feedmob-reports"
export WEEKLY_HUBSPOT_REPORT__AWS_REGION="us-west-2"  # Optional
```

**For Zsh (~/.zshrc):**
```bash
# HubSpot Report Generation
export FEMINI_API_TOKEN="your-femini-token-here"
export FEEDAI_API_TOKEN="your-feedai-token-here"

# AWS S3 Upload Configuration
export WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID="your-aws-access-key"
export WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET="feedmob-reports"
export WEEKLY_HUBSPOT_REPORT__AWS_REGION="us-west-2"  # Optional
```

**For Project .env File:**
```bash
FEMINI_API_TOKEN=your-femini-token-here
FEEDAI_API_TOKEN=your-feedai-token-here
WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID=your-aws-access-key
WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY=your-aws-secret-key
WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET=feedmob-reports
WEEKLY_HUBSPOT_REPORT__AWS_REGION=us-west-2
```

### Verify Configuration

```bash
# Quick check (verifies variables are set without exposing values)
[ -n "$FEMINI_API_TOKEN" ] && echo "✓ FEMINI_API_TOKEN is set" || echo "✗ FEMINI_API_TOKEN not set"
[ -n "$FEEDAI_API_TOKEN" ] && echo "✓ FEEDAI_API_TOKEN is set" || echo "✗ FEEDAI_API_TOKEN not set"
[ -n "$WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID" ] && echo "✓ AWS_ACCESS_KEY_ID is set" || echo "✗ AWS_ACCESS_KEY_ID not set"
[ -n "$WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY" ] && echo "✓ AWS_SECRET_ACCESS_KEY is set" || echo "✗ AWS_SECRET_ACCESS_KEY not set"
[ -n "$WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET" ] && echo "✓ AWS_S3_BUCKET: $WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET" || echo "✗ AWS_S3_BUCKET not set"
echo "AWS_REGION: ${WEEKLY_HUBSPOT_REPORT__AWS_REGION:-us-west-2 (default)}"
```

### Getting Token Values

Contact your FeedMob team administrator to obtain:
- FEMINI_API_TOKEN
- FEEDAI_API_TOKEN
- AWS credentials (Access Key ID, Secret Access Key, S3 Bucket name)

### Additional Resources

For detailed setup instructions and troubleshooting:

- **[Environment Setup Guide](references/environment-setup.md)** - Complete instructions for setting up all environment variables
- **[Troubleshooting Guide](references/troubleshooting.md)** - Common issues and solutions

## Notes

- Skills are installed to the agent's skills directory  
- The feedmob-skills repository is cloned to `/tmp/feedmob-skills` temporarily
- Environment variables must be set before using the HubSpot reporting skills
- Restart your terminal/agent session after adding variables to shell config files
- Use `.env` files for project-specific configurations
- Keep tokens secure - never commit them to version control
- Verification commands never expose token values for security
