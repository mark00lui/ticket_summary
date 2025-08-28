"""
網站診斷工具 - 幫助識別正確的登入 URL 和頁面結構
"""

import time
import logging
import getpass
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

def diagnose_website(site_name, site_config):
    """診斷網站結構並嘗試登入"""
    driver = None
    try:
        # 設定 Chrome 選項
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 啟動瀏覽器
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print(f"🔍 開始診斷 {site_name} 網站...")
        print(f"📍 目標 URL: {site_config['login_url']}")
        print()
        
        # 步驟 1: 導航到網站
        print("步驟 1: 導航到網站...")
        driver.get(site_config['login_url'])
        time.sleep(3)
        
        # 檢查當前 URL
        current_url = driver.current_url
        print(f"📍 當前 URL: {current_url}")
        print(f"📄 頁面標題: {driver.title}")
        print()
        
        # 步驟 2: 分析頁面內容
        print("步驟 2: 分析頁面內容...")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 尋找可能的登入表單
        print("🔍 尋找登入表單...")
        forms = soup.find_all('form')
        print(f"找到 {len(forms)} 個表單")
        
        for i, form in enumerate(forms):
            print(f"\n📋 表單 {i+1}:")
            print(f"   Action: {form.get('action', 'N/A')}")
            print(f"   Method: {form.get('method', 'N/A')}")
            print(f"   ID: {form.get('id', 'N/A')}")
            print(f"   Class: {form.get('class', 'N/A')}")
            
            # 尋找輸入欄位
            inputs = form.find_all('input')
            print(f"   輸入欄位 ({len(inputs)} 個):")
            for inp in inputs:
                input_type = inp.get('type', 'text')
                input_name = inp.get('name', 'N/A')
                input_id = inp.get('id', 'N/A')
                input_placeholder = inp.get('placeholder', 'N/A')
                print(f"     - Type: {input_type}, Name: {input_name}, ID: {input_id}, Placeholder: {input_placeholder}")
        
        # 尋找可能的登入按鈕
        print("\n🔍 尋找登入按鈕...")
        buttons = soup.find_all(['button', 'input'], type=['submit', 'button'])
        print(f"找到 {len(buttons)} 個按鈕")
        
        for i, button in enumerate(buttons):
            print(f"\n🔘 按鈕 {i+1}:")
            print(f"   Type: {button.get('type', 'N/A')}")
            print(f"   Text: {button.get_text(strip=True) or button.get('value', 'N/A')}")
            print(f"   ID: {button.get('id', 'N/A')}")
            print(f"   Class: {button.get('class', 'N/A')}")
        
        # 檢查是否有重定向
        print("\n步驟 3: 檢查重定向...")
        if current_url != site_config['login_url']:
            print(f"⚠️  檢測到重定向: {site_config['login_url']} -> {current_url}")
        else:
            print("✅ 沒有重定向")
        
        # 步驟 4: 處理雙重登入
        print("\n步驟 4: 處理雙重登入...")
        print("檢測到 eService 有雙重登入機制")
        print("請按照以下步驟進行:")
        
        # 詢問帳號密碼
        username = input(f"請輸入 {site_name} 帳號: ").strip()
        password = getpass.getpass(f"請輸入 {site_name} 密碼: ").strip()
        
        if not username or not password:
            print("❌ 帳號或密碼不能為空")
            return
        
        print("\n🔐 正在嘗試第一次登入...")
        
        # 嘗試第一次登入
        from browser_automation import BrowserAutomation
        browser = BrowserAutomation()
        browser.driver = driver
        browser.wait = wait
        
        first_login_success = browser.login_to_website(site_config, username, password)
        
        if first_login_success:
            print("✅ 第一次登入成功！")
            
            # 檢查是否需要第二次登入
            print("\n🔍 檢查是否需要第二次登入...")
            time.sleep(3)
            
            current_url = driver.current_url
            current_title = driver.title
            print(f"📍 當前 URL: {current_url}")
            print(f"📄 當前標題: {current_title}")
            
            # 分析當前頁面
            current_page_source = driver.page_source
            current_soup = BeautifulSoup(current_page_source, 'html.parser')
            
            # 檢查是否還在登入頁面或有新的登入表單
            login_indicators = [
                'login' in current_url.lower(),
                'signin' in current_url.lower(),
                'auth' in current_url.lower(),
                'sso' in current_url.lower(),
                'oauth' in current_url.lower()
            ]
            
            has_login_form = len(current_soup.find_all('form')) > 0
            
            # 檢查是否已經進入 dashboard
            dashboard_indicators = [
                'dashboard' in current_url.lower(),
                'dashboard' in current_title.lower(),
                'home' in current_url.lower(),
                'main' in current_url.lower(),
                'portal' in current_url.lower(),
                'freshdesk.com' in current_url.lower() and 'login' not in current_url.lower(),
                'e-service.quectel.com' in current_url.lower() and 'login' not in current_url.lower()
            ]
            
            if any(dashboard_indicators):
                print("✅ 已經成功進入 Dashboard！")
                login_success = True
            elif any(login_indicators) or has_login_form:
                print("⚠️  檢測到需要第二次登入")
                print("請在瀏覽器中完成第二次登入，然後按 Enter 繼續...")
                input()
                
                # 再次檢查頁面狀態
                time.sleep(2)
                final_url = driver.current_url
                final_title = driver.title
                print(f"📍 最終 URL: {final_url}")
                print(f"📄 最終標題: {final_title}")
                
                # 檢查是否成功進入 dashboard
                final_dashboard_indicators = [
                    'dashboard' in final_url.lower(),
                    'dashboard' in final_title.lower(),
                    'home' in final_url.lower(),
                    'main' in final_url.lower(),
                    'portal' in final_url.lower(),
                    'freshdesk.com' in final_url.lower() and 'login' not in final_url.lower(),
                    'e-service.quectel.com' in final_url.lower() and 'login' not in final_url.lower()
                ]
                
                if any(final_dashboard_indicators):
                    print("✅ 成功進入 Dashboard！")
                    login_success = True
                else:
                    print("❌ 可能還未完全登入")
                    login_success = False
            else:
                print("✅ 看起來已經完成登入")
                login_success = True
            
            if login_success:
                print("\n步驟 5: 分析最終頁面...")
                time.sleep(2)
                
                final_page_source = driver.page_source
                final_soup = BeautifulSoup(final_page_source, 'html.parser')
                
                # 尋找可能的活動記錄區域
                print("\n🔍 尋找可能的活動記錄區域...")
                activity_selectors = [
                    '.activity', '.activities', '.activity-list', '.activity-stream',
                    '.ticket', '.tickets', '.ticket-list', '.issue', '.issues', '.issue-list',
                    '.conversation', '.conversations', '.message', '.messages',
                    '.dashboard', '.dashboard-content', '.recent', '.recent-activity',
                    '.timeline', '.feed', '.news', '.updates',
                    '.my-tickets', '.my-issues', '.assigned-to-me',
                    '.created-by-me', '.reported-by-me'
                ]
                
                found_activities = []
                for selector in activity_selectors:
                    elements = final_soup.select(selector)
                    if elements:
                        print(f"✅ 找到活動記錄容器: {selector} ({len(elements)} 個元素)")
                        found_activities.append(selector)
                
                if not found_activities:
                    print("❌ 未找到常見的活動記錄容器")
                    print("💡 建議手動瀏覽頁面，尋找包含活動記錄的區域")
                
                # 尋找包含日期的元素
                print("\n🔍 尋找包含日期的元素...")
                date_patterns = ['2024', '2023', '2025', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                date_elements = []
                
                for pattern in date_patterns:
                    elements = final_soup.find_all(text=lambda text: text and pattern in text)
                    if elements:
                        print(f"✅ 找到包含日期的元素: {pattern} ({len(elements)} 個)")
                        date_elements.extend(elements[:3])  # 只取前3個
                
                if not date_elements:
                    print("❌ 未找到包含日期的元素")
            else:
                found_activities = []
                date_elements = []
                
        else:
            print("❌ 第一次登入失敗")
            print("💡 可能的原因:")
            print("   - 帳號密碼錯誤")
            print("   - 網站有額外驗證機制")
            print("   - 選擇器配置不正確")
            login_success = False
            found_activities = []
            date_elements = []
        
        # 總結
        print("\n" + "="*60)
        print("💡 診斷總結:")
        print("="*60)
        print(f"1. 登入狀態: {'✅ 成功' if login_success else '❌ 失敗'}")
        print(f"2. 活動記錄容器: {len(found_activities)} 個")
        print(f"3. 日期元素: {len(date_elements)} 個")
        
        if login_success:
            print("\n🔧 下一步建議:")
            print("1. 手動瀏覽頁面，找到活動記錄的實際位置")
            print("2. 告訴我活動記錄的 HTML 結構")
            print("3. 我們可以更新配置來正確提取資料")
        
        print("\n" + "="*60)
        input("按 Enter 繼續...")
        
    except Exception as e:
        print(f"❌ 診斷過程中發生錯誤: {e}")
        logger.error(f"診斷錯誤: {e}")
    
    finally:
        if driver:
            print("\n🔄 關閉瀏覽器...")
            try:
                driver.quit()
            except:
                pass

def diagnose_eservice_website():
    """診斷 eService 網站結構"""
    diagnose_website("eService", config.ESERVICE_CONFIG)

def diagnose_jira_website():
    """診斷 Jira 網站結構"""
    diagnose_website("Jira", config.JIRA_CONFIG)

def test_login_selectors(site_name, site_config):
    """測試登入選擇器"""
    driver = None
    try:
        # 設定 Chrome 選項
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 啟動瀏覽器
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print(f"🧪 測試 {site_name} 登入選擇器...")
        
        # 導航到網站
        driver.get(site_config['login_url'])
        time.sleep(3)
        
        # 測試使用者名稱輸入欄位
        print("\n🔍 測試使用者名稱輸入欄位...")
        username_selectors = site_config['selectors']['username_input'].split(',')
        username_found = False
        
        for selector in username_selectors:
            selector = selector.strip()
            try:
                if selector.startswith('#'):
                    element = driver.find_element(By.ID, selector[1:])
                elif selector.startswith('.'):
                    element = driver.find_element(By.CLASS_NAME, selector[1:])
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                
                print(f"✅ 找到使用者名稱欄位: {selector}")
                username_found = True
                break
            except NoSuchElementException:
                print(f"❌ 找不到使用者名稱欄位: {selector}")
        
        if not username_found:
            print("⚠️  無法找到任何使用者名稱輸入欄位")
        
        # 測試密碼輸入欄位
        print("\n🔍 測試密碼輸入欄位...")
        password_selectors = site_config['selectors']['password_input'].split(',')
        password_found = False
        
        for selector in password_selectors:
            selector = selector.strip()
            try:
                if selector.startswith('#'):
                    element = driver.find_element(By.ID, selector[1:])
                elif selector.startswith('.'):
                    element = driver.find_element(By.CLASS_NAME, selector[1:])
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                
                print(f"✅ 找到密碼欄位: {selector}")
                password_found = True
                break
            except NoSuchElementException:
                print(f"❌ 找不到密碼欄位: {selector}")
        
        if not password_found:
            print("⚠️  無法找到任何密碼輸入欄位")
        
        # 測試登入按鈕
        print("\n🔍 測試登入按鈕...")
        login_selectors = site_config['selectors']['login_button'].split(',')
        login_found = False
        
        for selector in login_selectors:
            selector = selector.strip()
            try:
                if selector.startswith('#'):
                    element = driver.find_element(By.ID, selector[1:])
                elif selector.startswith('.'):
                    element = driver.find_element(By.CLASS_NAME, selector[1:])
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                
                print(f"✅ 找到登入按鈕: {selector}")
                login_found = True
                break
            except NoSuchElementException:
                print(f"❌ 找不到登入按鈕: {selector}")
        
        if not login_found:
            print("⚠️  無法找到任何登入按鈕")
        
        print("\n" + "="*50)
        if username_found and password_found and login_found:
            print("✅ 所有登入元素都找到了！")
        else:
            print("❌ 部分登入元素未找到，需要更新配置")
        print("="*50)
        
        input("按 Enter 繼續...")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        logger.error(f"測試錯誤: {e}")
    
    finally:
        if driver:
            print("\n🔄 關閉瀏覽器...")
            try:
                driver.quit()
            except:
                pass

def test_eservice_selectors():
    """測試 eService 登入選擇器"""
    test_login_selectors("eService", config.ESERVICE_CONFIG)

def test_jira_selectors():
    """測試 Jira 登入選擇器"""
    test_login_selectors("Jira", config.JIRA_CONFIG)

def main():
    """主函數"""
    print("🔧 網站診斷工具")
    print("="*50)
    print("選擇診斷模式:")
    print("1. 診斷 eService 網站結構")
    print("2. 診斷 Jira 網站結構")
    print("3. 測試 eService 登入選擇器")
    print("4. 測試 Jira 登入選擇器")
    print("5. 退出")
    
    while True:
        choice = input("\n請選擇 (1-5): ").strip()
        
        if choice == "1":
            diagnose_eservice_website()
            break
        elif choice == "2":
            diagnose_jira_website()
            break
        elif choice == "3":
            test_eservice_selectors()
            break
        elif choice == "4":
            test_jira_selectors()
            break
        elif choice == "5":
            print("👋 再見！")
            break
        else:
            print("❌ 無效選擇，請重新輸入")

if __name__ == "__main__":
    main()
