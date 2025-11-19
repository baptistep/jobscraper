# Job Board Scraper

An automated job board scraper that runs twice daily to fetch new job postings from multiple sources. Easily shareable and configurable for different job boards.

## Features

- **Web Interface**: Beautiful, simple web UI to view jobs, manage companies, and add new trackers
- **Multiple Job Board Support**: Works with Greenhouse, Lever, Ashby, Next.js, generic job boards, and custom APIs
- **Automatic Deduplication**: Prevents duplicate job postings
- **Scheduled Execution**: Runs twice daily (9 AM & 6 PM) via launchd/cron
- **Easy Configuration**: JSON-based config that's simple to share and modify
- **Extensible**: Add new job boards without touching code
- **Data Persistence**: Stores jobs in JSON format with automatic cleanup
- **New Job Highlighting**: Automatically highlights jobs scraped in the last 24 hours

## Quick Start

### 1. Clone or Download This Repository

```bash
cd /path/to/DailyScraper
```

### 2. Run Setup Script

```bash
./setup.sh
```

This will:
- Check Python 3 installation
- Install required dependencies
- Create `config.json` from template
- Create logs directory
- Run a test scrape

### 3. Add Your Job Boards

#### Option A: Interactive Helper (Recommended)

```bash
python3 add_board.py
```

Follow the prompts to add job boards. The script will help you configure:
- Board name and URL
- Board type (Generic, Greenhouse, Lever, or API)
- CSS selectors (for generic boards)
- API headers (for API boards)

#### Option B: Manual Configuration

Edit `config.json` directly:

```json
{
  "job_boards": [
    {
      "name": "My Company Careers",
      "url": "https://company.com/careers",
      "type": "generic",
      "enabled": true,
      "selectors": {
        "job_container": "div.job-listing",
        "title": "h3.job-title",
        "location": "span.location",
        "link": "a.apply-link"
      }
    }
  ]
}
```

### 4. Test the Scraper

```bash
python3 scraper.py
```

Check `jobs.json` for results.

### 5. Start the Web Interface (Optional)

Launch the web UI to view and manage your jobs:

```bash
python3 web_ui.py
```

Then open your browser to **http://localhost:5001**

The web interface provides:
- **Dashboard**: Overview of all tracked companies and their jobs
- **Companies Tracked**: Manage your tracked companies (enable/disable/delete)
- **Add New Company**: Easy form to add new job boards
- **Job Listings**: View all jobs with new ones highlighted
- **Sorting**: Jobs automatically sorted by most recently scraped

## Supported Job Board Types

### 1. Generic Boards (Custom CSS Selectors)

For any job board, you just need to find the CSS selectors:

```json
{
  "name": "Company Careers",
  "url": "https://company.com/careers",
  "type": "generic",
  "enabled": true,
  "selectors": {
    "job_container": "div.job-item",
    "title": "h2.title",
    "location": "span.location",
    "description": "p.description",
    "link": "a",
    "date_posted": "time"
  }
}
```

**How to find selectors:**
1. Open the job board in your browser
2. Right-click on a job listing → Inspect
3. Find the CSS selector for each element
4. Test selectors in browser console: `document.querySelectorAll('your-selector')`

### 2. Greenhouse Boards

Many companies use Greenhouse for their careers pages:

```json
{
  "name": "Company Name",
  "url": "https://boards.greenhouse.io/company",
  "type": "greenhouse",
  "enabled": true
}
```

The scraper automatically uses Greenhouse's JSON API.

### 3. Lever Boards

Similar to Greenhouse, Lever has a standard structure:

```json
{
  "name": "Company Name",
  "url": "https://jobs.lever.co/company",
  "type": "lever",
  "enabled": true
}
```

### 4. Custom APIs

For job boards with public APIs:

```json
{
  "name": "API Job Board",
  "url": "https://api.company.com/jobs",
  "type": "api",
  "enabled": true,
  "headers": {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
  }
}
```

## Configuration Reference

### Settings

```json
{
  "settings": {
    "output_file": "jobs.json",
    "dedupe": true,
    "max_age_days": 30,
    "notifications": {
      "enabled": false,
      "email": "your-email@example.com"
    }
  }
}
```

- **output_file**: Where to save job data
- **dedupe**: Remove duplicate jobs (recommended: true)
- **max_age_days**: Auto-delete jobs older than X days (set to null to keep all)
- **notifications**: Email notifications (not yet implemented)

## Setting Up Scheduled Runs

### macOS (launchd)

1. Edit the plist file to use your username:
```bash
nano com.dailyscraper.plist
```

