#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全增强版苹果ID自动登录工具
包含密码加密存储、安全检查等功能
"""

import os
import json
import getpass
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring

class SecureCredentialManager:
    """安全凭据管理器"""
    
    def __init__(self, service_name="apple_id_login"):
        self.service_name = service_name
        self.config_file = "secure_config.enc"
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """从密码派生加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_credentials(self, email: str, password: str, master_password: str) -> bool:
        """加密并保存凭据"""
        try:
            # 生成随机盐
            salt = os.urandom(16)
            
            # 派生加密密钥
            key = self._derive_key(master_password, salt)
            cipher = Fernet(key)
            
            # 准备数据
            credentials = {
                'email': email,
                'password': password
            }
            
            # 加密数据
            encrypted_data = cipher.encrypt(json.dumps(credentials).encode())
            
            # 保存到文件
            with open(self.config_file, 'wb') as f:
                f.write(salt + encrypted_data)
            
            print("✅ 凭据已加密保存")
            return True
            
        except Exception as e:
            print(f"❌ 加密保存失败: {e}")
            return False
    
    def decrypt_credentials(self, master_password: str) -> tuple:
        """解密凭据"""
        try:
            if not os.path.exists(self.config_file):
                return None, None
            
            # 读取文件
            with open(self.config_file, 'rb') as f:
                data = f.read()
            
            # 提取盐和加密数据
            salt = data[:16]
            encrypted_data = data[16:]
            
            # 派生密钥并解密
            key = self._derive_key(master_password, salt)
            cipher = Fernet(key)
            
            decrypted_data = cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            
            return credentials['email'], credentials['password']
            
        except Exception as e:
            print(f"❌ 解密失败: {e}")
            return None, None
    
    def save_to_keyring(self, email: str, password: str) -> bool:
        """使用系统密钥环保存凭据"""
        try:
            keyring.set_password(self.service_name, email, password)
            print("✅ 凭据已保存到系统密钥环")
            return True
        except Exception as e:
            print(f"❌ 保存到密钥环失败: {e}")
            return False
    
    def get_from_keyring(self, email: str) -> str:
        """从系统密钥环获取密码"""
        try:
            password = keyring.get_password(self.service_name, email)
            return password
        except Exception as e:
            print(f"❌ 从密钥环获取失败: {e}")
            return None

