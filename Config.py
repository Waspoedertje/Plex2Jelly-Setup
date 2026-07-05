#!/usr/bin/env python3

import json
from pathlib import Path

from utils import header, success, warning, pause

ENV_FILE = Path(".env")


DEFAULTS = {

    "DRYRUN": "False",
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


############################################################


def load():

    env = DEFAULTS.copy()

    if not ENV_FILE.exists():
        return env

    with open(ENV_FILE, encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            env[key] = value.strip().strip('"')

    return env


############################################################


def save(env):

    with open(ENV_FILE, "w", encoding="utf-8") as f:

        for key, value in env.items():

            f.write(f'{key}="{value}"\n')


############################################################


def get(key):

    env = load()

    return env.get(key)


############################################################


def set(key, value):

    env = load()

    if isinstance(value, dict):

        value = json.dumps(value)

    env[key] = str(value)

    save(env)


############################################################


def configure():

    env = load()

    header("Configure Servers")

    print("Plex")

    value = input(
        f"URL [{env['PLEX_BASEURL']}]: "
    ).strip()

    if value:
        env["PLEX_BASEURL"] = value

    value = input(
        "Token: "
    ).strip()

    if value:
        env["PLEX_TOKEN"] = value

    print()

    print("Jellyfin")

    value = input(
        f"URL [{env['JELLYFIN_BASEURL']}]: "
    ).strip()

    if value:
        env["JELLYFIN_BASEURL"] = value

    value = input(
        "API Key: "
    ).strip()

    if value:
        env["JELLYFIN_TOKEN"] = value

    save(env)

    print()

    try:

        from plex import Plex

        if Plex().test_connection():
            success("Plex OK")
        else:
            warning("Plex failed")

    except Exception as e:

        warning(e)

    print()

    try:

        from jellyfin import Jellyfin

        if Jellyfin().test_connection():
            success("Jellyfin OK")
        else:
            warning("Jellyfin failed")

    except Exception as e:

        warning(e)

    pause()


############################################################


def update_user_mapping(mapping):

    set(

        "USER_MAPPING",

        mapping

    )


############################################################


def update_library_mapping(mapping):

    set(

        "LIBRARY_MAPPING",

        mapping

    )


############################################################


def show():

    env = load()

    header(".env")

    for k, v in env.items():

        print(f"{k:<30}{v}")

    pause()
