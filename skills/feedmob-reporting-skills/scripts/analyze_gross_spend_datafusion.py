#!/usr/bin/env python3
"""
DataFusion Analysis Script - Multi-dimensional Gross Spend Comparison Report Analysis (Python Version)

Features: Generates 10 dimension analysis reports (CSV format), suitable for LLM reading
Automatically installs dependencies: datafusion, pandas, pyarrow

Usage:
    python3 analyze_gross_spend_datafusion.py <comparison_report.csv> <output_dir>
"""

import sys
import subprocess
from pathlib import Path


def check_and_install_dependencies():
    """Check and automatically install dependencies"""
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


def run_analysis(input_csv, output_dir):
    """Run multi-dimensional analysis"""
    from datafusion import SessionContext
    import pandas as pd

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("DataFusion Gross Spend Analysis")
    print("=" * 60)
    print(f"Input:  {input_csv}")
    print(f"Output: {output_dir}/")
    print()

    # Create DataFusion session
    ctx = SessionContext()
    ctx.register_csv('comparison_report', str(input_csv), has_header=True)

    print("Generating analysis reports...")
    print()

    queries = {
        "01_global_summary.csv": """
            SELECT
                COUNT(*) as total_rows,
                COUNT(DISTINCT click_url_id) as unique_campaigns,
                COUNT(DISTINCT vendor_name) as unique_vendors,
                COUNT(DISTINCT date) as date_range_days,
                SUM(event_count) as total_events,
                ROUND(SUM(calculated_gross_spend), 2) as total_calculated,
                ROUND(SUM(direct_gross_spend), 2) as total_direct,
                ROUND(SUM(difference), 2) as total_difference,
                ROUND(CASE
                    WHEN SUM(direct_gross_spend) = 0 THEN 0
                    ELSE (SUM(difference) / SUM(direct_gross_spend) * 100)
                END, 2) as diff_pct
            FROM comparison_report
        """,

        "02_by_vendor.csv": """
            SELECT
                vendor_name,
                COUNT(*) as rows,
                COUNT(DISTINCT click_url_id) as campaigns,
                SUM(event_count) as events,
                ROUND(SUM(calculated_gross_spend), 2) as calculated,
                ROUND(SUM(direct_gross_spend), 2) as direct,
                ROUND(SUM(difference), 2) as diff,
                ROUND(CASE
                    WHEN SUM(direct_gross_spend) = 0 THEN 0
                    ELSE (SUM(difference) / SUM(direct_gross_spend) * 100)
                END, 2) as diff_pct
            FROM comparison_report
            GROUP BY vendor_name
            ORDER BY ABS(SUM(difference)) DESC
        """,

        "03_by_paid_action.csv": """
            SELECT
                client_paid_action,
                COUNT(DISTINCT click_url_id) as campaigns,
                COUNT(*) as rows,
                SUM(event_count) as events,
                ROUND(SUM(calculated_gross_spend), 2) as calculated,
                ROUND(SUM(direct_gross_spend), 2) as direct,
                ROUND(SUM(difference), 2) as diff,
                ROUND(CASE
                    WHEN SUM(direct_gross_spend) = 0 THEN 0
                    ELSE (SUM(difference) / SUM(direct_gross_spend) * 100)
                END, 2) as diff_pct
            FROM comparison_report
            GROUP BY client_paid_action
            ORDER BY ABS(SUM(difference)) DESC
        """,

        "04_cpm_vs_cpi.csv": """
            SELECT
                CASE
                    WHEN gross_cpi = -1 THEN 'CPM'
                    ELSE 'CPA_CPI'
                END as campaign_type,
                COUNT(DISTINCT click_url_id) as campaigns,
                COUNT(*) as rows,
                SUM(event_count) as events,
                ROUND(SUM(calculated_gross_spend), 2) as calculated,
                ROUND(SUM(direct_gross_spend), 2) as direct,
                ROUND(SUM(difference), 2) as diff,
                ROUND(CASE
                    WHEN SUM(direct_gross_spend) = 0 THEN 0
                    ELSE (SUM(difference) / SUM(direct_gross_spend) * 100)
                END, 2) as diff_pct
            FROM comparison_report
            GROUP BY
                CASE
                    WHEN gross_cpi = -1 THEN 'CPM'
                    ELSE 'CPA_CPI'
                END
            ORDER BY ABS(SUM(difference)) DESC
        """,

        "05_match_status.csv": """
            SELECT
                CASE
                    WHEN ABS(difference) < 0.01 THEN 'Perfect_Match'
                    WHEN ABS(difference_pct) < 5 THEN 'Minor_Diff'
                    WHEN ABS(difference_pct) >= 5 THEN 'Major_Diff'
                    ELSE 'Unknown'
                END as status,
                COUNT(*) as rows,
                ROUND(SUM(calculated_gross_spend), 2) as calculated,
                ROUND(SUM(direct_gross_spend), 2) as direct,
                ROUND(SUM(ABS(difference)), 2) as abs_diff
            FROM comparison_report
            GROUP BY
                CASE
                    WHEN ABS(difference) < 0.01 THEN 'Perfect_Match'
                    WHEN ABS(difference_pct) < 5 THEN 'Minor_Diff'
                    WHEN ABS(difference_pct) >= 5 THEN 'Major_Diff'
                    ELSE 'Unknown'
                END
            ORDER BY SUM(ABS(difference)) DESC
        """,

        "06_top50_anomalies.csv": """
            SELECT
                date,
                click_url_id,
                vendor_name,
                client_paid_action,
                event_count,
                ROUND(calculated_gross_spend, 2) as calculated,
                ROUND(direct_gross_spend, 2) as direct,
                ROUND(difference, 2) as diff,
                ROUND(difference_pct, 2) as diff_pct
            FROM comparison_report
            WHERE ABS(difference) > 0.01
            ORDER BY ABS(difference) DESC
            LIMIT 50
        """,

        "07_by_click_url.csv": """
            SELECT
                click_url_id,
                MAX(vendor_name) as vendor,
                MAX(client_paid_action) as paid_action,
                COUNT(DISTINCT date) as days,
                COUNT(*) as rows,
                SUM(event_count) as events,
                ROUND(SUM(calculated_gross_spend), 2) as calculated,
                ROUND(SUM(direct_gross_spend), 2) as direct,
                ROUND(SUM(difference), 2) as diff,
                ROUND(CASE
                    WHEN SUM(direct_gross_spend) = 0 THEN 0
                    ELSE (SUM(difference) / SUM(direct_gross_spend) * 100)
                END, 2) as diff_pct
            FROM comparison_report
            GROUP BY click_url_id
            ORDER BY ABS(SUM(difference)) DESC
        """,

        "08_daily_trend.csv": """
            SELECT
                date,
                COUNT(DISTINCT click_url_id) as campaigns,
                SUM(event_count) as events,
                ROUND(SUM(calculated_gross_spend), 2) as calculated,
                ROUND(SUM(direct_gross_spend), 2) as direct,
                ROUND(SUM(difference), 2) as diff,
                ROUND(CASE
                    WHEN SUM(direct_gross_spend) = 0 THEN 0
                    ELSE (SUM(difference) / SUM(direct_gross_spend) * 100)
                END, 2) as diff_pct
            FROM comparison_report
            GROUP BY date
            ORDER BY date DESC
        """,

        "09_duplicates.csv": """
            SELECT
                click_url_id,
                vendor_name,
                date,
                COUNT(*) as duplicate_count,
                SUM(event_count) as events,
                ROUND(SUM(calculated_gross_spend), 2) as calculated,
                ROUND(SUM(direct_gross_spend), 2) as direct
            FROM comparison_report
            GROUP BY click_url_id, vendor_name, date
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC, date DESC
            LIMIT 50
        """,

        "10_weekly_trend.csv": """
            SELECT
                DATE_TRUNC('week', date) as week_start,
                COUNT(DISTINCT click_url_id) as campaigns,
                COUNT(DISTINCT date) as days,
                SUM(event_count) as events,
                ROUND(SUM(calculated_gross_spend), 2) as calculated,
                ROUND(SUM(direct_gross_spend), 2) as direct,
                ROUND(SUM(difference), 2) as diff,
                ROUND(CASE
                    WHEN SUM(direct_gross_spend) = 0 THEN 0
                    ELSE (SUM(difference) / SUM(direct_gross_spend) * 100)
                END, 2) as diff_pct
            FROM comparison_report
            GROUP BY DATE_TRUNC('week', date)
            ORDER BY DATE_TRUNC('week', date) DESC
        """
    }

    query_names = {
        "01_global_summary.csv": "Global Summary",
        "02_by_vendor.csv": "By Vendor",
        "03_by_paid_action.csv": "By Paid Action",
        "04_cpm_vs_cpi.csv": "CPM vs CPI",
        "05_match_status.csv": "Match Status",
        "06_top50_anomalies.csv": "Top 50 Anomalies",
        "07_by_click_url.csv": "By Click URL",
        "08_daily_trend.csv": "Daily Trend",
        "09_duplicates.csv": "Duplicates",
        "10_weekly_trend.csv": "Weekly Trend"
    }

    # Execute all queries
    for filename, query in queries.items():
        try:
            df = ctx.sql(query).to_pandas()
            output_file = output_dir / filename
            df.to_csv(output_file, index=False)
            print(f"  ✓ {query_names[filename]}")
        except Exception as e:
            print(f"  ✗ {query_names[filename]} (error: {e})")

    print()
    print("=" * 60)
    print("Analysis Complete")
    print("=" * 60)
    print()

    # Display quick summary
    summary_file = output_dir / "01_global_summary.csv"
    if summary_file.exists():
        summary_df = pd.read_csv(summary_file)
        if not summary_df.empty:
            row = summary_df.iloc[0]
            print(f"Total Rows:        {int(row['total_rows'])}")
            print(f"Campaigns:         {int(row['unique_campaigns'])}")
            print(f"Vendors:           {int(row['unique_vendors'])}")
            print(f"Date Range:        {int(row['date_range_days'])} days")
            print(f"Total Events:      {int(row['total_events'])}")
            print(f"Calculated Spend:  ${row['total_calculated']}")
            print(f"Direct Spend:      ${row['total_direct']}")
            print(f"Difference:        ${row['total_difference']} ({row['diff_pct']}%)")

    print()
    print(f"✓ All reports generated in: {output_dir}/")
    print()


def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python3 analyze_gross_spend_datafusion.py <comparison_report.csv> <output_dir>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_dir = sys.argv[2]

    # Validate input file
    if not Path(input_csv).exists():
        print(f"✗ Error: File not found: {input_csv}")
        sys.exit(1)

    # Check and install dependencies
    if not check_and_install_dependencies():
        sys.exit(1)
    print()

    # Run analysis
    try:
        run_analysis(input_csv, output_dir)
    except Exception as e:
        print(f"✗ Error: Analysis failed")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
