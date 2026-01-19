"""微博平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class WeiboPlatform(BasePlatform):
    """微博平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "weibo"
        self.title = "微博"
        self.type = "热搜榜"
        self.description = "实时热点，每分钟更新一次"
        self.link = "https://s.weibo.com/top/summary/"
        self.category = "社交媒体"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://weibo.com/ajax/side/hotSearch"
        
        result = await self.http_client.get(
            url=url,
            headers={
                "Referer": "https://weibo.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
        )
        
        if not result.get("data", {}).get("realtime"):
            return []
        
        list_data = result["data"]["realtime"]
        return [
            {
                "id": item.get("mid") or item.get("word_scheme") or f"weibo-{index}",
                "title": item.get("word") or item.get("word_scheme") or f"热搜{index + 1}",
                "desc": item.get("word_scheme") or f"#{item.get('word', '')}#",
                "timestamp": get_time(item.get("onboard_time")),
                "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                "mobileUrl": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
            }
            for index, item in enumerate(list_data)
        ]
