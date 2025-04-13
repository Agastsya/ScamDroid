from solcx import compile_source, install_solc, set_solc_version
from web3 import Web3
import time

# Install and set Solidity compiler version (only need to install once)
try:
    set_solc_version('0.8.0')
except:
    install_solc('0.8.0')
    set_solc_version('0.8.0')

# Solidity contract source code
contract_source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LogStorage {
    string[] public logs;

    function storeLog(string memory log) public {
        logs.push(log);
    }

    function getLogs() public view returns (string[] memory) {
        return logs;
    }
}
"""

def main():
    # Compile the contract
    compiled_sol = compile_source(contract_source)
    contract_interface = compiled_sol["<stdin>:LogStorage"]

    # Connect to Ganache (make sure it's running!)
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    
    # Check connection
    if not w3.is_connected():
        print("❌ Failed to connect to Ethereum node. Make sure Ganache is running!")
        print("👉 Is Ganache running? Default RPC URL: http://127.0.0.1:7545")
        return

    print("✅ Successfully connected to Ganache")

    # Set default account (use first account from Ganache)
    w3.eth.default_account = w3.eth.accounts[0]
    print(f"Using account: {w3.eth.default_account}")

    # Create contract factory
    LogStorage = w3.eth.contract(
        abi=contract_interface["abi"],
        bytecode=contract_interface["bin"]
    )

    # Deploy the contract
    print("Deploying contract...")
    tx_hash = LogStorage.constructor().transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    print(f"✅ Contract deployed at address: {contract_address}")

    # Interact with the deployed contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_interface["abi"]
    )

    # Store a log
    print("Storing a log message...")
    tx_hash = contract.functions.storeLog("First log entry").transact()
    w3.eth.wait_for_transaction_receipt(tx_hash)

    # Retrieve logs
    print("Retrieving logs...")
    logs = contract.functions.getLogs().call()
    print("📜 Current logs:", logs)

if __name__ == "__main__":
    main()
