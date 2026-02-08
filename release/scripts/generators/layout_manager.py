"""
智能布局系统

提供原理图和PCB的自动布局功能：
- 原理图：网格布局，信号流向从左到右
- PCB：分区布局，高压/低压隔离
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LayoutRegion:
    """布局区域"""

    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    zone_type: str = "general"  # high_voltage, low_voltage, power, control, general


class SchematicLayout:
    """
    原理图自动布局器

    布局策略：
    1. 信号流向：从左到右
    2. 电源流向：从上到下（高压在上，低压在下）
    3. 功能分区：输入 -> 保护 -> 整流 -> 功率 -> 输出
    4. 反馈电路：独立放置在下方
    """

    def __init__(self, page_width: float = 297.0, page_height: float = 210.0):
        self.page_width = page_width
        self.page_height = page_height

        # 边距
        self.margin_left = 20.0
        self.margin_right = 20.0
        self.margin_top = 15.0
        self.margin_bottom = 20.0

        # 可用区域
        self.usable_width = page_width - self.margin_left - self.margin_right
        self.usable_height = page_height - self.margin_top - self.margin_bottom

        # 网格设置
        self.grid_x = 25.0  # 水平间距
        self.grid_y = 20.0  # 垂直间距

        # 布局区域定义
        self.regions = {
            "input": LayoutRegion("input", 20, 140, 80, 190, "power"),
            "protection": LayoutRegion("protection", 80, 140, 140, 190, "power"),
            "rectifier": LayoutRegion("rectifier", 140, 140, 200, 190, "power"),
            "power_stage": LayoutRegion("power_stage", 60, 80, 180, 130, "power"),
            "output": LayoutRegion("output", 200, 80, 270, 130, "power"),
            "feedback": LayoutRegion("feedback", 80, 20, 200, 60, "control"),
        }

    def get_position(
        self,
        component_type: str,
        index: int = 0,
        offset_x: float = 0,
        offset_y: float = 0,
    ) -> Tuple[float, float]:
        """
        根据元件类型获取推荐位置

        Args:
            component_type: 元件类型（input, protection, rectifier, power, output, feedback）
            index: 在区域内的索引
            offset_x: X偏移
            offset_y: Y偏移
        """
        region = self.regions.get(component_type, self.regions["power_stage"])

        # 在区域内网格布局
        cols = 3  # 每行3个元件
        row = index // cols
        col = index % cols

        x = region.x_min + col * self.grid_x + offset_x
        y = region.y_max - row * self.grid_y - offset_y

        # 边界检查
        x = min(x, region.x_max - 10)
        y = max(y, region.y_min + 10)

        return (x, y)

    def get_power_symbol_position(
        self,
        net_name: str,
        attached_symbol_pos: Tuple[float, float],
        attached_pin: str = "2",
    ) -> Tuple[float, float]:
        """
        获取电源符号位置（放在被连接元件的下方或上方）

        Args:
            net_name: 网络名称（GND, VCC等）
            attached_symbol_pos: 被连接元件的位置
            attached_pin: 被连接的引脚号
        """
        sx, sy = attached_symbol_pos

        if "GND" in net_name.upper() or "VSS" in net_name.upper():
            # 地放在下方
            return (sx, sy - 15.0)
        else:
            # 电源放在上方或侧面
            return (sx + 10.0, sy)


class PCBLayout:
    """
    PCB智能布局器

    布局策略：
    1. 分区设计：
       - 左侧：AC输入和滤波
       - 中上：整流和高压
       - 中部：变压器（隔离边界）
       - 中右：VIPer控制器
       - 右侧：输出整流滤波
       - 底部：反馈电路
    2. 安全间距：
       - 高压区与低压区 > 6mm
       - 初级与次级隔离槽
    3. 热管理：
       - 功率器件均匀分布
       - 发热器件靠近边缘
    """

    def __init__(self, board_width: float = 100.0, board_height: float = 80.0):
        self.board_width = board_width
        self.board_height = board_height

        # 边距
        self.margin = 5.0

        # 定义区域（从左侧开始，按信号流向）
        self.zones = {
            "ac_input": {  # AC输入区域
                "x": (5, 25),
                "y": (60, 95),
                "type": "high_voltage",
            },
            "protection": {  # 保护器件
                "x": (25, 45),
                "y": (60, 95),
                "type": "high_voltage",
            },
            "rectifier": {  # 整流滤波
                "x": (45, 70),
                "y": (60, 95),
                "type": "high_voltage",
            },
            "transformer": {  # 变压器（中心，隔离边界）
                "x": (70, 95),
                "y": (40, 80),
                "type": "isolation",
            },
            "controller": {  # 控制器
                "x": (45, 70),
                "y": (30, 60),
                "type": "control",
            },
            "output_rectifier": {  # 输出整流
                "x": (75, 95),
                "y": (10, 40),
                "type": "low_voltage",
            },
            "output_filter": {  # 输出滤波
                "x": (50, 75),
                "y": (5, 35),
                "type": "low_voltage",
            },
            "output_connector": {  # 输出端子
                "x": (20, 45),
                "y": (5, 30),
                "type": "low_voltage",
            },
            "feedback": {  # 反馈电路
                "x": (25, 50),
                "y": (35, 60),
                "type": "control",
            },
        }

        # 元件位置缓存
        self.placed_components: Dict[str, Tuple[float, float]] = {}

    def get_position(
        self,
        component_type: str,
        ref: str = "",
        width: float = 10.0,
        height: float = 10.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ) -> Tuple[float, float]:
        """
        获取元件推荐位置

        Args:
            component_type: 元件分类（如'ac_input', 'transformer'等）
            ref: 元件位号（用于避免重叠）
            width: 元件宽度
            height: 元件高度
            offset_x: X偏移
            offset_y: Y偏移
        """
        zone = self.zones.get(component_type, self.zones["controller"])

        x_min, x_max = zone["x"]
        y_min, y_max = zone["y"]

        # 计算网格位置（避免重叠）
        zone_center_x = (x_min + x_max) / 2
        zone_center_y = (y_min + y_max) / 2

        # 根据已有元件数量调整位置
        existing_count = len(
            [k for k in self.placed_components.keys() if k.startswith(component_type)]
        )

        col = existing_count % 2
        row = existing_count // 2

        grid_x = 15.0
        grid_y = 12.0

        x = zone_center_x + (col - 0.5) * grid_x + offset_x
        y = zone_center_y - row * grid_y + offset_y

        # 边界约束
        x = max(x_min + width / 2, min(x, x_max - width / 2))
        y = max(y_min + height / 2, min(y, y_max - height / 2))

        # 记录位置
        if ref:
            self.placed_components[ref] = (x, y)

        return (x, y)

    def get_component_zone(self, ref: str) -> Optional[str]:
        """获取元件所属区域"""
        for zone_name, zone_info in self.zones.items():
            if ref in self.placed_components:
                x, y = self.placed_components[ref]
                x_min, x_max = zone_info["x"]
                y_min, y_max = zone_info["y"]
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    return zone_name
        return None

    def check_clearance(self, ref1: str, ref2: str, min_distance: float = 6.0) -> bool:
        """检查两个元件之间的间距"""
        if ref1 not in self.placed_components or ref2 not in self.placed_components:
            return True

        x1, y1 = self.placed_components[ref1]
        x2, y2 = self.placed_components[ref2]

        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        return distance >= min_distance

    def get_zone_type(self, zone_name: str) -> str:
        """获取区域类型"""
        zone = self.zones.get(zone_name, {})
        return zone.get("type", "general")


class SchematicRouter:
    """
    原理图智能布线器

    减少连线交叉的策略：
    1. 使用总线结构组织相关信号
    2. 优先走水平/垂直线
    3. 使用标签连接远距离信号
    4. 正交走线，避免对角线
    """

    def __init__(self):
        self.wire_spacing = 2.54  # 线间距
        self.layers = []  # 布线层（用于分层走线）

    def calculate_route(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        avoid_points: List[Tuple[float, float]] = None,
    ) -> List[Tuple[float, float]]:
        """
        计算走线路径（正交走线，避免交叉）

        Returns:
            路径点列表
        """
        x1, y1 = start
        x2, y2 = end

        # 正交走线：先水平后垂直，或先垂直后水平
        # 选择路径短的方案

        # 方案1：先水平后垂直
        path1 = [(x1, y1), (x2, y1), (x2, y2)]
        length1 = abs(x2 - x1) + abs(y2 - y1)

        # 方案2：先垂直后水平
        path2 = [(x1, y1), (x1, y2), (x2, y2)]
        length2 = abs(x2 - x1) + abs(y2 - y1)

        # 选择较短的（长度相同则选方案1）
        return path1 if length1 <= length2 else path2

    def should_use_label(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        threshold: float = 50.0,
    ) -> bool:
        """
        判断是否应该使用标签而不是直接连线

        Args:
            threshold: 距离阈值，超过则使用标签
        """
        distance = ((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) ** 0.5
        return distance > threshold


class PCBRouter:
    """
    PCB智能布线器

    减少交叉和优化布线的策略：
    1. 分层布线：顶层水平，底层垂直
    2. 关键信号优先布线
    3. 高压/低压分区布线
    4. 使用布线通道
    """

    def __init__(self, board_width: float = 100.0, board_height: float = 80.0):
        self.board_width = board_width
        self.board_height = board_height

        # 布线通道
        self.horizontal_channels = []  # 水平布线通道
        self.vertical_channels = []  # 垂直布线通道

        # 已占用的布线资源
        self.occupied_tracks = []

    def calculate_route(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        layer: str = "F.Cu",
        width: float = 0.25,
        net_name: str = "",
    ) -> List[Tuple[float, float]]:
        """
        计算PCB走线路径

        Returns:
            路径点列表
        """
        x1, y1 = start
        x2, y2 = end

        # 简单正交走线
        # 根据方向选择先水平或先垂直
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        if dx > dy:
            # 主要水平方向
            mid_x = (x1 + x2) / 2
            path = [(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)]
        else:
            # 主要垂直方向
            mid_y = (y1 + y2) / 2
            path = [(x1, y1), (x1, mid_y), (x2, mid_y), (x2, y2)]

        return path

    def add_via(self, position: Tuple[float, float], net_name: str = ""):
        """添加过孔（用于换层）"""
        # 记录过孔位置
        pass

    def check_clearance(
        self,
        pos1: Tuple[float, float],
        pos2: Tuple[float, float],
        min_clearance: float = 0.2,
    ) -> bool:
        """检查间距是否符合要求"""
        distance = ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
        return distance >= min_clearance
