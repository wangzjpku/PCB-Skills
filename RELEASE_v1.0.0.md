# KiCad Auto-Design Skill v1.0.0 Release Notes

## 发布日期
2026-02-06

## 版本概述
KiCad Auto-Design Skill v1.0.0 是首个正式版本，提供从Python代码生成KiCad PCB和原理图文件的能力。

## 核心功能

### 1. 原理图生成
- 生成标准KiCad .kicad_sch文件
- 支持符号、连线、连接点、电源符号
- 符合KiCad 9.0格式规范

### 2. PCB生成
- 生成标准KiCad .kicad_pcb文件
- 支持元件封装、走线、网络定义
- 支持板框定义

### 3. 预设设计模板
- LED电路示例
- 220V转12V电源模块示例

## 文件结构

```
PCB-Skills/
├── scripts/                    # 核心代码
│   ├── __init__.py            # 包初始化
│   ├── core_designer.py       # 主设计器
│   └── generators/            # 生成器模块
│       ├── __init__.py
│       ├── sch_generator.py   # 原理图生成器
│       └── pcb_generator.py   # PCB生成器
├── examples/                   # 示例代码
│   ├── led_circuit.py
│   └── esp32_board.py
├── simple_designer.py         # 简化版独立示例
├── requirements.txt           # 依赖
├── README.md                  # 说明文档
├── SKILL.md                   # Skill定义
└── LICENSE                    # 许可证
```

## 使用示例

### Python API
```python
from scripts.core_designer import create_led_circuit

result = create_led_circuit("./output")
print(f"Generated: {result['sch_file']}, {result['pcb_file']}")
```

### 命令行
```bash
python scripts/core_designer.py --led -o ./output
```

## 系统要求
- Python 3.8+
- KiCad 7.0+ (用于查看和编辑生成的文件)

## 已知限制
1. 自动布线功能简化，复杂设计需要手动优化
2. 使用通用封装名，可能需要手动映射到实际库
3. 不支持完整的自然语言解析（移除了不稳定的NLP模块）

## 技术细节
- 使用KiCad标准S-expression格式
- 坐标单位为毫米(mm)
- 支持多层板定义
- 兼容KiCad 7.x/8.x/9.x

## 许可证
GPL-3.0-or-later

## 作者
wangzjpku

## 版本历史
- v1.0.0 (2026-02-06): 初始发布
  - 原理图生成功能
  - PCB生成功能
  - LED电路示例
  - 电源模块示例
