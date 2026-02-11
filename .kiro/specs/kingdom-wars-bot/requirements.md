# Requirements Document

## Introduction

Kingdom Wars Bot is an AI-powered HTTP server that plays a multiplayer tower defense game. The bot must make strategic decisions during negotiation and combat phases to be the last tower standing among 4 players. The bot will leverage AWS Bedrock AI models to analyze game state and make optimal tactical decisions.

## Glossary

- **Tower**: A player's structure with HP, armor, resources, and level
- **Bot_Server**: The HTTP server that implements the game AI
- **Game_Engine**: The external system that orchestrates the game and sends requests
- **Negotiation_Phase**: Game phase where players declare alliances and attack intentions
- **Combat_Phase**: Game phase where players execute actions (attack, armor, upgrade)
- **Bedrock_Client**: AWS Bedrock service client for AI model inference
- **Strategy_Engine**: Component that uses AI to determine optimal actions
- **Resource**: In-game currency used for actions (attack, upgrade, armor)
- **Fatigue**: Escalating damage applied to all towers after turn 25

## Requirements

### Requirement 1: HTTP Server Interface

**User Story:** As the Game Engine, I want to communicate with the bot via HTTP endpoints, so that I can orchestrate game phases and receive bot actions.

#### Acceptance Criteria

1. WHEN the Game Engine sends a GET request to /healthz, THEN the Bot_Server SHALL respond with status 200 and JSON body {"status": "OK"}
2. WHEN the Game Engine sends a POST request to /negotiate, THEN the Bot_Server SHALL respond within 1 second with valid diplomacy actions
3. WHEN the Game Engine sends a POST request to /combat, THEN the Bot_Server SHALL respond within 1 second with valid combat actions
4. WHEN the Game Engine sends a GET request to /info, THEN the Bot_Server SHALL respond with bot metadata including name, strategy "AI-trapped-strategy", and version
5. WHEN any request is received, THEN the Bot_Server SHALL print "[KW-BOT] Mega ogudor" to stdout

### Requirement 2: Negotiation Strategy

**User Story:** As a bot player, I want to make strategic alliance and attack declarations, so that I can coordinate with allies and signal intentions to enemies.

#### Acceptance Criteria

1. WHEN the negotiation phase begins, THEN the Strategy_Engine SHALL analyze all enemy tower states and combat actions
2. WHEN determining alliances, THEN the Strategy_Engine SHALL identify potential allies based on mutual threats and relative strength
3. WHEN declaring attack intentions, THEN the Strategy_Engine SHALL signal targets to coordinate with allies
4. WHEN no beneficial diplomacy exists, THEN the Bot_Server SHALL return an empty array
5. WHEN multiple messages to the same allyId are attempted, THEN the Bot_Server SHALL prevent duplicate messages

### Requirement 3: Combat Decision Making

**User Story:** As a bot player, I want to make optimal combat decisions using AI analysis, so that I can maximize my chances of winning.

#### Acceptance Criteria

1. WHEN the combat phase begins, THEN the Strategy_Engine SHALL analyze current game state including player tower, enemy towers, diplomacy, and previous attacks
2. WHEN resources are available, THEN the Strategy_Engine SHALL evaluate all possible action combinations (armor, attack, upgrade)
3. WHEN determining actions, THEN the Strategy_Engine SHALL use Bedrock AI models to predict optimal strategy
4. WHEN armor is needed, THEN the Bot_Server SHALL include at most one armor action per combat phase
5. WHEN upgrading, THEN the Bot_Server SHALL include at most one upgrade action per combat phase
6. WHEN attacking, THEN the Bot_Server SHALL prevent multiple attacks with identical targetId
7. WHEN selecting attack targets, THEN the Bot_Server SHALL only target towers with HP > 0
8. WHEN no beneficial actions exist, THEN the Bot_Server SHALL return an empty array

### Requirement 4: Game Rules Validation

**User Story:** As a bot developer, I want all actions to be validated against game rules, so that invalid responses don't cause the entire turn to be rejected.

#### Acceptance Criteria

