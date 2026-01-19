"""36氪平台"""

import time
from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class Platform36kr(BasePlatform):
    """36氪平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "36kr"
        self.title = "36氪"
        self.type = "人气榜"
        self.link = "https://m.36kr.com/hot-list-m"
        self.category = "新闻资讯"
    
    async def fetch(self, type: str = "hot", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://gateway.36kr.com/api/mis/nav/home/nav/rank/{type}"
        
        try:
            result = await self.http_client.post(
                url=url,
                json_data={
                    "partner_id": "wap",
                    "param": {
                        "siteId": 1,
                        "platformId": 2,
                    },
                    "timestamp": int(time.time() * 1000),
                },
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                }
            )
        except Exception as e:
            return []
        
        if not isinstance(result, dict):
            return []
        
        list_type_map = {
            "hot": "hotRankList",
            "video": "videoList",
            "comment": "remarkList",
            "collect": "collectList",
        }
        
        # 尝试多种数据路径
        list_data = None
        expected_key = list_type_map.get(type, "hotRankList")
        
        # 路径1: result.data.data.hotRankList
        if result.get("data") and isinstance(result.get("data"), dict):
            if result.get("data").get("data") and isinstance(result.get("data").get("data"), dict):
                list_data = result.get("data").get("data").get(expected_key, [])
        
        # 路径2: result.data.hotRankList (如果路径1失败)
        if not list_data and result.get("data") and isinstance(result.get("data"), dict):
            list_data = result.get("data").get(expected_key, [])
        
        # 路径3: result.hotRankList (如果路径2失败)
        if not list_data:
            list_data = result.get(expected_key, [])
        
        if not isinstance(list_data, list):
            return []
        
        return [
            {
                "id": item.get("itemId", ""),
                "title": item.get("templateMaterial", {}).get("widgetTitle", ""),
                "cover": item.get("templateMaterial", {}).get("widgetImage", ""),
                "author": item.get("templateMaterial", {}).get("authorName", ""),
                "timestamp": get_time(item.get("publishTime")),
                "hot": item.get("templateMaterial", {}).get("statCollect"),
                "url": f"https://www.36kr.com/p/{item.get('itemId', '')}",
                "mobileUrl": f"https://m.36kr.com/p/{item.get('itemId', '')}",
            }
            for item in list_data
        ]
