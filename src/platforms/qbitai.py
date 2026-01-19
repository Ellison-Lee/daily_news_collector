"""量子位平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class QbitaiPlatform(BasePlatform):
    """量子位平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "qbitai"
        self.title = "量子位"
        self.type = "热榜"
        self.link = "https://www.qbitai.com/"
        self.category = "科技资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["量子位"],
            platform_name="qbitai"
        )
