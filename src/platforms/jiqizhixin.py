"""机器之心平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.tophub_helper import fetch_from_tophub


class JiqizhixinPlatform(BasePlatform):
    """机器之心平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "jiqizhixin"
        self.title = "机器之心"
        self.type = "热榜"
        self.link = "https://www.jiqizhixin.com/"
        self.category = "科技资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        return await fetch_from_tophub(
            self.http_client,
            platform_keywords=["机器之心"],
            platform_name="jiqizhixin"
        )
