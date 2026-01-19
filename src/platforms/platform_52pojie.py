"""吾爱破解平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..collectors.rss_collector import RSSCollector
from ..utils.time_utils import get_time


class Platform52pojie(BasePlatform):
    """吾爱破解平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "52pojie"
        self.title = "吾爱破解"
        self.type = "最新精华"
        self.link = "https://www.52pojie.cn/"
        self.category = "技术社区"
    
    async def fetch(self, type: str = "digest", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://www.52pojie.cn/forum.php?mod=guide&view={type}&rss=1"
        
        # 获取 RSS 内容并处理 GBK 编码
        html = await self.http_client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36",
            },
            response_type="bytes"
        )
        
        # 尝试解码 GBK
        try:
            content = html.decode("gbk")
        except:
            content = html.decode("utf-8", errors="ignore")
        
        rss_collector = RSSCollector(self.cache_manager, self.http_client)
        items = await rss_collector.fetch(rss_content=content)
        
        return [
            {
                "id": item.get("id", index),
                "title": item.get("title", ""),
                "desc": item.get("desc", "").strip() if item.get("desc") else "",
                "author": item.get("author", ""),
                "timestamp": get_time(item.get("pubDate")),
                "hot": None,
                "url": item.get("url", ""),
                "mobileUrl": item.get("url", ""),
            }
            for index, item in enumerate(items)
        ]
