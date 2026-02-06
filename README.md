# KiCad Auto-Design Skill v1.0.0

自动生成KiCad PCB和原理图文件的Python工具。

## 功能

- **原理图生成**: 创建.kicad_sch文件
- **PCB生成**: 创建.kicad_pcb文件  
- **KiCad兼容**: 支持KiCad 7.x/8.x/9.x
- **直接可用**: 生成的文件可直接在KiCad GUI中打开

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 使用

**Python API:**
```python
from scripts.core_designer import create_led_circuit, create_power_supply

# 生成LED电路
result = create_led_circuit("./output")
print(f"SCH: {result['sch_file']}")
print(f"PCB: {result['pcb_file']}")

# 生成12V电源模块
result = create_power_supply("./output")
```

**命令行:**
```bash
# 生成LED电路
python scripts/core_designer.py --led -o ./output

# 生成电源模块
python scripts/core_designer.py --psu -o ./output
```

### 简单示例

```python
from scripts.generators.sch_generator import SchematicFileGenerator, SCHSymbol
from scripts.generators.pcb_generator import PCBFileGenerator, PCBComponent

# 创建原理图
sch = SchematicFileGenerator()
sch.set_page_properties(210.0, 297.0, "My Design")

# 添加电阻
r1 = SCHSymbol(ref="R1", name="R", value="1k", 
               position=(50, 50), 
               pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}])
sch.add_symbol(r1)

# 保存
sch.save("./output/my_design.kicad_sch")

# 创建PCB
pcb = PCBFileGenerator()
pcb.set_board_properties(50.0, 50.0, name="My PCB")

# 添加组件
comp = PCBComponent(ref="R1", footprint="R_0805", value="1k", position=(25, 25))
pcb.add_component(comp)

# 保存
pcb.save("./output/my_design.kicad_pcb")
```

## 项目结构

```
PCB-Skills/
├── scripts/
│   ├── core_designer.py         # 主设计器
│   └── generators/
│       ├── sch_generator.py     # 原理图生成器
│       └── pcb_generator.py     # PCB生成器
├── simple_designer.py           # 简化版示例
├── requirements.txt
└── README.md
```

## API文档

### SchematicFileGenerator

生成KiCad原理图(.kicad_sch)。

```python
from scripts.generators.sch_generator import SchematicFileGenerator, SCHSymbol, SCHWire

gen = SchematicFileGenerator()
gen.set_page_properties(width=210.0, height=297.0, name="Design")

# 添加符号
symbol = SCHSymbol(
    ref="R1",
    name="R", 
    value="1k",
    position=(50, 50),
    pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}]
)
gen.add_symbol(symbol)

# 添加连线
gen.add_wire(SCHWire(start=(40, 50), end=(60, 50)))

# 保存
gen.save("design.kicad_sch")
```

### PCBFileGenerator

生成KiCad PCB(.kicad_pcb)。

```python
from scripts.generators.pcb_generator import PCBFileGenerator, PCBComponent

gen = PCBFileGenerator()
gen.set_board_properties(width=50.0, height=50.0, name="PCB")

# 添加组件
comp = PCBComponent(
    ref="R1",
    footprint="R_0805_2012Metric",
    value="1k",
    position=(25, 25),
    pads=[
        {"number": "1", "x": -0.95, "y": 0, "net": 1, "net_name": "VCC"},
        {"number": "2", "x": 0.95, "y": 0, "net": 2, "net_name": "GND"}
    ]
)
gen.add_component(comp)

# 设置板框
gen.set_board_outline([(0,0), (50,0), (50,50), (0,50), (0,0)])

# 保存
gen.save("design.kicad_pcb")
```

## 生成的文件

生成的文件可在KiCad中直接打开：

```bash
# 打开PCB
pcbnew design.kicad_pcb

# 打开原理图
eeschema design.kicad_sch
```

## 系统要求

- Python 3.8+
- KiCad 7.0+ (用于查看和编辑)

## 许可证

GPL-3.0-or-later

## 版本历史

### v1.0.0
- 初始版本
- 原理图生成功能
- PCB生成功能
- LED电路示例
- 12V电源模块示例
