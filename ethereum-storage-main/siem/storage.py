from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.is_connected():
    print("❌ Failed to connect to Ganache. Is it running?")
    exit(1)

# Replace with your contract address (from smartContract.py)
contract_address = "0x02d59D928816F712078a22bD9a2DBf4AE9e48C69"  # e.g., "0x123..."
contract_abi = [
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

# Fix: Use checksum address to avoid ENS resolution
contract = w3.eth.contract(
    address=Web3.to_checksum_address(contract_address),
    abi=contract_abi
)

# Read logs (Linux syslog)
try:
    with open("/var/log/syslog", "r") as f:
        logs = f.readlines()
except PermissionError:
    print("⚠️ Run with 'sudo' to access /var/log/syslog!")
    exit(1)

# Store logs on-chain (first 5 logs)
for log in logs[:5]:
    tx = contract.functions.storeLog(log[:200]).transact({"from": w3.eth.accounts[0]})
    w3.eth.wait_for_transaction_receipt(tx)
    print(f"✅ Log stored: {log[:200]}")
