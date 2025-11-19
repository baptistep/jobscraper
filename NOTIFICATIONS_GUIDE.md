# Job Scraper Notifications Guide

## 📍 Where Notifications Appear

### On Your Screen

Notifications pop up in the **TOP-RIGHT corner** of your Mac screen.

```
┌─────────────────────────────────────────────────────────────┐
│                                         🔋 🔊 📶 🕐 Nov 18  │  ← Menu Bar
├─────────────────────────────────────────────────────────────┤
│                                                               │
│                        ┌───────────────────────────┐         │
│                        │ Job Scraper          [×]  │  ← Banner
│                        │ ───────────────────────── │
│                        │ Found 5 new job(s)!       │
│                        │ Total: 64                 │
│                        └───────────────────────────┘         │
│                                                               │
│   Your Desktop / Applications                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### In Notification Center

Click the **clock/date** in your menu bar (top-right) to see all notifications:

```
Click here ──────────┐
                     ▼
┌────────────────────────────────────────┐
│  🔋 🔊 📶 🕐 Mon Nov 18, 5:30 PM  ◀── │  ← Click this
└────────────────────────────────────────┘

Opens Notification Center:
┌─────────────────────────────────────┐
│  Notifications                      │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Job Scraper        5:30 PM  │   │
│  │ Found 5 new job(s)!         │   │
│  │ Total: 64                   │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Job Scraper        9:00 AM  │   │
│  │ Found 3 new job(s)!         │   │
│  │ Total: 59                   │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔔 When You'll Get Notified

### ✅ You WILL Get Notifications When:

- **Automatic scrapes find new jobs** (9 AM & 6 PM daily)
- **Manual scrapes find new jobs** (`python3 scraper.py`)
- **Any time new job postings are detected**

### ❌ You WON'T Get Notifications When:

- **No new jobs found** (0 new jobs)
- **Only re-scraping existing jobs**
- **Scraper encounters errors**

---

## 📱 Notification Examples

### Example 1: Few New Jobs
```
┌─────────────────────────────────┐
│ Job Scraper                     │
│ Found 3 new job(s)! Total: 62   │
└─────────────────────────────────┘
```

### Example 2: Many New Jobs
```
┌─────────────────────────────────┐
│ Job Scraper                     │
│ Found 15 new job(s)! Total: 74  │
└─────────────────────────────────┘
```

### Example 3: First Run (All Jobs New)
```
┌─────────────────────────────────┐
│ Job Scraper                     │
│ Found 59 new job(s)! Total: 59  │
└─────────────────────────────────┘
```

---

## ⚙️ Enable Notifications

If you're not seeing notifications, check your settings:

### macOS Ventura or later:

1. Open **System Settings**
2. Click **Notifications**
3. Scroll down to find one of these:
   - **Script Editor**
   - **Terminal**
   - **Python**
4. Toggle ON: **Allow Notifications**
5. Choose notification style: **Banners** or **Alerts**

### macOS Monterey or earlier:

1. Open **System Preferences**
2. Click **Notifications & Focus**
3. Select **Script Editor** or **Terminal**
4. Enable notifications

---

## 🧪 Test Your Notifications

### Quick Test (Right Now):

```bash
osascript -e 'display notification "Test notification from Job Scraper!" with title "Job Scraper Test"'
```

**Did you see it?**
- ✅ **YES** → Notifications working perfectly!
- ❌ **NO** → Check System Settings > Notifications

### Test With Real Scraper:

To see a real notification with new jobs:

```bash
# Backup current data
mv jobs.json jobs_backup.json

# Run scraper (all 59 jobs will be "new")
python3 scraper.py

# You'll get a notification!

# Restore backup if you want
mv jobs_backup.json jobs.json
```

---

## 🔍 View Past Notifications

### Method 1: Notification Center
1. Click the **date/time** in your menu bar
2. Scroll through to see past "Job Scraper" notifications

### Method 2: Trackpad Gesture
1. **Swipe left** with two fingers from the **right edge** of trackpad
2. Notification Center slides in

### Method 3: Check Logs
If you missed a notification, check the scraper logs:

```bash
tail -20 logs/scraper.log
```

Look for lines like:
```
New jobs found: 5
```

---

## 🎯 What Notifications Tell You

### The Message Format:

```
Found X new job(s)! Total: Y
```

- **X** = Number of NEW jobs just discovered
- **Y** = Total jobs in your database

### What To Do When You Get One:

1. **Check new jobs:**
   ```bash
   python3 view_new_jobs.py
   ```

2. **View updated CSV:**
   ```bash
   open jobs.csv
   ```

3. **Or use auto-viewer:**
   ```bash
   python3 auto_view_csv.py
   ```

---

## 🔧 Troubleshooting

### Not Getting Notifications?

**Check 1: System Settings**
```
System Settings > Notifications > Script Editor
Make sure "Allow Notifications" is ON
```

**Check 2: Do Not Disturb**
```
Make sure Do Not Disturb is OFF
Check menu bar for moon icon 🌙
```

**Check 3: Notification Style**
```
Set to "Banners" or "Alerts" (not "None")
```

**Check 4: Test Command**
```bash
osascript -e 'display notification "Test" with title "Test"'
```

### Still Not Working?

The scraper still works fine without notifications! You can:

1. **Check logs manually:**
   ```bash
   tail -f logs/scraper.log
   ```

2. **Use auto-viewer:**
   ```bash
   python3 auto_view_csv.py
   ```

3. **Just open files after scheduled runs:**
   - 9:00 AM - check `jobs.csv`
   - 6:00 PM - check `jobs.csv`

---

## 📅 Daily Workflow

### Morning (9:00 AM):
1. **Scraper runs automatically**
2. **Notification appears** (if new jobs found)
3. **Click notification** or run: `python3 view_new_jobs.py`

### Evening (6:00 PM):
1. **Same as above**

### Anytime:
- **Check Notification Center** for missed alerts
- **View logs:** `tail logs/scraper.log`
- **Open CSV:** `open jobs.csv`

---

## 💡 Pro Tips

1. **Keep Notification Center open** in a separate desktop space
2. **Enable "Show previews"** in notification settings for more detail
3. **Use auto-viewer** (`python3 auto_view_csv.py`) for live updates
4. **Check notifications in morning** after overnight scrapes
5. **Save important jobs immediately** - they might be gone later!

---

## Quick Reference

| Action | Command |
|--------|---------|
| Test notification | `osascript -e 'display notification "Test" with title "Job Scraper"'` |
| View new jobs | `python3 view_new_jobs.py` |
| Open CSV | `open jobs.csv` |
| Check logs | `tail -f logs/scraper.log` |
| System Settings | System Settings > Notifications |

---

Happy job hunting! 🎯
