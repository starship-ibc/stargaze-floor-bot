import logging
import os

import discord

from .config import ConfigManager
from .floor_client import FloorClient

LOG_LEVEL = os.environ.get("LOG_LEVEL", default="INFO")
print(f"Setting logging level to {LOG_LEVEL}")

logging.basicConfig(level=logging._nameToLevel[LOG_LEVEL])
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("stargazeutils.market.market_ask").setLevel(logging.ERROR)
LOG = logging.getLogger(__name__)

if "DISCORD_KEY" not in os.environ.keys():
    LOG.error("DISCORD_KEY environment variable is not set")
    exit(1)

discord_key = os.environ.get("DISCORD_KEY")
interval = int(os.environ.get("REFRESH_INTERVAL", default="300"))

sv = os.environ.get("STRICT_VALIDATION", default="False")
strict_validation = sv in ["true", "True", "TRUE", "1", "yes", "YES", "Yes"]

LOG.info(f"Config interval = {interval} seconds")
LOG.info(f"Config strict validation = {strict_validation}")

config_manager = ConfigManager.from_env_var("BOT_CONFIG")
intents = discord.Intents.default()
client = FloorClient(
    intents=intents,
    config_manager=config_manager,
    interval=interval,
    strict_validation=strict_validation,
)

client.run(discord_key)
