<div align="center">

🤖 Telegram Bridge bot
A simple, powerful Python bot to execute shell commands on your server directly from Telegram.

</div>

This is a Python-based Telegram bot that allows you to execute shell commands on a server, making it easier to deploy web applications directly from Telegram.

🚨 Extremely Important Security Warning
Warning
This bot can provide full terminal access to your server. If misused or if it falls into the wrong hands, your server could be completely compromised. Use this at your own risk.

🔒 Keep Your Bot Token Secure: Do not share your TELEGRAM_BOT_TOKEN with anyone.

👤 User ID Whitelisting: The bot will only listen to commands sent from the ALLOWED_USER_ID. This is a basic but crucial security measure.

🛡️ Server Security: Ensure that your server is also protected by other security measures like firewalls and regular updates.

✨ Features
/start: Initializes the bot and displays the security warning.

Direct Command Execution: Any text message is executed as a shell command.

Persistent Working Directory: All commands are executed within a predefined PROJECT_DIRECTORY, and you can navigate using cd.

Real-time Output: Get the standard output and error of your commands sent back to you on Telegram.

Long Output Handling: Outputs longer than 4096 characters are automatically split into multiple messages.

🚀 Getting Started
Follow these instructions to get your bot up and running on your server.

Prerequisites
Python 3.8+

pip (Python package installer)

A Telegram Account

A server (Linux, macOS, or Windows) where you want to run the bot.

Installation & Configuration
Get a Bot Token from BotFather

Open Telegram and talk to @BotFather.

Use the /newbot command and follow the instructions.

BotFather will give you an HTTP API token. Copy it and keep it safe.

Get Your Telegram User ID

Talk to @userinfobot on Telegram.

Send the /start command.

The bot will reply with your User ID.

Clone & Install Dependencies

Download or clone the bot.py file to your server.

Install the required Python library:

Bash

pip install python-telegram-bot
Configure the Bot

Open the bot.py file and fill in your details in the configuration section:

Python

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN' # BotFather se mila token
ALLOWED_USER_ID = 123456789                  # @userinfobot se mila ID
PROJECT_DIRECTORY = '/var/www/my-project'      # Aapka project folder
Run the Bot

Execute the script from your server's terminal:

Bash

python bot.py
To keep the bot running 24/7, use a process manager like systemd or run it inside a screen or tmux session.

💻 How to Use
Open your bot in Telegram.

Type /start to begin.

Send any shell command you want to execute. For example:

Bash

# Check files in the current directory
ls -l

# Pull the latest changes from your Git repository
git pull origin main

# Rebuild and restart your Docker containers
docker-compose up -d --build

# Install dependencies and build your frontend project
npm install && npm run build
The bot will execute the command in the specified PROJECT_DIRECTORY and send the output back to you. Happy deploying!
