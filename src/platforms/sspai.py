"""少数派平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class SspaiPlatform(BasePlatform):
    """少数派平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "sspai"
        self.title = "少数派"
        self.type = "热榜"
        self.link = "https://sspai.com/"
        self.category = "生活消费"
    
    async def fetch(self, type: str = "热门文章", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://sspai.com/api/v1/article/tag/page/get?limit=40&tag={type}"
        
        result = await self.http_client.get(url=url)
        
        # 处理可能的列表或字典响应
        data = result.get("data", {})
        if isinstance(data, list):
            list_data = data
        else:
            list_data = data.get("data", [])
        
        if not isinstance(list_data, list):
            return []
        
        return [
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "desc": item.get("summary", ""),
                "cover": item.get("banner", ""),
                "author": item.get("author", {}).get("nickname", "") if isinstance(item.get("author"), dict) else "",
                "timestamp": get_time(item.get("released_time")),
                "hot": item.get("like_count", 0),
                "url": f"https://sspai.com/post/{item.get('id', '')}",
                "mobileUrl": f"https://sspai.com/post/{item.get('id', '')}",
            }
            for item in list_data if isinstance(item, dict)
        ]
