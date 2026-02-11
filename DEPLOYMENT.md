# Kingdom Wars Bot - Deployment Guide

## Overview

This is an AI-powered strategic bot for Kingdom Wars that uses AWS Bedrock (Claude models) to make intelligent decisions. The bot is designed to WIN by thinking strategically about alliances, attacks, defense, and resource management.

## Prerequisites

- Python 3.9 or higher
- AWS Account with Bedrock access
- AWS credentials with permissions to invoke Bedrock models

## Local Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials:

```env
AWS_REGION=eu-north-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

PORT=3000
BOT_NAME=Mega ogudor
BOT_STRATEGY=AI-trapped-strategy
BOT_VERSION=1.0

PRIMARY_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
FALLBACK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

REQUEST_TIMEOUT=1.0
AI_TIMEOUT=0.8

LOG_LEVEL=INFO
```

### 3. Run Locally

```bash
python main.py
```

The server will start on `http://localhost:3000`

### 4. Test Endpoints

Health check:
```bash
curl http://localhost:3000/healthz
```

Bot info:
```bash
curl http://localhost:3000/info
```

## AWS IAM Permissions

Your AWS credentials need the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
      ]
    }
  ]
}
```

## Deployment Options

### Option 1: AWS EC2 (Recommended for Hackathon)

Deploy to EC2 in `eu-north-1` (Stockholm) for lowest latency:

1. Launch EC2 instance (t3.small or larger)
2. Install Python and dependencies
3. Copy code to instance
4. Set environment variables
5. Run with systemd or screen:

```bash
# Using screen
screen -S kingdom-wars
python main.py
# Detach with Ctrl+A, D
```

6. Configure security group to allow inbound traffic on port 3000

### Option 2: AWS Lambda + API Gateway

For serverless deployment:

1. Package code and dependencies
2. Create Lambda function
3. Set environment variables
4. Create API Gateway
5. Map endpoints to Lambda

Note: Lambda cold starts may affect response time. Keep function warm with scheduled pings.

### Option 3: AWS App Runner

Quick deployment option:

1. Push code to GitHub
2. Create App Runner service
3. Configure environment variables
4. Deploy

## Testing the Bot

### Sample Negotiation Request

```bash
curl -X POST http://localhost:3000/negotiate \
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
  }'
```

### Sample Combat Request

```bash
curl -X POST http://localhost:3000/combat \
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
  }'
```

## Bot Strategy

The bot uses a phase-based strategy:

### Early Game (Turns 1-10): Resource Growth
- Upgrade to level 3-4 as fast as possible
- Build armor only if HP < 60
- Light attacks on weakest opponent

### Mid Game (Turns 11-24): Dominance
- Upgrade to level 4
- Focus attacks on weakest to eliminate
- Maintain HP > 50 with armor

### Late Game (Turns 25+): Survival & Elimination
- **CRITICAL**: Fatigue damage doubles each turn (10, 20, 40, 80, 160...)
- Aggressive attacks (70-80% of resources)
- Focus fire on weakest to eliminate
- Minimal armor (only if HP < 30)
- NO upgrades

### Key Strategic Principles
1. **Never attack destroyed towers** (HP ≤ 0) - wastes resources
2. **Monitor own HP** - build armor before taking lethal damage
3. **Understand fatigue** - game becomes elimination race after turn 25
4. **Upgrade early** - level 3-4 provides massive resource advantage
5. **Form smart alliances** - coordinate to eliminate strongest threat

## Monitoring

Logs are written to stdout. Monitor with:

```bash
tail -f /path/to/logs
```

Key log messages:
- `[KW-BOT] Mega ogudor` - Required log for every request
- `Negotiation request: Game X, Turn Y` - Negotiation phase
- `Combat request: Game X, Turn Y` - Combat phase
- `AI generated N actions` - AI successfully generated actions
- `Using fallback strategy` - AI failed, using heuristics

## Troubleshooting

### Bot returns empty arrays
- Check AWS credentials are valid
- Check Bedrock model access in your region
- Check logs for errors
- Bot will use fallback strategy if AI fails

### Response time > 1 second
- Check network latency to AWS
- Consider deploying closer to game engine (eu-north-1)
- Check AI timeout setting (default 0.8s)

### Bot makes bad decisions
- Check logs to see if AI or fallback is being used
- Review AI prompts in logs
- Adjust strategy in fallback_strategy.py if needed

## Performance Optimization

- Deploy in eu-north-1 (Stockholm) for lowest latency
- Use Claude 3.5 Sonnet for best strategic reasoning
- Fall back to Claude 3 Haiku if Sonnet is slow
- Keep Lambda warm with scheduled pings (if using Lambda)
- Monitor response times and adjust AI timeout

## Winning Tips

1. **Early game**: Rush to level 3-4 for resource advantage
2. **Mid game**: Eliminate weakest opponents one by one
3. **Late game**: Go aggressive when fatigue starts - eliminate before fatigue kills everyone
4. **Always**: Never waste resources attacking destroyed towers!

Good luck winning the hackathon! 🏆
