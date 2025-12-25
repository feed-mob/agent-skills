# FeedMob Brand Guidelines

![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-00B5AD?style=flat-square)
![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

A Claude Code Skill for generating FeedMob-branded content including reports, presentations, charts, and artifacts. Ensures all content follows official FeedMob brand guidelines.

> **Skill Type**: Agent Skill
> **Compatible with**: Claude Code CLI
> **Version**: 1.0.0

## Table of Contents

- [Features](#features)
- [About FeedMob Brand](#about-feedmob-brand)
- [Logo Assets](#logo-assets)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Quick Start](#quick-start)
- [Brand Guidelines Summary](#brand-guidelines-summary)
- [Integration with Other Skills](#integration-with-other-skills)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Packaging for Distribution](#packaging-for-distribution)
- [Documentation](#documentation)
- [Support](#support)
- [Contributing](#contributing)

## Features

- 🎨 **Brand Consistency**: Automatically applies FeedMob brand standards to all content
- 📝 **Typography Control**: Uses approved Lato font family exclusively
- 🎨 **Color Palette**: Applies official FeedMob color scheme (#00B5AD teal primary)
- 📊 **Data Visualization**: Creates on-brand charts and graphs
- 🖼️ **Logo Compliance**: Handles logo usage with proper specifications
- 📄 **Multiple Formats**: Supports reports, presentations, charts, and artifacts
- ✅ **Quality Assurance**: Built-in checklist for brand compliance

## About FeedMob Brand

**FeedMob** is a Mobile Analytics and Anti-Fraud Platform with a distinctive brand identity:

- **Primary Color**: Teal (#00B5AD)
- **Typography**: Lato font family (Light, Regular, Bold)
- **Logo**: Black text + teal plus sign (signature element)
- **Design**: Modern, clean, minimalist aesthetic
- **Voice**: Professional but friendly, intelligent but approachable

## Logo Assets

This plugin includes official FeedMob logo files ready to use in your branded content:

### Available Logos

Located in `assets/logos/`:

| File | Usage | Background |
|------|-------|------------|
| `feedmob-logo-black-teal.svg` | **Primary logo** | White or light backgrounds |
| `feedmob-logo-white-teal.svg` | **Alternative logo** | Dark or teal backgrounds |
| `feedmob-plus-icon-teal.svg` | **Design element** | Decorative accent |

### Logo Specifications

- **Format**: SVG (scalable vector graphics)
- **Minimum Width**: 190px
- **Clear Space**: 1.5x the diameter of the plus sign on all sides
- **Placement**: Top left (preferred), top right, or bottom right

### When to Use Each Logo

**Black Logo (`feedmob-logo-black-teal.svg`)**:
- ✅ White backgrounds (reports, presentations, documents)
- ✅ Light colored backgrounds
- ✅ Most common use case

**White Logo (`feedmob-logo-white-teal.svg`)**:
- ✅ Dark backgrounds
- ✅ Teal (#00B5AD) backgrounds
- ✅ Section divider slides

**Plus Icon (`feedmob-plus-icon-teal.svg`)**:
- ✅ Bullet point replacements
- ✅ Section markers
- ✅ Visual accents and design elements

The skill automatically selects the appropriate logo based on your content's background color.

## Directory Structure

```
feedmob-brand-guidelines/
├── Skill.md                           # Main skill file with brand guidelines
├── README.md                          # This file
└── assets/
    └── logos/
        ├── feedmob-logo-black-teal.svg    # Primary logo (white backgrounds)
        ├── feedmob-logo-white-teal.svg    # Alternative logo (dark backgrounds)
        └── feedmob-plus-icon-teal.svg     # Plus icon design element
```

## Installation

### Option 1: From Claude Code Marketplace (Recommended)

This skill is part of the FeedMob Claude Code marketplace. It will be automatically available when installed through the marketplace.

### Option 2: Manual Installation

1. Download or clone this repository
2. Create a ZIP file of the `feedmob-brand-guidelines` folder
3. In Claude Code, navigate to Settings > Skills
4. Upload the ZIP file
5. Enable the skill in your Claude Code settings

**Note**: When packaging as a ZIP file, ensure the folder structure is maintained with `Skill.md` at the root level of the ZIP contents.

## How It Works

This skill follows the [Claude Code Skills specification](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills):

1. **Automatic Activation**: Claude Code reads the `description` field in `Skill.md` and determines when to invoke this skill
2. **Context Loading**: When activated, the skill loads comprehensive FeedMob brand guidelines
3. **Content Generation**: All generated content automatically follows FeedMob branding standards
4. **Asset Access**: The skill can reference logo files from the `assets/logos/` directory

## Usage

The FeedMob Branded Content skill will automatically activate when you mention:

- "Create a FeedMob report about..."
- "Generate FeedMob-branded presentation"
- "Make a FeedMob chart showing..."
- "Create FeedMob artifact for..."
- "Design FeedMob branded content for..."

Or explicitly invoke the skill when creating any content that needs FeedMob branding.

### Manual Invocation

You can also explicitly invoke this skill in Claude Code:

```
Use the feedmob-brand-guidelines skill to create...
```

## Quick Start

### Example 1: Create a Branded Report

**Request:**
```
Create a FeedMob-branded quarterly report with charts showing revenue growth and user metrics
```

**Result:**
- Generates report with proper FeedMob branding
- Uses Lato font throughout
- Applies teal (#00B5AD) accents
- Includes properly styled charts
- Maintains brand consistency

### Example 2: Generate a Branded Presentation

**Request:**
```
Create a FeedMob presentation about our anti-fraud platform features
```

**Result:**
- Creates PowerPoint with FeedMob color scheme
- Uses white backgrounds with teal accents
- Applies proper logo placement
- Follows typography guidelines
- Professional slide layouts

### Example 3: Create Branded Charts

**Request:**
```
Generate a FeedMob-branded line chart showing user growth over 12 months
```

**Result:**
- Creates chart with FeedMob brand colors
- Uses Lato font for labels
- Applies teal (#00B5AD) for primary metric
- Includes proper spacing and styling

## Brand Guidelines Summary

### Typography

✅ **DO USE**:
- **Lato Light**: Body text (14-18pt)
- **Lato Regular**: Headers and titles (24-44pt)
- **Lato Bold**: Emphasis (sparingly)
- **Lato Light Italic**: Quotes and references

❌ **NEVER USE**:
- **Ostrich Sans**: Logo only, never in content!
- Other font families
- Font sizes below 14pt

### Colors

**Primary Colors**:
- **Teal**: #00B5AD (primary brand color)
- **White**: #FFFFFF (backgrounds)
- **Dark Grey**: #444444 (body text)

**Secondary Colors** (accents only):
- **Blue**: #1B9BC2
- **Coral**: #EE6969
- **Gold**: #F7BD63
- **Purple**: #A06ACD

**Rules**:
- Use white backgrounds as default
- Apply teal for accents and emphasis
- Maximum 4 colors per chart
- Consistent color mapping across visualizations

### Logo Usage

**Specifications**:
- Minimum width: 190px
- Clear space: 1.5x the plus sign diameter
- Placement: Top left (preferred), top right, or bottom right

**Variations**:
- Black logo + teal plus (for white backgrounds)
- White logo + teal plus (for dark backgrounds)
- All white logo (when necessary)

**Restrictions**:
- Never modify, stretch, or distort
- Never add effects (shadows, glows)
- Never show wordmark without plus sign
- Always maintain clear space

### Data Visualization

**Chart Principles**:
1. Always use Lato font
2. Use brand colors only
3. Maximum 4 colors per chart
4. Consistent colors for same variables
5. Grey for less important elements

**Chart Type Selection**:
- **Line charts**: Time series data only
- **Bar charts**: Long labels, horizontal orientation
- **Column charts**: Short labels, vertical orientation
- **Pie charts**: Maximum 4 segments

### Document Structure

**Standard Margins**:
- Top/Bottom: 60px (0.83 inches)
- Left/Right: 80px (1.11 inches)

**Layout Rules**:
- White backgrounds as primary choice
- 20% minimum margins for white space
- 12-column grid system with 20px gutters
- Consistent spacing and alignment

## What This Skill Ensures

When you create FeedMob-branded content, this skill guarantees:

### Typography Compliance
- ✅ Lato font family used exclusively
- ✅ Proper font sizes (minimum 14pt)
- ✅ Correct font weights for hierarchy
- ❌ Ostrich Sans never used in content

### Color Compliance
- ✅ Official color palette applied
- ✅ Teal (#00B5AD) as primary accent
- ✅ White backgrounds as default
- ✅ Maximum 4 colors per visualization
- ✅ Consistent color mapping

### Logo Compliance
- ✅ Correct logo variation for background
- ✅ Proper sizing (minimum 190px)
- ✅ Adequate clear space (1.5x plus sign)
- ✅ No modifications or distortions

### Design Quality
- ✅ Clean, modern layouts
- ✅ Adequate white space (20% margins)
- ✅ Professional imagery (diverse, modern)
- ✅ Consistent spacing and alignment
- ✅ Clear visual hierarchy

### Content Quality
- ✅ "FeedMob" spelled correctly (F and M caps)
- ✅ Concise, focused content
- ✅ Professional tone
- ✅ Clear structure and organization

## Integration with Other Skills

### PPT Generator Integration

This skill works seamlessly with the `feedmob-presentations` skill:

```
Create a FeedMob presentation about quarterly results
```

The skill will:
1. Invoke `feedmob-presentations` with FeedMob color scheme
2. Apply proper typography (Lato font)
3. Use FeedMob brand colors
4. Place logo according to guidelines
5. Create professional, on-brand slides

### Chart Generation

When creating charts or data visualizations:
1. Applies FeedMob color palette
2. Uses Lato font for all text
3. Maintains consistent color mapping
4. Includes proper spacing and styling
5. Follows chart type best practices

## File Naming Convention

The skill recommends this format:

```
YYYY-MM-DD_FeedMob_[Type]_[Topic]_v[Version].ext
```

**Examples**:
- `2025-01-15_FeedMob_Report_Q1Analysis_v1.pdf`
- `2025-02-03_FeedMob_Presentation_ProductDemo_v2.pptx`
- `2025-03-20_FeedMob_Chart_UserGrowth_v1.png`

## Quality Checklist

The skill includes a comprehensive quality checklist:

### Brand Compliance
- [ ] Logo used correctly
- [ ] Only Lato font family used
- [ ] Brand colors applied consistently
- [ ] "FeedMob" spelled correctly
- [ ] Charts use brand colors

### Design Quality
- [ ] Consistent spacing and alignment
- [ ] Adequate white space
- [ ] No overcrowding
- [ ] High-quality images
- [ ] Clear visual hierarchy

### Content Quality
- [ ] Clear titles
- [ ] Concise content
- [ ] Accurate data
- [ ] No errors
- [ ] Professional tone

### Technical Quality
- [ ] Optimized file size
- [ ] Fonts embedded
- [ ] Images compressed
- [ ] Proper naming

### Accessibility
- [ ] Sufficient contrast (4.5:1)
- [ ] Readable fonts (14pt+)
- [ ] Alt text on images
- [ ] Clear reading order

## Examples

### Creating a Branded Report

**Input:**
```
Create a FeedMob-branded report analyzing mobile ad fraud trends with charts
```

**Output:**
- Cover page with FeedMob logo and teal accents
- Body text in Lato Light, 16pt, #444444
- Section headers in Lato Regular, 28pt, #444444
- Charts using brand colors (teal, blue, coral, gold)
- Professional layout with 20% margins
- Consistent branding throughout

### Creating a Branded Presentation

**Input:**
```
Generate a FeedMob presentation for investor deck with financial metrics
```

**Output:**
- Title slide with teal accent shapes
- Content slides with white backgrounds
- Logo in top left (100-120px width)
- Metrics dashboard with colorful KPI boxes
- Charts with brand color palette
- Professional typography (Lato family)

### Creating a Branded Chart

**Input:**
```
Create a FeedMob line chart showing monthly revenue growth
```

**Output:**
- Line chart with teal (#00B5AD) primary line
- Lato Light font for axis labels (14pt)
- Grey background grid for reference
- Clear title in Lato Regular (24pt)
- 1-2 sentence insight below chart
- Proper spacing and margins

## Best Practices

1. **Plan Structure First**: Define content organization before adding details
2. **Keep It Simple**: Follow the principle of simplicity and clarity
3. **Use White Space**: Don't overcrowd pages or slides
4. **Be Consistent**: Maintain uniform styling throughout
5. **Check Quality**: Review against the quality checklist before finalizing
6. **Get Approval**: External content requires marketing@feedmob.com approval

## Common Mistakes to Avoid

❌ **Typography Errors**:
- Using Ostrich Sans in content (logo only!)
- Mixing multiple font families
- Font sizes below 14pt
- Excessive bold or italic

❌ **Color Errors**:
- Using off-brand colors
- More than 4 colors in one chart
- Inconsistent color mapping
- Low contrast combinations

❌ **Logo Errors**:
- Insufficient clear space
- Modifying or distorting logo
- Wrong logo variation for background
- Adding effects to logo

❌ **Design Errors**:
- Overcrowding content
- Insufficient white space
- Inconsistent spacing
- Poor visual hierarchy

❌ **Content Errors**:
- Misspelling "FeedMob"
- Unprofessional imagery
- Excessive text per page/slide
- Unclear structure

## Troubleshooting

### Issue: Content doesn't look on-brand

**Solution**: Ensure you're explicitly mentioning "FeedMob" in your request to activate the skill. Say "Create a FeedMob-branded..." rather than just "Create a..."

### Issue: Wrong fonts are being used

**Solution**: The skill enforces Lato font family. If you see other fonts, explicitly state "using FeedMob brand guidelines" in your request.

### Issue: Colors don't match brand

**Solution**: Request "FeedMob brand colors" or specify "teal #00B5AD as primary color" in your prompt.

### Issue: Logo placement is incorrect

**Solution**: Specify "following FeedMob logo guidelines" to ensure proper placement and clear space.

## Packaging for Distribution

To create a distributable ZIP file of this skill:

```bash
# Navigate to the parent directory
cd /path/to/plugins

# Create ZIP file (ensure folder structure is correct)
zip -r feedmob-brand-guidelines.zip feedmob-brand-guidelines/ \
  -x "*.DS_Store" -x "*/.git/*"
```

The ZIP should contain:
```
feedmob-brand-guidelines.zip
└── feedmob-brand-guidelines/
    ├── Skill.md
    ├── README.md
    └── assets/
        └── logos/
            ├── feedmob-logo-black-teal.svg
            ├── feedmob-logo-white-teal.svg
            └── feedmob-plus-icon-teal.svg
```

## Documentation

- [Skill.md](Skill.md) - Complete brand guidelines and technical specifications
- [Official Claude Code Skills Documentation](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

## Support

**For Brand Guidelines Questions**:
- Email: marketing@feedmob.com
- Review: All external content requires marketing approval

**For Skill Questions**:
- Check [Skill.md](Skill.md) for detailed guidelines
- Review examples in this README
- Consult the official brand guidelines document
- Visit [Claude Code Skills Documentation](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

## Contributing

Improvements to this skill are welcome! When contributing:

### Development Guidelines
- Follow the [Claude Code Skills standards](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- Maintain `Skill.md` as the primary skill file in the root directory
- Keep the YAML frontmatter updated with accurate metadata
- Test thoroughly before submitting changes

### Contribution Ideas
- Enhance brand guideline coverage
- Add more content type templates
- Improve quality checks and validation
- Add usage examples and case studies
- Update logo assets when new versions are released
- Provide feedback and suggestions

### Before Submitting
- Ensure all changes align with FeedMob brand guidelines
- Update README.md if directory structure changes
- Test skill activation with various prompts
- Verify logo assets are working correctly

---

**Last Updated**: December 2025
**Version**: 1.0.0
**Contact**: marketing@feedmob.com
