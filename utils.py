#!/usr/bin/env python3

import csv
import os
import secrets
import string
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

CREDENTIALS_CSV = BASE_DIR / "credentials.csv"


def clear():
    """Clear terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def pause(message="\nPress Enter to continue..."):
    input(message)


def random_password(length=20):
    """Generate a secure random password."""

    chars = (
        string.ascii_letters +
        string.digits +
        "!@#$%^&*()-_=+?"
    )

    return "".join(secrets.choice(chars) for _ in range(length))


def write_credentials(rows):
    """
    rows = [
        {
            "plex": "...",
            "jellyfin": "...",
            "password": "..."
        }
    ]
    """

    with open(CREDENTIALS_CSV, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "plex",
                "jellyfin",
                "password"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)


def success(text):
    print(f"\n✅ {text}")


def warning(text):
    print(f"\n⚠️ {text}")


def error(text):
    print(f"\n❌ {text}")


def header(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def run(command):
    """
    Run shell command.
    """

    return subprocess.run(
        command,
        shell=True,
        text=True
    )


def command_exists(command):
    """
    Check if a command exists.
    """

    return (
        subprocess.run(
            f"which {command}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode == 0
    )


def yes_no(question):

    while True:

        answer = input(f"{question} [y/n]: ").lower().strip()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False


def quit_program():

    print("\n👋 Bye!")

    sys.exit(0)
