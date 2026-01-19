"""网易新闻平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class NeteaseNewsPlatform(BasePlatform):
    """网易新闻平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "netease-news"
        self.title = "网易新闻"
        self.type = "热点榜"
        self.link = "https://m.163.com/hot"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://m.163.com/fe/api/hot/news/flow"
        
        result = await self.http_client.get(url=url)
        
        list_data = result.get("data", {}).get("list", [])
        
        return [
            {
                "id": item.get("docid", ""),
                "title": item.get("title", ""),
                "cover": item.get("imgsrc", ""),
                "author": item.get("source", ""),
                "hot": None,
                "timestamp": get_time(item.get("ptime")),
                "url": f"https://www.163.com/dy/article/{item.get('docid', '')}.html",
                "mobileUrl": f"https://m.163.com/dy/article/{item.get('docid', '')}.html",
            }
            for item in list_data
        ]
