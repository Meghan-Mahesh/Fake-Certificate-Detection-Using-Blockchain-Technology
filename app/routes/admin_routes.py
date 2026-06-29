from flask import request, jsonify, session
from datetime import datetime
import sqlite3
import random
from blockchain.blockchain import w3, contract
from ..app import app
import os
from ..database import get_connection

admin_otps = {}

def admin_required():
    if not session.get("admin_logged_in"):
        return False
    return True

@app.route("/admin")
def admin_page():
    if not session.get("admin_logged_in"):
        return "Unauthorized", 403
    return app.send_static_file("admin.html")

@app.route("/admin_login")
def admin_login_page():
    return app.send_static_file("admin_login.html")

@app.route("/api/admin/generate_otp", methods=["POST"])
def generate_admin_otp():
    data = request.get_json()
    email = data.get("email")

    print("=" * 50)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM admin WHERE email = ?", (email,))
    admin = cursor.fetchone()
    conn.close()

    if not admin:
        return jsonify({"message": "Admin not found"}), 404

    otp = str(random.randint(100000, 999999))
    admin_otps[email] = otp

    print("ADMIN OTP:", otp)   # For demo purpose

    return jsonify({"message": "OTP generated (check server console)"}), 200

@app.route("/api/admin/verify_otp", methods=["POST"])
def verify_admin_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if admin_otps.get(email) == otp:
        session["admin_logged_in"] = True
        session["admin_email"] = email
        return jsonify({"status": "success", "message": "Login successful"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid OTP"}), 401
    
@app.route("/api/admin/pending_issuers", methods=["GET"])
def get_pending_issuers():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT issuerId, organizationName, organizationType,
               email, blockchainAddress, approvalStatus, registrationDate
        FROM issuer
        WHERE approvalStatus = 'PENDING'
        ORDER BY registrationDate DESC
    """)

    issuers = cursor.fetchall()
    conn.close()

    result = []
    for i in issuers:
        result.append({
            "issuerId": i[0],
            "organizationName": i[1],
            "organizationType": i[2],
            "email": i[3],
            "blockchainAddress": i[4],
            "approvalStatus": i[5],
            "registrationDate": i[6]
        })

    return jsonify(result), 200

@app.route("/api/admin/approved_issuers", methods=["GET"])
def get_approved_issuers():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT issuerId, organizationName, organizationType,
               email, blockchainAddress, approvalStatus, registrationDate
        FROM issuer
        WHERE approvalStatus = 'APPROVED'
        ORDER BY registrationDate DESC
    """)

    issuers = cursor.fetchall()
    conn.close()

    result = []
    for i in issuers:
        result.append({
            "issuerId": i[0],
            "organizationName": i[1],
            "organizationType": i[2],
            "email": i[3],
            "blockchainAddress": i[4],
            "approvalStatus": i[5],
            "registrationDate": i[6]
        })

    return jsonify(result), 200

@app.route("/api/admin/rejected_issuers", methods=["GET"])
def get_rejected_issuers():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT issuerId, organizationName, organizationType,
               email, blockchainAddress, approvalStatus, registrationDate
        FROM issuer
        WHERE approvalStatus = 'REJECTED'
        ORDER BY registrationDate DESC
    """)

    issuers = cursor.fetchall()
    conn.close()

    result = []
    for i in issuers:
        result.append({
            "issuerId": i[0],
            "organizationName": i[1],
            "organizationType": i[2],
            "email": i[3],
            "blockchainAddress": i[4],
            "approvalStatus": i[5],
            "registrationDate": i[6]
        })

    return jsonify(result), 200

@app.route("/api/admin/approve", methods=["POST"])
def approve_issuer():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    issuer_id = data.get("issuerId")

    if not issuer_id:
        return jsonify({"error": "issuerId required"}), 400

    SYSTEM_ACCOUNT = w3.eth.accounts[0]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE issuer
        SET approvalStatus='APPROVED',
            blockchainAddress=?
        WHERE issuerId=?
    """,(SYSTEM_ACCOUNT, issuer_id))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"success"
    }),200

@app.route("/api/admin/reject", methods=["POST"])
def reject_issuer():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    issuer_id = data.get("issuerId")

    if not issuer_id:
        return jsonify({"error": "issuerId required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE issuer
        SET approvalStatus = 'REJECTED'
        WHERE issuerId = ?
    """, (issuer_id,))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"}), 200

@app.route("/admin/transactions")
def admin_transactions_page():
    if not session.get("admin_logged_in"):
        return "Unauthorized", 403
    return app.send_static_file("admin_transactions.html")

@app.route("/admin/approved")
def admin_approved_page():
    if not session.get("admin_logged_in"):
        return "Unauthorized", 403
    return app.send_static_file("admin_approved.html")

@app.route("/admin/pending")
def admin_pending_page():
    if not session.get("admin_logged_in"):
        return "Unauthorized", 403
    return app.send_static_file("admin_pending.html")

@app.route("/admin/rejected")
def admin_rejected_page():
    if not session.get("admin_logged_in"):
        return "Unauthorized", 403
    return app.send_static_file("admin_rejected.html")

@app.route("/api/admin/transactions")
def get_transactions():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 403

    events = contract.events.CertificateStored.get_logs(
        from_block=0,
        to_block='latest'
    )

    result = []

    for event in events:
        block = w3.eth.get_block(event.blockNumber)
        raw_timestamp = block.timestamp

        result.append({
            "transactionHash": event.transactionHash.hex(),
            "issuer": event.args.issuerId,
            "timestamp_raw": raw_timestamp
        })

    result.sort(key=lambda x: x["timestamp_raw"], reverse=True)

    # Convert timestamp to readable format
    final_result = []
    for r in result:
        formatted_time = datetime.fromtimestamp(
            r["timestamp_raw"]
        ).strftime("%Y-%m-%d %H:%M:%S")

        final_result.append({
            "transactionHash": r["transactionHash"],
            "issuer": r["issuer"],
            "timestamp": formatted_time
        })

    return jsonify(final_result)

@app.route("/api/admin/stats")
def admin_stats():
    if not session.get("admin_logged_in"):
        return jsonify({"error":"Unauthorized"}),403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM issuer WHERE approvalStatus='APPROVED'")
    approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issuer WHERE approvalStatus='PENDING'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issuer WHERE approvalStatus='REJECTED'")
    rejected = cursor.fetchone()[0]

    conn.close()

    events = contract.events.CertificateStored.get_logs(
            from_block=0,
            to_block='latest'
        )
    transactions = len(events)

    return jsonify({
        "transactions": transactions,
        "approved": approved,
        "pending": pending,
        "rejected": rejected
    })
