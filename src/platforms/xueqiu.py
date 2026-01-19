"""雪球平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class XueqiuPlatform(BasePlatform):
    """雪球平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "xueqiu"
        self.title = "雪球"
        self.type = "热榜"
        self.link = "https://xueqiu.com/"
        self.category = "金融财经"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["雪球"],
            platform_name="xueqiu"
        )
