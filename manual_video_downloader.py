#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso视频手动下载工具
通过分析浏览器网络请求来下载视频
避免Selenium配置问题
"""

import requests
import json
import os
import time
from urllib.parse import urlparse, parse_qs
import re

class ManualVideoDownloader:
    def __init__(self, uid=None, sid=None):
        self.uid = uid
        self.sid = sid
        self.session = requests.Session()
        
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 如果提供了认证信息，设置Cookie
        if uid and sid:
            self.session.cookies.set('uid', uid)
            self.session.cookies.set('sid', sid)
            print(f"✅ 已设置认证信息: uid={uid[:10]}..., sid={sid[:10]}...")
    
    def analyze_page(self, url):
        """分析页面内容，查找视频相关信息"""
        print(f"\n🔍 分析页面: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            print(f"📋 响应状态: {response.status_code}")
            print(f"📋 响应大小: {len(response.content)} bytes")
            
            # 保存页面内容用于分析
            with open('page_content.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 页面内容已保存到 page_content.html")
            
            # 查找视频相关的URL模式
            video_patterns = [
                r'"(https?://[^"]*\.mp4[^"]*?)"',
                r'"(https?://[^"]*video[^"]*?)"',
                r'"(/api/[^"]*video[^"]*?)"',
                r'videoUrl.*?["\047]([^"\047]*.mp4[^"\047]*)["\047]',
                r'src.*?["\047]([^"\047]*.mp4[^"\047]*)["\047]',
                r'url.*?["\047]([^"\047]*.mp4[^"\047]*)["\047]',
            ]
            
            found_urls = set()
            for pattern in video_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if match.startswith('/'):
                        # 相对URL，转换为绝对URL
                        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                        match = base_url + match
                    found_urls.add(match)
            
            if found_urls:
                print(f"\n🎯 找到 {len(found_urls)} 个可能的视频URL:")
                for i, video_url in enumerate(found_urls, 1):
                    print(f"  {i}. {video_url}")
                return list(found_urls)
            else:
                print("⚠️ 未在页面中找到明显的视频URL")
                return []
                
        except Exception as e:
            print(f"❌ 页面分析失败: {e}")
            return []
    
    def try_download_video(self, video_url, filename=None):
        """尝试下载视频"""
        print(f"\n📥 尝试下载: {video_url}")
        
        if not filename:
            # 从URL生成文件名
            parsed = urlparse(video_url)
            filename = os.path.basename(parsed.path)
            if not filename or not filename.endswith('.mp4'):
                filename = f"video_{int(time.time())}.mp4"
        
        try:
            # 发送HEAD请求检查资源
            head_response = self.session.head(video_url, allow_redirects=True)
            print(f"📋 HEAD响应状态: {head_response.status_code}")
            
            if head_response.status_code == 200:
                content_type = head_response.headers.get('Content-Type', '')
                content_length = head_response.headers.get('Content-Length', '0')
                
                print(f"📋 内容类型: {content_type}")
                print(f"📋 文件大小: {content_length} bytes")
                
                if 'video' in content_type or content_type.startswith('application/octet-stream'):
                    # 看起来是视频文件，尝试下载
                    print("🎬 检测到视频内容，开始下载...")
                    
                    response = self.session.get(video_url, stream=True)
                    response.raise_for_status()
                    
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    file_size = os.path.getsize(filename)
                    print(f"✅ 视频下载成功: {filename} ({file_size} bytes)")
                    return True
                else:
                    print(f"⚠️ 不是视频内容: {content_type}")
            else:
                print(f"❌ 无法访问视频URL: {head_response.status_code}")
                
        except Exception as e:
            print(f"❌ 下载失败: {e}")
        
        return False
    
    def try_api_endpoints(self, file_id):
        """尝试各种API端点"""
        print(f"\n🔧 尝试API端点，文件ID: {file_id}")
        
        api_endpoints = [
            f"https://metaso.cn/api/file/{file_id}/video",
            f"https://metaso.cn/api/file/{file_id}/video/url",
            f"https://metaso.cn/api/ppt/{file_id}/video",
            f"https://metaso.cn/api/ppt/{file_id}/video/url",
            f"https://metaso.cn/api/export/{file_id}/video",
            f"https://metaso.cn/api/generate/{file_id}/video",
            f"https://metaso.cn/api/chapter/{file_id}/video",
            f"https://metaso.cn/api/chapter/{file_id}/video/url",
        ]
        
        for endpoint in api_endpoints:
            print(f"\n🔗 测试: {endpoint}")
            
            try:
                response = self.session.get(endpoint)
                print(f"📋 状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    print(f"📋 内容类型: {content_type}")
                    
                    if 'application/json' in content_type or 'text/json' in content_type:
                        # JSON响应，查看内容
                        try:
                            data = response.json()
                            print(f"📋 完整JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                            
                            # 特殊处理：如果errCode是401但errMsg包含URL，尝试提取
                            if data.get('errCode') == 401 and 'errMsg' in data:
                                err_msg = data['errMsg']
                                if 'http' in err_msg:
                                    print(f"🎯 从错误消息中提取到可能的视频URL: {err_msg}")
                                    if self.try_download_video(err_msg):
                                        return True
                            
                            # 查找JSON中的视频URL
                            video_url = self.extract_video_url_from_json(data)
                            if video_url:
                                print(f"🎯 从JSON中提取到视频URL: {video_url}")
                                if self.try_download_video(video_url):
                                    return True
                        except json.JSONDecodeError:
                            print("⚠️ 无法解析JSON响应")
                            print(f"📋 原始响应内容: {response.text[:500]}...")
                    
                    elif 'video' in content_type:
                        # 直接是视频内容
                        filename = f"video_from_api_{int(time.time())}.mp4"
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        
                        file_size = os.path.getsize(filename)
                        print(f"✅ 直接下载视频成功: {filename} ({file_size} bytes)")
                        return True
                    
                    else:
                        # 其他内容类型，显示部分内容
                        print(f"📋 响应内容预览: {response.text[:200]}...")
                
            except Exception as e:
                print(f"❌ API请求失败: {e}")
        
        return False
    
    def extract_video_url_from_json(self, data):
        """从JSON数据中提取视频URL"""
        if isinstance(data, dict):
            # 查找常见的视频URL字段
            url_fields = ['url', 'videoUrl', 'video_url', 'downloadUrl', 'download_url', 'src', 'href']
            
            for field in url_fields:
                if field in data and data[field]:
                    url = data[field]
                    if isinstance(url, str) and ('http' in url or url.endswith('.mp4')):
                        return url
            
            # 递归查找嵌套对象
            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self.extract_video_url_from_json(value)
                    if result:
                        return result
        
        elif isinstance(data, list):
            for item in data:
                result = self.extract_video_url_from_json(item)
                if result:
                    return result
        
        return None
    
    def download_from_url(self, url):
        """从Metaso URL下载视频"""
        print(f"🚀 开始处理URL: {url}")
        
        # 提取文件ID
        file_id_match = re.search(r'/file/([0-9]+)', url)
        if not file_id_match:
            print("❌ 无法从URL中提取文件ID")
            return False
        
        file_id = file_id_match.group(1)
        print(f"📋 文件ID: {file_id}")
        
        # 1. 分析页面内容
        video_urls = self.analyze_page(url)
        
        # 2. 尝试下载找到的视频URL
        for video_url in video_urls:
            if self.try_download_video(video_url):
                return True
        
        # 3. 尝试API端点
        if self.try_api_endpoints(file_id):
            return True
        
        print("\n❌ 所有下载尝试都失败了")
        return False

def main():
    """主函数"""
    print("🎬 Metaso视频手动下载工具")
    print("=" * 50)
    
    # 从命令行参数获取认证信息
    import sys
    
    uid = None
    sid = None
    target_url = "https://metaso.cn/file/8651522172447916032"
    
    # 解析命令行参数
    for i, arg in enumerate(sys.argv):
        if arg == '--uid' and i + 1 < len(sys.argv):
            uid = sys.argv[i + 1]
        elif arg == '--sid' and i + 1 < len(sys.argv):
            sid = sys.argv[i + 1]
        elif arg == '--url' and i + 1 < len(sys.argv):
            target_url = sys.argv[i + 1]
    
    if not uid or not sid:
        print("⚠️ 未提供认证信息，将尝试无认证访问")
        print("💡 使用方法: python manual_video_downloader.py --uid YOUR_UID --sid YOUR_SID [--url TARGET_URL]")
    
    # 创建下载器
    downloader = ManualVideoDownloader(uid, sid)
    
    # 开始下载
    success = downloader.download_from_url(target_url)
    
    if success:
        print("\n🎉 视频下载成功！")
    else:
        print("\n💡 下载失败，建议:")
        print("1. 确认视频已生成完成")
        print("2. 检查认证信息是否正确")
        print("3. 尝试在浏览器中手动访问并查看网络请求")
        print("4. 使用浏览器开发者工具复制视频请求")
        
        print("\n🔧 手动操作指南:")
        print("1. 在Chrome中打开: https://metaso.cn/file/8651522172447916032")
        print("2. 按F12打开开发者工具")
        print("3. 切换到Network标签")
        print("4. 播放视频，观察网络请求")
        print("5. 找到.mp4文件或video相关请求")
        print("6. 右键点击请求 -> Copy -> Copy as cURL")
        print("7. 使用cURL命令下载视频")

if __name__ == "__main__":
    main()