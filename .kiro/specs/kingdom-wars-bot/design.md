# Design Document: Kingdom Wars Bot

## Overview

The Kingdom Wars Bot is an AI-powered HTTP server designed to WIN a multiplayer tower defense game through intelligent strategic decision-making. The system uses AWS Bedrock AI models to analyze game state and make optimal tactical decisions during negotiation and combat phases. The primary goal is victory through smart resource management, strategic alliances, calculated attacks, and endgame survival.

The bot operates in a request-response cycle where the Game Engine sends game state information and expects strategic actions in return. The core innovation is using large language models to evaluate complex game states—including player health, opponent health, armor levels, resource availability, and fatigue timing—to generate winning strategies rather than random or simplistic actions.

**Key Strategic Principles**:
1. **Survival First**: Monitor own HP and armor, defend when vulnerable
2. **Smart Targeting**: Attack weakest opponents, avoid wasting resources on destroyed towers
3. **Resource Optimization**: Balance immediate needs vs. long-term growth (upgrades)
4. **Fatigue Awareness**: Adapt strategy dramatically after turn 25 when exponential damage begins
5. **Alliance Leverage**: Form strategic alliances to eliminate threats cooperatively

## Architecture

The system follows a layered architecture:

```
┌─────────────────────────────────────────┐
│         HTTP Server Layer               │
│  (Express/FastAPI - handles endpoints)  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Request Validation Layer          │
│   (validates game state, sanitizes)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Strategy Engine Layer            │
│  (AI-powered decision making core)      │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────────┐
│  Bedrock AI    │  │  Rule-Based     │
│  Client        │  │  Fallback       │
└────────────────┘  └─────────────────┘
```

**Key Design Decisions:**

1. **AI-First Strategy**: Use Bedrock models as the primary decision engine to analyze complex game states and make winning decisions
2. **Stateless Design**: Each request is independent; all strategic context derived from current game state
3. **Intelligent Analysis**: AI evaluates HP, armor, resources, opponent states, and fatigue to make optimal choices
4. **Winning Focus**: Every decision optimized for victory, not just valid responses
5. **Graceful Degradation**: If AI fails, fall back to intelligent heuristic-based strategies (not random actions)

## Components and Interfaces

### 1. HTTP Server Component

**Responsibility**: Handle incoming HTTP requests and route to appropriate handlers.

**Interface**:
```typescript
interface HTTPServer {
  start(port: number): Promise<void>
  stop(): Promise<void>
}

// Endpoints
GET  /healthz  → HealthCheckHandler
POST /negotiate → NegotiationHandler
POST /combat   → CombatHandler
GET  /info     → InfoHandler
```

**Implementation Notes**:
- Use Express.js (Node.js) or FastAPI (Python) for HTTP server
- Add request timeout middleware (1 second max)
- Log "[KW-BOT] Mega ogudor" on every request
- Return 200 with empty array on errors rather than 500

### 2. Request Validation Component

**Responsibility**: Validate and sanitize incoming game state data.

**Interface**:
```typescript
interface GameState {
  gameId: number
  turn: number
  playerTower: Tower
  enemyTowers: Tower[]
}

interface NegotiationRequest extends GameState {
  combatActions: CombatAction[]
}

interface CombatRequest extends GameState {
  diplomacy: DiplomacyAction[]
  previousAttacks: AttackAction[]
}

interface Validator {
  validateNegotiationRequest(req: any): NegotiationRequest | ValidationError
  validateCombatRequest(req: any): CombatRequest | ValidationError
}
```

**Validation Rules**:
- All required fields present
- Numeric values within valid ranges
- Player tower exists in game state
- Enemy towers array is valid

### 3. Strategy Engine Component

**Responsibility**: Core decision-making logic using AI and fallback heuristics.

