"""开源中国平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class OsChinaPlatform(BasePlatform):
    """开源中国平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "oschina"
        self.title = "开源中国"
        self.type = "热榜"
        self.link = "https://www.oschina.net/"
        self.category = "技术社区"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["开源中国"],
            platform_name="oschina"
        )
