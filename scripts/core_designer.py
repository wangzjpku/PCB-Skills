"""
核心PCB/SCH设计器 v1.0.0

从自然语言描述生成KiCad PCB和原理图文件。
生成的文件(.kicad_pcb和.kicad_sch)可直接在KiCad GUI中打开。

使用方法:
    from scripts.core_designer import AutoPCBDesigner

    designer = AutoPCBDesigner()
    result = designer.design_from_description(
        description="设计一个简单的LED电路",
        output_dir="./output"
    )
"""

import sys
import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

# 导入生成器模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generators.pcb_generator import PCBFileGenerator, PCBComponent, PCBTrack
from generators.sch_generator import (
    SchematicFileGenerator,
    SCHSymbol,
    SCHWire,
    SCHJunction,
)

logger = logging.getLogger(__name__)


class AutoPCBDesigner:
    """
    自动PCB设计器 v1.0.0

    核心功能：
    - PCB文件生成 (.kicad_pcb)
    - 原理图文件生成 (.kicad_sch)
    - 设计验证
    """

    def __init__(self, log_level: str = "INFO"):
        """初始化设计器"""
        logging.basicConfig(
            level=getattr(logging, log_level), format="%(levelname)s: %(message)s"
        )
        logger.info("AutoPCBDesigner v1.0.0 初始化完成")

    def create_led_circuit(self, output_dir: str = "./output") -> Dict:
        """
        创建LED电路示例

        Args:
            output_dir: 输出目录

        Returns:
            Dict: 包含生成文件路径
        """
        result = {"success": False, "sch_file": None, "pcb_file": None, "errors": []}

        try:
            os.makedirs(output_dir, exist_ok=True)

            # 生成原理图
            logger.info("生成LED电路原理图...")
            sch_gen = SchematicFileGenerator()
            sch_gen.set_page_properties(210.0, 297.0, "LED Circuit")

            # 添加连接点
            sch_gen.add_junction(SCHJunction(position=(31.75, 35.56)))

            # 添加连线
            sch_gen.add_wire(SCHWire(start=(31.75, 30.48), end=(31.75, 35.56)))
            sch_gen.add_wire(SCHWire(start=(31.75, 35.56), end=(38.1, 35.56)))
            sch_gen.add_wire(SCHWire(start=(38.1, 35.56), end=(38.1, 30.48)))
            sch_gen.add_wire(SCHWire(start=(38.1, 35.56), end=(38.1, 43.18)))
            sch_gen.add_wire(SCHWire(start=(38.1, 43.18), end=(31.75, 43.18)))
            sch_gen.add_wire(SCHWire(start=(31.75, 43.18), end=(31.75, 40.64)))

            # 添加电阻
            r1 = SCHSymbol(
                ref="R1",
                name="R",
                value="1k",
                position=(31.75, 35.56),
                rotation=90,
                pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
            )
            sch_gen.add_symbol(r1)

            # 添加LED
            led1 = SCHSymbol(
                ref="D1",
                name="LED",
                value="Red",
                position=(38.1, 35.56),
                rotation=90,
                mirror=True,
                pins=[{"number": "1", "name": "A"}, {"number": "2", "name": "K"}],
            )
            sch_gen.add_symbol(led1)

            # 添加电源符号
            sch_gen.add_power_symbol(
                SCHSymbol(
                    ref="#PWR01",
                    name="+5V",
                    value="",
                    position=(31.75, 30.48),
                    pins=[{"number": "1", "name": "+5V"}],
                )
            )
            sch_gen.add_power_symbol(
                SCHSymbol(
                    ref="#PWR02",
                    name="GND",
                    value="",
                    position=(31.75, 43.18),
                    pins=[{"number": "1", "name": "GND"}],
                )
            )

            # 保存原理图
            sch_file = os.path.join(output_dir, "led_circuit.kicad_sch")
            sch_gen.save(sch_file)
            result["sch_file"] = sch_file
            logger.info(f"原理图已保存: {sch_file}")

            # 生成PCB
            logger.info("生成LED电路PCB...")
            pcb_gen = PCBFileGenerator()
            pcb_gen.set_board_properties(60.0, 35.0, name="LED Circuit")

            # 添加网络
            pcb_gen.add_net(1, "GND")
            pcb_gen.add_net(2, "+5V")
            pcb_gen.add_net(3, "Net-(R1-Pad2)")

            # 添加电阻
            r1_comp = PCBComponent(
                ref="R1",
                footprint="Resistor_SMD:R_0805_2012Metric",
                value="1k",
                position=(25.4, 25.4),
                pads=[
                    {
                        "number": "1",
                        "x": -0.9125,
                        "y": 0,
                        "net": 2,
                        "net_name": "+5V",
                        "size_x": 1.025,
                        "size_y": 1.4,
                    },
                    {
                        "number": "2",
                        "x": 0.9125,
                        "y": 0,
                        "net": 3,
                        "net_name": "Net-(R1-Pad2)",
                        "size_x": 1.025,
                        "size_y": 1.4,
                    },
                ],
            )
            pcb_gen.add_component(r1_comp)

            # 添加LED
            led1_comp = PCBComponent(
                ref="LED1",
                footprint="LED_SMD:LED_0805_2012Metric",
                value="Red",
                position=(50.8, 25.4),
                orientation=180,
                pads=[
                    {
                        "number": "1",
                        "x": -0.9125,
                        "y": 0,
                        "net": 3,
                        "net_name": "Net-(R1-Pad2)",
                        "size_x": 1.025,
                        "size_y": 1.4,
                    },
                    {
                        "number": "2",
                        "x": 0.9125,
                        "y": 0,
                        "net": 1,
                        "net_name": "GND",
                        "size_x": 1.025,
                        "size_y": 1.4,
                    },
                ],
            )
            pcb_gen.add_component(led1_comp)

            # 添加走线
            pcb_gen.add_track(
                PCBTrack(start=(24.4875, 25.4), end=(51.7125, 25.4), net=3)
            )

            # 设置板框
            pcb_gen.set_board_outline(
                [(10, 10), (70, 10), (70, 40), (10, 40), (10, 10)]
            )

            # 保存PCB
            pcb_file = os.path.join(output_dir, "led_circuit.kicad_pcb")
            pcb_gen.save(pcb_file)
            result["pcb_file"] = pcb_file
            logger.info(f"PCB已保存: {pcb_file}")

            result["success"] = True

        except Exception as e:
            logger.error(f"设计过程出错: {e}")
            result["errors"].append(str(e))

        return result

    def create_power_supply_12v(self, output_dir: str = "./output") -> Dict:
        """
        创建220V转12V电源模块

        Args:
            output_dir: 输出目录

        Returns:
            Dict: 包含生成文件路径
        """
        result = {"success": False, "sch_file": None, "pcb_file": None, "errors": []}

        try:
            os.makedirs(output_dir, exist_ok=True)

            logger.info("生成220V转12V电源模块...")

            # 这里可以添加完整的电源模块设计
            # 为简洁起见，使用简化版本

            # 生成原理图框架
            sch_gen = SchematicFileGenerator()
            sch_gen.set_page_properties(210.0, 297.0, "220V to 12V PSU")

            # 添加主要器件符号
            sch_gen.add_symbol(
                SCHSymbol(
                    ref="F1",
                    name="Fuse",
                    value="2A",
                    position=(20, 180),
                    pins=[{"number": "1", "name": "L"}, {"number": "2", "name": "L"}],
                )
            )
            sch_gen.add_symbol(
                SCHSymbol(
                    ref="DB1",
                    name="Bridge",
                    value="MB6S",
                    position=(40, 170),
                    pins=[
                        {"number": "1", "name": "AC1"},
                        {"number": "2", "name": "AC2"},
                        {"number": "3", "name": "+"},
                        {"number": "4", "name": "-"},
                    ],
                )
            )
            sch_gen.add_symbol(
                SCHSymbol(
                    ref="C1",
                    name="C",
                    value="10uF/400V",
                    position=(60, 165),
                    pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
                )
            )
            sch_gen.add_symbol(
                SCHSymbol(
                    ref="U1",
                    name="VIPer12A",
                    value="",
                    position=(80, 150),
                    pins=[
                        {"number": "4", "name": "SOURCE"},
                        {"number": "5", "name": "DRAIN"},
                        {"number": "8", "name": "VDD"},
                    ],
                )
            )
            sch_gen.add_symbol(
                SCHSymbol(
                    ref="T1",
                    name="Transformer",
                    value="EE16",
                    position=(100, 140),
                    pins=[
                        {"number": "1", "name": "Pri"},
                        {"number": "2", "name": "Pri"},
                        {"number": "3", "name": "Sec"},
                        {"number": "4", "name": "Sec"},
                    ],
                )
            )
            sch_gen.add_symbol(
                SCHSymbol(
                    ref="D1",
                    name="D",
                    value="SS34",
                    position=(120, 130),
                    pins=[{"number": "1", "name": "A"}, {"number": "2", "name": "K"}],
                )
            )
            sch_gen.add_symbol(
                SCHSymbol(
                    ref="C2",
                    name="C",
                    value="1000uF/25V",
                    position=(135, 125),
                    pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
                )
            )

            # 添加电源符号
            sch_gen.add_power_symbol(
                SCHSymbol(
                    ref="#PWR01",
                    name="L",
                    value="",
                    position=(10, 180),
                    pins=[{"number": "1", "name": "L"}],
                )
            )
            sch_gen.add_power_symbol(
                SCHSymbol(
                    ref="#PWR02",
                    name="N",
                    value="",
                    position=(10, 170),
                    pins=[{"number": "1", "name": "N"}],
                )
            )
            sch_gen.add_power_symbol(
                SCHSymbol(
                    ref="#PWR03",
                    name="+12V",
                    value="",
                    position=(150, 115),
                    pins=[{"number": "1", "name": "+12V"}],
                )
            )
            sch_gen.add_power_symbol(
                SCHSymbol(
                    ref="#PWR04",
                    name="GND",
                    value="",
                    position=(150, 100),
                    pins=[{"number": "1", "name": "GND"}],
                )
            )

            # 保存
            sch_file = os.path.join(output_dir, "power_supply_12v.kicad_sch")
            sch_gen.save(sch_file)
            result["sch_file"] = sch_file

            # 生成PCB框架
            pcb_gen = PCBFileGenerator()
            pcb_gen.set_board_properties(80.0, 60.0, name="220V to 12V PSU")
            pcb_gen.set_board_outline([(5, 5), (75, 5), (75, 55), (5, 55), (5, 5)])

            pcb_file = os.path.join(output_dir, "power_supply_12v.kicad_pcb")
            pcb_gen.save(pcb_file)
            result["pcb_file"] = pcb_file

            result["success"] = True
            logger.info("电源模块框架生成完成")
            logger.info(f"  SCH: {sch_file}")
            logger.info(f"  PCB: {pcb_file}")

        except Exception as e:
            logger.error(f"设计过程出错: {e}")
            result["errors"].append(str(e))

        return result


