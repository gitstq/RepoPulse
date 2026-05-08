# RepoPulse

轻量级Git仓库智能管理TUI引擎。

## 安装

```bash
pip install -e .
```

## 使用

```bash
repopulse dashboard    # 启动交互式TUI仪表盘
repopulse list         # 列出仓库
repopulse health       # 查看仓库健康评分
repopulse search       # 搜索与过滤仓库
repopulse tags         # 查看智能标签
repopulse batch        # 批量操作
repopulse deps         # 依赖安全检查
```

## 配置

创建配置文件 `~/.repopulse/config.json`：

```json
{
    "github_token": "your_github_token",
    "default_user": "your_username",
    "cache_ttl": 300
}
```

## License

MIT
