"""
自动布局模块 - KiCad PCB 自动元件布局

基于 GitHub 项目:
- snhobbs/kicad-parts-placer
- mcbridejc/kicad_component_layout

cd
功能:
- 按原理图位置自动布局
- 基于分组/功能区域布局
- 网格对齐布局
"""

import sys
import os
import logging
import yaml
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ComponentPosition:
    """元件位置定义"""

    ref: str  # 参考位号
    x: float  # X坐标 (mm)
    y: float  # Y坐标 (mm)
    rotation: float = 0.0  # 旋转角度
    layer: str = "F.Cu"  # 层
    group: str = ""  # 所属分组


@dataclass
class LayoutGroup:
    """布局分组"""

    name: str
    components: List[str] = field(default_factory=list)
    position: Tuple[float, float] = (0.0, 0.0)
    spacing: float = 2.54  # 元件间距
    direction: str = "horizontal"  # horizontal/vertical/grid


class AutoLayoutEngine:
    """
    自动布局引擎

    提供多种布局算法:
    1. 原理图驱动布局 - 按原理图位置映射
    2. 分组布局 - 按功能分组布局
    3. 网格布局 - 网格对齐布局
    """

    def __init__(self, board_width: float = 100.0, board_height: float = 80.0):
        self.board_width = board_width
        self.board_height = board_height
        self.margin = 5.0  # 边距
        self.components: Dict[str, ComponentPosition] = {}
        self.groups: Dict[str, LayoutGroup] = {}

    def load_from_schematic_positions(self, sch_components: List[Dict]) -> None:
        """
        从原理图位置加载元件布局

        Args:
            sch_components: 原理图元件列表，每项包含 ref, x, y
        """
        # 计算原理图边界
        if not sch_components:
            return

        min_x = min(c.get("x", 0) for c in sch_components)
        max_x = max(c.get("x", 0) for c in sch_components)
        min_y = min(c.get("y", 0) for c in sch_components)
        max_y = max(c.get("y", 0) for c in sch_components)

        # 映射到PCB区域
        sch_width = max_x - min_x if max_x != min_x else 1
        sch_height = max_y - min_y if max_y != min_y else 1

        pcb_width = self.board_width - 2 * self.margin
        pcb_height = self.board_height - 2 * self.margin

        scale_x = pcb_width / sch_width if sch_width > 0 else 1
        scale_y = pcb_height / sch_height if sch_height > 0 else 1
        scale = min(scale_x, scale_y) * 0.8  # 留一些余量

        for comp in sch_components:
            ref = comp.get("ref", "")
            sch_x = comp.get("x", 0)
            sch_y = comp.get("y", 0)

            # 映射到PCB坐标
            pcb_x = self.margin + (sch_x - min_x) * scale
            pcb_y = self.margin + (sch_y - min_y) * scale

            self.components[ref] = ComponentPosition(
                ref=ref,
                x=pcb_x,
                y=pcb_y,
                rotation=comp.get("rotation", 0),
                layer=comp.get("layer", "F.Cu"),
            )

        logger.info(f"从原理图加载了 {len(self.components)} 个元件位置")

    def create_functional_groups(self, netlist: Dict[str, Any]) -> None:
        """
        基于网表创建功能分组

        Args:
            netlist: 网表数据，包含网络和元件连接关系
        """
        # 识别电源网络
        power_nets = {"GND", "VCC", "VDD", "3V3", "5V", "+5V", "+3.3V"}

        # 按电源网络分组
        power_components = set()
        for net_name, net_info in netlist.get("nets", {}).items():
            if any(power in net_name.upper() for power in power_nets):
                for ref in net_info.get("pins", {}).keys():
                    power_components.add(ref)

        if power_components:
            self.groups["power"] = LayoutGroup(
                name="power",
                components=list(power_components),
                position=(self.margin, self.margin),
                spacing=5.08,
                direction="grid",
            )

        # 可以添加更多分组逻辑：MCU组、连接器组等
        logger.info(f"创建了 {len(self.groups)} 个功能分组")

    def layout_grid(
        self,
        components: List[str],
        start_pos: Tuple[float, float] = (10, 10),
        cols: int = 5,
        spacing: float = 5.08,
    ) -> Dict[str, ComponentPosition]:
        """
        网格布局

        Args:
            components: 元件位号列表
            start_pos: 起始位置
            cols: 列数
            spacing: 间距

        Returns:
            Dict[str, ComponentPosition]: 元件位置映射
        """
        positions = {}
        x0, y0 = start_pos

        for i, ref in enumerate(components):
            col = i % cols
            row = i // cols

            x = x0 + col * spacing
            y = y0 + row * spacing

            positions[ref] = ComponentPosition(ref=ref, x=x, y=y, rotation=0)

        logger.info(f"网格布局: {len(components)} 个元件, {cols} 列")
        return positions

    def layout_linear(
        self,
        components: List[str],
        start_pos: Tuple[float, float] = (10, 10),
        direction: str = "horizontal",
        spacing: float = 5.08,
    ) -> Dict[str, ComponentPosition]:
        """
        线性布局

        Args:
            components: 元件位号列表
            start_pos: 起始位置
            direction: horizontal/vertical
            spacing: 间距

        Returns:
            Dict[str, ComponentPosition]: 元件位置映射
        """
        positions = {}
        x0, y0 = start_pos

        for i, ref in enumerate(components):
            if direction == "horizontal":
                x = x0 + i * spacing
                y = y0
            else:
                x = x0
                y = y0 + i * spacing

            positions[ref] = ComponentPosition(
                ref=ref, x=x, y=y, rotation=0 if direction == "horizontal" else 90
            )

        return positions

    def optimize_placement(self) -> None:
        """
        优化元件布局
        - 避免重叠
        - 最小化飞线交叉
        """
        # 简单的防重叠处理
        refs = list(self.components.keys())
        min_spacing = 2.0  # 最小间距

        for i, ref1 in enumerate(refs):
            comp1 = self.components[ref1]
            for ref2 in refs[i + 1 :]:
                comp2 = self.components[ref2]

                # 检查重叠
                dx = abs(comp1.x - comp2.x)
                dy = abs(comp1.y - comp2.y)

                if dx < min_spacing and dy < min_spacing:
                    # 推开元件
                    if dx < dy:
                        comp2.x += min_spacing
                    else:
                        comp2.y += min_spacing

    def generate_layout_yaml(self, output_file: str) -> bool:
        """
        生成布局 YAML 文件（兼容 mcbridejc/kicad_component_layout）

        Args:
            output_file: 输出文件路径

        Returns:
            bool: 是否成功
        """
        try:
            layout_data = {"origin": [0, 0], "components": {}}

            for ref, comp in self.components.items():
                layout_data["components"][ref] = {
                    "location": [round(comp.x, 2), round(comp.y, 2)],
                    "rotation": comp.rotation,
                    "flip": comp.layer == "B.Cu",
                }

            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(layout_data, f, allow_unicode=True, default_flow_style=False)

            logger.info(f"布局 YAML 已保存: {output_file}")
            return True

        except Exception as e:
            logger.error(f"生成布局 YAML 失败: {e}")
            return False

    def get_all_positions(self) -> Dict[str, Tuple[float, float]]:
        """获取所有元件位置"""
        return {ref: (comp.x, comp.y) for ref, comp in self.components.items()}


