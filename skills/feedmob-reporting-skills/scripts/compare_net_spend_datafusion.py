#!/usr/bin/env python3
"""
Dynamic DataFusion Python - Net Spend Comparison

Compares partner_net_spend (from partner reports) with feedmob_net_spend (from direct spends).
Unlike gross spend (which requires calculation), net spend is a direct comparison.

Works with all partner reports:
- Jampp, Kayzen, YouAppi, Samsung (1-step API)
- Smadex, InMobi, Liftoff (multi-step API)

Usage Examples:
    python3 compare_net_spend_datafusion.py \
        ./tmp/jampp_reports_2025-01-01_2025-01-31.csv \
        ./tmp/direct_spends_2025-01-01_2025-01-31.csv \
        ./tmp/net_spend_comparison.csv

    python3 compare_net_spend_datafusion.py \
        ./tmp/smadex_reports_2025-01-01_2025-01-31.csv \
        ./tmp/direct_spends_2025-01-01_2025-01-31.csv \
        ./tmp/net_spend_comparison.csv
"""

import sys
import csv
import subprocess
from pathlib import Path
from datetime import datetime


def check_and_install_dependencies():
    """Check and automatically install dependencies (from requirements.txt)"""
    missing_packages = []

    try:
        import datafusion
        print("✓ datafusion installed")
    except ImportError:
        missing_packages.append("datafusion")

    try:
        import pandas
        print("✓ pandas installed")
    except ImportError:
        missing_packages.append("pandas")

    try:
        import pyarrow
        print("✓ pyarrow installed")
    except ImportError:
        missing_packages.append("pyarrow")

    if missing_packages:
        print(f"⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Auto-installing from requirements.txt...")

        script_dir = Path(__file__).parent
        requirements_file = script_dir / "requirements.txt"

        if not requirements_file.exists():
            print(f"✗ requirements.txt not found: {requirements_file}")
            print("Please install manually: pip install datafusion pandas pyarrow --user")
            return False

        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file),
                "--user", "--quiet"
            ])
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file),
                    "--break-system-packages", "--quiet"
                ])
                print("✓ Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install dependencies: {e}")
                print(f"Please install manually: pip install -r {requirements_file} --user")
                print("Or use a virtual environment:")
                print("  python3 -m venv venv")
                print("  source venv/bin/activate")
                print(f"  pip install -r {requirements_file}")
                return False

    return True


def detect_partner_report_columns(csv_path):
    """Detect available columns in partner report CSV"""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames

    # Find key columns
    has_click_url_id = 'click_url_id' in columns
    has_partner_net_spend = 'partner_net_spend' in columns
    has_date = 'date' in columns

    # Look for other useful columns
    optional_columns = {
        'campaign_name': 'campaign_name' in columns,
        'vendor_name': 'vendor_name' in columns,
    }

    return columns, {
        'has_click_url_id': has_click_url_id,
        'has_partner_net_spend': has_partner_net_spend,
        'has_date': has_date,
        **optional_columns
    }


def create_empty_direct_spend_csv(output_path):
    """Create an empty direct spend CSV with proper headers"""
    headers = [
        'click_url_id', 'date', 'campaign_name',
        'feedmob_net_spend', 'feedmob_gross_spend'
    ]
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)


def validate_and_prepare_direct_spend_csv(direct_spend_csv):
    """Validate direct spend CSV, create empty one if missing or empty.
    Returns: 'empty', 'has_data'"""
    direct_spend_path = Path(direct_spend_csv)

    if not direct_spend_path.exists():
        print(f"⚠️  Direct spend file not found, creating empty file: {direct_spend_csv}")
        create_empty_direct_spend_csv(direct_spend_csv)
        return 'empty'

    with open(direct_spend_csv, 'r') as f:
        content = f.read().strip()
        if not content:
            print(f"⚠️  Direct spend file is empty, adding headers: {direct_spend_csv}")
            create_empty_direct_spend_csv(direct_spend_csv)
            return 'empty'

        lines = content.split('\n')
        if len(lines) <= 1:
            print(f"⚠️  Direct spend file has no data rows, using as-is: {direct_spend_csv}")
            return 'empty'

    print(f"✓ Direct spend file has {len(lines) - 1} data rows")
    return 'has_data'


