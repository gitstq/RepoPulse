"""
配置管理模块 - Configuration management module.

管理RepoPulse的全局配置，支持从配置文件和环境变量读取设置。
Manages RepoPulse global configuration, supporting config file and env var settings.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


# 默认配置目录
DEFAULT_CONFIG_DIR = Path.home() / ".repopulse"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"

# 默认配置值
DEFAULT_CONFIG: Dict[str, Any] = {
    "github_token": "",           # GitHub Personal Access Token
    "default_user": "",           # 默认查询的GitHub用户名
    "cache_ttl": 300,             # 缓存有效期（秒）
    "api_base_url": "https://api.github.com",  # GitHub API基础URL
    "per_page": 30,               # 每页返回数量
    "health_weights": {           # 健康评分权重
        "update_activity": 25,    # 更新活跃度
        "community_engagement": 25,  # 社区参与度
        "code_quality": 20,       # 代码质量指标
        "documentation": 15,      # 文档完整度
        "maintenance_response": 15,  # 维护响应度
    },
    "tag_rules": {                # 标签规则阈值
        "active_days": 30,        # 活跃仓库：30天内有更新
        "stale_days": 180,        # 停滞仓库：180天无更新
        "archived_days": 365,     # 归档仓库：365天无更新
        "rising_star_stars": 50,  # 新星仓库：50+ stars且创建不足1年
        "high_impact_stars": 500, # 高影响力：500+ stars
        "watch_threshold": 10,    # 待关注：有issue但长时间无响应
    },
}


class Config:
    """RepoPulse配置管理器。

    Manages all configuration for RepoPulse, loading from file
    with fallback to defaults. Supports environment variable overrides.

    配置优先级：环境变量 > 配置文件 > 默认值
    Priority: environment variables > config file > defaults
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        """初始化配置管理器。

        Args:
            config_path: 自定义配置文件路径，为None时使用默认路径。
                         Custom config file path, uses default if None.
        """
        self._config_path = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """从配置文件加载配置，合并默认值。

        Loads configuration from file and merges with defaults.
        """
        # 从默认配置开始
        self._data = dict(DEFAULT_CONFIG)

        # 如果配置文件存在，读取并合并
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                self._merge(self._data, user_config)
            except (json.JSONDecodeError, OSError) as e:
                # 配置文件损坏时使用默认值，不中断程序
                self._data = dict(DEFAULT_CONFIG)

        # 环境变量覆盖（优先级最高）
        env_token = os.environ.get("GITHUB_TOKEN", "")
        if env_token:
            self._data["github_token"] = env_token

        env_user = os.environ.get("REPOPULSE_DEFAULT_USER", "")
        if env_user:
            self._data["default_user"] = env_user

    @staticmethod
    def _merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """递归合并字典，override中的值覆盖base中的同名键。

        Recursively merge dicts, override values take precedence.

        Args:
            base: 基础字典（会被就地修改）. Base dict (modified in-place).
            override: 覆盖字典. Override dict.
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Config._merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值。

        Get a configuration value by key.

        Args:
            key: 配置键名. Configuration key.
            default: 键不存在时的默认值. Default value if key not found.

        Returns:
            对应的配置值. The configuration value.
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置值（仅内存中生效）。

        Set a configuration value (in-memory only).

        Args:
            key: 配置键名. Configuration key.
            value: 配置值. Configuration value.
        """
        self._data[key] = value

    def save(self) -> None:
        """将当前配置保存到配置文件。

        Save current configuration to file.
        """
        # 确保配置目录存在
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def github_token(self) -> str:
        """获取GitHub Token。"""
        return self._data.get("github_token", "")

    @property
    def default_user(self) -> str:
        """获取默认用户名。"""
        return self._data.get("default_user", "")

    @property
    def cache_ttl(self) -> int:
        """获取缓存有效期（秒）。"""
        return int(self._data.get("cache_ttl", 300))

    @property
    def api_base_url(self) -> str:
        """获取GitHub API基础URL。"""
        return self._data.get("api_base_url", "https://api.github.com")

    @property
    def per_page(self) -> int:
        """获取每页返回数量。"""
        return int(self._data.get("per_page", 30))

    @property
    def health_weights(self) -> Dict[str, int]:
        """获取健康评分权重配置。"""
        return dict(self._data.get("health_weights", DEFAULT_CONFIG["health_weights"]))

    @property
    def tag_rules(self) -> Dict[str, int]:
        """获取标签规则阈值配置。"""
        return dict(self._data.get("tag_rules", DEFAULT_CONFIG["tag_rules"]))

    def __repr__(self) -> str:
        return f"Config(path={self._config_path})"
