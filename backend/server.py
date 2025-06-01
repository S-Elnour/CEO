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
app = FastAPI(title="Global Supply Chain Simulator")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums for decision types
class DecisionType(str, Enum):
    FACTORY_LOCATION = "factory_location"
    RAW_MATERIALS = "raw_materials"
    SHIPPING_METHOD = "shipping_method"
    EMPLOYEE_COUNT = "employee_count"
    SALARY = "salary"
    MARKETING_BUDGET = "marketing_budget"

# Game Models
class CompanyMetrics(BaseModel):
    profit: float = Field(default=0.0, description="Total profit in USD")
    pollution: float = Field(default=0.0, description="Pollution score (lower is better)")
    employee_treatment: float = Field(default=50.0, description="Employee treatment score (higher is better)")
    global_awareness: float = Field(default=0.0, description="Educational points gained")

class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    current_year: int = Field(default=1, description="Current business year")
    current_decision: int = Field(default=1, description="Current decision in year (1-6)")
    metrics: CompanyMetrics = Field(default_factory=CompanyMetrics)
    yearly_decisions: Dict[int, Dict[str, str]] = Field(default_factory=dict, description="Decisions made each year")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    company_id: str
    total_score: float = Field(default=0.0, description="Overall performance score")
    years_completed: int = Field(default=0, description="Number of years completed")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Decision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    year: int
    decision_type: DecisionType
    choice_made: str
    consequences: Dict[str, float] = Field(default_factory=dict)
    educational_fact: str = Field(default="", description="Educational fact shown after decision")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DecisionOption(BaseModel):
    id: str
    text: str
    description: str
    consequences: Dict[str, float]

class YearlyDecision(BaseModel):
    decision_type: DecisionType
    title: str
    question: str
    description: str
    options: List[DecisionOption]
    educational_facts: List[str]

class GameState(BaseModel):
    player: Player
    company: Company
    current_decision: Optional[YearlyDecision] = None
    year_complete: bool = Field(default=False)
    game_complete: bool = Field(default=False)

# Request Models
class CompanyCreate(BaseModel):
    player_name: str
    company_name: str

class DecisionMake(BaseModel):
    player_id: str
    choice_id: str

