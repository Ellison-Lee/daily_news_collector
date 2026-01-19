"""TapTap平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class TaptapPlatform(BasePlatform):
    """TapTap平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "taptap"
        self.title = "TapTap"
        self.type = "热榜"
        self.link = "https://www.taptap.cn/"
        self.category = "游戏娱乐"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["TapTap"],
            platform_name="taptap"
        )
