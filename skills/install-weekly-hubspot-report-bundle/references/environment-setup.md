# Environment Setup Guide

Complete guide for setting up environment variables required by the weekly-hubspot-report skills.

## Overview

The weekly-hubspot-report skills bundle requires several environment variables to function properly. These variables provide API authentication and AWS credentials for report generation and S3 upload.

## Required Environment Variables

### For weekly-hubspot-report

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `FEMINI_API_TOKEN` | FeedMob Femini API authentication token | Yes | `eyJhbGc...` |
| `FEEDAI_API_TOKEN` | FeedAI MCP server authentication token | Yes | `sk-proj-...` |

### For weekly-hubspot-report-pipeline

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID` | AWS access key ID for S3 upload | Yes | `AKIAIOSFODNN7EXAMPLE` |
| `WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY` | AWS secret access key for S3 upload | Yes | `wJalrXUtnFEMI/K7MDENG/...` |
| `WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET` | Target S3 bucket name for reports | Yes | `my-reports-bucket` |
| `WEEKLY_HUBSPOT_REPORT__AWS_REGION` | AWS region for S3 bucket | No | `us-west-2` (default) |

## How to Obtain API Tokens

### FEMINI_API_TOKEN

1. Contact your FeedMob administrator or team lead
2. Request access to the Femini API
3. You will receive a JWT token that looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
4. Store this token securely

**Note:** This token provides access to FeedMob's internal Femini service for client and pod data.

### FEEDAI_API_TOKEN

1. Contact your FeedAI administrator or team lead
2. Request access to the FeedAI MCP server
3. You will receive an authentication token
4. Store this token securely

**Note:** This token provides access to HubSpot ticket data through the FeedAI MCP server.

### AWS Credentials

**Option 1: Use Existing AWS Credentials**

If you already have AWS credentials configured:
```bash
# Check existing credentials
cat ~/.aws/credentials
```

Use the `aws_access_key_id` and `aws_secret_access_key` from your profile.

**Option 2: Create New IAM User**

1. Log in to AWS Console
2. Go to IAM → Users → Add User
3. Enable "Programmatic access"
4. Attach policy: `AmazonS3FullAccess` (or create custom policy with S3 write permissions)
5. Save the access key ID and secret access key

**Minimum S3 Policy (Recommended):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

## Setting Environment Variables

### Method 1: Shell Configuration Files (Persistent)

Add environment variables to your shell configuration file so they persist across sessions.

**For Bash (~/.bashrc or ~/.bash_profile):**

```bash
# Open your shell config
nano ~/.bashrc

# Add these lines at the end:
export FEMINI_API_TOKEN="your-femini-token-here"
export FEEDAI_API_TOKEN="your-feedai-token-here"
export WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID="your-aws-access-key"
export WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET="your-bucket-name"
export WEEKLY_HUBSPOT_REPORT__AWS_REGION="us-west-2"

# Save and reload:
source ~/.bashrc
```

**For Zsh (~/.zshrc):**

```bash
# Open your shell config
nano ~/.zshrc

# Add the same export lines as above

# Save and reload:
source ~/.zshrc
```

**For Fish (~/.config/fish/config.fish):**

```fish
# Open your shell config
nano ~/.config/fish/config.fish

# Add these lines:
set -x FEMINI_API_TOKEN "your-femini-token-here"
set -x FEEDAI_API_TOKEN "your-feedai-token-here"
set -x WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID "your-aws-access-key"
set -x WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY "your-aws-secret-key"
set -x WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET "your-bucket-name"
set -x WEEKLY_HUBSPOT_REPORT__AWS_REGION "us-west-2"

# Save and reload:
source ~/.config/fish/config.fish
```

### Method 2: .env File (Project-Specific)

Create a `.env` file in your project directory:

```bash
# Create .env file
cat > ~/.config/opencode/.env << 'EOF'
FEMINI_API_TOKEN=your-femini-token-here
FEEDAI_API_TOKEN=your-feedai-token-here
WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID=your-aws-access-key
WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY=your-aws-secret-key
WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET=your-bucket-name
WEEKLY_HUBSPOT_REPORT__AWS_REGION=us-west-2
EOF

