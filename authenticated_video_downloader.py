#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso认证视频下载器
使用浏览器cookies进行认证下载
"""

import requests
import json
import os
from urllib.parse import urljoin

class AuthenticatedVideoDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://metaso.cn/',
            'Origin': 'https://metaso.cn'
        })
        
        # 从URL中提取的参数
        self.file_id = "8651522172447916032"
        self.chapter_id = "8651523279591608320"
        self.base_url = "https://metaso.cn"
        
        # 下载目录
        self.download_dir = "downloads"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
    
    def set_cookies_from_browser(self):
        """设置从浏览器获取的cookies"""
        print("\n🍪 请按以下步骤获取cookies:")
        print("1. 在浏览器中打开 https://metaso.cn 并登录")
        print("2. 打开开发者工具 (F12)")
        print("3. 进入 Network 标签页")
        print("4. 刷新页面或访问视频页面")
        print("5. 找到任意请求，复制 Cookie 头部的值")
        print("6. 将完整的 Cookie 字符串粘贴到下面:")
        
        cookie_string = input("\n请输入Cookie字符串: ").strip()
        
        if cookie_string:
            # 解析cookie字符串
            cookies = {}
            for item in cookie_string.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookies[key] = value
            
            # 设置cookies
            for key, value in cookies.items():
                self.session.cookies.set(key, value)
            
            print(f"✅ 已设置 {len(cookies)} 个cookies")
            return True
        else:
            print("❌ 未输入cookies")
            return False
    
    def test_authentication(self):
        """测试认证状态"""
        print("\n🔐 测试认证状态...")
        
        # 测试下载权限
        download_url = f"/api/file/{self.file_id}/download"
        url = urljoin(self.base_url, download_url)
        
        try:
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if data.get('errCode') == -1 and '权限' in data.get('errMsg', ''):
                print("❌ 认证失败，仍然没有权限")
                return False
            elif data.get('errCode') == 0 or 'url' in data:
                print("✅ 认证成功，有下载权限")
                return True
            else:
                print(f"⚠️ 未知状态: {data}")
                return False
                
        except Exception as e:
            print(f"❌ 测试认证时出错: {str(e)}")
            return False
    
    def try_video_endpoints(self):
        """尝试各种视频端点"""
        print("\n🎬 尝试获取视频下载链接...")
        
        # 可能的视频端点
        video_endpoints = [
            f"/api/ppt/{self.file_id}/video/url",
            f"/api/chapter/{self.chapter_id}/video/url", 
            f"/api/export/{self.file_id}/video",
            f"/api/generate/{self.file_id}/video",
            f"/api/file/{self.file_id}/video/download",
            f"/api/courseware/{self.file_id}/video/export",
            f"/api/file/{self.file_id}/export/video",
            f"/api/chapter/{self.chapter_id}/export/video",
        ]
        
        for endpoint in video_endpoints:
            url = urljoin(self.base_url, endpoint)
            print(f"\n🔍 尝试: {endpoint}")
            
            try:
                response = self.session.get(url, timeout=10)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
                        
                        # 检查是否有视频URL
                        if self.extract_video_url(data, endpoint):
                            return True
                            
                    except json.JSONDecodeError:
                        print(f"   非JSON响应: {response.text[:200]}...")
                        
            except Exception as e:
                print(f"   错误: {str(e)}")
        
        return False
    
    def extract_video_url(self, data, endpoint):
        """从响应数据中提取视频URL"""
        video_url = None
        
        # 检查常见的视频URL字段
        url_fields = ['url', 'videoUrl', 'downloadUrl', 'streamUrl', 'playUrl', 'mediaUrl']
        
        def find_url_in_data(obj, path=""):
            nonlocal video_url
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in [f.lower() for f in url_fields]:
                        if isinstance(value, str) and ('http' in value or value.startswith('/')):
                            print(f"   🎯 发现视频URL字段 {path}.{key}: {value}")
                            video_url = value
                            return True
                    
                    if find_url_in_data(value, f"{path}.{key}" if path else key):
                        return True
                        
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if find_url_in_data(item, f"{path}[{i}]"):
                        return True
                        
            elif isinstance(obj, str):
                # 检查是否是视频文件URL
                if any(ext in obj.lower() for ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']):
                    print(f"   🎬 发现视频文件URL {path}: {obj}")
                    video_url = obj
                    return True
                    
            return False
        
        if find_url_in_data(data):
            return self.download_video(video_url, endpoint)
        
        return False
    
    def download_video(self, video_url, source_endpoint):
        """下载视频文件"""
        print(f"\n📥 开始下载视频: {video_url}")
        
        # 如果是相对URL，转换为绝对URL
        if video_url.startswith('/'):
            video_url = urljoin(self.base_url, video_url)
        
        try:
            # 获取文件信息
            response = self.session.head(video_url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 无法访问视频URL，状态码: {response.status_code}")
                return False
            
            # 获取文件大小
            file_size = int(response.headers.get('Content-Length', 0))
            content_type = response.headers.get('Content-Type', '')
            
            print(f"   文件大小: {file_size / 1024 / 1024:.2f} MB")
            print(f"   内容类型: {content_type}")
            
            # 确定文件名
            filename = f"metaso_video_{self.file_id}.mp4"
            filepath = os.path.join(self.download_dir, filename)
            
            # 下载文件
            print(f"   保存到: {filepath}")
            
            response = self.session.get(video_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 显示进度
                            if file_size > 0:
                                progress = (downloaded / file_size) * 100
                                print(f"\r   下载进度: {progress:.1f}%", end='', flush=True)
                
                print(f"\n✅ 视频下载成功: {filepath}")
                print(f"   来源端点: {source_endpoint}")
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
        print("🎬 Metaso认证视频下载器")
        print(f"📋 文件ID: {self.file_id}")
        print(f"📋 章节ID: {self.chapter_id}")
        
        # 设置cookies
        if not self.set_cookies_from_browser():
            print("❌ 无法继续，需要有效的cookies")
            return False
        
        # 测试认证
        if not self.test_authentication():
            print("❌ 认证失败，请检查cookies是否正确")
            return False
        
        # 尝试下载视频
        if self.try_video_endpoints():
            print("\n🎉 视频下载完成！")
            return True
        else:
            print("\n❌ 未能找到可下载的视频")
            return False

if __name__ == "__main__":
    downloader = AuthenticatedVideoDownloader()
    downloader.run()