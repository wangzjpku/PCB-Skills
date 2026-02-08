#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCB可视化评估工具
创建HTML页面展示PCB布局，使用Playwright截图评估
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple


class PCBVisualizer:
    """PCB可视化工具"""

    def __init__(self, pcb_file: str):
        self.pcb_file = Path(pcb_file)
        self.components = []
        self.tracks = []
        self.board_size = (0, 0)
        self.nets = []

    def parse_pcb(self):
        """解析PCB文件"""
        content = self.pcb_file.read_text(encoding="utf-8")

        # 解析板尺寸
        setup_match = re.search(
            r"\(setup.*?\(size\s+([\d\.]+)\s+([\d\.]+)\)", content, re.DOTALL
        )
        if setup_match:
            self.board_size = (float(setup_match.group(1)), float(setup_match.group(2)))

        # 解析元件
        footprints = re.findall(
            r'\(footprint\s+"([^"]+)".*?\(at\s+([\d\.]+)\s+([\d\.]+)(?:\s+([\d\.]+))?\).*?\(property\s+"Reference"\s+"([^"]+)"',
            content,
            re.DOTALL,
        )

        for fp in footprints:
            self.components.append(
                {
                    "footprint": fp[0],
                    "x": float(fp[1]),
                    "y": float(fp[2]),
                    "rotation": float(fp[3]) if fp[3] else 0,
                    "reference": fp[4],
                }
            )

        # 解析走线
        segments = re.findall(
            r"\(segment\s+\(start\s+([\d\.]+)\s+([\d\.]+)\)\s+\(end\s+([\d\.]+)\s+([\d\.]+)\)",
            content,
        )

        for seg in segments:
            self.tracks.append(
                {
                    "x1": float(seg[0]),
                    "y1": float(seg[1]),
                    "x2": float(seg[2]),
                    "y2": float(seg[3]),
                }
            )

        # 解析板框
        self.board_outline = []
        gr_lines = re.findall(
            r"\(gr_line\s+\(start\s+([\d\.]+)\s+([\d\.]+)\)\s+\(end\s+([\d\.]+)\s+([\d\.]+)\)",
            content,
        )

        for line in gr_lines:
            self.board_outline.append(
                {
                    "x1": float(line[0]),
                    "y1": float(line[1]),
                    "x2": float(line[2]),
                    "y2": float(line[3]),
                }
            )

    def generate_html(self, output_file: str = "pcb_preview.html"):
        """生成HTML可视化页面"""

        if not self.components:
            self.parse_pcb()

        width, height = self.board_size
        if width == 0:
            width, height = 100, 80

        # 计算缩放比例
        scale = 8
        canvas_width = width * scale
        canvas_height = height * scale

        # 生成元件SVG
        component_svg = ""
        for comp in self.components:
            x = comp["x"] * scale
            y = canvas_height - comp["y"] * scale  # 翻转Y轴
            ref = comp["reference"]
            fp = comp["footprint"]

            # 根据封装类型设置颜色和大小
            if "TerminalBlock" in fp:
                color = "#FF6B6B"
                size = 20
            elif "DIP" in fp or "Transformer" in fp:
                color = "#4ECDC4"
                size = 25
            elif "C_Elec" in fp:
                color = "#95E1D3"
                size = 15
            elif "D_" in fp:
                color = "#F38181"
                size = 18
            else:
                color = "#AA96DA"
                size = 12

            component_svg += f'''
            <g transform="translate({x}, {y})">
                <rect x="-{size / 2}" y="-{size / 2}" width="{size}" height="{size}" 
                      fill="{color}" stroke="#333" stroke-width="1" rx="2"/>
                <text x="0" y="{size / 2 + 12}" text-anchor="middle" 
                      font-size="8" fill="#333">{ref}</text>
            </g>'''

        # 生成走线SVG
        track_svg = ""
        for track in self.tracks:
            x1 = track["x1"] * scale
            y1 = canvas_height - track["y1"] * scale
            x2 = track["x2"] * scale
            y2 = canvas_height - track["y2"] * scale

            track_svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            track_svg += f'stroke="#2196F3" stroke-width="2"/>'

        # 生成板框SVG
        outline_svg = ""
        for line in self.board_outline:
            x1 = line["x1"] * scale
            y1 = canvas_height - line["y1"] * scale
            x2 = line["x2"] * scale
            y2 = canvas_height - line["y2"] * scale

            outline_svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            outline_svg += f'stroke="#FF0000" stroke-width="3" stroke-dasharray="5,5"/>'

        # 生成完整HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PCB Layout Preview - {self.pcb_file.stem}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f0f0f0;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 10px;
        }}
        .info {{
            margin: 20px 0;
            padding: 15px;
            background: #E3F2FD;
            border-radius: 4px;
        }}
        .info-item {{
            margin: 5px 0;
            font-size: 14px;
        }}
        .pcb-container {{
            border: 2px solid #333;
            display: inline-block;
            background: #1a1a2e;
            margin: 20px 0;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 4px;
        }}
        .legend-item {{
            display: inline-block;
            margin: 5px 15px;
            font-size: 12px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 5px;
            vertical-align: middle;
            border: 1px solid #333;
        }}
        .assessment {{
            margin-top: 20px;
            padding: 15px;
            background: #FFF3E0;
            border-radius: 4px;
            border-left: 4px solid #FF9800;
        }}
        .assessment h3 {{
            margin-top: 0;
            color: #E65100;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PCB Layout Preview</h1>
        <div class="info">
            <div class="info-item"><strong>File:</strong> {self.pcb_file.name}</div>
            <div class="info-item"><strong>Board Size:</strong> {width}mm x {height}mm</div>
            <div class="info-item"><strong>Components:</strong> {len(self.components)}</div>
            <div class="info-item"><strong>Tracks:</strong> {len(self.tracks)}</div>
            <div class="info-item"><strong>Board Outline:</strong> {"Yes" if self.board_outline else "No"}</div>
        </div>
        
        <div class="pcb-container">
            <svg width="{canvas_width}" height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">
                <!-- Background -->
                <rect width="100%" height="100%" fill="#1a1a2e"/>
                
                <!-- Board Outline -->
                {outline_svg}
                
                <!-- Tracks -->
                {track_svg}
                
                <!-- Components -->
                {component_svg}
            </svg>
        </div>
        
        <div class="legend">
            <h3>Component Legend:</h3>
            <div class="legend-item">
                <span class="legend-color" style="background: #FF6B6B;"></span>
                Terminal Block (Input/Output)
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #4ECDC4;"></span>
                IC / Transformer
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #95E1D3;"></span>
                Capacitor
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #F38181;"></span>
                Diode
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #AA96DA;"></span>
                Resistor/Other
            </div>
            <br>
            <div class="legend-item">
                <span style="color: #2196F3; font-weight: bold;">━━</span> Track (PCB Trace)
            </div>
            <div class="legend-item">
                <span style="color: #FF0000; font-weight: bold;">┅┅</span> Board Outline
            </div>
        </div>
        
        <div class="assessment">
            <h3>Layout Assessment</h3>
            <ul>
                <li>Board outline: {"Complete" if len(self.board_outline) >= 4 else "Incomplete"} ({len(self.board_outline)} lines)</li>
                <li>Component placement: {len(self.components)} components placed</li>
                <li>Track routing: {len(self.tracks)} track segments</li>
                <li>Power path: {"Defined" if len(self.tracks) > 5 else "Minimal"}</li>
            </ul>
            <p><strong>Recommendation:</strong> {"Good for initial layout. Add more tracks for complete routing." if len(self.tracks) >= 10 else "Need more track connections between components."}</p>
        </div>
    </div>
</body>
</html>'''

        # 保存HTML文件
        output_path = Path(output_file)
        output_path.write_text(html, encoding="utf-8")
        print(f"HTML preview saved to: {output_path.absolute()}")
        return output_path


def compare_designs(old_pcb: str, new_pcb: str):
    """对比旧版和新版设计"""

    print("=" * 70)
    print("PCB Design Comparison")
    print("=" * 70)

    # 解析旧版
    old_vis = PCBVisualizer(old_pcb)
    old_vis.parse_pcb()

    # 解析新版
    new_vis = PCBVisualizer(new_pcb)
    new_vis.parse_pcb()

    print(f"\nOld Design: {Path(old_pcb).name}")
    print(f"  Components: {len(old_vis.components)}")
    print(f"  Tracks: {len(old_vis.tracks)}")
    print(f"  Board outline: {len(old_vis.board_outline)} lines")

    print(f"\nNew Design: {Path(new_pcb).name}")
    print(f"  Components: {len(new_vis.components)}")
    print(f"  Tracks: {len(new_vis.tracks)}")
    print(f"  Board outline: {len(new_vis.board_outline)} lines")

    print("\nImprovements:")
    print(f"  Components: +{len(new_vis.components) - len(old_vis.components)}")
    print(f"  Tracks: +{len(new_vis.tracks) - len(old_vis.tracks)}")
    print(
        f"  Board outline: +{len(new_vis.board_outline) - len(old_vis.board_outline)}"
    )

    # 生成对比HTML
    old_vis.generate_html("old_design_preview.html")
    new_vis.generate_html("new_design_preview.html")

    print("\n" + "=" * 70)


def main():
    """主函数"""
    # 对比旧版和新版
    old_pcb = "output-result/design_001_5V0.5A_USB充电器_VIPer22A/v1.0.1/design_001_5V0.5A_USB充电器_VIPer22A_v1.0.1.kicad_pcb"
    new_pcb = "output-result/improved_001_5V0.5A_USB充电器_VIPer22A/v1.0.0/improved_001_5V0.5A_USB充电器_VIPer22A_v1.0.0.kicad_pcb"

    compare_designs(old_pcb, new_pcb)

    print("\nGenerated preview files:")
    print("  - old_design_preview.html")
    print("  - new_design_preview.html")
    print("\nOpen these files in a browser to visualize the PCB layout.")


if __name__ == "__main__":
    main()
