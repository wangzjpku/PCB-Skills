#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展设计数据库 - 生成100+电源设计方案
通过系统性地组合芯片、输入输出规格生成多样化设计
"""

from typing import List, Dict
from chip_database import CHIP_DATABASE, Topology


def generate_extended_designs() -> List[Dict]:
    """
    生成扩展的设计方案列表
    通过组合不同芯片和规格，生成100+设计
    """
    designs = []

    # ========== AC-DC 反激式设计 ==========
    acdc_chips = [
        "VIPer22A",
        "VIPer12A",
        "VIPer35",
        "TNY279",
        "LNK304",
        "UC3842",
        "UC3843",
        "UC3844",
        "UC3845",
        "TL494",
    ]

    # 输出规格组合 (电压, 电流, 应用场景)
    acdc_output_specs = [
        # 小功率适配器类
        {"voltage": 5, "current": 0.5, "apps": "USB充电器", "power_range": (0, 5)},
        {"voltage": 5, "current": 1.0, "apps": "手机充电器", "power_range": (0, 10)},
        {"voltage": 5, "current": 2.0, "apps": "快充适配器", "power_range": (5, 15)},
        {"voltage": 5, "current": 2.4, "apps": "平板充电器", "power_range": (10, 20)},
        # 12V应用
        {"voltage": 12, "current": 0.5, "apps": "小功率LED", "power_range": (0, 10)},
        {"voltage": 12, "current": 1.0, "apps": "监控电源", "power_range": (5, 20)},
        {"voltage": 12, "current": 2.0, "apps": "路由器电源", "power_range": (10, 30)},
        {"voltage": 12, "current": 3.0, "apps": "硬盘电源", "power_range": (20, 40)},
        {"voltage": 12, "current": 5.0, "apps": "工业电源", "power_range": (40, 80)},
        # 24V应用
        {"voltage": 24, "current": 0.5, "apps": "传感器电源", "power_range": (5, 20)},
        {"voltage": 24, "current": 1.0, "apps": "PLC电源", "power_range": (10, 30)},
        {"voltage": 24, "current": 2.0, "apps": "工业控制", "power_range": (30, 60)},
        {"voltage": 24, "current": 3.0, "apps": "电机驱动", "power_range": (50, 100)},
        # 其他电压
        {"voltage": 3.3, "current": 1.0, "apps": "单片机电源", "power_range": (0, 5)},
        {"voltage": 9, "current": 1.0, "apps": "音响电源", "power_range": (5, 15)},
        {"voltage": 15, "current": 1.0, "apps": "仪器电源", "power_range": (10, 25)},
        {"voltage": 36, "current": 1.0, "apps": "通信电源", "power_range": (20, 50)},
        {"voltage": 48, "current": 1.0, "apps": "POE电源", "power_range": (30, 60)},
    ]

    # 为每个AC-DC芯片生成多个设计
    for chip in acdc_chips:
        chip_info = CHIP_DATABASE.get(chip)
        if not chip_info:
            continue

        max_power = chip_info.max_power

        for spec in acdc_output_specs:
            power = spec["voltage"] * spec["current"]

            # 只生成芯片功率范围内的设计
            if power <= max_power * 0.9:  # 留10%余量
                # 选择合适的外围器件
                components = select_acdc_components(chip, spec, power)

                design = {
                    "name": f"{spec['voltage']}V{spec['current']}A_{spec['apps']}_{chip}",
                    "chip": chip,
                    "topology": "FLYBACK",
                    "input": {"min": 85, "max": 265, "type": "AC"},
                    "output": {
                        "voltage": spec["voltage"],
                        "current": spec["current"],
                        "power": power,
                    },
                    "features": [
                        "隔离",
                        chip_info.features[0] if chip_info.features else "宽电压输入",
                    ],
                    "components": components,
                    "application": spec["apps"],
                }
                designs.append(design)

    # ========== DC-DC Buck设计 ==========
    buck_chips = ["MP1584", "LM2596", "MP2307", "XL4015"]

    buck_input_specs = [
        {"vin_min": 7, "vin_max": 24, "desc": "12V系统"},
        {"vin_min": 12, "vin_max": 36, "desc": "24V系统"},
        {"vin_min": 18, "vin_max": 36, "desc": "工业24V"},
        {"vin_min": 7, "vin_max": 40, "desc": "宽压输入"},
    ]

    buck_output_specs = [
        # 3.3V输出
        {"vout": 3.3, "current": 0.5, "apps": "MCU电源"},
        {"vout": 3.3, "current": 1.0, "apps": "单片机供电"},
        {"vout": 3.3, "current": 2.0, "apps": "树莓派供电"},
        {"vout": 3.3, "current": 3.0, "apps": "嵌入式系统"},
        # 5V输出
        {"vout": 5, "current": 0.5, "apps": "小功率5V"},
        {"vout": 5, "current": 1.0, "apps": "标准5V"},
        {"vout": 5, "current": 2.0, "apps": "USB供电"},
        {"vout": 5, "current": 3.0, "apps": "多USB口"},
        {"vout": 5, "current": 5.0, "apps": "大功率5V"},
        # 9V输出
        {"vout": 9, "current": 1.0, "apps": "音响9V"},
        {"vout": 9, "current": 2.0, "apps": "功放供电"},
        # 12V输出
        {"vout": 12, "current": 0.5, "apps": "小功率12V"},
        {"vout": 12, "current": 1.0, "apps": "标准12V"},
        {"vout": 12, "current": 2.0, "apps": "风扇供电"},
        {"vout": 12, "current": 3.0, "apps": "LED驱动"},
        {"vout": 12, "current": 5.0, "apps": "电机12V"},
        # 可调输出
        {"vout": "1.25-35", "current": 2.0, "apps": "可调电源"},
        {"vout": "1.25-35", "current": 3.0, "apps": "实验室电源"},
        {"vout": "1.25-35", "current": 5.0, "apps": "大功率可调"},
    ]

    for chip in buck_chips:
        chip_info = CHIP_DATABASE.get(chip)
        if not chip_info:
            continue

        for vin_spec in buck_input_specs:
            # 检查输入电压范围是否支持
            if vin_spec["vin_max"] > chip_info.input_voltage[1]:
                continue

            for vout_spec in buck_output_specs:
                # 计算功率
                if isinstance(vout_spec["vout"], str):
                    # 可调输出，使用典型值
                    vout_typ = 12.0
                else:
                    vout_typ = vout_spec["vout"]

                power = vout_typ * vout_spec["current"]

                # 检查功率限制
                if power > chip_info.max_power * 0.9:
                    continue

                # 检查输入输出压差
                if vin_spec["vin_min"] <= vout_typ * 1.5:  # 需要足够压差
                    continue

                components = select_buck_components(chip, vout_spec, vin_spec)

                design = {
                    "name": f"Buck_{vout_spec['vout']}V{vout_spec['current']}A_{chip}_{vin_spec['desc']}",
                    "chip": chip,
                    "topology": "BUCK",
                    "input": {
                        "min": vin_spec["vin_min"],
                        "max": vin_spec["vin_max"],
                        "type": "DC",
                    },
                    "output": {
                        "voltage": vout_spec["vout"],
                        "current": vout_spec["current"],
                        "power": power,
                    },
                    "features": ["非隔离", "高效率", "Buck降压"],
                    "components": components,
                    "application": vout_spec["apps"],
                }
                designs.append(design)

    # ========== DC-DC Boost设计 ==========
    boost_chips = ["MT3608", "XL6009"]

    boost_input_specs = [
        {"vin_min": 2, "vin_max": 12, "desc": "锂电池"},
        {"vin_min": 5, "vin_max": 12, "desc": "USB/5V"},
        {"vin_min": 12, "vin_max": 24, "desc": "12V系统"},
    ]

    boost_output_specs = [
        {"vout": 5, "current": 1.0, "apps": "5V升压"},
        {"vout": 9, "current": 1.0, "apps": "9V升压"},
        {"vout": 12, "current": 0.5, "apps": "12V小功率"},
        {"vout": 12, "current": 1.0, "apps": "12V标准"},
        {"vout": 12, "current": 2.0, "apps": "12V大功率"},
        {"vout": 24, "current": 0.5, "apps": "24V升压"},
        {"vout": 24, "current": 1.0, "apps": "24V工业"},
    ]

    for chip in boost_chips:
        chip_info = CHIP_DATABASE.get(chip)
        if not chip_info:
            continue

        for vin_spec in boost_input_specs:
            if vin_spec["vin_max"] > chip_info.input_voltage[1]:
                continue

            for vout_spec in boost_output_specs:
                power = vout_spec["vout"] * vout_spec["current"]

                if power > chip_info.max_power * 0.9:
                    continue

                # 确保升压有效
                if vout_spec["vout"] <= vin_spec["vin_max"]:
                    continue

                components = select_boost_components(chip, vout_spec, vin_spec)

                design = {
                    "name": f"Boost_{vout_spec['vout']}V{vout_spec['current']}A_{chip}_{vin_spec['desc']}",
                    "chip": chip,
                    "topology": "BOOST",
                    "input": {
                        "min": vin_spec["vin_min"],
                        "max": vin_spec["vin_max"],
                        "type": "DC",
                    },
                    "output": {
                        "voltage": vout_spec["vout"],
                        "current": vout_spec["current"],
                        "power": power,
                    },
                    "features": ["非隔离", "升压", "DC-DC"],
                    "components": components,
                    "application": vout_spec["apps"],
                }
                designs.append(design)

    return designs


def select_acdc_components(chip: str, spec: Dict, power: float) -> Dict:
    """为AC-DC设计选择合适的外围器件"""

    voltage = spec["voltage"]
    current = spec["current"]

    # 整流桥选择
    if power <= 10:
        bridge = "MB6S"
    elif power <= 30:
        bridge = "KBP307"
    else:
        bridge = "GBU606"

    # 输入电容选择
    if power <= 5:
        input_cap = "10uF/400V"
    elif power <= 15:
        input_cap = "22uF/400V"
    elif power <= 40:
        input_cap = "47uF/400V"
    else:
        input_cap = "100uF/400V"

    # 输出二极管选择
    if voltage <= 12:
        if current <= 1:
            output_diode = "SS34"
        elif current <= 3:
            output_diode = "SS54"
        else:
            output_diode = "MBR20100"
    elif voltage <= 24:
        if current <= 1:
            output_diode = "BYW100"
        elif current <= 3:
            output_diode = "MUR420"
        else:
            output_diode = "MBR20200"
    else:
        output_diode = "MUR460"

    # 输出电容选择
    cap_voltage = voltage * 1.5
    if cap_voltage < 10:
        cap_voltage = 10
    elif cap_voltage < 16:
        cap_voltage = 16
    elif cap_voltage < 25:
        cap_voltage = 25
    elif cap_voltage < 35:
        cap_voltage = 35
    else:
        cap_voltage = 50

    if current <= 1:
        output_cap = f"470uF/{cap_voltage}V"
    elif current <= 3:
        output_cap = f"1000uF/{cap_voltage}V"
    else:
        output_cap = f"2200uF/{cap_voltage}V"

    # MOSFET选择 (UC384x系列需要外置MOSFET)
    mosfet = None
    if "UC384" in chip or "TL494" in chip:
        if power <= 30:
            mosfet = "4N60"
        elif power <= 60:
            mosfet = "7N65"
        else:
            mosfet = "12N65"

    components = {
        "bridge": bridge,
        "input_cap": input_cap,
        "output_diode": output_diode,
        "output_cap": output_cap,
        "feedback": "PC817+TL431",
    }

    if mosfet:
        components["mosfet"] = mosfet

    return components


def select_buck_components(chip: str, vout_spec: Dict, vin_spec: Dict) -> Dict:
    """为Buck设计选择外围器件"""

    vout = vout_spec["vout"]
    current = vout_spec["current"]

    # 电感选择 (简化计算)
    if isinstance(vout, str):
        inductor = "33uH"
    elif vout <= 3.3:
        inductor = "10uH" if current <= 2 else "22uH"
    elif vout <= 5:
        inductor = "15uH" if current <= 2 else "33uH"
    elif vout <= 9:
        inductor = "22uH" if current <= 2 else "47uH"
    else:
        inductor = "33uH" if current <= 2 else "68uH"

    # 输入电容
    if vin_spec["vin_max"] <= 16:
        input_cap = "22uF/25V"
    elif vin_spec["vin_max"] <= 35:
        input_cap = "22uF/50V"
    else:
        input_cap = "10uF/100V"

    # 输出电容
    if current <= 1:
        output_cap = "22uF/25V"
    elif current <= 3:
        output_cap = "22uF/25V x2"
    else:
        output_cap = "47uF/25V x2"

    # 肖特基二极管
    if current <= 1:
        schottky = "SS14"
    elif current <= 3:
        schottky = "SS34"
    else:
        schottky = "SS54"

    return {
        "inductor": inductor,
        "input_cap": input_cap,
        "output_cap": output_cap,
        "schottky": schottky,
    }


def select_boost_components(chip: str, vout_spec: Dict, vin_spec: Dict) -> Dict:
    """为Boost设计选择外围器件"""

    vout = vout_spec["vout"]
    current = vout_spec["current"]

    # 电感选择
    if vout <= 9:
        inductor = "10uH"
    elif vout <= 12:
        inductor = "22uH"
    elif vout <= 24:
        inductor = "33uH"
    else:
        inductor = "47uH"

    # 输入电容
    input_cap = "22uF/25V"

    # 输出电容
    if vout <= 12:
        output_cap = "22uF/25V"
    else:
        output_cap = "22uF/50V"

    # 肖特基
    if current <= 1:
        schottky = "SS34"
    else:
        schottky = "SS54"

    # MOSFET (XL6009内置)
    mosfet = None
    if chip == "MT3608":
        mosfet = "外置MOS"

    components = {
        "inductor": inductor,
        "input_cap": input_cap,
        "output_cap": output_cap,
        "schottky": schottky,
    }

    if mosfet:
        components["mosfet"] = mosfet

    return components


def get_all_designs() -> List[Dict]:
    """获取所有设计方案"""
    return generate_extended_designs()


if __name__ == "__main__":
    designs = generate_extended_designs()
    print(f"生成了 {len(designs)} 个设计方案")
    print(f"\n按拓扑分类:")

    flyback = [d for d in designs if d["topology"] == "FLYBACK"]
    buck = [d for d in designs if d["topology"] == "BUCK"]
    boost = [d for d in designs if d["topology"] == "BOOST"]

    print(f"  反激式 (AC-DC): {len(flyback)} 个")
    print(f"  Buck (DC-DC): {len(buck)} 个")
    print(f"  Boost (DC-DC): {len(boost)} 个")

    print(f"\n按芯片分类:")
    from collections import Counter

    chip_counts = Counter(d["chip"] for d in designs)
    for chip, count in chip_counts.most_common():
        print(f"  {chip}: {count} 个设计")
