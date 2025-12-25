---
name: feedmob-presentations
description: Create, edit, and analyze PowerPoint presentations with professional styling, themes, and layouts. Supports python-pptx for creation and OOXML manipulation for advanced editing.
allowed-tools: Read, Write, Bash
---

# PPT Generator

This skill enables comprehensive PowerPoint presentation management through multiple approaches:

1. **Python-based Creation**: Use python-pptx library for programmatic generation with professional styling
2. **Direct OOXML Editing**: Unpack, modify XML content, and repack PPTX files for advanced control
3. **Template-based Workflow**: Leverage existing templates with content replacement

**PPTX files are ZIP archives containing XML files and resources.** This architecture enables both high-level creation and low-level manipulation.

## Core Capabilities

### Creating Presentations
- Generate from scratch with python-pptx
- Multiple color schemes (FeedMob, Binance, Professional, Modern, Corporate)
- Automatic background selection based on content
- Smart logo insertion for brand consistency
- Professional typography and layouts

### Editing Presentations
- Unpack PPTX to access raw XML
- Modify slide content, layouts, and structure
- Rearrange, duplicate, or delete slides
- Replace text and images programmatically
- Repack into valid PPTX format

### Analyzing Presentations
- Extract text content as markdown
- Access raw XML for comments and notes
- Examine slide layouts and structure
- Validate presentation integrity

## Instructions

When invoked, this skill will:

1. **Understand Requirements**: Analyze what presentation operation is needed
2. **Select Approach**: Choose creation, editing, or analysis workflow
3. **Apply Design Principles**: Use content-informed design with proper hierarchy
4. **Execute Operations**: Run appropriate tools (python-pptx, XML manipulation, etc.)
5. **Validate Output**: Ensure generated PPTX is valid and properly formatted

## Features

### Core Capabilities

- **Create new presentations**: Generate fresh PowerPoint files with professional styling
- **Multiple color schemes**: Choose from FeedMob, Binance (default), professional, modern, or corporate themes
- **FeedMob branding**: Native support for FeedMob color scheme with custom slide layouts
- **Footer logo**: Automatic FeedMob logo placement in footer (bottom-right) on every slide
- **Advanced layouts**: Create section headers, comparison slides, two-column layouts, metrics dashboards
- **Typography**: Professional fonts (Arial) with consistent sizing and colors
- **Image effects**: Add shadows, proper sizing, and positioning for images
- **Background styling**: Gradient backgrounds and image support for title slides
- **Professional templates**: Corporate-quality slide designs with company-specific styling

### NEW: Professional Design Principles Integration

#### Intelligent Background & Logo System
- **Automatic background selection**: Choose appropriate background images based on slide content keywords
- **Smart logo insertion**: Automatically add logos to slides without backgrounds for brand consistency
- **Content-aware matching**: Backgrounds selected by analyzing slide titles and content for context
- **Flexible control**: Enable/disable automatic backgrounds and logos via command line or JSON
- **Professional positioning**: Logos placed strategically (bottom-right by default) with transparency
- **Theme consistency**: Backgrounds and logos complement the chosen color scheme

#### Design Principles Implementation
- **6x6 Rule**: Automatically optimize content to maximum 6 lines per slide, 6 words per line
- **Typography Standards**: Title ≥28pt, Body ≥18pt with Arial sans-serif font
- **60-30-10 Color Rule**: 60% primary color, 30% secondary, 10% accent for visual harmony
- **Visual Hierarchy**: Automatic emphasis for first items, action words, and metrics with colors
- **Grid Alignment System**: 12x8 grid for precise element positioning and balance
- **White Space Optimization**: 20% minimum margins for improved readability
- **Content Simplification**: Automatic truncation of long text with ellipsis for clarity

### Background Selection Logic

The system intelligently selects backgrounds based on content:

- **Business/Professional**: Uses corporate-style backgrounds (bg4.jpg, bg5.jpg)
- **Technology/Digital**: Uses tech-themed backgrounds (bg2.png, bg3.png)
- **Analytics/Data**: Uses data-visualization backgrounds (bg3.png)
- **Marketing/Growth**: Uses marketing-focused backgrounds (bg1.jpg)
- **General Content**: Uses appropriate backgrounds for overviews, introductions, features, benefits

### Logo Features

**Important**: All FeedMob logo assets should be obtained from the `feedmob-brand-guidelines` skill, which contains official FeedMob logo files in its `assets/logos/` directory:
- `feedmob-logo-black-teal.svg` - Black text + teal plus (for white backgrounds)
- `feedmob-logo-white-teal.svg` - White text + teal plus (for dark backgrounds)
- `feedmob-plus-icon-teal.svg` - Standalone teal plus icon (design element)

