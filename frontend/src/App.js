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
  }
};

// Components
const CountrySelection = ({ countries, onSelectCountry, playerName, setPlayerName }) => (
  <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 flex items-center justify-center p-4">
    <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">🌍 Global Dynamics</h1>
        <p className="text-lg text-gray-600">Educational Globalization Simulation Game</p>
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

const IndicatorCard = ({ title, value, unit, color, icon }) => (
  <div className={`bg-white rounded-lg shadow-md p-4 border-l-4 ${color}`}>
    <div className="flex items-center justify-between">
      <div>
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <p className="text-2xl font-bold text-gray-800">
          {typeof value === 'number' ? value.toFixed(1) : value}{unit}
        </p>
      </div>
      <div className="text-2xl">{icon}</div>
    </div>
  </div>
);

const GameDashboard = ({ gameState, onMakeDecision, onViewLeaderboard, onViewFacts }) => {
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
      }, 5000);
    } catch (error) {
      console.error('Error making decision:', error);
    }
  };
  
  if (showDecisionResult && decisionResult) {
    return (
      <div className="min-h-screen bg-gray-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <h2 className="text-3xl font-bold text-gray-800 mb-6">Decision Results</h2>
            
            <div className="mb-6">
              <div className="text-6xl mb-4">🎯</div>
              <p className="text-xl text-gray-600">You gained {decisionResult.score_gained} points!</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800">Economic Impact</h3>
                <p className="text-sm text-blue-600">
                  GDP: {decisionResult.consequences.gdp > 0 ? '+' : ''}{decisionResult.consequences.gdp || 0}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800">Environmental Impact</h3>
                <p className="text-sm text-green-600">
                  Carbon: {decisionResult.consequences.carbon_emissions > 0 ? '+' : ''}{decisionResult.consequences.carbon_emissions || 0}
                </p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800">Cultural Impact</h3>
                <p className="text-sm text-purple-600">
                  Openness: {decisionResult.consequences.cultural_openness > 0 ? '+' : ''}{decisionResult.consequences.cultural_openness || 0}
                </p>
              </div>
            </div>
            
            {decisionResult.educational_content && (
              <div className="bg-yellow-50 p-6 rounded-lg mb-6 text-left">
                <h3 className="font-semibold text-yellow-800 mb-2">📚 Did You Know?</h3>
                <p className="text-yellow-700 mb-4">{decisionResult.educational_content.scenario_context}</p>
                
                <div className="bg-white p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800">{decisionResult.educational_content.historical_fact.title}</h4>
                  <p className="text-sm text-gray-600">{decisionResult.educational_content.historical_fact.content}</p>
                </div>
              </div>
            )}
            
            <p className="text-gray-500">Loading next scenario...</p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
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
              <button
                onClick={onViewLeaderboard}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                🏆 Leaderboard
              </button>
              <button
                onClick={onViewFacts}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                📚 Learn
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto p-6">
        {/* Country Indicators */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Country Indicators</h2>
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
              title="Renewable Energy"
              value={country.environmental_indicators.renewable_energy}
              unit="%"
              color="border-emerald-500"
              icon="🌱"
            />
            <IndicatorCard
              title="Diversity Index"
              value={country.cultural_indicators.diversity_index}
              unit=""
              color="border-pink-500"
              icon="🤝"
            />
          </div>
        </div>
        
        {/* Current Scenario */}
        {current_scenario && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="mb-6">
              <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium mb-4">
                {current_scenario.decision_type.charAt(0).toUpperCase() + current_scenario.decision_type.slice(1)} Decision
              </span>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">{current_scenario.title}</h2>
              <p className="text-gray-600 text-lg leading-relaxed">{current_scenario.description}</p>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800">What will you do?</h3>
              {current_scenario.choices.map((choice, index) => (
                <button
                  key={index}
                  onClick={() => handleDecision(index)}
                  className="w-full p-4 text-left border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-gray-800 group-hover:text-blue-800">{choice.text}</span>
                    <span className="text-blue-500 group-hover:text-blue-700">→</span>
                  </div>
                </button>
              ))}
            </div>
            
            {current_scenario.historical_context && (
              <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
                <h4 className="font-semibold text-yellow-800 mb-2">🕰️ Historical Context</h4>
                <p className="text-yellow-700 text-sm">{current_scenario.historical_context}</p>
              </div>
            )}
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
                  className={`flex items-center justify-between p-4 rounded-lg ${
                    index === 0 ? 'bg-yellow-50 border-2 border-yellow-200' :
                    index === 1 ? 'bg-gray-50 border-2 border-gray-200' :
                    index === 2 ? 'bg-orange-50 border-2 border-orange-200' :
                    'bg-white border border-gray-200'
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <div className="text-2xl">
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">{player.name}</div>
                      <div className="text-sm text-gray-600">{player.decisions_made} decisions made</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-blue-600">{player.score} pts</div>
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
                  <p className="text-gray-700 leading-relaxed">{fact.content}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {fact.relevance_tags.map((tag, tagIndex) => (
                      <span key={tagIndex} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
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
  const [gamePhase, setGamePhase] = useState('country-selection'); // country-selection, game, leaderboard, education
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