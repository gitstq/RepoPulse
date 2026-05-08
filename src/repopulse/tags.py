"""
智能标签管理模块 - Smart tag management module.

根据仓库特征自动分类标签，支持自定义规则。
Automatically classifies repositories with tags based on their characteristics.
"""

from typing import Any, Dict, List, Optional, Set

from .config import Config
from .core import Repository


# 所有可用标签及其描述
TAG_DEFINITIONS: Dict[str, str] = {
    "active": "活跃 - 近期有频繁更新",
    "stale": "停滞 - 较长时间未更新",
    "archived": "归档 - 已归档或超长期未更新",
    "rising_star": "新星 - 创建时间短但增长迅速",
    "high_impact": "高影响力 - 高Star数",
    "needs_attention": "待关注 - 需要维护关注",
    "well_documented": "文档完善 - README、Wiki、描述齐全",
    "popular": "热门 - Fork和Star数量多",
    "personal": "个人项目 - 无Fork、低Star",
    "mature": "成熟 - 创建超过2年且持续维护",
}


class TagEngine:
    """智能标签引擎。

    Smart tag engine that automatically assigns tags to repositories
    based on configurable rules and thresholds.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """初始化标签引擎。

        Args:
            config: 配置管理器实例. Config instance.
        """
        self._config = config or Config()
        rules = self._config.tag_rules
        self._active_days = rules.get("active_days", 30)
        self._stale_days = rules.get("stale_days", 180)
        self._archived_days = rules.get("archived_days", 365)
        self._rising_star_stars = rules.get("rising_star_stars", 50)
        self._high_impact_stars = rules.get("high_impact_stars", 500)
        self._watch_threshold = rules.get("watch_threshold", 10)

    def tag(self, repo: Repository) -> List[str]:
        """为单个仓库生成标签。

        Generate tags for a single repository.

        Args:
            repo: 仓库对象. Repository object.

        Returns:
            标签列表. List of tag strings.
        """
        tags: Set[str] = set()

        # 1. 归档标签（最高优先级）
        if repo.is_archived:
            tags.add("archived")
            return sorted(tags)

        days_since_push = repo.days_since_push
        days_since_creation = repo.days_since_creation

        # 2. 活跃度标签
        if days_since_push is not None:
            if days_since_push <= self._active_days:
                tags.add("active")
            elif days_since_push <= self._stale_days:
                tags.add("stale")
            elif days_since_push > self._archived_days:
                tags.add("archived")

        # 3. 新星标签（创建不足1年且有足够Star）
        if (
            days_since_creation is not None
            and days_since_creation < 365
            and repo.stars >= self._rising_star_stars
        ):
            tags.add("rising_star")

        # 4. 高影响力标签
        if repo.stars >= self._high_impact_stars:
            tags.add("high_impact")

        # 5. 热门标签（Fork和Star都较多）
        if repo.stars >= 100 and repo.forks >= 50:
            tags.add("popular")

        # 6. 待关注标签（有开放Issue但长时间未更新）
        if (
            repo.open_issues > 0
            and days_since_push is not None
            and days_since_push > self._stale_days
        ):
            tags.add("needs_attention")

        # 7. 文档完善标签
        if repo.has_readme and repo.has_wiki and repo.description:
            tags.add("well_documented")

        # 8. 个人项目标签（无Fork、低Star、非组织项目）
        if (
            repo.forks == 0
            and repo.stars < 10
            and repo.owner_type == "User"
            and not repo.is_fork
        ):
            tags.add("personal")

        # 9. 成熟项目标签（创建超过2年且仍活跃）
        if (
            days_since_creation is not None
            and days_since_creation > 730
            and "active" in tags
        ):
            tags.add("mature")

        return sorted(tags)

    def tag_all(self, repos: List[Repository]) -> Dict[str, List[Repository]]:
        """为多个仓库生成标签，并按标签分组。

        Generate tags for multiple repositories and group by tag.

        Args:
            repos: 仓库列表. List of Repository objects.

        Returns:
            标签到仓库列表的映射. Tag to repository list mapping.
        """
        tag_groups: Dict[str, List[Repository]] = {}

        for repo in repos:
            repo_tags = self.tag(repo)
            repo.tags = repo_tags
            for t in repo_tags:
                if t not in tag_groups:
                    tag_groups[t] = []
                tag_groups[t].append(repo)

        return tag_groups

    def get_tag_stats(self, repos: List[Repository]) -> Dict[str, Any]:
        """获取标签统计信息。

        Get tag statistics.

        Args:
            repos: 仓库列表. List of Repository objects.

        Returns:
            标签统计字典. Tag statistics dict.
        """
        # 先为所有仓库打标签
        tag_groups = self.tag_all(repos)

        stats: Dict[str, Any] = {
            "total_repos": len(repos),
            "tagged_repos": sum(1 for r in repos if r.tags),
            "untagged_repos": sum(1 for r in repos if not r.tags),
            "tag_counts": {},
            "tag_details": {},
        }

        # 各标签数量
        for tag, repo_list in tag_groups.items():
            stats["tag_counts"][tag] = len(repo_list)
            stats["tag_details"][tag] = {
                "count": len(repo_list),
                "description": TAG_DEFINITIONS.get(tag, "未知标签"),
                "repos": [r.full_name for r in repo_list[:10]],  # 最多显示10个
            }

        # 按数量排序
        stats["tag_counts"] = dict(
            sorted(
                stats["tag_counts"].items(),
                key=lambda x: x[1],
                reverse=True,
            )
        )

        return stats

    @staticmethod
    def get_tag_description(tag: str) -> str:
        """获取标签描述。

        Get description for a tag.

        Args:
            tag: 标签名称. Tag name.

        Returns:
            标签描述. Tag description.
        """
        return TAG_DEFINITIONS.get(tag, "未知标签")

    @staticmethod
    def list_all_tags() -> Dict[str, str]:
        """列出所有可用标签及其描述。

        List all available tags with descriptions.

        Returns:
            标签到描述的映射. Tag to description mapping.
        """
        return dict(TAG_DEFINITIONS)
