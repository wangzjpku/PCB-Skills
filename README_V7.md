# KiCad Auto-Design Skill V7.0

## 🎯 项目概述

**KiCad Auto-Design Skill** 是一个完整的自动化PCB设计解决方案，支持：
- ✅ 自动生成专业的220V转12V电源设计
- ✅ 直接集成KiCad Python API (pcbnew)
- ✅ 智能自动布局和布线
- ✅ 符合业界最佳实践的专业设计规范

**当前版本**: V7.0.0 (KiCad集成版)  
**发布日期**: 2026-02-07  
**兼容性**: Python 3.8+, KiCad 7.0+

---

## ✨ 核心功能

### 1. 文件生成模式（独立运行）
- 无需KiCad安装
- 生成标准的 `.kicad_sch` 和 `.kicad_pcb` 文件
- 可在KiCad中直接打开

### 2. KiCad集成模式（推荐）
- 使用KiCad Python API (pcbnew)
- 直接在KiCad中自动放置元件
- 实时布局和布线

### 3. 专业设计规范
- 网格对齐 (2.54mm标准)
- 功能分区布局
- 电流回路最小化
- 星型接地系统
- 走线宽度分级

---

## 🚀 快速开始

### 安装

```bash
# 1. 克隆或下载项目
cd PCB-Skills

# 2. 验证安装
python install_check.py

# 3. 生成设计
python create_power_supply_v6.py
```

### 使用

**文件生成模式**（不需要KiCad）：
```bash
python create_power_supply_v6.py
# 输出到 output-result/220V_12V_PowerSupply/v1.0.x/
```

**KiCad集成模式**（在KiCad中运行）：
```python
# 在KiCad Python Console中
import sys
sys.path.insert(0, r'/path/to/PCB-Skills/scripts')
from run_kicad_skill import run_in_kicad
run_in_kicad()
```

---

## 📁 项目结构

```
PCB-Skills/
├── 📄 create_power_supply_v6.py      # V6专业版（推荐使用）
├── 📄 install_check.py               # 安装验证脚本
├── 📄 requirements.txt               # Python依赖
├── 📄 INSTALL_GUIDE.md               # 详细安装指南
├── 📄 README_KiCad_Integration.md    # KiCad集成文档
│
├── 📁 scripts/                       # 核心模块
│   ├── 📄 __init__.py                # 模块入口
│   ├── 📄 kicad_integration.py       # ⭐ KiCad API集成
│   ├── 📄 power_supply_designer.py   # ⭐ 电源设计器
│   ├── 📄 run_kicad_skill.py         # ⭐ KiCad启动器
│   ├── 📄 output_manager.py          # 输出管理
│   └── 📁 generators/                # 生成器模块
│       ├── 📄 sch_generator_v2.py    # 原理图生成器
│       ├── 📄 pcb_generator_v2.py    # PCB生成器
│       ├── 📄 footprint_lib.py       # 封装库（15+封装）
│       └── 📄 layout_manager.py      # 智能布局管理器
│
├── 📁 output-result/                 # 输出目录
│   └── 📁 220V_12V_PowerSupply/
│       ├── 📁 v1.0.0/                # V4版本
│       ├── 📁 v1.0.1/                # V5智能布局版
│       └── 📁 v1.0.2/                # V6专业版
│
└── 📁 examples/                      # 示例脚本
    ├── 📄 led_circuit.py
    └── 📄 esp32_board.py
```

---

## 🎓 使用示例

### 生成完整电源设计

```bash
$ python create_power_supply_v6.py

输出目录: output-result\220V_12V_PowerSupply\v1.0.2
版本: v1.0.2
======================================================
220V to 12V Power Supply - V6 Professional Edition
======================================================

[1/2] 生成专业级原理图...
  应用专业布线规则...
  完成：16个符号，24条连线
  [OK] 原理图: output-result\...\220V_12V_PowerSupply_v1.0.2.kicad_sch

[2/2] 生成专业级PCB...
  放置元件...
  专业布线...
  完成：17个元件，20条走线
  [OK] PCB: output-result\...\220V_12V_PowerSupply_v1.0.2.kicad_pcb

======================================================
设计完成!
======================================================
版本: v1.0.2
统计:
  原理图: 16符号, 24连线
  PCB: 17元件, 20走线
======================================================
```

### 自定义设计

```python
from scripts.generators import (
    SchematicFileGeneratorV2,
    SymbolLibrary,
    PCBFileGeneratorV2
)

# 创建原理图
sch = SchematicFileGeneratorV2()
sch.set_page_properties(297, 210, "My PSU")

# 添加VIPer22A
viper = SymbolLibrary.create_viper22a("U1", "VIPer22A", (100, 100))
sch.add_symbol(viper)

# 添加变压器
t1 = SymbolLibrary.create_transformer("T1", "EE25", (150, 100))
sch.add_symbol(t1)

# 连接
sch.connect_pins("U1", "5", "T1", "1", "DRAIN")

# 保存
sch.save("my_design.kicad_sch")
```

