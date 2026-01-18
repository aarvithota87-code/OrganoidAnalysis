#!/bin/bash
# Startup script for Organoid Analysis Web Application

echo "Starting Organoid Analysis Web Application..."
echo "=============================================="
echo ""
echo "Server will be available at:"
echo "  - http://localhost:5174"
echo "  - http://127.0.0.1:5174"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
python3 app.py

