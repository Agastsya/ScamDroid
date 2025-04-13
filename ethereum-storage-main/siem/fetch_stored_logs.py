from web3 import Web3

def fetch_stored_logs(contract_address, contract_abi):
    """
    Fetch and display all logs stored in the LogStorage smart contract.
    
    Args:
        contract_address (str): Address of the deployed LogStorage contract.
        contract_abi (list): ABI of the LogStorage contract.
    """
    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Ganache. Is it running?")
        return

    # Initialize the contract
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=contract_abi
    )

    # Fetch logs
    try:
        logs = contract.functions.getLogs().call()
        if not logs:
            print("📭 No logs found in the contract.")
        else:
            print("📜 Stored Logs:")
            for i, log in enumerate(logs, 1):
                print(f"{i}. {log}")
    except Exception as e:
        print(f"❌ Error fetching logs: {e}")

# Example Usage (replace with your contract address and ABI)
if __name__ == "__main__":
    # Replace these with your actual contract details (from smartContract.py)
    CONTRACT_ADDRESS = "0x02d59D928816F712078a22bD9a2DBf4AE9e48C69"  # e.g., "0x123..."
    CONTRACT_ABI = [
        {
            "inputs": [{"internalType": "string", "name": "log", "type": "string"}],
            "name": "storeLog",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "getLogs",
            "outputs": [{"internalType": "string[]", "name": "", "type": "string[]"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]

    fetch_stored_logs(CONTRACT_ADDRESS, CONTRACT_ABI)
