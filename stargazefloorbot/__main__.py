import logging
import os

import discord

from stargazefloorbot.config.config import Config

from .floor_client import FloorClient

logging.basicConfig(level=logging.INFO)
CONFIG_FILE = os.environ.get("CONFIG_FILE", default="config.yaml")
config = Config.from_yaml(CONFIG_FILE)

logging.basicConfig(level=logging._nameToLevel[config.log_level])
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("stargazeutils.market.market_client").setLevel(logging.WARNING)
logging.getLogger("stargazeutils.market.market_ask").setLevel(logging.ERROR)
LOG = logging.getLogger(__name__)

intents = discord.Intents.default()
client = FloorClient(
    intents=intents,
    config=config,
)

client.run(config.discord_key)
