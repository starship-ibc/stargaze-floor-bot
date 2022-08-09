import logging
import os

from stargazeutils.collection import Sg721Client
from stargazeutils.common import DEFAULT_MARKET_CONTRACT
from stargazeutils.market import MarketClient
from stargazeutils.stargaze import QueryMethod, StargazeClient

LOG = logging.getLogger(__name__)
sg_client = StargazeClient(query_method=QueryMethod.REST)
market = MarketClient(DEFAULT_MARKET_CONTRACT, sg_client=sg_client)


def fetch_trait_asks(collection_name: str, strict_validation: bool = False):
    client = Sg721Client.from_collection_name(collection_name, sg_client)
    if client is None:
        LOG.warning(f"No client found for collection {collection_name}")

    cache_dir = os.path.join(os.curdir, "cache", "collections")
    json_file = collection_name.lower().replace(" ", "-") + ".json"
    json_trait_cache_file = os.path.join(cache_dir, json_file)
    collection = client.fetch_nft_collection(json_trait_cache_file)
    LOG.info(f"Fetching asks for {collection_name}")
    asks = market.fetch_asks_for_collection(collection, strict_verify=strict_validation)
    trait_asks = asks.create_asks_by_trait()
    return trait_asks
