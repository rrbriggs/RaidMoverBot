# RaidMoverBot

RaidMoverBot is a Discord bot designed to manage and move users in voice channels during raids. It supports setting specific raid channels and allows administrators to move users from a raid channel to a destination channel effortlessly. The bot is deployed using [Fly.io](https://fly.io/) for easy and lightweight hosting with a simple SQLite database for configuration storage.

## Features

- **Set Admin Role:** Allows the server owner or administrator to set an admin role for bot commands, limiting who can use the bot commands.
- **Set Raid and Alt-Raid Channels:** Admins can set the primary and alternate raid voice channels.
- **Set Destination Channel:** Admins can set a destination voice channel for moving raid participants.
- **Move Users:** Move users from the configured raid or alt-raid channels to a destination channel with a simple command.
- **SQLite Database:** Stores configuration settings for each server (guild).
- **Auto Role Check:** Verifies if a user has the required permissions or roles to execute admin commands.

## Setup and Deployment

### Prerequisites

1. [Python 3.12](https://www.python.org/downloads/)
2. A [Discord Bot Token](https://discord.com/developers/applications)
3. [Fly.io](https://fly.io/) account for deployment
4. Docker (optional, for containerized deployment and required for fly.io)

### Local Development

1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/raidmoverbot.git
    cd raidmoverbot
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create an `.env` file with the following content:
    ```
    DISCORD_BOT_TOKEN=your-discord-bot-token
    ```

4. Run the bot:
    ```bash
    python bot.py
    ```

### Docker Deployment

1. Build the Docker image:
    ```bash
    docker build -t raidmoverbot .
    ```

2. Run the Docker container:
    ```bash
    docker run -d --name raidmoverbot -v data_volume:/data raidmoverbot
    ```

### Fly.io Deployment

1. Install the Fly.io CLI and log in:
    ```bash
    flyctl auth login
    ```

2. Create and configure your app on Fly.io:
    ```bash
    flyctl launch
    ```

3. Deploy the bot to Fly.io:
    ```bash
    flyctl deploy
    ```

4. Set your bot token as a secret on Fly.io:
    ```bash
    flyctl secrets set DISCORD_BOT_TOKEN=your-discord-bot-token
    ```

## Configuration

The bot uses an SQLite database located at `/data/settings.db` for storing guild-specific settings. The database is automatically initialized with the required tables on first run. Configuration commands include:

- `/setadminrole` – Set the admin role for who is allowed to manage bot commands.
- `/setraidchannel` – Set the primary raid voice channel.
- `/setaltraidchannel` – Set the alt raid voice channel.
- `/setdestinationchannel` – Set the destination voice channel.
- `/getconfigs` – Retrieve current configuration for the guild.
- `/moveraid` – Move all users from the raid channel to the destination channel.
- `/movealtraid` – Move all users from the alternate raid channel to the destination channel.

## Fly.io Configuration (fly.toml)

The provided `fly.toml` file contains the Fly.io configuration settings. Key configurations include:

- **Memory and CPU Allocation:** Allocates 256MB of memory and 1 shared CPU.
- **Storage:** The bot requires a persistent volume mounted at `/data` for storing the SQLite database.
- **Auto Scaling:** The app will auto-stop and auto-start machines based on traffic.

## Scaling Limitations

Currently, RaidMoverBot is **not built for scaling beyond one machine**. This might be solved as simply as swapping to a different db, if you're using fly.io, their postgres setup is probably a good choice.

