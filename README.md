# AchieveItTogether Bot

**AchieveItTogether** is a powerful, interactive Discord bot designed to help communities and individuals track their goals, reach milestones, and stay consistent with customizable reminders. 

Whether your server is tracking daily steps, reading books, or learning new skills, this bot seamlessly integrates into your chat to keep everyone motivated.

## Key Features

* **Lightning-Fast Progress Tracking**: Log your progress via slash commands (`/add`) or naturally in the chat using quick text commands (e.g., `$steps 5000` or `$books 1 @User`).
* **Milestones**: Automatically detects and celebrates when users reach predefined milestones.
* **Smart Reminders (UI)**: Features an intuitive, interactive UI (Dropdowns & Modals) for setting up recurring DM reminders for specific days of the week.
* **Multi-language Support (i18n)**: Fully supports English and partially Polish out of the box. The bot automatically detects the user's Discord app language for slash commands!
* **Highly Optimized**: Uses a fast in-memory Lazy Loading Cache (`services/cache.py`) to minimize database queries while reading chat messages.
* **Deployment Flexibility**: Easily deployable via Docker or natively on low-end servers (like Alpine Linux LXC containers with low RAM).

## Tech Stack

* **Language**: Python 3.14
* **Framework**: [Discord.py](https://github.com/Rapptz/discord.py)
* **Database**: SQLite with SQLAlchemy (Async via `aiosqlite`)
* **Deployment**: Docker & Docker Compose or Bare Metal

## Commands Overview

### Slash Commands
* `/create <name>` - Create a new goal on the server (locks it to the current channel).
* `/add <goal> <amount> [@user]` - Add progress to a specific goal.
* `/notify <goal>` - Opens an interactive menu to set up DM reminders for a goal.
* `/milestone <goal>` - Adds a milestone to a goal using a form.
* `/lock_channel` - Locks a goal to the current channel.
* `/unlock_channel` - Unlock a goal (make it available in all channels).
* `/help` - Displays the help menu with a list of currently active goals.

### Quick Chat Command
Typing directly in the chat is the fastest way to log progress!
* `$<goal> <amount> [@user]` - Logs progress for yourself (e.g., `$pushups 50`) or someone else.

## Installation & Setup

The recommended way to run the bot is via Docker.

### 1. Clone the repository
```bash
git clone https://github.com/Donkrzawayan/AchieveItTogether.git
cd AchieveItTogether
```

### 2. Configure Environment Variables
Create a .env file in the root directory.
```ini
# Discord Configuration
DISCORD_TOKEN=discord_bot_token
ALLOWED_ROLE_ID=123456789012345678 # ID of the role allowed to manage locking goals to channels
```

### 3a. Method 1: Docker (Recommended)
The easiest way to run the bot.
```bash
docker-compose up -d --build
```

### 3b. Method 2: Bare Metal / Alpine Linux (Low RAM)
Perfect for extremely low-budget VPS or LXC containers (e.g., 256MB RAM).

```sh
# Install system dependencies:
apk update
apk add python3 py3-pip git tmux sqlite
# Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate
# Install Python packages:
pip install --no-cache-dir -r requirements.txt
# Run the bot in the background (using tmux):
tmux new-session -d -s bot_session 'python main.py'
```
(To view the logs later, use `tmux attach -t bot_session`. To detach, press `Ctrl+B, D`.)

## Backups (`Backup-Db.ps1`)

Because the bot uses SQLite, the database is stored in a single file (`achievebot.db`).  
To perform safe remote backups use the included PowerShell script (`Backup-Db.ps1`) from local Windows machine.
