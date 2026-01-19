"""HTML 爬虫采集器"""

import re
from typing import Dict, List, Optional, Any

from bs4 import BeautifulSoup
from parsel import Selector

from .base import BaseCollector
from ..utils.http_client import HTTPClient
from ..cache.cache_manager import CacheManager


class HTMLCollector(BaseCollector):
    """HTML 爬虫采集器"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None, http_client: Optional[HTTPClient] = None):
        """初始化 HTML 采集器"""
        super().__init__(cache_manager, http_client)
    
    async def fetch(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        selector: Optional[str] = None,
        parser: str = "html.parser",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取 HTML 数据"""
        html = await self.http_client.get(
            url=url,
            params=params,
            headers=headers,
            response_type="text",
            **kwargs
        )
        
        # 如果提供了 selector，使用 parsel
        if selector:
            sel = Selector(text=html)
            return sel.css(selector).getall()
        
        # 否则使用 BeautifulSoup
        soup = BeautifulSoup(html, parser)
        return [soup]
    
    def extract_json_from_html(self, html: str, pattern: str) -> Optional[Dict]:
        """从 HTML 中提取 JSON 数据"""
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                import json
                return json.loads(match.group(1))
            except Exception:
                pass
        return None
