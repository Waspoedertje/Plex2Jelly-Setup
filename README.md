# Plex2Jelly-Setup
Automatically migrate Plex users to Jellyfin, generate secure passwords and create JellyPlex-Watched mappings.


# Plex2Jelly-Setup

Automatically migrate Plex users to Jellyfin before syncing watch history.

This project is designed to work together with JellyPlex-Watched.

## Features

- Read all shared Plex users
- Create Jellyfin users automatically
- Generate secure random passwords
- Generate `user_mapping.json`
- Export `credentials.csv`
- Skip existing Jellyfin users
- Interactive name mapping
- Works with JellyPlex-Watched

## Example

Plex:

```
angeloudjsjs2837
anik_3372bdnsndtemp
Robert-ilovepussycats
```

Wizard:

```
angeloudjsjs2837           -> Angelo
anik_3372bdnsndtemp        -> Aniek
Robert-ilovepussycats      -> Robert
```

Generated:

```
credentials.csv
```

| Plex | Jellyfin | Password |
|------|----------|----------|
| anik_3372bdnsndtemp | Angelo | ******** |
| anik_3372bdnsndtemp | Aniek | ******** |

and

```
user_mapping.json
```

```json
{
  "anik_3372bdnsndtemp": "Angelo",
  "anik_3372bdnsndtemp": "Aniek",
  "Robert-ilovepussycats": "Robert"
}
```

## Workflow

1. Read all Plex users
2. Ask for the desired Jellyfin username
3. Create missing Jellyfin users
4. Generate secure passwords
5. Save credentials.csv
6. Save user_mapping.json
7. Run JellyPlex-Watched to migrate watched status and playback progress

## Planned Features

- Web interface
- Automatic detection of new Plex users
- Password reset
- Email export
- QR codes
- One-click JellyPlex-Watched integration

## Requirements

- Python 3.11+
- Plex Admin Account
- Jellyfin Admin API Key

## Credits

Watch history synchronization is powered by:

https://github.com/luigi311/JellyPlex-Watched

This project focuses on automating user migration and account creation.
