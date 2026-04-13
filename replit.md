# Aistiqrar Telegram Bot

A Telegram bot built with **Aiogram v3** and **FastAPI**, supporting Arabic and English languages. It helps users browse job listings and manage their profiles.

## Tech Stack

- **Language:** Python 3.12
- **Telegram Framework:** aiogram 3.3.0
- **Web Framework:** FastAPI + uvicorn (health check endpoint)
- **Storage:** In-memory (dictionary-based session storage)
- **Data:** `app/data/jobs.json` (static job listings)
- **i18n:** JSON locale files in `app/locales/` (ar.json, en.json)

## Project Structure

```
run.py                  # Entry point — starts FastAPI + bot polling
app/
  config.py             # Reads BOT_TOKEN from environment
  bot/
    bot.py              # Bot instance
    dispatcher.py       # Aiogram dispatcher
    routers.py          # Route registration
    handlers/           # Command and message handlers
      menu/             # Modular menu system (categories, profile, help, etc.)
  services/
    job_service.py      # Job listing business logic
  database/
    storage.py          # In-memory user session storage
  data/
    jobs.json           # Static job data
  locales/
    ar.json             # Arabic translations
    en.json             # English translations
  keyboards/            # Telegram keyboard builders
  utils/
    translator.py       # Multi-language support
```

## Environment Variables / Secrets

- `BOT_TOKEN` — Telegram bot token from @BotFather (required)

## Running

The app runs on port 5000 via uvicorn. The FastAPI server exposes a `/` health check endpoint and starts the bot polling in the background on startup.

```
python run.py
```

## Deployment

- **Type:** VM (always-running process)
- **Run command:** `python run.py`
