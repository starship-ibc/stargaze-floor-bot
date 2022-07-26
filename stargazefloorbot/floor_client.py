import asyncio
import logging

import discord

# from .stargaze import fetch_floor
from discord import app_commands

from stargazefloorbot.floor_flow import FloorFlow

from .config import ConfigManager
from .stargaze import fetch_floor, fetch_trait_asks

LOG = logging.getLogger(__name__)


class FloorClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager: ConfigManager = kwargs["config_manager"]
        self.interval = kwargs["interval"]
        self.strict_validation = kwargs["strict_validation"]
        self.latest_asks = {}
        self.floors = {}

        self.tree = app_commands.CommandTree(self)

        list_collections_cmd = discord.app_commands.Command(
            name="listcollections",
            description="List tracked Stargaze collections with their floor price",
            callback=self.list_collections,
        )
        self.tree.add_command(list_collections_cmd)

        query_floor_cmd = discord.app_commands.Command(
            name="querytraitfloor",
            description="Query the floor pricing for a specific trait",
            callback=self.query_trait_floor,
        )
        self.tree.add_command(query_floor_cmd)

    async def setup_hook(self) -> None:
        # create the background task and run it in the background
        # self.tree.copy_global_to(guild=MY_GUILD)
        for config in self.config_manager.get_configs():
            guild = discord.Object(config.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        self.bg_task = self.loop.create_task(self.track_floor_pricing())

    async def on_ready(self):
        LOG.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def update_floor(self):
        for config in self.config_manager.get_configs():
            guild = await self.fetch_guild(config.guild_id)
            channels = {c.id: c for c in await guild.fetch_channels()}
            channel = channels[config.channel_id]
            floor = fetch_floor(config.sg721)
            self.floors[config.collection_name] = floor
            LOG.info(f"Updating floor for {config.sg721} to {floor}")
            await channel.edit(name=f"{config.prefix}{floor}")

    async def update_asks(self):
        for config in self.config_manager.get_configs():
            LOG.info(f"Updating asks for '{config.collection_name}'")
            self.latest_asks[config.collection_name] = fetch_trait_asks(
                config.collection_name,
                self.strict_validation
            )
            LOG.info(f"Finished updating asks for '{config.collection_name}'")

    async def track_floor_pricing(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await self.update_floor()
            await self.update_asks()
            await asyncio.sleep(self.interval)  # task runs every 60 seconds

    async def list_collections(self, interaction: discord.Interaction):
        """List the currently tracked collections."""
        message = "**Tracked collections**\n"
        for collection, floor in self.floors.items():
            message += f"- {collection}: ({floor} $STARS)\n"
        await interaction.response.send_message(message)

    async def query_trait_floor(
        self,
        interaction: discord.Interaction,
    ):
        floor_flow = FloorFlow(self.latest_asks)
        await floor_flow.start(interaction)
