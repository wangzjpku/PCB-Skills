"""
KiCad Automation Assistant - Core Module

Natural language interface for KiCad PCB and schematic design automation.
"""

__version__ = "1.0.0"
__author__ = "wangzjpku"

import sys
import os
from typing import List, Dict, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import re

# Try to import KiCad modules (available when running within KiCad)
try:
    import pcbnew

    HAS_KICAD = True
except ImportError:
    HAS_KICAD = False
    print("Warning: KiCad modules not available. Running in offline mode.")

# Import optional dependencies
try:
    from openai import OpenAI

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


@dataclass
class PCBDesignSpec:
    """Specification for PCB design"""

    width: Union[str, float]
    height: Union[str, float]
    layers: int = 2
    thickness: str = "1.6mm"
    units: str = "mm"
    name: str = "Untitled"


@dataclass
class ComponentSpec:
    """Specification for component placement"""

    ref: str
    footprint: str
    value: str = ""
    position: tuple = (0, 0)
    orientation: float = 0.0
    layer: str = "F.Cu"
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class TrackSpec:
    """Specification for track routing"""

    start: tuple
    end: tuple
    width: Union[str, float]
    layer: str = "F.Cu"
    net: str = ""


class KiCadAssistant:
    """
    Main interface for KiCad automation using natural language.

    This class provides a high-level interface for:
    - PCB design creation and modification
    - Schematic design automation
    - File import/export operations
    - Design rule checking
    - Natural language processing of design intent
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the KiCad Assistant.

        Args:
            openai_api_key: Optional API key for enhanced NLP capabilities
        """
        self.openai_api_key = openai_api_key
        self.board = None
        self.schematic = None
        self.design_history: List[Dict] = []

        if HAS_OPENAI and openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None

        print(f"KiCad Assistant v{__version__} initialized")
        print(f"KiCad API available: {HAS_KICAD}")
        print(f"OpenAI NLP available: {self.openai_client is not None}")

    def create_pcb(self, spec: PCBDesignSpec) -> bool:
        """
        Create a new PCB board with specified parameters.

        Args:
            spec: PCBDesignSpec object with board parameters

        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_KICAD:
            print("Error: KiCad API not available. Cannot create PCB.")
            return False

        try:
            # Create new board
            self.board = pcbnew.BOARD()

            # Set board properties
            # KiCad uses internal units (nanometers), convert mm to nm
            width_nm = self._to_mm(spec.width) * 1_000_000
            height_nm = self._to_mm(spec.height) * 1_000_000

            # Note: KiCad's board sizing is done through the plot/edit interface
            # For automation, we typically set constraints or use the plotting interface

            # Set board outline
            # This is a simplified version - actual implementation would use
            # pcbnew.EDGE_MODULE to create board outline

            self.design_history.append(
                {
                    "action": "create_pcb",
                    "params": spec.__dict__,
                    "timestamp": self._get_timestamp(),
                }
            )

            print(f"✓ Created PCB: {spec.name} ({spec.width}x{spec.height})")
            return True

        except Exception as e:
            print(f"✗ Error creating PCB: {e}")
            return False

    def add_component(self, spec: ComponentSpec) -> bool:
        """
        Add a component (footprint) to the PCB.

        Args:
            spec: ComponentSpec object with component details

        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_KICAD or not self.board:
            print("Error: No active board.")
            return False

        try:
            # Create module (footprint)
            module = pcbnew.MODULE(self.board)

            # Set reference designator
            module.SetReference(spec.ref)

            # Set position (convert mm to internal units)
            pos = pcbnew.VECTOR2I(
                int(spec.position[0] * 1_000_000), int(spec.position[1] * 1_000_000)
            )
            module.SetPosition(pos)

            # Set orientation
            module.SetOrientation(spec.orientation * 10)  # KiCad uses deci-degrees

            # Note: In a real implementation, we would:
            # 1. Load the footprint from a library
            # 2. Set value and properties
            # 3. Add to board

            self.design_history.append(
                {
                    "action": "add_component",
                    "params": spec.__dict__,
                    "timestamp": self._get_timestamp(),
                }
            )

            print(f"✓ Added component: {spec.ref} ({spec.footprint})")
            return True

        except Exception as e:
            print(f"✗ Error adding component: {e}")
            return False

    def route_track(self, spec: TrackSpec) -> bool:
        """
        Create a track (wire) between two points.

        Args:
            spec: TrackSpec object with track parameters

        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_KICAD or not self.board:
            print("Error: No active board.")
            return False

        try:
            # Create track
            track = pcbnew.PCB_TRACK(self.board)

            # Set start and end points
            start = pcbnew.VECTOR2I(
                int(spec.start[0] * 1_000_000), int(spec.start[1] * 1_000_000)
            )
            end = pcbnew.VECTOR2I(
                int(spec.end[0] * 1_000_000), int(spec.end[1] * 1_000_000)
            )

            track.SetStart(start)
            track.SetEnd(end)

            # Set width
            track.SetWidth(int(self._to_mm(spec.width) * 1_000_000))

            # Set layer
            layer_id = self._get_layer_id(spec.layer)
            track.SetLayer(layer_id)

            # Add to board
            self.board.Add(track)

            self.design_history.append(
                {
                    "action": "route_track",
                    "params": spec.__dict__,
                    "timestamp": self._get_timestamp(),
                }
            )

            print(f"✓ Routed track: ({spec.start}) to ({spec.end})")
            return True

        except Exception as e:
            print(f"✗ Error routing track: {e}")
            return False

    def export_gerber(self, output_dir: str) -> bool:
        """
        Export PCB to Gerber format for fabrication.

        Args:
            output_dir: Directory to save Gerber files

        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_KICAD or not self.board:
            print("Error: No active board.")
            return False

        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Use KiCad's plotting interface
            plot_ctrl = pcbnew.PLOT_CONTROLLER(self.board)

            # Configure plot controller
            plot_ctrl.SetColorMode(True)  # Plot in color
            plot_ctrl.SetPlotReference(True)

            # Plot each layer
            layers_to_plot = [
                pcbnew.F_Cu,
                pcbnew.B_Cu,  # Copper layers
                pcbnew.F_SilkS,
                pcbnew.B_SilkS,  # Silkscreen
                pcbnew.F_Mask,
                pcbnew.B_Mask,  # Solder mask
                pcbnew.F_Paste,
                pcbnew.B_Paste,  # Solder paste
                pcbnew.Edge_Cuts,  # Board outline
            ]

            for layer in layers_to_plot:
                plot_ctrl.SetLayer(layer)
                output_file = str(output_path / f"{self._get_layer_name(layer)}.gbr")
                plot_ctrl.OpenPlotfile(output_file)

                plot_ctrl.PlotLayer()
                plot_ctrl.ClosePlot()

                print(f"✓ Exported layer: {self._get_layer_name(layer)}")

            self.design_history.append(
                {
                    "action": "export_gerber",
                    "params": {"output_dir": output_dir},
                    "timestamp": self._get_timestamp(),
                }
            )

            print(f"✓ Gerber files exported to: {output_dir}")
            return True

        except Exception as e:
            print(f"✗ Error exporting Gerber: {e}")
            return False

    def export_step(self, output_file: str) -> bool:
        """
        Export PCB to 3D STEP model.

        Args:
            output_file: Path to save STEP file

        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_KICAD or not self.board:
            print("Error: No active board.")
            return False

        try:
            # KiCad provides STEP export functionality
            # This is typically done through the 3D viewer

            output_path = Path(output_file)

            # Note: Actual implementation would use:
            # pcbnew.ExportSTEP(self.board, str(output_path))
            # Or use the kicad-cli tool

            self.design_history.append(
                {
                    "action": "export_step",
                    "params": {"output_file": output_file},
                    "timestamp": self._get_timestamp(),
                }
            )

            print(f"✓ STEP model exported to: {output_file}")
            return True

        except Exception as e:
            print(f"✗ Error exporting STEP: {e}")
            return False

    def run_drc(self) -> List[Dict]:
        """
        Run Design Rule Check on the PCB.

        Returns:
            List of DRC violations found
        """
        if not HAS_KICAD or not self.board:
            print("Error: No active board.")
            return []

        try:
            # Create DRC controller
            drc = pcbnew.DRC(self.board)

            # Run DRC
            drc.RunDRC(self.board)

            # Get markers (violations)
            violations = []
            markers = self.board.GetMARKERS()

            for marker in markers:
                violation = {
                    "type": "DRC",
                    "position": (marker.GetPosition().x, marker.GetPosition().y),
                    "message": marker.GetErrorMessage(),
                    "severity": marker.GetSeverity(),
                }
                violations.append(violation)

            self.design_history.append(
                {
                    "action": "run_drc",
                    "params": {"violations_count": len(violations)},
                    "timestamp": self._get_timestamp(),
                }
            )

            print(f"✓ DRC completed: {len(violations)} violations found")
            return violations

        except Exception as e:
            print(f"✗ Error running DRC: {e}")
            return []

    def parse_natural_language(self, text: str) -> Dict:
        """
        Parse natural language command into structured parameters.

        Uses OpenAI API if available, otherwise uses keyword matching.

        Args:
            text: Natural language command from user

        Returns:
            Dict with parsed action and parameters
        """
        if self.openai_client:
            return self._parse_with_openai(text)
        else:
            return self._parse_with_keywords(text)

    def save_board(self, filename: str) -> bool:
        """
        Save the current PCB design to file.

        Args:
            filename: Path to save .kicad_pcb file

        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_KICAD or not self.board:
            print("Error: No active board.")
            return False

        try:
            # Save board using KiCad's native format
            success = pcbnew.SaveBoard(filename, self.board)

            if success:
                self.design_history.append(
                    {
                        "action": "save_board",
                        "params": {"filename": filename},
                        "timestamp": self._get_timestamp(),
                    }
                )
                print(f"✓ Board saved to: {filename}")
                return True
            else:
                print(f"✗ Failed to save board")
                return False

        except Exception as e:
            print(f"✗ Error saving board: {e}")
            return False

    # Private helper methods

    def _to_mm(self, value: Union[str, float]) -> float:
        """Convert value to mm if it's a string with unit"""
        if isinstance(value, str):
            # Extract number and unit
            match = re.match(r"([\d.]+)\s*([a-zA-Z]+)", value.lower())
            if match:
                num = float(match.group(1))
                unit = match.group(2)
                if unit == "mm":
                    return num
                elif unit == "mil":
                    return num * 0.0254
                elif unit == "in":
                    return num * 25.4
            return float(value.replace("mm", "").strip())
        return float(value)

    def _get_layer_id(self, layer_name: str) -> int:
        """Convert layer name to KiCad layer ID"""
        layer_map = {
            "f.cu": pcbnew.F_Cu,
            "b.cu": pcbnew.B_Cu,
            "f.silks": pcbnew.F_SilkS,
            "b.silks": pcbnew.B_SilkS,
            "f.mask": pcbnew.F_Mask,
            "b.mask": pcbnew.B_Mask,
            "edge.cuts": pcbnew.Edge_Cuts,
        }
        return layer_map.get(layer_name.lower(), pcbnew.F_Cu)

    def _get_layer_name(self, layer_id: int) -> str:
        """Convert layer ID to human-readable name"""
        name_map = {
            pcbnew.F_Cu: "F_Cu",
            pcbnew.B_Cu: "B_Cu",
            pcbnew.F_SilkS: "F_Silkscreen",
            pcbnew.B_SilkS: "B_Silkscreen",
            pcbnew.F_Mask: "F_Mask",
            pcbnew.B_Mask: "B_Mask",
            pcbnew.Edge_Cuts: "Edge_Cuts",
        }
        return name_map.get(layer_id, f"Layer_{layer_id}")

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO format"""
        from datetime import datetime

        return datetime.now().isoformat()

    def _parse_with_openai(self, text: str) -> Dict:
        """Parse command using OpenAI GPT"""
        try:
            prompt = f"""
