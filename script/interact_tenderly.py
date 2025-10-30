from src import favorites
from moccasin.boa_tools import VyperContract
from moccasin.config import get_active_network

def deploy_favorites() -> VyperContract:
    active_network = get_active_network()

    # previously deployed on tenderly at 
    favorites_contract: VyperContract = favorites.at("0x2C38Ab9EA520723719ad24AbFB871c9367c60082")
    starting_number: int = favorites_contract.retrieve()
    print(f"starting number is {starting_number}")

    return favorites_contract

def moccasin_main() -> VyperContract:
    deploy_favorites()