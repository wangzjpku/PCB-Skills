# KiCad 自动截图分析系统 V1.0

🤖 **小白友好的PCB设计智能助手**

自动截图、智能分析、给出改进建议，一键完成！

## 功能特点

✅ **全自动截图** - 自动检测KiCad窗口并截图  
✅ **智能分析** - 自动识别设计问题和界面状态  
✅ **改进建议** - 针对问题给出具体的改进方案  
✅ **一键修复** - 支持自动修复常见问题（可选）  
✅ **多种截图方式** - 自动选择最佳可用的截图方案  

## 快速开始

### 1. 安装依赖

```bash
cd PCB-Skills
pip install pillow mss pyautogui psutil
```

Windows用户额外安装（用于窗口检测）：
```bash
pip install pywin32
```

### 2. 运行分析

**方式1: 一键分析（最简单）**
```bash
python -m scripts.vision.auto_analyzer
```

**方式2: 分析指定PCB文件**
```bash
python -m scripts.vision.auto_analyzer --pcb ./output/my_design.kicad_pcb
```

**方式3: 启用自动修复**
```bash
python -m scripts.vision.auto_analyzer --auto-fix
```

### 3. 查看结果

分析完成后，会在 `./analysis_reports` 目录生成：
- `screenshots/` - 截图文件
- `analysis_report_YYYYMMDD_HHMMSS.json` - 详细分析报告

## 使用场景

### 场景1: 设计完成后检查

1. 在KiCad中完成PCB设计
2. 切换到PCB编辑器窗口
3. 运行：`python -m scripts.vision.auto_analyzer`
4. 系统会：
   - 自动截图
   - 检查是否有板框、敷铜、走线
   - 给出设计得分和改进建议

### 场景2: 批量检查多个设计

```python
from scripts.vision.auto_analyzer import KiCadAutoAnalyzer
import glob

analyzer = KiCadAutoAnalyzer()

# 批量分析所有PCB文件
for pcb_file in glob.glob("./output/**/*.kicad_pcb", recursive=True):
    print(f"\n分析: {pcb_file}")
    report = analyzer.analyze(pcb_file=pcb_file, wait_time=1)
    print(f"得分: {report.overall_score}")
```

### 场景3: 持续监控

```python
import time
from scripts.vision.auto_analyzer import KiCadAutoAnalyzer

analyzer = KiCadAutoAnalyzer()

# 每5分钟检查一次
while True:
    report = analyzer.analyze(wait_time=0)
    if report.overall_score < 60:
        print("⚠️ 设计需要改进！")
    time.sleep(300)
```

## 命令行参数

```
usage: auto_analyzer.py [-h] [--pcb PCB] [--auto-fix] [--wait WAIT] [--output OUTPUT]

KiCad自动截图分析工具

可选参数:
  -h, --help       显示帮助信息
  --pcb PCB        PCB文件路径（可选）
  --auto-fix       自动修复可修复的问题
  --wait WAIT      截图前等待时间（秒），默认2秒
  --output OUTPUT  输出目录，默认./analysis_reports
```

## 常见问题

### Q: 截图失败怎么办？

A: 系统会自动尝试多种截图方式，如果都失败会提示安装依赖：
```bash
pip install pillow mss pyautogui
```

### Q: 如何确保截图的是KiCad窗口？

A: 运行命令后，在倒计时结束前确保KiCad窗口是可见的（不要最小化）。

### Q: 分析结果不准确？

A: 当前版本使用启发式规则分析，建议同时提供PCB文件路径以获得更准确的分析：
```bash
python -m scripts.vision.auto_analyzer --pcb ./your_design.kicad_pcb
```

### Q: 支持Mac/Linux吗？

A: 支持！截图功能跨平台，但窗口检测在Mac/Linux上可能有限制。

## 技术架构

```
scripts/vision/
├── __init__.py          # 模块入口
├── auto_analyzer.py     # 主分析器
└── README.md            # 本文档

核心组件:
- ScreenshotCapture: 多后端截图器
- KiCadWindowDetector: KiCad窗口检测
- SimpleImageAnalyzer: 基础图像分析
- DesignAdvisor: 设计建议生成器
```

## 扩展开发

### 添加新的截图后端

```python
class ScreenshotCapture:
    def _capture_with_my_backend(self, file_path: str) -> ScreenshotResult:
        # 你的截图实现
        return ScreenshotResult(
            success=True,
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            backend_used="my_backend"
        )
```

### 添加新的设计规则

```python
# 在 DesignAdvisor._load_common_issues() 中添加
"my_rule": {
    "type": "我的规则",
    "severity": "warning",
    "description": "描述",
    "suggestion": "建议",
    "auto_fixable": False,
}
```

## 后续改进计划

- [ ] 集成AI视觉模型进行深度分析
- [ ] 支持自动鼠标点击修复
- [ ] 生成可视化报告（HTML）
- [ ] 集成到KiCad插件
- [ ] 支持原理图分析

## 许可证

MIT License
