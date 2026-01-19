"""TopHub 备用数据获取工具"""

import json
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

from ..utils.http_client import HTTPClient


async def fetch_douyin_from_tophub(http_client: HTTPClient) -> List[Dict[str, Any]]:
    """从 TopHub 获取抖音总榜数据"""
    try:
        # 直接访问首页，查找抖音总榜的链接
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
        
        # 查找抖音总榜的链接 - 搜索包含"抖音"和"总榜"的链接
        douyin_url = None
        links = soup.find_all('a', href=True)
        
        for link in links:
            link_text = link.get_text(strip=True)
            href = link.get('href', '')
            # 检查链接文本或父元素文本
            parent_text = ""
            if link.parent:
                parent_text = link.parent.get_text()
            
            if ('抖音' in link_text or '抖音' in parent_text) and ('总榜' in link_text or '总榜' in parent_text or '/n/' in href):
                if '/n/' in href:
                    douyin_url = href if href.startswith('http') else f"https://tophub.today{href}"
                    break
        
        # 如果找到了链接，访问该页面
        if douyin_url:
            page_html = await http_client.get(
                url=douyin_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Referer": "https://tophub.today/",
                },
                response_type="text"
            )
            
            soup = BeautifulSoup(page_html, 'html.parser')
        
        # 解析表格数据 - 查找常见的表格结构
        table_rows = soup.select('table tbody tr')
        if not table_rows:
            # 尝试其他选择器
            table_rows = soup.select('.table tbody tr, .list tbody tr, tbody tr')
        
        if table_rows:
            result = []
            for idx, row in enumerate(table_rows[:50]):
                # 提取标题 - 通常在第一个td或a标签中
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
                        url_full = f"https://www.douyin.com/hot/{idx}"
                    
                    # 提取热度值 - 通常在最后一个td中
                    hot_elem = row.select_one('td:last-child, .hot, .score, .heat, td:nth-child(2)')
                    hot_value = 0
                    if hot_elem:
                        hot_text = hot_elem.get_text(strip=True)
                        # 处理中文数字（如"100万"、"1.2万"）
                        hot_text = hot_text.replace('万', '0000').replace('千', '000').replace('次播放', '')
                        hot_match = re.search(r'(\d+(?:\.\d+)?)', hot_text.replace(',', ''))
                        if hot_match:
                            try:
                                num = float(hot_match.group(1))
                                hot_value = int(num)
                            except:
                                pass
                    
                    result.append({
                        "id": str(idx),
                        "title": title,
                        "timestamp": 0,
                        "hot": hot_value,
                        "url": url_full,
                        "mobileUrl": url_full,
                    })
            
            if result:
                return result
        
        return []
        
    except Exception as e:
        return []


async def fetch_tieba_from_tophub(http_client: HTTPClient) -> List[Dict[str, Any]]:
    """从 TopHub 获取百度贴吧热议榜数据"""
    try:
        # 直接访问首页，查找百度贴吧热议榜的链接
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
        
        # 查找百度贴吧热议榜的链接 - 搜索包含"贴吧"和"热议"的链接
        tieba_url = None
        links = soup.find_all('a', href=True)
        
        for link in links:
            link_text = link.get_text(strip=True)
            href = link.get('href', '')
            # 检查链接文本或父元素文本
            parent_text = ""
            if link.parent:
                parent_text = link.parent.get_text()
            
            if ('贴吧' in link_text or '贴吧' in parent_text) and ('热议' in link_text or '热议' in parent_text or '/n/' in href):
                if '/n/' in href:
                    tieba_url = href if href.startswith('http') else f"https://tophub.today{href}"
                    break
        
        # 如果找到了链接，访问该页面
        if tieba_url:
            page_html = await http_client.get(
                url=tieba_url,
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
                        url_full = f"https://tieba.baidu.com/hottopic/browse/topicList"
                    
                    # 提取热度值
                    hot_elem = row.select_one('td:last-child, .hot, .score, .heat, td:nth-child(2)')
                    hot_value = 0
                    if hot_elem:
                        hot_text = hot_elem.get_text(strip=True)
                        # 处理中文数字（如"100万"、"1.2万"）
                        hot_text = hot_text.replace('万', '0000').replace('千', '000').replace('实时讨论', '')
                        hot_match = re.search(r'(\d+(?:\.\d+)?)', hot_text.replace(',', ''))
                        if hot_match:
                            try:
                                num = float(hot_match.group(1))
                                hot_value = int(num)
                            except:
                                pass
                    
                    result.append({
                        "id": str(idx),
                        "title": title,
                        "desc": "",
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
