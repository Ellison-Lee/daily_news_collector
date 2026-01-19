"""TopHub 通用数据获取工具"""

import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

from ..utils.http_client import HTTPClient


async def fetch_from_tophub(http_client: HTTPClient, platform_keywords: List[str], platform_name: str) -> List[Dict[str, Any]]:
    """
    从 TopHub 获取指定平台的数据
    
    Args:
        http_client: HTTP客户端
        platform_keywords: 平台关键词列表，用于在首页查找链接（如 ["微信", "24h", "热文"]）
        platform_name: 平台名称，用于生成默认URL
    
    Returns:
        数据列表
    """
    try:
        # 直接访问首页，查找平台的链接
        home_url = "https://tophub.today/"
        
        html = await http_client.get(
            url=home_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
            response_type="text"
        )
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找平台的链接
        platform_url = None
        links = soup.find_all('a', href=True)
        
        for link in links:
            link_text = link.get_text(strip=True)
            href = link.get('href', '')
            parent_text = ""
            if link.parent:
                parent_text = link.parent.get_text()
            
            # 检查是否匹配所有关键词
            full_text = f"{link_text} {parent_text}"
            if all(keyword in full_text for keyword in platform_keywords) and '/n/' in href:
                platform_url = href if href.startswith('http') else f"https://tophub.today{href}"
                break
        
        # 如果找到了链接，访问该页面
        if platform_url:
            page_html = await http_client.get(
                url=platform_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Referer": "https://tophub.today/",
                },
                response_type="text"
            )
            
            soup = BeautifulSoup(page_html, 'html.parser')
        
        # 解析表格数据
        table_rows = soup.select('table tbody tr')
        if not table_rows:
            table_rows = soup.select('.table tbody tr, .list tbody tr, tbody tr')
        
        if table_rows:
            result = []
            for idx, row in enumerate(table_rows[:50]):
                # 提取标题
                title_elem = row.select_one('td:first-child a, td a:first-child, .title a, a.title')
                if not title_elem:
                    title_elem = row.select_one('td:first-child, .title')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 2:
                        continue
                    
                    # 提取链接
                    href = ""
                    if title_elem.name == 'a':
                        href = title_elem.get('href', '')
                    else:
                        link_elem = row.select_one('a')
                        if link_elem:
                            href = link_elem.get('href', '')
                    
                    # 构建完整URL
                    if href:
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                url_full = f"https://tophub.today{href}"
                            else:
                                url_full = f"https://tophub.today/{href}"
                        else:
                            url_full = href
                    else:
                        url_full = platform_url or f"https://tophub.today/"
                    
                    # 提取热度值
                    hot_elem = row.select_one('td:last-child, .hot, .score, .heat, td:nth-child(2)')
                    hot_value = 0
                    if hot_elem:
                        hot_text = hot_elem.get_text(strip=True)
                        # 处理中文数字（如"100万"、"1.2万"）
                        hot_text = hot_text.replace('万', '0000').replace('千', '000').replace('次播放', '').replace('实时讨论', '')
                        hot_match = re.search(r'(\d+(?:\.\d+)?)', hot_text.replace(',', ''))
                        if hot_match:
                            try:
                                num = float(hot_match.group(1))
                                hot_value = int(num)
                            except:
                                pass
                    
                    # 提取描述（如果有）
                    desc_elem = row.select_one('td:nth-child(2), .desc, .description')
                    desc = ""
                    if desc_elem and desc_elem != hot_elem:
                        desc = desc_elem.get_text(strip=True)
                    
                    result.append({
                        "id": str(idx),
                        "title": title,
                        "desc": desc,
                        "cover": "",
                        "hot": hot_value,
                        "timestamp": 0,
                        "url": url_full,
                        "mobileUrl": url_full,
                    })
            
            if result:
                return result
        
        return []
        
    except Exception as e:
        return []
