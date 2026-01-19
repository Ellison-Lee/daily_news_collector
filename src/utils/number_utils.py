"""数字工具函数"""


def parse_chinese_number(chinese_number: str) -> float:
    """解析中文数字"""
    if not chinese_number:
        return 0.0
    
    # 单位对照表
    units = {
        "亿": 1e8,
        "万": 1e4,
        "千": 1e3,
        "百": 1e2,
    }
    
    # 移除逗号
    chinese_number = chinese_number.replace(",", "")
    
    # 遍历单位对照表
    for unit, multiplier in units.items():
        if unit in chinese_number:
            # 转换为数字
            number_part = float(chinese_number.replace(unit, ""))
            return number_part * multiplier
    
    try:
        return float(chinese_number)
    except (ValueError, TypeError):
        return 0.0
