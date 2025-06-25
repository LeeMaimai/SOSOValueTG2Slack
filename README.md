# 📡 RSS to Slack Bot

自动抓取 SoSoValue 中文频道的 RSS 内容并推送到 Slack 频道，支持定时推送和自动删除功能。

## ✨ 功能特性

- 🔄 **自动抓取**: 从 RSS 源获取最新内容
- 📅 **定时推送**: 每周一到周五早上 10:00 自动推送
- 🗑️ **自动删除**: 消息 48 小时后自动删除
- 🎯 **内容过滤**: 支持关键词过滤
- 🔧 **多环境**: 支持本地运行和 GitHub Actions 部署
- 🧹 **消息清理**: 提供多种删除工具

## 🚀 快速开始

### 方式一：GitHub Actions 部署（推荐）

1. **Fork 或克隆仓库**
   ```bash
   git clone https://github.com/你的用户名/SOSOValueTG2Slack.git
   cd SOSOValueTG2Slack
   ```

2. **设置 GitHub Secrets**
   - 进入仓库 `Settings` → `Secrets and variables` → `Actions`
   - 添加以下 secrets：
     - `SLACK_BOT_TOKEN`: 你的 Slack Bot Token
     - `SLACK_CHANNEL_A`: Slack 频道 A ID
     - `SLACK_CHANNEL_B`: Slack 频道 B ID
     - `CONTENT_FILTER_KEYWORDS`: 过滤关键词（可选）

3. **手动触发测试**
   - 进入 `Actions` 标签页
   - 点击 `Deploy to Server` 工作流
   - 点击 `Run workflow` 测试

### 方式二：本地运行

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   cp config.env.example .env
   # 编辑 .env 文件，填入你的配置
   ```

3. **运行机器人**
   ```bash
   python rss_to_slack.py
   ```

## 🧹 消息删除工具

项目提供了多种删除工具：

### 1. 快速删除所有消息
```bash
python3 quick_delete_all.py
```

### 2. 交互式删除工具
```bash
python3 delete_channel_messages.py
```

### 3. 删除Bot消息
```bash
python3 delete_bot_messages.py
```

### 4. 删除特定频道消息
```bash
python3 delete_c06_channel.py
```

## 📋 配置说明

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `SLACK_BOT_TOKEN` | Slack Bot Token | `xoxb-1234567890-abcdef` |
| `SLACK_CHANNEL_A` | 频道 A ID | `C08V4E78D70` |
| `SLACK_CHANNEL_B` | 频道 B ID | `C090Y9QUQCU` |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `CONTENT_FILTER_KEYWORDS` | 过滤关键词 | `每日加密热点新闻榜单` |

## ⏰ 执行时间

- **GitHub Actions**: 每周一到周五 UTC 02:00 (北京时间 10:00)
- **本地运行**: 每周一到周五 10:00

## 📊 监控和日志

### GitHub Actions
- 在 `Actions` 页面查看运行日志
- 支持手动触发测试
- 失败时自动发送通知

### 本地运行
- 控制台实时输出日志
- 支持详细调试信息

## 🔧 自定义配置

### 修改执行时间
编辑 `.github/workflows/deploy.yml` 中的 cron 表达式：
```yaml
- cron: '0 2 * * 1-5'  # UTC 02:00 = 北京时间 10:00
```

### 修改删除时间
编辑 `rss_to_slack.py` 中的删除时间：
```python
delete_after_seconds = 172800  # 48小时
```

### 修改 RSS 源
编辑 `rss_to_slack.py` 中的 RSS 地址：
```python
self.rss_url = "https://rsshub.app/telegram/channel/SoSoValue_CN"
```

## 🛠️ 故障排除

### 常见问题

1. **GitHub Actions 不执行**
   - 检查 cron 语法
   - 确认仓库是公开的或使用 GitHub Pro

2. **Slack 消息发送失败**
   - 检查 Bot Token 是否正确
   - 确认 Bot 已添加到目标频道

3. **RSS 获取失败**
   - 检查网络连接
   - 确认 RSS 地址有效

4. **删除消息失败**
   - 检查 Bot 权限
   - 确认消息时间戳正确

### 调试方法

1. 查看 GitHub Actions 日志
2. 手动触发工作流测试
3. 在本地环境测试代码
4. 使用删除工具检查消息状态

## 📁 项目结构

```
SOSOValueTG2Slack/
├── .github/workflows/     # GitHub Actions 配置
├── rss_to_slack.py       # 主程序
├── config.py             # 配置管理
├── requirements.txt      # 依赖列表
├── delete_*.py           # 删除工具
├── test_*.py             # 测试文件
├── DEPLOYMENT.md         # 部署指南
└── README.md            # 项目说明
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如果遇到问题，请：
1. 检查 GitHub Actions 日志
2. 确认所有配置设置正确
3. 在本地环境测试代码
4. 使用删除工具清理消息 