#!/bin/bash

echo "🚀 Starting arXiv Assistant Web UI..."
echo ""
echo "📍 Open in browser: http://localhost:5000"
echo "⌨️  Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python3 web/app.py
