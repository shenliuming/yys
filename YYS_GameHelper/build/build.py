#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阴阳师游戏助手 - PyInstaller打包脚本
支持打包周年庆任务和探索任务为独立可执行文件
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

# 打包目标配置
TARGETS = {
    "anniversary": {
        "name": "YYS_Anniversary",
        "entry": "tasks/anniversary/main.py",
        "description": "周年庆任务助手"
    },
    "exploration": {
        "name": "YYS_Exploration", 
        "entry": "tasks/exploration/exploration.py",
        "description": "探索任务助手"
    }
}

# PyInstaller通用参数
COMMON_PYINSTALLER_ARGS = [
    "--onefile",
    "--console",
    "--add-data", f"{CONFIG_FILE};.",
    "--add-data", f"{TEMPLATES_DIR};templates",
    "--exclude-module", "torch",
    "--exclude-module", "tensorflow",
    "--exclude-module", "matplotlib",
    "--exclude-module", "scipy",
    "--exclude-module", "pandas",
    "--exclude-module", "sklearn",
    "--exclude-module", "IPython",
    "--exclude-module", "jupyter",
    "--exclude-module", "notebook",
    "--exclude-module", "tkinter",
    "--hidden-import", "win32gui",
    "--hidden-import", "win32con",
    "--hidden-import", "win32api",
    "--hidden-import", "pywintypes",
    "--hidden-import", "cv2",
    "--hidden-import", "numpy",
    "--hidden-import", "PIL",
    "--hidden-import", "yaml",
    "--hidden-import", "adbutils"
]

