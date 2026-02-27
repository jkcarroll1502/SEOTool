#!/bin/bash
# ─────────────────────────────────────────────
# Jasleen — SEO Article Tool Launcher
# ─────────────────────────────────────────────

cd "$(dirname "$0")"

echo ""
echo "════════════════════════════════════════════════"
echo "  Jasleen — SEO Article Generation Tool"
echo "════════════════════════════════════════════════"

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo ""
  echo "  ⚠️  ANTHROPIC_API_KEY not set in environment."
  echo "  Enter your Anthropic API key:"
  read -r -s -p "  API Key: " api_key
  echo ""
  export ANTHROPIC_API_KEY="$api_key"
fi

echo ""
echo "  Starting server..."
echo "  Opening browser at http://127.0.0.1:5000"
echo ""
echo "  Press Ctrl+C to stop"
echo "════════════════════════════════════════════════"
echo ""

# Open browser after short delay
(sleep 2 && open "http://127.0.0.1:5000") &

python3 app.py
