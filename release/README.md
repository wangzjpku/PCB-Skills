# KiCad Auto Power Supply Designer

自动生成KiCad电源设计文件(PCB/SCH)的Python工具。

## 功能特性

- **自动生成PCB/SCH文件** - 基于芯片型号和规格自动生成
- **支持多种拓扑** - 反激式(FLYBACK)、Buck、Boost
- **14种电源芯片** - VIPer、UC384x、TL494、MP1584等
- **可视化评估** - 使用Playwright生成PCB预览
- **自动修复** - 检测并修复板框、走线等问题

## 支持的芯片

### AC-DC (反激式)
- VIPer22A/12A/35
- UC3842/43/44/45
- TL494, TNY279, LNK304

### DC-DC (Buck)
- MP1584, LM2596, XL4015, MP2307

### DC-DC (Boost)
- MT3608, XL6009

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行设计生成
python complete_automation.py

# 或使用主系统
python auto_power_design_system.py
```

## 项目结构

```
├── scripts/              # 核心脚本
│   ├── generators/      # PCB/SCH生成器
│   └── automation/      # 自动化工具
├── examples/            # 示例
├── chip_database.py     # 芯片数据库
└── auto_power_design_system.py  # 主系统
```

## 使用方法

```python
from auto_power_design_system import AutoPowerDesignSystem

system = AutoPowerDesignSystem()

# 运行完整流程
import asyncio
asyncio.run(system.run_full_pipeline())
```

## 文档

- `INSTALL_GUIDE.md` - 安装指南
- `SKILL.md` - Skill使用说明
- `AGENTS.md` - 开发者指南

## 版本

**v1.0.0** - 初始版本
- 55个参考案例
- 23个生成设计
- 完整PCB/SCH文件

## License

MIT License
