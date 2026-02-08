"""
自动敷铜模块 - KiCad PCB 自动敷铜管理

功能:
- 自动创建铜箔区域 (Zones)
- GND/VCC 电源层自动敷铜
- 热焊盘处理
- 敷铜优先级管理
- 缝合过孔 (Via Stitching)

参考: KiCad 9.0 Zone Manager
"""

import logging
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CopperZone:
    """铜箔区域定义"""

    name: str
    net_name: str  # 关联网络 (如 GND, VCC)
    layer: str  # 层 (F.Cu, B.Cu, In1.Cu 等)
    priority: int = 0  # 优先级 (高优先级先填充)

    # 边界定义
    points: List[Tuple[float, float]] = field(default_factory=list)

    # 填充设置
    fill_style: str = "solid"  # solid/hatched
    min_thickness: float = 0.25  # 最小铜箔厚度

    # 间隙设置
    clearance: float = 0.5  # 与其他网络的间隙
    thermal_gap: float = 0.3  # 热焊盘间隙

    # 连接风格
    pad_connection: str = "thermal"  # thermal/direct/none
    thermal_width: float = 0.3  # 热焊盘连接宽度

    # 缝合过孔
    via_stitching: bool = False
    via_spacing: float = 2.0  # 过孔间距
    via_size: float = 0.6
    via_drill: float = 0.3


@dataclass
class ViaStitchingConfig:
    """缝合过孔配置"""

    enabled: bool = True
    net_name: str = "GND"
    via_size: float = 0.6
    via_drill: float = 0.3
    spacing: float = 2.54  # 过孔间距
    grid_pattern: str = "grid"  # grid/staggered
    layers: List[str] = field(default_factory=lambda: ["F.Cu", "B.Cu"])


