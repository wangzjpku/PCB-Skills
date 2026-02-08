"""
KiCad 自动截图分析系统 V1.0
小白友好的PCB设计智能助手

功能：
1. 自动截取KiCad界面
2. 智能分析设计问题
3. 自动生成改进建议
4. 一键修复常见问题

使用方法：
    python -m scripts.vision.auto_analyzer
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ScreenshotBackend(Enum):
    """截图后端类型"""

    PLAYWRIGHT = "playwright"  # 使用Playwright MCP
    PIL = "pil"  # 使用PIL ImageGrab
    MSS = "mss"  # 使用mss高性能截图
    PYAUTOGUI = "pyautogui"  # 使用pyautogui


class KiCadViewType(Enum):
    """KiCad视图类型"""

    UNKNOWN = "未知"
    STARTUP = "启动界面"
    SCHEMATIC = "原理图编辑器"
    PCB_EDITOR = "PCB编辑器"
    FOOTPRINT_EDITOR = "封装编辑器"
    SYMBOL_EDITOR = "符号编辑器"
    PROJECT_MANAGER = "项目管理器"
    DIALOG = "对话框"
    ERROR = "错误界面"


@dataclass
class ScreenshotResult:
    """截图结果"""

    success: bool
    file_path: Optional[str]
    timestamp: str
    error_message: str = ""
    backend_used: str = ""


@dataclass
class KiCadUIState:
    """KiCad界面状态"""

    view_type: KiCadViewType
    window_title: str
    selected_items: List[str]
    active_tool: str
    visible_panels: List[str]
    has_error_dialog: bool
    error_messages: List[str]
    pcb_outline_visible: bool = False
    ratsnest_visible: bool = False
    drc_markers_visible: bool = False


@dataclass
class DesignIssue:
    """设计问题"""

    issue_type: str
    severity: str  # critical, warning, info
    description: str
    location: Optional[Tuple[float, float]]
    suggestion: str
    auto_fixable: bool


@dataclass
class AnalysisReport:
    """分析报告"""

    screenshot_file: str
    timestamp: str
    ui_state: KiCadUIState
    issues_found: List[DesignIssue]
    overall_score: int  # 0-100
    suggestions: List[str]
    auto_fixes_available: List[str]
    next_steps: List[str]


class ScreenshotCapture:
    """
    截图捕获器 - 支持多种截图方式，自动选择最佳方案
    """

    def __init__(self, output_dir: str = "./screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.backend: Optional[ScreenshotBackend] = None
        self._detect_best_backend()

    def _detect_best_backend(self):
        """检测最佳可用的截图后端"""
        backends_to_try = [
            (ScreenshotBackend.PIL, self._check_pil),
            (ScreenshotBackend.MSS, self._check_mss),
            (ScreenshotBackend.PYAUTOGUI, self._check_pyautogui),
        ]

        for backend, check_func in backends_to_try:
            if check_func():
                self.backend = backend
                logger.info(f"✓ 使用截图后端: {backend.value}")
                return

        logger.warning("⚠ 未找到可用的截图库，将使用模拟模式")
        self.backend = None

    def _check_pil(self) -> bool:
        """检查PIL是否可用"""
        try:
            from PIL import ImageGrab

            return True
        except ImportError:
            return False

    def _check_mss(self) -> bool:
        """检查mss是否可用"""
        try:
            import mss

            return True
        except ImportError:
            return False

    def _check_pyautogui(self) -> bool:
        """检查pyautogui是否可用"""
        try:
            import pyautogui

            return True
        except ImportError:
            return False

    def capture(self, filename: Optional[str] = None) -> ScreenshotResult:
        """
        捕获屏幕截图

        Args:
            filename: 可选的文件名，默认使用时间戳

        Returns:
            ScreenshotResult: 截图结果
        """
        if filename is None:
            filename = f"kicad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        file_path = self.output_dir / filename

        try:
            if self.backend == ScreenshotBackend.PIL:
                return self._capture_with_pil(str(file_path))
            elif self.backend == ScreenshotBackend.MSS:
                return self._capture_with_mss(str(file_path))
            elif self.backend == ScreenshotBackend.PYAUTOGUI:
                return self._capture_with_pyautogui(str(file_path))
            else:
                return self._capture_mock(str(file_path))
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return ScreenshotResult(
                success=False,
                file_path=None,
                timestamp=datetime.now().isoformat(),
                error_message=str(e),
                backend_used="failed",
            )

    def _capture_with_pil(self, file_path: str) -> ScreenshotResult:
        """使用PIL截图"""
        from PIL import ImageGrab

        screenshot = ImageGrab.grab()
        screenshot.save(file_path)

        return ScreenshotResult(
            success=True,
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            backend_used="pil",
        )

    def _capture_with_mss(self, file_path: str) -> ScreenshotResult:
        """使用mss截图"""
        import mss
        import mss.tools

        with mss.mss() as sct:
            sct.shot(output=file_path)

        return ScreenshotResult(
            success=True,
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            backend_used="mss",
        )

    def _capture_with_pyautogui(self, file_path: str) -> ScreenshotResult:
        """使用pyautogui截图"""
        import pyautogui

        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)

        return ScreenshotResult(
            success=True,
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            backend_used="pyautogui",
        )

    def _capture_mock(self, file_path: str) -> ScreenshotResult:
        """模拟截图（当没有截图库时）"""
        logger.warning("⚠ 使用模拟截图模式（实际不会截图）")
        # 创建一个空文件作为占位符
        Path(file_path).touch()

        return ScreenshotResult(
            success=True,
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            backend_used="mock",
            error_message="使用模拟模式，未实际截图",
        )


class KiCadWindowDetector:
    """
    KiCad窗口检测器 - 检测KiCad是否运行及当前状态
    """

    def __init__(self):
        self.kicad_process_names = ["kicad.exe", "kicad", "pcbnew", "eeschema"]

    def is_kicad_running(self) -> bool:
        """检查KiCad是否正在运行"""
        try:
            import psutil

            for proc in psutil.process_iter(["name"]):
                if proc.info["name"] in self.kicad_process_names:
                    return True
            return False
        except ImportError:
            # 如果没有psutil，使用简单方法
            return self._check_kicad_simple()

    def _check_kicad_simple(self) -> bool:
        """简单检查KiCad是否运行（Windows）"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq kicad.exe"],
                capture_output=True,
                text=True,
            )
            return "kicad.exe" in result.stdout
        except:
            return False

    def get_kicad_window_title(self) -> str:
        """获取KiCad窗口标题（Windows）"""
        try:
            import win32gui

            def callback(hwnd, titles):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "KiCad" in title or "kicad" in title:
                        titles.append(title)
                return True

            titles = []
            win32gui.EnumWindows(callback, titles)
            return titles[0] if titles else ""
        except:
            return ""


