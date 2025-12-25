---
name: feedmob-brand-guidelines
description: Generate FeedMob-branded content including reports, presentations, charts, and artifacts following official brand guidelines. Use when creating any FeedMob-branded materials.
allowed-tools: Read, Write, Bash, Skill
---

# FeedMob Branded Content Generator

This skill ensures all generated content (reports, presentations, charts, artifacts, and other materials) follows FeedMob's official brand guidelines. It provides comprehensive styling rules for typography, colors, layouts, data visualization, and imagery.

## Instructions

When invoked, this skill will:

1. **Apply brand standards**: Ensure all content follows FeedMob brand guidelines
2. **Typography control**: Use approved fonts (Lato for content, never Ostrich Sans except in logos)
3. **Color consistency**: Apply the FeedMob color palette correctly
4. **Logo compliance**: Handle logo usage with proper clear space and variations
5. **Professional output**: Create polished, on-brand materials suitable for business use

## When to Use This Skill

Activate this skill when:
- Creating reports or documents with FeedMob branding
- Generating PowerPoint presentations for FeedMob
- Creating charts, graphs, or data visualizations for FeedMob
- Producing artifacts that need FeedMob brand compliance
- Any content that will represent FeedMob externally or internally

## Brand Identity Overview

**Company**: FeedMob - Mobile Analytics and Anti-Fraud Platform

**Brand Voice**:
- Professional but friendly
- Intelligent but approachable
- Innovative but humble
- Honest but realistic

**Design Principles**:
- Simplicity: Clean, focused designs with clear purpose
- Consistency: Uniform use of colors, fonts, and logo placement
- Modern Aesthetic: Flat design, minimalist layouts, contemporary feel

---

## Color Palette

### Primary Colors (Main Use)

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Teal** | #00B5AD | R0 G181 B173 | Primary brand color - backgrounds, accents, emphasis |
| **White** | #FFFFFF | R255 G255 B255 | Default backgrounds, text on dark backgrounds |
| **Dark Grey** | #444444 | R68 G68 B68 | Body text, headers |

### Primary Colors (Dark) - For Emphasis

- **Dark Teal**: #008682
- **Navy Blue**: #31404E
- **Deep Blue**: #1D262F

### Neutral Colors - Supporting Elements

**Dark Shades**: #1C262F, #32404E, #4C5864
**Light Shades**: #A2A4A4, #B2B7BD, #E5E7E9

### Secondary Colors - Accents Only

- **Blue**: #1B9BC2
- **Coral**: #EE6969
- **Gold**: #F7BD63
- **Purple**: #A06ACD

### Gradient Options

**Primary Gradients** (Preferred):
- Teal to Blue: #00B5AD → #1B9BC2
- Dark Teal to Teal: #008682 → #00B5AD
- Teal to White: #00B5AD → #FFFFFF

**Secondary Gradients** (Use sparingly):
- Coral to Gold: #EE6969 → #F7BD63
- Coral to Purple: #EE6969 → #A06ACD

### Color Usage Rules

