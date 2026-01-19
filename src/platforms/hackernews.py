"""Hacker News 平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform
from ..utils.time_utils import get_time


class HackernewsPlatform(BasePlatform):
    """Hacker News 平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "hackernews"
        self.title = "Hacker News"
        self.type = "热榜"
        self.link = "https://news.ycombinator.com/"
        self.category = "技术社区"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        import asyncio
        
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        
        story_ids = await self.http_client.get(url=url)
        
        if not story_ids or len(story_ids) == 0:
            return []
        
        # 获取前30个故事详情
        story_ids = story_ids[:30]
        tasks = [
            self.http_client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
            for story_id in story_ids
        ]
        
        stories = await asyncio.gather(*tasks)
        
        result = []
        for story in stories:
            if not story or story.get("type") != "story":
                continue
            
            result.append({
                "id": str(story.get("id", "")),
                "title": story.get("title", ""),
                "desc": f"{story.get('score', 0)} points by {story.get('by', '')}",
                "author": story.get("by", ""),
                "hot": story.get("score", 0),
                "timestamp": get_time(story.get("time")),
                "url": story.get("url") or f"https://news.ycombinator.com/item?id={story.get('id', '')}",
                "mobileUrl": story.get("url") or f"https://news.ycombinator.com/item?id={story.get('id', '')}",
            })
        
        return result
