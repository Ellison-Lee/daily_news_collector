"""平台注册表"""

from .bilibili import BilibiliPlatform
from .weibo import WeiboPlatform
from .zhihu import ZhihuPlatform
from .baidu import BaiduPlatform
from .douban_movie import DoubanMoviePlatform
from .zhihu_daily import ZhihuDailyPlatform
from .juejin import JuejinPlatform
from .v2ex import V2exPlatform
from .toutiao import ToutiaoPlatform
from .netease_news import NeteaseNewsPlatform
from .ithome import IthomePlatform
from .platform_36kr import Platform36kr
from .douyin import DouyinPlatform
from .qq_news import QqNewsPlatform
from .thepaper import ThepaperPlatform
from .csdn import CsdnPlatform
from .acfun import AcfunPlatform
from .tieba import TiebaPlatform
from .sspai import SspaiPlatform
from .weread import WereadPlatform
from .hupu import HupuPlatform
from .douban_group import DoubanGroupPlatform
from .kuaishou import KuaishouPlatform
from .sina_news import SinaNewsPlatform
from .sina import SinaPlatform
from .huxiu import HuxiuPlatform
from .ifanr import IfanrPlatform
from .guokr import GuokrPlatform
from .jianshu import JianshuPlatform
from .platform_52pojie import Platform52pojie
from .github import GithubPlatform
from .hackernews import HackernewsPlatform
from .ngabbs import NgabbsPlatform
from .tophub_ai_brief import TopHubAIBriefPlatform
from .wechat_hot import WechatHotPlatform
from .jiqizhixin import JiqizhixinPlatform
from .qbitai import QbitaiPlatform
from .xueqiu import XueqiuPlatform
from .taptap import TaptapPlatform
from .oschina import OsChinaPlatform
from .readhub import ReadhubPlatform
from .jike import JikePlatform
from .zcool import ZcoolPlatform
from .dongchedi import DongchediPlatform
from .autohome import AutohomePlatform

# 平台注册表
PLATFORMS = {
    "bilibili": BilibiliPlatform,
    "weibo": WeiboPlatform,
    "zhihu": ZhihuPlatform,
    "baidu": BaiduPlatform,
    "douban-movie": DoubanMoviePlatform,
    "zhihu-daily": ZhihuDailyPlatform,
    "juejin": JuejinPlatform,
    "v2ex": V2exPlatform,
    "toutiao": ToutiaoPlatform,
    "netease-news": NeteaseNewsPlatform,
    "ithome": IthomePlatform,
    "36kr": Platform36kr,
    "douyin": DouyinPlatform,
    "qq-news": QqNewsPlatform,
    "thepaper": ThepaperPlatform,
    "csdn": CsdnPlatform,
    "acfun": AcfunPlatform,
    "tieba": TiebaPlatform,
    "sspai": SspaiPlatform,
    "weread": WereadPlatform,
    "hupu": HupuPlatform,
    "douban-group": DoubanGroupPlatform,
    "kuaishou": KuaishouPlatform,
    "sina-news": SinaNewsPlatform,
    "sina": SinaPlatform,
    "huxiu": HuxiuPlatform,
    "ifanr": IfanrPlatform,
    "guokr": GuokrPlatform,
    "jianshu": JianshuPlatform,
    "52pojie": Platform52pojie,
    "github": GithubPlatform,
    "hackernews": HackernewsPlatform,
    "ngabbs": NgabbsPlatform,
    "tophub-ai-brief": TopHubAIBriefPlatform,
    "wechat-hot": WechatHotPlatform,
    "jiqizhixin": JiqizhixinPlatform,
    "qbitai": QbitaiPlatform,
    "xueqiu": XueqiuPlatform,
    "taptap": TaptapPlatform,
    "oschina": OsChinaPlatform,
    "readhub": ReadhubPlatform,
    "jike": JikePlatform,
    "zcool": ZcoolPlatform,
    "dongchedi": DongchediPlatform,
    "autohome": AutohomePlatform,
}

# 平台分类
CATEGORIES = {
    "新闻资讯": ["baidu", "toutiao", "ithome", "netease-news", "zhihu-daily", "36kr", "qq-news", "thepaper", "sina-news", "sina", "huxiu", "ifanr", "guokr", "jianshu", "jiqizhixin", "qbitai", "readhub"],
    "社交媒体": ["weibo", "zhihu", "bilibili", "douyin", "acfun", "tieba", "kuaishou", "wechat-hot", "jike"],
    "技术社区": ["juejin", "v2ex", "csdn", "52pojie", "github", "hackernews", "oschina"],
    "娱乐内容": ["douban-movie", "douban-group", "weread", "ngabbs", "taptap"],
    "生活消费": ["sspai", "hupu"],
    "金融财经": ["xueqiu"],
    "设计创意": ["zcool"],
    "汽车": ["dongchedi", "autohome"],
    "简报": ["tophub-ai-brief"],
}


def get_platform(name: str):
    """获取平台实例"""
    platform_class = PLATFORMS.get(name)
    if platform_class:
        return platform_class()
    return None


def get_all_platforms():
    """获取所有平台实例"""
    return {name: cls() for name, cls in PLATFORMS.items()}


def get_platforms_by_category():
    """按类别获取平台"""
    result = {}
    for category, platform_names in CATEGORIES.items():
        result[category] = {
            name: PLATFORMS[name]()
            for name in platform_names
            if name in PLATFORMS
        }
    return result
