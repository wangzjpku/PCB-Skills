# KiCad Automation Skill

Natural language interface for KiCad PCB and schematic design automation.

[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/downloads/)

## Overview

This skill provides a natural language interface to control KiCad, enabling:
- **PCB Design**: Create boards, add components, route tracks, export Gerber/STEP
- **Schematic Design**: Add symbols, wire circuits, generate netlists
- **Automation**: DRC/ERC checks, BOM generation, file conversions
- **Natural Language Control**: Describe what you want in plain English/Chinese

## Features

- 🎯 **Natural Language Interface**: Design using plain language
- 🛠️ **Full PCB Capabilities**: From board creation to manufacturing files
- 📊 **Schematic Support**: Symbol placement, wiring, netlist generation
- 🤖 **AI-Powered**: Optional OpenAI integration for advanced parsing
- 🔌 **File-Based**: Works with KiCad's native .kicad_pcb/.kicad_sch files
- 🧪 **DRC/ERC**: Automated design rule checking
- 📦 **Multiple Formats**: Gerber, STEP, BOM, netlist, and more

## Installation

### Prerequisites

- Python 3.8 or higher
- KiCad 7.0 or later (with Python scripting support)

### Step 1: Clone the Repository

```bash
git clone https://github.com/wangzjpku/PCB-Skills.git
cd PCB-Skills
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install as KiCad Plugin (Optional)

For GUI integration within KiCad:

**Windows:**
```bash
xcopy /E /I /Y scripts\kicad_plugin "%USERPROFILE%\Documents\KiCad\7.0\scripting\plugins\KiCadAssistant"
```

**Linux:**
```bash
mkdir -p ~/.local/share/kicad/7.0/scripting/plugins/KiCadAssistant
cp scripts/kicad_plugin/* ~/.local/share/kicad/7.0/scripting/plugins/KiCadAssistant/
```

**macOS:**
```bash
mkdir -p ~/Library/Preferences/kicad/7.0/scripting/plugins/KiCadAssistant
cp scripts/kicad_plugin/* ~/Library/Preferences/kicad/7.0/scripting/plugins/KiCadAssistant/
```

### Step 4: Configure (Optional)

Create a configuration file `config.yaml`:

```yaml
openai:
  api_key: "your-openai-api-key"  # Optional, for enhanced NLP

ki cad:
  default_layers: 2
  default_thickness: "1.6mm"
  default_units: "mm"
```

## Usage

### Command Line Interface

```bash
# Interactive mode
python scripts/core.py

# Execute single command
python scripts/core.py "create a 100mm by 100mm PCB"

# Use OpenAI for enhanced parsing
python scripts/core.py --api-key YOUR_KEY "add a resistor at 10,10"
```

### Python API

```python
from scripts.core import KiCadAssistant, PCBDesignSpec, execute_command

# Create assistant
assistant = KiCadAssistant(openai_api_key="your-key")

# Create PCB
spec = PCBDesignSpec(width="100mm", height="80mm", name="LED Controller")
assistant.create_pcb(spec)

# Add components
from scripts.core import ComponentSpec
comp = ComponentSpec(ref="LED1", footprint="LED_0805", value="Red LED")
assistant.add_component(comp)

# Route tracks
from scripts.core import TrackSpec
track = TrackSpec(start=(10, 10), end=(30, 10), width="0.5mm")
assistant.route_track(track)

# Export
assistant.export_gerber("./output/gerber")
assistant.export_step("./output/model.step")
```

### Natural Language Commands

Try these natural language commands:

```
# Board creation
"Create a 100x100mm 2-layer PCB"
"New board named Arduino Uno with 4 layers"

# Components
"Add a resistor at position 10,10"
"Place ATmega328P footprint at 20,30"
"Add capacitor C1 value 100nF to front copper"

# Routing
"Connect pin 1 to pin 2 with 0.5mm track"
"Route from LED1 to R1 with 0.3mm wire"
"Add track from 5,5 to 15,5"

# Exports
"Export Gerber files to gerber folder"
"Generate STEP model 3d_model.step"

# Checks
"Run DRC check"
"Verify design rules"

# Save
"Save design as my_project.kicad_pcb"
```

## Examples

See the `examples/` directory for complete examples:

- `examples/led_circuit.py` - Simple LED circuit
- `examples/mcu_board.py` - Microcontroller board
- `examples/4layer_pcb.py` - Multi-layer design

## Documentation

- **API Reference**: `docs/api.md`
- **Tutorials**: `docs/tutorials.md`
- **Troubleshooting**: `docs/troubleshooting.md`

## Architecture

### How It Works

1. **Natural Language Parsing**: Converts user input to structured commands
   - With OpenAI: GPT-4 parses intent and extracts parameters
   - Without OpenAI: Keyword-based matching and regex

2. **KiCad API Integration**: Uses KiCad's Python bindings (SWIG)
   - `pcbnew` module for PCB operations
   - `eeschema` module for schematic operations

3. **File-Based Automation**: Reads/writes KiCad's native file formats
   - `.kicad_pcb` - PCB design (S-expression)
   - `.kicad_sch` - Schematic (S-expression)

4. **CLI/GUI Modes**:
   - **CLI**: Standalone scripts and batch processing
   - **GUI**: Plugin that integrates into KiCad Tools menu

### Components

- **KiCadAssistant**: Main interface class
- **PCBDesigner**: PCB-specific operations
- **SchematicDesigner**: Schematic-specific operations
- **FileManager**: Import/export operations
- **DesignValidator**: DRC/ERC operations

## Limitations

- Requires KiCad to be installed with Python scripting support
- Some operations require KiCad GUI to be running (for plugin mode)
- OpenAI integration requires API key and network connection
- Complex designs may need manual review after automation

## Contributing

Contributions are welcome! Areas for improvement:

- 🎨 Better natural language parsing
- 🔧 Additional KiCad features
- 📚 More examples and tutorials
- 🐛 Bug fixes and optimizations
- 🌍 i18n (internationalization)

## License

This project is licensed under **GPL-3.0-or-later**, compatible with KiCad's license.

## Acknowledgments

Built on top of KiCad's Python scripting API.
Inspired by:
- [kicad-jlcpcb-tools](https://github.com/Bouni/kicad-jlcpcb-tools)
- [kicad-kbplacer](https://github.com/adamws/kicad-kbplacer)
- [JLC2KiCad_lib](https://github.com/TousstNicolas/JLC2KiCad_lib)

## Contact

- **Issues**: [GitHub Issues](https://github.com/wangzjpku/PCB-Skills/issues)
- **Author**: wangzjpku@163.com

---

**Happy PCB Designing! 🛠️📦**
