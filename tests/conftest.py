from script.deploy import deploy_favorites
import pytest

@pytest.fixture(scope="session")
def favorites_contract():
    return deploy_favorites()