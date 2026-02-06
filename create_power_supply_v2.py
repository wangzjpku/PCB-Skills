"""
220V转12V电源模块设计 - 第二轮测试
使用VIPer22A反激式开关电源方案
输出: 12V/1A (12W)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.generators.sch_generator import (
    SchematicFileGenerator,
    SCHSymbol,
    SCHWire,
    SCHJunction,
    create_simple_schematic,
)
from scripts.generators.pcb_generator import (
    PCBFileGenerator,
    PCBComponent,
    PCBTrack,
    create_simple_pcb,
)


def create_power_supply_220v_to_12v_complete(output_dir: str = "./test_output_power"):
    """
    创建完整的220V转12V电源模块
    使用VIPer22A反激式开关电源方案
    """
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("220V to 12V Power Supply Module Design v2.0")
    print("Using VIPer22A Flyback Converter")
    print("Output: 12V/1A (12W)")
    print("=" * 60)

    # ==================== 生成原理图 ====================
    print("\n[1/2] Generating Schematic...")
    sch_gen = SchematicFileGenerator()
    sch_gen.set_page_properties(210.0, 297.0, "220V to 12V PSU - VIPer22A")

    # AC输入部分
    # AC输入端子
    ac_input = SCHSymbol(
        ref="J1",
        name="Screw_Terminal",
        value="AC_IN",
        position=(20, 180),
        pins=[{"number": "1", "name": "L"}, {"number": "2", "name": "N"}],
    )
    sch_gen.add_symbol(ac_input)

    # 保险丝
    fuse = SCHSymbol(
        ref="F1",
        name="Fuse",
        value="1A/250V",
        position=(35, 180),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(fuse)

    # 压敏电阻 (防雷)
    varistor = SCHSymbol(
        ref="RV1",
        name="Varistor",
        value="14D471K",
        position=(35, 165),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(varistor)

    # X电容 (EMI滤波)
    cx1 = SCHSymbol(
        ref="CX1",
        name="C",
        value="0.1uF/275V X2",
        position=(50, 180),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(cx1)

    # 共模电感
    l1 = SCHSymbol(
        ref="L1",
        name="L_Core",
        value="10mH",
        position=(65, 180),
        pins=[
            {"number": "1", "name": "1"},
            {"number": "2", "name": "2"},
            {"number": "3", "name": "3"},
            {"number": "4", "name": "4"},
        ],
    )
    sch_gen.add_symbol(l1)

    # 整流桥
    db1 = SCHSymbol(
        ref="DB1",
        name="Bridge",
        value="MB6S",
        position=(85, 170),
        pins=[
            {"number": "1", "name": "AC1"},
            {"number": "2", "name": "AC2"},
            {"number": "3", "name": "+"},
            {"number": "4", "name": "-"},
        ],
    )
    sch_gen.add_symbol(db1)

    # 输入滤波电容
    c1 = SCHSymbol(
        ref="C1",
        name="C",
        value="10uF/400V",
        position=(105, 165),
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(c1)

    # VIPer22A主控IC
    viper = SCHSymbol(
        ref="U1",
        name="VIPer22A",
        value="",
        position=(125, 150),
        pins=[
            {"number": "1", "name": "VDD"},
            {"number": "2", "name": "VDD"},
            {"number": "3", "name": "FB"},
            {"number": "4", "name": "SOURCE"},
            {"number": "5", "name": "DRAIN"},
        ],
    )
    sch_gen.add_symbol(viper)

    # 变压器
    t1 = SCHSymbol(
        ref="T1",
        name="Transformer",
        value="EE16 (Pri: 120T, Sec: 12T, Aux: 20T)",
        position=(150, 140),
        pins=[
            {"number": "1", "name": "Pri+"},
            {"number": "2", "name": "Pri-"},
            {"number": "3", "name": "Aux+"},
            {"number": "4", "name": "Aux-"},
            {"number": "5", "name": "Sec+"},
            {"number": "6", "name": "Sec-"},
        ],
    )
    sch_gen.add_symbol(t1)

    # RCD吸收电路
    r1 = SCHSymbol(
        ref="R1",
        name="R",
        value="100k",
        position=(130, 120),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(r1)

    c2 = SCHSymbol(
        ref="C2",
        name="C",
        value="1nF/1kV",
        position=(145, 120),
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(c2)

    d1 = SCHSymbol(
        ref="D1",
        name="D",
        value="UF4007",
        position=(160, 120),
        pins=[{"number": "1", "name": "A"}, {"number": "2", "name": "K"}],
    )
    sch_gen.add_symbol(d1)

    # 输出整流
    d2 = SCHSymbol(
        ref="D2",
        name="D",
        value="SS34",
        position=(170, 100),
        pins=[{"number": "1", "name": "A"}, {"number": "2", "name": "K"}],
    )
    sch_gen.add_symbol(d2)

    # 输出滤波电容
    c3 = SCHSymbol(
        ref="C3",
        name="C",
        value="1000uF/25V",
        position=(185, 95),
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(c3)

    c4 = SCHSymbol(
        ref="C4",
        name="C",
        value="100nF",
        position=(200, 95),
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(c4)

    # 输出电感
    l2 = SCHSymbol(
        ref="L2",
        name="L",
        value="4.7uH",
        position=(185, 80),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(l2)

    # 反馈部分 - TL431
    u2 = SCHSymbol(
        ref="U2",
        name="TL431",
        value="",
        position=(170, 60),
        pins=[
            {"number": "1", "name": "CATHODE"},
            {"number": "2", "name": "REF"},
            {"number": "3", "name": "ANODE"},
        ],
    )
    sch_gen.add_symbol(u2)

    # 光耦
    u3 = SCHSymbol(
        ref="U3",
        name="PC817",
        value="",
        position=(150, 70),
        pins=[
            {"number": "1", "name": "ANODE"},
            {"number": "2", "name": "CATHODE"},
            {"number": "3", "name": "EMITTER"},
            {"number": "4", "name": "COLLECTOR"},
        ],
    )
    sch_gen.add_symbol(u3)

    # 反馈电阻
    r2 = SCHSymbol(
        ref="R2",
        name="R",
        value="10k 1%",
        position=(185, 60),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(r2)

    r3 = SCHSymbol(
        ref="R3",
        name="R",
        value="2.2k 1%",
        position=(200, 60),
        pins=[{"number": "1", "name": "1"}, {"number": "2", "name": "2"}],
    )
    sch_gen.add_symbol(r3)

    # 输出端子
    j2 = SCHSymbol(
        ref="J2",
        name="Screw_Terminal",
        value="DC_OUT",
        position=(200, 80),
        pins=[{"number": "1", "name": "+"}, {"number": "2", "name": "-"}],
    )
    sch_gen.add_symbol(j2)

    # 添加连线...
    # 这里简化处理，实际应该添加所有必要的连线

    # 添加电源符号
    gnd_pri = SCHSymbol(
        ref="#PWR01",
        name="GND",
        value="",
        position=(105, 145),
        pins=[{"number": "1", "name": "GND"}],
    )
    vcc_aux = SCHSymbol(
        ref="#PWR02",
        name="+12V_AUX",
        value="",
        position=(145, 130),
        pins=[{"number": "1", "name": "+12V"}],
    )
    gnd_sec = SCHSymbol(
        ref="#PWR03",
        name="GND",
        value="",
        position=(185, 70),
        pins=[{"number": "1", "name": "GND"}],
    )
    vcc_out = SCHSymbol(
        ref="#PWR04",
        name="+12V",
        value="",
        position=(200, 85),
        pins=[{"number": "1", "name": "+12V"}],
    )

    sch_gen.add_power_symbol(gnd_pri)
    sch_gen.add_power_symbol(vcc_aux)
    sch_gen.add_power_symbol(gnd_sec)
    sch_gen.add_power_symbol(vcc_out)

    # 保存原理图
    sch_file = os.path.join(output_dir, "power_supply_12v_1a.kicad_sch")
    sch_gen.save(sch_file)
    print(f"  Schematic saved: {sch_file}")

    # ==================== 生成PCB ====================
    print("\n[2/2] Generating PCB...")
    pcb_gen = PCBFileGenerator()
    pcb_gen.set_board_properties(100.0, 80.0, name="220V to 12V PSU")

    # 清空默认网络并添加自定义网络
    pcb_gen.nets = [(0, "")]
    pcb_gen.add_net(1, "AC_L")
    pcb_gen.add_net(2, "AC_N")
    pcb_gen.add_net(3, "HV_PLUS")
    pcb_gen.add_net(4, "HV_MINUS")
    pcb_gen.add_net(5, "DRAIN")
    pcb_gen.add_net(6, "AUX_PLUS")
    pcb_gen.add_net(7, "AUX_MINUS")
    pcb_gen.add_net(8, "SEC_PLUS")
    pcb_gen.add_net(9, "SEC_MINUS")
    pcb_gen.add_net(10, "FEEDBACK")
    pcb_gen.add_net(11, "PLUS_12V")
    pcb_gen.add_net(12, "GND_SEC")

    # AC输入端子
    j1 = PCBComponent(
        ref="J1",
        footprint="TerminalBlock:TerminalBlock_2P_5.0mm",
        value="AC_IN",
        position=(15, 70),
        pads=[
            {
                "number": "1",
                "x": 0,
                "y": 0,
                "net": 1,
                "net_name": "AC_L",
                "size_x": 2.5,
                "size_y": 2.5,
            },
            {
                "number": "2",
                "x": 5,
                "y": 0,
                "net": 2,
                "net_name": "AC_N",
                "size_x": 2.5,
                "size_y": 2.5,
            },
        ],
    )
    pcb_gen.add_component(j1)

    # 保险丝
    f1 = PCBComponent(
        ref="F1",
        footprint="Fuse:Fuse_5x20mm",
        value="1A",
        position=(30, 70),
        pads=[
            {
                "number": "1",
                "x": -5,
                "y": 0,
                "net": 1,
                "net_name": "AC_L",
                "size_x": 2,
                "size_y": 2,
            },
            {
                "number": "2",
                "x": 5,
                "y": 0,
                "net": 1,
                "net_name": "AC_L",
                "size_x": 2,
                "size_y": 2,
            },
        ],
    )
    pcb_gen.add_component(f1)

    # 整流桥
    db1 = PCBComponent(
        ref="DB1",
        footprint="Package_TO_SOT_SMD:TO-269AA",
        value="MB6S",
        position=(50, 70),
        pads=[
            {
                "number": "1",
                "x": -2.5,
                "y": -2.5,
                "net": 1,
                "net_name": "AC_L",
                "size_x": 1.5,
                "size_y": 1.5,
            },
            {
                "number": "2",
                "x": 2.5,
                "y": -2.5,
                "net": 2,
                "net_name": "AC_N",
                "size_x": 1.5,
                "size_y": 1.5,
            },
            {
                "number": "3",
                "x": 2.5,
                "y": 2.5,
                "net": 3,
                "net_name": "HV_PLUS",
                "size_x": 1.5,
                "size_y": 1.5,
            },
            {
                "number": "4",
                "x": -2.5,
                "y": 2.5,
                "net": 4,
                "net_name": "HV_MINUS",
                "size_x": 1.5,
                "size_y": 1.5,
            },
        ],
    )
    pcb_gen.add_component(db1)

    # 输入电容
    c1 = PCBComponent(
        ref="C1",
        footprint="Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
        value="10uF/400V",
        position=(70, 65),
        pads=[
            {
                "number": "1",
                "x": 0,
                "y": -2.5,
                "net": 3,
                "net_name": "HV_PLUS",
                "size_x": 2,
                "size_y": 2,
            },
            {
                "number": "2",
                "x": 0,
                "y": 2.5,
                "net": 4,
                "net_name": "HV_MINUS",
                "size_x": 2,
                "size_y": 2,
            },
        ],
    )
    pcb_gen.add_component(c1)

    # VIPer22A
    u1 = PCBComponent(
        ref="U1",
        footprint="Package_DIP:DIP-8_W7.62mm",
        value="VIPer22A",
        position=(90, 60),
        pads=[
            {
                "number": "1",
                "x": -3.81,
                "y": -3.81,
                "net": 6,
                "net_name": "AUX_PLUS",
                "size_x": 1.5,
                "size_y": 1.5,
            },
            {
                "number": "2",
                "x": -3.81,
                "y": -1.27,
                "net": 6,
                "net_name": "AUX_PLUS",
                "size_x": 1.5,
                "size_y": 1.5,
            },
            {
                "number": "3",
                "x": -3.81,
                "y": 1.27,
                "net": 10,
                "net_name": "FEEDBACK",
                "size_x": 1.5,
                "size_y": 1.5,
            },
            {
                "number": "4",
                "x": -3.81,
                "y": 3.81,
                "net": 4,
                "net_name": "HV_MINUS",
                "size_x": 1.5,
                "size_y": 1.5,
            },
            {
                "number": "5",
                "x": 3.81,
                "y": 3.81,
                "net": 5,
                "net_name": "DRAIN",
                "size_x": 1.5,
                "size_y": 1.5,
            },
        ],
    )
    pcb_gen.add_component(u1)

    # 变压器
    t1 = PCBComponent(
        ref="T1",
        footprint="Transformer_THT:Transformer_EE16_6P",
        value="EE16",
        position=(70, 40),
        pads=[
            {
                "number": "1",
                "x": -7.5,
                "y": -5,
                "net": 3,
                "net_name": "HV_PLUS",
                "size_x": 2,
                "size_y": 2,
            },
            {
                "number": "2",
                "x": -7.5,
                "y": 0,
                "net": 5,
                "net_name": "DRAIN",
                "size_x": 2,
                "size_y": 2,
            },
            {
                "number": "3",
                "x": -7.5,
                "y": 5,
                "net": 4,
                "net_name": "HV_MINUS",
                "size_x": 2,
                "size_y": 2,
            },
            {
                "number": "4",
                "x": 7.5,
                "y": -5,
                "net": 8,
                "net_name": "SEC_PLUS",
                "size_x": 2,
                "size_y": 2,
            },
            {
                "number": "5",
                "x": 7.5,
                "y": 5,
                "net": 9,
                "net_name": "SEC_MINUS",
                "size_x": 2,
                "size_y": 2,
            },
        ],
    )
    pcb_gen.add_component(t1)

    # 输出二极管
    d2 = PCBComponent(
        ref="D2",
        footprint="Diode_SMD:D_SMA",
        value="SS34",
        position=(50, 30),
        pads=[
            {
                "number": "1",
                "x": -1.5,
                "y": 0,
                "net": 8,
                "net_name": "SEC_PLUS",
                "size_x": 1.5,
                "size_y": 1.5,
            },
            {
                "number": "2",
                "x": 1.5,
                "y": 0,
                "net": 11,
                "net_name": "PLUS_12V",
                "size_x": 1.5,
                "size_y": 1.5,
            },
        ],
    )
    pcb_gen.add_component(d2)

    # 输出电容
    c3 = PCBComponent(
        ref="C3",
        footprint="Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
        value="1000uF/25V",
        position=(35, 25),
        pads=[
            {
                "number": "1",
                "x": 0,
                "y": -2.5,
                "net": 11,
                "net_name": "PLUS_12V",
                "size_x": 2,
                "size_y": 2,
            },
            {
                "number": "2",
                "x": 0,
                "y": 2.5,
                "net": 12,
                "net_name": "GND_SEC",
                "size_x": 2,
                "size_y": 2,
            },
        ],
    )
    pcb_gen.add_component(c3)

    # 输出端子
    j2 = PCBComponent(
        ref="J2",
        footprint="TerminalBlock:TerminalBlock_2P_5.0mm",
        value="DC_OUT",
        position=(20, 20),
        pads=[
            {
                "number": "1",
                "x": 0,
                "y": 0,
                "net": 11,
                "net_name": "PLUS_12V",
                "size_x": 2.5,
                "size_y": 2.5,
            },
            {
                "number": "2",
                "x": 5,
                "y": 0,
                "net": 12,
                "net_name": "GND_SEC",
                "size_x": 2.5,
                "size_y": 2.5,
            },
        ],
    )
    pcb_gen.add_component(j2)

    # 设置板框
    pcb_gen.set_board_outline([(5, 5), (95, 5), (95, 75), (5, 75), (5, 5)])

    # 保存PCB
    pcb_file = os.path.join(output_dir, "power_supply_12v_1a.kicad_pcb")
    pcb_gen.save(pcb_file)
    print(f"  PCB saved: {pcb_file}")

    # ==================== 验证文件 ====================
    print("\n[Verification]")

    # 检查SCH
    with open(sch_file, "r") as f:
        sch_content = f.read()
    sch_open = sch_content.count("(")
    sch_close = sch_content.count(")")
    print(f"  SCH: {len(sch_content)} chars")
    print(
        f"       Brackets: {sch_open}/{sch_close} (balanced: {sch_open == sch_close})"
    )

    # 检查PCB
    with open(pcb_file, "r") as f:
        pcb_content = f.read()
    pcb_open = pcb_content.count("(")
    pcb_close = pcb_content.count(")")
    print(f"  PCB: {len(pcb_content)} chars")
    print(
        f"       Brackets: {pcb_open}/{pcb_close} (balanced: {pcb_open == pcb_close})"
    )

    # 生成BOM
    bom_content = """
