# Troubleshooting Guide

Common issues and solutions for installing the weekly-hubspot-report skills bundle.

## Git Clone Failures

### SSH Permission Denied

**Error:**
```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Cause:** SSH keys are not set up or not added to your GitHub account.

**Solutions:**

**Option 1: Use HTTPS instead (Quick Fix)**
```bash
git clone https://github.com/feed-mob/feedmob-skills.git /tmp/feedmob-skills
```

**Option 2: Set up SSH keys (Recommended)**

1. Generate SSH key:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Start ssh-agent:
```bash
eval "$(ssh-agent -s)"
```

3. Add key to ssh-agent:
```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy public key:
```bash
cat ~/.ssh/id_ed25519.pub
```

5. Add to GitHub:
   - Go to https://github.com/settings/keys
   - Click "New SSH key"
   - Paste the public key
   - Save

6. Test connection:
```bash
ssh -T git@github.com
```

### Network Connectivity Issues

**Error:**
```
fatal: unable to access 'https://github.com/...': Could not resolve host
```

**Cause:** Network connection problems or DNS issues.

**Solutions:**

1. Check internet connection:
```bash
ping github.com
```

2. Try alternative DNS (Google DNS):
```bash
# Temporary fix
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

3. Check proxy settings if behind corporate firewall:
```bash
git config --global http.proxy http://proxy.example.com:8080
```

### Repository Access Denied

**Error:**
```
fatal: repository 'https://github.com/feed-mob/feedmob-skills.git/' not found
```

**Cause:** No access to the private repository.

**Solutions:**

1. Verify you have access to the `feed-mob/feedmob-skills` repository
2. Contact repository administrator for access
3. Check if you're logged in with the correct GitHub account
4. **Alternative:** Use zip file upload method (see below)

### No Git Access - Use Zip File Upload

**Scenario:** You don't have git installed, SSH keys configured, or repository access.

**Solution:** Upload the repository as a zip file instead.

**Steps:**

1. **Obtain the zip file:**
   - If you have GitHub access: Download from https://github.com/feed-mob/feedmob-skills/archive/refs/heads/main.zip
   - If no access: Request the zip file from your team administrator

2. **Upload the zip file** to the agent/conversation

3. **Extract and install:**
```bash
# Save uploaded file to /tmp
# (Agent will handle this automatically when you upload)

# Extract the zip
unzip /tmp/feedmob-skills.zip -d /tmp/

# Handle GitHub's default naming (feedmob-skills-main/)
if [ -d "/tmp/feedmob-skills-main" ]; then
    mv /tmp/feedmob-skills-main /tmp/feedmob-skills
fi

# Verify extraction
ls /tmp/feedmob-skills/skills/

# Install skills
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent openclaw -y
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent openclaw -y
```

4. **If unzip is not available:**
```bash
# Install unzip
# Linux (Ubuntu/Debian):
sudo apt install unzip

# Linux (Fedora/RHEL):
sudo dnf install unzip

# macOS: (usually pre-installed)
brew install unzip
```

### Git Not Installed

**Error:**
```
bash: git: command not found
```

**Solutions:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install git
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install git
```

**macOS:**
```bash
brew install git
```

**Verify installation:**
```bash
git --version
```

## Zip File Upload Errors

### Zip Extraction Failed

**Error:**
```
unzip: command not found
```
OR
```
Archive: feedmob-skills.zip
  End-of-central-directory signature not found
```

**Solutions:**

1. **If unzip is missing:**
```bash
# Linux (Ubuntu/Debian):
sudo apt install unzip

# Linux (Fedora/RHEL):
sudo dnf install unzip

# macOS: (usually pre-installed)
brew install unzip
```

2. **If zip file is corrupted:**
   - Re-download the zip file
   - Verify file integrity: `unzip -t feedmob-skills.zip`
   - Try downloading with a different browser or method

3. **If extraction succeeds but directory is wrong:**
```bash
# GitHub archives usually extract to repository-name-branch/
# For example: feedmob-skills-main/
# Rename to expected directory:
mv /tmp/feedmob-skills-main /tmp/feedmob-skills
```

### Wrong Directory Structure After Extraction

**Symptoms:** 
- `npx skills add` can't find skills
- `ls /tmp/feedmob-skills/skills/` shows no directories

**Solutions:**

1. **Check actual structure:**
```bash
ls -la /tmp/feedmob-skills/
```

2. **If nested incorrectly:**
```bash
# Example: Files are in /tmp/feedmob-skills/feedmob-skills/
# Move contents up one level:
mv /tmp/feedmob-skills/feedmob-skills/* /tmp/feedmob-skills/
rmdir /tmp/feedmob-skills/feedmob-skills
```