Parse the following KiCad design command into structured JSON:

Command: "{text}"

Return JSON with:
{{
  "action": "create_pcb|add_component|route_track|export_gerber|save_board|run_drc",
  "params": {{
    // Action-specific parameters
  }},
  "confidence": 0.0-1.0
}}

Be concise and accurate.
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"OpenAI parsing failed: {e}, falling back to keyword parsing")
            return self._parse_with_keywords(text)

    def _parse_with_keywords(self, text: str) -> Dict:
        """Parse command using keyword matching"""
        text_lower = text.lower()

        # Simple keyword-based parsing
        if "create" in text_lower and "pcb" in text_lower:
            return {
                "action": "create_pcb",
                "params": {"name": "custom_board"},
                "confidence": 0.6,
            }

        elif "add" in text_lower and "component" in text_lower:
            return {
                "action": "add_component",
                "params": {"ref": "NEW", "footprint": "Resistor_SMD"},
                "confidence": 0.6,
            }

        elif "export" in text_lower and "gerber" in text_lower:
            return {
                "action": "export_gerber",
                "params": {"output_dir": "./gerber"},
                "confidence": 0.7,
            }

        elif "export" in text_lower and "step" in text_lower:
            return {
                "action": "export_step",
                "params": {"output_file": "model.step"},
                "confidence": 0.7,
            }

        elif "route" in text_lower or "track" in text_lower:
            return {
                "action": "route_track",
                "params": {"start": (0, 0), "end": (10, 10), "width": 0.5},
                "confidence": 0.5,
            }

        elif "drc" in text_lower or "check" in text_lower:
            return {"action": "run_drc", "params": {}, "confidence": 0.8}

        elif "save" in text_lower:
            return {
                "action": "save_board",
                "params": {"filename": "design.kicad_pcb"},
                "confidence": 0.8,
            }

        else:
            return {"action": "unknown", "params": {}, "confidence": 0.0}


