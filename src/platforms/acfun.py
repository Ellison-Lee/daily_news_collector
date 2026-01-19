"""AcFun 平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class AcfunPlatform(BasePlatform):
    """AcFun 平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "acfun"
        self.title = "AcFun"
        self.type = "排行榜"
        self.description = "AcFun是一家弹幕视频网站，致力于为每一个人带来欢乐。"
        self.link = "https://www.acfun.cn/rank/list/"
        self.category = "社交媒体"
    
    async def fetch(self, type: str = "-1", range: str = "DAY", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        channel_id = "" if type == "-1" else type
        url = f"https://www.acfun.cn/rest/pc-direct/rank/channel?channelId={channel_id}&rankLimit=30&rankPeriod={range}"
        
        try:
            result = await self.http_client.get(
                url=url,
                headers={
                    "Referer": f"https://www.acfun.cn/rank/list/?cid=-1&pcid={type}&range={range}",
                }
            )
        except Exception as e:
            return []
        
        # 尝试多种数据路径
        list_data = None
        
        # 路径1: result.data.rankList
        if result.get("data") and isinstance(result.get("data"), dict):
            list_data = result.get("data").get("rankList", [])
        
        # 路径2: result.rankList (如果路径1失败)
        if not list_data:
            list_data = result.get("rankList", [])
        
        # 如果还是没有数据，尝试直接获取result中的列表
        if not list_data and isinstance(result, dict):
            # 查找包含列表的键
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    list_data = value
                    break
        
        if not list_data:
            list_data = []
        
        return [
            {
                "id": item.get("dougaId", ""),
                "title": item.get("contentTitle", ""),
                "desc": item.get("contentDesc", ""),
                "cover": item.get("coverUrl", ""),
                "author": item.get("userName", ""),
                "timestamp": get_time(item.get("contributeTime")),
                "hot": item.get("likeCount", 0),
                "url": f"https://www.acfun.cn/v/ac{item.get('dougaId', '')}",
                "mobileUrl": f"https://m.acfun.cn/v/?ac={item.get('dougaId', '')}",
            }
            for item in list_data
        ]
