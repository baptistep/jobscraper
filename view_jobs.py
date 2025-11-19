#!/usr/bin/env python3
"""
Simple job viewer - shows all jobs organized by company
"""

import json
from collections import defaultdict


def main():
    try:
        with open('jobs.json', 'r') as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print("No jobs found. Run 'python3 scraper.py' first.")
        return

    if not jobs:
        print("No jobs in database.")
        return

    # Group by company
    by_company = defaultdict(list)
    for job in jobs:
        by_company[job['source']].append(job)

    # Display summary
    print("\n" + "=" * 70)
    print(f"TOTAL JOBS: {len(jobs)}")
    print("=" * 70)

    for company in sorted(by_company.keys()):
        print(f"\n{company}: {len(by_company[company])} jobs")

    # Display all jobs
    for company in sorted(by_company.keys()):
        company_jobs = by_company[company]

        print("\n" + "=" * 70)
        print(f"{company} ({len(company_jobs)} jobs)")
        print("=" * 70)

        for i, job in enumerate(company_jobs, 1):
            location = f" | {job['location']}" if job['location'] else ""

            print(f"\n{i}. {job['title']}")
            print(f"   Location: {job['location'] or 'Not specified'}")
            if job.get('department'):
                print(f"   Department: {job['department']}")
            if job.get('employment_type'):
                print(f"   Type: {job['employment_type']}")
            print(f"   Apply: {job['url']}")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
