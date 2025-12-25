# Office Open XML (OOXML) for PowerPoint

This guide covers the OOXML structure and operations for directly manipulating PowerPoint presentations at the XML level.

## Overview

PowerPoint (.pptx) files are ZIP archives containing XML files and resources. This structure enables:
- Direct content manipulation
- Slide management operations
- Advanced customization beyond library capabilities
- Debugging and validation

**Warning**: Incorrect OOXML implementation creates invalid files that PowerPoint cannot open. Always validate changes.

## PPTX Archive Structure

```
presentation.pptx (ZIP archive)
├── [Content_Types].xml          # File type declarations
├── _rels/
│   └── .rels                    # Root relationships
├── docProps/
│   ├── app.xml                  # Application metadata
│   └── core.xml                 # Core properties
└── ppt/
    ├── presentation.xml         # Main presentation structure
    ├── _rels/
    │   └── presentation.xml.rels # Slide relationships
    ├── slides/
    │   ├── slide1.xml           # Slide content
    │   ├── slide2.xml
    │   └── _rels/
    │       ├── slide1.xml.rels  # Slide-specific relationships
    │       └── slide2.xml.rels
    ├── slideLayouts/
    │   └── slideLayout*.xml     # Layout templates
    ├── slideMasters/
    │   └── slideMaster*.xml     # Master slides
    ├── theme/
    │   └── theme*.xml           # Theme definitions
    └── media/
        ├── image1.png           # Embedded images
        └── image2.jpg
```

## Basic Operations

### Unpacking PPTX

```bash
# Extract all files
unzip presentation.pptx -d unpacked_pptx/

# View structure
cd unpacked_pptx/
tree
```

### Repacking PPTX

```bash
# Navigate to unpacked directory
cd unpacked_pptx/

# Create new PPTX (exclude system files)
zip -r ../modified.pptx * -x "*.DS_Store" -x "__MACOSX/*"

# Important: Maintain directory structure exactly
```

### Validation

After modification, validate:
1. Open in PowerPoint - Does it load?
2. Check relationships - Are all references valid?
3. Verify Content_Types - Are all files declared?
4. Test compatibility - Works in PowerPoint, LibreOffice, Google Slides?

## Key XML Files

### presentation.xml

Controls slide order and IDs:

```xml
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId2"/>
    <p:sldId id="257" r:id="rId3"/>
    <p:sldId id="258" r:id="rId4"/>
  </p:sldIdLst>
</p:presentation>
```

**Operations**:
- Reorder slides: Change `<p:sldId>` sequence
- Delete slides: Remove `<p:sldId>` entry
- Unique IDs: Each slide needs unique `id` attribute

### slide.xml

Contains slide content:

```xml
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <!-- Shapes, text boxes, images go here -->
      <p:sp>
        <p:txBody>
          <a:p>
            <a:r>
              <a:t>Slide Title</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>
```

**Key Elements**:
- `<p:sp>`: Shape (text box, title, etc.)
- `<p:txBody>`: Text container
- `<a:p>`: Paragraph
- `<a:r>`: Text run
- `<a:t>`: Actual text content

### [Content_Types].xml

Declares all file types:

```xml
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Default Extension="jpeg" ContentType="image/jpeg"/>

  <Override PartName="/ppt/slides/slide1.xml"
            ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
  <Override PartName="/ppt/slides/slide2.xml"
            ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
</Types>
```

**Critical**: Every slide and resource must be declared here.

### Relationship Files

`ppt/_rels/presentation.xml.rels`:

```xml
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
                Target="slides/slide1.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
                Target="slides/slide2.xml"/>
</Relationships>
```

**Important**: Relationship IDs (`rId*`) must match references in presentation.xml.

## Common OOXML Operations

### 1. Rearrange Slides

Edit `ppt/presentation.xml`:

