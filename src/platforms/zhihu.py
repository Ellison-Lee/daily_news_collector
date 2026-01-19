"""知乎平台"""

import os
from typing import Dict, List, Any

from dotenv import load_dotenv

from .base_platform import BasePlatform
from ..utils.time_utils import get_time

load_dotenv()


class ZhihuPlatform(BasePlatform):
    """知乎平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "zhihu"
        self.title = "知乎"
        self.type = "热榜"
        self.link = "https://www.zhihu.com/hot"
        self.category = "社交媒体"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://api.zhihu.com/topstory/hot-lists/total?limit=50"
        
        headers = {}
        zhihu_cookie = os.getenv("ZHIHU_COOKIE", "")
        if zhihu_cookie:
            headers["Cookie"] = zhihu_cookie
        
        result = await self.http_client.get(url=url, headers=headers)
        
        list_data = result.get("data", [])
        return [
            {
                "id": item.get("target", {}).get("id", ""),
                "title": item.get("target", {}).get("title", ""),
                "desc": item.get("target", {}).get("excerpt", ""),
                "cover": item.get("children", [{}])[0].get("thumbnail", ""),
                "timestamp": get_time(item.get("target", {}).get("created")),
                "hot": int(float(item.get("detail_text", "0").split(" ")[0]) * 10000) if item.get("detail_text") else None,
                "url": f"https://www.zhihu.com/question/{item.get('target', {}).get('url', '').split('/')[-1]}",
                "mobileUrl": f"https://www.zhihu.com/question/{item.get('target', {}).get('url', '').split('/')[-1]}",
            }
            for item in list_data
        ]
