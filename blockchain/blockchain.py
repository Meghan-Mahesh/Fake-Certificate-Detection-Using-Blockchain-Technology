from web3 import Web3
from app.hash_util import generate_hash
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# -------------------------------
# CONNECT TO GANACHE
# -------------------------------
GANACHE_URL = os.getenv("BLOCKCHAIN_URL", "http://127.0.0.1:7545")
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise Exception("❌ Blockchain not connected")

# -------------------------------
# LOAD ABI
# -------------------------------
ABI_PATH = os.path.join(BASE_DIR, "abi.json")

with open(ABI_PATH,'r') as f:
    abi = json.load(f)

# -------------------------------
# LOAD CONTRACT ADDRESS
# -------------------------------
CONTRACT_ADDRESS_PATH = os.path.join(BASE_DIR, "contract_address.txt")

with open(CONTRACT_ADDRESS_PATH,'r') as f:
    CONTRACT_ADDRESS = f.read().strip()

contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=abi
)

# -------------------------------
# SYSTEM ACCOUNT (SINGLE ACCOUNT)
# -------------------------------
SYSTEM_ACCOUNT = w3.eth.accounts[0]


# =========================================================
# 🔥 STORE CERTIFICATE ON BLOCKCHAIN
# =========================================================
def store_certificate(cert_id, file, issuer_id):
    try:
        # Generate hash
        hash_value = generate_hash(file)

        # Convert to bytes32 (keccak for consistency)
        hash_bytes = Web3.keccak(text=hash_value)

        # Send transaction
        tx = contract.functions.storeCertificateHash(
            cert_id,
            hash_bytes,
            issuer_id   # ✅ store issuerId
        ).transact({
            "from": SYSTEM_ACCOUNT,
            "gas": 3000000
        })

        print("✅ Using system account:", SYSTEM_ACCOUNT)
        print("✅ Issuer ID stored:", issuer_id)

        # Wait for confirmation
        receipt = w3.eth.wait_for_transaction_receipt(tx)

        return {
            "status": "success",
            "hash": hash_value,
            "tx_hash": tx.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed
        }

    except Exception as e:
        print("❌ Blockchain error:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# 🔍 FETCH CERTIFICATE DETAILS FROM BLOCKCHAIN
# =========================================================
def get_certificate_details(cert_id):
    try:
        certHash, issuerId, issuedAt = contract.functions.getCertificateDetails(cert_id).call()

        return {
            "status": "success",
            "certHash": certHash.hex(),
            "issuerId": issuerId,
            "issuedAt": issuedAt
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# 🔍 VERIFY CERTIFICATE (HASH MATCHING)
# =========================================================
def verify_certificate(cert_id, file):
    try:
        # Generate uploaded file hash
        uploaded_hash = generate_hash(file)
        uploaded_hash_bytes = Web3.keccak(text=uploaded_hash)

        # Fetch blockchain data
        certHash, issuerId, issuedAt = contract.functions.getCertificateDetails(cert_id).call()

        # Compare hashes
        if uploaded_hash_bytes == certHash:
            return {
                "status": "success",
                "result": "VALID",
                "issuer": issuerId,
                "issued_at": issuedAt
            }
        else:
            return {
                "status": "success",
                "result": "FAKE",
                "issuer": issuerId,
                "issued_at": issuedAt
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }