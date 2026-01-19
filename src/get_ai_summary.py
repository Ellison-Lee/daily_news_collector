"""
使用 undetected-chromedriver 模拟用户打开豆包网页并发送一条消息
基于 https://www.doubao.com/chat/ 页面分析

前置要求：
  首次运行前需要安装 Chrome 浏览器和 undetected-chromedriver：
  pip install undetected-chromedriver selenium

登录状态保持：
  程序使用持久化浏览器上下文，首次运行需要手动登录一次，
  之后会自动保持登录状态，无需重复登录。
  登录信息保存在 .browser_data 目录中。
"""

import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# #region agent log
# Debug logging configuration
DEBUG_LOG_PATH = Path("/Users/lisheng/Documents/Working File/.cursor/debug.log")

def debug_log(hypothesis_id, location, message, data=None):
    """写入调试日志"""
    try:
        log_entry = {
            "sessionId": "debug-session",
            "runId": "test-agent",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000)
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        pass  # 静默失败，不影响主流程
# #endregion

# CSV文件路径（相对于工作区根目录）
CSV_FILE_PATH = Path(__file__).parent.parent / 'data' / 'daily_hot_titles.csv'

def load_csv_content():
    """读取CSV文件内容并格式化为文本"""
    # #region agent log
    debug_log("A", "get_ai_summary.py:load_csv_content", "开始加载CSV文件", {"path": str(CSV_FILE_PATH)})
    # #endregion
    try:
        if not CSV_FILE_PATH.exists():
            # #region agent log
            debug_log("A", "get_ai_summary.py:load_csv_content", "CSV文件不存在", {"path": str(CSV_FILE_PATH)})
            # #endregion
            print(f"CSV文件不存在: {CSV_FILE_PATH}")
            return ""
        
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            # #region agent log
            debug_log("A", "get_ai_summary.py:load_csv_content", "CSV文件为空", {"path": str(CSV_FILE_PATH)})
            # #endregion
            return ""
        
        # 格式化CSV内容为文本
        content_lines = []
        for row in rows:
            category = row.get('类别', '')
            platform = row.get('平台', '')
            title = row.get('标题', '')
            if title:
                content_lines.append(f"{category} | {platform} | {title}")
        
        result = '\n'.join(content_lines)
        # #region agent log
        debug_log("A", "get_ai_summary.py:load_csv_content", "CSV文件加载成功", {"row_count": len(rows), "content_length": len(result)})
        # #endregion
        return result
    except Exception as e:
        # #region agent log
        debug_log("A", "get_ai_summary.py:load_csv_content", "CSV文件加载失败", {"error": str(e)})
        # #endregion
        print(f"读取CSV文件时出错: {e}")
        return ""

# 注意：CSV内容在函数内部动态加载，确保每次调用时都使用最新的数据

# 用户数据目录路径（用于保存登录状态）
USER_DATA_DIR = Path(__file__).parent / '.browser_data'

# 保存回答的目录
RESPONSES_DIR = Path(__file__).parent / 'responses'
RESPONSES_DIR.mkdir(exist_ok=True)

# Chrome 二进制文件路径（如果为 None，则使用系统默认的 Chrome）
# 示例路径（根据实际情况修改）:
# macOS: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
# Windows: r'C:\Program Files\Google\Chrome\Application\chrome.exe'
# Linux: '/usr/bin/google-chrome'
# 便携版 Chrome: '/path/to/chrome-portable/chrome.exe'
CHROME_BINARY_PATH = None  # 设置为 None 使用系统 Chrome，或指定自定义路径

# 性能优化选项
USE_SYSTEM_USER_DATA = True  # 设置为 True 使用系统默认用户数据目录（更快，但可能影响登录状态保持）
DISABLE_IMAGES = True  # 设置为 True 禁用图片加载以提升速度


