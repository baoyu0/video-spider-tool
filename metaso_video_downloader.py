#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso视频下载器
专门用于下载Metaso网站上由PPT转换生成的视频文件
"""

import sys
import os
import re
import json
import time
import requests
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class MetasoVideoDownloader:
    """Metaso视频下载器"""
    
    def __init__(self, download_dir="downloads", uid=None, sid=None):
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
        
        # 如果提供了认证信息，添加Authorization头
        if uid and sid:
            token = f"{uid}-{sid}"
            headers['Authorization'] = f'Bearer {token}'
            print(f"🔐 已设置认证信息: {uid[:10]}...")
        
        self.session.headers.update(headers)
    
    def parse_url_info(self, url):
        """解析URL中的文件信息"""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        info = {
            'file_id': query_params.get('_id', [''])[0],
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
    
    def get_page_content(self, url):
        """获取页面内容"""
        try:
            print(f"📄 正在获取页面内容: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup, response.text
            
        except Exception as e:
            print(f"❌ 获取页面内容失败: {e}")
            return None, None
    
    def find_video_apis(self, page_content):
        """在页面内容中查找视频相关的API端点"""
        video_apis = []
        
        # 查找可能的视频API模式 - 使用简化的正则表达式
        patterns = [
            r'/api/[^/\s]*/video[^\s"]*',  # 视频API
            r'/api/[^/\s]*/stream[^\s"]*',  # 流媒体API
            r'/api/[^/\s]*/media[^\s"]*',   # 媒体API
            r'/api/[^/\s]*/play[^\s"]*',    # 播放API
            r'/api/[^/\s]*/export[^\s"]*',  # 导出API
            r'/api/[^/\s]*/generate[^\s"]*', # 生成API
            r'videoUrl.*?(["\'])([^"\']*)\1',     # videoUrl变量
            r'streamUrl.*?(["\'])([^"\']*)\1',    # streamUrl变量
            r'downloadUrl.*?(["\'])([^"\']*)\1',  # downloadUrl变量
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # 对于带分组的匹配，取最后一个分组
                    match = match[-1]
                
                if match and not match.startswith('http'):
                    # 补全URL
                    full_url = f"https://metaso.cn{match}" if match.startswith('/') else f"https://metaso.cn/{match}"
                    video_apis.append(full_url)
                elif match and match.startswith('http'):
                    video_apis.append(match)
        
        # 去重
        return list(set(video_apis))
    
    def find_video_elements(self, soup):
        """查找页面中的视频元素"""
        video_elements = []
        
        # 查找video标签
        videos = soup.find_all('video')
        for video in videos:
            src = video.get('src')
            if src:
                video_elements.append({
                    'type': 'video_tag',
                    'src': src,
                    'attributes': dict(video.attrs)
                })
            
            # 查找source标签
            sources = video.find_all('source')
            for source in sources:
                src = source.get('src')
                if src:
                    video_elements.append({
                        'type': 'source_tag',
                        'src': src,
                        'attributes': dict(source.attrs)
                    })
        
        # 查找iframe
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src')
            if src and ('video' in src.lower() or 'stream' in src.lower() or 'play' in src.lower()):
                video_elements.append({
                    'type': 'iframe',
                    'src': src,
                    'attributes': dict(iframe.attrs)
                })
        
        return video_elements
    
    def try_video_api_endpoints(self, file_info):
        """尝试各种可能的视频API端点"""
        file_id = file_info['file_id']
        chapter_id = file_info['chapter_id']
        
        # 可能的视频API端点
        api_endpoints = [
            f"/api/file/{file_id}/video",
            f"/api/file/{file_id}/stream",
            f"/api/file/{file_id}/media",
            f"/api/file/{file_id}/play",
            f"/api/file/{file_id}/export/video",
            f"/api/file/{file_id}/generate/video",
            f"/api/chapter/{chapter_id}/video",
            f"/api/chapter/{chapter_id}/stream",
            f"/api/chapter/{chapter_id}/export",
            f"/api/video/{file_id}",
            f"/api/media/{file_id}",
            f"/api/stream/{file_id}",
            f"/api/ppt/{file_id}/video",
            f"/api/courseware/{file_id}/video",
        ]
        
        successful_endpoints = []
        
        for endpoint in api_endpoints:
            full_url = f"https://metaso.cn{endpoint}"
            try:
                print(f"🔍 尝试API端点: {endpoint}")
                response = self.session.get(full_url, timeout=10)
                
                print(f"   状态码: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    # 检查是否是视频文件
                    if content_type.startswith('video/'):
                        print(f"✅ 找到视频文件: {endpoint}")
                        successful_endpoints.append({
                            'url': full_url,
                            'content_type': content_type,
                            'size': response.headers.get('content-length', 'unknown')
                        })
                    
                    # 检查是否是JSON响应
                    elif content_type.startswith('application/json'):
                        try:
                            data = response.json()
                            print(f"   JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                            
                            # 查找JSON中的视频URL
                            video_url = self.extract_video_url_from_json(data)
                            if video_url:
                                print(f"✅ 在JSON中找到视频URL: {video_url}")
                                successful_endpoints.append({
                                    'url': video_url,
                                    'source': 'json_response',
                                    'api_endpoint': full_url
                                })
                        except:
                            pass
                    
                    # 检查响应内容长度
                    elif len(response.content) > 1000:  # 可能是视频文件
                        print(f"⚠️ 大文件响应，可能是视频: {len(response.content)} bytes")
                        successful_endpoints.append({
                            'url': full_url,
                            'content_type': content_type,
                            'size': len(response.content)
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
            
            time.sleep(0.5)  # 避免请求过于频繁
        
        return successful_endpoints
    
    def extract_video_url_from_json(self, data):
        """从JSON数据中提取视频URL"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in ['video_url', 'videourl', 'stream_url', 'streamurl', 'media_url', 'mediaurl', 'download_url', 'downloadurl']:
                    if isinstance(value, str) and (value.startswith('http') or value.startswith('/')):
                        return value
                elif isinstance(value, (dict, list)):
                    result = self.extract_video_url_from_json(value)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self.extract_video_url_from_json(item)
                if result:
                    return result
        return None
    
    def download_video(self, video_url, filename):
        """下载视频文件"""
        try:
            print(f"📥 开始下载视频: {filename}")
            print(f"   URL: {video_url}")
            
            response = self.session.get(video_url, stream=True, timeout=60)
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
            
            print(f"\n✅ 视频下载完成: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return False
    
    def download_from_url(self, url):
        """从Metaso URL下载视频"""
        print("=" * 80)
        print("🎬 Metaso视频下载器")
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
        
        # 获取页面内容
        soup, page_content = self.get_page_content(url)
        if not soup:
            return False
        
        # 查找页面中的视频API
        print(f"\n🔍 查找视频API端点...")
        video_apis = self.find_video_apis(page_content)
        if video_apis:
            print(f"   找到 {len(video_apis)} 个可能的视频API:")
            for api in video_apis:
                print(f"   - {api}")
        
        # 查找视频元素
        print(f"\n🎥 查找视频元素...")
        video_elements = self.find_video_elements(soup)
        if video_elements:
            print(f"   找到 {len(video_elements)} 个视频元素:")
            for element in video_elements:
                print(f"   - {element['type']}: {element['src']}")
        
        # 尝试各种API端点
        print(f"\n🚀 尝试视频API端点...")
        successful_endpoints = self.try_video_api_endpoints(file_info)
        
        if successful_endpoints:
            print(f"\n✅ 找到 {len(successful_endpoints)} 个可用的视频源:")
            for i, endpoint in enumerate(successful_endpoints):
                print(f"   {i+1}. {endpoint['url']}")
                if 'content_type' in endpoint:
                    print(f"      类型: {endpoint['content_type']}")
                if 'size' in endpoint:
                    print(f"      大小: {endpoint['size']}")
                
                # 尝试下载第一个找到的视频
                if i == 0:
                    filename = f"{file_info['title']}.mp4" if file_info['title'] else f"video_{file_info['file_id']}.mp4"
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    
                    success = self.download_video(endpoint['url'], filename)
                    if success:
                        return True
        
        print("\n❌ 未找到可下载的视频文件")
        print("\n💡 建议:")
        print("   1. 确认视频已经生成完成")
        print("   2. 检查是否需要登录认证")
        print("   3. 尝试手动登录后再运行脚本")
        
        return False

def main():
    import sys
    
    # 解析命令行参数
    uid = None
    sid = None
    
    for arg in sys.argv[1:]:
        if arg.startswith('--uid='):
            uid = arg.split('=', 1)[1]
        elif arg.startswith('--sid='):
            sid = arg.split('=', 1)[1]
    
    # 用户提供的URL
    target_url = "https://metaso.cn/bookshelf?displayUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&url=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&page=1&totalPage=44&file_path=&_id=8651522172447916032&title=%E3%80%90%E8%AF%BE%E4%BB%B6%E3%80%91%E7%AC%AC1%E7%AB%A0_%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E6%A6%82%E8%BF%B0.pptx&snippet=undefined&sessionId=null&tag=%E6%9C%AC%E5%9C%B0%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E5%88%B0%E4%B9%A6%E6%9E%B6%E4%B8%93%E7%94%A8%E4%B8%93%E9%A2%98654ce6f986a91de24c79b52f&author=&publishDate=undefined&showFront=false&downloadUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fdownload&previewUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&internalFile=true&topicId=undefined&type=pptx&readMode=false&chapterId=8651523279591608320&level=3&scene=%E9%BB%98%E8%AE%A4&voiceLanguage=cn&pptLanguage=cn&ttsTimbre=uk_woman16&voiceSpeed=100&showCaptions=true"
    
    print("="*80)
    print("🎬 Metaso视频下载器 (带认证支持)")
    print("="*80)
    
    if uid and sid:
        print(f"🔐 使用认证信息: UID={uid[:10]}..., SID={sid[:10]}...")
    else:
        print("⚠️ 未提供认证信息，将尝试无认证下载")
        print("💡 如需认证，请使用: python metaso_video_downloader.py --uid=你的uid --sid=你的sid")
    
    downloader = MetasoVideoDownloader(uid=uid, sid=sid)
    downloader.download_from_url(target_url)

if __name__ == "__main__":
    main()