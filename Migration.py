#!/usr/bin/env python3
"""
Plex2Jelly-Setup - migration.py

Creates Jellyfin users from Plex shared users, generates credentials.csv,
writes USER_MAPPING and LIBRARY_MAPPING to .env, then starts/restarts
JellyPlex-Watched and tails the logs.
"""

import re
import subprocess
from typing import Dict, List, Optional

from plex import Plex
from jellyfin import Jellyfin
from utils import (
    random_password,
    write_credentials,
    header,
    pause,
    success,
    warning,
    error,
    yes_no,
)
from config import update_user_mapping, update_library_mapping, set as set_env, get as get_env


CONTAINER_NAME = "jellyplexwatched"
IMAGE_NAME = "ghcr.io/luigi311/jellyplex-watched:latest"


# Optional built-in suggestions for ugly Plex usernames.
# Users can always override these in the wizard.
KNOWN_NAME_SUGGESTIONS = {
    "angelovanvlierden": "Angelo",
    "aniek_3": "Aniek",
    "bissiie": "Lies",
    "candyma44": "Johan",
    "dmast19": "Norman",
    "robert-dol": "Robert",
    "dol1985": "Robert",
    "gabriel1890": "Tess",
    "hamachi.": "Andre",
    "ilona_m1": "Ilona",
    "jerni804": "Jeroen",
    "jimhermsen": "Jim",
    "k.pa76": "Kevin",
    "leslie9745": "Leslie",
    "montessa25": "Tess",
    "onderweg": "Onderweg",
    "robinpruissen": "Robin",
    "scheff19": "Nick",
    "shirley_o3": "Shirley",
    "sjors-van-dormolen": "Sjors",
    "sjorsvandormolen": "Sjors",
    "t.v.vl": "Tonie",
    "tineked5": "Mama",
    "vaal1989": "Vaal",
    "viezeharry": "Zouhair",
    "wesleyvdwardt": "Wesley",
    "zoemers.": "Jimbo",
    "waspoedertje": "Niemand",
}


def normalize_key(value: str) -> str:
    return value.strip().lower()


def suggest_name(plex_username: str) -> str:
    """Create a human-ish Jellyfin username suggestion."""

    key = normalize_key(plex_username)
    if key in KNOWN_NAME_SUGGESTIONS:
        return KNOWN_NAME_SUGGESTIONS[key]

    name = plex_username.strip()

    # Remove email domain if someone uses an email as Plex username.
    if "@" in name:
        name = name.split("@", 1)[0]

    # Replace separators with spaces.
    name = re.sub(r"[._-]+", " ", name)

    # Remove standalone digits and trailing digits.
    name = re.sub(r"\b\d+\b", "", name)
    name = re.sub(r"\d+$", "", name)

    # Collapse whitespace.
    name = re.sub(r"\s+", " ", name).strip()

    if not name:
        name = plex_username

    # First word as a simple default.
    first = name.split()[0]

    return first[:1].upper() + first[1:].lower()


def choose_jellyfin_name(plex_username: str, existing_lower: Dict[str, str]) -> Optional[str]:
    """Ask user for Jellyfin name. Return None when skipped."""

    suggested = suggest_name(plex_username)

    print("-" * 60)
    print(f"Plex user : {plex_username}")
    print(f"Suggested : {suggested}")
    print()
    print("Press Enter to accept, type a new name, or type 'skip'.")

    value = input("Jellyfin name: ").strip()

    if value.lower() == "skip":
        return None

    jelly_name = value or suggested

    if jelly_name.lower() in existing_lower:
        print(f"Already exists: {existing_lower[jelly_name.lower()]}")
        return existing_lower[jelly_name.lower()]

    return jelly_name


def map_libraries(plex: Plex, jellyfin: Jellyfin) -> Dict[str, str]:
    """Map Plex libraries to Jellyfin libraries."""

    header("Library Mapping")

    plex_libs = plex.library_names()
    jelly_libs = jellyfin.library_names()
    jelly_lower = {name.lower(): name for name in jelly_libs}

    mapping: Dict[str, str] = {}

    defaults = {
        "movies": "Films",
        "movie": "Films",
        "tv shows": "Series",
        "shows": "Series",
        "series": "Series",
    }

    print("Jellyfin libraries:")
    for name in jelly_libs:
        print(f"  - {name}")
    print()

    for plex_lib in plex_libs:
        # Skip music by default; watched migration usually only needs movies/shows.
        lower = plex_lib.lower()
        if lower in ("muziek", "music", "muziekbeste"):
            continue

        default = defaults.get(lower, plex_lib)
        if default.lower() in jelly_lower:
            default = jelly_lower[default.lower()]

        print(f"Plex library: {plex_lib}")
        value = input(f"Jellyfin library [{default}] (empty=accept, skip=skip): ").strip()

        if value.lower() == "skip":
            continue

        mapping[plex_lib] = value or default
        print()

    return mapping


