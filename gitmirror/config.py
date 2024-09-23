"""
Configuration module for Git Mirror.

This module provides abstract and concrete classes for handling
configuration data. It supports both INI-style configuration files
and dictionary-based configuration.
"""

from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import Any, Dict


class ConfigProvider(ABC):
    """
    Abstract base class for configuration providers.

    This class defines the interface for configuration providers,
    allowing for different types of configuration sources to be used.
    """

    @abstractmethod
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """
        Get a configuration value.

        Parameters
        ----------
        section : str
            The section name in the configuration.
        key : str
            The key name within the section.
        fallback : Any, optional
            The fallback value if the key is not found.

        Returns
        -------
        Any
            The configuration value if found, otherwise the fallback value.
        """
        pass

    @abstractmethod
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Parameters
        ----------
        section : str
            The section name in the configuration.
        key : str
            The key name within the section.
        value : Any
            The value to set.
        """
        pass


class IniConfigProvider(ConfigProvider):
    """
    Configuration provider that reads from an INI file.

    This class implements the ConfigProvider interface for INI-style
    configuration files.
    """

    def __init__(self, config_file: str):
        """
        Initialize the IniConfigProvider.

        Parameters
        ----------
        config_file : str
            Path to the INI configuration file.
        """
        self.config = ConfigParser()
        self.config.read(config_file)

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """
        Get a configuration value from the INI file.

        Parameters
        ----------
        section : str
            The section name in the INI file.
        key : str
            The key name within the section.
        fallback : Any, optional
            The fallback value if the key is not found.

        Returns
        -------
        Any
            The configuration value if found, otherwise the fallback value.
        """
        return self.config.get(section, key, fallback=fallback)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value in the INI file.

        Parameters
        ----------
        section : str
            The section name in the INI file.
        key : str
            The key name within the section.
        value : Any
            The value to set.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))


class DictConfigProvider(ConfigProvider):
    """
    Configuration provider that uses a dictionary.

    This class implements the ConfigProvider interface for dictionary-based
    configuration.
    """

    def __init__(self, config_dict: Dict[str, Dict[str, Any]]):
        """
        Initialize the DictConfigProvider.

        Parameters
        ----------
        config_dict : Dict[str, Dict[str, Any]]
            A dictionary containing the configuration data.
            The outer dictionary keys are section names, and the inner
            dictionary keys are option names.
        """
        self.config = config_dict

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """
        Get a configuration value from the dictionary.

        Parameters
        ----------
        section : str
            The section name in the configuration.
        key : str
            The key name within the section.
        fallback : Any, optional
            The fallback value if the key is not found.

        Returns
        -------
        Any
            The configuration value if found, otherwise the fallback value.
        """
        return self.config.get(section, {}).get(key, fallback)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value in the dictionary.

        Parameters
        ----------
        section : str
            The section name in the configuration.
        key : str
            The key name within the section.
        value : Any
            The value to set.
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
