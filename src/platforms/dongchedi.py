"""懂车帝平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class DongchediPlatform(BasePlatform):
    """懂车帝平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "dongchedi"
        self.title = "懂车帝"
        self.type = "热榜"
        self.link = "https://www.dongchedi.com/"
        self.category = "汽车"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["懂车帝"],
            platform_name="dongchedi"
        )
