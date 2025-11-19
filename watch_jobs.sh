#!/bin/bash

# Auto-watch for job updates and display CSV
# This script watches for changes to jobs.csv and automatically displays it

CSV_FILE="jobs.csv"
LAST_MODIFIED=""

echo "=========================================="
echo "Job Scraper Auto-Viewer"
echo "=========================================="
echo ""
echo "Watching for updates to jobs.csv..."
echo "Press Ctrl+C to stop"
echo ""

# Function to display CSV nicely
display_csv() {
    clear
    echo "=========================================="
    echo "JOBS DATABASE - Updated $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo ""

    # Count jobs
    TOTAL=$(tail -n +2 "$CSV_FILE" | wc -l | xargs)
    echo "Total Jobs: $TOTAL"
    echo ""

    # Display with column formatting
    echo "Latest entries:"
    echo "------------------------------------------"
    head -1 "$CSV_FILE"
    echo "------------------------------------------"
    tail -20 "$CSV_FILE"
    echo ""
    echo "=========================================="
    echo "Watching for updates... (Ctrl+C to stop)"
    echo "Full CSV: $CSV_FILE"
    echo "=========================================="
}

# Initial display
if [ -f "$CSV_FILE" ]; then
    display_csv
else
    echo "No jobs.csv found yet. Waiting for first scrape..."
fi

# Watch for changes
while true; do
    if [ -f "$CSV_FILE" ]; then
        CURRENT_MODIFIED=$(stat -f "%m" "$CSV_FILE" 2>/dev/null || stat -c "%Y" "$CSV_FILE" 2>/dev/null)

        if [ "$CURRENT_MODIFIED" != "$LAST_MODIFIED" ]; then
            LAST_MODIFIED="$CURRENT_MODIFIED"
            if [ -n "$LAST_MODIFIED" ]; then
                display_csv
                # Optional: play sound
                # afplay /System/Library/Sounds/Glass.aiff
            fi
        fi
    fi
    sleep 5
done
