"""微信读书平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class WereadPlatform(BasePlatform):
    """微信读书平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "weread"
        self.title = "微信读书"
        self.type = "飙升榜"
        self.link = "https://weread.qq.com/"
        self.category = "娱乐内容"
    
    async def fetch(self, type: str = "rising", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://weread.qq.com/web/bookListInCategory/{type}?rank=1"
        
        try:
            result = await self.http_client.get(
                url=url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }
            )
        except Exception as e:
            return []
        
        # 尝试多种数据路径
        list_data = None
        
        # 路径1: result.data.books
        if result.get("data") and isinstance(result.get("data"), dict):
            list_data = result.get("data").get("books", [])
        
        # 路径2: result.books (如果路径1失败)
        if not list_data:
            list_data = result.get("books", [])
        
        # 如果还是没有数据，尝试直接获取result中的列表
        if not list_data and isinstance(result, dict):
            # 查找包含列表的键
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    list_data = value
                    break
        
        if not list_data:
            list_data = []
        
        return [
            {
                "id": item.get("bookInfo", {}).get("bookId", ""),
                "title": item.get("bookInfo", {}).get("title", ""),
                "author": item.get("bookInfo", {}).get("author", ""),
                "desc": item.get("bookInfo", {}).get("intro", ""),
                "cover": item.get("bookInfo", {}).get("cover", "").replace("s_", "t9_"),
                "timestamp": get_time(item.get("bookInfo", {}).get("publishTime")),
                "hot": item.get("readingCount", 0),
                "url": f"https://weread.qq.com/web/bookDetail/{item.get('bookInfo', {}).get('bookId', '')}",
                "mobileUrl": f"https://weread.qq.com/web/bookDetail/{item.get('bookInfo', {}).get('bookId', '')}",
            }
            for item in list_data
        ]
