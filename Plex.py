from plexapi.server import PlexServer
from config import get


class Plex:

    def __init__(self):

        self.server = PlexServer(
            get("PLEX_BASEURL"),
            get("PLEX_TOKEN")
        )

    def server_name(self):
        return self.server.friendlyName

    def version(self):
        return self.server.version

    def libraries(self):

        libs = []

        for lib in self.server.library.sections():

            libs.append({
                "name": lib.title,
                "type": lib.type
            })

        return libs

    def users(self):

        return self.server.myPlexAccount().users()

    def usernames(self):

        return sorted(
            [u.username for u in self.users()],
            key=str.lower
        )
