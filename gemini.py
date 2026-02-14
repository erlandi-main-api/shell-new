# -*- coding: utf-8 -*-

import os
import time
import sqlite3
from dotenv import load_dotenv

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from google import genai

# =========================
# LOAD ENV
# =========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN belum diisi di file .env")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY belum diisi di file .env")

# =========================
# GEMINI CLIENT
# =========================
client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# AUTO DETECT MODEL
# =========================
PREFERRED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
]

def pick_available_model():
    try:
        models = [m.name for m in client.models.list()]

        for pref in PREFERRED_MODELS:
            for name in models:
                if name.endswith(pref):
                    return name

        return models[0]

    except Exception as e:
        print("MODEL LIST ERROR:", e)
        return "gemini-2.5-flash"


MODEL_NAME = pick_available_model()
print("Using model:", MODEL_NAME)

# =========================
# CONFIG
# =========================
SYSTEM_PROMPT = (
    "Kamu adalah asisten AI Telegram yang sopan, jelas, dan membantu. "
    "Jawaban singkat tapi informatif."
)

DB_FILE = "chat_history.db"
MAX_HISTORY = 6
RATE_LIMIT_SECONDS = 3

# =========================
# DATABASE SQLITE AUTO CREATE
# =========================
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    message TEXT
)
""")
conn.commit()

# =========================
# RATE LIMIT MEMORY
# =========================
last_request_time = {}

# =========================
# DATABASE FUNCTIONS
# =========================
def save_message(user_id, role, message):
    cursor.execute(
        "INSERT INTO history (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, role, message)
    )
    conn.commit()


def load_history(user_id):
    cursor.execute(
        "SELECT role, message FROM history "
        "WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, MAX_HISTORY)
    )
    rows = cursor.fetchall()
    rows.reverse()
    return rows


def reset_history(user_id):
    cursor.execute("DELETE FROM history WHERE user_id=?", (user_id,))
    conn.commit()

# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Saya bot Gemini AI (2026).\n\n"
        "Silakan ketik pertanyaan.\n"
        "Gunakan /reset untuk hapus konteks."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_history(update.effective_user.id)
    await update.message.reply_text("Konteks berhasil direset.")

# =========================
# CHAT HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    text = (update.message.text or "").strip()

    if not text:
        return

    # GROUP MODE (reply only if mentioned)
    if chat_type in ["group", "supergroup"]:
        bot_username = context.bot.username
        if bot_username and f"@{bot_username}" not in text:
            return
        if bot_username:
            text = text.replace(f"@{bot_username}", "").strip()

    # RATE LIMIT
    now = time.time()
    if user_id in last_request_time:
        if now - last_request_time[user_id] < RATE_LIMIT_SECONDS:
            await update.message.reply_text("Tunggu sebentar...")
            return

    last_request_time[user_id] = now

    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        # Load history
        history = load_history(user_id)

        # Build prompt
        prompt = SYSTEM_PROMPT + "\n\n"
        for role, msg in history:
            prompt += f"{role.upper()}: {msg}\n"

        prompt += f"USER: {text}\nAI:"

        # Call Gemini
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        reply = (resp.text or "").strip()
        if not reply:
            reply = "Tidak ada respons dari Gemini."

        # Save DB
        save_message(user_id, "user", text)
        save_message(user_id, "ai", reply)

        # Send reply
        for chunk in [reply[i:i+3500] for i in range(0, len(reply), 3500)]:
            await update.message.reply_text(chunk)

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        await update.message.reply_text(
            "Terjadi kesalahan saat memanggil Gemini. Cek log terminal."
        )

# =========================
# RUN BOT
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Telegram Gemini AI berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
