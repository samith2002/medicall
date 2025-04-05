#!/bin/bash
set -e

echo "Installing Modal if not already installed..."
pip install -q modal

echo "Setting up Modal CLI..."
modal token new

echo "Deploying to Modal..."
modal deploy modal_app.py

echo "Application deployed to Modal!"
echo "Run 'modal endpoints list' to get your app URL" 