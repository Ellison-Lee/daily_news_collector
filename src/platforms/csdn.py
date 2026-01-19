"""CSDN 平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class CsdnPlatform(BasePlatform):
    """CSDN 平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "csdn"
        self.title = "CSDN"
        self.type = "排行榜"
        self.description = "专业开发者社区"
        self.link = "https://www.csdn.net/"
        self.category = "技术社区"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=30"
        
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
                "id": item.get("productId", ""),
                "title": item.get("articleTitle", ""),
                "cover": item.get("picList", [""])[0] if item.get("picList") else "",
                "author": item.get("nickName", ""),
                "timestamp": get_time(item.get("period")),
                "hot": int(item.get("hotRankScore", 0)),
                "url": item.get("articleDetailUrl", ""),
                "mobileUrl": item.get("articleDetailUrl", ""),
            }
            for item in list_data if isinstance(item, dict)
        ]
