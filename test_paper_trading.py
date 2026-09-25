
import unittest
from unittest.mock import patch

from paper_trading import execute_buy, execute_sell

class TestPaperTradingTerminal(unittest.TestCase):

    def setUp(self):
        """
        Runs before each test. We define a default clean account state.
        """
        self.state = {
            "cash": 10000.0,
            "portfolio": {},
            "history": []
        }

    @patch("paper_trading.fetch_price")
    @patch("paper_trading.save_state")
    def test_execute_buy_successful(self, mock_save, mock_fetch):
        """
        Verify buying shares updates cash and portfolio holdings.
        """
        mock_fetch.return_value = 150.0  # Set price of AAPL to $150
        
        # Buy 10 shares of AAPL (costing $1,500)
        updated_state = execute_buy(self.state, "AAPL", 10.0)
        
        # Cash should drop to 10000.0 - 1500.0 = 8500.0
        self.assertEqual(updated_state["cash"], 8500.0)
        
        # Portfolio should contain AAPL position
        self.assertIn("AAPL", updated_state["portfolio"])
        self.assertEqual(updated_state["portfolio"]["AAPL"]["shares"], 10.0)
        self.assertEqual(updated_state["portfolio"]["AAPL"]["avg_cost"], 150.0)
        
        # History log should have 1 item
        self.assertEqual(len(updated_state["history"]), 1)
        self.assertEqual(updated_state["history"][0]["type"], "BUY")

    @patch("paper_trading.fetch_price")
    def test_execute_buy_insufficient_funds(self, mock_fetch):
        """
        Verify buying shares fails if cost exceeds cash balance.
        """
        mock_fetch.return_value = 200.0
        
        # Try to buy 60 shares of AAPL (cost $12,000, but cash is only $10,000)
        updated_state = execute_buy(self.state, "AAPL", 60.0)
        
        # Cash should remain unchanged
        self.assertEqual(updated_state["cash"], 10000.0)
        self.assertNotIn("AAPL", updated_state["portfolio"])
        self.assertEqual(len(updated_state["history"]), 0)

    @patch("paper_trading.fetch_price")
    @patch("paper_trading.save_state")
    def test_execute_sell_successful(self, mock_save, mock_fetch):
        """
        Verify selling shares updates cash and deletes holding once balance reaches 0.
        """
        mock_fetch.return_value = 180.0  # Price goes up to $180
        
        # Setup pre-owned portfolio state (holding 10 shares of AAPL)
        self.state["portfolio"] = {"AAPL": {"shares": 10.0, "avg_cost": 150.0}}
        self.state["cash"] = 8500.0
        
        # Sell 10 shares (revenue: $1,800)
        updated_state = execute_sell(self.state, "AAPL", 10.0)
        
        # Cash: 8500 + 1800 = 10300.0
        self.assertEqual(updated_state["cash"], 10300.0)
        
        # AAPL position should be deleted completely
        self.assertNotIn("AAPL", updated_state["portfolio"])

    def test_execute_sell_insufficient_shares(self):
        """
        Verify selling shares fails if the user tries to sell more than they hold.
        """
        # User only holds 5 shares of AAPL
        self.state["portfolio"] = {"AAPL": {"shares": 5.0, "avg_cost": 150.0}}
        
        updated_state = execute_sell(self.state, "AAPL", 10.0)
        
        # Transaction should fail; portfolio holdings remain unchanged
        self.assertEqual(updated_state["portfolio"]["AAPL"]["shares"], 5.0)
        self.assertEqual(updated_state["cash"], 10000.0)

if __name__ == "__main__":
    unittest.main()
