import logging

LOG = logging.getLogger(__name__)


class ChannelConfig:
    def __init__(self, guild_id: int, channel_id: int):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.guild = None
        self.channel = None
        LOG.info(f"  - guild: {self.guild_id}")
        LOG.info(f"    channel: {self.channel_id}")

    @classmethod
    def from_dict(cls, d):
        return cls(d["guild_id"], d["channel_id"])
