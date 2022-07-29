import asyncio
import logging
from typing import List

import discord

from stargazefloorbot.floor_flow import FloorFlow

from .config import ConfigManager
from .stargaze import fetch_trait_asks

LOG = logging.getLogger(__name__)


def get_trend_emoji(x: List[int]) -> str:
    if x[0] > x[-1]:
        return "↗️"
    elif x[0] == x[-1]:
        return "➡️"
    return "↘️"


def get_min_ask(trait_asks: dict):
    def asking_price(x):
        return x["ask"].price.amount

    return min(
        (
            [
                min(
                    [v[0] for v in t.values()],
                    key=asking_price,
                )
                for t in trait_asks.values()
            ]
        ),
        key=asking_price,
    )


class FloorClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager: ConfigManager = kwargs["config_manager"]
        self.interval = kwargs["interval"]
        self.strict_validation = kwargs["strict_validation"]
        self.latest_asks = {}
        self.floors = {}

        for config in self.config_manager.get_configs():
            self.floors[config.collection_name] = [0, 0, 0, 0, 0]

        self.tree = discord.app_commands.CommandTree(self)

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
            floor_history = self.floors[config.collection_name]
            floor = floor_history[0]
            trend_emoji = get_trend_emoji(floor_history)
            LOG.info(f"{config.collection_name} history: {floor_history}")
            await channel.edit(name=f"{config.prefix}{floor:,} {trend_emoji}")

    async def update_asks(self):
        for config in self.config_manager.get_configs():
            LOG.info(f"Updating asks for '{config.collection_name}'")
            trait_asks = fetch_trait_asks(
                config.collection_name, self.strict_validation
            )
            collection_floor = get_min_ask(trait_asks)

            self.latest_asks[config.collection_name] = trait_asks
            new_floor = collection_floor["ask"].price.get_stars()
            self.floors[config.collection_name].insert(0, new_floor)
            self.floors[config.collection_name].pop()
            LOG.info(f"Finished updating asks for '{config.collection_name}'")

    async def track_floor_pricing(self):
        await self.wait_until_ready()
        print("ready")
        while not self.is_closed():
            await self.update_asks()
            await self.update_floor()
            await asyncio.sleep(self.interval)  # task runs every 60 seconds

    async def list_collections(self, interaction: discord.Interaction):
        """List the currently tracked collections."""
        message = "**Tracked collections**\n"
        for collection, floor in self.floors.items():
            message += f"- {collection}: ({floor[0]:,} $STARS)\n"
        await interaction.response.send_message(message)

    async def query_trait_floor(
        self,
        interaction: discord.Interaction,
    ):
        floor_flow = FloorFlow(self.latest_asks)
        await floor_flow.start(interaction)
