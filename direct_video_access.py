#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接访问视频端点尝试下载
"""

import requests
import json
from urllib.parse import urljoin
import os

class DirectVideoDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://metaso.cn/'
        })
        
        self.file_id = "8651522172447916032"
        self.chapter_id = "8651523279591608320"
        self.base_url = "https://metaso.cn"
        
        # 从之前分析中发现的可能的视频端点
        self.video_endpoints = [
            f"/api/ppt/{self.file_id}/video",
            f"/api/chapter/{self.chapter_id}/video",
            f"/api/export/{self.file_id}/video",
            f"/api/generate/{self.file_id}/video",
            f"/api/file/{self.file_id}/video",
            f"/api/courseware/{self.file_id}/video"
        ]
        
    def try_download_from_endpoint(self, endpoint):
        """尝试从端点下载视频"""
        url = urljoin(self.base_url, endpoint)
        print(f"\n🔍 尝试访问: {endpoint}")
        
        try:
            response = self.session.get(url, timeout=30)
            print(f"   状态码: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                
                # 检查是否是视频文件
                if 'video/' in content_type:
                    print(f"   ✅ 发现视频文件！Content-Type: {content_type}")
                    return self.download_video(response, endpoint)
                
                # 检查是否是JSON响应包含视频链接
                elif 'json' in content_type:
                    try:
                        data = response.json()
                        print(f"   JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
                        
                        # 查找视频链接
                        video_url = self.extract_video_url(data)
                        if video_url:
                            print(f"   🎬 发现视频链接: {video_url}")
                            return self.download_from_url(video_url)
                            
                    except json.JSONDecodeError:
                        print("   ❌ JSON解析失败")
                
                else:
                    print(f"   ⚠️ 未知内容类型: {content_type}")
                    
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
            
        return False
        
    def extract_video_url(self, data):
        """从JSON数据中提取视频URL"""
        # 递归搜索可能的视频URL字段
        def search_video_url(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 检查常见的视频URL字段名
                    if key.lower() in ['url', 'video_url', 'download_url', 'stream_url', 'media_url', 'src', 'href']:
                        if isinstance(value, str) and ('http' in value or value.startswith('/')):
                            print(f"     发现可能的视频URL ({current_path}): {value}")
                            return value
                    
                    # 递归搜索
                    result = search_video_url(value, current_path)
                    if result:
                        return result
                        
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result = search_video_url(item, f"{path}[{i}]")
                    if result:
                        return result
                        
            return None
            
        return search_video_url(data)
        
    def download_from_url(self, video_url):
        """从URL下载视频"""
        if not video_url.startswith('http'):
            video_url = urljoin(self.base_url, video_url)
            
        print(f"   🚀 开始下载: {video_url}")
        
        try:
            response = self.session.get(video_url, stream=True, timeout=30)
            if response.status_code == 200:
                return self.download_video(response, video_url)
            else:
                print(f"   ❌ 下载失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 下载异常: {str(e)}")
            
        return False
        
    def download_video(self, response, source):
        """下载视频文件"""
        try:
            # 创建下载目录
            download_dir = "downloads"
            os.makedirs(download_dir, exist_ok=True)
            
            # 生成文件名
            filename = f"metaso_video_{self.file_id}.mp4"
            filepath = os.path.join(download_dir, filename)
            
            # 下载文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            file_size = os.path.getsize(filepath)
            print(f"   ✅ 下载完成: {filepath} ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"   ❌ 保存文件失败: {str(e)}")
            return False
            
    def run(self):
        """运行下载器"""
        print("="*80)
        print("🎬 直接视频端点访问器")
        print(f"📋 文件ID: {self.file_id}")
        print(f"📋 章节ID: {self.chapter_id}")
        
        success = False
        for endpoint in self.video_endpoints:
            if self.try_download_from_endpoint(endpoint):
                success = True
                break
                
        if not success:
            print("\n❌ 未能从任何端点下载视频")
            print("💡 建议:")
            print("   1. 检查网络连接")
            print("   2. 确认视频已生成完成")
            print("   3. 可能需要登录认证")
        else:
            print("\n✅ 视频下载成功！")
            
if __name__ == "__main__":
    downloader = DirectVideoDownloader()
    downloader.run()