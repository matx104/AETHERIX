"""
Tests for AETHERIX Link Budget Calculator

These tests validate the optical link budget calculations for
Mars-Earth interplanetary communication.
"""

import math
import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.link_budget import LinkBudgetCalculator, OpticalLinkBudget


class TestLinkBudgetCalculator(unittest.TestCase):
    """Test cases for LinkBudgetCalculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = LinkBudgetCalculator()
    
    def test_free_space_loss_calculation(self):
        """Test free space path loss calculation."""
        # At 390 million km, expect very large path loss
        fspl = self.calculator.calculate_free_space_loss_db(390_000_000)
        
        # FSPL should be negative (loss)
        self.assertLess(fspl, 0)
        
        # For 390M km at 1550nm, expect approximately -365 to -375 dB
        self.assertLess(fspl, -365)
        self.assertGreater(fspl, -375)
    
    def test_antenna_gain_calculation(self):
        """Test antenna/telescope gain calculation."""
        # 22 cm aperture at 1550 nm
        gain = self.calculator.calculate_antenna_gain_db(0.22)
        
        # Should be positive (gain)
        self.assertGreater(gain, 0)
        
        # Larger aperture should have higher gain
        gain_large = self.calculator.calculate_antenna_gain_db(1.0)
        self.assertGreater(gain_large, gain)
    
    def test_watts_to_dbm_conversion(self):
        """Test power conversion from Watts to dBm."""
        # 1 Watt = 30 dBm
        self.assertAlmostEqual(self.calculator.watts_to_dbm(1.0), 30.0, places=5)
        
        # 5 Watts ≈ 36.99 dBm
        self.assertAlmostEqual(self.calculator.watts_to_dbm(5.0), 36.99, places=1)
    
    def test_one_way_light_time(self):
        """Test one-way light time calculation."""
        # Speed of light: ~300,000 km/s
        # At 390M km, expect about 1300 seconds (~22 minutes)
        owlt = self.calculator.calculate_one_way_light_time(390_000_000)
        
        self.assertGreater(owlt, 1200)
        self.assertLess(owlt, 1400)
        
        # Should be approximately 22 minutes
        self.assertAlmostEqual(owlt / 60, 22, delta=1)
    
    def test_optical_link_budget_mars_max_distance(self):
        """Test complete link budget at maximum Mars distance."""
        budget = self.calculator.calculate_optical_link_budget(
            distance_km=390_000_000,
            tx_power_watts=5.0,
            tx_aperture_m=0.22,
            rx_aperture_m=1.0,
            data_rate_mbps=10.0
        )
        
        # Validate return type
        self.assertIsInstance(budget, OpticalLinkBudget)
        
        # Validate distance is stored correctly
        self.assertEqual(budget.distance_km, 390_000_000)
        
        # Validate data rate
        self.assertEqual(budget.data_rate_mbps, 10.0)
        
        # EIRP should be positive (high power + gain)
        self.assertGreater(budget.eirp_dbm, 0)
        
        # Free space loss should be very negative (around -370 dB)
        self.assertLess(budget.free_space_loss_db, -365)
    
    def test_mars_earth_link_scenarios(self):
        """Test predefined Mars-Earth scenarios."""
        for scenario in ["minimum", "average", "maximum"]:
            budget = self.calculator.calculate_mars_earth_link(scenario)
            self.assertIsInstance(budget, OpticalLinkBudget)
        
        # Minimum distance should have best margin
        min_budget = self.calculator.calculate_mars_earth_link("minimum")
        max_budget = self.calculator.calculate_mars_earth_link("maximum")
        
        self.assertGreater(min_budget.link_margin_db, max_budget.link_margin_db)
    
    def test_invalid_scenario_raises_error(self):
        """Test that invalid scenario raises ValueError."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_mars_earth_link("invalid")
    
    def test_link_budget_string_representation(self):
        """Test that link budget can be converted to string."""
        budget = self.calculator.calculate_mars_earth_link("maximum")
        budget_str = str(budget)
        
        # Should contain key information
        self.assertIn("AETHERIX", budget_str)
        self.assertIn("LINK MARGIN", budget_str)
        self.assertIn("dB", budget_str)


class TestOpticalLinkBudget(unittest.TestCase):
    """Test cases for OpticalLinkBudget dataclass."""
    
    def test_dataclass_creation(self):
        """Test that OpticalLinkBudget can be created with all fields."""
        budget = OpticalLinkBudget(
            transmitter_power_dbm=37.0,
            transmitter_antenna_gain_db=110.0,
            transmitter_pointing_loss_db=-1.0,
            transmitter_optics_efficiency_db=-2.0,
            free_space_loss_db=-390.0,
            atmospheric_loss_db=-3.0,
            distance_km=390_000_000,
            receiver_antenna_gain_db=120.0,
            receiver_optics_efficiency_db=-2.0,
            receiver_pointing_loss_db=-0.5,
            implementation_loss_db=-2.0,
            required_snr_db=10.0,
            eirp_dbm=144.0,
            received_power_dbm=-135.0,
            link_margin_db=5.0,
            data_rate_mbps=10.0
        )
        
        self.assertEqual(budget.distance_km, 390_000_000)
        self.assertEqual(budget.link_margin_db, 5.0)


if __name__ == '__main__':
    unittest.main()
