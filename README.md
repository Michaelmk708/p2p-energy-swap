# P2P Energy Swap ⚡

**The Regulated Web3 Settlement Layer for Private Microgrids.**

P2P Energy Swap is a Decentralized Physical Infrastructure Network (DePIN) that empowers gated communities and institutions to tokenize and trade surplus solar energy instantly, legally, and profitably. 

By combining IoT Hardware Oracles with the high-throughput Solana blockchain, we eliminate curtailed solar waste and provide an immutable, 100% transparent sub-metering ledger that is fully compliant with the Kenyan Energy Act (Section 117).

## 🏗️ System Architecture

Our tech stack bridges the physical and digital worlds using four distinct layers:

1. **Hardware (IoT Oracle):** ESP32 microcontrollers act as trusted hardware oracles. They monitor solar PV generation and house load in real-time. When a "Solar Glut" (Surplus) is detected, they trigger the settlement layer.
2. **Backend (Oracle Node):** A Python/Django API intercepts hardware telemetry, updates the local state, and acts as the Web3 signer to anchor transactions to the blockchain.
3. **Web3 (Settlement Layer):** Deployed on the Solana Devnet, our smart contracts mint immutable receipts for every kilowatt-hour traded. This acts as an un-hackable audit trail for regulators (EPRA) and a tokenized Real-World Asset (RWA) ledger for investors.
4. **Frontend (Consumer UX):** A React.js dashboard provides a "zero-crypto" experience. Users see their physical power metrics and financial savings without needing to manage private keys or crypto wallets.

## 📂 Project Structure

```text
p2p-energy-swap/
├── backend/       # Django Oracle Node (Python)
├── blockchain/    # Solana Smart Contracts (Rust/Anchor)
├── frontend/      # React User Dashboard (TypeScript/Tailwind)
└── firmware/      # ESP32 C++ Code / Wokwi Simulation

🚀 Quick Start (Running the Live Pitch Demo)
To run the full end-to-end system on your local machine:

1. Start the Backend (Web3 Node)

Bash

cd backend
python manage.py runserver
# Runs on http://localhost:8000
2. Start the Frontend (React Dashboard)

Bash

cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
3. Trigger the Hardware Oracle
Open the firmware/diagram.json in Wokwi.

Hit Play.

Increase the Solar PV dial so it exceeds the House Load.

The hardware will automatically ping the Django backend, which will instantly sign and broadcast a live transaction to the Solana Devnet.

⚖️ Regulatory Compliance
P2P Energy Swap is designed with a compliance-first architecture. We do not act as a public utility. We provide a Software-as-a-Service (SaaS) sub-metering platform for captive solar generation (< 1 MW) strictly behind a single bulk meter, adhering to Section 117 of the Energy Act.


---

### 2. The Blockchain Directory `README.md`
*(Save this inside your `blockchain` folder, e.g., `~/D/p2p-energy-swap/blockchain/README.md`)*

```markdown
# ⛓️ P2P Energy Swap - Web3 Settlement Layer

This directory contains the Rust-based Solana Smart Contracts (Anchor framework) that power the decentralized settlement engine of P2P Energy Swap.

## 🎯 Purpose

In a peer-to-peer energy microgrid, trust is the biggest bottleneck. Landlords and estate managers currently rely on manual, opaque sub-metering which leads to tenant disputes. 

We solve this by using the Solana blockchain as an **Immutable Cost-Allocation Ledger**. 

* **For Regulators (EPRA):** It provides a transparent, un-hackable audit trail proving that tenants are billed fairly for exact energy consumed.
* **For Investors:** It establishes a DePIN (Decentralized Physical Infrastructure) architecture, tokenizing Real-World Assets (energy) with micro-transaction fees costing fractions of a cent.

## 🛠️ Prerequisites

To build and deploy these contracts, ensure you have the Solana toolchain installed:
* [Rust](https://www.rust-lang.org/tools/install)
* [Solana CLI](https://docs.solana.com/cli/install-solana-cli-tools) (v1.18+)
* [Anchor CLI](https://www.anchor-lang.com/docs/installation)

## 🏗️ Build & Deploy Instructions

**1. Configure your environment for Devnet**
```bash
solana config set --url devnet
# Ensure your local wallet has devnet SOL
solana airdrop 2
2. Build the Anchor Program

Bash

anchor build
3. Sync Program Keys
Anchor generates a unique Program ID upon building. Sync it to your source code:

Bash

anchor keys sync
anchor build # Rebuild with new keys
4. Deploy to Solana Devnet

Bash

anchor deploy
Note: Save the Program ID outputted in the terminal. You can view your live contract on the Solana Explorer.

🔌 Architecture: The Hardware Oracle Pattern
Smart contracts cannot see the real world. To securely bring physical energy data on-chain, we utilize a Hardware Oracle Pattern:

An ESP32 Smart Meter acts as the root of trust, verifying physical electron flow.

The ESP32 sends a cryptographic payload to our Django Backend (The Oracle Node).

The Django Backend uses the solders Python SDK to sign a VersionedTransaction.

The transaction interacts with the Solana network to anchor the [P2P Energy Swap] ORACLE VERIFIED event immutably to the ledger.
