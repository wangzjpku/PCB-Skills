"""
PCB封装库定义

提供常用电子元件的完整KiCad封装定义，包含：
- 焊盘（位置、尺寸、形状、层）
- 丝印图形
- 装配层图形
- 3D模型引用
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Pad:
    """焊盘定义"""

    number: str
    x: float
    y: float
    size_x: float
    size_y: float
    shape: str = "rect"  # rect, circle, oval, roundrect
    layer: str = "F.Cu"
    drill: float = 0.0  # 通孔焊盘的钻孔直径
    net: int = 0
    net_name: str = ""


@dataclass
class Footprint:
    """封装定义"""

    name: str
    description: str
    pads: List[Pad]
    silkscreen: List[Dict] = field(default_factory=list)  # 丝印图形
    fab_layer: List[Dict] = field(default_factory=list)  # 装配层
    courtyard: List[Tuple[float, float]] = field(default_factory=list)  # courtyard边界
    model_3d: str = ""


# ==================== 电阻封装 ====================


def create_r_0805() -> Footprint:
    """0805贴片电阻封装"""
    return Footprint(
        name="R_0805_2012Metric",
        description="Resistor SMD 0805 (2012 Metric)",
        pads=[
            Pad(number="1", x=-1.025, y=0, size_x=1.15, size_y=1.05, shape="roundrect"),
            Pad(number="2", x=1.025, y=0, size_x=1.15, size_y=1.05, shape="roundrect"),
        ],
        silkscreen=[
            {"type": "line", "start": (-0.227, 0.735), "end": (0.227, 0.735)},
            {"type": "line", "start": (-0.227, -0.735), "end": (0.227, -0.735)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-1.0, -0.625), "end": (1.0, 0.625)},
        ],
        courtyard=[(-1.68, -0.95), (1.68, -0.95), (1.68, 0.95), (-1.68, 0.95)],
    )


def create_r_1206() -> Footprint:
    """1206贴片电阻封装"""
    return Footprint(
        name="R_1206_3216Metric",
        description="Resistor SMD 1206 (3216 Metric)",
        pads=[
            Pad(
                number="1", x=-1.4625, y=0, size_x=1.125, size_y=1.75, shape="roundrect"
            ),
            Pad(
                number="2", x=1.4625, y=0, size_x=1.125, size_y=1.75, shape="roundrect"
            ),
        ],
        silkscreen=[
            {"type": "line", "start": (-0.5, 1.0), "end": (0.5, 1.0)},
            {"type": "line", "start": (-0.5, -1.0), "end": (0.5, -1.0)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-1.6, -0.8), "end": (1.6, 0.8)},
        ],
    )


def create_r_axial() -> Footprint:
    """轴向引线电阻（直插）"""
    return Footprint(
        name="R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
        description="Resistor, Axial, 1/4W, 6.3mm body",
        pads=[
            Pad(
                number="1",
                x=-5.08,
                y=0,
                size_x=1.8,
                size_y=1.8,
                shape="circle",
                drill=0.8,
            ),
            Pad(
                number="2",
                x=5.08,
                y=0,
                size_x=1.8,
                size_y=1.8,
                shape="circle",
                drill=0.8,
            ),
        ],
        silkscreen=[
            {"type": "rect", "start": (-3.0, -1.25), "end": (3.0, 1.25)},
            {"type": "line", "start": (-5.08, 0), "end": (-3.0, 0)},
            {"type": "line", "start": (3.0, 0), "end": (5.08, 0)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-3.15, -1.25), "end": (3.15, 1.25)},
        ],
    )


# ==================== 电容封装 ====================


def create_c_0805() -> Footprint:
    """0805贴片电容封装"""
    return Footprint(
        name="C_0805_2012Metric",
        description="Capacitor SMD 0805 (2012 Metric)",
        pads=[
            Pad(number="1", x=-0.95, y=0, size_x=1.0, size_y=1.25, shape="roundrect"),
            Pad(number="2", x=0.95, y=0, size_x=1.0, size_y=1.25, shape="roundrect"),
        ],
        silkscreen=[
            {"type": "line", "start": (-0.5, 0.85), "end": (0.5, 0.85)},
            {"type": "line", "start": (-0.5, -0.85), "end": (0.5, -0.85)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-1.0, -0.625), "end": (1.0, 0.625)},
        ],
    )


def create_c_elec_8x10() -> Footprint:
    """8x10mm 电解电容（直插）"""
    return Footprint(
        name="CP_Radial_D8.0mm_P3.50mm",
        description="Electrolytic Capacitor, 8mm diameter, 3.5mm pitch",
        pads=[
            Pad(
                number="1",
                x=-1.75,
                y=0,
                size_x=2.0,
                size_y=2.0,
                shape="rect",
                drill=1.0,
            ),
            Pad(
                number="2",
                x=1.75,
                y=0,
                size_x=2.0,
                size_y=2.0,
                shape="circle",
                drill=1.0,
            ),
        ],
        silkscreen=[
            {"type": "circle", "center": (0, 0), "radius": 4.2},
            {"type": "line", "start": (-4.2, -2), "end": (-4.2, 2)},  # 极性标记
        ],
        fab_layer=[
            {"type": "circle", "center": (0, 0), "radius": 4.0},
        ],
    )


def create_c_elec_10x10() -> Footprint:
    """10x10mm 电解电容（直插）"""
    return Footprint(
        name="CP_Radial_D10.0mm_P5.00mm",
        description="Electrolytic Capacitor, 10mm diameter, 5mm pitch",
        pads=[
            Pad(
                number="1", x=-2.5, y=0, size_x=2.5, size_y=2.5, shape="rect", drill=1.0
            ),
            Pad(
                number="2",
                x=2.5,
                y=0,
                size_x=2.5,
                size_y=2.5,
                shape="circle",
                drill=1.0,
            ),
        ],
        silkscreen=[
            {"type": "circle", "center": (0, 0), "radius": 5.2},
            {"type": "line", "start": (-5.2, -2.5), "end": (-5.2, 2.5)},
        ],
        fab_layer=[
            {"type": "circle", "center": (0, 0), "radius": 5.0},
        ],
    )


def create_c_disc() -> Footprint:
    """圆片电容（直插）"""
    return Footprint(
        name="C_Disc_D7.5mm_W4.4mm_P5.00mm",
        description="Disc Capacitor, 7.5mm diameter, 5mm pitch",
        pads=[
            Pad(
                number="1",
                x=-2.5,
                y=0,
                size_x=2.0,
                size_y=2.0,
                shape="circle",
                drill=0.8,
            ),
            Pad(
                number="2",
                x=2.5,
                y=0,
                size_x=2.0,
                size_y=2.0,
                shape="circle",
                drill=0.8,
            ),
        ],
        silkscreen=[
            {"type": "rect", "start": (-3.75, -2.2), "end": (3.75, 2.2)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-3.75, -2.2), "end": (3.75, 2.2)},
        ],
    )


# ==================== 二极管封装 ====================


def create_d_sod123() -> Footprint:
    """SOD-123 贴片二极管"""
    return Footprint(
        name="D_SOD-123",
        description="Diode SOD-123",
        pads=[
            Pad(number="1", x=-1.4, y=0, size_x=1.1, size_y=0.9, shape="rect"),  # 阴极
            Pad(
                number="2", x=1.4, y=0, size_x=1.1, size_y=0.9, shape="roundrect"
            ),  # 阳极
        ],
        silkscreen=[
            {"type": "line", "start": (-0.4, 0.7), "end": (-0.4, -0.7)},  # 阴极标记
            {"type": "line", "start": (-0.4, 0.7), "end": (0.8, 0)},
            {"type": "line", "start": (-0.4, -0.7), "end": (0.8, 0)},
            {"type": "line", "start": (0.8, 0.7), "end": (0.8, -0.7)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-0.775, -0.55), "end": (0.775, 0.55)},
        ],
    )


def create_d_do41() -> Footprint:
    """DO-41 直插二极管"""
    return Footprint(
        name="D_DO-41_SOD81_P10.16mm_Horizontal",
        description="Diode DO-41 (SOD81), Axial",
        pads=[
            Pad(
                number="1",
                x=-5.08,
                y=0,
                size_x=2.0,
                size_y=2.0,
                shape="rect",
                drill=1.0,
            ),
            Pad(
                number="2",
                x=5.08,
                y=0,
                size_x=2.0,
                size_y=2.0,
                shape="circle",
                drill=1.0,
            ),
        ],
        silkscreen=[
            {"type": "rect", "start": (-2.5, -1.3), "end": (2.5, 1.3)},
            {"type": "line", "start": (-1.5, 1.3), "end": (-1.5, -1.3)},  # 阴极标记
            {"type": "line", "start": (-5.08, 0), "end": (-2.5, 0)},
            {"type": "line", "start": (2.5, 0), "end": (5.08, 0)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-2.5, -1.3), "end": (2.5, 1.3)},
        ],
    )


def create_d_bridge() -> Footprint:
    """桥式整流器（DIP-4）"""
    return Footprint(
        name="Diode_Bridge_DIP-4",
        description="Diode Bridge, DIP-4",
        pads=[
            Pad(
                number="1",
                x=-3.81,
                y=-2.54,
                size_x=1.5,
                size_y=1.5,
                shape="rect",
                drill=0.8,
            ),
            Pad(
                number="2",
                x=-3.81,
                y=2.54,
                size_x=1.5,
                size_y=1.5,
                shape="circle",
                drill=0.8,
            ),
            Pad(
                number="3",
                x=3.81,
                y=2.54,
                size_x=1.5,
                size_y=1.5,
                shape="circle",
                drill=0.8,
            ),
            Pad(
                number="4",
                x=3.81,
                y=-2.54,
                size_x=1.5,
                size_y=1.5,
                shape="circle",
                drill=0.8,
            ),
        ],
        silkscreen=[
            {"type": "rect", "start": (-5.0, -4.0), "end": (5.0, 4.0)},
            {"type": "circle", "center": (-4.0, -3.0), "radius": 0.3},  # Pin 1标记
        ],
        fab_layer=[
            {"type": "rect", "start": (-4.8, -3.8), "end": (4.8, 3.8)},
        ],
    )


def create_d_schottky_to220() -> Footprint:
    """肖特基二极管 TO-220AC"""
    return Footprint(
        name="D_TO-220AC",
        description="Diode TO-220AC",
        pads=[
            Pad(
                number="1",
                x=-2.54,
                y=0,
                size_x=2.5,
                size_y=2.5,
                shape="rect",
                drill=1.2,
            ),  # 阴极
            Pad(
                number="2",
                x=2.54,
                y=0,
                size_x=2.5,
                size_y=2.5,
                shape="circle",
                drill=1.2,
            ),  # 阳极
        ],
        silkscreen=[
            {"type": "rect", "start": (-5.0, -7.0), "end": (5.0, 2.0)},  # 主体
            {"type": "circle", "center": (-4.0, -6.0), "radius": 0.5},  # Pin 1
        ],
        fab_layer=[
            {"type": "rect", "start": (-5.0, -7.0), "end": (5.0, 2.0)},
        ],
    )


# ==================== IC封装 ====================


def create_dip8() -> Footprint:
    """DIP-8 双列直插封装"""
    pads = []
    for i in range(4):
        pads.append(
            Pad(
                number=str(i + 1),
                x=-3.81,
                y=3.81 - i * 2.54,
                size_x=1.5,
                size_y=1.5,
                shape="circle",
                drill=0.8,
            )
        )
        pads.append(
            Pad(
                number=str(i + 5),
                x=3.81,
                y=-3.81 + i * 2.54,
                size_x=1.5,
                size_y=1.5,
                shape="circle",
                drill=0.8,
            )
        )

    # Pin 1改为方形
    pads[0].shape = "rect"

    return Footprint(
        name="DIP-8_W7.62mm",
        description="DIP-8, 7.62mm width",
        pads=pads,
        silkscreen=[
            {"type": "rect", "start": (-5.0, -5.5), "end": (5.0, 5.5)},
            {
                "type": "arc",
                "center": (-5.0, 5.5),
                "radius": 0.8,
                "start": 0,
                "end": 180,
            },  # Pin 1标记
        ],
        fab_layer=[
            {"type": "rect", "start": (-4.8, -5.3), "end": (4.8, 5.3)},
        ],
    )


def create_sop8() -> Footprint:
    """SOP-8 贴片封装"""
    pads = []
    for i in range(4):
        pads.append(
            Pad(
                number=str(i + 1),
                x=-2.7,
                y=2.275 - i * 1.27,
                size_x=1.5,
                size_y=0.6,
                shape="roundrect",
            )
        )
        pads.append(
            Pad(
                number=str(i + 5),
                x=2.7,
                y=-2.275 + i * 1.27,
                size_x=1.5,
                size_y=0.6,
                shape="roundrect",
            )
        )

    return Footprint(
        name="SOIC-8_3.9x4.9mm_P1.27mm",
        description="SOIC-8, 3.9x4.9mm, 1.27mm pitch",
        pads=pads,
        silkscreen=[
            {"type": "rect", "start": (-2.0, -2.5), "end": (2.0, 2.5)},
            {"type": "circle", "center": (-2.5, 2.5), "radius": 0.3},  # Pin 1
        ],
        fab_layer=[
            {"type": "rect", "start": (-1.95, -2.45), "end": (1.95, 2.45)},
        ],
    )


def create_to92() -> Footprint:
    """TO-92 三极管封装"""
    return Footprint(
        name="TO-92_Inline",
        description="TO-92, Inline",
        pads=[
            Pad(
                number="1",
                x=-2.54,
                y=0,
                size_x=1.5,
                size_y=1.5,
                shape="rect",
                drill=0.8,
            ),
            Pad(
                number="2", x=0, y=0, size_x=1.5, size_y=1.5, shape="circle", drill=0.8
            ),
            Pad(
                number="3",
                x=2.54,
                y=0,
                size_x=1.5,
                size_y=1.5,
                shape="circle",
                drill=0.8,
            ),
        ],
        silkscreen=[
            {"type": "circle", "center": (0, 0), "radius": 2.0},
            {"type": "line", "start": (-2.0, -1.0), "end": (2.0, -1.0)},  # 平底
        ],
        fab_layer=[
            {"type": "circle", "center": (0, 0), "radius": 2.0},
        ],
    )


# ==================== 连接器封装 ====================


def create_terminal_block_2p() -> Footprint:
    """2引脚螺钉端子，5.08mm间距"""
    return Footprint(
        name="TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        description="Terminal Block, 2 pins, 5.08mm pitch",
        pads=[
            Pad(
                number="1",
                x=-2.54,
                y=0,
                size_x=2.5,
                size_y=2.5,
                shape="rect",
                drill=1.3,
            ),
            Pad(
                number="2",
                x=2.54,
                y=0,
                size_x=2.5,
                size_y=2.5,
                shape="circle",
                drill=1.3,
            ),
        ],
        silkscreen=[
            {"type": "rect", "start": (-5.0, -4.0), "end": (5.0, 4.0)},
            {"type": "circle", "center": (-4.0, -3.0), "radius": 0.5},
        ],
        fab_layer=[
            {"type": "rect", "start": (-5.0, -4.0), "end": (5.0, 4.0)},
        ],
    )


def create_header_2p() -> Footprint:
    """2引脚排针"""
    return Footprint(
        name="PinHeader_1x02_P2.54mm_Vertical",
        description="Pin Header, 1x2, 2.54mm pitch, Vertical",
        pads=[
            Pad(
                number="1",
                x=0,
                y=-1.27,
                size_x=1.7,
                size_y=1.7,
                shape="rect",
                drill=1.0,
            ),
            Pad(
                number="2",
                x=0,
                y=1.27,
                size_x=1.7,
                size_y=1.7,
                shape="circle",
                drill=1.0,
            ),
        ],
        silkscreen=[
            {"type": "rect", "start": (-1.25, -2.5), "end": (1.25, 2.5)},
            {"type": "rect", "start": (-1.25, -2.5), "end": (0, -1.25)},  # Pin 1
        ],
        fab_layer=[
            {"type": "rect", "start": (-1.25, -2.5), "end": (1.25, 2.5)},
        ],
    )


# ==================== 电感/变压器封装 ====================


def create_inductor_radial() -> Footprint:
    """径向引线电感"""
    return Footprint(
        name="L_Radial_D7.0mm_P5.00mm",
        description="Inductor, Radial, 7mm diameter, 5mm pitch",
        pads=[
            Pad(
                number="1",
                x=-2.5,
                y=0,
                size_x=2.0,
                size_y=2.0,
                shape="circle",
                drill=0.8,
            ),
            Pad(
                number="2",
                x=2.5,
                y=0,
                size_x=2.0,
                size_y=2.0,
                shape="circle",
                drill=0.8,
            ),
        ],
        silkscreen=[
            {"type": "circle", "center": (0, 0), "radius": 3.5},
        ],
        fab_layer=[
            {"type": "circle", "center": (0, 0), "radius": 3.5},
        ],
    )


def create_transformer_ee25() -> Footprint:
    """EE-25 变压器"""
    # 6引脚：初级2pin + 辅助2pin + 次级2pin
    return Footprint(
        name="Transformer_EE25",
        description="Transformer, EE-25 core, 6 pins",
        pads=[
            # 初级（左侧）
            Pad(
                number="1",
                x=-7.5,
                y=5.0,
                size_x=2.5,
                size_y=2.5,
                shape="rect",
                drill=1.0,
            ),
            Pad(
                number="2",
                x=-7.5,
                y=-5.0,
                size_x=2.5,
                size_y=2.5,
                shape="circle",
                drill=1.0,
            ),
            # 辅助（中间）
            Pad(
                number="3",
                x=0,
                y=5.0,
                size_x=2.0,
                size_y=2.0,
                shape="circle",
                drill=1.0,
            ),
            Pad(
                number="4",
                x=0,
                y=-5.0,
                size_x=2.0,
                size_y=2.0,
                shape="circle",
                drill=1.0,
            ),
            # 次级（右侧）
            Pad(
                number="5",
                x=7.5,
                y=5.0,
                size_x=2.5,
                size_y=2.5,
                shape="circle",
                drill=1.0,
            ),
            Pad(
                number="6",
                x=7.5,
                y=-5.0,
                size_x=2.5,
                size_y=2.5,
                shape="circle",
                drill=1.0,
            ),
        ],
        silkscreen=[
            {"type": "rect", "start": (-10.0, -7.5), "end": (10.0, 7.5)},
            {"type": "line", "start": (-3.0, -7.5), "end": (-3.0, 7.5)},  # 隔离槽
            {"type": "line", "start": (3.0, -7.5), "end": (3.0, 7.5)},
            {"type": "circle", "center": (-9.0, -6.5), "radius": 0.5},  # Pin 1
        ],
        fab_layer=[
            {"type": "rect", "start": (-10.0, -7.5), "end": (10.0, 7.5)},
        ],
    )


# ==================== 保险丝封装 ====================


def create_fuse_5x20() -> Footprint:
    """5x20mm 保险丝座（直插）"""
    return Footprint(
        name="Fuseholder_Cylinder-5x20mm_StaggeredPins",
        description="Fuse Holder, 5x20mm cylinder",
        pads=[
            Pad(
                number="1",
                x=-5.08,
                y=0,
                size_x=2.5,
                size_y=2.5,
                shape="circle",
                drill=1.3,
            ),
            Pad(
                number="2",
                x=5.08,
                y=0,
                size_x=2.5,
                size_y=2.5,
                shape="circle",
                drill=1.3,
            ),
        ],
        silkscreen=[
            {"type": "rect", "start": (-8.0, -3.0), "end": (8.0, 3.0)},
            {"type": "line", "start": (-5.08, 0), "end": (-3.0, 0)},
            {"type": "line", "start": (3.0, 0), "end": (5.08, 0)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-8.0, -3.0), "end": (8.0, 3.0)},
        ],
    )


def create_fuse_1206() -> Footprint:
    """1206 贴片保险丝"""
    return Footprint(
        name="Fuse_1206_3216Metric",
        description="Fuse SMD 1206",
        pads=[
            Pad(number="1", x=-1.5, y=0, size_x=1.0, size_y=1.6, shape="roundrect"),
            Pad(number="2", x=1.5, y=0, size_x=1.0, size_y=1.6, shape="roundrect"),
        ],
        silkscreen=[
            {"type": "rect", "start": (-0.8, 1.0), "end": (0.8, 1.0)},
            {"type": "rect", "start": (-0.8, -1.0), "end": (0.8, -1.0)},
        ],
        fab_layer=[
            {"type": "rect", "start": (-1.6, -0.8), "end": (1.6, 0.8)},
        ],
    )


# ==================== 封装字典 ====================

FOOTPRINT_LIBRARY = {
    # 电阻
    "R_0805": create_r_0805,
    "R_1206": create_r_1206,
    "R_Axial": create_r_axial,
    # 电容
    "C_0805": create_c_0805,
    "C_Elec_8x10": create_c_elec_8x10,
    "C_Elec_10x10": create_c_elec_10x10,
    "C_Disc": create_c_disc,
    # 二极管
    "D_SOD123": create_d_sod123,
    "D_DO41": create_d_do41,
    "D_Bridge": create_d_bridge,
    "D_Schottky_TO220": create_d_schottky_to220,
    # IC
    "DIP8": create_dip8,
    "SOP8": create_sop8,
    "TO92": create_to92,
    # 连接器
    "TerminalBlock_2P": create_terminal_block_2p,
    "Header_2P": create_header_2p,
    # 电感/变压器
    "L_Radial": create_inductor_radial,
    "Transformer_EE25": create_transformer_ee25,
    # 保险丝
    "Fuse_5x20": create_fuse_5x20,
    "Fuse_1206": create_fuse_1206,
}


def get_footprint(name: str) -> Optional[Footprint]:
    """获取封装定义"""
    creator = FOOTPRINT_LIBRARY.get(name)
    if creator:
        return creator()
    return None


def list_footprints() -> List[str]:
    """列出所有可用封装"""
    return list(FOOTPRINT_LIBRARY.keys())
