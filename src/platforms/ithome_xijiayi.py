"""IT之家「喜加一」平台"""

from typing import Dict, List, Any

from bs4 import BeautifulSoup

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class IthomeXijiayiPlatform(BasePlatform):
    """IT之家「喜加一」平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "ithome-xijiayi"
        self.title = "IT之家「喜加一」"
        self.type = "最新动态"
        self.link = "https://www.ithome.com/"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        try:
            url = "https://www.ithome.com/zt/xijiayi/"
            
            html = await self.http_client.get(
                url=url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
                response_type="text"
            )
            
            soup = BeautifulSoup(html, "html.parser")
            articles = soup.select("div.post-list li")
            
            result = []
            for article in articles:
                title_elem = article.select_one("h2 a")
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                article_url = title_elem.get("href", "")
                if article_url and not article_url.startswith("http"):
                    article_url = f"https://www.ithome.com{article_url}"
                
                time_elem = article.select_one("span.post-time")
                time_str = time_elem.get_text(strip=True) if time_elem else ""
                
                result.append({
                    "id": article_url.split("/")[-1].replace(".html", "") if article_url else "",
                    "title": title,
                    "desc": None,
                    "author": None,
                    "hot": None,
                    "timestamp": get_time(time_str),
                    "url": article_url,
                    "mobileUrl": article_url,
                })
            
            return result
        except Exception as e:
            return []
