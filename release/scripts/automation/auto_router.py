"""
自动布线模块 - KiCad PCB 自动布线

集成 FreeRouting (freerouting/freerouting)
https://github.com/freerouting/freerouting

功能:
- 自动导出 DSN 文件
- 调用 FreeRouting 自动布线
- 导入 SES 文件
- 支持批处理和命令行模式
"""

import os
import sys
import subprocess
import logging
import tempfile
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RoutingConstraints:
    """布线约束设置"""

    min_track_width: float = 0.25  # 最小线宽 (mm)
    min_via_size: float = 0.8  # 最小过孔尺寸 (mm)
    min_via_drill: float = 0.4  # 最小过孔钻孔 (mm)
    min_clearance: float = 0.2  # 最小间距 (mm)
    max_passes: int = 10  # 最大布线轮数
    optimize_vias: bool = True  # 优化过孔


@dataclass
class NetClass:
    """网络类定义"""

    name: str
    track_width: float = 0.25
    via_size: float = 0.8
    via_drill: float = 0.4
    clearance: float = 0.2


class FreeRoutingBridge:
    """
    FreeRouting 桥接器

    负责与 FreeRouting 自动布线器的交互:
    1. 生成 DSN 文件 (Specctra 格式)
    2. 调用 FreeRouting 进行布线
    3. 解析 SES 文件并应用结果
    """

    def __init__(self, freerouting_path: Optional[str] = None):
        """
        初始化

        Args:
            freerouting_path: FreeRouting 可执行文件路径 (JAR 文件)
                           如果为 None，尝试自动检测
        """
        self.freerouting_path = freerouting_path or self._find_freerouting()
        self.constraints = RoutingConstraints()
        self.net_classes: Dict[str, NetClass] = {}

    def _find_freerouting(self) -> Optional[str]:
        """自动查找 FreeRouting 安装"""
        # 常见安装路径
        possible_paths = [
            # Windows
            os.path.expandvars(
                r"%LOCALAPPDATA%\\KiCad\\8.0\\3rdparty\\plugins\\com.github.freerouting.freerouting\\freerouting.jar"
            ),
            os.path.expandvars(
                r"%LOCALAPPDATA%\\KiCad\\9.0\\3rdparty\\plugins\\com.github.freerouting.freerouting\\freerouting.jar"
            ),
            # Linux
            os.path.expanduser(
                "~/.local/share/kicad/8.0/3rdparty/plugins/com.github.freerouting.freerouting/freerouting.jar"
            ),
            os.path.expanduser(
                "~/.local/share/kicad/9.0/3rdparty/plugins/com.github.freerouting.freerouting/freerouting.jar"
            ),
            # macOS
            os.path.expanduser(
                "~/Library/Application Support/kicad/8.0/3rdparty/plugins/com.github.freerouting.freerouting/freerouting.jar"
            ),
            # 系统 PATH
            "freerouting.jar",
        ]

        for path in possible_paths:
            if os.path.isfile(path):
                logger.info(f"找到 FreeRouting: {path}")
                return path

        logger.warning("未找到 FreeRouting，请手动指定路径或安装插件")
        return None

    def check_installation(self) -> bool:
        """检查 FreeRouting 是否可用"""
        if not self.freerouting_path:
            return False

        if not os.path.isfile(self.freerouting_path):
            logger.error(f"FreeRouting 文件不存在: {self.freerouting_path}")
            return False

        # 检查 Java
        try:
            result = subprocess.run(
                ["java", "-version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                logger.info("Java 运行环境已安装")
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("未找到 Java 运行环境，请先安装 JRE 17+")

        return False

    def generate_dsn_content(
        self,
        board_name: str,
        components: List[Dict],
        nets: List[Dict],
        board_outline: List[Tuple[float, float]],
    ) -> str:
        """
        生成 DSN 文件内容 (Specctra 格式)

        Args:
            board_name: 板子名称
            components: 元件列表
            nets: 网络列表
            board_outline: 板框坐标

        Returns:
            str: DSN 文件内容
        """
        lines = []

        # 文件头
        lines.append('(pcb "{}")'.format(board_name))
        lines.append("  (parser")
        lines.append('    (string_quote "\'")')
        lines.append("    (space_in_quoted_tokens on)")
        lines.append('    (host_cad "KiCad")')
        lines.append('    (host_version "9.0")')
        lines.append("  )")

        # 分辨率
        lines.append("  (resolution mm 1000000)")

        # 单位
        lines.append("  (unit mm)")

        # 结构定义 (板框)
        lines.append("  (structure")
        # 板框边界
        if board_outline:
            outline_str = " ".join([f"{x} {y}" for x, y in board_outline])
            lines.append(f"    (boundary (rect pcb {outline_str}))")

        # 布线约束
        lines.append(f"    (rule")
        lines.append(f"      (width {self.constraints.min_track_width})")
        lines.append(f"      (clearance {self.constraints.min_clearance})")
        lines.append(f"      (via (via_sizes {self.constraints.min_via_size}))")
        lines.append("    )")
        lines.append("  )")

        # 放置定义
        lines.append("  (placement")
        for comp in components:
            ref = comp.get("ref", "U?")
            x = comp.get("x", 0)
            y = comp.get("y", 0)
            rotation = comp.get("rotation", 0)
            side = comp.get("layer", "F.Cu")
            place_side = "front" if side == "F.Cu" else "back"

            lines.append(f'    (component "{ref}"')
            lines.append(f"      (place {ref} {x} {y} {rotation} {place_side})")
            lines.append("    )")
        lines.append("  )")

        # 库定义 (简化)
        lines.append("  (library")
        for comp in components:
            ref = comp.get("ref", "U?")
            footprint = comp.get("footprint", "SMD")
            lines.append(f'    (image "{footprint}"')
            lines.append("      (outline (rect front -1 -1 1 1))")
            # 引脚
            for pin in comp.get("pins", []):
                pin_num = pin.get("number", "1")
                pin_x = pin.get("x", 0)
                pin_y = pin.get("y", 0)
                lines.append(f"      (pin {pin_num} {pin_x} {pin_y})")
            lines.append("    )")
            lines.append(f'    (padstack "Pin_{ref}"')
            lines.append(f"      (pin {ref})")
            lines.append("    )")
        lines.append("  )")

        # 网络定义
        lines.append("  (network")
        for net in nets:
            net_name = net.get("name", "unnamed")
            lines.append(f'    (net "{net_name}"')

            # 引脚连接
            for pin in net.get("pins", []):
                ref = pin.get("ref", "")
                pin_num = pin.get("pin", "1")
                lines.append(f'      (pin "{ref}" "{pin_num}")')

            lines.append("    )")
        lines.append("  )")

        lines.append(")")

        return "\n".join(lines)

    def export_dsn(
        self,
        pcb_file: str,
        output_dsn: str,
        components: List[Dict],
        nets: List[Dict],
        board_outline: List[Tuple[float, float]],
    ) -> bool:
        """
        导出 DSN 文件

        Args:
            pcb_file: 原始 PCB 文件路径
            output_dsn: 输出 DSN 文件路径
            components: 元件列表
            nets: 网络列表
            board_outline: 板框坐标

        Returns:
            bool: 是否成功
        """
        try:
            board_name = Path(pcb_file).stem
            dsn_content = self.generate_dsn_content(
                board_name, components, nets, board_outline
            )

            with open(output_dsn, "w", encoding="utf-8") as f:
                f.write(dsn_content)

            logger.info(f"DSN 文件已导出: {output_dsn}")
            return True

        except Exception as e:
            logger.error(f"导出 DSN 失败: {e}")
            return False

    def run_autorouter(
        self,
        dsn_file: str,
        output_ses: str,
        timeout: int = 300,
        ignore_nets: Optional[List[str]] = None,
    ) -> bool:
        """
        运行自动布线

        Args:
            dsn_file: 输入 DSN 文件
            output_ses: 输出 SES 文件
            timeout: 超时时间 (秒)
            ignore_nets: 忽略的网络列表 (如 GND, VCC 等手动处理)

        Returns:
            bool: 是否成功
        """
        if not self.check_installation():
            return False

        try:
            # 构建命令
            cmd = [
                "java",
                "-jar",
                self.freerouting_path,
                "-de",
                dsn_file,
                "-do",
                output_ses,
                "-mp",
                str(self.constraints.max_passes),
            ]

            # 添加忽略的网络
            if ignore_nets:
                cmd.extend(["-inc", ",".join(ignore_nets)])

            # 优化选项
            if self.constraints.optimize_vias:
                cmd.append("-opt_via")

            logger.info(f"启动自动布线: {cmd}")

            # 运行
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )

            if result.returncode == 0:
                logger.info(f"自动布线完成: {output_ses}")
                return True
            else:
                logger.error(f"自动布线失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"自动布线超时 (>{timeout}秒)")
            return False
        except Exception as e:
            logger.error(f"运行自动布线出错: {e}")
            return False

    def parse_ses_file(self, ses_file: str) -> List[Dict]:
        """
        解析 SES 文件，提取走线信息

        Args:
            ses_file: SES 文件路径

        Returns:
            List[Dict]: 走线列表
        """
        tracks = []

        try:
            with open(ses_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 简单解析 (实际 SES 格式更复杂)
            # 这里需要根据实际 SES 格式完善
            logger.info(f"解析 SES 文件: {ses_file}")

            # TODO: 完整 SES 解析实现

        except Exception as e:
            logger.error(f"解析 SES 文件失败: {e}")

        return tracks

    def autoroute_pcb(
        self,
        pcb_file: str,
        components: List[Dict],
        nets: List[Dict],
        board_outline: List[Tuple[float, float]],
        ignore_nets: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
    ) -> Dict:
        """
        完整的自动布线流程

        Args:
            pcb_file: PCB 文件路径
            components: 元件列表
            nets: 网络列表
            board_outline: 板框坐标
            ignore_nets: 忽略的网络
            output_dir: 输出目录

        Returns:
            Dict: 包含 success, tracks, message
        """
        result = {"success": False, "tracks": [], "message": ""}

        # 准备工作目录
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        else:
            os.makedirs(output_dir, exist_ok=True)

        board_name = Path(pcb_file).stem
        dsn_file = os.path.join(output_dir, f"{board_name}.dsn")
        ses_file = os.path.join(output_dir, f"{board_name}.ses")

        # 1. 导出 DSN
        if not self.export_dsn(pcb_file, dsn_file, components, nets, board_outline):
            result["message"] = "DSN 导出失败"
            return result

        # 2. 运行自动布线
        if not self.run_autorouter(dsn_file, ses_file, ignore_nets=ignore_nets):
            result["message"] = "自动布线失败"
            return result

        # 3. 解析 SES
        tracks = self.parse_ses_file(ses_file)

        result["success"] = True
        result["tracks"] = tracks
        result["message"] = f"布线完成，生成 {len(tracks)} 条走线"
        result["ses_file"] = ses_file
        result["dsn_file"] = dsn_file

        return result


class SimpleRouter:
    """
    简单自动布线器 (不依赖 FreeRouting)

    适用于简单电路的直接走线生成
    """

    def __init__(self):
        self.tracks: List[Dict] = []

    def route_direct_connection(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        net: str,
        layer: str = "F.Cu",
        width: float = 0.25,
    ) -> Dict:
        """
        创建直接连接走线

        Args:
            start: 起点坐标
            end: 终点坐标
            net: 网络名称
            layer: 层
            width: 线宽

        Returns:
            Dict: 走线定义
        """
        track = {"start": start, "end": end, "net": net, "layer": layer, "width": width}
        self.tracks.append(track)
        return track

    def route_l_shape(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        net: str,
        prefer_horizontal: bool = True,
    ) -> List[Dict]:
        """
        L 型走线

        Args:
            start: 起点
            end: 终点
            net: 网络
            prefer_horizontal: 优先水平走线

        Returns:
            List[Dict]: 走线段列表
        """
        tracks = []
        x1, y1 = start
        x2, y2 = end

        if prefer_horizontal:
            # 水平 -> 垂直
            mid = (x2, y1)
            tracks.append(self.route_direct_connection(start, mid, net))
            tracks.append(self.route_direct_connection(mid, end, net))
        else:
            # 垂直 -> 水平
            mid = (x1, y2)
            tracks.append(self.route_direct_connection(start, mid, net))
            tracks.append(self.route_direct_connection(mid, end, net))

        return tracks

    def get_all_tracks(self) -> List[Dict]:
        """获取所有走线"""
        return self.tracks


def quick_autoroute(
    components: List[Dict], connections: List[Dict], method: str = "simple"
) -> List[Dict]:
    """
    快速自动布线

    Args:
        components: 元件列表
        connections: 连接列表 [{from: (ref, pin), to: (ref, pin), net: name}]
        method: 布线方法 (simple/freerouting)

    Returns:
        List[Dict]: 走线列表
    """
    if method == "simple":
        router = SimpleRouter()

        for conn in connections:
            from_ref, from_pin = conn["from"]
            to_ref, to_pin = conn["to"]
            net = conn.get("net", "")

            # 查找元件位置
            from_comp = next((c for c in components if c["ref"] == from_ref), None)
            to_comp = next((c for c in components if c["ref"] == to_ref), None)

            if from_comp and to_comp:
                start = (from_comp["x"], from_comp["y"])
                end = (to_comp["x"], to_comp["y"])
                router.route_l_shape(start, end, net)

        return router.get_all_tracks()

    # TODO: FreeRouting 集成
    return []


if __name__ == "__main__":
    # 测试
    bridge = FreeRoutingBridge()

    if bridge.check_installation():
        print("✓ FreeRouting 已安装")
    else:
        print("✗ FreeRouting 未安装或未找到")
        print("  请安装 FreeRouting 插件或 Java 运行环境")
