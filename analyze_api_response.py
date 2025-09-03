#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso API响应分析器
分析各个API端点的响应内容，找出视频下载链接
"""

import requests
import json
import re
from urllib.parse import urljoin, urlparse

class MetasoAPIAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://metaso.cn/'
        })
        
        # 从URL中提取的参数
        self.file_id = "8651522172447916032"
        self.chapter_id = "8651523279591608320"
        self.base_url = "https://metaso.cn"
        
    def analyze_api_endpoint(self, endpoint):
        """分析单个API端点"""
        url = urljoin(self.base_url, endpoint)
        print(f"\n🔍 分析API端点: {endpoint}")
        
        try:
            response = self.session.get(url, timeout=10)
            print(f"   状态码: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            
            if response.status_code == 200:
                try:
                    # 尝试解析JSON
                    data = response.json()
                    print(f"   JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                    
                    # 查找可能的视频链接
                    self.find_video_links(data, endpoint)
                    
                except json.JSONDecodeError:
                    # 如果不是JSON，显示文本内容
                    text = response.text[:500]
                    print(f"   文本响应: {text}...")
                    
            else:
                print(f"   错误: {response.status_code}")
                
        except Exception as e:
            print(f"   异常: {str(e)}")
    
    def find_video_links(self, data, endpoint):
        """在JSON数据中查找视频链接"""
        video_patterns = [
            r'https?://[^\s"]+\.(?:mp4|avi|mov|wmv|flv|webm|m4v)',
            r'[^\s"]*\.(?:mp4|avi|mov|wmv|flv|webm|m4v)',
            r'https?://[^\s"]+/(?:video|stream|media|download)',
        ]
        
        def search_in_value(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 检查关键字段
                    if any(keyword in key.lower() for keyword in ['video', 'stream', 'media', 'download', 'url', 'link', 'path']):
                        print(f"   🎯 关键字段 {current_path}: {value}")
                    
                    search_in_value(value, current_path)
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_in_value(item, f"{path}[{i}]")
                    
            elif isinstance(obj, str):
                # 检查是否包含视频相关的URL
                for pattern in video_patterns:
                    matches = re.findall(pattern, obj, re.IGNORECASE)
                    if matches:
                        print(f"   🎬 发现视频链接 {path}: {matches}")
        
        search_in_value(data)
    
    def run_analysis(self):
        """运行完整分析"""
        print("="*80)
        print("🔍 Metaso API响应分析器")
        print(f"📋 分析文件ID: {self.file_id}")
        print(f"📋 分析章节ID: {self.chapter_id}")
        
        # 要分析的API端点列表
        api_endpoints = [
            f"/api/file/{self.file_id}",
            f"/api/file/{self.file_id}/download",
            f"/api/file/{self.file_id}/video",
            f"/api/file/{self.file_id}/stream",
            f"/api/file/{self.file_id}/media",
            f"/api/file/{self.file_id}/play",
            f"/api/file/{self.file_id}/export",
            f"/api/file/{self.file_id}/export/video",
            f"/api/file/{self.file_id}/generate/video",
            f"/api/chapter/{self.chapter_id}",
            f"/api/chapter/{self.chapter_id}/video",
            f"/api/chapter/{self.chapter_id}/stream",
            f"/api/chapter/{self.chapter_id}/export",
            f"/api/video/{self.file_id}",
            f"/api/media/{self.file_id}",
            f"/api/stream/{self.file_id}",
            f"/api/courseware/{self.file_id}",
            f"/api/courseware/{self.file_id}/video",
            f"/api/courseware/{self.file_id}/export",
            # 新增一些可能的端点
            f"/api/ppt/{self.file_id}/video/url",
            f"/api/file/{self.file_id}/video/url",
            f"/api/chapter/{self.chapter_id}/video/url",
            f"/api/export/{self.file_id}/video",
            f"/api/generate/{self.file_id}/video",
        ]
        
        for endpoint in api_endpoints:
            self.analyze_api_endpoint(endpoint)
        
        print("\n" + "="*80)
        print("✅ 分析完成")

if __name__ == "__main__":
    analyzer = MetasoAPIAnalyzer()
    analyzer.run_analysis()