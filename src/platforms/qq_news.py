"""腾讯新闻平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class QqNewsPlatform(BasePlatform):
    """腾讯新闻平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "qq-news"
        self.title = "腾讯新闻"
        self.type = "热点榜"
        self.link = "https://news.qq.com/"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://r.inews.qq.com/gw/event/hot_ranking_list?page_size=50"
        
        result = await self.http_client.get(url=url)
        
        idlist = result.get("idlist", [])
        list_data = idlist[0].get("newslist", [])[1:] if idlist and isinstance(idlist, list) and len(idlist) > 0 else []
        
        return [
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "desc": item.get("abstract", ""),
                "cover": item.get("miniProShareImage", ""),
                "author": item.get("source", ""),
                "hot": item.get("hotEvent", {}).get("hotScore", 0),
                "timestamp": get_time(item.get("timestamp")),
                "url": f"https://new.qq.com/rain/a/{item.get('id', '')}",
                "mobileUrl": f"https://view.inews.qq.com/k/{item.get('id', '')}",
            }
            for item in list_data
        ]
