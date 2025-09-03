#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Selenium Metaso视频下载器
"""

import time
import os
import sys
from pathlib import Path
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ 请先安装selenium: pip install selenium")
    sys.exit(1)

def check_chromedriver():
    """检查ChromeDriver是否可用"""
    print("🔍 检查ChromeDriver...")
    
    try:
        # 尝试使用系统PATH中的chromedriver
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("✅ ChromeDriver可用")
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver不可用: {e}")
        print("\n💡 解决方案:")
        print("   1. 确保已安装Chrome浏览器")
        print("   2. 下载对应版本的ChromeDriver: https://chromedriver.chromium.org/")
        print("   3. 将chromedriver.exe放在系统PATH中或当前目录")
        print("   4. 或者使用: pip install webdriver-manager")
        return False

def simple_browser_test():
    """简单的浏览器测试"""
    print("\n🌐 启动浏览器进行简单测试...")
    
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,720")
        
        # 不使用headless模式，让用户可以看到浏览器
        print("📱 启动Chrome浏览器...")
        driver = webdriver.Chrome(options=options)
        
        # 访问Metaso页面
        target_url = "https://metaso.cn/search/8651522172447916032"
        print(f"🔗 访问: {target_url}")
        driver.get(target_url)
        
        # 等待页面加载
        time.sleep(5)
        
        print(f"📄 页面标题: {driver.title}")
        print(f"🌐 当前URL: {driver.current_url}")
        
        # 创建截图目录
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)
        
        # 截图
        screenshot_path = download_dir / "metaso_page_screenshot.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"📸 页面截图已保存: {screenshot_path}")
        
        # 查找页面元素
        print("\n🔍 分析页面元素:")
        
        # 查找视频相关元素
        video_elements = driver.find_elements(By.TAG_NAME, "video")
        print(f"   视频元素: {len(video_elements)}个")
        
        # 查找链接
        links = driver.find_elements(By.TAG_NAME, "a")
        video_links = []
        download_links = []
        
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip().lower()
            
            if href:
                if 'video' in href.lower() or '.mp4' in href.lower():
                    video_links.append(href)
                if 'download' in href.lower() or 'download' in text:
                    download_links.append(href)
        
        print(f"   视频相关链接: {len(video_links)}个")
        for i, link in enumerate(video_links[:5]):  # 只显示前5个
            print(f"     {i+1}. {link}")
        
        print(f"   下载相关链接: {len(download_links)}个")
        for i, link in enumerate(download_links[:5]):  # 只显示前5个
            print(f"     {i+1}. {link}")
        
        # 查找按钮
        buttons = driver.find_elements(By.TAG_NAME, "button")
        relevant_buttons = []
        
        for button in buttons:
            text = button.text.strip().lower()
            onclick = button.get_attribute("onclick") or ""
            class_name = button.get_attribute("class") or ""
            
            if any(keyword in text for keyword in ['下载', 'download', '导出', 'export', '生成', 'generate']):
                relevant_buttons.append({
                    'text': button.text,
                    'onclick': onclick,
                    'class': class_name
                })
        
        print(f"   相关按钮: {len(relevant_buttons)}个")
        for i, btn in enumerate(relevant_buttons[:3]):  # 只显示前3个
            print(f"     {i+1}. 文本: '{btn['text']}', 类: '{btn['class']}'")
        
        # 检查页面源码中的关键信息
        page_source = driver.page_source.lower()
        keywords = ['video', 'mp4', 'download', 'stream', 'blob:']
        
        print("\n🔍 页面关键词检查:")
        for keyword in keywords:
            count = page_source.count(keyword)
            if count > 0:
                print(f"   '{keyword}': 出现{count}次")
        
        # 保持浏览器打开让用户查看
        print("\n⏳ 浏览器将保持打开状态60秒，请手动查看页面...")
        print("   您可以:")
        print("   1. 查看页面是否显示视频")
        print("   2. 尝试手动点击下载按钮")
        print("   3. 检查浏览器开发者工具的网络选项卡")
        print("   4. 按Ctrl+C提前结束")
        
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n⚠️ 用户中断")
        
        driver.quit()
        print("🔒 浏览器已关闭")
        
        return True
        
    except Exception as e:
        print(f"❌ 浏览器测试失败: {e}")
        return False

def install_webdriver_manager():
    """安装webdriver-manager"""
    print("\n📦 尝试安装webdriver-manager...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "webdriver-manager"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ webdriver-manager安装成功")
            return True
        else:
            print(f"❌ 安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安装异常: {e}")
        return False

def try_webdriver_manager():
    """尝试使用webdriver-manager"""
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        print("🔧 使用webdriver-manager自动管理ChromeDriver...")
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 简单测试
        driver.get("https://www.google.com")
        print(f"✅ 测试成功: {driver.title}")
        driver.quit()
        
        return True
        
    except ImportError:
        print("❌ webdriver-manager未安装")
        return False
    except Exception as e:
        print(f"❌ webdriver-manager测试失败: {e}")
        return False

def main():
    print("="*80)
    print("🎬 简化版Metaso视频下载器")
    print("="*80)
    
    # 检查ChromeDriver
    if check_chromedriver():
        # 直接进行浏览器测试
        simple_browser_test()
    else:
        # 尝试安装和使用webdriver-manager
        print("\n🔧 尝试使用webdriver-manager解决ChromeDriver问题...")
        
        if install_webdriver_manager():
            if try_webdriver_manager():
                print("\n✅ webdriver-manager配置成功，重新运行脚本应该可以工作")
            else:
                print("\n❌ webdriver-manager配置失败")
        
        print("\n💡 手动解决方案:")
        print("   1. 打开Chrome浏览器，访问 chrome://version/ 查看版本")
        print("   2. 访问 https://chromedriver.chromium.org/downloads")
        print("   3. 下载对应版本的ChromeDriver")
        print("   4. 将chromedriver.exe放在当前目录或系统PATH中")
        print("   5. 重新运行此脚本")

if __name__ == "__main__":
    main()