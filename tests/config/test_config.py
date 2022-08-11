from unittest import mock
from stargazefloorbot.config.channel_config import ChannelConfig
from stargazefloorbot.config.collection_config import CollectionConfig
from stargazefloorbot.config.config import Config

def test_config_should_load_defaults():
    yaml_file = "tests/assets/configs/min_config.yaml"
    config = Config.from_yaml(yaml_file)
    assert config.log_level == "INFO"
    assert config.refresh_interval == 300
    assert config.strict_validation is False
    assert len(config.collections) == 1

    c: CollectionConfig = config.collections[0]
    c.sg721 == "stars1"
    c.name is None
    c.enable_trait_query is False
    c.prefix == "Floor: "
    c.refresh_interval == 300
    assert len(c.channels) == 1

    ch: ChannelConfig = c.channels[0]
    assert ch.guild_id == 0
    assert ch.channel_id == 1

def test_config_should_override():
    yaml_file = "tests/assets/configs/test_config.yaml"
    config = Config.from_yaml(yaml_file)
    assert config.log_level == "DEBUG"
    assert config.refresh_interval == 30
    assert config.strict_validation is False

    assert len(config.collections) == 2

    c: CollectionConfig = config.collections[0]
    c.sg721 == "stars1"
    c.name == "C1"
    c.enable_trait_query is True
    c.strict_validation is False
    c.prefix == "Test: "
    c.refresh_interval == 30
    assert len(c.channels) == 2
    assert c.channels[0].guild_id == 0
    assert c.channels[0].channel_id == 1
    assert c.channels[1].guild_id == 2
    assert c.channels[1].channel_id == 3

    c: CollectionConfig = config.collections[1]
    c.sg721 == "stars2"
    c.name == "stars2"
    c.enable_trait_query is False
    c.strict_validation is True
    c.prefix == "Test2: "
    c.refresh_interval == 6000
    assert len(c.channels) == 2
    assert c.channels[0].guild_id == 0
    assert c.channels[0].channel_id == 4
    assert c.channels[1].guild_id == 2
    assert c.channels[1].channel_id == 5
