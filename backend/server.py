from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime
from enum import Enum
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Global Dynamics - Globalization Education Game")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums for game mechanics
class DecisionType(str, Enum):
    TRADE = "trade"
    CULTURAL = "cultural"
    ENVIRONMENTAL = "environmental"
    BUSINESS = "business"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# Game Models
class EconomicIndicators(BaseModel):
    gdp: float = Field(default=1000.0, description="Gross Domestic Product")
    trade_balance: float = Field(default=0.0, description="Trade balance (exports - imports)")
    unemployment: float = Field(default=5.0, description="Unemployment percentage")
    inflation: float = Field(default=2.0, description="Inflation rate")
    
class EnvironmentalIndicators(BaseModel):
    carbon_emissions: float = Field(default=100.0, description="Carbon emissions level")
    renewable_energy: float = Field(default=20.0, description="Renewable energy percentage")
    pollution_level: float = Field(default=50.0, description="Overall pollution level")
    sustainability_score: float = Field(default=40.0, description="Sustainability score out of 100")

class CulturalIndicators(BaseModel):
    diversity_index: float = Field(default=50.0, description="Cultural diversity index")
    international_relations: Dict[str, float] = Field(default_factory=dict, description="Relations with other countries")
    cultural_events_hosted: int = Field(default=0, description="Number of cultural events hosted")
    cultural_openness: float = Field(default=50.0, description="Openness to other cultures")

