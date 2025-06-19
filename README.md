# LogHelpers

LogHelpers is a Python library for managing logging configurations, dynamic feature flags, and contextual logging in a structured and extensible way.

## Features
- Centralized logging configuration
- Dynamic feature flags
- Contextual logging with thread-local storage
- Pluggable log formatters
- Configuration validation

## Installation
```bash
pip install loghelpers
```

## Usage

### Centralized Logging
```python
from loghelpers.config import Configuration
from loghelpers.handlers import setup_logging

config = Configuration(log_level="DEBUG", log_file="app.log")
setup_logging(config)
```

### Dynamic Feature Flags
```python
from loghelpers.config import Configuration, Feature

config = Configuration(features=Feature.NONE)
feature_manager = FeatureManager(config)

feature_manager.enable(Feature.ALLOW_PROVIDER_OVERWRITE)
print(feature_manager.is_enabled(Feature.ALLOW_PROVIDER_OVERWRITE))  # True
```

### Configuration Validation
```python
from loghelpers.config import Configuration

config = Configuration(log_level="INVALID")
try:
    config.validate()
except ValueError as e:
    print(f"Validation error: {e}")
```

### Pluggable Formatters

```python

from loghelpers.utils import load_formatter
from loghelpers.config import Configuration

config = Configuration(log_format="%(message)s")
formatter = load_formatter("JsonFormatter", config)
print(formatter)
```

### Contextual Logging

```python

from loghelpers.context import LoggingContext

LoggingContext.set_context(user_id="12345", request_id="abcde")
print(LoggingContext.get_context())
LoggingContext.clear_context()
```
