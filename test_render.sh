#!/bin/bash

# Replace with your actual Render URL
RENDER_URL="https://dost-ai.onrender.com"

echo "🧪 Testing DOST AI on Render..."
echo "URL: $RENDER_URL"
echo ""

echo "1. 💓 Health Check:"
curl -s "$RENDER_URL/health" | jq '.' || curl -s "$RENDER_URL/health"
echo ""

echo "2. 👋 Welcome Message:"
curl -s "$RENDER_URL/" | jq '.' || curl -s "$RENDER_URL/"
echo ""

echo "3. 📊 System Status:"
curl -s "$RENDER_URL/ping" | jq '.' || curl -s "$RENDER_URL/ping"
echo ""

echo "4. 📖 API Documentation:"
echo "Visit: $RENDER_URL/docs"
echo ""

echo "✅ All tests completed!"
echo "🌍 Your DOST AI is live at: $RENDER_URL" 