**Footer Logo (Always Present)**:
- Automatically added to ALL slides in the footer area
- Position: Bottom-right corner (0.8x0.8 inches)
- Logo: Use FeedMob brand logo from feedmob-brand-guidelines skill
- Purpose: Consistent branding across entire presentation

**Content Logo (Optional)**:
- **Added to**: Content slides, comparison slides, visual content, two-column layouts
- **Not added to**: Title slides, section headers, metrics dashboards, slides with existing backgrounds
- **Positioning**: Bottom-right corner with subtle transparency
- **Selection**: Use appropriate logo from feedmob-brand-guidelines skill based on background color (when auto_logos enabled)

### Enhanced Slide Types

- **FeedMob title slides**: Gradient backgrounds with orange accent bars and 52pt white titles
- **FeedMob content slides**: Blue accent bar with gray title background and green bullet points
- **Professional title slides**: Solid color background with large 54pt titles (Binance style)
- **Visual content slides**: Bullet points with image support and colored accent bars
- **Metrics dashboard slides**: Grid layout with colorful KPI boxes (up to 4 metrics)
- **Content slides**: Professional bullet points with consistent styling
- **Section headers**: Eye-catching gradient backgrounds
- **Comparison slides**: Side-by-side content with colored backgrounds
- **Two-column slides**: Balanced content layout
- **Blank slides**: Canvas for custom layouts with shapes and text

### Supported Operations

- Apply professional color schemes (FeedMob, Binance, Professional, Modern, Corporate)
- Create FeedMob-branded title slides with gradient backgrounds
- Create FeedMob content slides with custom styling
- Create professional title slides with solid color backgrounds
- Create metrics dashboards with colorful KPI boxes
- Create visual content slides with images and accent bars
- Add section headers with gradient backgrounds
- Generate comparison and two-column layouts
- Style text with professional Arial fonts and colors
- Add images with shadow effects
- Create custom shapes with text
- Format text with consistent typography

## JSON Configuration (Enhanced)

The JSON format now supports automatic background and logo control:

```json
{
  "color_scheme": "feedmob",
  "auto_backgrounds": true,
  "auto_logos": true,
  "slides": [
    {
      "type": "title",
      "title": "Company Overview"
    },
    {
      "type": "content",
      "title": "Technology Features",
      "content": ["Cloud platform", "Real-time analytics", "Mobile support"]
    }
  ]
}
```

### JSON Options

- **auto_backgrounds** (boolean): Enable automatic background selection (default: true)
- **auto_logos** (boolean): Enable automatic logo insertion (default: true)

## Implementation

The skill uses Python with the python-pptx library to process PowerPoint files. Run the processing script:

```bash
python scripts/create_ppt.py [options]
```

### Script Usage

The script supports multiple ways to create presentations:

**1. Simple command-line creation:**
```bash
python scripts/create_ppt.py --output presentation.pptx --title "My Presentation"
```

**2. JSON-based content definition:**
```bash
python scripts/create_ppt.py --output presentation.pptx --json slides.json
```

**3. Enhanced command-line creation with color scheme:**
```bash
python scripts/create_ppt.py --output presentation.pptx --title "My Presentation" --color-scheme feedmob
```

**4. Presentation with background image:**
```bash
python scripts/create_ppt.py --output presentation.pptx --title "My Presentation" --background-image "bg.jpg"
```

**5. Presentation with automatic backgrounds and logos (NEW):**
```bash
python scripts/create_ppt.py --output presentation.pptx --title "My Presentation" --color-scheme feedmob
```

**6. Disable automatic backgrounds or logos:**
```bash
python scripts/create_ppt.py --output presentation.pptx --title "My Presentation" --no-auto-backgrounds
python scripts/create_ppt.py --output presentation.pptx --title "My Presentation" --no-auto-logos
```

The script will:
- Create a new PowerPoint presentation with professional styling
- Apply FeedMob or Binance color scheme by default (or selected alternative theme)
- **NEW**: Automatically select background images based on slide content (enabled by default)
- **NEW**: Automatically add logos to slides without backgrounds (enabled by default)
- Add slides with enhanced typography and layout
- Insert text and images with proper formatting
- Save the final .pptx file
- Handle errors gracefully with clear messages

## Usage Examples

**Create a FeedMob-branded presentation:**
```
Create a PowerPoint presentation about FeedMob platform using FeedMob color scheme
```

