"""RSS 解析采集器"""

from typing import Dict, List, Optional, Any

import feedparser

from .base import BaseCollector
from ..utils.http_client import HTTPClient
from ..cache.cache_manager import CacheManager


class RSSCollector(BaseCollector):
    """RSS 解析采集器"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None, http_client: Optional[HTTPClient] = None):
        """初始化 RSS 采集器"""
        super().__init__(cache_manager, http_client)
    
    async def fetch(
        self,
        url: Optional[str] = None,
        rss_content: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取 RSS 数据"""
        if rss_content:
            feed = feedparser.parse(rss_content)
        elif url:
            # 获取 RSS 内容
            content = await self.http_client.get(url=url, response_type="text", **kwargs)
            feed = feedparser.parse(content)
        else:
            raise ValueError("必须提供 url 或 rss_content")
        
        items = []
        for entry in feed.entries:
            items.append({
                "id": entry.get("id", entry.get("link", "")),
                "title": entry.get("title", ""),
                "desc": entry.get("summary", ""),
                "author": entry.get("author", ""),
                "url": entry.get("link", ""),
                "mobileUrl": entry.get("link", ""),
                "timestamp": None,  # RSS 通常没有热度值
                "hot": None,
            })
        
        return items
