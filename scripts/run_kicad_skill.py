#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KiCad Skill 启动器

在KiCad环境中启动自动设计功能
使用方法:
1. 在KiCad的Tools -> Scripting Console中运行
2. 或者作为Action Plugin安装
"""

import sys
import os

# 添加脚本路径
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)


def run_in_kicad():
    """在KiCad环境中运行"""
    try:
        from kicad_integration import KiCadAPI
        from power_supply_designer import PowerSupplyDesigner

        print("=" * 60)
        print("KiCad Auto-Design Skill")
        print("220V转12V电源自动设计")
        print("=" * 60)

        # 创建API
        api = KiCadAPI()

        if not api.board:
            print("\n错误: 请先打开一个PCB文件!")
            print("操作步骤:")
            print("1. 在KiCad中打开或创建一个PCB项目")
            print("2. 确保PCB编辑器已打开")
            print("3. 然后再次运行此脚本")
            return False

        # 创建设计器
        designer = PowerSupplyDesigner(api)

        # 执行设计
        result = designer.create_220v_to_12v_design()

        # 优化
        print("\n优化检查...")
        opt_result = designer.optimize_layout()
        for detail in opt_result.get("details", []):
            print(f"  {detail}")

        print("\n" + "=" * 60)
        print("设计完成! 请检查PCB布局。")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback

        traceback.print_exc()
        return False


def generate_standalone():
    """生成独立文件（不依赖KiCad）"""
    print("生成KiCad文件...")

    # 使用文件生成器
    sys.path.insert(0, os.path.dirname(script_dir))
    from create_power_supply_v6 import create_power_supply_v6

    result = create_power_supply_v6()

    print(f"\n文件已生成到: {result['output_dir']}")
    print("请在KiCad中打开这些文件查看设计。")

    return True


def main():
    """主函数"""
    # 检测是否在KiCad环境中
    try:
        import pcbnew

        in_kicad = True
    except ImportError:
        in_kicad = False

    if in_kicad:
        print("检测到KiCad环境，启动集成模式...")
        run_in_kicad()
    else:
        print("未检测到KiCad，生成独立文件...")
        generate_standalone()


if __name__ == "__main__":
    main()
