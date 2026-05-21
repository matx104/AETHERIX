"""
AETHERIX RF Link Budget Calculator

Provides comprehensive RF link budget calculations for Ka-band, X-band,
S-band, and UHF links in deep-space and planetary-surface communication
networks, specifically designed for Earth-to-Mars DTN operations.

Reference Standards:
- CCSDS 401.0-B-30: Radio Frequency and Modulation Systems
- CCSDS 131.0-B-4: Flexible Advanced Coding and Modulation
- ITU-R P.676: Attenuation by Atmospheric Gases
- ITU-R P.618: Propagation Data for Rain Attenuation
"""

import math
from dataclasses import dataclass

SPEED_OF_LIGHT_M_S = 299_792_458
BOLTZMANN_CONSTANT_W_HZ_K = 1.380649e-23
REFERENCE_TEMPERATURE_K = 290.0

KA_BAND_FREQ_HZ = 26.5e9
X_BAND_FREQ_HZ = 8.4e9
S_BAND_FREQ_HZ = 2.3e9
UHF_FREQ_HZ = 401e6

MARS_EARTH_DISTANCES_KM = {
    "minimum": 55_000_000,
    "average": 225_000_000,
    "maximum": 401_000_000,
}


@dataclass
class RFLinkBudget:
    """
    Complete RF link budget calculation result.

    All dB values representing losses are negative. All gains are positive.
    Power values in dBm unless otherwise noted.
    """

    transmitter_power_dbm: float
    transmitter_gain_dbi: float
    transmitter_line_loss_db: float
    free_space_loss_db: float
    atmospheric_loss_db: float
    rain_attenuation_db: float
    polarization_mismatch_db: float
    receiver_gain_dbi: float
    receiver_line_loss_db: float
    receiver_noise_figure_db: float
    system_temperature_k: float
    bandwidth_hz: float
    required_ebn0_db: float
    implementation_loss_db: float
    distance_km: float
    frequency_hz: float

    eirp_dbm: float
    received_power_dbm: float
    noise_power_dbm: float
    cnr_db: float
    eb_n0_db: float
    link_margin_db: float
    data_rate_bps: float

    def __str__(self) -> str:
        wavelength_mm = (SPEED_OF_LIGHT_M_S / self.frequency_hz) * 1000
        if self.frequency_hz >= 1e9:
            freq_label = f"{self.frequency_hz / 1e9:.1f} GHz"
        else:
            freq_label = f"{self.frequency_hz / 1e6:.1f} MHz"

        margin_status = "CLOSED" if self.link_margin_db >= 0 else "OPEN"

        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      AETHERIX RF LINK BUDGET ANALYSIS                       ║
║              Mars-Earth Deep-Space Communication Link                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ LINK PARAMETERS                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Distance: {self.distance_km:,.0f} km ({self.distance_km / 1e6:.1f} million km)
║ Frequency: {freq_label}  (wavelength: {wavelength_mm:.1f} mm)
║ Data Rate: {self.data_rate_bps / 1e6:.2f} Mbps
║ Bandwidth: {self.bandwidth_hz / 1e6:.2f} MHz
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ TRANSMITTER                                                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Transmitter Power:                 {self.transmitter_power_dbm:+8.2f} dBm    ║
║ Transmit Antenna Gain:             {self.transmitter_gain_dbi:+8.2f} dBi    ║
║ Transmit Line Loss:                {self.transmitter_line_loss_db:+8.2f} dB     ║
║ ────────────────────────────────────────────────────────────────────         ║
║ EIRP:                              {self.eirp_dbm:+8.2f} dBm    ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PROPAGATION LOSSES                                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Free Space Path Loss:              {self.free_space_loss_db:+9.2f} dB    ║
║ Atmospheric Attenuation:           {self.atmospheric_loss_db:+8.2f} dB     ║
║ Rain Attenuation:                  {self.rain_attenuation_db:+8.2f} dB     ║
║ Polarization Mismatch:             {self.polarization_mismatch_db:+8.2f} dB     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ RECEIVER                                                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Receive Antenna Gain:              {self.receiver_gain_dbi:+8.2f} dBi    ║
║ Receive Line Loss:                 {self.receiver_line_loss_db:+8.2f} dB     ║
║ Receiver Noise Figure:             {self.receiver_noise_figure_db:+8.2f} dB     ║
║ System Temperature:                {self.system_temperature_k:8.1f} K      ║
║ Implementation Loss:               {self.implementation_loss_db:+8.2f} dB     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ LINK BUDGET SUMMARY                                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Received Signal Power:             {self.received_power_dbm:+8.2f} dBm    ║
║ Noise Power:                       {self.noise_power_dbm:+8.2f} dBm    ║
║ Carrier-to-Noise Ratio (C/N):      {self.cnr_db:+8.2f} dB     ║
║ Eb/N0 (achieved):                  {self.eb_n0_db:+8.2f} dB     ║
║ Eb/N0 (required):                  {self.required_ebn0_db:+8.2f} dB     ║
║ ════════════════════════════════════════════════════════════════════         ║
║ LINK MARGIN:                       {self.link_margin_db:+8.2f} dB     ║
║ LINK STATUS:                       {margin_status:>8s}         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