```xml
<!-- Before: Original order -->
<p:sldIdLst>
  <p:sldId id="256" r:id="rId2"/>  <!-- Slide 1 -->
  <p:sldId id="257" r:id="rId3"/>  <!-- Slide 2 -->
  <p:sldId id="258" r:id="rId4"/>  <!-- Slide 3 -->
</p:sldIdLst>

<!-- After: Reordered (Slide 3, Slide 1, Slide 2) -->
<p:sldIdLst>
  <p:sldId id="258" r:id="rId4"/>  <!-- Slide 3 now first -->
  <p:sldId id="256" r:id="rId2"/>  <!-- Slide 1 now second -->
  <p:sldId id="257" r:id="rId3"/>  <!-- Slide 2 now third -->
</p:sldIdLst>
```

### 2. Replace Text

Edit `ppt/slides/slide1.xml`:

```xml
<!-- Find text elements -->
<a:t>Old Title</a:t>

<!-- Replace with new text -->
<a:t>New Title</a:t>
```

**Tip**: Use `grep` to find text across all slides:

```bash
grep -r "Old Title" ppt/slides/
```

### 3. Duplicate Slide

1. Copy slide file:
```bash
cp ppt/slides/slide1.xml ppt/slides/slide4.xml
cp ppt/slides/_rels/slide1.xml.rels ppt/slides/_rels/slide4.xml.rels
```

2. Add to `presentation.xml`:
```xml
<p:sldId id="259" r:id="rId5"/>  <!-- New unique ID -->
```

3. Add relationship in `ppt/_rels/presentation.xml.rels`:
```xml
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
              Target="slides/slide4.xml"/>
```

4. Declare in `[Content_Types].xml`:
```xml
<Override PartName="/ppt/slides/slide4.xml"
          ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
```

### 4. Delete Slide

1. Remove from `presentation.xml`:
```xml
<!-- Delete this line -->
<p:sldId id="257" r:id="rId3"/>
```

2. Remove relationship from `ppt/_rels/presentation.xml.rels`:
```xml
<!-- Delete this line -->
<Relationship Id="rId3" ... Target="slides/slide2.xml"/>
```

3. Remove from `[Content_Types].xml`:
```xml
<!-- Delete this line -->
<Override PartName="/ppt/slides/slide2.xml" .../>
```

4. Delete slide files:
```bash
rm ppt/slides/slide2.xml
rm ppt/slides/_rels/slide2.xml.rels
```

5. Clean up unused media (if any):
- Check slide relationships for image references
- Remove orphaned images from `ppt/media/`

## Text Formatting

### Basic Formatting

```xml
<!-- Bold text -->
<a:r>
  <a:rPr b="1"/>
  <a:t>Bold Text</a:t>
</a:r>

<!-- Italic text -->
<a:r>
  <a:rPr i="1"/>
  <a:t>Italic Text</a:t>
</a:r>

<!-- Underline text -->
<a:r>
  <a:rPr u="sng"/>
  <a:t>Underlined Text</a:t>
</a:r>

<!-- Colored text -->
<a:r>
  <a:rPr>
    <a:solidFill>
      <a:srgbClr val="FF0000"/>  <!-- Red -->
    </a:solidFill>
  </a:rPr>
  <a:t>Red Text</a:t>
</a:r>

<!-- Font size (in points * 100) -->
<a:r>
  <a:rPr sz="2400"/>  <!-- 24pt = 2400 -->
  <a:t>Large Text</a:t>
</a:r>
```

### Lists

```xml
<!-- Bulleted list -->
<a:p>
  <a:pPr lvl="0">  <!-- Level 0 = first level -->
    <a:buChar char="•"/>
  </a:pPr>
  <a:r>
    <a:t>First bullet point</a:t>
  </a:r>
</a:p>

<!-- Nested bullet (indent level 1) -->
<a:p>
  <a:pPr lvl="1">  <!-- Level 1 = nested -->
    <a:buChar char="◦"/>
  </a:pPr>
  <a:r>
    <a:t>Nested bullet</a:t>
  </a:r>
</a:p>

<!-- Numbered list -->
<a:p>
  <a:pPr>
    <a:buAutoNum type="arabicPeriod"/>  <!-- 1. 2. 3. -->
  </a:pPr>
  <a:r>
    <a:t>First item</a:t>
  </a:r>
</a:p>
```

