# Stargaze Floor Bot

This is a [Discord] bot designed to display floor pricing for Stargaze NFT collections.

- Uses a private locked channel to display the current floor price and trend
- Allows users to query for floor pricing of specific traits

## Table of Contents

- [Setup](#setup)
  - [Create the floor channels](#create-the-floor-channels)
  - [Create a discord bot](#create-a-discord-bot)
  - [Create cached collection info](#create-cached-collection-info)
- [Installation](#installation)
  - [Build the docker image](#build-the-docker-image)
  - [Configuration](#configuration)
  - [Run the docker image](#run-the-docker-image)
  - [Running without docker](#running-without-docker)
- [Usage](#usage)
- [Deployment](#deployemnt)
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

```txt
https://discord.com/channels/<GUILD_ID>/<CHANNEL_ID>
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
- Connect to voice channels

Now copy the URL generated at the bottom and paste it in your browser to invite the bot to your server.

You will also need to know your `DISCORD_KEY` which can be found by clicking on "Bot" and selecting "Reset Token."

### Create cached collection info

The bot requires the collection metadata to be cached ahead of time. When building the docker image (later) it will copy the `cache` folder to the docker image so it's best to pre-build those files if you haven't done so yet.

You can generate cache files by looking at the following examples in the [stargaze-utils] github repo:

- [/examples/get_collection_info.py]
- [/examples/get_new_collections.py]

## Installation

This bot is designed to run in a discord server without needing the stars CLI. Instead, it queries the blockchain using via HTTPS calls.

### Build the docker image

You can build the docker file with the following command:

```sh
docker build -t stargazefloorbot:dev .
```

If you need to build a multi-platform image, you can set up a [buildx] context that supports the architectures you want and then build:

```sh
docker buildx build --push \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/starship-ibc/stargaze-floor-bot:dev \
  .

docker pull ghcr.io/starship-ibc/stargaze-floor-bot:dev
```

> For buildx, you will need to `--push` to a registry and then pull it down because docker does not currently support loading multi-architecture images locally.

### Configuration

Configuration is now handled by a minimal set of environment variables and a yaml file that must be present for the system to start.

The following environment variables should be set:

- `DISCORD_KEY` The discord bot secret key
- `CONFIG_FILE` The path to the yaml config file

The following is an example yaml config file:

```yaml
# optional, logging level
log_level: INFO

# optional, a default refresh interval for all collections
refresh_interval: 300

# optional, if true for a collection, will perform strict validation. this is 
# more accurate but can take a significantly longer time and may cause discord issues
strict_validation: False 

# A list of collection information
collections:
    # optional, the name of the collection (defaults to the SG721 address)
  - name: Andromaverse

    # required, the SG721 address
    sg721: stars1quce89l8clsn8s5tmq5sylg370h58xfnkwadx72crjv90jmetp4syt4sgr

    # optional, a prefix to put in front of the floor value
    # note the space at the end is often desired
    prefix: "Floor: "

    # optional, overwrites the default interval for this collection only
    refresh_interval: 300

    # optional, overwrites the default value above for this collection only
    strict_validation: False

    # optional, use to disable the "querytraitfloor" command, such as if the
    # collection has no traits to query
    enable_trait_query: True

    # required, a list of channels to set the floor price
    channels:
        # required, the guild id
      - guild_id: 977279710713245766

        # required, the channel id. the bot should have view, manage, and connect
        # permissions for this to work
        channel_id: 983204853545316392
```

### Run the docker image

To run the docker image with a local yaml file, you can mount it within the container:

```sh
docker run -v $PWD/config.yaml:/stargaze-floor-bot/config.yaml stargazefloorbot:dev
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

## Deployment

This bot is designed to be deployed to [Akash], which lets you deploy containers to a decentralized cloud at a very low cost. The recommended method for deploying to Akash is to use [Akashlytics]. You will need at least 5 $AKT to create a deployment, which should be enough for the bot to run for a few months. You can also follow any of the published [Akash deployment guides].

Before you deploy to akash, you'll need to create an image with the `config.yaml` file built in. We hope to update this in the future, but right now Akash doesn't have a great way to add a configuration file to an existing container.

Edit the `Dockerfile` to copy the appropriate config.yaml file into the image and then build it with a tag like "1.0.6-andr".

> If you're on a computer with arm64 architecture such as M1 mac, you'll need to cross-compile with buildx as most of the Akash providers run amd64 architecture.

1. Copy `akash.yaml` to `akash-deploy.yaml`
2. Set the `image` to your custom image you created.
3. Set the `DISCORD_KEY` environment variable.
4. In Akashlytics, click "CREATE DEPLOYMENT"
5. Select "From a file" and select your `akash-deploy.yaml` file
6. Give your deployment a name and click "CREATE DEPLOYMENT ➡️"

    > You will be prompted to deposit 5 $AKT to get bids on your deployment. This will be used as an escrow account and the remainder refunded when you close the deployment.

6. Click "DEPOSIT" and "Approve" to sign the transaction

    > This will transmit a **"Create Deployment"** message that initializes the escrow contract and allows you to accept bids on your deployment.

7. Select a bid and click "Accept Bid" and "Approve" to sign the transaction

    > This is a **"Create Lease"** message and reserves your compute space until you close the deployment or the assicated escrow contract runs out of funds.

It may take a few minutes your deployment to be published and get started. You should be able to see the container logs and system events.

### Closing a deployment

In order to stop spending $AKT, you will need to close your deployment which will shut down the bot and release any funds remaining in the deployment escrow account.

Click on the "•••" next to your deployment and choose "Close deloyment." You should be prompted to sign a transaction that contains the "Close deployment" message. Approve this to shut down your deployment.

## Donations

A special thanks to [Andromeda Labs] for sponsoring this bot.

If you'd like to make a donation, you may send $STARS to the following address. If you're like to sponsor a specific issue, feel free to include it in the memo line so I know what's most important to the community.

```txt
stars1z6mj02l2s8v0vsxfsark5v7t076ds8pu9nj2fv
```


[Akash]: https://akash.network/
[Akashlytics]: https://www.akashlytics.com/
[Akash deployment guides]: https://docs.akash.network/guides
[buildx]: https://docs.docker.com/build/buildx/
[Discord]: https://discord.com/
[Andromeda Labs]: https://twitter.com/AndromaverseLab
[stargaze-utils]: https://github.com/starship-ibc/stargaze-utils
[/examples/get_collection_info.py]: https://github.com/starship-ibc/stargaze-utils/blob/main/examples/get_collection_info.py
[/examples/get_new_collections.py]: https://github.com/starship-ibc/stargaze-utils/blob/main/examples/get_new_collections.py
