"""
ESP32开发板生成示例

使用AutoPCBDesigner生成ESP32开发板。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core_designer import design_from_natural_language


def main():
    """示例：生成ESP32开发板"""
    
    # 自然语言描述
    description = """
    设计一个ESP32开发板：
    - 使用ESP32-WROOM-32芯片
    - 包含USB转串口（CP2102）
    - 3.3V稳压电路（AMS1117）
    - 板载LED（GPIO2）
    - 4个用户LED
    - 2个按键
    - 面包板兼容引脚排列
    - 4层板设计
    """
    
    # 生成设计
    result = design_from_natural_language(
        description.strip(),
        output_dir="./output",
        log_level="INFO"
    )
    
    # 打印结果
    print("\n" + "="*50)
    print("ESP32开发板生成完成")
    print("="*50)
    print(f"\n成功: {result['success']}")
    
    if result['success']:
        print(f"原理图: {result.get('sch_file', 'N/A')}")
        print(f"PCB文件: {result.get('pcb_file', 'N/A')}")
        
        report = result.get('report', '')
        if report:
            print(report)
            
        print("\n✓ 生成的文件可以直接用KiCad GUI打开")
    else:
        print(f"\n错误: {'、'.join(result.get('errors', []))}")
    
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
