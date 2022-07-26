import base64
import json
import logging
import os
from datetime import datetime

import requests
from stargazeutils.stargaze import QueryMethod
from stargazeutils.stargaze import StargazeClient
from stargazeutils.collection import Sg721Client
from stargazeutils.common import MARKET_CONTRACT
from stargazeutils.market import MarketClient

LOG = logging.getLogger(__name__)
sg_client = StargazeClient(query_method=QueryMethod.REST)
market = MarketClient(MARKET_CONTRACT, sg_client=sg_client)


def fetch_asks(collection):
    query = {
        "asks_sorted_by_price": {
            "collection": collection,
            "include_inactive": False,
            "limit": 25,
        }
    }
    contract = "stars1fvhcnyddukcqfnt7nlwv3thm5we22lyxyxylr9h77cvgkcn43xfsvgv0pl"
    encoded_query = base64.b64encode(json.dumps(query).encode()).decode()
    url = (
        "https://rest.stargaze-apis.com/cosmwasm/wasm/v1/contract/"
        + f"{contract}/smart/{encoded_query}"
    )
    return requests.get(url).json()["data"]["asks"]


def fetch_floor(collection) -> str:
    asks = fetch_asks(collection)
    for ask in asks:
        expiration = datetime.fromtimestamp(int(ask["expires_at"][:10]))
        if expiration > datetime.utcnow():
            return f"{int(ask['price'][:-6]):0,}"
    return "???"


def fetch_trait_asks(collection_name: str, strict_validation: bool = False):
    client = Sg721Client.from_collection_name(collection_name, sg_client)
    if client is None:
        LOG.warning(f"No client found for collection {collection_name}")

    cache_dir = os.path.join(os.curdir, "cache", "collections")
    json_file = collection_name.lower().replace(" ", "-") + ".json"
    json_trait_cache_file = os.path.join(cache_dir, json_file)
    collection = client.fetch_nft_collection(json_trait_cache_file)
    print("Fetching asks for collection")
    asks = market.fetch_asks_for_collection(collection, strict_verify=strict_validation)
    trait_asks = asks.create_asks_by_trait()
    return trait_asks
