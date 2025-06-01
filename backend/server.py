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
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    HUMAN_RESOURCES = "human_resources"
    MARKETING = "marketing"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class MaterialType(str, Enum):
    LOCAL_SUSTAINABLE = "local_sustainable"
    LOCAL_STANDARD = "local_standard"
    INTERNATIONAL_CHEAP = "international_cheap"
    INTERNATIONAL_PREMIUM = "international_premium"

class ShipmentMethod(str, Enum):
    AIR_EXPRESS = "air_express"
    AIR_STANDARD = "air_standard"
    SEA_FREIGHT = "sea_freight"
    LAND_TRANSPORT = "land_transport"
    MULTIMODAL = "multimodal"

# Enhanced Game Models
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

class BusinessIndicators(BaseModel):
    production_efficiency: float = Field(default=70.0, description="Production efficiency percentage")
    supply_chain_resilience: float = Field(default=60.0, description="Supply chain resilience score")
    employee_satisfaction: float = Field(default=65.0, description="Employee satisfaction index")
    brand_reputation: float = Field(default=70.0, description="Brand reputation score")
    profit_margin: float = Field(default=15.0, description="Profit margin percentage")
    market_share: float = Field(default=10.0, description="Market share percentage")
    innovation_index: float = Field(default=50.0, description="Innovation capability index")

class ManufacturingMetrics(BaseModel):
    factory_count: int = Field(default=1, description="Number of factories")
    total_employees: int = Field(default=500, description="Total number of employees")
    average_salary: float = Field(default=45000.0, description="Average annual salary in USD")
    working_conditions_score: float = Field(default=70.0, description="Working conditions quality score")
    automation_level: float = Field(default=30.0, description="Automation level percentage")
    production_capacity: float = Field(default=1000.0, description="Production capacity units per day")

class LogisticsMetrics(BaseModel):
    shipping_cost_per_unit: float = Field(default=5.0, description="Average shipping cost per unit")
    delivery_time_days: float = Field(default=14.0, description="Average delivery time in days")
    logistics_efficiency: float = Field(default=75.0, description="Logistics efficiency score")
    carbon_footprint_shipping: float = Field(default=50.0, description="Carbon footprint from shipping")

class MarketingMetrics(BaseModel):
    marketing_spend: float = Field(default=100000.0, description="Annual marketing spend")
    brand_awareness: float = Field(default=40.0, description="Brand awareness percentage")
    customer_acquisition_cost: float = Field(default=50.0, description="Customer acquisition cost")
    customer_retention_rate: float = Field(default=80.0, description="Customer retention percentage")
    global_market_presence: float = Field(default=20.0, description="Global market presence score")

