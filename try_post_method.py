#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尝试使用POST方法和不同的认证方式下载视频
"""

import requests
import json
import os
from pathlib import Path

def try_different_auth_methods(url, uid, sid, filename):
    """尝试不同的认证方法"""
    
    # 方法1: Bearer Token (uid-sid)
    print(f"\n🔍 方法1: Bearer Token (uid-sid)")
    session1 = requests.Session()
    token1 = f"{uid}-{sid}"
    headers1 = {
        'Authorization': f'Bearer {token1}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, */*',
        'Content-Type': 'application/json',
        'Referer': 'https://metaso.cn/',
        'Origin': 'https://metaso.cn'
    }
    session1.headers.update(headers1)
    
    # 尝试POST方法
    try:
        response = session1.post(url, timeout=30)
        print(f"   POST状态码: {response.status_code}")
        if response.status_code == 200:
            return handle_response(response, filename, "POST-Bearer")
    except Exception as e:
        print(f"   POST异常: {e}")
    
    # 尝试GET方法
    try:
        response = session1.get(url, timeout=30)
        print(f"   GET状态码: {response.status_code}")
        if response.status_code == 200:
            return handle_response(response, filename, "GET-Bearer")
    except Exception as e:
        print(f"   GET异常: {e}")
    
    # 方法2: 直接在Cookie中设置uid和sid
    print(f"\n🔍 方法2: Cookie认证")
    session2 = requests.Session()
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, */*',
        'Content-Type': 'application/json',
        'Referer': 'https://metaso.cn/',
        'Origin': 'https://metaso.cn',
        'Cookie': f'uid={uid}; sid={sid}'
    }
    session2.headers.update(headers2)
    
    # 尝试POST方法
    try:
        response = session2.post(url, timeout=30)
        print(f"   POST状态码: {response.status_code}")
        if response.status_code == 200:
            return handle_response(response, filename, "POST-Cookie")
    except Exception as e:
        print(f"   POST异常: {e}")
    
    # 尝试GET方法
    try:
        response = session2.get(url, timeout=30)
        print(f"   GET状态码: {response.status_code}")
        if response.status_code == 200:
            return handle_response(response, filename, "GET-Cookie")
    except Exception as e:
        print(f"   GET异常: {e}")
    
    # 方法3: 在请求体中发送认证信息
    print(f"\n🔍 方法3: 请求体认证")
    session3 = requests.Session()
    headers3 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, */*',
        'Content-Type': 'application/json',
        'Referer': 'https://metaso.cn/',
        'Origin': 'https://metaso.cn'
    }
    session3.headers.update(headers3)
    
    # 尝试POST方法，在请求体中包含认证信息
    auth_data = {
        'uid': uid,
        'sid': sid
    }
    
    try:
        response = session3.post(url, json=auth_data, timeout=30)
        print(f"   POST状态码: {response.status_code}")
        if response.status_code == 200:
            return handle_response(response, filename, "POST-Body")
    except Exception as e:
        print(f"   POST异常: {e}")
    
    return False

def handle_response(response, filename, method):
    """处理响应"""
    content_type = response.headers.get('Content-Type', '')
    print(f"   Content-Type: {content_type}")
    
    if 'video/' in content_type or 'application/octet-stream' in content_type:
        print(f"   ✅ 发现视频文件! 方法: {method}")
        
        # 创建下载目录
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)
        
        file_path = download_dir / f"{method}_{filename}"
        
        # 下载文件
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(file_path)
        print(f"   ✅ 下载完成: {file_path} ({file_size} bytes)")
        return True
    
    elif 'json' in content_type:
        try:
            json_data = response.json()
            print(f"   📄 JSON响应: {json_data}")
            
            # 检查是否包含视频URL或其他有用信息
            if 'data' in json_data:
                data = json_data['data']
                if isinstance(data, dict):
                    for key in ['videoUrl', 'url', 'downloadUrl', 'streamUrl']:
                        if key in data:
                            video_url = data[key]
                            print(f"   🎬 发现{key}: {video_url}")
                            # 可以递归尝试下载这个URL
                            return try_download_from_url(video_url, filename)
            
            # 检查错误信息
            if 'errCode' in json_data:
                err_code = json_data['errCode']
                err_msg = json_data.get('errMsg', '')
                print(f"   ❌ 错误码: {err_code}, 错误信息: {err_msg}")
                
                # 如果错误信息包含URL，尝试访问
                if 'http' in err_msg:
                    print(f"   🔗 尝试错误信息中的URL: {err_msg}")
                    return try_download_from_url(err_msg, filename)
        
        except Exception as e:
            print(f"   ❌ JSON解析错误: {e}")
    
    else:
        print(f"   ⚠️ 未知内容类型，保存前1024字节查看")
        content_preview = response.content[:1024]
        print(f"   内容预览: {content_preview}")
    
    return False

def try_download_from_url(url, filename):
    """尝试从URL下载"""
    try:
        response = requests.get(url, timeout=30, stream=True)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'video/' in content_type:
                download_dir = Path("downloads")
                download_dir.mkdir(exist_ok=True)
                file_path = download_dir / filename
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(file_path)
                print(f"   ✅ 从URL下载完成: {file_path} ({file_size} bytes)")
                return True
    except Exception as e:
        print(f"   ❌ URL下载异常: {e}")
    
    return False

def main():
    # 用户认证信息
    uid = "654ce6f986a91de24c79b52f"
    sid = "7db6149bc7944aff8fc5632fb5e91e75"
    
    # 重点测试的API端点
    test_endpoints = [
        "https://metaso.cn/api/ppt/8651522172447916032/video",
        "https://metaso.cn/api/generate/8651522172447916032/video",
        "https://metaso.cn/api/export/8651522172447916032/video"
    ]
    
    print("="*80)
    print("🎬 尝试不同的认证方法和请求方式")
    print(f"🔐 认证信息: UID={uid[:10]}..., SID={sid[:10]}...")
    print("="*80)
    
    for i, endpoint in enumerate(test_endpoints, 1):
        print(f"\n📹 测试端点 {i}/{len(test_endpoints)}: {endpoint}")
        filename = f"metaso_video_method_{i}.mp4"
        
        success = try_different_auth_methods(endpoint, uid, sid, filename)
        if success:
            print(f"\n🎉 视频下载成功！")
            break
    
    else:
        print(f"\n❌ 所有方法都失败了")
        print(f"\n💡 建议:")
        print(f"   1. 检查认证信息是否正确")
        print(f"   2. 确认视频是否已经生成完成")
        print(f"   3. 可能需要在浏览器中手动触发视频生成")
        print(f"   4. API可能需要特殊的参数或头信息")

if __name__ == "__main__":
    main()