import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// API Helper Functions
const api = {
  async getCountries() {
    const response = await fetch(`${API_BASE_URL}/api/countries`);
    return response.json();
  },
  
  async createPlayer(name, countryName) {
    const response = await fetch(`${API_BASE_URL}/api/player`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, country_name: countryName })
    });
    return response.json();
  },
  
  async getGameState(playerId) {
    const response = await fetch(`${API_BASE_URL}/api/game-state/${playerId}`);
    return response.json();
  },
  
  async makeDecision(playerId, scenarioId, choiceIndex) {
    const response = await fetch(`${API_BASE_URL}/api/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        player_id: playerId, 
        scenario_id: scenarioId, 
        choice_index: choiceIndex 
      })
    });
    return response.json();
  },
  
  async getLeaderboard() {
    const response = await fetch(`${API_BASE_URL}/api/leaderboard`);
    return response.json();
  },
  
  async getHistoricalFacts() {
    const response = await fetch(`${API_BASE_URL}/api/educational-content/facts`);
    return response.json();
  },
  
  async getAnalytics(playerId) {
    const response = await fetch(`${API_BASE_URL}/api/analytics/${playerId}`);
    return response.json();
  }
};

// Helper function to get decision type emoji and color
const getDecisionTypeInfo = (type) => {
  const types = {
    trade: { emoji: '🌍', color: 'blue', name: 'Trade' },
    cultural: { emoji: '🎭', color: 'purple', name: 'Cultural' },
    environmental: { emoji: '🌱', color: 'green', name: 'Environmental' },
    business: { emoji: '💼', color: 'indigo', name: 'Business' },
    manufacturing: { emoji: '🏭', color: 'orange', name: 'Manufacturing' },
    logistics: { emoji: '🚢', color: 'cyan', name: 'Logistics' },
    human_resources: { emoji: '👥', color: 'pink', name: 'Human Resources' },
    marketing: { emoji: '📢', color: 'yellow', name: 'Marketing'
    }
  };
  return types[type] || { emoji: '❓', color: 'gray', name: 'Unknown' };
};

// Components
const CountrySelection = ({ countries, onSelectCountry, playerName, setPlayerName }) => (
  <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 flex items-center justify-center p-4">
    <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">🌍 Global Dynamics</h1>
        <p className="text-lg text-gray-600">Advanced Globalization Business Simulation</p>
        <p className="text-sm text-gray-500 mt-2">Make strategic decisions in trade, manufacturing, logistics, and more!</p>
      </div>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Your Name</label>
          <input
            type="text"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your name"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">Choose Your Country</label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {countries.map((country) => (
              <button
                key={country.name}
                onClick={() => onSelectCountry(country.name)}
                disabled={!playerName.trim()}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 text-left disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="font-semibold text-gray-800">{country.name}</div>
                <div className="text-sm text-gray-600">{country.region}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  </div>
);

const IndicatorCard = ({ title, value, unit, color, icon, description }) => (
  <div className={`bg-white rounded-lg shadow-md p-4 border-l-4 ${color} hover:shadow-lg transition-shadow duration-200`}>
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <p className="text-2xl font-bold text-gray-800">
          {typeof value === 'number' ? value.toFixed(1) : value}{unit}
        </p>
        {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
      </div>
      <div className="text-2xl">{icon}</div>
    </div>
  </div>
);

const BusinessMetricsPanel = ({ country }) => (
  <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
    <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
      <span className="mr-2">🏢</span>
      Business & Operations Dashboard
    </h2>
    
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Business Indicators */}
      <IndicatorCard
        title="Profit Margin"
        value={country.business_indicators.profit_margin}
        unit="%"
        color="border-green-500"
        icon="💰"
        description="Current profitability"
      />
      <IndicatorCard
        title="Market Share"
        value={country.business_indicators.market_share}
        unit="%"
        color="border-blue-500"
        icon="📊"
        description="Global market position"
      />
      <IndicatorCard
        title="Brand Reputation"
        value={country.business_indicators.brand_reputation}
        unit=""
        color="border-purple-500"
        icon="⭐"
        description="Brand perception score"
      />
      <IndicatorCard
        title="Innovation Index"
        value={country.business_indicators.innovation_index}
        unit=""
        color="border-indigo-500"
        icon="💡"
        description="Innovation capability"
      />
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Manufacturing Metrics */}
      <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
        <h3 className="font-semibold text-orange-800 mb-3 flex items-center">
          <span className="mr-2">🏭</span>Manufacturing
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Employees:</span>
            <span className="font-semibold">{country.manufacturing_metrics.total_employees.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Avg Salary:</span>
            <span className="font-semibold">${country.manufacturing_metrics.average_salary.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Automation:</span>
            <span className="font-semibold">{country.manufacturing_metrics.automation_level.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Production:</span>
            <span className="font-semibold">{country.manufacturing_metrics.production_capacity.toFixed(0)} units/day</span>
          </div>
        </div>
      </div>
      
      {/* Logistics Metrics */}
      <div className="bg-cyan-50 p-4 rounded-lg border border-cyan-200">
        <h3 className="font-semibold text-cyan-800 mb-3 flex items-center">
          <span className="mr-2">🚢</span>Logistics
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Shipping Cost:</span>
            <span className="font-semibold">${country.logistics_metrics.shipping_cost_per_unit.toFixed(2)}/unit</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Delivery Time:</span>
            <span className="font-semibold">{country.logistics_metrics.delivery_time_days.toFixed(1)} days</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Efficiency:</span>
            <span className="font-semibold">{country.logistics_metrics.logistics_efficiency.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Carbon Impact:</span>
            <span className="font-semibold">{country.logistics_metrics.carbon_footprint_shipping.toFixed(1)}</span>
          </div>
        </div>
      </div>
      
      {/* Marketing Metrics */}
      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
        <h3 className="font-semibold text-yellow-800 mb-3 flex items-center">
          <span className="mr-2">📢</span>Marketing
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Annual Spend:</span>
            <span className="font-semibold">${(country.marketing_metrics.marketing_spend / 1000).toFixed(0)}K</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Brand Awareness:</span>
            <span className="font-semibold">{country.marketing_metrics.brand_awareness.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Acquisition Cost:</span>
            <span className="font-semibold">${country.marketing_metrics.customer_acquisition_cost.toFixed(0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Global Presence:</span>
            <span className="font-semibold">{country.marketing_metrics.global_market_presence.toFixed(1)}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const GameDashboard = ({ gameState, onMakeDecision, onViewLeaderboard, onViewFacts, onViewAnalytics }) => {
  const { player, country, current_scenario } = gameState;
  const [selectedChoice, setSelectedChoice] = useState(null);
  const [showDecisionResult, setShowDecisionResult] = useState(false);
  const [decisionResult, setDecisionResult] = useState(null);
  
  const handleDecision = async (choiceIndex) => {
    try {
      const result = await api.makeDecision(player.id, current_scenario.title, choiceIndex);
      setDecisionResult(result);
      setShowDecisionResult(true);
      setTimeout(() => {
        setShowDecisionResult(false);
        onMakeDecision(); // Refresh game state
      }, 6000);
    } catch (error) {
      console.error('Error making decision:', error);
    }
  };
  
  if (showDecisionResult && decisionResult) {
    return (
      <div className="min-h-screen bg-gray-100 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <h2 className="text-3xl font-bold text-gray-800 mb-6">Decision Results</h2>
            
            <div className="mb-6">
              <div className="text-6xl mb-4">🎯</div>
              <p className="text-xl text-gray-600">You gained {decisionResult.score_gained} points!</p>
              {decisionResult.level_up && (
                <p className="text-lg text-green-600 font-semibold mt-2">🎊 Level Up! You're now level {player.level + 1}!</p>
              )}
              {decisionResult.achievements && decisionResult.achievements.length > 0 && (
                <p className="text-lg text-yellow-600 font-semibold mt-2">
                  🏆 Achievement Unlocked: {decisionResult.achievements[decisionResult.achievements.length - 1]}
                </p>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {Object.entries(decisionResult.consequences).map(([key, value]) => (
                <div key={key} className={`p-4 rounded-lg ${value > 0 ? 'bg-green-50 border border-green-200' : value < 0 ? 'bg-red-50 border border-red-200' : 'bg-gray-50 border border-gray-200'}`}>
                  <h3 className={`font-semibold text-sm ${value > 0 ? 'text-green-800' : value < 0 ? 'text-red-800' : 'text-gray-800'}`}>
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </h3>
                  <p className={`text-lg font-bold ${value > 0 ? 'text-green-600' : value < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                    {value > 0 ? '+' : ''}{value}
                  </p>
                </div>
              ))}
            </div>
            
            {decisionResult.educational_content && (
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-lg mb-6 text-left">
                <h3 className="font-semibold text-blue-800 mb-4 flex items-center">
                  <span className="mr-2">📚</span>Educational Insights
                </h3>
                <p className="text-blue-700 mb-4">{decisionResult.educational_content.scenario_context}</p>
                
                <div className="bg-white p-4 rounded-lg mb-4">
                  <h4 className="font-semibold text-gray-800 flex items-center mb-2">
                    <span className="mr-2">🕰️</span>{decisionResult.educational_content.historical_fact.title}
                  </h4>
                  <p className="text-sm text-gray-600">{decisionResult.educational_content.historical_fact.content}</p>
                </div>
                
                {decisionResult.educational_content.trivia_question && (
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-yellow-800 mb-2">💡 Quick Quiz</h4>
                    <p className="text-sm text-yellow-700 mb-2">{decisionResult.educational_content.trivia_question.question}</p>
                    <p className="text-xs text-yellow-600">
                      Answer: {decisionResult.educational_content.trivia_question.options[decisionResult.educational_content.trivia_question.correct_answer]}
                    </p>
                  </div>
                )}
              </div>
            )}
            
            <p className="text-gray-500">Loading next scenario...</p>
          </div>
        </div>
      </div>
    );
  }
  
  const decisionTypeInfo = getDecisionTypeInfo(current_scenario?.decision_type);
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Enhanced Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">🌍 Global Dynamics</h1>
              <p className="text-gray-600">{player.name} - {country.name}</p>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="text-sm text-gray-600">Score</div>
                <div className="text-xl font-bold text-blue-600">{player.score}</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">Level</div>
                <div className="text-xl font-bold text-green-600">{player.level}</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">Decisions</div>
                <div className="text-xl font-bold text-purple-600">{player.decisions_made}</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">Experience</div>
                <div className="text-xl font-bold text-orange-600">{player.business_experience || 0}</div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={onViewAnalytics}
                  className="px-3 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors text-sm"
                >
                  📊 Analytics
                </button>
                <button
                  onClick={onViewLeaderboard}
                  className="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
                >
                  🏆 Leaderboard
                </button>
                <button
                  onClick={onViewFacts}
                  className="px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                >
                  📚 Learn
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto p-6">
        {/* Achievements Display */}
        {player.achievements && player.achievements.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">🏆 Your Achievements</h3>
            <div className="flex flex-wrap gap-2">
              {player.achievements.map((achievement, index) => (
                <span key={index} className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                  {achievement}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Business Metrics Panel */}
        <BusinessMetricsPanel country={country} />
        
        {/* Traditional Indicators */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Core Country Indicators</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <IndicatorCard
              title="GDP"
              value={country.economic_indicators.gdp}
              unit="B"
              color="border-blue-500"
              icon="💰"
            />
            <IndicatorCard
              title="Unemployment"
              value={country.economic_indicators.unemployment}
              unit="%"
              color="border-red-500"
              icon="📊"
            />
            <IndicatorCard
              title="Carbon Emissions"
              value={country.environmental_indicators.carbon_emissions}
              unit=""
              color="border-orange-500"
              icon="🏭"
            />
            <IndicatorCard
              title="Cultural Openness"
              value={country.cultural_indicators.cultural_openness}
              unit=""
              color="border-purple-500"
              icon="🌐"
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <IndicatorCard
              title="Trade Balance"
              value={country.economic_indicators.trade_balance}
              unit=""
              color="border-green-500"
              icon="📈"
            />
            <IndicatorCard
              title="Sustainability Score"
              value={country.environmental_indicators.sustainability_score}
              unit=""
              color="border-emerald-500"
              icon="🌱"
            />
            <IndicatorCard
              title="Employee Satisfaction"
              value={country.business_indicators.employee_satisfaction}
              unit=""
              color="border-pink-500"
              icon="😊"
            />
          </div>
        </div>
        
        {/* Enhanced Current Scenario */}
        {current_scenario && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="mb-6">
              <div className="flex items-center mb-4">
                <span className={`inline-flex items-center px-4 py-2 bg-${decisionTypeInfo.color}-100 text-${decisionTypeInfo.color}-800 rounded-full text-sm font-medium mr-4`}>
                  <span className="mr-2">{decisionTypeInfo.emoji}</span>
                  {decisionTypeInfo.name} Decision
                </span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  current_scenario.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                  current_scenario.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {current_scenario.difficulty.toUpperCase()}
                </span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">{current_scenario.title}</h2>
              <p className="text-gray-600 text-lg leading-relaxed">{current_scenario.description}</p>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800">What will you do?</h3>
              {current_scenario.choices.map((choice, index) => (
                <button
                  key={index}
                  onClick={() => handleDecision(index)}
                  className="w-full p-6 text-left border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-gray-800 group-hover:text-blue-800 font-medium">{choice.text}</span>
                    <span className="text-blue-500 group-hover:text-blue-700 text-xl">→</span>
                  </div>
                </button>
              ))}
            </div>
            
            {current_scenario.historical_context && (
              <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <h4 className="font-semibold text-yellow-800 mb-2 flex items-center">
                  <span className="mr-2">🕰️</span>Historical Context
                </h4>
                <p className="text-yellow-700 text-sm">{current_scenario.historical_context}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const Analytics = ({ playerId, playerName, onBack }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const data = await api.getAnalytics(playerId);
        setAnalytics(data);
      } catch (error) {
        console.error('Error loading analytics:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadAnalytics();
  }, [playerId]);
  
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-800">📊 {playerName}'s Analytics</h1>
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              ← Back to Game
            </button>
          </div>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="text-gray-500">Loading analytics...</div>
            </div>
          ) : analytics ? (
            <div className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-blue-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-blue-800 mb-4">Decision Summary</h3>
                  <p className="text-3xl font-bold text-blue-600 mb-2">{analytics.total_decisions}</p>
                  <p className="text-blue-700">Total Decisions Made</p>
                </div>
                
                <div className="bg-green-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-green-800 mb-4">Experience Areas</h3>
                  <div className="space-y-2">
                    {Object.entries(analytics.experience_by_category).map(([category, count]) => {
                      const info = getDecisionTypeInfo(category);
                      return (
                        <div key={category} className="flex items-center justify-between">
                          <span className="flex items-center">
                            <span className="mr-2">{info.emoji}</span>
                            {info.name}
                          </span>
                          <span className="font-semibold">{count}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
              
              <div className="bg-purple-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-purple-800 mb-4">Decision Breakdown</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(analytics.decision_breakdown).map(([type, count]) => {
                    const info = getDecisionTypeInfo(type);
                    return (
                      <div key={type} className="text-center p-4 bg-white rounded-lg">
                        <div className="text-2xl mb-2">{info.emoji}</div>
                        <div className="font-semibold text-gray-800">{count}</div>
                        <div className="text-sm text-gray-600">{info.name}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-gray-500">No analytics data available</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const Leaderboard = ({ onBack }) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadLeaderboard = async () => {
      try {
        const data = await api.getLeaderboard();
        setLeaderboard(data);
      } catch (error) {
        console.error('Error loading leaderboard:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadLeaderboard();
  }, []);
  
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-800">🏆 Global Leaders</h1>
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              ← Back to Game
            </button>
          </div>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="text-gray-500">Loading leaderboard...</div>
            </div>
          ) : (
            <div className="space-y-4">
              {leaderboard.map((player, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-6 rounded-lg ${
                    index === 0 ? 'bg-yellow-50 border-2 border-yellow-200' :
                    index === 1 ? 'bg-gray-50 border-2 border-gray-200' :
                    index === 2 ? 'bg-orange-50 border-2 border-orange-200' :
                    'bg-white border border-gray-200'
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <div className="text-3xl">
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800 text-lg">{player.name}</div>
                      <div className="text-sm text-gray-600">
                        {player.decisions_made} decisions • {player.business_experience || 0} business experience
                      </div>
                      {player.achievements && player.achievements.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {player.achievements.slice(0, 3).map((achievement, i) => (
                            <span key={i} className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                              {achievement}
                            </span>
                          ))}
                          {player.achievements.length > 3 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{player.achievements.length - 3} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">{player.score}</div>
                    <div className="text-sm text-gray-600">Level {player.level}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const EducationalContent = ({ onBack }) => {
  const [facts, setFacts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadFacts = async () => {
      try {
        const data = await api.getHistoricalFacts();
        setFacts(data);
      } catch (error) {
        console.error('Error loading facts:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadFacts();
  }, []);
  
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-800">📚 Learn About Globalization</h1>
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              ← Back to Game
            </button>
          </div>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="text-gray-500">Loading educational content...</div>
            </div>
          ) : (
            <div className="space-y-6">
              {facts.map((fact, index) => (
                <div key={index} className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border-l-4 border-blue-500">
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">{fact.title}</h3>
                  {fact.year && (
                    <div className="text-sm text-blue-600 mb-2">
                      📅 {fact.year > 0 ? `${fact.year} CE` : `${Math.abs(fact.year)} BCE`}
                    </div>
                  )}
                  <p className="text-gray-700 leading-relaxed mb-3">{fact.content}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      fact.category === 'manufacturing' ? 'bg-orange-100 text-orange-800' :
                      fact.category === 'logistics' ? 'bg-cyan-100 text-cyan-800' :
                      fact.category === 'marketing' ? 'bg-yellow-100 text-yellow-800' :
                      fact.category === 'human_resources' ? 'bg-pink-100 text-pink-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {fact.category.replace(/_/g, ' ')}
                    </span>
                    {fact.relevance_tags.map((tag, tagIndex) => (
                      <span key={tagIndex} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        {tag.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [gamePhase, setGamePhase] = useState('country-selection'); // country-selection, game, leaderboard, education, analytics
  const [countries, setCountries] = useState([]);
  const [player, setPlayer] = useState(null);
  const [playerName, setPlayerName] = useState('');
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const loadCountries = async () => {
      try {
        const data = await api.getCountries();
        setCountries(data);
      } catch (error) {
        console.error('Error loading countries:', error);
      }
    };
    
    loadCountries();
  }, []);
  
  const handleCountrySelection = async (countryName) => {
    if (!playerName.trim()) return;
    
    setLoading(true);
    try {
      const newPlayer = await api.createPlayer(playerName, countryName);
      setPlayer(newPlayer);
      const state = await api.getGameState(newPlayer.id);
      setGameState(state);
      setGamePhase('game');
    } catch (error) {
      console.error('Error creating player:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const refreshGameState = async () => {
    if (player) {
      try {
        const state = await api.getGameState(player.id);
        setGameState(state);
      } catch (error) {
        console.error('Error refreshing game state:', error);
      }
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🌍</div>
          <div className="text-xl text-gray-600">Loading Global Dynamics...</div>
        </div>
      </div>
    );
  }
  
  if (gamePhase === 'country-selection') {
    return (
      <CountrySelection
        countries={countries}
        onSelectCountry={handleCountrySelection}
        playerName={playerName}
        setPlayerName={setPlayerName}
      />
    );
  }
  
  if (gamePhase === 'analytics') {
    return (
      <Analytics
        playerId={player.id}
        playerName={player.name}
        onBack={() => setGamePhase('game')}
      />
    );
  }
  
  if (gamePhase === 'leaderboard') {
    return <Leaderboard onBack={() => setGamePhase('game')} />;
  }
  
  if (gamePhase === 'education') {
    return <EducationalContent onBack={() => setGamePhase('game')} />;
  }
  
  if (gamePhase === 'game' && gameState) {
    return (
      <GameDashboard
        gameState={gameState}
        onMakeDecision={refreshGameState}
        onViewLeaderboard={() => setGamePhase('leaderboard')}
        onViewFacts={() => setGamePhase('education')}
        onViewAnalytics={() => setGamePhase('analytics')}
      />
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">⚠️</div>
        <div className="text-xl text-gray-600">Something went wrong. Please refresh the page.</div>
      </div>
    </div>
  );
};

export default App;