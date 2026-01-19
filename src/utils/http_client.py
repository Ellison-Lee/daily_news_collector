"""HTTP 客户端封装"""

import asyncio
import hashlib
import json
import os
from typing import Dict, Optional, Any
from urllib.parse import urlencode

import aiohttp
import chardet
from aiohttp import ClientTimeout

from dotenv import load_dotenv

load_dotenv()

# 默认请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))


class HTTPClient:
    """异步 HTTP 客户端"""
    
    def __init__(self):
        self.timeout = ClientTimeout(total=REQUEST_TIMEOUT)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=DEFAULT_HEADERS
            )
        return self.session
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _generate_cache_key(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> str:
        """生成缓存键"""
        key_data = {
            "url": url,
            "params": params or {},
            "headers": {k: v for k, v in (headers or {}).items() if k.lower() not in ["cookie", "authorization"]}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        response_type: str = "json",
        retries: int = MAX_RETRIES,
        **kwargs
    ) -> Any:
        """GET 请求"""
        session = await self._get_session()
        
        # 合并请求头
        request_headers = {**DEFAULT_HEADERS}
        if headers:
            request_headers.update(headers)
        
        # 如果kwargs中有timeout，使用它；否则使用session的默认timeout
        request_timeout = kwargs.pop('timeout', None)
        
        for attempt in range(retries):
            try:
                async with session.get(url, params=params, headers=request_headers, timeout=request_timeout, **kwargs) as response:
                    response.raise_for_status()
                    
                    if response_type == "json":
                        # 检查 Content-Type，如果不是 JSON 则返回文本
                        content_type = response.headers.get("Content-Type", "").lower()
                        if "application/json" not in content_type and "text/json" not in content_type:
                            # 尝试解析为 JSON
                            text = await response.text()
                            if not text or not text.strip():
                                # 空响应，返回空字典
                                return {}
                            try:
                                import json
                                return json.loads(text)
                            except json.JSONDecodeError:
                                # JSON解析失败，返回空字典而不是抛出异常
                                return {}
                        try:
                            return await response.json()
                        except Exception:
                            # JSON解析失败，尝试从文本解析
                            text = await response.text()
                            if not text or not text.strip():
                                return {}
                            try:
                                import json
                                return json.loads(text)
                            except json.JSONDecodeError:
                                return {}
                    elif response_type == "text":
                        # 处理编码
                        content = await response.read()
                        # 尝试解码 brotli
                        try:
                            import brotli
                            content = brotli.decompress(content)
                        except (ImportError, Exception):
                            pass
                        # 优先使用UTF-8，如果检测到其他编码则使用检测结果，但始终使用errors='replace'避免解码失败
                        try:
                            encoding = chardet.detect(content)["encoding"] or "utf-8"
                            # 如果检测到的编码不可靠，强制使用UTF-8
                            if encoding and encoding.lower() not in ['utf-8', 'utf8', 'ascii']:
                                # 对于非UTF-8编码，先尝试UTF-8，失败再使用检测的编码
                                try:
                                    return content.decode('utf-8', errors='replace')
                                except Exception:
                                    return content.decode(encoding, errors='replace')
                            else:
                                return content.decode(encoding or 'utf-8', errors='replace')
                        except Exception:
                            # 如果chardet失败，直接使用UTF-8
                            return content.decode('utf-8', errors='replace')
                    elif response_type == "bytes":
                        return await response.read()
                    else:
                        return await response.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指数退避
        
        raise Exception(f"请求失败，已重试 {retries} 次")
    
    async def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        retries: int = MAX_RETRIES,
        **kwargs
    ) -> Any:
        """POST 请求"""
        session = await self._get_session()
        
        # 合并请求头
        request_headers = {**DEFAULT_HEADERS}
        if headers:
            request_headers.update(headers)
        
        for attempt in range(retries):
            try:
                async with session.post(
                    url,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    **kwargs
                ) as response:
                    response.raise_for_status()
                    try:
                        return await response.json()
                    except Exception:
                        # JSON解析失败，尝试从文本解析
                        text = await response.text()
                        if not text or not text.strip():
                            return {}
                        try:
                            import json
                            return json.loads(text)
                        except json.JSONDecodeError:
                            return {}
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"请求失败，已重试 {retries} 次")
