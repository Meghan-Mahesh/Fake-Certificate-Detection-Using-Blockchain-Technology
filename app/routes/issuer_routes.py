from flask import request, jsonify, session, redirect
from datetime import datetime
import sqlite3
from blockchain.blockchain import w3, contract
from werkzeug.security import check_password_hash
from blockchain.blockchain import store_certificate
from werkzeug.security import generate_password_hash
import uuid
from ..app import app
from ..database import get_connection


@app.route("/issuer_login")
def issuer_login_page():
    return app.send_static_file("issuer_login.html")

@app.route("/api/issuer/login", methods=["POST"])
def issuer_login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT issuerId, passwordHash, approvalStatus
        FROM issuer
        WHERE email=?
    """, (email,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"status":"error", "message":"Invalid email"}), 401

    issuerId, passwordHash, status = row

    # Check password
    if not check_password_hash(passwordHash, password):
        return jsonify({"status":"error", "message":"Wrong password"}), 401

    if status != "APPROVED":
        return jsonify({"status":"error", "message":"Not approved yet"}), 403

    # 🔥🔥 THIS IS THE IMPORTANT PART
    session["issuer_logged_in"] = True
    session["issuer_email"] = email
    session["issuer_id"] = issuerId   # ✅ ADD THIS

    return jsonify({
        "status": "success",
        "message": "Login successful"
    })

@app.route("/issuer")
def issuer_dashboard():
    if not session.get("issuer_logged_in"):
        return "Unauthorized",403
    return app.send_static_file("issuer.html")

@app.route("/api/issuer/stats")
def issuer_stats():
    if not session.get("issuer_logged_in"):
        return jsonify({"error": "Unauthorized"}), 403

    issuer_id = session.get("issuer_id")

    try:
        # Fetch all certificate events
        events = contract.events.CertificateStored.get_logs(
            from_block=0,
            to_block='latest'
        )

        # Count certificates issued by this issuer
        total = sum(
            1 for e in events
            if e.args.issuerId == issuer_id
        )

        return jsonify({"total": total})

    except Exception as e:
        print("Error fetching stats:", e)
        return jsonify({"total": 0})

@app.route("/issuer/issue")
def issue_page():
    if not session.get("issuer_logged_in"):
        return "Unauthorized",403
    return app.send_static_file("issuer_issue.html")

@app.route("/api/issuer/issue", methods=["POST"])
def issuer_issue_certificate():
    try:
        if not session.get("issuer_logged_in"):
            return jsonify({"error": "Unauthorized"}), 403

        cert_id = request.form.get("cert_id")
        file = request.files.get("file")

        if not cert_id or not file:
            return jsonify({"error": "cert_id and file required"}), 400

        # 🔥 GET issuerId FROM SESSION
        issuer_id = session.get("issuer_id")

        if not issuer_id:
            return jsonify({"error": "Issuer ID not found"}), 400

        # 🔥 CALL BLOCKCHAIN WITH issuerId
        result = store_certificate(cert_id, file, issuer_id)

        return jsonify({
            "status": "success",
            "message": "Certificate issued successfully",
            "hash": result["hash"],
            "tx_hash": result["tx_hash"]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/issuer/issued")
def issuer_issued_page():
    if not session.get("issuer_logged_in"):
        return "Unauthorized",403
    return app.send_static_file("issuer_issued.html")

@app.route("/api/issuer/issued")
def get_issuer_certificates():
    if not session.get("issuer_logged_in"):
        return jsonify([])
    print("SESSION:", session)
    issuer_id = session.get("issuer_id")

    try:
        events = contract.events.CertificateStored.get_logs(
            from_block=0,
            to_block='latest'
        )

        result = []

        for e in events:
            print("EVENT:", e.args)  # 🔥 debug

            # 🔥 SAFER ACCESS
            event_issuer = e.args.get("issuerId")

            # Normalize values safely
            event_issuer = str(event_issuer).strip()
            session_issuer = str(issuer_id).strip()

            print("🔍 EVENT issuerId:", event_issuer)
            print("🔍 SESSION issuerId:", session_issuer)

            if event_issuer == session_issuer:

                block = w3.eth.get_block(e.blockNumber)

                result.append({
                    "certId": e.args.get("certId"),
                    "timestamp": datetime.fromtimestamp(
                        block.timestamp
                    ).strftime("%Y-%m-%d %H:%M:%S")
                })

        print("✅ Total certificates found:", len(result))
        result.sort(key=lambda x: x["timestamp"], reverse=True)
        return jsonify(result)

    except Exception as e:
        print("❌ Error:", e)
        return jsonify([])

@app.route("/issuer_register")
def issuer_register_page():
    return app.send_static_file("issuer_register.html")

@app.route("/api/register_issuer", methods=["POST"])
def register_issuer():
    try:
        data = request.get_json()

        organization_name = data.get("organizationName")
        organization_type = data.get("organizationType")
        email = data.get("email")
        password = data.get("password")

        if not all([organization_name, organization_type, email, password]):
            return jsonify({"error": "All fields are required"}), 400

        password_hash = generate_password_hash(password)
        issuer_id = str(uuid.uuid4())
        registration_date = datetime.now().strftime("%Y-%m-%d")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO issuer (
                issuerId,
                organizationName,
                organizationType,
                email,
                passwordHash,
                approvalStatus,
                registrationDate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            issuer_id,
            organization_name,
            organization_type,
            email,
            password_hash,
            "PENDING",
            registration_date
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Registration successful"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "status": "error",
            "message": "Email already registered"
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")