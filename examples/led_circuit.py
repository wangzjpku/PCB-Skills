"""
Simple LED Circuit Example

Demonstrates basic KiCad automation capabilities.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import core module
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.core import KiCadAssistant, PCBDesignSpec, ComponentSpec, TrackSpec
except ImportError:
    print("Error: Cannot import core module")
    print("Make sure you're running from the PCB-Skills directory")
    sys.exit(1)


def create_led_circuit():
    """Create a simple LED circuit with current-limiting resistor"""

    print("=" * 60)
    print("Creating LED Circuit Example")
    print("=" * 60 + "\n")

    # Create assistant
    assistant = KiCadAssistant()

    # Step 1: Create PCB
    print("\n[Step 1] Creating PCB...")
    board_spec = PCBDesignSpec(
        width="50mm", height="30mm", layers=2, thickness="1.6mm", name="LED_Circuit"
    )
    if not assistant.create_pcb(board_spec):
        print("Failed to create PCB")
        return

    # Step 2: Add LED
    print("\n[Step 2] Adding LED...")
    led_spec = ComponentSpec(
        ref="LED1",
        footprint="LED_0805",
        value="Red LED",
        position=(15, 15),
        orientation=0.0,
    )
    assistant.add_component(led_spec)

    # Step 3: Add Resistor
    print("\n[Step 3] Adding Resistor...")
    resistor_spec = ComponentSpec(
        ref="R1",
        footprint="Resistor_SMD:R_0805_2012",
        value="330Ω",
        position=(25, 15),
        orientation=90.0,
    )
    assistant.add_component(resistor_spec)

    # Step 4: Add Connector
    print("\n[Step 4] Adding Connector...")
    conn_spec = ComponentSpec(
        ref="J1",
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        value="2-pin",
        position=(35, 15),
        orientation=0.0,
    )
    assistant.add_component(conn_spec)

    # Step 5: Route connections
    print("\n[Step 5] Routing connections...")

    # Route LED cathode to resistor
    track1 = TrackSpec(
        start=(17, 15), end=(23, 15), width="0.5mm", layer="F.Cu", net="LED_net"
    )
    assistant.route_track(track1)

    # Route resistor to connector pin 1
    track2 = TrackSpec(
        start=(27, 15), end=(35, 15), width="0.5mm", layer="F.Cu", net="LED_net"
    )
    assistant.route_track(track2)

    # Route connector pin 2 to LED anode
    track3 = TrackSpec(
        start=(35, 15), end=(13, 15), width="0.5mm", layer="F.Cu", net="VCC"
    )
    assistant.route_track(track3)

    # Step 6: Save design
    print("\n[Step 6] Saving design...")
    output_file = Path("./led_circuit.kicad_pcb")
    assistant.save_board(str(output_file))

    print("\n" + "=" * 60)
    print("✓ LED circuit created successfully!")
    print(f"✓ File saved: {output_file.absolute()}")
    print("=" * 60)

    # Note: Since we're not running within KiCad, the actual file
    # won't be created. This example demonstrates the API usage.


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a simple LED circuit using KiCad Automation"
    )
    parser.add_argument(
        "--output", "-o", default="led_circuit.kicad_pcb", help="Output filename"
    )
    parser.add_argument(
        "--openai-key", help="OpenAI API key for enhanced NLP (optional)"
    )

    args = parser.parse_args()

    print("\nKiCad Automation - LED Circuit Example\n")
    print("Note: This example demonstrates the API structure.")
    print("For actual PCB creation, run within KiCad or use KiCad's Python.\n")

    create_led_circuit()


if __name__ == "__main__":
    main()