class RFLinkBudgetCalculator:
    """
    RF link budget calculator for deep-space and planetary communications.

    Supports Ka-band, X-band, S-band, and UHF frequency planning for
    the AETHERIX Earth-Mars DTN architecture. Calculates complete link
    budgets including free-space loss, antenna gains, noise analysis,
    and Eb/N0-based margin analysis.

    Example:
        >>> calc = RFLinkBudgetCalculator(KA_BAND_FREQ_HZ)
        >>> budget = calc.calculate_rf_link_budget(
        ...     distance_km=225_000_000,
        ...     tx_power_watts=20.0,
        ...     tx_antenna_diameter_m=3.0,
        ...     rx_antenna_diameter_m=34.0,
        ...     data_rate_bps=10e6,
        ... )
        >>> print(budget)
    """

    def __init__(self, frequency_hz: float):
        """
        Initialize the RF link budget calculator.

        Args:
            frequency_hz: Operating frequency in Hz (e.g., 26.5e9 for Ka-band)
        """
        self.frequency_hz = frequency_hz
        self.wavelength_m = SPEED_OF_LIGHT_M_S / frequency_hz

    def calculate_free_space_loss_db(self, distance_km: float) -> float:
        """
        Calculate free space path loss.

        FSPL = 20 * log10(4 * pi * d * f / c)

        Args:
            distance_km: Propagation distance in kilometers

        Returns:
            Free space path loss in dB (negative value representing loss)
        """
        distance_m = distance_km * 1000
        fspl_ratio = 4 * math.pi * distance_m * self.frequency_hz / SPEED_OF_LIGHT_M_S
        return -20 * math.log10(fspl_ratio)

    def calculate_antenna_gain_dbi(self, diameter_m: float, efficiency: float = 0.55) -> float:
        """
        Calculate parabolic dish antenna gain.

        G = eta * (pi * D * f / c)^2

        Args:
            diameter_m: Antenna dish diameter in meters
            efficiency: Antenna efficiency factor (0.0 to 1.0, default 0.55)

        Returns:
            Antenna gain in dBi
        """
        gain_linear = efficiency * (math.pi * diameter_m * self.frequency_hz / SPEED_OF_LIGHT_M_S) ** 2
        return 10 * math.log10(gain_linear)

    def watts_to_dbm(self, power_watts: float) -> float:
        """
        Convert power from Watts to dBm.

        Args:
            power_watts: Power in Watts

        Returns:
            Power in dBm
        """
        return 10 * math.log10(power_watts * 1000)

    def dbm_to_watts(self, power_dbm: float) -> float:
        """
        Convert power from dBm to Watts.

        Args:
            power_dbm: Power in dBm

        Returns:
            Power in Watts
        """
        return 10 ** ((power_dbm - 30) / 10)

    def calculate_system_temperature(
        self,
        antenna_temp_k: float = 50.0,
        receiver_noise_figure_db: float = 2.0,
    ) -> float:
        """
        Calculate receiver system noise temperature.

        Tsys = Tant + T0 * (10^(NF/10) - 1)

        Args:
            antenna_temp_k: Antenna noise temperature in Kelvin (default 50 K for
                            deep-space sky)
            receiver_noise_figure_db: Receiver noise figure in dB (default 2.0 dB)

        Returns:
            System noise temperature in Kelvin
        """
        nf_linear = 10 ** (receiver_noise_figure_db / 10)
        return antenna_temp_k + REFERENCE_TEMPERATURE_K * (nf_linear - 1)

    def calculate_noise_power_dbm(self, system_temp_k: float, bandwidth_hz: float) -> float:
        """
        Calculate thermal noise power.

        N = k * T * B

        Args:
            system_temp_k: System noise temperature in Kelvin
            bandwidth_hz: Receiver bandwidth in Hz

        Returns:
            Noise power in dBm
        """
        noise_watts = BOLTZMANN_CONSTANT_W_HZ_K * system_temp_k * bandwidth_hz
        return self.watts_to_dbm(noise_watts)

    def calculate_rf_link_budget(
        self,
        distance_km: float,
        tx_power_watts: float,
        tx_antenna_diameter_m: float,
        rx_antenna_diameter_m: float,
        data_rate_bps: float,
        tx_line_loss_db: float = -1.0,
        rx_line_loss_db: float = -0.5,
        atmospheric_loss_db: float = -1.0,
        rain_attenuation_db: float = 0.0,
        polarization_mismatch_db: float = -0.5,
        implementation_loss_db: float = -2.0,
        required_ebn0_db: float = 10.0,
        tx_efficiency: float = 0.55,
        rx_efficiency: float = 0.55,
    ) -> RFLinkBudget:
        """
        Calculate a complete RF link budget.

        Computes the full signal chain from transmitter EIRP through
        propagation losses to receiver Eb/N0 and link margin.

        Args:
            distance_km: Link distance in kilometers
            tx_power_watts: Transmitter RF output power in Watts
            tx_antenna_diameter_m: Transmit dish diameter in meters
            rx_antenna_diameter_m: Receive dish diameter in meters
            data_rate_bps: Symbol/data rate in bits per second
            tx_line_loss_db: Transmit feed/line losses in dB (negative)
            rx_line_loss_db: Receive feed/line losses in dB (negative)
            atmospheric_loss_db: Atmospheric gaseous attenuation in dB (negative)
            rain_attenuation_db: Rain fade margin in dB (negative or 0)
            polarization_mismatch_db: Polarization loss in dB (negative)
            implementation_loss_db: Modem/coding implementation loss in dB (negative)
            required_ebn0_db: Required Eb/N0 for target BER in dB (positive)
            tx_efficiency: Transmit antenna aperture efficiency (0 to 1)
            rx_efficiency: Receive antenna aperture efficiency (0 to 1)

        Returns:
            RFLinkBudget dataclass with all calculated link parameters
        """
        tx_power_dbm = self.watts_to_dbm(tx_power_watts)
        tx_gain_dbi = self.calculate_antenna_gain_dbi(tx_antenna_diameter_m, tx_efficiency)
        rx_gain_dbi = self.calculate_antenna_gain_dbi(rx_antenna_diameter_m, rx_efficiency)

        eirp_dbm = tx_power_dbm + tx_gain_dbi + tx_line_loss_db

        fspl_db = self.calculate_free_space_loss_db(distance_km)

        received_power_dbm = (
            eirp_dbm
            + fspl_db
            + atmospheric_loss_db
            + rain_attenuation_db
            + polarization_mismatch_db
            + rx_gain_dbi
            + rx_line_loss_db
            + implementation_loss_db
        )

        receiver_noise_figure_db = 2.0
        system_temp_k = self.calculate_system_temperature(
            antenna_temp_k=50.0,
            receiver_noise_figure_db=receiver_noise_figure_db,
        )

        bandwidth_hz = data_rate_bps * 1.2
        noise_power_dbm = self.calculate_noise_power_dbm(system_temp_k, bandwidth_hz)

        cnr_db = received_power_dbm - noise_power_dbm
        eb_n0_db = cnr_db - 10 * math.log10(bandwidth_hz / data_rate_bps)
        link_margin_db = eb_n0_db - required_ebn0_db

        return RFLinkBudget(
            transmitter_power_dbm=tx_power_dbm,
            transmitter_gain_dbi=tx_gain_dbi,
            transmitter_line_loss_db=tx_line_loss_db,
            free_space_loss_db=fspl_db,
            atmospheric_loss_db=atmospheric_loss_db,
            rain_attenuation_db=rain_attenuation_db,
            polarization_mismatch_db=polarization_mismatch_db,
            receiver_gain_dbi=rx_gain_dbi,
            receiver_line_loss_db=rx_line_loss_db,
            receiver_noise_figure_db=receiver_noise_figure_db,
            system_temperature_k=system_temp_k,
            bandwidth_hz=bandwidth_hz,
            required_ebn0_db=required_ebn0_db,
            implementation_loss_db=implementation_loss_db,
            distance_km=distance_km,
            frequency_hz=self.frequency_hz,
            eirp_dbm=eirp_dbm,
            received_power_dbm=received_power_dbm,
            noise_power_dbm=noise_power_dbm,
            cnr_db=cnr_db,
            eb_n0_db=eb_n0_db,
            link_margin_db=link_margin_db,
            data_rate_bps=data_rate_bps,
        )

    def calculate_mars_earth_link(self, scenario: str = "maximum") -> RFLinkBudget:
        """
        Calculate RF link budget for standard Mars-Earth distance scenarios.

        Uses representative deep-space network parameters: a spacecraft
        with a modest dish transmitting to a 34-meter DSN ground station.

        Args:
            scenario: Distance scenario -- "minimum" (55M km),
                     "average" (225M km), or "maximum" (401M km)

        Returns:
            RFLinkBudget for the specified scenario

        Raises:
            ValueError: If scenario is not recognized
        """
        if scenario not in MARS_EARTH_DISTANCES_KM:
            raise ValueError(
                f"Invalid scenario: {scenario}. "
                f"Must be one of {list(MARS_EARTH_DISTANCES_KM.keys())}"
            )

        distance_km = MARS_EARTH_DISTANCES_KM[scenario]

        is_uhf = self.frequency_hz < 1e9

        if is_uhf:
            return self.calculate_rf_link_budget(
                distance_km=distance_km,
                tx_power_watts=10.0,
                tx_antenna_diameter_m=0.3,
                rx_antenna_diameter_m=5.0,
                data_rate_bps=256e3,
                tx_line_loss_db=-0.5,
                rx_line_loss_db=-0.5,
                atmospheric_loss_db=-0.3,
                rain_attenuation_db=0.0,
                polarization_mismatch_db=-0.3,
                implementation_loss_db=-1.5,
                required_ebn0_db=9.0,
                tx_efficiency=0.50,
                rx_efficiency=0.50,
            )

        return self.calculate_rf_link_budget(
            distance_km=distance_km,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
            tx_line_loss_db=-1.0,
            rx_line_loss_db=-0.5,
            atmospheric_loss_db=-1.0,
            rain_attenuation_db=-3.0,
            polarization_mismatch_db=-0.5,
            implementation_loss_db=-2.0,
            required_ebn0_db=10.0,
            tx_efficiency=0.55,
            rx_efficiency=0.55,
        )


