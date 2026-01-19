"""站酷平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class ZcoolPlatform(BasePlatform):
    """站酷平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "zcool"
        self.title = "站酷"
        self.type = "热榜"
        self.link = "https://www.zcool.com.cn/"
        self.category = "设计创意"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["站酷"],
            platform_name="zcool"
        )
