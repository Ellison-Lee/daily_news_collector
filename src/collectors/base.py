"""基础采集器类"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..cache.cache_manager import CacheManager
from ..utils.http_client import HTTPClient
from ..utils.time_utils import format_time


class BaseCollector(ABC):
    """基础采集器抽象类"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None, http_client: Optional[HTTPClient] = None):
        """初始化采集器"""
        self.cache_manager = cache_manager or CacheManager()
        self.http_client = http_client or HTTPClient()
        self.name = ""
        self.title = ""
        self.type = ""
        self.description = ""
        self.link = ""
    
    def normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """标准化数据项"""
        return {
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "cover": item.get("cover"),
            "author": item.get("author"),
            "desc": item.get("desc"),
            "hot": item.get("hot"),
            "timestamp": item.get("timestamp"),
            "url": item.get("url", ""),
            "mobileUrl": item.get("mobileUrl", item.get("url", "")),
        }
    
    def normalize_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """标准化数据列表"""
        return [self.normalize_item(item) for item in data]
    
    @abstractmethod
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据（子类必须实现）"""
        pass
    
    async def collect(self, no_cache: bool = False, **kwargs) -> Dict[str, Any]:
        """采集数据"""
        cache_key = f"{self.name}:{json.dumps(kwargs, sort_keys=True)}"
        
        # 检查缓存
        if not no_cache:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return {
                    "fromCache": True,
                    "updateTime": cached_data.get("updateTime"),
                    "data": cached_data.get("data", []),
                }
        
        # 获取新数据
        try:
            data = await self.fetch(**kwargs)
            normalized_data = self.normalize_data(data)
            update_time = format_time()
            
            # 保存到缓存
            if not no_cache:
                self.cache_manager.set(cache_key, {"data": normalized_data}, ttl=self.cache_manager.default_ttl)
            
            return {
                "fromCache": False,
                "updateTime": update_time,
                "data": normalized_data,
            }
        except Exception as e:
            raise Exception(f"采集失败: {str(e)}")
    
    async def close(self):
        """关闭资源"""
        await self.http_client.close()
