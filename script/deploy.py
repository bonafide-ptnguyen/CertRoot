# from src import favorites, favorites_factory
# from moccasin.boa_tools import VyperContract
# from moccasin.config import get_active_network

# def deploy_favorites() -> VyperContract:
#     favorites_contract: VyperContract = favorites.deploy()
#     starting_number: int = favorites_contract.retrieve()
#     print(f"starting number is {starting_number}")

#     favorites_contract.store(77)
#     ending_number = favorites_contract.retrieve()
#     print(f"ending number is {ending_number}")

#     active_network = get_active_network()

#     if active_network.has_explorer():
#         result = active_network.moccasin_verify(favorites_contract)
#         result.wait_for_verification()

#     return favorites_contract

# def deploy_factory(favorites_contract: VyperContract):
#     factory_contract: VyperContract = favorites_factory.deploy(favorites_contract.address)
#     factory_contract.create_favorites_contract()

#     new_favorites_address: str = factory_contract.list_of_favorite_contracts(0)
#     new_favorites_contract: VyperContract = favorites.at(new_favorites_address)
#     new_favorites_contract.store(98)
#     print(f"Stored value is: {new_favorites_contract.retrieve()}")

# def moccasin_main() -> VyperContract:
#     # deploy_favorites()
#     favorites_contract = deploy_favorites()
#     deploy_factory(favorites_contract)

from src import favorites
from moccasin.boa_tools import VyperContract
from moccasin.config import get_active_network


def deploy_favorites() -> VyperContract:
    active_network = get_active_network()
    print("Currently on network: ", active_network.name)

    favorites_contract: VyperContract = favorites.deploy()
    print("Starting favorite number: ", favorites_contract.retrieve())
    favorites_contract.store(77)
    print("Ending favorite number: ", favorites_contract.retrieve())

    if active_network.has_explorer():
        print("Verifying contract on explorer...")
        result = active_network.moccasin_verify(favorites_contract)
        result.wait_for_verification()
    return favorites_contract


def moccasin_main() -> VyperContract:
    return deploy_favorites()