class Country(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    region: str
    population: int
    economic_indicators: EconomicIndicators = Field(default_factory=EconomicIndicators)
    environmental_indicators: EnvironmentalIndicators = Field(default_factory=EnvironmentalIndicators)
    cultural_indicators: CulturalIndicators = Field(default_factory=CulturalIndicators)
    business_indicators: BusinessIndicators = Field(default_factory=BusinessIndicators)
    manufacturing_metrics: ManufacturingMetrics = Field(default_factory=ManufacturingMetrics)
    logistics_metrics: LogisticsMetrics = Field(default_factory=LogisticsMetrics)
    marketing_metrics: MarketingMetrics = Field(default_factory=MarketingMetrics)
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
    business_experience: int = Field(default=0)
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

# Enhanced sample data with business decisions
SAMPLE_COUNTRIES = [
    {"name": "United States", "region": "North America", "population": 331000000},
    {"name": "China", "region": "Asia", "population": 1441000000},
    {"name": "Germany", "region": "Europe", "population": 83000000},
    {"name": "Brazil", "region": "South America", "population": 213000000},
    {"name": "India", "region": "Asia", "population": 1380000000},
    {"name": "Nigeria", "region": "Africa", "population": 206000000},
]

ENHANCED_SCENARIOS = [
    # Existing scenarios...
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
            "accept": {"gdp": 50, "unemployment": 10, "trade_balance": 30, "market_share": 15},
            "negotiate": {"gdp": 25, "unemployment": 5, "trade_balance": 15, "brand_reputation": 10},
            "reject": {"gdp": -10, "trade_balance": -5, "cultural_openness": -10, "supply_chain_resilience": -15}
        },
        "difficulty": "medium",
        "historical_context": "Similar to NAFTA negotiations in the 1990s",
        "educational_content": "Free trade agreements can boost economic growth but may displace workers in certain industries."
    },
    
    # NEW MANUFACTURING SCENARIOS
    {
        "title": "Raw Materials Sourcing Strategy",
        "description": "Your company needs to choose raw materials for your new product line. You can source locally for sustainability, or internationally for cost savings.",
        "decision_type": "manufacturing",
        "choices": [
            {"id": "local_sustainable", "text": "Source sustainable local materials (+30% cost)"},
            {"id": "local_standard", "text": "Use standard local materials (+15% cost)"},
            {"id": "international_cheap", "text": "Import cheap materials from developing countries"},
            {"id": "international_premium", "text": "Import premium materials from established suppliers"}
        ],
        "consequences": {
            "local_sustainable": {"sustainability_score": 40, "production_efficiency": -10, "profit_margin": -8, "brand_reputation": 25, "carbon_emissions": -20},
            "local_standard": {"sustainability_score": 15, "production_efficiency": 5, "profit_margin": -3, "brand_reputation": 10, "carbon_emissions": -5},
            "international_cheap": {"profit_margin": 15, "production_efficiency": 10, "carbon_emissions": 30, "brand_reputation": -15, "supply_chain_resilience": -20},
            "international_premium": {"profit_margin": -5, "production_efficiency": 20, "brand_reputation": 20, "supply_chain_resilience": 15, "carbon_emissions": 10}
        },
        "difficulty": "medium",
        "historical_context": "Similar to Nike's supply chain controversies in the 1990s and their subsequent sustainability initiatives",
        "educational_content": "Material sourcing decisions impact not just costs but also environmental footprint, brand reputation, and supply chain resilience."
    },
    
    {
        "title": "Factory Workforce Expansion",
        "description": "Demand for your products is growing. You need to decide how to scale your manufacturing workforce and what compensation to offer.",
        "decision_type": "human_resources",
        "choices": [
            {"id": "hire_local_premium", "text": "Hire 200 local workers with above-market salaries"},
            {"id": "hire_local_standard", "text": "Hire 300 local workers with standard market wages"},
            {"id": "automate_reduce", "text": "Invest in automation, hire only 50 specialized workers"},
            {"id": "offshore_cheap", "text": "Open factory in lower-cost country with 500 workers"}
        ],
        "consequences": {
            "hire_local_premium": {"total_employees": 200, "average_salary": 8000, "employee_satisfaction": 30, "unemployment": -15, "production_efficiency": 20, "profit_margin": -12},
            "hire_local_standard": {"total_employees": 300, "average_salary": 2000, "employee_satisfaction": 10, "unemployment": -20, "production_efficiency": 15, "profit_margin": -8},
            "automate_reduce": {"total_employees": 50, "average_salary": 15000, "automation_level": 40, "production_efficiency": 35, "unemployment": 5, "profit_margin": 10},
            "offshore_cheap": {"total_employees": 500, "average_salary": -20000, "profit_margin": 25, "unemployment": 10, "brand_reputation": -20, "carbon_emissions": 25}
        },
        "difficulty": "hard",
        "historical_context": "Similar to automotive industry decisions during globalization, like GM's factory relocations",
        "educational_content": "Workforce decisions affect not just company profits but local employment, worker welfare, and community development."
    },
    
    {
        "title": "Shipping and Logistics Strategy",
        "description": "You need to establish a global distribution network. Different shipping methods have varying costs, speed, and environmental impacts.",
        "decision_type": "logistics",
        "choices": [
            {"id": "air_express", "text": "Air freight for fastest delivery (2-3 days)"},
            {"id": "sea_sustainable", "text": "Sea freight with carbon-neutral shipping"},
            {"id": "multimodal_balanced", "text": "Multimodal transport balancing cost and speed"},
            {"id": "local_distribution", "text": "Focus on local/regional distribution only"}
        ],
        "consequences": {
            "air_express": {"delivery_time_days": -10, "shipping_cost_per_unit": 8, "carbon_footprint_shipping": 50, "customer_acquisition_cost": -15, "global_market_presence": 25},
            "sea_sustainable": {"delivery_time_days": 5, "shipping_cost_per_unit": -2, "carbon_footprint_shipping": -30, "sustainability_score": 20, "brand_reputation": 15},
            "multimodal_balanced": {"delivery_time_days": 0, "shipping_cost_per_unit": 0, "logistics_efficiency": 20, "supply_chain_resilience": 15, "global_market_presence": 15},
            "local_distribution": {"delivery_time_days": -5, "shipping_cost_per_unit": -5, "carbon_footprint_shipping": -20, "global_market_presence": -15, "profit_margin": -10}
        },
        "difficulty": "medium",
        "historical_context": "Similar to Amazon's logistics evolution from book shipping to global same-day delivery",
        "educational_content": "Logistics decisions create trade-offs between speed, cost, environmental impact, and market reach in global commerce."
    },
    
    {
        "title": "Marketing Campaign Strategy",
        "description": "Launch a new product globally. You need to decide on marketing approach, budget allocation, and cultural adaptation strategies.",
        "decision_type": "marketing",
        "choices": [
            {"id": "global_uniform", "text": "Standardized global campaign (cost-efficient)"},
            {"id": "localized_premium", "text": "Culturally adapted campaigns for each region"},
            {"id": "digital_focused", "text": "Heavy digital marketing with social media"},
            {"id": "sustainable_values", "text": "Values-based marketing emphasizing sustainability"}
        ],
        "consequences": {
            "global_uniform": {"marketing_spend": -30000, "brand_awareness": 15, "global_market_presence": 20, "cultural_openness": -10, "customer_acquisition_cost": -10},
            "localized_premium": {"marketing_spend": 50000, "brand_awareness": 35, "cultural_openness": 25, "customer_retention_rate": 15, "global_market_presence": 30},
            "digital_focused": {"marketing_spend": -20000, "brand_awareness": 25, "customer_acquisition_cost": -20, "innovation_index": 15, "global_market_presence": 20},
            "sustainable_values": {"marketing_spend": 0, "brand_reputation": 30, "sustainability_score": 15, "customer_retention_rate": 20, "brand_awareness": 10}
        },
        "difficulty": "medium",
        "historical_context": "Similar to McDonald's 'glocalization' strategy adapting menus to local tastes while maintaining global brand",
        "educational_content": "Global marketing requires balancing brand consistency with cultural sensitivity and local market preferences."
    },
    
    {
        "title": "Supply Chain Crisis Management",
        "description": "A major supplier in your supply chain faces political instability. You need to quickly adapt your sourcing strategy.",
        "decision_type": "business",
        "choices": [
            {"id": "diversify_suppliers", "text": "Rapidly diversify supplier base across multiple countries"},
            {"id": "vertical_integration", "text": "Acquire supplier facilities to gain direct control"},
            {"id": "stockpile_inventory", "text": "Build large inventory buffers for future disruptions"},
            {"id": "redesign_product", "text": "Redesign product to use alternative materials"}
        ],
        "consequences": {
            "diversify_suppliers": {"supply_chain_resilience": 40, "shipping_cost_per_unit": 3, "production_efficiency": -5, "cultural_openness": 15},
            "vertical_integration": {"supply_chain_resilience": 30, "profit_margin": -15, "production_efficiency": 25, "innovation_index": 10},
            "stockpile_inventory": {"supply_chain_resilience": 20, "profit_margin": -10, "carbon_emissions": 15, "logistics_efficiency": -10},
            "redesign_product": {"supply_chain_resilience": 25, "innovation_index": 30, "profit_margin": -5, "brand_reputation": 10}
        },
        "difficulty": "hard",
        "historical_context": "Similar to semiconductor shortages during COVID-19 affecting automotive and electronics industries",
        "educational_content": "Supply chain resilience requires strategic planning and trade-offs between efficiency, cost, and risk management."
    },
    
    # Environmental scenario enhanced
    {
        "title": "Green Technology Investment",
        "description": "A choice between investing in renewable energy for manufacturing or expanding traditional production to boost short-term profits.",
        "decision_type": "environmental",
        "choices": [
            {"id": "green_factory", "text": "Build solar-powered smart factory"},
            {"id": "carbon_neutral", "text": "Achieve carbon neutrality with offsets"},
            {"id": "balanced_approach", "text": "Gradual green transition over 5 years"},
            {"id": "traditional_expand", "text": "Expand traditional manufacturing capacity"}
        ],
        "consequences": {
            "green_factory": {"renewable_energy": 50, "carbon_emissions": -40, "profit_margin": -20, "sustainability_score": 50, "brand_reputation": 30, "innovation_index": 25},
            "carbon_neutral": {"carbon_emissions": -25, "sustainability_score": 30, "marketing_spend": 20000, "brand_reputation": 20, "profit_margin": -10},
            "balanced_approach": {"renewable_energy": 20, "carbon_emissions": -15, "sustainability_score": 20, "profit_margin": 0, "production_efficiency": 10},
            "traditional_expand": {"profit_margin": 30, "production_capacity": 500, "carbon_emissions": 40, "sustainability_score": -30, "brand_reputation": -15}
        },
        "difficulty": "hard",
        "historical_context": "Similar to Germany's Energiewende (energy transition) and Tesla's impact on automotive industry",
        "educational_content": "Environmental investments often involve upfront costs but can provide long-term competitive advantages and regulatory compliance."
    }
]

