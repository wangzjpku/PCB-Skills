"""
增强版原理图生成器 V2

大幅改进的版本，包含：
- 完整的符号库（IC、连接器、变压器等）
- 自动连线系统
- 引脚到引脚的智能连接
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SCHPin:
    """原理图引脚定义"""

    number: str
    name: str
    x: float
    y: float
    direction: str = "R"  # R=右, L=左, U=上, D=下
    length: float = 2.54
    electrical_type: str = "passive"  # passive, power_in, power_out, input, output


@dataclass
class SCHSymbolV2:
    """增强版原理图符号"""

    ref: str
    name: str
    value: str
    position: Tuple[float, float]
    pins: List[SCHPin] = field(default_factory=list)
    rotation: float = 0.0
    mirror: bool = False
    # 符号图形元素
    rectangles: List[Dict] = field(default_factory=list)
    polylines: List[Dict] = field(default_factory=list)
    circles: List[Dict] = field(default_factory=list)
    arcs: List[Dict] = field(default_factory=list)
    texts: List[Dict] = field(default_factory=list)


@dataclass
class SCHWireV2:
    """原理图连线"""

    start: Tuple[float, float]
    end: Tuple[float, float]
    width: float = 0.0


@dataclass
class SCHConnection:
    """引脚连接关系"""

    from_symbol: str
    from_pin: str
    to_symbol: str
    to_pin: str
    net_name: str = ""


class SymbolLibrary:
    """符号库 - 定义完整的KiCad符号"""

    @staticmethod
    def create_resistor(
        ref: str = "R", value: str = "1k", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建标准电阻符号"""
        return SCHSymbolV2(
            ref=ref,
            name="R",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "~", -2.54, 0, "L"),
                SCHPin("2", "~", 2.54, 0, "R"),
            ],
            rectangles=[{"start": (-1.016, -2.54), "end": (1.016, 2.54)}],
        )

    @staticmethod
    def create_capacitor(
        ref: str = "C",
        value: str = "100n",
        pos: Tuple[float, float] = (0, 0),
        polarized: bool = False,
    ) -> SCHSymbolV2:
        """创建电容符号"""
        pins = [
            SCHPin("1", "~", 0, 2.54, "U"),
            SCHPin("2", "~", 0, -2.54, "D"),
        ]

        # 两条平行线
        polylines = [
            {"pts": [(-1.27, 0.635), (1.27, 0.635)]},
            {"pts": [(-1.27, -0.635), (1.27, -0.635)]},
        ]

        if polarized:
            # 添加极性标记
            texts = [
                {"text": "+", "pos": (-1.5, 1.5), "effects": {}},
            ]
        else:
            texts = []

        return SCHSymbolV2(
            ref=ref,
            name="C_Polarized" if polarized else "C",
            value=value,
            position=pos,
            pins=pins,
            polylines=polylines,
            texts=texts,
        )

    @staticmethod
    def create_inductor(
        ref: str = "L", value: str = "10uH", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建电感符号（弧形线圈）"""
        arcs = [
            {"center": (-1.905, 0), "radius": 0.635, "start": 0, "end": 180},
            {"center": (-0.635, 0), "radius": 0.635, "start": 0, "end": 180},
            {"center": (0.635, 0), "radius": 0.635, "start": 0, "end": 180},
            {"center": (1.905, 0), "radius": 0.635, "start": 0, "end": 180},
        ]

        return SCHSymbolV2(
            ref=ref,
            name="L",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "~", -3.81, 0, "L"),
                SCHPin("2", "~", 3.81, 0, "R"),
            ],
            arcs=arcs,
        )

    @staticmethod
    def create_diode(
        ref: str = "D", value: str = "1N4148", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建二极管符号"""
        polylines = [
            # 三角形
            {"pts": [(-1.27, -1.27), (1.27, 0), (-1.27, 1.27), (-1.27, -1.27)]},
            # 竖线（阴极）
            {"pts": [(1.27, -1.27), (1.27, 1.27)]},
        ]

        return SCHSymbolV2(
            ref=ref,
            name="D",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "K", -3.81, 0, "L"),  # 阴极
                SCHPin("2", "A", 3.81, 0, "R"),  # 阳极
            ],
            polylines=polylines,
        )

    @staticmethod
    def create_schottky_diode(
        ref: str = "D", value: str = "SS34", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建肖特基二极管符号（带弯曲标记）"""
        polylines = [
            {"pts": [(-1.27, -1.27), (1.27, 0), (-1.27, 1.27), (-1.27, -1.27)]},
            {"pts": [(1.27, -1.27), (1.27, 1.27)]},
            # 肖特基弯曲标记
            {"pts": [(0.5, -1.0), (0.8, -0.8), (0.8, -0.3)]},
            {"pts": [(0.0, -1.0), (0.3, -0.8), (0.3, -0.3)]},
        ]

        return SCHSymbolV2(
            ref=ref,
            name="D_Schottky",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "K", -3.81, 0, "L"),
                SCHPin("2", "A", 3.81, 0, "R"),
            ],
            polylines=polylines,
        )

    @staticmethod
    def create_bridge_rectifier(
        ref: str = "BR", value: str = "MB6S", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建桥式整流器符号（菱形）"""
        polylines = [
            # 外框 - 菱形
            {"pts": [(0, -2.54), (2.54, 0), (0, 2.54), (-2.54, 0), (0, -2.54)]},
            # 内部二极管符号
            {"pts": [(-1.0, -0.5), (0, 0), (-1.0, 0.5)]},
            {"pts": [(0.5, -1.0), (0, 0), (0.5, 1.0)]},
        ]

        return SCHSymbolV2(
            ref=ref,
            name="Bridge_Rectifier",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "+", 0, -3.81, "D"),
                SCHPin("2", "~", -3.81, 0, "L"),
                SCHPin("3", "-", 0, 3.81, "U"),
                SCHPin("4", "~", 3.81, 0, "R"),
            ],
            polylines=polylines,
        )

    @staticmethod
    def create_viper22a(
        ref: str = "U1", value: str = "VIPer22A", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建VIPer22A开关电源IC符号"""
        # 矩形框
        rectangles = [{"start": (-7.62, -10.16), "end": (7.62, 10.16)}]

        # 引脚定义（DIP-8）
        pins = [
            SCHPin("1", "SOURCE", -10.16, 7.62, "L", electrical_type="power_out"),
            SCHPin("2", "SOURCE", -10.16, 5.08, "L", electrical_type="power_out"),
            SCHPin("3", "FB", -10.16, 2.54, "L", electrical_type="input"),
            SCHPin("4", "VDD", -10.16, 0, "L", electrical_type="power_in"),
            SCHPin("5", "DRAIN", -10.16, -2.54, "L", electrical_type="power_in"),
            SCHPin("6", "DRAIN", -10.16, -5.08, "L", electrical_type="power_in"),
            SCHPin("7", "DRAIN", -10.16, -7.62, "L", electrical_type="power_in"),
            SCHPin("8", "DRAIN", 10.16, 7.62, "R", electrical_type="power_in"),
        ]

        texts = [
            {
                "text": "VIPer22A",
                "pos": (0, 0),
                "effects": {"size": (1.27, 1.27), "bold": True},
            },
        ]

        return SCHSymbolV2(
            ref=ref,
            name="VIPer22A",
            value=value,
            position=pos,
            pins=pins,
            rectangles=rectangles,
            texts=texts,
        )

    @staticmethod
    def create_tl431(
        ref: str = "U2", value: str = "TL431", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建TL431可调稳压器符号（三角形）"""
        polylines = [
            {"pts": [(-2.54, -2.54), (2.54, 0), (-2.54, 2.54), (-2.54, -2.54)]},
        ]

        texts = [
            {"text": "TL", "pos": (0, 0.8), "effects": {"size": (1.0, 1.0)}},
            {"text": "431", "pos": (0, -0.8), "effects": {"size": (1.0, 1.0)}},
        ]

        return SCHSymbolV2(
            ref=ref,
            name="TL431",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "REF", -5.08, 0, "L", electrical_type="input"),
                SCHPin("2", "A", 0, -3.81, "D", electrical_type="power_in"),
                SCHPin("3", "K", 0, 3.81, "U", electrical_type="power_out"),
            ],
            polylines=polylines,
            texts=texts,
        )

    @staticmethod
    def create_optocoupler(
        ref: str = "U3", value: str = "PC817", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建光耦符号（LED + 光电晶体管）"""
        rectangles = [{"start": (-5.08, -5.08), "end": (5.08, 5.08)}]

        # LED侧（左侧）
        polylines = [
            # LED三角形
            {"pts": [(-3.81, 1.27), (-2.54, 0), (-3.81, -1.27), (-3.81, 1.27)]},
            # LED箭头（发光方向）
            {"pts": [(-3.0, 1.5), (-2.0, 2.5)]},
            {"pts": [(-2.5, 1.3), (-1.5, 2.3)]},
            # 晶体管
            {"pts": [(2.54, -1.27), (2.54, 1.27)]},
            {"pts": [(2.54, 0), (3.81, -1.27)]},
            {"pts": [(2.54, 0), (3.81, 1.27)]},
        ]

        return SCHSymbolV2(
            ref=ref,
            name="PC817",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "A", -7.62, 2.54, "L"),  # LED阳极
                SCHPin("2", "K", -7.62, -2.54, "L"),  # LED阴极
                SCHPin("3", "E", 7.62, -2.54, "R"),  # 发射极
                SCHPin("4", "C", 7.62, 2.54, "R"),  # 集电极
            ],
            rectangles=rectangles,
            polylines=polylines,
        )

    @staticmethod
    def create_transformer(
        ref: str = "T1", value: str = "EE-25", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建变压器符号（带隔离标记）"""
        # 初级线圈（左侧，弧形）
        arcs_left = [
            {"center": (-3.81, 3.81), "radius": 0.8, "start": 0, "end": 180},
            {"center": (-3.81, 1.27), "radius": 0.8, "start": 0, "end": 180},
            {"center": (-3.81, -1.27), "radius": 0.8, "start": 0, "end": 180},
            {"center": (-3.81, -3.81), "radius": 0.8, "start": 0, "end": 180},
        ]

        # 次级线圈（右侧，弧形）
        arcs_right = [
            {"center": (3.81, 3.81), "radius": 0.8, "start": 180, "end": 0},
            {"center": (3.81, 1.27), "radius": 0.8, "start": 180, "end": 0},
            {"center": (3.81, -1.27), "radius": 0.8, "start": 180, "end": 0},
            {"center": (3.81, -3.81), "radius": 0.8, "start": 180, "end": 0},
        ]

        # 虚线隔离标记
        polylines = [
            {"pts": [(0, -5.08), (0, 5.08)], "style": "dash"},
        ]

        return SCHSymbolV2(
            ref=ref,
            name="Transformer",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "PRI+", -7.62, 5.08, "L"),
                SCHPin("2", "PRI-", -7.62, -5.08, "L"),
                SCHPin("3", "AUX+", -7.62, 2.54, "L"),
                SCHPin("4", "AUX-", -7.62, -2.54, "L"),
                SCHPin("5", "SEC+", 7.62, 5.08, "R"),
                SCHPin("6", "SEC-", 7.62, -5.08, "R"),
            ],
            arcs=arcs_left + arcs_right,
            polylines=polylines,
        )

    @staticmethod
    def create_screw_terminal(
        ref: str = "J1",
        value: str = "Screw_Terminal",
        pos: Tuple[float, float] = (0, 0),
        pins_count: int = 2,
    ) -> SCHSymbolV2:
        """创建螺钉端子"""
        rectangles = [
            {"start": (-2.54, -1.27 * pins_count), "end": (2.54, 1.27 * pins_count)}
        ]

        pins = []
        for i in range(pins_count):
            y_pos = (pins_count - 1) * 1.27 / 2 - i * 2.54
            pins.append(SCHPin(str(i + 1), f"Pin{i + 1}", -5.08, y_pos, "L"))

        return SCHSymbolV2(
            ref=ref,
            name="Screw_Terminal",
            value=value,
            position=pos,
            pins=pins,
            rectangles=rectangles,
        )

    @staticmethod
    def create_fuse(
        ref: str = "F1", value: str = "500mA", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建保险丝符号（中间有横线的矩形）"""
        rectangles = [{"start": (-2.54, -1.27), "end": (2.54, 1.27)}]

        polylines = [
            {"pts": [(-1.5, 0), (1.5, 0)]},  # 中间横线
        ]

        return SCHSymbolV2(
            ref=ref,
            name="Fuse",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "~", -5.08, 0, "L"),
                SCHPin("2", "~", 5.08, 0, "R"),
            ],
            rectangles=rectangles,
            polylines=polylines,
        )

    @staticmethod
    def create_varistor(
        ref: str = "RV1", value: str = "10D561K", pos: Tuple[float, float] = (0, 0)
    ) -> SCHSymbolV2:
        """创建压敏电阻符号（带斜线填充的矩形）"""
        rectangles = [{"start": (-2.54, -1.27), "end": (2.54, 1.27)}]

        polylines = [
            {"pts": [(-1.5, -0.5), (1.5, 0.5)]},
            {"pts": [(-1.5, 0.5), (1.5, -0.5)]},
        ]

        return SCHSymbolV2(
            ref=ref,
            name="Varistor",
            value=value,
            position=pos,
            pins=[
                SCHPin("1", "~", -5.08, 0, "L"),
                SCHPin("2", "~", 5.08, 0, "R"),
            ],
            rectangles=rectangles,
            polylines=polylines,
        )

    @staticmethod
    def create_gnd(pos: Tuple[float, float] = (0, 0)) -> SCHSymbolV2:
        """创建GND电源符号"""
        polylines = [
            {"pts": [(0, 0), (0, -1.27)]},
            {"pts": [(-1.27, -1.27), (1.27, -1.27)]},
            {"pts": [(-0.762, -1.905), (0.762, -1.905)]},
            {"pts": [(-0.254, -2.54), (0.254, -2.54)]},
        ]

        return SCHSymbolV2(
            ref="#PWR",
            name="GND",
            value="GND",
            position=pos,
            pins=[SCHPin("1", "GND", 0, 0, "U", electrical_type="power_in")],
            polylines=polylines,
        )

    @staticmethod
    def create_vcc(
        pos: Tuple[float, float] = (0, 0), voltage: str = "+5V"
    ) -> SCHSymbolV2:
        """创建VCC电源符号"""
        polylines = [
            {"pts": [(0, 0), (0, -1.27)]},
            {"pts": [(-0.762, -1.27), (0, -2.54), (0.762, -1.27)]},
        ]

        return SCHSymbolV2(
            ref="#PWR",
            name=voltage,
            value=voltage,
            position=pos,
            pins=[SCHPin("1", voltage, 0, 0, "D", electrical_type="power_out")],
            polylines=polylines,
            texts=[
                {"text": voltage, "pos": (0.5, -3.0), "effects": {"size": (1.0, 1.0)}}
            ],
        )


class SchematicFileGeneratorV2:
    """
    增强版原理图生成器 V2

    特性：
    - 完整的符号库支持
    - 自动连线系统
    - 引脚到引脚连接
    """

    def __init__(self):
        self.symbols: List[SCHSymbolV2] = []
        self.wires: List[SCHWireV2] = []
        self.connections: List[SCHConnection] = []
        self.power_symbols: List[SCHSymbolV2] = []

        self.page_width = 210.0
        self.page_height = 297.0
        self.schematic_name = "Untitled"
        self.schematic_uuid = str(uuid.uuid4())

    def set_page_properties(
        self, width: float = 210.0, height: float = 297.0, name: str = "Untitled"
    ):
        """设置页面属性"""
        self.page_width = width
        self.page_height = height
        self.schematic_name = name

    def add_symbol(self, symbol: SCHSymbolV2):
        """添加符号"""
        self.symbols.append(symbol)
        logger.debug(f"添加符号: {symbol.ref}")

    def add_power_symbol(self, symbol: SCHSymbolV2):
        """添加电源符号"""
        self.power_symbols.append(symbol)

    def add_wire(self, wire: SCHWireV2):
        """添加连线"""
        self.wires.append(wire)

    def connect_pins(
        self,
        sym1_ref: str,
        pin1_num: str,
        sym2_ref: str,
        pin2_num: str,
        net_name: str = "",
    ):
        """
        连接两个器件的引脚

        Args:
            sym1_ref: 器件1位号
            pin1_num: 器件1引脚号
            sym2_ref: 器件2位号
            pin2_num: 器件2引脚号
            net_name: 网络名称（可选）
        """
        # 查找符号和引脚
        sym1 = self._find_symbol(sym1_ref)
        sym2 = self._find_symbol(sym2_ref)

        if not sym1 or not sym2:
            logger.error(f"符号未找到: {sym1_ref} 或 {sym2_ref}")
            return False

        pin1 = self._find_pin(sym1, pin1_num)
        pin2 = self._find_pin(sym2, pin2_num)

        if not pin1 or not pin2:
            logger.error(f"引脚未找到: {pin1_num} 或 {pin2_num}")
            return False

        # 计算绝对位置
        pos1 = self._get_pin_absolute_position(sym1, pin1)
        pos2 = self._get_pin_absolute_position(sym2, pin2)

        # 添加连线
        self.add_wire(SCHWireV2(start=pos1, end=pos2))

        # 记录连接关系
        if not net_name:
            net_name = f"Net-({sym1_ref}-{pin1_num})-({sym2_ref}-{pin2_num})"

        self.connections.append(
            SCHConnection(
                from_symbol=sym1_ref,
                from_pin=pin1_num,
                to_symbol=sym2_ref,
                to_pin=pin2_num,
                net_name=net_name,
            )
        )

        logger.debug(
            f"连接: {sym1_ref}.{pin1_num} -> {sym2_ref}.{pin2_num}, 网络={net_name}"
        )
        return True

    def _find_symbol(self, ref: str) -> Optional[SCHSymbolV2]:
        """查找符号"""
        for sym in self.symbols:
            if sym.ref == ref:
                return sym
        for sym in self.power_symbols:
            if sym.ref == ref:
                return sym
        return None

    def _find_pin(self, symbol: SCHSymbolV2, pin_num: str) -> Optional[SCHPin]:
        """查找引脚"""
        for pin in symbol.pins:
            if pin.number == pin_num:
                return pin
        return None

    def _get_pin_absolute_position(
        self, symbol: SCHSymbolV2, pin: SCHPin
    ) -> Tuple[float, float]:
        """获取引脚的绝对位置"""
        import math

        sx, sy = symbol.position
        px, py = pin.x, pin.y
        angle = symbol.rotation

        # 应用旋转
        angle_rad = math.radians(angle)
        rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
        ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)

        # 应用平移
        return (sx + rx, sy + ry)

    def generate(self) -> str:
        """生成.kicad_sch文件内容"""
        lines = []

        # 文件头
        lines.append('(kicad_sch (version 20240108) (generator "pcb-nlp-skill-v2")')
        lines.append(f"  (uuid {self.schematic_uuid})")
        lines.append('  (paper "A4")')
        lines.append("")

        # 标题块
        lines.append("  (title_block")
        lines.append(f'    (title "{self.schematic_name}")')
        lines.append('    (date "2026-02-07")')
        lines.append('    (rev "1")')
        lines.append('    (company "Auto Generated")')
        lines.append("  )")
        lines.append("")

        # 库符号定义
        lines.append("  (lib_symbols")
        lines.extend(self._generate_lib_symbols())
        lines.append("  )")
        lines.append("")

        # 连线
        for wire in self.wires:
            lines.extend(self._generate_wire(wire))
        if self.wires:
            lines.append("")

        # 符号实例
        for symbol in self.symbols:
            lines.extend(self._generate_symbol_instance(symbol))
        if self.symbols:
            lines.append("")

        # 电源符号实例
        for symbol in self.power_symbols:
            lines.extend(self._generate_power_symbol_instance(symbol))
        if self.power_symbols:
            lines.append("")

        # 工作表实例
        lines.append("  (sheet_instances")
        lines.append('    (path "/" (page "1"))')
        lines.append("  )")

        # 文件尾
        lines.append(")")

        return "\n".join(lines)

    def _generate_lib_symbols(self) -> List[str]:
        """生成库符号定义"""
        lines = []

        # 收集所有唯一的符号类型
        symbol_types = {}
        for sym in self.symbols + self.power_symbols:
            key = f"{sym.name}"
            if key not in symbol_types:
                symbol_types[key] = sym

        for name, sym in symbol_types.items():
            lines.extend(self._generate_single_lib_symbol(sym))

        return lines

    def _generate_single_lib_symbol(self, sym: SCHSymbolV2) -> List[str]:
        """生成单个库符号定义"""
        lines = [
            f'    (symbol "Device:{sym.name}"',
            "      (pin_numbers hide)",
            "      (pin_names (offset 0))",
            "      (exclude_from_sim no)",
            "      (in_bom yes)",
            "      (on_board yes)",
            f'      (property "Reference" "{sym.ref[0] if sym.ref else "U"}"',
            "        (at 0 0 0)",
            "        (effects (font (size 1.27 1.27)))",
            "      )",
            f'      (property "Value" "{sym.name}"',
            "        (at 0 0 0)",
            "        (effects (font (size 1.27 1.27)))",
            "      )",
        ]

        # 图形元素
        unit_name = f"{sym.name}_0_0"
        lines.append(f'      (symbol "{unit_name}"')

        # 矩形
        for rect in sym.rectangles:
            start = rect.get("start", (0, 0))
            end = rect.get("end", (0, 0))
            lines.append(
                f"        (rectangle (start {start[0]} {start[1]}) (end {end[0]} {end[1]})"
            )
            lines.append("          (stroke (width 0.254) (type default))")
            lines.append("          (fill (type none))")
            lines.append("        )")

        # 多段线
        for pl in sym.polylines:
            pts = pl.get("pts", [])
            if pts:
                lines.append("        (polyline")
                lines.append("          (pts")
                for pt in pts:
                    lines.append(f"            (xy {pt[0]} {pt[1]})")
                lines.append("          )")
                lines.append("          (stroke (width 0) (type default))")
                lines.append("          (fill (type none))")
                lines.append("        )")

        # 圆弧
        for arc in sym.arcs:
            center = arc.get("center", (0, 0))
            radius = arc.get("radius", 1.0)
            start = arc.get("start", 0)
            end = arc.get("end", 180)
            lines.append(
                f"        (arc (start {center[0] - radius} {center[1]}) (mid {center[0]} {center[1] + radius}) (end {center[0] + radius} {center[1]})"
            )
            lines.append("          (stroke (width 0) (type default))")
            lines.append("        )")

        # 文本
        for text in sym.texts:
            t = text.get("text", "")
            pos = text.get("pos", (0, 0))
            lines.append(f'        (text "{t}" (at {pos[0]} {pos[1]} 0)')
            lines.append("          (effects (font (size 1.27 1.27)))")
            lines.append("        )")

        lines.append("      )")

        # 引脚定义
        pin_unit = f"{sym.name}_1_0"
        lines.append(f'      (symbol "{pin_unit}"')
        for pin in sym.pins:
            lines.extend(self._generate_pin_definition(pin))
        lines.append("      )")

        lines.append("    )")

        return lines

    def _generate_pin_definition(self, pin: SCHPin) -> List[str]:
        """生成引脚定义"""
        direction_map = {"R": 0, "U": 90, "L": 180, "D": 270}
        angle = direction_map.get(pin.direction, 0)

        lines = [
            f"        (pin {pin.electrical_type} line (at {pin.x} {pin.y} {angle}) (length {pin.length})",
            f'          (name "{pin.name}" (effects (font (size 1.27 1.27))))',
            f'          (number "{pin.number}" (effects (font (size 1.27 1.27))))',
            "        )",
        ]
        return lines

    def _generate_wire(self, wire: SCHWireV2) -> List[str]:
        """生成连线"""
        x1, y1 = wire.start
        x2, y2 = wire.end
        return [
            f"  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))",
            "    (stroke (width 0) (type default))",
            f"    (uuid {uuid.uuid4()})",
            "  )",
        ]

    def _generate_symbol_instance(self, sym: SCHSymbolV2) -> List[str]:
        """生成符号实例"""
        x, y = sym.position

        lines = [
            f'  (symbol (lib_id "Device:{sym.name}") (at {x} {y} {sym.rotation}) (unit 1)',
            "    (in_bom yes) (on_board yes) (dnp no)",
            f"    (uuid {uuid.uuid4()})",
            f'    (property "Reference" "{sym.ref}"',
            f"      (at {x + 2.54} {y - 2.54} {sym.rotation})",
            "      (effects (font (size 1.27 1.27)) (justify left))",
            "    )",
            f'    (property "Value" "{sym.value}"',
            f"      (at {x + 2.54} {y + 2.54} {sym.rotation})",
            "      (effects (font (size 1.27 1.27)) (justify left))",
            "    )",
        ]

        # 引脚实例
        for pin in sym.pins:
            lines.append(f'    (pin "{pin.number}" (uuid {uuid.uuid4()}))')

        lines.append("  )")
        return lines

    def _generate_power_symbol_instance(self, sym: SCHSymbolV2) -> List[str]:
        """生成电源符号实例"""
        x, y = sym.position

        lines = [
            f'  (symbol (lib_id "power:{sym.name}") (at {x} {y} 0) (unit 1)',
            "    (in_bom yes) (on_board yes) (dnp no)",
            f"    (uuid {uuid.uuid4()})",
            f'    (property "Reference" "{sym.ref}"',
            "      (at 0 -3.81 0)",
            "      (effects (font (size 1.27 1.27)) hide)",
            "    )",
            f'    (property "Value" "{sym.value}"',
            "      (at 0 -1.27 0)",
            "      (effects (font (size 1.27 1.27)))",
            "    )",
        ]

        for pin in sym.pins:
            lines.append(f'    (pin "{pin.number}" (uuid {uuid.uuid4()}))')

        lines.append("  )")
        return lines

    def save(self, filename: str) -> bool:
        """保存到文件"""
        try:
            content = self.generate()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"原理图已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return False


# 向后兼容
SCHSymbol = SCHSymbolV2
SCHWire = SCHWireV2
SchematicFileGenerator = SchematicFileGeneratorV2
