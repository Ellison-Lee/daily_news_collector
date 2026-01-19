"""认证工具函数"""

import hashlib
import os
import re
import time
import base64
import random
import string
from typing import Dict, Optional

from dotenv import load_dotenv

from ..utils.http_client import HTTPClient

load_dotenv()

# B站 WBI 签名相关
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28,
    14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54,
    21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]


def get_mixin_key(orig: str) -> str:
    """对 imgKey 和 subKey 进行字符顺序打乱编码"""
    return "".join([orig[n] for n in MIXIN_KEY_ENC_TAB])[:32]


def enc_wbi(params: Dict, img_key: str, sub_key: str) -> str:
    """为请求参数进行 wbi 签名"""
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = int(time.time())
    
    # 添加 wts 字段
    params["wts"] = curr_time
    
    # 按照 key 重排参数
    query = "&".join([
        f"{key}={value}".replace("'", "").replace("(", "").replace(")", "").replace("*", "")
        for key, value in sorted(params.items())
    ])
    
    # 计算 w_rid
    wbi_sign = hashlib.md5((query + mixin_key).encode()).hexdigest()
    return f"{query}&w_rid={wbi_sign}"


async def get_bilibili_wbi(http_client: HTTPClient) -> str:
    """获取 B站 WBI 签名"""
    try:
        # 获取 keys
        result = await http_client.get(
            url="https://api.bilibili.com/x/web-interface/nav",
            headers={
                "Cookie": f"SESSDATA={os.getenv('BILIBILI_SESSDATA', '')}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.bilibili.com/",
            }
        )
        
        img_url = result.get("data", {}).get("wbi_img", {}).get("img_url", "")
        sub_url = result.get("data", {}).get("wbi_img", {}).get("sub_url", "")
        
        img_key = img_url.split("/")[-1].split(".")[0]
        sub_key = sub_url.split("/")[-1].split(".")[0]
        
        # 生成签名
        params = {"foo": "114", "bar": "514", "baz": 1919810}
        return enc_wbi(params, img_key, sub_key)
    except Exception as e:
        # 如果获取失败，返回空字符串
        return ""


def get_random_device_id() -> str:
    """获取随机的 DEVICE_ID"""
    id_lengths = [10, 6, 6, 6, 14]
    parts = []
    for length in id_lengths:
        part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        parts.append(part)
    return "-".join(parts)


def get_coolapk_token() -> str:
    """获取酷安 APP_TOKEN"""
    device_id = get_random_device_id()
    now = int(time.time())
    hex_now = "0x" + hex(now)[2:]
    md5_now = hashlib.md5(str(now).encode()).hexdigest()
    
    s = f"token://com.coolapk.market/c67ef5943784d09750dcfbb31020f0ab?{md5_now}${device_id}&com.coolapk.market"
    md5_s = hashlib.md5(base64.b64encode(s.encode())).hexdigest()
    token = md5_s + device_id + hex_now
    return token


def gen_coolapk_headers() -> Dict[str, str]:
    """生成酷安请求头"""
    return {
        "X-Requested-With": "XMLHttpRequest",
        "X-App-Id": "com.coolapk.market",
        "X-App-Token": get_coolapk_token(),
        "X-Sdk-Int": "29",
        "X-Sdk-Locale": "zh-CN",
        "X-App-Version": "11.0",
        "X-Api-Version": "11",
        "X-App-Code": "2101202",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mi 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.15 Mobile Safari/537.36",
    }


async def get_douyin_cookie(http_client: HTTPClient) -> Optional[str]:
    """获取抖音临时 Cookie"""
    try:
        url = "https://www.douyin.com/passport/general/login_guiding_strategy/?aid=6383"
        # 需要获取原始响应头
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                cookies = response.cookies
                if 'passport_csrf_token' in cookies:
                    return str(cookies['passport_csrf_token'].value)
                # 尝试从 Set-Cookie 头中提取
                set_cookie = response.headers.get('Set-Cookie', '')
                pattern = r'passport_csrf_token=([^;]+)'
                match = re.search(pattern, set_cookie)
                if match:
                    return match.group(1)
    except Exception:
        pass
    return None
