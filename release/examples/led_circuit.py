"""
LED电路生成示例

使用AutoPCBDesigner生成简单LED电路。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core_designer import design_from_natural_language


def main():
    """示例：生成LED电路"""
    
    description = """
    设计一个简单的LED电路：
    - 1个红色LED
    - 1个1kΩ电阻
    - 5V供电
    - 单层PCB
    """
    
    result = design_from_natural_language(
        description.strip(),
        output_dir="./output",
        log_level="INFO"
    )
    
    print("\n" + "="*50)
    print("LED电路生成完成")
    print("="*50)
    print(f"\n成功: {result['success']}")
    
    if result['success']:
        print(f"原理图: {result.get('sch_file', 'N/A')}")
        print(f"PCB文件: {result.get('pcb_file', 'N/A')}")
        print("\n✓ 文件已生成，可用KiCad打开")
    else:
        print(f"\n错误: {', '.join(result.get('errors', []))}")
    
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
