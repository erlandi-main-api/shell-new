#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shlex
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import config

LOG_FILE = "bot.log"

TERM_ON = set()
PROMPT_MSG_ID = {}
CHAT_CWD = {}

def log_save(text):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}]\n{text}\n\n")

def is_owner(update):
    if config.OWNER_CHAT_ID == 0:
        return True
    return update.effective_chat and update.effective_chat.id == config.OWNER_CHAT_ID

def get_cwd(chat_id):
    if chat_id not in CHAT_CWD:
        CHAT_CWD[chat_id] = os.getcwd()
    return CHAT_CWD[chat_id]

def set_cwd(chat_id, path):
    CHAT_CWD[chat_id] = path

async def run_shell(cmd, cwd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        res = await asyncio.wait_for(proc.communicate(), timeout=config.CMD_TIMEOUT)
        stdout, stderr = res[0], res[1]
    except asyncio.TimeoutError:
        proc.kill()
        return 124, "TIMEOUT"

    rc = proc.returncode or 0
    output = (stdout or b"") + (b"\n" if stdout and stderr else b"") + (stderr or b"")
    text = output.decode("utf-8", errors="replace").strip()

    if len(text) > 3500:
        text = text[:3500] + "\n...[dipotong]..."

    return rc, text

async def handle_cmd(chat_id, raw):
    raw = raw.strip()
    cwd = get_cwd(chat_id)

    if raw.startswith("cd"):
        parts = shlex.split(raw)
        target = parts[1] if len(parts) > 1 else "~"
        target = os.path.expanduser(target)
        new_path = os.path.normpath(os.path.join(cwd, target))
        if os.path.isdir(new_path):
            set_cwd(chat_id, new_path)
            return 0, new_path, "(cd ok)"
        return 1, cwd, "cd: directory tidak ditemukan"

    if raw == "pwd":
        return 0, cwd, cwd

    rc, out = await run_shell(raw, cwd)
    return rc, cwd, out

def fmt(cwd, cmd, rc, out):
    return f"[DIR] {cwd}\n[CMD] {cmd}\n[RC]  {rc}\n\n[OUT]\n{out}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Shell Bot Aktif.\n"
        "/term on  -> mode reply (seperti foto)\n"
        "/term off -> matikan mode\n"
        "/r <cmd>  -> jalankan command langsung\n"
        "/id       -> chat_id\n"
        "Contoh reply: ls, cd .., pwd, df -h"
    )

async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"chat_id: {update.effective_chat.id}")

async def term(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("Tidak diizinkan.")
        return

    chat_id = update.effective_chat.id
    arg = context.args[0].lower() if context.args else ""

    if arg == "on":
        TERM_ON.add(chat_id)
        prompt = await update.message.reply_text("Terminal mode ON. Reply pesan ini untuk command.")
        PROMPT_MSG_ID[chat_id] = prompt.message_id
        get_cwd(chat_id)
        return

    if arg == "off":
        TERM_ON.discard(chat_id)
        PROMPT_MSG_ID.pop(chat_id, None)
        await update.message.reply_text("Terminal mode OFF.")
        return

    await update.message.reply_text("Gunakan: /term on atau /term off")

async def r(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    if not context.args:
        await update.message.reply_text("Gunakan: /r <command>")
        return

    chat_id = update.effective_chat.id
    cmd = " ".join(context.args)
    rc, cwd, out = await handle_cmd(chat_id, cmd)
    msg = fmt(cwd, cmd, rc, out)
    await update.message.reply_text(msg)
    log_save(msg)

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    chat_id = update.effective_chat.id
    if chat_id not in TERM_ON:
        return

    m = update.message
    if not m or not m.text or not m.reply_to_message:
        return

    if PROMPT_MSG_ID.get(chat_id) != m.reply_to_message.message_id:
        return

    cmd = m.text.strip()
    rc, cwd, out = await handle_cmd(chat_id, cmd)
    msg = fmt(cwd, cmd, rc, out)
    await m.reply_text(msg)
    log_save(msg)

def main():
    if not config.BOT_TOKEN:
        raise SystemExit("BOT_TOKEN kosong. Jalankan: python3 set.py")

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(CommandHandler("term", term))
    app.add_handler(CommandHandler("r", r))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.run_polling()

if __name__ == "__main__":
    main()