1. WHEN building armor, THEN the Bot_Server SHALL verify cost equals amount × 1 resource
2. WHEN attacking, THEN the Bot_Server SHALL verify cost equals troopCount × 1 resource
3. WHEN upgrading from level N, THEN the Bot_Server SHALL verify cost equals 50 × (1.75 ^ (N - 1)) resources
4. WHEN total action costs are calculated, THEN the Bot_Server SHALL verify total does not exceed available resources
5. WHEN actions are generated, THEN the Bot_Server SHALL validate no duplicate armor actions exist
6. WHEN actions are generated, THEN the Bot_Server SHALL validate no duplicate upgrade actions exist
7. WHEN actions are generated, THEN the Bot_Server SHALL validate no duplicate attack targetIds exist

### Requirement 5: AI Strategy Integration

**User Story:** As a bot player, I want to leverage AWS Bedrock AI models for strategic decision making, so that I can make intelligent, adaptive choices.

#### Acceptance Criteria

1. WHEN the Strategy_Engine needs to make decisions, THEN it SHALL invoke Bedrock AI models with game state context
2. WHEN constructing AI prompts, THEN the Strategy_Engine SHALL include current turn, tower states, resources, diplomacy, and game phase
3. WHEN receiving AI responses, THEN the Strategy_Engine SHALL parse and validate suggested actions
4. WHEN AI model calls fail, THEN the Strategy_Engine SHALL fall back to rule-based heuristics
5. WHEN AI responses are invalid, THEN the Strategy_Engine SHALL use fallback logic to generate valid actions

### Requirement 6: Resource Management

**User Story:** As a bot player, I want to track and manage resources accurately, so that I can plan multi-turn strategies.

#### Acceptance Criteria

1. WHEN calculating resource generation, THEN the Bot_Server SHALL use formula 20 × (1.5 ^ (level - 1)) rounded to nearest integer
2. WHEN planning actions, THEN the Strategy_Engine SHALL account for resource generation in next turn
3. WHEN evaluating upgrade timing, THEN the Strategy_Engine SHALL consider resource generation increase versus immediate combat needs
4. WHEN resources are insufficient for desired actions, THEN the Strategy_Engine SHALL prioritize actions by strategic value

### Requirement 7: Fatigue Handling

**User Story:** As a bot player, I want to adapt strategy when fatigue begins, so that I can survive the endgame.

#### Acceptance Criteria

1. WHEN calculating fatigue damage for turn N ≥ 25, THEN the Bot_Server SHALL use formula 10 × 2^(N - 25)
2. WHEN turn number is 25 or greater, THEN the Strategy_Engine SHALL factor fatigue damage into survival calculations
3. WHEN fatigue is active, THEN the Strategy_Engine SHALL prioritize aggressive actions to eliminate opponents quickly
4. WHEN multiple towers remain after turn 25, THEN the Strategy_Engine SHALL evaluate armor investment versus offensive pressure

### Requirement 8: Performance and Reliability

**User Story:** As the Game Engine, I want the bot to respond quickly and reliably, so that games proceed smoothly.

#### Acceptance Criteria

1. WHEN any endpoint receives a request, THEN the Bot_Server SHALL respond within 1 second
2. WHEN the Bot_Server handles 100-150 requests per second, THEN it SHALL maintain response time requirements
3. WHEN errors occur during processing, THEN the Bot_Server SHALL log errors and return valid empty response rather than timing out
4. WHEN the Bot_Server starts, THEN it SHALL initialize all dependencies before accepting requests

### Requirement 9: Logging and Observability

**User Story:** As a bot developer, I want comprehensive logging, so that I can debug strategies and analyze game performance.

#### Acceptance Criteria

1. WHEN any request is received, THEN the Bot_Server SHALL print "[KW-BOT] Mega ogudor" to stdout
2. WHEN actions are decided, THEN the Bot_Server SHALL log the reasoning and chosen actions
3. WHEN errors occur, THEN the Bot_Server SHALL log error details with context
4. WHEN AI model calls are made, THEN the Bot_Server SHALL log prompts and responses for analysis
