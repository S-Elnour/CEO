import requests
import unittest
import json
import time
from datetime import datetime

class GlobalDynamicsAPITester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(GlobalDynamicsAPITester, self).__init__(*args, **kwargs)
        self.base_url = "https://89b642e9-fce9-40f3-9d44-9b780dc99924.preview.emergentagent.com/api"
        self.player_id = None
        self.country_id = None
        self.test_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.player_name = f"TestPlayer_{self.test_timestamp}"

    def test_01_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n🔍 Testing root endpoint...")
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print("✅ Root endpoint test passed")

    def test_02_get_countries(self):
        """Test getting available countries"""
        print("\n🔍 Testing get countries endpoint...")
        response = requests.get(f"{self.base_url}/countries")
        self.assertEqual(response.status_code, 200)
        countries = response.json()
        self.assertIsInstance(countries, list)
        self.assertGreater(len(countries), 0)
        print(f"✅ Retrieved {len(countries)} countries")
        return countries

    def test_03_create_player(self):
        """Test creating a new player"""
        print(f"\n🔍 Testing player creation with name: {self.player_name}...")
        countries = self.test_02_get_countries()
        country_name = countries[0]["name"]
        
        response = requests.post(
            f"{self.base_url}/player",
            json={"name": self.player_name, "country_name": country_name}
        )
        self.assertEqual(response.status_code, 200)
        player = response.json()
        self.assertIn("id", player)
        self.assertEqual(player["name"], self.player_name)
        self.player_id = player["id"]
        self.country_id = player["country_id"]
        print(f"✅ Created player with ID: {self.player_id}")
        return player

    def test_04_get_game_state(self):
        """Test getting game state for a player"""
        if not self.player_id:
            self.test_03_create_player()
            
        print(f"\n🔍 Testing game state retrieval for player: {self.player_id}...")
        response = requests.get(f"{self.base_url}/game-state/{self.player_id}")
        self.assertEqual(response.status_code, 200)
        game_state = response.json()
        
        # Verify game state structure
        self.assertIn("player", game_state)
        self.assertIn("country", game_state)
        self.assertIn("current_scenario", game_state)
        
        # Verify player data
        self.assertEqual(game_state["player"]["id"], self.player_id)
        self.assertEqual(game_state["player"]["name"], self.player_name)
        
        # Verify country data
        self.assertEqual(game_state["country"]["id"], self.country_id)
        
        # Verify scenario data
        self.assertIn("title", game_state["current_scenario"])
        self.assertIn("description", game_state["current_scenario"])
        self.assertIn("choices", game_state["current_scenario"])
        
        print("✅ Game state retrieved successfully")
        return game_state

    def test_05_make_decision(self):
        """Test making a decision"""
        game_state = self.test_04_get_game_state()
        scenario = game_state["current_scenario"]
        
        print(f"\n🔍 Testing decision making for scenario: {scenario['title']}...")
        
        # Make a decision (choose the first option)
        response = requests.post(
            f"{self.base_url}/decision",
            json={
                "player_id": self.player_id,
                "scenario_id": scenario["title"],
                "choice_index": 0
            }
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Verify decision result structure
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("score_gained", result)
        self.assertIn("consequences", result)
        self.assertIn("educational_content", result)
        self.assertIn("updated_indicators", result)
        
        print(f"✅ Decision made successfully, gained {result['score_gained']} points")
        return result

    def test_06_get_scenarios_by_type(self):
        """Test getting scenarios by decision type"""
        print("\n🔍 Testing scenarios by type...")
        
        # Test each decision type
        decision_types = [
            "trade", "cultural", "environmental", "business", 
            "manufacturing", "logistics", "human_resources", "marketing"
        ]
        
        for decision_type in decision_types:
            print(f"  Testing decision type: {decision_type}")
            response = requests.get(f"{self.base_url}/scenarios/{decision_type}")
            self.assertEqual(response.status_code, 200)
            scenario = response.json()
            
            # Verify scenario structure
            self.assertIn("title", scenario)
            self.assertIn("description", scenario)
            self.assertIn("choices", scenario)
            self.assertEqual(scenario["decision_type"], decision_type)
            
        print("✅ All scenario types retrieved successfully")

    def test_07_get_educational_content(self):
        """Test getting educational content"""
        print("\n🔍 Testing educational content endpoints...")
        
        # Test historical facts
        response = requests.get(f"{self.base_url}/educational-content/facts")
        self.assertEqual(response.status_code, 200)
        facts = response.json()
        self.assertIsInstance(facts, list)
        self.assertGreater(len(facts), 0)
        print(f"✅ Retrieved {len(facts)} historical facts")
        
        # Test trivia questions
        response = requests.get(f"{self.base_url}/educational-content/trivia")
        self.assertEqual(response.status_code, 200)
        trivia = response.json()
        self.assertIsInstance(trivia, list)
        self.assertGreater(len(trivia), 0)
        print(f"✅ Retrieved {len(trivia)} trivia questions")

    def test_08_get_leaderboard(self):
        """Test getting leaderboard"""
        print("\n🔍 Testing leaderboard endpoint...")
        response = requests.get(f"{self.base_url}/leaderboard")
        self.assertEqual(response.status_code, 200)
        leaderboard = response.json()
        self.assertIsInstance(leaderboard, list)
        print(f"✅ Retrieved leaderboard with {len(leaderboard)} entries")

    def test_09_get_analytics(self):
        """Test getting player analytics"""
        if not self.player_id:
            self.test_03_create_player()
            self.test_05_make_decision()
            
        print(f"\n🔍 Testing analytics for player: {self.player_id}...")
        response = requests.get(f"{self.base_url}/analytics/{self.player_id}")
        self.assertEqual(response.status_code, 200)
        analytics = response.json()
        
        # Verify analytics structure
        self.assertIn("decision_breakdown", analytics)
        self.assertIn("total_decisions", analytics)
        self.assertIn("experience_by_category", analytics)
        
        print("✅ Player analytics retrieved successfully")

    def test_10_specific_business_scenarios(self):
        """Test specific business scenarios"""
        if not self.player_id:
            self.test_03_create_player()
        
        # Test specific business scenarios
        scenarios = [
            {"title": "Raw Materials Sourcing Strategy", "type": "manufacturing"},
            {"title": "Factory Workforce Expansion", "type": "human_resources"},
            {"title": "Shipping and Logistics Strategy", "type": "logistics"},
            {"title": "Marketing Campaign Strategy", "type": "marketing"}
        ]
        
        for scenario_info in scenarios:
            print(f"\n🔍 Testing specific scenario: {scenario_info['title']}...")
            
            # Get scenario of the specific type
            response = requests.get(f"{self.base_url}/scenarios/{scenario_info['type']}")
            self.assertEqual(response.status_code, 200)
            scenario = response.json()
            
            # Make a decision for this scenario
            response = requests.post(
                f"{self.base_url}/decision",
                json={
                    "player_id": self.player_id,
                    "scenario_id": scenario["title"],
                    "choice_index": 0
                }
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result["success"])
            
            # Verify updated indicators include the relevant metrics
            if scenario_info["type"] == "manufacturing":
                self.assertIn("manufacturing", result["updated_indicators"])
            elif scenario_info["type"] == "human_resources":
                self.assertIn("business", result["updated_indicators"])
            elif scenario_info["type"] == "logistics":
                self.assertIn("logistics", result["updated_indicators"])
            elif scenario_info["type"] == "marketing":
                self.assertIn("marketing", result["updated_indicators"])
                
            print(f"✅ {scenario_info['type']} decision made successfully")
            
            # Small delay to avoid overwhelming the API
            time.sleep(1)

def run_tests():
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add tests in order
    test_methods = [
        'test_01_root_endpoint',
        'test_02_get_countries',
        'test_03_create_player',
        'test_04_get_game_state',
        'test_05_make_decision',
        'test_06_get_scenarios_by_type',
        'test_07_get_educational_content',
        'test_08_get_leaderboard',
        'test_09_get_analytics',
        'test_10_specific_business_scenarios'
    ]
    
    for test_method in test_methods:
        suite.addTest(GlobalDynamicsAPITester(test_method))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n📊 TEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("\n✅ All backend API tests PASSED!")
    else:
        print("\n❌ Some tests FAILED!")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()