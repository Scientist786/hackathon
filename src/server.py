"""FastAPI server for Kingdom Wars Bot."""
import sys
import logging
import time
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from typing import List
from src.models import (
    HealthCheck, BotInfo, NegotiationRequest, CombatRequest,
    DiplomacyAction, CombatAction
)
from src.strategy_engine import StrategyEngine
from src.bedrock_client import BedrockClient
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Kingdom Wars Bot",
    description="AI-powered strategic bot for Kingdom Wars",
    version=settings.bot_version
)

# Initialize components
bedrock_client = None
strategy_engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global bedrock_client, strategy_engine
    
    logger.info("Starting Kingdom Wars Bot...")
    logger.info(f"Bot Name: {settings.bot_name}")
    logger.info(f"Bot Strategy: {settings.bot_strategy}")
    logger.info(f"AWS Region: {settings.aws_region}")
    
    # Initialize Bedrock client
    try:
        bedrock_client = BedrockClient(
            region=settings.aws_region,
            primary_model_id=settings.primary_model_id,
            fallback_model_id=settings.fallback_model_id,
            timeout=settings.ai_timeout
        )
        logger.info("Bedrock client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock client: {e}")
        logger.warning("Bot will use fallback strategy only")
        bedrock_client = None
    
    # Initialize strategy engine
    strategy_engine = StrategyEngine(bedrock_client=bedrock_client)
    logger.info("Strategy engine initialized")
    
    logger.info("Kingdom Wars Bot ready!")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests.
    
    CRITICAL: Must print "[KW-BOT] Mega ogudor" for every request.
    """
    # Print required log message
    print(f"[KW-BOT] {settings.bot_name}")
    
    # Log request details
    logger.info(f"{request.method} {request.url.path}")
    
    # Process request with timeout
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Log response time
        duration = time.time() - start_time
        logger.info(f"Request completed in {duration:.3f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Request failed: {e}")
        # Return empty array on error (valid "no action" response)
        return JSONResponse(
            status_code=200,
            content=[]
        )


@app.get("/healthz", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        {"status": "OK"}
    """
    return HealthCheck(status="OK")


@app.get("/info", response_model=BotInfo)
async def bot_info():
    """
    Bot metadata endpoint.
    
    Returns:
        Bot name, strategy, and version
    """
    return BotInfo(
        name=settings.bot_name,
        strategy=settings.bot_strategy,
        version=settings.bot_version
    )


@app.post("/negotiate")
async def negotiate(request: NegotiationRequest) -> List[DiplomacyAction]:
    """
    Negotiation phase endpoint.
    
    Receives game state and returns diplomacy actions.
    
    Args:
        request: Negotiation request with game state
    
    Returns:
        List of diplomacy actions (or empty array)
    """
    try:
        logger.info(f"Negotiation request: Game {request.gameId}, Turn {request.turn}")
        logger.info(f"Player: HP={request.playerTower.hp}, Resources={request.playerTower.resources}, Level={request.playerTower.level}")
        logger.info(f"Enemies: {len(request.enemyTowers)} towers")
        
        # Decide actions using strategy engine
        actions = await strategy_engine.decide_negotiation(request)
        
        logger.info(f"Negotiation response: {len(actions)} actions")
        for action in actions:
            logger.info(f"  - Ally with {action.allyId}, attack {action.attackTargetId}")
        
        return actions
        
    except Exception as e:
        logger.error(f"Error in negotiation: {e}", exc_info=True)
        # Return empty array on error
        return []


@app.post("/combat")
async def combat(request: CombatRequest) -> List[CombatAction]:
    """
    Combat phase endpoint.
    
    Receives game state and returns combat actions.
    
    Args:
        request: Combat request with game state
    
    Returns:
        List of combat actions (or empty array)
    """
    try:
        logger.info(f"Combat request: Game {request.gameId}, Turn {request.turn}")
        logger.info(f"Player: HP={request.playerTower.hp}, Armor={request.playerTower.armor}, Resources={request.playerTower.resources}, Level={request.playerTower.level}")
        logger.info(f"Enemies: {len(request.enemyTowers)} towers")
        
        # Decide actions using strategy engine
        actions = await strategy_engine.decide_combat(request)
        
        logger.info(f"Combat response: {len(actions)} actions")
        for action in actions:
            if hasattr(action, 'amount'):
                logger.info(f"  - {action.type}: amount={action.amount}")
            elif hasattr(action, 'targetId'):
                logger.info(f"  - {action.type}: target={action.targetId}, troops={action.troopCount}")
            else:
                logger.info(f"  - {action.type}")
        
        return actions
        
    except Exception as e:
        logger.error(f"Error in combat: {e}", exc_info=True)
        # Return empty array on error
        return []


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    
    Returns empty array on any error to avoid game engine rejection.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content=[]
    )