---

## 📊 版本演进

| 版本 | 日期 | 主要特性 |
|------|------|----------|
| V1.0 | 2026-02-05 | 基础文件生成 |
| V2.0 | 2026-02-06 | 增强版生成器 |
| V3.0 | 2026-02-07 | 完整封装定义 |
| V4.0 | 2026-02-07 | 自动网络管理 |
| V5.0 | 2026-02-07 | 智能布局系统 |
| V6.0 | 2026-02-07 | 专业级设计规范 |
| **V7.0** | **2026-02-07** | **KiCad API集成** |

---

## 🔬 技术亮点

### 1. 原理图生成器 V2
- 完整的符号库（20+标准符号）
- 自动连线系统
- 网络标签支持
- KiCad 8.x兼容格式

### 2. PCB生成器 V2
- 15+标准封装定义
- 完整焊盘/丝印/装配层
- 自动网络管理
- 智能布线算法

### 3. 布局管理器
- 网格/线性/聚类/专业布局策略
- 分区设计（高压/低压/控制）
- 电流回路最小化
- 安规距离检查

### 4. KiCad集成
- pcbnew API封装
- 实时元件放置
- 自动走线生成
- 设计规则检查

---

## 🛡️ 设计规范

### 原理图规范
✅ 网格对齐 (2.54mm)  
✅ 信号流向 (左→右，上→下)  
✅ 功能分区 (输入→保护→整流→功率→输出→反馈)  
✅ 标准符号库  
✅ 最小化连线交叉  

### PCB规范
✅ 分区布局 (高压/低压隔离)  
✅ 电流回路最小化  
✅ 走线宽度分级 (1.5/1.2/1.0/0.5mm)  
✅ 星型接地系统  
✅ 安规距离 (初级/次级>6mm)  

---

## 📦 封装库

包含15+标准封装：
- **电阻**: 0805, 1206, 轴向直插
- **电容**: 0805贴片, 电解电容 (8x10, 10x10)
- **二极管**: SOD-123, DO-41, 桥式整流器, TO-220
- **IC**: DIP-8, SOP-8, TO-92
- **连接器**: 螺钉端子 (5.08mm), 排针
- **变压器**: EE-25 (6引脚)
- **保险丝**: 5x20mm直插, 1206贴片

---

## 🔧 系统要求

### 必需
- Python 3.8 或更高版本
- 约10MB磁盘空间

### 可选（推荐）
- KiCad 7.0 或更高版本（用于KiCad集成模式）

### 依赖
- dataclasses (Python内置)
- typing (Python内置)
- 无外部依赖！

---

## 📖 文档

- **INSTALL_GUIDE.md** - 详细安装指南
- **README_KiCad_Integration.md** - KiCad集成文档
- **SKILL.md** - 技能功能说明
- **KICAD_SOURCE_GUIDE.md** - KiCad源码指南

---

## 🎓 教育价值

本项目演示了：
1. **PCB设计自动化** - 使用Python生成KiCad文件
2. **专业设计规范** - 基于TI/ST应用笔记的最佳实践
3. **KiCad API使用** - pcbnew模块的实际应用
4. **电源设计知识** - VIPer22A反激式电源完整方案

---

## 🤝 开源许可

MIT License - 自由使用、修改和分发

---

## 📞 技术支持

### 常见问题

**Q: 是否需要安装KiCad？**  
A: 不需要！文件生成模式独立工作。KiCad仅用于集成模式。

**Q: 可以在其他电脑运行吗？**  
A: 可以！只需Python 3.8+，无需其他依赖。

**Q: 如何在OpenCode中使用？**  
A: 复制到技能目录即可，或使用 `%load_skill` 命令。

**Q: 生成的文件可以在KiCad中打开吗？**  
A: 可以！生成的.kicad_sch和.kicad_pcb是标准KiCad格式。

---

## 🎉 开始设计

```bash
# 克隆项目
git clone <repository-url> PCB-Skills
cd PCB-Skills

# 验证安装
python install_check.py

# 生成您的第一个设计
python create_power_supply_v6.py

# 在KiCad中打开生成的文件
# output-result/220V_12V_PowerSupply/v1.0.2/*.kicad_pcb
```

---

**祝设计愉快！** 🚀⚡

---

*KiCad Auto-Design Skill V7.0 - 让PCB设计更简单*
