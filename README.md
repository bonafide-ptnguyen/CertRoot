# CertRoot

A secure, blockchain-based certification and file verification system. CertRoot leverages distributed ledger technology to ensure the integrity and authenticity of digital records, providing a tamper-proof solution for issuing and verifying certificates.

## 🚀 Live Demo
Check out the live application here:  
👉 **[https://cert-root.vercel.app/](https://cert-root.vercel.app/)**

**Backup links**:
* **Frontend:** [https://certroot-frontend.onrender.com/](https://certroot-frontend.onrender.com/)
* **Backend:** [https://certroot-backend.onrender.com/docs](https://certroot-backend.onrender.com/docs)

> **Note:** Due to free-tier limitations on our hosting provider, the backend services may spin down after periods of inactivity. If the link above does not load properly or data is missing, please contact a team member to trigger a redeployment on Render.

---

## 🛠️ Tech Stack

* **Frontend:** React, Vite
* **Backend:** Python, FastAPI, Uvicorn
* **Database:** MongoDB Atlas
* **Blockchain:** Ethereum (Sepolia Tenderly Testnet)
* **DevOps:** Docker, GitHub Actions (CI/CD), Render, Vercel

---

## ⚙️ Local Installation & Setup

Follow these steps to get the application running on your local machine (localhost).

### 1. Clone the Repository
Open your terminal and run:

```bash
git clone https://github.com/bonafide-ptnguyen/CertRoot.git
cd CertRoot
```

### 2. Backend Setup
**Prerequisites:** Ensure you have Python 3.11 or higher installed.

Navigate to the backend directory and set up the environment:

```bash
cd backend
```

**Activate Virtual Environment:**

*Unix/Linux/macOS:*
```bash
source .venv/bin/activate
```

*Windows:*
```powershell
.venv\Scripts\activate
```

**Install Dependencies & Run:**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### 3. Frontend Setup
Open a new terminal window, navigate to the frontend directory, and start the client:

```bash
cd frontend
npm install
npm run dev
```

### 🔍 Verification
Once both the backend and frontend are running locally, you can access the application in your browser (usually at `http://localhost:5173` if using Vite, or the port shown in your terminal).
