"""
搜索与过滤模块 - Search and filter module.

支持按语言、Stars范围、Forks范围、更新时间、关键词等条件过滤仓库。
Supports filtering repositories by language, stars range, forks range,
update time, keywords, and other criteria.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from .api import GitHubAPI, APIError
from .config import Config
from .core import Repository


class SearchFilter:
    """仓库搜索与过滤器。

    Repository search and filter engine supporting multiple criteria.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """初始化搜索过滤器。

        Args:
            config: 配置管理器实例. Config instance.
        """
        self._config = config or Config()
        self._api = GitHubAPI(self._config)

    def filter_repos(
        self,
        repos: List[Repository],
        language: Optional[str] = None,
        min_stars: Optional[int] = None,
        max_stars: Optional[int] = None,
        min_forks: Optional[int] = None,
        max_forks: Optional[int] = None,
        updated_within_days: Optional[int] = None,
        keyword: Optional[str] = None,
        is_archived: Optional[bool] = None,
        is_fork: Optional[bool] = None,
        has_license: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "stars",
        sort_desc: bool = True,
    ) -> List[Repository]:
        """根据条件过滤仓库列表。

        Filter repositories based on multiple criteria.

        Args:
            repos: 仓库列表. Repository list to filter.
            language: 编程语言过滤. Programming language filter.
            min_stars: 最小Stars数. Minimum stars.
            max_stars: 最大Stars数. Maximum stars.
            min_forks: 最小Forks数. Minimum forks.
            max_forks: 最大Forks数. Maximum forks.
            updated_within_days: 在N天内更新过. Updated within N days.
            keyword: 关键词搜索（匹配名称或描述）.
                     Keyword search (matches name or description).
            is_archived: 是否归档. Archived status.
            is_fork: 是否为Fork. Fork status.
            has_license: 是否有License. License status.
            tags: 按标签过滤. Filter by tags.
            sort_by: 排序字段 (stars, forks, updated, name, health).
                     Sort field.
            sort_desc: 是否降序排序. Sort descending.

        Returns:
            过滤后的仓库列表. Filtered repository list.
        """
        result = list(repos)

        # 按语言过滤（不区分大小写）
        if language:
            lang_lower = language.lower()
            result = [
                r for r in result
                if r.language and r.language.lower() == lang_lower
            ]

        # 按Stars范围过滤
        if min_stars is not None:
            result = [r for r in result if r.stars >= min_stars]
        if max_stars is not None:
            result = [r for r in result if r.stars <= max_stars]

        # 按Forks范围过滤
        if min_forks is not None:
            result = [r for r in result if r.forks >= min_forks]
        if max_forks is not None:
            result = [r for r in result if r.forks <= max_forks]

        # 按更新时间过滤
        if updated_within_days is not None:
            cutoff = datetime.now(timezone.utc) - timedelta(
                days=updated_within_days
            )
            filtered = []
            for r in result:
                dt = r.pushed_datetime
                if dt and dt >= cutoff:
                    filtered.append(r)
            result = filtered

        # 按关键词过滤（匹配名称或描述）
        if keyword:
            kw_lower = keyword.lower()
            result = [
                r for r in result
                if kw_lower in r.name.lower()
                or kw_lower in r.description.lower()
                or kw_lower in r.full_name.lower()
            ]

        # 按归档状态过滤
        if is_archived is not None:
            result = [r for r in result if r.is_archived == is_archived]

        # 按Fork状态过滤
        if is_fork is not None:
            result = [r for r in result if r.is_fork == is_fork]

        # 按License状态过滤
        if has_license is not None:
            result = [r for r in result if r.has_license == has_license]

        # 按标签过滤
        if tags:
            tags_set = set(tags)
            result = [
                r for r in result
                if tags_set.issubset(set(r.tags))
            ]

        # 排序
        result = self._sort_repos(result, sort_by, sort_desc)

        return result

    def search_github(
        self,
        query: str,
        language: Optional[str] = None,
        min_stars: Optional[int] = None,
        sort: str = "updated",
        page: int = 1,
    ) -> List[Repository]:
        """通过GitHub API搜索仓库。

        Search repositories via GitHub API.

        Args:
            query: 搜索关键词. Search query.
            language: 限制语言. Language filter.
            min_stars: 最小Stars. Minimum stars.
            sort: 排序字段. Sort field.
            page: 页码. Page number.

        Returns:
            搜索结果仓库列表. List of Repository objects.
        """
        # 构建搜索查询
        search_query = query

        if language:
            search_query += f" language:{language}"
        if min_stars is not None:
            search_query += f" stars:>={min_stars}"

        try:
            result = self._api.search_repos(
                query=search_query,
                sort=sort,
                page=page,
            )
            items = result.get("items", [])
            return [Repository.from_github_api(item) for item in items]
        except APIError as e:
            raise ValueError(f"搜索失败: {e}") from e

    @staticmethod
    def _sort_repos(
        repos: List[Repository],
        sort_by: str,
        sort_desc: bool = True,
    ) -> List[Repository]:
        """对仓库列表排序。

        Sort repository list by specified field.

        Args:
            repos: 仓库列表. Repository list.
            sort_by: 排序字段. Sort field.
            sort_desc: 是否降序. Sort descending.

        Returns:
            排序后的仓库列表. Sorted repository list.
        """
        reverse = sort_desc

        if sort_by == "stars":
            return sorted(repos, key=lambda r: r.stars, reverse=reverse)
        elif sort_by == "forks":
            return sorted(repos, key=lambda r: r.forks, reverse=reverse)
        elif sort_by == "updated":
            return sorted(
                repos,
                key=lambda r: r.pushed_at or "",
                reverse=reverse,
            )
        elif sort_by == "name":
            return sorted(repos, key=lambda r: r.name.lower(), reverse=reverse)
        elif sort_by == "health":
            return sorted(
                repos, key=lambda r: r.health_score, reverse=reverse
            )
        elif sort_by == "issues":
            return sorted(
                repos, key=lambda r: r.open_issues, reverse=reverse
            )
        elif sort_by == "size":
            return sorted(repos, key=lambda r: r.size, reverse=reverse)
        else:
            return repos

    @staticmethod
    def get_unique_languages(repos: List[Repository]) -> List[str]:
        """获取仓库列表中所有唯一语言。

        Get all unique languages from repository list.

        Args:
            repos: 仓库列表. Repository list.

        Returns:
            排序后的唯一语言列表. Sorted unique language list.
        """
        languages = set()
        for r in repos:
            if r.language:
                languages.add(r.language)
        return sorted(languages)
