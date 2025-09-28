#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境设置脚本
自动安装和配置苹果ID自动登录工具所需的环境
"""

import os
import sys
import subprocess
import platform

def run_command(command, description=""):
    """运行系统命令"""
    print(f"🔧 {description}")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def install_chrome_driver():
    """安装Chrome浏览器驱动"""
    system = platform.system().lower()
    
    if system == "linux":
        # Ubuntu/Debian系统
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y wget unzip",
            "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
            "sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'",
            "sudo apt-get update",
            "sudo apt-get install -y google-chrome-stable"
        ]
        
        for cmd in commands:
            if not run_command(cmd, f"安装Chrome浏览器依赖"):
                return False
                
    elif system == "darwin":  # macOS
        if not run_command("brew --version", "检查Homebrew"):
            print("请先安装Homebrew: https://brew.sh/")
            return False
        
        if not run_command("brew install --cask google-chrome", "安装Chrome浏览器"):
            print("Chrome可能已经安装，继续...")
    
    elif system == "windows":
        print("Windows系统请手动下载安装Chrome浏览器:")
        print("https://www.google.com/chrome/")
        input("安装完成后按Enter继续...")
    
    return True

def install_python_dependencies():
    """安装Python依赖包"""
    print("\n📦 安装Python依赖包...")
    
    # 升级pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip")
    
    # 安装依赖
    if os.path.exists("requirements.txt"):
        return run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                          "安装项目依赖")
    else:
        # 手动安装核心依赖
        dependencies = [
            "selenium>=4.15.0",
            "webdriver-manager>=4.0.1", 
            "requests>=2.31.0"
        ]
        
        for dep in dependencies:
            if not run_command(f"{sys.executable} -m pip install {dep}", 
                             f"安装 {dep}"):
                return False
        return True

def create_config_template():
    """创建配置文件模板"""
    config_template = {
        "email": "your_apple_id@example.com",
        "password": "your_password_here"
    }
    
    import json
    
    try:
        with open("apple_credentials_template.json", "w", encoding="utf-8") as f:
            json.dump(config_template, f, indent=2, ensure_ascii=False)
        
        print("✅ 配置文件模板已创建: apple_credentials_template.json")
        print("   您可以复制并重命名为 apple_credentials.json 来保存凭据")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件模板失败: {e}")
        return False

def check_environment():
    """检查环境配置"""
    print("\n🔍 检查环境配置...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        return False
    else:
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要的包
    required_packages = ["selenium", "webdriver_manager"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    return len(missing_packages) == 0

def main():
    """主安装流程"""
    print("🍎 苹果ID自动登录工具 - 环境设置")
    print("=" * 50)
    
    steps = [
        ("检查环境", check_environment),
        ("安装Chrome浏览器", install_chrome_driver),
        ("安装Python依赖", install_python_dependencies),
        ("创建配置模板", create_config_template),
        ("最终检查", check_environment)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🚀 步骤: {step_name}")
        if not step_func():
            print(f"❌ 步骤 '{step_name}' 失败，请检查错误信息")
            return False
    
    print("\n🎉 环境设置完成!")
    print("\n📝 使用说明:")
    print("1. 运行 'python apple_id_auto_login.py' 开始自动登录")
    print("2. 首次运行时会提示输入苹果ID和密码")
    print("3. 可以选择保存凭据以便下次使用")
    print("4. 支持双重认证，会在需要时提示输入验证码")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  安装被用户中断")
    except Exception as e:
        print(f"\n❌ 安装过程出现异常: {e}")
        sys.exit(1)