**Interface**:
```typescript
interface StrategyEngine {
  decideNegotiation(state: NegotiationRequest): Promise<DiplomacyAction[]>
  decideCombat(state: CombatRequest): Promise<CombatAction[]>
}

interface DiplomacyAction {
  allyId: number
  attackTargetId?: number
}

interface CombatAction {
  type: 'armor' | 'attack' | 'upgrade'
  amount?: number        // for armor
  targetId?: number      // for attack
  troopCount?: number    // for attack
}
```

**Strategy Approach**:

The Strategy Engine uses a two-phase decision process focused on winning:

**Phase 1: AI Strategic Analysis**
- Construct detailed prompt with complete game state
- Include strategic context: own HP/armor, opponent HP/armor, turn number, fatigue status
- Call Bedrock model (Claude 3.5 Sonnet for superior strategic reasoning)
- AI analyzes:
  - **Survival threat**: Is our HP low? Do we need armor?
  - **Target selection**: Which opponent is weakest? Which is most dangerous?
  - **Resource optimization**: Should we upgrade now or attack?
  - **Fatigue timing**: Are we in endgame? Need aggressive elimination?
  - **Wasted attacks**: Avoid attacking destroyed towers (HP ≤ 0)
- Parse AI response into structured actions

**Phase 2: Validation & Intelligent Fallback**
- Validate AI-suggested actions against game rules
- If invalid or AI fails, use intelligent rule-based strategy (not random)
- Ensure resource constraints satisfied
- Verify no attacks on destroyed towers

### 4. Bedrock AI Client Component

**Responsibility**: Interface with AWS Bedrock for AI inference.

**Interface**:
```typescript
interface BedrockClient {
  invokeModel(prompt: string, modelId: string): Promise<string>
  invokeModelWithRetry(prompt: string, modelId: string, maxRetries: number): Promise<string>
}

interface PromptBuilder {
  buildNegotiationPrompt(state: NegotiationRequest): string
  buildCombatPrompt(state: CombatRequest): string
}
```

**Model Selection**:
- Primary: `anthropic.claude-3-5-sonnet-20241022-v2:0` (best reasoning)
- Fallback: `anthropic.claude-3-haiku-20240307-v1:0` (faster, cheaper)

**Prompt Strategy**:
- Include complete game state in structured format
- Provide game rules and constraints
- Request JSON-formatted response
- Include examples of valid actions

### 5. Action Validator Component

**Responsibility**: Validate generated actions against game rules and resource constraints.

**Interface**:
```typescript
interface ActionValidator {
  validateCombatActions(actions: CombatAction[], resources: number, level: number): ValidationResult
  calculateActionCost(action: CombatAction, level: number): number
  hasDuplicateTargets(actions: CombatAction[]): boolean
  hasMultipleArmor(actions: CombatAction[]): boolean
  hasMultipleUpgrades(actions: CombatAction[]): boolean
}

interface ValidationResult {
  valid: boolean
  errors: string[]
  totalCost: number
}
```

**Validation Logic**:
- Armor cost: `amount × 1`
- Attack cost: `troopCount × 1`
- Upgrade cost: `50 × (1.75 ^ (level - 1))`
- Total cost ≤ available resources
- At most one armor action
- At most one upgrade action
- No duplicate attack targets

### 6. Fallback Strategy Component

**Responsibility**: Provide intelligent rule-based strategies when AI is unavailable.

**Interface**:
```typescript
interface FallbackStrategy {
  generateNegotiationActions(state: NegotiationRequest): DiplomacyAction[]
  generateCombatActions(state: CombatRequest): CombatAction[]
}
```

### 7. Target Selection Component

**Responsibility**: Intelligently select attack targets based on game state.

**Interface**:
```typescript
interface TargetSelector {
  filterAliveTowers(towers: Tower[]): Tower[]
  findWeakestTower(towers: Tower[]): Tower | null
  findStrongestTower(towers: Tower[]): Tower | null
  calculateEffectiveHP(tower: Tower): number
  shouldAttackTarget(target: Tower, ourResources: number): boolean
}
```

