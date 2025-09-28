#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苹果ID自动登录工具使用示例
演示不同的使用方法和配置选项
"""

from apple_id_auto_login import AppleIDLogin
import logging

# 配置日志级别
logging.basicConfig(level=logging.INFO)

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 最简单的使用方式
    with AppleIDLogin() as login_tool:
        success = login_tool.login()
        print(f"登录结果: {'成功' if success else '失败'}")

def example_headless_mode():
    """无头模式示例"""
    print("=== 无头模式示例 ===")
    
    # 使用无头模式（后台运行，不显示浏览器窗口）
    with AppleIDLogin(headless=True) as login_tool:
        success = login_tool.login()
        print(f"无头模式登录结果: {'成功' if success else '失败'}")

def example_custom_credentials():
    """自定义凭据示例"""
    print("=== 自定义凭据示例 ===")
    
    # 直接提供邮箱和密码
    email = "your_email@example.com"  # 替换为实际邮箱
    password = "your_password"        # 替换为实际密码
    
    with AppleIDLogin(wait_timeout=60) as login_tool:
        success = login_tool.login(email, password)
        print(f"自定义凭据登录结果: {'成功' if success else '失败'}")

def example_step_by_step():
    """分步骤控制示例"""
    print("=== 分步骤控制示例 ===")
    
    login_tool = AppleIDLogin()
    
    try:
        # 1. 获取凭据
        email, password = login_tool.get_credentials()
        print(f"获取到凭据: {email}")
        
        # 2. 导航到登录页面
        if login_tool.navigate_to_login_page():
            print("✅ 登录页面加载成功")
        else:
            print("❌ 登录页面加载失败")
            return
        
        # 3. 填写凭据
        if login_tool.fill_credentials(email, password):
            print("✅ 凭据填写成功")
        else:
            print("❌ 凭据填写失败")
            return
        
        # 4. 提交登录
        if login_tool.submit_login():
            print("✅ 登录表单提交成功")
        else:
            print("❌ 登录表单提交失败")
            return
        
        # 5. 处理双重认证（如果需要）
        if login_tool.handle_two_factor_auth():
            print("✅ 双重认证处理完成")
        else:
            print("❌ 双重认证处理失败")
            return
        
        # 6. 检查登录结果
        success = login_tool.check_login_success()
        print(f"最终登录结果: {'成功' if success else '失败'}")
        
    except Exception as e:
        print(f"登录过程出现异常: {e}")
    
    finally:
        login_tool.close()

def example_error_handling():
    """错误处理示例"""
    print("=== 错误处理示例 ===")
    
    try:
        with AppleIDLogin() as login_tool:
            # 尝试使用无效凭据登录
            success = login_tool.login("invalid@email.com", "wrongpassword")
            
            if not success:
                print("登录失败，可能的原因:")
                print("1. 邮箱或密码错误")
                print("2. 网络连接问题")
                print("3. 苹果服务器限制")
                print("4. 需要双重认证")
    
    except Exception as e:
        print(f"发生异常: {e}")
        print("建议检查:")
        print("- Chrome浏览器是否正确安装")
        print("- 网络连接是否正常")
        print("- 防火墙设置是否阻止访问")

def main():
    """主函数 - 运行所有示例"""
    print("🍎 苹果ID自动登录工具 - 使用示例")
    print("=" * 50)
    
    examples = [
        ("基础使用", example_basic_usage),
        ("无头模式", example_headless_mode),
        ("自定义凭据", example_custom_credentials),
        ("分步骤控制", example_step_by_step),
        ("错误处理", example_error_handling)
    ]
    
    print("可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("0. 运行所有示例")
    
    try:
        choice = input("\n请选择要运行的示例 (0-5): ").strip()
        
        if choice == "0":
            for name, func in examples:
                print(f"\n{'='*20} {name} {'='*20}")
                func()
        else:
            index = int(choice) - 1
            if 0 <= index < len(examples):
                name, func = examples[index]
                print(f"\n{'='*20} {name} {'='*20}")
                func()
            else:
                print("无效选择")
    
    except ValueError:
        print("请输入有效的数字")
    except KeyboardInterrupt:
        print("\n\n用户中断操作")

if __name__ == "__main__":
    main()