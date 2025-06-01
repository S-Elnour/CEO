import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// API Helper Functions
const api = {
  async createCompany(playerName, companyName) {
    const response = await fetch(`${API_BASE_URL}/api/company`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        player_name: playerName, 
        company_name: companyName
      })
    });
    return response.json();
  },
  
  async getGameState(playerId) {
    const response = await fetch(`${API_BASE_URL}/api/game-state/${playerId}`);
    return response.json();
  },
  
  async makeDecision(playerId, choiceId) {
    const response = await fetch(`${API_BASE_URL}/api/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        player_id: playerId, 
        choice_id: choiceId
      })
    });
    return response.json();
  },
  
  async startNextYear(playerId) {
    const response = await fetch(`${API_BASE_URL}/api/next-year/${playerId}`, {
      method: 'POST'
    });
    return response.json();
  },
  
  async getLeaderboard() {
    const response = await fetch(`${API_BASE_URL}/api/leaderboard`);
    return response.json();
  }
};

// Helper functions
const getDecisionIcon = (decisionType) => {
  const icons = {
    factory_location: '🏭',
    raw_materials: '📦',
    shipping_method: '🚢',
    employee_count: '👥',
    salary: '💰',
    marketing_budget: '📢'
  };
  return icons[decisionType] || '❓';
};

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

// Components
const CompanySetup = ({ onCreateCompany }) => {
  const [playerName, setPlayerName] = useState('');
  const [companyName, setCompanyName] = useState('');
  
  const handleSubmit = () => {
    if (playerName.trim() && companyName.trim()) {
      onCreateCompany(playerName, companyName);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-600 via-blue-600 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-2xl w-full text-center">
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">🌍 Global Supply Chain Simulator</h1>
          <p className="text-xl text-gray-600 mb-2">Make Strategic Business Decisions</p>
          <p className="text-lg text-gray-500">Navigate the trade-offs between profit, pollution, and employee treatment</p>
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
          
          <button
            onClick={handleSubmit}
            disabled={!playerName.trim() || !companyName.trim()}
            className="w-full py-4 bg-gradient-to-r from-green-600 to-blue-600 text-white text-lg font-semibold rounded-lg hover:from-green-700 hover:to-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🚀 Start Your Global Business
          </button>
        </div>
      </div>
    </div>
  );
};

const MetricsDisplay = ({ metrics, year }) => (
  <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
    <h2 className="text-2xl font-semibold text-gray-800 mb-4">Year {year} Performance</h2>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="text-center p-4 bg-green-50 rounded-lg">
        <div className="text-3xl mb-2">💰</div>
        <h3 className="text-lg font-semibold text-green-800">Profit</h3>
        <p className="text-2xl font-bold text-green-600">{formatCurrency(metrics.profit)}</p>
        <p className="text-sm text-gray-600">Higher is better</p>
      </div>
      
      <div className="text-center p-4 bg-red-50 rounded-lg">
        <div className="text-3xl mb-2">🏭</div>
        <h3 className="text-lg font-semibold text-red-800">Pollution</h3>
        <p className="text-2xl font-bold text-red-600">{metrics.pollution.toFixed(1)}</p>
        <p className="text-sm text-gray-600">Lower is better</p>
      </div>
      
      <div className="text-center p-4 bg-blue-50 rounded-lg">
        <div className="text-3xl mb-2">👥</div>
        <h3 className="text-lg font-semibold text-blue-800">Employee Treatment</h3>
        <p className="text-2xl font-bold text-blue-600">{metrics.employee_treatment.toFixed(1)}</p>
        <p className="text-sm text-gray-600">Higher is better</p>
      </div>
    </div>
  </div>
);

const DecisionCard = ({ decision, onMakeChoice }) => (
  <div className="bg-white rounded-2xl shadow-xl p-8">
    <div className="text-center mb-6">
      <div className="text-6xl mb-4">{getDecisionIcon(decision.decision_type)}</div>
      <h2 className="text-3xl font-bold text-gray-800 mb-2">{decision.title}</h2>
      <p className="text-xl text-gray-600 font-medium">{decision.question}</p>
      <p className="text-gray-500 mt-2">{decision.description}</p>
    </div>
    
    <div className="space-y-4">
      {decision.options.map((option, index) => (
        <button
          key={option.id}
          onClick={() => onMakeChoice(option.id)}
          className="w-full p-6 text-left border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 group"
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-800 group-hover:text-blue-800 mb-2">
                {option.text}
              </h3>
              <p className="text-gray-600 text-sm mb-3">{option.description}</p>
              
              <div className="flex flex-wrap gap-2">
                {Object.entries(option.consequences).map(([key, value]) => (
                  <span
                    key={key}
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      value > 0 
                        ? key === 'pollution' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                        : value < 0
                          ? key === 'pollution'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {key.replace('_', ' ')}: {value > 0 ? '+' : ''}{value}
                    {key === 'profit' ? '' : ''}
                  </span>
                ))}
              </div>
            </div>
            <div className="text-blue-500 group-hover:text-blue-700 text-2xl ml-4">→</div>
          </div>
        </button>
      ))}
    </div>
  </div>
);

const DecisionResult = ({ result, onContinue }) => (
  <div className="min-h-screen bg-gray-100 p-4 flex items-center justify-center">
    <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-4xl w-full text-center">
      <h2 className="text-4xl font-bold text-gray-800 mb-6">Decision Made!</h2>
      
      <div className="mb-8">
        <div className="text-6xl mb-4">✅</div>
        <p className="text-xl text-gray-700 mb-4">You chose: <strong>{result.choice_made}</strong></p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {Object.entries(result.consequences).map(([key, value]) => (
          <div key={key} className={`p-4 rounded-lg ${
            value > 0 
              ? key === 'pollution' 
                ? 'bg-red-50 border border-red-200' 
                : 'bg-green-50 border border-green-200'
              : value < 0
                ? key === 'pollution'
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
                : 'bg-gray-50 border border-gray-200'
          }`}>
            <h3 className={`font-semibold text-lg ${
              value > 0 
                ? key === 'pollution' 
                  ? 'text-red-800' 
                  : 'text-green-800'
                : value < 0
                  ? key === 'pollution'
                    ? 'text-green-800'
                    : 'text-red-800'
                  : 'text-gray-800'
            }`}>
              {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h3>
            <p className={`text-2xl font-bold ${
              value > 0 
                ? key === 'pollution' 
                  ? 'text-red-600' 
                  : 'text-green-600'
                : value < 0
                  ? key === 'pollution'
                    ? 'text-green-600'
                    : 'text-red-600'
                  : 'text-gray-600'
            }`}>
              {value > 0 ? '+' : ''}{value}
              {key === 'profit' ? '' : ''}
            </p>
          </div>
        ))}
      </div>
      
      <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200 mb-8 text-left">
        <h3 className="font-semibold text-yellow-800 mb-2 flex items-center">
          <span className="mr-2">💡</span>Did You Know?
        </h3>
        <p className="text-yellow-700">{result.educational_fact}</p>
      </div>
      
      <button
        onClick={onContinue}
        className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
      >
        Continue to Next Decision
      </button>
    </div>
  </div>
);

const YearEndReport = ({ yearScore, metrics, year, onNextYear, onViewLeaderboard }) => (
  <div className="min-h-screen bg-gray-100 p-4 flex items-center justify-center">
    <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-4xl w-full text-center">
      <h2 className="text-4xl font-bold text-gray-800 mb-6">Year {year} Complete!</h2>
      
      <div className="mb-8">
        <div className="text-7xl mb-4">
          {yearScore >= 80 ? '🏆' : 
           yearScore >= 60 ? '🎉' : 
           yearScore >= 40 ? '👍' : '😬'}
        </div>
        <p className="text-3xl font-bold text-blue-600 mb-2">Year Score: {yearScore}/100</p>
        <p className="text-lg text-gray-600">
          {yearScore >= 80 ? 'Outstanding Performance!' : 
           yearScore >= 60 ? 'Good Job!' : 
           yearScore >= 40 ? 'Room for Improvement' : 'Challenging Year'}
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="p-6 bg-green-50 rounded-lg border border-green-200">
          <div className="text-4xl mb-2">💰</div>
          <h3 className="text-lg font-semibold text-green-800">Final Profit</h3>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(metrics.profit)}</p>
        </div>
        
        <div className="p-6 bg-red-50 rounded-lg border border-red-200">
          <div className="text-4xl mb-2">🏭</div>
          <h3 className="text-lg font-semibold text-red-800">Total Pollution</h3>
          <p className="text-2xl font-bold text-red-600">{metrics.pollution.toFixed(1)}</p>
        </div>
        
        <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
          <div className="text-4xl mb-2">👥</div>
          <h3 className="text-lg font-semibold text-blue-800">Employee Treatment</h3>
          <p className="text-2xl font-bold text-blue-600">{metrics.employee_treatment.toFixed(1)}</p>
        </div>
      </div>
      
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 mb-8">
        <h3 className="text-xl font-semibold text-blue-800 mb-2">Scoring Breakdown</h3>
        <p className="text-blue-700 text-sm">
          Your score is calculated from: Profit (40%) + Environmental Impact (30%) + Employee Treatment (30%)
        </p>
      </div>
      
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        {year < 5 ? (
          <button
            onClick={onNextYear}
            className="px-8 py-4 bg-gradient-to-r from-green-600 to-blue-600 text-white text-lg font-semibold rounded-lg hover:from-green-700 hover:to-blue-700 transition-all duration-200"
          >
            Start Year {year + 1}
          </button>
        ) : (
          <button
            onClick={onViewLeaderboard}
            className="px-8 py-4 bg-gradient-to-r from-yellow-600 to-orange-600 text-white text-lg font-semibold rounded-lg hover:from-yellow-700 hover:to-orange-700 transition-all duration-200"
          >
            View Final Results
          </button>
        )}
        
        <button
          onClick={onViewLeaderboard}
          className="px-8 py-4 bg-gray-600 text-white text-lg font-semibold rounded-lg hover:bg-gray-700 transition-all duration-200"
        >
          View Leaderboard
        </button>
      </div>
    </div>
  </div>
);

const Leaderboard = ({ onBack, isGameComplete = false }) => {
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
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-4xl font-bold text-gray-800">
              🏆 {isGameComplete ? 'Final Results' : 'Global Leaderboard'}
            </h1>
            <button
              onClick={onBack}
              className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
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
                      <div className="text-sm text-gray-500">
                        {entry.years_completed} years completed • Year {entry.current_year}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-blue-600">
                      {entry.total_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">Total Score</div>
                  </div>
                </div>
              ))}
              
              {leaderboard.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No companies yet. Be the first to start your global business!
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ProgressIndicator = ({ currentDecision, year }) => (
  <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
    <div className="flex items-center justify-between mb-2">
      <h3 className="text-lg font-semibold text-gray-800">Year {year} Progress</h3>
      <span className="text-sm text-gray-600">Decision {currentDecision}/6</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-3">
      <div 
        className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-300"
        style={{ width: `${(currentDecision / 6) * 100}%` }}
      ></div>
    </div>
    <div className="flex justify-between text-xs text-gray-500 mt-1">
      <span>🏭 Factory</span>
      <span>📦 Materials</span>
      <span>🚢 Shipping</span>
      <span>👥 Staff</span>
      <span>💰 Salary</span>
      <span>📢 Marketing</span>
    </div>
  </div>
);

// Main App Component
const App = () => {
  const [gamePhase, setGamePhase] = useState('setup'); // setup, game, decision-result, year-end, leaderboard
  const [player, setPlayer] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [decisionResult, setDecisionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleCreateCompany = async (playerName, companyName) => {
    setLoading(true);
    try {
      const newPlayer = await api.createCompany(playerName, companyName);
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
  
  const handleMakeDecision = async (choiceId) => {
    try {
      const result = await api.makeDecision(player.id, choiceId);
      setDecisionResult(result);
      setGamePhase('decision-result');
    } catch (error) {
      console.error('Error making decision:', error);
    }
  };
  
  const handleContinueAfterDecision = async () => {
    await refreshGameState();
    if (decisionResult.year_complete) {
      setGamePhase('year-end');
    } else {
      setGamePhase('game');
    }
  };
  
  const handleNextYear = async () => {
    try {
      await api.startNextYear(player.id);
      await refreshGameState();
      setGamePhase('game');
    } catch (error) {
      console.error('Error starting next year:', error);
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🌍</div>
          <div className="text-2xl text-gray-600">Setting up your global business...</div>
        </div>
      </div>
    );
  }
  
  if (gamePhase === 'setup') {
    return <CompanySetup onCreateCompany={handleCreateCompany} />;
  }
  
  if (gamePhase === 'decision-result' && decisionResult) {
    return (
      <DecisionResult 
        result={decisionResult}
        onContinue={handleContinueAfterDecision}
      />
    );
  }
  
  if (gamePhase === 'year-end' && decisionResult) {
    return (
      <YearEndReport
        yearScore={decisionResult.year_score}
        metrics={decisionResult.updated_metrics}
        year={gameState.company.current_year - 1}
        onNextYear={handleNextYear}
        onViewLeaderboard={() => setGamePhase('leaderboard')}
      />
    );
  }
  
  if (gamePhase === 'leaderboard') {
    return (
      <Leaderboard 
        onBack={() => setGamePhase(gameState.game_complete ? 'year-end' : 'game')}
        isGameComplete={gameState?.game_complete}
      />
    );
  }
  
  if (gamePhase === 'game' && gameState) {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Header */}
        <div className="bg-white shadow-lg border-b">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-800 flex items-center">
                  <span className="mr-3">🌍</span>
                  {gameState.company.name}
                </h1>
                <p className="text-gray-600 mt-1">CEO: {gameState.player.name}</p>
              </div>
              <button
                onClick={() => setGamePhase('leaderboard')}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-200"
              >
                🏆 Leaderboard
              </button>
            </div>
          </div>
        </div>
        
        <div className="max-w-6xl mx-auto p-6">
          {gameState.year_complete ? (
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Year {gameState.company.current_year} Complete!</h2>
              <p className="text-gray-600 mb-6">All decisions made for this year.</p>
              <button
                onClick={handleNextYear}
                className="px-8 py-4 bg-gradient-to-r from-green-600 to-blue-600 text-white text-lg font-semibold rounded-lg"
              >
                Start Year {gameState.company.current_year + 1}
              </button>
            </div>
          ) : gameState.current_decision ? (
            <>
              <ProgressIndicator 
                currentDecision={gameState.company.current_decision} 
                year={gameState.company.current_year}
              />
              <MetricsDisplay 
                metrics={gameState.company.metrics} 
                year={gameState.company.current_year}
              />
              <DecisionCard 
                decision={gameState.current_decision}
                onMakeChoice={handleMakeDecision}
              />
            </>
          ) : (
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Game Complete!</h2>
              <p className="text-gray-600 mb-6">You've completed all 5 years of the simulation.</p>
              <button
                onClick={() => setGamePhase('leaderboard')}
                className="px-8 py-4 bg-gradient-to-r from-yellow-600 to-orange-600 text-white text-lg font-semibold rounded-lg"
              >
                View Final Results
              </button>
            </div>
          )}
        </div>
      </div>
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