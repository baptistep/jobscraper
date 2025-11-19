#!/usr/bin/env python3
"""
Interactive script to help users add new job boards to their config
"""

import json
import os


def load_config():
    """Load current config"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Run setup.sh first.")
        exit(1)


def save_config(config):
    """Save config to file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_input(prompt, default=''):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def select_board_type():
    """Let user select board type"""
    print("\nSelect job board type:")
    print("1. Generic (custom CSS selectors)")
    print("2. Greenhouse")
    print("3. Lever")
    print("4. Ashby")
    print("5. Next.js (embedded JSON)")
    print("6. API")

    choice = input("Enter choice (1-6): ").strip()

    type_map = {
        '1': 'generic',
        '2': 'greenhouse',
        '3': 'lever',
        '4': 'ashby',
        '5': 'nextjs',
        '6': 'api'
    }

    return type_map.get(choice, 'generic')


def add_generic_board():
    """Add a generic job board with custom selectors"""
    print("\n=== Adding Generic Job Board ===")
    print("You'll need to inspect the website to find the CSS selectors.\n")

    board = {
        'name': get_input("Board name (e.g., 'Acme Corp Careers')"),
        'url': get_input("URL"),
        'type': 'generic',
        'enabled': True,
        'selectors': {}
    }

    print("\nCSS Selectors (press Enter to skip optional fields):")
    board['selectors']['job_container'] = get_input("Job container selector", "div.job")
    board['selectors']['title'] = get_input("Title selector", "h2")
    board['selectors']['location'] = get_input("Location selector (optional)", "")
    board['selectors']['description'] = get_input("Description selector (optional)", "")
    board['selectors']['link'] = get_input("Link selector", "a")
    board['selectors']['date_posted'] = get_input("Date posted selector (optional)", "")

    # Remove empty selectors
    board['selectors'] = {k: v for k, v in board['selectors'].items() if v}

    return board


def add_greenhouse_board():
    """Add a Greenhouse job board"""
    print("\n=== Adding Greenhouse Job Board ===")

    board = {
        'name': get_input("Board name"),
        'url': get_input("Greenhouse URL (e.g., https://boards.greenhouse.io/company)"),
        'type': 'greenhouse',
        'enabled': True
    }

    return board


def add_lever_board():
    """Add a Lever job board"""
    print("\n=== Adding Lever Job Board ===")

    board = {
        'name': get_input("Board name"),
        'url': get_input("Lever URL (e.g., https://jobs.lever.co/company)"),
        'type': 'lever',
        'enabled': True
    }

    return board


def add_ashby_board():
    """Add an Ashby job board"""
    print("\n=== Adding Ashby Job Board ===")

    board = {
        'name': get_input("Board name"),
        'url': get_input("Ashby URL (e.g., https://jobs.ashbyhq.com/company)"),
        'type': 'ashby',
        'enabled': True
    }

    return board


def add_nextjs_board():
    """Add a Next.js job board"""
    print("\n=== Adding Next.js Job Board ===")

    board = {
        'name': get_input("Board name"),
        'url': get_input("Next.js site URL"),
        'type': 'nextjs',
        'enabled': True
    }

    return board


def add_api_board():
    """Add an API-based job board"""
    print("\n=== Adding API Job Board ===")

    board = {
        'name': get_input("Board name"),
        'url': get_input("API URL"),
        'type': 'api',
        'enabled': True
    }

    add_headers = input("\nDoes this API require headers? (y/n): ").lower() == 'y'

    if add_headers:
        board['headers'] = {}
        print("\nEnter headers (press Enter with empty key to finish):")

        while True:
            key = input("Header key (e.g., 'Authorization'): ").strip()
            if not key:
                break
            value = input(f"Value for {key}: ").strip()
            board['headers'][key] = value

    return board


def main():
    """Main function"""
    print("=" * 50)
    print("Add Job Board to Config")
    print("=" * 50)

    config = load_config()

    board_type = select_board_type()

    if board_type == 'generic':
        new_board = add_generic_board()
    elif board_type == 'greenhouse':
        new_board = add_greenhouse_board()
    elif board_type == 'lever':
        new_board = add_lever_board()
    elif board_type == 'ashby':
        new_board = add_ashby_board()
    elif board_type == 'nextjs':
        new_board = add_nextjs_board()
    elif board_type == 'api':
        new_board = add_api_board()

    # Add to config
    config['job_boards'].append(new_board)

    # Save config
    save_config(config)

    print("\n✓ Job board added successfully!")
    print(f"\nBoard '{new_board['name']}' has been added and enabled.")
    print("Run 'python3 scraper.py' to test it.")

    # Ask if they want to add another
    another = input("\nAdd another board? (y/n): ").lower()
    if another == 'y':
        main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        exit(0)
