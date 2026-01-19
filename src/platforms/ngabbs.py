"""NGA 平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class NgabbsPlatform(BasePlatform):
    """NGA 平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "ngabbs"
        self.title = "NGA"
        self.type = "热帖"
        self.link = "https://ngabbs.com/"
        self.category = "娱乐内容"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        try:
            url = "https://ngabbs.com/nuke.php?__lib=subject&__act=list&tid=&page=1&limit=20"
            
            result = await self.http_client.get(
                url=url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }
            )
            
            if not isinstance(result, dict):
                return []
            
            # 尝试多种数据路径
            list_data = None
            
            # 路径1: result.data.result
            if result.get("data") and isinstance(result.get("data"), dict):
                list_data = result.get("data").get("result", [])
            
            # 路径2: result.result (如果路径1失败)
            if not list_data:
                list_data = result.get("result", [])
            
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
                    "id": str(item.get("tid", "")),
                    "title": item.get("subject", ""),
                    "desc": item.get("summary", ""),
                    "author": item.get("author", ""),
                    "hot": item.get("replies", 0),
                    "timestamp": get_time(item.get("postdate")),
                    "url": f"https://ngabbs.com/read.php?tid={item.get('tid', '')}",
                    "mobileUrl": f"https://ngabbs.com/read.php?tid={item.get('tid', '')}",
                }
                for item in list_data if isinstance(item, dict)
            ]
        except Exception as e:
            return []
