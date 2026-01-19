"""IT之家平台"""

import re
from typing import Dict, List, Any

from bs4 import BeautifulSoup

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class IthomePlatform(BasePlatform):
    """IT之家平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "ithome"
        self.title = "IT之家"
        self.type = "热榜"
        self.description = "爱科技，爱这里 - 前沿科技新闻网站"
        self.link = "https://m.ithome.com/rankm/"
        self.category = "新闻资讯"
    
    def _replace_link(self, url: str, get_id: bool = False) -> str:
        """链接处理"""
        match = re.search(r'[html|live]/(\d+)\.htm', url)
        if match and match.group(1):
            if get_id:
                return match.group(1)
            else:
                article_id = match.group(1)
                return f"https://www.ithome.com/0/{article_id[:3]}/{article_id[3:]}.htm"
        return url
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://m.ithome.com/rankm/"
        
        html = await self.http_client.get(url=url, response_type="text")
        
        soup = BeautifulSoup(html, "html.parser")
        list_dom = soup.select(".rank-box .placeholder")
        
        return [
            {
                "id": int(self._replace_link(item.select_one("a").get("href", ""), True)) if item.select_one("a") else 100000,
                "title": item.select_one(".plc-title").text.strip() if item.select_one(".plc-title") else "",
                "cover": item.select_one("img").get("data-original", "") if item.select_one("img") else "",
                "timestamp": get_time(item.select_one("span.post-time").text.strip() if item.select_one("span.post-time") else ""),
                "hot": int(re.sub(r'\D', '', item.select_one(".review-num").text if item.select_one(".review-num") else "0")),
                "url": self._replace_link(item.select_one("a").get("href", "")) if item.select_one("a") else "",
                "mobileUrl": self._replace_link(item.select_one("a").get("href", "")) if item.select_one("a") else "",
            }
            for item in list_dom
        ]
