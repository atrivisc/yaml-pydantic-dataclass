import io
import os
import yaml
from typing import ClassVar, Any
from cachetools import TTLCache
from abc import ABCMeta
from pydantic.dataclasses import dataclass
from jinja2 import Template

@dataclass
class YamlConfig(metaclass=ABCMeta):
    __path__: ClassVar[str] = ""
    __config_dir__: ClassVar[str] = ""
    __config_file__: ClassVar[str] = ""

    @classmethod
    def parse_config(cls, config_stream: io.StringIO | str) -> 'Self':
        if isinstance(config_stream, str):
            config_stream = io.StringIO(config_stream)

        jinja2_parsed_config = Template(config_stream.read()).render(env=os.environ)
        loaded = yaml.safe_load(jinja2_parsed_config)

        if cls.__path__:
            for part in cls.__path__.split('.'):
                if isinstance(loaded, dict) and part in loaded:
                    loaded = loaded[part]
                else:
                    raise ValueError(f"Path '{cls.__path__}' not found in YAML content")

        if not isinstance(loaded, dict):
            raise ValueError(f"YAML content at path '{cls.__path__}' must be a dictionary")

        return cls(**loaded)

    @classmethod
    def read_config(cls, config_path: str = None) -> Any:
        if config_path is None:
            config_path = cls.__config_file__

        with open(config_path, 'r') as config_file:
            return cls.parse_config(config_file)

@dataclass
class YamlConfigCached(YamlConfig):
    __ttl_cache__: ClassVar[TTLCache] = TTLCache(maxsize=5, ttl=10)

    @classmethod
    def read_config(cls, config_path: str = None) -> Any:
        if config_path is None:
            config_path = cls.__config_file__

        if not cls.__ttl_cache__.get(config_path):
            with open(config_path, 'r') as config_file:
                cls.__ttl_cache__[config_path] = cls.parse_config(config_file)

        return cls.__ttl_cache__[config_path]
