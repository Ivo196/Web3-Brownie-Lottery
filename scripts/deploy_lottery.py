from brownie import Lottery, config, network
from scripts.hepful_scripts import get_account, get_contract, fund_with_link
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Lottery deploy")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_txt = lottery.startLottery({"from": account})
    starting_txt.wait(1)
    print("Lottery Started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("Enter Lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    # ending_transaction = lottery.endLottery({"from": account})
    # ending_transaction = lottery.endLottery({"from": account, "gas_limit": 300000})
    ending_transaction = lottery.endLottery(
        {"from": account, "gas_limit": 6500000, "allow_revert": True}
    )
    ending_transaction.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new Winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
