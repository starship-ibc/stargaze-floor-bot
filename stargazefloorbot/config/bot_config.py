class BotConfig:
    def __init__(
        self,
        guild_id: int,
        channel_id: int,
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