class SecurityChecker:
    """安全检查器"""
    
    @staticmethod
    def check_password_strength(password: str) -> dict:
        """检查密码强度"""
        issues = []
        score = 0
        
        if len(password) >= 8:
            score += 1
        else:
            issues.append("密码长度应至少8位")
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            issues.append("应包含大写字母")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            issues.append("应包含小写字母")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            issues.append("应包含数字")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            issues.append("应包含特殊字符")
        
        strength_levels = {
            0: "极弱",
            1: "很弱", 
            2: "弱",
            3: "中等",
            4: "强",
            5: "很强"
        }
        
        return {
            'score': score,
            'strength': strength_levels[score],
            'issues': issues
        }
    
    @staticmethod
    def check_email_format(email: str) -> bool:
        """检查邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def check_network_security():
        """检查网络安全性"""
        import socket
        import ssl
        
        try:
            # 检查是否能访问苹果服务器
            context = ssl.create_default_context()
            with socket.create_connection(("appleid.apple.com", 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname="appleid.apple.com") as ssock:
                    print("✅ 网络连接正常，SSL证书有效")
                    return True
        except Exception as e:
            print(f"❌ 网络安全检查失败: {e}")
            return False

def secure_input_credentials():
    """安全的凭据输入流程"""
    credential_manager = SecureCredentialManager()
    security_checker = SecurityChecker()
    
    print("\n🔐 安全凭据输入")
    print("=" * 30)
    
    # 检查是否有已保存的凭据
    storage_options = []
    
    # 检查加密文件
    if os.path.exists("secure_config.enc"):
        storage_options.append("encrypted_file")
    
    # 检查系统密钥环
    email_hint = input("如果之前保存过凭据，请输入邮箱以检查密钥环: ").strip()
    if email_hint and credential_manager.get_from_keyring(email_hint):
        storage_options.append("keyring")
    
    if storage_options:
        print("\n检测到已保存的凭据:")
        for i, option in enumerate(storage_options, 1):
            if option == "encrypted_file":
                print(f"{i}. 加密文件")
            elif option == "keyring":
                print(f"{i}. 系统密钥环")
        
        print(f"{len(storage_options) + 1}. 重新输入凭据")
        
        choice = input(f"请选择 (1-{len(storage_options) + 1}): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(storage_options):
                selected_option = storage_options[choice_idx]
                
                if selected_option == "encrypted_file":
                    master_password = getpass.getpass("请输入主密码解锁凭据: ")
                    email, password = credential_manager.decrypt_credentials(master_password)
                    if email and password:
                        return email, password
                    else:
                        print("解锁失败，请重新输入")
                
                elif selected_option == "keyring":
                    password = credential_manager.get_from_keyring(email_hint)
                    if password:
                        return email_hint, password
                    else:
                        print("从密钥环获取失败，请重新输入")
        
        except (ValueError, IndexError):
            print("无效选择，请重新输入凭据")
    
    # 手动输入新凭据
    while True:
        email = input("\n请输入苹果ID邮箱: ").strip()
        
        if not email:
            print("❌ 邮箱不能为空")
            continue
        
        if not security_checker.check_email_format(email):
            print("❌ 邮箱格式不正确")
            continue
        
        break
    
    while True:
        password = getpass.getpass("请输入密码: ")
        
        if not password:
            print("❌ 密码不能为空")
            continue
        
        # 检查密码强度
        strength_result = security_checker.check_password_strength(password)
        print(f"\n密码强度: {strength_result['strength']} ({strength_result['score']}/5)")
        
        if strength_result['issues']:
            print("密码强度建议:")
            for issue in strength_result['issues']:
                print(f"  - {issue}")
        
        if strength_result['score'] < 3:
            use_weak = input("密码强度较弱，是否继续使用? (y/n): ").lower() == 'y'
            if not use_weak:
                continue
        
        break
    
    # 保存凭据选项
    print("\n💾 凭据保存选项:")
    print("1. 不保存（每次都需要输入）")
    print("2. 加密文件保存（需要主密码）")
    print("3. 系统密钥环保存（推荐）")
    
    save_choice = input("请选择保存方式 (1-3): ").strip()
    
    if save_choice == "2":
        while True:
            master_password = getpass.getpass("设置主密码（用于加密凭据）: ")
            confirm_password = getpass.getpass("确认主密码: ")
            
            if master_password == confirm_password:
                credential_manager.encrypt_credentials(email, password, master_password)
                break
            else:
                print("❌ 密码不匹配，请重新设置")
    
    elif save_choice == "3":
        credential_manager.save_to_keyring(email, password)
    
    return email, password

def main():
    """安全版本主函数"""
    print("🔒 安全增强版苹果ID自动登录工具")
    print("=" * 50)
    
    # 执行安全检查
    security_checker = SecurityChecker()
    
    print("\n🔍 执行安全检查...")
    if not security_checker.check_network_security():
        print("⚠️  网络安全检查失败，建议检查网络连接")
        proceed = input("是否继续? (y/n): ").lower() == 'y'
        if not proceed:
            return
    
    # 安全获取凭据
    try:
        email, password = secure_input_credentials()
        
        print(f"\n✅ 凭据获取成功")
        print(f"邮箱: {email}")
        print("密码: " + "*" * len(password))
        
        # 这里可以调用原始的登录代码
        print("\n🚀 准备执行登录...")
        print("💡 提示: 现在可以调用 apple_id_auto_login.py 的登录功能")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    main()