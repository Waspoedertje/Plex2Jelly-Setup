#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET

from config import get


class Plex:

    def __init__(self):

        self.base_url = get("PLEX_BASEURL").rstrip("/")
        self.token = get("PLEX_TOKEN")

        self.headers = {
            "Accept": "application/xml"
        }

    ############################################################

    def _get(self, endpoint):

        url = f"{self.base_url}{endpoint}"

        r = requests.get(
            url,
            headers=self.headers,
            params={
                "X-Plex-Token": self.token
            },
            timeout=30
        )

        r.raise_for_status()

        return r.text

    ############################################################

    def validate(self):

        try:

            self._get("/")

            return True

        except Exception:

            return False

    ############################################################

    def server_name(self):

        xml = self._get("/")

        root = ET.fromstring(xml)

        return root.attrib.get("friendlyName")

    ############################################################

    def version(self):

        xml = self._get("/")

        root = ET.fromstring(xml)

        return root.attrib.get("version")

    ############################################################

    def libraries(self):

        xml = self._get("/library/sections")

        root = ET.fromstring(xml)

        libraries = []

        for library in root.findall("Directory"):

            libraries.append({

                "id": library.attrib["key"],

                "name": library.attrib["title"],

                "type": library.attrib["type"]

            })

        return libraries

    ############################################################

    def shared_users(self):

        r = requests.get(

            "https://plex.tv/api/users",

            params={

                "X-Plex-Token": self.token

            },

            timeout=30

        )

        r.raise_for_status()

        root = ET.fromstring(r.text)

        users = []

        for user in root.findall("User"):

            users.append({

                "id": user.attrib.get("id"),

                "username": user.attrib.get("username"),

                "email": user.attrib.get("email"),

                "title": user.attrib.get("title")

            })

        return users

    ############################################################

    def usernames(self):

        names = []

        for user in self.shared_users():

            username = user["username"]

            if username:

                names.append(username)

        return sorted(names, key=str.lower)

    ############################################################

    def print_summary(self):

        print()

        print("Server :", self.server_name())

        print("Version:", self.version())

        print()

        print("Libraries")

        print("----------------")

        for library in self.libraries():

            print(

                f'{library["name"]}'

                f' ({library["type"]})'

            )

        print()

        print(

            f"Shared Users: {len(self.shared_users())}"

        )
