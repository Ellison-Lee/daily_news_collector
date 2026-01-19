"""今日头条平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class ToutiaoPlatform(BasePlatform):
    """今日头条平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "toutiao"
        self.title = "今日头条"
        self.type = "热榜"
        self.link = "https://www.toutiao.com/"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        
        result = await self.http_client.get(url=url)
        
        list_data = result.get("data", [])
        
        return [
            {
                "id": item.get("ClusterIdStr", ""),
                "title": item.get("Title", ""),
                "cover": item.get("Image", {}).get("url", ""),
                "timestamp": get_time(item.get("ClusterIdStr")),
                "hot": int(item.get("HotValue", 0)),
                "url": f"https://www.toutiao.com/trending/{item.get('ClusterIdStr', '')}/",
                "mobileUrl": f"https://api.toutiaoapi.com/feoffline/amos_land/new/html/main/index.html?topic_id={item.get('ClusterIdStr', '')}",
            }
            for item in list_data
        ]
