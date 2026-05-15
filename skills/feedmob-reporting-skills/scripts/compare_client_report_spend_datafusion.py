#!/usr/bin/env python3
"""
Compare Client Report Spend vs Direct Spend (Gross)

Compares gross_spend from client_report_spends with feedmob_gross_spend from direct_spends.

Two comparison modes:
1. Click URL level: When client_report has click_url_id, join on click_url_id + date
2. Campaign level: When client_report has no click_url_id, aggregate by campaign_name

Usage:
    python3 compare_client_report_spend_datafusion.py \
        ./tmp/client_report_spends_possible_finance.csv \
        ./tmp/direct_spends.csv \
        ./tmp/client_report_comparison.csv
"""

import sys
import csv
import subprocess
from pathlib import Path


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
                return False

    return True


def detect_client_report_columns(csv_path):
    """Detect available columns in client report CSV"""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames

    has_click_url_id = 'click_url_id' in columns
    has_spend_date = 'spend_date' in columns
    has_gross_spend = 'gross_spend' in columns
    has_campaign_name = 'campaign_name' in columns
    has_vendor_name = 'vendor_name' in columns

    # Check if click_url_id has actual values (not all empty)
    has_click_url_data = False
    if has_click_url_id:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = row.get('click_url_id', '').strip()
                if val and val != '0':
                    has_click_url_data = True
                    break

    return columns, {
        'has_click_url_id': has_click_url_id,
        'has_click_url_data': has_click_url_data,
        'has_spend_date': has_spend_date,
        'has_gross_spend': has_gross_spend,
        'has_campaign_name': has_campaign_name,
        'has_vendor_name': has_vendor_name,
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


def execute_click_url_query(client_csv, direct_spend_csv, output_csv, column_info):
    """Execute comparison at click_url_id + date level"""
    from datafusion import SessionContext

    ctx = SessionContext()
    ctx.register_csv('client_report', client_csv, has_header=True)
    ctx.register_csv('direct_spend', direct_spend_csv, has_header=True)

    vendor_name_select = ", MAX(vendor_name) as vendor_name" if column_info.get('has_vendor_name') else ""

    query = f"""
WITH client_agg AS (
    SELECT
        spend_date as date,
        CAST(click_url_id AS BIGINT) as click_url_id,
        campaign_name,
        SUM(CAST(COALESCE(gross_spend, 0) AS DOUBLE)) as client_gross_spend
        {vendor_name_select}
    FROM client_report
    WHERE click_url_id IS NOT NULL AND click_url_id != ''
    GROUP BY spend_date, click_url_id, campaign_name
),
comparison AS (
    SELECT
        c.date,
        c.click_url_id,
        c.campaign_name,
        {"c.vendor_name," if column_info.get('has_vendor_name') else ""}
        ROUND(c.client_gross_spend, 2) as client_gross_spend,
        ROUND(COALESCE(d.feedmob_gross_spend, 0), 2) as feedmob_gross_spend,
        ROUND(COALESCE(d.feedmob_net_spend, 0), 2) as feedmob_net_spend,
        ROUND(c.client_gross_spend - COALESCE(d.feedmob_gross_spend, 0), 2) as difference,
        ROUND(
            CASE
                WHEN COALESCE(d.feedmob_gross_spend, 0) > 0
                THEN ((c.client_gross_spend - COALESCE(d.feedmob_gross_spend, 0)) / d.feedmob_gross_spend * 100)
                ELSE 0
            END,
            2
        ) as difference_pct
    FROM client_agg c
    LEFT JOIN direct_spend d
        ON CAST(c.click_url_id AS BIGINT) = CAST(d.click_url_id AS BIGINT)
        AND c.date = d.date
)
SELECT
    date,
    click_url_id,
    campaign_name,
    {"vendor_name," if column_info.get('has_vendor_name') else ""}
    client_gross_spend,
    feedmob_gross_spend,
    feedmob_net_spend,
    difference,
    difference_pct,
    CASE
        WHEN ABS(difference) < 0.01 THEN '✅ Perfect'
        WHEN ABS(difference_pct) < 2 THEN '⚠️ Minor'
        ELSE '🚨 Significant'
    END as status
FROM comparison
WHERE client_gross_spend > 0 OR feedmob_gross_spend > 0
ORDER BY date, ABS(difference) DESC
"""

    df = ctx.sql(query)
    pandas_df = df.to_pandas()
    pandas_df.to_csv(output_csv, index=False)
    return pandas_df


def execute_campaign_query(client_csv, direct_spend_csv, output_csv, column_info):
    """Execute comparison at campaign level (no click_url_id)"""
    from datafusion import SessionContext

    ctx = SessionContext()
    ctx.register_csv('client_report', client_csv, has_header=True)
    ctx.register_csv('direct_spend', direct_spend_csv, has_header=True)

    vendor_name_select = ", MAX(vendor_name) as vendor_name" if column_info.get('has_vendor_name') else ""

    query = f"""
WITH client_agg AS (
    SELECT
        campaign_name,
        SUM(CAST(COALESCE(gross_spend, 0) AS DOUBLE)) as client_gross_spend
        {vendor_name_select}
    FROM client_report
    GROUP BY campaign_name
),
direct_agg AS (
    SELECT
        campaign_name,
        SUM(CAST(COALESCE(feedmob_gross_spend, 0) AS DOUBLE)) as feedmob_gross_spend,
        SUM(CAST(COALESCE(feedmob_net_spend, 0) AS DOUBLE)) as feedmob_net_spend
    FROM direct_spend
    GROUP BY campaign_name
),
comparison AS (
    SELECT
        c.campaign_name,
        {"c.vendor_name," if column_info.get('has_vendor_name') else ""}
        ROUND(c.client_gross_spend, 2) as client_gross_spend,
        ROUND(COALESCE(d.feedmob_gross_spend, 0), 2) as feedmob_gross_spend,
        ROUND(COALESCE(d.feedmob_net_spend, 0), 2) as feedmob_net_spend,
        ROUND(c.client_gross_spend - COALESCE(d.feedmob_gross_spend, 0), 2) as difference,
        ROUND(
            CASE
                WHEN COALESCE(d.feedmob_gross_spend, 0) > 0
                THEN ((c.client_gross_spend - COALESCE(d.feedmob_gross_spend, 0)) / d.feedmob_gross_spend * 100)
                ELSE 0
            END,
            2
        ) as difference_pct
    FROM client_agg c
    LEFT JOIN direct_agg d
        ON c.campaign_name = d.campaign_name
)
SELECT
    campaign_name,
    {"vendor_name," if column_info.get('has_vendor_name') else ""}
    client_gross_spend,
    feedmob_gross_spend,
    feedmob_net_spend,
    difference,
    difference_pct,
    CASE
        WHEN ABS(difference) < 0.01 THEN '✅ Perfect'
        WHEN ABS(difference_pct) < 2 THEN '⚠️ Minor'
        ELSE '🚨 Significant'
    END as status
FROM comparison
WHERE client_gross_spend > 0 OR feedmob_gross_spend > 0
ORDER BY ABS(difference) DESC
"""

    df = ctx.sql(query)
    pandas_df = df.to_pandas()
    pandas_df.to_csv(output_csv, index=False)
    return pandas_df


def generate_summary(df, comparison_mode):
    """Generate summary statistics"""
    total_client = df['client_gross_spend'].sum()
    total_feedmob = df['feedmob_gross_spend'].sum()
    total_diff = df['difference'].sum()
    total_diff_pct = (total_diff / total_feedmob * 100) if total_feedmob > 0 else 0

    status_counts = df['status'].value_counts().to_dict() if 'status' in df.columns else {}

    return {
        'total_client': total_client,
        'total_feedmob': total_feedmob,
        'total_diff': total_diff,
        'total_diff_pct': total_diff_pct,
        'row_count': len(df),
        'status_counts': status_counts,
        'comparison_mode': comparison_mode,
    }


def print_summary(summary):
    """Print summary report"""
    print("\n" + "="*60)
    print("Client Report Spend vs Direct Spend Comparison")
    print("="*60)
    print()

    mode_label = "Click URL Level" if summary['comparison_mode'] == 'click_url' else "Campaign Level"
    print(f"Comparison Mode: {mode_label}")
    print()

    print(f"Total Client Report Spend:  ${summary['total_client']:,.2f}")
    print(f"Total Direct Gross Spend:   ${summary['total_feedmob']:,.2f}")
    print(f"Total Difference:           ${summary['total_diff']:,.2f} ({summary['total_diff_pct']:.2f}%)")
    print()

    status_counts = summary.get('status_counts', {})
    if status_counts:
        print("Status Breakdown:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        print()

    abs_diff_pct = abs(summary['total_diff_pct'])
    if summary['row_count'] == 0 or (summary['total_client'] == 0 and summary['total_feedmob'] == 0):
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
        print("Usage: python3 compare_client_report_spend_datafusion.py <client_report_spends.csv> <direct_spend.csv> <output.csv>")
        sys.exit(1)

    client_csv = sys.argv[1]
    direct_spend_csv = sys.argv[2]
    output_csv = sys.argv[3]

    # Validate client report file
    print("Validating input files...")
    if not Path(client_csv).exists():
        print(f"✗ Error: Client report file not found: {client_csv}")
        sys.exit(1)
    print("✓ Client report file exists")

    # Handle direct spend file (can be missing or empty)
    direct_spend_status = validate_and_prepare_direct_spend_csv(direct_spend_csv)
    print()

    # Check and install dependencies
    if not check_and_install_dependencies():
        sys.exit(1)
    print()

    # Detect columns
    print("Detecting columns in client report...")
    columns, column_info = detect_client_report_columns(client_csv)
    print(f"CSV Header: {', '.join(columns)}")
    print()

    if not column_info['has_spend_date']:
        print("✗ Error: spend_date column not found in client report")
        sys.exit(1)
    if not column_info['has_gross_spend']:
        print("✗ Error: gross_spend column not found in client report")
        sys.exit(1)
    if not column_info['has_campaign_name']:
        print("✗ Error: campaign_name column not found in client report")
        sys.exit(1)

    print(f"✓ Required columns found: spend_date, gross_spend, campaign_name")

    # Determine comparison mode
    if column_info['has_click_url_data']:
        comparison_mode = 'click_url'
        print("✓ click_url_id has data → Click URL level comparison")
    else:
        comparison_mode = 'campaign'
        print("⚠️  click_url_id empty → Campaign level comparison")
    print()

    # Execute query
    print("Starting DataFusion analysis...")
    print()

    try:
        if comparison_mode == 'click_url':
            df = execute_click_url_query(client_csv, direct_spend_csv, output_csv, column_info)
        else:
            df = execute_campaign_query(client_csv, direct_spend_csv, output_csv, column_info)

        row_count = len(df)
        print(f"✓ Query executed successfully")
        print(f"✓ Report saved to: {output_csv}")
        print(f"✓ Processed {row_count} rows")

        # Generate summary
        summary = generate_summary(df, comparison_mode)
        print_summary(summary)

        print("Done!")

    except Exception as e:
        print(f"✗ Error: Query execution failed")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
