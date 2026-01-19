"""微信24h热文榜平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class WechatHotPlatform(BasePlatform):
    """微信24h热文榜平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "wechat-hot"
        self.title = "微信24h热文榜"
        self.type = "热榜"
        self.link = "https://tophub.today/"
        self.category = "社交媒体"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["微信", "24h", "热文"],
            platform_name="wechat-hot"
        )