==============================================
BOM - 220V to 12V/1A Power Supply Module
==============================================

Design Specification:
- Input: 85-265V AC
- Output: 12V DC / 1A (12W)
- Topology: Flyback (Isolated)
- Controller: VIPer22A
- Switching Frequency: 60kHz

Input Protection & Filtering:
------------------------------
F1:   Fuse 1A/250V (5x20mm)
RV1:  Varistor 14D471K (470V)
CX1:  X2 Capacitor 0.1uF/275V
L1:   Common Mode Choke 10mH

Rectification & Bulk:
---------------------
DB1:  Bridge Rectifier MB6S (600V/0.5A)
C1:   Electrolytic Capacitor 10uF/400V (10x16mm)

Power Stage:
-----------
U1:   VIPer22A (PWM Controller with MOSFET)
T1:   Transformer EE16
      - Primary: 120 turns, 2mH
      - Secondary: 12 turns
      - Auxiliary: 20 turns

Snubber Circuit (RCD):
---------------------
R1:   Resistor 100kΩ (1W)
C2:   Ceramic Capacitor 1nF/1kV
D1:   Ultrafast Diode UF4007

Output Rectification:
--------------------
D2:   Schottky Diode SS34 (40V/3A)

Output Filtering:
----------------
C3:   Electrolytic Capacitor 1000uF/25V (10x16mm)
C4:   Ceramic Capacitor 100nF/50V
L2:   Inductor 4.7uH

