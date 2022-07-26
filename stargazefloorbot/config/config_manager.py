import json
import logging
from typing import List

from .bot_config import BotConfig

LOG = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self):
        self._configs = {}

    def add_config(self, config: BotConfig):
        self._configs[config.key] = config

    def remove_config(self, guild_id: int, collection: str) -> BotConfig:
        key = BotConfig(guild_id, None, collection).key
        if key in self._configs:
            return self._configs.pop(key)
        return None

    def get_configs(self) -> List[BotConfig]:
        return self._configs.values()

    def get_configs_for_guild(self, guild: int) -> List[BotConfig]:
        return list(filter(lambda x: x.guild_id == guild, self._configs.values()))

    @classmethod
    def from_json_file(cls, filename):
        LOG.info(f"Loading configuration from {filename}")
        with open(filename) as f:
            configs = json.load(f)
        config_manager = cls()
        for config_data in configs:
            config = BotConfig.from_dict(config_data)
            LOG.info(f"Config loaded for guild: {config.guild_id}")
            LOG.info(f" Channel Id: {config.channel_id}")
            LOG.info(f" Collection SG721: {config.sg721}")
            LOG.info(f" Prefix: '{config.prefix}'")
            config_manager.add_config(config)
        return config_manager
