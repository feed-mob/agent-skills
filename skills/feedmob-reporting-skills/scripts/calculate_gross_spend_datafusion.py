#!/usr/bin/env python3
"""
Dynamic DataFusion Python - Gross Spend Comparison (Universal)

Uses Python datafusion library for SQL analysis, no need to install datafusion-cli.
Script automatically checks and installs required dependencies.

Works with all client reports (Possible Finance, TextNow, Privacy Hawk, etc.)
Dynamically detects available columns in attribution report CSV and generates corresponding CASE statements.

Usage Examples:
    # Possible Finance (Singular reports)
    python3 calculate_gross_spend_datafusion.py \
        ./tmp/possible_finance_singular_reports_2026-01-01_2026-01-20.csv \
        ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
        ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
        ./tmp/output.csv

    # TextNow (Adjust reports)
    python3 calculate_gross_spend_datafusion.py \
        ./tmp/textnow_adjust_reports_2026-01-01_2026-01-20.csv \
        ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
        ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
        ./tmp/output.csv
"""

import sys
import csv
import subprocess
from pathlib import Path
from datetime import datetime


def check_and_install_dependencies():
    """Check and automatically install dependencies (from requirements.txt)"""
    # Check required packages
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

    # If there are missing packages, install from requirements.txt
    if missing_packages:
        print(f"⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Auto-installing from requirements.txt...")

        # Find requirements.txt path (same directory as script)
        script_dir = Path(__file__).parent
        requirements_file = script_dir / "requirements.txt"

        if not requirements_file.exists():
            print(f"✗ requirements.txt not found: {requirements_file}")
            print("Please install manually: pip install datafusion pandas pyarrow --user")
            return False

        try:
            # Try installing with --user flag (compatible with PEP 668)
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file),
                "--user", "--quiet"
            ])
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            # If that fails, try with --break-system-packages
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


def detect_event_columns(csv_path):
    """Detect available event columns in CSV file"""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames

    # Exclude reserved columns
    reserved_columns = {'click_url_id', 'date', 'campaign_name', 'vendor_name'}

    # Event field mapping
    event_mapping = {
        'first_purchase': 'purchase',
        'purchase': 'purchase',
        'first_install': 'install',
        'install': 'install',
        'registration': 'registration',
        'first_registration': 'registration',
        'tutorial': 'tutorial',
        'retained': 'retained',
        'level': 'level',
        'open': 'open',
        'all_event_a': 'all_event_a',
        'all_event_b': 'all_event_b',
        'first_event_a': 'first_event_a',
        'first_event_b': 'first_event_b',
        'click': 'click',
        'impression': 'impression'
    }

    # Find available event columns
    available_events = []
    for col in columns:
        if col not in reserved_columns and col in event_mapping.values():
            available_events.append(col)

    return columns, available_events, event_mapping


def generate_aggregation_columns(available_events):
    """Generate SQL fragment for aggregation columns"""
    if not available_events:
        return ""

    agg_columns = []
    for col in available_events:
        agg_columns.append(f"        SUM(CAST(COALESCE({col}, 0) AS BIGINT)) as {col}")

    return ",\n".join(agg_columns)


def generate_event_case_statements(available_events, event_mapping):
    """Generate SQL fragment for CASE statements"""
    event_count_cases = []
    event_field_cases = []

    # Generate CASE statements for each action -> column mapping
    for action, column in event_mapping.items():
        if column in available_events:
            event_count_cases.append(
                f"            WHEN '{action}' THEN CAST(COALESCE(s.{column}, 0) AS BIGINT)"
            )
            event_field_cases.append(
                f"            WHEN '{action}' THEN '{column}'"
            )

    # Add ELSE clause
    event_count_cases.append("            ELSE 0")
    event_field_cases.append("            ELSE h.client_paid_action")

    return "\n".join(event_count_cases), "\n".join(event_field_cases)


