# Quick Start Guide

## Daily Usage

### Run scraper manually
```bash
python3 scraper.py
```

### View all jobs
```bash
cat jobs.json | python3 -m json.tool | less
```

### See job count
```bash
python3 -c "import json; print(f'Total jobs: {len(json.load(open(\"jobs.json\")))}')"
```

### View summary by company
```bash
python3 -c "
import json
from collections import defaultdict

jobs = json.load(open('jobs.json'))
by_source = defaultdict(int)

for job in jobs:
    by_source[job['source']] += 1

print('Jobs by company:')
for source, count in sorted(by_source.items()):
    print(f'  {source}: {count} jobs')
print(f'\nTotal: {len(jobs)} jobs')
"
```

## Configuration

### Add a job board (interactive)
```bash
python3 add_board.py
```

### Edit config manually
```bash
nano config.json
# or
open -a TextEdit config.json
```

### Disable a board
Edit `config.json` and set `"enabled": false`

### View current config
```bash
python3 -c "
import json
config = json.load(open('config.json'))
for board in config['job_boards']:
    status = '✅' if board.get('enabled') else '❌'
    print(f'{status} {board[\"name\"]} ({board[\"type\"]})')
"
```

## Automatic Scheduling

### Enable automatic runs (9 AM & 6 PM daily)
```bash
cp com.dailyscraper.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.dailyscraper.plist
```

### Check if scheduler is running
```bash
launchctl list | grep dailyscraper
```

### View logs
```bash
tail -f logs/scraper.log
# or
tail -f logs/scraper.error.log
```

### Stop automatic runs
```bash
launchctl unload ~/Library/LaunchAgents/com.dailyscraper.plist
```

### Change schedule times
1. Edit `com.dailyscraper.plist`
2. Change `<integer>9</integer>` and `<integer>18</integer>` to your preferred hours (0-23)
3. Reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.dailyscraper.plist
cp com.dailyscraper.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.dailyscraper.plist
```

## Troubleshooting

### No new jobs found
- This is normal if you ran it recently
- Jobs are deduplicated automatically
- Old jobs (>30 days) are auto-removed

### Error: module not found
```bash
pip3 install -r requirements.txt
```

### See detailed errors
```bash
cat logs/scraper.error.log
```

### Test a specific board
Temporarily disable others in `config.json` by setting `"enabled": false`

## File Locations

- **Config**: `config.json` (your settings)
- **Jobs**: `jobs.json` (scraped data)
- **Logs**: `logs/scraper.log` and `logs/scraper.error.log`
- **Schedule**: `~/Library/LaunchAgents/com.dailyscraper.plist`

## Quick Tips

- Run `python3 scraper.py` anytime to get latest jobs
- Jobs are automatically deduplicated by title+company+url
- Old jobs are removed after 30 days (configurable in config.json)
- All 3 of your boards are currently enabled and working
- Check logs if something seems wrong: `tail -f logs/scraper.log`