def create_ka_band_calculator() -> RFLinkBudgetCalculator:
    """
    Create a Ka-band (26.5 GHz) RF link budget calculator.

    Ka-band is the primary high-data-rate downlink band for Mars missions,
    offering wide bandwidth but higher atmospheric sensitivity.

    Returns:
        Configured RFLinkBudgetCalculator for Ka-band
    """
    return RFLinkBudgetCalculator(KA_BAND_FREQ_HZ)


def create_uhf_calculator() -> RFLinkBudgetCalculator:
    """
    Create a UHF (401 MHz) RF link budget calculator.

    UHF is used for Mars surface-to-orbiter relay links, providing
    reliable communication with modest antenna gain requirements.

    Returns:
        Configured RFLinkBudgetCalculator for UHF
    """
    return RFLinkBudgetCalculator(UHF_FREQ_HZ)


def main():
    """
    Demonstrate AETHERIX RF link budget calculations.

    Computes Ka-band and UHF budgets across all three canonical
    Mars-Earth distances (minimum, average, maximum).
    """
    print("=" * 80)
    print("AETHERIX Platform - RF Link Budget Analysis for Earth-Mars DTN")
    print("=" * 80)

    ka_calc = create_ka_band_calculator()
    uhf_calc = create_uhf_calculator()

    print("\n" + "-" * 80)
    print("Ka-Band (26.5 GHz) -- Mars Orbiter to Earth DSN 34-m Station")
    print("-" * 80)

    for scenario in ("minimum", "average", "maximum"):
        budget = ka_calc.calculate_mars_earth_link(scenario)
        print(budget)
        distance_km = budget.distance_km
        owlt_s = (distance_km * 1000) / SPEED_OF_LIGHT_M_S
        print(f"  One-way light time: {owlt_s:.1f} s ({owlt_s / 60:.1f} min)")

    print("\n" + "-" * 80)
    print("UHF (401 MHz) -- Mars Surface to Orbiter Relay")
    print("-" * 80)

    for scenario in ("minimum", "average", "maximum"):
        budget = uhf_calc.calculate_mars_earth_link(scenario)
        print(budget)

    print("\n" + "=" * 80)
    print("Summary Comparison")
    print("=" * 80)
    header = f"{'Scenario':<12} {'Band':<8} {'Margin (dB)':>12} {'Rx Pwr (dBm)':>14} {'Eb/N0 (dB)':>12}"
    print(header)
    print("-" * len(header))

    for scenario in ("minimum", "average", "maximum"):
        ka = ka_calc.calculate_mars_earth_link(scenario)
        uhf = uhf_calc.calculate_mars_earth_link(scenario)
        print(
            f"{scenario:<12} {'Ka':<8} {ka.link_margin_db:>+12.2f} {ka.received_power_dbm:>+14.2f} {ka.eb_n0_db:>+12.2f}"
        )
        print(
            f"{scenario:<12} {'UHF':<8} {uhf.link_margin_db:>+12.2f} {uhf.received_power_dbm:>+14.2f} {uhf.eb_n0_db:>+12.2f}"
        )


if __name__ == "__main__":
    main()
