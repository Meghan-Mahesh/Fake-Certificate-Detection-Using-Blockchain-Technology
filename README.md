# Blockchain-Based Certificate Verification System

A secure certificate verification system that leverages **Blockchain Technology** to prevent certificate forgery by storing certificate hashes on the Ethereum blockchain. The application enables educational institutions or organizations to issue certificates securely while allowing anyone to verify certificate authenticity.

---

## 🚀 Features

* Secure certificate issuance using Ethereum Blockchain
* Certificate verification using SHA-256 hashing
* Role-based access control:

  * **Admin**
  * **Issuer**
  * **Verifier**
* Admin approval workflow for issuer registration
* Blockchain-based immutable certificate storage
* RESTful APIs developed using Flask
* User-friendly web interface

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* Web3.py

### Blockchain

* Solidity
* Ganache
* Ethereum

### Database

* SQLite

### Frontend

* HTML
* CSS
* JavaScript

### Security

* SHA-256 Hashing
* Password Hashing
* Session Management

---

# Project Structure

```
certchain/
│
├── app/
│   ├── app.py
│   ├── database.py
│   ├── hash_util.py
│   └── routes/
│       ├── admin_routes.py
│       ├── issuer_routes.py
│       └── verifier_routes.py
│
├── blockchain/
│   ├── blockchain.py
│   ├── deploy_contract.py
│   ├── CertificateVerification.sol
│   ├── abi.json
│   └── contract_address.txt
│
├── database/
│   └── certchain.db
│
├── static/
│
├── requirements.txt
├── run.py
└── README.md
```

---

# Prerequisites

Before running the project, ensure the following software is installed:

* Python 3.11 or above
* Ganache Local Blockchain
* Git
* Visual Studio Code (Recommended)

---

# Ganache Configuration

Install and open **Ganache**.

Create a **New Workspace** with the following configuration:

| Configuration | Value    |
| ------------- | -------- |
| Port Number   | **7545** |
| Network ID    | **1337** |

After creating the workspace, **Start** the Ganache server.

> **Important:** The application will not work if Ganache is not running.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Blockchain-Certificate-Verification-System.git

cd Blockchain-Certificate-Verification-System
```

---

## 2. Create Virtual Environment

Windows

```bash
python -m venv .venv
```

Activate Virtual Environment

PowerShell

```bash
.venv\Scripts\Activate.ps1
```

Command Prompt

```bash
.venv\Scripts\activate
```

---

## 3. Install Required Packages

```bash
pip install -r requirements.txt
```

---

# Deploy Smart Contract

Navigate to the blockchain directory.

```bash
cd blockchain
```

Deploy the smart contract.

```bash
python deploy_contract.py
```

This script automatically:

* Compiles the Solidity smart contract
* Deploys the contract on Ganache
* Generates **abi.json**
* Generates **contract_address.txt**

These files are required for blockchain interaction.

---

# Run the Application

Navigate back to the project root.

```bash
cd ..
```

Run the Flask application.

```bash
python run.py
```

The application starts at:

```
http://127.0.0.1:5000
```

---

# Default Admin Credentials

The application automatically creates a default admin account during the first run.

| Email                                     | Password |
| ----------------------------------------- | -------- |
| [admin@gmail.com](mailto:admin@gmail.com) | admin123 |

---

# Application Workflow

## Step 1 – Register Issuer

* Open the Issuer Registration page.
* Fill in the organization details.
* Submit the registration request.

The issuer status will be **Pending**.

---

## Step 2 – Admin Approval

* Login as Admin.
* View pending issuer requests.
* Approve or Reject the issuer.

Only approved issuers can access the dashboard.

---

## Step 3 – Issuer Login

After approval:

* Login using registered credentials.
* Access the Issuer Dashboard.

---

## Step 4 – Issue Certificate

The issuer can issue certificates by providing:

* Certificate ID
* Certificate PDF

Click **Issue Certificate**.

The application:

* Generates SHA-256 hash of the certificate.
* Stores the hash on the Ethereum blockchain.
* Records blockchain transaction details.

---

## Step 5 – Verify Certificate

Verification does **not require login**.

The verifier provides:

* Certificate ID
* Certificate PDF

The system:

* Generates SHA-256 hash of the uploaded certificate.
* Retrieves the stored hash from the blockchain.
* Compares both hashes.

If both hashes match:

```
VALID
```

Otherwise:

```
FAKE
```

---

# Blockchain Workflow

```
Issuer Uploads Certificate
            │
            ▼
Generate SHA-256 Hash
            │
            ▼
Store Hash on Ethereum Blockchain
            │
            ▼
Verifier Uploads Certificate
            │
            ▼
Generate SHA-256 Hash
            │
            ▼
Compare with Blockchain Hash
            │
            ▼
VALID / FAKE
```

---

# Security Features

* Immutable blockchain storage
* SHA-256 certificate hashing
* Password hashing
* Role-based authentication
* Session management
* Smart contract-based certificate verification

---

# Future Enhancements

* IPFS integration for decentralized certificate storage
* Email OTP authentication
* QR code-based certificate verification
* Certificate expiration support
* Multi-admin support
* Cloud deployment
* Docker containerization

---

# Author

**Lenka Meghan Mahesh**

B.Tech – Cyber Security

Aspiring Software Engineer