class Builder:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        
    def log(self, message: str, level: str = "INFO"):
        """打印日志信息"""
        if self.verbose or level == "ERROR":
            print(f"[{level}] {message}")
    
    def check_dependencies(self) -> bool:
        """检查构建依赖"""
        self.log("检查构建依赖...")
        
        # 检查Python版本
        if sys.version_info < (3, 7):
            self.log("Python版本需要3.7或更高", "ERROR")
            return False
            
        # 检查PyInstaller
        try:
            result = subprocess.run(["pyinstaller", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.log("PyInstaller未安装，正在安装...", "INFO")
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        except FileNotFoundError:
            self.log("正在安装PyInstaller...", "INFO")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
            
        # 检查项目文件
        if not CONFIG_FILE.exists():
            self.log(f"配置文件不存在: {CONFIG_FILE}", "ERROR")
            return False
            
        if not TEMPLATES_DIR.exists():
            self.log(f"模板目录不存在: {TEMPLATES_DIR}", "ERROR")
            return False
            
        return True
    
    def clean_build(self):
        """清理构建目录"""
        self.log("清理构建目录...")
        
        # 清理dist目录
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        DIST_DIR.mkdir(exist_ok=True)
        
        # 清理PyInstaller缓存
        cache_dirs = [
            PROJECT_ROOT / "build",
            PROJECT_ROOT / "__pycache__"
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists() and cache_dir != BUILD_DIR:
                shutil.rmtree(cache_dir)
                
        # 清理spec文件
        for spec_file in PROJECT_ROOT.glob("*.spec"):
            spec_file.unlink()
    
    def build_target(self, target: str) -> bool:
        """构建指定目标"""
        if target not in TARGETS:
            self.log(f"未知目标: {target}", "ERROR")
            return False
            
        config = TARGETS[target]
        self.log(f"开始构建 {config['description']}...")
        
        # 构建PyInstaller命令
        entry_file = PROJECT_ROOT / config["entry"]
        if not entry_file.exists():
            self.log(f"入口文件不存在: {entry_file}", "ERROR")
            return False
            
        cmd = ["python", "-m", "PyInstaller"] + COMMON_PYINSTALLER_ARGS + [
            "--name", config['name'],
            "--distpath", str(DIST_DIR),
            "--workpath", str(BUILD_DIR / "work"),
            "--specpath", str(BUILD_DIR),
            str(entry_file)
        ]
        
        self.log(f"执行命令: {' '.join(cmd)}")
        
        # 执行构建
        try:
            result = subprocess.run(cmd, cwd=PROJECT_ROOT, 
                                  capture_output=not self.verbose)
            if result.returncode != 0:
                self.log(f"构建失败: {target}", "ERROR")
                if not self.verbose and result.stderr:
                    self.log(result.stderr.decode(), "ERROR")
                return False
        except Exception as e:
            self.log(f"构建异常: {e}", "ERROR")
            return False
            
        # 检查输出文件
        output_file = DIST_DIR / f"{config['name']}.exe"
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            self.log(f"构建成功: {output_file} ({size_mb:.1f}MB)")
            return True
        else:
            self.log(f"构建失败: 输出文件不存在", "ERROR")
            return False
    
    def create_launcher_scripts(self):
        """创建启动脚本"""
        self.log("创建启动脚本...")
        
        for target, config in TARGETS.items():
            exe_file = f"{config['name']}.exe"
            bat_content = f"""@echo off
chcp 65001 >nul
echo 启动 {config['description']}...
echo.

if not exist "{exe_file}" (
    echo 错误: 找不到 {exe_file}
    pause
    exit /b 1
)

start "" "{exe_file}"
"""
            
            bat_file = DIST_DIR / f"启动_{config['name']}.bat"
            with open(bat_file, 'w', encoding='gbk') as f:
                f.write(bat_content)
    
    def copy_additional_files(self):
        """复制额外文件"""
        self.log("复制配置和说明文件...")
        
        # 复制配置文件
        if CONFIG_FILE.exists():
            shutil.copy2(CONFIG_FILE, DIST_DIR)
            
        # 复制requirements.txt
        req_file = PROJECT_ROOT / "requirements.txt"
        if req_file.exists():
            shutil.copy2(req_file, DIST_DIR)
            
        # 创建使用说明
        readme_content = """# YYS游戏助手 - 使用说明

## 快速开始

1. 确保Android设备已连接并开启USB调试
2. 双击对应的exe文件或启动脚本
3. 程序会自动执行相应任务

## 文件说明

- `YYS_Anniversary.exe` - 周年庆任务助手
- `YYS_Exploration.exe` - 探索任务助手  
- `启动_*.bat` - 对应的启动脚本
- `config.yaml` - 配置文件
- `requirements.txt` - 依赖列表

## 注意事项

1. 首次运行可能需要较长时间初始化
2. 确保设备分辨率与模板匹配
3. 遵守游戏规则，合理使用工具

## 故障排除

- 如果程序无法启动，请检查ADB连接
- 如果识别失败，请检查模板文件
- 详细日志请查看程序输出

## 版本信息

- 打包工具: PyInstaller
- Python版本: {sys.version}
- 打包时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        readme_file = DIST_DIR / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def build(self, targets: List[str], clean: bool = False) -> bool:
        """执行构建流程"""
        self.log("开始构建流程...")
        
        # 检查依赖
        if not self.check_dependencies():
            return False
            
        # 清理构建
        if clean:
            self.clean_build()
        else:
            DIST_DIR.mkdir(exist_ok=True)
            
        # 构建目标
        success_count = 0
        for target in targets:
            if self.build_target(target):
                success_count += 1
            else:
                self.log(f"目标构建失败: {target}", "ERROR")
                
        if success_count == 0:
            self.log("所有目标构建失败", "ERROR")
            return False
            
        # 创建启动脚本和说明文件
        self.create_launcher_scripts()
        self.copy_additional_files()
        
        self.log(f"构建完成! 成功: {success_count}/{len(targets)}")
        self.log(f"输出目录: {DIST_DIR}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="YYS游戏助手打包工具")
    parser.add_argument("--target", choices=list(TARGETS.keys()) + ["all"],
                       default="all", help="打包目标")
    parser.add_argument("--clean", action="store_true", help="清理后打包")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--no-deps-check", action="store_true", help="跳过依赖检查")
    
    args = parser.parse_args()
    
    # 确定构建目标
    if args.target == "all":
        targets = list(TARGETS.keys())
    else:
        targets = [args.target]
    
    # 创建构建器
    builder = Builder(verbose=args.verbose)
    
    # 执行构建
    success = builder.build(targets, clean=args.clean)
    
    if success:
        print("\n构建成功! 🎉")
        print(f"输出目录: {DIST_DIR}")
        sys.exit(0)
    else:
        print("\n构建失败! ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()