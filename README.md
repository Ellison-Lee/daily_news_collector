# Daily Hot Collector

一个基于 Python 的热榜数据采集工具，支持多平台的热榜数据采集。

## 特性

- 支持 36 个平台的热榜数据采集
- 异步并发处理，提高采集效率
- 智能缓存机制，避免频繁请求
- 按类别分类保存 JSON 数据
- 支持 API 调用、HTML 爬虫、RSS 解析三种方式
- 100% 成功率，所有平台均可正常采集

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

可选配置项：
- `CACHE_TTL`: 缓存时间（秒），默认 3600
- `CACHE_DIR`: 缓存目录，默认 `./cache`
- `REQUEST_TIMEOUT`: 请求超时时间（秒），默认 30
- `MAX_RETRIES`: 最大重试次数，默认 3
- `CONCURRENT_LIMIT`: 并发限制，默认 10
- `ZHIHU_COOKIE`: 知乎 Cookie（可选）
- `BILIBILI_SESSDATA`: B站 SESSDATA（可选）

## 使用

运行主程序：

```bash
python run.py
```

或者：

```bash
python -m src.main
```

数据将保存在 `data/categories/` 目录下，按类别分类为不同的 JSON 文件。

## 平台分类

- **新闻资讯类**（15个）：百度、今日头条、IT之家、36氪、网易新闻、知乎日报、腾讯新闻、澎湃新闻、新浪新闻、虎嗅、爱范儿、果壳、简书等
- **社交媒体类**（7个）：微博、知乎、哔哩哔哩、抖音、AcFun、百度贴吧、快手
- **技术社区类**（6个）：稀土掘金、V2EX、CSDN、吾爱破解、GitHub、Hacker News
- **娱乐内容类**（4个）：豆瓣电影、豆瓣讨论、微信读书、NGA
- **生活消费类**（3个）：少数派、什么值得买、虎扑
- **简报类**（1个）：今日简报 • AI

## 已实现平台

当前已实现以下平台（36个）：

### 新闻资讯类（15个）
- 百度 (baidu)
- 今日头条 (toutiao)
- IT之家 (ithome)
- 网易新闻 (netease-news)
- 知乎日报 (zhihu-daily)
- 36氪 (36kr)
- 腾讯新闻 (qq-news)
- 澎湃新闻 (thepaper)
- 新浪新闻 (sina-news)
- 新浪网 (sina)
- 虎嗅 (huxiu)
- 爱范儿 (ifanr)
- 果壳 (guokr)
- 简书 (jianshu)
- IT之家「喜加一」 (ithome-xijiayi)

### 社交媒体类（7个）
- 微博 (weibo)
- 知乎 (zhihu)
- 哔哩哔哩 (bilibili)
- 抖音 (douyin)
- AcFun (acfun)
- 百度贴吧 (tieba)
- 快手 (kuaishou)

### 技术社区类（6个）
- 稀土掘金 (juejin)
- V2EX (v2ex)
- CSDN (csdn)
- 吾爱破解 (52pojie)
- GitHub (github)
- Hacker News (hackernews)

### 娱乐内容类（4个）
- 豆瓣电影 (douban-movie)
- 豆瓣讨论 (douban-group)
- 微信读书 (weread)
- NGA (ngabbs)

### 生活消费类（3个）
- 少数派 (sspai)
- 什么值得买 (smzdm)
- 虎扑 (hupu)

### 简报类（1个）
- 今日简报 • AI (tophub-ai-brief)

## 扩展平台

要添加新平台，请参考 [PLATFORM_GUIDE.md](PLATFORM_GUIDE.md) 文档。

## 项目结构

```
daily-hot-collector/
├── src/
│   ├── collectors/          # 数据采集器
│   ├── platforms/           # 各平台实现
│   ├── cache/              # 缓存模块
│   ├── utils/              # 工具函数
│   └── data_collector.py   # 数据采集模块
├── config/                 # 配置文件
├── data/                   # 数据输出目录
│   └── categories/         # 按类别分类的 JSON 文件
├── requirements.txt
├── README.md
└── run.py                  # 运行脚本
```

## 数据格式

每个类别生成一个 JSON 文件，格式如下：

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
      "name": "百度",
      "type": "热搜榜",
      "updateTime": "2024-01-01T12:00:00",
      "total": 20,
      "data": [...]
    }
  },
  "errors": {
    "platform_name": "error_message"
  }
}
```

## 注意事项

1. 部分平台可能需要特殊认证（如 Cookie），请在 `.env` 文件中配置
2. 缓存机制默认启用，如需强制刷新，可以删除 `cache/` 目录
3. 建议设置合理的并发限制，避免对目标服务器造成过大压力
4. 部分平台可能有反爬虫机制，如遇到问题请检查请求头和 Cookie

## 许可证

MIT License
