#!/usr/bin/env python3

import requests

from config import get


class Jellyfin:

    def __init__(self):

        self.base_url = get("JELLYFIN_BASEURL").rstrip("/")
        self.token = get("JELLYFIN_TOKEN")

        self.headers = {
            "X-Emby-Token": self.token,
            "Content-Type": "application/json"
        }

    ############################################################

    def _get(self, endpoint):

        r = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            timeout=30
        )

        r.raise_for_status()

        return r.json()

    ############################################################

    def _post(self, endpoint, data=None):

        r = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data,
            timeout=30
        )

        r.raise_for_status()

        if r.text:
            return r.json()

        return None

    ############################################################

    def validate(self):

        try:

            self._get("/System/Info")

            return True

        except Exception:

            return False

    ############################################################

    def server_name(self):

        return self._get("/System/Info")["ServerName"]

    ############################################################

    def version(self):

        return self._get("/System/Info")["Version"]

    ############################################################

    def users(self):

        users = {}

        for user in self._get("/Users"):

            users[user["Name"]] = user

        return users

    ############################################################

    def usernames(self):

        return sorted(self.users().keys(), key=str.lower)

    ############################################################

    def user_exists(self, username):

        users = self.users()

        return username in users

    ############################################################

    def create_user(self, username):

        self._post(

            "/Users/New",

            {
                "Name": username
            }

        )

        return self.users()[username]

    ############################################################

    def set_password(self, user_id, password):

        self._post(

            f"/Users/{user_id}/Password",

            {

                "CurrentPw": "",

                "NewPw": password,

                "ResetPassword": False

            }

        )

    ############################################################

    def create_user_with_password(self, username, password):

        if self.user_exists(username):

            return False

        user = self.create_user(username)

        self.set_password(

            user["Id"],

            password

        )

        return True

    ############################################################

    def libraries(self):

        libraries = []

        for folder in self._get("/Library/VirtualFolders"):

            libraries.append({

                "name": folder["Name"],

                "type": folder["CollectionType"]

            })

        return libraries

    ############################################################

    def library_names(self):

        return [

            library["name"]

            for library in self.libraries()

        ]

    ############################################################

    def test_connection(self):

        print()
        print("Testing Jellyfin...")
        print("-" * 40)

        try:

            print(f"Server : {self.server_name()}")
            print(f"Version: {self.version()}")

            print()
            print("Libraries")

            for library in self.libraries():

                print(
                    f'  • {library["name"]} '
                    f'({library["type"]})'
                )

            print()

            print(
                f"Users : {len(self.users())}"
            )

            print()
            print("✔ Jellyfin connection successful.")

            return True

        except Exception as e:

            print()
            print("❌ Unable to connect to Jellyfin.")
            print(e)

            return False

    ############################################################

    def print_summary(self):

        print()

        print(f"Server : {self.server_name()}")
        print(f"Version: {self.version()}")

        print()

        print("Libraries")
        print("-" * 40)

        for library in self.libraries():

            print(
                f'{library["name"]} '
                f'({library["type"]})'
            )

        print()

        print(f"Users : {len(self.users())}")
