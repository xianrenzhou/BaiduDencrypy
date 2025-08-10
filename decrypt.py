#!/usr/bin/env python3
"""
百度网盘加密文件解密工具 (核心逻辑库)

此文件包含解密的核心功能，被设计为可供其他脚本（如GUI）导入使用。
它本身不应直接产生控制台输出（如print），以便在无控制台环境（如打包后的GUI程序）中稳定运行。
所有状态和结果都通过函数返回值传递。
"""

import os
import sys
import argparse
import hashlib
from pathlib import Path

# 让调用方（GUI或CLI的main函数）来处理这个错误。
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
except ImportError:
    # Pass here, the error will be caught by the calling script's entry point.
    pass

# --- Core Decryption Functions (Silent, for Library Use) ---

def derive_key(password, salt, iterations=100000):
    """从密码派生密钥"""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, dklen=32)

def decrypt_data(encrypted_data, password="123456"):
    """解密数据"""
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    actual_encrypted_data = encrypted_data[32:]
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded_data = cipher.decrypt(actual_encrypted_data)
    decrypted_data = unpad(decrypted_padded_data, AES.block_size)
    return decrypted_data

def is_encrypted_file(file_path):
    """简单检查文件是否可能是我们的加密文件"""
    try:
        if os.path.getsize(file_path) < 48:
            return False
        with open(file_path, 'rb') as f:
            header = f.read(32)
            return len(header) == 32
    except Exception:
        return False

def decrypt_file(input_file_path, output_file_path=None, password="123456", keep_original=False, output_dir=None):
    """解密单个文件 (静默模式)"""
    if not os.path.exists(input_file_path):
        return False, f"文件不存在: {input_file_path}"

    if not output_file_path:
        if output_dir:
            filename = os.path.basename(input_file_path)
            output_file_path = os.path.join(output_dir, filename)
        else:
            if input_file_path.lower().endswith('.enc'):
                output_file_path = input_file_path[:-4]
            else:
                base_dir = os.path.dirname(input_file_path)
                filename = os.path.basename(input_file_path)
                output_file_path = os.path.join(base_dir, f"{filename}.dec")
    
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    try:
        with open(input_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        if not is_encrypted_file(input_file_path):
             return False, f"文件可能不是加密文件: {input_file_path}"

        decrypted_data = decrypt_data(encrypted_data, password)
        
        with open(output_file_path, 'wb') as f:
            f.write(decrypted_data)
        
        if not keep_original:
            os.remove(input_file_path)
        
        return True, "解密成功"
    except Exception:
        return False, "解密失败，密码可能不正确或文件已损坏。"

def decrypt_directory(directory_path, password="123456", recursive=False, keep_original=False, output_dir=None, progress_callback=None):
    """解密目录中的所有加密文件，并复制其他文件 (静默模式)"""
    if not os.path.isdir(directory_path):
        return False, f"错误: 目录不存在: {directory_path}"
    
    decrypt_success_count = 0
    decrypt_failed_count = 0
    copy_count = 0
    skipped_count = 0
    
    try:
        if recursive:
            all_files = [str(p) for p in Path(directory_path).rglob('*') if p.is_file()]
        else:
            all_files = [str(p) for p in Path(directory_path).glob('*') if p.is_file()]

        total_files = len(all_files)
        for i, file_path in enumerate(all_files):
            if progress_callback:
                progress_callback(i + 1, total_files)

            rel_path = os.path.relpath(file_path, directory_path)
            
            if output_dir:
                target_path = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                if is_encrypted_file(file_path):
                    success, _ = decrypt_file(file_path, target_path, password, keep_original)
                    if success:
                        decrypt_success_count += 1
                    else:
                        decrypt_failed_count += 1
                else:
                    import shutil
                    shutil.copy2(file_path, target_path)
                    copy_count += 1
                    if not keep_original:
                        os.remove(file_path)
            else:
                if is_encrypted_file(file_path):
                    success, _ = decrypt_file(file_path, None, password, keep_original)
                    if success:
                        decrypt_success_count += 1
                    else:
                        decrypt_failed_count += 1
                else:
                    skipped_count += 1
        
        message = (f"处理完成! 成功: {decrypt_success_count}, 失败: {decrypt_failed_count}, "
                   f"复制: {copy_count}, 跳过: {skipped_count}")
        return True, message
        
    except Exception as e:
        return False, f"处理目录时出错: {str(e)}"

# --- Command-Line Interface (CLI) Specific Code ---

def main_cli():
    """This function is for command-line use only. Print statements here are safe."""
    try:
        from tqdm import tqdm
    except ImportError:
        print("错误: 缺少 'tqdm' 库。请运行: pip install tqdm")
        sys.exit(1)
        
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
    except ImportError:
        print("错误: 缺少 'pycryptodome' 库。请运行: pip install pycryptodome")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="百度网盘加密文件解密工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="要解密的单个文件路径")
    group.add_argument("-d", "--directory", help="包含加密文件的目录路径")
    
    parser.add_argument("-p", "--password", default="123456", help="解密密码，默认为123456")
    parser.add_argument("-o", "--output", help="输出路径（单个文件时为输出文件路径，目录时为输出目录路径）")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子目录")
    parser.add_argument("-k", "--keep", action="store_true", help="保留原始加密文件")
    
    args = parser.parse_args()
    
    if args.file:
        success, message = decrypt_file(args.file, args.output, args.password, args.keep)
        if success:
            output_path = args.output or (args.file[:-4] if args.file.lower().endswith('.enc') else f"{args.file}.dec")
            print(f"✅ 文件解密成功: {output_path}")
        else:
            print(f"❌ {message}")
    
    elif args.directory:
        print(f"开始解密目录: {args.directory} {'(递归)' if args.recursive else ''}")
        if args.output:
            print(f"输出目录: {args.output}")
        
        if not os.path.isdir(args.directory):
            print(f"错误: 目录不存在: {args.directory}")
            sys.exit(1)
        
        if args.recursive:
            all_files = [str(p) for p in Path(args.directory).rglob('*') if p.is_file()]
        else:
            all_files = [str(p) for p in Path(args.directory).glob('*') if p.is_file()]
        
        decrypt_success_count = 0
        decrypt_failed_count = 0
        copy_count = 0
        skipped_count = 0

        with tqdm(all_files, desc="处理进度") as pbar:
            for file_path in pbar:
                pbar.set_description(f"处理: {os.path.basename(file_path)}")
                
                rel_path = os.path.relpath(file_path, args.directory)
                
                if args.output:
                    target_path = os.path.join(args.output, rel_path)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    if is_encrypted_file(file_path):
                        success, _ = decrypt_file(file_path, target_path, args.password, args.keep)
                        if success:
                            decrypt_success_count += 1
                        else:
                            decrypt_failed_count += 1
                    else:
                        import shutil
                        shutil.copy2(file_path, target_path)
                        copy_count += 1
                        if not args.keep:
                            os.remove(file_path)
                else:
                    if is_encrypted_file(file_path):
                        success, _ = decrypt_file(file_path, None, args.password, args.keep)
                        if success:
                            decrypt_success_count += 1
                        else:
                            decrypt_failed_count += 1
                    else:
                        skipped_count += 1
        
        message = (f"处理完成! 成功: {decrypt_success_count}, 失败: {decrypt_failed_count}, "
                   f"复制: {copy_count}, 跳过: {skipped_count}")
        print(f"\n{message}")

if __name__ == "__main__":
    try:
        main_cli()
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"程序出错: {str(e)}")
        sys.exit(1)