# Load before running skills:
source ~/.config/opencode/.env
```

**Important:** Add `.env` to `.gitignore` to avoid committing secrets:
```bash
echo ".env" >> .gitignore
```

### Method 3: Session-Only (Temporary)

Set variables for the current terminal session only:

```bash
export FEMINI_API_TOKEN="your-femini-token-here"
export FEEDAI_API_TOKEN="your-feedai-token-here"
export WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID="your-aws-access-key"
export WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET="your-bucket-name"
export WEEKLY_HUBSPOT_REPORT__AWS_REGION="us-west-2"
```

**Note:** These will be lost when you close the terminal.

### Method 4: System-Wide (Advanced)

For system-wide availability (all users):

```bash
# Edit /etc/environment (requires sudo)
sudo nano /etc/environment

# Add these lines:
FEMINI_API_TOKEN="your-femini-token-here"
FEEDAI_API_TOKEN="your-feedai-token-here"
WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID="your-aws-access-key"
WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET="your-bucket-name"
WEEKLY_HUBSPOT_REPORT__AWS_REGION="us-west-2"

# Save and reboot or log out/in
```

## Validation

After setting environment variables, verify they are correctly set:

### Check Individual Variables

```bash
[ -n "$FEMINI_API_TOKEN" ] && echo "FEMINI_API_TOKEN: set" || echo "FEMINI_API_TOKEN: not set"
[ -n "$FEEDAI_API_TOKEN" ] && echo "FEEDAI_API_TOKEN: set" || echo "FEEDAI_API_TOKEN: not set"
[ -n "$WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID" ] && echo "WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID: set" || echo "WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID: not set"
[ -n "$WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY" ] && echo "WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY: set" || echo "WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY: not set"
[ -n "$WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET" ] && echo "WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET: set ($WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET)" || echo "WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET: not set"
echo "WEEKLY_HUBSPOT_REPORT__AWS_REGION: ${WEEKLY_HUBSPOT_REPORT__AWS_REGION:-us-west-2 (default)}"
```

Each variable should report `set`.

### Check All at Once

```bash
for var in \
  FEMINI_API_TOKEN \
  FEEDAI_API_TOKEN \
  WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID \
  WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY \
  WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET; do
  [ -n "${!var}" ] && echo "$var: set" || echo "$var: not set"
done

echo "WEEKLY_HUBSPOT_REPORT__AWS_REGION: ${WEEKLY_HUBSPOT_REPORT__AWS_REGION:-us-west-2 (default)}"
```

This prints only set/not-set status and does not reveal secret values.

### Test AWS Credentials

Verify AWS credentials work:

```bash
# Install AWS CLI if not already installed
# Ubuntu/Debian: sudo apt install awscli
# macOS: brew install awscli

# Test S3 access
aws s3 ls s3://${WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET}/ \
  --region ${WEEKLY_HUBSPOT_REPORT__AWS_REGION:-us-west-2}
```

If successful, you'll see the bucket contents (or empty list if bucket is empty).

### Test API Tokens

Test Femini API token:

```bash
curl -H "Authorization: Bearer ${FEMINI_API_TOKEN}" \
  https://claude.feedmob.com/femini/mcp/health
```

Test FeedAI API token:

```bash
curl -H "Authorization: Bearer ${FEEDAI_API_TOKEN}" \
  https://claude.feedmob.com/feedai/mcp/health
```

Both should return success responses (not authentication errors).

## Security Best Practices

### 1. Never Commit Secrets to Git

Always add secret-containing files to `.gitignore`:

```bash
# .gitignore
.env
.env.*
*.key
*.pem
credentials
secrets.txt
```

### 2. Use Secure Storage

Consider using a secret manager:

**Option 1: AWS Secrets Manager**
```bash
aws secretsmanager get-secret-value --secret-id hubspot-report-tokens
```

**Option 2: Pass (Password Store)**
```bash
pass insert hubspot/femini-token
pass insert hubspot/feedai-token
```

**Option 3: 1Password CLI**
```bash
op read "op://vault/hubspot-tokens/femini"
```

### 3. Rotate Tokens Regularly

- Change API tokens every 90 days
- Update AWS credentials periodically
- Revoke old tokens after rotation

### 4. Limit Token Scope

- Use the minimum required permissions
- Don't use root AWS credentials
- Create service-specific IAM users

### 5. Audit Access

Regularly review:
- Who has access to these tokens
- Where they are stored
- Recent API usage logs

## Troubleshooting

### Variables Not Set After Adding to Config File

**Problem:** Variables not available in new terminal sessions.

**Solutions:**

1. Make sure you edited the correct config file:
```bash
# Check which shell you're using
echo $SHELL

