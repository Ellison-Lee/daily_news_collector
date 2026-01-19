"""百度平台"""

import re
from typing import Dict, List, Any

from .base_platform import BasePlatform


class BaiduPlatform(BasePlatform):
    """百度平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "baidu"
        self.title = "百度"
        self.type = "热搜榜"
        self.link = "https://top.baidu.com/board"
        self.category = "新闻资讯"
    
    async def fetch(self, type: str = "realtime", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://top.baidu.com/board?tab={type}"
        
        html = await self.http_client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) AppleWebKit/605.1.15",
            },
            response_type="text"
        )
        
        # 正则提取 JSON 数据
        pattern = r'<!--s-data:(.*?)-->'
        match = re.search(pattern, html, re.DOTALL)
        if not match:
            return []
        
        import json
        json_data = json.loads(match.group(1))
        list_data = json_data.get("cards", [{}])[0].get("content", [])
        
        return [
            {
                "id": item.get("index", 0),
                "title": item.get("word", ""),
                "desc": item.get("desc", ""),
                "cover": item.get("img", ""),
                "author": " ".join(item.get("show", [])) if item.get("show") else "",
                "timestamp": 0,
                "hot": int(item.get("hotScore", 0)),
                "url": f"https://www.baidu.com/s?wd={item.get('query', '')}",
                "mobileUrl": item.get("rawUrl", ""),
            }
            for item in list_data
        ]