**Target Selection Logic**:
- **Filter alive towers**: Exclude towers with HP ≤ 0
- **Effective HP**: HP + armor (total damage needed to destroy)
- **Weakest tower**: Lowest effective HP among alive towers
- **Strongest tower**: Highest level + effective HP among alive towers
- **Attack worthiness**: Can we deal meaningful damage (> 20% of effective HP)?

### 8. Fatigue Calculator Component

**Responsibility**: Calculate fatigue damage and adapt strategy accordingly.

**Interface**:
```typescript
interface FatigueCalculator {
  calculateFatigueDamage(turn: number): number
  isFatigueActive(turn: number): boolean
  turnsUntilFatigue(turn: number): number
  estimateSurvivalTurns(hp: number, armor: number, currentTurn: number): number
}
```

**Fatigue Mechanics**:
- Fatigue starts at turn 25
- Damage formula: `10 × 2^(turn - 25)`
- Turn 25: 10 damage
- Turn 26: 20 damage
- Turn 27: 40 damage
- Turn 28: 80 damage
- Turn 29: 160 damage
- Game typically ends by turn 29-30

**Heuristic Rules**:

**Negotiation Heuristics** (Intelligent Alliance Formation):
1. **Identify threats**: Find the strongest opponent (highest level + HP)
2. **Form strategic alliance**: Ally with 2nd strongest player to counter the threat
3. **Declare coordinated attack**: Signal attack on strongest opponent to ally
4. **If we're strongest**: Ally with weakest to protect them, attack 2nd strongest
5. **Never ally with someone attacking us**

**Combat Heuristics** (Winning Strategy):

**Turn 1-24 (Pre-Fatigue)**:
1. **Survival check**: If HP < 40, prioritize armor (amount = expected incoming damage + 10)
2. **Upgrade priority**: If resources ≥ upgrade cost AND level < 4, upgrade (better resource generation)
3. **Smart targeting**: 
   - Filter out destroyed towers (HP ≤ 0)
   - Attack weakest remaining opponent with 50% of remaining resources
   - If multiple weak opponents, spread attacks to eliminate multiple threats
4. **Resource conservation**: Keep 20% resources as buffer for next turn defense

**Turn 25+ (Fatigue Active)**:
1. **Fatigue damage calculation**: Turn N damage = 10 × 2^(N-25)
   - Turn 25: 10 damage
   - Turn 26: 20 damage
   - Turn 27: 40 damage
   - Turn 28: 80 damage
   - Turn 29: 160 damage (likely game over)
2. **Aggressive elimination**: Spend 80% of resources on attacks to eliminate opponents before fatigue kills everyone
3. **Minimal armor**: Only build armor if HP < 30 (survival critical)
4. **No upgrades**: No time for long-term investment
5. **Focus fire**: Attack single weakest opponent to eliminate them completely
6. **Endgame calculation**: If turn > 27, go all-in on attacks (game ending soon)

## Data Models

### Tower Model
```typescript
interface Tower {
  playerId: number
  hp: number
  armor: number
  resources: number
  level: number
}
```

### Game State Models
```typescript
interface NegotiationRequest {
  gameId: number
  turn: number
  playerTower: Tower
  enemyTowers: Tower[]
  combatActions: Array<{
    playerId: number
    action: {
      targetId: number
      troopCount: number
    }
  }>
}

interface CombatRequest {
  gameId: number
  turn: number
  playerTower: Tower
  enemyTowers: Tower[]
  diplomacy: Array<{
    playerId: number
    action: {
      allyId: number
      attackTargetId?: number
    }
  }>
  previousAttacks: Array<{
    playerId: number
    action: {
      targetId: number
      troopCount: number
    }
  }>
}
```

### Action Models
```typescript
type DiplomacyAction = {
  allyId: number
  attackTargetId?: number
}

type ArmorAction = {
  type: 'armor'
  amount: number
}

type AttackAction = {
  type: 'attack'
  targetId: number
  troopCount: number
}

type UpgradeAction = {
  type: 'upgrade'
}

type CombatAction = ArmorAction | AttackAction | UpgradeAction
```

