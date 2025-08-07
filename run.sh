#!/bin/bash
set -e

# Load .env if exists
if [ -f ".env" ]; then
  export $(cat .env | xargs)
fi

# Pick your bot entry file
if [ -f "main.py" ]; then
  python main.py
elif [ -f "bot.py" ]; then
  python bot.py
elif [ -f "final_bot_with_weighted_sizing.py" ]; then
  python final_bot_with_weighted_sizing.py
else
  echo "No bot file found. Please create main.py or edit run.sh"
  exit 1
fi
