import os
import shutil
import sys
import subprocess
from pathlib import Path

# --- 配置 ---
APP_NAME = "GoDecrypt"
MAIN_SCRIPT = "run_gui.py"
# 可选: 在同一目录下创建一个名为 icon.ico 的图标文件
ICON_FILE = "icon.ico"
OUTPUT_DIR = "dist"

def find_library_path(library_name):
    """动态查找已安装库的路径"""
    try:
        # __import__ 是一个内置函数，可以像 import 语句一样导入模块
        lib = __import__(library_name)
        # Path(lib.__file__).parent 获取库的 __init__.py 文件所在的目录
        path = Path(lib.__file__).parent
        print(f"找到库 '{library_name}' 路径: {path}")
        return str(path)
    except (ImportError, AttributeError):
        print(f"错误: 未安装 '{library_name}' 库或无法找到其路径。")
        print(f"请运行: pip install {library_name}")
        sys.exit(1)

def build():
    """运行 PyInstaller 构建命令"""
    # 动态查找 customtkinter 的路径
    customtkinter_path = find_library_path("customtkinter")
    
    # 清理旧的构建文件
    print("正在清理旧的构建文件...")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    if os.path.exists("build"):
        shutil.rmtree("build")
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)

    # 构建 PyInstaller 命令
    # --noconsole: 隐藏控制台窗口 (对于GUI应用是必须的)
    # --onefile: 创建单个可执行文件
    # --name: 设置可执行文件的名称
    # --add-data: 包含额外的数据文件或文件夹。
    #             对于 customtkinter, 需要将其整个目录包含进来以支持主题和资源。
    #             os.pathsep 是路径分隔符 (Windows上是';', Linux/Mac上是':')
    # --clean: 在构建前清理 PyInstaller 的缓存
    # --log-level: 设置日志级别
    command = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        f"--name={APP_NAME}",
        f"--add-data={customtkinter_path}{os.pathsep}customtkinter",
        "--clean",
        "--log-level=INFO",
        MAIN_SCRIPT
    ]
    
    # 如果图标文件存在，则添加图标参数
    if os.path.exists(ICON_FILE):
        command.insert(4, f"--icon={ICON_FILE}")

    # 将命令列表连接成一个字符串以便打印
    command_str = " ".join(f'"{c}"' if " " in c else c for c in command)
    print(f"\n正在执行命令:\n{command_str}\n")
    
    # 执行命令
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        print("\n--- 构建成功 ---")
        exe_path = os.path.join(OUTPUT_DIR, f'{APP_NAME}.exe')
        print(f"可执行文件位于: {exe_path}")
        # 打印文件大小
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"文件大小: {size_mb:.2f} MB")

    except subprocess.CalledProcessError as e:
        print("\n--- 构建失败 ---")
        print("PyInstaller 在构建过程中发生错误。")
        print("\n--- STDOUT ---")
        print(e.stdout)
        print("\n--- STDERR ---")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("错误: 'pyinstaller' 命令未找到。")
        print("请确保 PyInstaller 已安装 (pip install pyinstaller) 并且在系统的 PATH 环境变量中。")
        sys.exit(1)


def main():
    """主函数，运行构建流程"""
    # 检查 PyInstaller 是否安装
    if shutil.which("pyinstaller") is None:
        print("错误: PyInstaller 未安装。请运行 'pip install pyinstaller'")
        sys.exit(1)
        
    build()

if __name__ == "__main__":
    main()