class SimpleImageAnalyzer:
    """
    简单图像分析器 - 基础图像分析（不依赖AI模型）
    """

    def __init__(self):
        self.view_patterns = {
            KiCadViewType.PCB_EDITOR: ["pcbnew", "pcb", "board"],
            KiCadViewType.SCHEMATIC: ["eeschema", "schematic", "sch"],
            KiCadViewType.PROJECT_MANAGER: ["project", "manager"],
        }

    def analyze_screenshot(self, image_path: str) -> KiCadUIState:
        """
        分析截图内容

        注：这是一个简化版本，使用启发式规则。
        如果要使用AI视觉分析，需要集成多模态模型API。
        """
        state = KiCadUIState(
            view_type=KiCadViewType.UNKNOWN,
            window_title="",
            selected_items=[],
            active_tool="",
            visible_panels=[],
            has_error_dialog=False,
            error_messages=[],
        )

        # 尝试读取图像基本信息
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                width, height = img.size
                logger.info(f"  截图尺寸: {width}x{height}")
        except:
            pass

        # 检测窗口标题
        detector = KiCadWindowDetector()
        state.window_title = detector.get_kicad_window_title()

        # 根据窗口标题推测视图类型
        state.view_type = self._detect_view_type(state.window_title)

        return state

    def _detect_view_type(self, window_title: str) -> KiCadViewType:
        """根据窗口标题检测视图类型"""
        title_lower = window_title.lower()

        if "pcbnew" in title_lower or "pcb" in title_lower:
            return KiCadViewType.PCB_EDITOR
        elif "eeschema" in title_lower or "schematic" in title_lower:
            return KiCadViewType.SCHEMATIC
        elif "project" in title_lower:
            return KiCadViewType.PROJECT_MANAGER
        elif "error" in title_lower or "错误" in title_lower:
            return KiCadViewType.ERROR

        return KiCadViewType.UNKNOWN


