import logging
import os

import discord

from .config import ConfigManager
from .floor_client import FloorClient

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

if "DISCORD_KEY" not in os.environ.keys():
    LOG.error("DISCORD_KEY environment variable is not set")
    exit(1)

discord_key = os.environ.get("DISCORD_KEY")
interval = int(os.environ.get("REFRESH_INTERVAL", default="300"))
config_file = os.environ.get("CONFIG_FILE", default="config.json")

sv = os.environ.get("STRICT_VALIDATION", default="False")
strict_validation = sv in ["true", "True", "TRUE", "1", "yes", "YES", "Yes"]

LOG.info(f"Config interval = {interval} seconds")
LOG.info(f"Config file = {config_file}")

config_manager = ConfigManager.from_json_file(config_file)
intents = discord.Intents.default()
client = FloorClient(
    intents=intents,
    config_manager=config_manager,
    interval=interval,
    strict_validation=strict_validation)

client.run(discord_key)