### Configuration Model
```typescript
interface BotConfig {
  port: number
  bedrockRegion: string
  primaryModelId: string
  fallbackModelId: string
  requestTimeout: number
  aiTimeout: number
  logLevel: string
}
```

## Data Flow

### Negotiation Phase Flow
```
1. Game Engine → POST /negotiate with game state
2. HTTP Server → log "[KW-BOT] Mega ogudor"
3. Validator → validate request structure
4. Strategy Engine → analyze game state
5. Bedrock Client → invoke AI model with prompt
6. AI Model → return suggested diplomacy actions
7. Strategy Engine → parse and validate AI response
8. (If invalid) → Fallback Strategy generates actions
9. HTTP Server → return diplomacy actions as JSON
```

### Combat Phase Flow
```
1. Game Engine → POST /combat with game state
2. HTTP Server → log "[KW-BOT] Mega ogudor"
3. Validator → validate request structure
4. Strategy Engine → analyze game state
5. Bedrock Client → invoke AI model with prompt
6. AI Model → return suggested combat actions
7. Action Validator → validate actions against rules
8. Action Validator → verify resource constraints
9. (If invalid) → Fallback Strategy generates actions
10. HTTP Server → return combat actions as JSON
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Response Time Compliance
*For any* valid HTTP request to any endpoint, the Bot_Server should respond within 1 second.
**Validates: Requirements 1.2, 1.3, 8.1**

### Property 2: Diplomacy Action Uniqueness
*For any* negotiation response, there should be no duplicate allyId values in the returned diplomacy actions.
**Validates: Requirements 2.5**

### Property 3: Single Armor Action Constraint
*For any* combat response, there should be at most one action with type "armor".
**Validates: Requirements 3.4, 4.5**

### Property 4: Single Upgrade Action Constraint
*For any* combat response, there should be at most one action with type "upgrade".
**Validates: Requirements 3.5, 4.6**

### Property 5: Unique Attack Targets
*For any* combat response, all attack actions should have unique targetId values.
**Validates: Requirements 3.6, 4.7**

### Property 6: Armor Cost Calculation
*For any* armor action with amount N, the calculated cost should equal N × 1 resource.
**Validates: Requirements 4.1**

### Property 7: Attack Cost Calculation
*For any* attack action with troopCount N, the calculated cost should equal N × 1 resource.
**Validates: Requirements 4.2**

### Property 8: Upgrade Cost Calculation
*For any* tower at level N, the calculated upgrade cost should equal 50 × (1.75 ^ (N - 1)) resources, rounded to nearest integer.
**Validates: Requirements 4.3**

### Property 9: Resource Constraint Satisfaction
*For any* combat response and available resources R, the total cost of all actions should not exceed R.
**Validates: Requirements 4.4**

### Property 10: Resource Generation Formula
*For any* tower level N, the calculated resource generation should equal 20 × (1.5 ^ (N - 1)) rounded to nearest integer.
**Validates: Requirements 6.1**

### Property 11: Request Logging
*For any* HTTP request to any endpoint, the string "[KW-BOT] Mega ogudor" should appear in stdout.
**Validates: Requirements 1.5, 9.1**

### Property 12: Action Decision Logging
*For any* negotiation or combat request, the logs should contain information about the chosen actions.
**Validates: Requirements 9.2**

### Property 13: AI Call Logging
*For any* request that invokes Bedrock AI, the logs should contain information about the AI model call.
**Validates: Requirements 9.4**

### Property 14: No Attacks on Destroyed Towers
*For any* combat response, all attack actions should target towers with HP > 0.
**Validates: Requirements 3.6 (implicit - smart targeting)**

### Property 15: Fatigue Damage Calculation
*For any* turn number N ≥ 25, the calculated fatigue damage should equal 10 × 2^(N - 25).
**Validates: Requirements 7.1 (implicit - fatigue mechanics)**

### Property 16: Effective HP Calculation
*For any* tower with HP H and armor A, the calculated effective HP should equal H + A.
**Validates: Requirements 3.1 (implicit - threat assessment)**

## Error Handling

### Error Categories

**1. Request Validation Errors**
- Invalid JSON format
- Missing required fields
- Invalid data types
- Out-of-range values

**Handling**: Log error, return 200 with empty array `[]`

**2. AI Model Errors**
- Bedrock API timeout
- Model invocation failure
- Invalid model response
- Rate limiting

**Handling**: Log error, fall back to rule-based strategy, return valid actions

**3. Internal Processing Errors**
- Action validation failure
- Resource calculation error
- Unexpected exceptions

**Handling**: Log error with stack trace, return 200 with empty array `[]`

**4. Timeout Errors**
- Request processing exceeds 1 second

**Handling**: Abort processing, return 200 with empty array `[]`

### Error Response Strategy

**Never return HTTP error codes (4xx, 5xx)** - the game engine treats these as bot failures and may reject the entire turn. Instead:

1. Log the error with full context
2. Return HTTP 200
3. Return empty array `[]` as valid "no action" response
4. Ensure response is sent before 1-second timeout

### Graceful Degradation Path

```
Primary: AI-powered strategy
    ↓ (on AI failure)
