import pytest
from pydantic.dataclasses import dataclass
from yaml_dataclass import YamlConfig, YamlConfigCached

@dataclass
class Person(YamlConfig):
    name: str
    age: int

@dataclass
class AppConfig(YamlConfig):
    __path__ = "app"
    port: int
    debug: bool

@dataclass
class EnvConfig(YamlConfig):
    user: str

def test_parse_config_basic():
    yaml_str = "name: Alice\nage: 30"
    person = Person.parse_config(yaml_str)
    assert person.name == "Alice"
    assert person.age == 30

def test_parse_config_with_path():
    yaml_str = """
app:
  port: 8080
  debug: true
other:
  key: value
"""
    config = AppConfig.parse_config(yaml_str)
    assert config.port == 8080
    assert config.debug is True

def test_parse_config_with_jinja2(monkeypatch):
    monkeypatch.setenv("APP_USER", "testuser")
    yaml_str = "user: {{ env.APP_USER }}"
    config = EnvConfig.parse_config(yaml_str)
    assert config.user == "testuser"

def test_load_from_file(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("name: Bob\nage: 25")
    
    @dataclass
    class Bob(YamlConfig):
        __config_file__ = str(config_file)
        name: str
        age: int
        
    bob = Bob.read_config()
    assert bob.name == "Bob"
    assert bob.age == 25

def test_cached_config(tmp_path):
    config_file = tmp_path / "cached_config.yaml"
    config_file.write_text("name: Charlie\nage: 40")
    
    @dataclass
    class Charlie(YamlConfigCached):
        __config_file__ = str(config_file)
        name: str
        age: int
    
    c1 = Charlie.read_config()
    assert c1.name == "Charlie"
    
    config_file.write_text("name: Dave\nage: 45")
    
    c2 = Charlie.read_config()
    assert c2.name == "Charlie"
    
    assert id(Charlie.__ttl_cache__[str(config_file)]) == id(Charlie.read_config())

def test_load_file_not_found():
    @dataclass
    class NonExistent(YamlConfig):
        __config_file__ = "non_existent_file.yaml"
        name: str

    with pytest.raises(FileNotFoundError):
        NonExistent.read_config()

def test_parse_config_invalid_path():
    yaml_str = "key: value"
    @dataclass
    class WrongPath(YamlConfig):
        __path__ = "nested.missing"
        name: str
    
    with pytest.raises(ValueError, match="Path 'nested.missing' not found in YAML content"):
        WrongPath.parse_config(yaml_str)

def test_parse_config_not_dict():
    yaml_str = "app: not_a_dict"
    with pytest.raises(ValueError, match="YAML content at path 'app' must be a dictionary"):
        AppConfig.parse_config(yaml_str)
