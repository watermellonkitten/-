"""
颜色工具模块
提供终端颜色支持
"""
import os


class ColorCodes:
    """ANSI颜色代码"""
    # 标准颜色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色
    LIGHT_BLACK = '\033[90m'
    LIGHT_RED = '\033[91m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_MAGENTA = '\033[95m'
    LIGHT_CYAN = '\033[96m'
    LIGHT_WHITE = '\033[97m'
    
    # 别名（bright = light）
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 深色（通过dim属性实现）
    DARK_RED = '\033[2;31m'
    DARK_GREEN = '\033[2;32m'
    DARK_YELLOW = '\033[2;33m'
    DARK_BLUE = '\033[2;34m'
    DARK_MAGENTA = '\033[2;35m'
    DARK_CYAN = '\033[2;36m'
    DARK_WHITE = '\033[2;37m'
    
    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKE = '\033[9m'
    
    # 重置
    RESET = '\033[0m'


# 颜色名称到代码的映射
COLOR_MAP = {
    "black": ColorCodes.BLACK,
    "red": ColorCodes.RED,
    "green": ColorCodes.GREEN,
    "yellow": ColorCodes.YELLOW,
    "blue": ColorCodes.BLUE,
    "magenta": ColorCodes.MAGENTA,
    "cyan": ColorCodes.CYAN,
    "white": ColorCodes.WHITE,
    "light_black": ColorCodes.LIGHT_BLACK,
    "light_red": ColorCodes.LIGHT_RED,
    "light_green": ColorCodes.LIGHT_GREEN,
    "light_yellow": ColorCodes.LIGHT_YELLOW,
    "light_blue": ColorCodes.LIGHT_BLUE,
    "light_magenta": ColorCodes.LIGHT_MAGENTA,
    "light_cyan": ColorCodes.LIGHT_CYAN,
    "light_white": ColorCodes.LIGHT_WHITE,
    "bright_black": ColorCodes.BRIGHT_BLACK,
    "bright_red": ColorCodes.BRIGHT_RED,
    "bright_green": ColorCodes.BRIGHT_GREEN,
    "bright_yellow": ColorCodes.BRIGHT_YELLOW,
    "bright_blue": ColorCodes.BRIGHT_BLUE,
    "bright_magenta": ColorCodes.BRIGHT_MAGENTA,
    "bright_cyan": ColorCodes.BRIGHT_CYAN,
    "bright_white": ColorCodes.BRIGHT_WHITE,
    "dark_red": ColorCodes.DARK_RED,
    "dark_green": ColorCodes.DARK_GREEN,
    "dark_yellow": ColorCodes.DARK_YELLOW,
    "dark_blue": ColorCodes.DARK_BLUE,
    "dark_magenta": ColorCodes.DARK_MAGENTA,
    "dark_cyan": ColorCodes.DARK_CYAN,
    "dark_white": ColorCodes.DARK_WHITE,
}


def colored(text: str, color: str) -> str:
    """
    为文本添加颜色
    
    Args:
        text: 要着色的文本
        color: 颜色名称
    
    Returns:
        着色后的文本
    """
    color_code = COLOR_MAP.get(color.lower(), ColorCodes.WHITE)
    return f"{color_code}{text}{ColorCodes.RESET}"


def print_colored(text: str, color: str, end: str = '\n') -> None:
    """
    打印带颜色的文本
    
    Args:
        text: 要打印的文本
        color: 颜色名称
        end: 行尾字符
    """
    print(colored(text, color), end=end)


def print_multi_color(parts: list[tuple[str, str]], end: str = '\n') -> None:
    """
    打印多色文本
    
    Args:
        parts: [(文本, 颜色), ...] 的列表
        end: 行尾字符
    """
    result = ""
    for text, color in parts:
        result += colored(text, color)
    print(result, end=end)


def strip_colors(text: str) -> str:
    """
    移除文本中的ANSI颜色代码
    
    Args:
        text: 带颜色的文本
    
    Returns:
        纯文本
    """
    import re
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return ansi_escape.sub('', text)


def enable_windows_colors() -> None:
    """在Windows上启用ANSI颜色支持"""
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


# 初始化Windows颜色支持
enable_windows_colors()
