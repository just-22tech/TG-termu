Telegram Web App Deployment Bot
This is a Python-based Telegram bot that allows you to execute shell commands on a server, making it easier to deploy web applications.

🚨🚨🚨 Extremely Important Security Warning 🚨🚨🚨
This bot can provide full terminal access to your server. If misused or if it falls into the wrong hands, your server could be completely compromised. Use this at your own risk.

Keep Your Bot Token Secure: Do not share your TELEGRAM_BOT_TOKEN with anyone.

User ID Whitelisting: The bot will only listen to commands sent from the ALLOWED_USER_ID. This is a basic security measure.

Server Security: Ensure that your server is also protected by other security measures.

Features
/start: Starts the bot and displays the security warning.

Direct Command Execution: Any text message sent (other than /start) is executed as a shell command.

Working Directory: All commands are executed in a predefined PROJECT_DIRECTORY.

Output/Error Reporting: The standard output and standard error of the command are sent back to you on Telegram.

Long Output Handling: Long outputs are split into 4096-character chunks before being sent.

How to Setup
1. Prerequisites
Python 3.8+

pip (Python package installer)

A Telegram account

A server where you want to run this bot.

2. Obtain a Bot Token
Talk to BotFather on Telegram.

Use the /newbot command to create a new bot.

Follow its instructions. BotFather will give you an HTTP API token. Keep this token safe.

3. Get Your Telegram User ID
Talk to @userinfobot on Telegram.

Send the /start command.

The bot will reply with your User ID.

4. Installation and Configuration
Clone this repository or download the bot.py file to your server.

Install the required Python library:

Bash

pip install python-telegram-bot
Edit the bot.py file and fill in the following variables with your information:

TELEGRAM_BOT_TOKEN: Enter your token obtained from BotFather here.

ALLOWED_USER_ID: Enter your User ID obtained from @userinfobot here.

PROJECT_DIRECTORY: The path of the directory where you want to execute commands (e.g., /var/www/my-project).

5. Run the Bot
In your server's terminal, run the following command:

Bash

python bot.py
Your bot is now online. To keep it running permanently, use a tool like a systemd service or screen/tmux.

How to Use
Open your bot in your Telegram client.

Type /start to begin.

Now, send any shell command, such as:

ls -l

git pull origin main

docker-compose up -d --build

npm install && npm run build

The bot will execute the command in the PROJECT_DIRECTORY and send the output back to you.
