# YYS游戏助手 (阴阳师游戏助手)

## 项目结构

```
YYS_GameHelper/
├── README.md           # 项目说明文档
├── main.py            # 主程序入口
├── config.yaml        # 配置文件
├── requirements.txt   # Python依赖包
├── core/              # 核心功能模块
├── tasks/             # 任务模块
├── templates/         # 图像模板
├── log/               # 运行日志
└── release/           # 打包发布目录
    ├── YYS_GameHelper_Final.exe  # 可执行文件 (95MB)
    ├── start.bat                 # 启动脚本
    ├── config.yaml               # 配置文件
    ├── README.md                 # 使用说明
    └── 使用说明.md               # 详细文档
```

## 开发环境

1. **运行源码**：
   ```bash
   pip install -r requirements.txt
   python main.py --help
   ```

2. **重新打包**：
   ```bash
   python -m PyInstaller --onefile --noconsole --add-data "config.yaml;." --add-data "templates;templates" --exclude-module torch --exclude-module tensorflow --hidden-import win32gui --hidden-import win32con --hidden-import win32api --hidden-import pywintypes --name YYS_GameHelper_Final main.py
   ```

## 使用发布版本

进入 `release/` 目录，双击 `YYS_GameHelper_Final.exe` 或运行 `start.bat`

## 功能特性

- 自动检测Android模拟器
- 支持多种游戏任务自动化
- 图像识别和OCR文字识别
- 完整的日志记录系统
- 可配置的参数设置

一个功能强大的阴阳师游戏自动化助手，支持周年庆任务和探索任务的自动执行。

## 🌟 功能特性

### 核心功能
- **设备管理**: 支持ADB连接和控制Android设备
- **图像识别**: 基于OpenCV的高精度模板匹配
- **截图功能**: 实时获取游戏画面
- **日志系统**: 彩色日志输出，便于调试
- **配置管理**: 灵活的YAML配置文件支持

### 任务模块
- **周年庆任务**: 自动完成周年庆相关活动
- **探索任务**: 自动进行探索副本挂机

## 📁 项目结构

```
YYS_GameHelper/
├── core/                    # 核心功能模块
│   ├── __init__.py
│   ├── device.py           # 设备管理
│   ├── screenshot.py       # 截图功能
│   ├── image_matcher.py    # 图像匹配
│   ├── logger.py           # 日志系统
│   ├── config.py           # 配置管理
│   └── utils.py            # 工具函数
├── tasks/                   # 任务模块
│   ├── __init__.py
│   ├── anniversary/        # 周年庆任务
│   │   ├── __init__.py
│   │   ├── anniversary_task.py
│   │   └── main.py
│   └── exploration/        # 探索任务
│       ├── __init__.py
│       ├── exploration_task.py
│       ├── exploration_config.py
│       └── start_exploration.py
├── templates/              # 图像模板
├── build/                  # 打包相关
│   ├── nuitka_config.py   # Nuitka配置
│   ├── build.py           # 打包脚本
│   └── build.bat          # Windows打包脚本
├── requirements.txt        # 依赖列表
└── README.md              # 项目说明
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Windows 10/11
- Android设备 (开启USB调试)
- ADB工具

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行任务

#### 周年庆任务
```bash
cd tasks/anniversary
python main.py
```

#### 探索任务
```bash
cd tasks/exploration
python start_exploration.py
```

## 📦 打包为可执行文件

本项目支持使用Nuitka将Python脚本打包为独立的可执行文件，无需安装Python环境即可运行。

### 方法一: 使用批处理脚本 (推荐)

1. 双击运行 `build/build.bat`
2. 按提示选择打包目标
3. 等待打包完成
4. 在 `dist/` 目录找到可执行文件

### 方法二: 使用Python脚本

```bash
cd build

# 打包所有目标
python build.py --target all

# 打包特定目标
python build.py --target anniversary
python build.py --target exploration

# 清理后打包
python build.py --target all --clean

# 显示详细输出
python build.py --target all --verbose
```

### 打包选项说明

- `--target`: 指定打包目标
  - `anniversary`: 仅打包周年庆任务
  - `exploration`: 仅打包探索任务
  - `all`: 打包所有任务 (默认)
- `--clean`: 打包前清理输出目录
- `--verbose`: 显示详细构建输出
- `--no-deps-check`: 跳过依赖检查

### 打包输出

打包完成后，在 `dist/` 目录下会生成:

- `YYS_Anniversary.exe` - 周年庆任务助手
- `YYS_Exploration.exe` - 探索任务助手
- `启动_YYS_Anniversary.bat` - 周年庆任务启动脚本
- `启动_YYS_Exploration.bat` - 探索任务启动脚本
- `requirements.txt` - 依赖列表
- `README.md` - 使用说明

## ⚙️ 配置说明

### 设备配置

确保Android设备:
1. 开启开发者选项
2. 启用USB调试
3. 连接到电脑并授权ADB调试

### 模板配置

图像模板存放在 `templates/` 目录下，支持PNG格式。可根据不同分辨率和游戏版本调整模板图片。

## 🔧 开发说明

### 添加新任务

1. 在 `tasks/` 下创建新的任务目录
2. 实现任务逻辑，继承核心功能模块
3. 在 `build/nuitka_config.py` 中添加新的入口点
4. 更新打包配置

### 核心模块扩展

核心功能模块位于 `core/` 目录，提供:
- 设备管理和控制
- 图像识别和匹配
- 日志和配置系统
- 通用工具函数

## 📝 注意事项

1. **设备兼容性**: 不同设备分辨率可能需要调整模板图片
2. **游戏版本**: 游戏更新后可能需要更新模板
3. **性能优化**: 长时间运行建议适当休息，避免设备过热
4. **安全使用**: 请遵守游戏规则，合理使用自动化工具

## 🐛 故障排除

### 常见问题

1. **ADB连接失败**
   - 检查USB调试是否开启
   - 重新授权ADB调试
   - 尝试重启ADB服务: `adb kill-server && adb start-server`

2. **图像识别失败**
   - 检查模板图片是否匹配当前游戏界面
   - 调整匹配阈值
   - 确认设备分辨率设置

3. **打包失败**
   - 检查Python和Nuitka版本
   - 确认所有依赖已安装
   - 查看详细错误输出

## 📄 许可证

本项目仅供学习和研究使用，请勿用于商业用途。使用本工具产生的任何后果由使用者自行承担。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

---

**免责声明**: 本工具仅用于学习和研究目的，请遵守相关游戏的使用条款和服务协议。