#!/usr/bin/env python3
"""
Job Board Scraper
Runs twice a day to fetch new job postings from configured job boards
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import hashlib
import re
from urllib.parse import urljoin
from typing import List, Dict, Optional


class JobScraper:
    """Main job scraper class that handles different job board types"""

    def __init__(self, config_path='config.json'):
        """Initialize scraper with configuration"""
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        self.config = self.load_config()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def load_config(self) -> Dict:
        """Load configuration from config.json"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.config_path} not found. Please create it from config.example.json")
            return {"job_boards": [], "settings": {}}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.config_path}")
            return {"job_boards": [], "settings": {}}

    def generate_job_id(self, job: Dict) -> str:
        """Generate unique ID for a job posting"""
        unique_string = f"{job.get('title', '')}{job.get('company', '')}{job.get('url', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def scrape_generic(self, board: Dict) -> List[Dict]:
        """Scrape generic job boards using custom selectors"""
        jobs = []
        try:
            response = requests.get(board['url'], headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            selectors = board.get('selectors', {})
            job_containers = soup.select(selectors.get('job_container', 'div'))

            for container in job_containers:
                try:
                    # Check if container itself is a link (for simple job boards)
                    if container.name == 'a' and container.get('href'):
                        title = container.text.strip()
                        link = urljoin(board['url'], container['href'])
                        location = ''
                        description = ''
                        date_posted = ''
                    else:
                        title_elem = container.select_one(selectors.get('title', 'h2'))
                        title = title_elem.text.strip() if title_elem else 'No title'

                        location_elem = container.select_one(selectors.get('location', ''))
                        location = location_elem.text.strip() if location_elem else ''

                        description_elem = container.select_one(selectors.get('description', ''))
                        description = description_elem.text.strip() if description_elem else ''

                        link_elem = container.select_one(selectors.get('link', 'a'))
                        link = ''
                        if link_elem and link_elem.get('href'):
                            link = urljoin(board['url'], link_elem['href'])

                        date_elem = container.select_one(selectors.get('date_posted', ''))
                        date_posted = date_elem.text.strip() if date_elem else ''

                    job = {
                        'title': title,
                        'company': board.get('name', 'Unknown'),
                        'location': location,
                        'description': description[:500],
                        'url': link,
                        'date_posted': date_posted,
                        'source': board['name'],
                        'scraped_at': datetime.now().isoformat()
                    }
                    job['id'] = self.generate_job_id(job)
                    jobs.append(job)

                except Exception as e:
                    print(f"Error parsing job container: {e}")
                    continue

        except requests.RequestException as e:
            print(f"Error scraping {board['name']}: {e}")

        return jobs

    def scrape_greenhouse(self, board: Dict) -> List[Dict]:
        """Scrape Greenhouse job boards"""
        jobs = []
        try:
            # Greenhouse boards often have JSON endpoints
            api_url = board['url'].rstrip('/') + '/embed/jobs.json'
            response = requests.get(api_url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                for job_data in data.get('jobs', []):
                    job = {
                        'title': job_data.get('title', 'No title'),
                        'company': board.get('name', 'Unknown'),
                        'location': job_data.get('location', {}).get('name', ''),
                        'description': '',
                        'url': job_data.get('absolute_url', ''),
                        'date_posted': job_data.get('updated_at', ''),
                        'source': board['name'],
                        'scraped_at': datetime.now().isoformat()
                    }
                    job['id'] = self.generate_job_id(job)
                    jobs.append(job)
            else:
                # Fallback to HTML scraping
                jobs = self.scrape_greenhouse_html(board)

        except Exception as e:
            print(f"Error scraping Greenhouse board {board['name']}: {e}")
            # Try HTML fallback
            jobs = self.scrape_greenhouse_html(board)

        return jobs

    def scrape_greenhouse_html(self, board: Dict) -> List[Dict]:
        """Scrape Greenhouse boards via HTML"""
        jobs = []
        try:
            response = requests.get(board['url'], headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            job_sections = soup.select('section.level-0')
            for section in job_sections:
                job_links = section.select('div.opening a')
                for link in job_links:
                    job = {
                        'title': link.text.strip(),
                        'company': board.get('name', 'Unknown'),
                        'location': '',
                        'description': '',
                        'url': urljoin(board['url'], link.get('href', '')),
                        'date_posted': '',
                        'source': board['name'],
                        'scraped_at': datetime.now().isoformat()
                    }
                    job['id'] = self.generate_job_id(job)
                    jobs.append(job)

        except Exception as e:
            print(f"Error scraping Greenhouse HTML for {board['name']}: {e}")

        return jobs

    def scrape_lever(self, board: Dict) -> List[Dict]:
        """Scrape Lever job boards with JSON API and HTML fallback"""
        jobs = []
        try:
            # Try Lever JSON API first
            api_url = board['url'].rstrip('/') + '?mode=json'
            response = requests.get(api_url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                # Check if response is actually JSON
                try:
                    job_listings = response.json()
                    # Parse JSON response
                    for job_data in job_listings:
                        job = {
                            'title': job_data.get('text', 'No title'),
                            'company': board.get('name', 'Unknown'),
                            'location': job_data.get('categories', {}).get('location', ''),
                            'description': job_data.get('description', '')[:500],
                            'url': job_data.get('hostedUrl', ''),
                            'date_posted': str(job_data.get('createdAt', '')),
                            'source': board['name'],
                            'scraped_at': datetime.now().isoformat()
                        }
                        job['id'] = self.generate_job_id(job)
                        jobs.append(job)
                    return jobs
                except ValueError:
                    # JSON parsing failed, response is HTML - fall back to HTML parsing
                    print(f"  Lever JSON API not available for {board['name']}, using HTML fallback")
                    pass

            # HTML fallback: parse the page directly
            html_url = board['url'].rstrip('/')
            response = requests.get(html_url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                postings = soup.find_all('div', class_='posting')

                for posting in postings:
                    # Extract title
                    title_elem = posting.find('h5')
                    title = title_elem.get_text(strip=True) if title_elem else 'No title'

                    # Extract link
                    link_elem = posting.find('a', href=True)
                    url = link_elem.get('href', '') if link_elem else ''

                    # Extract location
                    location_elem = posting.find(class_='location')
                    location = location_elem.get_text(strip=True) if location_elem else ''

                    # Extract team/department if available
                    department_elem = posting.find(class_='department')
                    department = department_elem.get_text(strip=True) if department_elem else ''

                    job = {
                        'title': title,
                        'company': board.get('name', 'Unknown'),
                        'location': location,
                        'department': department,
                        'description': '',  # HTML version doesn't have description on listing page
                        'url': url,
                        'date_posted': '',  # HTML version doesn't have date on listing page
                        'source': board['name'],
                        'scraped_at': datetime.now().isoformat()
                    }
                    job['id'] = self.generate_job_id(job)
                    jobs.append(job)

        except Exception as e:
            print(f"Error scraping Lever board {board['name']}: {e}")

        return jobs

    def scrape_api(self, board: Dict) -> List[Dict]:
        """Scrape jobs from custom API endpoints"""
        jobs = []
        try:
            headers = self.headers.copy()
            if 'headers' in board:
                headers.update(board['headers'])

            response = requests.get(board['url'], headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Customize based on your API structure
            job_list = data if isinstance(data, list) else data.get('jobs', [])

            for job_data in job_list:
                job = {
                    'title': job_data.get('title', 'No title'),
                    'company': job_data.get('company', board.get('name', 'Unknown')),
                    'location': job_data.get('location', ''),
                    'description': job_data.get('description', '')[:500],
                    'url': job_data.get('url', job_data.get('link', '')),
                    'date_posted': job_data.get('posted_date', job_data.get('date', '')),
                    'source': board['name'],
                    'scraped_at': datetime.now().isoformat()
                }
                job['id'] = self.generate_job_id(job)
                jobs.append(job)

        except Exception as e:
            print(f"Error scraping API {board['name']}: {e}")

        return jobs

    def scrape_nextjs(self, board: Dict) -> List[Dict]:
        """Scrape Next.js job boards with embedded __NEXT_DATA__"""
        jobs = []
        try:
            response = requests.get(board['url'], headers=self.headers, timeout=15)
            response.raise_for_status()

            # Find __NEXT_DATA__ script tag
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                            response.text, re.DOTALL)

            if match:
                data = json.loads(match.group(1))

                # Extract job list from pageProps
                job_list = []
                if 'props' in data and 'pageProps' in data['props']:
                    page_props = data['props']['pageProps']
                    job_list = page_props.get('list', page_props.get('jobs', []))

                for job_data in job_list:
                    # Skip dummy or inactive jobs
                    if job_data.get('jobTitle', '').lower() == 'dummy job':
                        continue
                    if not job_data.get('visible', True):
                        continue
                    if job_data.get('status') != 'active':
                        continue

                    # Extract location
                    locations = job_data.get('officeLocations', [])
                    location = locations[0].get('title', '') if locations else ''

                    job = {
                        'title': job_data.get('jobTitle', 'No title'),
                        'company': board.get('name', 'Unknown'),
                        'location': location,
                        'description': job_data.get('description', '')[:500],
                        'url': urljoin(board['url'], f"/positions/{job_data.get('id', '')}"),
                        'date_posted': '',
                        'source': board['name'],
                        'scraped_at': datetime.now().isoformat()
                    }
                    job['id'] = self.generate_job_id(job)
                    jobs.append(job)
            else:
                print(f"Could not find Next.js data in {board['name']}")

        except Exception as e:
            print(f"Error scraping Next.js board {board['name']}: {e}")

        return jobs

    def scrape_ashby(self, board: Dict) -> List[Dict]:
        """Scrape Ashby job boards"""
        jobs = []
        try:
            response = requests.get(board['url'], headers=self.headers, timeout=15)
            response.raise_for_status()

            # Parse HTML to extract embedded JSON data
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find script tag with window.__appData
            script_tags = soup.find_all('script')
            job_data = None

            for script in script_tags:
                if script.string and 'window.__appData' in script.string:
                    # Extract JSON from window.__appData using regex
                    script_content = script.string
                    match = re.search(r'window\.__appData\s*=\s*(\{.*?\});', script_content, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        job_data = json.loads(json_str)
                        break

            # Check multiple possible structures for job postings
            job_postings = []
            if job_data:
                if 'jobPostings' in job_data:
                    job_postings = job_data['jobPostings']
                elif 'jobBoard' in job_data and isinstance(job_data['jobBoard'], dict):
                    # Check nested structure
                    job_board = job_data['jobBoard']
                    if 'jobPostings' in job_board:
                        job_postings = job_board['jobPostings']
                    elif 'jobs' in job_board:
                        job_postings = job_board['jobs']

            if job_postings:
                for job_posting in job_postings:
                    if not job_posting.get('isListed', True):
                        continue

                    job = {
                        'title': job_posting.get('title', 'No title'),
                        'company': board.get('name', 'Unknown'),
                        'location': job_posting.get('locationName', ''),
                        'description': job_posting.get('descriptionPlain', '')[:500],
                        'url': urljoin(board['url'], f"/{job_posting.get('id', '')}"),
                        'date_posted': job_posting.get('publishedDate', ''),
                        'source': board['name'],
                        'employment_type': job_posting.get('employmentType', ''),
                        'department': job_posting.get('departmentName', ''),
                        'scraped_at': datetime.now().isoformat()
                    }
                    job['id'] = self.generate_job_id(job)
                    jobs.append(job)
            else:
                print(f"Could not find job data in Ashby board {board['name']}")

        except Exception as e:
            print(f"Error scraping Ashby board {board['name']}: {e}")

        return jobs

    def scrape_board(self, board: Dict) -> List[Dict]:
        """Scrape a single job board based on its type"""
        board_type = board.get('type', 'generic').lower()

        scraper_map = {
            'generic': self.scrape_generic,
            'greenhouse': self.scrape_greenhouse,
            'lever': self.scrape_lever,
            'ashby': self.scrape_ashby,
            'nextjs': self.scrape_nextjs,
            'api': self.scrape_api,
        }

        scraper_func = scraper_map.get(board_type, self.scrape_generic)
        return scraper_func(board)

    def load_existing_jobs(self, filepath: str) -> List[Dict]:
        """Load existing jobs from file"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def dedupe_jobs(self, new_jobs: List[Dict], existing_jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on job ID"""
        existing_ids = {job['id'] for job in existing_jobs}
        return [job for job in new_jobs if job['id'] not in existing_ids]

    def clean_old_jobs(self, jobs: List[Dict], max_age_days: int) -> List[Dict]:
        """Remove jobs older than max_age_days"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        cleaned_jobs = []
        for job in jobs:
            try:
                scraped_at = datetime.fromisoformat(job.get('scraped_at', ''))
                if scraped_at > cutoff_date:
                    cleaned_jobs.append(job)
            except (ValueError, TypeError):
                # Keep job if we can't parse date
                cleaned_jobs.append(job)

        return cleaned_jobs

    def save_jobs(self, jobs: List[Dict], filepath: str):
        """Save jobs to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(jobs, f, indent=2)
        print(f"Saved {len(jobs)} jobs to {filepath}")

    def export_to_csv(self, jobs: List[Dict], csv_path: str):
        """Export jobs to CSV format"""
        try:
            with open(csv_path, 'w') as f:
                f.write("Company,Title,Location,Department,Type,URL,Date Posted,Scraped At\n")
                for job in jobs:
                    company = job['source'].replace(',', ' ')
                    title = job['title'].replace(',', ' ')
                    location = job.get('location', '').replace(',', ' ')
                    department = job.get('department', '').replace(',', ' ')
                    emp_type = job.get('employment_type', '').replace(',', ' ')
                    url = job['url']
                    date_posted = job.get('date_posted', '')
                    scraped_at = job.get('scraped_at', '')
                    f.write(f"{company},{title},{location},{department},{emp_type},{url},{date_posted},{scraped_at}\n")
            print(f"Exported to CSV: {csv_path}")
        except Exception as e:
            print(f"Warning: Could not export CSV: {e}")

    def send_notification(self, title: str, message: str):
        """Send macOS notification"""
        try:
            os.system(f"""
                osascript -e 'display notification "{message}" with title "{title}"'
            """)
        except:
            pass  # Silently fail if notifications don't work

    def run(self):
        """Main scraping workflow"""
        print(f"Starting job scrape at {datetime.now()}")

        settings = self.config.get('settings', {})
        output_file = os.path.join(
            os.path.dirname(__file__),
            settings.get('output_file', 'jobs.json')
        )

        # Load existing jobs
        existing_jobs = self.load_existing_jobs(output_file)
        print(f"Loaded {len(existing_jobs)} existing jobs")

        # Scrape all enabled job boards
        all_new_jobs = []
        for board in self.config.get('job_boards', []):
            if not board.get('enabled', False):
                print(f"Skipping disabled board: {board.get('name', 'Unknown')}")
                continue

            print(f"Scraping {board.get('name', 'Unknown')}...")
            jobs = self.scrape_board(board)
            print(f"  Found {len(jobs)} jobs")
            all_new_jobs.extend(jobs)

        # Deduplicate if enabled
        if settings.get('dedupe', True):
            unique_new_jobs = self.dedupe_jobs(all_new_jobs, existing_jobs)
            print(f"Found {len(unique_new_jobs)} new unique jobs")
        else:
            unique_new_jobs = all_new_jobs

        # Combine with existing jobs
        all_jobs = existing_jobs + unique_new_jobs

        # Clean old jobs if max_age_days is set
        max_age = settings.get('max_age_days')
        if max_age:
            all_jobs = self.clean_old_jobs(all_jobs, max_age)
            print(f"After cleaning old jobs: {len(all_jobs)} total jobs")

        # Save results
        self.save_jobs(all_jobs, output_file)

        # Auto-export to CSV
        csv_path = output_file.replace('.json', '.csv')
        self.export_to_csv(all_jobs, csv_path)

        # Export to text file as well
        txt_path = output_file.replace('.json', '_titles.txt')
        try:
            with open(txt_path, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write(f"JOB TITLES - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("=" * 70 + "\n")
                f.write(f"Total Jobs: {len(all_jobs)}\n")
                f.write("=" * 70 + "\n\n")

                from collections import defaultdict
                by_company = defaultdict(list)
                for job in all_jobs:
                    by_company[job['source']].append(job)

                for company in sorted(by_company.keys()):
                    company_jobs = by_company[company]
                    f.write(f"\n{company} ({len(company_jobs)} jobs)\n")
                    f.write("-" * 70 + "\n")
                    for i, job in enumerate(company_jobs, 1):
                        location = f" | {job['location']}" if job['location'] else ""
                        f.write(f"{i}. {job['title']}{location}\n")

                f.write("\n" + "=" * 70 + "\n")
            print(f"Exported to TXT: {txt_path}")
        except Exception as e:
            print(f"Warning: Could not export TXT: {e}")

        # Send notification if new jobs found
        if len(unique_new_jobs) > 0:
            self.send_notification(
                "Job Scraper",
                f"Found {len(unique_new_jobs)} new job(s)! Total: {len(all_jobs)}"
            )

        print(f"Scraping completed at {datetime.now()}")
        print(f"New jobs found: {len(unique_new_jobs)}")
        print(f"Total jobs stored: {len(all_jobs)}")
        print(f"\nFiles updated:")
        print(f"  • {output_file}")
        print(f"  • {csv_path}")
        print(f"  • {txt_path}")


def main():
    """Main entry point"""
    scraper = JobScraper()
    scraper.run()


if __name__ == '__main__':
    main()
