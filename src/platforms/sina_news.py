"""新浪新闻平台"""

import json
from datetime import datetime
from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class SinaNewsPlatform(BasePlatform):
    """新浪新闻平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "sina-news"
        self.title = "新浪新闻"
        self.type = "总排行"
        self.link = "https://sinanews.sina.cn/"
        self.category = "新闻资讯"
    
    def _parse_jsonp(self, data: str) -> Dict:
        """解析 JSONP 数据"""
        if not data:
            raise ValueError("Input data is empty or invalid")
        
        prefix = "var data = "
        if not data.startswith(prefix):
            raise ValueError("Input data does not start with the expected prefix")
        
        json_string = data[len(prefix):].strip()
        if json_string.endswith(";"):
            json_string = json_string[:-1].strip()
        
        if json_string.startswith("{") and json_string.endswith("}"):
            try:
                return json.loads(json_string)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON: {e}")
        else:
            raise ValueError("Invalid JSON format")
    
    async def fetch(self, type: str = "1", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        # 榜单类别配置
        list_type_map = {
            "1": {"www": "news", "params": "www_www_all_suda_suda"},
            "2": {"www": "news", "params": "video_news_all_by_vv"},
            "3": {"www": "news", "params": "total_slide_suda"},
            "4": {"www": "news", "params": "news_china_suda"},
            "5": {"www": "news", "params": "news_world_suda"},
            "6": {"www": "news", "params": "news_society_suda"},
            "7": {"www": "sports", "params": "sports_suda"},
            "8": {"www": "finance", "params": "finance_0_suda"},
            "9": {"www": "ent", "params": "ent_suda"},
            "10": {"www": "tech", "params": "tech_news_suda"},
            "11": {"www": "news", "params": "news_mil_suda"},
        }
        
        config = list_type_map.get(type, list_type_map["1"])
        now = datetime.now()
        date_str = f"{now.year}{now.month:02d}{now.day:02d}"
        
        url = f"https://top.{config['www']}.sina.com.cn/ws/GetTopDataList.php?top_type=day&top_cat={config['params']}&top_time={date_str}&top_show_num=50"
        
        result = await self.http_client.get(url=url, response_type="text")
        
        json_data = self._parse_jsonp(result)
        list_data = json_data.get("data", [])
        
        return [
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "author": item.get("media"),
                "hot": float(item.get("top_num", "0").replace(",", "")),
                "timestamp": get_time(f"{item.get('create_date', '')} {item.get('create_time', '')}"),
                "url": item.get("url", ""),
                "mobileUrl": item.get("url", ""),
            }
            for item in list_data
        ]
