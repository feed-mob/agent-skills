#!/usr/bin/env python3
"""
Calculate Gross Spend Comparison (Universal)

This script works with ANY client report (Possible Finance, TextNow, etc.)

Features:
1. Reads attribution reports (Singular/Adjust), click_url_histories, and direct_spends from CSV files
2. Calculates expected gross spend using: client_paid_action_count × gross_cpi
3. Dynamically matches event fields based on client_paid_action
4. Compares calculated vs direct gross spend
5. Generates a detailed comparison report

Usage Examples:
    # Possible Finance (Singular reports)
    python3 calculate_gross_spend.py \
        --report ./tmp/possible_finance_singular_reports_2026-01-01_2026-01-20.csv \
        --histories ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
        --direct-spend ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
        --output ./tmp/gross_spend_comparison_report.csv

    # TextNow (Adjust reports)
    python3 calculate_gross_spend.py \
        --report ./tmp/textnow_adjust_reports_2026-01-01_2026-01-20.csv \
        --histories ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
        --direct-spend ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
        --output ./tmp/gross_spend_comparison_report.csv
"""

import csv
import argparse
import sys
from pathlib import Path
from collections import defaultdict


def load_csv(filepath):
    """Load CSV file into list of dictionaries"""
    with open(filepath, 'r') as f:
        return list(csv.DictReader(f))


def load_data(report_path, histories_path, direct_spend_path):
    """Load all required CSV files"""
    print("Loading data files...")

    try:
        report_data = load_csv(report_path)
        print(f"✓ Loaded {len(report_data)} rows from attribution reports")

        histories_data = load_csv(histories_path)
        print(f"✓ Loaded {len(histories_data)} rows from click_url_histories")

        direct_spend_data = load_csv(direct_spend_path)
        print(f"✓ Loaded {len(direct_spend_data)} rows from direct_spends")

        return report_data, histories_data, direct_spend_data
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)


def get_click_url_rate_map(histories_data):
    """Create mapping: (click_url_id, date) -> (gross_cpi, client_paid_action)"""
    print("\nBuilding rate map from click_url_histories...")

    rate_map = {}
    for row in histories_data:
        key = (int(row['click_url_id']), row['date'])
        rate_map[key] = {
            'gross_cpi': float(row['gross_cpi']),
            'client_paid_action': row['client_paid_action'],
            'campaign_name': row['campaign_name'],
            'vendor_name': row['vendor_name']
        }

    print(f"✓ Created rate map for {len(rate_map)} (click_url_id, date) combinations")
    return rate_map


def calculate_gross_spend(report_data, rate_map):
    """Calculate expected gross spend for each row"""
    print("\nCalculating expected gross spend...")

    results = []

    for row in report_data:
        click_url_id = int(row['click_url_id'])
        date = row['date']
        key = (click_url_id, date)

        # Get rate info
        rate_info = rate_map.get(key)
        if not rate_info:
            print(f"⚠ Warning: No rate data for click_url_id={click_url_id}, date={date}")
            continue

        gross_cpi = rate_info['gross_cpi']
        client_paid_action = rate_info['client_paid_action']

        # Map client_paid_action to CSV column name
        event_field_map = {
            'first_purchase': 'purchase',
            'first_install': 'install',
            'install': 'install',
            'registration': 'registration',
            'retained': 'retained',
            'tutorial': 'tutorial',
            'purchase': 'purchase',
            'level': 'level',
            'open': 'open',
            'all_event_a': 'all_event_a',
            'all_event_b': 'all_event_b',
            'first_event_a': 'first_event_a',
            'first_event_b': 'first_event_b'
        }

        event_field = event_field_map.get(client_paid_action, client_paid_action)

        if event_field not in row:
            print(f"⚠ Warning: Event field '{event_field}' not found for click_url_id={click_url_id}")
            event_count = 0
        else:
            event_count = int(row[event_field]) if row[event_field] else 0

        # Calculate: client_paid_action_count × gross_cpi
        calculated_gross = event_count * gross_cpi

        results.append({
            'date': date,
            'click_url_id': click_url_id,
            'campaign_name': rate_info['campaign_name'],
            'vendor_name': rate_info['vendor_name'],
            'client_paid_action': client_paid_action,
            'event_field': event_field,
            'event_count': event_count,
            'gross_cpi': gross_cpi,
            'calculated_gross_spend': round(calculated_gross, 2)
        })

    print(f"✓ Calculated gross spend for {len(results)} rows")
    return results


