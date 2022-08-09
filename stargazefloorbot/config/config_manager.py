import logging
import os
from typing import List

from .bot_config import BotConfig

LOG = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self):
        self._configs = {}

    def add_config(self, config: BotConfig):
        self._configs[config.key] = config
        LOG.info(f"Config loaded for guild: {config.guild_id}")
        LOG.info(f" Channel Id: {config.channel_id}")
        LOG.info(f" Collection Name: {config.collection_name}")
        LOG.info(f" Collection SG721: {config.sg721}")
        LOG.info(f" Prefix: '{config.prefix}'")

    def get_configs(self) -> List[BotConfig]:
        return self._configs.values()

    @classmethod
    def from_env_var(cls, base_env_var):
        LOG.info(f"Loading configuration from environment {base_env_var}")

        def load_config(i):
            guild_id = int(os.environ.get(f"{base_env_var}_{i}_GUILD_ID"))
            channel_id = int(os.environ.get(f"{base_env_var}_{i}_CHANNEL_ID"))
            collection_name = os.environ.get(f"{base_env_var}_{i}_COLLECTION_NAME")
            sg721 = os.environ.get(f"{base_env_var}_{i}_SG721")
            prefix = os.environ.get(f"{base_env_var}_{i}_PREFIX", "Floor: ")
            return BotConfig(guild_id, channel_id, collection_name, sg721, prefix)

        i = 0
        config_manager = cls()
        while f"{base_env_var}_{i}_SG721" in os.environ.keys():
            config_manager.add_config(load_config(i))
            i += 1

        return config_manager
