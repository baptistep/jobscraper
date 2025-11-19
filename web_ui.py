#!/usr/bin/env python3
"""
Simple web interface for DailyScraper
View tracked websites, jobs, and add new job boards
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'dailyscraper-secret-key-change-in-production'

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
JOBS_PATH = os.path.join(BASE_DIR, 'jobs.json')


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