# Bash: ~/.bashrc (Linux) or ~/.bash_profile (macOS)
# Zsh: ~/.zshrc
# Fish: ~/.config/fish/config.fish
```

2. Reload the config file:
```bash
source ~/.bashrc  # or ~/.zshrc or ~/.config/fish/config.fish
```

3. Start a new terminal session to test.

### AWS Credentials Not Working

**Problem:** S3 upload fails with authentication error.

**Solutions:**

1. Verify credentials are valid:
```bash
aws sts get-caller-identity
```

2. Check IAM user has S3 permissions:
```bash
aws iam list-user-policies --user-name your-username
aws iam list-attached-user-policies --user-name your-username
```

3. Verify bucket exists and you have access:
```bash
aws s3 ls s3://${WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET}/
```

### API Tokens Expired

**Problem:** API calls return 401 Unauthorized.

**Solutions:**

1. Contact administrator for new tokens
2. Update environment variables with new tokens
3. Reload shell config or restart terminal

### Variables Set but Skills Don't See Them

**Problem:** Skills report missing environment variables despite being set.

**Solutions:**

1. Verify OpenCode/Claude can see the variables:
```bash
# Run a test command in the same session where you'll use the skills
[ -n "$FEMINI_API_TOKEN" ] && echo "FEMINI_API_TOKEN visible in this session" || echo "FEMINI_API_TOKEN not visible in this session"
```

2. If using systemd services or non-interactive shells, environment variables may not be loaded. Add them to the service configuration or use a .env file.

3. Try setting variables in the same terminal session before running the skill.

## Quick Setup Script

Save this as `setup-env.sh` for quick setup:

```bash
#!/bin/bash
# Quick environment setup script for HubSpot reporting skills

read -p "Enter FEMINI_API_TOKEN: " FEMINI_TOKEN
read -p "Enter FEEDAI_API_TOKEN: " FEEDAI_TOKEN
read -p "Enter AWS_ACCESS_KEY_ID: " AWS_KEY
read -sp "Enter AWS_SECRET_ACCESS_KEY: " AWS_SECRET
echo ""
read -p "Enter AWS_S3_BUCKET: " S3_BUCKET
read -p "Enter AWS_REGION [us-west-2]: " AWS_REGION
AWS_REGION=${AWS_REGION:-us-west-2}

# Detect shell and config file
if [ -n "$ZSH_VERSION" ]; then
    CONFIG_FILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    CONFIG_FILE="$HOME/.bashrc"
else
    CONFIG_FILE="$HOME/.profile"
fi

# Append to config file
cat >> "$CONFIG_FILE" << EOF

# HubSpot Reporting Skills - Added $(date)
export FEMINI_API_TOKEN="$FEMINI_TOKEN"
export FEEDAI_API_TOKEN="$FEEDAI_TOKEN"
export WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID="$AWS_KEY"
export WEEKLY_HUBSPOT_REPORT__AWS_SECRET_ACCESS_KEY="$AWS_SECRET"
export WEEKLY_HUBSPOT_REPORT__AWS_S3_BUCKET="$S3_BUCKET"
export WEEKLY_HUBSPOT_REPORT__AWS_REGION="$AWS_REGION"
EOF

echo "✅ Environment variables added to $CONFIG_FILE"
echo "Run: source $CONFIG_FILE"
echo "Or open a new terminal to load the variables."
```

Make it executable and run:
```bash
chmod +x setup-env.sh
./setup-env.sh
```

## Summary

1. **Obtain tokens** from your administrators
2. **Choose a method** (shell config, .env file, or session-only)
3. **Set variables** using export commands
4. **Validate** using echo or env commands
5. **Test** API access before using skills
6. **Secure** your tokens following best practices

Once environment variables are properly set, the weekly-hubspot-report skills will be ready to use!
