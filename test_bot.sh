#!/bin/bash

# Kingdom Wars Bot - Quick Test Script
# This script tests all endpoints to verify the bot is working

echo "🤖 Testing Kingdom Wars Bot..."
echo ""

BASE_URL="http://localhost:3000"

# Test 1: Health Check
echo "1️⃣  Testing /healthz endpoint..."
HEALTH=$(curl -s $BASE_URL/healthz)
echo "Response: $HEALTH"
echo ""

# Test 2: Bot Info
echo "2️⃣  Testing /info endpoint..."
INFO=$(curl -s $BASE_URL/info)
echo "Response: $INFO"
echo ""

# Test 3: Negotiation (Early Game)
echo "3️⃣  Testing /negotiate endpoint (Early Game - Turn 5)..."
curl -s -X POST $BASE_URL/negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "gameId": 12345,
    "turn": 5,
    "playerTower": {
      "playerId": 101,
      "hp": 100,
      "armor": 5,
      "resources": 50,
      "level": 2
    },
    "enemyTowers": [
      {"playerId": 102, "hp": 95, "armor": 3, "resources": 0, "level": 1},
      {"playerId": 103, "hp": 80, "armor": 10, "resources": 0, "level": 3}
    ],
    "combatActions": []
  }' | python -m json.tool
echo ""

# Test 4: Combat (Early Game)
echo "4️⃣  Testing /combat endpoint (Early Game - Turn 5)..."
curl -s -X POST $BASE_URL/combat \
  -H "Content-Type: application/json" \
  -d '{
    "gameId": 12345,
    "turn": 5,
    "playerTower": {
      "playerId": 101,
      "hp": 100,
      "armor": 5,
      "resources": 100,
      "level": 2
    },
    "enemyTowers": [
      {"playerId": 102, "hp": 95, "armor": 3, "resources": 0, "level": 1},
      {"playerId": 103, "hp": 80, "armor": 10, "resources": 0, "level": 3}
    ],
    "diplomacy": [],
    "previousAttacks": []
  }' | python -m json.tool
echo ""

# Test 5: Combat (Late Game - Fatigue Active)
echo "5️⃣  Testing /combat endpoint (Late Game - Turn 26, Fatigue Active)..."
curl -s -X POST $BASE_URL/combat \
  -H "Content-Type: application/json" \
  -d '{
    "gameId": 12345,
    "turn": 26,
    "playerTower": {
      "playerId": 101,
      "hp": 80,
      "armor": 10,
      "resources": 150,
      "level": 4
    },
    "enemyTowers": [
      {"playerId": 102, "hp": 45, "armor": 5, "resources": 0, "level": 3},
      {"playerId": 103, "hp": 0, "armor": 0, "resources": 0, "level": 2}
    ],
    "diplomacy": [],
    "previousAttacks": []
  }' | python -m json.tool
echo ""

# Test 6: Combat with Destroyed Tower
echo "6️⃣  Testing bot never attacks destroyed towers (HP ≤ 0)..."
curl -s -X POST $BASE_URL/combat \
  -H "Content-Type: application/json" \
  -d '{
    "gameId": 12345,
    "turn": 15,
    "playerTower": {
      "playerId": 101,
      "hp": 90,
      "armor": 10,
      "resources": 100,
      "level": 3
    },
    "enemyTowers": [
      {"playerId": 102, "hp": 0, "armor": 0, "resources": 0, "level": 2},
      {"playerId": 103, "hp": 50, "armor": 5, "resources": 0, "level": 2}
    ],
    "diplomacy": [],
    "previousAttacks": []
  }' | python -m json.tool
echo ""

echo "✅ All tests complete!"
echo ""
echo "Check the responses above:"
echo "- /healthz should return {\"status\": \"OK\"}"
echo "- /info should return bot metadata"
echo "- /negotiate should return diplomacy actions (or [])"
echo "- /combat should return combat actions"
echo "- Bot should NEVER attack player 102 (HP=0) in test 6"
echo ""
echo "Check server logs for:"
echo "- [KW-BOT] Mega ogudor (printed for every request)"
echo "- AI or fallback strategy being used"
echo "- Action decisions and reasoning"