# Define the 6 annual decisions
YEARLY_DECISIONS = [
    {
        "decision_type": "factory_location",
        "title": "Factory Location",
        "question": "Where do you want to build your factory?",
        "description": "Choose the location for your manufacturing facility. Each location has different costs, regulations, and working conditions.",
        "options": [
            {
                "id": "developed_country",
                "text": "Developed Country (USA/Germany)",
                "description": "High labor costs, strict regulations, excellent worker conditions",
                "consequences": {"profit": -20000, "pollution": -10, "employee_treatment": 30}
            },
            {
                "id": "emerging_market",
                "text": "Emerging Market (Brazil/India)",
                "description": "Moderate costs, growing infrastructure, decent conditions",
                "consequences": {"profit": 5000, "pollution": 5, "employee_treatment": 10}
            },
            {
                "id": "low_cost_country",
                "text": "Low-Cost Country (Bangladesh/Vietnam)",
                "description": "Very low costs, minimal regulations, basic conditions",
                "consequences": {"profit": 40000, "pollution": 20, "employee_treatment": -20}
            },
            {
                "id": "tax_haven",
                "text": "Tax Haven (Ireland/Singapore)",
                "description": "Low taxes, good infrastructure, high setup costs",
                "consequences": {"profit": 15000, "pollution": 0, "employee_treatment": 15}
            }
        ],
        "educational_facts": [
            "Manufacturing jobs in developing countries often pay 10-20 times less than similar jobs in developed countries.",
            "The 'race to the bottom' refers to countries competing to offer the lowest wages and weakest regulations to attract foreign investment.",
            "Labor arbitrage is the practice of moving production to countries with lower labor costs.",
            "Special Economic Zones (SEZs) offer tax incentives and relaxed regulations to attract foreign manufacturers."
        ]
    },
    {
        "decision_type": "raw_materials",
        "title": "Raw Materials",
        "question": "Where do you want to source your materials?",
        "description": "Select your supply chain strategy for raw materials. Consider cost, quality, environmental impact, and supply chain reliability.",
        "options": [
            {
                "id": "local_sustainable",
                "text": "Local & Sustainable",
                "description": "Eco-friendly materials from local suppliers",
                "consequences": {"profit": -15000, "pollution": -25, "employee_treatment": 5}
            },
            {
                "id": "global_certified",
                "text": "Global Certified",
                "description": "Certified sustainable materials from international suppliers",
                "consequences": {"profit": -5000, "pollution": -15, "employee_treatment": 0}
            },
            {
                "id": "cheapest_available",
                "text": "Cheapest Available",
                "description": "Lowest cost materials regardless of source",
                "consequences": {"profit": 25000, "pollution": 30, "employee_treatment": -10}
            },
            {
                "id": "mixed_strategy",
                "text": "Mixed Strategy",
                "description": "Balance of cost-effective and sustainable materials",
                "consequences": {"profit": 8000, "pollution": 5, "employee_treatment": 0}
            }
        ],
        "educational_facts": [
            "The fashion industry is responsible for 10% of global carbon emissions, largely due to fast fashion and cheap materials.",
            "Rare earth minerals used in electronics often come from mines with poor environmental and labor standards.",
            "Supply chain transparency initiatives help consumers understand the true cost of their purchases.",
            "Circular economy principles encourage reusing and recycling materials rather than extracting new resources."
        ]
    },
    {
        "decision_type": "shipping_method",
        "title": "Shipping Methods",
        "question": "How will you ship your products?",
        "description": "Choose your logistics strategy. Consider speed, cost, environmental impact, and customer expectations.",
        "options": [
            {
                "id": "air_freight",
                "text": "Air Freight",
                "description": "Fast delivery, high cost, highest emissions",
                "consequences": {"profit": -30000, "pollution": 40, "employee_treatment": 0}
            },
            {
                "id": "sea_freight",
                "text": "Sea Freight",
                "description": "Slow but cost-effective, moderate emissions",
                "consequences": {"profit": 15000, "pollution": 10, "employee_treatment": 0}
            },
            {
                "id": "rail_transport",
                "text": "Rail Transport",
                "description": "Moderate speed and cost, lower emissions",
                "consequences": {"profit": 5000, "pollution": -5, "employee_treatment": 0}
            },
            {
                "id": "road_transport",
                "text": "Road Transport",
                "description": "Flexible routing, moderate cost and emissions",
                "consequences": {"profit": 0, "pollution": 15, "employee_treatment": 0}
            }
        ],
        "educational_facts": [
            "Shipping accounts for about 3% of global CO2 emissions, roughly equivalent to the entire country of Germany.",
            "A single cargo ship can carry as much as 20,000 trucks, making sea freight highly efficient per unit.",
            "The 'last mile' of delivery (to your door) often accounts for 50% of total shipping costs.",
            "Container shipping revolutionized global trade by standardizing cargo sizes and handling methods."
        ]
    },
    {
        "decision_type": "employee_count",
        "title": "Number of Employees",
        "question": "How many employees do you want to hire?",
        "description": "Determine your workforce size. More employees increase capacity but also costs and management complexity.",
        "options": [
            {
                "id": "minimal_staff",
                "text": "50 Employees (Minimal)",
                "description": "Small, lean operation with automation",
                "consequences": {"profit": 20000, "pollution": -5, "employee_treatment": 10}
            },
            {
                "id": "moderate_staff",
                "text": "200 Employees (Moderate)",
                "description": "Balanced workforce with good productivity",
                "consequences": {"profit": 10000, "pollution": 0, "employee_treatment": 5}
            },
            {
                "id": "large_staff",
                "text": "500 Employees (Large)",
                "description": "High capacity, labor-intensive operation",
                "consequences": {"profit": -5000, "pollution": 10, "employee_treatment": -5}
            },
            {
                "id": "maximum_staff",
                "text": "1000 Employees (Maximum)",
                "description": "Massive workforce, maximum local impact",
                "consequences": {"profit": -20000, "pollution": 20, "employee_treatment": -15}
            }
        ],
        "educational_facts": [
            "Automation has eliminated millions of manufacturing jobs globally, but also created new jobs in technology and maintenance.",
            "The 'gig economy' allows companies to hire temporary workers without providing traditional benefits.",
            "Labor-intensive industries often move to countries with large populations of young workers.",
            "Unemployment in manufacturing communities can lead to social and economic problems lasting decades."
        ]
    },
    {
        "decision_type": "salary",
        "title": "Salary",
        "question": "What average yearly salary will you offer?",
        "description": "Set compensation levels for your workforce. Higher pay improves worker satisfaction but reduces profits.",
        "options": [
            {
                "id": "minimum_wage",
                "text": "$3,000/year (Minimum)",
                "description": "Local minimum wage, basic survival level",
                "consequences": {"profit": 50000, "pollution": 0, "employee_treatment": -30}
            },
            {
                "id": "living_wage",
                "text": "$8,000/year (Living)",
                "description": "Enough for basic needs and small savings",
                "consequences": {"profit": 25000, "pollution": 0, "employee_treatment": 0}
            },
            {
                "id": "competitive_wage",
                "text": "$15,000/year (Competitive)",
                "description": "Above-average local wages, good quality of life",
                "consequences": {"profit": 0, "pollution": 0, "employee_treatment": 25}
            },
            {
                "id": "premium_wage",
                "text": "$25,000/year (Premium)",
                "description": "High wages, excellent worker retention",
                "consequences": {"profit": -30000, "pollution": 0, "employee_treatment": 40}
            }
        ],
        "educational_facts": [
            "The global median income is approximately $3,000 per year, but varies dramatically by country.",
            "A 'living wage' covers basic needs like food, housing, and healthcare, while minimum wage often doesn't.",
            "Higher wages can increase productivity through better nutrition, education, and worker motivation.",
            "Income inequality has grown significantly in most countries over the past 40 years."
        ]
    },
    {
        "decision_type": "marketing_budget",
        "title": "Marketing Budget",
        "question": "How much will you spend on marketing and promotion?",
        "description": "Invest in building your brand and reaching customers. Marketing drives sales but reduces immediate profits.",
        "options": [
            {
                "id": "no_marketing",
                "text": "$0 (No Marketing)",
                "description": "Rely on word-of-mouth and natural demand",
                "consequences": {"profit": 0, "pollution": 0, "employee_treatment": 0}
            },
            {
                "id": "basic_marketing",
                "text": "$10,000 (Basic)",
                "description": "Local advertising and simple promotions",
                "consequences": {"profit": 15000, "pollution": 2, "employee_treatment": 0}
            },
            {
                "id": "standard_marketing",
                "text": "$50,000 (Standard)",
                "description": "Regional campaigns and digital marketing",
                "consequences": {"profit": 40000, "pollution": 8, "employee_treatment": 0}
            },
            {
                "id": "premium_marketing",
                "text": "$150,000 (Premium)",
                "description": "Global campaigns and celebrity endorsements",
                "consequences": {"profit": 80000, "pollution": 20, "employee_treatment": 0}
            }
        ],
        "educational_facts": [
            "The global advertising industry spends over $600 billion annually, with digital ads growing fastest.",
            "Social media influencer marketing has become a $16 billion industry targeting younger consumers.",
            "Greenwashing is when companies exaggerate their environmental benefits in marketing materials.",
            "Viral marketing can reach millions of people at very low cost compared to traditional advertising."
        ]
    }
]

