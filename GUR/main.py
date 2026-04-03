#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kimi 终端助手
一个支持多会话、人格切换、颜色自定义的终端AI对话应用

作者: AI Assistant
版本: 1.0.0
Python: 3.13+
"""

import os
import sys
import time
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.colors import enable_windows_colors, colored
from utils.ui import ui
from core.config import config
from core.session import session_manager
from core.personality import personality_manager
from core.kimi_api import kimi_api, KimiAPIError
from core.commands import command_handler


class KimiTerminal:
    """终端"""
    
    def __init__(self):
        self.running = False
        self.waiting_for_session_id = False
        
        # 确保目录存在
        self._ensure_directories()
        
        # 启用Windows颜色支持
        enable_windows_colors()
    
    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        dirs = ["Cha", "memory"]
        for d in dirs:
            Path(d).mkdir(exist_ok=True)
    
    def _show_manual_config_help(self) -> None:
        """显示手动配置帮助"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
                # 构建消息列表
║    "api_base": "https://api.moonshot.cn/v1",                 ║
║    "model": "kimi-latest",                                   ║
║    "thinking_enabled": false,                                ║
║    "auto_save": true                                         ║
║  }                                                            ║
║                                                              ║
║  3. 保存文件后重新运行程序                                    ║
║                                                              ║
║  注意: 密钥请从 https://platform.moonshot.cn/ 获取           ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(help_text)
    
    def _check_api_key(self) -> bool:
        """启动时检查 API 密钥。

        行为：
        - 如果 `config` 中已配置 `api_key`，则将其设置到 `kimi_api` 并返回 True。
        - 如果未配置（为空），则不进行交互式输入，提示用户手动编辑 `config.json`，返回 False。
        """
        # 只在启动时强制检查配置，禁止交互式输入
        if not config.is_configured() or not config.api_key:
            ui.print_error("未在 config.json 中配置 API 密钥 (api_key)。")
            ui.print_info("请手动编辑 config.json，添加：\n  \"api_key\": \"你的密钥\"\n然后重新启动程序。")
            return False

        # 已配置，设定给 API 客户端并继续
        kimi_api.set_api_key(config.api_key)
        return True
    
    def _build_messages(self, user_input: str) -> list:
        # 构建消息列表
        messages = []
        personality = personality_manager.get_current_personality()
        if personality:
            messages.append({
                "role": "system",
                "content": personality.get_system_prompt()
            })
        session = session_manager.get_current_session()
        if session:
            recent_messages = session.messages[-20:] if len(session.messages) > 20 else session.messages
            for msg in recent_messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role and content and role != "system":
                    messages.append({
                        "role": role,
                        "content": content
                    })
        messages.append({
            "role": "user",
            "content": user_input
        })
        return messages

    def _send_message(self, user_input: str) -> None:
        # 发送消息到Kimi并显示响应
        session = session_manager.get_current_session()
        if session:
            session.add_message("user", user_input)
            session_manager.save_current_session()
        messages = self._build_messages(user_input)
        try:
            ui.print_separator()
            full_response = ""
            is_first = True
            for chunk in kimi_api.chat_completion(
                messages=messages,
                stream=True,
                temperature=1,
                thinking=config.thinking_enabled
            ):
                if is_first:
                    color = config.get_color("ai")
                    prefix = colored("[Kimi] ", color)
                    print(prefix, end='')
                print(chunk, end='', flush=True)
                full_response += chunk
                is_first = False
            print()
            ui.print_separator()
            if session and full_response:
                session.add_message("assistant", full_response)
                session_manager.save_current_session()
        except KimiAPIError as e:
            ui.print_error(str(e))
        except Exception as e:
            ui.print_error(f"发生错误: {str(e)}")
    
    def _handle_change_chat(self, user_input: str) -> bool:
        """
        处理交互式会话切换
        
        Args:
            user_input: 用户输入
        
        Returns:
            是否处理了输入
        """
        if not self.waiting_for_session_id:
            return False
        
        user_input = user_input.strip()
        
        if user_input.lower() in ['cancel', '取消', 'c']:
            self.waiting_for_session_id = False
            ui.print_info("已取消切换")
            return True
        
        try:
            session_id = int(user_input)
            if session_manager.switch_session(session_id):
                session = session_manager.get_current_session()
                ui.print_success(f"已切换到会话: {session.name} [ID: {session_id}]")
            else:
                ui.print_error(f"会话 {session_id} 不存在")
        except ValueError:
            ui.print_error("请输入有效的数字会话ID")
        
        self.waiting_for_session_id = False
        return True
    
    def _process_command(self, user_input: str) -> bool:
        """
        处理命令
        
        Args:
            user_input: 用户输入
        
        Returns:
            是否退出程序
        """
        # 检查是否是切换会话的等待状态
        if self.waiting_for_session_id:
            self._handle_change_chat(user_input)
            return False
        
        # 处理命令
        should_exit, response = command_handler.process(user_input)

        if response:
            ui.print_info(response)

            # 如果命令返回了一个等待输入的提示（例如 /change chat），
            # 设定等待标志以便下一次用户输入被视为会话ID
            if "[等待输入]" in response:
                self.waiting_for_session_id = True
                return False
        
        return should_exit
    
    def _print_status(self) -> None:
        """打印状态栏"""
        session = session_manager.get_current_session()
        session_name = session.name if session else "无"
        personality_name = personality_manager.get_current_name()
        ui.print_status_bar(session_name, personality_name, config.thinking_enabled)
    
    def run(self):
        """运行主循环"""
        self.running = True

        # 检查API密钥
        if not self._check_api_key():
            ui.print_error("程序需要有效的API密钥才能运行")
            input("按Enter键退出...")
            return

        # 清屏并显示欢迎信息
        ui.clear()
        ui.print_header()
        ui.print_welcome()

        # 显示当前会话信息
        session = session_manager.get_current_session()
        if session:
            ui.print_info(f"当前会话: {session.name} [ID: {session.session_id}]")

        personality = personality_manager.get_current_personality()
        if personality:
            ui.print_info(f"当前人格: {personality.display_name}")

        print()

        # 主循环
        while self.running:
            try:
                self._print_status()
                ui.print_prompt(command_handler.in_settings_mode)

                # 多行输入支持
                lines = []
                newline_key = config.get_newline_key().lower()
                allowed_keys = ["ctrl", "alt", "tab", "fn"] + [f"f{i}" for i in range(1, 13)]
                prompt_tip = f"（按 {newline_key.upper()} 换行，Enter 发送）"
                if not command_handler.in_settings_mode:
                    print(prompt_tip)

                import msvcrt
                # 使用 GetAsyncKeyState 检测 Ctrl / Alt 修饰键（仅 Windows）
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    VK_CONTROL = 0x11
                    VK_MENU = 0x12

                    def _is_key_pressed(vk: int) -> bool:
                        return (user32.GetAsyncKeyState(vk) & 0x8000) != 0
                except Exception:
                    # 如果无法使用 ctypes，则不支持 Ctrl/Alt 检测
                    def _is_key_pressed(vk: int) -> bool:
                        return False

                buffer = ""
                while True:
                    ch = msvcrt.getwch()
                    # Enter: 如果配置为 Ctrl/Alt 换行且相应修饰键被按下，则作为换行处理
                    if ch == '\r' or ch == '\n':
                        if newline_key == "ctrl" and _is_key_pressed(VK_CONTROL):
                            lines.append(buffer)
                            buffer = ""
                            print()
                            continue
                        if newline_key == "alt" and _is_key_pressed(VK_MENU):
                            lines.append(buffer)
                            buffer = ""
                            print()
                            continue
                        if buffer:
                            lines.append(buffer)
                        break

                    # Tab 作为换行键
                    if newline_key == "tab" and ch == '\t':
                        lines.append(buffer)
                        buffer = ""
                        print()
                        continue

                    # F1-F12 处理（功能键通常返回两个字符前缀 + 代码）
                    if newline_key.startswith("f") and newline_key[1:].isdigit():
                        fnum = int(newline_key[1:])
                        if ch == '\0' or ch == '\xe0':
                            ch2 = msvcrt.getwch()
                            if ord(ch2) == 58 + fnum:  # F1=59
                                lines.append(buffer)
                                buffer = ""
                                print()
                                continue
                            else:
                                # 非目标功能键，将 ch2 作为普通字符处理
                                buffer += ch2
                                print(ch2, end='', flush=True)
                                continue

                    # 其他（fn 无法捕获）
                    buffer += ch
                    print(ch, end='', flush=True)

                user_input = "\n".join(lines).strip()
                print()  # 输入结束换行

                if not user_input:
                    continue
                if user_input.startswith('/'):
                    should_exit = self._process_command(user_input)
                    if should_exit:
                        break
                    continue
                if self._handle_change_chat(user_input):
                    continue
                self._send_message(user_input)

            except KeyboardInterrupt:
                print()
                ui.print_info("程序被中断")
                break
            except Exception as e:
                ui.print_error(f"发生错误: {str(e)}")

        ui.print_info("正在保存会话...")
        session_manager.save_all_sessions()
        config.save()
        ui.print_success("已保存，再见！")


def main():
    """主入口函数"""
    try:
        app = KimiTerminal()
        app.run()
    except Exception as e:
        print(f"程序发生致命错误: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")


if __name__ == "__main__":
    main()
