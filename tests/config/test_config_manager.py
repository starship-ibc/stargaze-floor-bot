from unittest import mock
from stargazefloorbot.config import ConfigManager
from stargazefloorbot.config.bot_config import BotConfig

MOCK_ENV = {
    "DISCORD_KEY": "discord-key",
    "REFRESH_INTERVAL": "60",
    "BOT_CONFIG_0_GUILD_ID": "1",
    "BOT_CONFIG_0_CHANNEL_ID": "2",
    "BOT_CONFIG_0_COLLECTION_NAME": "Collection 1",
    "BOT_CONFIG_0_SG721": "stars1",
    "BOT_CONFIG_0_PREFIX": "Cheap=",
    "BOT_CONFIG_1_GUILD_ID": "1",
    "BOT_CONFIG_1_CHANNEL_ID": "2",
    "BOT_CONFIG_1_COLLECTION_NAME": "Collection 2",
    "BOT_CONFIG_1_SG721": "stars2",
}

def get_env_val(*args, **kwargs):
    key = args[0]
    if key not in MOCK_ENV:
        return None
    return MOCK_ENV[key]

def test_config_manager_should_add_config():
    cm = ConfigManager()
    assert len(cm.get_configs()) == 0
    
    config = BotConfig(1, 123, "collection", "stars1")
    cm.add_config(config)
    configs = list(cm.get_configs())
    assert len(configs) == 1
    assert configs[0].guild_id == config.guild_id
    assert configs[0].channel_id == config.channel_id
    assert configs[0].collection_name == config.collection_name
    assert configs[0].sg721 == config.sg721
    assert configs[0].prefix == config.prefix


@mock.patch("os.environ")
def test_config_manager_should_load_from_env(env):
    env.keys.return_value = MOCK_ENV.keys()
    env.get.side_effect = get_env_val
    cm = ConfigManager.from_env_var("BOT_CONFIG")
    configs = list(cm.get_configs())
    assert len(configs) == 2

    assert configs[0].guild_id == int(MOCK_ENV["BOT_CONFIG_0_GUILD_ID"])
    assert configs[0].channel_id == int(MOCK_ENV["BOT_CONFIG_0_CHANNEL_ID"])
    assert configs[0].collection_name == MOCK_ENV["BOT_CONFIG_0_COLLECTION_NAME"]
    assert configs[0].sg721 == MOCK_ENV["BOT_CONFIG_0_SG721"]
    assert configs[0].prefix == MOCK_ENV["BOT_CONFIG_0_PREFIX"]
    assert configs[1].guild_id == int(MOCK_ENV["BOT_CONFIG_1_GUILD_ID"])
    assert configs[1].channel_id == int(MOCK_ENV["BOT_CONFIG_1_CHANNEL_ID"])
    assert configs[1].collection_name == MOCK_ENV["BOT_CONFIG_1_COLLECTION_NAME"]
    assert configs[1].sg721 == MOCK_ENV["BOT_CONFIG_1_SG721"]