def wait_for_page_load_complete(driver, timeout: int = 30):
    """等待页面完全加载完成
    
    检测多个指标：
    1. document.readyState 是否为 'complete'
    2. 网络请求是否完成
    3. 页面是否稳定（不再变化）
    """
    print("检测页面加载状态...")
    # #region agent log
    debug_log("C", "get_ai_summary.py:wait_for_page_load_complete", "开始检测页面加载", {"timeout": timeout})
    # #endregion
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        try:
            # 方法1: 检查 document.readyState
            ready_state = driver.execute_script("return document.readyState")
            # #region agent log
            debug_log("C", "get_ai_summary.py:wait_for_page_load_complete", "检查readyState", {"ready_state": ready_state})
            # #endregion
            if ready_state != 'complete':
                print(f"  页面状态: {ready_state}，等待中...")
                time.sleep(0.5)
                continue
            
            # 方法2: 检查网络请求是否完成（通过 performance API）
            network_idle = driver.execute_script("""
                if (window.performance && window.performance.timing) {
                    var perf = window.performance.timing;
                    var loadTime = perf.loadEventEnd - perf.navigationStart;
                    return loadTime > 0;
                }
                return true;
            """)
            
            # 方法3: 检查是否有正在进行的 AJAX 请求（如果页面使用 jQuery）
            ajax_complete = driver.execute_script("""
                if (typeof jQuery !== 'undefined' && jQuery.active !== undefined) {
                    return jQuery.active === 0;
                }
                return true;
            """)
            
            # 方法4: 检查页面是否稳定（DOM 不再变化）
            # 获取当前页面高度和元素数量
            page_info = driver.execute_script("""
                return {
                    height: document.body.scrollHeight,
                    elementCount: document.querySelectorAll('*').length,
                    hasInput: document.querySelector('textarea') !== null
                };
            """)
            
            # 如果所有条件都满足，认为页面已加载完成
            if network_idle and ajax_complete:
                # 额外检查：等待关键元素出现（输入框）
                if page_info.get('hasInput'):
                    # #region agent log
                    debug_log("C", "get_ai_summary.py:wait_for_page_load_complete", "页面加载完成", {"page_info": page_info})
                    # #endregion
                    print("✓ 页面加载完成（所有检测通过）")
                    return True
                else:
                    # 如果输入框还没出现，再等待一下
                    # #region agent log
                    debug_log("C", "get_ai_summary.py:wait_for_page_load_complete", "等待输入框出现", {"page_info": page_info})
                    # #endregion
                    print(f"  页面基本加载完成，等待关键元素出现...")
                    time.sleep(1)
                    continue
            
            time.sleep(0.5)
            
        except Exception as e:
            # #region agent log
            debug_log("C", "get_ai_summary.py:wait_for_page_load_complete", "检测页面状态出错", {"error": str(e)})
            # #endregion
            print(f"  检测页面状态时出错: {e}")
            time.sleep(0.5)
    
    # #region agent log
    debug_log("C", "get_ai_summary.py:wait_for_page_load_complete", "页面加载检测超时", {"timeout": timeout})
    # #endregion
    print(f"⚠ 页面加载检测超时（{timeout}秒），继续执行...")
    return False


def is_element_fully_loaded(driver, element):
    """检测元素是否完全加载并可用"""
    try:
        # 检查元素是否存在
        if not element:
            return False
        
        # 检查元素是否可见
        if not element.is_displayed():
            return False
        
        # 检查元素是否启用
        if not element.is_enabled():
            return False
        
        # 检查元素尺寸
        size = element.size
        if size['height'] <= 0 or size['width'] <= 0:
            return False
        
        # 检查元素是否在视口中（通过 JavaScript）
        is_in_viewport = driver.execute_script("""
            var rect = arguments[0].getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        """, element)
        
        # 检查元素是否可以交互（通过 JavaScript）
        is_interactable = driver.execute_script("""
            var el = arguments[0];
            var style = window.getComputedStyle(el);
            return style.pointerEvents !== 'none' && 
                   style.visibility !== 'hidden' && 
                   style.opacity !== '0';
        """, element)
        
        return is_in_viewport and is_interactable
        
    except Exception as e:
        print(f"检测元素状态时出错: {e}")
        return False


