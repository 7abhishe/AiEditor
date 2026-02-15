#!/usr/bin/env bash
# ============================
# CodeGenie — Render Build Script
# Runs during deployment to install dependencies
# ============================

set -o errexit  # Exit on error

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build complete!"
