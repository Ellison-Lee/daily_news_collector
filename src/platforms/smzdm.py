"""什么值得买平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class SmzdmPlatform(BasePlatform):
    """什么值得买平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "smzdm"
        self.title = "什么值得买"
        self.type = "今日热门"
        self.description = "什么值得买是一个中立的、致力于帮助广大网友买到更有性价比网购产品的最热门推荐网站。"
        self.link = "https://www.smzdm.com/top/"
        self.category = "生活消费"
    
    async def fetch(self, type: str = "1", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://post.smzdm.com/rank/json_more/?unit={type}"
        
        try:
            result = await self.http_client.get(
                url=url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.smzdm.com/",
                }
            )
            
            if not isinstance(result, dict):
                return []
            
            # 尝试多种数据路径
            list_data = None
            
            # 路径1: result.data.data
            if result.get("data") and isinstance(result.get("data"), dict):
                list_data = result.get("data").get("data", [])
            
            # 路径2: result.data (如果路径1失败)
            if not list_data and result.get("data"):
                if isinstance(result.get("data"), list):
                    list_data = result.get("data")
            
            # 路径3: result (如果路径2失败，result本身就是列表)
            if not list_data and isinstance(result, list):
                list_data = result
            
            # 如果还是没有数据，尝试直接获取result中的列表
            if not list_data and isinstance(result, dict):
                # 查找包含列表的键
                for key, value in result.items():
                    if isinstance(value, list) and len(value) > 0:
                        list_data = value
                        break
            
            if not list_data:
                list_data = []
            
            if not isinstance(list_data, list):
                return []
            
            return [
                {
                    "id": str(item.get("article_id", "")),
                    "title": item.get("title", ""),
                    "desc": item.get("content", ""),
                    "cover": item.get("pic_url", ""),
                    "author": item.get("nickname", ""),
                    "hot": int(item.get("collection_count", 0)) if item.get("collection_count") else 0,
                    "timestamp": get_time(item.get("time_sort")),
                    "url": item.get("jump_link", ""),
                    "mobileUrl": item.get("jump_link", ""),
                }
                for item in list_data if isinstance(item, dict)
            ]
        except Exception as e:
            return []
