"""TopHub 今日简报 • AI 平台"""

import json
import re
from typing import Dict, List, Any
from bs4 import BeautifulSoup

from .base_platform import BasePlatform


class TopHubAIBriefPlatform(BasePlatform):
    """TopHub 今日简报 • AI 平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "tophub-ai-brief"
        self.title = "今日简报 • AI"
        self.type = "AI简报"
        self.description = "AI 驱动，从 10,000+ 热榜信息源中精选摘要，呈现每日核心资讯"
        self.link = "https://tophub.today/daily"
        self.category = "简报"
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        base_url = "https://tophub.today/daily"
        api_base = "https://idaily.today/tophub/share"
        
        # 1. 获取页面HTML
        html = await self.http_client.get(
            url=base_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
            response_type="text"
        )
        
        # 2. 提取hash值
        soup = BeautifulSoup(html, 'html.parser')
        ai_content = soup.find('div', id='ai-summary-content')
        if not ai_content:
            return []
        
        hash_value = ai_content.get('data-hash', '')
        if not hash_value:
            return []
        
        # 3. 调用API获取数据
        import time
        timestamp = int(time.time() * 1000)
        callback = f"jQuery{timestamp}_{timestamp}"
        
        params = {
            'callback': callback,
            'hash': hash_value,
            '_': timestamp
        }
        
        try:
            api_response = await self.http_client.get(
                url=api_base,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "*/*",
                    "Referer": "https://tophub.today/daily",
                },
                response_type="text"
            )
            
            # 解析JSONP响应
            text = api_response
            # 移除JSONP包装
            if text.startswith(callback + '('):
                json_str = text[len(callback) + 1:-1]  # 移除 callback( 和 )
                api_data = json.loads(json_str)
            else:
                # 尝试匹配任何jQuery回调
                match = re.match(r'jQuery\d+_\d+\((.*)\);?$', text)
                if match:
                    json_str = match.group(1)
                    api_data = json.loads(json_str)
                else:
                    return []
            
            # 4. 解析HTML内容
            result = []
            if isinstance(api_data, list):
                for item in api_data:
                    if isinstance(item, dict) and 'html' in item:
                        category_title = item.get('title', '')
                        html_content = item['html']
                        
                        # 解析HTML，提取标题和内容
                        soup = BeautifulSoup(html_content, 'html.parser')
                        lis = soup.find_all('li')
                        
                        for idx, li in enumerate(lis):
                            strong = li.find('strong')
                            if strong:
                                title = strong.get_text(strip=True)
                                # 移除strong标签后获取剩余文本
                                strong.extract()
                                content = li.get_text(strip=True)
                                # 去除content开头的冒号和空格
                                if content.startswith('：'):
                                    content = content[1:].strip()
                                elif content.startswith(':'):
                                    content = content[1:].strip()
                            else:
                                title = ""
                                content = li.get_text(strip=True)
                            
                            # 生成唯一ID
                            item_id = f"{hash_value}_{category_title}_{idx}"
                            
                            result.append({
                                "id": item_id,
                                "title": title,
                                "desc": content,
                                "cover": None,
                                "author": None,
                                "hot": None,
                                "timestamp": None,
                                "url": self.link,
                                "mobileUrl": self.link,
                            })
            
            return result
            
        except Exception as e:
            # 如果API调用失败，返回空列表
            return []
