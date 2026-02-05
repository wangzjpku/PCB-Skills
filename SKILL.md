---
name: kicad-automation
description: Natural language interface for KiCad PCB and schematic design automation
version: 1.0.0
author: wangzjpku
tags:
  - kicad
  - pcb-design
  - schematic-design
  - automation
  - python-scripting
  - eda
license: GPL-3.0-or-later

# KiCad Automation Skill

A comprehensive skill that enables natural language control of KiCad EDA (Electronic Design Automation) for PCB and schematic design.

## Capabilities

### PCB Design Automation
- Create new PCB boards with custom dimensions
- Add/place footprints and components
- Create and route tracks
- Define and manage layers
- Add zones (copper pours)
- Export Gerber files
- Export 3D models (STEP)
- Run Design Rule Checks (DRC)
- Generate BOM (Bill of Materials)

### Schematic Design Automation
- Create new schematic sheets
- Add schematic symbols
- Wire components together
- Add labels and annotations
- Generate netlists
- Export to various formats
- Run Electrical Rule Checks (ERC)

### Integration Capabilities
- File-based automation (read/write .kicad_pcb, .kicad_sch)
- Python scripting via KiCad's SWIG bindings
- CLI automation via kicad-cli
- Plugin system integration
- Natural language processing for design intent

## Usage

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/wangzjpku/PCB-Skills.git
   cd PCB-Skills
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For KiCad plugin mode:
   - Copy `scripts/kicad_plugin/` to your KiCad scripting plugins directory
   - Windows: `C:\Users\<username>\Documents\KiCad\<version>\scripting\plugins\`
   - Linux: `~/.local/share/kicad/<version>/scripting/plugins/`
   - macOS: `~/Library/Preferences/kicad/scripting/plugins/`

### Basic Usage

#### Natural Language Interface

```python
from scripts.core import KiCadAssistant

assistant = KiCadAssistant()

# Create a new PCB
assistant.create_pcb(width="100mm", height="100mm", name="my_design")

# Add components via natural language
assistant.add_component(ref="U1", footprint="SOIC-8", value="ATmega328P")
assistant.add_component(ref="C1", footprint="C0805", value="100nF")

# Route connections
assistant.route_tracks("Connect U1 pin 1 to C1 pin 1", width="0.5mm")

# Export files
assistant.export_gerber(output_dir="./gerber")
assistant.export_step("./model.step")

# Run DRC
assistant.run_drc()
```

#### Standalone Scripting

```bash
# Using Python scripts directly
python scripts/pcb_designer.py --config design.json --output board.kicad_pcb

# Using CLI (if available)
kicad-cli pcb export gerber board.kicad_pcb --output gerber/
```

#### Plugin Mode

Load the plugin in KiCad:
1. Open KiCad
2. Go to Tools → External Plugins
3. Select "KiCad Automation Assistant"
4. Use the integrated interface for natural language commands

## API Reference

### Core Classes

- `KiCadAssistant`: Main interface for natural language automation
- `PCBDesigner`: PCB-specific design operations
- `SchematicDesigner`: Schematic-specific design operations
- `FileManager`: File I/O operations
- `DesignValidator`: DRC/ERC validation

### Supported File Formats

- `.kicad_pcb` - PCB design files
- `.kicad_sch` - Schematic design files
- `.kicad_pro` - Project files
- `.gerber` - Gerber fabrication files
- `.step` - 3D model files
- `.csv` - BOM files

## Examples

See `examples/` directory for:
- Simple LED circuit design
- MCU board with multiple components
- Multi-layer PCB design
- Schematic to PCB workflow

## Documentation

- `docs/api.md` - Complete API reference
- `docs/tutorials.md` - Step-by-step tutorials
- `docs/troubleshooting.md` - Common issues and solutions

## License

This skill is licensed under GPL-3.0-or-later, compatible with KiCad's license.

## Contributing

Contributions welcome! Please submit issues and pull requests to improve:
- Natural language parsing
- Design automation workflows
- Additional KiCad features
- Documentation and examples

## Requirements

- Python 3.8+
- KiCad 7.0 or later (with Python scripting support)
- Optional: kicad-cli for some operations

## Acknowledgments

Built on top of KiCad's Python scripting API (SWIG bindings).
Inspired by existing KiCad automation tools:
- kicad-jlcpcb-tools
- kicad-kbplacer
- JLC2KiCad_lib
