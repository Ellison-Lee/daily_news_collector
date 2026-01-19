#!/usr/bin/env python3
"""运行脚本"""

import sys
import os
import asyncio
from src.data_collector import collect_data
# from src.get_ai_summary import doubao_chat_example  # 已注释，暂不使用

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

async def run_all():
    """运行所有任务：数据采集 + AI总结"""
    
    # 1. 先运行数据采集
    await collect_data()
    
    # # 2. 然后运行AI总结
    # print("\n" + "=" * 80)
    # print("开始运行AI总结...")
    # print("=" * 80)
    
    # try:
    #     doubao_chat_example()
    # except Exception as e:
    #     raise

if __name__ == "__main__":
    asyncio.run(run_all())