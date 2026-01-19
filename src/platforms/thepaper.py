"""澎湃新闻平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class ThepaperPlatform(BasePlatform):
    """澎湃新闻平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "thepaper"
        self.title = "澎湃新闻"
        self.type = "热榜"
        self.link = "https://www.thepaper.cn/"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar"
        
        result = await self.http_client.get(url=url)
        
        list_data = result.get("data", {}).get("hotNews", [])
        
        return [
            {
                "id": item.get("contId", ""),
                "title": item.get("name", ""),
                "cover": item.get("pic", ""),
                "hot": int(item.get("praiseTimes", 0)),
                "timestamp": get_time(item.get("pubTimeLong")),
                "url": f"https://www.thepaper.cn/newsDetail_forward_{item.get('contId', '')}",
                "mobileUrl": f"https://m.thepaper.cn/newsDetail_forward_{item.get('contId', '')}",
            }
            for item in list_data
        ]
