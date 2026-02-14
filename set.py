#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.py")

TEMPLATE = """# -*- coding: utf-8 -*-

BOT_TOKEN = {token!r}
OWNER_CHAT_ID = {owner}
CMD_TIMEOUT = {timeout}
"""

def main():
    print("=== SETUP CONFIG BOT ===\n")

    token = input("Masukkan BOT TOKEN: ").strip()
    owner = input("Masukkan OWNER CHAT ID: ").strip()
    timeout = input("Masukkan TIMEOUT (detik) [20]: ").strip()

    if not timeout:
        timeout = "20"

    CONFIG_PATH.write_text(
        TEMPLATE.format(
            token=token,
            owner=int(owner),
            timeout=int(timeout)
        ),
        encoding="utf-8"
    )

    os.chmod(CONFIG_PATH, 0o600)

    print("\nOK: config.py berhasil diupdate!")
    print("Jalankan bot: python3 shell.py")

if __name__ == "__main__":
    main()
