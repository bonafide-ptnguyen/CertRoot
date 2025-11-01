import warnings
import pytest

# Suppress all deprecation warnings from websockets
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*websockets.*")

# Also add pytest option to not show warnings summary
def pytest_configure(config):
    config.option.disable_warnings = True