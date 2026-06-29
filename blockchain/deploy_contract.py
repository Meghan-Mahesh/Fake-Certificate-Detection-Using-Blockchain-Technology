from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTRACT_PATH = os.path.join(BASE_DIR, "CertificateVerification.sol")

ABI_PATH = os.path.join(BASE_DIR, "abi.json")

CONTRACT_ADDRESS_PATH = os.path.join(BASE_DIR, "contract_address.txt")
# -------------------------------------------------
# STEP 1: Connect to Ganache
# -------------------------------------------------

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.is_connected():
    raise Exception("Ganache not connected")

print("Connected to Ganache")

# -------------------------------------------------
# STEP 2: Install Solidity Compiler (Stable Version)
# -------------------------------------------------

install_solc("0.8.17")

# -------------------------------------------------
# STEP 3: Read Solidity File
# -------------------------------------------------

with open(CONTRACT_PATH, "r", encoding="utf-8") as file:
    contract_source = file.read()

# -------------------------------------------------
# STEP 4: Compile Contract
# -------------------------------------------------

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "CertificateVerification.sol": {
                "content": contract_source
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        },
    },
    solc_version="0.8.17",
)

# -------------------------------------------------
# STEP 5: Extract ABI and Bytecode
# -------------------------------------------------

abi = compiled_sol["contracts"]["CertificateVerification.sol"]["CertificateStorage"]["abi"]
bytecode = compiled_sol["contracts"]["CertificateVerification.sol"]["CertificateStorage"]["evm"]["bytecode"]["object"]

# Save ABI automatically
with open(ABI_PATH, "w") as f:
    json.dump(abi, f)

print("ABI saved to abi.json")

# -------------------------------------------------
# STEP 6: Deploy Contract (Manual Gas Fix)
# -------------------------------------------------

account = w3.eth.accounts[0]

Certificate = w3.eth.contract(
    abi=abi,
    bytecode=bytecode
)

print("Deploying contract...")

tx_hash = Certificate.constructor().transact({
    "from": account,
    "gas": 3000000,
    "gasPrice": w3.to_wei("20", "gwei")
})

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress

print("Contract deployed successfully!")
print("Contract Address:", contract_address)

# -------------------------------------------------
# STEP 7: Save Contract Address
# -------------------------------------------------

with open(CONTRACT_ADDRESS_PATH, "w") as f:
    f.write(contract_address)

print("Contract address saved to contract_address.txt")
