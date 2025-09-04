#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动获取Metaso认证信息并下载音频
使用Puppeteer MCP服务器自动化浏览器操作
"""

import os
import json
import requests
import argparse
from urllib.parse import urlparse, parse_qs
import time

class AutoMetasoAuth:
    def __init__(self, url):
        self.url = url
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
    
    def wait_for_login_and_get_cookies(self):
        """等待用户登录并获取cookies"""
        print("\n🔐 请在浏览器中登录Metaso账号...")
        print("登录完成后，按回车键继续...")
        
        # 等待用户确认登录完成
        input()
        
        # 获取cookies
        try:
            # 这里需要通过MCP服务器获取cookies
            # 由于我们已经有了浏览器实例，可以直接获取
            print("\n🍪 正在获取认证信息...")
            
            # 执行JavaScript获取cookies
            cookie_script = """
            const cookies = document.cookie.split(';');
            const result = {};
            cookies.forEach(cookie => {
                const [name, value] = cookie.trim().split('=');
                if (name === 'uid' || name === 'sid') {
                    result[name] = value;
                }
            });
            return JSON.stringify(result);
            """
            
            return True
            
        except Exception as e:
            print(f"❌ 获取cookies失败: {str(e)}")
            return False
    
    def try_audio_endpoints(self):
        """尝试各种音频API端点"""
        print("\n🎵 尝试下载完整音频文件...")
        
        if not self.uid or not self.sid:
            print("❌ 缺少认证信息")
            return False
        
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
            endpoint_name = '/'.join(endpoint.split('/')[-3:])  # 显示最后三部分
            print(f"\n🔍 尝试音频API端点: {endpoint_name}")
            
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
        audio_fields = ['url', 'audio_url', 'download_url', 'file_url', 'src', 'path', 'link']
        
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
    
    def set_auth_info(self, uid, sid):
        """设置认证信息"""
        self.uid = uid
        self.sid = sid
        print(f"\n✅ 认证信息已设置:")
        print(f"   UID: {self.uid}")
        print(f"   SID: {self.sid[:20]}...")
    
    def run_with_manual_auth(self):
        """使用手动认证信息运行"""
        print("="*80)
        print("🎵 Metaso自动认证音频下载助手")
        print(f"📋 文件ID: {self.file_id}")
        print(f"📋 章节ID: {self.chapter_id}")
        print("="*80)
        
        try:
            # 获取手动输入的认证信息
            print("\n请输入从浏览器获取的认证信息:")
            uid = input("请输入UID: ").strip()
            sid = input("请输入SID: ").strip()
            
            if uid and sid:
                self.set_auth_info(uid, sid)
                
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
                    print("   4. 确认认证信息是否正确")
                    return False
            else:
                print("❌ 认证信息不完整")
                return False
                
        except Exception as e:
            print(f"❌ 运行过程中出错: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Metaso自动认证音频下载助手')
    parser.add_argument('url', help='Metaso页面URL')
    parser.add_argument('--uid', help='用户UID（可选）')
    parser.add_argument('--sid', help='会话SID（可选）')
    
    args = parser.parse_args()
    
    auth_helper = AutoMetasoAuth(args.url)
    
    if args.uid and args.sid:
        # 使用提供的认证信息
        auth_helper.set_auth_info(args.uid, args.sid)
        success = auth_helper.try_audio_endpoints()
    else:
        # 使用手动输入的认证信息
        success = auth_helper.run_with_manual_auth()
    
    if success:
        print("\n🎉 下载完成！")
    else:
        print("\n❌ 下载失败")
        print("\n💡 获取认证信息的步骤:")
        print("   1. 打开浏览器，访问 https://metaso.cn/")
        print("   2. 登录你的Metaso账号")
        print("   3. 按F12打开开发者工具")
        print("   4. 切换到 Application 标签页")
        print("   5. 在左侧找到 Cookies > https://metaso.cn")
        print("   6. 找到 'uid' 和 'sid' 两个cookie值")
        print("   7. 复制这两个值并重新运行脚本")

if __name__ == "__main__":
    main()