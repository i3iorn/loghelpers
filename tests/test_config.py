import os
import pytest
from loghelpers.config import Configuration, Feature

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

def test_default_configuration(default_config):
    assert default_config.log_level == "INFO"
    assert default_config.log_file == "test.log"
    assert default_config.features == Feature.NONE

def test_feature_manager(feature_manager):
    feature_manager.enable(Feature.ALLOW_PROVIDER_OVERWRITE)
    assert feature_manager.is_enabled(Feature.ALLOW_PROVIDER_OVERWRITE)
    feature_manager.disable(Feature.ALLOW_PROVIDER_OVERWRITE)
    assert not feature_manager.is_enabled(Feature.ALLOW_PROVIDER_OVERWRITE)
