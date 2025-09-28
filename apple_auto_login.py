#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苹果ID自动登录脚本
使用Selenium WebDriver自动化登录苹果官网
"""

import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class AppleAutoLogin:
    def __init__(self, config_file="config.json"):
        """
        初始化苹果自动登录类
        
        Args:
            config_file (str): 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.driver = None
        self.wait = None
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 创建默认配置文件
            default_config = {
                "apple_id": "",
                "password": "",
                "apple_website": "https://appleid.apple.com/",
                "chrome_driver_path": "",
                "headless": False,
                "wait_timeout": 10
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            print(f"已创建默认配置文件: {self.config_file}")
            print("请填写您的Apple ID和密码后再运行程序")
            return default_config
    
    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            chrome_options = Options()
            
            # 基础设置
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 设置用户代理
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # 是否无头模式
            if self.config.get('headless', False):
                chrome_options.add_argument('--headless')
            
            # 设置Chrome驱动路径
            if self.config.get('chrome_driver_path'):
                service = Service(self.config['chrome_driver_path'])
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # 尝试使用系统PATH中的chromedriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # 设置窗口大小
            self.driver.set_window_size(1920, 1080)
            
            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 设置等待对象
            self.wait = WebDriverWait(self.driver, self.config.get('wait_timeout', 10))
            
            print("WebDriver 初始化成功")
            return True
            
        except Exception as e:
            print(f"WebDriver 初始化失败: {e}")
            print("请确保已安装Chrome浏览器和对应版本的ChromeDriver")
            return False
    
    def open_apple_website(self):
        """打开苹果官网登录页面"""
        try:
            apple_url = self.config.get('apple_website', 'https://appleid.apple.com/')
            print(f"正在打开苹果官网: {apple_url}")
            
            self.driver.get(apple_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 检查是否成功加载页面
            if "Apple ID" in self.driver.title:
                print("苹果官网页面加载成功")
                return True
            else:
                print("页面加载异常，可能网络问题或网站结构变化")
                return False
                
        except Exception as e:
            print(f"打开苹果官网失败: {e}")
            return False
    
    def find_login_elements(self):
        """查找登录表单元素"""
        try:
            # 等待登录表单加载
            print("正在查找登录表单...")
            
            # 可能的用户名输入框选择器
            username_selectors = [
                '#account_name_text_field',
                'input[name="accountName"]',
                'input[placeholder*="Apple ID"]',
                'input[type="email"]',
                'input[id*="username"]',
                'input[id*="account"]'
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"找到用户名输入框: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                print("未找到用户名输入框")
                return None, None
            
            # 查找密码输入框（可能需要先输入用户名后才出现）
            password_selectors = [
                '#password_text_field',
                'input[name="password"]',
                'input[type="password"]',
                'input[id*="password"]'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"找到密码输入框: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            return username_field, password_field
            
        except Exception as e:
            print(f"查找登录元素失败: {e}")
            return None, None
    
    def auto_login(self):
        """执行自动登录"""
        try:
            if not self.config.get('apple_id') or not self.config.get('password'):
                print("请在配置文件中设置Apple ID和密码")
                return False
            
            # 查找登录元素
            username_field, password_field = self.find_login_elements()
            
            if not username_field:
                print("无法找到登录表单，可能网站结构已变化")
                return False
            
            # 输入用户名
            print("正在输入Apple ID...")
            username_field.clear()
            username_field.send_keys(self.config['apple_id'])
            time.sleep(1)
            
            # 查找并点击继续按钮（如果存在）
            continue_selectors = [
                'button[id*="continue"]',
                'button[class*="continue"]',
                'input[type="submit"]',
                'button[type="submit"]'
            ]
            
            continue_button = None
            for selector in continue_selectors:
                try:
                    continue_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if continue_button.is_displayed() and continue_button.is_enabled():
                        print(f"找到继续按钮: {selector}")
                        continue_button.click()
                        time.sleep(2)
                        break
                except NoSuchElementException:
                    continue
            
            # 重新查找密码输入框（可能在点击继续后才出现）
            if not password_field:
                for selector in ['#password_text_field', 'input[name="password"]', 'input[type="password"]']:
                    try:
                        password_field = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        print(f"找到密码输入框: {selector}")
                        break
                    except TimeoutException:
                        continue
            
            if password_field:
                # 输入密码
                print("正在输入密码...")
                password_field.clear()
                password_field.send_keys(self.config['password'])
                time.sleep(1)
                
                # 查找并点击登录按钮
                login_selectors = [
                    'button[id*="sign-in"]',
                    'button[id*="signin"]',
                    'button[class*="sign-in"]',
                    'button[type="submit"]',
                    'input[type="submit"]'
                ]
                
                for selector in login_selectors:
                    try:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if login_button.is_displayed() and login_button.is_enabled():
                            print(f"点击登录按钮: {selector}")
                            login_button.click()
                            break
                    except NoSuchElementException:
                        continue
                
                # 等待登录结果
                print("等待登录结果...")
                time.sleep(5)
                
                # 检查是否登录成功
                current_url = self.driver.current_url
                if "account" in current_url.lower() or "dashboard" in current_url.lower():
                    print("登录成功！")
                    return True
                else:
                    print("登录可能失败，请检查凭据或手动处理验证")
                    return False
            else:
                print("未找到密码输入框")
                return False
                
        except Exception as e:
            print(f"自动登录过程出错: {e}")
            return False
    
    def handle_two_factor_auth(self):
        """处理双重认证（需要手动输入验证码）"""
        try:
            # 检查是否出现双重认证页面
            two_factor_indicators = [
                "verification code",
                "验证码",
                "two-factor",
                "双重认证"
            ]
            
            page_text = self.driver.page_source.lower()
            for indicator in two_factor_indicators:
                if indicator in page_text:
                    print("检测到双重认证，请手动输入验证码...")
                    print("程序将等待60秒供您手动操作...")
                    time.sleep(60)
                    return True
            
            return False
            
        except Exception as e:
            print(f"处理双重认证时出错: {e}")
            return False
    
    def run(self):
        """运行完整的自动登录流程"""
        try:
            print("开始苹果ID自动登录流程...")
            
            # 初始化WebDriver
            if not self.setup_driver():
                return False
            
            # 打开苹果官网
            if not self.open_apple_website():
                return False
            
            # 执行自动登录
            login_success = self.auto_login()
            
            if login_success:
                # 检查是否需要双重认证
                self.handle_two_factor_auth()
                
                print("登录流程完成，浏览器将保持打开状态")
                print("按 Enter 键关闭浏览器...")
                input()
            
            return login_success
            
        except KeyboardInterrupt:
            print("用户中断操作")
            return False
        except Exception as e:
            print(f"运行过程中出错: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                print("浏览器已关闭")


def main():
    """主函数"""
    print("苹果ID自动登录工具")
    print("=" * 50)
    
    # 创建自动登录实例
    auto_login = AppleAutoLogin()
    
    # 运行自动登录
    success = auto_login.run()
    
    if success:
        print("程序执行完成")
    else:
        print("程序执行失败，请检查配置和网络连接")


if __name__ == "__main__":
    main()