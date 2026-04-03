"""
配置管理模块
管理颜色设置、API配置等
"""
import json
import os
from typing import Dict, Any, Optional


class Config:
    """配置管理类"""
    
    # 默认颜色配置
    DEFAULT_COLORS = {
        "user": "white",
        "ai": "cyan",
        "system": "green",
        "error": "red",
        "warning": "yellow",
        "info": "blue"
    }
    
    # 支持的颜色列表
    SUPPORTED_COLORS = [
        "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
        "light_black", "light_red", "light_green", "light_yellow", 
        "light_blue", "light_magenta", "light_cyan", "light_white",
        "bright_black", "bright_red", "bright_green", "bright_yellow",
        "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
        "dark_red", "dark_green", "dark_yellow", "dark_blue",
        "dark_magenta", "dark_cyan", "dark_white"
    ]
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.colors = self.DEFAULT_COLORS.copy()
        self.api_key: Optional[str] = None
        self.api_base: str = "https://api.moonshot.cn/v1"
        self.model: str = "kimi-k2.5"
        self.thinking_enabled: bool = False
        self.auto_save: bool = True
        self.newline_key: str = "tab"  # 换行键，默认tab
        self.load()
    
    def load(self) -> None:
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        print(f"[警告] 配置文件为空，将使用默认配置")
                        return
                    data = json.loads(content)
                    self.colors.update(data.get("colors", {}))
                    self.api_key = data.get("api_key", self.api_key)
                    self.api_base = data.get("api_base", self.api_base)
                    self.model = data.get("model", self.model)
                    self.thinking_enabled = data.get("thinking_enabled", self.thinking_enabled)
                    self.auto_save = data.get("auto_save", self.auto_save)
                    self.newline_key = data.get("newline_key", self.newline_key)
            except json.JSONDecodeError as e:
                print(f"[警告] 配置文件格式错误: {e}")
                print(f"[提示] 请检查 {self.config_file} 是否为有效的JSON格式")
                print(f"[提示] 您可以删除该文件让程序重新创建")
            except Exception as e:
                print(f"[警告] 加载配置文件失败: {e}")
    
    def save(self) -> None:
        """保存配置到文件"""
        data = {
            "colors": self.colors,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "model": self.model,
            "thinking_enabled": self.thinking_enabled,
            "auto_save": self.auto_save,
            "newline_key": self.newline_key
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[错误] 保存配置文件失败: {e}")

    def set_newline_key(self, key: str) -> None:
        """设置换行键"""
        self.newline_key = key
        self.save()

    def get_newline_key(self) -> str:
        """获取换行键"""
        return self.newline_key
    
    def set_color(self, target: str, color: str) -> bool:
        """
        设置颜色
        target: 'user', 'ai', 'system', 'error', 'warning', 'info'
        color: 颜色名称
        """
        color_lower = color.lower()
        if color_lower not in self.SUPPORTED_COLORS:
            return False
        
        target_lower = target.lower()
        if target_lower in ["ai", "ai_talk", "assistant"]:
            self.colors["ai"] = color_lower
        elif target_lower in ["user", "me"]:
            self.colors["user"] = color_lower
        elif target_lower in ["system", "sys"]:
            self.colors["system"] = color_lower
        elif target_lower in ["error", "err"]:
            self.colors["error"] = color_lower
        elif target_lower in ["warning", "warn"]:
            self.colors["warning"] = color_lower
        elif target_lower in ["info", "information"]:
            self.colors["info"] = color_lower
        else:
            return False
        
        self.save()
        return True
    
    def get_color(self, target: str) -> str:
        """获取指定目标的颜色"""
        target_lower = target.lower()
        if target_lower in ["ai", "ai_talk", "assistant"]:
            return self.colors.get("ai", "cyan")
        elif target_lower in ["user", "me"]:
            return self.colors.get("user", "white")
        elif target_lower in ["system", "sys"]:
            return self.colors.get("system", "green")
        elif target_lower in ["error", "err"]:
            return self.colors.get("error", "red")
        elif target_lower in ["warning", "warn"]:
            return self.colors.get("warning", "yellow")
        elif target_lower in ["info", "information"]:
            return self.colors.get("info", "blue")
        return "white"
    
    def set_api_key(self, api_key: str) -> None:
        """设置API密钥"""
        self.api_key = api_key
        self.save()
    
    def set_model(self, model: str) -> None:
        """设置模型"""
        self.model = model
        self.save()
    
    def toggle_thinking(self) -> bool:
        """切换思考模式"""
        self.thinking_enabled = not self.thinking_enabled
        self.save()
        return self.thinking_enabled
    
    def is_configured(self) -> bool:
        """检查是否已配置API密钥"""
        return self.api_key is not None and len(self.api_key) > 0
    
    def create_example_config(self, output_path: str = "config.example.json") -> bool:
        """
        创建示例配置文件
        
        Args:
            output_path: 输出路径
        
        Returns:
            是否成功
        """
        example_data = {
            "colors": {
                "user": "white",
                "ai": "cyan",
                "system": "green",
                "error": "red",
                "warning": "yellow",
                "info": "blue"
            },
            "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "api_base": "https://api.moonshot.cn/v1",
            "model": "kimi-k2.5",
            "thinking_enabled": False,
            "auto_save": True
        }
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(example_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[错误] 创建示例配置文件失败: {e}")
            return False


# 全局配置实例
config = Config()
