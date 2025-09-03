#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso Selenium视频下载器
使用Selenium自动化浏览器操作来下载视频
"""

import time
import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SeleniumVideoDownloader:
    def __init__(self):
        self.driver = None
        self.target_url = "https://metaso.cn/bookshelf?displayUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&url=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&page=1&totalPage=44&file_path=&_id=8651522172447916032&title=%E3%80%90%E8%AF%BE%E4%BB%B6%E3%80%91%E7%AC%AC1%E7%AB%A0_%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E6%A6%82%E8%BF%B0.pptx&snippet=undefined&sessionId=null&tag=%E6%9C%AC%E5%9C%B0%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E5%88%B0%E4%B9%A6%E6%9E%B6%E4%B8%93%E7%94%A8%E4%B8%93%E9%A2%98654ce6f986a91de24c79b52f&author=&publishDate=undefined&showFront=false&downloadUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fdownload&previewUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&type=pptx"
        self.file_id = "8651522172447916032"
        self.chapter_id = "8651523279591608320"
        
        # 下载目录
        self.download_dir = "downloads"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
    
    def setup_driver(self):
        """设置Chrome浏览器"""
        print("🚀 启动浏览器...")
        
        chrome_options = Options()
        # 设置下载目录
        prefs = {
            "download.default_directory": os.path.abspath(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 可选：无头模式（后台运行）
        # chrome_options.add_argument("--headless")
        
        # 其他有用的选项
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ 浏览器启动成功")
            return True
        except Exception as e:
            print(f"❌ 浏览器启动失败: {str(e)}")
            print("💡 请确保已安装Chrome浏览器和ChromeDriver")
            return False
    
    def navigate_to_page(self):
        """导航到目标页面"""
        print(f"🌐 访问页面: {self.target_url[:100]}...")
        
        try:
            self.driver.get(self.target_url)
            time.sleep(3)
            
            # 检查页面是否加载成功
            if "metaso.cn" in self.driver.current_url:
                print("✅ 页面加载成功")
                return True
            else:
                print(f"❌ 页面加载失败，当前URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            print(f"❌ 访问页面失败: {str(e)}")
            return False
    
    def wait_for_login(self):
        """等待用户手动登录"""
        print("\n🔐 请在浏览器中手动登录Metaso账户")
        print("登录完成后，请在此处按回车键继续...")
        input()
        
        # 检查是否已登录
        try:
            # 刷新页面以确保登录状态生效
            self.driver.refresh()
            time.sleep(3)
            
            # 简单检查：看看页面是否还在登录页面
            if "login" in self.driver.current_url.lower():
                print("⚠️ 似乎还在登录页面，请确认已成功登录")
                return False
            else:
                print("✅ 登录状态确认")
                return True
                
        except Exception as e:
            print(f"❌ 检查登录状态失败: {str(e)}")
            return False
    
    def find_video_elements(self):
        """查找页面中的视频相关元素"""
        print("\n🔍 查找视频相关元素...")
        
        # 可能的视频相关选择器
        video_selectors = [
            "video",
            "[src*='mp4']",
            "[src*='video']",
            "[href*='video']",
            "[href*='download']",
            "button[class*='download']",
            "a[class*='download']",
            ".download-btn",
            ".video-download",
            "[data-url*='video']",
            "[data-src*='video']"
        ]
        
        found_elements = []
        
        for selector in video_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   找到 {len(elements)} 个元素: {selector}")
                    for i, element in enumerate(elements):
                        try:
                            tag_name = element.tag_name
                            text = element.text[:50] if element.text else ""
                            src = element.get_attribute('src') or ""
                            href = element.get_attribute('href') or ""
                            data_url = element.get_attribute('data-url') or ""
                            
                            element_info = {
                                'selector': selector,
                                'index': i,
                                'tag': tag_name,
                                'text': text,
                                'src': src,
                                'href': href,
                                'data_url': data_url,
                                'element': element
                            }
                            
                            found_elements.append(element_info)
                            print(f"     [{i}] {tag_name}: {text} | src={src[:50]} | href={href[:50]}")
                            
                        except Exception as e:
                            print(f"     错误处理元素 {i}: {str(e)}")
                            
            except Exception as e:
                print(f"   查找选择器 {selector} 时出错: {str(e)}")
        
        return found_elements
    
    def intercept_network_requests(self):
        """拦截网络请求以找到视频API"""
        print("\n🕸️ 监听网络请求...")
        
        # 启用网络日志
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        # 清除现有日志
        self.driver.execute_cdp_cmd('Log.clear', {})
        
        print("   请在浏览器中执行可能触发视频加载的操作（如点击播放、下载按钮等）")
        print("   等待10秒钟收集网络请求...")
        
        time.sleep(10)
        
        # 获取网络日志
        try:
            logs = self.driver.get_log('performance')
            video_requests = []
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    url = message['message']['params']['response']['url']
                    content_type = message['message']['params']['response'].get('headers', {}).get('content-type', '')
                    
                    # 检查是否是视频相关的请求
                    if any(keyword in url.lower() for keyword in ['video', 'stream', 'media', 'download', 'export', 'generate']):
                        video_requests.append({
                            'url': url,
                            'content_type': content_type,
                            'status': message['message']['params']['response']['status']
                        })
                        print(f"   🎬 发现视频请求: {url}")
            
            return video_requests
            
        except Exception as e:
            print(f"❌ 获取网络日志失败: {str(e)}")
            return []
    
    def try_download_with_cookies(self):
        """使用浏览器cookies尝试下载"""
        print("\n🍪 使用浏览器cookies尝试下载...")
        
        # 获取浏览器cookies
        cookies = self.driver.get_cookies()
        
        # 创建requests session并设置cookies
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        # 设置headers
        session.headers.update({
            'User-Agent': self.driver.execute_script("return navigator.userAgent;"),
            'Referer': self.driver.current_url,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        })
        
        # 尝试各种视频API端点
        video_endpoints = [
            f"https://metaso.cn/api/ppt/{self.file_id}/video/url",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/video/url",
            f"https://metaso.cn/api/export/{self.file_id}/video",
            f"https://metaso.cn/api/generate/{self.file_id}/video",
            f"https://metaso.cn/api/file/{self.file_id}/video/download",
            f"https://metaso.cn/api/courseware/{self.file_id}/video/export"
        ]
        
        for endpoint in video_endpoints:
            print(f"\n🔍 尝试: {endpoint}")
            
            try:
                response = session.get(endpoint, timeout=10)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                        
                        # 检查响应中是否有视频URL
                        if self.extract_and_download_video(data, session, endpoint):
                            return True
                            
                    except json.JSONDecodeError:
                        print(f"   非JSON响应: {response.text[:100]}...")
                        
            except Exception as e:
                print(f"   错误: {str(e)}")
        
        return False
    
    def extract_and_download_video(self, data, session, source_endpoint):
        """从响应数据中提取并下载视频"""
        video_url = None
        
        # 查找视频URL
        def find_video_url(obj):
            nonlocal video_url
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in ['url', 'videourl', 'downloadurl', 'streamurl', 'playurl', 'mediaurl']:
                        if isinstance(value, str) and ('http' in value or value.startswith('/')):
                            video_url = value
                            return True
                    if find_video_url(value):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if find_video_url(item):
                        return True
            elif isinstance(obj, str):
                if any(ext in obj.lower() for ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']):
                    video_url = obj
                    return True
            return False
        
        if find_video_url(data) and video_url:
            print(f"   🎯 发现视频URL: {video_url}")
            
            # 如果是相对URL，转换为绝对URL
            if video_url.startswith('/'):
                video_url = f"https://metaso.cn{video_url}"
            
            # 下载视频
            return self.download_video_file(video_url, session, source_endpoint)
        
        return False
    
    def download_video_file(self, video_url, session, source_endpoint):
        """下载视频文件"""
        print(f"\n📥 开始下载视频: {video_url}")
        
        try:
            response = session.get(video_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                filename = f"metaso_video_{self.file_id}.mp4"
                filepath = os.path.join(self.download_dir, filename)
                
                file_size = int(response.headers.get('Content-Length', 0))
                print(f"   文件大小: {file_size / 1024 / 1024:.2f} MB")
                print(f"   保存到: {filepath}")
                
                with open(filepath, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if file_size > 0:
                                progress = (downloaded / file_size) * 100
                                print(f"\r   下载进度: {progress:.1f}%", end='', flush=True)
                
                print(f"\n✅ 视频下载成功: {filepath}")
                print(f"   来源: {source_endpoint}")
                return True
            else:
                print(f"❌ 下载失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 下载视频时出错: {str(e)}")
            return False
    
    def run(self):
        """运行下载器"""
        print("="*80)
        print("🎬 Metaso Selenium视频下载器")
        print(f"📋 文件ID: {self.file_id}")
        print(f"📋 章节ID: {self.chapter_id}")
        
        try:
            # 设置浏览器
            if not self.setup_driver():
                return False
            
            # 访问页面
            if not self.navigate_to_page():
                return False
            
            # 等待用户登录
            if not self.wait_for_login():
                return False
            
            # 查找视频元素
            video_elements = self.find_video_elements()
            
            # 监听网络请求
            network_requests = self.intercept_network_requests()
            
            # 使用cookies尝试下载
            if self.try_download_with_cookies():
                print("\n🎉 视频下载成功！")
                return True
            else:
                print("\n❌ 未能下载视频")
                print("\n💡 建议:")
                print("   1. 确认视频已经生成完成")
                print("   2. 尝试在浏览器中手动点击下载按钮")
                print("   3. 检查网络请求中是否有视频相关的API")
                return False
                
        except Exception as e:
            print(f"❌ 运行过程中出错: {str(e)}")
            return False
            
        finally:
            if self.driver:
                print("\n🔚 关闭浏览器")
                self.driver.quit()

if __name__ == "__main__":
    downloader = SeleniumVideoDownloader()
    downloader.run()