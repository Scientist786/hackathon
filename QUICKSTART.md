# Kingdom Wars Bot - Quick Start Guide

## Get Running in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up AWS Credentials

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your AWS credentials:

```env
AWS_REGION=eu-north-1
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
```

### 3. Run the Bot

```bash
python main.py
```

The bot will start on `http://localhost:3000`

### 4. Test It Works

```bash
# Health check
curl http://localhost:3000/healthz

# Bot info
curl http://localhost:3000/info
```

## What Makes This Bot Win

### 🧠 AI-Powered Strategy
- Uses AWS Bedrock (Claude 3.5 Sonnet) to analyze game state
- Makes intelligent decisions about alliances, attacks, and upgrades
- Falls back to smart heuristics if AI is unavailable

### 🎯 Key Winning Features

1. **Never Attacks Destroyed Towers** (HP ≤ 0)
   - Wastes no resources on dead opponents

2. **Correct Fatigue Mechanics**
   - Understands fatigue damage: 10 × 2^(turn-25)
   - Turn 25: 10 damage, Turn 26: 20, Turn 27: 40, Turn 28: 80...
   - Adapts strategy when fatigue starts

3. **Phase-Based Strategy**
   - **Early (1-10)**: Rush upgrades to level 3-4
   - **Mid (11-24)**: Eliminate weak opponents
   - **Late (25+)**: Aggressive attacks before fatigue kills everyone

4. **Smart Target Selection**
   - Calculates effective HP (HP + armor)
   - Focuses on weakest opponents
   - Forms strategic alliances

5. **Resource Optimization**
   - Knows when to upgrade vs attack
   - Builds armor only when necessary
   - Maximizes resource generation

## Strategy Summary

### Early Game (Turns 1-10)
- **Goal**: Reach level 3-4 fast
- **Actions**: Save for upgrades, minimal attacks
- **Why**: Higher level = more resources per turn

### Mid Game (Turns 11-24)
- **Goal**: Eliminate 1-2 opponents
- **Actions**: Balanced attacks and upgrades
- **Why**: Reduce competition before fatigue

### Late Game (Turns 25+)
- **Goal**: Be last tower standing
- **Actions**: 70-80% resources on attacks, minimal armor
- **Why**: Fatigue doubles each turn - eliminate before it kills you

## Deployment for Hackathon

### Option 1: Local Testing
```bash
python main.py
# Bot runs on localhost:3000
```

### Option 2: AWS EC2 (Recommended)
1. Launch EC2 in eu-north-1 (Stockholm)
2. Install Python and dependencies
3. Copy code and set environment variables
4. Run: `python main.py`
5. Expose port 3000

### Option 3: Quick Deploy
```bash
# Using screen to keep running
screen -S kingdom-wars
python main.py
# Detach: Ctrl+A, D
```

## Monitoring

Watch the logs to see the bot thinking:

```bash
# You'll see:
[KW-BOT] Mega ogudor                    # Required log
Negotiation request: Game X, Turn Y     # Negotiation phase
Combat request: Game X, Turn Y          # Combat phase
AI generated N actions                  # AI working
Using fallback strategy                 # AI failed, using heuristics
```

## Troubleshooting

**Bot returns empty arrays?**
- Check AWS credentials
- Check Bedrock access in your region
- Bot will use fallback strategy if AI fails (still works!)

**Response too slow?**
- Deploy closer to game engine (eu-north-1)
- Adjust AI_TIMEOUT in .env (default 0.8s)

**Bot makes bad decisions?**
- Check logs to see if AI or fallback is used
- Fallback strategy is still intelligent!

## Files Overview

```
.
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── .env                       # Your config (create this!)
├── config/
│   └── settings.py           # Configuration
├── src/
│   ├── server.py             # FastAPI endpoints
│   ├── models.py             # Data models
│   ├── strategy_engine.py    # AI decision engine
│   ├── bedrock_client.py     # AWS Bedrock client
│   ├── prompt_builder.py     # AI prompts
│   ├── fallback_strategy.py  # Heuristic strategies
│   ├── validators.py         # Action validation
│   ├── targeting.py          # Target selection
│   ├── fatigue.py            # Fatigue calculations
│   └── resources.py          # Resource calculations
└── DEPLOYMENT.md             # Detailed deployment guide
```

## Next Steps

1. **Test locally** with sample requests (see DEPLOYMENT.md)
2. **Deploy to AWS** in eu-north-1 for best latency
3. **Monitor logs** to see bot strategy
4. **Win the hackathon!** 🏆

## Key Reminders

- ✅ Bot thinks strategically using AI
- ✅ Never attacks destroyed towers
- ✅ Understands fatigue mechanics
- ✅ Adapts strategy by game phase
- ✅ Falls back to smart heuristics if AI fails
- ✅ Responds within 1 second
- ✅ Logs all decisions for debugging

Good luck! 🎮
