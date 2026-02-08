"""
KiCad Vision 模块 - 自动截图和分析系统

提供KiCad界面自动截图、分析和改进建议功能。

主要功能:
- 自动截图（支持多种后端）
- 界面状态检测
- 设计问题分析
- 自动生成改进建议

使用:
    from scripts.vision.auto_analyzer import KiCadAutoAnalyzer

    analyzer = KiCadAutoAnalyzer()
    report = analyzer.analyze()
"""

from .auto_analyzer import (
    KiCadAutoAnalyzer,
    ScreenshotCapture,
    KiCadWindowDetector,
    SimpleImageAnalyzer,
    DesignAdvisor,
    AnalysisReport,
    DesignIssue,
    KiCadUIState,
)

__all__ = [
    "KiCadAutoAnalyzer",
    "ScreenshotCapture",
    "KiCadWindowDetector",
    "SimpleImageAnalyzer",
    "DesignAdvisor",
    "AnalysisReport",
    "DesignIssue",
    "KiCadUIState",
]
