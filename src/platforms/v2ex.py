"""V2EX 平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform


class V2exPlatform(BasePlatform):
    """V2EX 平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "v2ex"
        self.title = "V2EX"
        self.type = "主题榜"
        self.link = "https://www.v2ex.com/"
        self.category = "技术社区"
    
    async def fetch(self, type: str = "hot", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://www.v2ex.com/api/topics/{type}.json"
        
        result = await self.http_client.get(url=url)
        
        return [
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "desc": item.get("content", ""),
                "author": item.get("member", {}).get("username", ""),
                "timestamp": None,
                "hot": item.get("replies", 0),
                "url": item.get("url", ""),
                "mobileUrl": item.get("url", ""),
            }
            for item in result
        ]
