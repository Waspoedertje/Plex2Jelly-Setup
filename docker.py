#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

from utils import (
    success,
    warning,
    error,
    pause,
    run,
    command_exists,
    header
)


PROJECT_DIR = Path.cwd()
CONFIG_DIR = PROJECT_DIR / "config"
COMPOSE_FILE = PROJECT_DIR / "docker-compose.yml"


IMAGE = "ghcr.io/luigi311/jellyplex-watched:latest"
CONTAINER = "jellyplexwatched"


############################################################


def docker_installed():

    return command_exists("docker")


############################################################


def compose_installed():

    result = subprocess.run(
        ["docker", "compose", "version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


############################################################


def install_container():

    header("Install JellyPlex-Watched")

    if not docker_installed():

        error("Docker is not installed.")

        print()
        print("Install Docker first.")
        pause()

        return

    if not compose_installed():

        error("Docker Compose not found.")
        pause()

        return

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    compose = f"""services:
  jellyplexwatched:
    image: {IMAGE}
    container_name: {CONTAINER}
    restart: unless-stopped

    env_file:
      - .env

    volumes:
      - ./config:/config
"""

    COMPOSE_FILE.write_text(
        compose,
        encoding="utf-8"
    )

    print()

    print("Pulling latest image...")

    run("docker compose pull")

    print()

    print("Starting container...")

    run("docker compose up -d")

    success("Container installed.")

    pause()


############################################################


def restart():

    header("Restart Container")

    run(
        f"docker restart {CONTAINER}"
    )

    success("Restarted.")

    pause()


############################################################


def stop():

    header("Stop Container")

    run(
        f"docker stop {CONTAINER}"
    )

    success("Stopped.")

    pause()


############################################################


def remove():

    header("Remove Container")

    run(
        f"docker rm -f {CONTAINER}"
    )

    success("Removed.")

    pause()


############################################################


def logs():

    header("Logs")

    os.system(

        f"docker logs -f {CONTAINER}"

    )


############################################################


def start_sync():

    header("Start Migration")

    result = subprocess.run(

        [

            "docker",

            "ps",

            "--format",

            "{{.Names}}"

        ],

        capture_output=True,

        text=True

    )

    if CONTAINER in result.stdout:

        print()

        print("Restarting container...")

        run(

            f"docker restart {CONTAINER}"

        )

    else:

        print()

        print("Starting container...")

        run(

            "docker compose up -d"

        )

    print()

    print("Watching logs...")

    print()

    logs()