def execute_query_and_save(attribution_csv, histories_csv, direct_spend_csv,
                          aggregation_columns, event_count_cases, event_field_cases,
                          output_csv):
    """Execute DataFusion query and save results"""
    from datafusion import SessionContext
    from datafusion import col, lit
    import datafusion.functions as F

    # Create DataFusion session
    ctx = SessionContext()

    # Register CSV tables
    ctx.register_csv('attribution_report', attribution_csv, has_header=True)
    ctx.register_csv('histories', histories_csv, has_header=True)
    ctx.register_csv('direct_spend', direct_spend_csv, has_header=True)

    # Build complete query (single SQL statement)
    full_query = f"""
WITH aggregated_attribution AS (
    SELECT
        date,
        CAST(click_url_id AS BIGINT) as click_url_id,
{aggregation_columns}
    FROM attribution_report
    GROUP BY date, click_url_id
),
calculated AS (
    SELECT
        s.date,
        s.click_url_id,
        h.campaign_name,
        h.vendor_name,
        h.client_paid_action,
        CAST(h.gross_cpi AS DOUBLE) as gross_cpi,
        CASE h.client_paid_action
{event_count_cases}
        END as event_count,
        CASE h.client_paid_action
{event_field_cases}
        END as event_field
    FROM aggregated_attribution s
    INNER JOIN histories h
        ON s.click_url_id = CAST(h.click_url_id AS BIGINT)
        AND s.date = h.date
),
calculated_with_spend AS (
    SELECT
        *,
        event_count * gross_cpi as calculated_gross_spend
    FROM calculated
)
SELECT
    c.date,
    c.click_url_id,
    c.campaign_name,
    c.vendor_name,
    c.client_paid_action,
    c.event_field,
    c.event_count,
    c.gross_cpi,
    ROUND(c.calculated_gross_spend, 2) as calculated_gross_spend,
    ROUND(COALESCE(d.feedmob_gross_spend, 0), 2) as direct_gross_spend,
    ROUND(c.calculated_gross_spend - COALESCE(d.feedmob_gross_spend, 0), 2) as difference,
    ROUND(
        CASE
            WHEN COALESCE(d.feedmob_gross_spend, 0) > 0
            THEN ((c.calculated_gross_spend - COALESCE(d.feedmob_gross_spend, 0)) / d.feedmob_gross_spend * 100)
            ELSE 0
        END,
        2
    ) as difference_pct
FROM calculated_with_spend c
LEFT JOIN direct_spend d
    ON CAST(c.click_url_id AS BIGINT) = CAST(d.feedmob_click_url_id AS BIGINT)
    AND c.date = d.date
WHERE c.event_count > 0 OR COALESCE(d.feedmob_gross_spend, 0) > 0
ORDER BY c.date, c.click_url_id
"""

    # Execute query
    df = ctx.sql(full_query)

    # Convert to pandas and save as CSV
    pandas_df = df.to_pandas()
    pandas_df.to_csv(output_csv, index=False)

    return pandas_df


def generate_summary(df):
    """Generate summary statistics"""
    total_calculated = df['calculated_gross_spend'].sum()
    total_direct = df['direct_gross_spend'].sum()
    total_diff = total_calculated - total_direct
    total_diff_pct = (total_diff / total_direct * 100) if total_direct > 0 else 0
    total_events = df['event_count'].sum()

    return {
        'total_calculated': total_calculated,
        'total_direct': total_direct,
        'total_diff': total_diff,
        'total_diff_pct': total_diff_pct,
        'total_events': int(total_events),
        'row_count': len(df)
    }


def print_summary(summary, available_events):
    """Print summary report"""
    print("\n" + "="*60)
    print("Summary Report")
    print("="*60)
    print()
    print(f"Total Calculated Gross Spend: ${summary['total_calculated']:,.2f}")
    print(f"Total Direct Gross Spend: ${summary['total_direct']:,.2f}")
    print(f"Total Difference: ${summary['total_diff']:,.2f} ({summary['total_diff_pct']:.2f}%)")
    print()

    # Status
    abs_diff_pct = abs(summary['total_diff_pct'])
    if abs_diff_pct < 1:
        status = "✅ Match"
    elif abs_diff_pct < 5:
        status = "⚠️  Minor Difference (<5%)"
    else:
        status = "🚨 Significant Difference (≥5%)"

    print(f"Status: {status}")
    print()
    print(f"Total Events Processed: {summary['total_events']}")
    print()
    print(f"Available Event Columns: {', '.join(available_events)}")
    print()


def main():
    """Main function"""
    if len(sys.argv) != 5:
        print("Usage: python3 calculate_gross_spend_datafusion.py <attribution_report.csv> <histories.csv> <direct_spend.csv> <output.csv>")
        sys.exit(1)

    attribution_csv = sys.argv[1]
    histories_csv = sys.argv[2]
    direct_spend_csv = sys.argv[3]
    output_csv = sys.argv[4]

    # Validate input files
    for filepath in [attribution_csv, histories_csv, direct_spend_csv]:
        if not Path(filepath).exists():
            print(f"✗ Error: File not found: {filepath}")
            sys.exit(1)

    print("Validating input files...")
    print("✓ All input files exist")
    print()

    # Check and install dependencies
    if not check_and_install_dependencies():
        sys.exit(1)
    print()

    # Detect available columns
    print("Detecting available columns in attribution report...")
    columns, available_events, event_mapping = detect_event_columns(attribution_csv)
    print(f"CSV Header: {', '.join(columns)}")
    print()
    print(f"Detected Available Event Columns: {', '.join(available_events)}")
    print()

    # Generate SQL fragments
    print(f"Generating dynamic CASE statements for {len(available_events)} event columns")
    print()

    aggregation_columns = generate_aggregation_columns(available_events)
    event_count_cases, event_field_cases = generate_event_case_statements(
        available_events, event_mapping
    )

    # Execute query
    print("Starting DataFusion Python analysis...")
    print()

    try:
        df = execute_query_and_save(
            attribution_csv, histories_csv, direct_spend_csv,
            aggregation_columns, event_count_cases, event_field_cases,
            output_csv
        )

        row_count = len(df) + 1  # +1 for header
        print(f"✓ Query executed successfully")
        print(f"✓ Report saved to: {output_csv}")
        print(f"✓ Processed {row_count} rows (including header)")

        # Generate summary
        summary = generate_summary(df)
        print_summary(summary, available_events)

        print("Done!")

    except Exception as e:
        print(f"✗ Error: Query execution failed")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
