#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriver测试脚本
用于验证ChromeDriver是否正确配置
"""

import os
import sys
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import time

def check_chrome_version():
    """检查Chrome浏览器版本"""
    try:
        # Windows Chrome路径
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME'))
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"✅ 找到Chrome浏览器: {path}")
                
                # 获取版本信息
                try:
                    result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        print(f"📋 Chrome版本: {version}")
                        return path, version
                except Exception as e:
                    print(f"⚠️ 无法获取Chrome版本: {e}")
                
                return path, "未知版本"
        
        print("❌ 未找到Chrome浏览器")
        return None, None
        
    except Exception as e:
        print(f"❌ 检查Chrome版本时出错: {e}")
        return None, None

def check_chromedriver():
    """检查ChromeDriver是否可用"""
    print("\n🔍 检查ChromeDriver...")
    
    # 检查当前目录
    current_dir = os.getcwd()
    chromedriver_path = os.path.join(current_dir, "chromedriver.exe")
    
    if os.path.exists(chromedriver_path):
        print(f"✅ 找到ChromeDriver: {chromedriver_path}")
        return chromedriver_path
    
    # 检查PATH环境变量
    try:
        result = subprocess.run(["chromedriver", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ ChromeDriver在PATH中可用: {version}")
            return "chromedriver"
    except Exception:
        pass
    
    print("❌ 未找到ChromeDriver")
    return None

def test_basic_webdriver():
    """测试基本的WebDriver功能"""
    print("\n🧪 测试基本WebDriver功能...")
    
    try:
        # 配置Chrome选项
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-proxy-server")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        
        # 检查ChromeDriver
        chromedriver_path = check_chromedriver()
        if not chromedriver_path:
            print("❌ ChromeDriver不可用，请先配置ChromeDriver")
            return False
        
        # 创建WebDriver
        if chromedriver_path != "chromedriver":
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        print("✅ WebDriver启动成功")
        
        # 测试基本功能
        print("📱 测试页面访问...")
        driver.get("https://www.baidu.com")
        
        # 等待页面加载
        time.sleep(3)
        
        # 获取页面信息
        title = driver.title
        url = driver.current_url
        
        print(f"📋 页面标题: {title}")
        print(f"🔗 当前URL: {url}")
        
        # 关闭浏览器
        driver.quit()
        print("✅ WebDriver测试成功！")
        
        return True
        
    except WebDriverException as e:
        print(f"❌ WebDriver错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_metaso_access():
    """测试访问Metaso页面"""
    print("\n🌐 测试Metaso页面访问...")
    
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # 检查ChromeDriver
        chromedriver_path = check_chromedriver()
        if not chromedriver_path:
            print("❌ ChromeDriver不可用")
            return False
        
        # 创建WebDriver
        if chromedriver_path != "chromedriver":
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        # 访问Metaso
        metaso_url = "https://metaso.cn/file/8651522172447916032"
        print(f"📱 访问: {metaso_url}")
        
        driver.get(metaso_url)
        time.sleep(5)
        
        # 获取页面信息
        title = driver.title
        print(f"📋 页面标题: {title}")
        
        # 检查是否需要登录
        page_source = driver.page_source
        if "登录" in page_source or "login" in page_source.lower():
            print("⚠️ 页面可能需要登录")
        
        # 查找视频元素
        video_elements = driver.find_elements("tag name", "video")
        if video_elements:
            print(f"✅ 找到 {len(video_elements)} 个视频元素")
        else:
            print("⚠️ 未找到视频元素")
        
        # 截图保存
        screenshot_path = "metaso_page_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 页面截图已保存: {screenshot_path}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Metaso访问测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 ChromeDriver配置测试")
    print("=" * 50)
    
    # 检查Chrome浏览器
    chrome_path, chrome_version = check_chrome_version()
    if not chrome_path:
        print("\n❌ 请先安装Chrome浏览器")
        return
    
    # 测试基本WebDriver功能
    if test_basic_webdriver():
        print("\n✅ 基本WebDriver功能正常")
        
        # 测试Metaso访问
        if test_metaso_access():
            print("\n✅ Metaso页面访问测试完成")
        else:
            print("\n⚠️ Metaso页面访问可能有问题")
    else:
        print("\n❌ WebDriver配置有问题")
        print("\n💡 解决建议:")
        print("1. 检查Chrome和ChromeDriver版本是否匹配")
        print("2. 下载正确版本的ChromeDriver: https://chromedriver.chromium.org/")
        print("3. 将chromedriver.exe放在当前目录或PATH中")
        print("4. 查看详细配置指南: CHROMEDRIVER_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()