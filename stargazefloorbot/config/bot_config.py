class BotConfig:
    def __init__(
        self,
        guild_id: str,
        channel_id: str,
        collection_name: str,
        sg721: str,
        prefix: str = "Floor: ",
    ):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.collection_name = collection_name
        self.sg721 = sg721
        self.prefix = prefix

    @property
    def key(self) -> str:
        return f"{self.guild_id}-{self.sg721}"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["guild_id"],
            data["channel_id"],
            data["collection_name"],
            data["sg721"],
            data["prefix"],
        )
