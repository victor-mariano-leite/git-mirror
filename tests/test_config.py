import configparser
from pathlib import Path

import pytest

from gitmirror.config import DictConfigProvider, IniConfigProvider


@pytest.fixture
def sample_ini_content():
    return """
[Section1]
key1 = value1
key2 = value2

[Section2]
key3 = value3
"""


@pytest.fixture
def sample_ini_file(tmp_path, sample_ini_content):
    ini_file = tmp_path / "test_config.ini"
    ini_file.write_text(sample_ini_content)
    return str(ini_file)


@pytest.fixture
def sample_dict_config():
    return {
        "Section1": {"key1": "value1", "key2": "value2"},
        "Section2": {"key3": "value3"},
    }


class TestIniConfigProvider:
    def test_initialization(self, sample_ini_file):
        provider = IniConfigProvider(sample_ini_file)
        assert isinstance(provider.config, configparser.ConfigParser)

    def test_get_existing_value(self, sample_ini_file):
        provider = IniConfigProvider(sample_ini_file)
        assert provider.get("Section1", "key1") == "value1"
        assert provider.get("Section2", "key3") == "value3"

    def test_get_non_existing_value(self, sample_ini_file):
        provider = IniConfigProvider(sample_ini_file)
        assert provider.get("Section1", "non_existing", fallback="default") == "default"
        assert (
            provider.get("NonExistingSection", "key", fallback="default") == "default"
        )

    def test_set_existing_value(self, sample_ini_file):
        provider = IniConfigProvider(sample_ini_file)
        provider.set("Section1", "key1", "new_value")
        assert provider.get("Section1", "key1") == "new_value"

    def test_set_new_value(self, sample_ini_file):
        provider = IniConfigProvider(sample_ini_file)
        provider.set("Section1", "new_key", "new_value")
        assert provider.get("Section1", "new_key") == "new_value"

    def test_set_new_section(self, sample_ini_file):
        provider = IniConfigProvider(sample_ini_file)
        provider.set("NewSection", "new_key", "new_value")
        assert provider.get("NewSection", "new_key") == "new_value"


class TestDictConfigProvider:
    def test_initialization(self, sample_dict_config):
        provider = DictConfigProvider(sample_dict_config)
        assert provider.config == sample_dict_config

    def test_get_existing_value(self, sample_dict_config):
        provider = DictConfigProvider(sample_dict_config)
        assert provider.get("Section1", "key1") == "value1"
        assert provider.get("Section2", "key3") == "value3"

    def test_get_non_existing_value(self, sample_dict_config):
        provider = DictConfigProvider(sample_dict_config)
        assert provider.get("Section1", "non_existing", fallback="default") == "default"
        assert (
            provider.get("NonExistingSection", "key", fallback="default") == "default"
        )

    def test_set_existing_value(self, sample_dict_config):
        provider = DictConfigProvider(sample_dict_config)
        provider.set("Section1", "key1", "new_value")
        assert provider.get("Section1", "key1") == "new_value"

    def test_set_new_value(self, sample_dict_config):
        provider = DictConfigProvider(sample_dict_config)
        provider.set("Section1", "new_key", "new_value")
        assert provider.get("Section1", "new_key") == "new_value"

    def test_set_new_section(self, sample_dict_config):
        provider = DictConfigProvider(sample_dict_config)
        provider.set("NewSection", "new_key", "new_value")
        assert provider.get("NewSection", "new_key") == "new_value"


def test_config_provider_interface():
    """Test that both providers implement the same interface"""
    ini_provider = IniConfigProvider("dummy.ini")
    dict_provider = DictConfigProvider({})

    assert hasattr(ini_provider, "get") and callable(getattr(ini_provider, "get"))
    assert hasattr(ini_provider, "set") and callable(getattr(ini_provider, "set"))
    assert hasattr(dict_provider, "get") and callable(getattr(dict_provider, "get"))
    assert hasattr(dict_provider, "set") and callable(getattr(dict_provider, "set"))


if __name__ == "__main__":
    pytest.main()
