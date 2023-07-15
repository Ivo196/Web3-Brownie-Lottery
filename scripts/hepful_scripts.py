from brownie import (
    network,
    config,
    accounts,
    Contract,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)

DECIMALS = 8
STARTING_PRICE = 200000000000

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIROMENTS = ["mainnet-fork", "mainnet-fork-dev"]

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_account(id=None, index=None):
    if id:
        return accounts.load(id)
    if index:
        return accounts[index]
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIROMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """
    Take contract address from brownie-config, if is defined. but oposite use Mocks of this contract
    Args:
        contact_name (string)
    Returns:
        brownie.network.contract.ProjectContract: The latest version of the contract
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        # MockV3Aggregator[-1] is the last deploy of MockV3Aggregator
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks():
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Mocks deployed")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    #### Using the interface ####
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    ####
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Contract Funded!")
    return tx
