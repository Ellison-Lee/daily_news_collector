"""即刻圈子平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class JikePlatform(BasePlatform):
    """即刻圈子平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "jike"
        self.title = "即刻圈子"
        self.type = "热榜"
        self.link = "https://web.okjike.com/"
        self.category = "社交媒体"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["即刻", "圈子"],
            platform_name="jike"
        )
