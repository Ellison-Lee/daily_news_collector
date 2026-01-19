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

# CSV文件路径（相对于工作区根目录）
CSV_FILE_PATH = Path(__file__).parent.parent / 'data' / 'daily_hot_titles.csv'

def load_csv_content():
    """读取CSV文件内容并格式化为文本"""
    try:
        if not CSV_FILE_PATH.exists():
            print(f"CSV文件不存在: {CSV_FILE_PATH}")
            return ""
        
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            return ""
        
        # 格式化CSV内容为文本
        content_lines = []
        for row in rows:
            category = row.get('类别', '')
            platform = row.get('平台', '')
            title = row.get('标题', '')
            if title:
                content_lines.append(f"{category} | {platform} | {title}")
        
        return '\n'.join(content_lines)
    except Exception as e:
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


def find_input_element(driver, timeout: int = 15):
    """查找输入框元素"""
    selector = 'textarea.semi-input-textarea.semi-input-textarea-autosize'
    
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        
        if element:
            is_displayed = element.is_displayed()
            is_enabled = element.is_enabled()
            if is_displayed and is_enabled:
                size = element.size
                if size['height'] > 0 and size['width'] > 0:
                    print(f"找到输入框")
                    return element
    except TimeoutException as e:
        print(f"查找输入框超时: {e}")
    except Exception as e:
        print(f"查找输入框时出错: {e}")
    
    return None


def send_message(driver, input_element, message: str):
    """发送消息"""
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
            
            # 清空输入框
            input_element.clear()
            time.sleep(0.1)
            
            # 输入文本
            input_element.send_keys(message)
            time.sleep(0.5)
            
            # 发送消息（使用 Enter 键）
            input_element.send_keys("\n")
            
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
    # 动态加载CSV内容，确保使用最新的数据
    csv_content = load_csv_content()
    
    if csv_content:
        message = f"请分析今日信息\n\n{csv_content}"
    else:
        message = "请分析今日信息"
        print("警告: CSV文件不存在或为空，将发送默认消息")
    
    # 创建浏览器选项
    options = uc.ChromeOptions()
    
    # 设置用户数据目录以保持登录状态
    user_data_dir_str = str(USER_DATA_DIR.absolute())
    options.add_argument(f'--user-data-dir={user_data_dir_str}')
    
    # 其他反检测选项
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    
    # 创建 undetected Chrome driver
    driver = None
    try:
        print("正在启动浏览器...")
        
        # 如果指定了自定义 Chrome 路径，使用该路径；否则使用系统默认 Chrome
        if CHROME_BINARY_PATH and Path(CHROME_BINARY_PATH).exists():
            print(f"使用自定义 Chrome: {CHROME_BINARY_PATH}")
            driver = uc.Chrome(options=options, version_main=None, browser_executable_path=CHROME_BINARY_PATH)
        else:
            if CHROME_BINARY_PATH:
                print(f"警告: 指定的 Chrome 路径不存在 ({CHROME_BINARY_PATH})，将使用系统默认 Chrome")
            else:
                print("使用系统默认 Chrome")
            driver = uc.Chrome(options=options, version_main=None)
        
        print("正在访问豆包聊天页面...")
        driver.get('https://www.doubao.com/chat/')
        
        print("等待页面加载...")
        time.sleep(2)
        
        # 查找输入框
        print("查找输入框...")
        input_element = find_input_element(driver, timeout=20)
        
        if not input_element:
            print("未找到输入框，请检查页面状态")
            return
        
        # 发送消息
        print(f"\n发送消息: {message}")
        try:
            send_message(driver, input_element, message)
        except Exception as send_error:
            raise
        
        # 等待AI响应完成
        print("等待 AI 响应完成...")
        wait_for_response_complete(driver, timeout=60)
        
        # 额外等待，确保所有内容都完全渲染
        print("等待内容完全渲染...")
        time.sleep(3)
        
        # 提取AI回答（带重试机制）
        print("\n提取 AI 回答...")
        
        # 尝试多次提取，确保获取完整文本
        ai_response = None
        last_length = 0
        for attempt in range(3):
            response = extract_ai_response(driver)
            if response:
                if len(response) > last_length:
                    ai_response = response
                    last_length = len(response)
                    if attempt > 0:
                        break
                elif len(response) == last_length and attempt > 0:
                    break
            
            if attempt < 2:
                time.sleep(2)
        
        if not ai_response:
            ai_response = extract_ai_response(driver)
        
        if ai_response:
            print(f"成功获取AI回答 ({len(ai_response)} 字符)")
            # 保存回答
            save_response(message, ai_response)
        else:
            print("未能提取到AI回答，请检查页面结构")
        
        # 保持浏览器打开一段时间
        print("\n浏览器将保持打开 30 秒，您可以查看对话结果...")
        time.sleep(30)
    
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    doubao_chat_example()