ENHANCED_HISTORICAL_FACTS = [
    {
        "title": "The Silk Road",
        "content": "The ancient Silk Road was one of the first examples of globalization, connecting Asia and Europe through trade routes that exchanged not just goods, but ideas, technologies, and cultures.",
        "category": "trade",
        "year": -130,
        "relevance_tags": ["trade", "cultural_exchange", "ancient_globalization"]
    },
    {
        "title": "The Toyota Production System",
        "content": "Developed by Toyota in the 1950s, this lean manufacturing approach revolutionized global production by emphasizing efficiency, quality, and just-in-time delivery, influencing supply chains worldwide.",
        "category": "manufacturing",
        "year": 1950,
        "relevance_tags": ["manufacturing", "efficiency", "supply_chain", "lean_production"]
    },
    {
        "title": "Container Shipping Revolution",
        "content": "The introduction of standardized shipping containers in the 1950s reduced shipping costs by 95% and enabled modern global trade, making it economical to manufacture products far from their markets.",
        "category": "logistics",
        "year": 1955,
        "relevance_tags": ["shipping", "logistics", "standardization", "cost_reduction"]
    },
    {
        "title": "Nike's Supply Chain Transformation",
        "content": "In the 1990s, Nike faced criticism for poor working conditions in overseas factories, leading to industry-wide changes in supply chain transparency and corporate social responsibility practices.",
        "category": "human_resources",
        "year": 1990,
        "relevance_tags": ["labor_practices", "corporate_responsibility", "supply_chain", "brand_reputation"]
    },
    {
        "title": "McDonald's Glocalization Strategy",
        "content": "McDonald's pioneered 'glocalization' by adapting its menu to local tastes while maintaining global brand consistency, such as offering rice burgers in Taiwan and vegetarian options in India.",
        "category": "marketing",
        "year": 1975,
        "relevance_tags": ["cultural_adaptation", "global_branding", "localization", "market_strategy"]
    }
]

