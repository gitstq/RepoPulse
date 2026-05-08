"""
TUI仪表盘模块 - TUI Dashboard module.

使用Rich库构建交互式终端仪表盘，展示仓库信息、健康评分和标签统计。
Builds an interactive terminal dashboard using Rich, displaying repository
info, health scores, and tag statistics.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.columns import Columns
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from .config import Config
from .core import Repository, RepositoryManager
from .health import HealthEngine, HealthReport
from .tags import TagEngine


class Dashboard:
    """TUI仪表盘。

    TUI Dashboard that renders repository information, health scores,
    tag statistics, and other data using Rich library.
    """

    def __init__(
        self,
        manager: Optional[RepositoryManager] = None,
        config: Optional[Config] = None,
    ) -> None:
        """初始化仪表盘。

        Args:
            manager: 仓库管理器实例. Repository manager instance.
            config: 配置管理器实例. Config instance.
        """
        self._config = config or Config()
        self._manager = manager or RepositoryManager(self._config)
        self._health_engine = HealthEngine(self._config)
        self._tag_engine = TagEngine(self._config)
        self._console = Console()

    @property
    def console(self) -> Console:
        """获取Rich Console实例。"""
        return self._console

    def render_dashboard(
        self,
        repos: Optional[List[Repository]] = None,
    ) -> None:
        """渲染完整的TUI仪表盘。

        Render the full TUI dashboard.

        Args:
            repos: 仓库列表，为None时使用管理器中已加载的仓库。
                   Repository list, uses manager's repos if None.
        """
        if repos is None:
            repos = self._manager.repositories

        if not repos:
            self._console.print(
                Panel(
                    "[yellow]没有仓库数据。请先使用 'repopulse list --user <username>' 加载仓库。[/yellow]",
                    title="RepoPulse 仪表盘",
                    border_style="blue",
                )
            )
            return

        # 计算健康评分和标签
        health_reports = self._health_engine.score_all(repos)
        tag_stats = self._tag_engine.get_tag_stats(repos)
        summary = self._manager.get_stats()

        # 构建布局
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )

        # 头部
        layout["header"].update(self._render_header(summary))

        # 主体
        layout["body"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1),
        )

        # 左侧：仓库表格
        layout["left"].update(self._render_repo_table(repos))

        # 右侧：统计面板
        layout["right"].split_column(
            Layout(name="health_summary"),
            Layout(name="tag_stats"),
            Layout(name="lang_stats"),
        )
        layout["right"]["health_summary"].update(
            self._render_health_summary(health_reports)
        )
        layout["right"]["tag_stats"].update(
            self._render_tag_stats(tag_stats)
        )
        layout["right"]["lang_stats"].update(
            self._render_language_stats(summary.get("languages", {}))
        )

        # 底部
        layout["footer"].update(self._render_footer())

        # 渲染
        self._console.print(layout)

    def render_repo_table(
        self,
        repos: List[Repository],
        show_health: bool = True,
        show_tags: bool = True,
        max_rows: int = 20,
    ) -> None:
        """渲染仓库列表表格。

        Render repository list table.

        Args:
            repos: 仓库列表. Repository list.
            show_health: 是否显示健康评分. Whether to show health scores.
            show_tags: 是否显示标签. Whether to show tags.
            max_rows: 最大显示行数. Maximum rows to display.
        """
        table = self._render_repo_table_widget(
            repos, show_health, show_tags, max_rows
        )
        self._console.print(table)

    def render_health_report(
        self,
        reports: List[HealthReport],
        detailed: bool = False,
    ) -> None:
        """渲染健康评分报告。

        Render health score report.

        Args:
            reports: 健康评分报告列表. List of HealthReport objects.
            detailed: 是否显示详细信息. Whether to show detailed info.
        """
        if not reports:
            self._console.print("[yellow]没有健康评分数据。[/yellow]")
            return

        # 摘要面板
        summary = self._health_engine.get_summary(reports)
        self._console.print(self._render_health_summary(reports))

        # 详细报告表格
        if detailed:
            table = Table(
                title="健康评分详情",
                box=box.ROUNDED,
                show_lines=True,
            )
            table.add_column("仓库", style="cyan", min_width=30)
            table.add_column("总分", justify="center", min_width=6)
            table.add_column("等级", justify="center", min_width=4)
            table.add_column("更新活跃", justify="center", min_width=8)
            table.add_column("社区参与", justify="center", min_width=8)
            table.add_column("代码质量", justify="center", min_width=8)
            table.add_column("文档完整", justify="center", min_width=8)
            table.add_column("维护响应", justify="center", min_width=8)

            for report in sorted(
                reports, key=lambda r: r.overall_score, reverse=True
            ):
                grade_style = report.grade_color
                table.add_row(
                    report.repo_name,
                    f"{report.overall_score:.1f}",
                    Text(report.grade, style=grade_style),
                    f"{report.update_activity:.0f}",
                    f"{report.community_engagement:.0f}",
                    f"{report.code_quality:.0f}",
                    f"{report.documentation:.0f}",
                    f"{report.maintenance_response:.0f}",
                )

            self._console.print(table)

    def render_tag_report(
        self,
        tag_stats: Dict[str, Any],
    ) -> None:
        """渲染标签统计报告。

        Render tag statistics report.

        Args:
            tag_stats: 标签统计信息. Tag statistics.
        """
        self._console.print(self._render_tag_stats(tag_stats))

    def render_search_results(
        self,
        repos: List[Repository],
        query: str = "",
    ) -> None:
        """渲染搜索结果。

        Render search results.

        Args:
            repos: 搜索结果仓库列表. Search result repositories.
            query: 搜索关键词. Search query.
        """
        if not repos:
            self._console.print(
                f"[yellow]没有找到匹配 '{query}' 的仓库。[/yellow]"
            )
            return

        self._console.print(
            f"[green]找到 {len(repos)} 个匹配的仓库[/green]\n"
        )
        self.render_repo_table(repos, show_health=False, show_tags=False)

    def render_deps_report(
        self,
        result: Dict[str, Any],
    ) -> None:
        """渲染依赖安全检查报告。

        Render dependency security check report.

        Args:
            result: 检查结果字典. Check result dict.
        """
        if "error" in result:
            self._console.print(
                f"[red]错误: {result['error']}[/red]"
            )
            return

        summary = result.get("summary", {})
        vulns = result.get("vulnerabilities", [])

        # 摘要面板
        panel_content = Text()
        panel_content.append(f"文件: {result.get('file', 'N/A')}\n")
        panel_content.append(f"类型: {result.get('file_type', 'N/A')}\n")
        panel_content.append(f"总依赖数: {result.get('total_dependencies', 0)}\n")
        panel_content.append(
            f"漏洞数量: ", style="bold"
        )
        total_vulns = summary.get("total_vulnerabilities", 0)
        if total_vulns > 0:
            panel_content.append(str(total_vulns), style="bold red")
        else:
            panel_content.append(str(total_vulns), style="bold green")

        self._console.print(
            Panel(panel_content, title="依赖安全检查", border_style="blue")
        )

        # 漏洞详情表格
        if vulns:
            table = Table(
                title="发现的安全漏洞",
                box=box.ROUNDED,
                show_lines=True,
            )
            table.add_column("漏洞ID", style="red", min_width=16)
            table.add_column("包名", style="cyan", min_width=15)
            table.add_column("当前版本", min_width=10)
            table.add_column("严重程度", justify="center", min_width=8)
            table.add_column("描述", min_width=30)

            for v in vulns:
                severity = v.get("severity", "low")
                if severity == "high":
                    sev_style = "bold red"
                elif severity == "medium":
                    sev_style = "yellow"
                else:
                    sev_style = "green"

                table.add_row(
                    v.get("vulnerability_id", ""),
                    v.get("package", ""),
                    v.get("installed_version", ""),
                    Text(severity.upper(), style=sev_style),
                    v.get("description", ""),
                )

            self._console.print(table)
        else:
            self._console.print(
                "[green]未发现已知漏洞，所有依赖包安全。[/green]"
            )

    def show_loading(self, message: str = "加载中...") -> Progress:
        """显示加载进度指示器。

        Show loading progress indicator.

        Args:
            message: 加载提示信息. Loading message.

        Returns:
            Rich Progress对象. Rich Progress object.
        """
        return Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]{message}"),
            console=self._console,
        )

    def print_error(self, message: str) -> None:
        """打印错误信息。

        Print error message.

        Args:
            message: 错误信息. Error message.
        """
        self._console.print(f"[bold red]错误: {message}[/bold red]")

    def print_success(self, message: str) -> None:
        """打印成功信息。

        Print success message.

        Args:
            message: 成功信息. Success message.
        """
        self._console.print(f"[bold green]{message}[/bold green]")

    def print_warning(self, message: str) -> None:
        """打印警告信息。

        Print warning message.

        Args:
            message: 警告信息. Warning message.
        """
        self._console.print(f"[bold yellow]{message}[/bold yellow]")

    def print_info(self, message: str) -> None:
        """打印信息。

        Print info message.

        Args:
            message: 信息内容. Info message.
        """
        self._console.print(f"[bold blue]{message}[/bold blue]")

    # ==================== 私有渲染方法 ====================

    def _render_header(self, summary: Dict[str, Any]) -> Panel:
        """渲染头部面板。

        Render header panel.
        """
        header_text = Text()
        header_text.append(" RepoPulse ", style="bold white on blue")
        header_text.append(
            f"  |  仓库: {summary.get('total', 0)}  "
            f"|  Stars: {summary.get('total_stars', 0)}  "
            f"|  Forks: {summary.get('total_forks', 0)}  "
            f"|  平均健康: {summary.get('avg_health', 0)}",
            style="dim",
        )
        return Panel(header_text, box=box.SIMPLE)

    def _render_footer(self) -> Panel:
        """渲染底部面板。

        Render footer panel.
        """
        footer_text = Text(
            " RepoPulse v0.1.0 | 轻量级Git仓库智能管理TUI引擎 ",
            style="dim",
            justify="center",
        )
        return Panel(footer_text, box=box.SIMPLE)

    def _render_repo_table(
        self,
        repos: List[Repository],
        show_health: bool = True,
        show_tags: bool = True,
        max_rows: int = 20,
    ) -> Table:
        """构建仓库表格组件。

        Build repository table widget.
        """
        table = Table(
            title="仓库列表",
            box=box.ROUNDED,
            show_lines=False,
            row_styles=["", "dim"],
        )
        table.add_column("仓库", style="cyan", min_width=30, no_wrap=True)
        table.add_column("语言", justify="center", min_width=8)
        table.add_column("Stars", justify="right", min_width=6)
        table.add_column("Forks", justify="right", min_width=6)
        table.add_column("Issues", justify="right", min_width=6)

        if show_health:
            table.add_column("健康", justify="center", min_width=6)

        table.add_column("更新时间", min_width=12)

        if show_tags:
            table.add_column("标签", min_width=15)

        # 只显示前max_rows个仓库
        display_repos = repos[:max_rows]
        for repo in display_repos:
            # 格式化更新时间（只显示日期部分）
            pushed = repo.pushed_at[:10] if repo.pushed_at else "N/A"

            # 语言颜色
            lang = repo.language or "N/A"

            # 健康评分颜色
            health_str = ""
            if show_health and repo.health_score > 0:
                score = repo.health_score
                if score >= 75:
                    health_str = f"[green]{score:.0f}[/green]"
                elif score >= 60:
                    health_str = f"[yellow]{score:.0f}[/yellow]"
                elif score >= 40:
                    health_str = f"[orange3]{score:.0f}[/orange3]"
                else:
                    health_str = f"[red]{score:.0f}[/red]"

            # 标签
            tags_str = ""
            if show_tags and repo.tags:
                tag_colors = {
                    "active": "green",
                    "stale": "yellow",
                    "archived": "dim",
                    "rising_star": "magenta",
                    "high_impact": "bold blue",
                    "needs_attention": "red",
                    "well_documented": "cyan",
                    "popular": "bold magenta",
                    "personal": "dim",
                    "mature": "green",
                }
                tag_parts = []
                for t in repo.tags[:3]:  # 最多显示3个标签
                    color = tag_colors.get(t, "white")
                    tag_parts.append(f"[{color}]{t}[/{color}]")
                tags_str = " ".join(tag_parts)

            row = [
                repo.full_name,
                lang,
                str(repo.stars),
                str(repo.forks),
                str(repo.open_issues),
            ]

            if show_health:
                row.append(health_str)
            row.append(pushed)
            if show_tags:
                row.append(tags_str)

            table.add_row(*row)

        if len(repos) > max_rows:
            table.add_row(
                f"[dim]... 共 {len(repos)} 个仓库，仅显示前 {max_rows} 个[/dim]",
                "", "", "", "", "", "", ""
            )

        return table

    def _render_health_summary(
        self, reports: List[HealthReport]
    ) -> Panel:
        """渲染健康评分摘要面板。

        Render health score summary panel.
        """
        if not reports:
            return Panel("[dim]无评分数据[/dim]", title="健康评分摘要")

        summary = self._health_engine.get_summary(reports)
        avg = summary.get("avg_score", 0)

        content = Text()
        content.append(f"平均评分: ", style="bold")
        if avg >= 75:
            content.append(f"{avg}", style="bold green")
        elif avg >= 60:
            content.append(f"{avg}", style="bold yellow")
        else:
            content.append(f"{avg}", style="bold red")

        content.append("\n\n等级分布:\n", style="bold")

        grade_dist = summary.get("grade_distribution", {})
        for grade in ["A", "B", "C", "D", "F"]:
            count = grade_dist.get(grade, 0)
            if count > 0:
                bar = "█" * count
                content.append(f"  {grade}: ", style="bold")
                content.append(f"{bar} ({count})\n")

        needs = summary.get("needs_attention", [])
        if needs:
            content.append(f"\n[red]需要关注: {len(needs)} 个仓库[/red]")

        return Panel(content, title="健康评分摘要", border_style="green")

    def _render_tag_stats(self, tag_stats: Dict[str, Any]) -> Panel:
        """渲染标签统计面板。

        Render tag statistics panel.
        """
        tag_counts = tag_stats.get("tag_counts", {})

        if not tag_counts:
            return Panel("[dim]无标签数据[/dim]", title="标签统计")

        content = Text()
        for tag, count in tag_counts.items():
            desc = TagEngine.get_tag_description(tag)
            # 提取中文标签名
            tag_label = desc.split(" - ")[0] if " - " in desc else tag
            bar = "█" * min(count, 20)
            content.append(f"{tag_label}: ", style="bold cyan")
            content.append(f"{bar} ", style="blue")
            content.append(f"({count})\n")

        return Panel(content, title="标签统计", border_style="magenta")

    def _render_language_stats(
        self, languages: Dict[str, int]
    ) -> Panel:
        """渲染语言统计面板。

        Render language statistics panel.
        """
        if not languages:
            return Panel("[dim]无语言数据[/dim]", title="语言分布")

        content = Text()
        # 显示前8种语言
        for lang, count in list(languages.items())[:8]:
            bar = "█" * min(count, 15)
            content.append(f"{lang}: ", style="bold")
            content.append(f"{bar} ", style="green")
            content.append(f"({count})\n")

        if len(languages) > 8:
            content.append(
                f"\n[dim]... 共 {len(languages)} 种语言[/dim]"
            )

        return Panel(content, title="语言分布", border_style="yellow")
