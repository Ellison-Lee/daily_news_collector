"""虎嗅平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class HuxiuPlatform(BasePlatform):
    """虎嗅平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "huxiu"
        self.title = "虎嗅"
        self.type = "24小时"
        self.link = "https://www.huxiu.com/moment/"
        self.category = "新闻资讯"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://moment-api.huxiu.com/web-v3/moment/feed?platform=www"
        
        result = await self.http_client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.huxiu.com/moment/",
            }
        )
        
        list_data = result.get("data", {}).get("moment_list", {}).get("datalist", [])
        
        return [
            {
                "id": item.get("object_id", ""),
                "title": self._extract_title(item.get("content", "")),
                "desc": self._extract_desc(item.get("content", "")),
                "author": item.get("user_info", {}).get("username", ""),
                "timestamp": get_time(item.get("publish_time")),
                "hot": item.get("count_info", {}).get("agree_num"),
                "url": f"https://www.huxiu.com/moment/{item.get('object_id', '')}.html",
                "mobileUrl": f"https://m.huxiu.com/moment/{item.get('object_id', '')}.html",
            }
            for item in list_data
        ]
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        if not content:
            return ""
        content = content.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        lines = [s.strip() for s in content.split("\n") if s.strip()]
        if lines:
            title = lines[0].replace("。", "")
            return title
        return ""
    
    def _extract_desc(self, content: str) -> str:
        """提取描述"""
        if not content:
            return ""
        content = content.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        lines = [s.strip() for s in content.split("\n") if s.strip()]
        if len(lines) > 1:
            return "\n".join(lines[1:])
        return ""
