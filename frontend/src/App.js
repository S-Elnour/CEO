import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// API Helper Functions
const api = {
  async getIndustries() {
    const response = await fetch(`${API_BASE_URL}/api/industries`);
    return response.json();
  },
  
  async createCompany(playerName, companyName, industry) {
    const response = await fetch(`${API_BASE_URL}/api/company`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        player_name: playerName, 
        company_name: companyName, 
        industry: industry 
      })
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
  }
};

// Helper functions for business decision types
const getDecisionTypeInfo = (type) => {
  const types = {
    materials: { emoji: '📦', color: 'orange', name: 'Materials', description: 'Supply chain and sourcing decisions' },
    logistics: { emoji: '🚚', color: 'blue', name: 'Logistics', description: 'Shipping and distribution strategies' },
    workforce: { emoji: '👥', color: 'green', name: 'Workforce', description: 'Human resources and talent management' },
    marketing: { emoji: '📈', color: 'purple', name: 'Marketing', description: 'Brand building and customer acquisition' },
    finance: { emoji: '💰', color: 'yellow', name: 'Finance', description: 'Investment and capital allocation' },
    expansion: { emoji: '🌍', color: 'red', name: 'Expansion', description: 'Growth and scaling strategies' }
  };
  return types[type] || { emoji: '❓', color: 'gray', name: 'Unknown', description: 'General business decision' };
};

