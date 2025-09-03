# Metaso视频下载指南

本项目提供了多种方法来下载Metaso平台上生成的视频，以绕过会员积分限制。

## 🎯 项目目标

从Metaso平台下载由PPT转换生成的视频，避免消耗会员积分。

## 📁 文件说明

### 核心下载工具

1. **`metaso_video_downloader.py`** - 基础视频下载器
   - 分析页面结构，查找视频API端点
   - 无需认证，但可能受权限限制

2. **`authenticated_video_downloader.py`** - 认证视频下载器
   - 需要手动输入浏览器cookies
   - 适合有登录权限的用户

3. **`selenium_video_downloader.py`** - 自动化浏览器下载器
   - 使用Selenium自动化浏览器操作
   - 可以模拟真实用户行为
   - 需要安装Chrome浏览器和ChromeDriver

### 分析工具

4. **`analyze_api_response.py`** - API响应分析器
   - 分析各个API端点的响应内容
   - 帮助找出视频下载链接

5. **`debug_page_content.py`** - 页面内容调试器
   - 分析页面结构和参数

## 🚀 使用方法

### 方法一：基础下载（推荐先尝试）

```bash
python metaso_video_downloader.py
```

这个方法会：
- 自动分析页面结构
- 尝试各种可能的视频API端点
- 如果没有权限限制，可以直接下载

### 方法二：使用浏览器Cookies认证

```bash
python authenticated_video_downloader.py
```

使用步骤：
1. 在浏览器中登录Metaso账户
2. 打开开发者工具(F12)
3. 进入Network标签页
4. 刷新页面，找到任意请求
5. 复制Cookie头部的完整值
6. 运行脚本时粘贴Cookie字符串

### 方法三：Selenium自动化（最强大）

首先安装依赖：
```bash
pip install selenium
```

确保已安装Chrome浏览器，然后运行：
```bash
python selenium_video_downloader.py
```

使用步骤：
1. 脚本会自动打开Chrome浏览器
2. 浏览器会导航到目标页面
3. 手动在浏览器中登录账户
4. 登录完成后在终端按回车继续
5. 脚本会自动查找视频元素和API
6. 使用浏览器的认证状态下载视频

## 🔧 环境准备

### 1. Python环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. Chrome和ChromeDriver（仅Selenium方法需要）

- 安装Chrome浏览器
- 下载对应版本的ChromeDriver：https://chromedriver.chromium.org/
- 将ChromeDriver添加到系统PATH中

## 📋 目标文件信息

当前配置的目标文件：
- **文件ID**: 8651522172447916032
- **章节ID**: 8651523279591608320
- **文件类型**: PPT转视频
- **标题**: 【课件】第1章_大语言模型概述.pptx

## 🎬 下载结果

成功下载的视频文件将保存在 `downloads/` 目录中，文件名格式：
- `metaso_video_{文件ID}.mp4`

## ⚠️ 注意事项

1. **权限问题**：Metaso平台对视频下载有权限控制，可能需要登录认证

2. **反爬虫措施**：网站可能有反爬虫机制，建议：
   - 适当延迟请求间隔
   - 使用真实的浏览器User-Agent
   - 避免频繁请求

3. **法律合规**：
   - 仅下载自己上传的内容
   - 遵守网站服务条款
   - 不要用于商业用途

4. **技术限制**：
   - 视频必须已经生成完成
   - 需要有效的网络连接
   - 某些API可能需要特定的认证状态

## 🐛 故障排除

### 常见错误及解决方案

1. **权限错误 (`{"errCode":-1,"errMsg":"您没有权限"}`)**
   - 解决：使用方法二或方法三，提供有效的登录认证

2. **服务器错误 (`{"errCode":500,"errMsg":"服务器错误"}`)**
   - 解决：检查文件ID是否正确，视频是否已生成完成

3. **ChromeDriver错误**
   - 解决：确保ChromeDriver版本与Chrome浏览器版本匹配

4. **网络超时**
   - 解决：检查网络连接，增加超时时间

## 📞 技术支持

如果遇到问题：
1. 检查错误日志
2. 确认目标URL和文件ID正确
3. 验证网络连接和认证状态
4. 尝试不同的下载方法

## 🔄 更新日志

- **v1.0**: 基础爬虫框架
- **v1.1**: 添加认证下载支持
- **v1.2**: 集成Selenium自动化
- **v1.3**: 完善API分析和错误处理

---

**免责声明**: 本工具仅供学习和研究使用，请遵守相关法律法规和网站服务条款。