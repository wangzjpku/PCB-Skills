"""
增强版PCB文件生成器

大幅改进的版本，包含：
- 完整的封装定义（焊盘、丝印、装配层）
- 自动网络管理
- 智能连线系统
- 支持多种标准封装
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import logging
import uuid
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from footprint_lib import (
        Footprint,
        Pad,
        get_footprint,
        create_r_0805,
        create_c_elec_10x10,
        create_dip8,
        create_terminal_block_2p,
        create_d_bridge,
        create_transformer_ee25,
        create_d_schottky_to220,
        create_to92,
    )
except ImportError:
    logging.warning("footprint_lib not found, using basic footprints")

    @dataclass
    class Pad:
        number: str
        x: float
        y: float
        size_x: float
        size_y: float
        shape: str = "rect"
        layer: str = "F.Cu"
        drill: float = 0.0
        net: int = 0
        net_name: str = ""

    @dataclass
    class Footprint:
        name: str
        description: str
        pads: List[Pad]
        silkscreen: List[Dict] = field(default_factory=list)
        fab_layer: List[Dict] = field(default_factory=list)
        courtyard: List[Tuple[float, float]] = field(default_factory=list)


logger = logging.getLogger(__name__)


@dataclass
class PCBComponent:
    """PCB组件（封装实例）"""

    ref: str  # 参考位号（U1, R1, C1等）
    footprint_name: str  # 封装名称
    value: str  # 器件值
    position: Tuple[float, float]  # (x, y) in mm
    orientation: float = 0.0  # 旋转角度（度）
    layer: str = "F.Cu"
    footprint_data: Optional[Footprint] = None  # 封装定义数据

    def __post_init__(self):
        if self.footprint_data is None:
            # 尝试从库中加载
            self.footprint_data = get_footprint(self.footprint_name)


@dataclass
class PCBTrack:
    """PCB走线"""

    start: Tuple[float, float]  # 起点 (x, y)
    end: Tuple[float, float]  # 终点 (x, y)
    width: float = 0.25  # 宽度 in mm
    layer: str = "F.Cu"
    net: int = 0  # 网络编号
    net_name: str = ""  # 网络名称


@dataclass
class PCBVia:
    """PCB过孔"""

    position: Tuple[float, float]
    drill: float = 0.8
    size: float = 1.2
    net: int = 0
    net_name: str = ""


class NetManager:
    """网络管理器 - 自动管理网络名称和ID"""

    def __init__(self):
        self.nets: Dict[int, str] = {0: ""}  # net_id -> net_name
        self.net_names: Dict[str, int] = {"": 0}  # net_name -> net_id
        self.next_net_id: int = 1

    def add_net(self, name: str) -> int:
        """添加网络，返回网络ID"""
        if name in self.net_names:
            return self.net_names[name]

        net_id = self.next_net_id
        self.nets[net_id] = name
        self.net_names[name] = net_id
        self.next_net_id += 1
        return net_id

    def get_net_id(self, name: str) -> int:
        """获取网络ID（如果不存在则创建）"""
        return self.add_net(name)

    def get_net_name(self, net_id: int) -> str:
        """获取网络名称"""
        return self.nets.get(net_id, "")

    def list_nets(self) -> List[Tuple[int, str]]:
        """列出所有网络"""
        return sorted(self.nets.items())


class PCBFileGeneratorV2:
    """
    增强版PCB文件生成器

    新特性：
    - 完整的封装图形（焊盘、丝印、装配层）
    - 自动网络管理
    - 支持从封装库加载
    """

    def __init__(self):
        self.components: List[PCBComponent] = []
        self.tracks: List[PCBTrack] = []
        self.vias: List[PCBVia] = []
        self.zones: List[Dict] = []
        self.texts: List[Dict] = []

        # 网络管理器
        self.net_manager = NetManager()

        # 默认添加GND网络
        self.net_manager.add_net("GND")

        # PCB规格
        self.board_width = 60.0
        self.board_height = 35.0
        self.layers = 2
        self.board_name = "Untitled"
        self.thickness = 1.6
        self.board_outline: List[Tuple[float, float]] = []

    def set_board_properties(
        self,
        width: float,
        height: float,
        layers: int = 2,
        name: str = "Untitled",
        thickness: float = 1.6,
    ):
        """设置PCB属性"""
        self.board_width = width
        self.board_height = height
        self.layers = layers
        self.board_name = name
        self.thickness = thickness
        logger.info(f"PCB规格: {width}x{height}mm, {layers}层")

    def set_board_outline(self, points: List[Tuple[float, float]]):
        """设置板框"""
        if points and points[0] != points[-1]:
            points = points + [points[0]]
        self.board_outline = points

    def add_component(self, component: PCBComponent):
        """添加组件"""
        self.components.append(component)
        logger.debug(f"添加组件: {component.ref}")

    def add_track(self, track: PCBTrack):
        """添加走线"""
        self.tracks.append(track)
        logger.debug(f"添加走线: {track.start}->{track.end}, net={track.net_name}")

    def add_via(self, via: PCBVia):
        """添加过孔"""
        self.vias.append(via)
        logger.debug(f"添加过孔: {via.position}")

    def connect_pins(
        self,
        comp1_ref: str,
        pin1: str,
        comp2_ref: str,
        pin2: str,
        net_name: str = "",
        width: float = 0.25,
        layer: str = "F.Cu",
    ) -> bool:
        """
        连接两个器件引脚

        Args:
            comp1_ref: 第一个器件位号
            pin1: 第一个器件引脚号
            comp2_ref: 第二个器件位号
            pin2: 第二个器件引脚号
            net_name: 网络名称（可选，自动生成）
            width: 走线宽度
            layer: 走线层

        Returns:
            bool: 是否成功
        """
        # 查找器件
        comp1 = None
        comp2 = None
        for comp in self.components:
            if comp.ref == comp1_ref:
                comp1 = comp
            if comp.ref == comp2_ref:
                comp2 = comp

        if not comp1 or not comp2:
            logger.error(f"器件未找到: {comp1_ref} 或 {comp2_ref}")
            return False

        if not comp1.footprint_data or not comp2.footprint_data:
            logger.error(f"器件缺少封装数据")
            return False

        # 查找引脚位置
        pos1 = None
        pos2 = None

        for pad in comp1.footprint_data.pads:
            if pad.number == pin1:
                # 计算绝对位置（考虑器件位置和旋转）
                pos1 = self._transform_point(
                    (pad.x, pad.y), comp1.position, comp1.orientation
                )

        for pad in comp2.footprint_data.pads:
            if pad.number == pin2:
                pos2 = self._transform_point(
                    (pad.x, pad.y), comp2.position, comp2.orientation
                )

        if not pos1 or not pos2:
            logger.error(f"引脚未找到: {pin1} 或 {pin2}")
            return False

        # 确定网络名称
        if not net_name:
            net_name = f"Net-({comp1_ref}-{pin1})-({comp2_ref}-{pin2})"

        # 获取或创建网络ID
        net_id = self.net_manager.get_net_id(net_name)

        # 添加走线
        track = PCBTrack(
            start=pos1,
            end=pos2,
            width=width,
            layer=layer,
            net=net_id,
            net_name=net_name,
        )
        self.add_track(track)

        # 更新焊盘网络
        self._update_pad_net(comp1, pin1, net_id, net_name)
        self._update_pad_net(comp2, pin2, net_id, net_name)

        return True

    def _transform_point(
        self, point: Tuple[float, float], offset: Tuple[float, float], angle: float
    ) -> Tuple[float, float]:
        """坐标变换（旋转+平移）"""
        import math

        x, y = point
        angle_rad = math.radians(angle)

        # 旋转
        x_rot = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        y_rot = x * math.sin(angle_rad) + y * math.cos(angle_rad)

        # 平移
        return (x_rot + offset[0], y_rot + offset[1])

    def _update_pad_net(self, comp: PCBComponent, pin: str, net_id: int, net_name: str):
        """更新焊盘的网络信息"""
        if comp.footprint_data:
            for pad in comp.footprint_data.pads:
                if pad.number == pin:
                    pad.net = net_id
                    pad.net_name = net_name

    def generate(self) -> str:
        """生成.kicad_pcb文件内容"""
        lines = []

        # 文件头
        lines.append('(kicad_pcb (version 20240108) (generator "pcb-nlp-skill-v2")')
        lines.append("")

        # 通用设置
        track_count = len(self.tracks)
        via_count = len(self.vias)
        lines.append("  (general")
        lines.append(f"    (thickness {self.thickness})")
        lines.append(f"    (drawings 4)")
        lines.append(f"    (tracks {track_count})")
        lines.append(f"    (zones 0)")
        lines.append(f"    (modules {len(self.components)})")
        lines.append(f"    (nets {len(self.net_manager.nets)})")
        lines.append("  )")
        lines.append("")

        # 纸张设置
        lines.append('  (paper "A4")')
        lines.append("")

        # 标题块
        lines.append("  (title_block")
        lines.append(f'    (title "{self.board_name}")')
        lines.append('    (date "2026-02-07")')
        lines.append('    (rev "1")')
        lines.append('    (company "Auto Generated")')
        lines.append("  )")
        lines.append("")

        # 层定义
        lines.extend(self._generate_layers())
        lines.append("")

        # Setup部分
        lines.extend(self._generate_setup())
        lines.append("")

        # 网络定义
        for net_id, net_name in sorted(self.net_manager.nets.items()):
            lines.append(f'  (net {net_id} "{net_name}")')
        lines.append("")

        # 组件（完整封装）
        if self.components:
            for comp in self.components:
                lines.extend(self._generate_footprint(comp))
            lines.append("")

        # 板框
        if self.board_outline:
            lines.extend(self._generate_board_outline())
            lines.append("")

        # 走线
        if self.tracks:
            for track in self.tracks:
                lines.extend(self._generate_track(track))
            lines.append("")

        # 过孔
        if self.vias:
            for via in self.vias:
                lines.extend(self._generate_via(via))
            lines.append("")

        # 文件尾
        lines.append(")")

        return "\n".join(lines)

    def _generate_layers(self) -> List[str]:
        """生成层定义"""
        lines = ["  (layers"]

        if self.layers == 2:
            lines.extend(
                [
                    '    (0 "F.Cu" signal)',
                    '    (31 "B.Cu" signal)',
                ]
            )
        elif self.layers == 4:
            lines.extend(
                [
                    '    (0 "F.Cu" signal)',
                    '    (1 "In1.Cu" signal)',
                    '    (2 "In2.Cu" signal)',
                    '    (31 "B.Cu" signal)',
                ]
            )

        lines.extend(
            [
                '    (32 "B.Adhes" user)',
                '    (33 "F.Adhes" user)',
                '    (34 "B.Paste" user)',
                '    (35 "F.Paste" user)',
                '    (36 "B.SilkS" user)',
                '    (37 "F.SilkS" user)',
                '    (38 "B.Mask" user)',
                '    (39 "F.Mask" user)',
                '    (40 "Dwgs.User" user)',
                '    (41 "Cmts.User" user)',
                '    (42 "Eco1.User" user)',
                '    (43 "Eco2.User" user)',
                '    (44 "Edge.Cuts" user)',
                '    (45 "Margin" user)',
                '    (46 "B.CrtYd" user)',
                '    (47 "F.CrtYd" user)',
                '    (48 "B.Fab" user)',
                '    (49 "F.Fab" user)',
            ]
        )
        lines.append("  )")
        return lines

    def _generate_setup(self) -> List[str]:
        """生成setup部分"""
        return [
            "  (setup",
            "    (pad_to_mask_clearance 0)",
            "    (pcbplotparams",
            "      (layerselection 0x00010fc_ffffffff)",
            "      (plot_on_all_layers_selection 0x0000000_00000000)",
            "      (disableapertmacros no)",
            "      (usegerberextensions no)",
            "      (usegerberattributes yes)",
            "      (usegerberadvancedattributes yes)",
            "      (creategerberjobfile yes)",
            "      (dashed_line_dash_ratio 12.000000)",
            "      (dashed_line_gap_ratio 3.000000)",
            "      (svgprecision 4)",
            "      (plotframeref no)",
            "      (viasonmask no)",
            "      (mode 1)",
            "      (useauxorigin no)",
            '      (outputdirectory "")',
            "    )",
            "  )",
        ]

    def _generate_uuid(self) -> str:
        """生成UUID"""
        return str(uuid.uuid4())

    def _generate_footprint(self, comp: PCBComponent) -> List[str]:
        """生成完整封装的S-expression"""
        x, y = comp.position

        lines = [
            f'  (footprint "{comp.footprint_name}"',
            f'    (layer "{comp.layer}")',
            f"    (tedit 646696B5)",
            f"    (tstamp {self._generate_uuid()})",
            f"    (at {x} {y} {comp.orientation})",
            f'    (descr "{comp.footprint_data.description if comp.footprint_data else comp.footprint_name}")',
            f'    (tags "{comp.footprint_name}")',
            f'    (property "Reference" "{comp.ref}"',
            f"      (at 0 -2.5 0)",
            f'      (layer "F.SilkS")',
            f"      (effects (font (size 1 1) (thickness 0.15)))",
            f"      (tstamp {self._generate_uuid()})",
            f"    )",
            f'    (property "Value" "{comp.value}"',
            f"      (at 0 2.5 0)",
            f'      (layer "F.Fab")',
            f"      (effects (font (size 1 1) (thickness 0.15)))",
            f"      (tstamp {self._generate_uuid()})",
            f"    )",
            f'    (path "/{comp.ref}")',
            f"    (attr through_hole)",  # 默认为通孔，可根据需要修改
        ]

        # 添加丝印
        if comp.footprint_data and comp.footprint_data.silkscreen:
            for elem in comp.footprint_data.silkscreen:
                lines.extend(self._generate_silkscreen_element(elem))

        # 添加装配层
        if comp.footprint_data and comp.footprint_data.fab_layer:
            for elem in comp.footprint_data.fab_layer:
                lines.extend(self._generate_fab_element(elem))

        # 添加焊盘
        if comp.footprint_data and comp.footprint_data.pads:
            for pad in comp.footprint_data.pads:
                lines.extend(self._generate_pad(pad, comp.orientation))

        lines.append("  )")
        return lines

    def _generate_silkscreen_element(self, elem: Dict) -> List[str]:
        """生成丝印元素"""
        elem_type = elem.get("type", "line")

        if elem_type == "line":
            start = elem.get("start", (0, 0))
            end = elem.get("end", (0, 0))
            return [
                f"    (fp_line",
                f"      (start {start[0]} {start[1]})",
                f"      (end {end[0]} {end[1]})",
                f'      (layer "F.SilkS")',
                f"      (width 0.12)",
                f"      (tstamp {self._generate_uuid()})",
                f"    )",
            ]
        elif elem_type == "rect":
            start = elem.get("start", (0, 0))
            end = elem.get("end", (0, 0))
            # 矩形用4条线表示
            lines = []
            pts = [
                (start[0], start[1]),
                (end[0], start[1]),
                (end[0], end[1]),
                (start[0], end[1]),
                (start[0], start[1]),
            ]
            for i in range(4):
                lines.extend(
                    [
                        f"    (fp_line",
                        f"      (start {pts[i][0]} {pts[i][1]})",
                        f"      (end {pts[i + 1][0]} {pts[i + 1][1]})",
                        f'      (layer "F.SilkS")',
                        f"      (width 0.12)",
                        f"      (tstamp {self._generate_uuid()})",
                        f"    )",
                    ]
                )
            return lines
        elif elem_type == "circle":
            center = elem.get("center", (0, 0))
            radius = elem.get("radius", 1.0)
            return [
                f"    (fp_circle",
                f"      (center {center[0]} {center[1]})",
                f"      (end {center[0] + radius} {center[1]})",
                f'      (layer "F.SilkS")',
                f"      (width 0.12)",
                f"      (fill none)",
                f"      (tstamp {self._generate_uuid()})",
                f"    )",
            ]

        return []

    def _generate_fab_element(self, elem: Dict) -> List[str]:
        """生成装配层元素"""
        elem_type = elem.get("type", "line")

        if elem_type == "line":
            start = elem.get("start", (0, 0))
            end = elem.get("end", (0, 0))
            return [
                f"    (fp_line",
                f"      (start {start[0]} {start[1]})",
                f"      (end {end[0]} {end[1]})",
                f'      (layer "F.Fab")',
                f"      (width 0.1)",
                f"      (tstamp {self._generate_uuid()})",
                f"    )",
            ]
        elif elem_type == "rect":
            start = elem.get("start", (0, 0))
            end = elem.get("end", (0, 0))
            lines = []
            pts = [
                (start[0], start[1]),
                (end[0], start[1]),
                (end[0], end[1]),
                (start[0], end[1]),
                (start[0], start[1]),
            ]
            for i in range(4):
                lines.extend(
                    [
                        f"    (fp_line",
                        f"      (start {pts[i][0]} {pts[i][1]})",
                        f"      (end {pts[i + 1][0]} {pts[i + 1][1]})",
                        f'      (layer "F.Fab")',
                        f"      (width 0.1)",
                        f"      (tstamp {self._generate_uuid()})",
                        f"    )",
                    ]
                )
            return lines
        elif elem_type == "circle":
            center = elem.get("center", (0, 0))
            radius = elem.get("radius", 1.0)
            return [
                f"    (fp_circle",
                f"      (center {center[0]} {center[1]})",
                f"      (end {center[0] + radius} {center[1]})",
                f'      (layer "F.Fab")',
                f"      (width 0.1)",
                f"      (fill none)",
                f"      (tstamp {self._generate_uuid()})",
                f"    )",
            ]

        return []

    def _generate_pad(self, pad: Pad, orientation: float) -> List[str]:
        """生成焊盘的S-expression"""
        pad_type = "thru_hole" if pad.drill > 0 else "smd"
        layers = '"F.Cu" "F.Paste" "F.Mask"' if pad.drill == 0 else '"*.Cu" "*.Mask"'

        lines = [
            f'    (pad "{pad.number}" {pad_type} {pad.shape}',
            f"      (at {pad.x} {pad.y} {orientation})",
        ]

        if pad.drill > 0:
            lines.append(f"      (size {pad.size_x} {pad.size_y})")
            lines.append(f"      (drill {pad.drill})")
        else:
            lines.append(f"      (size {pad.size_x} {pad.size_y})")

        lines.extend(
            [
                f"      (layers {layers})",
                f"      (roundrect_rratio 0.25)",
            ]
        )

        if pad.net > 0:
            lines.append(f'      (net {pad.net} "{pad.net_name}")')

        lines.append(f"      (tstamp {self._generate_uuid()})")
        lines.append(f"    )")

        return lines

    def _generate_track(self, track: PCBTrack) -> List[str]:
        """生成走线的S-expression"""
        x1, y1 = track.start
        x2, y2 = track.end

        lines = [
            f"  (segment",
            f"    (start {x1} {y1})",
            f"    (end {x2} {y2})",
            f"    (width {track.width})",
            f'    (layer "{track.layer}")',
            f"    (net {track.net})",
            f"    (tstamp {self._generate_uuid()})",
            f"  )",
        ]
        return lines

    def _generate_via(self, via: PCBVia) -> List[str]:
        """生成过孔的S-expression"""
        x, y = via.position

        lines = [
            f"  (via",
            f"    (at {x} {y})",
            f"    (size {via.size})",
            f"    (drill {via.drill})",
            f'    (layers "F.Cu" "B.Cu")',
            f"    (net {via.net})",
            f"    (tstamp {self._generate_uuid()})",
            f"  )",
        ]
        return lines

    def _generate_board_outline(self) -> List[str]:
        """生成板框（Edge.Cuts层）"""
        lines = []

        points = (
            self.board_outline
            if self.board_outline
            else [
                (0, 0),
                (self.board_width, 0),
                (self.board_width, self.board_height),
                (0, self.board_height),
                (0, 0),
            ]
        )

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            lines.extend(
                [
                    f"  (gr_line",
                    f"    (start {x1} {y1})",
                    f"    (end {x2} {y2})",
                    f'    (layer "Edge.Cuts")',
                    f"    (width 0.1)",
                    f"    (tstamp {self._generate_uuid()})",
                    f"  )",
                ]
            )

        return lines

    def save(self, filename: str) -> bool:
        """保存到文件"""
        try:
            content = self.generate()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"PCB已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return False


# 向后兼容
PCBFileGenerator = PCBFileGeneratorV2
