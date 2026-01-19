"""汽车之家平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class AutohomePlatform(BasePlatform):
    """汽车之家平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "autohome"
        self.title = "汽车之家"
        self.type = "热榜"
        self.link = "https://www.autohome.com.cn/"
        self.category = "汽车"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["汽车之家"],
            platform_name="autohome"
        )