Fallback: Rule-based heuristics
    ↓ (on validation failure)
Safe: Empty array (no actions)
```

## Testing Strategy

### Dual Testing Approach

The system will use both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
- Test specific endpoint responses (/healthz, /info)
- Test empty array responses for edge cases
- Test AI fallback behavior when models fail
- Test error handling paths
- Test server initialization

**Property-Based Tests**: Verify universal properties across all inputs
- Test response time compliance across random game states
- Test action uniqueness constraints across random responses
- Test cost calculations across random action sets
- Test resource constraints across random game states
- Test logging behavior across random requests

### Property-Based Testing Configuration

**Library**: Use `fast-check` (for TypeScript/JavaScript) or `hypothesis` (for Python)

**Test Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with: `Feature: kingdom-wars-bot, Property {N}: {property_text}`
- Generate random but valid game states for testing
- Use shrinking to find minimal failing examples

### Test Generators

**Game State Generator**:
```typescript
// Generate random valid game states
- gameId: random integer
- turn: random 1-50
- playerTower: random valid tower
- enemyTowers: array of 1-3 random valid towers
```

**Tower Generator**:
```typescript
// Generate random valid towers
- playerId: random unique integer
- hp: random 0-200
- armor: random 0-50
- resources: random 0-500
- level: random 1-5
```

**Action Generator**:
```typescript
// Generate random valid actions
- armor: random amount 1-100
- attack: random targetId from enemy list, troopCount 1-100
- upgrade: no parameters
```

### Integration Testing

**End-to-End Tests**:
1. Start bot server
2. Send sample negotiation request
3. Verify valid response format
4. Send sample combat request
5. Verify valid response format
6. Verify logs contain required output
7. Shutdown server

**Load Testing** (optional for hackathon):
- Use `autocannon` or `wrk` to simulate 100-150 req/s
- Verify response times remain under 1 second
- Monitor for memory leaks or resource exhaustion

### Manual Testing

**Test with Game Engine**:
1. Deploy bot to accessible endpoint
2. Register with game engine
3. Observe bot behavior in actual games
4. Review logs for strategy decisions
5. Iterate on AI prompts based on performance

### Test Coverage Goals

- Unit test coverage: >80% of code paths
- Property test coverage: All correctness properties implemented
- Integration test coverage: All endpoints tested
- Error path coverage: All error handlers tested

## Implementation Notes

### Technology Stack Recommendation

**Option 1: TypeScript + Express**
- Fast development
- Excellent AWS SDK support
- Good for hackathon speed
- Easy to deploy

**Option 2: Python + FastAPI**
- Clean async support
- Great for AI/ML integration
- Boto3 for Bedrock
- Slightly slower than Node.js

**Recommendation**: TypeScript + Express for fastest development and best performance.

### AWS Bedrock Setup

**Required IAM Permissions**:
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

**Environment Variables**:
```
AWS_REGION=eu-north-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
BOT_PORT=3000
PRIMARY_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
FALLBACK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### Deployment Considerations

