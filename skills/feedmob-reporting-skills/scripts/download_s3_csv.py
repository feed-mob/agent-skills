#!/usr/bin/env python3
"""
Download CSV/ZIP file from S3 URL and save locally.

This script handles downloading data files from S3 URLs returned by
MCP tools like get_possible_finance_singular_reports. Automatically
extracts ZIP files if needed.

Usage:
    # Download from S3 URL
    python download_s3_csv.py "https://s3.amazonaws.com/..."

    # Specify output directory
    python download_s3_csv.py "https://s3.amazonaws.com/..." --output-dir ./tmp

    # From JSON with s3_url field
    python download_s3_csv.py --from-json '{"s3_url": "https://..."}'

    # From JSON file
    python download_s3_csv.py --from-json-file response.json

    # Keep ZIP file (don't extract)
    python download_s3_csv.py "https://s3.amazonaws.com/..." --keep-zip
"""

import json
import sys
import os
import argparse
import zipfile
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime
from pathlib import Path


def extract_zip(zip_path, output_dir=None):
    """
    Extract ZIP file to directory.

    Args:
        zip_path: Path to ZIP file
        output_dir: Directory to extract to (defaults to same dir as ZIP)

    Returns:
        List of extracted file paths
    """
    if output_dir is None:
        output_dir = os.path.dirname(zip_path)

    extracted_files = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files in ZIP
            file_list = zip_ref.namelist()

            # Extract all files
            for file_name in file_list:
                extracted_path = zip_ref.extract(file_name, output_dir)
                extracted_files.append(os.path.abspath(extracted_path))

        return {
            'success': True,
            'extracted_files': extracted_files,
            'count': len(extracted_files)
        }
    except zipfile.BadZipFile:
        return {
            'success': False,
            'error': 'Invalid ZIP file'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Extraction failed: {str(e)}'
        }


def download_file(url, output_dir=None, keep_zip=False, chunk_size=8192):
    """
    Download file from URL and save to local path. Auto-extracts ZIP files.

    Args:
        url: S3 URL to download from
        output_dir: Local directory to save to (optional, defaults to /tmp/)
        keep_zip: Keep ZIP file after extraction (default: False)
        chunk_size: Download chunk size in bytes

    Returns:
        Dictionary with download results and extracted files
    """
    # Determine output directory
    if not output_dir:
        output_dir = "/tmp"

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Extract filename from URL
    url_path = url.split('?')[0]  # Remove query params if any
    filename = os.path.basename(url_path)

    # Generate output path
    output_path = os.path.join(output_dir, filename)

    # If file exists, add timestamp
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        output_path = os.path.join(output_dir, filename)

    try:
        # Create request with headers
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')

        # Download file
        print(f"Downloading {filename}...", file=sys.stderr)
        with urlopen(req) as response:
            total_size = response.headers.get('Content-Length')
            downloaded = 0

            with open(output_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Print progress if size is known
                    if total_size:
                        progress = (downloaded / int(total_size)) * 100
                        print(f"\rDownloading: {progress:.1f}%", end='', file=sys.stderr)

        if total_size:
            print("\r", end='', file=sys.stderr)  # Clear progress line

        # Verify file was created
        if not os.path.exists(output_path):
            return {
                'success': False,
                'error': 'File was not created'
            }

        file_size = os.path.getsize(output_path)
        result = {
            'success': True,
            'downloaded_file': os.path.abspath(output_path),
            'size_bytes': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2),
            'file_type': 'zip' if filename.endswith('.zip') else 'csv'
        }

        # Auto-extract ZIP files
        if filename.endswith('.zip'):
            print(f"Extracting {filename}...", file=sys.stderr)
            extract_result = extract_zip(output_path, output_dir)

            if extract_result['success']:
                result['extracted_files'] = extract_result['extracted_files']
                result['extracted_count'] = extract_result['count']

                # Delete ZIP file unless keep_zip is True
                if not keep_zip:
                    os.remove(output_path)
                    result['zip_removed'] = True
                    print(f"Extracted {extract_result['count']} file(s)", file=sys.stderr)
                else:
                    result['zip_kept'] = True
                    print(f"Extracted {extract_result['count']} file(s), kept ZIP", file=sys.stderr)
            else:
                result['extraction_error'] = extract_result['error']
                print(f"Warning: {extract_result['error']}", file=sys.stderr)

        return result

    except HTTPError as e:
        return {
            'success': False,
            'error': f'HTTP Error {e.code}: {e.reason}',
            'url': url
        }
    except URLError as e:
        return {
            'success': False,
            'error': f'URL Error: {e.reason}',
            'url': url
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'url': url
        }


def extract_s3_url_from_json(json_data):
    """
    Extract s3_url from JSON response.

    Handles formats:
    - {"s3_url": "https://..."}
    - {"data": {"s3_url": "https://..."}}
    - {"singular_reports": [...], "s3_url": "https://..."}
    """
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    # Direct s3_url field
    if 's3_url' in json_data:
        return json_data['s3_url']

    # Nested in data
    if 'data' in json_data and isinstance(json_data['data'], dict):
        if 's3_url' in json_data['data']:
            return json_data['data']['s3_url']

    return None


def main():
    parser = argparse.ArgumentParser(
        description='Download CSV/ZIP file from S3 URL and auto-extract'
    )

    # Input methods
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        'url',
        nargs='?',
        help='S3 URL to download from'
    )
    input_group.add_argument(
        '--from-json',
        help='JSON string containing s3_url field'
    )
    input_group.add_argument(
        '--from-json-file',
        help='JSON file containing s3_url field'
    )

    # Output options
    parser.add_argument(
        '--output-dir', '-o',
        help='Output directory path (default: /tmp/)'
    )
    parser.add_argument(
        '--keep-zip',
        action='store_true',
        help='Keep ZIP file after extraction'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )

    args = parser.parse_args()

    # Redirect stderr if quiet mode
    if args.quiet:
        sys.stderr = open(os.devnull, 'w')

    # Extract URL
    url = None
    if args.url:
        url = args.url
    elif args.from_json:
        try:
            url = extract_s3_url_from_json(args.from_json)
        except json.JSONDecodeError as e:
            print(json.dumps({
                'success': False,
                'error': f'Invalid JSON: {e}'
            }))
            sys.exit(1)
    elif args.from_json_file:
        try:
            with open(args.from_json_file, 'r') as f:
                json_data = json.load(f)
                url = extract_s3_url_from_json(json_data)
        except FileNotFoundError:
            print(json.dumps({
                'success': False,
                'error': f'File not found: {args.from_json_file}'
            }))
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(json.dumps({
                'success': False,
                'error': f'Invalid JSON in file: {e}'
            }))
            sys.exit(1)

    if not url:
        print(json.dumps({
            'success': False,
            'error': 'No s3_url found in JSON data'
        }))
        sys.exit(1)

    # Download file
    result = download_file(url, args.output_dir, keep_zip=args.keep_zip)

    # Output result as JSON
    print(json.dumps(result, indent=2))

    if result['success']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
