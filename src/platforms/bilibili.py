"""哔哩哔哩平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.token_utils import get_bilibili_wbi
from ..utils.time_utils import get_time


class BilibiliPlatform(BasePlatform):
    """哔哩哔哩平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "bilibili"
        self.title = "哔哩哔哩"
        self.type = "热榜"
        self.description = "你所热爱的，就是你的生活"
        self.link = "https://www.bilibili.com/v/popular/rank/all"
        self.category = "社交媒体"
    
    async def fetch(self, type: str = "0", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        wbi_data = await get_bilibili_wbi(self.http_client)
        url = f"https://api.bilibili.com/x/web-interface/ranking/v2?rid={type}&type=all&{wbi_data}"
        
        result = await self.http_client.get(
            url=url,
            headers={
                "Referer": "https://www.bilibili.com/ranking/all",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
        )
        
        if result.get("data", {}).get("list"):
            list_data = result["data"]["list"]
            return [
                {
                    "id": item.get("bvid", ""),
                    "title": item.get("title", ""),
                    "desc": item.get("desc", "该视频暂无简介"),
                    "cover": item.get("pic", "").replace("http:", "https:"),
                    "author": item.get("owner", {}).get("name", ""),
                    "timestamp": get_time(item.get("pubdate")),
                    "hot": item.get("stat", {}).get("view", 0),
                    "url": item.get("short_link_v2") or f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    "mobileUrl": f"https://m.bilibili.com/video/{item.get('bvid', '')}",
                }
                for item in list_data
            ]
        
        # 备用接口
        url = f"https://api.bilibili.com/x/web-interface/ranking?jsonp=jsonp?rid={type}&type=all&callback=__jp0"
        result = await self.http_client.get(
            url=url,
            headers={"Referer": "https://www.bilibili.com/ranking/all"}
        )
        
        list_data = result.get("data", {}).get("list", [])
        return [
            {
                "id": item.get("bvid", ""),
                "title": item.get("title", ""),
                "desc": item.get("desc", "该视频暂无简介"),
                "cover": item.get("pic", "").replace("http:", "https:"),
                "author": item.get("author", ""),
                "timestamp": None,
                "hot": item.get("video_review", 0),
                "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                "mobileUrl": f"https://m.bilibili.com/video/{item.get('bvid', '')}",
            }
            for item in list_data
        ]
