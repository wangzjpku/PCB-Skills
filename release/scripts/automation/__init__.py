"""
KiCad PCB 自动化工具包

集成三个核心功能:
1. 自动布局 (Auto Layout) - auto_layout.py
2. 自动布线 (Auto Router) - auto_router.py
3. 自动敷铜 (Auto Copper Pour) - auto_copper.py

基于 GitHub 开源项目:
- snhobbs/kicad-parts-placer (布局)
- mcbridejc/kicad_component_layout (布局)
- freerouting/freerouting (布线)

使用方法:
    from scripts.automation import AutoPCBToolkit

    toolkit = AutoPCBToolkit(board_width=100, board_height=80)

    # 1. 自动布局
    toolkit.auto_layout(components, method="schematic")

    # 2. 自动布线
    toolkit.auto_route(nets, use_freerouting=True)

    # 3. 自动敷铜
    toolkit.auto_copper(layers=2, power_nets=['GND', 'VCC'])
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# 导入子模块
from .auto_layout import AutoLayoutEngine, create_smart_layout
from .auto_router import FreeRoutingBridge, SimpleRouter, quick_autoroute
from .auto_copper import AutoCopperPour, quick_copper_setup
from .freerouting_integration import (
    FreeRoutingIntegration,
    RouterConfig,
    DesignRules,
    SimpleAutorouter,
)

logger = logging.getLogger(__name__)

__all__ = [
    "AutoPCBToolkit",
    "AutoLayoutEngine",
    "FreeRoutingBridge",
    "AutoCopperPour",
    "FreeRoutingIntegration",
    "RouterConfig",
    "DesignRules",
    "SimpleAutorouter",
]


class AutoPCBToolkit:
    """
    KiCad PCB 自动化工具包主类

    一站式解决方案，集成布局、布线、敷铜三大功能。
    """

    def __init__(
        self,
        board_width: float = 100.0,
        board_height: float = 80.0,
        output_dir: str = "./output",
    ):
        """
        初始化自动化工具包

        Args:
            board_width: PCB 宽度 (mm)
            board_height: PCB 高度 (mm)
            output_dir: 输出目录
        """
        self.board_width = board_width
        self.board_height = board_height
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化子模块
        self.layout_engine = AutoLayoutEngine(board_width, board_height)
        self.router = FreeRoutingIntegration()
        self.copper_manager = AutoCopperPour(board_width, board_height)

        # 设计数据
        self.components: List[Dict] = []
        self.nets: List[Dict] = []
        self.tracks: List[Dict] = []

        logger.info(f"AutoPCBToolkit 初始化完成: {board_width}x{board_height}mm")

    def load_design(
        self, components: List[Dict], nets: Optional[List[Dict]] = None
    ) -> None:
        """
        加载设计数据

        Args:
            components: 元件列表 [{ref, x, y, footprint, layer, ...}]
            nets: 网络列表 [{name, pins: [{ref, pin}]}]
        """
        self.components = components
        self.nets = nets or []

        logger.info(f"加载设计数据: {len(components)} 个元件, {len(self.nets)} 个网络")

    def auto_layout(
        self, method: str = "schematic", optimize: bool = True
    ) -> Dict[str, Tuple[float, float]]:
        """
        自动布局

        Args:
            method: 布局方法 (schematic/grid/linear)
            optimize: 是否优化布局

        Returns:
            Dict: 元件位置映射 {ref: (x, y)}
        """
        logger.info(f"开始自动布局: 方法={method}")

        # 使用布局引擎
        engine = create_smart_layout(
            self.components, self.board_width, self.board_height, layout_type=method
        )

        if optimize:
            engine.optimize_placement()

        positions = engine.get_all_positions()

        # 更新元件位置
        for comp in self.components:
            ref = comp.get("ref")
            if ref in positions:
                comp["x"], comp["y"] = positions[ref]

        # 保存布局 YAML
        yaml_file = self.output_dir / "auto_layout.yaml"
        engine.generate_layout_yaml(str(yaml_file))

        logger.info(f"自动布局完成: {len(positions)} 个元件")
        return positions

    def auto_route(
        self,
        method: str = "simple",
        ignore_nets: Optional[List[str]] = None,
        use_freerouting: bool = False,
    ) -> List[Dict]:
        """
        自动布线

        Args:
            method: 布线方法 (simple/freerouting)
            ignore_nets: 忽略的网络 (如 ['GND'])
            use_freerouting: 是否使用 FreeRouting

        Returns:
            List[Dict]: 走线列表
        """
        logger.info(f"开始自动布线: 方法={method}")

        if use_freerouting and self.router.is_available():
            # 使用 FreeRouting
            board_outline = [
                (0, 0),
                (self.board_width, 0),
                (self.board_width, self.board_height),
                (0, self.board_height),
                (0, 0),
            ]

            result = self.router.autoroute(
                board_outline=board_outline,
                components=self.components,
                nets=self.nets,
                output_dir=str(self.output_dir),
                ignore_nets=ignore_nets or [],
            )

            if result["success"]:
                self.tracks = result["tracks"]
                logger.info(f"FreeRouting 布线完成: {len(self.tracks)} 条走线")
            else:
                logger.error(f"FreeRouting 布线失败: {result['message']}")
        else:
            # 使用简单布线
            simple_router = SimpleAutorouter()
            self.tracks = simple_router.route_netlist(self.components, self.nets)
            logger.info(f"简单布线完成: {len(self.tracks)} 条走线")

        return self.tracks

    def auto_copper(
        self,
        layers: int = 2,
        power_nets: Optional[List[str]] = None,
        via_stitching: bool = True,
    ) -> Dict:
        """
        自动敷铜

        Args:
            layers: PCB 层数
            power_nets: 电源网络列表
            via_stitching: 是否添加缝合过孔

        Returns:
            Dict: 包含 zones 和 vias
        """
        logger.info(f"开始自动敷铜: {layers} 层板")

        # 重置铜箔管理器
        self.copper_manager = AutoCopperPour(self.board_width, self.board_height)

        # 启用缝合过孔
        self.copper_manager.via_stitching_config.enabled = via_stitching

        # 自动设置标准敷铜
        result = self.copper_manager.auto_setup_standard_board(
            layers=layers, power_nets=power_nets
        )

        logger.info(
            f"自动敷铜完成: {len(result['zones'])} 个区域, {len(result['vias'])} 个过孔"
        )
        return result

    def full_auto_design(
        self,
        components: List[Dict],
        nets: List[Dict],
        layers: int = 2,
        power_nets: Optional[List[str]] = None,
    ) -> Dict:
        """
        完整自动设计流程

        一键完成: 布局 -> 布线 -> 敷铜

        Args:
            components: 元件列表
            nets: 网络列表
            layers: PCB 层数
            power_nets: 电源网络列表

        Returns:
            Dict: 完整设计结果
        """
        logger.info("=" * 60)
        logger.info("开始完整自动设计流程")
        logger.info("=" * 60)

        # 1. 加载设计
        self.load_design(components, nets)

        # 2. 自动布局
        positions = self.auto_layout(method="schematic", optimize=True)

        # 3. 自动布线
        tracks = self.auto_route(method="simple")

        # 4. 自动敷铜
        copper = self.auto_copper(layers=layers, power_nets=power_nets)

        result = {
            "success": True,
            "positions": positions,
            "tracks": tracks,
            "zones": copper["zones"],
            "vias": copper["vias"],
            "recommendations": copper["recommendations"],
        }

        logger.info("=" * 60)
        logger.info("自动设计流程完成")
        logger.info(f"  元件数量: {len(positions)}")
        logger.info(f"  走线数量: {len(tracks)}")
        logger.info(f"  敷铜区域: {len(copper['zones'])}")
        logger.info(f"  缝合过孔: {len(copper['vias'])}")
        logger.info("=" * 60)

        return result

    def export_to_pcb(self, output_file: Optional[str] = None) -> str:
        """
        导出到 PCB 文件

        Args:
            output_file: 输出文件路径

        Returns:
            str: 输出文件路径
        """
        if output_file is None:
            output_file = str(self.output_dir / "autorouted_design.kicad_pcb")

        # 使用现有的 PCB 生成器
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from generators.pcb_generator import PCBFileGenerator, PCBComponent, PCBTrack

        pcb = PCBFileGenerator()
        pcb.set_board_properties(
            width=self.board_width, height=self.board_height, name="Auto Generated PCB"
        )

        # 添加元件
        for comp in self.components:
            pads = comp.get("pads", [])
            component = PCBComponent(
                ref=comp["ref"],
                footprint=comp.get("footprint", "R_0805"),
                value=comp.get("value", ""),
                position=(comp.get("x", 0), comp.get("y", 0)),
                orientation=comp.get("rotation", 0),
                layer=comp.get("layer", "F.Cu"),
                pads=pads,
            )
            pcb.add_component(component)

        # 添加走线
        for track in self.tracks:
            pcb.add_track(
                PCBTrack(
                    start=track["start"],
                    end=track["end"],
                    net=track.get("net", ""),
                    width=track.get("width", 0.25),
                    layer=track.get("layer", "F.Cu"),
                )
            )

        # 设置板框
        pcb.set_board_outline(
            [
                (5, 5),
                (self.board_width - 5, 5),
                (self.board_width - 5, self.board_height - 5),
                (5, self.board_height - 5),
                (5, 5),
            ]
        )

        # 保存
        pcb.save(output_file)
        logger.info(f"PCB 文件已导出: {output_file}")

        return output_file

    def get_summary(self) -> str:
        """获取设计摘要"""
        lines = []
        lines.append("=" * 60)
        lines.append("自动 PCB 设计摘要")
        lines.append("=" * 60)
        lines.append(f"板子尺寸: {self.board_width} x {self.board_height} mm")
        lines.append(f"元件数量: {len(self.components)}")
        lines.append(f"网络数量: {len(self.nets)}")
        lines.append(f"走线数量: {len(self.tracks)}")
        lines.append(f"敷铜区域: {len(self.copper_manager.zones)}")
        lines.append("=" * 60)
        return "\n".join(lines)


# 便捷函数
def quick_autopcb(
    components: List[Dict],
    nets: List[Dict],
    board_width: float = 100.0,
    board_height: float = 80.0,
    layers: int = 2,
) -> Dict:
    """
    快速自动 PCB 设计

    Args:
        components: 元件列表
        nets: 网络列表
        board_width: 板宽
        board_height: 板高
        layers: 层数

    Returns:
        Dict: 设计结果
    """
    toolkit = AutoPCBToolkit(board_width, board_height)
    return toolkit.full_auto_design(components, nets, layers)


if __name__ == "__main__":
    # 测试示例
    print("\n" + "=" * 70)
    print("KiCad PCB 自动化工具包测试")
    print("=" * 70)

    # 测试元件
    test_components = [
        {"ref": "R1", "value": "1k", "footprint": "R_0805"},
        {"ref": "R2", "value": "10k", "footprint": "R_0805"},
        {"ref": "C1", "value": "100nF", "footprint": "C_0805"},
        {"ref": "LED1", "value": "Red", "footprint": "LED_0805"},
        {"ref": "U1", "value": "MCU", "footprint": "QFN-32"},
    ]

    # 测试网络
    test_nets = [
        {"name": "GND", "pins": [{"ref": "R1", "pin": "2"}, {"ref": "C1", "pin": "2"}]},
        {"name": "VCC", "pins": [{"ref": "R1", "pin": "1"}, {"ref": "R2", "pin": "1"}]},
        {
            "name": "LED_NET",
            "pins": [{"ref": "R2", "pin": "2"}, {"ref": "LED1", "pin": "A"}],
        },
    ]

    # 运行完整自动化流程
    toolkit = AutoPCBToolkit(board_width=60, board_height=40)
    result = toolkit.full_auto_design(
        test_components, test_nets, layers=2, power_nets=["GND", "VCC"]
    )

    print("\n" + toolkit.get_summary())

    # 导出 PCB
    if result["success"]:
        pcb_file = toolkit.export_to_pcb()
        print(f"\n✓ PCB 文件已生成: {pcb_file}")
