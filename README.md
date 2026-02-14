# 🖥 Telegram Shell Bot (Reply Terminal Mode)

Telegram Shell Bot adalah bot sederhana yang memungkinkan kamu menjalankan command Linux langsung dari Telegram.

Bot ini mendukung dua mode utama:

- `/r <command>` → Jalankan command langsung
- `/term on` → Mode terminal interaktif via reply chat (seperti shell)

Semua output otomatis menampilkan:

- Directory aktif
- Command
- Exit Code
- Output command

Dan otomatis disimpan ke file log.

---

# ✨ Features

- Run Linux command from Telegram
- Reply-mode terminal (mirip SSH chat)
- Built-in `cd` dan `pwd`
- Directory state per chat
- Timeout protection
- Auto logging (`bot.log`)
- Setup config otomatis via `set.py`

---

# 📂 Project Structure

```
shell-new/
 ├── shell.py
 ├── config.py
 ├── set.py
 └── bot.log (auto created)
```

---

# ⚠ Security Warning

Bot ini memiliki akses penuh untuk menjalankan command di server.

Pastikan:

- OWNER_CHAT_ID sudah di-set
- Token bot tidak dibagikan
- Jangan gunakan di server publik tanpa proteksi tambahan

---

# 🔧 Requirements

- Linux VPS / Local Server
- Python 3.8+
- pip
- Telegram Bot Token dari @BotFather

---

# 📦 Installation (All Linux Distros)

## 1️⃣ Install Python & pip

### Ubuntu / Debian
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

### Arch Linux
```bash
sudo pacman -S python python-pip
```

### Fedora
```bash
sudo dnf install python3 python3-pip -y
```

---

## 2️⃣ Install Telegram Library

```bash
pip3 install --user python-telegram-bot
```

Jika pip error:
```bash
python3 -m pip install --user python-telegram-bot
```

---

## 3️⃣ Clone Repository

```bash
git clone https://github.com/erlandi-main-api/shell-new.git
cd shell-new
```

---

# ⚙ Configuration Setup

Jalankan:

```bash
python3 set.py
```

Masukkan:

- BOT TOKEN
- OWNER CHAT ID
- TIMEOUT (default 20 detik)

Config akan tersimpan di `config.py`.

---

# 🚀 Run Bot

```bash
python3 shell.py
```

Jika berhasil:

```
Bot running...
```

---

# 📌 Usage

## 1️⃣ Start Bot

Di Telegram:

```
/start
```

---

## 2️⃣ Jalankan Command Langsung

```
/r ls
```

Output contoh:

```
[DIR] /home/user
[CMD] ls
[RC]  0

[OUT]
shell.py
config.py
bot.log
```

---

## 3️⃣ Terminal Reply Mode (Seperti Shell Chat)

Aktifkan mode reply:

```
/term on
```

Bot akan mengirim prompt:

```
Terminal mode ON. Reply pesan ini untuk command.
```

Sekarang cukup reply pesan tersebut dengan:

```
ls
cd ..
pwd
df -h
```

---

## 4️⃣ Matikan Reply Mode

```
/term off
```

---

# 📝 Logging

Semua output otomatis disimpan ke:

```
bot.log
```

Contoh isi:

```
[2026-02-14 10:22:00]
[DIR] /root
[CMD] uname -a
[RC] 0

[OUT]
Linux server ...
```

---

# 🔁 Auto Start (systemd VPS)

Buat service:

```bash
sudo nano /etc/systemd/system/shellbot.service
```

Isi:

```
[Unit]
Description=Telegram Shell Bot
After=network.target

[Service]
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/shell-new
ExecStart=/usr/bin/python3 shell.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Aktifkan:

```bash
sudo systemctl daemon-reload
sudo systemctl enable shellbot
sudo systemctl start shellbot
```

---

# 🛠 Troubleshooting

## Bot tidak jalan?
```bash
python3 shell.py
```

## Dependency error?
```bash
pip3 install --upgrade python-telegram-bot
```

## Chat ID salah?
Gunakan:
```
/id
```

---

# 📜 License

MIT License

Free to use and modify.
