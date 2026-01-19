"""数据采集模块 - 负责采集所有平台的热榜数据"""

import asyncio
import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Any

from loguru import logger

from .platforms.registry import get_all_platforms, get_platforms_by_category, CATEGORIES
from .utils.tophub_fallback import fetch_douyin_from_tophub, fetch_tieba_from_tophub
from .utils.http_client import HTTPClient
from .utils.time_utils import format_time


def truncate_log_file_half(file_path: str, max_size: int = 5 * 1024 * 1024):
    """
    当日志文件超过指定大小时，删除前一半内容，保留后一半
    
    Args:
        file_path: 日志文件路径
        max_size: 最大文件大小（字节），默认5MB
    """
    if not os.path.exists(file_path):
        return
    
    file_size = os.path.getsize(file_path)
    
    if file_size <= max_size:
        return
    
    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 如果文件很小或只有很少行，直接清空
        if len(lines) < 10:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")
            return
        
        # 保留后一半内容
        half_point = len(lines) // 2
        
        # 找到第一个完整行的开始位置（避免截断中间的行）
        # 向后查找换行符，确保从完整行开始
        while half_point < len(lines) and not lines[half_point].endswith('\n'):
            half_point += 1
        
        # 如果找不到合适的位置，就保留最后1/3
        if half_point >= len(lines):
            half_point = len(lines) * 2 // 3
        
        # 写入后一半内容
        with open(file_path, "w", encoding="utf-8") as f:
            # 添加一个标记，说明日志被截断
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | INFO     | [日志文件已截断，保留后 {len(lines) - half_point} 行]\n")
            f.writelines(lines[half_point:])
        
        # 使用 print 而不是 logger，因为此时 logger 可能还未完全初始化
        print(f"[日志截断] {file_path}, 原始大小: {file_size} bytes, 保留行数: {len(lines) - half_point}")
    except Exception as e:
        print(f"[错误] 截断日志文件失败: {e}")


def should_rotate_log(record, file):
    """
    自定义轮转函数：当日志文件超过5MB时，删除前一半内容
    
    Args:
        record: 日志记录
        file: 文件对象
    
    Returns:
        bool: 是否需要轮转（这里返回False，因为我们手动处理）
    """
    file_path = file.name
    max_size = 5 * 1024 * 1024  # 5MB
    
    # 检查文件大小
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            # 在写入新日志前截断文件
            truncate_log_file_half(file_path, max_size)
    
    # 返回False，表示不进行默认轮转，继续在原文件写入
    return False


def setup_logger():
    """配置日志"""
    # 获取项目根目录（run.py 所在的目录）
    # data_collector.py 在 src/ 目录下，所以项目根目录是 src 的上一级
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_file_dir)
    
    # 移除默认的处理器
    logger.remove()
    
    # 添加控制台输出（带颜色）
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    
    # 添加文件输出（日志文件，超过5MB时删除前一半内容）
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "daily_hot_collector.log")
    
    # 启动时检查文件大小，如果超过5MB则先截断
    truncate_log_file_half(log_file, 5 * 1024 * 1024)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation=should_rotate_log,  # 使用自定义轮转函数（超过5MB时删除前一半内容）
        encoding="utf-8",
        enqueue=True,  # 异步写入，提高性能
    )
    
    return logger


