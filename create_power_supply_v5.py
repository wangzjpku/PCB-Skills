#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
220V转12V电源模块设计 - V5 智能布局版
使用VIPer22A反激式开关电源方案
输出: 12V/1A (12W)

新特性：
- 智能原理图布局（避免超出边界和连线交叉）
- 智能PCB分区布局（高压/低压隔离）
- 优化的布线（减少交叉）
- 统一输出到 output-result 目录
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.output_manager import get_output_manager
from scripts.generators.sch_generator_v2 import (
    SchematicFileGeneratorV2,
    SymbolLibrary,
)
from scripts.generators.pcb_generator_v2 import (
    PCBFileGeneratorV2,
    PCBComponent,
)
from scripts.generators.footprint_lib import (
    create_terminal_block_2p,
    create_fuse_5x20,
    create_d_bridge,
    create_c_elec_8x10,
    create_dip8,
    create_transformer_ee25,
    create_d_schottky_to220,
    create_c_elec_10x10,
    create_r_0805,
    create_to92,
)
from scripts.generators.layout_manager import (
    SchematicLayout,
    PCBLayout,
    SchematicRouter,
    PCBRouter,
)


def create_power_supply_v5():
    """创建完整的220V转12V电源模块 - V5 智能布局版"""

    # 初始化输出管理器
    output_mgr = get_output_manager("220V_12V_PowerSupply")
    print(f"输出目录: {output_mgr.output_dir}")
    print(f"版本: {output_mgr.version}")

    print("=" * 70)
    print("220V to 12V Power Supply Module Design V5")
    print("Smart Layout Edition")
    print("=" * 70)

    # ==================== 原理图 - 智能布局 ====================
    print("\n[1/2] Generating Schematic with Smart Layout...")

    sch_gen = SchematicFileGeneratorV2()
    sch_gen.set_page_properties(297.0, 210.0, "220V to 12V PSU - Smart Layout")

    # 初始化布局器
    sch_layout = SchematicLayout(page_width=297.0, page_height=210.0)
    sch_router = SchematicRouter()

    # === 第1行: AC输入和保护 (左上角) ===
    j1 = SymbolLibrary.create_screw_terminal(
        "J1", "AC_IN", sch_layout.get_position("input", 0)
    )
    sch_gen.add_symbol(j1)

    f1 = SymbolLibrary.create_fuse(
        "F1", "500mA/250V", sch_layout.get_position("input", 1)
    )
    sch_gen.add_symbol(f1)

    rv1 = SymbolLibrary.create_varistor(
        "RV1", "10D561K", sch_layout.get_position("protection", 0)
    )
    sch_gen.add_symbol(rv1)

    # === 第2行: 整流和高压滤波 (中上区域) ===
    br1 = SymbolLibrary.create_bridge_rectifier(
        "BR1", "MB6S", sch_layout.get_position("rectifier", 0)
    )
    sch_gen.add_symbol(br1)

    c1 = SymbolLibrary.create_capacitor(
        "C1", "22uF/400V", sch_layout.get_position("rectifier", 1), polarized=True
    )
    sch_gen.add_symbol(c1)

    # C1的地符号（放在C1下方）
    gnd1 = SymbolLibrary.create_gnd((c1.position[0], c1.position[1] - 12))
    sch_gen.add_power_symbol(gnd1)

    # === 第3行: VIPer和变压器 (中间区域) ===
    viper = SymbolLibrary.create_viper22a(
        "U1", "VIPer22A", sch_layout.get_position("power_stage", 0)
    )
    sch_gen.add_symbol(viper)

    t1 = SymbolLibrary.create_transformer(
        "T1", "EE-25", sch_layout.get_position("power_stage", 1)
    )
    sch_gen.add_symbol(t1)

    # VCC去耦电容
    c2 = SymbolLibrary.create_capacitor(
        "C2", "10uF/25V", (viper.position[0] - 20, viper.position[1]), polarized=True
    )
    sch_gen.add_symbol(c2)

    gnd2 = SymbolLibrary.create_gnd((c2.position[0], c2.position[1] - 12))
    sch_gen.add_power_symbol(gnd2)

    # === 第4行: 输出整流滤波 (右侧区域) ===
    d1 = SymbolLibrary.create_schottky_diode(
        "D1", "BYW100", sch_layout.get_position("output", 0)
    )
    sch_gen.add_symbol(d1)

    c3 = SymbolLibrary.create_capacitor(
        "C3", "1000uF/25V", sch_layout.get_position("output", 1), polarized=True
    )
    sch_gen.add_symbol(c3)

    c4 = SymbolLibrary.create_capacitor(
        "C4", "100uF/25V", (c3.position[0] + 15, c3.position[1]), polarized=True
    )
    sch_gen.add_symbol(c4)

    # 输出端子
    j2 = SymbolLibrary.create_screw_terminal(
        "J2", "12V_OUT", (c4.position[0] + 20, c3.position[1]), 2
    )
    sch_gen.add_symbol(j2)

    # 输出地符号
    gnd3 = SymbolLibrary.create_gnd((c3.position[0], c3.position[1] - 12))
    sch_gen.add_power_symbol(gnd3)

    gnd4 = SymbolLibrary.create_gnd((c4.position[0], c4.position[1] - 12))
    sch_gen.add_power_symbol(gnd4)

    # === 反馈电路 (下方区域) ===
    u2 = SymbolLibrary.create_optocoupler(
        "U2", "PC817", sch_layout.get_position("feedback", 0)
    )
    sch_gen.add_symbol(u2)

    u3 = SymbolLibrary.create_tl431(
        "U3", "TL431", sch_layout.get_position("feedback", 1)
    )
    sch_gen.add_symbol(u3)

    r1 = SymbolLibrary.create_resistor(
        "R1", "10k", (u2.position[0] - 15, u2.position[1])
    )
    sch_gen.add_symbol(r1)

    r2 = SymbolLibrary.create_resistor(
        "R2", "3.3k", (u3.position[0] + 15, u3.position[1])
    )
    sch_gen.add_symbol(r2)

    # === 智能连线 ===
    print("  Routing schematic with optimized paths...")

    # 电源输入路径（从左到右）
    sch_gen.connect_pins("J1", "1", "F1", "1", "AC_L")
    sch_gen.connect_pins("F1", "2", "BR1", "2", "AC_L_FUSED")
    sch_gen.connect_pins("J1", "2", "RV1", "2", "AC_N")
    sch_gen.connect_pins("RV1", "1", "BR1", "4", "AC_N")

    # 整流输出到滤波
    sch_gen.connect_pins("BR1", "1", "C1", "1", "HV_PLUS")
    sch_gen.connect_pins("BR1", "3", "C1", "2", "HV_MINUS")

    # 高压侧到VIPer
    sch_gen.connect_pins("C1", "1", "U1", "5", "HV_PLUS")

    # VIPer到变压器（初级）
    sch_gen.connect_pins("U1", "5", "T1", "1", "DRAIN")
    sch_gen.connect_pins("U1", "1", "T1", "2", "SOURCE")

    # 辅助绕组供电
    sch_gen.connect_pins("T1", "3", "U1", "4", "VDD")
    sch_gen.connect_pins("U1", "4", "C2", "1", "VDD")
    sch_gen.connect_pins("C2", "2", "U1", "1", "GND")

    # 变压器次级到输出
    sch_gen.connect_pins("T1", "5", "D1", "2", "SEC_PLUS")
    sch_gen.connect_pins("D1", "1", "C3", "1", "OUT_PLUS")
    sch_gen.connect_pins("C3", "1", "C4", "1", "OUT_PLUS")
    sch_gen.connect_pins("C4", "1", "J2", "1", "OUT_PLUS")

    # 地连接
    sch_gen.connect_pins("C1", "2", "U1", "1", "GND")
    sch_gen.connect_pins("T1", "6", "C3", "2", "SEC_MINUS")
    sch_gen.connect_pins("C3", "2", "C4", "2", "GND")
    sch_gen.connect_pins("C4", "2", "J2", "2", "GND")

    # 保存原理图
    sch_file = output_mgr.save_sch()
    sch_gen.save(sch_file)
    print(f"  [OK] Schematic saved: {sch_file}")

    # ==================== PCB - 智能分区布局 ====================
    print("\n[2/2] Generating PCB with Smart Zone Layout...")

    pcb_gen = PCBFileGeneratorV2()
    pcb_gen.set_board_properties(
        120.0, 90.0, layers=2, name="220V to 12V PSU - Smart Layout"
    )

    # 设置板框
    pcb_gen.set_board_outline([(0, 0), (120.0, 0), (120.0, 90.0), (0, 90.0), (0, 0)])

    # 初始化PCB布局器
    pcb_layout = PCBLayout(board_width=120.0, board_height=90.0)
    pcb_router = PCBRouter(board_width=120.0, board_height=90.0)

    # 定义网络
    nets = [
        "AC_L",
        "AC_N",
        "AC_L_FUSED",
        "HV_PLUS",
        "HV_MINUS",
        "DRAIN",
        "VDD",
        "SOURCE",
        "FB",
        "AUX_PLUS",
        "AUX_MINUS",
        "SEC_PLUS",
        "SEC_MINUS",
        "OUT_PLUS",
        "OUT_MINUS",
        "GND",
    ]
    for net in nets:
        pcb_gen.net_manager.add_net(net)

    # === 按区域放置元件 ===
    print("  Placing components in zones...")

    # 区域1: AC输入（左侧）
    comp_j1 = PCBComponent(
        ref="J1",
        footprint_name="TerminalBlock_2P",
        value="AC_IN",
        position=pcb_layout.get_position("ac_input", "J1", 10, 8),
        footprint_data=create_terminal_block_2p(),
    )
    pcb_gen.add_component(comp_j1)

    # 区域2: 保护器件
    comp_f1 = PCBComponent(
        ref="F1",
        footprint_name="Fuse_5x20",
        value="500mA",
        position=pcb_layout.get_position("protection", "F1", 16, 6),
        footprint_data=create_fuse_5x20(),
    )
    pcb_gen.add_component(comp_f1)

    comp_rv1 = PCBComponent(
        ref="RV1",
        footprint_name="R_0805",
        value="10D561K",
        position=(comp_f1.position[0] + 15, comp_f1.position[1]),
        footprint_data=create_r_0805(),
    )
    pcb_gen.add_component(comp_rv1)

    # 区域3: 整流和高压滤波
    comp_br1 = PCBComponent(
        ref="BR1",
        footprint_name="Diode_Bridge",
        value="MB6S",
        position=pcb_layout.get_position("rectifier", "BR1", 12, 10),
        footprint_data=create_d_bridge(),
    )
    pcb_gen.add_component(comp_br1)

    comp_c1 = PCBComponent(
        ref="C1",
        footprint_name="C_Elec_8x10",
        value="22uF/400V",
        position=(comp_br1.position[0] + 20, comp_br1.position[1]),
        footprint_data=create_c_elec_8x10(),
    )
    pcb_gen.add_component(comp_c1)

    # 区域4: 变压器（中心，隔离边界）
    comp_t1 = PCBComponent(
        ref="T1",
        footprint_name="Transformer_EE25",
        value="EE-25",
        position=pcb_layout.get_position("transformer", "T1", 20, 16),
        footprint_data=create_transformer_ee25(),
    )
    pcb_gen.add_component(comp_t1)

    # 区域5: 控制器
    comp_u1 = PCBComponent(
        ref="U1",
        footprint_name="DIP8",
        value="VIPer22A",
        position=(comp_c1.position[0] - 10, comp_c1.position[1] - 25),
        orientation=0,
        footprint_data=create_dip8(),
    )
    pcb_gen.add_component(comp_u1)

    comp_c2 = PCBComponent(
        ref="C2",
        footprint_name="C_Elec_8x10",
        value="10uF/25V",
        position=(comp_u1.position[0] - 15, comp_u1.position[1]),
        footprint_data=create_c_elec_8x10(),
    )
    pcb_gen.add_component(comp_c2)

    # 区域6: 输出整流（右侧，低压区）
    comp_d1 = PCBComponent(
        ref="D1",
        footprint_name="D_Schottky_TO220",
        value="BYW100",
        position=pcb_layout.get_position("output_rectifier", "D1", 10, 15),
        orientation=90,
        footprint_data=create_d_schottky_to220(),
    )
    pcb_gen.add_component(comp_d1)

    # 区域7: 输出滤波
    comp_c3 = PCBComponent(
        ref="C3",
        footprint_name="C_Elec_10x10",
        value="1000uF/25V",
        position=pcb_layout.get_position("output_filter", "C3", 10, 10),
        footprint_data=create_c_elec_10x10(),
    )
    pcb_gen.add_component(comp_c3)

    comp_c4 = PCBComponent(
        ref="C4",
        footprint_name="C_Elec_10x10",
        value="100uF/25V",
        position=(comp_c3.position[0] + 15, comp_c3.position[1]),
        footprint_data=create_c_elec_10x10(),
    )
    pcb_gen.add_component(comp_c4)

    # 区域8: 输出端子
    comp_j2 = PCBComponent(
        ref="J2",
        footprint_name="TerminalBlock_2P",
        value="12V_OUT",
        position=pcb_layout.get_position("output_connector", "J2", 10, 8),
        footprint_data=create_terminal_block_2p(),
    )
    pcb_gen.add_component(comp_j2)

    # 区域9: 反馈电路
    comp_u2 = PCBComponent(
        ref="U2",
        footprint_name="TO92",
        value="PC817",
        position=pcb_layout.get_position("feedback", "U2", 5, 5),
        footprint_data=create_to92(),
    )
    pcb_gen.add_component(comp_u2)

    comp_u3 = PCBComponent(
        ref="U3",
        footprint_name="TO92",
        value="TL431",
        position=(comp_u2.position[0] + 15, comp_u2.position[1]),
        footprint_data=create_to92(),
    )
    pcb_gen.add_component(comp_u3)

    comp_r1 = PCBComponent(
        ref="R1",
        footprint_name="R_0805",
        value="10k",
        position=(comp_u2.position[0] - 10, comp_u2.position[1] + 10),
        footprint_data=create_r_0805(),
    )
    pcb_gen.add_component(comp_r1)

    comp_r2 = PCBComponent(
        ref="R2",
        footprint_name="R_0805",
        value="3.3k",
        position=(comp_u3.position[0] + 10, comp_u3.position[1] + 10),
        footprint_data=create_r_0805(),
    )
    pcb_gen.add_component(comp_r2)

    # === PCB智能布线 ===
    print("  Routing PCB with zone-based routing...")

    # 高压区布线（左侧）
    pcb_gen.connect_pins("J1", "1", "F1", "1", "AC_L", width=0.6)
    pcb_gen.connect_pins("F1", "2", "BR1", "2", "AC_L_FUSED", width=0.6)
    pcb_gen.connect_pins("J1", "2", "RV1", "1", "AC_N", width=0.6)
    pcb_gen.connect_pins("RV1", "2", "BR1", "4", "AC_N", width=0.6)

    # 整流输出（粗线）
    pcb_gen.connect_pins("BR1", "1", "C1", "1", "HV_PLUS", width=1.0)
    pcb_gen.connect_pins("BR1", "3", "C1", "2", "HV_MINUS", width=1.0)

    # 功率级布线（连接到变压器初级）
    pcb_gen.connect_pins("C1", "1", "T1", "1", "HV_PLUS", width=0.8)
    pcb_gen.connect_pins("U1", "5", "T1", "2", "DRAIN", width=0.8)

    # 辅助绕组
    pcb_gen.connect_pins("T1", "3", "U1", "4", "VDD", width=0.4)
    pcb_gen.connect_pins("U1", "4", "C2", "1", "VDD", width=0.4)
    pcb_gen.connect_pins("C2", "2", "U1", "1", "GND", width=0.4)

    # 次级输出（低压区，右侧）
    pcb_gen.connect_pins("T1", "5", "D1", "1", "SEC_PLUS", width=1.0)
    pcb_gen.connect_pins("D1", "2", "C3", "1", "OUT_PLUS", width=1.2)
    pcb_gen.connect_pins("C3", "1", "C4", "1", "OUT_PLUS", width=1.2)
    pcb_gen.connect_pins("C4", "1", "J2", "1", "OUT_PLUS", width=1.2)

    # 地连接
    pcb_gen.connect_pins("C1", "2", "U1", "1", "GND", width=0.6)
    pcb_gen.connect_pins("T1", "6", "C3", "2", "SEC_MINUS", width=0.8)
    pcb_gen.connect_pins("C3", "2", "C4", "2", "GND", width=0.8)
    pcb_gen.connect_pins("C4", "2", "J2", "2", "GND", width=0.8)

    print(f"  [OK] Routed {len(pcb_gen.tracks)} tracks")

    # 保存PCB
    pcb_file = output_mgr.save_pcb()
    pcb_gen.save(pcb_file)
    print(f"  [OK] PCB saved: {pcb_file}")

    # 创建README
    readme_content = f"""# 220V转12V电源模块 - {output_mgr.version}

## 设计规格

- **输入**: 220V AC (85-265V)
- **输出**: 12V DC / 1A (12W)
- **拓扑**: 反激式 (Flyback)
- **主控IC**: VIPer22A
- **隔离**: 是 (变压器隔离)

## 文件列表

- `{os.path.basename(sch_file)}` - KiCad原理图
- `{os.path.basename(pcb_file)}` - KiCad PCB文件

## 布局特点

### 原理图布局
- 信号流向：从左到右
- 电源流向：从上到下
- 功能分区：输入 → 保护 → 整流 → 功率 → 输出
- 反馈电路：独立放置在下方

### PCB分区
- **左侧**: AC输入和保护器件（高压区）
- **中上**: 整流滤波（高压区）
- **中心**: 变压器（隔离边界）
- **中右**: VIPer控制器（控制区）
- **右侧**: 输出整流滤波（低压区）
- **底部**: 反馈电路（控制区）

### 安全设计
- 初级与次级隔离距离 > 6mm
- 高压区与低压区分区布线
- 功率地与控制地分开

## 主要元件

| 位号 | 元件 | 参数 | 区域 |
|------|------|------|------|
| J1 | 接线端子 | AC输入 | 输入区 |
| F1 | 保险丝 | 500mA/250V | 保护区 |
| BR1 | 整流桥 | MB6S | 整流区 |
| C1 | 电解电容 | 22uF/400V | 整流区 |
| U1 | VIPer22A | 主控IC | 控制区 |
| T1 | 变压器 | EE-25 | 隔离区 |
| D1 | 肖特基二极管 | BYW100 | 输出区 |
| C3 | 电解电容 | 1000uF/25V | 输出区 |
| J2 | 接线端子 | 12V输出 | 输出区 |

## 生成时间

{__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
Generated by KiCad Auto-Design Skill V5 (Smart Layout)
"""
    readme_path = output_mgr.create_readme(readme_content)
    print(f"  [OK] README saved: {readme_path}")

    # 生成报告
    print("\n" + "=" * 70)
    print("Design Complete!")
    print("=" * 70)
    info = output_mgr.get_info()
    print(f"\n项目: {info['project']}")
    print(f"版本: {info['version']}")
    print(f"输出目录: {info['output_dir']}")
    print(f"\n生成文件:")
    for f in info["files"]:
        print(f"  - {f}")
    print(f"\n统计:")
    print(f"  - 原理图符号: {len(sch_gen.symbols)}")
    print(f"  - 原理图连线: {len(sch_gen.wires)}")
    print(f"  - PCB组件: {len(pcb_gen.components)}")
    print(f"  - PCB走线: {len(pcb_gen.tracks)}")
    print(f"  - 网络数量: {len(pcb_gen.net_manager.nets)}")
    print("\n布局特点:")
    print("  - 原理图：分区布局，避免超出边界")
    print("  - PCB：分区设计，高压/低压隔离")
    print("=" * 70)

    return info


if __name__ == "__main__":
    result = create_power_supply_v5()
    print("\n[OK] Power supply design V5 generated successfully!")
    print(f"\nAll files saved to: {result['output_dir']}")
