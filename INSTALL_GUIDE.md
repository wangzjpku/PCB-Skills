# KiCad Auto-Design Skill - 安装指南

## 📦 系统要求

### 必需
- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10/11, macOS 10.14+, Linux

### 可选（推荐）
- **KiCad**: 7.0 或更高版本（用于KiCad集成模式）

---

## 🚀 快速安装

### 步骤1: 下载Skill

将PCB-Skills文件夹复制到您的项目目录，或使用git克隆：

```bash
git clone <repository-url> PCB-Skills
cd PCB-Skills
```

### 步骤2: 验证安装

运行安装检查脚本：

```bash
python install_check.py
```

如果看到 `[SUCCESS] 所有检查通过！`，说明安装成功。

### 步骤3: 生成您的第一个设计

```bash
python create_power_supply_v6.py
```

输出文件将保存在 `output-result/220V_12V_PowerSupply/v1.0.x/` 目录中。

---

## 💻 OpenCode 集成

### 在OpenCode中使用

1. **安装到OpenCode技能目录**

   将 `PCB-Skills` 文件夹复制到OpenCode的技能目录：
   ```
   %USERPROFILE%\.claude\skills\  (Windows)
   ~/.claude/skills/              (macOS/Linux)
   ```

2. **在OpenCode中加载**

   OpenCode会自动识别技能。或者手动加载：
   ```python
   # 在OpenCode中
   %load_skill PCB-Skills
   ```

3. **使用Skill**

   ```python
   # 生成电源设计
   !python PCB-Skills/create_power_supply_v6.py
   
   # 或者使用Python API
   from PCB-Skills.scripts.generators import SchematicFileGeneratorV2
   ```

---

## 🎯 使用方式

### 方式1: 文件生成模式（推荐初学者）

**不需要KiCad安装**，生成.kicad_sch和.kicad_pcb文件：

```bash
cd PCB-Skills
python create_power_supply_v6.py
```

然后在KiCad中打开生成的文件。

### 方式2: Python API模式

```python
from scripts.generators import SchematicFileGeneratorV2, SymbolLibrary

# 创建原理图
sch = SchematicFileGeneratorV2()
sch.set_page_properties(297, 210, "My Design")

# 添加元件
r = SymbolLibrary.create_resistor("R1", "1k", (50, 100))
sch.add_symbol(r)

# 保存
sch.save("output.kicad_sch")
```

### 方式3: KiCad集成模式（需要KiCad）

在KiCad的Python Console中运行：

```python
import sys
sys.path.insert(0, r'/path/to/PCB-Skills/scripts')

from run_kicad_skill import run_in_kicad
run_in_kicad()
```

---

## 📁 文件结构

```
PCB-Skills/
├── create_power_supply_v6.py      # V6专业版（推荐使用）
├── install_check.py               # 安装验证脚本
├── requirements.txt               # Python依赖
├── scripts/
│   ├── __init__.py                # 模块入口
│   ├── kicad_integration.py       # KiCad API集成
│   ├── power_supply_designer.py   # 电源设计器
│   ├── run_kicad_skill.py         # KiCad启动器
│   ├── output_manager.py          # 输出管理
│   └── generators/                # 生成器模块
│       ├── sch_generator_v2.py    # 原理图生成器
│       ├── pcb_generator_v2.py    # PCB生成器
│       ├── footprint_lib.py       # 封装库
│       └── layout_manager.py      # 布局管理
├── output-result/                 # 输出目录
└── examples/                      # 示例脚本
```

---

## ⚙️ 配置选项

### 修改输出目录

编辑 `scripts/output_manager.py`：

```python
BASE_OUTPUT_DIR = "您的输出目录"
```

### 修改板子尺寸

在 `create_power_supply_v6.py` 中：

```python
pcb_gen.set_board_properties(
    width=120.0,      # 修改宽度
    height=95.0,      # 修改高度
    layers=2,         # 层数
    name="My Design"  # 设计名称
)
```

---

## 🔧 故障排除

