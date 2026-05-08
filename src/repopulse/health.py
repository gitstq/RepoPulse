"""
健康评分引擎模块 - Health scoring engine module.

基于多维度指标对Git仓库进行健康评分，总分100分。
Scores Git repository health based on multi-dimensional metrics, total 100 points.

评分维度 (Scoring Dimensions):
1. 更新活跃度 (Update Activity) - 25分
2. 社区参与度 (Community Engagement) - 25分
3. 代码质量指标 (Code Quality Indicators) - 20分
4. 文档完整度 (Documentation Completeness) - 15分
5. 维护响应度 (Maintenance Responsiveness) - 15分
"""

from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import Config
from .core import Repository


@dataclass
class HealthReport:
    """健康评分报告。

    Health scoring report with per-dimension scores and overall score.
    """

    repo_name: str = ""                              # 仓库名称
    overall_score: float = 0.0                       # 总分 (0-100)
    update_activity: float = 0.0                     # 更新活跃度得分
    community_engagement: float = 0.0                # 社区参与度得分
    code_quality: float = 0.0                        # 代码质量指标得分
    documentation: float = 0.0                       # 文档完整度得分
    maintenance_response: float = 0.0                # 维护响应度得分
    details: Dict[str, Any] = field(default_factory=dict)  # 评分详情

    @property
    def grade(self) -> str:
        """根据总分返回等级。

        Return grade based on overall score.

        Returns:
            等级: A(90+), B(75-89), C(60-74), D(40-59), F(<40)
        """
        if self.overall_score >= 90:
            return "A"
        elif self.overall_score >= 75:
            return "B"
        elif self.overall_score >= 60:
            return "C"
        elif self.overall_score >= 40:
            return "D"
        else:
            return "F"

    @property
    def grade_color(self) -> str:
        """返回等级对应的颜色名称（用于Rich渲染）。

        Return color name for the grade (for Rich rendering).
        """
        grade_colors = {
            "A": "green",
            "B": "blue",
            "C": "yellow",
            "D": "red",
            "F": "bold red",
        }
        return grade_colors.get(self.grade, "white")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。Convert to dict."""
        return {
            "repo_name": self.repo_name,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "update_activity": self.update_activity,
            "community_engagement": self.community_engagement,
            "code_quality": self.code_quality,
            "documentation": self.documentation,
            "maintenance_response": self.maintenance_response,
            "details": self.details,
        }


class HealthEngine:
    """仓库健康评分引擎。

    Repository health scoring engine that evaluates repositories
    across five dimensions and produces an overall health score.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """初始化健康评分引擎。

        Args:
            config: 配置管理器实例. Config instance.
        """
        self._config = config or Config()
        weights = self._config.health_weights
        self._weight_update = weights.get("update_activity", 25)
        self._weight_community = weights.get("community_engagement", 25)
        self._weight_quality = weights.get("code_quality", 20)
        self._weight_docs = weights.get("documentation", 15)
        self._weight_maintenance = weights.get("maintenance_response", 15)

    def score(self, repo: Repository) -> HealthReport:
        """对单个仓库进行健康评分。

        Score a single repository's health.

        Args:
            repo: 仓库对象. Repository object.

        Returns:
            健康评分报告. Health report.
        """
        report = HealthReport(repo_name=repo.full_name)

        # 计算各维度得分（每维度满分100）
        report.update_activity = self._score_update_activity(repo)
        report.community_engagement = self._score_community_engagement(repo)
        report.code_quality = self._score_code_quality(repo)
        report.documentation = self._score_documentation(repo)
        report.maintenance_response = self._score_maintenance_response(repo)

        # 计算加权总分
        total_weight = (
            self._weight_update
            + self._weight_community
            + self._weight_quality
            + self._weight_docs
            + self._weight_maintenance
        )
        report.overall_score = round(
            (
                report.update_activity * self._weight_update
                + report.community_engagement * self._weight_community
                + report.code_quality * self._weight_quality
                + report.documentation * self._weight_docs
                + report.maintenance_response * self._weight_maintenance
            )
            / total_weight,
            1,
        )

        # 填充详情
        report.details = {
            "days_since_push": repo.days_since_push,
            "stars": repo.stars,
            "forks": repo.forks,
            "open_issues": repo.open_issues,
            "language": repo.language,
            "has_readme": repo.has_readme,
            "has_license": repo.has_license,
            "is_archived": repo.is_archived,
            "age_category": repo.age_category,
        }

        return report

    def score_all(self, repos: List[Repository]) -> List[HealthReport]:
        """对多个仓库进行健康评分。

        Score multiple repositories.

        Args:
            repos: 仓库列表. List of Repository objects.

        Returns:
            健康评分报告列表. List of HealthReport objects.
        """
        reports = []
        for repo in repos:
            report = self.score(repo)
            # 将评分写回仓库对象
            repo.health_score = report.overall_score
            reports.append(report)
        return reports

    def _score_update_activity(self, repo: Repository) -> float:
        """评估更新活跃度（满分100）。

        Score update activity (max 100).

        评分规则：
        - 7天内推送: 100分
        - 30天内推送: 80分
        - 90天内推送: 60分
        - 180天内推送: 40分
        - 365天内推送: 20分
        - 超过365天: 5分
        - 已归档: 0分
        """
        if repo.is_archived:
            return 0.0

        days = repo.days_since_push
        if days is None:
            return 10.0

        if days <= 7:
            return 100.0
        elif days <= 30:
            # 线性衰减: 100 -> 80
            return 80.0 + (30 - days) / 23 * 20.0
        elif days <= 90:
            # 线性衰减: 80 -> 60
            return 60.0 + (90 - days) / 60 * 20.0
        elif days <= 180:
            # 线性衰减: 60 -> 40
            return 40.0 + (180 - days) / 90 * 20.0
        elif days <= 365:
            # 线性衰减: 40 -> 20
            return 20.0 + (365 - days) / 185 * 20.0
        else:
            return 5.0

    def _score_community_engagement(self, repo: Repository) -> float:
        """评估社区参与度（满分100）。

        Score community engagement (max 100).

        评分规则（基于Stars和Forks）：
        - Stars评分 (0-50分):
          - 1000+: 50分
          - 500-999: 40分
          - 100-499: 30分
          - 50-99: 20分
          - 10-49: 10分
          - <10: 5分
        - Forks评分 (0-30分):
          - 200+: 30分
          - 50-199: 20分
          - 10-49: 10分
          - <10: 5分
        - Watchers评分 (0-20分):
          - 100+: 20分
          - 50-99: 15分
          - 10-49: 10分
          - <10: 5分
        """
        # Stars评分
        stars = repo.stars
        if stars >= 1000:
            stars_score = 50.0
        elif stars >= 500:
            stars_score = 40.0
        elif stars >= 100:
            stars_score = 30.0
        elif stars >= 50:
            stars_score = 20.0
        elif stars >= 10:
            stars_score = 10.0
        else:
            stars_score = 5.0

        # Forks评分
        forks = repo.forks
        if forks >= 200:
            forks_score = 30.0
        elif forks >= 50:
            forks_score = 20.0
        elif forks >= 10:
            forks_score = 10.0
        else:
            forks_score = 5.0

        # Watchers评分
        watchers = repo.watchers
        if watchers >= 100:
            watchers_score = 20.0
        elif watchers >= 50:
            watchers_score = 15.0
        elif watchers >= 10:
            watchers_score = 10.0
        else:
            watchers_score = 5.0

        return min(100.0, stars_score + forks_score + watchers_score)

    def _score_code_quality(self, repo: Repository) -> float:
        """评估代码质量指标（满分100）。

        Score code quality indicators (max 100).

        评分规则：
        - 有License: +25分
        - 有明确的主要语言: +25分
        - 非Fork仓库: +25分
        - 仓库大小合理(>0且<100000KB): +25分
        - 已归档: -50分
        """
        score = 0.0

        # 有License
        if repo.has_license:
            score += 25.0

        # 有主要语言
        if repo.language:
            score += 25.0

        # 非Fork
        if not repo.is_fork:
            score += 25.0

        # 仓库大小合理
        if 0 < repo.size < 100000:
            score += 25.0
        elif repo.size > 0:
            score += 15.0  # 超大仓库给部分分

        # 归档仓库扣分
        if repo.is_archived:
            score = max(0.0, score - 50.0)

        return score

    def _score_documentation(self, repo: Repository) -> float:
        """评估文档完整度（满分100）。

        Score documentation completeness (max 100).

        评分规则：
        - 有README: +40分
        - 有Wiki: +20分
        - 有描述: +20分
        - 有Topics标签: +20分
        """
        score = 0.0

        # 有README
        if repo.has_readme:
            score += 40.0

        # 有Wiki
        if repo.has_wiki:
            score += 20.0

        # 有描述
        if repo.description:
            score += 20.0

        # 有Topics标签
        if repo.topics:
            score += 20.0

        return score

    def _score_maintenance_response(self, repo: Repository) -> float:
        """评估维护响应度（满分100）。

        Score maintenance responsiveness (max 100).

        评分规则：
        - 开放Issue数量适中(1-50): +40分
        - 开放Issue过多(>50): +20分
        - 无开放Issue: +30分
        - 非归档且近期有更新: +30分
        - 有License(表明正式维护): +15分
        - 有描述(表明维护者关注): +15分
        """
        score = 0.0

        # Issue数量评分
        issues = repo.open_issues
        if 1 <= issues <= 50:
            score += 40.0
        elif issues == 0:
            score += 30.0
        else:
            score += 20.0  # Issue过多，可能维护不过来

        # 近期更新
        days = repo.days_since_push
        if days is not None and days <= 90:
            score += 30.0
        elif days is not None and days <= 180:
            score += 15.0

        # 有License
        if repo.has_license:
            score += 15.0

        # 有描述
        if repo.description:
            score += 15.0

        return min(100.0, score)

    def get_summary(self, reports: List[HealthReport]) -> Dict[str, Any]:
        """获取健康评分摘要统计。

        Get health score summary statistics.

        Args:
            reports: 健康评分报告列表. List of HealthReport objects.

        Returns:
            摘要统计字典. Summary statistics dict.
        """
        if not reports:
            return {
                "total": 0,
                "avg_score": 0.0,
                "grade_distribution": {},
                "top_repos": [],
                "needs_attention": [],
            }

        total = len(reports)
        avg_score = round(
            sum(r.overall_score for r in reports) / total, 1
        )

        # 等级分布
        grade_dist: Dict[str, int] = {}
        for r in reports:
            grade_dist[r.grade] = grade_dist.get(r.grade, 0) + 1

        # Top仓库（按评分排序）
        top_repos = sorted(reports, key=lambda r: r.overall_score, reverse=True)[:5]

        # 需要关注的仓库（评分低于60）
        needs_attention = [
            r for r in reports if r.overall_score < 60
        ]
        needs_attention.sort(key=lambda r: r.overall_score)

        return {
            "total": total,
            "avg_score": avg_score,
            "grade_distribution": grade_dist,
            "top_repos": [r.to_dict() for r in top_repos],
            "needs_attention": [r.to_dict() for r in needs_attention],
        }
