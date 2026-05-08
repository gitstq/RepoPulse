"""
GitHub API交互模块 - GitHub API interaction module.

封装GitHub REST API v3的调用逻辑，支持Token认证、速率限制处理和缓存机制。
Wraps GitHub REST API v3 calls with token auth, rate limit handling, and caching.
"""

import time
from typing import Any, Dict, List, Optional

import requests

from .config import Config


class APIError(Exception):
    """GitHub API调用异常。GitHub API call exception."""

    def __init__(self, message: str, status_code: int = 0) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RateLimitError(APIError):
    """API速率限制异常。Rate limit exceeded exception."""

    def __init__(self, reset_time: int) -> None:
        self.reset_time = reset_time
        message = f"API速率限制已触发，将在 {reset_time} 秒后重置"
        super().__init__(message, 403)


class GitHubAPI:
    """GitHub REST API v3 客户端。

    GitHub REST API v3 client with authentication, rate limiting,
    and response caching support.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """初始化GitHub API客户端。

        Args:
            config: 配置管理器实例，为None时使用默认配置。
                    Config instance, uses defaults if None.
        """
        self._config = config or Config()
        self._base_url = self._config.api_base_url
        self._session = requests.Session()
        self._cache: Dict[str, Dict[str, Any]] = {}  # 缓存: {key: {data, timestamp}}
        self._cache_ttl = self._config.cache_ttl

        # 设置请求头
        self._session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RepoPulse/0.1.0",
        })

        # 如果有Token则添加认证头
        token = self._config.github_token
        if token:
            self._session.headers["Authorization"] = f"Bearer {token}"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """发送API请求。

        Send an API request with rate limit handling and optional caching.

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE).
            endpoint: API端点路径（不含base_url）.
            params: URL查询参数. Query parameters.
            data: 请求体数据. Request body data.
            use_cache: 是否使用缓存（仅对GET请求有效）.
                       Whether to use cache (GET requests only).

        Returns:
            API响应的JSON数据. Response JSON data.

        Raises:
            APIError: API调用失败时抛出.
            RateLimitError: 速率限制时抛出.
        """
        url = f"{self._base_url}{endpoint}"

        # GET请求使用缓存
        cache_key = ""
        if method.upper() == "GET" and use_cache:
            cache_key = f"{method}:{endpoint}:{str(params)}"
            cached = self._get_cache(cache_key)
            if cached is not None:
                return cached

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=30,
            )
        except requests.exceptions.Timeout:
            raise APIError("请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise APIError("网络连接失败，请检查网络设置")
        except requests.exceptions.RequestException as e:
            raise APIError(f"请求异常: {e}")

        # 处理速率限制
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining", "0")
            if remaining == "0":
                reset_ts = int(response.headers.get("X-RateLimit-Reset", "0"))
                reset_in = max(0, reset_ts - int(time.time()))
                raise RateLimitError(reset_in)

        # 处理其他错误
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", f"HTTP {response.status_code}")
            except (ValueError, KeyError):
                message = f"HTTP {response.status_code}: {response.text[:200]}"
            raise APIError(message, response.status_code)

        # 处理204 No Content
        if response.status_code == 204:
            return {"status": "success"}

        try:
            result = response.json()
        except ValueError:
            result = {"raw": response.text}

        # 写入缓存
        if method.upper() == "GET" and use_cache and cache_key:
            self._set_cache(cache_key, result)

        return result

    def _get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取数据。

        Get data from cache if not expired.

        Args:
            key: 缓存键. Cache key.

        Returns:
            缓存的数据，过期或不存在则返回None。
            Cached data, or None if expired/missing.
        """
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self._cache_ttl:
                return entry["data"]
            # 缓存过期，删除
            del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """写入缓存。

        Write data to cache.

        Args:
            key: 缓存键. Cache key.
            data: 要缓存的数据. Data to cache.
        """
        self._cache[key] = {
            "data": data,
            "timestamp": time.time(),
        }

    def clear_cache(self) -> None:
        """清空所有缓存。Clear all cached data."""
        self._cache.clear()

    # ==================== 仓库相关API ====================

    def list_user_repos(
        self,
        username: Optional[str] = None,
        sort: str = "updated",
        direction: str = "desc",
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户/组织的仓库列表。

        List repositories for a user or organization.

        Args:
            username: GitHub用户名，为None时使用认证用户。
                      GitHub username, uses authenticated user if None.
            sort: 排序字段 (updated, created, pushed, full_name).
            direction: 排序方向 (asc, desc).
            page: 页码. Page number.
            per_page: 每页数量. Items per page.

        Returns:
            仓库信息列表. List of repository info dicts.
        """
        if username:
            endpoint = f"/users/{username}/repos"
        else:
            endpoint = "/user/repos"

        params = {
            "sort": sort,
            "direction": direction,
            "page": page,
            "per_page": per_page or self._config.per_page,
            "type": "all",
        }

        result = self._make_request("GET", endpoint, params=params)
        return result if isinstance(result, list) else [result]

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取单个仓库详情。

        Get details for a single repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.

        Returns:
            仓库详情字典. Repository details dict.
        """
        return self._make_request("GET", f"/repos/{owner}/{repo}")

    def get_repo_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库的Issues列表。

        Get issues for a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.
            state: Issue状态 (open, closed, all).
            page: 页码. Page number.
            per_page: 每页数量. Items per page.

        Returns:
            Issue信息列表. List of issue dicts.
        """
        params = {
            "state": state,
            "page": page,
            "per_page": per_page or self._config.per_page,
        }
        result = self._make_request(
            "GET", f"/repos/{owner}/{repo}/issues", params=params
        )
        return result if isinstance(result, list) else [result]

    def get_repo_pulls(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库的Pull Requests列表。

        Get pull requests for a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.
            state: PR状态 (open, closed, all).
            page: 页码. Page number.
            per_page: 每页数量. Items per page.

        Returns:
            PR信息列表. List of PR dicts.
        """
        params = {
            "state": state,
            "page": page,
            "per_page": per_page or self._config.per_page,
        }
        result = self._make_request(
            "GET", f"/repos/{owner}/{repo}/pulls", params=params
        )
        return result if isinstance(result, list) else [result]

    def get_repo_contributors(
        self,
        owner: str,
        repo: str,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库贡献者列表。

        Get contributors for a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.
            page: 页码. Page number.
            per_page: 每页数量. Items per page.

        Returns:
            贡献者信息列表. List of contributor dicts.
        """
        params = {
            "page": page,
            "per_page": per_page or self._config.per_page,
        }
        result = self._make_request(
            "GET", f"/repos/{owner}/{repo}/contributors", params=params
        )
        return result if isinstance(result, list) else [result]

    def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """获取仓库语言构成。

        Get language breakdown for a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.

        Returns:
            语言到字节数的映射. Language to byte count mapping.
        """
        return self._make_request("GET", f"/repos/{owner}/{repo}/languages")

    def get_repo_readme(
        self, owner: str, repo: str
    ) -> Optional[Dict[str, Any]]:
        """获取仓库README内容。

        Get README content for a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.

        Returns:
            README信息字典（含content字段），不存在则返回None。
            README info dict (with content field), or None if not found.
        """
        try:
            return self._make_request(
                "GET", f"/repos/{owner}/{repo}/readme"
            )
        except APIError:
            return None

    def get_file_content(
        self, owner: str, repo: str, path: str
    ) -> Optional[Dict[str, Any]]:
        """获取仓库中指定文件的内容。

        Get content of a specific file in a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.
            path: 文件路径. File path.

        Returns:
            文件内容信息字典，不存在则返回None。
            File content info dict, or None if not found.
        """
        try:
            return self._make_request(
                "GET", f"/repos/{owner}/{repo}/contents/{path}"
            )
        except APIError:
            return None

    # ==================== Star操作 ====================

    def star_repo(self, owner: str, repo: str) -> bool:
        """给仓库加Star。

        Star a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.

        Returns:
            操作是否成功. Whether the operation succeeded.
        """
        try:
            self._make_request(
                "PUT", f"/user/starred/{owner}/{repo}", use_cache=False
            )
            return True
        except APIError:
            return False

    def unstar_repo(self, owner: str, repo: str) -> bool:
        """取消仓库Star。

        Unstar a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.

        Returns:
            操作是否成功. Whether the operation succeeded.
        """
        try:
            self._make_request(
                "DELETE", f"/user/starred/{owner}/{repo}", use_cache=False
            )
            return True
        except APIError:
            return False

    def check_starred(self, owner: str, repo: str) -> bool:
        """检查当前用户是否已Star该仓库。

        Check if the authenticated user has starred a repository.

        Args:
            owner: 仓库所有者. Repository owner.
            repo: 仓库名称. Repository name.

        Returns:
            是否已Star. Whether starred.
        """
        try:
            self._make_request(
                "GET", f"/user/starred/{owner}/{repo}"
            )
            return True
        except APIError as e:
            if e.status_code == 404:
                return False
            raise

    # ==================== 搜索API ====================

    def search_repos(
        self,
        query: str,
        sort: str = "updated",
        order: str = "desc",
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """搜索仓库。

        Search repositories.

        Args:
            query: 搜索关键词. Search query.
            sort: 排序字段. Sort field.
            order: 排序方向. Sort order.
            page: 页码. Page number.
            per_page: 每页数量. Items per page.

        Returns:
            搜索结果字典（含total_count和items）.
            Search result dict (with total_count and items).
        """
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": per_page or self._config.per_page,
        }
        return self._make_request("GET", "/search/repositories", params=params)

    # ==================== 用户信息 ====================

    def get_authenticated_user(self) -> Dict[str, Any]:
        """获取当前认证用户信息。

        Get the authenticated user's info.

        Returns:
            用户信息字典. User info dict.
        """
        return self._make_request("GET", "/user")

    def get_rate_limit(self) -> Dict[str, Any]:
        """获取API速率限制状态。

        Get API rate limit status.

        Returns:
            速率限制信息字典. Rate limit info dict.
        """
        return self._make_request("GET", "/rate_limit")
