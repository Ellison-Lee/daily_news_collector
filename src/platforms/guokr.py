"""果壳平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class GuokrPlatform(BasePlatform):
    """果壳平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "guokr"
        self.title = "果壳"
        self.type = "热门文章"
        self.description = "科技有意思"
        self.link = "https://www.guokr.com/"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://www.guokr.com/beta/proxy/science_api/articles?limit=30"
        
        try:
            result = await self.http_client.get(
                url=url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }
            )
            
            # 处理可能的列表或字典响应
            if isinstance(result, list):
                list_data = result
            else:
                list_data = result.get("data", []) if isinstance(result, dict) else []
            
            if not isinstance(list_data, list):
                return []
            
            return [
                {
                    "id": str(item.get("id", "")),
                    "title": item.get("title", ""),
                    "desc": item.get("summary", ""),
                    "cover": item.get("small_image", ""),
                    "author": item.get("author", {}).get("nickname", "") if isinstance(item.get("author"), dict) else "",
                    "hot": None,
                    "timestamp": get_time(item.get("date_modified")),
                    "url": f"https://www.guokr.com/article/{item.get('id', '')}",
                    "mobileUrl": f"https://m.guokr.com/article/{item.get('id', '')}",
                }
                for item in list_data if isinstance(item, dict)
            ]
        except Exception:
            return []