class AutoCopperPour:
    """
    自动敷铜管理器

    自动创建和管理铜箔区域:
    1. 电源/地层自动敷铜
    2. 信号层局部敷铜
    3. 缝合过孔
    """

    def __init__(self, board_width: float = 100.0, board_height: float = 80.0):
        self.board_width = board_width
        self.board_height = board_height
        self.margin = 1.0  # 板边距
        self.zones: List[CopperZone] = []
        self.via_stitching_config = ViaStitchingConfig()

    def create_board_outline(
        self, width: Optional[float] = None, height: Optional[float] = None
    ) -> List[Tuple[float, float]]:
        """
        创建板框边界

        Args:
            width: 板宽 (默认使用 self.board_width)
            height: 板高

        Returns:
            List[Tuple[float, float]]: 边界点列表
        """
        w = width or self.board_width
        h = height or self.board_height
        m = self.margin

        return [
            (m, m),
            (w - m, m),
            (w - m, h - m),
            (m, h - m),
            (m, m),  # 闭合
        ]

    def add_ground_plane(
        self,
        layer: str = "F.Cu",
        priority: int = 1,
        keepout_areas: Optional[List[List[Tuple[float, float]]]] = None,
    ) -> CopperZone:
        """
        添加 GND 平面

        Args:
            layer: 层
            priority: 优先级
            keepout_areas: 禁区列表

        Returns:
            CopperZone: 创建的铜箔区域
        """
        zone = CopperZone(
            name=f"GND_Plane_{layer}",
            net_name="GND",
            layer=layer,
            priority=priority,
            points=self.create_board_outline(),
            fill_style="solid",
            clearance=0.5,
            thermal_gap=0.3,
            pad_connection="thermal",
            thermal_width=0.3,
        )

        self.zones.append(zone)
        logger.info(f"添加 GND 平面: {layer}")
        return zone

    def add_power_plane(
        self, net_name: str = "VCC", layer: str = "B.Cu", priority: int = 2
    ) -> CopperZone:
        """
        添加电源平面

        Args:
            net_name: 电源网络名称
            layer: 层
            priority: 优先级

        Returns:
            CopperZone: 创建的铜箔区域
        """
        zone = CopperZone(
            name=f"{net_name}_Plane_{layer}",
            net_name=net_name,
            layer=layer,
            priority=priority,
            points=self.create_board_outline(),
            fill_style="solid",
            clearance=0.6,  # 电源层间隙稍大
            thermal_gap=0.3,
            pad_connection="thermal",
            thermal_width=0.4,
        )

        self.zones.append(zone)
        logger.info(f"添加 {net_name} 平面: {layer}")
        return zone

    def add_signal_pour(
        self,
        net_name: str,
        points: List[Tuple[float, float]],
        layer: str = "F.Cu",
        priority: int = 0,
    ) -> CopperZone:
        """
        添加信号层局部敷铜

        Args:
            net_name: 网络名称
            points: 敷铜区域边界点
            layer: 层
            priority: 优先级

        Returns:
            CopperZone: 创建的铜箔区域
        """
        zone = CopperZone(
            name=f"Signal_{net_name}_{layer}",
            net_name=net_name,
            layer=layer,
            priority=priority,
            points=points,
            fill_style="solid",
            clearance=0.3,
            pad_connection="direct",  # 信号层通常直接连接
        )

        self.zones.append(zone)
        logger.info(f"添加信号敷铜: {net_name} on {layer}")
        return zone

    def create_split_power_plane(
        self, power_nets: List[str], layer: str = "In1.Cu"
    ) -> List[CopperZone]:
        """
        创建分割电源平面

        Args:
            power_nets: 电源网络列表 (如 ['3V3', '5V', '1V8'])
            layer: 内层

        Returns:
            List[CopperZone]: 创建的铜箔区域列表
        """
        zones = []
        zone_width = self.board_width / len(power_nets)

        for i, net in enumerate(power_nets):
            # 每个电源区域占一部分
            x_start = i * zone_width
            x_end = (i + 1) * zone_width

            points = [
                (x_start, self.margin),
                (x_end, self.margin),
                (x_end, self.board_height - self.margin),
                (x_start, self.board_height - self.margin),
                (x_start, self.margin),
            ]

            zone = CopperZone(
                name=f"Power_{net}",
                net_name=net,
                layer=layer,
                priority=i + 1,
                points=points,
                clearance=0.8,  # 分割平面间隙更大
                pad_connection="thermal",
            )

            zones.append(zone)
            self.zones.append(zone)

        logger.info(f"创建分割电源平面: {len(zones)} 个区域")
        return zones

    def generate_via_stitching(
        self, area: Optional[Tuple[float, float, float, float]] = None
    ) -> List[Dict]:
        """
        生成缝合过孔

        Args:
            area: 区域 (x1, y1, x2, y2)，None 表示整个板子

        Returns:
            List[Dict]: 过孔列表
        """
        if not self.via_stitching_config.enabled:
            return []

        cfg = self.via_stitching_config

        if area is None:
            x1, y1 = self.margin, self.margin
            x2, y2 = self.board_width - self.margin, self.board_height - self.margin
        else:
            x1, y1, x2, y2 = area

        vias = []
        spacing = cfg.spacing

        # 计算网格
        cols = int((x2 - x1) / spacing)
        rows = int((y2 - y1) / spacing)

        for row in range(rows):
            for col in range(cols):
                x = x1 + col * spacing
                y = y1 + row * spacing

                # 交错模式
                if cfg.grid_pattern == "staggered" and row % 2 == 1:
                    x += spacing / 2

                via = {
                    "x": x,
                    "y": y,
                    "net": cfg.net_name,
                    "size": cfg.via_size,
                    "drill": cfg.via_drill,
                    "layers": cfg.layers,
                }
                vias.append(via)

        logger.info(f"生成缝合过孔: {len(vias)} 个")
        return vias

    def generate_zone_sexpr(self, zone: CopperZone) -> str:
        """
        生成 KiCad S-expression 格式的 zone 定义

        Args:
            zone: 铜箔区域

        Returns:
            str: S-expression 字符串
        """
        lines = []

        lines.append(
            f'  (zone (net 0) (net_name "{zone.net_name}") (layer "{zone.layer}") (tstamp "")'
        )
        lines.append(f"    (hatch edge {zone.min_thickness})")
        lines.append(f"    (priority {zone.priority})")

        # 连接设置
        if zone.pad_connection == "thermal":
            lines.append(
                "    (connect_pads (yes) (thermal_bridge_width {}) (thermal_bridge_angle 45))".format(
                    zone.thermal_width
                )
            )
        elif zone.pad_connection == "direct":
            lines.append("    (connect_pads (yes) (clearance 0))")
        else:
            lines.append("    (connect_pads (no))")

        # 间隙
        lines.append(f"    (min_thickness {zone.min_thickness})")
        lines.append(f"    (filled_areas_thickness no)")
        lines.append(
            f"    (fill (thermal_gap {zone.thermal_gap}) (thermal_bridge_width {zone.thermal_width}))"
        )

        # 多边形边界
        lines.append("    (polygon")
        lines.append("      (pts")
        for x, y in zone.points:
            lines.append(f"        (xy {x} {y})")
        lines.append("      )")
        lines.append("    )")

        lines.append("  )")

        return "\n".join(lines)

    def generate_all_zones(self) -> str:
        """
        生成所有铜箔区域的 S-expression

        Returns:
            str: 完整的 zones 定义
        """
        all_zones = []

        # 按优先级排序
        sorted_zones = sorted(self.zones, key=lambda z: z.priority, reverse=True)

        for zone in sorted_zones:
            all_zones.append(self.generate_zone_sexpr(zone))

        return "\n".join(all_zones)

    def auto_setup_standard_board(
        self, layers: int = 2, power_nets: Optional[List[str]] = None
    ) -> Dict:
        """
        自动设置标准板子的敷铜

        Args:
            layers: 层数 (2 或 4)
            power_nets: 电源网络列表

        Returns:
            Dict: 包含所有敷铜配置
        """
        result = {"zones": [], "vias": [], "recommendations": []}

        if layers == 2:
            # 双层板: 顶层 GND，底层 VCC (或混合)
            self.add_ground_plane("F.Cu", priority=1)
            if power_nets:
                self.add_power_plane(power_nets[0], "B.Cu", priority=2)
            else:
                self.add_ground_plane("B.Cu", priority=1)

            result["recommendations"].append("双层板: 顶层和底层都铺 GND")

        elif layers == 4:
            # 四层板: 内层为完整的电源/地层
            self.add_ground_plane("In1.Cu", priority=2)

            if power_nets:
                self.create_split_power_plane(power_nets, "In2.Cu")
            else:
                self.add_power_plane("VCC", "In2.Cu", priority=2)

            # 顶层和底层也铺 GND
            self.add_ground_plane("F.Cu", priority=1)
            self.add_ground_plane("B.Cu", priority=1)

            result["recommendations"].append("四层板: 内层为完整电源/地平面")

        # 生成缝合过孔
        vias = self.generate_via_stitching()

        result["zones"] = self.zones
        result["vias"] = vias

        logger.info(f"标准板敷铜设置完成: {len(self.zones)} 个区域, {len(vias)} 个过孔")
        return result

    def get_zone_summary(self) -> str:
        """获取敷铜摘要"""
        lines = ["=" * 50]
        lines.append("自动敷铜配置摘要")
        lines.append("=" * 50)

        for zone in self.zones:
            lines.append(f"\n区域: {zone.name}")
            lines.append(f"  网络: {zone.net_name}")
            lines.append(f"  层: {zone.layer}")
            lines.append(f"  优先级: {zone.priority}")
            lines.append(f"  连接方式: {zone.pad_connection}")

        if self.via_stitching_config.enabled:
            lines.append(f"\n缝合过孔:")
            lines.append(f"  网络: {self.via_stitching_config.net_name}")
            lines.append(f"  间距: {self.via_stitching_config.spacing} mm")

        lines.append("=" * 50)
        return "\n".join(lines)


