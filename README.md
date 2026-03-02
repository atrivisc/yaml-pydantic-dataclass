# yaml-dataclass

A simple Python library for mapping YAML data to Python dataclasses.

## Installation

```bash
pip install yaml-pydantic-dataclass
```

## Usage

```yaml
# config.yaml
app:
  port: 8080
  debug: false
```

```python
from pydantic.dataclasses import dataclass
from yaml_pydantic_dataclass import YamlConfig

@dataclass
class AppConfig(YamlConfig):
    __path__ = "app"
    __config_file__ = "./config.yaml"

    port: int
    debug: bool

if __name__ == '__main__':
    config = AppConfig.read_config()
    print(config.port)  # 8080
    print(config.debug)  # False
```
