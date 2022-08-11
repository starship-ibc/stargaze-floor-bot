import asyncio
import logging
from typing import List

import discord
from discord import ActivityType

from stargazefloorbot.config.collection_config import CollectionConfig
from stargazefloorbot.floor_flow import FloorFlow

from .config import Config
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
        [
            min(
                [
                    min(value_asks, key=asking_price)
                    for value_asks in trait_value.values()
                ],
                key=asking_price,
            )
            for trait_value in trait_asks.values()
        ],
        key=asking_price,
    )


class FloorClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config: Config = kwargs["config"]
        self.latest_asks = {}
        self.floors = {}

        for c in self.config.collections:
            self.floors[c.name] = [0, 0, 0, 0, 0]

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
        guild_ids = set()
        for c in self.config.collections:
            for channel in c.channels:
                guild_ids.add(channel.guild_id)

        for guild_id in guild_ids:
            guild = discord.Object(guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        LOG.info(f"Logged in as {self.user} (ID: {self.user.id})")

        # We're going to pre-fetch the guild and channel objects
        # so we don't get rate-limited as much.
        guilds = {}
        guild_channels = {}
        for collection in self.config.collections:
            for channel in collection.channels:
                if channel.guild_id not in guilds:
                    guilds[channel.guild_id] = await self.fetch_guild(channel.guild_id)
                channel.guild = guilds[channel.guild_id]

                if channel.guild_id not in guild_channels:
                    guild_channels[channel.guild_id] = {
                        c.id: c for c in await channel.guild.fetch_channels()
                    }
                channel.channel = guild_channels[channel.guild_id][channel.channel_id]

        self.bg_tasks = []
        for collection in self.config.collections:
            task = self.loop.create_task(self.track_floor_pricing(collection))
            self.bg_tasks.append(task)

    async def update_floor(self, collection: CollectionConfig):
        name = collection.name
        floor_history = self.floors[name]
        floor = floor_history[0]
        trend_emoji = get_trend_emoji(floor_history)

        LOG.info(f"{name} history: {[str(x) for x in floor_history]}")
        for ch in collection.channels:
            await ch.channel.edit(name=f"{collection.prefix}{floor:,} {trend_emoji}")

    async def update_asks(self, collection: CollectionConfig):
        name = collection.name
        activity = discord.Activity(type=ActivityType.watching, name="the stars 🌌🔭")
        await self.change_presence(activity=activity)

        LOG.info(f"Updating asks for '{name}'")
        trait_asks = fetch_trait_asks(name, collection.strict_validation)
        collection_floor = get_min_ask(trait_asks)

        if collection.enable_trait_query:
            self.latest_asks[name] = trait_asks
        new_floor = collection_floor["ask"].price.get_stars()
        self.floors[name].insert(0, new_floor)
        self.floors[name].pop()
        LOG.info(f"Finished updating asks for '{name}'")

        await self.change_presence(activity=None)

    async def track_floor_pricing(self, collection: CollectionConfig):
        interval = collection.refresh_interval

        while True:
            await self.update_asks(collection)
            LOG.info("Waiting until ready...")
            await self.wait_until_ready()
            await self.update_floor(collection)
            LOG.info(f"Refreshing {collection.name} in {interval} seconds")
            await asyncio.sleep(interval)

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
