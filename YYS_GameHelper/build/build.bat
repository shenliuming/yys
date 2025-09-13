@echo off
chcp 65001 >nul
echo ========================================
echo     YYS游戏助手 - PyInstaller打包工具
echo ========================================
echo.

cd /d "%~dp0.."

echo 当前目录: %CD%
echo.

echo 可用打包目标:
echo   1. anniversary  - 周年庆任务助手
echo   2. exploration  - 探索任务助手
echo   3. all         - 打包所有目标
echo.

set /p choice="请选择打包目标 (1-3, 默认为3): "

if "%choice%"=="" set choice=3
if "%choice%"=="1" set target=anniversary
if "%choice%"=="2" set target=exploration
if "%choice%"=="3" set target=all

echo.
echo 开始打包目标: %target%
echo.

python build\build.py --target %target% --clean --verbose

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo          打包完成! 🎉
    echo ========================================
    echo.
    echo 输出目录: dist\
    echo.
    echo 按任意键打开输出目录...
    pause >nul
    start "" "dist"
) else (
    echo.
    echo ========================================
    echo          打包失败! ❌
    echo ========================================
    echo.
    echo 请检查错误信息并重试
    pause
)