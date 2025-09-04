#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso完整音频下载器
专门用于下载Metaso网站上的完整音频文件（MP3等格式）
而非音频片段
"""

import sys
import os
import re
import json
import time
import sqlite3
import requests
from urllib.parse import urlparse, parse_qs, unquote, urljoin
from bs4 import BeautifulSoup
from pathlib import Path

class CompleteAudioDownloader:
    """完整音频下载器"""
    
    def __init__(self, download_dir="downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://metaso.cn/',
            'Origin': 'https://metaso.cn'
        }
        
        self.session.headers.update(headers)
        
        # 自动获取认证信息
        self.auto_authenticate()
    
    def auto_authenticate(self):
        """自动获取认证信息"""
        print("🔄 正在尝试认证...")
        
        # 方法1: 尝试从环境变量获取认证信息
        if self.try_env_auth():
            return
            
        # 方法2: 尝试从浏览器cookie文件获取
        if self.try_browser_cookies():
            return
            
        # 方法3: 尝试无认证访问
        print("⚠️ 认证方法失败，将尝试无认证访问")
    
    def try_env_auth(self):
        """尝试从环境变量获取认证信息"""
        uid = os.environ.get('METASO_UID')
        sid = os.environ.get('METASO_SID')
        
        if uid and sid:
            print("🔑 从环境变量获取认证信息")
            self.session.cookies.set('uid', uid)
            self.session.cookies.set('sid', sid)
            
            if self.test_authentication():
                print("✅ 环境变量认证成功")
                return True
            else:
                print("❌ 环境变量认证失败")
        else:
            print("💡 提示: 可以设置环境变量 METASO_UID 和 METASO_SID 来启用认证")
            print("   例如: set METASO_UID=your_uid && set METASO_SID=your_sid")
        
        return False
    
    def try_browser_cookies(self):
        """尝试从浏览器cookie文件获取认证信息"""
        try:
            # Chrome cookies路径
            chrome_path = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cookies"
            
            if chrome_path.exists():
                print("🍪 尝试从Chrome获取cookies")
                # 注意：实际实现需要处理Chrome的加密cookies
                # 这里只是一个框架，实际使用时需要更复杂的解密逻辑
                return False
            
        except Exception as e:
            print(f"⚠️ 读取浏览器cookies失败: {e}")
        
        return False
    

    
    def test_authentication(self):
        """测试认证状态"""
        try:
            # 测试用户信息接口
            response = self.session.get('https://metaso.cn/api/user/info', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('errCode') == 0:
                    user_info = data.get('data', {})
                    print(f"✅ 认证成功，用户: {user_info.get('nickname', '未知')}")
                    return True
                else:
                    print(f"❌ 认证失败: {data.get('errMsg', '未知错误')}")
            else:
                print(f"❌ 认证请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试认证时出错: {e}")
        
        return False
    
    def parse_url_info(self, url):
        """解析URL中的文件信息"""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # 从查询参数中获取信息（适用于bookshelf格式的URL）
        file_id = query_params.get('_id', [''])[0]
        
        # 如果查询参数中没有文件ID，尝试从路径中提取（适用于UUID格式的URL）
        if not file_id:
            path_parts = parsed_url.path.strip('/').split('/')
            if path_parts and len(path_parts[-1]) > 10:  # 假设文件ID长度大于10
                file_id = path_parts[-1]
        
        info = {
            'file_id': file_id,
            'chapter_id': query_params.get('chapterId', [''])[0],
            'total_pages': query_params.get('totalPage', [''])[0],
            'file_type': query_params.get('type', [''])[0],
            'title': unquote(query_params.get('title', [''])[0], encoding='utf-8'),
            'scene': unquote(query_params.get('scene', [''])[0], encoding='utf-8'),
            'voice_language': query_params.get('voiceLanguage', [''])[0],
            'voice_speed': query_params.get('voiceSpeed', [''])[0],
            'tts_timbre': query_params.get('ttsTimbre', [''])[0],
            'show_captions': query_params.get('showCaptions', [''])[0]
        }
        
        return info
    
    def try_audio_api_endpoints(self, file_info):
        """尝试各种可能的音频API端点"""
        file_id = file_info['file_id']
        chapter_id = file_info['chapter_id']
        
        # 专门针对音频的API端点
        audio_endpoints = [
            # 完整音频导出端点
            f"/api/file/{file_id}/audio/export",
            f"/api/file/{file_id}/export/audio",
            f"/api/chapter/{chapter_id}/audio/export",
            f"/api/chapter/{chapter_id}/export/audio",
            
            # 音频生成端点
            f"/api/file/{file_id}/generate/audio",
            f"/api/file/{file_id}/audio/generate",
            f"/api/chapter/{chapter_id}/generate/audio",
            f"/api/chapter/{chapter_id}/audio/generate",
            
            # 音频下载端点
            f"/api/file/{file_id}/audio/download",
            f"/api/file/{file_id}/download/audio",
            f"/api/chapter/{chapter_id}/audio/download",
            f"/api/chapter/{chapter_id}/download/audio",
            
            # 音频流端点
            f"/api/file/{file_id}/audio/stream",
            f"/api/file/{file_id}/stream/audio",
            f"/api/chapter/{chapter_id}/audio/stream",
            f"/api/chapter/{chapter_id}/stream/audio",
            
            # 音频URL获取端点
            f"/api/file/{file_id}/audio/url",
            f"/api/file/{file_id}/url/audio",
            f"/api/chapter/{chapter_id}/audio/url",
            f"/api/chapter/{chapter_id}/url/audio",
            
            # PPT音频端点
            f"/api/ppt/{file_id}/audio",
            f"/api/ppt/{file_id}/audio/export",
            f"/api/ppt/{file_id}/audio/download",
            f"/api/ppt/{file_id}/audio/url",
            
            # 课件音频端点
            f"/api/courseware/{file_id}/audio",
            f"/api/courseware/{file_id}/audio/export",
            f"/api/courseware/{file_id}/audio/download",
            
            # TTS相关端点
            f"/api/tts/{file_id}/export",
            f"/api/tts/{file_id}/download",
            f"/api/tts/{chapter_id}/export",
            f"/api/tts/{chapter_id}/download",
            
            # 媒体端点
            f"/api/media/{file_id}/audio",
            f"/api/media/{chapter_id}/audio",
            
            # 通用导出端点（可能包含音频）
            f"/api/file/{file_id}/export",
            f"/api/chapter/{chapter_id}/export",
        ]
        
        successful_endpoints = []
        
        for endpoint in audio_endpoints:
            full_url = f"https://metaso.cn{endpoint}"
            try:
                print(f"🔍 尝试音频API端点: {endpoint}")
                response = self.session.get(full_url, timeout=15)
                
                print(f"   状态码: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    # 检查是否是音频文件
                    if content_type.startswith('audio/'):
                        print(f"✅ 找到音频文件: {endpoint}")
                        successful_endpoints.append({
                            'url': full_url,
                            'content_type': content_type,
                            'size': response.headers.get('content-length', 'unknown'),
                            'type': 'direct_audio'
                        })
                    
                    # 检查是否是JSON响应
                    elif content_type.startswith('application/json') or 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                            
                            # 查找JSON中的音频URL
                            audio_url = self.extract_audio_url_from_json(data)
                            if audio_url:
                                print(f"✅ 在JSON中找到音频URL: {audio_url}")
                                successful_endpoints.append({
                                    'url': audio_url,
                                    'source': 'json_response',
                                    'api_endpoint': full_url,
                                    'type': 'json_audio_url'
                                })
                        except Exception as e:
                            print(f"   JSON解析错误: {e}")
                    
                    # 检查响应内容长度（可能是音频文件）
                    elif len(response.content) > 10000:  # 音频文件通常较大
                        print(f"⚠️ 大文件响应，可能是音频: {len(response.content)} bytes")
                        successful_endpoints.append({
                            'url': full_url,
                            'content_type': content_type,
                            'size': len(response.content),
                            'type': 'potential_audio'
                        })
                
                elif response.status_code == 401:
                    print(f"   需要认证")
                elif response.status_code == 403:
                    print(f"   权限不足")
                elif response.status_code == 404:
                    print(f"   端点不存在")
                else:
                    print(f"   其他错误: {response.status_code}")
                    
            except Exception as e:
                print(f"   请求失败: {e}")
            
            time.sleep(0.3)  # 避免请求过于频繁
        
        return successful_endpoints
    
    def extract_audio_url_from_json(self, data):
        """从JSON数据中提取音频URL"""
        if isinstance(data, dict):
            for key, value in data.items():
                # 查找音频相关的URL字段
                if key.lower() in ['audio_url', 'audiourl', 'audio', 'mp3_url', 'mp3url', 'sound_url', 'soundurl', 'voice_url', 'voiceurl', 'tts_url', 'ttsurl']:
                    if isinstance(value, str) and (value.startswith('http') or value.startswith('/')):
                        return value
                # 也检查通用的URL字段，但优先级较低
                elif key.lower() in ['url', 'download_url', 'downloadurl', 'export_url', 'exporturl']:
                    if isinstance(value, str) and (value.startswith('http') or value.startswith('/')):
                        # 检查URL是否包含音频相关关键词
                        if any(keyword in value.lower() for keyword in ['audio', 'mp3', 'wav', 'sound', 'voice', 'tts']):
                            return value
                elif isinstance(value, (dict, list)):
                    result = self.extract_audio_url_from_json(value)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self.extract_audio_url_from_json(item)
                if result:
                    return result
        return None
    
    def download_audio(self, audio_url, filename):
        """下载音频文件"""
        try:
            print(f"📥 开始下载音频: {filename}")
            print(f"   URL: {audio_url}")
            
            response = self.session.get(audio_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")
            
            # 检查文件大小
            total_size = int(response.headers.get('content-length', 0))
            print(f"   文件大小: {total_size} bytes ({total_size / 1024 / 1024:.2f} MB)")
            
            if total_size < 1000:  # 文件太小，可能是错误信息
                content = response.content.decode('utf-8', errors='ignore')
                print(f"   响应内容: {content}")
                return False
            
            # 根据content-type确定文件扩展名
            if 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
                if not filename.endswith('.mp3'):
                    filename = filename.rsplit('.', 1)[0] + '.mp3'
            elif 'audio/wav' in content_type:
                if not filename.endswith('.wav'):
                    filename = filename.rsplit('.', 1)[0] + '.wav'
            elif 'audio/ogg' in content_type:
                if not filename.endswith('.ogg'):
                    filename = filename.rsplit('.', 1)[0] + '.ogg'
            elif 'audio/m4a' in content_type:
                if not filename.endswith('.m4a'):
                    filename = filename.rsplit('.', 1)[0] + '.m4a'
            
            filepath = self.download_dir / filename
            downloaded_size = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r   下载进度: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ 音频下载完成: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return False
    
    def download_from_url(self, url):
        """从Metaso URL下载完整音频"""
        print("=" * 80)
        print("🎵 Metaso完整音频下载器")
        print("=" * 80)
        
        # 解析URL信息
        file_info = self.parse_url_info(url)
        print(f"\n📋 文件信息:")
        for key, value in file_info.items():
            if value:
                print(f"   {key}: {value}")
        
        if not file_info['file_id']:
            print("❌ 无法从URL中提取文件ID")
            return False
        
        # 尝试各种音频API端点
        print(f"\n🚀 尝试音频API端点...")
        successful_endpoints = self.try_audio_api_endpoints(file_info)
        
        if successful_endpoints:
            print(f"\n✅ 找到 {len(successful_endpoints)} 个可用的音频源:")
            for i, endpoint in enumerate(successful_endpoints):
                print(f"   {i+1}. {endpoint['url']}")
                if 'content_type' in endpoint:
                    print(f"      类型: {endpoint['content_type']}")
                if 'size' in endpoint:
                    print(f"      大小: {endpoint['size']}")
                print(f"      来源: {endpoint['type']}")
                
                # 尝试下载第一个找到的音频
                if i == 0:
                    # 生成文件名
                    title = file_info['title'] if file_info['title'] else f"audio_{file_info['file_id']}"
                    filename = f"{title}.mp3"  # 默认使用mp3扩展名
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    
                    success = self.download_audio(endpoint['url'], filename)
                    if success:
                        return True
        
        print("\n❌ 未找到可下载的完整音频文件")
        print("\n💡 建议:")
        print("   1. 确认音频已经生成完成")
        print("   2. 检查是否需要登录认证")
        print("   3. 尝试手动登录后再运行脚本")
        print("   4. 确认该文件支持音频导出功能")
        
        return False

def main():
    import sys
    
    # 获取目标URL（从命令行参数或使用默认值）
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://metaso.cn/b63854f1-ea44-4176-8d30-df7412d7d852"
    
    print("="*80)
    print("🎵 Metaso完整音频下载器 (自动认证)")
    print("="*80)
    print("🔄 正在自动获取认证信息...")
    
    # 使用自动认证机制
    downloader = CompleteAudioDownloader()
    downloader.download_from_url(target_url)

if __name__ == "__main__":
    main()