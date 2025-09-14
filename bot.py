# -*- coding: utf-8 -*-

import os
import subprocess
import html
import asyncio
import time
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
# WARNING: Kripya apne real values yahan daalein.
# Apna bot token yahan daalein jo aapko BotFather se mila hai.
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
# Sirf is User ID se bheje gaye commands hi execute honge. Apna Telegram User ID yahan daalein.
# Aap @userinfobot se apna ID prapt kar sakte hain.
ALLOWED_USER_ID = 123456789
# Woh directory jahan se bot shuru hoga.
# Windows ke liye path is tarah ka hoga: '/path'
PROJECT_DIRECTORY = ''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start command ke liye handler. User ko welcome karta hai aur suraksha chetavni deta hai."""
    # Suraksha jaanch: Kya yeh authorized user hai?
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Access Denied! Aap is bot ko istemal karne ke liye authorized nahi hain.")
        return

    # Welcome sandesh
    welcome_message = f"""
Yeh bot aapko is machine par terminal commands chalane ki anumati deta hai.
- Sirf authorized users (aap) iska upyog kar sakte hain.
- Apna Bot Token kisi ke saath share na karein.
- Savdhani se commands ka upyog karein.

Aap `cd <directory>` ka upyog karke directory badal sakte hain.
Shuru karne ke liye, main '{context.bot_data.get('cwd', PROJECT_DIRECTORY)}' directory mein hoon.
"""
    await update.message.reply_text(welcome_message)


async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shell commands ko handle karne wala function, live updates aur persistent directory ke saath."""
    # Suraksha jaanch: Sirf allowed user hi command chala sakta hai.
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Access Denied! Aap is bot ko istemal karne ke liye authorized nahi hain.")
        return

    command = update.message.text
    current_dir = context.bot_data.get('cwd', PROJECT_DIRECTORY)

    # --- 1. 'cd' command ko alag se handle karein ---
    if command.strip().startswith('cd'):
        parts = command.strip().split(maxsplit=1)
        target_path = ""
        if len(parts) > 1:
            target_path = parts[1]
        
        if not target_path:
            # Agar sirf 'cd' hai, toh project directory par reset karein
            new_path = os.path.abspath(PROJECT_DIRECTORY)
        else:
            # Anyatha, naye path par jaane ki koshish karein
            new_path = os.path.abspath(os.path.join(current_dir, target_path))

        if os.path.isdir(new_path):
            context.bot_data['cwd'] = new_path
            escaped_path = new_path.replace("\\", "\\\\").replace("`", "\\`")
            await update.message.reply_text(f"Working directory badal kar yahan ho gayi hai:\n`{escaped_path}`", parse_mode=constants.ParseMode.MARKDOWN_V2)
        else:
            escaped_path = target_path.replace("`", "\\`")
            await update.message.reply_text(f"❌ Error: Directory nahi mili: `{escaped_path}`", parse_mode=constants.ParseMode.MARKDOWN_V2)
        return

    # --- 2. Dusre commands ko bina live updates ke chalayein ---
    msg = await update.message.reply_text(
        f"🚀 Running command...\n<pre>{html.escape(command)}</pre>\n\n"
        f"⏳ Command poora hone par result bhejunga.",
        parse_mode=constants.ParseMode.HTML
    )
    
    start_time = time.monotonic()

    # stderr ko stdout par redirect karein (2>&1) taaki dono streams live update hon.
    process = await asyncio.create_subprocess_shell(
        f"{command} 2>&1",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, # stderr ko bhi capture karein
        cwd=current_dir
    )
    
    # Command ke poora hone ka intezaar karein aur poora output prapt karein.
    stdout, stderr = await process.communicate()
    end_time = time.monotonic()
    duration = end_time - start_time
    return_code = process.returncode

    # Output ko decode karein.
    full_output = stdout.decode('utf-8', errors='replace')
    if stderr: # Agar stderr mein kuch hai, toh use bhi jod dein.
        full_output += stderr.decode('utf-8', errors='replace')

    # Naya logic: Agar command 5 second se kam samay mein poora hota hai, toh poora output dikhayein.
    if duration <= 5:
        header_message = f"Command {duration:.2f} seconds mein poora hua. Yahan poora output hai:\n\n"
        truncated_output = full_output.strip()
    else:
        # Anyatha, aakhiri 40 lines dikhayein.
        header_message = f"Command {duration:.2f} seconds tak chala. Yahan aakhiri 40 lines hain:\n\n"
        output_lines = full_output.strip().split('\n')
        last_40_lines = output_lines[-40:]
        truncated_output = '\n'.join(last_40_lines)

    # Final sandesh banayein.
    final_text = (
        f"{header_message}"
        f"{truncated_output}\n\n"
        f"---\n✅ Process finished with exit code {return_code}"
    )

    try:
        # Sandesh ko edit karke final output dikhayein.
        display_text = f"<pre>{html.escape(final_text[-4000:])}</pre>"
        await msg.edit_text(display_text, parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        if "not modified" not in str(e):
            print(f"Final update error: {e}")


def main() -> None:
    """Bot ko start karta hai."""
    # Yakeen karein ki project directory maujood hai.
    if not os.path.isdir(PROJECT_DIRECTORY):
        print(f"Error: Project directory '{PROJECT_DIRECTORY}' nahi mili. Kripya `bot.py` mein path theek karein.")
        return

    # Application banayein.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Bot ke data mein current working directory (cwd) set karein.
    application.bot_data['cwd'] = os.path.abspath(PROJECT_DIRECTORY)

    # Handlers add karein.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_command))

    # Bot ko start karein.
    print("Bot start ho gaya hai... (Press Ctrl C to stop)")
    application.run_polling()


if __name__ == '__main__':
    main()

