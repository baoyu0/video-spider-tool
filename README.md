# Metaso视频下载工具

一个用于分析和下载Metaso平台视频的Python工具集。

## 快速开始

### 环境要求

- Python 3.7+
- Chrome浏览器（可选，用于Selenium）
- ChromeDriver（可选）

## 项目结构

```
video-spider-tool/
├── metaso_video_downloader.py      # 基础视频下载器
├── authenticated_video_downloader.py # 认证视频下载器（使用Cookie）
├── selenium_video_downloader.py     # Selenium自动化下载器
├── analyze_api_response.py          # API响应分析工具
├── VIDEO_DOWNLOAD_GUIDE.md          # 详细使用指南
├── requirements.txt                 # Python依赖包
├── .gitignore                      # Git忽略文件
└── README.md                       # 项目说明文档
```

## 安装和使用

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd video-spider-tool

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

### 2. 基本使用

#### 方法一：基础下载器
```bash
python metaso_video_downloader.py
```

#### 方法二：认证下载器（推荐）
```bash
python authenticated_video_downloader.py
```

#### 方法三：Selenium自动化下载器
```bash
python selenium_video_downloader.py
```

### 3. 配置说明

使用前需要配置目标文件信息：

```python
# 在脚本中修改以下参数
file_id = "your_file_id"        # 文件ID
chapter_id = "your_chapter_id"  # 章节ID
title = "your_video_title"      # 视频标题
```

## 工具说明

### 1. metaso_video_downloader.py
基础视频下载器，通过分析网页内容和API响应来查找视频下载链接。

### 2. authenticated_video_downloader.py
认证视频下载器，支持使用浏览器Cookie进行身份验证，提高下载成功率。

### 3. selenium_video_downloader.py
Selenium自动化下载器，可以模拟真实浏览器操作，自动处理登录和下载过程。

### 4. analyze_api_response.py
API响应分析工具，用于分析Metaso平台的API响应，查找潜在的视频下载链接。

## 使用指南

详细的使用方法和故障排除请参考：[VIDEO_DOWNLOAD_GUIDE.md](VIDEO_DOWNLOAD_GUIDE.md)

## 注意事项

1. **合规使用**：请遵守网站的使用条款和相关法律法规
2. **请求频率**：建议设置合理的请求间隔，避免对服务器造成压力
3. **数据使用**：下载的内容仅供个人学习使用，请勿用于商业用途
4. **版权声明**：请尊重原作者的版权，合理使用下载的内容
5. **会员权益**：本工具旨在帮助用户下载已有权限的内容，不消耗会员积分

## 故障排除

- 如果遇到403/401错误，请尝试使用认证下载器
- 如果API返回空响应，请检查文件ID和章节ID是否正确
- 如果下载失败，请查看日志文件获取详细错误信息

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

**免责声明**：本工具仅供学习和研究使用，使用者需自行承担使用风险，并遵守相关法律法规。