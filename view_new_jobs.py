#!/usr/bin/env python3
"""
View new jobs from the most recent scrape
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict


def main():
    # Load all jobs
    try:
        with open('jobs.json', 'r') as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print("No jobs found. Run 'python3 scraper.py' first.")
        return

    if not jobs:
        print("No jobs in database yet.")
        return

    # Get jobs from last 24 hours
    cutoff = datetime.now() - timedelta(hours=24)
    new_jobs = []

    for job in jobs:
        try:
            scraped_at = datetime.fromisoformat(job['scraped_at'])
            if scraped_at > cutoff:
                new_jobs.append(job)
        except (ValueError, KeyError):
            continue

    # Display results
    print("=" * 70)
    print(f"Jobs Scraped in Last 24 Hours: {len(new_jobs)}")
    print("=" * 70)
    print()

    if not new_jobs:
        print("No new jobs in the last 24 hours.")
        print("Run 'python3 scraper.py' to fetch the latest jobs.")
        return

    # Group by source
    by_source = defaultdict(list)
    for job in new_jobs:
        by_source[job['source']].append(job)

    # Display by company
    for source in sorted(by_source.keys()):
        source_jobs = by_source[source]
        print(f"\n{'='*70}")
        print(f"{source} ({len(source_jobs)} new jobs)")
        print('='*70)

        for i, job in enumerate(source_jobs, 1):
            location = f" | {job['location']}" if job['location'] else ""
            employment = f" | {job.get('employment_type', '')}" if job.get('employment_type') else ""

            print(f"\n{i}. {job['title']}")
            print(f"   Location: {job['location'] or 'Not specified'}")
            if job.get('department'):
                print(f"   Department: {job['department']}")
            print(f"   URL: {job['url']}")

            # Show when it was scraped
            try:
                scraped = datetime.fromisoformat(job['scraped_at'])
                time_ago = datetime.now() - scraped
                hours_ago = int(time_ago.total_seconds() / 3600)
                if hours_ago < 1:
                    time_str = "just now"
                elif hours_ago == 1:
                    time_str = "1 hour ago"
                else:
                    time_str = f"{hours_ago} hours ago"
                print(f"   Discovered: {time_str}")
            except:
                pass

    print("\n" + "=" * 70)
    print(f"Total new jobs: {len(new_jobs)}")
    print("=" * 70)


if __name__ == '__main__':
    main()
