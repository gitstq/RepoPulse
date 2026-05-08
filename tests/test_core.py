"""
RepoPulse 核心模块单元测试 - Unit tests for core modules.

覆盖 Repository 数据模型、Config 配置管理、HealthEngine 健康评分、
TagEngine 智能标签、SearchFilter 搜索过滤、DependencyChecker 依赖检查等核心模块。
"""

import json
import os
import tempfile
from datetime import datetime, timezone, timedelta

import pytest

from repopulse.config import Config, DEFAULT_CONFIG
from repopulse.core import Repository, RepositoryManager
from repopulse.health import HealthEngine, HealthReport
from repopulse.tags import TagEngine, TAG_DEFINITIONS
from repopulse.search import SearchFilter
from repopulse.batch import BatchOperator
from repopulse.deps import DependencyChecker


# ==================== 测试数据工厂 ====================


def make_github_api_data(
    name: str = "test-repo",
    owner: str = "testuser",
    stars: int = 100,
    forks: int = 20,
    open_issues: int = 5,
    language: str = "Python",
    pushed_days_ago: int = 10,
    created_days_ago: int = 200,
    description: str = "A test repository",
    archived: bool = False,
    is_fork: bool = False,
    has_license: bool = True,
    topics: list = None,
) -> dict:
    """创建模拟的GitHub API仓库数据。

    Create mock GitHub API repository data.
    """
    now = datetime.now(timezone.utc)
    pushed_at = (now - timedelta(days=pushed_days_ago)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    created_at = (now - timedelta(days=created_days_ago)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    updated_at = (now - timedelta(days=max(0, pushed_days_ago - 1))).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    return {
        "id": 12345,
        "name": name,
        "full_name": f"{owner}/{name}",
        "description": description,
        "html_url": f"https://github.com/{owner}/{name}",
        "ssh_url": f"git@github.com:{owner}/{name}.git",
        "owner": {
            "login": owner,
            "type": "User",
        },
        "stargazers_count": stars,
        "forks_count": forks,
        "watchers_count": stars,
        "open_issues_count": open_issues,
        "language": language,
        "size": 1024,
        "created_at": created_at,
        "updated_at": updated_at,
        "pushed_at": pushed_at,
        "archived": archived,
        "fork": is_fork,
        "private": False,
        "has_issues": True,
        "has_wiki": True,
        "default_branch": "main",
        "topics": topics or [],
        "license": {"key": "mit"} if has_license else None,
    }


def make_repo(**kwargs) -> Repository:
    """创建Repository实例的便捷方法。

    Convenience method to create Repository instances.
    """
    data = make_github_api_data(**kwargs)
    return Repository.from_github_api(data)


# ==================== Repository 数据模型测试 ====================


class TestRepository:
    """Repository数据模型测试。"""

    def test_from_github_api_basic(self):
        """测试从GitHub API数据创建Repository。"""
        data = make_github_api_data()
        repo = Repository.from_github_api(data)

        assert repo.name == "test-repo"
        assert repo.full_name == "testuser/test-repo"
        assert repo.stars == 100
        assert repo.forks == 20
        assert repo.open_issues == 5
        assert repo.language == "Python"
        assert repo.is_archived is False
        assert repo.is_fork is False
        assert repo.has_license is True

    def test_from_github_api_no_description(self):
        """测试无描述的仓库。"""
        data = make_github_api_data(description=None)
        repo = Repository.from_github_api(data)

        assert repo.description == ""

    def test_from_github_api_no_language(self):
        """测试无语言的仓库。"""
        data = make_github_api_data(language=None)
        repo = Repository.from_github_api(data)

        assert repo.language == ""

    def test_from_github_api_no_license(self):
        """测试无License的仓库。"""
        data = make_github_api_data(has_license=False)
        repo = Repository.from_github_api(data)

        assert repo.has_license is False

    def test_from_github_api_archived(self):
        """测试归档仓库。"""
        data = make_github_api_data(archived=True)
        repo = Repository.from_github_api(data)

        assert repo.is_archived is True

    def test_from_github_api_fork(self):
        """测试Fork仓库。"""
        data = make_github_api_data(is_fork=True)
        repo = Repository.from_github_api(data)

        assert repo.is_fork is True

    def test_days_since_push(self):
        """测试距最后推送天数的计算。"""
        repo = make_repo(pushed_days_ago=10)
        days = repo.days_since_push

        assert days is not None
        assert 9 <= days <= 11  # 允许1天误差

    def test_days_since_push_none(self):
        """测试无推送时间时返回None。"""
        repo = Repository()
        assert repo.days_since_push is None

    def test_days_since_creation(self):
        """测试仓库年龄计算。"""
        repo = make_repo(created_days_ago=365)
        days = repo.days_since_creation

        assert days is not None
        assert 364 <= days <= 366

    def test_age_category_new(self):
        """测试新仓库分类。"""
        repo = make_repo(created_days_ago=30)
        assert repo.age_category == "new"

    def test_age_category_mature(self):
        """测试成熟仓库分类。"""
        repo = make_repo(created_days_ago=400)
        assert repo.age_category == "mature"

    def test_age_category_old(self):
        """测试老仓库分类。"""
        repo = make_repo(created_days_ago=800)
        assert repo.age_category == "old"

    def test_age_category_unknown(self):
        """测试无创建时间的仓库。"""
        repo = Repository()
        assert repo.age_category == "unknown"

    def test_to_dict(self):
        """测试转换为字典。"""
        repo = make_repo()
        d = repo.to_dict()

        assert isinstance(d, dict)
        assert d["name"] == "test-repo"
        assert d["stars"] == 100
        assert "health_score" in d
        assert "tags" in d

    def test_repr(self):
        """测试字符串表示。"""
        repo = make_repo()
        r = repr(repo)

        assert "testuser/test-repo" in r
        assert "100" in r
        assert "Python" in r


# ==================== Config 配置管理测试 ====================


class TestConfig:
    """Config配置管理测试。"""

    def test_default_config(self):
        """测试默认配置加载。"""
        config = Config()

        assert config.cache_ttl == 300
        assert config.api_base_url == "https://api.github.com"
        assert config.per_page == 30

    def test_custom_config_file(self):
        """测试自定义配置文件。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({"github_token": "test123", "per_page": 50}, f)
            f.flush()
            config = Config(config_path=f.name)

        assert config.github_token == "test123"
        assert config.per_page == 50

        os.unlink(f.name)

    def test_config_merge(self):
        """测试配置合并。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({"per_page": 100, "cache_ttl": 600}, f)
            f.flush()
            config = Config(config_path=f.name)

        # 自定义值覆盖默认值
        assert config.per_page == 100
        assert config.cache_ttl == 600
        # 未覆盖的保持默认值
        assert config.api_base_url == "https://api.github.com"

        os.unlink(f.name)

    def test_config_set_and_save(self):
        """测试配置设置和保存。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.flush()
            config = Config(config_path=f.name)

        config.set("default_user", "newuser")
        config.save()

        # 重新加载验证
        config2 = Config(config_path=f.name)
        assert config2.default_user == "newuser"

        os.unlink(f.name)

    def test_config_get(self):
        """测试配置获取。"""
        config = Config()
        assert config.get("nonexistent", "default") == "default"
        assert config.get("cache_ttl") == 300

    def test_config_health_weights(self):
        """测试健康评分权重配置。"""
        config = Config()
        weights = config.health_weights

        assert "update_activity" in weights
        assert weights["update_activity"] == 25

    def test_config_tag_rules(self):
        """测试标签规则配置。"""
        config = Config()
        rules = config.tag_rules

        assert "active_days" in rules
        assert rules["active_days"] == 30

    def test_broken_config_file(self):
        """测试损坏的配置文件不中断程序。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{invalid json")
            f.flush()
            config = Config(config_path=f.name)

        # 应使用默认值
        assert config.cache_ttl == 300

        os.unlink(f.name)


# ==================== HealthEngine 健康评分测试 ====================


class TestHealthEngine:
    """HealthEngine健康评分引擎测试。"""

    def setup_method(self):
        """每个测试方法前执行。"""
        self.engine = HealthEngine()

    def test_score_active_repo(self):
        """测试活跃仓库的高评分。"""
        repo = make_repo(
            pushed_days_ago=5,
            stars=500,
            forks=100,
            open_issues=10,
            description="Great project",
            has_license=True,
        )
        repo.has_readme = True
        repo.has_wiki = True
        repo.topics = ["python", "cli"]

        report = self.engine.score(repo)

        assert report.overall_score >= 60
        assert report.repo_name == "testuser/test-repo"

    def test_score_archived_repo(self):
        """测试归档仓库的低评分。"""
        repo = make_repo(archived=True, stars=0, forks=0)

        report = self.engine.score(repo)

        assert report.overall_score < 40

    def test_score_stale_repo(self):
        """测试停滞仓库的评分。"""
        repo = make_repo(pushed_days_ago=300, stars=5, forks=0)

        report = self.engine.score(repo)

        # 更新活跃度应该较低
        assert report.update_activity < 50

    def test_score_high_star_repo(self):
        """测试高Star仓库的社区参与度评分。"""
        repo = make_repo(stars=2000, forks=500)

        report = self.engine.score(repo)

        assert report.community_engagement >= 80

    def test_grade_a(self):
        """测试A等级。"""
        report = HealthReport(overall_score=92.0)
        assert report.grade == "A"
        assert report.grade_color == "green"

    def test_grade_b(self):
        """测试B等级。"""
        report = HealthReport(overall_score=80.0)
        assert report.grade == "B"
        assert report.grade_color == "blue"

    def test_grade_c(self):
        """测试C等级。"""
        report = HealthReport(overall_score=65.0)
        assert report.grade == "C"
        assert report.grade_color == "yellow"

    def test_grade_d(self):
        """测试D等级。"""
        report = HealthReport(overall_score=45.0)
        assert report.grade == "D"
        assert report.grade_color == "red"

    def test_grade_f(self):
        """测试F等级。"""
        report = HealthReport(overall_score=20.0)
        assert report.grade == "F"
        assert report.grade_color == "bold red"

    def test_score_all(self):
        """测试批量评分。"""
        repos = [
            make_repo(name=f"repo-{i}", pushed_days_ago=i * 30)
            for i in range(5)
        ]
        reports = self.engine.score_all(repos)

        assert len(reports) == 5
        # 所有仓库都应有评分
        for report in reports:
            assert 0 <= report.overall_score <= 100

    def test_score_all_updates_repo_health(self):
        """测试批量评分会更新仓库的health_score字段。"""
        repos = [make_repo(name="repo-1")]
        self.engine.score_all(repos)

        assert repos[0].health_score > 0

    def test_get_summary_empty(self):
        """测试空列表的摘要。"""
        summary = self.engine.get_summary([])

        assert summary["total"] == 0
        assert summary["avg_score"] == 0.0

    def test_get_summary(self):
        """测试摘要统计。"""
        repos = [make_repo(name=f"repo-{i}") for i in range(3)]
        reports = self.engine.score_all(repos)
        summary = self.engine.get_summary(reports)

        assert summary["total"] == 3
        assert "avg_score" in summary
        assert "grade_distribution" in summary
        assert len(summary["top_repos"]) <= 5

    def test_report_to_dict(self):
        """测试报告转换为字典。"""
        repo = make_repo()
        report = self.engine.score(repo)
        d = report.to_dict()

        assert "repo_name" in d
        assert "overall_score" in d
        assert "grade" in d


# ==================== TagEngine 智能标签测试 ====================


class TestTagEngine:
    """TagEngine智能标签引擎测试。"""

    def setup_method(self):
        """每个测试方法前执行。"""
        self.engine = TagEngine()

    def test_active_tag(self):
        """测试活跃标签。"""
        repo = make_repo(pushed_days_ago=10)
        tags = self.engine.tag(repo)

        assert "active" in tags

    def test_stale_tag(self):
        """测试停滞标签。"""
        repo = make_repo(pushed_days_ago=100)
        tags = self.engine.tag(repo)

        assert "stale" in tags
        assert "active" not in tags

    def test_archived_tag(self):
        """测试归档标签。"""
        repo = make_repo(archived=True)
        tags = self.engine.tag(repo)

        assert "archived" in tags
        # 归档仓库只有archived标签
        assert len(tags) == 1

    def test_rising_star_tag(self):
        """测试新星标签。"""
        repo = make_repo(
            created_days_ago=100,
            stars=80,
        )
        tags = self.engine.tag(repo)

        assert "rising_star" in tags

    def test_high_impact_tag(self):
        """测试高影响力标签。"""
        repo = make_repo(stars=600)
        tags = self.engine.tag(repo)

        assert "high_impact" in tags

    def test_popular_tag(self):
        """测试热门标签。"""
        repo = make_repo(stars=200, forks=80)
        tags = self.engine.tag(repo)

        assert "popular" in tags

    def test_needs_attention_tag(self):
        """测试待关注标签。"""
        repo = make_repo(
            pushed_days_ago=200,
            open_issues=10,
        )
        tags = self.engine.tag(repo)

        assert "needs_attention" in tags

    def test_well_documented_tag(self):
        """测试文档完善标签。"""
        repo = make_repo(description="A well documented project")
        repo.has_readme = True
        repo.has_wiki = True
        tags = self.engine.tag(repo)

        assert "well_documented" in tags

    def test_personal_tag(self):
        """测试个人项目标签。"""
        repo = make_repo(stars=3, forks=0)
        tags = self.engine.tag(repo)

        assert "personal" in tags

    def test_mature_tag(self):
        """测试成熟项目标签。"""
        repo = make_repo(
            pushed_days_ago=10,
            created_days_ago=1000,
        )
        tags = self.engine.tag(repo)

        assert "mature" in tags
        assert "active" in tags

    def test_tag_all(self):
        """测试批量标签。"""
        repos = [
            make_repo(name=f"repo-{i}", pushed_days_ago=i * 50)
            for i in range(5)
        ]
        tag_groups = self.engine.tag_all(repos)

        assert isinstance(tag_groups, dict)
        # 至少应该有一些标签分组
        assert len(tag_groups) > 0

    def test_tag_all_updates_repo_tags(self):
        """测试批量标签会更新仓库的tags字段。"""
        repos = [make_repo(pushed_days_ago=5)]
        self.engine.tag_all(repos)

        assert len(repos[0].tags) > 0

    def test_get_tag_stats(self):
        """测试标签统计。"""
        repos = [
            make_repo(name=f"repo-{i}", pushed_days_ago=i * 50)
            for i in range(5)
        ]
        stats = self.engine.get_tag_stats(repos)

        assert stats["total_repos"] == 5
        assert "tag_counts" in stats
        assert "tag_details" in stats

    def test_get_tag_description(self):
        """测试获取标签描述。"""
        desc = TagEngine.get_tag_description("active")
        assert "活跃" in desc

    def test_list_all_tags(self):
        """测试列出所有标签。"""
        all_tags = TagEngine.list_all_tags()

        assert isinstance(all_tags, dict)
        assert "active" in all_tags
        assert "stale" in all_tags
        assert "archived" in all_tags


# ==================== SearchFilter 搜索过滤测试 ====================


class TestSearchFilter:
    """SearchFilter搜索过滤器测试。"""

    def setup_method(self):
        """每个测试方法前执行。"""
        self.filter = SearchFilter()
        self.repos = [
            make_repo(name="python-project", language="Python", stars=100),
            make_repo(name="js-project", language="JavaScript", stars=200),
            make_repo(name="go-project", language="Go", stars=50),
            make_repo(name="rust-tool", language="Rust", stars=300),
        ]

    def test_filter_by_language(self):
        """测试按语言过滤。"""
        result = self.filter.filter_repos(self.repos, language="Python")

        assert len(result) == 1
        assert result[0].name == "python-project"

    def test_filter_by_language_case_insensitive(self):
        """测试语言过滤不区分大小写。"""
        result = self.filter.filter_repos(self.repos, language="python")

        assert len(result) == 1

    def test_filter_by_min_stars(self):
        """测试按最小Stars过滤。"""
        result = self.filter.filter_repos(self.repos, min_stars=150)

        assert len(result) == 2

    def test_filter_by_stars_range(self):
        """测试按Stars范围过滤。"""
        result = self.filter.filter_repos(
            self.repos, min_stars=50, max_stars=200
        )

        assert len(result) == 3

    def test_filter_by_keyword(self):
        """测试按关键词过滤。"""
        result = self.filter.filter_repos(self.repos, keyword="project")

        assert len(result) == 3  # python-project, js-project, go-project

    def test_filter_by_archived(self):
        """测试按归档状态过滤。"""
        archived_repo = make_repo(name="old-repo", archived=True)
        all_repos = self.repos + [archived_repo]

        result = self.filter.filter_repos(all_repos, is_archived=False)
        assert len(result) == 4

        result = self.filter.filter_repos(all_repos, is_archived=True)
        assert len(result) == 1

    def test_filter_by_updated_within_days(self):
        """测试按更新时间过滤。"""
        old_repo = make_repo(name="old", pushed_days_ago=100)
        new_repo = make_repo(name="new", pushed_days_ago=5)
        repos = [old_repo, new_repo]

        result = self.filter.filter_repos(repos, updated_within_days=30)
        assert len(result) == 1
        assert result[0].name == "new"

    def test_filter_by_tags(self):
        """测试按标签过滤。"""
        repo1 = make_repo(name="tagged")
        repo1.tags = ["active", "popular"]
        repo2 = make_repo(name="untagged")
        repo2.tags = ["stale"]

        result = self.filter.filter_repos([repo1, repo2], tags=["active"])
        assert len(result) == 1

    def test_sort_by_stars(self):
        """测试按Stars排序。"""
        result = self.filter.filter_repos(
            self.repos, sort_by="stars", sort_desc=True
        )

        assert result[0].stars >= result[1].stars

    def test_sort_by_name(self):
        """测试按名称排序。"""
        result = self.filter.filter_repos(
            self.repos, sort_by="name", sort_desc=False
        )

        names = [r.name for r in result]
        assert names == sorted(names)

    def test_get_unique_languages(self):
        """测试获取唯一语言列表。"""
        languages = SearchFilter.get_unique_languages(self.repos)

        assert "Python" in languages
        assert "JavaScript" in languages
        assert len(languages) == 4

    def test_empty_filter(self):
        """测试空过滤条件返回所有仓库。"""
        result = self.filter.filter_repos(self.repos)

        assert len(result) == 4

    def test_no_match(self):
        """测试无匹配结果。"""
        result = self.filter.filter_repos(
            self.repos, language="Fortran"
        )

        assert len(result) == 0


# ==================== DependencyChecker 依赖检查测试 ====================


class TestDependencyChecker:
    """DependencyChecker依赖安全检查测试。"""

    def setup_method(self):
        """每个测试方法前执行。"""
        self.checker = DependencyChecker()

    def test_parse_requirements_txt(self):
        """测试解析requirements.txt。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("requests==2.28.0\n")
            f.write("flask>=2.0.0\n")
            f.write("numpy\n")
            f.write("# 这是注释\n")
            f.write("-r other.txt\n")
            f.flush()

            deps = self.checker.parse_requirements_txt(f.name)

        assert len(deps) == 3
        assert deps[0]["name"] == "requests"
        assert deps[0]["version_spec"] == "==2.28.0"
        assert deps[1]["name"] == "flask"
        assert deps[2]["name"] == "numpy"

        os.unlink(f.name)

    def test_parse_requirements_empty(self):
        """测试解析空文件。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("")
            f.flush()

            deps = self.checker.parse_requirements_txt(f.name)

        assert len(deps) == 0
        os.unlink(f.name)

    def test_parse_requirements_nonexistent(self):
        """测试解析不存在的文件。"""
        deps = self.checker.parse_requirements_txt("/nonexistent/file.txt")
        assert len(deps) == 0

    def test_parse_package_json(self):
        """测试解析package.json。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "name": "test-project",
                "dependencies": {
                    "express": "^4.18.0",
                    "lodash": "4.17.20",
                },
                "devDependencies": {
                    "axios": "^1.5.0",
                },
            }, f)
            f.flush()

            deps = self.checker.parse_package_json(f.name)

        assert len(deps) == 3
        dep_names = {d["name"] for d in deps}
        assert "express" in dep_names
        assert "lodash" in dep_names
        assert "axios" in dep_names

        os.unlink(f.name)

    def test_parse_package_json_nonexistent(self):
        """测试解析不存在的package.json。"""
        deps = self.checker.parse_package_json("/nonexistent/package.json")
        assert len(deps) == 0

    def test_check_vulnerable_dependencies(self):
        """测试检测有漏洞的依赖。"""
        deps = [
            {"name": "flask", "version_spec": "==2.3.0"},
            {"name": "pyyaml", "version_spec": "==5.3"},
        ]

        vulns = self.checker.check_dependencies(deps)

        assert len(vulns) >= 2
        vuln_ids = {v["vulnerability_id"] for v in vulns}
        assert "CVE-2023-30861" in vuln_ids  # Flask
        assert "CVE-2020-14343" in vuln_ids  # PyYAML

    def test_check_safe_dependencies(self):
        """测试安全的依赖。"""
        deps = [
            {"name": "requests", "version_spec": "==2.31.0"},
            {"name": "urllib3", "version_spec": "==2.0.7"},
        ]

        vulns = self.checker.check_dependencies(deps)

        # 这些版本已修复漏洞
        assert len(vulns) == 0

    def test_check_file_requirements(self):
        """测试检查requirements.txt文件。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("flask==2.3.0\n")
            f.write("django==4.2.0\n")
            f.write("requests==2.31.0\n")
            f.flush()

            result = self.checker.check_file(f.name)

        assert result["file_type"] == "pip"
        assert result["total_dependencies"] == 3
        assert result["summary"]["total_vulnerabilities"] >= 2

        os.unlink(f.name)

    def test_check_file_package_json(self):
        """测试检查package.json文件。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "dependencies": {
                    "lodash": "4.17.20",
                    "express": "4.18.0",
                }
            }, f)
            f.flush()

            result = self.checker.check_file(f.name)

        assert result["file_type"] == "npm"
        assert result["total_dependencies"] == 2
        assert result["summary"]["total_vulnerabilities"] >= 1

        os.unlink(f.name)

    def test_check_file_unsupported(self):
        """测试检查不支持的文件类型。"""
        result = self.checker.check_file("test.py")
        assert "error" in result

    def test_extract_version(self):
        """测试版本号提取。"""
        assert DependencyChecker._extract_version("==2.28.0") == "2.28.0"
        assert DependencyChecker._extract_version(">=1.0.0") == "1.0.0"
        assert DependencyChecker._extract_version("^4.18.0") == "4.18.0"
        assert DependencyChecker._extract_version("~1.2.3") == "1.2.3"
        assert DependencyChecker._extract_version("1.0.0") == "1.0.0"

    def test_is_affected(self):
        """测试版本影响判断。"""
        assert DependencyChecker._is_affected("2.28.0", "<2.31.0") is True
        assert DependencyChecker._is_affected("2.31.0", "<2.31.0") is False
        assert DependencyChecker._is_affected("2.32.0", "<2.31.0") is False
        assert DependencyChecker._is_affected("1.0.0", ">=2.0.0") is False
        assert DependencyChecker._is_affected("2.0.0", ">=2.0.0") is True
        assert DependencyChecker._is_affected("3.0.0", ">=2.0.0") is True

    def test_get_vulnerability_db_info(self):
        """测试获取漏洞数据库信息。"""
        info = self.checker.get_vulnerability_db_info()

        assert info["total_packages_tracked"] > 0
        assert info["total_vulnerabilities"] > 0
        assert "high" in info["severity_distribution"]
        assert "medium" in info["severity_distribution"]
        assert len(info["packages"]) > 0


# ==================== BatchOperator 批量操作测试 ====================


class TestBatchOperator:
    """BatchOperator批量操作测试。"""

    def test_filter_by_names(self):
        """测试按名称筛选。"""
        repos = [
            make_repo(name="repo-1", owner="user"),
            make_repo(name="repo-2", owner="user"),
            make_repo(name="repo-3", owner="user"),
        ]

        batch = BatchOperator()
        result = batch.filter_by_names(
            repos, ["user/repo-1", "user/repo-3"]
        )

        assert len(result) == 2

    def test_filter_by_names_short(self):
        """测试按短名称筛选。"""
        repos = [
            make_repo(name="repo-1", owner="user"),
            make_repo(name="repo-2", owner="user"),
        ]

        batch = BatchOperator()
        result = batch.filter_by_names(repos, ["repo-1"])

        assert len(result) == 1

    def test_batch_export_json(self, tmp_path):
        """测试JSON导出。"""
        repos = [make_repo(name="repo-1"), make_repo(name="repo-2")]
        filepath = str(tmp_path / "export.json")

        batch = BatchOperator()
        result = batch.batch_export_json(repos, filepath)

        assert result == filepath

        # 验证文件内容
        with open(filepath, "r") as f:
            data = json.load(f)
        assert len(data) == 2

    def test_batch_export_csv(self, tmp_path):
        """测试CSV导出。"""
        repos = [make_repo(name="repo-1"), make_repo(name="repo-2")]
        filepath = str(tmp_path / "export.csv")

        batch = BatchOperator()
        result = batch.batch_export_csv(repos, filepath)

        assert result == filepath

        # 验证文件存在且非空
        with open(filepath, "r") as f:
            content = f.read()
        assert "repo-1" in content
        assert "repo-2" in content

    def test_batch_export_empty(self, tmp_path):
        """测试空列表导出。"""
        filepath = str(tmp_path / "empty.json")

        batch = BatchOperator()
        batch.batch_export_json([], filepath)

        with open(filepath, "r") as f:
            data = json.load(f)
        assert len(data) == 0

    def test_batch_mark_archived(self):
        """测试批量归档标记。"""
        repos = [
            make_repo(name="repo-1"),
            make_repo(name="repo-2"),
        ]

        batch = BatchOperator()
        result = batch.batch_mark_archived(repos)

        assert all(r.is_archived for r in result)
        assert all("archived" in r.tags for r in result)


# ==================== RepositoryManager 测试 ====================


class TestRepositoryManager:
    """RepositoryManager仓库管理器测试。"""

    def test_get_stats_empty(self):
        """测试空仓库列表的统计。"""
        manager = RepositoryManager()
        stats = manager.get_stats()

        assert stats["total"] == 0
        assert stats["total_stars"] == 0

    def test_get_stats(self):
        """测试仓库列表统计。"""
        manager = RepositoryManager()
        manager._repositories = [
            make_repo(name="repo-1", language="Python", stars=100),
            make_repo(name="repo-2", language="Python", stars=200),
            make_repo(name="repo-3", language="Go", stars=50),
        ]

        stats = manager.get_stats()

        assert stats["total"] == 3
        assert stats["total_stars"] == 350
        assert stats["languages"]["Python"] == 2
        assert stats["languages"]["Go"] == 1

    def test_export_json(self, tmp_path):
        """测试JSON导出。"""
        manager = RepositoryManager()
        manager._repositories = [make_repo(name="repo-1")]
        filepath = str(tmp_path / "test.json")

        manager.export_json(filepath)

        with open(filepath, "r") as f:
            data = json.load(f)
        assert len(data) == 1

    def test_export_csv(self, tmp_path):
        """测试CSV导出。"""
        manager = RepositoryManager()
        manager._repositories = [make_repo(name="repo-1")]
        filepath = str(tmp_path / "test.csv")

        manager.export_csv(filepath)

        with open(filepath, "r") as f:
            content = f.read()
        assert "repo-1" in content

    def test_repr(self):
        """测试字符串表示。"""
        manager = RepositoryManager()
        assert "repos=0" in repr(manager)

        manager._repositories = [make_repo()]
        assert "repos=1" in repr(manager)
