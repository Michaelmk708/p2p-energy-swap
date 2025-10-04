⚡ P2P Energy Swap
Empowering Sustainable Communities through Decentralized Green Energy Trading
🌍 Overview

P2P Energy Swap is a decentralized, AI-assisted energy trading platform that enables households with solar panels or other renewable energy sources to sell and buy energy directly with each other.

Instead of wasting surplus power, users can tokenize their excess energy and trade it securely through blockchain-backed smart contracts, ensuring transparency and trust without intermediaries.

This project was built as part of the DeKUT Hackathon, themed around Green Energy and Sustainable Cities.

💡 Problem Statement

In many regions, households with renewable energy systems (like solar panels) generate more power than they consume. Unfortunately, this excess power often goes unused due to lack of local microgrid coordination or infrastructure to sell small-scale energy back to the grid.

Meanwhile, nearby homes may experience power shortages, relying heavily on expensive or non-renewable sources.

🌱 Our Solution

P2P Energy Swap bridges this gap through a peer-to-peer microgrid where:

Producers can tokenize surplus energy (1 kWh = 1 token)

Consumers can purchase tokens representing energy using M-Pesa or crypto

Smart contracts handle automatic settlement and trustless transactions

AI predicts energy demand and price trends, optimizing trading efficiency

⚙️ System Architecture

1. IoT Layer

Smart meters simulate or measure power production and consumption.

Data flows to the backend in real-time (using MQTT or Wokwi simulation).

2. Backend (Django + DRF)

Handles user registration, authentication, and token balance tracking.

Interfaces with blockchain APIs for transaction verification.

Predictive AI models estimate future usage and suggest trade strategies.

3. Blockchain Layer (Solana)

Stores transactions and token trades via smart contracts.

Ensures energy tokenization and transparent ledger management.

4. Frontend (Next.js + Tailwind CSS)

User-friendly dashboard for tracking energy, token balances, and trades.

Real-time visualization of market activity and smart pricing suggestions.

5. Payment Integration (M-Pesa API)

Users can buy/sell tokens using real currency for accessibility.

🧠 AI Integration

An AI forecasting model analyzes historical consumption and weather data to:

Predict next-day household energy needs.

Recommend optimal selling or buying times.

Detect trading anomalies or grid imbalances early.

🔐 Blockchain & Smart Contracts

Using Solana smart contracts, we handle:

Token creation (minting and burning per transaction)

Escrow for trades (holding tokens until delivery confirmed)

Decentralized ledger ensuring immutable records

This ensures fair, verifiable, and efficient energy trading between households.

🖥️ Features

✅ User registration & login (secure JWT-based authentication)
✅ Tokenized energy marketplace
✅ Real-time IoT data simulation
✅ AI-based usage and price prediction
✅ Smart contract–driven trustless payments
✅ M-Pesa integration for local accessibility
✅ Transparent dashboards with energy and token stats

🧩 Tech Stack
Layer	Technology
Frontend	Next.js, Tailwind CSS, ShadCN UI
Backend	Django, Django REST Framework
Database	PostgreSQL
Blockchain	Solana Smart Contracts
AI/ML	Python (Scikit-learn / TensorFlow)
IoT Simulation	Wokwi or MQTT
Payments	M-Pesa API
Authentication	JWT (SimpleJWT)
