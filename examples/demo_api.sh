#!/bin/bash

# Demo script for Admin Dashboard API
# This script demonstrates common workflows using the Admin Dashboard API

API_KEY="change-me-in-production"
BASE_URL="http://localhost:8000"

echo "=== Admin Dashboard API Demo ==="
echo ""

# Check system status
echo "1. Checking system status..."
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/admin/status" | python3 -m json.tool
echo ""

# Create a new channel
echo "2. Creating a new channel..."
curl -s -X POST "$BASE_URL/admin/channels" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_name": "Demo Tech Channel",
    "channel_id": "UC_DEMO_123",
    "description": "A demo channel for testing",
    "content_type": "educational",
    "video_length": "short",
    "video_style": "informative",
    "ai_provider": "openai"
  }' | python3 -m json.tool
echo ""

# List all channels
echo "3. Listing all channels..."
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/admin/channels" | python3 -m json.tool
echo ""

# Create a schedule for the channel
echo "4. Creating a schedule..."
curl -s -X POST "$BASE_URL/admin/schedules" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": 1,
    "frequency": "daily",
    "preferred_time": "09:00",
    "timezone": "UTC",
    "is_active": true
  }' | python3 -m json.tool
echo ""

# Test AI generation
echo "5. Testing AI generation..."
curl -s -X POST "$BASE_URL/admin/actions/test-ai-generation" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "test_ai_generation",
    "details": "Testing AI generation from demo script"
  }' | python3 -m json.tool
echo ""

# View job history
echo "6. Viewing job history..."
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/admin/jobs/history?limit=5" | python3 -m json.tool
echo ""

# View upcoming jobs
echo "7. Viewing upcoming scheduled jobs..."
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/admin/jobs/upcoming" | python3 -m json.tool
echo ""

echo "=== Demo Complete ==="
echo "Visit http://localhost:8000/admin/dashboard to use the web interface"
