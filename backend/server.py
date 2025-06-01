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
app = FastAPI(title="Business Empire - Educational Business Simulation")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums for game mechanics
class BusinessDecisionType(str, Enum):
    MATERIALS = "materials"
    LOGISTICS = "logistics"
    WORKFORCE = "workforce"
    MARKETING = "marketing"
    FINANCE = "finance"
    EXPANSION = "expansion"

class MaterialType(str, Enum):
    CHEAP_OVERSEAS = "cheap_overseas"
    PREMIUM_LOCAL = "premium_local"
    SUSTAINABLE_FAIR = "sustainable_fair"
    BULK_DISCOUNT = "bulk_discount"

class ShippingMethod(str, Enum):
    ECONOMY_SEA = "economy_sea"
    STANDARD_LAND = "standard_land"
    EXPRESS_AIR = "express_air"
    PREMIUM_RUSH = "premium_rush"

# Game Models
class BusinessMetrics(BaseModel):
    cash: float = Field(default=100000.0, description="Available cash")
    revenue: float = Field(default=0.0, description="Monthly revenue")
    profit_margin: float = Field(default=0.0, description="Profit margin percentage")
    market_share: float = Field(default=5.0, description="Market share percentage")
    reputation: float = Field(default=50.0, description="Business reputation score")
    efficiency: float = Field(default=50.0, description="Operational efficiency")

class ProductionMetrics(BaseModel):
    units_produced: int = Field(default=0, description="Units produced this month")
    production_capacity: int = Field(default=1000, description="Maximum production capacity")
    material_cost_per_unit: float = Field(default=10.0, description="Material cost per unit")
    production_time_days: int = Field(default=7, description="Days to produce and ship")
    quality_score: float = Field(default=70.0, description="Product quality score")

class WorkforceMetrics(BaseModel):
    total_employees: int = Field(default=50, description="Total number of employees")
    average_salary: float = Field(default=50000.0, description="Average annual salary")
    employee_satisfaction: float = Field(default=70.0, description="Employee satisfaction score")
    productivity: float = Field(default=70.0, description="Workforce productivity score")
    training_level: float = Field(default=50.0, description="Employee training level")

class MarketingMetrics(BaseModel):
    brand_awareness: float = Field(default=30.0, description="Brand awareness percentage")
    customer_loyalty: float = Field(default=60.0, description="Customer loyalty score")
    marketing_budget: float = Field(default=10000.0, description="Monthly marketing budget")
    customer_acquisition_cost: float = Field(default=50.0, description="Cost to acquire new customer")
    market_penetration: float = Field(default=15.0, description="Market penetration percentage")

class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    industry: str
    founded_date: datetime = Field(default_factory=datetime.utcnow)
    business_metrics: BusinessMetrics = Field(default_factory=BusinessMetrics)
    production_metrics: ProductionMetrics = Field(default_factory=ProductionMetrics)
    workforce_metrics: WorkforceMetrics = Field(default_factory=WorkforceMetrics)
    marketing_metrics: MarketingMetrics = Field(default_factory=MarketingMetrics)

class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    company_id: str
    level: int = Field(default=1)
    experience_points: int = Field(default=0)
    total_decisions: int = Field(default=0)
    successful_decisions: int = Field(default=0)
    achievements: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BusinessDecision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    decision_type: BusinessDecisionType
    scenario_title: str
    choice_made: str
    consequences: Dict[str, float] = Field(default_factory=dict)
    success_score: float = Field(default=50.0, description="Decision success score 0-100")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BusinessScenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    decision_type: BusinessDecisionType
    current_situation: str
    choices: List[Dict[str, str]]
    consequences: Dict[str, Dict[str, float]]
    learning_objective: str

class BusinessChallenge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    challenge_type: str
    reward_xp: int
    reward_cash: float
    requirements: Dict[str, float]

# Request Models
class CompanyCreate(BaseModel):
    player_name: str
    company_name: str
    industry: str

class DecisionMake(BaseModel):
    player_id: str
    scenario_id: str
    choice_index: int

class GameState(BaseModel):
    player: Player
    company: Company
    current_scenario: Optional[BusinessScenario] = None
    monthly_report: Dict[str, float] = Field(default_factory=dict)
    available_challenges: List[BusinessChallenge] = Field(default_factory=list)

