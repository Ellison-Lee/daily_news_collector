"""简书平台"""

import re
from typing import Dict, List, Any

from bs4 import BeautifulSoup

from .base_platform import BasePlatform


class JianshuPlatform(BasePlatform):
    """简书平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "jianshu"
        self.title = "简书"
        self.type = "热门推荐"
        self.description = "一个优质的创作社区"
        self.link = "https://www.jianshu.com/"
        self.category = "新闻资讯"
    
    def _get_id(self, url: str) -> str:
        """获取 ID"""
        if not url:
            return "undefined"
        match = re.search(r'([^/]+)$', url)
        return match.group(1) if match else "undefined"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://www.jianshu.com/"
        
        html = await self.http_client.get(
            url=url,
            headers={"Referer": "https://www.jianshu.com"},
            response_type="text"
        )
        
        soup = BeautifulSoup(html, "html.parser")
        list_dom = soup.select("ul.note-list li")
        
        return [
            {
                "id": self._get_id(item.select_one("a").get("href", "") if item.select_one("a") else ""),
                "title": item.select_one("a.title").text.strip() if item.select_one("a.title") else "",
                "cover": item.select_one("img").get("src", "") if item.select_one("img") else "",
                "desc": item.select_one("p.abstract").text.strip() if item.select_one("p.abstract") else "",
                "author": item.select_one("a.nickname").text.strip() if item.select_one("a.nickname") else "",
                "hot": None,
                "timestamp": None,
                "url": f"https://www.jianshu.com{item.select_one('a').get('href', '')}" if item.select_one("a") else "",
                "mobileUrl": f"https://www.jianshu.com{item.select_one('a').get('href', '')}" if item.select_one("a") else "",
            }
            for item in list_dom
        ]