def execute_query_and_save(partner_csv, direct_spend_csv, output_csv, column_info):
    """Execute DataFusion query and save results"""
    from datafusion import SessionContext

    # Create DataFusion session
    ctx = SessionContext()

    # Register CSV tables
    ctx.register_csv('partner_report', partner_csv, has_header=True)
    ctx.register_csv('direct_spend', direct_spend_csv, has_header=True)

    # Build dynamic column selection - use direct column reference since aggregated_partner already has the column
    campaign_name_expr = "p.campaign_name" if column_info.get('campaign_name') else "'Unknown'"
    vendor_name_expr = "p.vendor_name" if column_info.get('vendor_name') else "'Unknown'"

    # Build query - aggregate partner report by click_url_id and date
    # Include campaign_name and vendor_name in aggregation if available
    campaign_name_select = ", MAX(campaign_name) as campaign_name" if column_info.get('campaign_name') else ""
    vendor_name_select = ", MAX(vendor_name) as vendor_name" if column_info.get('vendor_name') else ""

    full_query = f"""
WITH aggregated_partner AS (
    SELECT
        date,
        CAST(click_url_id AS BIGINT) as click_url_id,
        SUM(CAST(COALESCE(partner_net_spend, 0) AS DOUBLE)) as partner_net_spend
        {campaign_name_select}
        {vendor_name_select}
    FROM partner_report
    WHERE click_url_id IS NOT NULL AND click_url_id != ''
    GROUP BY date, click_url_id
),
comparison AS (
    SELECT
        p.date,
        p.click_url_id,
        {campaign_name_expr} as campaign_name,
        {vendor_name_expr} as vendor_name,
        ROUND(p.partner_net_spend, 2) as partner_net_spend,
        ROUND(COALESCE(d.feedmob_net_spend, 0), 2) as feedmob_net_spend,
        ROUND(p.partner_net_spend - COALESCE(d.feedmob_net_spend, 0), 2) as difference,
        ROUND(
            CASE
                WHEN COALESCE(d.feedmob_net_spend, 0) > 0
                THEN ((p.partner_net_spend - COALESCE(d.feedmob_net_spend, 0)) / d.feedmob_net_spend * 100)
                ELSE 0
            END,
            2
        ) as difference_pct
    FROM aggregated_partner p
    LEFT JOIN direct_spend d
        ON CAST(p.click_url_id AS BIGINT) = CAST(d.click_url_id AS BIGINT)
        AND p.date = d.date
)
SELECT
    date,
    click_url_id,
    campaign_name,
    vendor_name,
    partner_net_spend,
    feedmob_net_spend,
    difference,
    difference_pct,
    CASE
        WHEN ABS(difference) < 0.01 THEN '✅ Perfect'
        WHEN ABS(difference_pct) < 2 THEN '⚠️ Minor'
        ELSE '🚨 Significant'
    END as status
FROM comparison
WHERE partner_net_spend > 0 OR feedmob_net_spend > 0
ORDER BY date, ABS(difference) DESC
"""

    # Execute query
    df = ctx.sql(full_query)

    # Convert to pandas and save as CSV
    pandas_df = df.to_pandas()
    pandas_df.to_csv(output_csv, index=False)

    return pandas_df


def generate_summary(df):
    """Generate summary statistics"""
    total_partner = df['partner_net_spend'].sum()
    total_feedmob = df['feedmob_net_spend'].sum()
    total_diff = df['difference'].sum()
    total_diff_pct = (total_diff / total_feedmob * 100) if total_feedmob > 0 else 0

    # Count by status
    status_counts = df['status'].value_counts().to_dict() if 'status' in df.columns else {}

    return {
        'total_partner': total_partner,
        'total_feedmob': total_feedmob,
        'total_diff': total_diff,
        'total_diff_pct': total_diff_pct,
        'row_count': len(df),
        'status_counts': status_counts
    }


def print_summary(summary):
    """Print summary report"""
    print("\n" + "="*60)
    print("Net Spend Comparison Summary")
    print("="*60)
    print()
    print(f"Total Partner Net Spend:    ${summary['total_partner']:,.2f}")
    print(f"Total FeedMob Net Spend:    ${summary['total_feedmob']:,.2f}")
    print(f"Total Difference:           ${summary['total_diff']:,.2f} ({summary['total_diff_pct']:.2f}%)")
    print()

    # Status breakdown
    status_counts = summary.get('status_counts', {})
    if status_counts:
        print("Status Breakdown:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        print()

    # Overall status
    abs_diff_pct = abs(summary['total_diff_pct'])
    if summary['row_count'] == 0 or (summary['total_partner'] == 0 and summary['total_feedmob'] == 0):
        status = "⚠️  No Data to Compare"
    elif abs_diff_pct < 0.01:
        status = "✅ Perfect Match"
    elif abs_diff_pct < 2:
        status = "⚠️  Minor Difference (<2%)"
    else:
        status = "🚨 Significant Difference (≥2%)"

    print(f"Overall Status: {status}")
    print()
    print(f"Rows Compared: {summary['row_count']}")
    print()


def main():
    """Main function"""
    if len(sys.argv) != 4:
        print("Usage: python3 compare_net_spend_datafusion.py <partner_report.csv> <direct_spend.csv> <output.csv>")
        sys.exit(1)

    partner_csv = sys.argv[1]
    direct_spend_csv = sys.argv[2]
    output_csv = sys.argv[3]

    # Validate partner report file
    print("Validating input files...")
    if not Path(partner_csv).exists():
        print(f"✗ Error: Partner report file not found: {partner_csv}")
        sys.exit(1)
    print("✓ Partner report file exists")

    # Handle direct spend file (can be missing or empty)
    direct_spend_status = validate_and_prepare_direct_spend_csv(direct_spend_csv)
    print()

    # Check and install dependencies
    if not check_and_install_dependencies():
        sys.exit(1)
    print()

    # Detect columns
    print("Detecting columns in partner report...")
    columns, column_info = detect_partner_report_columns(partner_csv)
    print(f"CSV Header: {', '.join(columns)}")
    print()

    if not column_info['has_click_url_id']:
        print("✗ Error: click_url_id column not found in partner report")
        sys.exit(1)
    if not column_info['has_partner_net_spend']:
        print("✗ Error: partner_net_spend column not found in partner report")
        sys.exit(1)

    print(f"✓ Required columns found: click_url_id, partner_net_spend")
    print()

    # Execute query
    print("Starting DataFusion Net Spend analysis...")
    print()

    try:
        df = execute_query_and_save(partner_csv, direct_spend_csv, output_csv, column_info)

        row_count = len(df)
        print(f"✓ Query executed successfully")
        print(f"✓ Report saved to: {output_csv}")
        print(f"✓ Processed {row_count} rows")

        # Generate summary
        summary = generate_summary(df)
        print_summary(summary)

        print("Done!")

    except Exception as e:
        print(f"✗ Error: Query execution failed")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