ENHANCED_TRIVIA = [
    {
        "question": "What percentage of global trade is transported by sea?",
        "options": ["50%", "70%", "80%", "90%"],
        "correct_answer": 3,
        "explanation": "Approximately 90% of global trade is carried by sea, making maritime shipping crucial for global commerce.",
        "category": "logistics",
        "difficulty": "medium"
    },
    {
        "question": "Which manufacturing philosophy emphasizes 'just-in-time' production?",
        "options": ["Fordism", "Taylorism", "Lean Manufacturing", "Mass Production"],
        "correct_answer": 2,
        "explanation": "Lean Manufacturing, pioneered by Toyota, emphasizes just-in-time production to reduce waste and improve efficiency.",
        "category": "manufacturing",
        "difficulty": "medium"
    },
    {
        "question": "What is the term for adapting global products to local markets?",
        "options": ["Globalization", "Localization", "Glocalization", "Standardization"],
        "correct_answer": 2,
        "explanation": "Glocalization combines global reach with local adaptation, balancing efficiency with cultural sensitivity.",
        "category": "marketing",
        "difficulty": "easy"
    }
]

# Enhanced game logic functions
def calculate_consequences(country: Country, consequences: Dict[str, float]) -> Country:
    """Apply decision consequences to country indicators"""
    updated_country = country.copy(deep=True)
    
    # Apply consequences to all indicator categories
    for indicator, change in consequences.items():
        # Economic indicators
        if hasattr(updated_country.economic_indicators, indicator):
            current_value = getattr(updated_country.economic_indicators, indicator)
            setattr(updated_country.economic_indicators, indicator, max(0, current_value + change))
        # Environmental indicators
        elif hasattr(updated_country.environmental_indicators, indicator):
            current_value = getattr(updated_country.environmental_indicators, indicator)
            setattr(updated_country.environmental_indicators, indicator, max(0, current_value + change))
        # Cultural indicators
        elif hasattr(updated_country.cultural_indicators, indicator):
            current_value = getattr(updated_country.cultural_indicators, indicator)
            setattr(updated_country.cultural_indicators, indicator, max(0, current_value + change))
        # Business indicators
        elif hasattr(updated_country.business_indicators, indicator):
            current_value = getattr(updated_country.business_indicators, indicator)
            setattr(updated_country.business_indicators, indicator, max(0, current_value + change))
        # Manufacturing metrics
        elif hasattr(updated_country.manufacturing_metrics, indicator):
            current_value = getattr(updated_country.manufacturing_metrics, indicator)
            setattr(updated_country.manufacturing_metrics, indicator, max(0, current_value + change))
        # Logistics metrics
        elif hasattr(updated_country.logistics_metrics, indicator):
            current_value = getattr(updated_country.logistics_metrics, indicator)
            setattr(updated_country.logistics_metrics, indicator, max(0, current_value + change))
        # Marketing metrics
        elif hasattr(updated_country.marketing_metrics, indicator):
            current_value = getattr(updated_country.marketing_metrics, indicator)
            setattr(updated_country.marketing_metrics, indicator, max(0, current_value + change))
    
    return updated_country

