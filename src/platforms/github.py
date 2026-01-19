"""GitHub 平台"""

from typing import Dict, List, Any

from bs4 import BeautifulSoup

from .base_platform import BasePlatform


class GithubPlatform(BasePlatform):
    """GitHub 平台"""
    
    def __init__(self):
        super().__init__()
        self.name = "github"
        self.title = "GitHub"
        self.type = "日榜"
        self.link = "https://github.com/trending"
        self.category = "技术社区"
    
    async def fetch(self, type: str = "daily", **kwargs) -> List[Dict[str, Any]]:
        """获取数据"""
        url = f"https://github.com/trending?since={type}"
        
        html = await self.http_client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            response_type="text"
        )
        
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article.Box-row")
        
        result = []
        for article in articles:
            # 仓库标题和链接
            repo_anchor = article.select_one("h2 a")
            if not repo_anchor:
                continue
            
            full_name_text = repo_anchor.get_text(strip=True).replace("\n", "").replace("  ", " ")
            parts = [s.strip() for s in full_name_text.split("/")]
            owner = parts[0] if len(parts) > 0 else ""
            repo_name = parts[1] if len(parts) > 1 else ""
            
            repo_url = "https://github.com" + repo_anchor.get("href", "")
            
            # 描述
            desc_elem = article.select_one("p.col-9.color-fg-muted")
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # 语言
            lang_elem = article.select_one('[itemprop="programmingLanguage"]')
            language = lang_elem.get_text(strip=True) if lang_elem else ""
            
            # Stars
            stars_elem = article.select_one('a[href$="/stargazers"]')
            stars = stars_elem.get_text(strip=True) if stars_elem else "0"
            
            # Forks
            forks_elem = article.select_one('a[href$="/forks"]')
            forks = forks_elem.get_text(strip=True) if forks_elem else "0"
            
            result.append({
                "id": f"{owner}/{repo_name}",
                "title": f"{owner}/{repo_name}",
                "desc": description,
                "author": owner,
                "hot": stars,
                "timestamp": None,
                "url": repo_url,
                "mobileUrl": repo_url,
            })
        
        return result