def find_input_element(driver, timeout: int = 15):
    """查找输入框元素（带完整加载检测）"""
    selector = 'textarea.semi-input-textarea.semi-input-textarea-autosize'
    
    try:
        print("查找输入框元素...")
        wait = WebDriverWait(driver, timeout)
        
        # 首先等待元素出现
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        
        if element:
            # 等待元素完全加载并可用
            max_wait = 10  # 最多等待10秒
            start_time = time.time()
            
            while (time.time() - start_time) < max_wait:
                if is_element_fully_loaded(driver, element):
                    print("✓ 输入框已完全加载并可用")
                    return element
                
                # 如果元素还没完全加载，重新查找（可能页面还在变化）
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                except:
                    pass
                
                time.sleep(0.3)
            
            # 如果超时，但元素存在，也返回（可能检测逻辑有问题）
            if element:
                print("⚠ 输入框检测超时，但元素存在，继续使用")
                return element
                
    except TimeoutException as e:
        print(f"✗ 查找输入框超时: {e}")
    except Exception as e:
        print(f"✗ 查找输入框时出错: {e}")
    
    return None


def send_message(driver, input_element, message: str):
    """发送消息（使用 JavaScript 避免 BMP 字符限制）"""
    if not input_element:
        raise ValueError("输入框不存在")
    
    selector = 'textarea.semi-input-textarea.semi-input-textarea-autosize'
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # 如果元素可能已失效，重新查找
            if attempt > 0:
                input_element = find_input_element(driver, timeout=5)
                if not input_element:
                    raise ValueError("无法重新找到输入框")
            
            # 滚动到元素可见
            driver.execute_script("arguments[0].scrollIntoView(true);", input_element)
            time.sleep(0.2)
            
            # 点击输入框聚焦
            input_element.click()
            time.sleep(0.2)
            
            # 使用 JavaScript 设置输入框值（避免 BMP 字符限制）
            # 这样可以支持所有 Unicode 字符，包括 emoji 和特殊符号
            # #region agent log
            debug_log("F", "get_ai_summary.py:send_message", "使用JavaScript设置输入框值", {"message_length": len(message), "attempt": attempt + 1})
            # #endregion
            
            driver.execute_script("""
                var element = arguments[0];
                var text = arguments[1];
                element.value = text;
                element.textContent = text;
                element.innerText = text;
                
                // 触发输入事件，确保页面识别到值的变化
                var event = new Event('input', { bubbles: true });
                element.dispatchEvent(event);
                
                var changeEvent = new Event('change', { bubbles: true });
                element.dispatchEvent(changeEvent);
            """, input_element, message)
            
            # 验证值是否设置成功
            actual_value = driver.execute_script("return arguments[0].value;", input_element)
            # #region agent log
            debug_log("F", "get_ai_summary.py:send_message", "验证输入框值", {"actual_length": len(actual_value) if actual_value else 0, "expected_length": len(message)})
            # #endregion
            
            time.sleep(0.5)
            
            # 发送消息（使用 Enter 键）
            input_element.send_keys("\n")
            # #region agent log
            debug_log("F", "get_ai_summary.py:send_message", "已发送Enter键")
            # #endregion
            
            return  # 成功发送，退出函数
            
        except Exception as e:
            # 如果是 StaleElementReferenceException 且还有重试机会，继续重试
            if isinstance(e, StaleElementReferenceException) and attempt < max_retries - 1:
                time.sleep(0.5)  # 等待页面稳定
                continue
            else:
                print(f"发送消息时出错: {e}")
                raise


