# Daily News Collector

<div align="center">
<img src="https://raw.githubusercontent.com/pudding0503/github-badge-collection/main/gif/3.gif" width="50%" alt="daily_news_collector">
</div>

<div align="center">

![Chrome](https://img.shields.io/badge/Chrome-Supported-000000?style=for-the-badge&logo=google-chrome&logoColor=000000&labelColor=FFD700)
![GitHub](https://img.shields.io/badge/GitHub-Ellison--Lee-000000?style=for-the-badge&logo=github&logoColor=000000&labelColor=FFD700)
![Python](https://img.shields.io/badge/Python-3.8+-000000?style=for-the-badge&logo=python&logoColor=000000&labelColor=FFD700)
![Cursor](https://img.shields.io/badge/Cursor-IDE-000000?style=for-the-badge&logo=cursor&logoColor=000000&labelColor=FFD700)
![Release](https://img.shields.io/badge/Release-v1.0.0-000000?style=for-the-badge&labelColor=FFD700)
![License](https://img.shields.io/badge/License-MIT-000000?style=for-the-badge&labelColor=FFD700)

一个强大的多平台热榜数据采集工具，支持 50+ 个主流平台的热榜数据采集与聚合。

</div>

## 项目简介

Daily News Collector 是一个基于 Python 的异步热榜数据采集系统，能够从多个平台（包括新闻资讯、社交媒体、技术社区等）采集热榜数据，并按类别进行分类整理。项目采用异步并发处理，支持智能缓存机制，确保高效稳定的数据采集。

## 核心特性

- **异步并发处理** - 采用 asyncio 实现高效的并发采集，大幅提升采集速度
- **智能缓存机制** - 内置缓存系统，避免频繁请求，减少对目标服务器的压力
- **多格式输出** - 支持 JSON 和 CSV 格式，按日期和类别自动分类保存
- **多种采集方式** - 支持 API 调用、HTML 爬虫、RSS 解析三种采集方式
- **容错机制** - 完善的错误处理和重试机制，部分平台支持备用数据源
- **详细日志** - 完整的日志记录系统，方便问题排查和监控
- **高成功率** - 经过优化的采集策略，确保各平台数据采集的稳定性

## 支持的平台

项目目前支持 **47 个平台**，涵盖以下类别：

### 新闻资讯类（18个）

| 平台名称 | 平台标识符 | 平台名称 | 平台标识符 |
|---------|-----------|---------|-----------|
| 百度 | `baidu` | 今日头条 | `toutiao` |
| IT之家 | `ithome` | 36氪 | `36kr` |
| 网易新闻 | `netease-news` | 知乎日报 | `zhihu-daily` |
| 腾讯新闻 | `qq-news` | 澎湃新闻 | `thepaper` |
| 新浪新闻 | `sina-news` | 新浪网 | `sina` |
| 虎嗅 | `huxiu` | 爱范儿 | `ifanr` |
| 果壳 | `guokr` | 简书 | `jianshu` |
| IT之家「喜加一」 | `ithome-xijiayi` | 机器之心 | `jiqizhixin` |
| 量子位 | `qbitai` | ReadHub | `readhub` |

### 社交媒体类（9个）

| 平台名称 | 平台标识符 | 平台名称 | 平台标识符 |
|---------|-----------|---------|-----------|
| 微博 | `weibo` | 知乎 | `zhihu` |
| 哔哩哔哩 | `bilibili` | 抖音 | `douyin` |
| AcFun | `acfun` | 百度贴吧 | `tieba` |
| 快手 | `kuaishou` | 微信热点 | `wechat-hot` |
| 即刻 | `jike` | | |

### 技术社区类（7个）

| 平台名称 | 平台标识符 | 平台名称 | 平台标识符 |
|---------|-----------|---------|-----------|
| 稀土掘金 | `juejin` | V2EX | `v2ex` |
| CSDN | `csdn` | 吾爱破解 | `52pojie` |
| GitHub | `github` | Hacker News | `hackernews` |
| 开源中国 | `oschina` | | |

### 娱乐内容类（5个）

| 平台名称 | 平台标识符 | 平台名称 | 平台标识符 |
|---------|-----------|---------|-----------|
| 豆瓣电影 | `douban-movie` | 豆瓣讨论 | `douban-group` |
| 微信读书 | `weread` | NGA | `ngabbs` |
| TapTap | `taptap` | | |

### 生活消费类（3个）

| 平台名称 | 平台标识符 | 平台名称 | 平台标识符 |
|---------|-----------|---------|-----------|
| 少数派 | `sspai` | 什么值得买 | `smzdm` |
| 虎扑 | `hupu` | | |

### 金融财经类（1个）

| 平台名称 | 平台标识符 |
|---------|-----------|
| 雪球 | `xueqiu` |

### 设计创意类（1个）

| 平台名称 | 平台标识符 |
|---------|-----------|
| 站酷 | `zcool` |

### 汽车类（2个）

| 平台名称 | 平台标识符 | 平台名称 | 平台标识符 |
|---------|-----------|---------|-----------|
| 懂车帝 | `dongchedi` | 汽车之家 | `autohome` |

### 简报类（1个）

| 平台名称 | 平台标识符 |
|---------|-----------|
| 今日简报 • AI | `tophub-ai-brief` |

## 快速开始

> [!IMPORTANT]
> 确保你的 Python 版本 >= 3.8，否则可能无法正常运行。

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone git@github.com:Ellison-Lee/daily_news_collector.git
cd daily_news_collector
```

2. **安装依赖**

> [!TIP]
> 建议使用虚拟环境来管理依赖，避免与系统 Python 环境冲突。

```bash
pip install -r requirements.txt
```

3. **运行采集**
```bash
python run.py
```

### 配置说明

> [!NOTE]
> 项目支持通过环境变量进行配置（可选），创建 `.env` 文件：

```bash
# 缓存配置
CACHE_TTL=3600              # 缓存时间（秒），默认 3600
CACHE_DIR=./cache          # 缓存目录，默认 ./cache

# 请求配置
REQUEST_TIMEOUT=30          # 请求超时时间（秒），默认 30
MAX_RETRIES=3              # 最大重试次数，默认 3
CONCURRENT_LIMIT=10        # 并发限制，默认 10

# 平台认证（可选）
ZHIHU_COOKIE=              # 知乎 Cookie（可选）
BILIBILI_SESSDATA=         # B站 SESSDATA（可选）
```

## 项目结构

```
daily_news_collector/
├── src/
│   ├── collectors/          # 数据采集器基类
│   │   ├── base.py         # 基础采集器
│   │   ├── api_collector.py # API 采集器
│   │   ├── html_collector.py # HTML 采集器
│   │   └── rss_collector.py # RSS 采集器
│   ├── platforms/          # 各平台实现
│   │   ├── base_platform.py # 平台基类
│   │   ├── registry.py     # 平台注册表
│   │   └── *.py            # 各平台具体实现
│   ├── utils/              # 工具函数
│   │   ├── http_client.py  # HTTP 客户端
│   │   ├── time_utils.py   # 时间工具
│   │   ├── number_utils.py # 数字工具
│   │   └── tophub_helper.py # TopHub 辅助工具
│   ├── data_collector.py   # 数据采集主模块
│   └── get_ai_summary.py   # AI 总结模块（可选）
├── data/                   # 数据输出目录
│   └── YYYY-MM-DD/        # 按日期分类
│       └── categories/     # 按类别分类的 JSON 文件
├── logs/                   # 日志目录
├── cache/                  # 缓存目录
├── requirements.txt        # 依赖列表
├── run.py                  # 运行脚本
└── README.md              # 项目说明
```

## 输出格式

### JSON 格式

数据按类别保存为 JSON 文件，格式如下：

```json
{
  "category": "新闻资讯",
  "timestamp": "2024-01-01T12:00:00",
  "total_platforms": 15,
  "successful_platforms": 15,
  "failed_platforms": 0,
  "total_items": 500,
  "platforms": {
    "baidu": {
      "name": "baidu",
      "title": "百度",
      "type": "热搜榜",
      "description": "百度实时热点",
      "link": "https://www.baidu.com",
      "updateTime": "2024-01-01T12:00:00",
      "total": 20,
      "data": [
        {
          "title": "热点标题",
          "url": "https://example.com",
          "hot": "100万"
        }
      ]
    }
  },
  "errors": {}
}
```

### CSV 格式

同时生成 `daily_hot_titles.csv` 文件，包含所有平台的标题数据：

| 类别 | 平台 | 标题 |
|------|------|------|
| 新闻资讯 | 百度 | 热点标题1 |
| 新闻资讯 | 百度 | 热点标题2 |

## 使用示例

### 基本使用

```bash
# 运行完整采集流程
python run.py
```

### 数据输出位置

- JSON 文件：`data/YYYY-MM-DD/categories/类别名.json`
- CSV 文件：`data/daily_hot_titles.csv`
- 日志文件：`logs/daily_hot_collector.log`

## 技术栈

**主要技术：**
- **异步框架**: asyncio
- **HTTP 客户端**: aiohttp
- **HTML 解析**: BeautifulSoup4, lxml, parsel
- **RSS 解析**: feedparser
- **缓存**: diskcache
- **日志**: loguru
- **其他**: python-dotenv, chardet, brotli

## 注意事项

> [!NOTE]
> **请求频率** - 请合理设置并发限制，避免对目标服务器造成过大压力
> 
> **认证信息** - 部分平台可能需要 Cookie 或 Token，请在 `.env` 文件中配置
> 
> **缓存机制** - 默认启用缓存，如需强制刷新可删除 `cache/` 目录
> 
> **日志管理** - 日志文件超过 5MB 时会自动截断，保留最新内容
> 
> **反爬虫** - 部分平台可能有反爬虫机制，如遇到问题请检查请求头和认证信息

## 开发指南

### 添加新平台

> [!TIP]
> 添加新平台时，建议先查看现有平台的实现示例，了解不同采集器的使用方式。

1. 在 `src/platforms/` 目录下创建新的平台文件
2. 继承 `BasePlatform` 或相应的采集器类
3. 实现 `get_route_data()` 方法
4. 在 `registry.py` 中注册新平台

### 扩展采集器

项目支持三种采集器类型：
- `APICollector` - 适用于提供 API 的平台
- `HTMLCollector` - 适用于需要解析 HTML 的平台
- `RSSCollector` - 适用于提供 RSS 订阅的平台

## 路线图

### 下一步迭代计划

#### 🤖 AI Agents 日报分析功能

我们计划在下一版本中集成 AI Agents 技术，实现智能日报分析功能：

**核心功能：**
- 📊 **智能内容分析** - 使用 AI Agents 对采集的热榜数据进行深度分析
- 🎯 **趋势预测** - 分析热点趋势，预测未来可能的热门话题
- 🔍 **内容分类与标签** - 智能识别内容主题，自动打标签和分类
- 💡 **关键信息提取** - 从海量数据中提取关键信息和洞察
- 📈 **数据可视化** - 生成图表和可视化报告，直观展示热点分布

**技术实现：**
- 集成主流 AI 模型（如 OpenAI GPT、Claude、国产大模型等）
- 构建多 Agent 协作系统，实现数据采集、分析、总结的自动化流程
- 支持自定义分析模板和报告格式
- 提供 API 接口，方便与其他系统集成

**预期效果：**
- 从原始数据采集到智能分析报告的全流程自动化
- 提供更深入、更有价值的洞察，而不仅仅是数据聚合
- 支持个性化定制，满足不同用户的分析需求

**开发进度：**
- [ ] AI Agents 框架设计与实现
- [ ] 日报生成模块开发
- [ ] 数据分析与洞察提取
- [ ] 报告模板系统
- [ ] API 接口开发
- [ ] 文档与示例完善

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 支持 50+ 个平台的数据采集
- 实现异步并发处理
- 添加智能缓存机制
- 支持 JSON 和 CSV 格式输出
