"""数据采集器模块"""

from .base import BaseCollector
from .api_collector import APICollector
from .html_collector import HTMLCollector
from .rss_collector import RSSCollector

__all__ = ["BaseCollector", "APICollector", "HTMLCollector", "RSSCollector"]