## Critical Rules

### Element Ordering

Text bodies must follow this order:
```xml
<p:txBody>
  <a:bodyPr/>      <!-- Body properties (FIRST) -->
  <a:lstStyle/>    <!-- List style (SECOND) -->
  <a:p>            <!-- Paragraphs (THIRD) -->
    <a:r>
      <a:t>Text</a:t>
    </a:r>
  </a:p>
</p:txBody>
```

**Wrong order causes corruption!**

### Whitespace Preservation

For text with leading/trailing spaces:
```xml
<a:t xml:space="preserve">  Text with spaces  </a:t>
```

### Special Characters

Escape special characters:
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&#34;` or `&quot;`
- `'` → `&#39;` or `&apos;`

### Clean State

Add to properties for clean state:
```xml
<a:rPr dirty="0"/>  <!-- Text run properties -->
<a:pPr dirty="0"/>  <!-- Paragraph properties -->
```

## Validation Checklist

Before repacking, verify:

- [ ] All slides referenced in `presentation.xml` exist
- [ ] All relationship IDs match between files
- [ ] All files declared in `[Content_Types].xml`
- [ ] No orphaned relationships or media files
- [ ] Unique slide IDs throughout presentation
- [ ] Proper XML element ordering
- [ ] Valid color codes (no `#` prefix in hex)
- [ ] Proper character escaping

## Debugging Tips

### File Won't Open

1. **Check ZIP integrity**:
```bash
unzip -t modified.pptx
```

2. **Validate XML syntax**:
```bash
xmllint --noout ppt/presentation.xml
xmllint --noout ppt/slides/*.xml
```

3. **Compare with working file**:
```bash
diff -r working_pptx/ broken_pptx/
```

### Missing Content

1. **Check Content_Types**: Is file declared?
2. **Check relationships**: Do IDs match?
3. **Check file paths**: Are paths correct (case-sensitive)?

### Corrupted Formatting

1. **Verify element order** in text bodies
2. **Check color codes** (no `#` prefix)
3. **Validate property attributes** (boolean values: 0 or 1)

## Advanced Techniques

### Batch Text Replacement

Python script for bulk replacements:

```python
import os
import re

def replace_text_in_slides(directory, old_text, new_text):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Replace text in <a:t> tags
                content = content.replace(f'<a:t>{old_text}</a:t>',
                                        f'<a:t>{new_text}</a:t>')

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

# Usage
replace_text_in_slides('unpacked_pptx/ppt/slides/', 'Old Company', 'New Company')
```

### Extract All Text

```bash
# Find all text content
grep -r '<a:t>' ppt/slides/ | sed 's/.*<a:t>\(.*\)<\/a:t>.*/\1/'
```

### List All Images

```bash
# Find all image relationships
grep -r 'image' ppt/slides/_rels/
```

## Resources

- [OOXML Specification](http://www.ecma-international.org/publications/standards/Ecma-376.htm)
- [PresentationML Reference](https://docs.microsoft.com/en-us/openspecs/office_standards/ms-pptx/)
- [Open XML SDK](https://github.com/OfficeDev/Open-XML-SDK)

## Summary

OOXML manipulation provides:
- ✅ Complete control over presentation structure
- ✅ Batch operations beyond library capabilities
- ✅ Debugging and validation tools
- ⚠️ Requires careful validation
- ⚠️ Easier to corrupt than high-level APIs

Use OOXML for operations that python-pptx cannot perform. For standard creation, prefer python-pptx.
