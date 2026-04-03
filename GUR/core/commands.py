"""
命令处理器模块
处理所有终端命令
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from utils.colors import colored, print_colored
from core.config import config
from core.session import session_manager
from core.personality import personality_manager


class CommandHandler:
    """命令处理器"""
    
    def __init__(self):
        self.in_settings_mode = False
        self.color_aliases = {
            # 标准颜色
            "black": "black", "red": "red", "green": "green", "yellow": "yellow",
            "blue": "blue", "magenta": "magenta", "cyan": "cyan", "white": "white",
            # 亮色
            "light_black": "light_black", "light_red": "light_red", 
            "light_green": "light_green", "light_yellow": "light_yellow",
            "light_blue": "light_blue", "light_magenta": "light_magenta",
            "light_cyan": "light_cyan", "light_white": "light_white",
            # bright别名
            "bright_black": "bright_black", "bright_red": "bright_red",
            "bright_green": "bright_green", "bright_yellow": "bright_yellow",
            "bright_blue": "bright_blue", "bright_magenta": "bright_magenta",
            "bright_cyan": "bright_cyan", "bright_white": "bright_white",
            # 深色
            "dark_red": "dark_red", "dark_green": "dark_green",
            "dark_yellow": "dark_yellow", "dark_blue": "dark_blue",
            "dark_magenta": "dark_magenta", "dark_cyan": "dark_cyan",
            "dark_white": "dark_white",
        }
    
    def process(self, command: str) -> Tuple[bool, str]:
        """
        处理命令
        
        Args:
            command: 命令字符串
        
        Returns:
            (是否退出程序, 响应消息)
        """
        cmd = command.strip()
        
        if not cmd.startswith('/'):
            return False, ""
        
        parts = cmd[1:].split()
        if not parts:
            return False, ""
        
        cmd_name = parts[0].lower()
        args = parts[1:]
        
        # 如果在设置模式
        if self.in_settings_mode:
            return self._handle_settings_command(cmd_name, args)
        
        # 普通命令
        handlers = {
            'output': self._cmd_output,
            'think': self._cmd_think,
            't': self._cmd_think,
            'options': self._cmd_settings,
            'settings': self._cmd_settings,
            'create': self._cmd_create,
            'change': self._cmd_change,
            'cha': self._cmd_cha,
            'help': self._cmd_help,
            'exit': self._cmd_exit,
            'quit': self._cmd_exit,
            'chat': self._cmd_chat_newline,
        }
        handler = handlers.get(cmd_name)
        if handler:
            return handler(args)
        else:
            return False, f"未知命令: /{cmd_name}，输入 /help 查看帮助"

    def _cmd_chat_newline(self, args: List[str]) -> Tuple[bool, str]:
        """
        /chat [键名] 命令 - 设置换行键
        /chat default 或 /chat tab 恢复为tab
        支持 ctrl/alt/tab/fn/f1~f12
        """
        allowed_keys = ["ctrl", "alt", "tab", "fn"] + [f"f{i}" for i in range(1, 13)]
        if not args or args[0].lower() in ["default", "tab"]:
            config.set_newline_key("tab")
            return False, "换行键已恢复为Tab键（默认）"
        key = args[0].lower()
        if key not in allowed_keys:
            return False, "换行键设置失败，仅支持: ctrl, alt, tab, fn, f1~f12"
        config.set_newline_key(key)
        return False, f"换行键已设置为: {key.upper()}"
    
    def _handle_settings_command(self, cmd_name: str, args: List[str]) -> Tuple[bool, str]:
        """处理设置模式下的命令"""
        handlers = {
            'out': self._cmd_exit_settings,
            'exit': self._cmd_exit_settings,
            'color': self._cmd_color,
        }
        
        handler = handlers.get(cmd_name)
        if handler:
            return handler(args)
        else:
            return False, f"设置模式下未知命令: /{cmd_name}"
    
    def _cmd_output(self, args: List[str]) -> Tuple[bool, str]:
        """
        /output 命令 - 导出会话到文件
        
        用法: /output [文件路径]
        """
        session = session_manager.get_current_session()
        if not session:
            return False, "当前没有活动会话"
        
        # 确定输出路径
        if args:
            output_path = ' '.join(args)
        else:
            # 默认路径
            default_name = f"session_{session.session_id}_{session.name}.txt"
            output_path = str(Path.home() / "Desktop" / default_name)
        
        # 确保路径是绝对路径
        output_path = os.path.abspath(output_path)
        
        # 导出
        if session_manager.export_session(session.session_id, output_path):
            return False, f"会话已导出到: {output_path}"
        else:
            return False, "导出失败"
    
    def _cmd_think(self, args: List[str]) -> Tuple[bool, str]:
        """
        /think 或 /t 命令 - 切换思考模式
        """
        enabled = config.toggle_thinking()
        status = "开启" if enabled else "关闭"
        return False, f"思考模式已{status}"
    
    def _cmd_settings(self, args: List[str]) -> Tuple[bool, str]:
        """
        /options 或 /settings 命令 - 进入设置模式
        """
        self.in_settings_mode = True
        return False, self._get_settings_help()
    
    def _cmd_exit_settings(self, args: List[str]) -> Tuple[bool, str]:
        """
        /out 或 /exit 命令 - 退出设置模式
        """
        self.in_settings_mode = False
        return False, "已退出设置模式"
    
    def _cmd_color(self, args: List[str]) -> Tuple[bool, str]:
        """
        /color 命令 - 设置颜色
        
        用法: 
        /color User red
        /color AI yellow
        /color AI talk light_yellow
        """
        if len(args) < 2:
            return False, "用法: /color <目标> <颜色>\n目标: user, ai, system, error, warning, info\n颜色: black, red, green, yellow, blue, magenta, cyan, white, light_*, bright_*, dark_*"
        
        # 解析目标
        target = args[0]
        
        # 处理 "AI talk" 这种情况
        if len(args) >= 3 and target.lower() == 'ai' and args[1].lower() == 'talk':
            color = args[2]
        else:
            color = args[1]
        
        # 标准化颜色名称
        color_lower = color.lower()
        if color_lower in self.color_aliases:
            color = self.color_aliases[color_lower]
        
        # 设置颜色
        if config.set_color(target, color):
            return False, f"已将 {target} 的颜色设置为 {color}"
        else:
            return False, f"设置失败，不支持的颜色: {color}"
    
    def _cmd_create(self, args: List[str]) -> Tuple[bool, str]:
        """
        /create 命令 - 创建新会话
        """
        name = ' '.join(args) if args else ""
        personality = personality_manager.get_current_name()
        session = session_manager.create_session(name, personality)
        return False, f"已创建新会话: {session.name} [ID: {session.session_id}]"
    
    def _cmd_change(self, args: List[str]) -> Tuple[bool, str]:
        """
        /change 命令 - 切换或显示会话
        
        用法:
        /change           - 显示所有会话
        /change <数字>    - 切换到指定会话
        /change chat      - 切换到其他会话（交互式）
        """
        if not args:
            # 显示所有会话
            sessions = session_manager.list_sessions()
            if not sessions:
                return False, "没有可用会话"
            
            result = ["当前会话列表:"]
            for s in sessions:
                marker = " <- 当前" if s.session_id == session_manager.current_session_id else ""
                result.append(f"  {s.get_display_info()}{marker}")
            
            return False, '\n'.join(result)
        
        arg = args[0].lower()
        
        if arg == 'chat':
            # 交互式切换
            sessions = session_manager.list_sessions()
            if len(sessions) <= 1:
                return False, "只有一个会话，无需切换"
            
            result = ["可用会话:"]
            for s in sessions:
                result.append(f"  [{s.session_id}] {s.name}")
            result.append("请输入会话ID切换到对应会话，或输入 'cancel' 取消")
            
            return False, '\n'.join(result) + "\n[等待输入]"
        
        # 尝试作为数字解析
        try:
            session_id = int(arg)
            if session_manager.switch_session(session_id):
                session = session_manager.get_current_session()
                return False, f"已切换到会话: {session.name} [ID: {session_id}]"
            else:
                return False, f"会话 {session_id} 不存在"
        except ValueError:
            return False, f"无效参数: {arg}，使用 /change 查看会话列表，或 /change <数字> 切换"
    
    def _cmd_cha(self, args: List[str]) -> Tuple[bool, str]:
        """
        /cha 命令 - 切换人格
        
        用法:
        /cha            - 显示所有人格
        /cha <名称>     - 切换到指定人格
        """
        if not args:
            # 显示所有人格
            personalities = personality_manager.list_personalities()
            if not personalities:
                return False, "没有可用人格"
            
            result = ["当前可用人格:"]
            for p in personalities:
                marker = " <- 当前" if p.name.lower() == personality_manager.get_current_name() else ""
                result.append(f"  [{p.name}] {p.display_name}{marker}")
            
            return False, '\n'.join(result)
        
        # 切换人格
        name = ' '.join(args)
        if personality_manager.switch_personality(name):
            personality = personality_manager.get_current_personality()
            return False, f"已切换到人格: {personality.display_name} [{personality.name}]"
        else:
            # 尝试重新加载
            personality_manager.reload()
            if personality_manager.switch_personality(name):
                personality = personality_manager.get_current_personality()
                return False, f"已切换到人格: {personality.display_name} [{personality.name}]"
            
            available = ', '.join(personality_manager.get_personality_names())
            return False, f"人格 '{name}' 不存在。可用人格: {available}"
    
    def _cmd_help(self, args: List[str]) -> Tuple[bool, str]:
        """
        /help 命令 - 显示帮助
        """
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                     薄荷 终端助手 - 命令帮助                   ║
╠══════════════════════════════════════════════════════════════╣
║  普通命令:                                                    ║
║    /output [路径]     导出当前会话到txt文件                    ║
║    /think 或 /t       切换思考模式显示                         ║
║    /options 或 /settings  进入设置模式                        ║
║    /create [名称]     创建新会话                              ║
║    /change            显示所有会话                            ║
║    /change <数字>     切换到指定会话                          ║
║    /change chat       交互式切换会话                          ║
║    /cha               显示所有人格                            ║
║    /cha <名称>        切换到指定人格                          ║
║    /help              显示此帮助                              ║
║    /exit 或 /quit     退出程序                                ║
╠══════════════════════════════════════════════════════════════╣
║  设置模式命令 (输入 /options 进入):                            ║
║    /out 或 /exit      退出设置模式                            ║
║    /color <目标> <颜色>  设置颜色                             ║
║      目标: user, ai, system, error, warning, info             ║
║      颜色: black, red, green, yellow, blue, magenta, cyan,    ║
║            white, light_*, bright_*, dark_*                   ║
║      示例: /color AI light_yellow  将AI输出设为亮黄色          ║
╚══════════════════════════════════════════════════════════════╝
"""
        return False, help_text
    
    def _cmd_exit(self, args: List[str]) -> Tuple[bool, str]:
        """
        /exit 或 /quit 命令 - 退出程序
        """
        return True, "再见！"
    
    def _get_settings_help(self) -> str:
        """获取设置模式帮助"""
        return """
╔══════════════════════════════════════════════════════════════╗
║                        设置模式                               ║
╠══════════════════════════════════════════════════════════════╣
║  可用命令:                                                    ║
║    /out 或 /exit      退出设置模式                            ║
║    /color <目标> <颜色>  设置颜色                             ║
║      目标: user, ai, system, error, warning, info             ║
║      颜色: black, red, green, yellow, blue, magenta, cyan,    ║
║            white, light_*, bright_*, dark_*                   ║
║      示例:                                                    ║
║        /color User red              用户输入为红色             ║
║        /color AI yellow             AI输出为黄色               ║
║        /color AI talk light_yellow  AI输出为亮黄色             ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    def is_waiting_for_session_selection(self) -> bool:
        """是否正在等待用户选择会话"""
        # 这个状态需要外部管理
        return False


# 全局命令处理器实例
command_handler = CommandHandler()