# Sample business scenarios
BUSINESS_SCENARIOS = [
    {
        "title": "Raw Material Sourcing Decision",
        "description": "Your supplier has increased prices by 25%. You need to decide how to handle material sourcing for next quarter.",
        "decision_type": "materials",
        "current_situation": "Current material cost: $10/unit. Demand is growing but margins are tight.",
        "choices": [
            {"id": "cheap_overseas", "text": "Switch to cheaper overseas supplier (-40% cost, +20 days delivery)"},
            {"id": "premium_local", "text": "Upgrade to premium local materials (+30% cost, +15% quality)"},
            {"id": "sustainable_fair", "text": "Choose sustainable fair-trade materials (+25% cost, +brand reputation)"},
            {"id": "negotiate_current", "text": "Negotiate better terms with current supplier"}
        ],
        "consequences": {
            "cheap_overseas": {"material_cost_per_unit": -4, "production_time_days": 5, "quality_score": -10, "reputation": -15, "profit_margin": 12},
            "premium_local": {"material_cost_per_unit": 3, "quality_score": 15, "reputation": 10, "profit_margin": -8, "customer_loyalty": 10},
            "sustainable_fair": {"material_cost_per_unit": 2.5, "reputation": 25, "brand_awareness": 8, "profit_margin": -6, "customer_loyalty": 15},
            "negotiate_current": {"material_cost_per_unit": -1, "reputation": 5, "efficiency": 5, "profit_margin": 3}
        },
        "learning_objective": "Understanding supply chain decisions and their impact on cost, quality, and brand reputation."
    },
    {
        "title": "Shipping Method Selection",
        "description": "You have a large order from a key client who needs delivery in different timeframes. Choose your shipping strategy.",
        "decision_type": "logistics",
        "current_situation": "Order value: $50,000. Customer is willing to pay premium for faster delivery.",
        "choices": [
            {"id": "economy_sea", "text": "Economy sea freight (30 days, $500 shipping)"},
            {"id": "standard_land", "text": "Standard ground shipping (10 days, $1,200 shipping)"},
            {"id": "express_air", "text": "Express air shipping (3 days, $3,000 shipping)"},
            {"id": "mixed_strategy", "text": "Split shipment: urgent items by air, rest by ground"}
        ],
        "consequences": {
            "economy_sea": {"cash": 49500, "production_time_days": 30, "customer_loyalty": -5, "efficiency": -5, "profit_margin": 8},
            "standard_land": {"cash": 48800, "production_time_days": 10, "customer_loyalty": 5, "efficiency": 5, "profit_margin": 6},
            "express_air": {"cash": 47000, "production_time_days": 3, "customer_loyalty": 15, "reputation": 10, "profit_margin": -2},
            "mixed_strategy": {"cash": 48000, "production_time_days": 8, "customer_loyalty": 10, "efficiency": 10, "profit_margin": 4}
        },
        "learning_objective": "Balancing shipping costs, delivery speed, and customer satisfaction in logistics decisions."
    },
    {
        "title": "Factory Workforce Expansion",
        "description": "Demand is increasing and you need to scale production. Decide how to expand your workforce.",
        "decision_type": "workforce",
        "current_situation": "Current: 50 employees at $50k average salary. Need 40% more production capacity.",
        "choices": [
            {"id": "hire_premium", "text": "Hire 25 skilled workers at $65k each"},
            {"id": "hire_standard", "text": "Hire 30 workers at standard $50k salary"},
            {"id": "automation_hybrid", "text": "Invest in automation + hire 10 specialists at $80k"},
            {"id": "outsource_production", "text": "Outsource 40% of production to third party"}
        ],
        "consequences": {
            "hire_premium": {"total_employees": 25, "average_salary": 7500, "productivity": 20, "employee_satisfaction": 15, "cash": -162500, "efficiency": 15},
            "hire_standard": {"total_employees": 30, "average_salary": 0, "productivity": 15, "employee_satisfaction": 5, "cash": -150000, "efficiency": 10},
            "automation_hybrid": {"total_employees": 10, "average_salary": 12000, "productivity": 35, "efficiency": 30, "cash": -280000, "quality_score": 15},
            "outsource_production": {"cash": -80000, "efficiency": -10, "quality_score": -8, "profit_margin": 8, "reputation": -5}
        },
        "learning_objective": "Understanding workforce decisions: hiring costs, productivity, automation vs. human workers."
    },
    {
        "title": "Marketing Campaign Strategy",
        "description": "Launch marketing for a new product. Choose your marketing approach and budget allocation.",
        "decision_type": "marketing",
        "current_situation": "New product launch. Target market: young professionals. Budget: $20,000/month.",
        "choices": [
            {"id": "digital_focused", "text": "All-digital campaign: social media, online ads, influencers"},
            {"id": "traditional_mix", "text": "Traditional mix: TV, radio, print advertising"},
            {"id": "experiential", "text": "Experiential marketing: events, demos, word-of-mouth"},
            {"id": "content_education", "text": "Content marketing: educational blogs, webinars, thought leadership"}
        ],
        "consequences": {
            "digital_focused": {"brand_awareness": 25, "customer_acquisition_cost": -15, "market_penetration": 12, "marketing_budget": 0, "customer_loyalty": 8},
            "traditional_mix": {"brand_awareness": 15, "market_penetration": 8, "customer_acquisition_cost": 5, "marketing_budget": 2000, "reputation": 5},
            "experiential": {"customer_loyalty": 20, "brand_awareness": 18, "customer_acquisition_cost": 10, "marketing_budget": 5000, "reputation": 15},
            "content_education": {"reputation": 20, "customer_loyalty": 15, "brand_awareness": 10, "customer_acquisition_cost": -5, "marketing_budget": -3000}
        },
        "learning_objective": "Different marketing strategies and their impact on brand awareness, customer acquisition, and loyalty."
    },
    {
        "title": "Financial Investment Decision",
        "description": "You have excess cash and multiple investment opportunities. Choose how to allocate your capital.",
        "decision_type": "finance",
        "current_situation": "Available cash: $100,000. Multiple growth opportunities requiring investment.",
        "choices": [
            {"id": "rd_innovation", "text": "Invest in R&D for product innovation ($80k)"},
            {"id": "market_expansion", "text": "Expand to new geographic market ($75k)"},
            {"id": "capacity_upgrade", "text": "Upgrade production capacity and equipment ($90k)"},
            {"id": "acquisition", "text": "Acquire smaller competitor ($85k)"}
        ],
        "consequences": {
            "rd_innovation": {"cash": -80000, "quality_score": 25, "reputation": 15, "market_share": 8, "efficiency": 10},
            "market_expansion": {"cash": -75000, "market_share": 15, "brand_awareness": 20, "revenue": 15000, "market_penetration": 10},
            "capacity_upgrade": {"cash": -90000, "production_capacity": 500, "efficiency": 25, "quality_score": 10, "profit_margin": 5},
            "acquisition": {"cash": -85000, "market_share": 12, "total_employees": 20, "production_capacity": 300, "customer_loyalty": 8}
        },
        "learning_objective": "Capital allocation decisions and their long-term vs. short-term business impacts."
    },
    {
        "title": "Business Expansion Strategy",
        "description": "Your business is successful locally. Time to decide on expansion strategy for growth.",
        "decision_type": "expansion",
        "current_situation": "Strong local presence. Considering national/international expansion options.",
        "choices": [
            {"id": "franchise_model", "text": "Franchise model: rapid expansion with partners"},
            {"id": "direct_expansion", "text": "Direct expansion: open company-owned locations"},
            {"id": "online_platform", "text": "Digital expansion: e-commerce and online platform"},
            {"id": "licensing_deals", "text": "Licensing deals: let others use your brand/process"}
        ],
        "consequences": {
            "franchise_model": {"market_share": 20, "revenue": 25000, "cash": 50000, "reputation": 5, "efficiency": -5},
            "direct_expansion": {"market_share": 15, "revenue": 30000, "cash": -120000, "reputation": 15, "customer_loyalty": 10},
            "online_platform": {"market_penetration": 30, "customer_acquisition_cost": -20, "cash": -60000, "brand_awareness": 25, "efficiency": 15},
            "licensing_deals": {"revenue": 15000, "cash": 30000, "market_share": 10, "reputation": -5, "efficiency": 5}
        },
        "learning_objective": "Different business expansion models and their trade-offs in terms of control, investment, and growth."
    }
]

