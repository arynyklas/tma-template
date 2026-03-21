#!/bin/sh
set -e

echo "Starting Telegram Bot..."

exec python -m src.presentation.bot.main
