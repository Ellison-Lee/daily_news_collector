"""豆瓣电影平台"""

import re
from typing import Dict, List, Any

from bs4 import BeautifulSoup

from .base_platform import BasePlatform


class DoubanMoviePlatform(BasePlatform):
    """豆瓣电影平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "douban-movie"
        self.title = "豆瓣电影"
        self.type = "新片榜"
        self.link = "https://movie.douban.com/chart"
        self.category = "娱乐内容"
    
    def _get_numbers(self, text: str) -> int:
        """提取数字"""
        if not text:
            return 0
        match = re.search(r'\d+', text)
        return int(match.group(0)) if match else 0
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://movie.douban.com/chart/"
        
        html = await self.http_client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            },
            response_type="text"
        )
        
        soup = BeautifulSoup(html, "html.parser")
        list_dom = soup.select(".article tr.item")
        
        return [
            {
                "id": self._get_numbers(item.select_one("a").get("href", "") if item.select_one("a") else ""),
                "title": f"【{item.select_one('.rating_nums').text if item.select_one('.rating_nums') else '0.0'}】{item.select_one('a').get('title', '') if item.select_one('a') else ''}",
                "cover": item.select_one("img").get("src", "") if item.select_one("img") else "",
                "desc": item.select_one("p.pl").text if item.select_one("p.pl") else "",
                "timestamp": None,
                "hot": self._get_numbers(item.select_one("span.pl").text if item.select_one("span.pl") else ""),
                "url": item.select_one("a").get("href", "") if item.select_one("a") else "",
                "mobileUrl": f"https://m.douban.com/movie/subject/{self._get_numbers(item.select_one('a').get('href', '') if item.select_one('a') else '')}/",
            }
            for item in list_dom
        ]
