"""
原理图文件生成器

直接生成KiCad .kicad_sch文件（S-expression格式）。
生成的文件可直接在KiCad GUI中打开。
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SCHSymbol:
    """原理图符号（器件）"""

    ref: str  # 参考位号
    name: str  # 符号名称
    value: str  # 器件值
    position: Tuple[float, float]  # (x, y) in mm
    pins: List[Dict] = field(
        default_factory=list
    )  # 引脚列表 [{"number": "1", "name": "VCC"}, ...]
    rotation: float = 0.0  # 旋转角度
    mirror: bool = False  # 是否镜像


@dataclass
class SCHWire:
    """原理图连线"""

    start: Tuple[float, float]  # (x, y) in mm
    end: Tuple[float, float]  # (x, y) in mm


@dataclass
class SCHLabel:
    """原理图标签"""

    text: str
    position: Tuple[float, float]
    label_type: str = "local"  # local, global, hierarchical
    rotation: float = 0.0


@dataclass
class SCHJunction:
    """原理图连接点（junction）"""

    position: Tuple[float, float]


class SchematicFileGenerator:
    """
    原理图文件生成器

    生成符合KiCad标准的.kicad_sch文件。
    文件格式为S-expression（Lisp风格）。
    """

    def __init__(self):
        self.symbols: List[SCHSymbol] = []
        self.wires: List[SCHWire] = []
        self.labels: List[SCHLabel] = []
        self.junctions: List[SCHJunction] = []
        self.power_symbols: List[SCHSymbol] = []

        # 原理图规格
        self.page_width = 210.0  # A4纸宽
        self.page_height = 297.0  # A4纸高
        self.schematic_name = "Untitled"
        self.schematic_uuid = self._generate_uuid()

    def _generate_uuid(self) -> str:
        """生成UUID"""
        return str(uuid.uuid4())

    def set_page_properties(
        self, width: float = 210.0, height: float = 297.0, name: str = "Untitled"
    ):
        """设置页面属性"""
        self.page_width = width
        self.page_height = height
        self.schematic_name = name
        logger.info(f"原理图: {width}x{height}mm, 名称={name}")

    def add_symbol(self, symbol: SCHSymbol):
        """添加符号"""
        self.symbols.append(symbol)
        logger.debug(f"添加符号: {symbol.ref}")

    def add_wire(self, wire: SCHWire):
        """添加连线"""
        self.wires.append(wire)
        logger.debug(f"添加连线")

    def add_label(self, label: SCHLabel):
        """添加标签"""
        self.labels.append(label)
        logger.debug(f"添加标签: {label.text}")

    def add_junction(self, junction: SCHJunction):
        """添加连接点"""
        self.junctions.append(junction)

    def add_power_symbol(self, symbol: SCHSymbol):
        """添加电源符号"""
        self.power_symbols.append(symbol)

    def generate(self) -> str:
        """
        生成.kicad_sch文件内容

        Returns:
            str: KiCad S-expression格式的内容
        """
        lines = []

        # 文件头 - 修正：添加uuid
        lines.append('(kicad_sch (version 20240108) (generator "pcb-nlp-skill")')
        lines.append(f"  (uuid {self.schematic_uuid})")
        lines.append('  (paper "A4")')
        lines.append("")

        # 标题块
        lines.append("  (title_block")
        lines.append(f'    (title "{self.schematic_name}")')
        lines.append('    (date "2026-02-06")')
        lines.append('    (rev "1")')
        lines.append('    (company "Auto Generated")')
        lines.append("  )")
        lines.append("")

        # 库符号定义
        lines.append("  (lib_symbols")
        lines.extend(self._generate_lib_symbols())
        lines.append("  )")
        lines.append("")

        # 连接点
        for junction in self.junctions:
            lines.extend(self._generate_junction(junction))
        if self.junctions:
            lines.append("")

        # 连线
        for wire in self.wires:
            lines.extend(self._generate_wire(wire))
        if self.wires:
            lines.append("")

        # 标签
        for label in self.labels:
            lines.extend(self._generate_label(label))
        if self.labels:
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

        # 根工作表实例 - 修正：添加必需的sheet_instances
        lines.append("  (sheet_instances")
        lines.append('    (path "/" (page "1"))')
        lines.append("  )")

        # 文件尾
        lines.append(")")

        return "\n".join(lines)

    def _generate_lib_symbols(self) -> List[str]:
        """生成库符号定义"""
        lines = []

        # 电阻符号
        lines.append('    (symbol "Device:R"')
        lines.append("      (pin_numbers hide)")
        lines.append("      (pin_names (offset 0))")
        lines.append("      (exclude_from_sim no)")
        lines.append("      (in_bom yes)")
        lines.append("      (on_board yes)")
        lines.append('      (property "Reference" "R"')
        lines.append("        (at 2.032 0 90)")
        lines.append("        (effects (font (size 1.27 1.27)))")
        lines.append("      )")
        lines.append('      (property "Value" "R"')
        lines.append("        (at 0 0 90)")
        lines.append("        (effects (font (size 1.27 1.27)))")
        lines.append("      )")
        lines.append('      (symbol "R_0_1"')
        lines.append("        (rectangle (start -1.016 -2.54) (end 1.016 2.54)")
        lines.append("          (stroke (width 0.254) (type default))")
        lines.append("          (fill (type none))")
        lines.append("        )")
        lines.append("      )")
        lines.append('      (symbol "R_1_1"')
        lines.append("        (pin passive line (at 0 3.81 270) (length 1.27)")
        lines.append('          (name "~" (effects (font (size 1.27 1.27))))')
        lines.append('          (number "1" (effects (font (size 1.27 1.27))))')
        lines.append("        )")
        lines.append("        (pin passive line (at 0 -3.81 90) (length 1.27)")
        lines.append('          (name "~" (effects (font (size 1.27 1.27))))')
        lines.append('          (number "2" (effects (font (size 1.27 1.27))))')
        lines.append("        )")
        lines.append("      )")
        lines.append("    )")

        # LED符号
        lines.append('    (symbol "Device:LED"')
        lines.append("      (pin_numbers hide)")
        lines.append("      (pin_names (offset 1.016) hide)")
        lines.append("      (exclude_from_sim no)")
        lines.append("      (in_bom yes)")
        lines.append("      (on_board yes)")
        lines.append('      (property "Reference" "D"')
        lines.append("        (at -1.27 3.81 0)")
        lines.append("        (effects (font (size 1.27 1.27)) (justify right))")
        lines.append("      )")
        lines.append('      (property "Value" "LED"')
        lines.append("        (at -1.27 1.27 0)")
        lines.append("        (effects (font (size 1.27 1.27)) (justify right))")
        lines.append("      )")
        lines.append('      (symbol "LED_0_1"')
        lines.append("        (polyline")
        lines.append("          (pts")
        lines.append(
            "            (xy -1.27 -1.27) (xy 1.27 0) (xy -1.27 1.27) (xy -1.27 -1.27)"
        )
        lines.append("          )")
        lines.append("          (stroke (width 0.2032) (type default))")
        lines.append("          (fill (type none))")
        lines.append("        )")
        lines.append("        (polyline")
        lines.append("          (pts (xy -1.27 0) (xy 1.27 0))")
        lines.append("          (stroke (width 0) (type default))")
        lines.append("          (fill (type none))")
        lines.append("        )")
        lines.append("      )")
        lines.append('      (symbol "LED_1_1"')
        lines.append("        (pin passive line (at -3.81 0 0) (length 2.54)")
        lines.append('          (name "K" (effects (font (size 1.27 1.27))))')
        lines.append('          (number "2" (effects (font (size 1.27 1.27))))')
        lines.append("        )")
        lines.append("        (pin passive line (at 3.81 0 180) (length 2.54)")
        lines.append('          (name "A" (effects (font (size 1.27 1.27))))')
        lines.append('          (number "1" (effects (font (size 1.27 1.27))))')
        lines.append("        )")
        lines.append("      )")
        lines.append("    )")

        # VCC电源符号
        lines.append('    (symbol "power:+5V"')
        lines.append("      (power)")
        lines.append("      (pin_numbers hide)")
        lines.append("      (pin_names (offset 0) hide)")
        lines.append("      (exclude_from_sim no)")
        lines.append("      (in_bom yes)")
        lines.append("      (on_board yes)")
        lines.append('      (property "Reference" "#PWR"')
        lines.append("        (at 0 -3.81 0)")
        lines.append("        (effects (font (size 1.27 1.27)) hide)")
        lines.append("      )")
        lines.append('      (property "Value" "+5V"')
        lines.append("        (at 0 3.556 0)")
        lines.append("        (effects (font (size 1.27 1.27)))")
        lines.append("      )")
        lines.append('      (symbol "+5V_0_0"')
        lines.append("        (polyline")
        lines.append("          (pts (xy -0.762 1.27) (xy 0 2.54) (xy 0.762 1.27))")
        lines.append("          (stroke (width 0) (type default))")
        lines.append("          (fill (type outline))")
        lines.append("        )")
        lines.append("        (polyline")
        lines.append("          (pts (xy 0 0) (xy 0 2.54))")
        lines.append("          (stroke (width 0) (type default))")
        lines.append("          (fill (type none))")
        lines.append("        )")
        lines.append("      )")
        lines.append('      (symbol "+5V_1_0"')
        lines.append("        (pin power_in line (at 0 0 90) (length 0)")
        lines.append('          (name "+5V" (effects (font (size 1.27 1.27))))')
        lines.append('          (number "1" (effects (font (size 1.27 1.27))))')
        lines.append("        )")
        lines.append("      )")
        lines.append("    )")

        # GND电源符号
        lines.append('    (symbol "power:GND"')
        lines.append("      (power)")
        lines.append("      (pin_numbers hide)")
        lines.append("      (pin_names (offset 0) hide)")
        lines.append("      (exclude_from_sim no)")
        lines.append("      (in_bom yes)")
        lines.append("      (on_board yes)")
        lines.append('      (property "Reference" "#PWR"')
        lines.append("        (at 0 -6.35 0)")
        lines.append("        (effects (font (size 1.27 1.27)) hide)")
        lines.append("      )")
        lines.append('      (property "Value" "GND"')
        lines.append("        (at 0 -3.81 0)")
        lines.append("        (effects (font (size 1.27 1.27)))")
        lines.append("      )")
        lines.append('      (symbol "GND_0_0"')
        lines.append(
            "        (polyline (pts (xy 0 0) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))"
        )
        lines.append(
            "        (polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27)) (stroke (width 0) (type default)) (fill (type none)))"
        )
        lines.append(
            "        (polyline (pts (xy -0.762 -1.905) (xy 0.762 -1.905)) (stroke (width 0) (type default)) (fill (type none)))"
        )
        lines.append(
            "        (polyline (pts (xy -0.254 -2.54) (xy 0.254 -2.54)) (stroke (width 0) (type default)) (fill (type none)))"
        )
        lines.append("      )")
        lines.append('      (symbol "GND_1_0"')
        lines.append("        (pin power_in line (at 0 0 90) (length 0)")
        lines.append('          (name "GND" (effects (font (size 1.27 1.27))))')
        lines.append('          (number "1" (effects (font (size 1.27 1.27))))')
        lines.append("        )")
        lines.append("      )")
        lines.append("    )")

        return lines

    def _generate_junction(self, junction: SCHJunction) -> List[str]:
        """生成连接点"""
        x, y = junction.position
        lines = [
            f"  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0)",
            f"    (uuid {self._generate_uuid()})",
            f"  )",
        ]
        return lines

    def _generate_wire(self, wire: SCHWire) -> List[str]:
        """生成连线 - 修正：使用正确的wire格式"""
        x1, y1 = wire.start
        x2, y2 = wire.end

        lines = [
            f"  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))",
            f"    (stroke (width 0) (type default))",
            f"    (uuid {self._generate_uuid()})",
            f"  )",
        ]
        return lines

    def _generate_label(self, label: SCHLabel) -> List[str]:
        """生成标签"""
        x, y = label.position

        if label.label_type == "global":
            lines = [
                f'  (global_label "{label.text}" (shape input)',
                f"    (at {x} {y} {label.rotation})",
                f"    (effects (font (size 1.27 1.27)))",
                f"    (uuid {self._generate_uuid()})",
                f"  )",
            ]
        else:
            lines = [
                f'  (label "{label.text}" (at {x} {y} {label.rotation})',
                f"    (effects (font (size 1.27 1.27)))",
                f"    (uuid {self._generate_uuid()})",
                f"  )",
            ]
        return lines

    def _generate_symbol_instance(self, symbol: SCHSymbol) -> List[str]:
        """生成符号实例 - 修正：使用正确的格式，毫米而非纳米"""
        x, y = symbol.position

        lines = [
            f'  (symbol (lib_id "Device:{symbol.name}") (at {x} {y} {symbol.rotation}) (unit 1)',
            f"    (in_bom yes) (on_board yes) (dnp no)",
        ]

        if symbol.mirror:
            lines.append("    (mirror y)")

        lines.append(f"    (uuid {self._generate_uuid()})")

        # 属性
        lines.append(f'    (property "Reference" "{symbol.ref}"')
        lines.append(f"      (at {x + 1.27} {y - 1.27} {symbol.rotation})")
        lines.append("      (effects (font (size 1.27 1.27)) (justify left))")
        lines.append("    )")

        lines.append(f'    (property "Value" "{symbol.value}"')
        lines.append(f"      (at {x + 1.27} {y + 1.27} {symbol.rotation})")
        lines.append("      (effects (font (size 1.27 1.27)) (justify left))")
        lines.append("    )")

        # 引脚
        for pin in symbol.pins:
            lines.append(f'    (pin "{pin["number"]}" (uuid {self._generate_uuid()}))')

        lines.append("  )")
        return lines

    def _generate_power_symbol_instance(self, symbol: SCHSymbol) -> List[str]:
        """生成电源符号实例"""
        x, y = symbol.position
        power_name = symbol.name

        lines = [
            f'  (symbol (lib_id "power:{power_name}") (at {x} {y} 0) (unit 1)',
            f"    (in_bom yes) (on_board yes) (dnp no)",
            f"    (uuid {self._generate_uuid()})",
            f'    (property "Reference" "{symbol.ref}"',
            f"      (at {x} {y - 3.81} 0)",
            "      (effects (font (size 1.27 1.27)) hide)",
            "    )",
            f'    (property "Value" "{power_name}"',
            f"      (at {x} {y - 1.27} 0)",
            "      (effects (font (size 1.27 1.27)))",
            "    )",
        ]

        # 引脚
        for pin in symbol.pins:
            lines.append(f'    (pin "{pin["number"]}" (uuid {self._generate_uuid()}))')

        lines.append("  )")
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
            logger.info(f"原理图已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return False


def create_simple_schematic(
    width: float = 210.0, height: float = 297.0, components: List[SCHSymbol] = None
) -> SchematicFileGenerator:
    """
    创建简单原理图的便捷函数

    Args:
        width: 页面宽度（mm）
        height: 页面高度（mm）
        components: 组件列表

    Returns:
        SchematicFileGenerator: 配置好的生成器
    """
    generator = SchematicFileGenerator()
    generator.set_page_properties(width, height)

    if components:
        for comp in components:
            generator.add_symbol(comp)

    return generator
