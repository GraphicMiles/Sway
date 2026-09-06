#!/bin/bash
# Trigger video render on Render

RENDER_URL=${1:-"https://ayipada-pilot.onrender.com"}

echo "🎬 Triggering render on $RENDER_URL..."

curl -X POST "$RENDER_URL/api/render" \
  -H "Content-Type: application/json" \
  -d '{
    "composition": "FullPilot",
    "output": "out/pilot.mp4"
  }'

echo ""
echo "✅ Render triggered! Check $RENDER_URL for status."
