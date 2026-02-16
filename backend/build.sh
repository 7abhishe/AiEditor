#!/usr/bin/env bash
# ============================
# CodeGenie — Render Build Script
# Runs during deployment to install dependencies
# ============================

set -o errexit  # Exit on error

echo "📦 Installing system dependencies..."
apt-get update && apt-get install -y --no-install-recommends \
    libopenblas-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "✅ Build complete!"
