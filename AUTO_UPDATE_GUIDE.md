# Auto-Update CSV Guide

## 🎉 What's Set Up

The scraper now **AUTOMATICALLY** updates CSV and text files every time it runs!

### Files That Auto-Update

Every scrape automatically creates/updates:

1. **jobs.csv** - Spreadsheet format (Excel, Google Sheets, Numbers)
2. **jobs_titles.txt** - Simple text list of all jobs
3. **jobs.json** - Complete database with all fields

### When Updates Happen

- ⏰ **9:00 AM daily** - Automatic scrape via scheduler
- ⏰ **6:00 PM daily** - Automatic scrape via scheduler
- 🔄 **Anytime you run:** `python3 scraper.py`

### Notifications

You'll get a macOS notification when new jobs are found! 🔔

---

## 📊 How to View Updated CSV

### Method 1: Auto-Viewer (Recommended)

**Live updates in terminal:**

```bash
python3 auto_view_csv.py
```

**What it does:**
- Shows jobs in a nice table
- Automatically refreshes when CSV updates
- Alerts with a beep
- Shows latest 15 entries
- Just leave it running!

**Perfect for:** Keeping a terminal window open to monitor new jobs

---

### Method 2: Spreadsheet App

**Open in Excel/Numbers:**

```bash
open jobs.csv
```

**Refresh the file:**
- Close and reopen jobs.csv to see updates
- Or use your spreadsheet app's "Refresh" feature

**Perfect for:** Sorting, filtering, and analyzing jobs

---

### Method 3: Quick Terminal View

**See the full CSV:**

```bash
cat jobs.csv
```

**Nicely formatted:**

```bash
cat jobs.csv | column -t -s ','
```

**With paging:**

```bash
cat jobs.csv | column -t -s ',' | less
```

**Perfect for:** Quick checks without opening apps

---

## 🔔 Notification System

When new jobs are found:

1. **macOS notification appears** with count of new jobs
2. **Files are auto-updated**:
   - jobs.csv
   - jobs_titles.txt
   - jobs.json

3. **Auto-viewer refreshes** (if running)

---

## 🚀 Complete Workflow

### Daily Use (Hands-Off)

1. **Morning (9 AM):**
   - Scraper runs automatically
   - CSV updates automatically
   - You get a notification if new jobs found

2. **Evening (6 PM):**
   - Same as above

3. **Check jobs:**
   ```bash
   open jobs.csv
   # or
   python3 view_new_jobs.py
   ```

### Active Monitoring

**Terminal 1 - Auto-Viewer:**
```bash
python3 auto_view_csv.py
```

**Terminal 2 - Manual runs:**
```bash
# Run scraper manually anytime
python3 scraper.py

# Terminal 1 will auto-update!
```

---

## 📁 File Formats Explained

### jobs.csv
```
Company,Title,Location,Department,Type,URL,Date Posted,Scraped At
Photoroom,Senior Engineer,Paris | Remote,R&D,FullTime,https://...,2025-11-18,2025-11-18T17:38:04
```

**Best for:** Excel, Google Sheets, data analysis

### jobs_titles.txt
```
Photoroom (13 jobs)
----------------------------------------------------------------------
1. Account Executive (EMEA) | Relocation to Europe
2. Business Development Rep | London | Remote
...
```

**Best for:** Quick reading, sharing via email/chat

### jobs.json
```json
{
  "title": "Senior Engineer",
  "company": "Photoroom",
  "location": "Paris | Remote",
  "url": "https://...",
  "department": "R&D",
  ...
}
```

**Best for:** Complete data, programming, custom scripts

---

## 🎯 Common Tasks

### See what's new today
```bash
python3 view_new_jobs.py
```

### Browse all jobs nicely
```bash
python3 view_jobs.py
```

### Watch for updates live
```bash
python3 auto_view_csv.py
```

### Open in spreadsheet
```bash
open jobs.csv
```

### Check scraper logs
```bash
tail -f logs/scraper.log
```

---

## ⚙️ Configuration

### Change notification settings

Edit the `run()` method in `scraper.py` to customize notifications.

### Change export formats

All formats are auto-generated. To disable one, comment out the relevant section in `scraper.py`.

### View only specific companies

Open `jobs.csv` in Excel/Sheets and use filtering.

---

## 💡 Pro Tips

1. **Keep auto-viewer running** in a dedicated terminal window
2. **Pin jobs.csv** to Finder sidebar for quick access
3. **Use spreadsheet filters** to find remote jobs, specific roles, etc.
4. **Check view_new_jobs.py daily** to see only new additions
5. **Export custom reports** from jobs.csv using pivot tables

---

## 🔍 Troubleshooting

### CSV not updating?

```bash
# Check if scraper is running
launchctl list | grep dailyscraper

# Check logs
tail logs/scraper.log

# Run manually to test
python3 scraper.py
```

### Auto-viewer not refreshing?

- Make sure CSV file path is correct
- Try restarting the viewer
- Check if scraper actually found new jobs

### No notifications?

- macOS may need notification permissions
- Check System Settings > Notifications

---

## 📊 Current Status

Check current files:
```bash
ls -lh jobs.csv jobs_titles.txt jobs.json
```

Count jobs:
```bash
echo "Total jobs: $(($(wc -l < jobs.csv) - 1))"
```

Last update:
```bash
stat -f "%Sm" jobs.csv
```

---

## Need Help?

Run these commands for quick help:

```bash
python3 scraper.py --help          # Scraper help
python3 view_new_jobs.py           # See new jobs
python3 view_jobs.py               # See all jobs
cat QUICKSTART.md                  # Quick reference
```

Happy job hunting! 🎯
