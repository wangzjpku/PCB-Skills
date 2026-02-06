"""
输出目录管理模块

管理所有KiCad文件的输出，统一放到 output-result 目录中
按版本号组织子目录
"""

import os
import shutil
from datetime import datetime
from typing import Optional
import re


class OutputManager:
    """
    输出目录管理器

    统一管理人员所有输出文件到 output-result 目录
    自动生成版本号子目录
    """

    BASE_OUTPUT_DIR = "output-result"

    def __init__(self, project_name: str):
        """
        初始化输出管理器

        Args:
            project_name: 项目名称，用于创建子目录
        """
        self.project_name = project_name
        self.version = self._get_next_version()
        self.output_dir = self._create_output_dir()

    def _get_next_version(self) -> str:
        """获取下一个版本号"""
        base_path = os.path.join(self.BASE_OUTPUT_DIR, self.project_name)

        if not os.path.exists(base_path):
            return "v1.0.0"

        # 查找现有版本
        versions = []
        for item in os.listdir(base_path):
            if os.path.isdir(os.path.join(base_path, item)):
                # 尝试解析版本号
                match = re.match(r"v(\d+)\.(\d+)\.(\d+)", item)
                if match:
                    versions.append(
                        (int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    )

        if not versions:
            return "v1.0.0"

        # 获取最新版本并递增
        latest = max(versions)
        return f"v{latest[0]}.{latest[1]}.{latest[2] + 1}"

    def _create_output_dir(self) -> str:
        """创建输出目录"""
        output_path = os.path.join(
            self.BASE_OUTPUT_DIR, self.project_name, self.version
        )
        os.makedirs(output_path, exist_ok=True)
        return output_path

    def get_path(self, filename: str) -> str:
        """获取文件的完整输出路径"""
        return os.path.join(self.output_dir, filename)

    def save_sch(self, filename: str = None) -> str:
        """获取原理图文件路径"""
        if filename is None:
            filename = f"{self.project_name}_{self.version}.kicad_sch"
        return self.get_path(filename)

    def save_pcb(self, filename: str = None) -> str:
        """获取PCB文件路径"""
        if filename is None:
            filename = f"{self.project_name}_{self.version}.kicad_pcb"
        return self.get_path(filename)

    def save_doc(self, filename: str) -> str:
        """获取文档文件路径"""
        return self.get_path(filename)

    def create_readme(self, content: str = None):
        """创建README文件"""
        readme_path = self.get_path("README.md")

        if content is None:
            content = f"""# {self.project_name} - {self.version}

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 文件列表

- `{self.project_name}_{self.version}.kicad_sch` - 原理图
- `{self.project_name}_{self.version}.kicad_pcb` - PCB文件

## 说明

本设计由KiCad Auto-Design Skill自动生成。
"""

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        return readme_path

    def list_files(self) -> list:
        """列出输出目录中的所有文件"""
        return os.listdir(self.output_dir)

    def get_info(self) -> dict:
        """获取输出信息"""
        return {
            "project": self.project_name,
            "version": self.version,
            "output_dir": self.output_dir,
            "files": self.list_files(),
        }


def get_output_manager(project_name: str) -> OutputManager:
    """便捷函数：获取输出管理器实例"""
    return OutputManager(project_name)