2. Update the paths to match your setup, then:
```bash
cp com.dailyscraper.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.dailyscraper.plist
```

3. Verify it's running:
```bash
launchctl list | grep dailyscraper
```

4. To stop:
```bash
launchctl unload ~/Library/LaunchAgents/com.dailyscraper.plist
```

### Linux (cron)

```bash
crontab -e
```

Add these lines for 9 AM and 6 PM daily:
```
0 9 * * * cd /path/to/DailyScraper && /usr/bin/python3 scraper.py >> logs/scraper.log 2>> logs/scraper.error.log
0 18 * * * cd /path/to/DailyScraper && /usr/bin/python3 scraper.py >> logs/scraper.log 2>> logs/scraper.error.log
```

Change times by editing the hour (9 and 18).

## Sharing with Others

To share this scraper with teammates:

1. **Copy the entire folder** or push to Git:
```bash
git init
git add .
git commit -m "Initial job scraper setup"
git push origin main
```

2. **Recipients run**:
```bash
git clone <your-repo>
cd DailyScraper
./setup.sh
```

3. **They customize** `config.json` with their job boards

**Note**: `config.json` is gitignored by default (may contain API keys). Share `config.example.json` instead.

## Finding CSS Selectors (Tutorial)

1. Open job board in Chrome/Firefox
2. Right-click on job title → Inspect Element
3. In DevTools, right-click the highlighted HTML → Copy → Copy selector
4. Test in console: `document.querySelector('paste-selector-here')`
5. For multiple jobs, use: `document.querySelectorAll('container-selector')`

Example:
```javascript
// Find all job containers
document.querySelectorAll('div.job-posting')

// Find title within each container
document.querySelector('div.job-posting h2.title')
```

## Troubleshooting

### No jobs found

- Check that `enabled: true` for your boards
- Verify selectors are correct (websites change their HTML)
- Check `logs/scraper.error.log` for errors
- Test manually: `python3 scraper.py`

### Import errors

```bash
pip3 install -r requirements.txt
```

### Permission denied

```bash
chmod +x setup.sh add_board.py scraper.py
```

### Jobs not updating

- Check if scraper is running: `launchctl list | grep dailyscraper` (macOS)
- Check logs: `tail -f logs/scraper.log`
- Manually run: `python3 scraper.py`

## File Structure

```
DailyScraper/
├── scraper.py              # Main scraper script
├── web_ui.py               # Web interface for viewing jobs
├── add_board.py            # Interactive helper to add job boards
├── setup.sh                # Setup script
├── config.json             # Your configuration (gitignored)
├── config.example.json     # Example config to share
├── requirements.txt        # Python dependencies
├── com.dailyscraper.plist  # macOS launchd config
├── jobs.json               # Scraped jobs (gitignored)
├── templates/              # HTML templates for web UI
│   ├── base.html
│   ├── dashboard.html
│   ├── boards.html
│   ├── add_board.html
│   └── jobs.html
├── logs/                   # Log files (gitignored)
│   ├── scraper.log
│   └── scraper.error.log
└── README.md
```

## Advanced Usage

### View Jobs

```bash
# Pretty print all jobs
cat jobs.json | python3 -m json.tool | less

# Count total jobs
cat jobs.json | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"

# Filter by company
cat jobs.json | python3 -c "import json,sys; jobs=[j for j in json.load(sys.stdin) if 'Google' in j['company']]; print(json.dumps(jobs, indent=2))"
```

### Custom Scraper Extensions

To add support for a new board type:

1. Edit `scraper.py`
2. Add a new method like `scrape_myboardtype(self, board: Dict)`
3. Update `scraper_map` in `scrape_board()` method
4. Add example to `config.example.json`

## Legal & Ethics

- **Check robots.txt**: Respect website scraping policies
- **Check Terms of Service**: Some sites prohibit scraping
- **Rate Limiting**: The scraper includes delays and runs twice daily
- **APIs First**: Use official APIs when available
- **Personal Use**: This tool is for personal job searching, not commercial data collection

## Contributing

To improve this scraper:

1. Fork the repository
2. Add your improvements
3. Submit a pull request

Ideas for contributions:
- Email notifications when new jobs found
- Webhook support (Slack, Discord)
- More board type integrations (Workday, SAP SuccessFactors, etc.)
- Search/filter functionality in web UI
- Export jobs to different formats
- Job alerts based on keywords

## License

This project is provided as-is for personal use. Modify and share freely.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs in `logs/`
3. Test with `python3 scraper.py -v` (if verbose mode added)
4. Open an issue on GitHub