### 问题1: 模块导入失败

**症状**: `ModuleNotFoundError: No module named 'scripts'`

**解决**:
```bash
cd PCB-Skills
python -c "import sys; sys.path.insert(0, '.'); from scripts.generators import *"
```

### 问题2: KiCad API不可用

**症状**: `WARNING: KiCad pcbnew模块不可用`

**解决**:
- 这是正常提示，仅在文件生成模式下工作
- 如需KiCad集成，请安装KiCad 7.0+

### 问题3: 输出目录权限错误

**症状**: `Permission denied: output-result`

**解决**:
```bash
# 创建输出目录并设置权限
mkdir output-result
chmod 755 output-result  # Linux/macOS
```

### 问题4: 中文显示乱码

**症状**: 控制台输出乱码

**解决**:
这是Windows控制台编码问题，不影响功能。生成的文件是正常的。

---

## 🎓 使用示例

### 示例1: 生成220V转12V电源

```bash
python create_power_supply_v6.py
```

输出：
- `output-result/220V_12V_PowerSupply/v1.0.x/`
  - `220V_12V_PowerSupply_v1.0.x.kicad_sch` - 原理图
  - `220V_12V_PowerSupply_v1.0.x.kicad_pcb` - PCB文件
  - `README.md` - 设计说明

### 示例2: 自定义设计

```python
# custom_design.py
import sys
sys.path.insert(0, '.')

from scripts.generators import (
    SchematicFileGeneratorV2,
    SymbolLibrary,
    PCBFileGeneratorV2
)

# 创建原理图
sch = SchematicFileGeneratorV2()
sch.set_page_properties(297, 210, "Custom PSU")

# 添加VIPer22A
viper = SymbolLibrary.create_viper22a("U1", "VIPer22A", (100, 100))
sch.add_symbol(viper)

# 添加变压器
t1 = SymbolLibrary.create_transformer("T1", "EE25", (150, 100))
sch.add_symbol(t1)

# 保存
sch.save("my_design.kicad_sch")
print("设计已生成: my_design.kicad_sch")
```

### 示例3: 批量生成多个版本

```bash
# 生成V4
python create_power_supply_v3.py

# 生成V5
python create_power_supply_v5.py

# 生成V6
python create_power_supply_v6.py
```

---

## 🔒 稳定性说明

### ✅ 已测试并稳定的功能

1. **文件生成** (v1.0.2)
   - ✅ 原理图生成 (.kicad_sch)
   - ✅ PCB生成 (.kicad_pcb)
   - ✅ 完整封装定义
   - ✅ 网络管理
   - ✅ 自动版本控制

2. **设计规范**
   - ✅ 网格对齐 (2.54mm)
   - ✅ 分区布局
   - ✅ 走线宽度分级
   - ✅ 星型接地

3. **兼容性**
   - ✅ KiCad 7.x
   - ✅ KiCad 8.x
   - ✅ Python 3.8-3.12

### ⚠️ 已知限制

1. **KiCad集成模式**
   - 需要KiCad安装
   - 仅在KiCad内可用
   - 需要手动复制到KiCad插件目录

2. **自动布线**
   - 基础走线已实现
   - 高级布线（差分对、等长）需要手动完成
   - 复杂PCB建议使用KiCad内置路由器

---

## 📞 技术支持

### 获取帮助

1. **查看日志**
   ```bash
   python create_power_supply_v6.py 2>&1 | tee log.txt
   ```

2. **运行诊断**
   ```bash
   python install_check.py
   ```

3. **检查文件**
   ```bash
   ls -la output-result/
   ```

### 版本信息

- **当前版本**: 7.0.0
- **最后更新**: 2026-02-07
- **兼容性**: KiCad 7.0+, Python 3.8+

---

## 📝 许可

MIT License - 自由使用和修改

---

## 🎉 恭喜！

您已成功安装KiCad Auto-Design Skill！

**开始设计**: `python create_power_supply_v6.py`

**享受自动化设计的乐趣！** 🚀
