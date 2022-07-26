# Stargaze Floor Bot

This is a [Discord] bot designed to display floor pricing for Stargaze NFT collections.

* Uses a private locked channel to display the current floor price
* Allows users to query for floor pricing of specific traits

## Table of Contents

- [Setup](#setup)
    - [Create the floor channels](#create-the-floor-channels)
    - [Create your configuration file](#create-your-configuration-file)
    - [Create a discord bot](#create-a-discord-bot)
    - [Create cached collection info](#create-cached-collection-info)
- [Installation](#installation)
- [Usage](#usage)
- [Donations](#donations)

## Setup

The following must be set up before you can use the bot.

### Create the floor channels

In order to reduce the number of permissions the bot needs to work, a one-time setup of a voice channel is required so that the bot can modify the channel name.

1. Create a new voice channel (the name does not matter)
2. Set up the following permissions for `@everyone`
    
    - View Channel ✅
    - Everything else ❌

3. Note your `GUILD_ID` and `CHANNEL_ID`. You can do this by copying a link to the channel and examining it:

```
https://discord.com/channels/<GUILD_ID>/<CHANNEL_ID>
```

### Create your configuration file

Create a `config.json` file that contains a list of the collections you want to track and how you want them to be displayed. Example:

```json
[
    {
        "guild_id": 1234,
        "channel_id": 1234,
        "collection_name": "name",
        "sg721": "stars-address",
        "prefix": "Floor: "
    }
]
```

### Create a discord bot

You will need to create a discord bot and invite it to your server.

1. Go to the [Discord Developer](https://discord.com/developers/applications) page
2. Click "New Application" and create a new app
3. Click on "Bot" and select "Add Bot"
4. Give your bot a username and icon (optional)
5. Click on "OAuth2" > "URL Generator"

You will want to give your bot the following permissions:

#### Scopes

- bot
- applications.commands

#### Bot Permissions

- Manage Channels
- Send Messages
- Manage Messages
- Embed Links
- Attach Files

Now copy the URL generated at the bottom and paste it in your browser to invite the bot to your server.

You will also need to know your `DISCORD_KEY` which can be found by clicking on "Bot" and selecting "Reset Token."

### Create cached collection info

The bot requires the collection metadata to be cached ahead of time. When building the docker image (later) it will copy the `cache` folder to the docker image so it's best to pre-build those files if you haven't done so yet.

You can generate cache files by looking at the following examples in the stargaze-utils github repo:

- /examples/get_collection_info.py
- /examples/get_new_collections.py

## Installation

This bot is designed to run in a discord server without needing the stars CLI. Instead, it queries the blockchain using via HTTPS calls.

### Build the docker image

```sh
docker build -t stargazefloorbot:dev .
```

### Environment variables

At minimum, you should set your DISCORD_KEY environment variable. The others are optional and can be included if you want to change them.

- `DISCORD_KEY` (required) The discord bot key
- `INTERVAL` (default 300) Seconds between fetching new asks
- `STRICT_VALIDATION` (default False) Uses strict validation when checking for asks. This will take longer to update the asks list, but will be more accurate as it checks for ownership, authorization, and other anomolies.
- `CONFIG_FILE` (default `stargaze-floor-bot/config.json`) Location of the config file

### Run the docker image

```sh
docker run \
  -e DISCORD_KEY \
  -v $PWD/config.json:/stargaze-floor-bot/config.json \
  stargazefloorbot:dev
```

You should see some basic output indicating that the configuration has loaded and a connection to Gateway established. Any invalid asks will also be sent to the output.

### Running without docker

Alternatively, you can run the bot without using containers as well. You will need to have the following dependencies installed on your machine:

- [Python3.10](https://www.python.org/)
- [Poetry](https://python-poetry.org/docs/master/#installation)

Install the python dependencies:

```sh
poetry install
```

Set up your environment variables:

```sh
export DISCORD_KEY=<discord_key>
```

Run the project

```sh
poetry run python -m stargazefloorbot
```


## Usage

Once your bot is running and invited to your server, you can use the following app commands via the slash menu:

### /listcollections

This command will list the enabled collections and the most recent floor price detected.

### /querytraitfloor

This command will prompt the user for a collection, trait name, and trait value and then display the lowest three tokens including traits and link to the Stargaze marketplace for purchase.

## Donations

A special thanks to [Andromeda Labs](https://twitter.com/AndromaverseLab) for sponsoring this bot.

If you'd like to make a donation, you may send $STARS to the following address. If you're like to sponsor a specific issue, feel free to include it in the memo line so I know what's most important to the community.

```
stars1z6mj02l2s8v0vsxfsark5v7t076ds8pu9nj2fv
```