async def collect_platform(platform_name: str, platform_instance, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """采集单个平台数据"""
    async with semaphore:
        # 保存平台实例的属性，以便在close后使用
        platform_title = platform_instance.title
        platform_type = platform_instance.type
        platform_description = platform_instance.description
        platform_link = platform_instance.link
        
        try:
            # 先尝试使用缓存
            result = await platform_instance.get_route_data(no_cache=False)
            total_items = result.get("total", 0)
            
            # 如果缓存中的数据为0条，强制重新采集
            if total_items == 0 and result.get("fromCache", False):
                logger.info(f"平台 {platform_name} 缓存数据为0条，强制重新采集...")
                result = await platform_instance.get_route_data(no_cache=True)
                total_items = result.get("total", 0)
            
            await platform_instance.close()
            
            # 必须是采集数据数 >= 1 才算是成功采集
            if total_items >= 1:
                logger.info(f"✓ 平台 {platform_name} 采集成功，共 {total_items} 条数据")
                return {
                    "success": True,
                    "platform": platform_name,
                    "data": result,
                    "error": None,
                }
            else:
                logger.warning(f"✗ 平台 {platform_name} 采集失败: 采集数据数为0")
                
                # 如果是 douyin 或 tieba，尝试从 TopHub 获取备用数据
                if platform_name in ["douyin", "tieba"]:
                    logger.info(f"尝试从 TopHub 获取 {platform_name} 备用数据...")
                    try:
                        fallback_http_client = HTTPClient()
                        
                        if platform_name == "douyin":
                            fallback_data = await fetch_douyin_from_tophub(fallback_http_client)
                        elif platform_name == "tieba":
                            fallback_data = await fetch_tieba_from_tophub(fallback_http_client)
                        else:
                            fallback_data = []
                        
                        await fallback_http_client.close()
                        
                        if fallback_data and len(fallback_data) >= 1:
                            # 构建与原始格式一致的结果
                            fallback_result = {
                                "name": result.get("name", platform_name),
                                "title": result.get("title", platform_title),
                                "type": result.get("type", platform_type),
                                "description": result.get("description", platform_description),
                                "link": result.get("link", platform_link),
                                "total": len(fallback_data),
                                "fromCache": False,
                                "updateTime": format_time(),
                                "data": fallback_data,
                            }
                            
                            logger.info(f"✓ 平台 {platform_name} 从 TopHub 备用方案采集成功，共 {len(fallback_data)} 条数据")
                            return {
                                "success": True,
                                "platform": platform_name,
                                "data": fallback_result,
                                "error": None,
                            }
                        else:
                            logger.warning(f"✗ 平台 {platform_name} TopHub 备用方案也失败: 未获取到数据")
                    except Exception as fallback_error:
                        logger.warning(f"✗ 平台 {platform_name} TopHub 备用方案失败: {str(fallback_error)}")
                
                return {
                    "success": False,
                    "platform": platform_name,
                    "data": None,
                    "error": "采集数据数为0",
                }
        except Exception as e:
            await platform_instance.close()
            logger.error(f"✗ 平台 {platform_name} 采集失败: {str(e)}")
            
            # 如果是 douyin 或 tieba，尝试从 TopHub 获取备用数据
            if platform_name in ["douyin", "tieba"]:
                logger.info(f"尝试从 TopHub 获取 {platform_name} 备用数据...")
                try:
                    fallback_http_client = HTTPClient()
                    
                    if platform_name == "douyin":
                        fallback_data = await fetch_douyin_from_tophub(fallback_http_client)
                    elif platform_name == "tieba":
                        fallback_data = await fetch_tieba_from_tophub(fallback_http_client)
                    else:
                        fallback_data = []
                    
                    await fallback_http_client.close()
                    
                    if fallback_data and len(fallback_data) >= 1:
                        # 构建与原始格式一致的结果
                        fallback_result = {
                            "name": platform_name,
                            "title": platform_title,
                            "type": platform_type,
                            "description": platform_description,
                            "link": platform_link,
                            "total": len(fallback_data),
                            "fromCache": False,
                            "updateTime": format_time(),
                            "data": fallback_data,
                        }
                        
                        logger.info(f"✓ 平台 {platform_name} 从 TopHub 备用方案采集成功，共 {len(fallback_data)} 条数据")
                        return {
                            "success": True,
                            "platform": platform_name,
                            "data": fallback_result,
                            "error": None,
                        }
                    else:
                        logger.warning(f"✗ 平台 {platform_name} TopHub 备用方案也失败: 未获取到数据")
                except Exception as fallback_error:
                    logger.warning(f"✗ 平台 {platform_name} TopHub 备用方案失败: {str(fallback_error)}")
            
            return {
                "success": False,
                "platform": platform_name,
                "data": None,
                "error": str(e),
            }


async def collect_all_platforms(concurrent_limit: int = 10) -> Dict[str, Any]:
    """采集所有平台数据"""
    platforms = get_all_platforms()
    semaphore = asyncio.Semaphore(concurrent_limit)
    
    tasks = [
        collect_platform(name, platform, semaphore)
        for name, platform in platforms.items()
    ]
    
    # 处理结果（实时处理完成的任务）
    all_results = {}
    errors = {}
    
    # 使用 as_completed 来实时处理完成的任务
    for task in asyncio.as_completed(tasks):
        try:
            result = await task
            platform_name = result["platform"]
            if result["success"]:
                all_results[platform_name] = result["data"]
            else:
                errors[platform_name] = result["error"]
        except Exception as e:
            logger.error(f"✗ 平台采集异常: {str(e)}")
    
    return {
        "results": all_results,
        "errors": errors,
    }


def group_by_category(data: Dict[str, Any]) -> Dict[str, Any]:
    """按类别分组数据"""
    categorized = {}
    
    for category, platform_names in CATEGORIES.items():
        category_data = {
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "total_platforms": len(platform_names),
            "successful_platforms": 0,
            "failed_platforms": 0,
            "total_items": 0,
            "platforms": {},
            "errors": {},
        }
        
        for platform_name in platform_names:
            if platform_name in data["results"]:
                platform_data = data["results"][platform_name]
                category_data["platforms"][platform_name] = platform_data
                category_data["successful_platforms"] += 1
                category_data["total_items"] += platform_data.get("total", 0)
            elif platform_name in data["errors"]:
                category_data["errors"][platform_name] = data["errors"][platform_name]
                category_data["failed_platforms"] += 1
        
        categorized[category] = category_data
    
    return categorized


def save_to_json(data: Dict[str, Any], base_dir: str = "data"):
    """保存数据到 JSON 文件，按当天日期创建文件夹"""
    # 获取当天日期，格式：YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 构建输出目录：data/YYYY-MM-DD/categories
    output_dir = os.path.join(base_dir, today, "categories")
    os.makedirs(output_dir, exist_ok=True)
    
    for category, category_data in data.items():
        filename = f"{category}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(category_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ 已保存: {filepath} ({category_data['total_items']} 条数据)")


