import logging

import discord
from stargazeutils.ipfs import IpfsClient

LOG = logging.getLogger(__name__)


class FloorFlow:
    def __init__(self, asks, ipfs_client: IpfsClient = None):
        self.asks = asks
        self.collection_name = None
        self.trait_name = None
        self.trait_value = None
        self.ipfs = ipfs_client or IpfsClient()

    async def start(self, interaction: discord.Interaction):
        collection_names = list(self.asks.keys())

        if len(collection_names) == 1:
            LOG.debug("Only one collection found. Proceeding to trait name selection")
            self.collection_name = collection_names[0]
            await self.select_trait_name(interaction)
            return

        LOG.debug("Creating collection selection response")
        placeholder = "Select a collection"
        options = [
            discord.SelectOption(label=c.replace("_", " "), value=c)
            for c in collection_names
        ]
        dropdown = discord.ui.Select(placeholder=placeholder, options=options)
        dropdown.callback = self.on_collection_selected

        view = discord.ui.View()
        view.add_item(dropdown)

        title = f"{len(collection_names)} collections supported"
        await interaction.response.send_message(content=title, view=view)

    async def on_collection_selected(self, interaction: discord.Interaction):
        self.collection_name = interaction.data["values"][0]
        await self.select_trait_name(interaction)

    async def select_trait_name(self, interaction: discord.Interaction):
        LOG.info(f"Creating trait name selection for '{self.collection_name}'")
        collection_asks = self.asks[self.collection_name]
        num_traits = len(collection_asks.keys())

        placeholder = f"Select a trait from {self.collection_name}"
        trait_names = sorted(list(collection_asks.keys()))
        options = [
            discord.SelectOption(label=t.replace("_", " "), value=t)
            for t in trait_names
        ]

        dropdown = discord.ui.Select(placeholder=placeholder, options=options)
        dropdown.callback = self.on_trait_name_selected

        view = discord.ui.View()
        view.add_item(dropdown)

        title = f"Found {num_traits} {self.collection_name} traits with listings"
        if interaction.message is None:
            await interaction.response.send_message(content=title, view=view)
        else:
            await interaction.response.defer()
            await interaction.message.edit(content=title, view=view)

    async def on_trait_name_selected(self, interaction: discord.Interaction):
        self.trait_name = interaction.data["values"][0]
        await self.select_trait_value(interaction)

    async def select_trait_value(self, interaction: discord.Interaction, page: int = 0):
        LOG.info(
            "Creating trait value selection for "
            f"{self.collection_name} > {self.trait_name} (page {page})"
        )
        trait_asks = self.asks[self.collection_name][self.trait_name]
        start = page * 25
        values = sorted(list(trait_asks.keys()))
        num_values = len(values)

        placeholder = f"Select a value for {self.collection_name} {self.trait_name}"
        options = [discord.SelectOption(label=v) for v in values[start : start + 25]]
        dropdown = discord.ui.Select(placeholder=placeholder, options=options)
        dropdown.callback = self.on_trait_value_selected

        view = discord.ui.View()
        view.add_item(dropdown)

        if num_values > 25:
            back_button = discord.ui.Button(label="Back", disabled=(page == 0))
            back_button.callback = lambda i: self.select_trait_value(i, page - 1)

            next_button = discord.ui.Button(
                label="Next", disabled=((page + 1) * 25 > num_values)
            )
            next_button.callback = lambda i: self.select_trait_value(i, page + 1)

            view.add_item(back_button)
            view.add_item(next_button)

        await interaction.response.defer()
        title = (
            f"Found {num_values} {self.collection_name} {self.trait_name} "
            "values with listings"
        )
        await interaction.message.edit(content=title, view=view)

    async def on_trait_value_selected(self, interaction: discord.Interaction):
        self.trait_value = interaction.data["values"][0]
        embeds = self.get_floor_embeds()
        await interaction.response.defer()
        await interaction.message.edit(embeds=embeds, content=None, view=None)

    def get_floor_embeds(self):
        LOG.info(
            "Getting floor pricing for "
            f"{self.collection_name} > {self.trait_name} > {self.trait_value}"
        )
        message = f"**{self.collection_name}**\n"
        asks = self.asks[self.collection_name][self.trait_name][self.trait_value]
        message += (
            f"{len(asks)} active listings for {self.trait_value} {self.trait_name}\n"
        )

        embeds = []
        embed = discord.Embed(title=f"{self.collection_name} listings")
        embed.add_field(name="Trait name", value=self.trait_name)
        embed.add_field(name="Trait value", value=self.trait_value)
        embed.add_field(name="Listings", value=len(asks))

        hubble_name = self.collection_name.lower().replace(" ", "-")
        hubble_params = (
            f"?sort=ask_price"
            f"&trait-name={self.trait_name}"
            f"&trait-value={self.trait_value}"
        )
        hubble_url = (
            f"https://www.hubble.tools/collections/{hubble_name}{hubble_params}"
        )
        embed.add_field(name="See all", value=f"[Hubble link]({hubble_url})")

        embeds.append(embed)

        for ask_data in asks[:3]:
            ask = ask_data["ask"]
            info = ask_data["token_info"]
            buy_url = (
                f"https://app.stargaze.zone/marketplace/{ask.collection}/{ask.token_id}"
            )

            embed = discord.Embed(title=f"{self.collection_name} {ask.token_id}")
            embed.description = f"[[Buy for {ask.price}]]({buy_url})"
            image_url = self.ipfs.ipfs_to_http(info["image"])
            embed.set_image(url=image_url)

            for trait, value in info.items():
                if trait not in ["image", "name", "id"]:
                    embed.add_field(name=trait, value=value, inline=True)

            embeds.append(embed)

        return embeds
