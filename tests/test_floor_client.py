from decimal import Decimal
from datetime import datetime, timedelta
from stargazeutils.coin import Coin
from stargazeutils.market.market_ask import MarketAsk
from stargazefloorbot.floor_client import get_trend_emoji
from stargazefloorbot.floor_client import get_min_ask

FUTURE = datetime.utcnow() + timedelta(25)

def test_get_trend_emoji_should_detect_pump():
    assert get_trend_emoji([5,4,1,2,3]) == "↗️"

def test_get_trend_emoji_should_detect_dump():
    assert get_trend_emoji([3,2,4,6,4]) == "↘️"

def test_get_trend_emoji_should_detect_crab():
    assert get_trend_emoji([1,3,1,3,1]) == "➡️"

def test_get_min_ask():
    asks = {
        "Type1": {
            "Value1": [{'ask': MarketAsk("", 1, "", Coin.from_stars(10), FUTURE)}],
            "Value2": [{'ask': MarketAsk("", 1, "", Coin.from_stars(3), FUTURE)}],
        },
        "Type2": {
            "Value1": [{'ask': MarketAsk("", 1, "", Coin.from_stars(3), FUTURE)}],
            "Value2": [{'ask': MarketAsk("", 1, "", Coin.from_stars(4), FUTURE)}],
            "Value3": [
                {'ask': MarketAsk("", 1, "", Coin.from_stars(2), FUTURE)},
                {'ask': MarketAsk("", 1, "", Coin.from_stars(1), FUTURE)}
            ],
        }
    }
    min_ask = get_min_ask(asks)
    print(min_ask)
    assert min_ask['ask'].price.amount == Decimal('1000000')