def extract_titles_to_csv(categorized_data: Dict[str, Any], base_dir: str = "data"):
    """从分类数据中提取所有标题，生成CSV文件（每天覆盖）"""
    # 确保data目录存在
    os.makedirs(base_dir, exist_ok=True)
    
    # CSV文件路径：直接保存在data目录下，每天覆盖
    csv_filepath = os.path.join(base_dir, "daily_hot_titles.csv")
    
    # 提取标题数据
    titles_data = []
    
    for category, category_data in categorized_data.items():
        platforms = category_data.get("platforms", {})
        
        for platform_name, platform_data in platforms.items():
            platform_title = platform_data.get("title", platform_name)
            data_items = platform_data.get("data", [])
            
            for item in data_items:
                title = item.get("title", "").strip()
                # 只添加非空标题
                if title:
                    titles_data.append({
                        "类别": category,
                        "平台": platform_title,
                        "标题": title,
                    })
    
    # 写入CSV文件
    if titles_data:
        with open(csv_filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["类别", "平台", "标题"])
            writer.writeheader()
            writer.writerows(titles_data)
        
        logger.info(f"✓ 已生成标题CSV文件: {csv_filepath} ({len(titles_data)} 条标题)")
        return csv_filepath
    else:
        logger.warning("⚠ 未找到任何标题数据")
        return None


async def collect_data():
    """采集所有平台的热榜数据"""
    # 配置日志
    setup_logger()
    
    # 获取项目根目录（run.py 所在的目录）
    # data_collector.py 在 src/ 目录下，所以项目根目录是 src 的上一级
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_file_dir)
    data_dir = os.path.join(project_root, "data")
    
    logger.info("=" * 80)
    logger.info("Daily Hot Collector - 热榜数据采集工具")
    logger.info("=" * 80)
    start_time = datetime.now()
    logger.info(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # 采集所有平台数据
    logger.info("正在采集所有平台数据...")
    logger.info("")
    data = await collect_all_platforms(concurrent_limit=10)
    
    # 统计信息
    total_platforms = len(data["results"]) + len(data["errors"])
    successful_platforms = len(data["results"])
    failed_platforms = len(data["errors"])
    total_items = sum(
        platform_data.get("total", 0)
        for platform_data in data["results"].values()
    )
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("采集统计")
    logger.info("=" * 80)
    logger.info(f"总平台数: {total_platforms}")
    logger.info(f"成功: {successful_platforms}")
    logger.info(f"失败: {failed_platforms}")
    
    # 如果有失败的平台，列出它们的名字和错误信息
    if failed_platforms > 0:
        logger.warning("失败平台列表:")
        for platform_name, error_msg in data["errors"].items():
            logger.warning(f"  - {platform_name}: {error_msg}")
    
    logger.info(f"总数据条数: {total_items}")
    logger.info("")
    
    # 按类别分组
    logger.info("正在按类别分组数据...")
    categorized_data = group_by_category(data)
    
    # 保存到 JSON 文件
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"正在保存数据到 JSON 文件 (日期: {today})...")
    save_to_json(categorized_data, base_dir=data_dir)
    logger.info(f"数据保存路径: {os.path.join(data_dir, today, 'categories')}")
    
    # 提取标题生成CSV文件（每天覆盖）
    logger.info("")
    logger.info("正在提取标题生成CSV文件...")
    csv_path = extract_titles_to_csv(categorized_data, base_dir=data_dir)
    if csv_path:
        logger.info(f"CSV文件路径: {csv_path}")
    
    logger.info("")
    logger.info("=" * 80)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info("完成!")
    logger.info(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"耗时: {duration:.2f} 秒")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(collect_data())
