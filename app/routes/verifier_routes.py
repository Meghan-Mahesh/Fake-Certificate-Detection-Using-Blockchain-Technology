from flask import request, jsonify
from datetime import datetime
import sqlite3
from blockchain.blockchain import contract
from ..hash_util import generate_hash
from web3 import Web3
from ..app import app
from ..database import get_connection

@app.route("/verifier")
def verifier_page():
    return app.send_static_file("verifier.html")


@app.route("/api/verify", methods=["POST"])
def verify_certificate():
    try:
        cert_id = request.form.get("cert_id")
        file = request.files.get("file")

        if not cert_id or not file:
            return jsonify({"error": "cert_id and file required"}), 400

        # 🔥 Step 1: Generate SAME hash as stored (SHA256 → keccak)
        uploaded_hash = generate_hash(file)
        uploaded_hash_bytes = Web3.keccak(text=uploaded_hash)

        # 🔥 Step 2: Fetch blockchain data
        try:
            certHash, issuerId, issuedAt = contract.functions.getCertificateDetails(cert_id).call()
        except Exception as e:
            error_message = str(e)

            if "Certificate not found" in error_message:
                return jsonify({
                    "status": "error",
                    "message": "Certificate not found"
                }), 404
            else:
                return jsonify({
                    "status": "error",
                    "message": "Blockchain error occurred"
                }), 500

        # 🔥 Step 3: Convert timestamp
        issued_time = datetime.fromtimestamp(issuedAt).strftime("%Y-%m-%d %H:%M:%S")

        # 🔥 Step 4: Get issuer name from DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT organizationName 
            FROM issuer 
            WHERE blockchainAddress = ?
        """, (issuerId,))
        org = cursor.fetchone()
        conn.close()

        issuer_name = org[0] if org else issuerId

        # 🔥 Step 5: Compare hashes (CORRECT WAY)
        result = "VALID" if uploaded_hash_bytes == certHash else "FAKE"

        return jsonify({
            "status": "success",
            "result": result,
            "issuer": issuer_name,
            "issued_at": issued_time
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500