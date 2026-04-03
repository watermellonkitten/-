"""
Kimi API 调用模块
处理与Kimi API的通信
"""
import json
import time
from typing import List, Dict, Any, Optional, Generator
import urllib.request
import urllib.error


class KimiAPIError(Exception):
    """Kimi API错误"""
    pass


class KimiAPI:
    """Kimi API客户端"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: str = "https://api.moonshot.cn/v1", model: str = "kimi-k2.5"):
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')  # 移除末尾的斜杠
        self.model = model
        self.timeout = 60
    
    def set_api_key(self, api_key: str) -> None:
        """设置API密钥"""
        self.api_key = api_key
    
    def set_api_base(self, api_base: str) -> None:
        """设置API基础URL"""
        self.api_base = api_base.rstrip('/')
    
    def set_model(self, model: str) -> None:
        """设置模型"""
        self.model = model
    
    def get_api_base(self) -> str:
        """获取当前API基础URL"""
        return self.api_base
    
    def _build_url(self, endpoint: str) -> str:
        """
        构建完整URL
        
        Args:
            endpoint: API端点（以/开头）
        
        Returns:
            完整URL
        """
        # 确保endpoint以/开头
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        return f"{self.api_base}{endpoint}"
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            endpoint: API端点
            data: 请求数据
        
        Returns:
            响应数据
        """
        if not self.api_key:
            raise KimiAPIError("API密钥未设置")
        
        url = self._build_url(endpoint)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            error_code = e.code
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('error', {}).get('message', str(e))
                error_code_detail = error_data.get('error', {}).get('code', '')
                if error_code_detail:
                    error_msg = f"[{error_code_detail}] {error_msg}"
            except:
                error_msg = error_body or str(e)
            raise KimiAPIError(f"API请求失败 (HTTP {error_code}): {error_msg}")
        except urllib.error.URLError as e:
            raise KimiAPIError(f"网络错误: {e.reason}")
        except Exception as e:
            raise KimiAPIError(f"请求错误: {str(e)}")
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        thinking: bool = False
    ) -> Generator[str, None, None]:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            stream: 是否流式输出
            temperature: 温度参数
            max_tokens: 最大token数
            thinking: 是否显示思考过程
        
        Yields:
            响应文本片段
        """
        endpoint = "/chat/completions"
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        # 如果启用思考模式，添加相关参数
        if thinking:
            # 注意：实际参数取决于Kimi API是否支持思考模式
            # 这里作为示例，可能需要根据实际API调整
            pass
        
        if not stream:
            # 非流式响应
            response = self._make_request(endpoint, data)
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            yield content
        else:
            # 流式响应
            yield from self._stream_request(endpoint, data)
    
    def _stream_request(self, endpoint: str, data: Dict[str, Any]) -> Generator[str, None, None]:
        """
        发送流式请求
        
        Args:
            endpoint: API端点
            data: 请求数据
        
        Yields:
            响应文本片段
        """
        if not self.api_key:
            raise KimiAPIError("API密钥未设置")
        
        url = self._build_url(endpoint)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                buffer = b""
                while True:
                    chunk = response.read(1024)
                    if not chunk:
                        break
                    buffer += chunk
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        try:
                            line_str = line.decode('utf-8').strip()
                        except UnicodeDecodeError:
                            continue
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str == '[DONE]':
                                return
                            try:
                                data_json = json.loads(data_str)
                                delta = data_json.get('choices', [{}])[0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            error_code = e.code
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('error', {}).get('message', error_body)
                error_code_detail = error_data.get('error', {}).get('code', '')
                if error_code_detail:
                    error_msg = f"[{error_code_detail}] {error_msg}"
            except:
                error_msg = error_body or str(e)
            raise KimiAPIError(f"流式请求失败 (HTTP {error_code}): {error_msg}")
        except Exception as e:
            raise KimiAPIError(f"流式请求错误: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """
        验证API密钥是否有效
        
        Returns:
            是否有效
        """
        if not self.api_key:
            return False
        
        try:
            # 发送一个简单的请求来验证
            messages = [{"role": "user", "content": "Hi"}]
            list(self.chat_completion(messages, stream=False, max_tokens=5))
            return True
        except Exception:
            return False
    
    def get_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            模型ID列表
        """
        if not self.api_key:
            return []
        
        try:
            url = self._build_url("/models")
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
                models = data.get('data', [])
                return [model.get('id') for model in models if model.get('id')]
        except Exception:
            return []


# 全局Kimi API实例
kimi_api = KimiAPI()
