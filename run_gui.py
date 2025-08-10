#!/usr/bin/env python3
"""
百度网盘加密文件解密工具 - GUI版本

现代化的图形界面解密工具，支持单文件解密和批量目录解密

作者: xianrenzhou
GitHub: https://github.com/xianrenzhou
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from pathlib import Path
import traceback

# 尝试导入customtkinter以获得现代化界面
try:
    import customtkinter as ctk
    HAS_CUSTOMTKINTER = True
    # 设置外观模式和颜色主题
    ctk.set_appearance_mode("light")  # 亮色模式
    ctk.set_default_color_theme("blue")  # 蓝色主题
except ImportError:
    HAS_CUSTOMTKINTER = False
    print("提示: 安装 customtkinter 可获得更好的界面效果: pip install customtkinter")

# 导入我们的解密模块
from decrypt import decrypt_file, decrypt_directory, is_encrypted_file


class ModernDecryptGUI:
    def __init__(self):
        if HAS_CUSTOMTKINTER:
            self.root = ctk.CTk()
            self.setup_modern_ui()
        else:
            self.root = tk.Tk()
            self.setup_classic_ui()
        
        self.setup_common()
        
    def show_error(self, title, message):
        """显示一个错误消息框"""
        # 确保在主线程中显示消息框
        self.root.after(0, lambda: messagebox.showerror(title, message))
        
    def setup_modern_ui(self):
        """设置现代化UI（使用customtkinter）"""
        self.root.title("百度网盘解密工具")
        self.root.geometry("580x480")
        self.root.resizable(True, True)
        
        # 主容器
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        # 标题
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="百度网盘加密文件解密工具",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(12, 6))
        
        # GitHub信息
        github_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        github_frame.pack(pady=(0, 12))
        
        github_label = ctk.CTkLabel(
            github_frame,
            text="作者: xianrenzhou",
            font=ctk.CTkFont(size=10)
        )
        github_label.pack(side="left", padx=(0, 6))
        
        github_button = ctk.CTkButton(
            github_frame,
            text="访问GitHub",
            command=self.open_github,
            width=80,
            height=24,
            font=ctk.CTkFont(size=10)
        )
        github_button.pack(side="left")
        
        # 选项卡
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 12))
        
        # 单文件解密选项卡
        self.file_tab = self.notebook.add("单文件解密")
        self.setup_file_tab_modern(self.file_tab)
        
        # 批量解密选项卡
        self.batch_tab = self.notebook.add("文件夹解密")
        self.setup_batch_tab_modern(self.batch_tab)
        
        # 底部框架
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(0, 8))
        
        # 状态栏
        self.status_label = ctk.CTkLabel(
            bottom_frame,
            text="就绪",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left")
        
        # 关闭按钮
        close_button = ctk.CTkButton(
            bottom_frame,
            text="关闭程序",
            command=self.on_closing,
            width=70,
            height=26,
            font=ctk.CTkFont(size=10),
            fg_color="gray70",
            hover_color="gray60"
        )
        close_button.pack(side="right")
        
    def setup_classic_ui(self):
        """设置经典UI（使用tkinter）"""
        self.root.title("百度网盘解密工具")
        self.root.geometry("580x480")
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        
        # 主容器
        self.main_frame = tk.Frame(self.root, bg='white')
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        # 标题
        title_label = tk.Label(
            self.main_frame,
            text="百度网盘加密文件解密工具",
            font=("Microsoft YaHei", 16, "bold"),
            bg='white',
            fg='#333333'
        )
        title_label.pack(pady=(15, 8))
        
        # GitHub信息
        github_frame = tk.Frame(self.main_frame, bg='white')
        github_frame.pack(pady=(0, 15))
        
        github_label = tk.Label(
            github_frame,
            text="作者: xianrenzhou",
            font=("Microsoft YaHei", 9),
            bg='white',
            fg='#666666'
        )
        github_label.pack(side="left", padx=(0, 8))
        
        github_button = tk.Button(
            github_frame,
            text="访问GitHub",
            command=self.open_github,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 9),
            relief='flat',
            padx=12,
            pady=3
        )
        github_button.pack(side="left")
        
        # 选项卡
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 15))
        
        # 单文件解密选项卡
        self.file_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.file_tab, text="单文件解密")
        self.setup_file_tab_classic(self.file_tab)
        
        # 批量解密选项卡
        self.batch_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.batch_tab, text="批量解密")
        self.setup_batch_tab_classic(self.batch_tab)
        
        # 底部框架
        bottom_frame = tk.Frame(self.main_frame, bg='white')
        bottom_frame.pack(fill="x", pady=(0, 10))
        
        # 状态栏
        self.status_label = tk.Label(
            bottom_frame,
            text="就绪",
            font=("Microsoft YaHei", 9),
            bg='white',
            fg='#666666'
        )
        self.status_label.pack(side="left")
        
        # 关闭按钮
        close_button = tk.Button(
            bottom_frame,
            text="关闭程序",
            command=self.on_closing,
            bg='#666666',
            fg='white',
            font=("Microsoft YaHei", 9),
            relief='flat',
            padx=15,
            pady=5
        )
        close_button.pack(side="right")
    
    def setup_file_tab_modern(self, parent):
        """设置单文件解密选项卡（现代版）"""
        # 输入文件选择
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", padx=12, pady=(12, 6))
        
        ctk.CTkLabel(input_frame, text="选择加密文件:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        input_file_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_file_frame.pack(fill="x", pady=(3, 0))
        
        self.input_file_var = tk.StringVar()
        self.input_file_entry = ctk.CTkEntry(
            input_file_frame,
            textvariable=self.input_file_var,
            placeholder_text="请选择要解密的文件...",
            height=28
        )
        self.input_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            input_file_frame,
            text="浏览",
            command=self.browse_input_file,
            width=60,
            height=28
        ).pack(side="right")
        
        # 输出文件选择
        output_frame = ctk.CTkFrame(parent, fg_color="transparent")
        output_frame.pack(fill="x", padx=12, pady=6)
        
        ctk.CTkLabel(output_frame, text="输出文件路径:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        output_file_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_file_frame.pack(fill="x", pady=(3, 0))
        
        self.output_file_var = tk.StringVar()
        self.output_file_entry = ctk.CTkEntry(
            output_file_frame,
            textvariable=self.output_file_var,
            placeholder_text="留空则自动生成输出路径...",
            height=28
        )
        self.output_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            output_file_frame,
            text="浏览",
            command=self.browse_output_file,
            width=60,
            height=28
        ).pack(side="right")
        
        # 密码输入
        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.pack(fill="x", padx=12, pady=6)
        
        ctk.CTkLabel(password_frame, text="解密密码:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        password_input_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        password_input_frame.pack(fill="x", pady=(3, 0))
        
        self.password_var = tk.StringVar(value="123456")
        self.password_show_var = tk.BooleanVar()
        self.password_entry = ctk.CTkEntry(
            password_input_frame,
            textvariable=self.password_var,
            placeholder_text="输入解密密码",
            height=28,
            show="*"
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        self.password_toggle_button = ctk.CTkButton(
            password_input_frame,
            text="显示",
            command=self.toggle_password_visibility,
            width=50,
            height=28,
            font=ctk.CTkFont(size=12)
        )
        self.password_toggle_button.pack(side="right")
        
        # 选项
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="x", padx=12, pady=6)
        
        self.keep_original_var = tk.BooleanVar()
        self.keep_original_var.set(True)
        ctk.CTkCheckBox(
            options_frame,
            text="保留原始文件",
            variable=self.keep_original_var
        ).pack(anchor="w")
        
        # 解密按钮
        decrypt_button = ctk.CTkButton(
            parent,
            text="开始解密",
            command=self.decrypt_single_file,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        decrypt_button.pack(pady=12)
    
    def setup_file_tab_classic(self, parent):
        """设置单文件解密选项卡（经典版）"""
        # 输入文件选择
        input_frame = tk.Frame(parent, bg='white')
        input_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(input_frame, text="选择加密文件:", font=("Microsoft YaHei", 12, "bold"), bg='white').pack(anchor="w")
        
        input_file_frame = tk.Frame(input_frame, bg='white')
        input_file_frame.pack(fill="x", pady=(5, 0))
        
        self.input_file_var = tk.StringVar()
        self.input_file_entry = tk.Entry(input_file_frame, textvariable=self.input_file_var, font=("Microsoft YaHei", 10))
        self.input_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Button(
            input_file_frame,
            text="浏览",
            command=self.browse_input_file,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 10),
            relief='flat'
        ).pack(side="right")
        
        # 输出文件选择
        output_frame = tk.Frame(parent, bg='white')
        output_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(output_frame, text="输出文件路径:", font=("Microsoft YaHei", 12, "bold"), bg='white').pack(anchor="w")
        
        output_file_frame = tk.Frame(output_frame, bg='white')
        output_file_frame.pack(fill="x", pady=(5, 0))
        
        self.output_file_var = tk.StringVar()
        self.output_file_entry = tk.Entry(output_file_frame, textvariable=self.output_file_var, font=("Microsoft YaHei", 10))
        self.output_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Button(
            output_file_frame,
            text="浏览",
            command=self.browse_output_file,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 10),
            relief='flat'
        ).pack(side="right")
        
        # 密码输入
        password_frame = tk.Frame(parent, bg='white')
        password_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(password_frame, text="解密密码:", font=("Microsoft YaHei", 12, "bold"), bg='white').pack(anchor="w")
        
        password_input_frame = tk.Frame(password_frame, bg='white')
        password_input_frame.pack(fill="x", pady=(5, 0))
        
        self.password_var = tk.StringVar(value="123456")
        self.password_entry = tk.Entry(password_input_frame, textvariable=self.password_var, font=("Microsoft YaHei", 10), show="*")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.classic_password_toggle_button = tk.Button(
            password_input_frame,
            text="显示",
            command=self.toggle_password_visibility,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 10),
            relief='flat',
            padx=10,
            pady=3
        )
        self.classic_password_toggle_button.pack(side="right")
        
        # 选项
        options_frame = tk.Frame(parent, bg='white')
        options_frame.pack(fill="x", padx=20, pady=10)
        
        self.keep_original_var = tk.BooleanVar()
        tk.Checkbutton(
            options_frame,
            text="保留原始文件",
            variable=self.keep_original_var,
            bg='white',
            font=("Microsoft YaHei", 10)
        ).pack(anchor="w")
        
        # 解密按钮
        decrypt_button = tk.Button(
            parent,
            text="开始解密",
            command=self.decrypt_single_file,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 14, "bold"),
            relief='flat',
            pady=10
        )
        decrypt_button.pack(pady=20)
    
    def setup_batch_tab_modern(self, parent):
        """设置批量解密选项卡（现代版）"""
        # 输入目录选择
        input_dir_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_dir_frame.pack(fill="x", padx=12, pady=(12, 6))
        
        ctk.CTkLabel(input_dir_frame, text="选择输入目录:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        input_dir_file_frame = ctk.CTkFrame(input_dir_frame, fg_color="transparent")
        input_dir_file_frame.pack(fill="x", pady=(3, 0))
        
        self.input_dir_var = tk.StringVar()
        self.input_dir_entry = ctk.CTkEntry(
            input_dir_file_frame,
            textvariable=self.input_dir_var,
            placeholder_text="请选择包含加密文件的目录...",
            height=28
        )
        self.input_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            input_dir_file_frame,
            text="浏览",
            command=self.browse_input_dir,
            width=60,
            height=28
        ).pack(side="right")
        
        # 输出目录选择
        output_dir_frame = ctk.CTkFrame(parent, fg_color="transparent")
        output_dir_frame.pack(fill="x", padx=12, pady=6)
        
        ctk.CTkLabel(output_dir_frame, text="输出目录:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        output_dir_file_frame = ctk.CTkFrame(output_dir_frame, fg_color="transparent")
        output_dir_file_frame.pack(fill="x", pady=(3, 0))
        
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ctk.CTkEntry(
            output_dir_file_frame,
            textvariable=self.output_dir_var,
            placeholder_text="选择输出目录（留空则原地解密）...",
            height=28
        )
        self.output_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            output_dir_file_frame,
            text="浏览",
            command=self.browse_output_dir,
            width=60,
            height=28
        ).pack(side="right")
        
        # 密码输入
        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.pack(fill="x", padx=12, pady=6)
        
        ctk.CTkLabel(password_frame, text="解密密码:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        batch_password_input_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        batch_password_input_frame.pack(fill="x", pady=(3, 0))
        
        self.batch_password_var = tk.StringVar(value="123456")
        self.batch_password_show_var = tk.BooleanVar()
        self.batch_password_entry = ctk.CTkEntry(
            batch_password_input_frame,
            textvariable=self.batch_password_var,
            placeholder_text="输入解密密码",
            height=28,
            show="*"
        )
        self.batch_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        self.batch_password_toggle_button = ctk.CTkButton(
            batch_password_input_frame,
            text="显示",
            command=self.toggle_batch_password_visibility,
            width=50,
            height=28,
            font=ctk.CTkFont(size=10)
        )
              
        self.batch_password_toggle_button.pack(side="right")
        
        # 选项
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="x", padx=12, pady=6)
        
        self.recursive_var = tk.BooleanVar()
        self.recursive_var.set(True)  # 默认勾选递归处理
        ctk.CTkCheckBox(
            options_frame,
            text="递归处理子目录",
            variable=self.recursive_var
        ).pack(anchor="w", pady=(0, 3))
        
        self.batch_keep_original_var = tk.BooleanVar()
        self.batch_keep_original_var.set(True)  # 默认勾选保留原始文件
        ctk.CTkCheckBox(
            options_frame,
            text="保留原始文件",
            variable=self.batch_keep_original_var
        ).pack(anchor="w")
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(parent)
        self.progress_bar.pack(fill="x", padx=12, pady=6)
        self.progress_bar.set(0)
        
        # 解密按钮
        decrypt_button = ctk.CTkButton(
            parent,
            text="开始批量解密",
            command=self.decrypt_batch,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        decrypt_button.pack(pady=12)
    
    def setup_batch_tab_classic(self, parent):
        """设置批量解密选项卡（经典版）"""
        # 输入目录选择
        input_dir_frame = tk.Frame(parent, bg='white')
        input_dir_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(input_dir_frame, text="选择输入目录:", font=("Microsoft YaHei", 12, "bold"), bg='white').pack(anchor="w")
        
        input_dir_file_frame = tk.Frame(input_dir_frame, bg='white')
        input_dir_file_frame.pack(fill="x", pady=(5, 0))
        
        self.input_dir_var = tk.StringVar()
        self.input_dir_entry = tk.Entry(input_dir_file_frame, textvariable=self.input_dir_var, font=("Microsoft YaHei", 10))
        self.input_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Button(
            input_dir_file_frame,
            text="浏览",
            command=self.browse_input_dir,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 10),
            relief='flat'
        ).pack(side="right")
        
        # 输出目录选择
        output_dir_frame = tk.Frame(parent, bg='white')
        output_dir_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(output_dir_frame, text="输出目录:", font=("Microsoft YaHei", 12, "bold"), bg='white').pack(anchor="w")
        
        output_dir_file_frame = tk.Frame(output_dir_frame, bg='white')
        output_dir_file_frame.pack(fill="x", pady=(5, 0))
        
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = tk.Entry(output_dir_file_frame, textvariable=self.output_dir_var, font=("Microsoft YaHei", 10))
        self.output_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Button(
            output_dir_file_frame,
            text="浏览",
            command=self.browse_output_dir,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 10),
            relief='flat'
        ).pack(side="right")
        
        # 密码输入
        password_frame = tk.Frame(parent, bg='white')
        password_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(password_frame, text="解密密码:", font=("Microsoft YaHei", 12, "bold"), bg='white').pack(anchor="w")
        
        batch_password_input_frame = tk.Frame(password_frame, bg='white')
        batch_password_input_frame.pack(fill="x", pady=(5, 0))
        
        self.batch_password_var = tk.StringVar(value="123456")
        self.batch_password_entry = tk.Entry(batch_password_input_frame, textvariable=self.batch_password_var, font=("Microsoft YaHei", 10), show="*")
        self.batch_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.classic_batch_password_toggle_button = tk.Button(
            batch_password_input_frame,
            text="显示",
            command=self.toggle_batch_password_visibility,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 9),
            relief='flat',
            padx=10,
            pady=3
        )
        self.classic_batch_password_toggle_button.pack(side="right")
        
        # 选项
        options_frame = tk.Frame(parent, bg='white')
        options_frame.pack(fill="x", padx=20, pady=10)
        
        self.recursive_var = tk.BooleanVar()
        self.recursive_var.set(True)  # 默认勾选递归处理
        tk.Checkbutton(
            options_frame,
            text="递归处理子目录",
            variable=self.recursive_var,
            bg='white',
            font=("Microsoft YaHei", 10)
        ).pack(anchor="w")
        
        self.batch_keep_original_var = tk.BooleanVar()
        self.batch_keep_original_var.set(True)  # 默认勾选保留原始文件
        tk.Checkbutton(
            options_frame,
            text="保留原始文件",
            variable=self.batch_keep_original_var,
            bg='white',
            font=("Microsoft YaHei", 10)
        ).pack(anchor="w")
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        
        # 解密按钮
        decrypt_button = tk.Button(
            parent,
            text="开始批量解密",
            command=self.decrypt_batch,
            bg='#0078d4',
            fg='white',
            font=("Microsoft YaHei", 14, "bold"),
            relief='flat',
            pady=10
        )
        decrypt_button.pack(pady=20)
    
    def setup_common(self):
        """设置通用组件"""
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 居中显示窗口
        self.center_window()
    
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def open_github(self):
        """打开GitHub页面"""
        webbrowser.open("https://github.com/xianrenzhou")
    
    def browse_input_file(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="选择要解密的文件",
            filetypes=[("所有文件", "*.*"), ("加密文件", "*.enc")]
        )
        if filename:
            self.input_file_var.set(filename)
    
    def browse_output_file(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="选择输出文件位置",
            filetypes=[("所有文件", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
    
    def browse_input_dir(self):
        """浏览输入目录"""
        dirname = filedialog.askdirectory(title="选择包含加密文件的目录")
        if dirname:
            self.input_dir_var.set(dirname)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir_var.set(dirname)
    
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.configure(text=message)
        self.root.update()
    
    def toggle_password_visibility(self):
        """切换单文件解密密码显示/隐藏"""
        if HAS_CUSTOMTKINTER:
            if self.password_entry.cget("show") == "*":
                self.password_entry.configure(show="")
                self.password_toggle_button.configure(text="隐藏")
            else:
                self.password_entry.configure(show="*")
                self.password_toggle_button.configure(text="显示")
        else:
            if self.password_entry.cget("show") == "*":
                self.password_entry.configure(show="")
                self.classic_password_toggle_button.configure(text="隐藏")
            else:
                self.password_entry.configure(show="*")
                self.classic_password_toggle_button.configure(text="显示")
    
    def toggle_batch_password_visibility(self):
        """切换批量解密密码显示/隐藏"""
        if HAS_CUSTOMTKINTER:
            if self.batch_password_entry.cget("show") == "*":
                self.batch_password_entry.configure(show="")
                self.batch_password_toggle_button.configure(text="隐藏")
            else:
                self.batch_password_entry.configure(show="*")
                self.batch_password_toggle_button.configure(text="显示")
        else:
            if self.batch_password_entry.cget("show") == "*":
                self.batch_password_entry.configure(show="")
                self.classic_batch_password_toggle_button.configure(text="隐藏")
            else:
                self.batch_password_entry.configure(show="*")
                self.classic_batch_password_toggle_button.configure(text="显示")
    
    def decrypt_single_file(self):
        """解密单个文件"""
        try:
            input_file = self.input_file_var.get().strip()
            output_file = self.output_file_var.get().strip()
            password = self.password_var.get().strip()
            keep_original = self.keep_original_var.get()
            
            if not input_file:
                self.show_error("错误", "请选择要解密的文件")
                return
            
            if not password:
                self.show_error("错误", "请输入解密密码")
                return
            
            if not os.path.exists(input_file):
                self.show_error("错误", "输入文件不存在")
                return
            
            self.update_status("正在解密文件...")
            
            def decrypt_thread():
                try:
                    output_path = output_file if output_file else None
                    success, message = decrypt_file(input_file, output_path, password, keep_original)
                    
                    if success:
                        final_output = output_path or (input_file[:-4] if input_file.endswith('.enc') else f"{input_file}.dec")
                        self.root.after(0, lambda: self.update_status("解密完成"))
                        self.root.after(0, lambda: messagebox.showinfo("成功", f"文件解密成功!\n输出文件: {final_output}"))
                    else:
                        self.root.after(0, lambda: self.update_status("解密失败"))
                        self.root.after(0, lambda: self.show_error("失败", f"文件解密失败: {message}"))
                except Exception as e:
                    error_info = traceback.format_exc()
                    self.root.after(0, lambda: self.update_status("解密出错"))
                    self.root.after(0, lambda: self.show_error("错误", f"解密过程中出错:\n{str(e)}\n\n详细信息:\n{error_info}"))
            
            threading.Thread(target=decrypt_thread, daemon=True).start()
        except Exception as e:
            error_info = traceback.format_exc()
            self.update_status("出现意外错误")
            self.show_error("程序错误", f"在启动单文件解密时发生未知错误:\n\n{str(e)}\n\n详细信息:\n{error_info}")
    
    def decrypt_batch(self):
        """批量解密"""
        try:
            input_dir = self.input_dir_var.get().strip()
            output_dir = self.output_dir_var.get().strip()
            password = self.batch_password_var.get().strip()
            recursive = self.recursive_var.get()
            keep_original = self.batch_keep_original_var.get()
            
            if not input_dir:
                self.show_error("错误", "请选择输入目录")
                return
            
            if not password:
                self.show_error("错误", "请输入解密密码")
                return
            
            if not os.path.isdir(input_dir):
                self.show_error("错误", "输入目录不存在")
                return
            
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    self.show_error("错误", f"无法创建输出目录: {str(e)}")
                    return
            
            self.update_status("正在批量解密...")
            if HAS_CUSTOMTKINTER:
                self.progress_bar.set(0)
            else:
                self.progress_var.set(0)
            
            def decrypt_batch_thread():
                try:
                    output_path = output_dir if output_dir else None
                    success, message = decrypt_directory(
                        input_dir, password, recursive, keep_original, output_path
                    )
                    
                    if HAS_CUSTOMTKINTER:
                        self.root.after(0, lambda: self.progress_bar.set(1.0))
                    else:
                        self.root.after(0, lambda: self.progress_var.set(100))
                    
                    if success:
                        self.root.after(0, lambda: self.update_status("批量解密完成"))
                        self.root.after(0, lambda: messagebox.showinfo("完成", message))
                    else:
                        self.root.after(0, lambda: self.update_status("批量解密失败"))
                        self.root.after(0, lambda: self.show_error("失败", message))
                    
                except Exception as e:
                    error_info = traceback.format_exc()
                    self.root.after(0, lambda: self.update_status("批量解密出错"))
                    self.root.after(0, lambda: self.show_error("错误", f"批量解密过程中出错:\n{str(e)}\n\n详细信息:\n{error_info}"))
            
            threading.Thread(target=decrypt_batch_thread, daemon=True).start()
        except Exception as e:
            error_info = traceback.format_exc()
            self.update_status("出现意外错误")
            self.show_error("程序错误", f"在启动批量解密时发生未知错误:\n\n{str(e)}\n\n详细信息:\n{error_info}")
    
    def on_closing(self):
        """窗口关闭事件处理"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = ModernDecryptGUI()
        app.run()
    except Exception as e:
        print(f"启动GUI失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()