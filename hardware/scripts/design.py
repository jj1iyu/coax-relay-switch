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

# PCB rev0.3: board 66 x 46 mm, origin (100,100). ALL connectors on the front edge (y = 146):
#   left -> right: U1 USB-C | J1 DC jack | LED1 (leads bent 90deg through the panel) | F-J (chassis, J4 behind it)
BOARD = (100.0, 100.0, 66.0, 46.0)
FRONT_Y = 146.0
FJ_X = 152.0                 # chassis F-J centre (keep-out in front of J4)
PLACE = {
    "U1": (117.0, 134.25, 180),    # USB-C flush with the front edge
    "J1": (133.0, 132.3, 90),      # plug face flush with the front edge
    "LED1": (141.0, 143.3, 0),
    "J4": (149.46, 127.9, 0),      # wire entries face the F-J
    "F1": (129.5, 126.5, 0),
    "Q2": (139.5, 126.5, 0),
    "D1": (129.0, 121.5, 0),
    "C1": (147.0, 116.5, 0),
    "C2": (155.0, 114.0, 270),
    "D2": (160.5, 112.0, 270),
    "R7": (130.0, 116.0, 0),
    "Q1": (141.0, 110.0, 0),
    "R1": (128.0, 111.0, 0),
    "R2": (128.0, 107.0, 0),
    "R5": (143.0, 130.0, 270),
    "R3": (110.0, 112.0, 0),
    "R4": (110.0, 116.0, 0),
    "C3": (122.0, 114.0, 270),
    "H1": (103.5, 103.5, 0), "H2": (162.5, 103.5, 0), "H3": (103.5, 142.5, 0), "H4": (162.5, 142.5, 0),
}
