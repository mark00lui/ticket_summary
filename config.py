"""
配置檔案 - 包含網站 URL 和選擇器設定
"""

# eService 網站配置 (雙重登入)
ESERVICE_CONFIG = {
    "original_url": "https://e-service.quectel.com",
    "login_url": "https://e-service.quectel.com/a/tickets/filters/search?label=Unresolved%20tickets&orderBy=created_at&orderType=desc&perPage=50&q[]=agent%3Fis_in%3A%5B0%5D&ref=_created",  # 第一次登入 URL
    "second_login_url": "https://quectel-team.freshworks.com/login",  # 第二次登入 URL (Freshworks SSO)
    "is_dual_login": True,  # 標記為雙重登入
    "selectors": {
        # 第一次登入選擇器
        "username_input": "#user_session_email, input[name='user_session[email]'], input[type='email']",
        "password_input": "#user_session_password, input[name='user_session[password]'], input[type='password']",
        "login_button": ".btn.btn-primary.btn-login, button[type='submit']",
        # 第二次登入選擇器 (Freshworks)
        "second_username_input": "input[name='email'], input[type='email'], #email",
        "second_password_input": "input[name='password'], input[type='password'], #password",
        "second_login_button": "button[type='submit'], input[type='submit'], .login-btn",
        # 活動記錄選擇器
        "activity_list": ".activity-list, .ticket-list, .conversation-list",
        "activity_item": ".activity-item, .ticket-item, .conversation-item",
        "activity_date": ".date, .timestamp, .created-date",
        "activity_title": ".title, .subject, .ticket-title",
        "activity_content": ".content, .description, .message",
        "activity_status": ".status, .state, .ticket-status"
    }
}

# Jira 配置
JIRA_CONFIG = {
    "login_url": "https://ticket.quectel.com/secure/Dashboard.jspa",  # 實際的登入 URL
    "selectors": {
        "username_input": "#login-form-username, input[name='os_username'], input[type='text']",
        "password_input": "#login-form-password, input[name='os_password'], input[type='password']",
        "login_button": "#login, .aui-button.aui-button-primary, button[type='submit']",
        "activity_list": ".activity-stream, .issue-list, .dashboard-content",
        "activity_item": ".activity-item, .issue-item, .dashboard-item",
        "activity_date": ".date, .timestamp, .created-date",
        "activity_title": ".title, .summary, .issue-summary",
        "activity_content": ".content, .description, .issue-description",
        "activity_status": ".status, .issue-status, .priority"
    }
}

# 週報配置
REPORT_CONFIG = {
    "output_dir": "./reports",
    "template_dir": "./templates",
    "date_format": "%Y-%m-%d",
    "time_format": "%H:%M:%S",
    "week_start": "monday",  # monday 或 sunday
    "categories": {
        "customer_support": ["客戶支援", "客服", "支援"],
        "bug_fixes": ["錯誤修復", "bug", "缺陷"],
        "feature_development": ["功能開發", "新功能", "enhancement"],
        "meetings": ["會議", "討論", "會議記錄"],
        "documentation": ["文件", "文檔", "documentation"],
        "other": ["其他", "雜項"]
    }
}

# Chrome 配置
CHROME_CONFIG = {
    "headless": False,  # 設為 True 可隱藏瀏覽器視窗
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "implicit_wait": 10,
    "page_load_timeout": 30
}
