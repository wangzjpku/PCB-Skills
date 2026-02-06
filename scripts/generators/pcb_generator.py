"""
PCB文件生成器

直接生成KiCad .kicad_pcb文件（S-expression格式）。
生成的文件可直接在KiCad GUI中打开。
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class PCBComponent:
    """PCB组件（封装）"""

    ref: str  # 参考位号（U1, R1, C1等）
    footprint: str  # 封装名称
    value: str  # 器件值
    position: Tuple[float, float]  # (x, y) in mm
    orientation: float = 0.0  # 旋转角度（度）
    layer: str = "F.Cu"
    pads: List[Dict] = field(default_factory=list)  # 焊盘定义


@dataclass
class PCBTrack:
    """PCB走线"""

    start: Tuple[float, float]  # 起点 (x, y) in mm
    end: Tuple[float, float]  # 终点 (x, y) in mm
    width: float = 0.25  # 宽度 in mm
    layer: str = "F.Cu"
    net: int = 0  # 网络编号


@dataclass
class PCBVia:
    """PCB过孔"""

    position: Tuple[float, float]  # 位置 (x, y) in mm
    drill: float = 0.8  # 钻孔直径 in mm
    size: float = 1.2  # 过孔直径 in mm
    net: int = 0  # 网络编号


class PCBFileGenerator:
    """
    PCB文件生成器

    生成符合KiCad标准的.kicad_pcb文件。
    文件格式为S-expression（Lisp风格）。
    """

    def __init__(self):
        self.components: List[PCBComponent] = []
        self.tracks: List[PCBTrack] = []
        self.vias: List[PCBVia] = []
        self.zones: List[Dict] = []
        self.texts: List[Dict] = []
        self.nets: List[Tuple[int, str]] = [(0, ""), (1, "GND")]

        # PCB规格
        self.board_width = 60.0
        self.board_height = 35.0
        self.layers = 2
        self.board_name = "Untitled"
        self.thickness = 1.6

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

    def add_net(self, net_id: int, net_name: str):
        """添加网络定义"""
        self.nets.append((net_id, net_name))

    def add_component(self, component: PCBComponent):
        """添加组件"""
        self.components.append(component)
        logger.debug(f"添加组件: {component.ref}")

    def add_track(self, track: PCBTrack):
        """添加走线"""
        self.tracks.append(track)
        logger.debug(f"添加走线: {track.start}->{track.end}")

    def add_via(self, via: PCBVia):
        """添加过孔"""
        self.vias.append(via)
        logger.debug(f"添加过孔: {via.position}")

    def set_board_outline(self, points: List[Tuple[float, float]]):
        """设置板框（由gr_line线段组成）"""
        # 确保闭合
        if points and points[0] != points[-1]:
            points = points + [points[0]]
        self.board_outline = points

    def generate(self) -> str:
        """
        生成.kicad_pcb文件内容

        Returns:
            str: KiCad S-expression格式的内容
        """
        lines = []

        # 文件头
        lines.append('(kicad_pcb (version 20240108) (generator "pcb-nlp-skill")')
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
        lines.append(f"    (nets {len(self.nets)})")
        lines.append("  )")
        lines.append("")

        # 纸张设置
        lines.append('  (paper "A4")')
        lines.append("")

        # 标题块
        lines.append("  (title_block")
        lines.append(f'    (title "{self.board_name}")')
        lines.append('    (date "2026-02-06")')
        lines.append('    (rev "1")')
        lines.append('    (company "Auto Generated")')
        lines.append("  )")
        lines.append("")

        # 层定义
        lines.append("  (layers")
        lines.append('    (0 "F.Cu" signal)')
        lines.append('    (31 "B.Cu" signal)')
        lines.append('    (32 "B.Adhes" user)')
        lines.append('    (33 "F.Adhes" user)')
        lines.append('    (34 "B.Paste" user)')
        lines.append('    (35 "F.Paste" user)')
        lines.append('    (36 "B.SilkS" user)')
        lines.append('    (37 "F.SilkS" user)')
        lines.append('    (38 "B.Mask" user)')
        lines.append('    (39 "F.Mask" user)')
        lines.append('    (40 "Dwgs.User" user)')
        lines.append('    (41 "Cmts.User" user)')
        lines.append('    (42 "Eco1.User" user)')
        lines.append('    (43 "Eco2.User" user)')
        lines.append('    (44 "Edge.Cuts" user)')
        lines.append('    (45 "Margin" user)')
        lines.append('    (46 "B.CrtYd" user)')
        lines.append('    (47 "F.CrtYd" user)')
        lines.append('    (48 "B.Fab" user)')
        lines.append('    (49 "F.Fab" user)')
        lines.append("  )")
        lines.append("")

        # Setup部分 - 必需的
        lines.append("  (setup")
        lines.append("    (pad_to_mask_clearance 0)")
        lines.append("    (pcbplotparams")
        lines.append("      (layerselection 0x00010fc_ffffffff)")
        lines.append("      (plot_on_all_layers_selection 0x0000000_00000000)")
        lines.append("      (disableapertmacros no)")
        lines.append("      (usegerberextensions no)")
        lines.append("      (usegerberattributes yes)")
        lines.append("      (usegerberadvancedattributes yes)")
        lines.append("      (creategerberjobfile yes)")
        lines.append("      (dashed_line_dash_ratio 12.000000)")
        lines.append("      (dashed_line_gap_ratio 3.000000)")
        lines.append("      (svgprecision 4)")
        lines.append("      (plotframeref no)")
        lines.append("      (viasonmask no)")
        lines.append("      (mode 1)")
        lines.append("      (useauxorigin no)")
        lines.append("      (hpglpennumber 1)")
        lines.append("      (hpglpenspeed 20)")
        lines.append("      (hpglpendiameter 15.000000)")
        lines.append("      (pdf_front_fp_property_popups yes)")
        lines.append("      (pdf_back_fp_property_popups yes)")
        lines.append("      (dxfpolygonmode yes)")
        lines.append("      (dxfimperialunits yes)")
        lines.append("      (dxfusepcbnewfont yes)")
        lines.append("      (psnegative no)")
        lines.append("      (psa4output no)")
        lines.append("      (plotreference yes)")
        lines.append("      (plotvalue yes)")
        lines.append("      (plotfptext yes)")
        lines.append("      (plotinvisibletext no)")
        lines.append("      (sketchpadsonfab no)")
        lines.append("      (subtractmaskfromsilk no)")
        lines.append("      (outputformat 1)")
        lines.append("      (mirror no)")
        lines.append("      (drillshape 1)")
        lines.append("      (scaleselection 1)")
        lines.append('      (outputdirectory "")')
        lines.append("    )")
        lines.append("  )")
        lines.append("")

        # 网络定义
        for net_id, net_name in self.nets:
            lines.append(f'  (net {net_id} "{net_name}")')
        lines.append("")

        # 组件（封装）
        if self.components:
            for comp in self.components:
                lines.extend(self._generate_footprint(comp))
            lines.append("")

        # 板框
        if hasattr(self, "board_outline") and self.board_outline:
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

    def _generate_uuid(self) -> str:
        """生成UUID"""
        return str(uuid.uuid4())

    def _generate_footprint(self, comp: PCBComponent) -> List[str]:
        """生成封装的S-expression - 使用毫米而非纳米"""
        x, y = comp.position

        lines = [
            f'  (footprint "{comp.footprint}"',
            f'    (layer "{comp.layer}")',
            f"    (tedit 646696B5)",
            f"    (tstamp {self._generate_uuid()})",
            f"    (at {x} {y} {comp.orientation})",
            f'    (descr "{comp.footprint}")',
            f'    (tags "{comp.footprint}")',
            f'    (property "Reference" "{comp.ref}")',
            f'    (property "Value" "{comp.value}")',
            f'    (path "/{comp.ref}")',
            f"    (attr smd)",
            f'    (fp_text reference "{comp.ref}"',
            f"      (at 0 -1.65 0)",
            f'      (layer "F.SilkS")',
            f"      (effects (font (size 1 1) (thickness 0.15)))",
            f"      (tstamp {self._generate_uuid()})",
            f"    )",
            f'    (fp_text value "{comp.value}"',
            f"      (at 0 1.65 0)",
            f'      (layer "F.Fab")',
            f"      (effects (font (size 1 1) (thickness 0.15)))",
            f"      (tstamp {self._generate_uuid()})",
            f"    )",
        ]

        # 添加焊盘
        if comp.pads:
            for pad in comp.pads:
                pad_num = pad.get("number", "1")
                pad_x = pad.get("x", 0)
                pad_y = pad.get("y", 0)
                pad_size_x = pad.get("size_x", 1.0)
                pad_size_y = pad.get("size_y", 1.0)
                pad_net = pad.get("net", 0)
                pad_net_name = pad.get("net_name", "")

                lines.append(f'    (pad "{pad_num}" smd roundrect')
                lines.append(f"      (at {pad_x} {pad_y} {comp.orientation})")
                lines.append(f"      (size {pad_size_x} {pad_size_y})")
                lines.append(f'      (layers "F.Cu" "F.Paste" "F.Mask")')
                lines.append(f"      (roundrect_rratio 0.25)")
                if pad_net > 0:
                    lines.append(f'      (net {pad_net} "{pad_net_name}")')
                lines.append(f"      (tstamp {self._generate_uuid()})")
                lines.append(f"    )")
        else:
            # 默认焊盘
            lines.append(f'    (pad "1" smd roundrect')
            lines.append(f"      (at -0.95 0 {comp.orientation})")
            lines.append(f"      (size 1.025 1.4)")
            lines.append(f'      (layers "F.Cu" "F.Paste" "F.Mask")')
            lines.append(f"      (roundrect_rratio 0.25)")
            lines.append(f"      (tstamp {self._generate_uuid()})")
            lines.append(f"    )")

        lines.append("  )")
        return lines

    def _generate_track(self, track: PCBTrack) -> List[str]:
        """生成走线的S-expression - 使用毫米"""
        x1, y1 = track.start
        x2, y2 = track.end
        width = track.width
        layer = track.layer
        net = track.net

        lines = [
            f"  (segment",
            f"    (start {x1} {y1})",
            f"    (end {x2} {y2})",
            f"    (width {width})",
            f'    (layer "{layer}")',
            f"    (net {net})",
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

        if not hasattr(self, "board_outline") or not self.board_outline:
            # 默认矩形板框
            margin = 5.0
            x1, y1 = margin, margin
            x2, y2 = self.board_width - margin, self.board_height - margin

            points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
        else:
            points = self.board_outline

        # 生成gr_line线段
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            lines.append(f"  (gr_line")
            lines.append(f"    (start {x1} {y1})")
            lines.append(f"    (end {x2} {y2})")
            lines.append(f'    (layer "Edge.Cuts")')
            lines.append(f"    (width 0.1)")
            lines.append(f"    (tstamp {self._generate_uuid()})")
            lines.append(f"  )")

        return lines

    def save(self, filename: str) -> bool:
        """
        保存到文件

        Args:
            filename: 输出文件路径

        Returns:
            bool: 是否成功
        """
        try:
            content = self.generate()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"PCB已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return False


def create_simple_pcb(
    width: float = 60.0, height: float = 35.0, components: List[PCBComponent] = None
) -> PCBFileGenerator:
    """
    创建简单PCB的便捷函数

    Args:
        width: 板子宽度（mm）
        height: 板子高度（mm）
        components: 组件列表

    Returns:
        PCBFileGenerator: 配置好的生成器
    """
    generator = PCBFileGenerator()
    generator.set_board_properties(width, height)

    if components:
        for comp in components:
            generator.add_component(comp)

    return generator
