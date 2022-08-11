import logging
from typing import List

from .channel_config import ChannelConfig

LOG = logging.getLogger(__name__)


class CollectionConfig:
    def __init__(self, sg721: str, refresh_interval: int, strict_validation: bool):
        self.sg721 = sg721
        self.name = sg721
        self.channels: List[ChannelConfig] = []
        self.prefix = "Floor: "
        self.refresh_interval = refresh_interval
        self.enable_trait_query = True
        self.strict_validation = strict_validation
        LOG.info(f"Collection {self.sg721}")

    def __str__(self):
        return self.name

    def _set_value(self, key, values):
        if key in values:
            self.__dict__[key] = values[key]
        LOG.info(f"- {key} = {self.__dict__[key]}")

    @classmethod
    def from_dict(cls, d, refresh_interval: int, strict_validation: bool):
        config = CollectionConfig(d["sg721"], refresh_interval, strict_validation)
        config._set_value("name", d)
        config._set_value("prefix", d)
        config._set_value("refresh_interval", d)
        config._set_value("enable_trait_query", d)
        config._set_value("strict_validation", d)
        config.channels = [ChannelConfig.from_dict(c) for c in d["channels"]]
        return config