def calculate_score(decision: Decision, consequences: Dict[str, float], difficulty: str) -> int:
    """Calculate score based on decision quality, consequences, and difficulty"""
    base_score = 10
    difficulty_multiplier = {"easy": 1.0, "medium": 1.5, "hard": 2.0}.get(difficulty, 1.0)
    
    # Positive consequences add to score
    positive_impact = sum(max(0, value) for value in consequences.values())
    negative_impact = sum(min(0, value) for value in consequences.values())
    
    # Bonus for balanced decisions (affecting multiple domains)
    balance_bonus = len([v for v in consequences.values() if v != 0]) * 2
    
    total_score = int((base_score + positive_impact - abs(negative_impact) + balance_bonus) * difficulty_multiplier)
    return max(1, total_score)

async def get_random_scenario(decision_type: Optional[DecisionType] = None) -> GameScenario:
    """Get a random scenario, optionally filtered by type"""
    scenarios = await db.scenarios.find().to_list(100)
    if not scenarios:
        scenarios = ENHANCED_SCENARIOS
    
    if decision_type:
        scenarios = [s for s in scenarios if s.get("decision_type") == decision_type]
    
    if scenarios:
        scenario_data = random.choice(scenarios)
        return GameScenario(**scenario_data)
    
    return GameScenario(**ENHANCED_SCENARIOS[0])

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Global Dynamics - Enhanced Globalization Education Game API"}

