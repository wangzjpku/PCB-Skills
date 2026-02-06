#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
220V转12V电源模块设计
使用VIPer22A反激式开关电源方案
输出: 12V/1A (12W)
"""

import sys
import os

# 添加脚本路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.generators.sch_generator import (
    SchematicFileGenerator,
    SCHSymbol,
    SCHWire,
    SCHJunction,
)
from scripts.generators.pcb_generator import (
    PCBFileGenerator,
    PCBComponent,
    PCBTrack,
)


def create_power_supply_220v_to_12v(output_dir: str = "./output_power_supply"):
    """
    创建完整的220V转12V电源模块
    使用VIPer22A反激式开关电源方案
    """
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("220V to 12V Power Supply Module Design")
    print("Using VIPer22A Flyback Converter")
    print("Output: 12V/1A (12W)")
    print("=" * 70)

    # ==================== 生成原理图 ====================
    print("\n[1/2] Generating Schematic...")
    sch_gen = SchematicFileGenerator()
    sch_gen.set_page_properties(297.0, 210.0, "220V to 12V PSU - VIPer22A")

    y_base = 50.0
    x_input = 30.0
    x_rect = 60.0
    x_filter = 90.0
    x_viper = 130.0
    x_transformer = 170.0
    x_output = 220.0
    x_feedback = 180.0

    # AC输入部分
    # AC输入端子
    ac_input = SCHSymbol(
        ref="J1",
        name="Screw_Terminal",
        value="AC_IN",
        position=(x_input, y_base + 20),
        pins=[{"number": "1", "name": "L"}, {"number": "2", "name": "N"}],
    )
    sch_gen.add_symbol(ac_input)

    # 保险丝 F1
    fuse_f1 = SCHSymbol(
        ref="F1",
        name="Fuse",
        value="500mA/250V",
        position=(x_input + 15, y_base + 35),
        rotation=90,
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(fuse_f1)

    # 压敏电阻 RV1
    varistor_rv1 = SCHSymbol(
        ref="RV1",
        name="Varistor",
        value="10D561K",
        position=(x_input + 15, y_base + 5),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(varistor_rv1)

    # X电容 CX1
    x_cap_cx1 = SCHSymbol(
        ref="CX1",
        name="C_X2",
        value="0.1µF/275V",
        position=(x_input + 25, y_base + 20),
        rotation=90,
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(x_cap_cx1)

    # 共模电感 L1
    cm_choke_l1 = SCHSymbol(
        ref="L1",
        name="Common_Mode_Choke",
        value="10mH",
        position=(x_rect - 5, y_base + 20),
        pins=[
            {"number": "1", "name": "1"},
            {"number": "2", "name": "2"},
            {"number": "3", "name": "3"},
            {"number": "4", "name": "4"},
        ],
    )
    sch_gen.add_symbol(cm_choke_l1)

    # 桥式整流器
    bridge_rect = SCHSymbol(
        ref="BR1",
        name="Bridge_Rectifier",
        value="MB6S",
        position=(x_rect + 15, y_base + 20),
        pins=[
            {"number": "1", "name": "+"},
            {"number": "2", "name": "~"},
            {"number": "3", "name": "-"},
            {"number": "4", "name": "~"},
        ],
    )
    sch_gen.add_symbol(bridge_rect)

    # 高压滤波电容 C1
    hv_cap_c1 = SCHSymbol(
        ref="C1",
        name="C_Electrolytic",
        value="22µF/400V",
        position=(x_filter, y_base + 35),
        rotation=90,
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(hv_cap_c1)

    # VIPer22A 主控IC
    viper22a = SCHSymbol(
        ref="U1",
        name="VIPer22A",
        value="VIPer22A",
        position=(x_viper, y_base + 20),
        pins=[
            {"number": "1", "name": "SOURCE"},
            {"number": "2", "name": "SOURCE"},
            {"number": "3", "name": "FB"},
            {"number": "4", "name": "VDD"},
            {"number": "5", "name": "DRAIN"},
            {"number": "6", "name": "DRAIN"},
            {"number": "7", "name": "DRAIN"},
            {"number": "8", "name": "DRAIN"},
        ],
    )
    sch_gen.add_symbol(viper22a)

    # VDD电容 C2
    vdd_cap = SCHSymbol(
        ref="C2",
        name="C_Ceramic",
        value="10µF/25V",
        position=(x_viper - 10, y_base + 5),
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(vdd_cap)

    # 启动电阻 R1
    r1_startup = SCHSymbol(
        ref="R1",
        name="R",
        value="100k",
        position=(x_viper - 15, y_base + 35),
        rotation=90,
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(r1_startup)

    # 变压器 T1
    transformer = SCHSymbol(
        ref="T1",
        name="Transformer",
        value="EE-25 (140T:14T:16T)",
        position=(x_transformer, y_base + 20),
        pins=[
            {"number": "1", "name": "PRI+"},
            {"number": "2", "name": "PRI-"},
            {"number": "3", "name": "AUX+"},
            {"number": "4", "name": "AUX-"},
            {"number": "5", "name": "SEC+"},
            {"number": "6", "name": "SEC-"},
        ],
    )
    sch_gen.add_symbol(transformer)

    # 输出整流二极管 D1
    out_diode = SCHSymbol(
        ref="D1",
        name="D_Schottky",
        value="BYW100",
        position=(x_output - 20, y_base + 20),
        rotation=90,
        pins=[{"number": "1", "name": "A"}, {"number": "2", "name": "K"}],
    )
    sch_gen.add_symbol(out_diode)

    # 输出滤波电容 C3
    out_cap_c3 = SCHSymbol(
        ref="C3",
        name="C_Electrolytic",
        value="1000µF/25V",
        position=(x_output - 10, y_base + 35),
        rotation=90,
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(out_cap_c3)

    # 输出LC滤波 L2
    out_inductor = SCHSymbol(
        ref="L2",
        name="L",
        value="4.7µH",
        position=(x_output - 5, y_base + 20),
        rotation=90,
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(out_inductor)

    # 输出滤波电容 C4
    out_cap_c4 = SCHSymbol(
        ref="C4",
        name="C_Ceramic",
        value="100µF/25V",
        position=(x_output, y_base + 35),
        rotation=90,
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(out_cap_c4)

    # 输出端子
    out_terminal = SCHSymbol(
        ref="J2",
        name="Screw_Terminal",
        value="12V_OUT",
        position=(x_output + 15, y_base + 20),
        pins=[{"number": "1", "name": "+12V"}, {"number": "2", "name": "GND"}],
    )
    sch_gen.add_symbol(out_terminal)

    # 反馈部分 - TL431
    tl431 = SCHSymbol(
        ref="U3",
        name="TL431",
        value="TL431",
        position=(x_feedback, y_base - 10),
        pins=[
            {"number": "1", "name": "REF"},
            {"number": "2", "name": "A"},
            {"number": "3", "name": "K"},
        ],
    )
    sch_gen.add_symbol(tl431)

    # 光耦 U2
    optocoupler = SCHSymbol(
        ref="U2",
        name="PC817",
        value="PC817",
        position=(x_viper + 20, y_base - 10),
        pins=[
            {"number": "1", "name": "A"},
            {"number": "2", "name": "K"},
            {"number": "3", "name": "E"},
            {"number": "4", "name": "C"},
        ],
    )
    sch_gen.add_symbol(optocoupler)

    # 反馈电阻 R2
    r2_fb = SCHSymbol(
        ref="R2",
        name="R",
        value="10k",
        position=(x_feedback - 15, y_base - 5),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(r2_fb)

    # 反馈电阻 R3
    r3_fb = SCHSymbol(
        ref="R3",
        name="R",
        value="3.3k",
        position=(x_feedback - 5, y_base - 20),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(r3_fb)

    # 限流电阻 R4
    r4_limit = SCHSymbol(
        ref="R4",
        name="R",
        value="1k",
        position=(x_viper + 10, y_base - 5),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(r4_limit)

    # 添加连线（简化版）
    # 这里添加一些关键连接线
    sch_gen.add_wire(
        SCHWire(start=(x_input + 5, y_base + 25), end=(x_input + 10, y_base + 35))
    )
    sch_gen.add_wire(
        SCHWire(start=(x_rect + 20, y_base + 25), end=(x_filter - 5, y_base + 35))
    )
    sch_gen.add_wire(
        SCHWire(
            start=(x_viper + 10, y_base + 30), end=(x_transformer - 10, y_base + 25)
        )
    )
    sch_gen.add_wire(
        SCHWire(
            start=(x_transformer + 15, y_base + 25), end=(x_output - 25, y_base + 20)
        )
    )

    # 保存原理图
    sch_file = os.path.join(output_dir, "power_supply_220v_12v.kicad_sch")
    sch_gen.save(sch_file)
    print(f"  [OK] Schematic saved: {sch_file}")

    # ==================== 生成PCB ====================
    print("\n[2/2] Generating PCB...")
    pcb_gen = PCBFileGenerator()
    pcb_gen.set_board_properties(80.0, 60.0, layers=2, name="220V to 12V PSU")

    # 定义板框（矩形）
    board_outline = [(0, 0), (80.0, 0), (80.0, 60.0), (0, 60.0), (0, 0)]
    pcb_gen.set_board_outline(board_outline)

    # 添加AC输入端子
    pcb_gen.add_component(
        PCBComponent(
            ref="J1",
            footprint="TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
            value="AC_IN",
            position=(10.0, 50.0),
            pads=[
                {"number": "1", "x": 0, "y": 2.54, "net": 1, "net_name": "AC_L"},
                {"number": "2", "x": 0, "y": -2.54, "net": 2, "net_name": "AC_N"},
            ],
        )
    )

    # 添加保险丝
    pcb_gen.add_component(
        PCBComponent(
            ref="F1",
            footprint="Fuse_Littelfuse_395Series",
            value="500mA/250V",
            position=(20.0, 50.0),
            pads=[
                {"number": "1", "x": -3.5, "y": 0, "net": 1, "net_name": "AC_L"},
                {"number": "2", "x": 3.5, "y": 0, "net": 3, "net_name": "AC_L_FUSED"},
            ],
        )
    )

    # 添加桥式整流器
    pcb_gen.add_component(
        PCBComponent(
            ref="BR1",
            footprint="Diode_Bridge_DIP-4",
            value="MB6S",
            position=(35.0, 50.0),
            pads=[
                {"number": "1", "x": -3.81, "y": -2.54, "net": 4, "net_name": "HV+"},
                {"number": "2", "x": -3.81, "y": 2.54, "net": 5, "net_name": "AC_L_IN"},
                {"number": "3", "x": 3.81, "y": 2.54, "net": 6, "net_name": "HV-"},
                {"number": "4", "x": 3.81, "y": -2.54, "net": 7, "net_name": "AC_N_IN"},
            ],
        )
    )

    # 添加高压滤波电容
    pcb_gen.add_component(
        PCBComponent(
            ref="C1",
            footprint="C_Elec_8x10.2",
            value="22µF/400V",
            position=(50.0, 50.0),
            pads=[
                {"number": "1", "x": -1.5, "y": 0, "net": 4, "net_name": "HV+"},
                {"number": "2", "x": 1.5, "y": 0, "net": 6, "net_name": "HV-"},
            ],
        )
    )

    # 添加VIPer22A
    pcb_gen.add_component(
        PCBComponent(
            ref="U1",
            footprint="DIP-8_W7.62mm",
            value="VIPer22A",
            position=(65.0, 45.0),
            orientation=90,
            pads=[
                {"number": "1", "x": -3.81, "y": 5.08, "net": 8, "net_name": "SOURCE"},
                {"number": "2", "x": -3.81, "y": 2.54, "net": 8, "net_name": "SOURCE"},
                {"number": "3", "x": -3.81, "y": 0, "net": 9, "net_name": "FB"},
                {"number": "4", "x": -3.81, "y": -2.54, "net": 10, "net_name": "VDD"},
                {"number": "5", "x": -3.81, "y": -5.08, "net": 11, "net_name": "DRAIN"},
                {"number": "6", "x": 3.81, "y": -5.08, "net": 11, "net_name": "DRAIN"},
                {"number": "7", "x": 3.81, "y": -2.54, "net": 11, "net_name": "DRAIN"},
                {"number": "8", "x": 3.81, "y": 2.54, "net": 11, "net_name": "DRAIN"},
            ],
        )
    )

    # 添加变压器
    pcb_gen.add_component(
        PCBComponent(
            ref="T1",
            footprint="Transformer_EE25",
            value="EE-25",
            position=(40.0, 35.0),
            pads=[
                {"number": "1", "x": -7.5, "y": 5.0, "net": 4, "net_name": "HV+"},
                {"number": "2", "x": -7.5, "y": -5.0, "net": 11, "net_name": "DRAIN"},
                {"number": "3", "x": 0, "y": 5.0, "net": 12, "net_name": "AUX+"},
                {"number": "4", "x": 0, "y": -5.0, "net": 10, "net_name": "VDD"},
                {"number": "5", "x": 7.5, "y": 5.0, "net": 13, "net_name": "SEC+"},
                {"number": "6", "x": 7.5, "y": -5.0, "net": 14, "net_name": "SEC-"},
            ],
        )
    )

    # 添加输出整流二极管
    pcb_gen.add_component(
        PCBComponent(
            ref="D1",
            footprint="D_SOD-128",
            value="BYW100",
            position=(60.0, 30.0),
            orientation=90,
            pads=[
                {"number": "1", "x": 0, "y": -2.0, "net": 13, "net_name": "SEC+"},
                {"number": "2", "x": 0, "y": 2.0, "net": 15, "net_name": "OUT+"},
            ],
        )
    )

    # 添加输出滤波电容
    pcb_gen.add_component(
        PCBComponent(
            ref="C3",
            footprint="C_Elec_10x10",
            value="1000µF/25V",
            position=(70.0, 25.0),
            pads=[
                {"number": "1", "x": -2.0, "y": 0, "net": 15, "net_name": "OUT+"},
                {"number": "2", "x": 2.0, "y": 0, "net": 16, "net_name": "GND"},
            ],
        )
    )

    # 添加输出端子
    pcb_gen.add_component(
        PCBComponent(
            ref="J2",
            footprint="TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
            value="12V_OUT",
            position=(70.0, 15.0),
            pads=[
                {"number": "1", "x": 0, "y": 2.54, "net": 15, "net_name": "OUT+"},
                {"number": "2", "x": 0, "y": -2.54, "net": 16, "net_name": "GND"},
            ],
        )
    )

    # 添加TL431
    pcb_gen.add_component(
        PCBComponent(
            ref="U3",
            footprint="TO-92_Inline",
            value="TL431",
            position=(25.0, 20.0),
            pads=[
                {"number": "1", "x": -2.54, "y": 0, "net": 17, "net_name": "REF"},
                {"number": "2", "x": 0, "y": 0, "net": 16, "net_name": "GND"},
                {"number": "3", "x": 2.54, "y": 0, "net": 18, "net_name": "CATHODE"},
            ],
        )
    )

    # 添加光耦
    pcb_gen.add_component(
        PCBComponent(
            ref="U2",
            footprint="DIP-4_W7.62mm",
            value="PC817",
            position=(45.0, 20.0),
            pads=[
                {
                    "number": "1",
                    "x": -3.81,
                    "y": 2.54,
                    "net": 18,
                    "net_name": "CATHODE",
                },
                {"number": "2", "x": -3.81, "y": -2.54, "net": 16, "net_name": "GND"},
                {"number": "3", "x": 3.81, "y": -2.54, "net": 8, "net_name": "SOURCE"},
                {"number": "4", "x": 3.81, "y": 2.54, "net": 9, "net_name": "FB"},
            ],
        )
    )

    # 添加一些走线
    pcb_gen.add_track(PCBTrack(start=(15.0, 50.0), end=(20.0, 50.0), width=0.5, net=1))
    pcb_gen.add_track(PCBTrack(start=(25.0, 50.0), end=(30.0, 50.0), width=0.5, net=3))
    pcb_gen.add_track(PCBTrack(start=(40.0, 50.0), end=(45.0, 50.0), width=0.8, net=4))
    pcb_gen.add_track(PCBTrack(start=(55.0, 50.0), end=(60.0, 50.0), width=0.8, net=4))

    # 保存PCB
    pcb_file = os.path.join(output_dir, "power_supply_220v_12v.kicad_pcb")
    pcb_gen.save(pcb_file)
    print(f"  [OK] PCB saved: {pcb_file}")

    # ==================== 生成报告 ====================
    print("\n" + "=" * 70)
    print("设计完成!")
    print("=" * 70)
    print(f"\n输出文件:")
    print(f"  原理图: {sch_file}")
    print(f"  PCB:    {pcb_file}")
    print(f"\n设计规格:")
    print(f"  输入:   220V AC (85-265V)")
    print(f"  输出:   12V DC / 1A (12W)")
    print(f"  拓扑:   反激式 (Flyback)")
    print(f"  主控:   VIPer22A")
    print(f"  隔离:   是 (变压器隔离)")
    print(f"\n变压器参数 (EE-25 磁芯):")
    print(f"  初级:   140匝, 0.25mm线径")
    print(f"  次级:   14匝, 0.5mm线径 (三层绝缘线)")
    print(f"  辅助:   16匝, 0.2mm线径")
    print(f"  气隙:   0.15mm")
    print(f"\n重要提示:")
    print(f"  1. 此电源涉及高压，调试时请使用隔离变压器")
    print(f"  2. 变压器需要自制或定制")
    print(f"  3. 初次上电请使用电流限制的电源供电")
    print(f"  4. 使用适当的保险丝和压敏电阻进行保护")
    print("=" * 70)

    return {
        "success": True,
        "sch_file": sch_file,
        "pcb_file": pcb_file,
        "output_dir": output_dir,
    }


if __name__ == "__main__":
    result = create_power_supply_220v_to_12v()
    if result["success"]:
        print("\n[OK] 电源模块设计生成成功!")
    else:
        print("\n[FAIL] 设计生成失败")
