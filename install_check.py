#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KiCad Auto-Design Skill - 安装验证脚本

在首次使用前运行此脚本检查环境
"""

import sys
import os


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python版本需要3.8+, 当前: {version.major}.{version.minor}")
        return False


def check_dependencies():
    """检查依赖"""
    print("\n检查依赖模块...")

    required = [
        ("dataclasses", "dataclasses"),
        ("typing", "typing"),
    ]

    optional = [
        ("pcbnew", "KiCad Python API (仅在KiCad内可用)"),
    ]

    all_ok = True

    for module, name in required:
        try:
            __import__(module)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [FAIL] {name} - 需要安装")
            all_ok = False

    print("\n可选模块:")
    for module, name in optional:
        try:
            __import__(module)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [INFO] {name} - 未安装（仅影响KiCad集成模式）")

    return all_ok


def check_skill_modules():
    """检查skill模块"""
    print("\n检查skill模块...")

    # 添加当前目录到路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    modules = [
        ("scripts.generators", "生成器模块"),
        ("scripts.output_manager", "输出管理器"),
        ("scripts.kicad_integration", "KiCad集成"),
        ("scripts.power_supply_designer", "电源设计器"),
    ]

    all_ok = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"  [OK] {name}: {module}")
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            all_ok = False

    return all_ok


def test_file_generation():
    """测试文件生成"""
    print("\n测试文件生成...")

    try:
        from scripts.generators import SchematicFileGeneratorV2, SymbolLibrary

        # 创建简单原理图
        sch = SchematicFileGeneratorV2()
        sch.set_page_properties(297, 210, "Test")

        # 添加一个电阻
        r = SymbolLibrary.create_resistor("R1", "1k", (50, 100))
        sch.add_symbol(r)

        print("  [OK] 原理图生成测试通过")
        return True

    except Exception as e:
        print(f"  [FAIL] 文件生成测试失败: {e}")
        return False


def check_output_directory():
    """检查输出目录"""
    print("\n检查输出目录...")

    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "output-result"
    )

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"  [OK] 创建输出目录: {output_dir}")
        except Exception as e:
            print(f"  [FAIL] 无法创建输出目录: {e}")
            return False
    else:
        print(f"  [OK] 输出目录存在: {output_dir}")

    # 测试写入权限
    test_file = os.path.join(output_dir, ".test_write")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("  [OK] 输出目录可写入")
        return True
    except Exception as e:
        print(f"  [FAIL] 输出目录无法写入: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("KiCad Auto-Design Skill - 安装验证")
    print("=" * 60)

    results = []

    # 检查Python版本
    results.append(("Python版本", check_python_version()))

    # 检查依赖
    results.append(("依赖模块", check_dependencies()))

    # 检查skill模块
    results.append(("Skill模块", check_skill_modules()))

    # 测试文件生成
    results.append(("文件生成", test_file_generation()))

    # 检查输出目录
    results.append(("输出目录", check_output_directory()))

    # 总结
    print("\n" + "=" * 60)
    print("验证结果总结")
    print("=" * 60)

    for name, result in results:
        status = "通过" if result else "失败"
        print(f"  {name}: {status}")

    all_passed = all(r for _, r in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] 所有检查通过！")
        print("\n可以使用以下命令生成设计:")
        print("  python create_power_supply_v6.py")
        print("\n或在KiCad中运行:")
        print("  from scripts.run_kicad_skill import run_in_kicad")
        print("  run_in_kicad()")
    else:
        print("[WARNING] 部分检查未通过")
        print("请修复上述问题后再使用")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
