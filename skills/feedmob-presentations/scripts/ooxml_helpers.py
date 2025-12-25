#!/usr/bin/env python3
"""
OOXML Helper Scripts for PowerPoint Manipulation
Provides utilities for unpacking, editing, and repacking PPTX files.
"""

import os
import sys
import json
import zipfile
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
import argparse


# XML Namespaces
NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types'
}

# Register namespaces for output
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


class PPTXManager:
    """Manage PPTX files via OOXML manipulation."""

    def __init__(self, pptx_path: str):
        self.pptx_path = Path(pptx_path)
        self.extract_dir = None

    def unpack(self, output_dir: Optional[str] = None) -> Path:
        """Unpack PPTX file to directory."""
        if output_dir:
            self.extract_dir = Path(output_dir)
        else:
            self.extract_dir = Path(f"{self.pptx_path.stem}_unpacked")

        # Remove existing directory
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)

        # Extract ZIP
        with zipfile.ZipFile(self.pptx_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_dir)

        print(f"✓ Unpacked to: {self.extract_dir}")
        return self.extract_dir

    def repack(self, output_path: Optional[str] = None) -> Path:
        """Repack directory to PPTX file."""
        if not self.extract_dir or not self.extract_dir.exists():
            raise ValueError("No extracted directory found. Unpack first.")

        if output_path:
            output = Path(output_path)
        else:
            output = self.pptx_path.parent / f"{self.pptx_path.stem}_modified.pptx"

        # Remove existing file
        if output.exists():
            output.unlink()

        # Create ZIP
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.extract_dir):
                # Skip system files
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]

                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.extract_dir)
                    zipf.write(file_path, arcname)

        print(f"✓ Repacked to: {output}")
        return output

    def get_slide_paths(self) -> List[Path]:
        """Get all slide XML file paths."""
        if not self.extract_dir:
            raise ValueError("Unpack PPTX first")

        slides_dir = self.extract_dir / 'ppt' / 'slides'
        if not slides_dir.exists():
            return []

        return sorted([f for f in slides_dir.glob('slide*.xml')])

    def extract_text_from_slide(self, slide_path: Path) -> List[str]:
        """Extract all text from a slide."""
        tree = ET.parse(slide_path)
        root = tree.getroot()

        texts = []
        for text_elem in root.findall('.//a:t', NS):
            if text_elem.text:
                texts.append(text_elem.text)

        return texts

    def replace_text_in_slide(self, slide_path: Path, old_text: str, new_text: str) -> int:
        """Replace text in a slide. Returns number of replacements."""
        tree = ET.parse(slide_path)
        root = tree.getroot()

        count = 0
        for text_elem in root.findall('.//a:t', NS):
            if text_elem.text and old_text in text_elem.text:
                text_elem.text = text_elem.text.replace(old_text, new_text)
                count += 1

        if count > 0:
            tree.write(slide_path, encoding='utf-8', xml_declaration=True)

        return count

    def get_slide_order(self) -> List[Dict]:
        """Get current slide order from presentation.xml."""
        if not self.extract_dir:
            raise ValueError("Unpack PPTX first")

        pres_path = self.extract_dir / 'ppt' / 'presentation.xml'
        tree = ET.parse(pres_path)
        root = tree.getroot()

        slides = []
        for sld_id in root.findall('.//p:sldId', NS):
            slide_info = {
                'id': sld_id.get('id'),
                'r_id': sld_id.get('{%s}id' % NS['r'])
            }
            slides.append(slide_info)

        return slides

    def inventory_text(self) -> Dict:
        """Create inventory of all text in presentation."""
        if not self.extract_dir:
            raise ValueError("Unpack PPTX first")

        inventory = {}
        for slide_path in self.get_slide_paths():
            slide_num = slide_path.stem.replace('slide', '')
            texts = self.extract_text_from_slide(slide_path)
            inventory[f"slide{slide_num}"] = texts

        return inventory


def unpack_command(args):
    """Unpack PPTX file."""
    manager = PPTXManager(args.input)
    output_dir = manager.unpack(args.output)
    print(f"\nUnpacked structure:")
    os.system(f"tree -L 2 {output_dir}")