def wait_for_response_complete(driver, timeout: int = 60):
    """等待 AI 响应完成
    
    通过检测页面中AI回答文本是否不再变化来判断回答是否完成
    """
    print("等待 AI 开始响应...")
    time.sleep(2)  # 先等待一下，让AI开始响应
    
    # 尝试多种方式检测回答是否完成
    max_wait_time = timeout
    check_interval = 1  # 每秒检查一次
    last_text = ""
    stable_count = 0
    required_stable_checks = 3  # 连续3次文本不变则认为完成
    empty_count = 0  # 连续检测到空文本的次数
    
    start_time = time.time()
    
    while True:
        current_time = time.time()
        if (current_time - start_time) > max_wait_time:
            print("等待超时，可能回答已完成或仍在生成中")
            break
        
        # 尝试查找AI回答区域（使用更精确的选择器）
        try:
            # 查找消息块容器（排除输入框容器）
            blocks = driver.find_elements(By.CSS_SELECTOR, 'div[class*="message-block-container"]')
            
            current_text = ""
            if blocks and len(blocks) >= 2:
                # 获取最后一个消息块（应该是AI的回答）
                block = blocks[-1]
                # 使用text属性获取完整文本
                text = block.text
                
                # 排除输入框容器
                if text and not any(keyword in text for keyword in ["深度思考", "编程", "图像生成", "帮我写作", "数据分析", "解题答疑", "更多"]):
                    # 排除用户消息（通常较短）
                    if len(text.strip()) > 20:
                        current_text = text.strip()
            
            # 如果找到了文本
            if current_text:
                if current_text == last_text:
                    stable_count += 1
                    if stable_count >= required_stable_checks:
                        print(f"AI 回答已完成 (共 {len(current_text)} 字符)")
                        break
                else:
                    stable_count = 0
                    empty_count = 0  # 重置空计数
                    last_text = current_text
                    print(f"  正在生成中... (已生成 {len(current_text)} 字符)")
            elif last_text:
                # 如果current_text为空但last_text有值，可能是页面结构变化
                # 等待一段时间看是否恢复
                empty_count += 1
                
                # 如果连续3次检测到空文本，且last_text有值，认为回答已完成
                if empty_count >= 3:
                    print(f"AI 回答已完成 (共 {len(last_text)} 字符，检测到页面结构变化)")
                    break
            else:
                # 重置空计数
                empty_count = 0
            
        except Exception as e:
            pass
        
        time.sleep(check_interval)
    
    # 额外等待，确保所有内容都渲染完成
    time.sleep(2)  # 增加等待时间到2秒


def clean_recommendations(text: str) -> str:
    """清理回答中的推荐信息
    
    推荐信息通常以"豆包，"开头，后面跟着问题，位于回答文本的末尾
    """
    if not text:
        return text
    
    # 移除末尾的空白字符
    cleaned = text.strip().rstrip('\n\r\t ')
    
    # 查找推荐信息的开始位置（通常以"豆包，"开头）
    recommendation_pattern = r'[\s\n]*分享[\s\n]*豆包，[^\n]*(?:\n[^\n]*豆包，[^\n]*)*'
    
    # 尝试从末尾移除推荐信息
    match = re.search(recommendation_pattern, cleaned, re.MULTILINE)
    if match:
        recommendation_start = match.start()
        before_recommendation = cleaned[:recommendation_start].rstrip('\n\r\t ')
        if before_recommendation and recommendation_start > len(cleaned) * 0.5:
            cleaned = before_recommendation
    
    # 模式2: 查找以"豆包，"开头的行，从末尾开始移除
    lines = cleaned.split('\n')
    recommendation_start_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line.startswith('豆包，') and ('？' in line or '?' in line or len(line) > 10):
            recommendation_start_idx = i
            if i > 0 and ('分享' in lines[i-1] or '复制' in lines[i-1] or '点赞' in lines[i-1]):
                recommendation_start_idx = i - 1
            break
    
    if recommendation_start_idx >= 0:
        before_recommendation = '\n'.join(lines[:recommendation_start_idx]).rstrip('\n\r\t ')
        if len(before_recommendation) > 20 and recommendation_start_idx < len(lines) * 0.8:
            cleaned = before_recommendation
    
    # 模式3: 查找包含结束语后的推荐信息
    ending_phrases = [
        "你今天想聊点什么呢？",
        "你想聊点什么呢？",
        "有什么可以帮你的吗？",
        "有什么问题吗？"
    ]
    
    for phrase in ending_phrases:
        if phrase in cleaned:
            phrase_pos = cleaned.find(phrase)
            if phrase_pos >= 0:
                after_phrase = cleaned[phrase_pos + len(phrase):].strip()
                if after_phrase.startswith('分享') or after_phrase.startswith('豆包，'):
                    cleaned = cleaned[:phrase_pos + len(phrase)].rstrip('\n\r\t ')
                    break
    
    # 移除末尾的UI元素文本（按钮等）
    ui_keywords = ["分享", "复制", "点赞", "收藏", "转发", "删除", "编辑"]
    for keyword in ui_keywords:
        if cleaned.endswith(keyword):
            cleaned = cleaned[:-len(keyword)].rstrip('\n\r\t ')
        elif cleaned.endswith('\n' + keyword):
            cleaned = cleaned[:-len('\n' + keyword)].rstrip('\n\r\t ')
        elif cleaned.endswith(' ' + keyword):
            cleaned = cleaned[:-len(' ' + keyword)].rstrip('\n\r\t ')
    
    return cleaned