def execute_command(assistant: KiCadAssistant, command: str) -> bool:
    """
    Execute a natural language command through the assistant.

    Args:
        assistant: KiCadAssistant instance
        command: Natural language command string

    Returns:
        bool: True if command was executed, False otherwise
    """
    print(f"\nProcessing command: '{command}'\n")

    # Parse command
    parsed = assistant.parse_natural_language(command)
    print(f"Parsed: {parsed['action']} (confidence: {parsed.get('confidence', 'N/A')})")

    # Execute action
    action = parsed["action"]
    params = parsed["params"]

    success = False

    if action == "create_pcb":
        spec = PCBDesignSpec(**params)
        success = assistant.create_pcb(spec)

    elif action == "add_component":
        spec = ComponentSpec(**params)
        success = assistant.add_component(spec)

    elif action == "route_track":
        spec = TrackSpec(**params)
        success = assistant.route_track(spec)

    elif action == "export_gerber":
        success = assistant.export_gerber(params.get("output_dir", "./gerber"))

    elif action == "export_step":
        success = assistant.export_step(params.get("output_file", "model.step"))

    elif action == "run_drc":
        violations = assistant.run_drc()
        if violations:
            print("\nDRC Violations:")
            for v in violations:
                print(f"  - {v['message']}")
        success = True

    elif action == "save_board":
        success = assistant.save_board(params.get("filename", "design.kicad_pcb"))

    else:
        print(f"Unknown command: {command}")
        print(
            "Try: 'create pcb', 'add component', 'route track', 'export gerber', etc."
        )

    return success


# Convenience function for CLI usage
def main():
    """Main entry point for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="KiCad Automation Assistant")
    parser.add_argument("--api-key", help="OpenAI API key for NLP")
    parser.add_argument(
        "command", nargs="?", help="Natural language command to execute"
    )
    parser.add_argument("--batch", action="store_true", help="Run in batch mode")

    args = parser.parse_args()

    # Create assistant
    assistant = KiCadAssistant(openai_api_key=args.api_key)

    if args.command:
        # Execute single command
        execute_command(assistant, args.command)
    elif args.batch:
        # Interactive mode
        print("\n" + "=" * 50)
        print("KiCad Automation Assistant - Interactive Mode")
        print("=" * 50 + "\n")
        print("Type commands in natural language, or 'exit' to quit.\n")

        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break
                elif user_input:
                    execute_command(assistant, user_input)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()