class Country(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    region: str
    population: int
    economic_indicators: EconomicIndicators = Field(default_factory=EconomicIndicators)
    environmental_indicators: EnvironmentalIndicators = Field(default_factory=EnvironmentalIndicators)
    cultural_indicators: CulturalIndicators = Field(default_factory=CulturalIndicators)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    country_id: str
    score: int = Field(default=0)
    level: int = Field(default=1)
    decisions_made: int = Field(default=0)
    achievements: List[str] = Field(default_factory=list)
    knowledge_points: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Decision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    decision_type: DecisionType
    scenario_id: str
    choice_made: str
    consequences: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GameScenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    decision_type: DecisionType
    choices: List[Dict[str, str]]
    consequences: Dict[str, Dict[str, float]]
    difficulty: DifficultyLevel
    historical_context: str
    educational_content: str

class HistoricalFact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    category: str
    year: Optional[int] = None
    relevance_tags: List[str] = Field(default_factory=list)

class TriviaQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    category: str
    difficulty: DifficultyLevel

# Request Models
class PlayerCreate(BaseModel):
    name: str
    country_name: str

class DecisionCreate(BaseModel):
    player_id: str
    scenario_id: str
    choice_index: int

class GameState(BaseModel):
    player: Player
    country: Country
    current_scenario: Optional[GameScenario] = None
    available_scenarios: List[GameScenario] = Field(default_factory=list)
    recent_decisions: List[Decision] = Field(default_factory=list)

# Initialize sample data
SAMPLE_COUNTRIES = [
    {"name": "United States", "region": "North America", "population": 331000000},
    {"name": "China", "region": "Asia", "population": 1441000000},
    {"name": "Germany", "region": "Europe", "population": 83000000},
    {"name": "Brazil", "region": "South America", "population": 213000000},
    {"name": "India", "region": "Asia", "population": 1380000000},
    {"name": "Nigeria", "region": "Africa", "population": 206000000},
]

SAMPLE_SCENARIOS = [
    {
        "title": "Trade Agreement Proposal",
        "description": "A neighboring country proposes a free trade agreement that would increase exports but may hurt local industries.",
        "decision_type": "trade",
        "choices": [
            {"id": "accept", "text": "Accept the trade agreement"},
            {"id": "negotiate", "text": "Negotiate for better terms"},
            {"id": "reject", "text": "Reject the agreement"}
        ],
        "consequences": {
            "accept": {"gdp": 50, "unemployment": 10, "trade_balance": 30},
            "negotiate": {"gdp": 25, "unemployment": 5, "trade_balance": 15},
            "reject": {"gdp": -10, "trade_balance": -5, "cultural_openness": -10}
        },
        "difficulty": "medium",
        "historical_context": "Similar to NAFTA negotiations in the 1990s",
        "educational_content": "Free trade agreements can boost economic growth but may displace workers in certain industries."
    },
    {
        "title": "Cultural Festival Invitation",
        "description": "Your country is invited to host an international cultural festival, promoting global understanding but requiring significant investment.",
        "decision_type": "cultural",
        "choices": [
            {"id": "host", "text": "Host the festival with full investment"},
            {"id": "participate", "text": "Participate but not host"},
            {"id": "decline", "text": "Decline the invitation"}
        ],
        "consequences": {
            "host": {"cultural_openness": 40, "diversity_index": 30, "gdp": -20},
            "participate": {"cultural_openness": 20, "diversity_index": 15, "gdp": -5},
            "decline": {"cultural_openness": -15, "international_relations": -10}
        },
        "difficulty": "easy",
        "historical_context": "Similar to Olympic Games or World Expo hosting decisions",
        "educational_content": "Cultural exchanges promote international understanding and soft power but require significant resources."
    },
    {
        "title": "Green Technology Investment",
        "description": "A choice between investing in renewable energy or expanding traditional manufacturing to boost short-term economic growth.",
        "decision_type": "environmental",
        "choices": [
            {"id": "green", "text": "Invest heavily in green technology"},
            {"id": "balanced", "text": "Balanced approach to both"},
            {"id": "traditional", "text": "Focus on traditional manufacturing"}
        ],
        "consequences": {
            "green": {"renewable_energy": 50, "carbon_emissions": -30, "gdp": -10, "sustainability_score": 40},
            "balanced": {"renewable_energy": 25, "carbon_emissions": -10, "gdp": 10, "sustainability_score": 20},
            "traditional": {"gdp": 40, "carbon_emissions": 30, "pollution_level": 20, "sustainability_score": -30}
        },
        "difficulty": "hard",
        "historical_context": "Similar to Germany's Energiewende (energy transition) policy",
        "educational_content": "Environmental policies often involve trade-offs between short-term economic costs and long-term sustainability benefits."
    }
]

SAMPLE_HISTORICAL_FACTS = [
    {
        "title": "The Silk Road",
        "content": "The ancient Silk Road was one of the first examples of globalization, connecting Asia and Europe through trade routes that exchanged not just goods, but ideas, technologies, and cultures.",
        "category": "trade",
        "year": -130,
        "relevance_tags": ["trade", "cultural_exchange", "ancient_globalization"]
    },
    {
        "title": "The Bretton Woods System",
        "content": "Established in 1944, the Bretton Woods system created the modern international monetary system and institutions like the IMF and World Bank, shaping global economic integration.",
        "category": "business",
        "year": 1944,
        "relevance_tags": ["international_finance", "global_institutions", "economic_cooperation"]
    }
]

SAMPLE_TRIVIA = [
    {
        "question": "Which organization was created to promote free trade worldwide?",
        "options": ["United Nations", "World Trade Organization", "International Monetary Fund", "World Bank"],
        "correct_answer": 1,
        "explanation": "The World Trade Organization (WTO) was established in 1995 to facilitate free trade between nations.",
        "category": "trade",
        "difficulty": "medium"
    }
]

# Game Logic Functions
def calculate_consequences(country: Country, consequences: Dict[str, float]) -> Country:
    """Apply decision consequences to country indicators"""
    updated_country = country.copy(deep=True)
    
    for indicator, change in consequences.items():
        if hasattr(updated_country.economic_indicators, indicator):
            current_value = getattr(updated_country.economic_indicators, indicator)
            setattr(updated_country.economic_indicators, indicator, max(0, current_value + change))
        elif hasattr(updated_country.environmental_indicators, indicator):
            current_value = getattr(updated_country.environmental_indicators, indicator)
            setattr(updated_country.environmental_indicators, indicator, max(0, current_value + change))
        elif hasattr(updated_country.cultural_indicators, indicator):
            current_value = getattr(updated_country.cultural_indicators, indicator)
            setattr(updated_country.cultural_indicators, indicator, max(0, current_value + change))
    
    return updated_country

def calculate_score(decision: Decision, consequences: Dict[str, float]) -> int:
    """Calculate score based on decision quality and consequences"""
    base_score = 10
    
    # Positive consequences add to score
    positive_impact = sum(max(0, value) for value in consequences.values())
    negative_impact = sum(min(0, value) for value in consequences.values())
    
    return max(1, int(base_score + positive_impact - abs(negative_impact)))

async def get_random_scenario(decision_type: Optional[DecisionType] = None) -> GameScenario:
    """Get a random scenario, optionally filtered by type"""
    scenarios = await db.scenarios.find().to_list(100)
    if not scenarios:
        # If no scenarios in DB, use sample data
        scenarios = SAMPLE_SCENARIOS
    
    if decision_type:
        scenarios = [s for s in scenarios if s.get("decision_type") == decision_type]
    
    if scenarios:
        scenario_data = random.choice(scenarios)
        return GameScenario(**scenario_data)
    
    # Fallback scenario
    return GameScenario(**SAMPLE_SCENARIOS[0])

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Global Dynamics - Globalization Education Game API"}

@api_router.post("/player", response_model=Player)
async def create_player(player_data: PlayerCreate):
    """Create a new player and assign them a country"""
    
    # Find or create country
    country = await db.countries.find_one({"name": player_data.country_name})
    if not country:
        # Create new country with sample data
        country_sample = next((c for c in SAMPLE_COUNTRIES if c["name"] == player_data.country_name), None)
        if not country_sample:
            raise HTTPException(status_code=400, detail="Country not found")
        
        country_obj = Country(**country_sample)
        await db.countries.insert_one(country_obj.dict())
        country_id = country_obj.id
    else:
        country_id = country["id"]
    
    # Create player
    player = Player(name=player_data.name, country_id=country_id)
    await db.players.insert_one(player.dict())
    
    return player

@api_router.get("/countries", response_model=List[Dict])
async def get_available_countries():
    """Get list of available countries"""
    return [{"name": c["name"], "region": c["region"]} for c in SAMPLE_COUNTRIES]

@api_router.get("/game-state/{player_id}", response_model=GameState)
async def get_game_state(player_id: str):
    """Get current game state for a player"""
    
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    country = await db.countries.find_one({"id": player["country_id"]})
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Get current scenario
    current_scenario = await get_random_scenario()
    
    # Get recent decisions
    recent_decisions = await db.decisions.find({"player_id": player_id}).sort("timestamp", -1).limit(5).to_list(5)
    
    return GameState(
        player=Player(**player),
        country=Country(**country),
        current_scenario=current_scenario,
        recent_decisions=[Decision(**d) for d in recent_decisions]
    )

@api_router.post("/decision", response_model=Dict)
async def make_decision(decision_data: DecisionCreate):
    """Process a player's decision and update game state"""
    
    # Get player and country
    player = await db.players.find_one({"id": decision_data.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    country = await db.countries.find_one({"id": player["country_id"]})
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Get scenario (for now use sample data)
    scenario_data = next((s for s in SAMPLE_SCENARIOS if s.get("title", "") == decision_data.scenario_id), SAMPLE_SCENARIOS[0])
    scenario = GameScenario(**scenario_data)
    
    # Get chosen option
    if decision_data.choice_index >= len(scenario.choices):
        raise HTTPException(status_code=400, detail="Invalid choice")
    
    choice = scenario.choices[decision_data.choice_index]
    consequences = scenario.consequences.get(choice["id"], {})
    
    # Apply consequences to country
    country_obj = Country(**country)
    updated_country = calculate_consequences(country_obj, consequences)
    
    # Create decision record
    decision = Decision(
        player_id=decision_data.player_id,
        decision_type=scenario.decision_type,
        scenario_id=scenario.id,
        choice_made=choice["text"],
        consequences=consequences
    )
    
    # Calculate score
    score_gained = calculate_score(decision, consequences)
    
    # Update player
    updated_player = Player(**player)
    updated_player.score += score_gained
    updated_player.decisions_made += 1
    updated_player.knowledge_points += 5
    
    # Save updates
    await db.countries.replace_one({"id": country["id"]}, updated_country.dict())
    await db.players.replace_one({"id": player["id"]}, updated_player.dict())
    await db.decisions.insert_one(decision.dict())
    
    # Get educational content
    educational_fact = random.choice(SAMPLE_HISTORICAL_FACTS)
    trivia_question = random.choice(SAMPLE_TRIVIA)
    
    return {
        "success": True,
        "score_gained": score_gained,
        "consequences": consequences,
        "educational_content": {
            "scenario_context": scenario.educational_content,
            "historical_fact": educational_fact,
            "trivia_question": trivia_question
        },
        "updated_indicators": {
            "economic": updated_country.economic_indicators.dict(),
            "environmental": updated_country.environmental_indicators.dict(),
            "cultural": updated_country.cultural_indicators.dict()
        }
    }

@api_router.get("/scenarios/{decision_type}")
async def get_scenarios_by_type(decision_type: DecisionType):
    """Get scenarios filtered by decision type"""
    scenario = await get_random_scenario(decision_type)
    return scenario

@api_router.get("/educational-content/facts", response_model=List[HistoricalFact])
async def get_historical_facts():
    """Get historical facts for educational content"""
    facts = await db.historical_facts.find().to_list(50)
    if not facts:
        return [HistoricalFact(**fact) for fact in SAMPLE_HISTORICAL_FACTS]
    return [HistoricalFact(**fact) for fact in facts]

@api_router.get("/educational-content/trivia", response_model=List[TriviaQuestion])
async def get_trivia_questions():
    """Get trivia questions for educational content"""
    questions = await db.trivia_questions.find().to_list(50)
    if not questions:
        return [TriviaQuestion(**q) for q in SAMPLE_TRIVIA]
    return [TriviaQuestion(**q) for q in questions]

@api_router.get("/leaderboard", response_model=List[Dict])
async def get_leaderboard():
    """Get top players leaderboard"""
    players = await db.players.find().sort("score", -1).limit(10).to_list(10)
    return [
        {
            "name": player["name"],
            "score": player["score"],
            "level": player["level"],
            "decisions_made": player["decisions_made"]
        }
        for player in players
    ]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data"""
    logger.info("Starting Global Dynamics API...")
    
    # Initialize sample data if collections are empty
    if await db.countries.count_documents({}) == 0:
        countries = [Country(**country_data) for country_data in SAMPLE_COUNTRIES]
        await db.countries.insert_many([country.dict() for country in countries])
        logger.info("Initialized sample countries")
    
    if await db.scenarios.count_documents({}) == 0:
        scenarios = [GameScenario(**scenario_data) for scenario_data in SAMPLE_SCENARIOS]
        await db.scenarios.insert_many([scenario.dict() for scenario in scenarios])
        logger.info("Initialized sample scenarios")
    
    if await db.historical_facts.count_documents({}) == 0:
        facts = [HistoricalFact(**fact_data) for fact_data in SAMPLE_HISTORICAL_FACTS]
        await db.historical_facts.insert_many([fact.dict() for fact in facts])
        logger.info("Initialized historical facts")
    
    if await db.trivia_questions.count_documents({}) == 0:
        questions = [TriviaQuestion(**q_data) for q_data in SAMPLE_TRIVIA]
        await db.trivia_questions.insert_many([question.dict() for question in questions])
        logger.info("Initialized trivia questions")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
