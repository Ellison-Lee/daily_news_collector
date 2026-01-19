"""抖音平台"""

import re
from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time
from ..utils.token_utils import get_douyin_cookie


class DouyinPlatform(BasePlatform):
    """抖音平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "douyin"
        self.title = "抖音"
        self.type = "热榜"
        self.description = "实时上升热点"
        self.link = "https://www.douyin.com"
        self.category = "社交媒体"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        try:
            # 获取 Cookie
            cookie = await get_douyin_cookie(self.http_client)
            
            url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            if cookie:
                headers["Cookie"] = f"passport_csrf_token={cookie}"
            
            result = await self.http_client.get(url=url, headers=headers)
            
            if not isinstance(result, dict):
                return []
            
            list_data = result.get("data", {}).get("data", {}).get("word_list", [])
            
            if not isinstance(list_data, list):
                return []
            
            return [
                {
                    "id": str(item.get("sentence_id", "")),
                    "title": item.get("word", ""),
                    "timestamp": get_time(item.get("event_time")),
                    "hot": item.get("hot_value", 0),
                    "url": f"https://www.douyin.com/hot/{item.get('sentence_id', '')}",
                    "mobileUrl": f"https://www.douyin.com/hot/{item.get('sentence_id', '')}",
                }
                for item in list_data if isinstance(item, dict)
            ]
        except Exception as e:
            return []
