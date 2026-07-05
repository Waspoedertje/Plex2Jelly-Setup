#!/usr/bin/env python3

import os
from config import configure
from migration import create_users
from docker import start_sync, install_container
from utils import clear


VERSION = "0.1"


def banner():
    print(r"""
===========================================
        Plex2Jelly Setup v%s
===========================================

1) Configure (.env)
2) Create Jellyfin Users
3) Install/Update JellyPlex-Watched
4) Start Watch History Migration
5) Exit

""" % VERSION)


def main():

    while True:

        clear()
        banner()

        choice = input("Select option: ").strip()

        if choice == "1":
            configure()

        elif choice == "2":
            create_users()

        elif choice == "3":
            install_container()

        elif choice == "4":
            start_sync()

        elif choice == "5":
            print("\nBye 👋")
            break

        else:
            input("\nInvalid option. Press Enter...")


if __name__ == "__main__":
    main()
