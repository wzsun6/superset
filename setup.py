#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苹果ID自动登录工具 - 安装脚本
"""

import subprocess
import sys
import os


def install_requirements():
    """安装Python依赖"""
    try:
        print("正在安装Python依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False


def check_chrome():
    """检查Chrome浏览器是否安装"""
    try:
        # 检查Chrome是否在PATH中
        subprocess.run(["google-chrome", "--version"], 
                      capture_output=True, check=True)
        print("✓ Chrome浏览器已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # 尝试其他可能的Chrome命令
            subprocess.run(["chromium-browser", "--version"], 
                          capture_output=True, check=True)
            print("✓ Chromium浏览器已安装")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠ 未检测到Chrome/Chromium浏览器")
            print("请安装Google Chrome浏览器: https://www.google.com/chrome/")
            return False


def setup_chromedriver():
    """设置ChromeDriver"""
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("正在下载并配置ChromeDriver...")
        ChromeDriverManager().install()
        print("✓ ChromeDriver配置完成")
        return True
    except ImportError:
        print("正在安装webdriver-manager...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
        return setup_chromedriver()
    except Exception as e:
        print(f"ChromeDriver配置失败: {e}")
        print("请手动下载ChromeDriver: https://chromedriver.chromium.org/")
        return False


def create_config():
    """创建配置文件"""
    config_file = "config.json"
    if not os.path.exists(config_file):
        print("创建配置文件...")
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("""{
    "apple_id": "",
    "password": "",
    "apple_website": "https://appleid.apple.com/",
    "chrome_driver_path": "",
    "headless": false,
    "wait_timeout": 10
}""")
        print(f"✓ 配置文件已创建: {config_file}")
        print("请编辑config.json文件，填写您的Apple ID和密码")
    else:
        print("✓ 配置文件已存在")


def main():
    """主安装流程"""
    print("苹果ID自动登录工具 - 安装向导")
    print("=" * 50)
    
    # 1. 安装Python依赖
    if not install_requirements():
        print("❌ 安装失败：无法安装Python依赖")
        return False
    
    # 2. 检查Chrome浏览器
    check_chrome()
    
    # 3. 设置ChromeDriver
    setup_chromedriver()
    
    # 4. 创建配置文件
    create_config()
    
    print("\n" + "=" * 50)
    print("✓ 安装完成！")
    print("\n使用步骤：")
    print("1. 编辑 config.json 文件，填写您的Apple ID和密码")
    print("2. 运行: python apple_auto_login.py")
    print("\n注意事项：")
    print("- 请确保网络连接正常")
    print("- 如果开启了双重认证，需要手动输入验证码")
    print("- 请妥善保管配置文件中的密码信息")
    
    return True


if __name__ == "__main__":
    main()