def quick_copper_setup(
    board_width: float, board_height: float, layers: int = 2, gnd_on_top: bool = True
) -> AutoCopperPour:
    """
    快速敷铜设置

    Args:
        board_width: 板宽
        board_height: 板高
        layers: 层数
        gnd_on_top: 顶层是否铺 GND

    Returns:
        AutoCopperPour: 配置好的敷铜管理器
    """
    manager = AutoCopperPour(board_width, board_height)

    if layers >= 2:
        if gnd_on_top:
            manager.add_ground_plane("F.Cu", priority=1)
        manager.add_ground_plane("B.Cu", priority=1)

    if layers >= 4:
        manager.add_ground_plane("In1.Cu", priority=2)
        manager.add_power_plane("VCC", "In2.Cu", priority=2)

    return manager


if __name__ == "__main__":
    # 测试示例
    print("\n" + "=" * 60)
    print("自动敷铜模块测试")
    print("=" * 60)

    # 双层板示例
    manager2 = AutoCopperPour(100, 80)
    manager2.auto_setup_standard_board(layers=2)
    print(manager2.get_zone_summary())

    # 四层板示例
    print("\n" + "=" * 60)
    manager4 = AutoCopperPour(100, 80)
    manager4.auto_setup_standard_board(layers=4, power_nets=["3V3", "5V"])
    print(manager4.get_zone_summary())
