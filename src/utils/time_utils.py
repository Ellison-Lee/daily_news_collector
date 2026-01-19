"""时间工具函数"""

from datetime import datetime
from typing import Optional, Union


def get_time(timestamp: Optional[Union[int, str]] = None) -> Optional[int]:
    """将时间戳转换为秒级时间戳"""
    if timestamp is None:
        return None
    
    try:
        if isinstance(timestamp, str):
            # 尝试解析字符串时间戳
            if timestamp.isdigit():
                timestamp = int(timestamp)
            else:
                # 尝试解析 ISO 格式时间
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return int(dt.timestamp())
        
        # 如果是毫秒级时间戳，转换为秒级
        if timestamp > 1e10:
            timestamp = timestamp // 1000
        
        return int(timestamp)
    except (ValueError, TypeError):
        return None


def format_time(timestamp: Optional[int] = None) -> str:
    """格式化时间为 ISO 格式"""
    if timestamp is None:
        return datetime.now().isoformat()
    
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.isoformat()
    except (ValueError, OSError):
        return datetime.now().isoformat()
