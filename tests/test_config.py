import logging
import os
import pytest
from loghelpers.config import Configuration, Feature
from loghelpers.exceptions import UnsupportedConfigurationFormatException


@pytest.fixture
def default_config():
    return Configuration(
        log_level="INFO",
        log_file="test.log",
        log_format="%(message)s",
        features=Feature.NONE
    )

@pytest.fixture
def feature_manager(default_config):
    from loghelpers.config import FeatureManager
    return FeatureManager(default_config)

def test_update_log_level_changes_logging_level(default_config):
    default_config.update_log_level("DEBUG")
    assert default_config.log_level == "DEBUG"
    assert logging.getLogger().level == logging.DEBUG

def test_update_sample_rate_changes_value(default_config):
    default_config.update_sample_rate(0.5)
    assert default_config.sample_rate == 0.5

def test_update_sensitive_keys_changes_set(default_config):
    new_keys = {"api_key", "auth_token"}
    default_config.update_sensitive_keys(new_keys)
    assert default_config.sensitive_keys == new_keys

def test_from_file_loads_valid_json_configuration(tmp_path, default_config):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"log_level": "DEBUG", "sample_rate": 0.8}')
    default_config.from_file(str(config_file))
    assert default_config.log_level == "DEBUG"
    assert default_config.sample_rate == 0.8

def test_from_file_raises_exception_for_invalid_format(tmp_path, default_config):
    config_file = tmp_path / "config.invalid"
    config_file.write_text("invalid content")
    with pytest.raises(UnsupportedConfigurationFormatException):
        default_config.from_file(str(config_file))

def test_validate_raises_exception_for_invalid_sample_rate(default_config):
    default_config.update_sample_rate(1.5)
    with pytest.raises(ValueError):
        default_config.validate()

def test_validate_raises_exception_for_invalid_sensitive_keys(default_config):
    with pytest.raises(ValueError):
        default_config.update_sensitive_keys(["not_a_set"])

def test_feature_manager_enables_and_disables_features(feature_manager):
    feature_manager.enable(Feature.ALLOW_PROVIDER_OVERWRITE)
    assert feature_manager.is_enabled(Feature.ALLOW_PROVIDER_OVERWRITE)
    feature_manager.disable(Feature.ALLOW_PROVIDER_OVERWRITE)
    assert not feature_manager.is_enabled(Feature.ALLOW_PROVIDER_OVERWRITE)