def repack_command(args):
    """Repack directory to PPTX."""
    manager = PPTXManager(args.original)
    manager.extract_dir = Path(args.directory)
    output_path = manager.repack(args.output)
    print(f"\nValidating...")
    os.system(f"unzip -t {output_path}")


def inventory_command(args):
    """Create text inventory."""
    manager = PPTXManager(args.input)
    manager.unpack()

    inventory = manager.inventory_text()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
        print(f"✓ Inventory saved to: {args.output}")
    else:
        print(json.dumps(inventory, indent=2, ensure_ascii=False))


def replace_command(args):
    """Replace text across all slides."""
    manager = PPTXManager(args.input)
    manager.unpack()

    total_replacements = 0
    for slide_path in manager.get_slide_paths():
        count = manager.replace_text_in_slide(slide_path, args.old, args.new)
        if count > 0:
            print(f"✓ {slide_path.name}: {count} replacement(s)")
            total_replacements += count

    if total_replacements > 0:
        output_path = manager.repack(args.output)
        print(f"\n✓ Total replacements: {total_replacements}")
    else:
        print(f"\n⚠ No matches found for '{args.old}'")


def validate_command(args):
    """Validate PPTX structure."""
    manager = PPTXManager(args.input)
    manager.unpack()

    print("Validating PPTX structure...\n")

    # Check key files exist
    key_files = [
        '[Content_Types].xml',
        'ppt/presentation.xml',
        'ppt/_rels/presentation.xml.rels'
    ]

    issues = []
    for file in key_files:
        file_path = manager.extract_dir / file
        if not file_path.exists():
            issues.append(f"✗ Missing: {file}")
        else:
            print(f"✓ Found: {file}")

    # Check slide consistency
    slides = manager.get_slide_paths()
    print(f"\n✓ Found {len(slides)} slides")

    slide_order = manager.get_slide_order()
    print(f"✓ Presentation.xml references {len(slide_order)} slides")

    if len(slides) != len(slide_order):
        issues.append(f"✗ Mismatch: {len(slides)} slide files but {len(slide_order)} references")

    # Report
    print("\n" + "="*50)
    if issues:
        print("VALIDATION FAILED:")
        for issue in issues:
            print(issue)
        return 1
    else:
        print("✓ VALIDATION PASSED")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='OOXML Helper Tools for PowerPoint',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Unpack command
    unpack_parser = subparsers.add_parser('unpack', help='Unpack PPTX file')
    unpack_parser.add_argument('input', help='Input PPTX file')
    unpack_parser.add_argument('-o', '--output', help='Output directory')

    # Repack command
    repack_parser = subparsers.add_parser('repack', help='Repack directory to PPTX')
    repack_parser.add_argument('directory', help='Unpacked directory')
    repack_parser.add_argument('original', help='Original PPTX file (for reference)')
    repack_parser.add_argument('-o', '--output', help='Output PPTX file')

    # Inventory command
    inventory_parser = subparsers.add_parser('inventory', help='Create text inventory')
    inventory_parser.add_argument('input', help='Input PPTX file')
    inventory_parser.add_argument('-o', '--output', help='Output JSON file')

    # Replace command
    replace_parser = subparsers.add_parser('replace', help='Replace text in all slides')
    replace_parser.add_argument('input', help='Input PPTX file')
    replace_parser.add_argument('old', help='Text to replace')
    replace_parser.add_argument('new', help='Replacement text')
    replace_parser.add_argument('-o', '--output', help='Output PPTX file')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate PPTX structure')
    validate_parser.add_argument('input', help='Input PPTX file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == 'unpack':
        return unpack_command(args)
    elif args.command == 'repack':
        return repack_command(args)
    elif args.command == 'inventory':
        return inventory_command(args)
    elif args.command == 'replace':
        return replace_command(args)
    elif args.command == 'validate':
        return validate_command(args)


if __name__ == '__main__':
    sys.exit(main() or 0)
