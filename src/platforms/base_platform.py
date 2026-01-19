"""平台基类"""

from typing import Dict, List, Optional, Any

from ..collectors.base import BaseCollector


class BasePlatform(BaseCollector):
    """平台基类"""
    
    def __init__(self):
        """初始化平台"""
        super().__init__()
        self.name = ""
        self.title = ""
        self.type = ""
        self.description = ""
        self.link = ""
        self.category = ""
    
    async def get_route_data(self, no_cache: bool = False, **kwargs) -> Dict[str, Any]:
        """获取路由数据"""
        result = await self.collect(no_cache=no_cache, **kwargs)
        return {
            "name": self.name,
            "title": self.title,
            "type": self.type,
            "description": self.description,
            "link": self.link,
            "total": len(result.get("data", [])),
            **result,
        }
