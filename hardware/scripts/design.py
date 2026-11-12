"""Single source of truth for parts, nets and placement."""

# ref: (lib_id, value, footprint, schematic (x, y), {pin: net}, extra fields)
PARTS = {
    "J1": ("Connector:Barrel_Jack_Switch", "MJ-179PH", "CoaxRelay:MJ-179PH", (30.48, 50.8),
           {"1": "VIN_RAW", "2": "GND"}),
    "F1": ("Device:Polyfuse", "MF-R050 0.5A", "CoaxRelay:Fuse_Bourns_MF-R050_P5.10mm", (55.88, 50.8),
           {"1": "VIN_RAW", "2": "VIN_F"}),
    "D1": ("Device:D_Schottky", "1N5819", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", (76.2, 50.8),
           {"2": "VIN_F", "1": "+12V"}),
    "C1": ("Device:C_Polarized", "100uF 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", (99.06, 50.8),
           {"1": "+12V", "2": "GND"}),
    "C2": ("Device:C", "0.1uF", "Capacitor_THT:C_Disc_D3.0mm_W2.0mm_P2.50mm", (114.3, 50.8),
           {"1": "+12V", "2": "GND"}),
    "R3": ("Device:R", "47k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", (147.32, 50.8),
           {"1": "+12V", "2": "VMON"}),
    "R4": ("Device:R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", (162.56, 50.8),
           {"1": "VMON", "2": "GND"}),
    "C3": ("Device:C", "0.1uF", "Capacitor_THT:C_Disc_D3.0mm_W2.0mm_P2.50mm", (177.8, 50.8),
           {"1": "VMON", "2": "GND"}),
    "J4": ("Connector:Screw_Terminal_01x02", "OUT to F-J", "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
           (40.64, 101.6), {"1": "OUT", "2": "GND"}),
    "D2": ("Device:D_Schottky", "1N5819", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", (66.04, 101.6),
           {"1": "OUT", "2": "GND"}),
    "Q2": ("Device:Q_PMOS_GDS", "IRFU9024N", "Package_TO_SOT_THT:TO-251-3_Vertical", (91.44, 101.6),
           {"1": "GATE", "2": "OUT", "3": "+12V"}),
    "R7": ("Device:R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", (109.22, 101.6),
           {"1": "+12V", "2": "GATE"}),
    "Q1": ("Transistor_BJT:2SC1815", "2SC1815", "Package_TO_SOT_THT:TO-92_Inline_Wide", (124.46, 101.6),
           {"1": "GND", "2": "GATE", "3": "Q_BASE"}),
    "R1": ("Device:R", "1k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", (142.24, 101.6),
           {"1": "RELAY_DRV", "2": "Q_BASE"}),
    "R2": ("Device:R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", (154.94, 101.6),
           {"1": "Q_BASE", "2": "GND"}),
    "R5": ("Device:R", "4.7k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", (167.64, 101.6),
           {"1": "OUT", "2": "LED_A"}),
    "LED1": ("Device:LED", "RED 3mm", "LED_THT:LED_D3.0mm", (182.88, 101.6),
             {"2": "LED_A", "1": "GND"}),
    "U1": ("CoaxRelay:RP2040-Zero", "RP2040-Zero", "CoaxRelay:RP2040-Zero_Socket", (233.68, 101.6),
           {"2": "GND", "7": "VMON", "12": "RELAY_DRV"}),
    "H1": ("Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", (30.48, 152.4), {}),
    "H2": ("Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", (40.64, 152.4), {}),
    "H3": ("Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", (50.8, 152.4), {}),
    "H4": ("Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", (60.96, 152.4), {}),
}

POWER_NETS = {"+12V": "power:+12V", "GND": "power:GND"}
FLAG_AT = [("D1", "1"), ("J1", "2")]   # PWR_FLAG on +12V and GND

# PCB: board 60 x 46 mm, origin (100,100). (x, y, rotation_deg)
BOARD = (100.0, 100.0, 60.0, 46.0)
PLACE = {
    "J1": (113.7, 120.0, 0),       # plug face flush with the left board edge
    "D1": (108.5, 104.0, 0),
    "F1": (110.0, 110.0, 0),
    "C1": (123.0, 104.5, 0),
    "C2": (130.0, 105.0, 270),
    "R3": (119.0, 113.0, 0),
    "R4": (119.0, 116.5, 0),
    "C3": (129.5, 113.5, 270),
    "U1": (143.0, 114.5, 0),       # USB-C toward the top edge
    "Q2": (119.5, 125.0, 0),
    "R7": (119.0, 129.0, 0),
    "LED1": (115.0, 136.5, 0),
    "R5": (121.0, 132.5, 270),
    "R2": (124.0, 132.5, 270),
    "Q1": (126.8, 135.5, 0),
    "R1": (134.8, 132.5, 270),
    "D2": (138.1, 132.5, 270),
    "J4": (143.8, 140.0, 0),       # wires to the chassis F-J leave through the bottom edge
    "H1": (103.5, 103.5, 0), "H2": (156.5, 103.5, 0), "H3": (103.5, 142.5, 0), "H4": (156.5, 142.5, 0),
}
