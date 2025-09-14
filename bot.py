# -*- coding: utf-8 -*-

import os
import subprocess
import html
import asyncio
import time
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
# WARNING: Please enter your actual values here.
# Enter your bot token here, which you received from BotFather.
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
# Only commands sent from this User ID will be executed. Enter your Telegram User ID here.
# You can get your ID from @userinfobot.
ALLOWED_USER_ID = 123456789
# The directory where the bot will start.
# For Windows, the path should look like this: 'C:/path/to/project'
# For Linux/macOS, the path will look like this: '/path/to/project'
PROJECT_DIRECTORY = 'C:/path/to/project'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /start command. Welcomes the user and gives a security warning."""
    # Security check: Is this the authorized user?
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Access Denied! You are not authorized to use this bot.")
        return

    # Welcome message
    welcome_message = f"""
This bot allows you to run terminal commands on this machine.
- Only authorized users (you) can use it.
- Do not share your Bot Token with anyone.
- Use commands with caution.

You can change the directory using `cd <directory>`.
To start, I am in the '{context.bot_data.get('cwd', PROJECT_DIRECTORY)}' directory.
"""
    await update.message.reply_text(welcome_message)


async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Function to handle shell commands with live updates and a persistent directory."""
    # Security check: Only the allowed user can run commands.
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Access Denied! You are not authorized to use this bot.")
        return

    command = update.message.text
    current_dir = context.bot_data.get('cwd', PROJECT_DIRECTORY)

    # --- 1. Handle the 'cd' command separately ---
    if command.strip().startswith('cd'):
        parts = command.strip().split(maxsplit=1)
        target_path = ""
        if len(parts) > 1:
            target_path = parts[1]
        
        if not target_path:
            # If it's just 'cd', reset to the project directory
            new_path = os.path.abspath(PROJECT_DIRECTORY)
        else:
            # Otherwise, try to navigate to the new path
            new_path = os.path.abspath(os.path.join(current_dir, target_path))

        if os.path.isdir(new_path):
            context.bot_data['cwd'] = new_path
            # Escape the path for MarkdownV2
            escaped_path = new_path.replace("\\", "\\\\").replace("`", "\\`")
            await update.message.reply_text(f"Working directory changed to:\n`{escaped_path}`", parse_mode=constants.ParseMode.MARKDOWN_V2)
        else:
            escaped_path = target_path.replace("`", "\\`")
            await update.message.reply_text(f"❌ Error: Directory not found: `{escaped_path}`", parse_mode=constants.ParseMode.MARKDOWN_V2)
        return

    # --- 2. Run other commands without live updates ---
    msg = await update.message.reply_text(
        f"🚀 Running command...\n<pre>{html.escape(command)}</pre>\n\n"
        f"⏳ I will send the result when the command completes.",
        parse_mode=constants.ParseMode.HTML
    )
    
    start_time = time.monotonic()

    # Redirect stderr to stdout (2>&1) to capture both streams.
    process = await asyncio.create_subprocess_shell(
        f"{command} 2>&1",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, # Also capture stderr
        cwd=current_dir
    )
    
    # Wait for the command to complete and get the full output.
    stdout, stderr = await process.communicate()
    end_time = time.monotonic()
    duration = end_time - start_time
    return_code = process.returncode

    # Decode the output.
    full_output = stdout.decode('utf-8', errors='replace')
    if stderr: # If there's anything in stderr, append it.
        full_output += stderr.decode('utf-8', errors='replace')

    # New logic: If the command completes in less than 5 seconds, show the full output.
    if duration <= 5:
        header_message = f"Command completed in {duration:.2f} seconds. Here is the full output:\n\n"
        truncated_output = full_output.strip()
    else:
        # Otherwise, show the last 40 lines.
        header_message = f"Command ran for {duration:.2f} seconds. Here are the last 40 lines:\n\n"
        output_lines = full_output.strip().split('\n')
        last_40_lines = output_lines[-40:]
        truncated_output = '\n'.join(last_40_lines)

    # Create the final message.
    final_text = (
        f"{header_message}"
        f"{truncated_output}\n\n"
        f"---\n✅ Process finished with exit code {return_code}"
    )

    try:
        # Edit the message to show the final output.
        # Trim to the last 4000 characters to stay within Telegram's limit.
        display_text = f"<pre>{html.escape(final_text[-4000:])}</pre>"
        await msg.edit_text(display_text, parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        # Ignore "message is not modified" errors, which are common.
        if "not modified" not in str(e):
            print(f"Final update error: {e}")


def main() -> None:
    """Starts the bot."""
    # Ensure the project directory exists.
    if not os.path.isdir(PROJECT_DIRECTORY):
        print(f"Error: Project directory '{PROJECT_DIRECTORY}' not found. Please correct the path in `bot.py`.")
        return

    # Create the Application.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Set the current working directory (cwd) in the bot's data.
    application.bot_data['cwd'] = os.path.abspath(PROJECT_DIRECTORY)

    # Add handlers.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_command))

    # Start the bot.
    print("Bot has started... (Press Ctrl+C to stop)")
    application.run_polling()


if __name__ == '__main__':
    main()
