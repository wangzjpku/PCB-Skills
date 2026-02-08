#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动截图分析示例
小白也能用的简单示例

使用方法:
    python examples/vision_analyzer_demo.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vision.auto_analyzer import KiCadAutoAnalyzer


def main():
    """主函数 - 最简单的使用示例"""
    print("=" * 70)
    print("🤖 KiCad自动截图分析 - 示例")
    print("=" * 70)
    print("\n这个示例会:")
    print("1. 检测KiCad是否运行")
    print("2. 自动截图")
    print("3. 分析设计问题")
    print("4. 给出改进建议")

    print("\n" + "-" * 70)
    print("请确保:")
    print("  ✓ KiCad已经打开")
    print("  ✓ 有项目正在编辑")
    print("  ✓ KiCad窗口可见（不要最小化）")
    print("-" * 70)

    input("\n准备好后按回车键开始分析...")

    # 创建分析器
    analyzer = KiCadAutoAnalyzer(output_dir="./vision_demo_output")

    # 运行分析（等待3秒让用户切换窗口）
    print("\n⏳ 3秒后开始截图...")
    report = analyzer.analyze(wait_time=3)

    # 显示结果摘要
    print("\n" + "=" * 70)
    print("📊 分析结果摘要")
    print("=" * 70)
    print(f"\n设计得分: {report.overall_score}/100")
    print(f"发现问题: {len(report.issues_found)}个")
    print(f"截图文件: {report.screenshot_file}")

    # 显示建议
    if report.suggestions:
        print("\n💡 改进建议:")
        for i, suggestion in enumerate(report.suggestions[:5], 1):
            print(f"  {i}. {suggestion}")

    # 显示下一步
    if report.next_steps:
        print("\n📋 建议的下一步:")
        for step in report.next_steps:
            print(f"  • {step}")

    print("\n" + "=" * 70)
    print("✅ 分析完成！")
    print("=" * 70)
    print(f"\n详细报告保存在: {analyzer.output_dir}")

    return 0


if __name__ == "__main__":
    exit(main())
