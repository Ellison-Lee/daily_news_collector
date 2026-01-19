"""快手平台"""

import json
from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.number_utils import parse_chinese_number


class KuaishouPlatform(BasePlatform):
    """快手平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "kuaishou"
        self.title = "快手"
        self.type = "热榜"
        self.description = "快手，拥抱每一种生活"
        self.link = "https://www.kuaishou.com/"
        self.category = "社交媒体"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://www.kuaishou.com/?isHome=1"
        
        html = await self.http_client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            response_type="text"
        )
        
        # 提取 APOLLO_STATE
        APOLLO_STATE_PREFIX = "window.__APOLLO_STATE__="
        start = html.find(APOLLO_STATE_PREFIX)
        if start == -1:
            raise ValueError("快手页面结构变更，未找到 APOLLO_STATE")
        
        script_slice = html[start + len(APOLLO_STATE_PREFIX):]
        sentinel_a = script_slice.find(";(function(")
        sentinel_b = script_slice.find("</script>")
        
        cut_index = min(sentinel_a, sentinel_b) if sentinel_a != -1 and sentinel_b != -1 else max(sentinel_a, sentinel_b)
        if cut_index == -1:
            raise ValueError("快手页面结构变更，未找到 APOLLO_STATE 结束标记")
        
        raw = script_slice[:cut_index].strip().rstrip(";")
        
        # 解析 JSON
        try:
            last_brace = raw.rfind("}")
            clean_raw = raw[:last_brace + 1] if last_brace != -1 else raw
            json_object = json.loads(clean_raw)["defaultClient"]
        except Exception as e:
            raise ValueError(f"快手数据解析失败: {str(e)}")
        
        # 获取热榜数据
        all_items = (
            json_object.get('$ROOT_QUERY.visionHotRank({"page":"home"})', {}).get("items", []) or
            json_object.get('$ROOT_QUERY.visionHotRank({"page":"home","platform":"web"})', {}).get("items", [])
        )
        
        result = []
        for item in all_items:
            hot_item = json_object.get(item.get("id", ""))
            if not hot_item:
                continue
            
            photo_id = hot_item.get("photoIds", {}).get("json", [""])[0] if hot_item.get("photoIds", {}).get("json") else ""
            hot_value = hot_item.get("hotValue", "")
            poster = hot_item.get("poster", "")
            if poster:
                import urllib.parse
                poster = urllib.parse.unquote(poster)
            
            result.append({
                "id": hot_item.get("id", ""),
                "title": hot_item.get("name", ""),
                "cover": poster,
                "hot": parse_chinese_number(str(hot_value)),
                "timestamp": None,
                "url": f"https://www.kuaishou.com/short-video/{photo_id}",
                "mobileUrl": f"https://www.kuaishou.com/short-video/{photo_id}",
            })
        
        return result
