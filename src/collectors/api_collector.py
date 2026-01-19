"""API 调用采集器"""

from typing import Dict, List, Optional, Any

from .base import BaseCollector
from ..utils.http_client import HTTPClient
from ..cache.cache_manager import CacheManager


class APICollector(BaseCollector):
    """API 调用采集器"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None, http_client: Optional[HTTPClient] = None):
        """初始化 API 采集器"""
        super().__init__(cache_manager, http_client)
    
    async def fetch(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        response_type: str = "json",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取 API 数据"""
        response = await self.http_client.get(
            url=url,
            params=params,
            headers=headers,
            response_type=response_type,
            **kwargs
        )
        return response if isinstance(response, list) else [response]
