#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Selenium自动化浏览器下载Metaso视频
"""

import time
import os
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

class MetasoSeleniumDownloader:
    def __init__(self, chromedriver_path=None, headless=False):
        """
        初始化Selenium下载器
        
        Args:
            chromedriver_path: ChromeDriver路径，如果为None则使用系统PATH中的
            headless: 是否使用无头模式
        """
        self.driver = None
        self.chromedriver_path = chromedriver_path
        self.headless = headless
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        
    def setup_driver(self):
        """设置Chrome浏览器"""
        chrome_options = Options()
        
        # 设置下载目录
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 其他选项
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # 设置User-Agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            if self.chromedriver_path:
                service = Service(self.chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            print("✅ Chrome浏览器启动成功")
            return True
            
        except Exception as e:
            print(f"❌ Chrome浏览器启动失败: {e}")
            return False
    
    def navigate_to_metaso(self, url):
        """导航到Metaso页面"""
        try:
            print(f"🌐 正在访问: {url}")
            self.driver.get(url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print(f"✅ 页面加载完成: {self.driver.title}")
            return True
            
        except TimeoutException:
            print("❌ 页面加载超时")
            return False
        except Exception as e:
            print(f"❌ 页面访问失败: {e}")
            return False
    
    def wait_for_video_generation(self, max_wait_time=300):
        """等待视频生成完成"""
        print(f"⏳ 等待视频生成完成（最多等待{max_wait_time}秒）...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                # 查找可能的视频元素
                video_elements = self.driver.find_elements(By.TAG_NAME, "video")
                if video_elements:
                    print("🎬 发现视频元素!")
                    return True
                
                # 查找下载按钮或链接
                download_selectors = [
                    "[href*='download']",
                    "[href*='video']", 
                    "button[class*='download']",
                    "a[class*='download']",
                    "[data-action='download']"
                ]
                
                for selector in download_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"📥 发现下载元素: {selector}")
                        return True
                
                # 检查页面是否有错误信息
                error_texts = ["生成失败", "错误", "error", "failed"]
                page_text = self.driver.page_source.lower()
                for error_text in error_texts:
                    if error_text in page_text:
                        print(f"❌ 页面显示错误: {error_text}")
                        return False
                
                print(f"⏳ 等待中... ({int(time.time() - start_time)}s)")
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ 检查过程中出现异常: {e}")
                time.sleep(5)
        
        print("⏰ 等待超时")
        return False
    
    def find_and_download_video(self):
        """查找并下载视频"""
        print("🔍 正在查找视频下载方式...")
        
        # 方法1: 查找video标签
        try:
            video_elements = self.driver.find_elements(By.TAG_NAME, "video")
            for i, video in enumerate(video_elements):
                src = video.get_attribute("src")
                if src:
                    print(f"🎬 发现视频源 {i+1}: {src}")
                    if self.download_video_from_url(src, f"video_{i+1}.mp4"):
                        return True
        except Exception as e:
            print(f"⚠️ 查找video标签失败: {e}")
        
        # 方法2: 查找下载链接
        download_selectors = [
            "a[href*='download']",
            "a[href*='video']",
            "a[href*='.mp4']",
            "button[onclick*='download']",
            "[data-action='download']"
        ]
        
        for selector in download_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for i, element in enumerate(elements):
                    href = element.get_attribute("href")
                    onclick = element.get_attribute("onclick")
                    
                    if href:
                        print(f"🔗 发现下载链接 {i+1}: {href}")
                        if self.download_video_from_url(href, f"download_{i+1}.mp4"):
                            return True
                    
                    if onclick:
                        print(f"🖱️ 尝试点击下载按钮 {i+1}")
                        try:
                            element.click()
                            time.sleep(3)
                            # 检查是否有新的下载开始
                            if self.check_download_started():
                                return True
                        except Exception as e:
                            print(f"⚠️ 点击失败: {e}")
                            
            except Exception as e:
                print(f"⚠️ 查找选择器 {selector} 失败: {e}")
        
        # 方法3: 监听网络请求
        print("🌐 尝试从网络请求中获取视频URL...")
        return self.extract_video_from_network()
    
    def download_video_from_url(self, url, filename):
        """从URL下载视频"""
        try:
            print(f"📥 正在下载: {url}")
            
            # 获取当前页面的cookies
            cookies = self.driver.get_cookies()
            session = requests.Session()
            
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            # 设置请求头
            headers = {
                'User-Agent': self.driver.execute_script("return navigator.userAgent;"),
                'Referer': self.driver.current_url
            }
            
            response = session.get(url, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'video/' in content_type or 'application/octet-stream' in content_type:
                    file_path = self.download_dir / filename
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    file_size = os.path.getsize(file_path)
                    print(f"✅ 下载完成: {file_path} ({file_size} bytes)")
                    return True
                else:
                    print(f"⚠️ 不是视频文件: {content_type}")
            else:
                print(f"❌ 下载失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 下载异常: {e}")
        
        return False
    
    def check_download_started(self):
        """检查是否有下载开始"""
        # 检查下载目录是否有新文件
        initial_files = set(self.download_dir.glob("*"))
        time.sleep(5)
        current_files = set(self.download_dir.glob("*"))
        
        new_files = current_files - initial_files
        if new_files:
            print(f"✅ 检测到新下载文件: {list(new_files)}")
            return True
        
        return False
    
    def extract_video_from_network(self):
        """从浏览器网络请求中提取视频URL"""
        try:
            # 获取浏览器日志（需要启用日志记录）
            logs = self.driver.get_log('performance')
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    url = response['url']
                    content_type = response.get('mimeType', '')
                    
                    if 'video/' in content_type or url.endswith('.mp4'):
                        print(f"🎬 从网络日志发现视频: {url}")
                        if self.download_video_from_url(url, "network_video.mp4"):
                            return True
                            
        except Exception as e:
            print(f"⚠️ 网络日志分析失败: {e}")
        
        return False
    
    def take_screenshot(self, filename="metaso_page.png"):
        """截取页面截图"""
        try:
            screenshot_path = self.download_dir / filename
            self.driver.save_screenshot(str(screenshot_path))
            print(f"📸 页面截图已保存: {screenshot_path}")
            return True
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return False
    
    def get_page_info(self):
        """获取页面信息"""
        try:
            print("\n📋 页面信息:")
            print(f"   标题: {self.driver.title}")
            print(f"   URL: {self.driver.current_url}")
            
            # 查找所有可能相关的元素
            video_count = len(self.driver.find_elements(By.TAG_NAME, "video"))
            audio_count = len(self.driver.find_elements(By.TAG_NAME, "audio"))
            iframe_count = len(self.driver.find_elements(By.TAG_NAME, "iframe"))
            
            print(f"   视频元素数量: {video_count}")
            print(f"   音频元素数量: {audio_count}")
            print(f"   iframe数量: {iframe_count}")
            
            # 查找包含特定关键词的元素
            keywords = ["download", "video", "play", "生成", "导出"]
            for keyword in keywords:
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                if elements:
                    print(f"   包含'{keyword}'的元素: {len(elements)}个")
            
        except Exception as e:
            print(f"⚠️ 获取页面信息失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("🔒 浏览器已关闭")

def main():
    # Metaso视频页面URL
    target_url = "https://metaso.cn/search/8651522172447916032"
    
    print("="*80)
    print("🎬 Metaso视频自动化下载器")
    print("="*80)
    
    downloader = MetasoSeleniumDownloader(headless=False)
    
    try:
        # 启动浏览器
        if not downloader.setup_driver():
            return
        
        # 访问页面
        if not downloader.navigate_to_metaso(target_url):
            return
        
        # 获取页面信息
        downloader.get_page_info()
        
        # 截图
        downloader.take_screenshot("initial_page.png")
        
        # 等待视频生成
        if downloader.wait_for_video_generation():
            # 尝试下载视频
            if downloader.find_and_download_video():
                print("\n🎉 视频下载成功！")
            else:
                print("\n❌ 视频下载失败")
                downloader.take_screenshot("final_page.png")
        else:
            print("\n⏰ 视频生成超时或失败")
            downloader.take_screenshot("timeout_page.png")
        
        # 保持浏览器打开一段时间供用户查看
        print("\n⏳ 浏览器将在30秒后关闭，您可以手动查看页面...")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
    finally:
        downloader.close()

if __name__ == "__main__":
    main()