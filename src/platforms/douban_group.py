"""豆瓣讨论小组平台"""

import re
from typing import Dict, List, Any

from bs4 import BeautifulSoup

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class DoubanGroupPlatform(BasePlatform):
    """豆瓣讨论小组平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "douban-group"
        self.title = "豆瓣讨论"
        self.type = "讨论精选"
        self.link = "https://www.douban.com/group/explore"
        self.category = "娱乐内容"
    
    def _get_numbers(self, text: str) -> int:
        """提取数字"""
        if not text:
            return 100000000
        match = re.search(r'\d+', text)
        return int(match.group(0)) if match else 100000000
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://www.douban.com/group/explore"
        
        html = await self.http_client.get(url=url, response_type="text")
        
        soup = BeautifulSoup(html, "html.parser")
        list_dom = soup.select(".article .channel-item")
        
        return [
            {
                "id": self._get_numbers(item.select_one("h3 a").get("href", "") if item.select_one("h3 a") else ""),
                "title": item.select_one("h3 a").text.strip() if item.select_one("h3 a") else "",
                "cover": item.select_one(".pic-wrap img").get("src", "") if item.select_one(".pic-wrap img") else "",
                "desc": item.select_one(".block p").text.strip() if item.select_one(".block p") else "",
                "timestamp": get_time(item.select_one("span.pubtime").text.strip() if item.select_one("span.pubtime") else ""),
                "hot": 0,
                "url": item.select_one("h3 a").get("href", "") if item.select_one("h3 a") else "",
                "mobileUrl": f"https://m.douban.com/group/topic/{self._get_numbers(item.select_one('h3 a').get('href', '') if item.select_one('h3 a') else '')}/",
            }
            for item in list_dom
        ]
