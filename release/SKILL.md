---
name: kicad-nlp-auto-design
description: Natural language to KiCad PCB/SCH generator with GUI compatibility
version: 1.0.0
author: wangzjpku
tags:
  - kicad
  - pcb-design
  - schematic-design
  - natural-language
  - automation
  - eda
  - python
license: GPL-3.0-or-later

# KiCad NLP Auto-Design Skill

A complete skill that converts natural language hardware descriptions into KiCad PCB and schematic files. Generated files (.kicad_pcb and .kicad_sch) can be directly opened and edited in KiCad GUI.

## Features

### Natural Language Processing
- **Chip Recognition**: Auto-detect MCU chips (ESP32, STM32, Arduino, AVR, PIC)
- **Component Extraction**: Identify LEDs, resistors, capacitors, buttons, sensors from text
- **Power Analysis**: Parse voltage requirements and regulator specifications
- **Interface Detection**: Identify UART, I2C, SPI, GPIO, PWM, USB communication
- **Control Logic**: Extract control schemes (GPIO toggle, PWM dimming, UART control)

### File Generation
- **Schematic Files**: Generate .kicad_sch files with symbols, wires, labels
- **PCB Files**: Generate .kicad_pcb files with footprints, tracks, vias, board outline
- **KiCad Standard**: Uses S-expression format compatible with KiCad 7.x/8.x/9.x
- **GUI Compatible**: Generated files open directly in KiCad GUI without conversion

### Core Capabilities

#### PCB Generation
- Multi-layer board support (2-12 layers)
- Automatic board outline creation
- Component footprint placement with position and rotation
- Track routing with customizable width and layers
- Via creation for multi-layer connections
- Copper zone (fill) support
- Design rule integration

#### Schematic Generation
- Symbol library with standard components (VCC, GND, resistors, capacitors)
- Wire connections between component pins
- Label system (local, global, hierarchical)
- Power symbol integration
- Net management

#### Design Validation
- DRC (Design Rule Check) integration
- ERC (Electrical Rule Check) support
- BOM (Bill of Materials) generation
- Gerber export for fabrication
- STEP model export for 3D viewing

## Installation

### Prerequisites
- Python 3.8 or higher
- KiCad 7.0 or later recommended (for GUI editing)
- No KiCad API dependencies required (uses native S-expression format)

### Installation Steps

1. Clone or download this skill
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify installation:
   ```bash
   python -c "from scripts.core_designer import design_from_natural_language; print('OK')"
   ```

## Usage

### Command Line

```bash
# Generate from natural language description
python scripts/core_designer.py "设计一个ESP32开发板，包含USB和LED" -o ./output

# Run examples
python examples/led_circuit.py
python examples/esp32_board.py
```

### Python API

```python
from scripts.core_designer import design_from_natural_language

# Generate design
result = design_from_natural_language(
    description="设计一个简单的LED电路，5V供电",
    output_dir="./output"
)

if result['success']:
    print(f"SCH: {result['sch_file']}")
    print(f"PCB: {result['pcb_file']}")
```

### Natural Language Examples

**Chinese Examples:**
- "设计一个ESP32开发板，包含WiFi和蓝牙功能"
- "创建STM32F103最小系统板"
- "做一个Arduino UNO兼容的板子"
- "生成4层PCB，尺寸100x80mm"
- "LED闪烁电路，GPIO2控制"

**English Examples:**
- "Design an ESP32 development board with WiFi and Bluetooth"
- "Create STM32F103 minimum system board"
- "Make an Arduino UNO compatible board"
- "Generate 4-layer PCB, size 100x80mm"
- "LED blink circuit controlled by GPIO2"

## Output Files

Generated files can be directly opened in KiCad:

- `.kicad_sch` - Schematic file (symbol view, wiring)
- `.kicad_pcb` - PCB file (footprints, tracks, layout)
- `design_report.txt` - Design summary and component list

## Architecture

```
┌─────────────────────────────────────────────┐
│      Natural Language Input               │
│  "设计ESP32开发板..."                   │
└───────────────┬───────────────────────────┘
                ↓
┌─────────────────────────────────────────────┐
│         NLP Parser                      │
│  - Chip detection                      │
│  - Component extraction                 │
│  - Power analysis                      │
└───────────────┬───────────────────────────┘
                ↓
┌─────────────────────────────────────────────┐
│       Design Generator                   │
│  - SCH Generator                     │
│  - PCB Generator                     │
└───────────────┬───────────────────────────┘
                ↓
┌─────────────────────────────────────────────┐
│      File Output                        │
│  - schematic.kicad_sch              │
│  - board.kicad_pcb                  │
│  - report.txt                       │
└─────────────────────────────────────────────┘
```

## Components

### Modules

- **scripts/core_designer.py**: Main design orchestrator
- **scripts/generators/sch_generator.py**: Schematic file generator
- **scripts/generators/pcb_generator.py**: PCB file generator
- **scripts/nlp/parser.py**: Natural language parser
- **examples/****: Usage examples

### Data Structures

- `HardwareSpec`: Parsed hardware specifications
- `SCHSymbol`: Schematic component symbol
- `PCBComponent`: PCB footprint component
- `SCHWire`: Schematic wire connection
- `PCBTrack`: PCB routing track

## Examples

See `examples/` directory for complete working examples:
- `led_circuit.py` - Simple LED circuit
- `esp32_board.py` - ESP32 development board

## Documentation

- **API Reference**: Complete API documentation for all classes
- **Tutorials**: Step-by-step guides
- **Troubleshooting**: Common issues and solutions

## Limitations

- Requires manual review for complex designs
- Auto-routing is basic (straight line connections)
- Component library is limited to standard parts
- High-speed signal design requires manual optimization

## Future Enhancements

- Enhanced natural language understanding with AI
- Intelligent auto-routing algorithms
- Component library expansion (thousands of parts)
- Signal integrity analysis
- 3D model integration

## License

GPL-3.0-or-later (compatible with KiCad license)

## Contributing

Contributions welcome! Areas for improvement:
- Natural language parsing accuracy
- Additional KiCad features support
- More component libraries
- Documentation improvements
- Test cases and examples

## Acknowledgments

Based on KiCad's S-expression file format.
Inspired by KiCad automation tools and community projects.
Compatible with KiCad 7.x/8.x/9.x GUI versions.
