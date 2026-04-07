"""
更多 LLM 提供商支持
"""

from typing import Optional
import os
from .llm_adapter import LLMAdapter


class ZAIAdapter(LLMAdapter):
    """z.ai/GLM API adapter"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "glm-4",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    ):
        self.api_key = api_key or os.getenv("ZAI_API_KEY")
        if not self.api_key:
            raise ValueError("z.ai API key not found. Set ZAI_API_KEY environment variable.")
        
        self.model = model
        self.base_url = base_url
        # z.ai 使用 OpenAI 兼容接口
        import openai
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


class KimiAdapter(LLMAdapter):
    """Kimi/Moonshot API adapter"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "moonshot-v1-8k",
        base_url: str = "https://api.moonshot.cn/v1"
    ):
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        if not self.api_key:
            raise ValueError("Kimi API key not found. Set KIMI_API_KEY environment variable.")
        
        self.model = model
        self.base_url = base_url
        # Kimi 使用 OpenAI 兼容接口
        import openai
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


class MiniMaxAdapter(LLMAdapter):
    """MiniMax API adapter"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "abab6.5-chat",
        group_id: Optional[str] = None,
        base_url: str = "https://api.minimax.chat/v1"
    ):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.group_id = group_id or os.getenv("MINIMAX_GROUP_ID")
        
        if not self.api_key or not self.group_id:
            raise ValueError(
                "MiniMax API key or Group ID not found. "
                "Set MINIMAX_API_KEY and MINIMAX_GROUP_ID environment variables."
            )
        
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        # MiniMax 有特殊的 API 格式
        import requests
        
        url = f"{self.base_url}/text/chatcompletion{self.group_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]


def get_llm_adapter(provider: str = "openai", **kwargs) -> LLMAdapter:
    """
    Factory function to get LLM adapter
    
    Args:
        provider: LLM 提供商 (openai, anthropic, zai, kimi, minimax)
        **kwargs: 传递给适配器的参数
    
    Returns:
        LLM 适配器实例
    """
    providers = {
        "openai": lambda: __import__('harness.llm_adapter', fromlist=['OpenAIAdapter']).OpenAIAdapter(**kwargs),
        "anthropic": lambda: __import__('harness.llm_adapter', fromlist=['AnthropicAdapter']).AnthropicAdapter(**kwargs),
        "zai": lambda: ZAIAdapter(**kwargs),
        "kimi": lambda: KimiAdapter(**kwargs),
        "minimax": lambda: MiniMaxAdapter(**kwargs),
    }
    
    if provider not in providers:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Supported providers: {list(providers.keys())}"
        )
    
    return providers[provider]()
