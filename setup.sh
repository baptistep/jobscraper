#!/bin/bash

# Job Board Scraper Setup Script
# This script helps you set up the job board scraper

set -e

echo "================================================"
echo "Job Board Scraper Setup"
echo "================================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed."
    echo "Please install pip3 first."
    exit 1
fi

echo "✓ pip3 found"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "✓ Dependencies installed"
echo ""

# Check if config.json exists, if not create from example
if [ ! -f "config.json" ]; then
    echo "Creating config.json from example..."
    cp config.example.json config.json
    echo "✓ config.json created"
    echo ""
    echo "⚠️  Please edit config.json to:"
    echo "   1. Add your job board URLs"
    echo "   2. Set 'enabled: true' for boards you want to scrape"
    echo "   3. Customize selectors for generic boards"
else
    echo "✓ config.json already exists"
fi

echo ""

# Create logs directory if it doesn't exist
mkdir -p logs
echo "✓ Logs directory ready"

echo ""

# Test run
echo "Running a test scrape..."
python3 scraper.py

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit config.json to add your job boards:"
echo "   nano config.json"
echo ""
echo "2. Test the scraper manually:"
echo "   python3 scraper.py"
echo ""
echo "3. Set up automatic scheduling:"
echo "   - On macOS: Copy plist file and load with launchctl"
echo "   - On Linux: Set up a cron job"
echo ""
echo "See README.md for detailed instructions."
echo ""