def extract_ai_response(driver):
    """提取 AI 的回答内容"""
    try:
        # 方法1: 查找消息块容器，排除输入框容器
        try:
            message_blocks = driver.find_elements(By.CSS_SELECTOR, 'div[class*="message-block-container"]')
            
            if message_blocks and len(message_blocks) >= 2:
                # 从后往前查找，跳过包含输入框的
                for i in range(len(message_blocks) - 1, -1, -1):
                    block = message_blocks[i]
                    
                    # 滚动到元素底部，确保所有内容都可见
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(false);", block)
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", block)
                        time.sleep(0.5)
                    except:
                        pass
                    
                    # 获取文本
                    text = block.text
                    
                    # 排除输入框容器（通常包含"深度思考"、"编程"等功能菜单）
                    if text and len(text.strip()) > 0:
                        if any(keyword in text for keyword in ["深度思考", "编程", "图像生成", "帮我写作", "数据分析", "解题答疑", "更多"]):
                            continue
                        
                        if len(text.strip()) > 20:  # AI回答通常较长
                            # 尝试使用JavaScript获取更完整的内容
                            try:
                                content_text = driver.execute_script("""
                                    var el = arguments[0];
                                    var clone = el.cloneNode(true);
                                    var actionBars = clone.querySelectorAll('[class*="action"], [class*="button"]');
                                    actionBars.forEach(function(bar) { bar.remove(); });
                                    return clone.textContent || clone.innerText || '';
                                """, block)
                                
                                if content_text and len(content_text.strip()) > len(text.strip()):
                                    text = content_text
                            except:
                                pass
                            
                            # 移除末尾的UI元素文本
                            ui_keywords = ["分享", "复制", "点赞", "收藏", "转发", "删除", "编辑"]
                            cleaned_text = text.strip().rstrip('\n\r\t ')
                            for keyword in ui_keywords:
                                if cleaned_text.endswith(keyword):
                                    cleaned_text = cleaned_text[:-len(keyword)].rstrip('\n\r\t ')
                                elif cleaned_text.endswith('\n' + keyword):
                                    cleaned_text = cleaned_text[:-len('\n' + keyword)].rstrip('\n\r\t ')
                                elif cleaned_text.endswith(' ' + keyword):
                                    cleaned_text = cleaned_text[:-len(' ' + keyword)].rstrip('\n\r\t ')
                            
                            return cleaned_text
        except Exception as e:
            pass
        
        # 方法2: 查找消息列表，提取最后一条AI消息
        try:
            message_list = driver.find_element(By.CSS_SELECTOR, 'div[class*="message-list"]')
            
            if message_list:
                blocks = message_list.find_elements(By.CSS_SELECTOR, 'div[class*="message-block-container"]')
                
                if blocks and len(blocks) >= 2:
                    for i in range(len(blocks) - 1, -1, -1):
                        block = blocks[i]
                        text = block.text
                        
                        if text and len(text.strip()) > 0:
                            if any(keyword in text for keyword in ["深度思考", "编程", "图像生成", "帮我写作", "数据分析", "解题答疑", "更多"]):
                                continue
                            
                            if len(text.strip()) > 20:
                                ui_keywords = ["分享", "复制", "点赞", "收藏", "转发", "删除", "编辑"]
                                cleaned_text = text.strip().rstrip('\n\r\t ')
                                for keyword in ui_keywords:
                                    if cleaned_text.endswith(keyword):
                                        cleaned_text = cleaned_text[:-len(keyword)].rstrip('\n\r\t ')
                                    elif cleaned_text.endswith('\n' + keyword):
                                        cleaned_text = cleaned_text[:-len('\n' + keyword)].rstrip('\n\r\t ')
                                    elif cleaned_text.endswith(' ' + keyword):
                                        cleaned_text = cleaned_text[:-len(' ' + keyword)].rstrip('\n\r\t ')
                                
                                return cleaned_text
        except Exception as e:
            pass
        
        # 方法3: 使用JavaScript直接查找AI回答
        try:
            ai_response = driver.execute_script("""
                var blocks = Array.from(document.querySelectorAll('div[class*="message-block-container"]'));
                var uiKeywords = ['分享', '复制', '点赞', '收藏', '转发', '删除', '编辑'];
                
                for (var i = blocks.length - 1; i >= 0; i--) {
                    var block = blocks[i];
                    var clone = block.cloneNode(true);
                    var actionBars = clone.querySelectorAll('[class*="action"], [class*="button"], [class*="share"], [class*="copy"]');
                    actionBars.forEach(function(bar) { bar.remove(); });
                    
                    var text = clone.textContent || clone.innerText || '';
                    
                    if (text.includes('深度思考') || text.includes('编程') || text.includes('图像生成') || 
                        text.includes('帮我写作') || text.includes('数据分析') || text.includes('解题答疑') || 
                        text.includes('更多')) {
                        continue;
                    }
                    
                    if (text.trim().length > 20) {
                        var cleanedText = text.trim();
                        for (var j = 0; j < uiKeywords.length; j++) {
                            var keyword = uiKeywords[j];
                            if (cleanedText.endsWith(keyword)) {
                                cleanedText = cleanedText.slice(0, -keyword.length).trim();
                            }
                        }
                        return cleanedText;
                    }
                }
                
                return null;
            """)
            
            if ai_response:
                return ai_response
        except Exception as e:
            pass
        
        return None
    except Exception as e:
        print(f"提取AI回答时出错: {e}")
        return None