def create_smart_layout(
    components: List[Dict],
    board_width: float = 100.0,
    board_height: float = 80.0,
    layout_type: str = "schematic",
) -> AutoLayoutEngine:
    """
    创建智能布局

    Args:
        components: 元件列表
        board_width: 板宽
        board_height: 板高
        layout_type: 布局类型 (schematic/grid/linear)

    Returns:
        AutoLayoutEngine: 布局引擎实例
    """
    engine = AutoLayoutEngine(board_width, board_height)

    if layout_type == "schematic":
        engine.load_from_schematic_positions(components)
    elif layout_type == "grid":
        refs = [c["ref"] for c in components]
        positions = engine.layout_grid(refs, cols=int(math.sqrt(len(refs))))
        engine.components = positions
    elif layout_type == "linear":
        refs = [c["ref"] for c in components]
        positions = engine.layout_linear(refs)
        engine.components = positions

    engine.optimize_placement()
    return engine


if __name__ == "__main__":
    # 测试示例
    test_components = [
        {"ref": "R1", "x": 50, "y": 50},
        {"ref": "R2", "x": 60, "y": 50},
        {"ref": "C1", "x": 50, "y": 60},
        {"ref": "LED1", "x": 70, "y": 50},
    ]

    engine = create_smart_layout(test_components, layout_type="schematic")
    positions = engine.get_all_positions()

    print("布局结果:")
    for ref, pos in positions.items():
        print(f"  {ref}: ({pos[0]:.2f}, {pos[1]:.2f})")

    # 保存 YAML
    engine.generate_layout_yaml("test_layout.yaml")
