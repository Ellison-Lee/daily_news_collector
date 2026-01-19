"""爱范儿平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class IfanrPlatform(BasePlatform):
    """爱范儿平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "ifanr"
        self.title = "爱范儿"
        self.type = "快讯"
        self.description = "15秒了解全球新鲜事"
        self.link = "https://www.ifanr.com/digest/"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://sso.ifanr.com/api/v5/wp/buzz/?limit=20&offset=0"
        
        result = await self.http_client.get(url=url)
        
        list_data = result.get("objects", [])
        
        return [
            {
                "id": item.get("id", ""),
                "title": item.get("post_title", ""),
                "desc": item.get("post_content", ""),
                "timestamp": get_time(item.get("created_at")),
                "hot": item.get("like_count") or item.get("comment_count", 0),
                "url": item.get("buzz_original_url") or f"https://www.ifanr.com/{item.get('post_id', '')}",
                "mobileUrl": item.get("buzz_original_url") or f"https://www.ifanr.com/digest/{item.get('post_id', '')}",
            }
            for item in list_data
        ]