✅ **DO**:
- Use white (#FFFFFF) as the primary background color
- Apply teal (#00B5AD) for primary accents and emphasis
- Use dark grey (#444444) for body text
- Maintain consistent colors for same variables across all visualizations
- Use grey (#A2A4A4) to de-emphasize less important elements

❌ **DON'T**:
- Use more than 4 colors in a single chart or visualization
- Use off-brand colors without marketing approval
- Place elements on low-contrast backgrounds
- Mix color schemes inconsistently

---

## Typography Guidelines

### CRITICAL: Font Usage Rules

**⚠️ NEVER use Ostrich Sans in content** - It is ONLY for the logo wordmark!

### Approved Fonts for Content

#### Body Text
- **Font**: Lato Light
- **Size**: 14-18pt for paragraphs
- **Color**: #444444 (dark grey)
- **Line Spacing**: 1.2-1.5

#### Headers/Titles
- **Font**: Lato Regular or Lato Light
- **Sizes**:
  - Main titles: 32-44pt
  - Section headers: 24-32pt
  - Subsection headers: 20-24pt
- **Color**: #444444 or #00B5AD (teal)

#### Emphasis Text
- **Font**: Lato Bold
- **Usage**: Sparingly for key points only
- **Don't overuse**: Bold should highlight critical information

#### Italics
- **Font**: Lato Light Italic
- **Usage**: Quotes, references, definitions

### Typography Hierarchy Example

```
Main Title - Lato Regular, 36pt, #00B5AD
Section Header - Lato Regular, 28pt, #444444
Body Text - Lato Light, 16pt, #444444
Bullet Points - Lato Light, 14pt, #444444
Emphasis - Lato Bold, 16pt, #00B5AD
Captions - Lato Light, 12pt, #A2A4A4
```

### Typography Best Practices

✅ **DO**:
- Use Lato font family exclusively for all content
- Maintain minimum 14pt font size for readability
- Keep line spacing at 1.2-1.5 for body text
- Use consistent font sizes for same content types

❌ **DON'T**:
- Use Ostrich Sans in slides, reports, or any content (logo only!)
- Mix multiple font families
- Use font sizes below 14pt
- Use all caps except for acronyms
- Apply excessive bold or italic styling

---

## Logo Usage

### Master Logo Specifications

**File Formats**: JPG, PNG, EPS, SVG

**Minimum Width**: 190px (no maximum)

**Clear Space**: 1.5x the diameter of the teal plus sign on all sides

**Preferred Placement**:
- Top left corner (most common)
- Top right corner (alternative)
- Bottom right corner (for continuous branding)

### Logo Variations

1. **Black Logo + Teal Plus** - PRIMARY for white backgrounds
2. **White Logo + Teal Plus** - PREFERRED for dark backgrounds
3. **All White Logo** - Use only when necessary on teal/dark backgrounds

### Available Logo Assets

The plugin includes official FeedMob logo files in the `assets/logos/` directory:

**Logo Files**:
- `feedmob-logo-black-teal.svg` - Black text + teal plus (for white backgrounds)
- `feedmob-logo-white-teal.svg` - White text + teal plus (for dark backgrounds)
- `feedmob-plus-icon-teal.svg` - Standalone teal plus icon (design element)

**Usage in Content Generation**:

When creating FeedMob-branded content, reference these logo files using their absolute path:

```python
# Example: Using logo in Python/PowerPoint generation
logo_path = os.path.join(PLUGIN_ROOT, "assets/logos/feedmob-logo-black-teal.svg")

# For white backgrounds (most common)
logo_file = "assets/logos/feedmob-logo-black-teal.svg"

# For dark/teal backgrounds
logo_file = "assets/logos/feedmob-logo-white-teal.svg"

# For design elements (plus icon only)
plus_icon = "assets/logos/feedmob-plus-icon-teal.svg"
```

**Selection Guidelines**:
- **White background** → Use `feedmob-logo-black-teal.svg`
- **Dark/teal background** → Use `feedmob-logo-white-teal.svg`
- **Decorative element** → Use `feedmob-plus-icon-teal.svg`

**Integration with Tools**:
- When using SVG format, ensure proper scaling while maintaining aspect ratio
- Minimum display width: 190px
- Maximum width: No limit, but keep proportional to content
- Always maintain 1.5x clear space around the logo

### Plus Sign as Design Element

The teal plus sign can be used as a supplemental design element:
- **Minimum Width**: 90px
- **Spacing**: Equal to the size of the plus sign itself
- **Usage**: Section markers, visual accents
- **Approval**: Requires marketing approval for standalone use

### Logo Restrictions

❌ **NEVER**:
- Use logo on low-contrast backgrounds
- Apply off-brand colors to the logo
- Show wordmark without the plus sign
- Modify, recreate, or edit the logo
- Stretch or distort the logo
- Add effects (shadows, glows, 3D, outlines)
- Place logo in areas without sufficient clear space

---

## Data Visualization Guidelines

### Chart Design Principles

**From Official Brand Guidelines**:

1. **Font**: Always use Lato (never Ostrich Sans)
2. **Colors**: Use on-brand colors only from the approved palette
3. **Consistency**: Same colors for same variables across ALL charts
4. **Simplicity**: Maximum 4 colors per chart
5. **Clarity**: Use grey for less important elements

### Chart-Specific Rules

#### Line Charts
- **Use for**: Time series data ONLY
- **Don't use for**: Category comparisons
- ✅ Correct: "Revenue Over Time", "User Growth Trend"
- ❌ Incorrect: "Revenue by Product Category"

#### Bar Charts (Horizontal)
- **Use for**: Long labels, category comparisons
- **When**: Labels are 10+ characters
- ✅ Correct: Categories like "Customer Acquisition Cost", "Return on Investment"
- ❌ Incorrect: Short labels like "Q1", "Q2", "Q3"

#### Column Charts (Vertical)
- **Use for**: Short labels, category comparisons
- **When**: Labels are brief
- ✅ Correct: "Q1", "Q2", "Q3", "Product A", "Product B"
- ❌ Incorrect: Long multi-word category names

#### Pie Charts
- **Maximum**: 4 segments only
- **Labels**: Clear, positioned outside the pie
- **Colors**: Use brand colors (teal, blue, coral, gold)
- **When**: Showing parts of a whole, percentage breakdowns

### Color Mapping for Charts

**Establish consistent mapping across all visualizations**:

```
Primary Metric/Category A → Always #00B5AD (Teal)
Secondary Metric/Category B → Always #1B9BC2 (Blue)
Third Metric/Category C → Always #EE6969 (Coral)
Fourth Metric/Category D → Always #F7BD63 (Gold)
Background/Less Important → #A2A4A4 (Grey)
```

### Chart Typography Specifications

- **Chart Title**: Lato Regular, 24pt, #444444
- **Axis Labels**: Lato Light, 14pt, #444444
- **Data Labels**: Lato Light, 12pt, #444444
- **Legend**: Lato Light, 14pt, #444444

### Data Visualization Best Practices

✅ **DO**:
- Use same colors for same variables across entire presentation/document
- Include clear title and axis labels
- Add 1-2 sentence insight below charts
- Use grey to de-emphasize benchmarks or less critical data
- Keep visualizations simple and focused
- Ensure proper chart type matches data type

❌ **DON'T**:
- Use more than 4 colors in a single chart
- Mix chart types unnecessarily
- Use off-brand colors
- Create overly complex visualizations
- Use column charts for long labels (use horizontal bars)
- Use line charts for non-time-series data

---

## Report & Document Guidelines

### Document Structure

**Standard Layout**:
- **Page Size**: A4 or US Letter
- **Margins**:
  - Top: 60px (0.83 inches)
  - Bottom: 60px (0.83 inches)
  - Left: 80px (1.11 inches)
  - Right: 80px (1.11 inches)
- **Grid System**: 12-column grid with 20px gutters

### Report Sections

1. **Cover Page**
   - FeedMob logo (top left, 190px+ width)
   - Report title: Lato Regular, 44pt, #00B5AD
   - Subtitle/date: Lato Light, 20pt, #444444
   - White background with optional teal accent shapes

2. **Table of Contents**
   - Lato Regular for section names, 16pt
   - Lato Light for page numbers, 14pt
   - Teal (#00B5AD) line separators

3. **Section Headers**
   - Lato Regular, 32pt, #444444
   - Optional teal accent bar on left side

4. **Body Content**
   - Lato Light, 16pt, #444444
   - Line spacing: 1.5
   - Headings: Lato Regular, 24pt

5. **Data Sections**
   - Follow chart design principles
   - Include insights below visualizations
   - Maintain consistent color mapping

### Document Best Practices

✅ **DO**:
- Use white backgrounds as primary choice
- Apply ample white space (20% minimum margins)
- Include FeedMob logo on first page/header
- Spell company name as "FeedMob" (F and M capitalized)
- Use high-quality, diverse imagery
- Include page numbers (bottom right, Lato Light, 10pt, #A2A4A4)

❌ **DON'T**:
- Overcrowd pages with content
- Use decorative fonts
- Misspell "FeedMob" (not: Feedmob, feedmob, Feed Mob)
- Include unapproved imagery
- Use more than 3 font sizes per page type

---

## Image Guidelines

### Photography Style

**Requirements from Brand Guidelines**:

1. **Modern Action Shots**
   - Feature prospective audience and partners
   - Show people using mobile devices
   - Professional business settings
   - Natural, authentic moments

2. **Diversity & Inclusion**
   - Diverse individuals (ethnicity, age, gender)
   - Multicultural representation
   - Various demographics
   - Inclusive imagery

3. **Technical Quality**
   - Professional photography
   - Good lighting and composition
   - High resolution (minimum 1920x1080px for full-page)
   - Optimized file sizes

### Recommended Image Types

- Business professionals in modern offices
- People using mobile technology
- Team collaboration scenes
- Remote work environments
- Industry events and conferences
- Mobile app screenshots on actual devices
- Clean product shots of devices

### Image Technical Specifications

- **Format**: JPG, PNG
- **Resolution**: Minimum 1920x1080px for full-page images
- **Aspect Ratio**: 16:9 preferred
- **File Size**: Optimize for documents (<5MB per image)
- **Device Imagery**: Use most up-to-date, culturally relevant devices

---

## Presentation Guidelines

### Slide Design Standards

**Dimensions**: Standard 16:9 (1920 x 1080px)

**Slide Types**:

1. **Title Slide**
   - White background with teal accent shapes
   - Title: Lato Regular, 44pt, #00B5AD
   - Subtitle: Lato Light, 20pt, #444444
   - Logo: Top left, 100-120px width

2. **Section Divider**
   - Teal background (#00B5AD) or gradient
   - Section title: Lato Regular, 52pt, white
   - Optional plus sign icon
   - No logo required

3. **Content Slide**
   - White background
   - Title: Lato Regular, 36pt, #444444
   - Body: Lato Light, 16pt, #444444
   - Logo: Top left, 100-120px width
   - Maximum 5 bullet points per slide

4. **Data Visualization Slide**
   - Title: Lato Regular, 24pt, #444444
   - Chart: Full width, following chart guidelines
   - Insight: 1-2 sentences below chart, Lato Light, 14pt

5. **Image Slide**
   - Full-width high-quality image
   - Caption: Lato Light, 14pt, #444444 (optional)
   - Logo: Top left

### Presentation Best Practices

✅ **DO**:
- Maintain consistent logo placement
- Use white backgrounds as primary choice
- Limit bullet points to 3-5 per slide
- Keep slides simple and focused
- Apply brand colors to all charts
- Include ample white space

❌ **DON'T**:
- Exceed 5-7 lines of text per slide
- Use Ostrich Sans in slide content
- Overcrowd slides with information
- Use more than 4 colors in visualizations

### When Creating Presentations

**If using the feedmob-presentations skill**:
- Automatically apply `color_scheme: "feedmob"`
- Enable FeedMob branding features
- Follow the slide layout specifications above
- Ensure all typography uses Lato font family
- Apply proper logo placement and sizing

---

## Artifact Creation Guidelines

When creating artifacts (HTML, Markdown, or other formats):

### HTML Artifacts

**Typography**:
```css
font-family: 'Lato', sans-serif;
```

**Color Variables**:
```css
--feedmob-teal: #00B5AD;
--feedmob-dark-grey: #444444;
--feedmob-white: #FFFFFF;
--feedmob-blue: #1B9BC2;
--feedmob-coral: #EE6969;
--feedmob-gold: #F7BD63;
```

**Layout**:
- Use clean, modern layouts
- Maintain 20% minimum margins
- Apply responsive design principles
- Include FeedMob logo in header

### Markdown Reports

**Structure**:
```markdown
# Report Title (Lato Regular equivalent)

**Date**: YYYY-MM-DD
**Prepared by**: [Name]

---

## Section 1 (Lato Regular)

Body text in regular weight (Lato Light equivalent)...

### Subsection (Lato Regular, smaller)

- Bullet point 1
- Bullet point 2

**Key Insight** (Lato Bold): Important finding...
```

**Color References** (for web-rendered Markdown):
- Use inline HTML for colored text when needed
- Apply `color: #00B5AD` for emphasis
- Use `color: #444444` for body text

---

## Quality Checklist

Before finalizing any FeedMob-branded content:

### Brand Compliance
- [ ] Logo used correctly (size, placement, clear space)
- [ ] Only Lato font family used (NO Ostrich Sans in content)
- [ ] Brand colors applied consistently
- [ ] "FeedMob" spelled correctly throughout
- [ ] All charts use brand colors with consistent mapping

### Design Quality
- [ ] Consistent spacing and alignment
- [ ] Adequate white space (20% minimum margins)
- [ ] No pages/slides overcrowded with content
- [ ] Images are high quality and relevant
- [ ] Visual hierarchy is clear

### Content Quality
- [ ] All sections have clear titles
- [ ] Maximum 5-7 lines of text per page/slide section
- [ ] Bullet points are concise
- [ ] Data visualizations are accurate
- [ ] No spelling or grammatical errors

### Technical Quality
- [ ] File size optimized
- [ ] Fonts embedded (if applicable)
- [ ] Images properly compressed
- [ ] Proper file naming convention

### Accessibility
- [ ] Sufficient color contrast (4.5:1 minimum)
- [ ] Font sizes readable (14pt minimum)
- [ ] Alt text added to images (where applicable)
- [ ] Clear reading order established

---

## Integration with Other Skills

### Using with feedmob-presentations

When creating PowerPoint presentations, automatically invoke the feedmob-presentations skill with FeedMob settings:

```bash
python scripts/create_ppt.py --output presentation.pptx --color-scheme feedmob --title "Presentation Title"
```

**Ensure**:
- Color scheme is set to "feedmob"
- Lato font is used throughout
- Logo placement follows guidelines
- Slides follow the layout specifications

### Creating Charts

When generating charts (via any method):
1. Use FeedMob color palette only
2. Apply Lato font to all text
3. Maintain consistent color mapping
4. Include insights below visualizations
5. Keep to maximum 4 colors per chart

---

## File Naming Convention

**Format**: `YYYY-MM-DD_FeedMob_[Type]_[Topic]_v[Version].ext`

**Examples**:
- `2025-01-15_FeedMob_Report_Q1Analysis_v1.pdf`
- `2025-02-03_FeedMob_Presentation_ProductDemo_v2.pptx`
- `2025-03-20_FeedMob_Chart_UserGrowth_v1.png`

---

## Approval Process

**For External Content**:
- All external presentations require marketing approval
- Email: marketing@feedmob.com
- Custom designs need pre-approval

**For Internal Content**:
- Follow brand guidelines strictly
- Request asset files from marketing team if needed
- Submit questions to marketing@feedmob.com

---

## Essential Rules Summary

1. **Always** use Lato font (NEVER Ostrich Sans in content)
2. **Always** use white backgrounds as default
3. **Always** apply teal (#00B5AD) as primary accent color
4. **Always** maintain clear space around logo (1.5x plus sign diameter)
5. **Always** use brand colors in charts with consistent mapping
6. **Always** spell as "FeedMob" (F and M capitalized)
7. **Never** modify or distort the logo
8. **Never** use more than 4 colors in a single chart
9. **Never** overcrowd pages/slides with content
10. **Never** use off-brand colors without marketing approval

---

## Output

When this skill is invoked:
- All generated content will follow FeedMob brand guidelines
- Typography will use Lato font family exclusively
- Colors will be applied from the approved palette
- Layouts will maintain proper spacing and hierarchy
- Logo usage will comply with official specifications
- Charts and visualizations will follow data viz guidelines
- Final output will be professional, polished, and on-brand

---

**Document Reference**: Based on FeedMob Brand Guidelines 2025
**Last Updated**: December 2025
**For Questions**: marketing@feedmob.com
