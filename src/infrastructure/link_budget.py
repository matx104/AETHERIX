"""
AETHERIX Link Budget Calculator

Provides preliminary link budget calculations for optical and RF links
in deep-space communication networks, specifically designed for
Earth-to-Mars interplanetary communication.

Reference Standards:
- CCSDS 141.0-B-1: Optical Communications Physical Layer
- CCSDS 401.0-B-30: Radio Frequency and Modulation Systems
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class OpticalLinkBudget:
    """
    Represents a complete optical link budget calculation result.
    
    All power values are in dBm or dB as specified.
    """
    # Transmitter parameters
    transmitter_power_dbm: float
    transmitter_antenna_gain_db: float
    transmitter_pointing_loss_db: float
    transmitter_optics_efficiency_db: float
    
    # Propagation parameters
    free_space_loss_db: float
    atmospheric_loss_db: float
    distance_km: float
    
    # Receiver parameters
    receiver_antenna_gain_db: float
    receiver_optics_efficiency_db: float
    receiver_pointing_loss_db: float
    
    # System parameters
    implementation_loss_db: float
    required_snr_db: float
    
    # Calculated values
    eirp_dbm: float
    received_power_dbm: float
    link_margin_db: float
    data_rate_mbps: float
    
    def __str__(self) -> str:
        """Format the link budget as a readable report."""
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    AETHERIX OPTICAL LINK BUDGET ANALYSIS                     ║
║              Mars Orbiter to Earth Ground Station Link                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ LINK PARAMETERS                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Distance: {self.distance_km:,.0f} km ({self.distance_km/1e6:.1f} million km)
║ Wavelength: 1550 nm (Near-IR Optical)
║ Data Rate: {self.data_rate_mbps:.1f} Mbps
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ TRANSMITTER (Mars Orbiter)                                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Laser Transmitter Power:           {self.transmitter_power_dbm:+8.2f} dBm    ║
║ Transmit Antenna Gain:             {self.transmitter_antenna_gain_db:+8.2f} dB     ║
║ Transmit Pointing Loss:            {self.transmitter_pointing_loss_db:+8.2f} dB     ║
║ Transmit Optics Efficiency:        {self.transmitter_optics_efficiency_db:+8.2f} dB     ║
║ ────────────────────────────────────────────────────────────────────         ║
║ EIRP:                              {self.eirp_dbm:+8.2f} dBm    ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PROPAGATION LOSSES                                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Free Space Path Loss:              {self.free_space_loss_db:+9.2f} dB    ║
║ Atmospheric Attenuation:           {self.atmospheric_loss_db:+8.2f} dB     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ RECEIVER (Earth Ground Station)                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Receive Antenna Gain:              {self.receiver_antenna_gain_db:+8.2f} dB     ║
║ Receive Optics Efficiency:         {self.receiver_optics_efficiency_db:+8.2f} dB     ║
║ Receive Pointing Loss:             {self.receiver_pointing_loss_db:+8.2f} dB     ║
║ Implementation Loss:               {self.implementation_loss_db:+8.2f} dB     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ LINK BUDGET SUMMARY                                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Received Signal Power:             {self.received_power_dbm:+8.2f} dBm    ║
║ Required SNR:                      {self.required_snr_db:+8.2f} dB     ║
║ ════════════════════════════════════════════════════════════════════         ║
║ LINK MARGIN:                       {self.link_margin_db:+8.2f} dB     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


class LinkBudgetCalculator:
    """
    AETHERIX Link Budget Calculator for deep-space optical communications.
    
    This calculator provides preliminary link budget analysis for optical
    links between spacecraft and ground stations, specifically designed
    for Earth-to-Mars interplanetary communication.
    
    Typical Use Case:
        Mars Orbiter (22 cm aperture) -> Earth Ground Station (1m aperture)
        Distance: 390 million km (maximum Earth-Mars distance)
        Wavelength: 1550 nm (Near-IR)
    
    Example:
        >>> calculator = LinkBudgetCalculator()
        >>> budget = calculator.calculate_optical_link_budget(
        ...     distance_km=390_000_000,  # 390 million km
        ...     tx_power_watts=5.0,       # 5W laser
        ...     tx_aperture_m=0.22,       # 22 cm Mars orbiter aperture
        ...     rx_aperture_m=1.0,        # 1m Earth ground station
        ...     data_rate_mbps=10.0       # Target data rate
        ... )
        >>> print(budget)
    """
    
    # Physical constants
    SPEED_OF_LIGHT_M_S = 299_792_458  # meters per second
    BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
    PLANCK_CONSTANT = 6.62607015e-34  # J*s
    
    # Default wavelength for deep-space optical communications
    DEFAULT_WAVELENGTH_M = 1550e-9  # 1550 nm (Near-IR)
    
    def __init__(self, wavelength_m: float = DEFAULT_WAVELENGTH_M):
        """
        Initialize the link budget calculator.
        
        Args:
            wavelength_m: Operating wavelength in meters (default: 1550 nm)
        """
        self.wavelength_m = wavelength_m
        self.frequency_hz = self.SPEED_OF_LIGHT_M_S / wavelength_m
    
    def calculate_free_space_loss_db(self, distance_km: float) -> float:
        """
        Calculate free space path loss for optical link.
        
        The free space path loss is calculated using:
        FSPL = -10*log10((4*π*d/λ)²) = -20*log10(4*π*d/λ)
        
        Note: Returns a negative value representing the loss in dB.
        This is equivalent to FSPL = 20*log10(4*π*d/λ) as a positive
        magnitude, but expressed as a loss (negative dB).
        
        Args:
            distance_km: Distance in kilometers
            
        Returns:
            Free space path loss in dB (negative value representing loss)
        """
        distance_m = distance_km * 1000
        fspl = (4 * math.pi * distance_m / self.wavelength_m) ** 2
        return -10 * math.log10(fspl)
    
    def calculate_antenna_gain_db(self, aperture_diameter_m: float, 
                                   efficiency: float = 0.55) -> float:
        """
        Calculate antenna/telescope gain for optical aperture.
        
        Gain = η * (π*D/λ)²
        
        Args:
            aperture_diameter_m: Aperture diameter in meters
            efficiency: Aperture efficiency (default: 0.55)
            
        Returns:
            Antenna gain in dB
        """
        gain = efficiency * (math.pi * aperture_diameter_m / self.wavelength_m) ** 2
        return 10 * math.log10(gain)
    
    def watts_to_dbm(self, power_watts: float) -> float:
        """Convert power from Watts to dBm."""
        return 10 * math.log10(power_watts * 1000)
    
    def calculate_one_way_light_time(self, distance_km: float) -> float:
        """
        Calculate one-way light time for the given distance.
        
        Args:
            distance_km: Distance in kilometers
            
        Returns:
            One-way light time in seconds
        """
        distance_m = distance_km * 1000
        return distance_m / self.SPEED_OF_LIGHT_M_S
    
    def calculate_optical_link_budget(
        self,
        distance_km: float,
        tx_power_watts: float = 5.0,
        tx_aperture_m: float = 0.22,
        rx_aperture_m: float = 1.0,
        data_rate_mbps: float = 10.0,
        tx_pointing_loss_db: float = -1.0,
        rx_pointing_loss_db: float = -0.5,
        tx_optics_efficiency_db: float = -2.0,
        rx_optics_efficiency_db: float = -2.0,
        atmospheric_loss_db: float = -3.0,
        implementation_loss_db: float = -2.0,
        required_snr_db: float = 10.0,
        tx_aperture_efficiency: float = 0.55,
        rx_aperture_efficiency: float = 0.55
    ) -> OpticalLinkBudget:
        """
        Calculate complete optical link budget for Mars-Earth link.
        
        This method calculates a preliminary link budget for an optical
        communication link between a Mars orbiter and an Earth ground
        station, following CCSDS optical communications standards.
        
        Args:
            distance_km: Link distance in kilometers (e.g., 390,000,000 for max Mars distance)
            tx_power_watts: Transmitter laser power in Watts (default: 5W)
            tx_aperture_m: Transmitter aperture diameter in meters (default: 0.22m / 22cm)
            rx_aperture_m: Receiver aperture diameter in meters (default: 1.0m)
            data_rate_mbps: Target data rate in Mbps (default: 10 Mbps)
            tx_pointing_loss_db: Transmitter pointing loss in dB (default: -1.0 dB)
            rx_pointing_loss_db: Receiver pointing loss in dB (default: -0.5 dB)
            tx_optics_efficiency_db: Transmitter optics efficiency in dB (default: -2.0 dB)
            rx_optics_efficiency_db: Receiver optics efficiency in dB (default: -2.0 dB)
            atmospheric_loss_db: Atmospheric attenuation in dB (default: -3.0 dB)
            implementation_loss_db: Implementation/system losses in dB (default: -2.0 dB)
            required_snr_db: Required SNR for target BER in dB (default: 10.0 dB)
            tx_aperture_efficiency: Transmitter aperture efficiency (default: 0.55)
            rx_aperture_efficiency: Receiver aperture efficiency (default: 0.55)
            
        Returns:
            OpticalLinkBudget object containing all calculated values
            
        Example:
            >>> calc = LinkBudgetCalculator()
            >>> budget = calc.calculate_optical_link_budget(
            ...     distance_km=390_000_000,
            ...     tx_power_watts=5.0,
            ...     tx_aperture_m=0.22,
            ...     rx_aperture_m=1.0,
            ...     data_rate_mbps=10.0
            ... )
            >>> print(f"Link Margin: {budget.link_margin_db:.2f} dB")
        """
        # Calculate transmitter parameters
        tx_power_dbm = self.watts_to_dbm(tx_power_watts)
        tx_antenna_gain_db = self.calculate_antenna_gain_db(tx_aperture_m, tx_aperture_efficiency)
        
        # Calculate EIRP (Effective Isotropic Radiated Power)
        eirp_dbm = (tx_power_dbm + 
                   tx_antenna_gain_db + 
                   tx_pointing_loss_db + 
                   tx_optics_efficiency_db)
        
        # Calculate propagation losses
        free_space_loss_db = self.calculate_free_space_loss_db(distance_km)
        
        # Calculate receiver parameters
        rx_antenna_gain_db = self.calculate_antenna_gain_db(rx_aperture_m, rx_aperture_efficiency)
        
        # Calculate received power
        received_power_dbm = (eirp_dbm +
                             free_space_loss_db +
                             atmospheric_loss_db +
                             rx_antenna_gain_db +
                             rx_optics_efficiency_db +
                             rx_pointing_loss_db +
                             implementation_loss_db)
        
        # Calculate receiver sensitivity based on data rate
        # For optical links, sensitivity depends on photon counting
        # Using simplified model: -50 dBm baseline at 1 Mbps, scales with data rate
        receiver_sensitivity_dbm = -50 + 10 * math.log10(data_rate_mbps)
        
        # Calculate link margin
        link_margin_db = received_power_dbm - receiver_sensitivity_dbm - required_snr_db
        
        return OpticalLinkBudget(
            transmitter_power_dbm=tx_power_dbm,
            transmitter_antenna_gain_db=tx_antenna_gain_db,
            transmitter_pointing_loss_db=tx_pointing_loss_db,
            transmitter_optics_efficiency_db=tx_optics_efficiency_db,
            free_space_loss_db=free_space_loss_db,
            atmospheric_loss_db=atmospheric_loss_db,
            distance_km=distance_km,
            receiver_antenna_gain_db=rx_antenna_gain_db,
            receiver_optics_efficiency_db=rx_optics_efficiency_db,
            receiver_pointing_loss_db=rx_pointing_loss_db,
            implementation_loss_db=implementation_loss_db,
            required_snr_db=required_snr_db,
            eirp_dbm=eirp_dbm,
            received_power_dbm=received_power_dbm,
            link_margin_db=link_margin_db,
            data_rate_mbps=data_rate_mbps
        )
    
    def calculate_mars_earth_link(self, 
                                   scenario: str = "maximum") -> OpticalLinkBudget:
        """
        Calculate link budget for standard Mars-Earth scenarios.
        
        This convenience method calculates link budgets for common
        Mars-Earth communication scenarios using typical parameters.
        
        Args:
            scenario: Distance scenario - "minimum" (55M km), "average" (225M km), 
                     or "maximum" (390M km)
                     
        Returns:
            OpticalLinkBudget for the specified scenario
            
        Example:
            >>> calc = LinkBudgetCalculator()
            >>> budget = calc.calculate_mars_earth_link("maximum")
            >>> print(f"Max distance margin: {budget.link_margin_db:.2f} dB")
        """
        distances = {
            "minimum": 55_000_000,    # 55 million km (closest approach)
            "average": 225_000_000,   # 225 million km (average distance)
            "maximum": 390_000_000,   # 390 million km (solar conjunction)
        }
        
        if scenario not in distances:
            raise ValueError(f"Invalid scenario: {scenario}. "
                           f"Must be one of {list(distances.keys())}")
        
        return self.calculate_optical_link_budget(
            distance_km=distances[scenario],
            tx_power_watts=5.0,        # 5W laser (typical for deep-space optical)
            tx_aperture_m=0.22,        # 22 cm aperture (DSOC-class)
            rx_aperture_m=1.0,         # 1m ground telescope
            data_rate_mbps=10.0        # 10 Mbps target rate
        )


def main():
    """
    Demonstrate the AETHERIX Link Budget Calculator.
    
    This function provides an example calculation for the first deliverable:
    Link Budget for Mars orbiter to Earth station at 390 million km.
    """
    print("=" * 80)
    print("AETHERIX Platform - Interplanetary Communication Link Budget Analysis")
    print("=" * 80)
    print()
    
    # Create calculator instance
    calculator = LinkBudgetCalculator()
    
    # Calculate link budget for maximum Mars-Earth distance
    print("Calculating optical link budget for Mars Orbiter to Earth Ground Station...")
    print(f"Distance: 390 million km (maximum Earth-Mars separation)")
    print()
    
    budget = calculator.calculate_optical_link_budget(
        distance_km=390_000_000,      # 390 million km
        tx_power_watts=5.0,           # 5W laser transmitter
        tx_aperture_m=0.22,           # 22 cm Mars orbiter telescope
        rx_aperture_m=1.0,            # 1m Earth ground station telescope
        data_rate_mbps=10.0,          # 10 Mbps target data rate
        atmospheric_loss_db=-3.0,     # Atmospheric attenuation (clear sky)
        required_snr_db=10.0          # Required SNR for 10^-6 BER
    )
    
    print(budget)
    
    # Calculate one-way light time
    one_way_time = calculator.calculate_one_way_light_time(390_000_000)
    print(f"\nOne-way light time: {one_way_time:.1f} seconds ({one_way_time/60:.1f} minutes)")
    print(f"Round-trip time: {2*one_way_time:.1f} seconds ({2*one_way_time/60:.1f} minutes)")
    
    # Compare different scenarios
    print("\n" + "=" * 80)
    print("Comparison of Link Margins at Different Mars-Earth Distances")
    print("=" * 80)
    
    for scenario in ["minimum", "average", "maximum"]:
        scenario_budget = calculator.calculate_mars_earth_link(scenario)
        owlt = calculator.calculate_one_way_light_time(scenario_budget.distance_km)
        print(f"\n{scenario.upper()} distance ({scenario_budget.distance_km/1e6:.0f}M km):")
        print(f"  Link Margin: {scenario_budget.link_margin_db:+.2f} dB")
        print(f"  Received Power: {scenario_budget.received_power_dbm:.2f} dBm")
        print(f"  One-way delay: {owlt/60:.1f} minutes")


if __name__ == "__main__":
    main()