3. **Verify correct structure:**
```bash
# Should show: weekly-hubspot-report/ and weekly-hubspot-report-pipeline/
ls /tmp/feedmob-skills/skills/
```

### Uploaded File Not Accessible

**Symptoms:**
- File uploaded but can't be found
- Agent can't access the uploaded file

**Solutions:**

1. **Ask agent to confirm upload location:**
   - Agent should indicate where the file was saved
   - Common locations: `/tmp/`, `~/Downloads/`, current working directory

2. **List files to find it:**
```bash
find /tmp -name "feedmob-skills*.zip" -type f 2>/dev/null
find ~ -name "feedmob-skills*.zip" -type f 2>/dev/null
```

3. **Re-upload with specific instructions:**
   - Ask agent to save file to `/tmp/feedmob-skills.zip`
   - Verify save location before proceeding

## npx skills add Errors

### npx Not Found

**Error:**
```
bash: npx: command not found
```

**Cause:** Node.js is not installed.

**Solutions:**

1. Install Node.js from https://nodejs.org/ (includes npx)

2. Or use package manager:

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**macOS:**
```bash
brew install node
```

3. Verify installation:
```bash
npx --version
```

### Skill Not Found in Repository

**Error:**
```
Error: Skill 'weekly-hubspot-report' not found in repository
```

**Cause:** 
- Skill name typo
- Repository structure changed
- Repository not fully cloned

**Solutions:**

1. Verify skill exists:
```bash
ls -la /tmp/feedmob-skills/skills/
```

Expected output should include:
- `weekly-hubspot-report/`
- `weekly-hubspot-report-pipeline/`

2. Check SKILL.md exists:
```bash
ls -la /tmp/feedmob-skills/skills/weekly-hubspot-report/SKILL.md
```

3. Re-clone repository:
```bash
rm -rf /tmp/feedmob-skills
git clone git@github.com:feed-mob/feedmob-skills.git /tmp/feedmob-skills
```

### Permission Denied (Skills Directory)

**Error:**
```
Error: EACCES: permission denied, mkdir '/home/user/.config/opencode/skills/...'
```

**Cause:** No write permissions to OpenCode skills directory.

**Solutions:**

1. Check directory permissions:
```bash
ls -la ~/.config/opencode/
```

2. Fix permissions:
```bash
chmod -R u+w ~/.config/opencode/skills/
```

3. If directory doesn't exist, create it:
```bash
mkdir -p ~/.config/opencode/skills
```

### Conflicting Skill Version

**Error:**
```
Error: Skill 'weekly-hubspot-report' already exists
```

**Cause:** Skill already installed or partial installation.

**Solutions:**

1. Check existing installation:
```bash
ls -la ~/.config/opencode/skills/weekly-hubspot-report/
```

2. Remove existing skill:
```bash
rm -rf ~/.config/opencode/skills/weekly-hubspot-report
rm -rf ~/.config/opencode/skills/weekly-hubspot-report-pipeline
```

3. Reinstall:
```bash
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent openclaw -y
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent openclaw -y
```

## Partial Installation Issues

### One Skill Installed, One Failed

**Scenario:** `weekly-hubspot-report-pipeline` installed successfully, but `weekly-hubspot-report` failed.

**Solutions:**

1. Identify which skill is missing by checking available skills or attempting to use them

2. Install only the missing skill:
```bash
# If weekly-hubspot-report is missing:
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent openclaw -y

# If weekly-hubspot-report-pipeline is missing:
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent openclaw -y
```

3. Try using both skills to verify they work

### Corrupted Installation

**Symptoms:** Skills appear installed but don't work or trigger.

**Solutions:**

1. Remove both skills completely:
```bash
rm -rf ~/.config/opencode/skills/weekly-hubspot-report*
```

2. Clean any cached data (if applicable):
```bash
rm -rf /tmp/feedmob-skills
```

3. Fresh installation:
```bash
git clone git@github.com:feed-mob/feedmob-skills.git /tmp/feedmob-skills
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report-pipeline --agent openclaw -y
npx skills add /tmp/feedmob-skills --skill weekly-hubspot-report --agent openclaw -y
```

## Disk Space Issues

### No Space Left on Device

**Error:**
```
fatal: write error: No space left on device
```

**Solutions:**

1. Check available space:
```bash
df -h /tmp
df -h ~/.config
```

2. Clean up /tmp:
```bash
# Be careful - this removes all /tmp contents
sudo rm -rf /tmp/*
```

3. Clone to alternative location:
```bash
mkdir -p ~/Downloads/feedmob-skills
git clone git@github.com:feed-mob/feedmob-skills.git ~/Downloads/feedmob-skills
npx skills add ~/Downloads/feedmob-skills --skill weekly-hubspot-report-pipeline --agent openclaw -y
npx skills add ~/Downloads/feedmob-skills --skill weekly-hubspot-report --agent openclaw -y
```