def save_response(question: str, answer: str):
    """保存问答到文件"""
    if not answer:
        print("未获取到AI回答，跳过保存")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = RESPONSES_DIR / f"response_{timestamp}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "answer_length": len(answer)
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"AI回答已保存到: {filename}")
        print(f"  回答长度: {len(answer)} 字符")
    except Exception as e:
        print(f"保存回答时出错: {e}")


def doubao_chat_example():
    """豆包对话示例 - 发送一条设定好的消息"""
    # #region agent log
    debug_log("START", "get_ai_summary.py:doubao_chat_example", "开始执行AI agent测试")
    # #endregion
    
    # 动态加载CSV内容，确保使用最新的数据
    csv_content = load_csv_content()
    
    if csv_content:
        message = f"请分析今日信息\n\n{csv_content}"
        # #region agent log
        debug_log("A", "get_ai_summary.py:doubao_chat_example", "使用CSV内容构建消息", {"message_length": len(message)})
        # #endregion
    else:
        message = "请分析今日信息"
        # #region agent log
        debug_log("A", "get_ai_summary.py:doubao_chat_example", "使用默认消息", {"message": message})
        # #endregion
        print("警告: CSV文件不存在或为空，将发送默认消息")
    
    # 创建浏览器选项
    options = uc.ChromeOptions()
    
    # 设置用户数据目录以保持登录状态
    if not USE_SYSTEM_USER_DATA:
        # 使用独立用户数据目录（保持登录状态，但可能较慢）
        user_data_dir_str = str(USER_DATA_DIR.absolute())
        options.add_argument(f'--user-data-dir={user_data_dir_str}')
        print(f"使用独立用户数据目录: {user_data_dir_str}")
    else:
        # 使用系统默认用户数据目录（更快，但会使用你的默认浏览器配置）
        print("使用系统默认用户数据目录（性能更优）")
        # 注意：使用系统默认目录可能会影响登录状态保持
    
    # 性能优化选项
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    
    # 加速加载的选项
    options.add_argument('--disable-extensions')  # 禁用扩展（如果不需要）
    options.add_argument('--disable-plugins')  # 禁用插件
    
    # 网络优化配置
    prefs = {
        'profile.default_content_setting_values': {
            'plugins': 2,  # 禁用插件
            'popups': 2,  # 禁用弹窗
        }
    }
    
    # 根据配置决定是否禁用图片
    if DISABLE_IMAGES:
        options.add_argument('--blink-settings=imagesEnabled=false')
        prefs['profile.default_content_setting_values']['images'] = 2
        prefs['profile.managed_default_content_settings'] = {'images': 2}
        print("已禁用图片加载以提升速度")
    
    options.add_experimental_option('prefs', prefs)
    
    # 注意：不要禁用 JavaScript，豆包网站需要 JS 才能正常工作
    
    # 创建 undetected Chrome driver
    driver = None
    try:
        # #region agent log
        debug_log("B", "get_ai_summary.py:doubao_chat_example", "准备启动浏览器", {"use_system_user_data": USE_SYSTEM_USER_DATA, "chrome_path": str(CHROME_BINARY_PATH)})
        # #endregion
        print("正在启动浏览器...")
        
        # 如果指定了自定义 Chrome 路径，使用该路径；否则使用系统默认 Chrome
        if CHROME_BINARY_PATH and Path(CHROME_BINARY_PATH).exists():
            print(f"使用自定义 Chrome: {CHROME_BINARY_PATH}")
            # #region agent log
            debug_log("B", "get_ai_summary.py:doubao_chat_example", "使用自定义Chrome路径启动", {"path": CHROME_BINARY_PATH})
            # #endregion
            driver = uc.Chrome(options=options, version_main=None, browser_executable_path=CHROME_BINARY_PATH)
        else:
            if CHROME_BINARY_PATH:
                print(f"警告: 指定的 Chrome 路径不存在 ({CHROME_BINARY_PATH})，将使用系统默认 Chrome")
                # #region agent log
                debug_log("B", "get_ai_summary.py:doubao_chat_example", "自定义Chrome路径不存在，使用系统默认", {"requested_path": CHROME_BINARY_PATH})
                # #endregion
            else:
                print("使用系统默认 Chrome")
                # #region agent log
                debug_log("B", "get_ai_summary.py:doubao_chat_example", "使用系统默认Chrome启动")
                # #endregion
            driver = uc.Chrome(options=options, version_main=None)
        
        # #region agent log
        debug_log("B", "get_ai_summary.py:doubao_chat_example", "浏览器启动成功", {"driver": str(type(driver))})
        # #endregion
        
        print("正在访问豆包聊天页面...")
        # #region agent log
        debug_log("C", "get_ai_summary.py:doubao_chat_example", "开始访问页面", {"url": "https://www.doubao.com/chat/"})
        # #endregion
        driver.get('https://www.doubao.com/chat/')
        
        # 使用智能页面加载检测
        # #region agent log
        debug_log("C", "get_ai_summary.py:doubao_chat_example", "开始检测页面加载状态")
        # #endregion
        page_loaded = wait_for_page_load_complete(driver, timeout=30)
        # #region agent log
        debug_log("C", "get_ai_summary.py:doubao_chat_example", "页面加载检测完成", {"loaded": page_loaded})
        # #endregion
        
        # 额外等待一小段时间确保所有动态内容加载完成
        time.sleep(1)
        
        # 查找输入框
        print("查找输入框...")
        # #region agent log
        debug_log("E", "get_ai_summary.py:doubao_chat_example", "开始查找输入框")
        # #endregion
        input_element = find_input_element(driver, timeout=20)
        
        if not input_element:
            # #region agent log
            debug_log("E", "get_ai_summary.py:doubao_chat_example", "输入框查找失败")
            # #endregion
            print("未找到输入框，请检查页面状态")
            return
        
        # #region agent log
        debug_log("E", "get_ai_summary.py:doubao_chat_example", "输入框查找成功", {"element": str(input_element)})
        # #endregion
        
        # 发送消息
        print(f"\n发送消息: {message}")
        # #region agent log
        debug_log("F", "get_ai_summary.py:doubao_chat_example", "准备发送消息", {"message_length": len(message)})
        # #endregion
        try:
            send_message(driver, input_element, message)
            # #region agent log
            debug_log("F", "get_ai_summary.py:doubao_chat_example", "消息发送成功")
            # #endregion
        except Exception as send_error:
            # #region agent log
            debug_log("F", "get_ai_summary.py:doubao_chat_example", "消息发送失败", {"error": str(send_error)})
            # #endregion
            raise
        
        # 等待AI响应完成
        print("等待 AI 响应完成...")
        # #region agent log
        debug_log("G", "get_ai_summary.py:doubao_chat_example", "开始等待AI响应")
        # #endregion
        wait_for_response_complete(driver, timeout=60)
        # #region agent log
        debug_log("G", "get_ai_summary.py:doubao_chat_example", "AI响应等待完成")
        # #endregion
        
        # 额外等待，确保所有内容都完全渲染
        print("等待内容完全渲染...")
        time.sleep(3)
        
        # 提取AI回答（带重试机制）
        print("\n提取 AI 回答...")
        # #region agent log
        debug_log("H", "get_ai_summary.py:doubao_chat_example", "开始提取AI回答")
        # #endregion
        
        # 尝试多次提取，确保获取完整文本
        ai_response = None
        last_length = 0
        for attempt in range(3):
            # #region agent log
            debug_log("H", "get_ai_summary.py:doubao_chat_example", f"提取AI回答尝试 {attempt + 1}/3")
            # #endregion
            response = extract_ai_response(driver)
            if response:
                if len(response) > last_length:
                    ai_response = response
                    last_length = len(response)
                    # #region agent log
                    debug_log("H", "get_ai_summary.py:doubao_chat_example", "提取到更长的回答", {"length": len(response)})
                    # #endregion
                    if attempt > 0:
                        break
                elif len(response) == last_length and attempt > 0:
                    # #region agent log
                    debug_log("H", "get_ai_summary.py:doubao_chat_example", "回答长度稳定", {"length": len(response)})
                    # #endregion
                    break
            
            if attempt < 2:
                time.sleep(2)
        
        if not ai_response:
            ai_response = extract_ai_response(driver)
        
        if ai_response:
            # #region agent log
            debug_log("H", "get_ai_summary.py:doubao_chat_example", "AI回答提取成功", {"length": len(ai_response)})
            debug_log("SUCCESS", "get_ai_summary.py:doubao_chat_example", "AI agent测试成功完成")
            # #endregion
            print(f"成功获取AI回答 ({len(ai_response)} 字符)")
            # 保存回答
            save_response(message, ai_response)
        else:
            # #region agent log
            debug_log("H", "get_ai_summary.py:doubao_chat_example", "AI回答提取失败")
            debug_log("FAIL", "get_ai_summary.py:doubao_chat_example", "AI agent测试失败：无法提取回答")
            # #endregion
            print("未能提取到AI回答，请检查页面结构")
        
        # 保持浏览器打开一段时间
        print("\n浏览器将保持打开 30 秒，您可以查看对话结果...")
        time.sleep(30)
    
    except Exception as e:
        # #region agent log
        import traceback
        error_trace = traceback.format_exc()
        debug_log("ERROR", "get_ai_summary.py:doubao_chat_example", "发生异常", {"error": str(e), "traceback": error_trace})
        # #endregion
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # #region agent log
        debug_log("CLEANUP", "get_ai_summary.py:doubao_chat_example", "清理资源", {"driver_exists": driver is not None})
        # #endregion
        if driver:
            driver.quit()


if __name__ == '__main__':
    doubao_chat_example()
