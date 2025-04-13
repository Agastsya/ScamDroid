from web3 import Web3
import hashlib

def get_hashed_logs(contract_address, contract_abi):
    """
    Fetch logs from the smart contract and compute their SHA-256 hashes.
    
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
            return

        print("🔍 Stored Logs with Hashes (SHA-256):")
        for i, log in enumerate(logs, 1):
            # Compute SHA-256 hash of the log
            log_hash = hashlib.sha256(log.encode('utf-8')).hexdigest()
            print(f"{i}. Log: {log[:50]}...")  # Truncate long logs
            print(f"   Hash: {log_hash}\n")

    except Exception as e:
        print(f"❌ Error fetching logs: {e}")

# Example Usage
if __name__ == "__main__":
    # Replace these with your actual contract details
    CONTRACT_ADDRESS = "0x02d59D928816F712078a22bD9a2DBf4AE9e48C69"  # From smartContract.py
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

    get_hashed_logs(CONTRACT_ADDRESS, CONTRACT_ABI)
