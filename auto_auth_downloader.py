#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso自动认证音频下载器
自动获取uid和sid，然后下载完整音频文件
"""

import time
import os
import json
import requests
import argparse
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

class AutoAuthAudioDownloader:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.uid = None
        self.sid = None
        
        # 解析URL获取文件ID和章节ID
        self.file_id, self.chapter_id = self.parse_url(url)
        
        # 下载目录
        self.download_dir = "downloads"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
    
    def parse_url(self, url):
        """解析URL获取文件ID和章节ID"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            file_id = params.get('_id', [None])[0]
            chapter_id = params.get('chapterId', [None])[0]
            
            print(f"📋 解析URL信息:")
            print(f"   文件ID: {file_id}")
            print(f"   章节ID: {chapter_id}")
            
            return file_id, chapter_id
            
        except Exception as e:
            print(f"❌ 解析URL失败: {str(e)}")
            return None, None
    
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
    
    def navigate_and_login(self):
        """导航到页面并等待登录"""
        print(f"🌐 访问页面: {self.url[:100]}...")
        
        try:
            self.driver.get(self.url)
            time.sleep(3)
            
            # 检查页面是否加载成功
            if "metaso.cn" in self.driver.current_url:
                print("✅ 页面加载成功")
            else:
                print(f"❌ 页面加载失败，当前URL: {self.driver.current_url}")
                return False
            
            # 等待用户手动登录
            print("\n🔐 请在浏览器中手动登录Metaso账户")
            print("登录完成后，请在此处按回车键继续...")
            input()
            
            # 刷新页面以确保登录状态生效
            self.driver.refresh()
            time.sleep(3)
            
            return True
                
        except Exception as e:
            print(f"❌ 访问页面失败: {str(e)}")
            return False
    
    def get_auth_cookies(self):
        """自动获取uid和sid"""
        print("\n🍪 自动获取认证信息...")
        
        try:
            # 获取所有cookies
            cookies = self.driver.get_cookies()
            
            # 查找uid和sid
            for cookie in cookies:
                if cookie['name'] == 'uid':
                    self.uid = cookie['value']
                elif cookie['name'] == 'sid':
                    self.sid = cookie['value']
            
            if self.uid and self.sid:
                print(f"✅ 成功获取认证信息:")
                print(f"   UID: {self.uid}")
                print(f"   SID: {self.sid[:20]}...")
                return True
            else:
                print("❌ 未找到uid或sid cookie")
                print("💡 请确认已成功登录Metaso账户")
                return False
                
        except Exception as e:
            print(f"❌ 获取认证信息失败: {str(e)}")
            return False
    
    def try_audio_endpoints(self):
        """尝试各种音频API端点"""
        print("\n🎵 尝试下载完整音频文件...")
        
        # 创建requests session
        session = requests.Session()
        
        # 设置cookies
        session.cookies.set('uid', self.uid)
        session.cookies.set('sid', self.sid)
        
        # 设置headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': self.url,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        })
        
        # 音频API端点列表
        audio_endpoints = [
            f"https://metaso.cn/api/ppt/{self.file_id}/audio/export",
            f"https://metaso.cn/api/ppt/{self.file_id}/audio/download",
            f"https://metaso.cn/api/ppt/{self.file_id}/audio/url",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/audio/export",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/audio/download",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/audio/url",
            f"https://metaso.cn/api/file/{self.file_id}/audio/export",
            f"https://metaso.cn/api/file/{self.file_id}/audio/download",
            f"https://metaso.cn/api/courseware/{self.file_id}/audio",
            f"https://metaso.cn/api/courseware/{self.file_id}/audio/export",
            f"https://metaso.cn/api/courseware/{self.file_id}/audio/download",
            f"https://metaso.cn/api/tts/{self.file_id}/export",
            f"https://metaso.cn/api/tts/{self.file_id}/download",
            f"https://metaso.cn/api/tts/{self.chapter_id}/export",
            f"https://metaso.cn/api/tts/{self.chapter_id}/download",
            f"https://metaso.cn/api/media/{self.file_id}/audio",
            f"https://metaso.cn/api/media/{self.chapter_id}/audio",
            f"https://metaso.cn/api/file/{self.file_id}/export",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/export"
        ]
        
        for endpoint in audio_endpoints:
            print(f"\n🔍 尝试音频API端点: {endpoint.split('/')[-2:]}")  # 只显示最后两部分
            
            try:
                response = session.get(endpoint, timeout=15)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    print(f"   Content-Type: {content_type}")
                    
                    # 检查是否是音频文件
                    if 'audio' in content_type or 'mp3' in content_type:
                        return self.download_audio_file(response, endpoint)
                    
                    # 检查是否是JSON响应
                    elif 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   JSON响应: {json.dumps(data, ensure_ascii=False)[:100]}...")
                            
                            # 从JSON中提取音频URL
                            audio_url = self.extract_audio_url(data)
                            if audio_url:
                                return self.download_audio_from_url(session, audio_url, endpoint)
                                
                        except json.JSONDecodeError:
                            print("   响应不是有效的JSON")
                
            except Exception as e:
                print(f"   请求失败: {str(e)}")
                continue
        
        return False
    
    def extract_audio_url(self, data):
        """从JSON数据中提取音频URL"""
        # 常见的音频URL字段
        audio_fields = ['url', 'audio_url', 'download_url', 'file_url', 'src', 'path']
        
        def search_dict(obj, fields):
            if isinstance(obj, dict):
                for field in fields:
                    if field in obj and obj[field]:
                        url = obj[field]
                        if isinstance(url, str) and ('.mp3' in url or '.wav' in url or '.m4a' in url or 'audio' in url):
                            return url
                
                # 递归搜索
                for value in obj.values():
                    result = search_dict(value, fields)
                    if result:
                        return result
            
            elif isinstance(obj, list):
                for item in obj:
                    result = search_dict(item, fields)
                    if result:
                        return result
            
            return None
        
        return search_dict(data, audio_fields)
    
    def download_audio_from_url(self, session, audio_url, source_endpoint):
        """从URL下载音频文件"""
        print(f"\n🎵 找到音频URL: {audio_url}")
        
        try:
            # 处理相对URL
            if audio_url.startswith('/'):
                audio_url = f"https://metaso.cn{audio_url}"
            
            response = session.get(audio_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                # 确定文件扩展名
                if '.mp3' in audio_url:
                    ext = '.mp3'
                elif '.wav' in audio_url:
                    ext = '.wav'
                elif '.m4a' in audio_url:
                    ext = '.m4a'
                else:
                    ext = '.mp3'  # 默认
                
                filename = f"metaso_audio_{self.file_id}{ext}"
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
                
                print(f"\n✅ 音频下载成功: {filepath}")
                print(f"   来源: {source_endpoint}")
                return True
            else:
                print(f"❌ 下载失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 下载音频时出错: {str(e)}")
            return False
    
    def download_audio_file(self, response, source_endpoint):
        """直接下载音频文件"""
        print(f"\n🎵 发现音频文件，开始下载...")
        
        try:
            filename = f"metaso_audio_{self.file_id}.mp3"
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
            
            print(f"\n✅ 音频下载成功: {filepath}")
            print(f"   来源: {source_endpoint}")
            return True
            
        except Exception as e:
            print(f"❌ 下载音频时出错: {str(e)}")
            return False
    
    def run(self):
        """运行自动认证下载器"""
        print("="*80)
        print("🎵 Metaso自动认证音频下载器")
        print(f"📋 文件ID: {self.file_id}")
        print(f"📋 章节ID: {self.chapter_id}")
        
        try:
            # 设置浏览器
            if not self.setup_driver():
                return False
            
            # 导航并登录
            if not self.navigate_and_login():
                return False
            
            # 获取认证信息
            if not self.get_auth_cookies():
                return False
            
            # 尝试下载音频
            if self.try_audio_endpoints():
                print("\n🎉 音频下载成功！")
                return True
            else:
                print("\n❌ 未找到可下载的完整音频文件")
                print("\n💡 建议:")
                print("   1. 确认音频已经生成完成")
                print("   2. 检查该文件是否支持音频导出功能")
                print("   3. 尝试在网页中手动生成音频")
                return False
                
        except Exception as e:
            print(f"❌ 运行过程中出错: {str(e)}")
            return False
            
        finally:
            if self.driver:
                print("\n🔚 关闭浏览器")
                self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Metaso自动认证音频下载器')
    parser.add_argument('url', help='Metaso页面URL')
    
    args = parser.parse_args()
    
    downloader = AutoAuthAudioDownloader(args.url)
    success = downloader.run()
    
    if success:
        print("\n🎉 下载完成！")
    else:
        print("\n❌ 下载失败")

if __name__ == "__main__":
    main()