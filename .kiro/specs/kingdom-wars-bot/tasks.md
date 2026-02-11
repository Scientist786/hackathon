# Implementation Plan: Kingdom Wars Bot

## Overview

This implementation plan focuses on building an AI-powered bot that thinks strategically and wins the Kingdom Wars game. The bot will use AWS Bedrock (Claude models) to analyze game state and make intelligent decisions about alliances, attacks, defense, and upgrades. Each task builds incrementally toward a complete, winning bot.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python project with FastAPI for HTTP server
  - Install dependencies: fastapi, uvicorn, boto3, pydantic
  - Create directory structure: src/, tests/, config/
  - Set up environment variables for AWS credentials and configuration
  - _Requirements: 8.4_

- [ ] 2. Implement core data models
  - [x] 2.1 Create Tower and GameState models using Pydantic
    - Define Tower model with playerId, hp, armor, resources, level
    - Define NegotiationRequest model with gameId, turn, playerTower, enemyTowers, combatActions
    - Define CombatRequest model with gameId, turn, playerTower, enemyTowers, diplomacy, previousAttacks
    - Define action models: DiplomacyAction, ArmorAction, AttackAction, UpgradeAction
    - _Requirements: 1.2, 1.3_

  - [x] 2.2 Write property test for data model validation
    - **Property 16: Effective HP Calculation**
    - **Validates: Requirements 3.1**

- [ ] 3. Implement game rules and calculations
  - [x] 3.1 Create ActionValidator class
    - Implement armor cost calculation (amount × 1)
    - Implement attack cost calculation (troopCount × 1)
    - Implement upgrade cost calculation (50 × 1.75^(level-1))
    - Implement total cost validation against available resources
    - Implement duplicate action detection (armor, upgrade, attack targets)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 3.2 Write property tests for cost calculations
    - **Property 6: Armor Cost Calculation**
    - **Property 7: Attack Cost Calculation**
    - **Property 8: Upgrade Cost Calculation**
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [x] 3.3 Write property test for resource constraints
    - **Property 9: Resource Constraint Satisfaction**
    - **Validates: Requirements 4.4**

  - [x] 3.4 Create FatigueCalculator class
    - Implement fatigue damage calculation: 10 × 2^(turn - 25)
    - Implement isFatigueActive check (turn ≥ 25)
    - Implement survival estimation based on HP, armor, and fatigue
    - _Requirements: 7.1, 7.2_

  - [x] 3.5 Write property test for fatigue calculation
    - **Property 15: Fatigue Damage Calculation**
    - **Validates: Requirements 7.1**

  - [x] 3.6 Create TargetSelector class
    - Implement filterAliveTowers (exclude HP ≤ 0)
    - Implement calculateEffectiveHP (HP + armor)
    - Implement findWeakestTower (lowest effective HP)
    - Implement findStrongestTower (highest level + effective HP)
    - _Requirements: 3.7, 6.1_

  - [x] 3.7 Write property test for target selection
    - **Property 14: No Attacks on Destroyed Towers**
    - **Validates: Requirements 3.7**

  - [x] 3.8 Create ResourceCalculator class
    - Implement resource generation formula: 20 × 1.5^(level - 1)
    - Round to nearest integer
    - _Requirements: 6.1_

  - [x] 3.9 Write property test for resource generation
    - **Property 10: Resource Generation Formula**
    - **Validates: Requirements 6.1**

- [x] 4. Checkpoint - Ensure all game rules tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement AWS Bedrock AI client
  - [x] 5.1 Create BedrockClient class
    - Initialize boto3 bedrock-runtime client
    - Implement invokeModel method with Claude 3.5 Sonnet
    - Implement retry logic with exponential backoff
    - Handle timeout and error cases
    - _Requirements: 5.1, 5.4_

  - [x] 5.2 Create PromptBuilder class for strategic AI prompts
    - Build negotiation prompt with game state, turn, fatigue status
    - Build combat prompt with complete game state and strategic context
    - Include instructions: never attack destroyed towers, consider fatigue
    - Include phase-specific strategy guidance (early/mid/late game)
    - Request JSON-formatted responses
    - _Requirements: 5.2_

  - [x] 5.3 Write unit tests for Bedrock client error handling
    - Test fallback behavior when AI fails
    - Test timeout handling
    - _Requirements: 5.4, 5.5_

- [ ] 6. Implement intelligent fallback strategy
  - [x] 6.1 Create FallbackStrategy class
    - Implement generateNegotiationActions with intelligent alliance logic
    - Identify strongest threat, form strategic alliance
    - Declare coordinated attack on strongest opponent
    - _Requirements: 2.2, 2.3_

  - [x] 6.2 Implement generateCombatActions with winning heuristics
    - Pre-fatigue strategy (turns 1-24): survival check, upgrade priority, smart targeting
    - Fatigue strategy (turns 25+): aggressive elimination, minimal armor, focus fire
    - Filter out destroyed towers before attacking
    - Calculate expected incoming damage for armor decisions
    - Prioritize actions: survival > upgrade (if early) > attack
    - _Requirements: 3.2, 7.2, 7.3_

  - [x] 6.3 Write unit tests for fallback strategy
    - Test early game strategy (upgrade focus)
    - Test mid game strategy (balanced)
    - Test late game strategy (aggressive)
    - Test survival scenarios (low HP)
    - _Requirements: 3.2, 7.2_

