"""
手動瀏覽工具 - 幫助找到活動記錄的位置
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

def manual_browse_for_activities(site_name, site_config):
    """手動瀏覽尋找活動記錄"""
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
        
        print(f"🔍 手動瀏覽 {site_name} 尋找活動記錄...")
        print(f"📍 起始 URL: {site_config['login_url']}")
        print()
        
        # 步驟 1: 登入
        print("步驟 1: 登入...")
        username = input(f"請輸入 {site_name} 帳號: ").strip()
        password = getpass.getpass(f"請輸入 {site_name} 密碼: ").strip()
        
        if not username or not password:
            print("❌ 帳號或密碼不能為空")
            return
        
        print("\n🔐 正在登入...")
        
        # 使用現有的登入邏輯
        from browser_automation import BrowserAutomation
        browser = BrowserAutomation()
        browser.driver = driver
        browser.wait = wait
        
        login_success = browser.login_to_website(site_config, username, password)
        
        if not login_success:
            print("❌ 登入失敗")
            return
        
        print("✅ 登入成功！")
        
        # 步驟 2: 手動瀏覽指導
        print("\n步驟 2: 手動瀏覽指導...")
        print("現在請在瀏覽器中手動瀏覽，尋找包含活動記錄的頁面")
        print("常見的活動記錄位置：")
        print("  - 我的工單 (My Tickets)")
        print("  - 最近活動 (Recent Activity)")
        print("  - 工單列表 (Ticket List)")
        print("  - 活動流 (Activity Stream)")
        print("  - 儀表板 (Dashboard)")
        print("  - 報告 (Reports)")
        print()
        
        while True:
            print("\n當前頁面信息：")
            current_url = driver.current_url
            current_title = driver.title
            print(f"📍 URL: {current_url}")
            print(f"📄 標題: {current_title}")
            
            # 分析當前頁面
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 尋找可能的活動記錄容器
            print("\n🔍 分析當前頁面...")
            
            # 常見的活動記錄選擇器
            activity_selectors = [
                '.activity', '.activities', '.activity-list', '.activity-stream',
                '.ticket', '.tickets', '.ticket-list', '.issue', '.issues', '.issue-list',
                '.conversation', '.conversations', '.message', '.messages',
                '.dashboard', '.dashboard-content', '.recent', '.recent-activity',
                '.timeline', '.feed', '.news', '.updates',
                '.my-tickets', '.my-issues', '.assigned-to-me',
                '.created-by-me', '.reported-by-me',
                '.table', '.list', '.grid', '.items'
            ]
            
            found_activities = []
            for selector in activity_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ 找到可能的容器: {selector} ({len(elements)} 個元素)")
                    found_activities.append(selector)
            
            if not found_activities:
                print("❌ 未找到常見的活動記錄容器")
            
            # 尋找包含日期的元素
            print("\n🔍 尋找包含日期的元素...")
            date_patterns = ['2024', '2023', '2025', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            date_elements = []
            
            for pattern in date_patterns:
                elements = soup.find_all(string=lambda text: text and pattern in text)
                if elements:
                    print(f"✅ 找到包含日期的元素: {pattern} ({len(elements)} 個)")
                    date_elements.extend(elements[:3])  # 只取前3個
            
            # 尋找表格和列表
            print("\n🔍 尋找表格和列表...")
            tables = soup.find_all('table')
            lists = soup.find_all(['ul', 'ol'])
            
            if tables:
                print(f"✅ 找到表格: {len(tables)} 個")
            if lists:
                print(f"✅ 找到列表: {len(lists)} 個")
            
            # 用戶選擇
            print("\n請選擇操作：")
            print("1. 繼續瀏覽其他頁面")
            print("2. 分析當前頁面的 HTML 結構")
            print("3. 記錄當前頁面為活動記錄頁面")
            print("4. 退出")
            
            choice = input("\n請選擇 (1-4): ").strip()
            
            if choice == "1":
                print("請在瀏覽器中導航到其他頁面，然後按 Enter 繼續...")
                input()
                continue
            elif choice == "2":
                print("\n📋 當前頁面 HTML 結構分析：")
                print("="*50)
                
                # 分析頁面結構
                print(f"頁面標題: {soup.title.string if soup.title else 'N/A'}")
                print(f"主要區域數量: {len(soup.find_all(['main', 'section', 'div'], class_=True))}")
                
                # 尋找主要內容區域
                main_content = soup.find(['main', 'section', 'div'], class_=True)
                if main_content:
                    print(f"主要內容區域: {main_content.get('class', 'N/A')}")
                
                # 尋找導航菜單
                nav_elements = soup.find_all(['nav', 'ul', 'ol'], class_=True)
                print(f"導航元素: {len(nav_elements)} 個")
                
                # 尋找按鈕和鏈接
                buttons = soup.find_all(['button', 'a'], class_=True)
                print(f"按鈕和鏈接: {len(buttons)} 個")
                
                print("="*50)
                input("按 Enter 繼續...")
                
            elif choice == "3":
                print("\n📝 記錄活動記錄頁面信息：")
                print(f"URL: {current_url}")
                print(f"標題: {current_title}")
                print(f"找到的容器: {found_activities}")
                print(f"日期元素: {len(date_elements)} 個")
                print(f"表格: {len(tables)} 個")
                print(f"列表: {len(lists)} 個")
                
                # 保存到文件
                with open(f"{site_name.lower()}_activity_page_info.txt", "w", encoding="utf-8") as f:
                    f.write(f"活動記錄頁面信息\n")
                    f.write(f"="*50 + "\n")
                    f.write(f"URL: {current_url}\n")
                    f.write(f"標題: {current_title}\n")
                    f.write(f"找到的容器: {found_activities}\n")
                    f.write(f"日期元素數量: {len(date_elements)}\n")
                    f.write(f"表格數量: {len(tables)}\n")
                    f.write(f"列表數量: {len(lists)}\n")
                
                print(f"✅ 信息已保存到 {site_name.lower()}_activity_page_info.txt")
                break
                
            elif choice == "4":
                print("👋 再見！")
                break
            else:
                print("❌ 無效選擇，請重新輸入")
        
    except Exception as e:
        print(f"❌ 瀏覽過程中發生錯誤: {e}")
        logger.error(f"瀏覽錯誤: {e}")
    
    finally:
        if driver:
            print("\n🔄 關閉瀏覽器...")
            try:
                driver.quit()
            except:
                pass

def main():
    """主函數"""
    print("🔍 手動瀏覽工具")
    print("="*50)
    print("這個工具會幫助您手動瀏覽並找到活動記錄")
    print("請選擇要瀏覽的網站:")
    print("1. 瀏覽 eService 尋找活動記錄")
    print("2. 瀏覽 Jira 尋找活動記錄")
    print("3. 退出")
    
    while True:
        choice = input("\n請選擇 (1-3): ").strip()
        
        if choice == "1":
            manual_browse_for_activities("eService", config.ESERVICE_CONFIG)
            break
        elif choice == "2":
            manual_browse_for_activities("Jira", config.JIRA_CONFIG)
            break
        elif choice == "3":
            print("👋 再見！")
            break
        else:
            print("❌ 無效選擇，請重新輸入")

if __name__ == "__main__":
    main()
