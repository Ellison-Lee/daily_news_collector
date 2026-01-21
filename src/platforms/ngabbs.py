"""NGA 平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class NgabbsPlatform(BasePlatform):
    """NGA 平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "ngabbs"
        self.title = "NGA"
        self.type = "热帖"
        self.link = "https://ngabbs.com/"
        self.category = "娱乐内容"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """
        获取数据
        
        注意：NGA的API当前不可用
        - 所有已知的API端点（nuke.php）都返回空数据
        - RSS feed返回404错误
        - HTML页面访问返回403 Forbidden（反爬虫机制）
        
        返回空列表，等待NGA API恢复或找到新的数据获取方式
        """
        # NGA的API已经改变，当前所有已知端点都不可用
        # 经过测试：
        # 1. nuke.php API端点返回空字典
        # 2. RSS feed返回404
        # 3. HTML页面访问返回403 Forbidden
        # 因此暂时返回空列表
        return []
