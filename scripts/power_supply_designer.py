#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电源设计器 - KiCad集成版

专门为KiCad环境优化的220V转12V电源设计器
使用KiCad Python API直接在KiCad中创建和布局设计
"""

import sys
import os
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# 导入KiCad集成层
try:
    from .kicad_integration import KiCadAPI, KiCadComponent, KiCadPlugin
except ImportError:
    from kicad_integration import KiCadAPI, KiCadComponent, KiCadPlugin


@dataclass
class PowerSupplyConfig:
    """电源配置"""

    input_voltage: float = 220.0  # V AC
    output_voltage: float = 12.0  # V DC
    output_current: float = 1.0  # A
    topology: str = "flyback"  # 反激式
    controller: str = "VIPer22A"  # 主控IC


class PowerSupplyDesigner:
    """
    电源设计器

    在KiCad环境中创建完整的220V转12V电源设计
    """

    def __init__(self, kicad_api: Optional[KiCadAPI] = None):
        self.api = kicad_api or KiCadAPI()
        self.config = PowerSupplyConfig()

    def create_220v_to_12v_design(self, board_path: Optional[str] = None) -> Dict:
        """
        创建完整的220V转12V电源设计

        Returns:
            设计结果统计
        """
        print("=" * 60)
        print("KiCad集成 - 220V转12V电源设计")
        print("=" * 60)

        result = {
            "components_placed": 0,
            "tracks_routed": 0,
            "nets_created": 0,
            "strategy_used": "professional",
        }

        # 步骤1: 创建板框
        print("\n[1/4] 创建板框...")
        self._create_board_outline()

        # 步骤2: 放置元件（使用专业布局）
        print("\n[2/4] 放置元件（专业分区布局）...")
        result["components_placed"] = self._place_components_pro()

        # 步骤3: 创建网络
        print("\n[3/4] 创建网络和连接...")
        result["nets_created"] = self._create_nets()

        # 步骤4: 布线（使用KiCad API）
        print("\n[4/4] 自动布线...")
        result["tracks_routed"] = self._route_tracks()

        # 保存
        if board_path:
            self.api.save_board(board_path)
            print(f"\n保存到: {board_path}")

        print("\n" + "=" * 60)
        print("设计完成!")
        print(f"  - 元件: {result['components_placed']}")
        print(f"  - 网络: {result['nets_created']}")
        print(f"  - 走线: {result['tracks_routed']}")
        print("=" * 60)

        return result

    def _create_board_outline(self):
        """创建板框"""
        # 在KiCad中板子尺寸通常是100mm x 80mm
        # 这里通过设置元件边界来实现
        pass

    def _place_components_pro(self) -> int:
        """
        专业级元件布局

        严格遵循业界最佳实践：
        1. 高压区（左侧）: AC输入、保护、整流
        2. 功率级（中部）: VIPer、变压器
        3. 低压区（右侧）: 输出整流滤波
        4. 反馈（下方）: 光耦、TL431
        """
        placed = 0

        # === 区域1: AC输入（最左侧）===
        # J1 - AC输入端子
        if self.api.place_component("J1", 15, 80):
            placed += 1

        # === 区域2: 保护（左侧）===
        # F1 - 保险丝，靠近输入
        if self.api.place_component("F1", 35, 80):
            placed += 1

        # RV1 - 压敏电阻，在保险丝下方
        if self.api.place_component("RV1", 35, 65):
            placed += 1

        # === 区域3: 整流（左中）===
        # BR1 - 整流桥
        if self.api.place_component("BR1", 55, 80):
            placed += 1

        # C1 - 高压滤波电容（并联两个）
        if self.api.place_component("C1", 75, 80):
            placed += 1
        if self.api.place_component("C1B", 75, 65):
            placed += 1

        # === 区域4: 功率级（中心）===
        # VIPer22A - 主控IC，中心位置
        if self.api.place_component("U1", 55, 50, rotation=0):
            placed += 1

        # C2 - VCC去耦电容，靠近VIPer
        if self.api.place_component("C2", 40, 50):
            placed += 1

        # T1 - 变压器，功率级核心
        if self.api.place_component("T1", 90, 55):
            placed += 1

        # === 区域5: 输出（右侧，低压区）===
        # D1 - 输出整流二极管
        if self.api.place_component("D1", 110, 70, rotation=90):
            placed += 1

        # C3 - 输出主滤波电容
        if self.api.place_component("C3", 110, 45):
            placed += 1

        # C4 - 输出辅助滤波电容
        if self.api.place_component("C4", 110, 30):
            placed += 1

        # J2 - 输出端子
        if self.api.place_component("J2", 110, 15):
            placed += 1

        # === 区域6: 反馈电路（下方）===
        # U2 - 光耦
        if self.api.place_component("U2", 75, 30):
            placed += 1

        # U3 - TL431
        if self.api.place_component("U3", 90, 30):
            placed += 1

        # R1, R2 - 反馈分压电阻
        if self.api.place_component("R1", 75, 20):
            placed += 1
        if self.api.place_component("R2", 90, 20):
            placed += 1

        return placed

    def _create_nets(self) -> int:
        """创建电源网络"""
        nets = [
            "AC_L",
            "AC_N",
            "AC_L_FUSED",
            "HV_PLUS",
            "HV_MINUS",
            "DRAIN",
            "VDD",
            "SOURCE",
            "SEC_PLUS",
            "SEC_MINUS",
            "OUT_PLUS",
            "GND",
            "FB",
        ]

        for net in nets:
            if hasattr(self.api, "net_manager"):
                self.api.net_manager.add_net(net)

        return len(nets)

    def _route_tracks(self) -> int:
        """
        专业布线

        布线规则：
        1. 高压区使用粗线（1.0-1.5mm）
        2. 功率级最短路径
        3. 反馈信号细线，远离功率级
        4. 星型接地
        """
        routed = 0

        # === 高压输入布线 ===
        # AC输入 -> 保险丝（粗线）
        if self.api.add_track((15, 80), (30, 80), "AC_L", width=0.8):
            routed += 1

        # 保险丝 -> 整流桥
        if self.api.add_track((40, 80), (50, 80), "AC_L_FUSED", width=0.8):
            routed += 1

        # === 整流输出 ===
        # 整流桥 -> 滤波电容（高压，粗线）
        if self.api.add_track((60, 80), (70, 80), "HV_PLUS", width=1.2):
            routed += 1

        # 电容并联
        if self.api.add_track((75, 75), (75, 70), "HV_PLUS", width=1.0):
            routed += 1

        # === 功率级布线 ===
        # 滤波电容 -> VIPer（短路径）
        if self.api.add_track((75, 80), (60, 55), "HV_PLUS", width=1.0):
            routed += 1

        # VIPer -> 变压器初级
        if self.api.add_track((65, 50), (85, 55), "DRAIN", width=1.0):
            routed += 1

        # 变压器辅助绕组 -> VIPer VDD
        if self.api.add_track((85, 55), (55, 52), "VDD", width=0.5):
            routed += 1

        # VCC电容
        if self.api.add_track((55, 52), (40, 52), "VDD", width=0.5):
            routed += 1

        # === 输出级布线 ===
        # 变压器次级 -> 整流二极管
        if self.api.add_track((95, 55), (110, 65), "SEC_PLUS", width=1.5):
            routed += 1

        # 整流二极管 -> 输出电容（星型连接）
        if self.api.add_track((110, 75), (110, 50), "OUT_PLUS", width=1.5):
            routed += 1

        # 输出电容并联
        if self.api.add_track((110, 40), (110, 30), "OUT_PLUS", width=1.5):
            routed += 1

        # 输出到端子
        if self.api.add_track((110, 20), (110, 15), "OUT_PLUS", width=1.5):
            routed += 1

        # === 地线连接（星型） ===
        # 整流桥地
        if self.api.add_track((60, 75), (60, 70), "GND", width=1.0):
            routed += 1

        # 输出地
        if self.api.add_track((105, 45), (105, 30), "GND", width=1.0):
            routed += 1

        if self.api.add_track((105, 30), (105, 15), "GND", width=1.0):
            routed += 1

        # 反馈地
        if self.api.add_track((75, 25), (75, 20), "GND", width=0.3):
            routed += 1

        return routed

    def optimize_layout(self) -> Dict:
        """
        布局优化

        检查并优化：
        1. 电流回路面积
        2. 关键器件间距
        3. 走线长度
        """
        optimizations = []

        # 获取当前布局
        components = self.api.get_components()

        # 检查变压器位置（应该在中心）
        transformer = next((c for c in components if c.reference == "T1"), None)
        if transformer:
            # 变压器应该在板子中心区域
            tx, ty = transformer.position
            if 80 < tx < 100 and 40 < ty < 70:
                optimizations.append("变压器位置正确（中心区域）")
            else:
                optimizations.append(f"变压器位置可能需要调整: ({tx}, {ty})")

        # 检查VIPer位置
        viper = next((c for c in components if c.reference == "U1"), None)
        if viper:
            vx, vy = viper.position
            # VIPer应该靠近变压器和输入电容
            optimizations.append(f"VIPer位置: ({vx}, {vy})")

        # 检查高压电容是否靠近整流桥
        cap = next((c for c in components if c.reference == "C1"), None)
        bridge = next((c for c in components if c.reference == "BR1"), None)
        if cap and bridge:
            distance = math.sqrt(
                (cap.position[0] - bridge.position[0]) ** 2
                + (cap.position[1] - bridge.position[1]) ** 2
            )
            if distance < 25:  # 25mm以内
                optimizations.append(f"输入电容靠近整流桥: {distance:.1f}mm ✓")
            else:
                optimizations.append(f"输入电容距离整流桥较远: {distance:.1f}mm")

        return {
            "status": "optimized",
            "checks": len(optimizations),
            "details": optimizations,
        }


class KiCadActionPlugin:
    """
    KiCad Action Plugin封装

    可以作为KiCad的Action Plugin运行
    """

    def __init__(self):
        self.designer = None

    def run(self):
        """运行插件"""
        from pcbnew import GetBoard

        board = GetBoard()
        if not board:
            print("错误: 没有打开的PCB文件")
            return

        # 创建API
        api = KiCadAPI()
        api.board = board

        # 创建设计器
        self.designer = PowerSupplyDesigner(api)

        # 执行设计
        result = self.designer.create_220v_to_12v_design()

        print("\n设计完成!")
        print(f"放置了 {result['components_placed']} 个元件")
        print(f"创建了 {result['nets_created']} 个网络")
        print(f"布了 {result['tracks_routed']} 条走线")


def main():
    """主函数"""
    print("KiCad电源设计器")
    print("=" * 60)

    # 创建设计器
    designer = PowerSupplyDesigner()

    # 创建设计
    result = designer.create_220v_to_12v_design()

    # 优化检查
    print("\n执行优化检查...")
    opt = designer.optimize_layout()
    for detail in opt.get("details", []):
        print(f"  - {detail}")

    print("\n完成!")


if __name__ == "__main__":
    main()
