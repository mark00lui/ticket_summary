"""
瀏覽器自動化模組
處理 Chrome 瀏覽器的登入和資料抓取
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
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

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserAutomation:
    """瀏覽器自動化類別"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """設定 Chrome 瀏覽器驅動程式"""
        try:
            chrome_options = Options()
            
            if config.CHROME_CONFIG["headless"]:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument(f"--window-size={config.CHROME_CONFIG['window_size']}")
            chrome_options.add_argument(f"--user-agent={config.CHROME_CONFIG['user_agent']}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # 自動下載並設定 ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 設定等待時間
            self.driver.implicitly_wait(config.CHROME_CONFIG["implicit_wait"])
            self.driver.set_page_load_timeout(config.CHROME_CONFIG["page_load_timeout"])
            
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Chrome 瀏覽器已成功啟動")
            
        except Exception as e:
            logger.error(f"啟動 Chrome 瀏覽器失敗: {e}")
            raise
    
    def close_driver(self):
        """關閉瀏覽器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome 瀏覽器已關閉")
            except Exception as e:
                logger.warning(f"關閉瀏覽器時發生錯誤: {e}")
                # 嘗試強制關閉
                try:
                    self.driver.close()
                except:
                    pass
    
    def find_element_by_selectors(self, selectors: str) -> Optional[webdriver.remote.webelement.WebElement]:
        """使用多個選擇器尋找元素"""
        selector_list = [s.strip() for s in selectors.split(',')]
        
        for selector in selector_list:
            try:
                if selector.startswith('#'):
                    element = self.driver.find_element(By.ID, selector[1:])
                elif selector.startswith('.'):
                    element = self.driver.find_element(By.CLASS_NAME, selector[1:])
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element
            except NoSuchElementException:
                continue
        
        return None
    
    def wait_for_element(self, selectors: str, timeout: int = 10):
        """等待元素出現"""
        selector_list = [s.strip() for s in selectors.split(',')]
        
        for selector in selector_list:
            try:
                if selector.startswith('#'):
                    element = self.wait.until(
                        EC.presence_of_element_located((By.ID, selector[1:]))
                    )
                elif selector.startswith('.'):
                    element = self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, selector[1:]))
                    )
                else:
                    element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                return element
            except TimeoutException:
                continue
        
        raise TimeoutException(f"無法找到元素: {selectors}")
    
    def login_to_website(self, site_config: Dict, username: str, password: str) -> bool:
        """登入網站"""
        try:
            logger.info(f"正在登入: {site_config['login_url']}")
            
            # 檢查是否為雙重登入
            is_dual_login = site_config.get('is_dual_login', False)
            
            # 第一次登入
            first_login_success = self._perform_first_login(site_config, username, password)
            
            if not first_login_success:
                logger.error("第一次登入失敗")
                return False
            
            # 如果是雙重登入，進行第二次登入
            if is_dual_login:
                logger.info("檢測到雙重登入，正在進行第二次登入...")
                second_login_success = self._perform_second_login(site_config, username, password)
                
                if not second_login_success:
                    logger.error("第二次登入失敗")
                    return False
                
                logger.info("雙重登入完成")
                return True
            else:
                logger.info("單次登入完成")
                return True
                
        except Exception as e:
            logger.error(f"登入過程中發生錯誤: {e}")
            return False
    
    def _perform_first_login(self, site_config: Dict, username: str, password: str) -> bool:
        """執行第一次登入"""
        try:
            # 導航到登入頁面
            self.driver.get(site_config['login_url'])
            time.sleep(2)
            
            # 檢查當前 URL 和頁面標題
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"第一次登入 URL: {current_url}")
            logger.info(f"第一次登入標題: {page_title}")
            
            # 等待頁面載入
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 輸入使用者名稱
            username_input = self.find_element_by_selectors(site_config['selectors']['username_input'])
            if username_input:
                username_input.clear()
                username_input.send_keys(username)
                logger.info("已輸入使用者名稱")
            else:
                logger.error("無法找到使用者名稱輸入欄位")
                logger.error(f"嘗試的選擇器: {site_config['selectors']['username_input']}")
                return False
            
            # 輸入密碼
            password_input = self.find_element_by_selectors(site_config['selectors']['password_input'])
            if password_input:
                password_input.clear()
                password_input.send_keys(password)
                logger.info("已輸入密碼")
            else:
                logger.error("無法找到密碼輸入欄位")
                logger.error(f"嘗試的選擇器: {site_config['selectors']['password_input']}")
                return False
            
            # 點擊登入按鈕
            login_button = self.find_element_by_selectors(site_config['selectors']['login_button'])
            if login_button:
                login_button.click()
                logger.info("已點擊第一次登入按鈕")
                
                # 等待登入完成
                time.sleep(3)
                
                # 檢查是否成功（對於雙重登入，成功意味著被重定向到第二次登入頁面）
                new_url = self.driver.current_url
                new_title = self.driver.title
                logger.info(f"第一次登入後 URL: {new_url}")
                logger.info(f"第一次登入後標題: {new_title}")
                
                # 檢查登入結果
                if site_config.get('is_dual_login', False):
                    # 雙重登入：檢查是否被重定向到第二次登入頁面
                    if 'freshworks.com' in new_url.lower() or 'freshdesk.com' in new_url.lower():
                        logger.info("第一次登入成功，已重定向到第二次登入頁面")
                        return True
                    elif 'e-service.quectel.com' in new_url.lower() and 'login' not in new_url.lower():
                        logger.info("第一次登入成功，已進入 Dashboard")
                        return True
                    else:
                        logger.warning("第一次登入可能失敗，未重定向到預期頁面")
                        logger.warning(f"當前 URL: {new_url}")
                        return False
                else:
                    # 單次登入：檢查是否離開登入頁面
                    if "login" not in new_url.lower():
                        logger.info("登入成功")
                        return True
                    else:
                        logger.warning("登入可能失敗，請檢查帳號密碼")
                        return False
            else:
                logger.error("無法找到登入按鈕")
                logger.error(f"嘗試的選擇器: {site_config['selectors']['login_button']}")
                return False
                
        except Exception as e:
            logger.error(f"第一次登入過程中發生錯誤: {e}")
            return False
    
    def _perform_second_login(self, site_config: Dict, username: str, password: str) -> bool:
        """執行第二次登入"""
        try:
            # 等待頁面載入
            time.sleep(2)
            
            # 檢查當前 URL 和頁面標題
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"第二次登入 URL: {current_url}")
            logger.info(f"第二次登入標題: {page_title}")
            
            # 等待頁面載入
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 輸入使用者名稱（第二次登入可能使用相同的帳號或不同的欄位）
            username_input = self.find_element_by_selectors(site_config['selectors']['second_username_input'])
            if username_input:
                username_input.clear()
                username_input.send_keys(username)
                logger.info("已輸入第二次登入使用者名稱")
            else:
                logger.error("無法找到第二次登入使用者名稱輸入欄位")
                logger.error(f"嘗試的選擇器: {site_config['selectors']['second_username_input']}")
                return False
            
            # 輸入密碼
            password_input = self.find_element_by_selectors(site_config['selectors']['second_password_input'])
            if password_input:
                password_input.clear()
                password_input.send_keys(password)
                logger.info("已輸入第二次登入密碼")
            else:
                logger.error("無法找到第二次登入密碼輸入欄位")
                logger.error(f"嘗試的選擇器: {site_config['selectors']['second_password_input']}")
                return False
            
            # 點擊登入按鈕
            login_button = self.find_element_by_selectors(site_config['selectors']['second_login_button'])
            if login_button:
                login_button.click()
                logger.info("已點擊第二次登入按鈕")
                
                # 等待登入完成
                time.sleep(3)
                
                # 檢查是否成功進入 dashboard
                new_url = self.driver.current_url
                new_title = self.driver.title
                logger.info(f"第二次登入後 URL: {new_url}")
                logger.info(f"第二次登入後標題: {new_title}")
                
                # 檢查是否成功進入 dashboard
                dashboard_indicators = [
                    'dashboard' in new_url.lower(),
                    'dashboard' in new_title.lower(),
                    'freshdesk.com' in new_url.lower() and 'login' not in new_url.lower(),
                    'e-service.quectel.com' in new_url.lower() and 'login' not in new_url.lower()
                ]
                
                if any(dashboard_indicators):
                    logger.info("第二次登入成功，已進入 Dashboard")
                    return True
                else:
                    logger.warning("第二次登入可能失敗，請檢查帳號密碼")
                    return False
            else:
                logger.error("無法找到第二次登入按鈕")
                logger.error(f"嘗試的選擇器: {site_config['selectors']['second_login_button']}")
                return False
                
        except Exception as e:
            logger.error(f"第二次登入過程中發生錯誤: {e}")
            return False
    
    def fetch_activities(self, site_config: Dict, days_back: int = 7) -> List[Dict]:
        """抓取活動資料"""
        activities = []
        
        try:
            logger.info(f"正在抓取過去 {days_back} 天的活動")
            
            # 等待活動列表載入
            activity_list = self.find_element_by_selectors(site_config['selectors']['activity_list'])
            if not activity_list:
                logger.warning("無法找到活動列表")
                return activities
            
            # 解析活動項目
            activity_items = activity_list.find_elements(By.CSS_SELECTOR, site_config['selectors']['activity_item'])
            
            for item in activity_items:
                try:
                    activity = self._parse_activity_item(item, site_config)
                    if activity:
                        # 檢查日期是否在指定範圍內
                        if self._is_within_date_range(activity['date'], days_back):
                            activities.append(activity)
                except Exception as e:
                    logger.warning(f"解析活動項目時發生錯誤: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(activities)} 個活動")
            
        except Exception as e:
            logger.error(f"抓取活動時發生錯誤: {e}")
        
        return activities
    
    def _parse_activity_item(self, item, site_config: Dict) -> Optional[Dict]:
        """解析單個活動項目"""
        try:
            # 提取日期
            date_element = item.find_element(By.CSS_SELECTOR, site_config['selectors']['activity_date'])
            date_text = date_element.text.strip()
            parsed_date = self._parse_date(date_text)
            
            # 提取標題
            title_element = item.find_element(By.CSS_SELECTOR, site_config['selectors']['activity_title'])
            title = title_element.text.strip()
            
            # 提取內容
            content_element = item.find_element(By.CSS_SELECTOR, site_config['selectors']['activity_content'])
            content = content_element.text.strip()
            
            # 提取狀態
            status = ""
            try:
                status_element = item.find_element(By.CSS_SELECTOR, site_config['selectors']['activity_status'])
                status = status_element.text.strip()
            except NoSuchElementException:
                pass
            
            return {
                'date': parsed_date,
                'title': title,
                'content': content,
                'status': status,
                'source': 'eservice' if 'eservice' in site_config['login_url'].lower() else 'jira'
            }
            
        except Exception as e:
            logger.warning(f"解析活動項目失敗: {e}")
            return None
    
    def _parse_date(self, date_text: str) -> datetime:
        """解析日期文字"""
        # 常見的日期格式
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y年%m月%d日",
            "%m月%d日",
            "%d日%m月%Y年"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue
        
        # 如果都無法解析，返回當前日期
        logger.warning(f"無法解析日期: {date_text}，使用當前日期")
        return datetime.now()
    
    def _is_within_date_range(self, activity_date: datetime, days_back: int) -> bool:
        """檢查活動日期是否在指定範圍內"""
        start_date = datetime.now() - timedelta(days=days_back)
        return activity_date >= start_date
