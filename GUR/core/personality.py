"""
人格文件管理模块
管理Cha文件夹下的人格文件
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional


class Personality:
    """人格类"""
    
    def __init__(self, name: str, file_path: str, content: str):
        self.name = name
        self.file_path = file_path
        self.content = content
        self.display_name = self._extract_display_name()
    
    def _extract_display_name(self) -> str:
        """从内容中提取显示名称（如果有）"""
        # 尝试从第一行提取标题
        lines = self.content.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            # 匹配Markdown标题
            if line.startswith('# '):
                return line[2:].strip()
            if line.startswith('## '):
                return line[3:].strip()
            # 匹配名称
            match = re.match(r'^[名称|Name][\s]*[:：]\s*(.+)$', line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 使用文件名（去掉扩展名）
        return self.name
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.content


class PersonalityManager:
    """人格管理器"""
    
    def __init__(self, cha_dir: str = "Cha"):
        self.cha_dir = Path(cha_dir)
        self.cha_dir.mkdir(exist_ok=True)
        self.personalities: Dict[str, Personality] = {}
        self.current_personality: Optional[str] = None
        self.load_all_personalities()
    
    def load_all_personalities(self) -> None:
        """加载所有人格文件"""
        self.personalities = {}
        
        if not self.cha_dir.exists():
            self.cha_dir.mkdir(exist_ok=True)
            return
        
        # 查找所有.md文件
        md_files = list(self.cha_dir.glob("*.md"))
        
        if not md_files:
            # 创建默认人格
            self._create_default_personality()
            return
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                name = file_path.stem  # 文件名（不含扩展名）
                personality = Personality(name, str(file_path), content)
                self.personalities[name.lower()] = personality
                # 优先将xigua_doctor设为默认人格
                if name.lower() == "xigua_doctor":
                    self.current_personality = "xigua_doctor"
                elif self.current_personality is None:
                    self.current_personality = name.lower()
            except Exception as e:
                print(f"[警告] 加载人格文件失败 {file_path}: {e}")
        
        # 如果没有成功加载任何人格，创建默认
        if not self.personalities:
            self._create_default_personality()
    
    def _create_default_personality(self) -> None:
        """创建默认人格"""
        default_content = """# 默认助手

你是一个AI助手，名为智能AI助手
你擅长中文和英文对话，能够回答用户的各种问题。
你的回答应该简洁、准确、有帮助。
"""
        file_path = self.cha_dir / "default.md"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
            
            personality = Personality("default", str(file_path), default_content)
            self.personalities["default"] = personality
            self.current_personality = "default"
        except Exception as e:
            print(f"[警告] 创建默认人格失败: {e}")
    
    def get_personality(self, name: str) -> Optional[Personality]:
        """获取指定人格"""
        return self.personalities.get(name.lower())
    
    def get_current_personality(self) -> Optional[Personality]:
        """获取当前人格"""
        if self.current_personality is None:
            return None
        return self.personalities.get(self.current_personality)
    
    def switch_personality(self, name: str) -> bool:
        """
        切换到指定人格
        
        Args:
            name: 人格名称（文件名，不含扩展名）
        
        Returns:
            是否切换成功
        """
        name_lower = name.lower()
        if name_lower in self.personalities:
            self.current_personality = name_lower
            return True
        
        # 尝试重新加载（可能是新添加的文件）
        self.load_all_personalities()
        
        if name_lower in self.personalities:
            self.current_personality = name_lower
            return True
        
        return False
    
    def list_personalities(self) -> List[Personality]:
        """列出所有可用人格"""
        return list(self.personalities.values())
    
    def get_personality_names(self) -> List[str]:
        """获取所有人格名称"""
        return list(self.personalities.keys())
    
    def get_current_name(self) -> str:
        """获取当前人格名称"""
        if self.current_personality:
            return self.current_personality
        return "default"
    
    def reload(self) -> None:
        """重新加载所有人格文件"""
        self.load_all_personalities()
    
    def create_personality(self, name: str, content: str) -> bool:
        """
        创建新的人格文件
        
        Args:
            name: 人格名称
            content: 人格内容
        
        Returns:
            是否创建成功
        """
        file_path = self.cha_dir / f"{name}.md"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            personality = Personality(name, str(file_path), content)
            self.personalities[name.lower()] = personality
            return True
        except Exception as e:
            print(f"[错误] 创建人格文件失败: {e}")
            return False
    
    def delete_personality(self, name: str) -> bool:
        """
        删除人格文件
        
        Args:
            name: 人格名称
        
        Returns:
            是否删除成功
        """
        name_lower = name.lower()
        if name_lower not in self.personalities:
            return False
        
        # 不能删除默认人格
        if name_lower == "default" and len(self.personalities) == 1:
            print("[警告] 不能删除唯一的默认人格")
            return False
        
        personality = self.personalities[name_lower]
        try:
            if os.path.exists(personality.file_path):
                os.remove(personality.file_path)
            
            del self.personalities[name_lower]
            
            # 如果删除的是当前人格，切换到其他人格
            if self.current_personality == name_lower:
                self.current_personality = next(iter(self.personalities.keys()), None)
            
            return True
        except Exception as e:
            print(f"[错误] 删除人格文件失败: {e}")
            return False


# 全局人格管理器实例
personality_manager = PersonalityManager()