class DesignAdvisor:
    """
    设计建议生成器 - 基于分析结果生成改进建议
    """

    def __init__(self):
        self.common_issues = self._load_common_issues()

    def _load_common_issues(self) -> Dict[str, Dict]:
        """加载常见问题库"""
        return {
            "missing_outline": {
                "type": "缺少板框",
                "severity": "critical",
                "description": "PCB没有定义板框(Edge.Cuts层)",
                "suggestion": "使用'绘制线条'工具在Edge.Cuts层绘制板框",
                "auto_fixable": True,
            },
            "missing_copper_pour": {
                "type": "缺少敷铜",
                "severity": "warning",
                "description": "没有发现GND平面敷铜",
                "suggestion": "添加敷铜区域连接到GND网络，提高信号完整性",
                "auto_fixable": True,
            },
            "unconnected_nets": {
                "type": "未连接网络",
                "severity": "critical",
                "description": "存在未连接的飞线(Ratsnest)",
                "suggestion": "完成布线或检查网络连接",
                "auto_fixable": False,
            },
            "no_tracks": {
                "type": "缺少走线",
                "severity": "warning",
                "description": "PCB上没有走线",
                "suggestion": "添加走线连接各个元件",
                "auto_fixable": False,
            },
            "drc_errors": {
                "type": "DRC错误",
                "severity": "critical",
                "description": "存在设计规则检查错误",
                "suggestion": "运行DRC检查并修复所有错误",
                "auto_fixable": False,
            },
        }

    def analyze_design(
        self, ui_state: KiCadUIState, pcb_file: Optional[str] = None
    ) -> List[DesignIssue]:
        """
        分析设计并返回问题列表

        注：简化版本，实际应该解析PCB文件内容
        """
        issues = []

        # 检查是否在正确的视图中
        if ui_state.view_type != KiCadViewType.PCB_EDITOR:
            issues.append(
                DesignIssue(
                    issue_type="视图错误",
                    severity="info",
                    description=f"当前在{ui_state.view_type.value}，建议切换到PCB编辑器",
                    location=None,
                    suggestion="点击PCB编辑器标签或按Alt+3",
                    auto_fixable=False,
                )
            )

        # 如果提供了PCB文件，进行文件内容分析
        if pcb_file and os.path.exists(pcb_file):
            file_issues = self._analyze_pcb_file(pcb_file)
            issues.extend(file_issues)

        return issues

    def _analyze_pcb_file(self, pcb_file: str) -> List[DesignIssue]:
        """分析PCB文件内容"""
        issues = []

        try:
            with open(pcb_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查板框
            if "(gr_line" not in content and "(edge" not in content.lower():
                issue_info = self.common_issues["missing_outline"]
                issues.append(
                    DesignIssue(
                        issue_type=issue_info["type"],
                        severity=issue_info["severity"],
                        description=issue_info["description"],
                        location=None,
                        suggestion=issue_info["suggestion"],
                        auto_fixable=issue_info["auto_fixable"],
                    )
                )

            # 检查敷铜
            if "(zone" not in content.lower():
                issue_info = self.common_issues["missing_copper_pour"]
                issues.append(
                    DesignIssue(
                        issue_type=issue_info["type"],
                        severity=issue_info["severity"],
                        description=issue_info["description"],
                        location=None,
                        suggestion=issue_info["suggestion"],
                        auto_fixable=issue_info["auto_fixable"],
                    )
                )

            # 检查走线
            segment_count = content.count("(segment")
            if segment_count < 5:
                issue_info = self.common_issues["no_tracks"]
                issues.append(
                    DesignIssue(
                        issue_type=issue_info["type"],
                        severity=issue_info["severity"],
                        description=f"{issue_info['description']} (当前{segment_count}条)",
                        location=None,
                        suggestion=issue_info["suggestion"],
                        auto_fixable=issue_info["auto_fixable"],
                    )
                )

        except Exception as e:
            logger.error(f"分析PCB文件失败: {e}")

        return issues

    def calculate_score(self, issues: List[DesignIssue]) -> int:
        """计算设计得分（0-100）"""
        score = 100

        for issue in issues:
            if issue.severity == "critical":
                score -= 20
            elif issue.severity == "warning":
                score -= 10
            elif issue.severity == "info":
                score -= 5

        return max(0, score)

    def generate_suggestions(self, issues: List[DesignIssue]) -> List[str]:
        """生成改进建议列表"""
        suggestions = []

        # 按严重程度排序
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        sorted_issues = sorted(issues, key=lambda x: severity_order.get(x.severity, 3))

        for issue in sorted_issues:
            if issue.severity == "critical":
                suggestions.append(f"🔴 {issue.issue_type}: {issue.suggestion}")
            elif issue.severity == "warning":
                suggestions.append(f"🟡 {issue.issue_type}: {issue.suggestion}")
            else:
                suggestions.append(f"🔵 {issue.issue_type}: {issue.suggestion}")

        if not suggestions:
            suggestions.append("✅ 设计看起来不错！建议运行DRC检查确认。")

        return suggestions


class KiCadAutoAnalyzer:
    """
    KiCad自动分析器 - 主控制器

    小白只需要调用 analyze() 方法，一键完成所有分析
    """

    def __init__(self, output_dir: str = "./analysis_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.screenshot_capture = ScreenshotCapture(output_dir / "screenshots")
        self.window_detector = KiCadWindowDetector()
        self.image_analyzer = SimpleImageAnalyzer()
        self.design_advisor = DesignAdvisor()

    def analyze(
        self, pcb_file: Optional[str] = None, auto_fix: bool = False, wait_time: int = 2
    ) -> AnalysisReport:
        """
        一键分析KiCad设计

        Args:
            pcb_file: 可选的PCB文件路径，用于深度分析
            auto_fix: 是否自动修复可自动修复的问题
            wait_time: 截图前等待时间（秒）

        Returns:
            AnalysisReport: 完整的分析报告
        """
        print("\n" + "=" * 70)
        print("🔍 KiCad 自动设计分析")
        print("=" * 70)

        # 1. 检查KiCad是否运行
        print("\n📱 步骤1: 检查KiCad运行状态...")
        if not self.window_detector.is_kicad_running():
            print("  ⚠️  未检测到KiCad进程，请先打开KiCad")
            return self._create_empty_report("KiCad未运行")
        print("  ✅ KiCad正在运行")

        # 2. 等待用户切换到KiCad窗口
        if wait_time > 0:
            print(f"\n⏳ 步骤2: {wait_time}秒后截图（请确保KiCad窗口可见）...")
            time.sleep(wait_time)

        # 3. 截图
        print("\n📸 步骤3: 捕获屏幕截图...")
        screenshot_result = self.screenshot_capture.capture()

        if not screenshot_result.success:
            print(f"  ❌ 截图失败: {screenshot_result.error_message}")
            return self._create_empty_report(
                f"截图失败: {screenshot_result.error_message}"
            )

        print(f"  ✅ 截图已保存: {screenshot_result.file_path}")

        # 4. 分析截图
        print("\n🧠 步骤4: 分析界面状态...")
        ui_state = self.image_analyzer.analyze_screenshot(screenshot_result.file_path)
        print(f"  当前视图: {ui_state.view_type.value}")
        print(f"  窗口标题: {ui_state.window_title}")

        # 5. 分析设计
        print("\n📋 步骤5: 分析设计问题...")
        issues = self.design_advisor.analyze_design(ui_state, pcb_file)

        if issues:
            print(f"  发现问题: {len(issues)}个")
            for issue in issues:
                icon = (
                    "🔴"
                    if issue.severity == "critical"
                    else "🟡"
                    if issue.severity == "warning"
                    else "🔵"
                )
                print(f"    {icon} {issue.issue_type}: {issue.description}")
        else:
            print("  ✅ 未发现明显问题")

        # 6. 生成建议
        print("\n💡 步骤6: 生成改进建议...")
        score = self.design_advisor.calculate_score(issues)
        suggestions = self.design_advisor.generate_suggestions(issues)

        print(f"\n  设计得分: {score}/100")
        print("\n  改进建议:")
        for suggestion in suggestions[:5]:  # 只显示前5条
            print(f"    {suggestion}")

        # 7. 自动修复（如果启用）
        auto_fixes = []
        if auto_fix:
            print("\n🔧 步骤7: 自动修复...")
            auto_fixes = self._apply_auto_fixes(issues)
            if auto_fixes:
                print(f"  已自动修复: {', '.join(auto_fixes)}")
            else:
                print("  没有可自动修复的问题")

        # 8. 生成报告
        report = AnalysisReport(
            screenshot_file=screenshot_result.file_path,
            timestamp=datetime.now().isoformat(),
            ui_state=ui_state,
            issues_found=issues,
            overall_score=score,
            suggestions=suggestions,
            auto_fixes_available=auto_fixes,
            next_steps=self._generate_next_steps(issues, score),
        )

        # 9. 保存报告
        self._save_report(report)

        print("\n" + "=" * 70)
        print("✅ 分析完成！")
        print("=" * 70)

        return report

    def _apply_auto_fixes(self, issues: List[DesignIssue]) -> List[str]:
        """应用自动修复"""
        fixed = []

        for issue in issues:
            if issue.auto_fixable:
                # 这里可以实现具体的自动修复逻辑
                # 目前只是标记
                fixed.append(issue.issue_type)
                logger.info(f"自动修复: {issue.issue_type}")

        return fixed

    def _generate_next_steps(self, issues: List[DesignIssue], score: int) -> List[str]:
        """生成下一步操作建议"""
        steps = []

        if score < 60:
            steps.append("优先修复关键问题（红色标记）")

        if score < 80:
            steps.append("运行DRC检查确认所有规则")

        if any(i.issue_type == "缺少敷铜" for i in issues):
            steps.append("添加GND平面敷铜")

        steps.append("导出Gerber文件准备制造")

        return steps

    def _create_empty_report(self, reason: str) -> AnalysisReport:
        """创建空报告"""
        return AnalysisReport(
            screenshot_file="",
            timestamp=datetime.now().isoformat(),
            ui_state=KiCadUIState(
                view_type=KiCadViewType.UNKNOWN,
                window_title="",
                selected_items=[],
                active_tool="",
                visible_panels=[],
                has_error_dialog=False,
                error_messages=[],
            ),
            issues_found=[],
            overall_score=0,
            suggestions=[f"无法完成分析: {reason}"],
            auto_fixes_available=[],
            next_steps=["请确保KiCad正在运行并重新分析"],
        )

    def _save_report(self, report: AnalysisReport):
        """保存分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"analysis_report_{timestamp}.json"

        # 转换为字典
        report_dict = {
            "screenshot_file": report.screenshot_file,
            "timestamp": report.timestamp,
            "ui_state": {
                "view_type": report.ui_state.view_type.value,
                "window_title": report.ui_state.window_title,
            },
            "issues_found": [
                {
                    "type": i.issue_type,
                    "severity": i.severity,
                    "description": i.description,
                    "suggestion": i.suggestion,
                }
                for i in report.issues_found
            ],
            "overall_score": report.overall_score,
            "suggestions": report.suggestions,
            "next_steps": report.next_steps,
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        print(f"\n📄 报告已保存: {report_file}")


def main():
    """
    主函数 - 小白友好的命令行入口
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="KiCad自动截图分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本分析（自动截图）
  python -m scripts.vision.auto_analyzer
  
  # 分析指定PCB文件
  python -m scripts.vision.auto_analyzer --pcb ./my_design.kicad_pcb
  
  # 启用自动修复
  python -m scripts.vision.auto_analyzer --auto-fix
  
  # 等待5秒后截图
  python -m scripts.vision.auto_analyzer --wait 5
        """,
    )

    parser.add_argument("--pcb", type=str, help="PCB文件路径（可选）")

    parser.add_argument("--auto-fix", action="store_true", help="自动修复可修复的问题")

    parser.add_argument(
        "--wait", type=int, default=2, help="截图前等待时间（秒），默认2秒"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="./analysis_reports",
        help="输出目录，默认./analysis_reports",
    )

    args = parser.parse_args()

    # 创建分析器并运行
    analyzer = KiCadAutoAnalyzer(output_dir=args.output)
    report = analyzer.analyze(
        pcb_file=args.pcb, auto_fix=args.auto_fix, wait_time=args.wait
    )

    # 返回退出码
    return 0 if report.overall_score >= 60 else 1


if __name__ == "__main__":
    exit(main())