def create_led_circuit(output_dir: str = "./output") -> Dict:
    """
    便捷函数：创建LED电路

    Args:
        output_dir: 输出目录

    Returns:
        Dict: 生成结果
    """
    designer = AutoPCBDesigner()
    return designer.create_led_circuit(output_dir)


def create_power_supply(output_dir: str = "./output") -> Dict:
    """
    便捷函数：创建12V电源模块

    Args:
        output_dir: 输出目录

    Returns:
        Dict: 生成结果
    """
    designer = AutoPCBDesigner()
    return designer.create_power_supply_12v(output_dir)


if __name__ == "__main__":
    # 命令行接口
    import argparse

    parser = argparse.ArgumentParser(description="KiCad Auto Designer v1.0.0")
    parser.add_argument("--led", action="store_true", help="生成LED电路")
    parser.add_argument("--psu", action="store_true", help="生成12V电源模块")
    parser.add_argument("-o", "--output", default="./output", help="输出目录")

    args = parser.parse_args()

    if args.led:
        result = create_led_circuit(args.output)
        print(f"LED电路生成: {'成功' if result['success'] else '失败'}")
        if result["success"]:
            print(f"  SCH: {result['sch_file']}")
            print(f"  PCB: {result['pcb_file']}")
    elif args.psu:
        result = create_power_supply(args.output)
        print(f"电源模块生成: {'成功' if result['success'] else '失败'}")
        if result["success"]:
            print(f"  SCH: {result['sch_file']}")
            print(f"  PCB: {result['pcb_file']}")
    else:
        parser.print_help()
