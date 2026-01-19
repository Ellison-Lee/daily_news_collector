"""百度贴吧平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class TiebaPlatform(BasePlatform):
    """百度贴吧平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "tieba"
        self.title = "百度贴吧"
        self.type = "热议榜"
        self.description = "全球领先的中文社区"
        self.link = "https://tieba.baidu.com/hottopic/browse/topicList"
        self.category = "社交媒体"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = "https://tieba.baidu.com/hottopic/browse/topicList"
        
        # 尝试使用aiohttp，如果失败则使用requests作为备选
        try:
            # 为tieba平台使用更长的超时时间和特定的请求头
            from aiohttp import ClientTimeout
            timeout = ClientTimeout(total=60, connect=30)
            
            result = await self.http_client.get(
                url=url,
                headers={
                    "Referer": "https://tieba.baidu.com/",
                    "Accept": "application/json, text/plain, */*",
                },
                timeout=timeout
            )
        except Exception:
            # 如果aiohttp失败，使用curl作为备选方案（因为curl可以正常访问）
            import asyncio
            import subprocess
            import json
            
            def curl_fetch():
                try:
                    # 使用curl命令获取数据
                    cmd = [
                        'curl', '-s', '-m', '30',
                        url,
                        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                        '-H', 'Referer: https://tieba.baidu.com/',
                        '-H', 'Accept: application/json, text/plain, */*',
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
                    result.check_returncode()
                    return json.loads(result.stdout)
                except Exception as e:
                    # 如果curl也失败，尝试使用requests
                    import requests
                    response = requests.get(
                        url,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                            "Referer": "https://tieba.baidu.com/",
                            "Accept": "application/json, text/plain, */*",
                        },
                        timeout=(10, 60)  # (connect timeout, read timeout)
                    )
                    response.raise_for_status()
                    return response.json()
            
            result = await asyncio.to_thread(curl_fetch)
            
        list_data = result.get("data", {}).get("bang_topic", {}).get("topic_list", [])
        
        return [
            {
                "id": item.get("topic_id", ""),
                "title": item.get("topic_name", ""),
                "desc": item.get("topic_desc", ""),
                "cover": item.get("topic_pic", ""),
                "hot": item.get("discuss_num", 0),
                "timestamp": get_time(item.get("create_time")),
                "url": item.get("topic_url", ""),
                "mobileUrl": item.get("topic_url", ""),
            }
            for item in list_data
        ]
