#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苹果ID自动登录脚本
支持账号密码输入和自动化登录流程
"""

import time
import getpass
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('apple_login.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppleIDLogin:
    """苹果ID自动登录类"""
    
    def __init__(self, headless=False, wait_timeout=30):
        """
        初始化登录器
        
        Args:
            headless (bool): 是否使用无头模式
            wait_timeout (int): 等待超时时间（秒）
        """
        self.wait_timeout = wait_timeout
        self.driver = None
        self.wait = None
        self.setup_driver(headless)
        
    def setup_driver(self, headless=False):
        """设置浏览器驱动"""
        try:
            chrome_options = Options()
            
            # 基础配置
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # 隐私和安全设置
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--disable-default-apps')
            
            # 用户代理设置
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            if headless:
                chrome_options.add_argument('--headless')
                
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
            
            logger.info("浏览器驱动初始化成功")
            
        except Exception as e:
            logger.error(f"浏览器驱动初始化失败: {e}")
            raise
    
    def get_credentials(self):
        """安全获取用户凭据"""
        print("\n=== 苹果ID登录凭据输入 ===")
        
        # 检查是否有保存的凭据配置文件
        config_file = "apple_credentials.json"
        if os.path.exists(config_file):
            use_saved = input("检测到已保存的凭据配置，是否使用? (y/n): ").lower() == 'y'
            if use_saved:
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        credentials = json.load(f)
                    return credentials['email'], credentials['password']
                except Exception as e:
                    logger.warning(f"读取保存的凭据失败: {e}")
        
        # 手动输入凭据
        email = input("请输入苹果ID邮箱: ").strip()
        if not email:
            raise ValueError("邮箱不能为空")
            
        password = getpass.getpass("请输入密码: ")
        if not password:
            raise ValueError("密码不能为空")
        
        # 询问是否保存凭据
        save_credentials = input("是否保存凭据以便下次使用? (y/n): ").lower() == 'y'
        if save_credentials:
            try:
                credentials = {
                    'email': email,
                    'password': password
                }
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(credentials, f, indent=2)
                logger.info("凭据已保存到配置文件")
            except Exception as e:
                logger.warning(f"保存凭据失败: {e}")
        
        return email, password
    
    def navigate_to_login_page(self):
        """导航到苹果ID登录页面"""
        try:
            login_url = "https://appleid.apple.com/sign-in"
            logger.info(f"导航到登录页面: {login_url}")
            
            self.driver.get(login_url)
            
            # 等待页面加载
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            logger.info("登录页面加载完成")
            return True
            
        except TimeoutException:
            logger.error("登录页面加载超时")
            return False
        except Exception as e:
            logger.error(f"导航到登录页面失败: {e}")
            return False
    
    def fill_credentials(self, email, password):
        """填写登录凭据"""
        try:
            logger.info("开始填写登录凭据")
            
            # 等待并填写邮箱
            email_selectors = [
                '#account_name_text_field',
                'input[type="email"]',
                'input[name="accountName"]',
                '#signIn.appleId'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not email_input:
                raise Exception("找不到邮箱输入框")
            
            email_input.clear()
            email_input.send_keys(email)
            logger.info("邮箱已填写")
            
            # 点击继续按钮（如果需要）
            try:
                continue_button = self.driver.find_element(By.CSS_SELECTOR, '#sign-in')
                if continue_button.is_enabled():
                    continue_button.click()
                    time.sleep(2)
            except NoSuchElementException:
                pass
            
            # 等待并填写密码
            password_selectors = [
                '#password_text_field',
                'input[type="password"]',
                'input[name="password"]',
                '#signIn.password'
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not password_input:
                raise Exception("找不到密码输入框")
            
            password_input.clear()
            password_input.send_keys(password)
            logger.info("密码已填写")
            
            return True
            
        except Exception as e:
            logger.error(f"填写凭据失败: {e}")
            return False
    
    def submit_login(self):
        """提交登录表单"""
        try:
            logger.info("提交登录表单")
            
            # 查找登录按钮
            login_button_selectors = [
                '#sign-in',
                'button[type="submit"]',
                '.signin-button',
                '.btn-signin'
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                raise Exception("找不到登录按钮")
            
            login_button.click()
            logger.info("登录按钮已点击")
            
            # 等待页面响应
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"提交登录失败: {e}")
            return False
    
    def handle_two_factor_auth(self):
        """处理双重认证"""
        try:
            logger.info("检查是否需要双重认证")
            
            # 检查是否出现双重认证页面
            two_factor_selectors = [
                '.two-factor',
                '.verification-code',
                'input[name="code"]',
                '#code'
            ]
            
            for selector in two_factor_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        logger.info("检测到双重认证页面")
                        
                        # 提示用户输入验证码
                        verification_code = input("\n请输入双重认证验证码: ").strip()
                        
                        if verification_code:
                            code_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="code"], #code')
                            code_input.clear()
                            code_input.send_keys(verification_code)
                            
                            # 提交验证码
                            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], .continue-button')
                            submit_button.click()
                            
                            time.sleep(3)
                            logger.info("双重认证验证码已提交")
                            return True
                        
                except NoSuchElementException:
                    continue
            
            logger.info("未检测到双重认证要求")
            return True
            
        except Exception as e:
            logger.error(f"处理双重认证失败: {e}")
            return False
    
    def check_login_success(self):
        """检查登录是否成功"""
        try:
            logger.info("检查登录状态")
            
            # 等待页面加载完成
            time.sleep(5)
            
            current_url = self.driver.current_url
            logger.info(f"当前URL: {current_url}")
            
            # 检查是否登录成功的指标
            success_indicators = [
                'appleid.apple.com/account',
                'appleid.apple.com/#/personal',
                '/account'
            ]
            
            for indicator in success_indicators:
                if indicator in current_url:
                    logger.info("登录成功!")
                    return True
            
            # 检查是否有错误信息
            error_selectors = [
                '.error',
                '.alert-error',
                '.signin-error'
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if error_element.is_displayed():
                        error_text = error_element.text
                        logger.error(f"登录错误: {error_text}")
                        return False
                except NoSuchElementException:
                    continue
            
            # 如果没有明确的成功或失败指示，检查页面标题
            page_title = self.driver.title
            if "Sign In" not in page_title:
                logger.info("登录可能成功（基于页面标题判断）")
                return True
            
            logger.warning("登录状态不明确")
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
    
    def login(self, email=None, password=None):
        """执行完整的登录流程"""
        try:
            logger.info("开始苹果ID自动登录流程")
            
            # 获取凭据
            if not email or not password:
                email, password = self.get_credentials()
            
            # 导航到登录页面
            if not self.navigate_to_login_page():
                return False
            
            # 填写凭据
            if not self.fill_credentials(email, password):
                return False
            
            # 提交登录
            if not self.submit_login():
                return False
            
            # 处理双重认证（如果需要）
            if not self.handle_two_factor_auth():
                return False
            
            # 检查登录结果
            success = self.check_login_success()
            
            if success:
                logger.info("=== 登录流程完成 ===")
                print("\n✅ 苹果ID登录成功!")
                
                # 保持浏览器打开一段时间以便用户查看
                input("\n按Enter键退出...")
            else:
                logger.error("=== 登录失败 ===")
                print("\n❌ 苹果ID登录失败，请检查凭据或网络连接")
            
            return success
            
        except Exception as e:
            logger.error(f"登录流程出现异常: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


def main():
    """主函数"""
    print("🍎 苹果ID自动登录工具")
    print("=" * 50)
    
    try:
        # 配置选项
        headless_mode = input("是否使用无头模式? (y/n): ").lower() == 'y'
        
        # 创建登录器并执行登录
        with AppleIDLogin(headless=headless_mode) as login_tool:
            success = login_tool.login()
            
            if not success:
                print("\n💡 提示:")
                print("1. 请确保网络连接正常")
                print("2. 检查苹果ID和密码是否正确")
                print("3. 如果启用了双重认证，请准备好验证设备")
                print("4. 某些地区可能需要VPN访问苹果服务")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        logger.error(f"程序执行出现异常: {e}")
        print(f"\n❌ 执行失败: {e}")


if __name__ == "__main__":
    main()