- [ ] 7. Implement core Strategy Engine with AI
  - [x] 7.1 Create StrategyEngine class
    - Implement decideNegotiation method
    - Call BedrockClient with negotiation prompt
    - Parse AI response into DiplomacyAction list
    - Validate no duplicate allyIds
    - Fall back to FallbackStrategy on AI failure
    - _Requirements: 2.1, 2.5, 5.3, 5.5_

  - [x] 7.2 Implement decideCombat method
    - Call BedrockClient with combat prompt including strategic context
    - Parse AI response into CombatAction list
    - Validate actions with ActionValidator
    - Filter out attacks on destroyed towers
    - Fall back to FallbackStrategy on AI failure or invalid actions
    - _Requirements: 3.1, 3.3, 3.4, 3.5, 3.6, 3.7, 5.3, 5.5_

  - [x] 7.3 Write property tests for action constraints
    - **Property 3: Single Armor Action Constraint**
    - **Property 4: Single Upgrade Action Constraint**
    - **Property 5: Unique Attack Targets**
    - **Validates: Requirements 3.4, 3.5, 3.6, 4.5, 4.6, 4.7**

  - [x] 7.4 Write property test for diplomacy uniqueness
    - **Property 2: Diplomacy Action Uniqueness**
    - **Validates: Requirements 2.5**

- [x] 8. Checkpoint - Ensure strategy engine works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement HTTP server endpoints
  - [x] 9.1 Create FastAPI application with logging middleware
    - Set up FastAPI app
    - Add middleware to log "[KW-BOT] Mega ogudor" on every request
    - Add request timeout middleware (1 second)
    - _Requirements: 1.5, 8.1, 9.1_

  - [x] 9.2 Implement GET /healthz endpoint
    - Return {"status": "OK"} with 200 status
    - _Requirements: 1.1_

  - [x] 9.3 Implement GET /info endpoint
    - Return bot metadata: name, strategy "AI-trapped-strategy", version
    - _Requirements: 1.4_

  - [x] 9.4 Implement POST /negotiate endpoint
    - Validate request body with Pydantic
    - Call StrategyEngine.decideNegotiation
    - Log chosen actions and reasoning
    - Return diplomacy actions as JSON
    - Handle errors gracefully (return empty array)
    - _Requirements: 1.2, 9.2_

  - [x] 9.5 Implement POST /combat endpoint
    - Validate request body with Pydantic
    - Call StrategyEngine.decideCombat
    - Log chosen actions and reasoning
    - Return combat actions as JSON
    - Handle errors gracefully (return empty array)
    - _Requirements: 1.3, 9.2_

  - [x] 9.6 Write unit tests for HTTP endpoints
    - Test /healthz returns correct response
    - Test /info returns correct metadata
    - Test /negotiate with sample game state
    - Test /combat with sample game state
    - Test error handling returns empty array
    - _Requirements: 1.1, 1.4, 2.4, 3.7, 8.3_

  - [x] 9.7 Write property tests for response time and logging
    - **Property 1: Response Time Compliance**
    - **Property 11: Request Logging**
    - **Validates: Requirements 1.2, 1.3, 1.5, 8.1, 9.1**

- [ ] 10. Implement comprehensive logging
  - [x] 10.1 Set up structured logging
    - Configure Python logging with JSON format
    - Log game state on each request
    - Log AI prompts and responses
    - Log chosen actions with reasoning
    - Log errors with full context
    - _Requirements: 9.2, 9.3, 9.4_

  - [x] 10.2 Write property tests for logging
    - **Property 12: Action Decision Logging**
    - **Property 13: AI Call Logging**
    - **Validates: Requirements 9.2, 9.4**

- [ ] 11. Create configuration and deployment setup
  - [x] 11.1 Create configuration file
    - Define environment variables: AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    - Define bot configuration: PORT, PRIMARY_MODEL_ID, FALLBACK_MODEL_ID
    - Set default values for eu-north-1 region
    - _Requirements: 8.4_

  - [x] 11.2 Create main.py entry point
    - Initialize all components (BedrockClient, StrategyEngine, etc.)
    - Start FastAPI server with uvicorn
    - Handle graceful shutdown
    - _Requirements: 8.4_

  - [x] 11.3 Create requirements.txt
    - List all Python dependencies with versions
    - Include: fastapi, uvicorn, boto3, pydantic, hypothesis (for property tests)

  - [x] 11.4 Create README with deployment instructions
    - Document environment variables
    - Document how to run locally
    - Document how to deploy to AWS (Lambda or EC2)
    - Include example requests for testing

- [ ] 12. Integration testing and refinement
  - [x] 12.1 Write integration tests
    - Test complete negotiation flow
    - Test complete combat flow
    - Test AI fallback scenarios
    - Test error handling end-to-end
    - _Requirements: 1.2, 1.3, 5.4, 5.5, 8.3_

  - [x] 12.2 Manual testing with sample game states
    - Test early game scenarios (turns 1-10)
    - Test mid game scenarios (turns 11-24)
    - Test fatigue scenarios (turns 25+)
    - Test low HP survival scenarios
    - Test destroyed tower filtering
    - Verify AI makes intelligent decisions
    - _Requirements: 3.7, 7.1, 7.2, 7.3_

- [x] 13. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.
  - Verify bot responds within 1 second
  - Verify bot never attacks destroyed towers
  - Verify bot adapts strategy based on game phase
  - Verify bot makes intelligent upgrade decisions
  - Verify bot handles fatigue correctly

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Focus is on building an AI that thinks strategically and wins
- The bot must never attack destroyed towers (HP ≤ 0)
- The bot must understand fatigue mechanics and adapt strategy
- The bot must make intelligent upgrade decisions for resource growth
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
