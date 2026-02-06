"""
PCB-Skills v1.0.0 - KiCad自动化设计工具

自动生成KiCad PCB和原理图文件。
生成的文件可直接在KiCad GUI中打开。
"""

__version__ = "1.0.0"
__author__ = "wangzjpku"

from .core_designer import AutoPCBDesigner, create_led_circuit, create_power_supply
from .generators.sch_generator import (
    SchematicFileGenerator,
    SCHSymbol,
    SCHWire,
    SCHJunction,
)
from .generators.pcb_generator import PCBFileGenerator, PCBComponent, PCBTrack

__all__ = [
    "AutoPCBDesigner",
    "create_led_circuit",
    "create_power_supply",
    "SchematicFileGenerator",
    "SCHSymbol",
    "SCHWire",
    "SCHJunction",
    "PCBFileGenerator",
    "PCBComponent",
    "PCBTrack",
]