SAMPLE_CHALLENGES = [
    {
        "title": "Efficiency Master",
        "description": "Achieve 85% operational efficiency",
        "challenge_type": "operational",
        "reward_xp": 500,
        "reward_cash": 10000.0,
        "requirements": {"efficiency": 85.0}
    },
    {
        "title": "People's Choice",
        "description": "Reach 80% employee satisfaction",
        "challenge_type": "workforce",
        "reward_xp": 300,
        "reward_cash": 5000.0,
        "requirements": {"employee_satisfaction": 80.0}
    }
]

# Game Logic Functions
def calculate_monthly_report(company: Company) -> Dict[str, float]:
    """Calculate monthly business performance"""
    bm = company.business_metrics
    pm = company.production_metrics
    wm = company.workforce_metrics
    mm = company.marketing_metrics
    
    # Calculate monthly revenue based on production and market factors
    units_sold = min(pm.units_produced, int(pm.production_capacity * (mm.market_penetration / 100)))
    price_per_unit = 25 + (pm.quality_score / 10)  # Base price + quality bonus
    monthly_revenue = units_sold * price_per_unit
    
    # Calculate costs
    material_costs = units_sold * pm.material_cost_per_unit
    labor_costs = wm.total_employees * (wm.average_salary / 12)
    marketing_costs = mm.marketing_budget
    total_costs = material_costs + labor_costs + marketing_costs
    
    # Calculate profit
    monthly_profit = monthly_revenue - total_costs
    profit_margin = (monthly_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
    
    return {
        "monthly_revenue": monthly_revenue,
        "monthly_profit": monthly_profit,
        "profit_margin": profit_margin,
        "units_sold": units_sold,
        "total_costs": total_costs,
        "material_costs": material_costs,
        "labor_costs": labor_costs
    }

def apply_decision_consequences(company: Company, consequences: Dict[str, float]) -> Company:
    """Apply decision consequences to company metrics"""
    updated_company = company.copy(deep=True)
    
    for metric, change in consequences.items():
        # Business metrics
        if hasattr(updated_company.business_metrics, metric):
            current = getattr(updated_company.business_metrics, metric)
            setattr(updated_company.business_metrics, metric, max(0, current + change))
        # Production metrics
        elif hasattr(updated_company.production_metrics, metric):
            current = getattr(updated_company.production_metrics, metric)
            setattr(updated_company.production_metrics, metric, max(0, current + change))
        # Workforce metrics
        elif hasattr(updated_company.workforce_metrics, metric):
            current = getattr(updated_company.workforce_metrics, metric)
            setattr(updated_company.workforce_metrics, metric, max(0, current + change))
        # Marketing metrics
        elif hasattr(updated_company.marketing_metrics, metric):
            current = getattr(updated_company.marketing_metrics, metric)
            setattr(updated_company.marketing_metrics, metric, max(0, current + change))
    
    return updated_company

def calculate_decision_success(consequences: Dict[str, float], company: Company) -> float:
    """Calculate decision success score based on consequences and company state"""
    positive_impact = sum(max(0, value) for value in consequences.values())
    negative_impact = sum(min(0, value) for value in consequences.values())
    
    # Consider company's current financial health
    financial_health = company.business_metrics.cash / 100000.0  # Normalize to 0-1
    
    success_score = 50 + (positive_impact * 2) + (negative_impact * 1.5) + (financial_health * 10)
    return max(0, min(100, success_score))

async def get_random_scenario(decision_type: Optional[BusinessDecisionType] = None) -> BusinessScenario:
    """Get a random business scenario"""
    scenarios = await db.scenarios.find().to_list(100)
    if not scenarios:
        scenarios = BUSINESS_SCENARIOS
    
    if decision_type:
        scenarios = [s for s in scenarios if s.get("decision_type") == decision_type]
    
    if scenarios:
        scenario_data = random.choice(scenarios)
        return BusinessScenario(**scenario_data)
    
    return BusinessScenario(**BUSINESS_SCENARIOS[0])

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Business Empire - Educational Business Simulation API"}

@api_router.post("/company", response_model=Player)
async def create_company(company_data: CompanyCreate):
    """Create a new company and player"""
    
    # Create company
    company = Company(
        name=company_data.company_name,
        industry=company_data.industry
    )
    await db.companies.insert_one(company.dict())
    
    # Create player
    player = Player(
        name=company_data.player_name,
        company_id=company.id
    )
    await db.players.insert_one(player.dict())
    
    return player

@api_router.get("/industries")
async def get_industries():
    """Get available industries"""
    return [
        {"name": "Technology", "description": "Software, hardware, digital products"},
        {"name": "Manufacturing", "description": "Physical goods production"},
        {"name": "Retail", "description": "Consumer goods and services"},
        {"name": "Food & Beverage", "description": "Food production and restaurants"},
        {"name": "Healthcare", "description": "Medical devices and services"},
        {"name": "Fashion", "description": "Clothing and accessories"}
    ]

@api_router.get("/game-state/{player_id}", response_model=GameState)
async def get_game_state(player_id: str):
    """Get current game state for a player"""
    
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    company = await db.companies.find_one({"id": player["company_id"]})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get current scenario
    current_scenario = await get_random_scenario()
    
    # Calculate monthly report
    company_obj = Company(**company)
    monthly_report = calculate_monthly_report(company_obj)
    
    return GameState(
        player=Player(**player),
        company=company_obj,
        current_scenario=current_scenario,
        monthly_report=monthly_report,
        available_challenges=[BusinessChallenge(**c) for c in SAMPLE_CHALLENGES]
    )

@api_router.post("/decision", response_model=Dict)
async def make_decision(decision_data: DecisionMake):
    """Process a business decision"""
    
    player = await db.players.find_one({"id": decision_data.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    company = await db.companies.find_one({"id": player["company_id"]})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get scenario
    scenario_data = next((s for s in BUSINESS_SCENARIOS if s.get("title", "") == decision_data.scenario_id), BUSINESS_SCENARIOS[0])
    scenario = BusinessScenario(**scenario_data)
    
    if decision_data.choice_index >= len(scenario.choices):
        raise HTTPException(status_code=400, detail="Invalid choice")
    
    choice = scenario.choices[decision_data.choice_index]
    consequences = scenario.consequences.get(choice["id"], {})
    
    # Apply consequences
    company_obj = Company(**company)
    updated_company = apply_decision_consequences(company_obj, consequences)
    
    # Calculate success score
    success_score = calculate_decision_success(consequences, updated_company)
    
    # Create decision record
    decision = BusinessDecision(
        player_id=decision_data.player_id,
        decision_type=scenario.decision_type,
        scenario_title=scenario.title,
        choice_made=choice["text"],
        consequences=consequences,
        success_score=success_score
    )
    
    # Update player
    updated_player = Player(**player)
    xp_gained = int(success_score / 10) + 10
    updated_player.experience_points += xp_gained
    updated_player.total_decisions += 1
    if success_score > 70:
        updated_player.successful_decisions += 1
    
    # Level up logic
    if updated_player.experience_points >= (updated_player.level * 100):
        updated_player.level += 1
    
    # Check achievements
    if updated_player.total_decisions >= 10 and "Business Rookie" not in updated_player.achievements:
        updated_player.achievements.append("Business Rookie")
    
    # Save updates
    await db.companies.replace_one({"id": company["id"]}, updated_company.dict())
    await db.players.replace_one({"id": player["id"]}, updated_player.dict())
    await db.decisions.insert_one(decision.dict())
    
    # Calculate new monthly report
    new_monthly_report = calculate_monthly_report(updated_company)
    
    return {
        "success": True,
        "success_score": success_score,
        "xp_gained": xp_gained,
        "level_up": updated_player.level > player["level"],
        "consequences": consequences,
        "monthly_report": new_monthly_report,
        "company_metrics": {
            "business": updated_company.business_metrics.dict(),
            "production": updated_company.production_metrics.dict(),
            "workforce": updated_company.workforce_metrics.dict(),
            "marketing": updated_company.marketing_metrics.dict()
        },
        "learning_objective": scenario.learning_objective
    }

@api_router.get("/leaderboard")
async def get_leaderboard():
    """Get top companies leaderboard"""
    players = await db.players.find().sort("experience_points", -1).limit(10).to_list(10)
    leaderboard = []
    
    for player in players:
        company = await db.companies.find_one({"id": player["company_id"]})
        if company:
            monthly_report = calculate_monthly_report(Company(**company))
            leaderboard.append({
                "player_name": player["name"],
                "company_name": company["name"],
                "industry": company["industry"],
                "level": player["level"],
                "experience_points": player["experience_points"],
                "monthly_revenue": monthly_report["monthly_revenue"],
                "success_rate": (player["successful_decisions"] / max(1, player["total_decisions"])) * 100
            })
    
    return leaderboard

@api_router.get("/scenarios/{decision_type}")
async def get_scenario_by_type(decision_type: BusinessDecisionType):
    """Get a scenario by business decision type"""
    scenario = await get_random_scenario(decision_type)
    return scenario

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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data"""
    logger.info("Starting Business Empire API...")
    
    if await db.scenarios.count_documents({}) == 0:
        scenarios = [BusinessScenario(**scenario_data) for scenario_data in BUSINESS_SCENARIOS]
        await db.scenarios.insert_many([scenario.dict() for scenario in scenarios])
        logger.info("Initialized business scenarios")
    
    if await db.challenges.count_documents({}) == 0:
        challenges = [BusinessChallenge(**challenge_data) for challenge_data in SAMPLE_CHALLENGES]
        await db.challenges.insert_many([challenge.dict() for challenge in challenges])
        logger.info("Initialized business challenges")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
