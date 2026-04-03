"""
会话管理模块
管理对话会话的创建、保存、加载和切换
"""
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ChatSession:
    """聊天会话类"""
    
    def __init__(self, session_id: int, name: str = "", personality: str = "default"):
        self.session_id = session_id
        self.name = name or f"会话_{session_id}"
        self.personality = personality
        self.messages: List[Dict[str, Any]] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息到会话"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "personality": self.personality,
            "messages": self.messages,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """从字典创建会话"""
        session = cls(
            session_id=data.get("session_id", 0),
            name=data.get("name", ""),
            personality=data.get("personality", "default")
        )
        session.messages = data.get("messages", [])
        session.created_at = data.get("created_at", datetime.now().isoformat())
        session.updated_at = data.get("updated_at", datetime.now().isoformat())
        return session
    
    def get_display_info(self) -> str:
        """获取显示信息"""
        msg_count = len(self.messages)
        time_str = datetime.fromisoformat(self.updated_at).strftime("%m-%d %H:%M")
        return f"[{self.session_id}] {self.name} ({msg_count}条消息) - 更新于 {time_str}"


class SessionManager:
    """会话管理器"""
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.sessions: Dict[int, ChatSession] = {}
        self.current_session_id: Optional[int] = None
        self.next_session_id = 0
        self.load_all_sessions()
    
    def load_all_sessions(self) -> None:
        """加载所有会话"""
        if not self.memory_dir.exists():
            return
        
        for file_path in self.memory_dir.glob("session_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = ChatSession.from_dict(data)
                    self.sessions[session.session_id] = session
                    # 更新下一个会话ID
                    if session.session_id >= self.next_session_id:
                        self.next_session_id = session.session_id + 1
            except Exception as e:
                print(f"[警告] 加载会话文件失败 {file_path}: {e}")
        
        # 如果没有会话，创建一个默认会话
        if not self.sessions:
            self.create_session("默认会话")
        
        # 设置当前会话为最新的
        if self.sessions:
            self.current_session_id = max(self.sessions.keys())
    
    def create_session(self, name: str = "", personality: str = "default") -> ChatSession:
        """创建新会话"""
        session_id = self.next_session_id
        self.next_session_id += 1
        
        session = ChatSession(session_id, name or f"会话_{session_id}", personality)
        self.sessions[session_id] = session
        self.current_session_id = session_id
        self.save_session(session_id)
        return session
    
    def get_session(self, session_id: int) -> Optional[ChatSession]:
        """获取指定会话"""
        return self.sessions.get(session_id)
    
    def get_current_session(self) -> Optional[ChatSession]:
        """获取当前会话"""
        if self.current_session_id is None:
            return None
        return self.sessions.get(self.current_session_id)
    
    def switch_session(self, session_id: int) -> bool:
        """切换到指定会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            return True
        return False
    
    def save_session(self, session_id: int) -> bool:
        """保存指定会话到文件"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        file_path = self.memory_dir / f"session_{session_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[错误] 保存会话失败: {e}")
            return False
    
    def save_current_session(self) -> bool:
        """保存当前会话"""
        if self.current_session_id is not None:
            return self.save_session(self.current_session_id)
        return False
    
    def save_all_sessions(self) -> None:
        """保存所有会话"""
        for session_id in self.sessions:
            self.save_session(session_id)
    
    def delete_session(self, session_id: int) -> bool:
        """删除会话"""
        if session_id not in self.sessions:
            return False
        
        # 删除文件
        file_path = self.memory_dir / f"session_{session_id}.json"
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"[警告] 删除会话文件失败: {e}")
        
        # 从内存中移除
        del self.sessions[session_id]
        
        # 如果删除的是当前会话，切换到其他会话
        if self.current_session_id == session_id:
            if self.sessions:
                self.current_session_id = max(self.sessions.keys())
            else:
                self.current_session_id = None
                self.create_session("默认会话")
        
        return True
    
    def list_sessions(self) -> List[ChatSession]:
        """列出所有会话"""
        return sorted(self.sessions.values(), key=lambda s: s.session_id)
    
    def get_session_count(self) -> int:
        """获取会话数量"""
        return len(self.sessions)
    
    def export_session(self, session_id: int, output_path: str) -> bool:
        """
        导出会话到文本文件
        
        Args:
            session_id: 会话ID
            output_path: 输出文件路径
        
        Returns:
            是否成功
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"会话名称: {session.name}\n")
                f.write(f"会话ID: {session.session_id}\n")
                f.write(f"人格: {session.personality}\n")
                f.write(f"创建时间: {session.created_at}\n")
                f.write(f"更新时间: {session.updated_at}\n")
                f.write("=" * 50 + "\n\n")
                
                for msg in session.messages:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    timestamp = msg.get("timestamp", "")
                    
                    if role == "user":
                        f.write(f"[用户] {timestamp}\n")
                    elif role == "assistant":
                        f.write(f"[AI] {timestamp}\n")
                    elif role == "system":
                        f.write(f"[系统] {timestamp}\n")
                    else:
                        f.write(f"[{role}] {timestamp}\n")
                    
                    f.write(f"{content}\n\n")
            
            return True
        except Exception as e:
            print(f"[错误] 导出会话失败: {e}")
            return False
    
    def rename_session(self, session_id: int, new_name: str) -> bool:
        """重命名会话"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.name = new_name
        session.updated_at = datetime.now().isoformat()
        self.save_session(session_id)
        return True


# 全局会话管理器实例
session_manager = SessionManager()