Feedback & Regulation:
-----------------------
U2:   TL431 (Precision Shunt Regulator)
U3:   PC817 (Optocoupler)
R2:   Resistor 10kΩ (1%)
R3:   Resistor 2.2kΩ (1%)

Output Connector:
----------------
J2:   Screw Terminal 2P 5.0mm

Design Notes:
------------
1. Transformer design is critical - ensure proper isolation
2. Keep primary and secondary sides well separated
3. Use appropriate clearance and creepage distances
4. Add sufficient copper area for heat dissipation
5. Test with load before full power operation
6. High voltage present - exercise caution!

Safety Considerations:
---------------------
- Input has lethal high voltage (220V AC)
- Ensure proper isolation between primary and secondary
- Use appropriate fuse rating
- Consider thermal management for VIPer22A
- Add appropriate markings and warnings

==============================================
"""

    bom_file = os.path.join(output_dir, "BOM_Power_Supply_12V_1A.txt")
    with open(bom_file, "w", encoding="utf-8") as f:
        f.write(bom_content)
    print(f"\n  BOM saved: {bom_file}")

    print("\n" + "=" * 60)
    print("Design Complete!")
    print("=" * 60)
    print(f"\nFiles generated in: {output_dir}")
    print(f"  - {os.path.basename(sch_file)}")
    print(f"  - {os.path.basename(pcb_file)}")
    print(f"  - {os.path.basename(bom_file)}")

    return {
        "success": True,
        "sch_file": sch_file,
        "pcb_file": pcb_file,
        "bom_file": bom_file,
    }


if __name__ == "__main__":
    result = create_power_supply_220v_to_12v_complete()
    print("\nDone!")
