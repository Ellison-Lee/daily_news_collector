"""稀土掘金平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform


class JuejinPlatform(BasePlatform):
    """稀土掘金平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "juejin"
        self.title = "稀土掘金"
        self.type = "文章榜"
        self.link = "https://juejin.cn/hot/articles"
        self.category = "技术社区"
    
    async def fetch(self, type: int = 1, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://api.juejin.cn/content_api/v1/content/article_rank?category_id={type}&type=hot"
        
        result = await self.http_client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
        )
        
        list_data = result.get("data", [])
        
        return [
            {
                "id": item.get("content", {}).get("content_id", ""),
                "title": item.get("content", {}).get("title", ""),
                "author": item.get("author", {}).get("name", ""),
                "hot": item.get("content_counter", {}).get("hot_rank", 0),
                "timestamp": None,
                "url": f"https://juejin.cn/post/{item.get('content', {}).get('content_id', '')}",
                "mobileUrl": f"https://juejin.cn/post/{item.get('content', {}).get('content_id', '')}",
            }
            for item in list_data
        ]