// Components
const CompanySetup = ({ industries, onCreateCompany }) => {
  const [playerName, setPlayerName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('');
  
  const handleSubmit = () => {
    if (playerName.trim() && companyName.trim() && selectedIndustry) {
      onCreateCompany(playerName, companyName, selectedIndustry);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-3xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">🏢 Business Empire</h1>
          <p className="text-xl text-gray-600">Build Your Business. Make Strategic Decisions. Dominate Markets.</p>
        </div>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Your Name</label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              placeholder="Enter your name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              placeholder="Enter your company name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">Choose Your Industry</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {industries.map((industry) => (
                <button
                  key={industry.name}
                  onClick={() => setSelectedIndustry(industry.name)}
                  className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                    selectedIndustry === industry.name
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-semibold text-gray-800">{industry.name}</div>
                  <div className="text-sm text-gray-600">{industry.description}</div>
                </button>
              ))}
            </div>
          </div>
          
          <button
            onClick={handleSubmit}
            disabled={!playerName.trim() || !companyName.trim() || !selectedIndustry}
            className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🚀 Start Your Business Empire
          </button>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, unit, icon, trend, color = "blue" }) => (
  <div className={`bg-white rounded-xl shadow-lg p-6 border-l-4 border-${color}-500 hover:shadow-xl transition-shadow duration-200`}>
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">{title}</h3>
        <p className="text-3xl font-bold text-gray-800 mt-2">
          {typeof value === 'number' ? 
            (value >= 1000 ? `${(value/1000).toFixed(1)}K` : value.toFixed(1)) 
            : value
          }{unit}
        </p>
        {trend && (
          <p className={`text-sm mt-1 flex items-center ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '↗️' : '↘️'} {Math.abs(trend).toFixed(1)}%
          </p>
        )}
      </div>
      <div className="text-4xl opacity-80">{icon}</div>
    </div>
  </div>
);

const BusinessDashboard = ({ gameState, onMakeDecision, onViewLeaderboard }) => {
  const { player, company, current_scenario, monthly_report } = gameState;
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
      }, 5000);
    } catch (error) {
      console.error('Error making decision:', error);
    }
  };
  
  if (showDecisionResult && decisionResult) {
    return (
      <div className="min-h-screen bg-gray-100 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-3xl shadow-2xl p-8 text-center">
            <h2 className="text-4xl font-bold text-gray-800 mb-6">Decision Results</h2>
            
            <div className="mb-8">
              <div className="text-7xl mb-4">
                {decisionResult.success_score >= 80 ? '🎉' : 
                 decisionResult.success_score >= 60 ? '👍' : 
                 decisionResult.success_score >= 40 ? '🤔' : '😬'}
              </div>
              <div className="text-2xl font-semibold text-gray-700 mb-2">
                Decision Success: {decisionResult.success_score.toFixed(1)}/100
              </div>
              <p className="text-xl text-blue-600">+{decisionResult.xp_gained} Experience Points!</p>
              {decisionResult.level_up && (
                <p className="text-lg text-green-600 font-semibold mt-2">
                  🎊 Level Up! You're now level {player.level + 1}!
                </p>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                <h3 className="font-semibold text-green-800 mb-2">📊 Monthly Revenue</h3>
                <p className="text-2xl font-bold text-green-600">
                  ${decisionResult.monthly_report.monthly_revenue.toLocaleString()}
                </p>
              </div>
              <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-800 mb-2">💰 Monthly Profit</h3>
                <p className="text-2xl font-bold text-blue-600">
                  ${decisionResult.monthly_report.monthly_profit.toLocaleString()}
                </p>
              </div>
              <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                <h3 className="font-semibold text-purple-800 mb-2">📈 Profit Margin</h3>
                <p className="text-2xl font-bold text-purple-600">
                  {decisionResult.monthly_report.profit_margin.toFixed(1)}%
                </p>
              </div>
            </div>
            
            {decisionResult.learning_objective && (
              <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200 mb-6 text-left">
                <h3 className="font-semibold text-yellow-800 mb-2 flex items-center">
                  <span className="mr-2">💡</span>Learning Objective
                </h3>
                <p className="text-yellow-700">{decisionResult.learning_objective}</p>
              </div>
            )}
            
            <p className="text-gray-500">Preparing next business challenge...</p>
          </div>
        </div>
      </div>
    );
  }
  
  const decisionTypeInfo = getDecisionTypeInfo(current_scenario?.decision_type);
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 flex items-center">
                <span className="mr-3">🏢</span>
                {company.name}
              </h1>
              <p className="text-gray-600 mt-1">
                {player.name} • {company.industry} • Level {player.level}
              </p>
            </div>
            <div className="flex items-center space-x-8">
              <div className="text-center">
                <div className="text-sm text-gray-600">Experience</div>
                <div className="text-xl font-bold text-purple-600">{player.experience_points}</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">Decisions</div>
                <div className="text-xl font-bold text-blue-600">{player.total_decisions}</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">Success Rate</div>
                <div className="text-xl font-bold text-green-600">
                  {player.total_decisions > 0 ? 
                    ((player.successful_decisions / player.total_decisions) * 100).toFixed(1) 
                    : 0}%
                </div>
              </div>
              <button
                onClick={onViewLeaderboard}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-200"
              >
                🏆 Leaderboard
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto p-6">
        {/* Achievements */}
        {player.achievements && player.achievements.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">🏆 Your Achievements</h3>
            <div className="flex flex-wrap gap-3">
              {player.achievements.map((achievement, index) => (
                <span key={index} className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-400 text-white rounded-full text-sm font-medium shadow-lg">
                  {achievement}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Monthly Performance */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">📊 Monthly Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Revenue"
              value={monthly_report.monthly_revenue}
              unit=""
              icon="💰"
              color="green"
            />
            <MetricCard
              title="Profit"
              value={monthly_report.monthly_profit}
              unit=""
              icon="📈"
              color="blue"
            />
            <MetricCard
              title="Profit Margin"
              value={monthly_report.profit_margin}
              unit="%"
              icon="📊"
              color="purple"
            />
            <MetricCard
              title="Units Sold"
              value={monthly_report.units_sold}
              unit=""
              icon="📦"
              color="orange"
            />
          </div>
        </div>
        
        {/* Business Metrics */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">🏢 Business Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Cash"
              value={company.business_metrics.cash}
              unit=""
              icon="💵"
              color="green"
            />
            <MetricCard
              title="Market Share"
              value={company.business_metrics.market_share}
              unit="%"
              icon="🎯"
              color="blue"
            />
            <MetricCard
              title="Reputation"
              value={company.business_metrics.reputation}
              unit=""
              icon="⭐"
              color="yellow"
            />
            <MetricCard
              title="Efficiency"
              value={company.business_metrics.efficiency}
              unit="%"
              icon="⚡"
              color="purple"
            />
          </div>
        </div>
        
        {/* Operational Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Production */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">🏭</span>Production
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Capacity:</span>
                <span className="font-semibold">{company.production_metrics.production_capacity} units</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Material Cost:</span>
                <span className="font-semibold">${company.production_metrics.material_cost_per_unit}/unit</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Quality Score:</span>
                <span className="font-semibold">{company.production_metrics.quality_score.toFixed(1)}/100</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Production Time:</span>
                <span className="font-semibold">{company.production_metrics.production_time_days} days</span>
              </div>
            </div>
          </div>
          
          {/* Workforce */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">👥</span>Workforce
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Employees:</span>
                <span className="font-semibold">{company.workforce_metrics.total_employees}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Salary:</span>
                <span className="font-semibold">${(company.workforce_metrics.average_salary/1000).toFixed(1)}K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Satisfaction:</span>
                <span className="font-semibold">{company.workforce_metrics.employee_satisfaction.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Productivity:</span>
                <span className="font-semibold">{company.workforce_metrics.productivity.toFixed(1)}%</span>
              </div>
            </div>
          </div>
          
          {/* Marketing */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">📢</span>Marketing
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Brand Awareness:</span>
                <span className="font-semibold">{company.marketing_metrics.brand_awareness.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Customer Loyalty:</span>
                <span className="font-semibold">{company.marketing_metrics.customer_loyalty.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Monthly Budget:</span>
                <span className="font-semibold">${(company.marketing_metrics.marketing_budget/1000).toFixed(1)}K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Market Penetration:</span>
                <span className="font-semibold">{company.marketing_metrics.market_penetration.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Current Business Challenge */}
        {current_scenario && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="mb-6">
              <div className="flex items-center mb-4">
                <span className={`inline-flex items-center px-4 py-2 bg-${decisionTypeInfo.color}-100 text-${decisionTypeInfo.color}-800 rounded-full text-sm font-medium mr-4`}>
                  <span className="mr-2">{decisionTypeInfo.emoji}</span>
                  {decisionTypeInfo.name} Challenge
                </span>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">{current_scenario.title}</h2>
              <p className="text-gray-600 text-lg leading-relaxed mb-4">{current_scenario.description}</p>
              <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                <p className="text-blue-800 font-medium">Current Situation:</p>
                <p className="text-blue-700">{current_scenario.current_situation}</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-800">Choose your strategy:</h3>
              {current_scenario.choices.map((choice, index) => (
                <button
                  key={index}
                  onClick={() => handleDecision(index)}
                  className="w-full p-6 text-left border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <span className="text-gray-800 group-hover:text-blue-800 font-medium text-lg">
                        {choice.text}
                      </span>
                    </div>
                    <span className="text-blue-500 group-hover:text-blue-700 text-2xl ml-4">→</span>
                  </div>
                </button>
              ))}
            </div>
            
            <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <h4 className="font-semibold text-yellow-800 mb-2 flex items-center">
                <span className="mr-2">🎯</span>Learning Focus
              </h4>
              <p className="text-yellow-700 text-sm">{current_scenario.learning_objective}</p>
            </div>
          </div>
        )}
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
      <div className="max-w-5xl mx-auto">
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-4xl font-bold text-gray-800">🏆 Business Empire Leaderboard</h1>
            <button
              onClick={onBack}
              className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              ← Back to Dashboard
            </button>
          </div>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="text-gray-500">Loading leaderboard...</div>
            </div>
          ) : (
            <div className="space-y-4">
              {leaderboard.map((entry, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-6 rounded-xl ${
                    index === 0 ? 'bg-gradient-to-r from-yellow-50 to-yellow-100 border-2 border-yellow-300' :
                    index === 1 ? 'bg-gradient-to-r from-gray-50 to-gray-100 border-2 border-gray-300' :
                    index === 2 ? 'bg-gradient-to-r from-orange-50 to-orange-100 border-2 border-orange-300' :
                    'bg-white border border-gray-200'
                  }`}
                >
                  <div className="flex items-center space-x-6">
                    <div className="text-4xl">
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                    </div>
                    <div>
                      <div className="font-bold text-xl text-gray-800">{entry.company_name}</div>
                      <div className="text-gray-600">CEO: {entry.player_name}</div>
                      <div className="text-sm text-gray-500">{entry.industry} • Level {entry.level}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-600">
                      ${(entry.monthly_revenue/1000).toFixed(1)}K/mo
                    </div>
                    <div className="text-sm text-gray-600">{entry.experience_points} XP</div>
                    <div className="text-sm text-blue-600">{entry.success_rate.toFixed(1)}% Success Rate</div>
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
  const [gamePhase, setGamePhase] = useState('setup'); // setup, game, leaderboard
  const [industries, setIndustries] = useState([]);
  const [player, setPlayer] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const loadIndustries = async () => {
      try {
        const data = await api.getIndustries();
        setIndustries(data);
      } catch (error) {
        console.error('Error loading industries:', error);
      }
    };
    
    loadIndustries();
  }, []);
  
  const handleCreateCompany = async (playerName, companyName, industry) => {
    setLoading(true);
    try {
      const newPlayer = await api.createCompany(playerName, companyName, industry);
      setPlayer(newPlayer);
      const state = await api.getGameState(newPlayer.id);
      setGameState(state);
      setGamePhase('game');
    } catch (error) {
      console.error('Error creating company:', error);
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
          <div className="text-6xl mb-4">🏢</div>
          <div className="text-2xl text-gray-600">Building Your Business Empire...</div>
        </div>
      </div>
    );
  }
  
  if (gamePhase === 'setup') {
    return (
      <CompanySetup
        industries={industries}
        onCreateCompany={handleCreateCompany}
      />
    );
  }
  
  if (gamePhase === 'leaderboard') {
    return <Leaderboard onBack={() => setGamePhase('game')} />;
  }
  
  if (gamePhase === 'game' && gameState) {
    return (
      <BusinessDashboard
        gameState={gameState}
        onMakeDecision={refreshGameState}
        onViewLeaderboard={() => setGamePhase('leaderboard')}
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