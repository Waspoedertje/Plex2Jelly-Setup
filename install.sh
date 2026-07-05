#!/usr/bin/env bash

set -e

REPO="https://github.com/Waspoedertje/Plex2Jelly-Setup.git"
INSTALL_DIR="$HOME/Plex2Jelly-Setup"

echo
echo "========================================"
echo " Plex2Jelly Setup Installer"
echo "========================================"
echo

# Git
if ! command -v git >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y git
fi

# Python
if ! command -v python3 >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Clone of update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "Downloading..."
    git clone "$REPO" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

# Dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Config
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo
echo "Starting Plex2Jelly..."
echo

python3 plex2jelly.py