# Game Logic Functions
def get_decision_by_type(decision_type: DecisionType) -> YearlyDecision:
    """Get decision data by type"""
    for decision_data in YEARLY_DECISIONS:
        if decision_data["decision_type"] == decision_type:
            return YearlyDecision(**decision_data)
    raise HTTPException(status_code=404, detail="Decision type not found")

def get_current_decision_type(decision_number: int) -> DecisionType:
    """Get decision type based on current decision number (1-6)"""
    decision_types = [
        DecisionType.FACTORY_LOCATION,
        DecisionType.RAW_MATERIALS,
        DecisionType.SHIPPING_METHOD,
        DecisionType.EMPLOYEE_COUNT,
        DecisionType.SALARY,
        DecisionType.MARKETING_BUDGET
    ]
    return decision_types[decision_number - 1]

def calculate_year_end_score(company: Company) -> float:
    """Calculate overall performance score for the year"""
    m = company.metrics
    
    # Balanced scoring: profit is important but not everything
    profit_score = max(0, min(100, (m.profit + 100000) / 2000))  # Normalize profit
    pollution_score = max(0, 100 - m.pollution)  # Lower pollution = higher score
    treatment_score = max(0, m.employee_treatment)  # Higher treatment = higher score
    
    # Weighted average: profit 40%, environment 30%, workers 30%
    total_score = (profit_score * 0.4) + (pollution_score * 0.3) + (treatment_score * 0.3)
    return round(total_score, 1)

def apply_decision_consequences(company: Company, consequences: Dict[str, float]) -> Company:
    """Apply decision consequences to company metrics"""
    updated_company = company.copy(deep=True)
    
    for metric, change in consequences.items():
        current_value = getattr(updated_company.metrics, metric)
        setattr(updated_company.metrics, metric, current_value + change)
    
    return updated_company

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Global Supply Chain Simulator API"}

