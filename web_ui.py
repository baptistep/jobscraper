#!/usr/bin/env python3
"""
Simple web interface for DailyScraper
View tracked websites, jobs, and add new job boards
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
import threading
import subprocess
import sys

app = Flask(__name__)
app.secret_key = 'dailyscraper-secret-key-change-in-production'

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
JOBS_PATH = os.path.join(BASE_DIR, 'jobs.json')
SCRAPER_PATH = os.path.join(BASE_DIR, 'scraper.py')

# Global state for scraping status
scraping_status = {
    'running': False,
    'last_run': None,
    'last_result': None,
    'error': None
}


def load_config():
    """Load configuration from config.json"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'job_boards': [], 'settings': {}}


def save_config(config):
    """Save configuration to config.json"""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def load_jobs():
    """Load jobs from jobs.json"""
    try:
        with open(JOBS_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def is_new_job(job, hours=24):
    """Check if a job was scraped within the last N hours"""
    try:
        scraped_at = datetime.fromisoformat(job.get('scraped_at', ''))
        return datetime.now() - scraped_at < timedelta(hours=hours)
    except (ValueError, TypeError):
        return False


def group_jobs_by_source(jobs):
    """Group jobs by their source/company"""
    grouped = {}
    for job in jobs:
        source = job.get('source', 'Unknown')
        if source not in grouped:
            grouped[source] = []
        grouped[source].append(job)

    # Sort jobs within each group by scraped_at (newest first)
    for source in grouped:
        grouped[source].sort(key=lambda x: x.get('scraped_at', ''), reverse=True)

    return grouped


def auto_detect_selectors(url):
    """
    Automatically detect CSS selectors for a job board URL
    Returns a dict of detected selectors or error message
    """
    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Common patterns for job listings
        job_patterns = [
            # Class-based patterns
            {'selector': 'div.job', 'priority': 1},
            {'selector': 'div.job-listing', 'priority': 1},
            {'selector': 'div.job-item', 'priority': 1},
            {'selector': 'div.position', 'priority': 1},
            {'selector': 'div.opening', 'priority': 1},
            {'selector': 'div.posting', 'priority': 1},
            {'selector': 'div[class*="job"]', 'priority': 2},
            {'selector': 'div[class*="position"]', 'priority': 2},
            {'selector': 'div[class*="career"]', 'priority': 2},
            {'selector': 'article', 'priority': 3},
            {'selector': 'li.job', 'priority': 1},
            {'selector': 'li[class*="job"]', 'priority': 2},
            # ID-based patterns
            {'selector': 'div#jobs div', 'priority': 2},
            {'selector': 'div#careers div', 'priority': 2},
        ]

        # Try each pattern to find job containers
        job_container_selector = None
        containers = []

        for pattern in sorted(job_patterns, key=lambda x: x['priority']):
            containers = soup.select(pattern['selector'])
            if len(containers) >= 2:  # At least 2 job listings found
                job_container_selector = pattern['selector']
                break

        if not job_container_selector or len(containers) < 2:
            return {'error': 'Could not find multiple job listings on the page. Try manual entry.'}

        # Analyze first container to find title, link, location patterns
        first_container = containers[0]

        selectors = {
            'job_container': job_container_selector,
            'title': '',
            'link': '',
            'location': '',
            'description': '',
            'date_posted': ''
        }

        # Detect title selector
        title_patterns = [
            'h1', 'h2', 'h3', 'h4',
            '.title', '.job-title', '.position-title',
            '[class*="title"]', '[class*="heading"]'
        ]
        for pattern in title_patterns:
            title_elem = first_container.select_one(pattern)
            if title_elem and title_elem.get_text(strip=True):
                selectors['title'] = pattern
                break

        # Detect link selector
        link_elem = first_container.find('a', href=True)
        if link_elem:
            # Try to find most specific selector
            if link_elem.get('class'):
                selectors['link'] = f"a.{link_elem['class'][0]}"
            else:
                selectors['link'] = 'a'

        # Detect location selector
        location_patterns = [
            '.location', '.job-location', '[class*="location"]',
            '.city', '[class*="city"]',
            'span:contains("Location")', 'div:contains("Location")'
        ]
        for pattern in location_patterns:
            loc_elem = first_container.select_one(pattern)
            if loc_elem and loc_elem.get_text(strip=True):
                selectors['location'] = pattern
                break

        # Detect date posted selector
        date_patterns = [
            'time', '.date', '.posted', '[class*="date"]', '[class*="posted"]'
        ]
        for pattern in date_patterns:
            date_elem = first_container.select_one(pattern)
            if date_elem:
                selectors['date_posted'] = pattern
                break

        # Detect description selector
        desc_patterns = [
            '.description', '.summary', 'p', '[class*="description"]'
        ]
        for pattern in desc_patterns:
            desc_elem = first_container.select_one(pattern)
            if desc_elem and len(desc_elem.get_text(strip=True)) > 20:
                selectors['description'] = pattern
                break

        # Filter out empty selectors
        selectors = {k: v for k, v in selectors.items() if v}

        # Add success info
        selectors['success'] = True
        selectors['found_jobs'] = len(containers)

        return selectors

    except requests.RequestException as e:
        return {'error': f'Failed to fetch URL: {str(e)}'}
    except Exception as e:
        return {'error': f'Error analyzing page: {str(e)}'}


def run_scraper_background():
    """Run the scraper in the background"""
    global scraping_status

    try:
        scraping_status['running'] = True
        scraping_status['error'] = None

        # Run scraper as subprocess to capture output
        result = subprocess.run(
            [sys.executable, SCRAPER_PATH],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # Parse output to get stats
        output = result.stdout
        stderr = result.stderr
        new_jobs = 0
        total_jobs = 0
        errors = []

        # Extract numbers and errors from output
        for line in output.split('\n'):
            if 'New jobs found:' in line:
                try:
                    new_jobs = int(line.split(':')[1].strip())
                except:
                    pass
            if 'Total jobs stored:' in line:
                try:
                    total_jobs = int(line.split(':')[1].strip())
                except:
                    pass
            if 'Error scraping' in line:
                errors.append(line.strip())

        scraping_status['last_result'] = {
            'new_jobs': new_jobs,
            'total_jobs': total_jobs,
            'success': result.returncode == 0,
            'errors': errors,
            'output': output  # Include full output for debugging
        }
        scraping_status['last_run'] = datetime.now().isoformat()

        if result.returncode != 0:
            scraping_status['error'] = f"Scraper exited with code {result.returncode}"
            if result.stderr:
                scraping_status['error'] += f": {result.stderr[:200]}"

    except subprocess.TimeoutExpired:
        scraping_status['error'] = 'Scraper timed out after 5 minutes'
    except Exception as e:
        scraping_status['error'] = f'Error running scraper: {str(e)}'
    finally:
        scraping_status['running'] = False


@app.route('/')
def index():
    """Main dashboard page"""
    config = load_config()
    jobs = load_jobs()

    # Group jobs by source
    grouped_jobs = group_jobs_by_source(jobs)

    # Calculate stats
    total_jobs = len(jobs)
    new_jobs_count = sum(1 for job in jobs if is_new_job(job))
    active_boards = sum(1 for board in config.get('job_boards', []) if board.get('enabled', True))

    # Mark new jobs
    for source_jobs in grouped_jobs.values():
        for job in source_jobs:
            job['is_new'] = is_new_job(job)

    return render_template('dashboard.html',
                         job_boards=config.get('job_boards', []),
                         grouped_jobs=grouped_jobs,
                         total_jobs=total_jobs,
                         new_jobs_count=new_jobs_count,
                         active_boards=active_boards)


@app.route('/boards')
def boards():
    """View and manage job boards"""
    config = load_config()
    return render_template('boards.html', job_boards=config.get('job_boards', []))


@app.route('/boards/add', methods=['GET', 'POST'])
def add_board():
    """Add a new job board"""
    if request.method == 'POST':
        config = load_config()

        # Create new board from form data
        new_board = {
            'name': request.form.get('name'),
            'url': request.form.get('url'),
            'type': request.form.get('type'),
            'enabled': True
        }

        # Add selectors for generic type
        if new_board['type'] == 'generic':
            selectors = {}
            for key in ['job_container', 'title', 'location', 'description', 'link', 'date_posted']:
                value = request.form.get(f'selector_{key}', '').strip()
                if value:
                    selectors[key] = value

            # Validate required selectors
            required = ['job_container', 'title', 'link']
            missing = [r for r in required if r not in selectors]
            if missing:
                flash(f"Error: Generic boards require these selectors: {', '.join(missing)}. Use auto-detect or fill manually.", 'error')
                return redirect(url_for('add_board'))

            new_board['selectors'] = selectors

        # Add to config
        if 'job_boards' not in config:
            config['job_boards'] = []
        config['job_boards'].append(new_board)

        # Save config
        save_config(config)

        flash(f"Company '{new_board['name']}' added successfully!", 'success')
        return redirect(url_for('boards'))

    return render_template('add_board.html')


@app.route('/api/auto-detect', methods=['POST'])
def api_auto_detect():
    """API endpoint to auto-detect selectors from a URL"""
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    result = auto_detect_selectors(url)
    return jsonify(result)


@app.route('/api/scrape', methods=['POST'])
def api_trigger_scrape():
    """API endpoint to trigger manual scraping"""
    global scraping_status

    if scraping_status['running']:
        return jsonify({'error': 'Scraper is already running'}), 409

    # Start scraper in background thread
    thread = threading.Thread(target=run_scraper_background, daemon=True)
    thread.start()

    return jsonify({'message': 'Scraper started', 'status': 'running'})


@app.route('/api/scrape/status')
def api_scrape_status():
    """API endpoint to check scraper status"""
    return jsonify(scraping_status)


@app.route('/boards/toggle/<int:board_index>')
def toggle_board(board_index):
    """Toggle a board's enabled status"""
    config = load_config()

    if 0 <= board_index < len(config.get('job_boards', [])):
        config['job_boards'][board_index]['enabled'] = not config['job_boards'][board_index].get('enabled', True)
        save_config(config)
        flash('Company status updated!', 'success')
    else:
        flash('Company not found!', 'error')

    return redirect(url_for('boards'))


@app.route('/boards/delete/<int:board_index>')
def delete_board(board_index):
    """Delete a job board"""
    config = load_config()

    if 0 <= board_index < len(config.get('job_boards', [])):
        removed = config['job_boards'].pop(board_index)
        save_config(config)
        flash(f"Company '{removed['name']}' deleted!", 'success')
    else:
        flash('Company not found!', 'error')

    return redirect(url_for('boards'))


@app.route('/jobs')
def all_jobs():
    """View all jobs"""
    jobs = load_jobs()

    # Mark new jobs
    for job in jobs:
        job['is_new'] = is_new_job(job)

    # Sort by scraped_at (newest first)
    jobs.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)

    return render_template('jobs.html', jobs=jobs)


@app.route('/jobs/<source>')
def jobs_by_source(source):
    """View jobs for a specific source"""
    jobs = load_jobs()
    filtered_jobs = [job for job in jobs if job.get('source') == source]

    # Mark new jobs
    for job in filtered_jobs:
        job['is_new'] = is_new_job(job)

    # Sort by scraped_at (newest first)
    filtered_jobs.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)

    return render_template('jobs.html', jobs=filtered_jobs, source=source)


@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    config = load_config()
    jobs = load_jobs()

    return jsonify({
        'total_jobs': len(jobs),
        'new_jobs': sum(1 for job in jobs if is_new_job(job)),
        'active_boards': sum(1 for board in config.get('job_boards', []) if board.get('enabled', True)),
        'total_boards': len(config.get('job_boards', []))
    })


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(BASE_DIR, 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    print("=" * 60)
    print("DailyScraper Web Interface")
    print("=" * 60)
    print(f"\nStarting server at http://localhost:5001")
    print("\nPress CTRL+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5001)
