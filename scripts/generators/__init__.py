"""
生成器模块 - KiCad文件生成器

提供完整的KiCad原理图和PCB文件生成功能。
"""

# 原理图生成器
from .sch_generator import (
    SchematicFileGenerator,
    SCHSymbol,
    SCHWire,
    SCHJunction,
    SCHLabel,
)

# 增强版原理图生成器 V2
from .sch_generator_v2 import (
    SchematicFileGeneratorV2,
    SymbolLibrary,
    SCHSymbolV2,
    SCHWireV2,
    SCHPin,
    SCHConnection,
)

# PCB生成器
from .pcb_generator import (
    PCBFileGenerator,
    PCBComponent,
    PCBTrack,
    PCBVia,
)

# 增强版PCB生成器 V2
from .pcb_generator_v2 import (
    PCBFileGeneratorV2,
    NetManager,
    PCBComponent as PCBComponentV2,
    PCBTrack as PCBTrackV2,
    PCBVia as PCBViaV2,
)

# 封装库
from .footprint_lib import (
    Footprint,
    Pad,
    get_footprint,
    list_footprints,
    # 电阻
    create_r_0805,
    create_r_1206,
    create_r_axial,
    # 电容
    create_c_0805,
    create_c_elec_8x10,
    create_c_elec_10x10,
    create_c_disc,
    # 二极管
    create_d_sod123,
    create_d_do41,
    create_d_bridge,
    create_d_schottky_to220,
    # IC
    create_dip8,
    create_sop8,
    create_to92,
    # 连接器
    create_terminal_block_2p,
    create_header_2p,
    # 电感/变压器
    create_inductor_radial,
    create_transformer_ee25,
    # 保险丝
    create_fuse_5x20,
    create_fuse_1206,
)

# 布局管理器
from .layout_manager import (
    LayoutRegion,
    SchematicLayout,
    PCBLayout,
    SchematicRouter,
    PCBRouter,
)

__all__ = [
    # V1 生成器（向后兼容）
    "SchematicFileGenerator",
    "SCHSymbol",
    "SCHWire",
    "SCHJunction",
    "SCHLabel",
    "PCBFileGenerator",
    "PCBComponent",
    "PCBTrack",
    "PCBVia",
    # V2 增强版生成器
    "SchematicFileGeneratorV2",
    "SymbolLibrary",
    "SCHSymbolV2",
    "SCHWireV2",
    "SCHPin",
    "SCHConnection",
    "PCBFileGeneratorV2",
    "NetManager",
    "PCBComponentV2",
    "PCBTrackV2",
    "PCBViaV2",
    # 封装库
    "Footprint",
    "Pad",
    "get_footprint",
    "list_footprints",
    # 封装创建函数
    "create_r_0805",
    "create_r_1206",
    "create_r_axial",
    "create_c_0805",
    "create_c_elec_8x10",
    "create_c_elec_10x10",
    "create_c_disc",
    "create_d_sod123",
    "create_d_do41",
    "create_d_bridge",
    "create_d_schottky_to220",
    "create_dip8",
    "create_sop8",
    "create_to92",
    "create_terminal_block_2p",
    "create_header_2p",
    "create_inductor_radial",
    "create_transformer_ee25",
    "create_fuse_5x20",
    "create_fuse_1206",
    # 布局管理器
    "LayoutRegion",
    "SchematicLayout",
    "PCBLayout",
    "SchematicRouter",
    "PCBRouter",
]
