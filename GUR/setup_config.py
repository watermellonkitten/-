#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件设置助手
用于手动创建或修改 config.json
"""

import json
import os
import sys
from pathlib import Path


def create_config_interactive():
    """交互式创建配置文件"""
    print("=" * 60)
    print("       Kimi 终端助手 - 配置文件设置")
    print("=" * 60)
    print()
    print("提示: 您可以从 https://platform.moonshot.cn/ 获取 API 密钥")
    print()
    
    # 读取现有配置（如果有）
    config_file = Path("config.json")
    existing_config = {}
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            print(f"[信息] 发现现有配置文件，将在此基础上修改")
        except Exception as e:
            print(f"[警告] 读取现有配置失败: {e}")
    
    # 获取API密钥
    print()
    print("-" * 60)
    api_key = input("请输入 Kimi API 密钥: ").strip()
    
    if not api_key:
        print("[错误] API 密钥不能为空！")
        input("按 Enter 键退出...")
        return False
    
    # 构建配置
    config = {
        "api_key": api_key,
        "api_base": existing_config.get("api_base", "https://api.moonshot.cn/v1"),
        "model": existing_config.get("model", "kimi-k2.5"),
        "thinking_enabled": existing_config.get("thinking_enabled", False),
        "auto_save": existing_config.get("auto_save", True),
        "colors": existing_config.get("colors", {
            "user": "white",
            "ai": "cyan",
            "system": "green",
            "error": "red",
            "warning": "yellow",
            "info": "blue"
        })
    }
    
    # 保存配置
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print()
        print("=" * 60)
        print("[成功] 配置文件已保存到:", config_file.absolute())
        print("=" * 60)
        print()
        print("现在您可以运行 main.py 开始使用终端助手了！")
        print()
        input("按 Enter 键退出...")
        return True
    except Exception as e:
        print(f"[错误] 保存配置文件失败: {e}")
        input("按 Enter 键退出...")
        return False


def show_config():
    """显示当前配置"""
    config_file = Path("config.json")
    
    if not config_file.exists():
        print("[信息] 未找到配置文件 config.json")
        return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("=" * 60)
        print("            当前配置")
        print("=" * 60)
        print()
        
        # 隐藏API密钥的部分内容
        api_key = config.get("api_key", "")
        if api_key:
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            print(f"API 密钥: {masked_key}")
        else:
            print("API 密钥: (未设置)")
        
        print(f"API 地址: {config.get('api_base', 'https://api.moonshot.cn/v1')}")
        print(f"模型: {config.get('model', 'kimi-latest')}")
        print(f"思考模式: {'开启' if config.get('thinking_enabled') else '关闭'}")
        print(f"自动保存: {'开启' if config.get('auto_save') else '关闭'}")
        print()
        print("颜色设置:")
        colors = config.get("colors", {})
        for key, value in colors.items():
            print(f"  {key}: {value}")
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"[错误] 读取配置文件失败: {e}")


def main():
    """主函数"""
    print()
    print("Kimi 终端助手 - 配置工具")
    print()
    
    while True:
        print("-" * 40)
        print("选项:")
        print("  1. 创建/修改配置文件")
        print("  2. 查看当前配置")
        print("  3. 退出")
        print()
        
        choice = input("请选择 (1/2/3): ").strip()
        
        if choice == '1':
            create_config_interactive()
            break
        elif choice == '2':
            show_config()
            print()
            input("按 Enter 键继续...")
            print()
        elif choice == '3':
            print("再见！")
            break
        else:
            print("[错误] 无效选项，请重新选择")
            print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("已取消")
        sys.exit(0)
