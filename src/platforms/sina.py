"""新浪网平台"""

from typing import Dict, List, Any

from .base_platform import BasePlatform


class SinaPlatform(BasePlatform):
    """新浪网平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "sina"
        self.title = "新浪网"
        self.type = "新浪热榜"
        self.description = "热榜太多，一个就够"
        self.link = "https://sinanews.sina.cn/"
        self.category = "新闻资讯"
    
    def _parse_chinese_number(self, text: str) -> int:
        """解析中文数字"""
        if not text:
            return 0
        # 移除逗号
        text = text.replace(",", "")
        # 处理万、千等单位
        if "万" in text:
            num = float(text.replace("万", ""))
            return int(num * 10000)
        elif "千" in text:
            num = float(text.replace("千", ""))
            return int(num * 1000)
        try:
            return int(float(text))
        except:
            return 0
    
    async def fetch(self, type: str = "all", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://newsapp.sina.cn/api/hotlist?newsId=HB-1-snhs%2Ftop_news_list-{type}"
        
        try:
            result = await self.http_client.get(url=url)
        except Exception as e:
            return []
        
        # 尝试多种数据路径
        list_data = None
        
        # 路径1: result.data.data.hotList
        if result.get("data") and isinstance(result.get("data"), dict):
            if result.get("data").get("data") and isinstance(result.get("data").get("data"), dict):
                list_data = result.get("data").get("data").get("hotList", [])
        
        # 路径2: result.data.hotList (如果路径1失败)
        if not list_data and result.get("data") and isinstance(result.get("data"), dict):
            list_data = result.get("data").get("hotList", [])
        
        # 路径3: result.hotList (如果路径2失败)
        if not list_data:
            list_data = result.get("hotList", [])
        
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
                "id": item.get("base", {}).get("base", {}).get("uniqueId", ""),
                "title": item.get("info", {}).get("title", ""),
                "desc": None,
                "author": None,
                "timestamp": None,
                "hot": self._parse_chinese_number(item.get("info", {}).get("hotValue", "")),
                "url": item.get("base", {}).get("base", {}).get("url", ""),
                "mobileUrl": item.get("base", {}).get("base", {}).get("url", ""),
            }
            for item in list_data
        ]
