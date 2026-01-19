"""虎扑平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform


class HupuPlatform(BasePlatform):
    """虎扑平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "hupu"
        self.title = "虎扑"
        self.type = "步行街热帖"
        self.link = "https://bbs.hupu.com/all-gambia"
        self.category = "生活消费"
    
    async def fetch(self, type: str = "1", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://m.hupu.com/api/v2/bbs/topicThreads?topicId={type}&page=1"
        
        try:
            result = await self.http_client.get(url=url)
        except Exception as e:
            return []
        
        # 尝试多种数据路径
        list_data = None
        
        # 路径1: result.data.data.topicThreads
        if result.get("data") and isinstance(result.get("data"), dict):
            if result.get("data").get("data") and isinstance(result.get("data").get("data"), dict):
                list_data = result.get("data").get("data").get("topicThreads", [])
        
        # 路径2: result.data.topicThreads (如果路径1失败)
        if not list_data and result.get("data") and isinstance(result.get("data"), dict):
            list_data = result.get("data").get("topicThreads", [])
        
        # 路径3: result.topicThreads (如果路径2失败)
        if not list_data:
            list_data = result.get("topicThreads", [])
        
        # 如果还是没有数据，尝试直接获取result中的列表
        if not list_data and isinstance(result, dict):
            # 查找包含列表的键
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    list_data = value
                    break
        
        if not list_data:
            list_data = []
        
        return [
            {
                "id": item.get("tid", ""),
                "title": item.get("title", ""),
                "author": item.get("username", ""),
                "hot": item.get("replies", 0),
                "timestamp": None,
                "url": f"https://bbs.hupu.com/{item.get('tid', '')}.html",
                "mobileUrl": item.get("url", ""),
            }
            for item in list_data
        ]
