#!/usr/bin/env python3
"""
安装KiCad自动截图分析系统的依赖

使用方法:
    python install_vision_deps.py
"""

import subprocess
import sys


def install_package(package):
    """安装单个包"""
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {package} 安装失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("KiCad自动截图分析系统 - 依赖安装")
    print("=" * 70)

    # 必需的依赖
    required_deps = [
        "pillow",  # 图像处理
        "mss",  # 高性能截图
        "pyautogui",  # GUI自动化
        "psutil",  # 进程管理
    ]

    # Windows特有的依赖
    windows_deps = [
        "pywin32",  # Windows API访问
    ]

    print("\n安装必需的依赖...")
    success_count = 0
    for dep in required_deps:
        if install_package(dep):
            success_count += 1

    # 检测Windows并安装Windows特有依赖
    if sys.platform == "win32":
        print("\n检测到Windows系统，安装Windows特有依赖...")
        for dep in windows_deps:
            if install_package(dep):
                success_count += 1

    print("\n" + "=" * 70)
    print(
        f"安装完成: {success_count}/{len(required_deps) + (len(windows_deps) if sys.platform == 'win32' else 0)} 个包"
    )
    print("=" * 70)

    if success_count > 0:
        print("\n✅ 可以开始使用自动截图分析系统了！")
        print("\n使用方法:")
        print("  python -m scripts.vision.auto_analyzer")
    else:
        print("\n⚠️ 没有成功安装任何包，请检查网络连接")

    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    exit(main())