def docker_available() -> bool:
    return subprocess.run(
        ["docker", "--version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def container_exists() -> bool:
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return CONTAINER_NAME in result.stdout.splitlines()


def container_running() -> bool:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return CONTAINER_NAME in result.stdout.splitlines()


def start_or_restart_jellyplexwatched() -> None:
    """Start/restart JellyPlex-Watched. Prefer docker compose if available."""

    header("Starting JellyPlex-Watched")

    if not docker_available():
        error("Docker is not installed or not available in PATH.")
        return

    # Use docker compose if docker-compose.yml exists.
    compose_exists = subprocess.run(
        ["test", "-f", "docker-compose.yml"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0

    if compose_exists:
        print("Using docker compose...")
        subprocess.run(["docker", "compose", "up", "-d"], check=False)
    elif container_exists():
        print("Restarting existing container...")
        subprocess.run(["docker", "restart", CONTAINER_NAME], check=False)
    else:
        warning("No docker-compose.yml and no existing jellyplexwatched container found.")
        print("Create the container manually or add docker-compose.yml first.")
        return

    print()
    if yes_no("Show live logs now?"):
        print("\nPress CTRL+C to stop viewing logs. The container keeps running.\n")
        try:
            subprocess.run(["docker", "logs", "-f", CONTAINER_NAME], check=False)
        except KeyboardInterrupt:
            print("\nStopped log view.")


def create_users() -> None:
    """Main wizard: create Jellyfin users, mappings, credentials, then run sync."""

    header("Plex → Jellyfin User Migration")

    plex = Plex()
    jellyfin = Jellyfin()

    print("Testing servers...")
    plex_ok = plex.test_connection()
    jelly_ok = jellyfin.test_connection()

    if not plex_ok or not jelly_ok:
        error("Fix server configuration first.")
        pause()
        return

    plex_users = plex.usernames()
    if not plex_users:
        warning("No Plex shared users found.")
        pause()
        return

    existing_lower = {name.lower(): name for name in jellyfin.usernames()}

    header(f"Users found: {len(plex_users)}")

    credentials: List[Dict[str, str]] = []
    user_mapping: Dict[str, str] = {}

    for plex_user in plex_users:
        jelly_name = choose_jellyfin_name(plex_user, existing_lower)

        if jelly_name is None:
            warning(f"Skipped {plex_user}")
            continue

        user_mapping[plex_user] = jelly_name

        if jelly_name.lower() in existing_lower:
            credentials.append({
                "plex": plex_user,
                "jellyfin": jelly_name,
                "password": "EXISTING",
            })
            continue

        password = random_password()

        try:
            jellyfin.create_user_with_password(jelly_name, password)
            existing_lower[jelly_name.lower()] = jelly_name
            print(f"Created: {jelly_name}")
            credentials.append({
                "plex": plex_user,
                "jellyfin": jelly_name,
                "password": password,
            })
        except Exception as exc:
            error(f"Failed to create {jelly_name}: {exc}")
            credentials.append({
                "plex": plex_user,
                "jellyfin": jelly_name,
                "password": "FAILED",
            })

    if not user_mapping:
        warning("No users mapped. Nothing to save.")
        pause()
        return

    write_credentials(credentials)
    update_user_mapping(user_mapping)

    library_mapping = map_libraries(plex, jellyfin)
    update_library_mapping(library_mapping)

    # Make sure watched sync runs live, not dry-run.
    set_env("DRYRUN", "False")
    set_env("SYNC_FROM_PLEX_TO_JELLYFIN", "True")
    set_env("SYNC_FROM_JELLYFIN_TO_PLEX", "False")

    success("Users, credentials and mappings saved.")
    print("Generated/updated:")
    print("  - credentials.csv")
    print("  - .env USER_MAPPING")
    print("  - .env LIBRARY_MAPPING")

    print()
    if yes_no("Start/restart JellyPlex-Watched now?"):
        start_or_restart_jellyplexwatched()
    else:
        pause()


# Alias for plex2jelly.py menu compatibility.
def run_migration():
    create_users()
