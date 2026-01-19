"""知乎日报平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform


class ZhihuDailyPlatform(BasePlatform):
    """知乎日报平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "zhihu-daily"
        self.title = "知乎日报"
        self.type = "推荐榜"
        self.description = "每天三次，每次七分钟"
        self.link = "https://daily.zhihu.com/"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://daily.zhihu.com/api/4/news/latest"
        
        result = await self.http_client.get(
            url=url,
            headers={
                "Referer": "https://daily.zhihu.com/api/4/news/latest",
                "Host": "daily.zhihu.com",
            }
        )
        
        list_data = [item for item in result.get("stories", []) if item.get("type") == 0]
        
        return [
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "cover": item.get("images", [""])[0] if item.get("images") else "",
                "author": item.get("hint", ""),
                "hot": None,
                "timestamp": None,
                "url": item.get("url", ""),
                "mobileUrl": item.get("url", ""),
            }
            for item in list_data
        ]
