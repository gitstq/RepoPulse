"""
核心数据模型与逻辑模块 - Core data models and logic module.

定义仓库数据模型、仓库管理器等核心组件。
Defines repository data models, repository manager, and core components.
"""

import json
import csv
import io
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .api import GitHubAPI
from .config import Config


@dataclass
class Repository:
    """Git仓库数据模型。

    Git repository data model representing a GitHub repository.
    """

    # 基本信息
    id: int = 0                                    # 仓库ID
    name: str = ""                                  # 仓库名称
    full_name: str = ""                             # 完整名称 (owner/repo)
    description: str = ""                           # 描述
    html_url: str = ""                              # 仓库主页URL
    ssh_url: str = ""                               # SSH克隆URL

    # 所有者信息
    owner_login: str = ""                           # 所有者登录名
    owner_type: str = ""                            # 所有者类型 (User/Organization)

    # 统计信息
    stars: int = 0                                  # Star数量
    forks: int = 0                                  # Fork数量
    watchers: int = 0                               # Watcher数量
    open_issues: int = 0                            # 开放Issue数
    open_pull_requests: int = 0                     # 开放PR数

    # 语言与大小
    language: str = ""                              # 主要语言
    languages: Dict[str, int] = field(default_factory=dict)  # 语言构成
    size: int = 0                                   # 仓库大小(KB)

    # 时间信息
    created_at: str = ""                            # 创建时间
    updated_at: str = ""                            # 更新时间
    pushed_at: str = ""                             # 最后推送时间

    # 状态信息
    is_archived: bool = False                       # 是否已归档
    is_fork: bool = False                           # 是否为Fork
    is_private: bool = False                        # 是否为私有仓库
    has_issues: bool = True                         # 是否启用Issues
    has_wiki: bool = True                           # 是否启用Wiki
    has_readme: bool = False                        # 是否有README
    has_license: bool = False                       # 是否有License

    # 默认分支
    default_branch: str = "main"

    # 主题标签
    topics: List[str] = field(default_factory=list)

    # 计算字段（由健康评分和标签模块填充）
    health_score: float = 0.0                       # 健康评分 (0-100)
    tags: List[str] = field(default_factory=list)   # 智能标签

    @classmethod
    def from_github_api(cls, data: Dict[str, Any]) -> "Repository":
        """从GitHub API响应数据创建Repository实例。

        Create a Repository instance from GitHub API response data.

        Args:
            data: GitHub API返回的仓库JSON数据.
                  Repository JSON data from GitHub API.

        Returns:
            Repository实例. Repository instance.
        """
        owner = data.get("owner", {})
        license_info = data.get("license")

        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description", "") or "",
            html_url=data.get("html_url", ""),
            ssh_url=data.get("ssh_url", ""),
            owner_login=owner.get("login", ""),
            owner_type=owner.get("type", ""),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            watchers=data.get("watchers_count", 0),
            open_issues=data.get("open_issues_count", 0),
            language=data.get("language", "") or "",
            size=data.get("size", 0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            pushed_at=data.get("pushed_at", ""),
            is_archived=data.get("archived", False),
            is_fork=data.get("fork", False),
            is_private=data.get("private", False),
            has_issues=data.get("has_issues", True),
            has_wiki=data.get("has_wiki", True),
            default_branch=data.get("default_branch", "main"),
            topics=data.get("topics", []) or [],
            has_license=license_info is not None,
        )

    @property
    def created_datetime(self) -> Optional[datetime]:
        """解析创建时间为datetime对象。

        Parse created_at to datetime object.
        """
        return self._parse_datetime(self.created_at)

    @property
    def pushed_datetime(self) -> Optional[datetime]:
        """解析最后推送时间为datetime对象。

        Parse pushed_at to datetime object.
        """
        return self._parse_datetime(self.pushed_at)

    @property
    def updated_datetime(self) -> Optional[datetime]:
        """解析更新时间为datetime对象。

        Parse updated_at to datetime object.
        """
        return self._parse_datetime(self.updated_at)

    @property
    def days_since_push(self) -> Optional[int]:
        """计算距离最后推送的天数。

        Calculate days since last push.
        """
        dt = self.pushed_datetime
        if dt is None:
            return None
        now = datetime.now(timezone.utc)
        return (now - dt).days

    @property
    def days_since_creation(self) -> Optional[int]:
        """计算仓库创建以来的天数。

        Calculate days since repository creation.
        """
        dt = self.created_datetime
        if dt is None:
            return None
        now = datetime.now(timezone.utc)
        return (now - dt).days

    @property
    def age_category(self) -> str:
        """根据创建时间返回年龄分类。

        Return age category based on creation time.

        Returns:
            年龄分类: "new"(<6月), "mature"(6月-2年), "old"(>2年)
        """
        days = self.days_since_creation
        if days is None:
            return "unknown"
        if days < 180:
            return "new"
        elif days < 730:
            return "mature"
        else:
            return "old"

    @staticmethod
    def _parse_datetime(dt_str: str) -> Optional[datetime]:
        """解析ISO 8601时间字符串。

        Parse ISO 8601 datetime string.

        Args:
            dt_str: 时间字符串. Datetime string.

        Returns:
            datetime对象，解析失败返回None。
            datetime object, or None if parsing fails.
        """
        if not dt_str:
            return None
        try:
            # GitHub API返回的时间格式: 2024-01-01T00:00:00Z
            return datetime.fromisoformat(
                dt_str.replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（排除不可序列化的字段）。

        Convert to dict, excluding non-serializable fields.
        """
        data = asdict(self)
        return data

    def __repr__(self) -> str:
        return (
            f"Repository(name={self.full_name!r}, "
            f"stars={self.stars}, language={self.language!r})"
        )


class RepositoryManager:
    """仓库管理器。

    Repository manager that orchestrates API calls, health scoring,
    tagging, and other operations on repositories.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        api: Optional[GitHubAPI] = None,
    ) -> None:
        """初始化仓库管理器。

        Args:
            config: 配置管理器实例. Config instance.
            api: GitHub API客户端实例，为None时自动创建。
                 GitHub API client instance, auto-created if None.
        """
        self._config = config or Config()
        self._api = api or GitHubAPI(self._config)
        self._repositories: List[Repository] = []

    @property
    def api(self) -> GitHubAPI:
        """获取API客户端实例。"""
        return self._api

    @property
    def repositories(self) -> List[Repository]:
        """获取已加载的仓库列表。"""
        return self._repositories

    def load_user_repos(
        self,
        username: Optional[str] = None,
        sort: str = "updated",
    ) -> List[Repository]:
        """加载用户/组织的仓库列表。

        Load repositories for a user or organization.

        Args:
            username: GitHub用户名，为None时使用认证用户。
                      GitHub username, uses authenticated user if None.
            sort: 排序字段. Sort field.

        Returns:
            仓库列表. List of Repository objects.
        """
        # 获取所有页的数据
        all_repos = []
        page = 1
        per_page = 100  # 最大每页数量

        while True:
            repos_data = self._api.list_user_repos(
                username=username,
                sort=sort,
                page=page,
                per_page=per_page,
            )
            if not repos_data:
                break
            all_repos.extend(repos_data)
            # 如果返回数量少于请求数量，说明没有更多页
            if len(repos_data) < per_page:
                break
            page += 1

        self._repositories = [
            Repository.from_github_api(rd) for rd in all_repos
        ]
        return self._repositories

    def enrich_repository(self, repo: Repository) -> Repository:
        """丰富单个仓库的详细信息（语言构成、README等）。

        Enrich a single repository with additional details.

        Args:
            repo: 要丰富的仓库对象. Repository to enrich.

        Returns:
            丰富后的仓库对象. Enriched repository.
        """
        owner, name = repo.full_name.split("/", 1)

        # 获取语言构成
        try:
            repo.languages = self._api.get_repo_languages(owner, name)
        except Exception:
            repo.languages = {}

        # 检查README
        try:
            readme = self._api.get_repo_readme(owner, name)
            repo.has_readme = readme is not None
        except Exception:
            repo.has_readme = False

        return repo

    def enrich_all(self) -> List[Repository]:
        """丰富所有已加载仓库的详细信息。

        Enrich all loaded repositories with additional details.

        Returns:
            丰富后的仓库列表. Enriched repository list.
        """
        for repo in self._repositories:
            self.enrich_repository(repo)
        return self._repositories

    def export_json(self, filepath: str) -> None:
        """将仓库列表导出为JSON文件。

        Export repository list to a JSON file.

        Args:
            filepath: 输出文件路径. Output file path.
        """
        data = [repo.to_dict() for repo in self._repositories]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def export_csv(self, filepath: str) -> None:
        """将仓库列表导出为CSV文件。

        Export repository list to a CSV file.

        Args:
            filepath: 输出文件路径. Output file path.
        """
        if not self._repositories:
            return

        # 定义要导出的字段
        fieldnames = [
            "full_name", "description", "language", "stars", "forks",
            "open_issues", "is_archived", "is_fork", "is_private",
            "pushed_at", "created_at", "html_url", "health_score",
            "tags",
        ]

        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for repo in self._repositories:
                row = {k: getattr(repo, k) for k in fieldnames}
                # 将列表转为字符串
                if isinstance(row.get("tags"), list):
                    row["tags"] = ",".join(row["tags"])
                writer.writerow(row)

    def get_stats(self) -> Dict[str, Any]:
        """获取仓库列表的统计摘要。

        Get a statistical summary of loaded repositories.

        Returns:
            统计摘要字典. Statistics summary dict.
        """
        if not self._repositories:
            return {
                "total": 0,
                "total_stars": 0,
                "total_forks": 0,
                "languages": {},
                "archived_count": 0,
                "fork_count": 0,
                "avg_health": 0.0,
            }

        total = len(self._repositories)
        total_stars = sum(r.stars for r in self._repositories)
        total_forks = sum(r.forks for r in self._repositories)

        # 语言统计
        lang_count: Dict[str, int] = {}
        for r in self._repositories:
            if r.language:
                lang_count[r.language] = lang_count.get(r.language, 0) + 1

        # 按数量排序
        languages = dict(
            sorted(lang_count.items(), key=lambda x: x[1], reverse=True)
        )

        archived = sum(1 for r in self._repositories if r.is_archived)
        forks = sum(1 for r in self._repositories if r.is_fork)

        # 平均健康评分
        scored = [r for r in self._repositories if r.health_score > 0]
        avg_health = (
            sum(r.health_score for r in scored) / len(scored)
            if scored
            else 0.0
        )

        return {
            "total": total,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "languages": languages,
            "archived_count": archived,
            "fork_count": forks,
            "avg_health": round(avg_health, 1),
        }

    def __repr__(self) -> str:
        return f"RepositoryManager(repos={len(self._repositories)})"
