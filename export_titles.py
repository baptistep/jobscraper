#!/usr/bin/env python3
"""
Export job titles to a simple text file
"""

import json
from collections import defaultdict
from datetime import datetime


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

    # Export to text file
    output_file = 'job_titles.txt'
    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write(f"JOB TITLES EXPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 70 + "\n")
        f.write(f"Total Jobs: {len(jobs)}\n")
        f.write("=" * 70 + "\n\n")

        for company in sorted(by_company.keys()):
            company_jobs = by_company[company]
            f.write(f"\n{company} ({len(company_jobs)} jobs)\n")
            f.write("-" * 70 + "\n")

            for i, job in enumerate(company_jobs, 1):
                location = f" | {job['location']}" if job['location'] else ""
                f.write(f"{i}. {job['title']}{location}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write(f"Total: {len(jobs)} job openings\n")
        f.write("=" * 70 + "\n")

    print(f"✓ Job titles exported to: {output_file}")
    print(f"✓ Total jobs exported: {len(jobs)}")

    # Also create CSV format
    csv_file = 'job_titles.csv'
    with open(csv_file, 'w') as f:
        f.write("Company,Title,Location,Department,Type,URL\n")
        for job in jobs:
            company = job['source'].replace(',', ' ')
            title = job['title'].replace(',', ' ')
            location = job.get('location', '').replace(',', ' ')
            department = job.get('department', '').replace(',', ' ')
            emp_type = job.get('employment_type', '').replace(',', ' ')
            url = job['url']
            f.write(f"{company},{title},{location},{department},{emp_type},{url}\n")

    print(f"✓ CSV format exported to: {csv_file}")
    print(f"\nYou can open these files in any text editor or spreadsheet app.")


if __name__ == '__main__':
    main()
