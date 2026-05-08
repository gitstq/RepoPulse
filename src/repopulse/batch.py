"""
批量操作模块 - Batch operations module.

支持批量Star/Unstar、批量导出仓库清单等操作。
Supports batch star/unstar, batch export, and other bulk operations.
"""

import json
import csv
import io
import time
from typing import Any, Dict, List, Optional, Set

from .api import GitHubAPI, APIError
from .config import Config
from .core import Repository


class BatchOperator:
    """批量操作器。

    Batch operator for performing bulk operations on repositories
    such as starring/unstarring and exporting.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        api: Optional[GitHubAPI] = None,
    ) -> None:
        """初始化批量操作器。

        Args:
            config: 配置管理器实例. Config instance.
            api: GitHub API客户端实例. GitHub API client instance.
        """
        self._config = config or Config()
        self._api = api or GitHubAPI(self._config)

    def batch_star(
        self,
        repos: List[Repository],
        delay: float = 0.5,
    ) -> Dict[str, Any]:
        """批量Star仓库。

        Batch star repositories.

        Args:
            repos: 要Star的仓库列表. Repositories to star.
            delay: 每次操作之间的延迟（秒），避免触发速率限制。
                   Delay between operations in seconds.

        Returns:
            操作结果字典，包含成功和失败的统计。
            Operation result dict with success/failure stats.
        """
        results = {
            "total": len(repos),
            "success": [],
            "failed": [],
        }

        for repo in repos:
            owner, name = repo.full_name.split("/", 1)
            try:
                success = self._api.star_repo(owner, name)
                if success:
                    results["success"].append(repo.full_name)
                else:
                    results["failed"].append({
                        "repo": repo.full_name,
                        "reason": "API返回失败",
                    })
            except APIError as e:
                results["failed"].append({
                    "repo": repo.full_name,
                    "reason": str(e),
                })
            except Exception as e:
                results["failed"].append({
                    "repo": repo.full_name,
                    "reason": f"未知错误: {e}",
                })

            # 延迟以避免速率限制
            if delay > 0:
                time.sleep(delay)

        return results

    def batch_unstar(
        self,
        repos: List[Repository],
        delay: float = 0.5,
    ) -> Dict[str, Any]:
        """批量取消Star仓库。

        Batch unstar repositories.

        Args:
            repos: 要取消Star的仓库列表. Repositories to unstar.
            delay: 每次操作之间的延迟（秒）.
                   Delay between operations in seconds.

        Returns:
            操作结果字典. Operation result dict.
        """
        results = {
            "total": len(repos),
            "success": [],
            "failed": [],
        }

        for repo in repos:
            owner, name = repo.full_name.split("/", 1)
            try:
                success = self._api.unstar_repo(owner, name)
                if success:
                    results["success"].append(repo.full_name)
                else:
                    results["failed"].append({
                        "repo": repo.full_name,
                        "reason": "API返回失败",
                    })
            except APIError as e:
                results["failed"].append({
                    "repo": repo.full_name,
                    "reason": str(e),
                })
            except Exception as e:
                results["failed"].append({
                    "repo": repo.full_name,
                    "reason": f"未知错误: {e}",
                })

            if delay > 0:
                time.sleep(delay)

        return results

    def batch_export_json(
        self,
        repos: List[Repository],
        filepath: str,
    ) -> str:
        """批量导出仓库清单为JSON文件。

        Batch export repository list to JSON file.

        Args:
            repos: 仓库列表. Repository list.
            filepath: 输出文件路径. Output file path.

        Returns:
            输出文件路径. Output file path.
        """
        data = []
        for repo in repos:
            repo_dict = repo.to_dict()
            data.append(repo_dict)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        return filepath

    def batch_export_csv(
        self,
        repos: List[Repository],
        filepath: str,
    ) -> str:
        """批量导出仓库清单为CSV文件。

        Batch export repository list to CSV file.

        Args:
            repos: 仓库列表. Repository list.
            filepath: 输出文件路径. Output file path.

        Returns:
            输出文件路径. Output file path.
        """
        if not repos:
            return filepath

        fieldnames = [
            "full_name", "name", "description", "language", "stars",
            "forks", "open_issues", "watchers", "size",
            "is_archived", "is_fork", "is_private",
            "has_readme", "has_license", "has_wiki",
            "pushed_at", "created_at", "updated_at",
            "html_url", "ssh_url", "default_branch",
            "health_score", "tags",
        ]

        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for repo in repos:
                row = {}
                for field in fieldnames:
                    value = getattr(repo, field, "")
                    if isinstance(value, list):
                        value = ",".join(str(v) for v in value)
                    row[field] = value
                writer.writerow(row)

        return filepath

    def batch_mark_archived(
        self,
        repos: List[Repository],
    ) -> List[Repository]:
        """批量标记仓库为归档状态（本地标记，不调用API）。

        Batch mark repositories as archived (local marking only, no API call).

        Note: GitHub API的归档操作需要仓库管理员权限且不可逆，
        因此这里仅做本地标记。

        Args:
            repos: 要标记的仓库列表. Repositories to mark.

        Returns:
            标记后的仓库列表. Marked repository list.
        """
        for repo in repos:
            repo.is_archived = True
            if "archived" not in repo.tags:
                repo.tags.append("archived")
        return repos

    def filter_by_names(
        self,
        repos: List[Repository],
        names: List[str],
    ) -> List[Repository]:
        """根据仓库名称筛选仓库。

        Filter repositories by name.

        Args:
            repos: 仓库列表. Repository list.
            names: 仓库名称列表（支持 owner/repo 格式）.
                   Repository name list (supports owner/repo format).

        Returns:
            匹配的仓库列表. Matched repository list.
        """
        name_set = set(names)
        return [r for r in repos if r.full_name in name_set or r.name in name_set]

    def get_star_status(
        self,
        repos: List[Repository],
    ) -> Dict[str, bool]:
        """批量检查仓库的Star状态。

        Batch check star status for repositories.

        Args:
            repos: 仓库列表. Repository list.

        Returns:
            仓库名到Star状态的映射. Repo name to starred status mapping.
        """
        status: Dict[str, bool] = {}
        for repo in repos:
            owner, name = repo.full_name.split("/", 1)
            try:
                status[repo.full_name] = self._api.check_starred(owner, name)
            except APIError:
                status[repo.full_name] = False
        return status
