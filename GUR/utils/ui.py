"""
UI工具模块
处理终端界面显示
"""
import os
import sys
from typing import Optional
from utils.colors import colored, print_colored, ColorCodes
from core.config import config


class UI:
    """用户界面类"""
    
    def __init__(self):
        self.width = 80
        self.update_terminal_size()
    
    def update_terminal_size(self) -> None:
        """更新终端大小"""
        try:
            import shutil
            terminal_size = shutil.get_terminal_size()
            self.width = terminal_size.columns
        except:
            self.width = 80
    
    def clear(self) -> None:
        """清屏"""
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    
    def print_header(self) -> None:
        """打印程序头部"""
        self.update_terminal_size()
        width = min(self.width, 80)
        
        header = """
╔══════════════════════════════════════════════════════════════╗
║                 小薄荷 终端助手 v1.0                          ║
║           虽然目前还没有什么很强大的功能                        ║
╚══════════════════════════════════════════════════════════════╝
"""
        print_colored(header, "cyan")
    
    def print_welcome(self) -> None:
        """打印欢迎信息"""
        welcome = """
欢迎使用 小薄荷 终端助手！

快速开始:
  1. 直接输入文字对话
  2. 输入 /help 查看所有命令
  3. 输入 /options 进入设置模式
  4. 输入 /exit 退出程序

提示:
  - 会话会自动保存到 memory/ 文件夹
  - 人格文件放在 Cha/ 文件夹（.md格式）
  - 使用 /cha 切换人格
  - 使用 /change 切换会话
"""
        print_colored(welcome, "white")
    
    def print_separator(self, char: str = '─') -> None:
        """打印分隔线"""
        self.update_terminal_size()
        width = min(self.width - 2, 78)
        line = char * width
        print_colored(line, "dark_white")
    
    def print_message(self, role: str, content: str, show_thinking: bool = False) -> None:
        """
        打印消息
        
        Args:
            role: 角色 (user, ai, system)
            content: 消息内容
            show_thinking: 是否显示思考过程
        """
        if role == "user":
            color = config.get_color("user")
            prefix = colored("[你] ", color)
            print(f"{prefix}{content}")
        
        elif role == "assistant":
            color = config.get_color("ai")
            prefix = colored("[Kimi] ", color)
            print(f"{prefix}{content}")
        
        elif role == "system":
            color = config.get_color("system")
            prefix = colored("[系统] ", color)
            print(f"{prefix}{content}")
        
        elif role == "thinking":
            if show_thinking:
                color = config.get_color("info")
                prefix = colored("[思考] ", color)
                print(f"{prefix}{content}")
        
        elif role == "error":
            color = config.get_color("error")
            prefix = colored("[错误] ", color)
            print(f"{prefix}{content}")
        
        elif role == "warning":
            color = config.get_color("warning")
            prefix = colored("[警告] ", color)
            print(f"{prefix}{content}")
        
        elif role == "info":
            color = config.get_color("info")
            prefix = colored("[信息] ", color)
            print(f"{prefix}{content}")
    
    def print_stream_chunk(self, chunk: str, is_first: bool = False) -> None:
        """
        打印流式响应片段
        
        Args:
            chunk: 文本片段
            is_first: 是否是第一个片段
        """
        color = config.get_color("ai")
        if is_first:
            prefix = colored("[Kimi] ", color)
            print(prefix, end='')
        
        # 直接输出，不添加颜色（保持流式输出的流畅性）
        print(chunk, end='', flush=True)
    
    def print_stream_end(self) -> None:
        """流式输出结束"""
        print()  # 换行
    
    def print_prompt(self, in_settings: bool = False) -> None:
        """
        打印输入提示符
        
        Args:
            in_settings: 是否在设置模式
        """
        if in_settings:
            prompt = colored("[设置] ", "yellow") + "> "
        else:
            prompt = colored("> ", config.get_color("user"))
        
        print(prompt, end='')
    
    def print_status_bar(self, session_name: str, personality_name: str, thinking: bool = False) -> None:
        """
        打印状态栏
        
        Args:
            session_name: 当前会话名称
            personality_name: 当前人格名称
            thinking: 思考模式是否开启
        """
        self.update_terminal_size()
        
        thinking_status = "开启" if thinking else "关闭"
        status = f" 会话: {session_name} | 人格: {personality_name} | 思考: {thinking_status} "
        
        # 居中显示
        width = min(self.width, 80)
        padding = (width - len(status)) // 2
        if padding < 0:
            padding = 0
        
        line = "─" * padding + status + "─" * (width - padding - len(status))
        print_colored(line, "dark_white")
    
    def print_api_key_prompt(self) -> str:
        """
        打印API密钥输入提示
        
        Returns:
            用户输入的API密钥
        """
        self.print_header()
        print()
        print_colored("首次使用需要设置Kimi API密钥", "yellow")
        print_colored("您可以从 https://platform.moonshot.cn/ 获取API密钥", "white")
        print()
        print_colored("提示: 输入时不会显示字符（密码保护），输入完成后按Enter", "dark_white")
        print()
        
        # 尝试使用getpass隐藏输入，如果失败则使用普通input
        api_key = ""
        try:
            import getpass
            # 使用提示文本调用getpass
            api_key = getpass.getpass(colored("请输入API密钥: ", "cyan"))
        except Exception as e:
            # getpass失败，使用普通input
            print_colored("（无法隐藏输入，将明文显示）", "yellow")
            print_colored("请输入API密钥: ", "cyan", end='')
            api_key = input()
        
        return api_key.strip()
    
    def print_error(self, message: str) -> None:
        """打印错误信息"""
        self.print_message("error", message)
    
    def print_warning(self, message: str) -> None:
        """打印警告信息"""
        self.print_message("warning", message)
    
    def print_info(self, message: str) -> None:
        """打印信息"""
        self.print_message("info", message)
    
    def print_success(self, message: str) -> None:
        """打印成功信息"""
        color = config.get_color("system")
        prefix = colored("[成功] ", color)
        print(f"{prefix}{message}")
    
    def confirm(self, message: str) -> bool:
        """
        确认对话框
        
        Args:
            message: 确认消息
        
        Returns:
            是否确认
        """
        prompt = colored(f"{message} (y/n): ", "yellow")
        response = input(prompt).strip().lower()
        return response in ['y', 'yes', '是', '确认', '确定']


# 全局UI实例
ui = UI()
