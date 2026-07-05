#!/usr/bin/env python3

from pathlib import Path

ENV_FILE = Path(".env")


DEFAULTS = {
    "DRYRUN": "True",
    "DEBUG_LEVEL": "INFO",
    "RUN_ONLY_ONCE": "False",
    "SLEEP_DURATION": "3600",
    "LOG_FILE": "log.log",
    "MARK_FILE": "mark.log",
    "REQUEST_TIMEOUT": "300",
    "MAX_THREADS": "1",

    "GENERATE_GUIDS": "True",
    "GENERATE_LOCATIONS": "True",

    "USER_MAPPING": "{}",
    "LIBRARY_MAPPING": "{}",

    "PLEX_BASEURL": "",
    "PLEX_TOKEN": "",

    "JELLYFIN_BASEURL": "",
    "JELLYFIN_TOKEN": "",

    "SYNC_FROM_PLEX_TO_JELLYFIN": "True",
    "SYNC_FROM_JELLYFIN_TO_PLEX": "False"
}


def load_env():
    env = DEFAULTS.copy()

    if not ENV_FILE.exists():
        return env

    with open(ENV_FILE, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            env[key.strip()] = value.strip().strip('"')

    return env


def save_env(env):

    with open(ENV_FILE, "w", encoding="utf-8") as f:

        for key, value in env.items():

            f.write(f'{key}="{value}"\n')


def configure():

    env = load_env()

    print()
    print("Configure Plex")
    print("-" * 40)

    plex = input(f"Plex URL [{env['PLEX_BASEURL']}]: ").strip()
    if plex:
        env["PLEX_BASEURL"] = plex

    token = input("Plex Token: ").strip()
    if token:
        env["PLEX_TOKEN"] = token

    print()
    print("Configure Jellyfin")
    print("-" * 40)

    jf = input(f"Jellyfin URL [{env['JELLYFIN_BASEURL']}]: ").strip()
    if jf:
        env["JELLYFIN_BASEURL"] = jf

    token = input("Jellyfin API Key: ").strip()
    if token:
        env["JELLYFIN_TOKEN"] = token

    save_env(env)

    print()
    print("✅ .env opgeslagen")
    input("Press Enter...")


def get(key):

    return load_env().get(key)


def set(key, value):

    env = load_env()

    env[key] = value

    save_env(env)
