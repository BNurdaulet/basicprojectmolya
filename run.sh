#!/usr/bin/env bash
# Бір командамен іске қосу: ./run.sh
set -e
cd "$(dirname "$0")"
[ -f .env ] || { cp .env.example .env; echo ".env жасалды — ішіне API кілттерін жазыңыз"; }
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
python main.py
