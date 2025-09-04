#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso音频下载器 - 使用获取到的认证信息
"""

import requests
import json
import os
from urllib.parse import urlparse, parse_qs

class AuthenticatedDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://metaso.cn"
        
        # 从Puppeteer获取到的认证信息
        self.cookies = {
            'tid': 'e7042c82-6288-479b-bd76-44e6a09db896',
            '__eventn_id_UMO2dYNwFz': '60460o3q4q',
            'traceid': '7e65828a1df04792',
            'uid': '654ce6f986a91de24c79b52f',
            'sid': 'b2e7ad52e4c74ec08f7e46db002f01b7'
        }
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://metaso.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        # 设置cookies和headers
        self.session.cookies.update(self.cookies)
        self.session.headers.update(self.headers)
    
    def parse_url(self, url):
        """解析URL获取文件ID和章节ID"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            file_id = None
            chapter_id = None
            
            # 从路径中提取文件ID
            if 'ppt' in path_parts:
                ppt_index = path_parts.index('ppt')
                if ppt_index + 1 < len(path_parts):
                    file_id = path_parts[ppt_index + 1]
            
            # 从查询参数中提取章节ID
            query_params = parse_qs(parsed.query)
            if 'chapterId' in query_params:
                chapter_id = query_params['chapterId'][0]
            
            print(f"解析URL结果:")
            print(f"  文件ID: {file_id}")
            print(f"  章节ID: {chapter_id}")
            
            return file_id, chapter_id
        except Exception as e:
            print(f"解析URL失败: {e}")
            return None, None
    
    def try_download_audio(self, file_id, chapter_id):
        """尝试多种API端点下载音频"""
        # 定义多个可能的API端点
        api_endpoints = [
            f"/api/ppt/{file_id}/audio/export",
            f"/api/chapter/{chapter_id}/audio/download",
            f"/api/ppt/{file_id}/chapter/{chapter_id}/audio",
            f"/api/audio/export/{file_id}",
            f"/api/audio/download/{chapter_id}",
            f"/api/ppt/{file_id}/audio",
            f"/api/chapter/{chapter_id}/audio"
        ]
        
        for endpoint in api_endpoints:
            print(f"\n尝试API端点: {endpoint}")
            
            try:
                # 尝试GET请求
                response = self.session.get(f"{self.base_url}{endpoint}")
                print(f"GET响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    print(f"响应类型: {content_type}")
                    
                    # 如果是JSON响应，尝试解析
                    if 'json' in content_type.lower():
                        try:
                            json_data = response.json()
                            print(f"JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                            
                            # 尝试从JSON中提取音频URL
                            audio_url = self.extract_audio_url_from_json(json_data)
                            if audio_url:
                                return self.download_audio_from_url(audio_url, f"audio_{file_id}_{chapter_id}.mp3")
                        except json.JSONDecodeError:
                            print("响应不是有效的JSON")
                            print(f"原始响应内容: {response.text[:500]}")
                    
                    # 如果是音频文件，直接下载
                    elif any(audio_type in content_type for audio_type in ['audio/', 'application/octet-stream']):
                        filename = f"audio_{file_id}_{chapter_id}.mp3"
                        return self.save_audio_file(response.content, filename)
                
                # 尝试POST请求
                post_data = {
                    'fileId': file_id,
                    'chapterId': chapter_id
                }
                
                response = self.session.post(f"{self.base_url}{endpoint}", json=post_data)
                print(f"POST响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    print(f"响应类型: {content_type}")
                    
                    if 'json' in content_type.lower():
                        try:
                            json_data = response.json()
                            print(f"JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                            
                            audio_url = self.extract_audio_url_from_json(json_data)
                            if audio_url:
                                return self.download_audio_from_url(audio_url, f"audio_{file_id}_{chapter_id}.mp3")
                        except json.JSONDecodeError:
                            print("响应不是有效的JSON")
                            print(f"原始响应内容: {response.text[:500]}")
                    
                    elif any(audio_type in content_type for audio_type in ['audio/', 'application/octet-stream']):
                        filename = f"audio_{file_id}_{chapter_id}.mp3"
                        return self.save_audio_file(response.content, filename)
                
            except Exception as e:
                print(f"请求失败: {e}")
                continue
            
            # 如果状态码不是200，显示错误信息
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
        
        print("\n所有API端点都尝试失败")
        return False
    
    def extract_audio_url_from_json(self, json_data):
        """从JSON响应中提取音频URL"""
        # 常见的音频URL字段名
        url_fields = ['url', 'audioUrl', 'downloadUrl', 'fileUrl', 'link', 'src', 'path']
        
        def search_in_dict(data, fields):
            if isinstance(data, dict):
                for field in fields:
                    if field in data and data[field]:
                        url = data[field]
                        if isinstance(url, str) and (url.startswith('http') or url.startswith('/')):
                            return url
                
                # 递归搜索嵌套字典
                for value in data.values():
                    result = search_in_dict(value, fields)
                    if result:
                        return result
            
            elif isinstance(data, list):
                for item in data:
                    result = search_in_dict(item, fields)
                    if result:
                        return result
            
            return None
        
        return search_in_dict(json_data, url_fields)
    
    def download_audio_from_url(self, audio_url, filename):
        """从URL下载音频文件"""
        try:
            print(f"\n从URL下载音频: {audio_url}")
            
            # 如果是相对URL，转换为绝对URL
            if audio_url.startswith('/'):
                audio_url = f"{self.base_url}{audio_url}"
            
            response = self.session.get(audio_url, stream=True)
            
            if response.status_code == 200:
                return self.save_audio_file(response.content, filename)
            else:
                print(f"下载失败，状态码: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"下载音频失败: {e}")
            return False
    
    def save_audio_file(self, content, filename):
        """保存音频文件"""
        try:
            # 确保downloads目录存在
            downloads_dir = "downloads"
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            
            filepath = os.path.join(downloads_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(content)
            
            file_size = len(content)
            print(f"\n✅ 音频文件下载成功!")
            print(f"文件路径: {filepath}")
            print(f"文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
            
            return True
        
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False
    
    def download(self, url):
        """主下载方法"""
        print(f"开始下载音频: {url}")
        print(f"使用认证信息: uid={self.cookies['uid']}, sid={self.cookies['sid']}")
        
        # 解析URL
        file_id, chapter_id = self.parse_url(url)
        
        if not file_id:
            print("❌ 无法从URL中提取文件ID")
            return False
        
        if not chapter_id:
            print("❌ 无法从URL中提取章节ID")
            return False
        
        # 尝试下载音频
        return self.try_download_audio(file_id, chapter_id)

def main():
    url = "https://metaso.cn/share/ppt/654ce6f986a91de24c79b52f?chapterId=654ce6f986a91de24c79b530"
    
    downloader = AuthenticatedDownloader()
    success = downloader.download(url)
    
    if success:
        print("\n🎉 音频下载完成!")
    else:
        print("\n❌ 音频下载失败")
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 确认URL是否正确")
        print("3. 检查认证信息是否有效")
        print("4. 尝试重新登录获取新的认证信息")

if __name__ == "__main__":
    main()