**For Hackathon**:
- Deploy to AWS Lambda + API Gateway (serverless)
- Or deploy to EC2 in eu-north-1 (Stockholm) for lowest latency
- Or use AWS App Runner for quick deployment

**Performance Optimization**:
- Keep Lambda warm with scheduled pings
- Cache Bedrock client initialization
- Use connection pooling
- Minimize cold start time

### AI Prompt Engineering Tips

**Effective Prompt Structure**:
1. Role: "You are a strategic AI playing Kingdom Wars"
2. Context: Current game state in structured format
3. Constraints: Game rules and resource limits
4. Task: "Generate optimal actions as JSON"
5. Format: Example of expected JSON response

**Prompt Optimization**:
- Keep prompts concise (< 2000 tokens)
- Use structured data format (JSON in prompt)
- Include 1-2 examples of good responses
- Specify JSON schema for response
- Request reasoning before actions (chain-of-thought)

### Winning Strategy Insights

**Critical Success Factors**:
1. **Never attack destroyed towers** (HP ≤ 0) - wasted resources
2. **Monitor own HP constantly** - build armor before taking lethal damage
3. **Understand fatigue exponential growth** - game becomes elimination race after turn 25
4. **Upgrade early** - level 3-4 by turn 15 provides massive resource advantage
5. **Form smart alliances** - coordinate to eliminate strongest threat

**Early Game (Turns 1-10)**: Resource Growth Phase
- **Goal**: Reach level 3 as fast as possible
- **Strategy**:
  - Turn 1-2: Save resources, minimal attacks
  - Turn 3-5: Upgrade to level 2 (50 resources)
  - Turn 6-10: Upgrade to level 3 (88 resources)
  - Build armor only if HP < 60
  - Light attacks on weakest opponent to slow their growth
- **Resource generation target**: 45/turn by turn 10

**Mid Game (Turns 11-24)**: Dominance Phase
- **Goal**: Eliminate 1-2 opponents, reach level 4
- **Strategy**:
  - Upgrade to level 4 if resources allow (153 resources)
  - Focus attacks on weakest opponent until eliminated
  - Build armor to maintain HP > 50
  - Form alliance with 2nd place to attack 1st place
  - Coordinate attacks with ally via diplomacy
- **Target**: Reduce field to 2-3 players by turn 24

**Late Game (Turns 25+)**: Fatigue Survival Phase
- **Goal**: Be last tower standing
- **Critical**: Fatigue damage doubles each turn
  - Turn 25: 10 damage to all
  - Turn 26: 20 damage to all
  - Turn 27: 40 damage to all
  - Turn 28: 80 damage to all
  - Turn 29: 160 damage to all (game likely ends)
- **Strategy**:
  - **Turn 25-26**: Aggressive attacks, eliminate weakest opponent
  - **Turn 27**: All-in attacks, minimal armor
  - **Turn 28+**: Whoever has highest HP wins, focus fire on last opponent
  - **No upgrades** - no time for ROI
  - **Armor only if HP < 30** - otherwise attack
- **Win condition**: Eliminate all opponents before fatigue kills you

**AI Strategy Prompt Guidance**:
The AI should be prompted with:
- Current turn number and fatigue status
- All player HP values (identify who's closest to death)
- All player armor values (calculate effective HP)
- Resource availability and action costs
- Strategic objective based on game phase
- Explicit instruction: "Never attack towers with HP ≤ 0"
- Explicit instruction: "After turn 25, fatigue damage is 10 × 2^(turn-25)"
