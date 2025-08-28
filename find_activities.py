"""
活動記錄查找和報告生成工具
自動登入、掃描 ticket、記錄活動並生成報告
"""

import time
import logging
import json
import csv
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import config
import getpass
import os

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActivityScanner:
    """活動掃描器"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.activities = []
        
    def setup_driver(self):
        """設定瀏覽器"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("瀏覽器已啟動")
            
        except Exception as e:
            logger.error(f"啟動瀏覽器失敗: {e}")
            raise
    
    def close_driver(self):
        """關閉瀏覽器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("瀏覽器已關閉")
            except Exception as e:
                logger.warning(f"關閉瀏覽器時發生錯誤: {e}")
    
    def login_to_eservice(self, username, password):
        """登入 eService"""
        try:
            print("🔐 正在登入 eService...")
            
            # 使用現有的登入邏輯
            from browser_automation import BrowserAutomation
            browser = BrowserAutomation()
            browser.driver = self.driver
            browser.wait = self.wait
            
            login_success = browser.login_to_website(config.ESERVICE_CONFIG, username, password)
            
            if login_success:
                print("✅ 登入成功！")
                return True
            else:
                print("❌ 登入失敗")
                return False
                
        except Exception as e:
            logger.error(f"登入失敗: {e}")
            return False
    
    def analyze_dashboard_structure(self):
        """分析 Dashboard 結構"""
        try:
            print("\n🔍 分析 Dashboard 結構...")
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            print(f"📍 當前 URL: {current_url}")
            print(f"📄 頁面標題: {page_title}")
            
            # 等待頁面載入
            time.sleep(3)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 尋找可能的 ticket 容器
            ticket_selectors = [
                '.ticket', '.tickets', '.ticket-list', '.issue', '.issues', '.issue-list',
                '.conversation', '.conversations', '.message', '.messages',
                '.dashboard', '.dashboard-content', '.recent', '.recent-activity',
                '.timeline', '.feed', '.news', '.updates',
                '.my-tickets', '.my-issues', '.assigned-to-me',
                '.created-by-me', '.reported-by-me',
                '.table', '.list', '.grid', '.items',
                '[data-ticket-id]', '[data-issue-id]', '[data-conversation-id]'
            ]
            
            found_containers = []
            for selector in ticket_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ 找到 {len(elements)} 個元素: {selector}")
                    found_containers.append({
                        'selector': selector,
                        'count': len(elements),
                        'elements': elements[:5]  # 只取前5個作為樣本
                    })
            
            # 尋找表格和列表
            tables = soup.find_all('table')
            lists = soup.find_all(['ul', 'ol'])
            
            print(f"📊 找到 {len(tables)} 個表格")
            print(f"📋 找到 {len(lists)} 個列表")
            
            # 分析第一個表格（如果存在）
            if tables:
                print("\n📊 分析第一個表格結構:")
                first_table = tables[0]
                rows = first_table.find_all('tr')
                print(f"   行數: {len(rows)}")
                
                if rows:
                    headers = rows[0].find_all(['th', 'td'])
                    print(f"   列數: {len(headers)}")
                    print("   標題:")
                    for i, header in enumerate(headers[:5]):  # 只顯示前5列
                        header_text = header.get_text(strip=True)
                        print(f"     列 {i+1}: {header_text}")
            
            return found_containers
            
        except Exception as e:
            logger.error(f"分析 Dashboard 結構失敗: {e}")
            return []
    
    def find_ticket_elements(self):
        """尋找 ticket 元素"""
        try:
            print("\n🔍 尋找 ticket 元素...")
            
            # 等待頁面載入
            time.sleep(2)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 嘗試多種選擇器來找到 ticket
            ticket_selectors = [
                'tr[data-ticket-id]', 'tr[data-issue-id]',
                '.ticket-item', '.issue-item', '.conversation-item',
                '.ticket-row', '.issue-row',
                'tr:has(td)', 'li:has(a)',
                '.item', '.entry', '.record'
            ]
            
            found_tickets = []
            for selector in ticket_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        print(f"✅ 使用選擇器 '{selector}' 找到 {len(elements)} 個 ticket")
                        found_tickets.extend(elements[:50])  # 限制為前50個
                        break
                except Exception as e:
                    continue
            
            # 如果沒有找到，嘗試更通用的方法
            if not found_tickets:
                print("⚠️  使用通用方法尋找 ticket...")
                
                # 尋找包含日期的行
                date_patterns = ['2024', '2023', '2025', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                for pattern in date_patterns:
                    elements = soup.find_all(text=lambda text: text and pattern in text)
                    if elements:
                        for element in elements:
                            parent = element.parent
                            if parent and parent.name in ['tr', 'li', 'div']:
                                found_tickets.append(parent)
                                if len(found_tickets) >= 50:
                                    break
                        if len(found_tickets) >= 50:
                            break
            
            print(f"📋 總共找到 {len(found_tickets)} 個可能的 ticket")
            return found_tickets[:50]  # 限制為50個
            
        except Exception as e:
            logger.error(f"尋找 ticket 元素失敗: {e}")
            return []
    
    def extract_ticket_info(self, ticket_element):
        """提取單個 ticket 信息"""
        try:
            ticket_info = {
                'id': '',
                'title': '',
                'date': '',
                'status': '',
                'content': '',
                'url': '',
                'full_url': '',
                'source': 'eservice',
                'raw_text': ticket_element.get_text(strip=True)[:500],  # 保存原始文本用於調試
                'detailed_interactions': []  # 詳細互動內容
            }
            
            # 提取 ID
            ticket_id = ticket_element.get('data-ticket-id') or ticket_element.get('data-issue-id')
            if ticket_id:
                ticket_info['id'] = ticket_id
            
            # 提取標題 - 嘗試多種方法
            title_element = ticket_element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'span', 'div'])
            if title_element:
                ticket_info['title'] = title_element.get_text(strip=True)
            
            # 提取日期 - 改進的日期提取
            date_patterns = [
                '2024', '2023', '2025',  # 年份
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',  # 英文月份
                'hours ago', 'days ago', 'minutes ago', 'ago',  # 相對時間
                'today', 'yesterday',  # 相對日期
                '分鐘前', '小時前', '天前'  # 中文相對時間
            ]
            
            for pattern in date_patterns:
                date_elements = ticket_element.find_all(string=lambda text: text and pattern in text)
                if date_elements:
                    ticket_info['date'] = date_elements[0].strip()
                    break
            
            # 提取狀態 - 改進的狀態提取
            status_keywords = ['open', 'closed', 'pending', 'resolved', 'active', 'inactive', 'new', 'old', 'high', 'low', 'medium']
            for keyword in status_keywords:
                status_elements = ticket_element.find_all(string=lambda text: text and keyword.lower() in text.lower())
                if status_elements:
                    ticket_info['status'] = status_elements[0].strip()
                    break
            
            # 提取內容
            content_element = ticket_element.find(['p', 'div', 'span'])
            if content_element:
                ticket_info['content'] = content_element.get_text(strip=True)[:200]
            
            # 提取 URL
            link_element = ticket_element.find('a', href=True)
            if link_element:
                ticket_info['url'] = link_element.get('href')
                # 構建完整 URL
                if ticket_info['url'] and not ticket_info['url'].startswith('http'):
                    ticket_info['full_url'] = config.ESERVICE_CONFIG['original_url'] + ticket_info['url']
                else:
                    ticket_info['full_url'] = ticket_info['url']
            
            return ticket_info
            
        except Exception as e:
            logger.warning(f"提取 ticket 信息失敗: {e}")
            return None
    
    def check_activity_within_days(self, ticket_info, days=10):
        """檢查活動是否在指定天數內"""
        try:
            if not ticket_info.get('date'):
                return False
            
            date_str = ticket_info['date']
            
            # 處理相對時間
            if 'hours ago' in date_str.lower():
                return True  # 幾小時前肯定在10天內
            elif 'days ago' in date_str.lower():
                # 提取天數
                import re
                match = re.search(r'(\d+)\s*days?\s*ago', date_str.lower())
                if match:
                    days_ago = int(match.group(1))
                    return days_ago <= days
                return True  # 如果無法解析，假設在範圍內
            elif 'minutes ago' in date_str.lower():
                return True  # 幾分鐘前肯定在10天內
            elif 'today' in date_str.lower() or 'yesterday' in date_str.lower():
                return True
            elif '分鐘前' in date_str or '小時前' in date_str or '天前' in date_str:
                return True
            
            # 嘗試解析具體日期
            date_formats = [
                "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
                "%Y年%m月%d日", "%m月%d日", "%d日%m月%Y年"
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    days_diff = (datetime.now() - parsed_date).days
                    return days_diff <= days
                except ValueError:
                    continue
            
            # 如果都無法解析，檢查是否包含相對時間詞
            relative_time_keywords = ['ago', '前']
            for keyword in relative_time_keywords:
                if keyword.lower() in date_str.lower():
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"檢查日期失敗: {e}")
            return False
    
    def get_ticket_detailed_interactions(self, ticket_info):
        """獲取 ticket 的詳細互動內容"""
        try:
            if not ticket_info.get('full_url'):
                logger.warning(f"無法獲取詳細內容：缺少完整 URL")
                return []
            
            print(f"  🔍 獲取詳細內容: {ticket_info['full_url']}")
            
            # 導航到 ticket 詳細頁面
            self.driver.get(ticket_info['full_url'])
            time.sleep(3)
            
            # 等待頁面載入
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                logger.warning(f"頁面載入超時: {ticket_info['full_url']}")
                return []
            
            # 解析頁面內容
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            interactions = []
            
            # 直接尋找 <div dir="ltr"> 標籤，這些包含實際的回應訊息
            ltr_divs = soup.find_all('div', attrs={'dir': 'ltr'})
            print(f"  📝 找到 {len(ltr_divs)} 個 <div dir='ltr'> 標籤")
            
            # 尋找互動內容的常見選擇器作為容器
            interaction_selectors = [
                '.conversation', '.conversations', '.messages', '.message',
                '.activity', '.activities', '.timeline', '.feed',
                '.comment', '.comments', '.reply', '.replies',
                '.thread', '.thread-item', '.conversation-item',
                '.ticket-conversation', '.ticket-messages'
            ]
            
            found_interactions = []
            for selector in interaction_selectors:
                elements = soup.select(selector)
                if elements:
                    found_interactions.extend(elements)
                    break
            
            # 如果沒有找到，嘗試更通用的方法
            if not found_interactions:
                # 尋找包含時間戳的元素
                time_patterns = ['ago', '前', 'hours', 'days', 'minutes', '小時', '天', '分鐘']
                for pattern in time_patterns:
                    time_elements = soup.find_all(string=lambda text: text and pattern in text)
                    if time_elements:
                        for time_element in time_elements:
                            parent = time_element.parent
                            if parent and parent.name in ['div', 'span', 'p', 'li']:
                                found_interactions.append(parent)
            
            # 提取互動信息
            for interaction in found_interactions[:10]:  # 限制為前10個互動
                try:
                    interaction_info = {
                        'timestamp': '',
                        'author': '',
                        'content': '',
                        'type': '',
                        'ltr_content': ''  # 新增：<div dir="ltr"> 的內容
                    }
                    
                    # 提取時間戳
                    time_patterns = ['ago', '前', 'hours', 'days', 'minutes', '小時', '天', '分鐘']
                    for pattern in time_patterns:
                        time_elements = interaction.find_all(string=lambda text: text and pattern in text)
                        if time_elements:
                            interaction_info['timestamp'] = time_elements[0].strip()
                            break
                    
                    # 提取作者
                    author_selectors = ['.author', '.user', '.name', '.username', '.by']
                    for selector in author_selectors:
                        author_element = interaction.select_one(selector)
                        if author_element:
                            interaction_info['author'] = author_element.get_text(strip=True)
                            break
                    
                    # 提取內容
                    content_element = interaction.find(['p', 'div', 'span'])
                    if content_element:
                        interaction_info['content'] = content_element.get_text(strip=True)[:300]
                    
                    # 提取 <div dir="ltr"> 的內容
                    ltr_div = interaction.find('div', attrs={'dir': 'ltr'})
                    if ltr_div:
                        ltr_content = ltr_div.get_text(strip=True)
                        interaction_info['ltr_content'] = ltr_content[:500]  # 限制長度
                        print(f"    📄 找到 LTR 內容: {ltr_content[:100]}...")
                    else:
                        # 如果當前互動容器中沒有，嘗試在整個頁面中尋找相關的 ltr_div
                        # 這裡可以根據時間戳或其他標識來匹配
                        pass
                    
                    # 判斷互動類型
                    interaction_text = interaction.get_text(strip=True).lower()
                    if 'customer' in interaction_text or '客戶' in interaction_text:
                        interaction_info['type'] = 'customer_response'
                    elif 'agent' in interaction_text or 'agent responded' in interaction_text:
                        interaction_info['type'] = 'agent_response'
                    elif 'created' in interaction_text or 'opened' in interaction_text:
                        interaction_info['type'] = 'ticket_created'
                    elif 'closed' in interaction_text or 'resolved' in interaction_text:
                        interaction_info['type'] = 'ticket_closed'
                    else:
                        interaction_info['type'] = 'other'
                    
                    if interaction_info['timestamp'] or interaction_info['content'] or interaction_info['ltr_content']:
                        interactions.append(interaction_info)
                
                except Exception as e:
                    logger.warning(f"提取互動信息失敗: {e}")
                    continue
            
            # 如果沒有找到足夠的互動，直接處理 ltr_divs
            if len(interactions) < len(ltr_divs):
                print(f"  🔄 直接處理 {len(ltr_divs)} 個 LTR div...")
                for i, ltr_div in enumerate(ltr_divs[:10]):  # 限制為前10個
                    try:
                        # 尋找相關的時間戳（在 ltr_div 附近）
                        parent_container = ltr_div.parent
                        timestamp = ''
                        
                        # 在父容器中尋找時間戳
                        time_patterns = ['ago', '前', 'hours', 'days', 'minutes', '小時', '天', '分鐘']
                        for pattern in time_patterns:
                            time_elements = parent_container.find_all(string=lambda text: text and pattern in text)
                            if time_elements:
                                timestamp = time_elements[0].strip()
                                break
                        
                        # 尋找作者信息
                        author = ''
                        author_selectors = ['.author', '.user', '.name', '.username', '.by']
                        for selector in author_selectors:
                            author_element = parent_container.select_one(selector)
                            if author_element:
                                author = author_element.get_text(strip=True)
                                break
                        
                        interaction_info = {
                            'timestamp': timestamp,
                            'author': author,
                            'content': ltr_div.get_text(strip=True)[:300],
                            'type': 'response',
                            'ltr_content': ltr_div.get_text(strip=True)[:500]
                        }
                        
                        interactions.append(interaction_info)
                        print(f"    📝 LTR {i+1}: {ltr_div.get_text(strip=True)[:100]}...")
                    
                    except Exception as e:
                        logger.warning(f"處理 LTR div 失敗: {e}")
                        continue
            
            print(f"  ✅ 找到 {len(interactions)} 個互動記錄")
            return interactions
            
        except Exception as e:
            logger.error(f"獲取詳細互動內容失敗: {e}")
            return []
    
    def scan_tickets_and_generate_report(self, username, password, days_back=10, max_tickets=50):
        """掃描 tickets 並生成報告"""
        try:
            print(f"🚀 開始掃描 eService tickets...")
            print(f"📅 掃描範圍: 過去 {days_back} 天")
            print(f"📊 最大掃描數量: {max_tickets} 個 tickets")
            print()
            
            # 設定瀏覽器
            self.setup_driver()
            
            # 登入
            if not self.login_to_eservice(username, password):
                return False
            
            # 分析 Dashboard 結構
            containers = self.analyze_dashboard_structure()
            
            # 尋找 ticket 元素
            ticket_elements = self.find_ticket_elements()
            
            if not ticket_elements:
                print("❌ 未找到任何 ticket 元素")
                return False
            
            print(f"\n📋 開始提取 {len(ticket_elements)} 個 tickets 的信息...")
            
            # 提取 ticket 信息
            all_tickets = []
            recent_activities = []
            
            for i, ticket_element in enumerate(ticket_elements):
                print(f"處理 ticket {i+1}/{len(ticket_elements)}...")
                
                ticket_info = self.extract_ticket_info(ticket_element)
                if ticket_info:
                    all_tickets.append(ticket_info)
                    
                    # 調試：顯示提取的信息
                    print(f"  📋 標題: {ticket_info.get('title', 'N/A')[:50]}...")
                    print(f"  📅 日期: {ticket_info.get('date', 'N/A')}")
                    print(f"  📊 狀態: {ticket_info.get('status', 'N/A')}")
                    
                    # 檢查是否在指定天數內
                    is_recent = self.check_activity_within_days(ticket_info, days_back)
                    if is_recent:
                        # 獲取詳細互動內容
                        detailed_interactions = self.get_ticket_detailed_interactions(ticket_info)
                        ticket_info['detailed_interactions'] = detailed_interactions
                        
                        recent_activities.append(ticket_info)
                        print(f"  ✅ 找到最近活動: {ticket_info.get('title', 'N/A')}")
                        print(f"  💬 詳細互動: {len(detailed_interactions)} 個記錄")
                    else:
                        print(f"  ⏰ 不在最近 {days_back} 天內")
                    
                    # 每處理10個ticket顯示一次進度
                    if (i + 1) % 10 == 0:
                        print(f"  📊 已處理 {i+1}/{len(ticket_elements)} 個 tickets，找到 {len(recent_activities)} 個最近活動")
            
            print(f"\n📊 掃描結果:")
            print(f"   總共處理: {len(all_tickets)} 個 tickets")
            print(f"   最近 {days_back} 天活動: {len(recent_activities)} 個")
            
            # 生成報告
            self.generate_report(recent_activities, days_back)
            
            return True
            
        except Exception as e:
            logger.error(f"掃描失敗: {e}")
            return False
        
        finally:
            self.close_driver()
    
    def generate_report(self, activities, days_back):
        """生成報告"""
        try:
            print(f"\n📝 生成報告...")
            
            # 創建報告目錄
            report_dir = "./reports"
            os.makedirs(report_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 生成 JSON 報告
            json_file = f"{report_dir}/eservice_activities_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'report_date': datetime.now().isoformat(),
                    'scan_days': days_back,
                    'total_activities': len(activities),
                    'activities': activities
                }, f, ensure_ascii=False, indent=2)
            
            # 生成 CSV 報告
            csv_file = f"{report_dir}/eservice_activities_{timestamp}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Title', 'Date', 'Status', 'Content', 'URL', 'Source', 'Full_URL', 'Interaction_Count'])
                
                for activity in activities:
                    interaction_count = len(activity.get('detailed_interactions', []))
                    writer.writerow([
                        activity.get('id', ''),
                        activity.get('title', ''),
                        activity.get('date', ''),
                        activity.get('status', ''),
                        activity.get('content', ''),
                        activity.get('url', ''),
                        activity.get('source', ''),
                        activity.get('full_url', ''),
                        interaction_count
                    ])
            
            # 生成詳細互動 CSV 報告
            interactions_csv_file = f"{report_dir}/eservice_interactions_{timestamp}.csv"
            with open(interactions_csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Ticket_ID', 'Ticket_Title', 'Interaction_Timestamp', 'Author', 'Content', 'Type', 'LTR_Content'])
                
                for activity in activities:
                    ticket_id = activity.get('id', '')
                    ticket_title = activity.get('title', '')
                    
                    for interaction in activity.get('detailed_interactions', []):
                        writer.writerow([
                            ticket_id,
                            ticket_title,
                            interaction.get('timestamp', ''),
                            interaction.get('author', ''),
                            interaction.get('content', ''),
                            interaction.get('type', ''),
                            interaction.get('ltr_content', '')
                        ])
            
            # 生成 Markdown 報告
            md_file = f"{report_dir}/eservice_activities_{timestamp}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# eService 活動報告\n\n")
                f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**掃描範圍**: 過去 {days_back} 天\n")
                f.write(f"**活動數量**: {len(activities)} 個\n\n")
                
                if activities:
                    f.write("## 活動列表\n\n")
                    for i, activity in enumerate(activities, 1):
                        f.write(f"### {i}. {activity.get('title', '無標題')}\n")
                        f.write(f"- **ID**: {activity.get('id', 'N/A')}\n")
                        f.write(f"- **日期**: {activity.get('date', 'N/A')}\n")
                        f.write(f"- **狀態**: {activity.get('status', 'N/A')}\n")
                        f.write(f"- **內容**: {activity.get('content', 'N/A')}\n")
                        if activity.get('full_url'):
                            f.write(f"- **完整連結**: {activity.get('full_url')}\n")
                        
                        # 添加詳細互動內容
                        interactions = activity.get('detailed_interactions', [])
                        if interactions:
                            f.write(f"- **互動記錄**: {len(interactions)} 個\n")
                            f.write("  \n")
                            f.write("  #### 詳細互動記錄\n")
                            for j, interaction in enumerate(interactions, 1):
                                f.write(f"  **{j}. {interaction.get('type', 'other')}**\n")
                                f.write(f"  - 時間: {interaction.get('timestamp', 'N/A')}\n")
                                f.write(f"  - 作者: {interaction.get('author', 'N/A')}\n")
                                f.write(f"  - 內容: {interaction.get('content', 'N/A')}\n")
                                if interaction.get('ltr_content'):
                                    f.write(f"  - **回應訊息**: {interaction.get('ltr_content', 'N/A')}\n")
                                f.write("  \n")
                        else:
                            f.write("- **互動記錄**: 無\n")
                        
                        f.write("\n")
                else:
                    f.write("## 無活動記錄\n\n")
                    f.write("在指定時間範圍內未找到任何活動記錄。\n")
            
            print(f"✅ 報告已生成:")
            print(f"   📄 JSON: {json_file}")
            print(f"   📊 CSV: {csv_file}")
            print(f"   💬 互動 CSV: {interactions_csv_file}")
            print(f"   📝 Markdown: {md_file}")
            
        except Exception as e:
            logger.error(f"生成報告失敗: {e}")

def main():
    """主函數"""
    print("🔍 eService 活動掃描和報告生成工具")
    print("="*60)
    
    # 獲取用戶輸入
    username = input("請輸入 eService 帳號: ").strip()
    password = getpass.getpass("請輸入 eService 密碼: ").strip()
    
    if not username or not password:
        print("❌ 帳號或密碼不能為空")
        return
    
    # 設定掃描參數
    days_back = 10
    max_tickets = 50
    
    print(f"\n📋 掃描設定:")
    print(f"   掃描範圍: 過去 {days_back} 天")
    print(f"   最大掃描數量: {max_tickets} 個 tickets")
    
    # 確認開始
    confirm = input("\n是否開始掃描？(y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 已取消")
        return
    
    # 開始掃描
    scanner = ActivityScanner()
    success = scanner.scan_tickets_and_generate_report(username, password, days_back, max_tickets)
    
    if success:
        print("\n✅ 掃描完成！請查看 reports 目錄中的報告文件。")
    else:
        print("\n❌ 掃描失敗，請檢查錯誤信息。")

if __name__ == "__main__":
    main()
