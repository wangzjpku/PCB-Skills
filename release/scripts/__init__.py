"""
PCB-Skills v7.0.0 - KiCad自动化设计工具 (KiCad集成版)

完整的KiCad集成解决方案：
1. KiCad Python API (pcbnew) 直接集成
2. 自动生成220V转12V电源设计
3. 专业级自动布局和布线
4. 可作为KiCad插件运行

作者: AI Assistant
版本: 7.0.0 (KiCad集成版)
"""

__version__ = "7.0.0"
__author__ = "AI Assistant"

# ========== KiCad集成模块 ==========
try:
    from .kicad_integration import KiCadAPI, KiCadComponent, KiCadPlugin
    from .power_supply_designer import PowerSupplyDesigner, PowerSupplyConfig

    KICAD_INTEGRATION_AVAILABLE = True
except ImportError:
    KICAD_INTEGRATION_AVAILABLE = False

# ========== 核心文件生成器 ==========
from .generators.sch_generator import (
    SchematicFileGenerator,
    SCHSymbol,
    SCHWire,
    SCHJunction,
    SCHLabel,
)

from .generators.sch_generator_v2 import (
    SchematicFileGeneratorV2,
    SymbolLibrary,
    SCHSymbolV2,
    SCHWireV2,
    SCHPin,
    SCHConnection,
)

from .generators.pcb_generator import (
    PCBFileGenerator,
    PCBComponent,
    PCBTrack,
    PCBVia,
)

from .generators.pcb_generator_v2 import (
    PCBFileGeneratorV2,
    NetManager,
    PCBComponent as PCBComponentV2,
    PCBTrack as PCBTrackV2,
    PCBVia as PCBViaV2,
)

# ========== 封装库 ==========
from .generators.footprint_lib import (
    Footprint,
    Pad,
    get_footprint,
    list_footprints,
    create_r_0805,
    create_r_1206,
    create_c_elec_8x10,
    create_c_elec_10x10,
    create_d_bridge,
    create_dip8,
    create_transformer_ee25,
    create_terminal_block_2p,
    create_fuse_5x20,
)

# ========== 布局管理器 ==========
from .generators.layout_manager import (
    LayoutRegion,
    SchematicLayout,
    PCBLayout,
    SchematicRouter,
    PCBRouter,
)

# ========== 输出管理 ==========
from .output_manager import OutputManager, get_output_manager

# ========== 向后兼容 ==========
try:
    from .core_designer import AutoPCBDesigner, create_led_circuit, create_power_supply

    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    # KiCad集成
    "KiCadAPI",
    "KiCadComponent",
    "KiCadPlugin",
    "PowerSupplyDesigner",
    "PowerSupplyConfig",
    "KICAD_INTEGRATION_AVAILABLE",
    # 文件生成器
    "SchematicFileGenerator",
    "SchematicFileGeneratorV2",
    "SymbolLibrary",
    "SCHSymbolV2",
    "SCHWireV2",
    "SCHPin",
    "SCHConnection",
    "PCBFileGenerator",
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
    "create_r_0805",
    "create_r_1206",
    "create_c_elec_8x10",
    "create_c_elec_10x10",
    "create_d_bridge",
    "create_dip8",
    "create_transformer_ee25",
    "create_terminal_block_2p",
    "create_fuse_5x20",
    # 布局
    "LayoutRegion",
    "SchematicLayout",
    "PCBLayout",
    "SchematicRouter",
    "PCBRouter",
    # 输出
    "OutputManager",
    "get_output_manager",
]

if LEGACY_AVAILABLE:
    __all__.extend(
        [
            "AutoPCBDesigner",
            "create_led_circuit",
            "create_power_supply",
            "LEGACY_AVAILABLE",
        ]
    )


def check_kicad_integration():
    """检查KiCad集成是否可用"""
    if KICAD_INTEGRATION_AVAILABLE:
        try:
            import pcbnew

            return True
        except ImportError:
            return False
    return False


def get_version_info():
    """获取版本信息"""
    return {
        "version": __version__,
        "author": __author__,
        "kicad_integration": check_kicad_integration(),
        "legacy_support": LEGACY_AVAILABLE
        if "LEGACY_AVAILABLE" in globals()
        else False,
        "features": [
            "KiCad Python API集成 (pcbnew)",
            "自动布局（网格/线性/聚类/专业）",
            "自动布线（使用KiCad PNS路由器）",
            "220V转12V完整电源设计",
            "VIPer22A反激式方案",
            "专业级分区布局",
            "电流回路最小化",
            "星型接地系统",
        ],
        "usage_modes": [
            "KiCad插件模式（推荐）",
            "Python脚本模式",
            "独立文件生成模式",
        ],
    }


def print_welcome():
    """打印欢迎信息"""
    info = get_version_info()
    print("=" * 70)
    print(f"KiCad Auto-Design Skill v{info['version']}")
    print(f"作者: {info['author']}")
    print("=" * 70)
    print(f"\nKiCad集成状态: {'✓ 可用' if info['kicad_integration'] else '✗ 不可用'}")
    print("\n功能列表:")
    for i, feat in enumerate(info["features"], 1):
        print(f"  {i}. {feat}")
    print("\n使用模式:")
    for i, mode in enumerate(info["usage_modes"], 1):
        print(f"  {i}. {mode}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print_welcome()
