@echo off
chcp 65001
echo 百度网盘解密工具 - 快速打包脚本
echo ========================================

REM 激活虚拟环境（如果使用的话）
if exist ".venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
)

REM 清理旧文件
echo 清理旧文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
if exist "百度网盘解密工具.exe" del /q "百度网盘解密工具.exe"

REM 构建EXE
echo 开始构建EXE文件...
pyinstaller --onefile --windowed --name="百度网盘解密工具" --add-data="decrypt.py;." --hidden-import=customtkinter --hidden-import=tkinter --hidden-import=PIL --clean run_gui.py

REM 检查结果
if exist "dist\百度网盘解密工具.exe" (
    echo.
    echo 构建成功！
    copy "dist\百度网盘解密工具.exe" "百度网盘解密工具.exe"
    echo 已复制到当前目录: 百度网盘解密工具.exe
    
    REM 显示文件信息
    for %%I in ("百度网盘解密工具.exe") do (
        echo 文件大小: %%~zI 字节
        set /a size_mb=%%~zI/1048576
    )
    echo 文件大小: %size_mb% MB（约）
) else (
    echo.
    echo 构建失败！请检查错误信息。
    pause
    exit /b 1
)

echo.
echo 打包完成！可以将 "百度网盘解密工具.exe" 复制到任何地方使用。
pause
