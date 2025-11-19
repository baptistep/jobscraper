#!/usr/bin/env python3
"""
Auto-viewer for jobs.csv - automatically shows updates when the file changes
"""

import os
import time
import json
from datetime import datetime


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def display_csv(csv_path='jobs.csv'):
    """Display CSV in a nice format"""
    clear_screen()

    print("=" * 80)
    print(f"JOBS DATABASE - Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    if not os.path.exists(csv_path):
        print("\nNo jobs.csv found yet. Waiting for first scrape...")
        print("The file will appear after running: python3 scraper.py")
        return

    # Read and parse CSV
    with open(csv_path, 'r') as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("\nNo jobs in database yet.")
        return

    # Count total jobs
    total_jobs = len(lines) - 1  # Exclude header

    print(f"\nTotal Jobs: {total_jobs}")
    print("\n" + "-" * 80)

    # Show header
    print(lines[0].strip())
    print("-" * 80)

    # Show latest 15 jobs
    display_count = min(15, len(lines) - 1)
    for line in lines[-display_count:]:
        print(line.strip())

    if total_jobs > display_count:
        print(f"\n... and {total_jobs - display_count} more jobs")

    print("\n" + "=" * 80)
    print("Watching for updates... (Press Ctrl+C to stop)")
    print(f"CSV File: {os.path.abspath(csv_path)}")
    print("=" * 80)


def watch_csv(csv_path='jobs.csv', check_interval=3):
    """Watch CSV file for changes and auto-display"""
    last_modified = None

    print("\n" + "=" * 80)
    print("JOB SCRAPER AUTO-VIEWER")
    print("=" * 80)
    print(f"\nWatching: {csv_path}")
    print(f"Check interval: {check_interval} seconds")
    print("\nThis will automatically update when the scraper runs!")
    print("Press Ctrl+C to stop watching\n")

    # Initial display
    display_csv(csv_path)

    if os.path.exists(csv_path):
        last_modified = os.path.getmtime(csv_path)

    try:
        while True:
            time.sleep(check_interval)

            if os.path.exists(csv_path):
                current_modified = os.path.getmtime(csv_path)

                if last_modified is None or current_modified != last_modified:
                    last_modified = current_modified
                    display_csv(csv_path)

                    # Beep to alert user
                    print('\a', end='', flush=True)

    except KeyboardInterrupt:
        print("\n\nStopped watching. Goodbye!")


if __name__ == '__main__':
    watch_csv()