**Create a professional presentation:**
```
Create a PowerPoint presentation about project status (uses Binance style by default)
```

**Add slides with enhanced styling:**
```
Generate a PPT with title slide and 3 content slides about quarterly results (uses FeedMob styling)
```

**Create presentation with section headers:**
```
Make a PowerPoint from this outline: Introduction, Features, Benefits, Conclusion with section headers (uses FeedMob theme)
```

**Create comparison slides:**
```
Create a presentation comparing our product vs competitors using FeedMob colors
```

**Add images with effects:**
```
Create a FeedMob presentation and add the logo image to the title slide with shadow effects
```

## Requirements

- Python 3.6 or higher
- python-pptx library (>=0.6.21)
- Image files must exist at specified paths (for image insertion)

## Output

- A .pptx file saved to the specified location
- Standard PowerPoint format compatible with Microsoft PowerPoint, LibreOffice, and Google Slides
- Preserves all formatting and layout settings

## OOXML Direct Manipulation

For advanced editing beyond python-pptx capabilities, directly manipulate the OOXML structure:

### Unpacking PPTX
```bash
# PPTX files are ZIP archives
unzip presentation.pptx -d unpacked/
```

### Key OOXML Files
- `ppt/presentation.xml` - Slide order and IDs
- `ppt/slides/slide*.xml` - Individual slide content
- `ppt/slideLayouts/` - Layout templates
- `ppt/media/` - Embedded images
- `[Content_Types].xml` - File type declarations
- `ppt/_rels/presentation.xml.rels` - Slide relationships

### Common Operations

**Rearrange Slides**: Modify `<p:sldId>` sequence in `presentation.xml`

**Replace Text**: Edit text within `<a:t>` tags in slide XML files

**Duplicate Slides**: Copy slide XML and update IDs in relationships

**Delete Slides**: Remove references from presentation.xml, relationships, and Content_Types

### Repacking PPTX
```bash
cd unpacked/
zip -r ../modified.pptx * -x "*.DS_Store"
```

**Critical**: Validate OOXML structure before repacking. Incorrect XML causes corrupted files.

## Design Principles

Follow these principles for professional presentations:

### Content-Informed Design
- Design should serve content, not overshadow it
- Use strong visual hierarchy
- Maintain readable contrast (WCAG AA minimum)
- Use web-safe fonts (Arial, Helvetica, Times New Roman, Georgia)

### Typography Standards
- Title: ≥28pt for readability
- Body: ≥18pt minimum
- Consistent font family throughout
- Limited font variations (2-3 weights max)

### Color Guidelines
- **60-30-10 Rule**: 60% primary, 30% secondary, 10% accent
- Maximum 4 colors per chart
- Consistent color mapping across visualizations
- Test contrast ratios for accessibility

### Layout Optimization
- **6x6 Rule**: Max 6 lines per slide, 6 words per line
- **20% Margins**: Minimum white space for readability
- **Grid Alignment**: Use 12x8 grid for element positioning
- **Visual Balance**: Distribute weight evenly across slide

### Recommended Color Palettes

Choose palettes that match presentation tone:

**Professional Business**: Navy (#1a3a5c), Gray (#6b7280), Blue (#3b82f6)
**Technology**: Teal (#00B5AD), Purple (#8b5cf6), Cyan (#06b6d4)
**Corporate**: Charcoal (#374151), Gold (#f59e0b), White (#ffffff)
**Modern**: Black (#000000), Coral (#EE6969), Mint (#10b981)

## Best Practices

### Planning
- **Define Structure First**: Outline slide flow before detailed content
- **Content-Informed Design**: Let content guide design choices
- **Consistent Theme**: Maintain visual consistency throughout

### Implementation
- **Use Appropriate Tools**: python-pptx for creation, OOXML for complex edits
- **Validate Early**: Check output after each major change
- **Keep Text Concise**: Follow 6x6 rule for readability
- **Optimize Assets**: Compress images before insertion

### Quality Assurance
- **Test Compatibility**: Open in PowerPoint, LibreOffice, Google Slides
- **Check Accessibility**: Verify contrast ratios and font sizes
- **Validate OOXML**: Ensure no corrupted relationships or missing files
- **Review on Device**: Test on actual presentation display

## Requirements

**Python Environment**:
- Python 3.6+
- python-pptx >= 0.6.21

**Optional Tools**:
- markitdown (text extraction)
- unzip/zip (OOXML manipulation)
- LibreOffice (validation and conversion)

For OOXML manipulation details, see [REFERENCE.md](REFERENCE.md).