@api_router.post("/company", response_model=Player)
async def create_company(company_data: CompanyCreate):
    """Create a new company and player"""
    
    # Create company
    company = Company(name=company_data.company_name)
    await db.companies.insert_one(company.dict())
    
    # Create player
    player = Player(name=company_data.player_name, company_id=company.id)
    await db.players.insert_one(player.dict())
    
    return player

@api_router.get("/game-state/{player_id}", response_model=GameState)
async def get_game_state(player_id: str):
    """Get current game state for a player"""
    
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    company = await db.companies.find_one({"id": player["company_id"]})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_obj = Company(**company)
    
    # Check if year is complete (all 6 decisions made)
    year_complete = company_obj.current_decision > 6
    game_complete = company_obj.current_year > 5  # 5 years total
    
    current_decision = None
    if not year_complete and not game_complete:
        decision_type = get_current_decision_type(company_obj.current_decision)
        current_decision = get_decision_by_type(decision_type)
    
    return GameState(
        player=Player(**player),
        company=company_obj,
        current_decision=current_decision,
        year_complete=year_complete,
        game_complete=game_complete
    )

@api_router.post("/decision", response_model=Dict)
async def make_decision(decision_data: DecisionMake):
    """Process a player's decision"""
    
    player = await db.players.find_one({"id": decision_data.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    company = await db.companies.find_one({"id": player["company_id"]})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_obj = Company(**company)
    
    # Get current decision
    decision_type = get_current_decision_type(company_obj.current_decision)
    yearly_decision = get_decision_by_type(decision_type)
    
    # Find the chosen option
    chosen_option = None
    for option in yearly_decision.options:
        if option.id == decision_data.choice_id:
            chosen_option = option
            break
    
    if not chosen_option:
        raise HTTPException(status_code=400, detail="Invalid choice")
    
    # Apply consequences
    updated_company = apply_decision_consequences(company_obj, chosen_option.consequences)
    
    # Record decision
    decision = Decision(
        player_id=decision_data.player_id,
        year=updated_company.current_year,
        decision_type=decision_type,
        choice_made=chosen_option.text,
        consequences=chosen_option.consequences,
        educational_fact=random.choice(yearly_decision.educational_facts)
    )
    
    # Update company state
    updated_company.current_decision += 1
    
    # Check if year is complete
    year_complete = updated_company.current_decision > 6
    if year_complete:
        # Calculate year-end score
        year_score = calculate_year_end_score(updated_company)
        
        # Update player
        updated_player = Player(**player)
        updated_player.total_score += year_score
        updated_player.years_completed += 1
        
        # Prepare for next year or end game
        if updated_company.current_year < 5:
            updated_company.current_year += 1
            updated_company.current_decision = 1
            # Reset some metrics for new year
            updated_company.metrics.profit = 0
            updated_company.metrics.pollution = 0
        
        await db.players.replace_one({"id": player["id"]}, updated_player.dict())
    
    # Save updates
    await db.companies.replace_one({"id": company["id"]}, updated_company.dict())
    await db.decisions.insert_one(decision.dict())
    
    return {
        "success": True,
        "choice_made": chosen_option.text,
        "consequences": chosen_option.consequences,
        "educational_fact": decision.educational_fact,
        "updated_metrics": updated_company.metrics.dict(),
        "year_complete": year_complete,
        "year_score": calculate_year_end_score(updated_company) if year_complete else None,
        "game_complete": updated_company.current_year > 5
    }

@api_router.post("/next-year/{player_id}")
async def start_next_year(player_id: str):
    """Start the next year"""
    
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    company = await db.companies.find_one({"id": player["company_id"]})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_obj = Company(**company)
    
    # Reset for next year if not already done
    if company_obj.current_decision > 6 and company_obj.current_year <= 5:
        company_obj.current_year += 1
        company_obj.current_decision = 1
        # Reset yearly metrics
        company_obj.metrics.profit = 0
        company_obj.metrics.pollution = 0
        
        await db.companies.replace_one({"id": company["id"]}, company_obj.dict())
    
    return {"success": True, "current_year": company_obj.current_year}

@api_router.get("/leaderboard")
async def get_leaderboard():
    """Get top companies leaderboard"""
    players = await db.players.find().sort("total_score", -1).limit(10).to_list(10)
    leaderboard = []
    
    for player in players:
        company = await db.companies.find_one({"id": player["company_id"]})
        if company:
            leaderboard.append({
                "player_name": player["name"],
                "company_name": company["name"],
                "total_score": player["total_score"],
                "years_completed": player["years_completed"],
                "current_year": company["current_year"]
            })
    
    return leaderboard

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
    logger.info("Starting Global Supply Chain Simulator API...")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