def merge_with_direct_spend(calculated_data, direct_spend_data):
    """Merge calculated gross spend with direct spend data"""
    print("\nMerging with direct spend data...")

    # Build direct spend lookup: (click_url_id, date) -> direct_gross_spend
    direct_spend_map = {}
    for row in direct_spend_data:
        key = (int(row['feedmob_click_url_id']), row['date'])
        direct_spend_map[key] = float(row['feedmob_gross_spend'])

    # Merge
    merged_data = []
    for row in calculated_data:
        key = (row['click_url_id'], row['date'])
        direct_gross = direct_spend_map.get(key, 0.0)

        difference = row['calculated_gross_spend'] - direct_gross
        difference_pct = round((difference / direct_gross * 100), 2) if direct_gross > 0 else 0

        merged_row = {
            **row,
            'direct_gross_spend': direct_gross,
            'difference': round(difference, 2),
            'difference_pct': difference_pct
        }
        merged_data.append(merged_row)

    print(f"✓ Merged {len(merged_data)} rows")
    return merged_data


def filter_non_zero_rows(data):
    """Filter out rows where both calculated and direct gross are 0"""
    print("\nFiltering out zero-activity rows...")

    original_count = len(data)
    filtered_data = [
        row for row in data
        if row['calculated_gross_spend'] != 0 or row['direct_gross_spend'] != 0
    ]

    filtered_count = original_count - len(filtered_data)
    print(f"✓ Filtered out {filtered_count} zero-activity rows")
    print(f"✓ Remaining: {len(filtered_data)} active rows")

    return filtered_data


def generate_summary(data):
    """Generate summary statistics"""
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)

    total_calculated = sum(row['calculated_gross_spend'] for row in data)
    total_direct = sum(row['direct_gross_spend'] for row in data)
    total_diff = total_calculated - total_direct
    total_diff_pct = (total_diff / total_direct * 100) if total_direct > 0 else 0

    print(f"\nTotal Calculated Gross Spend: ${total_calculated:,.2f}")
    print(f"Total Direct Gross Spend:     ${total_direct:,.2f}")
    print(f"Total Difference:             ${total_diff:,.2f} ({total_diff_pct:.2f}%)")

    # Status
    if abs(total_diff_pct) < 1:
        status = "✅ MATCH"
    elif abs(total_diff_pct) < 5:
        status = "⚠️  MINOR DIFFERENCE (<5%)"
    else:
        status = "🚨 SIGNIFICANT DIFFERENCE (≥5%)"

    print(f"\nStatus: {status}")

    # Breakdown by client_paid_action
    print(f"\n{'='*60}")
    print("BREAKDOWN BY PAID ACTION")
    print(f"{'='*60}")

    grouped = defaultdict(lambda: {'event_count': 0, 'calculated_gross_spend': 0})
    for row in data:
        action = row['client_paid_action']
        grouped[action]['event_count'] += row['event_count']
        grouped[action]['calculated_gross_spend'] += row['calculated_gross_spend']

    for action, values in sorted(grouped.items()):
        print(f"  {action}: {values['event_count']} events, ${values['calculated_gross_spend']:,.2f} calculated")

    return {
        'total_calculated': total_calculated,
        'total_direct': total_direct,
        'total_difference': total_diff,
        'total_difference_pct': total_diff_pct,
        'status': status
    }


def save_to_csv(data, output_path):
    """Save data to CSV file"""
    if not data:
        print("⚠ Warning: No data to save")
        return

    fieldnames = list(data[0].keys())

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(description='Calculate Gross Spend Comparison (Universal - works with any client)')
    parser.add_argument('--report', required=True, help='Path to attribution reports CSV (Singular/Adjust/etc)')
    parser.add_argument('--histories', required=True, help='Path to click_url_histories CSV')
    parser.add_argument('--direct-spend', required=True, help='Path to direct_spends CSV')
    parser.add_argument('--output', default='./tmp/gross_spend_comparison_report.csv',
                        help='Output CSV file path')
    parser.add_argument('--show-zero', action='store_true',
                        help='Include zero-activity rows in output')

    args = parser.parse_args()

    # Load data
    report_data, histories_data, direct_spend_data = load_data(
        args.report,
        args.histories,
        args.direct_spend
    )

    # Build rate map
    rate_map = get_click_url_rate_map(histories_data)

    # Calculate gross spend
    calculated_data = calculate_gross_spend(report_data, rate_map)

    # Merge with direct spend
    comparison_data = merge_with_direct_spend(calculated_data, direct_spend_data)

    # Filter zero rows (unless --show-zero flag)
    if not args.show_zero:
        comparison_data = filter_non_zero_rows(comparison_data)

    # Sort by date and click_url_id
    comparison_data.sort(key=lambda x: (x['date'], x['click_url_id']))

    # Generate summary
    summary = generate_summary(comparison_data)

    # Save to CSV
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_to_csv(comparison_data, output_path)

    print(f"\n✓ Report saved to: {output_path}")
    print(f"\nDone! Processed {len(comparison_data)} rows.")


if __name__ == '__main__':
    main()