## Permission Issues

### /tmp Permission Denied

**Error:**
```
mkdir: cannot create directory '/tmp/feedmob-skills': Permission denied
```

**Solutions:**

1. Check /tmp permissions:
```bash
ls -la /tmp
```

2. Use alternative location:
```bash
mkdir -p ~/.cache/feedmob-skills
git clone git@github.com:feed-mob/feedmob-skills.git ~/.cache/feedmob-skills
npx skills add ~/.cache/feedmob-skills --skill weekly-hubspot-report-pipeline --agent openclaw -y
npx skills add ~/.cache/feedmob-skills --skill weekly-hubspot-report --agent openclaw -y
```

3. Or use ~/Downloads:
```bash
git clone git@github.com:feed-mob/feedmob-skills.git ~/Downloads/feedmob-skills
npx skills add ~/Downloads/feedmob-skills --skill weekly-hubspot-report-pipeline --agent openclaw -y
npx skills add ~/Downloads/feedmob-skills --skill weekly-hubspot-report --agent openclaw -y
```

## Environment Variable Issues

### Skills Installed but Don't Work

**Cause:** Required environment variables not set.

**Solution:** See [environment-setup.md](environment-setup.md) for detailed setup instructions.

Quick check:
```bash
# Check if env vars are set
[ -n "$FEMINI_API_TOKEN" ] && echo "FEMINI_API_TOKEN: set" || echo "FEMINI_API_TOKEN: not set"
[ -n "$FEEDAI_API_TOKEN" ] && echo "FEEDAI_API_TOKEN: set" || echo "FEEDAI_API_TOKEN: not set"
[ -n "$WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID" ] && echo "WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID: set" || echo "WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID: not set"
```

If any are empty, they need to be set before using the skills.

## Verification Issues

### Installation Complete but Skills Don't Appear

**Symptoms:**
- Installation commands succeeded
- Skills don't appear in available skills list

**Solutions:**

1. Try using the skills directly - they may be installed but not showing up in listings

2. Check if files exist manually (paths may vary by system):
```bash
# Common locations - check all of these
ls -la ~/.config/opencode/skills/ | grep weekly-hubspot-report
ls -la ~/.claude/skills/ | grep weekly-hubspot-report
ls -la ~/Library/Application\ Support/opencode/skills/ | grep weekly-hubspot-report  # macOS
```

3. Check SKILL.md exists in any of these locations:
```bash
find ~ -name "weekly-hubspot-report" -type d 2>/dev/null
```

4. If files exist, try restarting the agent or reloading skills

## Getting Help

If none of these solutions work:

1. **Check OpenCode logs:**
```bash
# Location varies by system
tail -f ~/.config/opencode/logs/agent.log
```

2. **Gather diagnostic information:**
```bash
# System info
uname -a
node --version
npm --version
git --version

# Skills directory
ls -la ~/.config/opencode/skills/

# Repository status
ls -la /tmp/feedmob-skills/
```

3. **Report the issue:**
- Create an issue in the agent-skills repository
- Include error messages, system info, and steps to reproduce
- Mention which troubleshooting steps you've tried

## Quick Diagnostic Script

Run this script to gather all diagnostic information:

```bash
#!/bin/bash
echo "=== System Information ==="
uname -a
echo ""

echo "=== Dependency Versions ==="
git --version
node --version
npx --version
python3 --version 2>/dev/null || echo "python3: not installed"
bun --version 2>/dev/null || echo "bun: not installed"
echo ""

echo "=== Disk Space ==="
df -h /tmp
df -h ~/.config
echo ""

echo "=== Skills Directory ==="
ls -la ~/.config/opencode/skills/ | grep weekly-hubspot-report
echo ""

echo "=== Repository Status ==="
ls -la /tmp/feedmob-skills/ 2>/dev/null || echo "/tmp/feedmob-skills: not found"
echo ""

echo "=== Environment Variables ==="
[ -n "$FEMINI_API_TOKEN" ] && echo "FEMINI_API_TOKEN: set" || echo "FEMINI_API_TOKEN: not set"
[ -n "$FEEDAI_API_TOKEN" ] && echo "FEEDAI_API_TOKEN: set" || echo "FEEDAI_API_TOKEN: not set"
[ -n "$WEEKLY_HUBSPOT_REPORT__AWS_ACCESS_KEY_ID" ] && echo "AWS_ACCESS_KEY_ID: set" || echo "AWS_ACCESS_KEY_ID: not set"
```

Save this as `diagnostic.sh`, make it executable with `chmod +x diagnostic.sh`, and run it to collect diagnostic information.
