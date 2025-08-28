"""
雙重登入配置工具 - 處理需要兩次登入的網站
"""

import time
import logging
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

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_dual_login_flow(site_name, site_config):
    """分析雙重登入流程"""
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
        
        print(f"🔍 分析 {site_name} 雙重登入流程...")
        print(f"📍 起始 URL: {site_config['login_url']}")
        print()
        
        # 步驟 1: 導航到初始登入頁面
        print("步驟 1: 導航到初始登入頁面...")
        driver.get(site_config['login_url'])
        time.sleep(3)
        
        initial_url = driver.current_url
        initial_title = driver.title
        print(f"📍 初始 URL: {initial_url}")
        print(f"📄 初始標題: {initial_title}")
        print()
        
        # 步驟 2: 分析第一次登入頁面
        print("步驟 2: 分析第一次登入頁面...")
        initial_page_source = driver.page_source
        initial_soup = BeautifulSoup(initial_page_source, 'html.parser')
        
        # 分析第一次登入表單
        initial_forms = initial_soup.find_all('form')
        print(f"找到 {len(initial_forms)} 個表單")
        
        for i, form in enumerate(initial_forms):
            print(f"\n📋 第一次登入表單 {i+1}:")
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
        
        # 步驟 3: 進行第一次登入
        print("\n步驟 3: 進行第一次登入...")
        username = input(f"請輸入 {site_name} 帳號: ").strip()
        password = getpass.getpass(f"請輸入 {site_name} 密碼: ").strip()
        
        if not username or not password:
            print("❌ 帳號或密碼不能為空")
            return
        
        print("\n🔐 正在進行第一次登入...")
        
        # 使用現有的登入邏輯
        from browser_automation import BrowserAutomation
        browser = BrowserAutomation()
        browser.driver = driver
        browser.wait = wait
        
        first_login_success = browser.login_to_website(site_config, username, password)
        
        if first_login_success:
            print("✅ 第一次登入成功！")
            
            # 步驟 4: 分析第二次登入頁面
            print("\n步驟 4: 分析第二次登入頁面...")
            time.sleep(3)
            
            second_url = driver.current_url
            second_title = driver.title
            print(f"📍 第二次登入 URL: {second_url}")
            print(f"📄 第二次登入標題: {second_title}")
            
            # 分析第二次登入頁面
            second_page_source = driver.page_source
            second_soup = BeautifulSoup(second_page_source, 'html.parser')
            
            # 分析第二次登入表單
            second_forms = second_soup.find_all('form')
            print(f"找到 {len(second_forms)} 個表單")
            
            for i, form in enumerate(second_forms):
                print(f"\n📋 第二次登入表單 {i+1}:")
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
            
            # 步驟 5: 手動完成第二次登入
            print("\n步驟 5: 請手動完成第二次登入...")
            print("請在瀏覽器中完成第二次登入，然後按 Enter 繼續...")
            input()
            
            # 步驟 6: 分析最終頁面
            print("\n步驟 6: 分析最終頁面...")
            time.sleep(2)
            
            final_url = driver.current_url
            final_title = driver.title
            print(f"📍 最終 URL: {final_url}")
            print(f"📄 最終標題: {final_title}")
            
            # 分析最終頁面
            final_page_source = driver.page_source
            final_soup = BeautifulSoup(final_page_source, 'html.parser')
            
            # 尋找活動記錄
            print("\n🔍 尋找活動記錄區域...")
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
            
            # 總結和建議
            print("\n" + "="*60)
            print("💡 雙重登入分析結果:")
            print("="*60)
            print(f"1. 第一次登入 URL: {initial_url}")
            print(f"2. 第二次登入 URL: {second_url}")
            print(f"3. 最終 Dashboard URL: {final_url}")
            print(f"4. 活動記錄容器: {len(found_activities)} 個")
            
            print("\n🔧 配置建議:")
            print("1. 第一次登入使用現有配置")
            print("2. 需要為第二次登入創建新的配置")
            print("3. 需要更新活動記錄選擇器")
            
            print("\n📝 請記錄以下信息:")
            print(f"   - 第二次登入 URL: {second_url}")
            print("   - 第二次登入表單的選擇器")
            print("   - 活動記錄的選擇器")
            
        else:
            print("❌ 第一次登入失敗")
        
        print("\n" + "="*60)
        input("按 Enter 繼續...")
        
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {e}")
        logger.error(f"分析錯誤: {e}")
    
    finally:
        if driver:
            print("\n🔄 關閉瀏覽器...")
            try:
                driver.quit()
            except:
                pass

def main():
    """主函數"""
    print("🔐 雙重登入配置工具")
    print("="*50)
    print("這個工具會幫助您分析雙重登入流程")
    print("請選擇要分析的網站:")
    print("1. 分析 eService 雙重登入")
    print("2. 分析 Jira 雙重登入")
    print("3. 退出")
    
    while True:
        choice = input("\n請選擇 (1-3): ").strip()
        
        if choice == "1":
            analyze_dual_login_flow("eService", config.ESERVICE_CONFIG)
            break
        elif choice == "2":
            analyze_dual_login_flow("Jira", config.JIRA_CONFIG)
            break
        elif choice == "3":
            print("👋 再見！")
            break
        else:
            print("❌ 無效選擇，請重新輸入")

if __name__ == "__main__":
    main()
