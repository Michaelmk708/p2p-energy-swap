#!/usr/bin/env bash
set -e

echo "🔧 Setting up dev environment..."

# Node.js packages
npm install -g yarn

# Python packages
pip3 install --upgrade pip
pip3 install jupyter scikit-learn pandas

# Solana config (point to devnet)
solana config set --url devnet

echo "✅ Dev environment setup complete!"