@api_router.post("/player", response_model=Player)
async def create_player(player_data: PlayerCreate):
    """Create a new player and assign them a country"""
    
    # Find or create country
    country = await db.countries.find_one({"name": player_data.country_name})
    if not country:
        country_sample = next((c for c in SAMPLE_COUNTRIES if c["name"] == player_data.country_name), None)
        if not country_sample:
            raise HTTPException(status_code=400, detail="Country not found")
        
        country_obj = Country(**country_sample)
        await db.countries.insert_one(country_obj.dict())
        country_id = country_obj.id
    else:
        country_id = country["id"]
    
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
    
    player = await db.players.find_one({"id": decision_data.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    country = await db.countries.find_one({"id": player["country_id"]})
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Get scenario
    scenario_data = next((s for s in ENHANCED_SCENARIOS if s.get("title", "") == decision_data.scenario_id), ENHANCED_SCENARIOS[0])
    scenario = GameScenario(**scenario_data)
    
    if decision_data.choice_index >= len(scenario.choices):
        raise HTTPException(status_code=400, detail="Invalid choice")
    
    choice = scenario.choices[decision_data.choice_index]
    consequences = scenario.consequences.get(choice["id"], {})
    
    # Apply consequences
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
    score_gained = calculate_score(decision, consequences, scenario.difficulty)
    
    # Update player
    updated_player = Player(**player)
    updated_player.score += score_gained
    updated_player.decisions_made += 1
    updated_player.knowledge_points += 5
    updated_player.business_experience += {"easy": 1, "medium": 2, "hard": 3}.get(scenario.difficulty, 1)
    
    # Level up logic
    if updated_player.decisions_made % 5 == 0:
        updated_player.level += 1
    
    # Achievement logic
    if scenario.decision_type == "manufacturing" and "Manufacturing Expert" not in updated_player.achievements:
        manufacturing_decisions = await db.decisions.count_documents({"player_id": decision_data.player_id, "decision_type": "manufacturing"})
        if manufacturing_decisions >= 3:
            updated_player.achievements.append("Manufacturing Expert")
    
    # Save updates
    await db.countries.replace_one({"id": country["id"]}, updated_country.dict())
    await db.players.replace_one({"id": player["id"]}, updated_player.dict())
    await db.decisions.insert_one(decision.dict())
    
    # Get educational content
    educational_fact = random.choice(ENHANCED_HISTORICAL_FACTS)
    trivia_question = random.choice(ENHANCED_TRIVIA)
    
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
            "cultural": updated_country.cultural_indicators.dict(),
            "business": updated_country.business_indicators.dict(),
            "manufacturing": updated_country.manufacturing_metrics.dict(),
            "logistics": updated_country.logistics_metrics.dict(),
            "marketing": updated_country.marketing_metrics.dict()
        },
        "achievements": updated_player.achievements,
        "level_up": updated_player.level > player["level"]
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
        return [HistoricalFact(**fact) for fact in ENHANCED_HISTORICAL_FACTS]
    return [HistoricalFact(**fact) for fact in facts]

@api_router.get("/educational-content/trivia", response_model=List[TriviaQuestion])
async def get_trivia_questions():
    """Get trivia questions for educational content"""
    questions = await db.trivia_questions.find().to_list(50)
    if not questions:
        return [TriviaQuestion(**q) for q in ENHANCED_TRIVIA]
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
            "decisions_made": player["decisions_made"],
            "business_experience": player.get("business_experience", 0),
            "achievements": player.get("achievements", [])
        }
        for player in players
    ]

@api_router.get("/analytics/{player_id}")
async def get_player_analytics(player_id: str):
    """Get detailed analytics for a player"""
    decisions = await db.decisions.find({"player_id": player_id}).to_list(100)
    
    analytics = {
        "decision_breakdown": {},
        "total_decisions": len(decisions),
        "experience_by_category": {}
    }
    
    for decision in decisions:
        decision_type = decision["decision_type"]
        analytics["decision_breakdown"][decision_type] = analytics["decision_breakdown"].get(decision_type, 0) + 1
        analytics["experience_by_category"][decision_type] = analytics["experience_by_category"].get(decision_type, 0) + 1
    
    return analytics

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
    """Initialize database with enhanced sample data"""
    logger.info("Starting Enhanced Global Dynamics API...")
    
    if await db.countries.count_documents({}) == 0:
        countries = [Country(**country_data) for country_data in SAMPLE_COUNTRIES]
        await db.countries.insert_many([country.dict() for country in countries])
        logger.info("Initialized sample countries with enhanced metrics")
    
    if await db.scenarios.count_documents({}) == 0:
        scenarios = [GameScenario(**scenario_data) for scenario_data in ENHANCED_SCENARIOS]
        await db.scenarios.insert_many([scenario.dict() for scenario in scenarios])
        logger.info("Initialized enhanced scenarios")
    
    if await db.historical_facts.count_documents({}) == 0:
        facts = [HistoricalFact(**fact_data) for fact_data in ENHANCED_HISTORICAL_FACTS]
        await db.historical_facts.insert_many([fact.dict() for fact in facts])
        logger.info("Initialized enhanced historical facts")
    
    if await db.trivia_questions.count_documents({}) == 0:
        questions = [TriviaQuestion(**q_data) for q_data in ENHANCED_TRIVIA]
        await db.trivia_questions.insert_many([question.dict() for question in questions])
        logger.info("Initialized enhanced trivia questions")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
